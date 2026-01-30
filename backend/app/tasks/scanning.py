"""Background scanning tasks for detecting data exposures."""

import asyncio
from datetime import datetime

from sqlalchemy import select, create_engine
from sqlalchemy.orm import Session

from app.tasks import celery_app
from app.core.config import settings
from app.models.family_member import FamilyMember
from app.models.exposure import Exposure, ExposureSource, ExposureStatus
from app.models.scan import Scan, ScanStatus, ScanType
from app.services.hibp import check_email_breaches, HIBPError, format_breach_for_exposure
from app.services.data_brokers import generate_search_urls, parse_address_for_location
from app.services.notifications import send_new_exposures_alert, send_scan_complete_alert


# Create sync engine for Celery tasks
sync_database_url = settings.database_url.replace("+asyncpg", "+psycopg2").replace("postgresql+psycopg2", "postgresql")
sync_engine = create_engine(sync_database_url)


def get_sync_db() -> Session:
    """Get a synchronous database session for Celery tasks."""
    return Session(sync_engine)


@celery_app.task(bind=True, max_retries=3)
def run_breach_scan(self, family_member_ids: list[int] | None = None, scan_id: int | None = None):
    """
    Scan Have I Been Pwned for breaches affecting family members.

    Args:
        family_member_ids: Optional list of member IDs to scan. If None, scans all.
        scan_id: Optional scan record ID to update with progress.
    """
    with get_sync_db() as db:
        # Get family members to scan
        query = select(FamilyMember)
        if family_member_ids:
            query = query.where(FamilyMember.id.in_(family_member_ids))

        members = db.execute(query).scalars().all()

        if not members:
            return {"status": "no_members", "message": "No family members to scan"}

        # Update scan status if tracking
        if scan_id:
            scan = db.get(Scan, scan_id)
            if scan:
                scan.status = ScanStatus.RUNNING
                db.commit()

        total_new_exposures = 0
        errors = []

        for member in members:
            # Get all emails to check (new array field + legacy single field)
            emails_to_check = []
            if member.emails:
                emails_to_check.extend(member.emails)
            if member.email and member.email not in emails_to_check:
                emails_to_check.append(member.email)

            if not emails_to_check:
                continue

            member_new_exposures = []  # Track new exposures for this member

            for email in emails_to_check:
                try:
                    # Run async HIBP check in sync context
                    breaches = asyncio.run(check_email_breaches(email))

                    for breach in breaches:
                        # Check if we already have this exposure
                        existing = db.execute(
                            select(Exposure).where(
                                Exposure.family_member_id == member.id,
                                Exposure.source == ExposureSource.BREACH,
                                Exposure.source_name == breach.get("Title", breach.get("Name")),
                            )
                        ).scalar_one_or_none()

                        if not existing:
                            # Create new exposure
                            breach_data = format_breach_for_exposure(breach, email)
                            exposure = Exposure(
                                family_member_id=member.id,
                                source=ExposureSource.BREACH,
                                source_name=breach_data["source_name"],
                                source_url=breach_data["source_url"],
                                data_exposed=breach_data["data_exposed"],
                                status=ExposureStatus.DETECTED,
                            )
                            db.add(exposure)
                            total_new_exposures += 1
                            member_new_exposures.append(breach_data)

                    db.commit()

                except HIBPError as e:
                    errors.append(f"{member.name} ({email}): {str(e)}")
                    # Retry on rate limit
                    if "rate limit" in str(e).lower():
                        raise self.retry(countdown=60 * 2)  # Retry in 2 minutes

            # Send alert if new exposures found for this member
            if member_new_exposures:
                try:
                    send_new_exposures_alert(member_new_exposures, member.name, "breach")
                except Exception:
                    pass  # Don't fail scan if notification fails

        # Update scan record
        if scan_id:
            scan = db.get(Scan, scan_id)
            if scan:
                scan.status = ScanStatus.COMPLETED if not errors else ScanStatus.FAILED
                scan.exposures_found = total_new_exposures
                scan.completed_at = datetime.utcnow()
                if errors:
                    scan.error_message = "; ".join(errors[:3])  # First 3 errors
                db.commit()

        # Send scan completion alert
        if total_new_exposures > 0 or errors:
            try:
                send_scan_complete_alert(
                    scan_type="breach",
                    total_members=len(members),
                    new_exposures=total_new_exposures,
                    errors=errors if errors else None,
                )
            except Exception:
                pass  # Don't fail if notification fails

        return {
            "status": "completed",
            "new_exposures": total_new_exposures,
            "members_scanned": len(members),
            "errors": errors,
        }


@celery_app.task
def run_data_broker_scan(family_member_ids: list[int] | None = None, scan_id: int | None = None):
    """
    Generate search URLs for known data broker sites.

    This creates exposure records with URLs to check. The user must manually
    verify if their data appears on each site, then update the exposure status.

    Args:
        family_member_ids: Optional list of member IDs to scan. If None, scans all.
        scan_id: Optional scan record ID to update with progress.
    """
    with get_sync_db() as db:
        # Get family members to scan
        query = select(FamilyMember)
        if family_member_ids:
            query = query.where(FamilyMember.id.in_(family_member_ids))

        members = db.execute(query).scalars().all()

        if not members:
            return {"status": "no_members", "message": "No family members to scan"}

        # Update scan status if tracking
        if scan_id:
            scan = db.get(Scan, scan_id)
            if scan:
                scan.status = ScanStatus.RUNNING
                db.commit()

        total_new_exposures = 0

        for member in members:
            # Use new name fields, fall back to parsing legacy name
            if member.first_name and member.last_name:
                first_name = member.first_name
                last_name = member.last_name
                middle_initial = member.middle_initial
            else:
                # Parse legacy name field
                name_parts = member.name.strip().split()
                if len(name_parts) < 2:
                    continue
                first_name = name_parts[0]
                last_name = name_parts[-1]
                middle_initial = None

            # Build list of name variations to search
            name_variations = [
                (first_name, last_name),  # Basic: "John Smith"
            ]
            if middle_initial:
                # Add variation with middle initial: "John M Smith"
                name_variations.append((f"{first_name} {middle_initial}", last_name))

            # Get all addresses to use for location
            addresses_to_check = []
            if member.addresses:
                addresses_to_check.extend(member.addresses)
            if member.address and member.address not in addresses_to_check:
                addresses_to_check.append(member.address)

            # If no addresses, still search with just name
            if not addresses_to_check:
                addresses_to_check = [None]

            member_new_exposures = []  # Track new exposures for this member

            # Search for each name variation with each address
            for fname, lname in name_variations:
                for addr in addresses_to_check:
                    city, state = parse_address_for_location(addr) if addr else (None, None)

                    # Generate search URLs for all data broker sites
                    search_results = generate_search_urls(
                        first_name=fname,
                        last_name=lname,
                        city=city,
                        state=state,
                    )

                    for result in search_results:
                        # Check if we already have this exposure (by site name only)
                        existing = db.execute(
                            select(Exposure).where(
                                Exposure.family_member_id == member.id,
                                Exposure.source == ExposureSource.PEOPLE_SEARCH,
                                Exposure.source_name == result["site_name"],
                            )
                        ).scalar_one_or_none()

                        if not existing:
                            # Create new exposure record
                            notes = result.get("notes") or ""
                            if result.get("opt_out_url"):
                                notes += f" Opt-out: {result['opt_out_url']}"

                            data_exposed = notes.strip() if notes.strip() else "Name, address, phone (verify manually)"

                            exposure = Exposure(
                                family_member_id=member.id,
                                source=ExposureSource.PEOPLE_SEARCH,
                                source_name=result["site_name"],
                                source_url=result["search_url"],
                                data_exposed=data_exposed,
                                status=ExposureStatus.DETECTED,
                            )
                            db.add(exposure)
                            total_new_exposures += 1
                            member_new_exposures.append({
                                "source_name": result["site_name"],
                                "source_url": result["search_url"],
                                "data_exposed": data_exposed,
                            })

            db.commit()

            # Send alert if new exposures found for this member
            if member_new_exposures:
                try:
                    send_new_exposures_alert(member_new_exposures, member.name, "data broker")
                except Exception:
                    pass  # Don't fail scan if notification fails

        # Update scan record
        if scan_id:
            scan = db.get(Scan, scan_id)
            if scan:
                scan.status = ScanStatus.COMPLETED
                scan.exposures_found = (scan.exposures_found or 0) + total_new_exposures
                scan.completed_at = datetime.utcnow()
                db.commit()

        # Send scan completion alert
        if total_new_exposures > 0:
            try:
                send_scan_complete_alert(
                    scan_type="data broker",
                    total_members=len(members),
                    new_exposures=total_new_exposures,
                )
            except Exception:
                pass  # Don't fail if notification fails

        return {
            "status": "completed",
            "new_exposures": total_new_exposures,
            "members_scanned": len(members),
        }


@celery_app.task
def run_full_scan(family_member_ids: list[int] | None = None):
    """Run a full scan for data exposures (breaches + data brokers)."""
    with get_sync_db() as db:
        # Create scan record
        scan = Scan(
            scan_type=ScanType.FULL,
            status=ScanStatus.PENDING,
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)
        scan_id = scan.id

    # Run both scans
    breach_result = run_breach_scan.delay(family_member_ids, scan_id)
    broker_result = run_data_broker_scan.delay(family_member_ids, scan_id)

    return {
        "scan_id": scan_id,
        "breach_task_id": breach_result.id,
        "broker_task_id": broker_result.id,
    }


@celery_app.task
def sync_incogni_status():
    """Sync removal request status from Incogni."""
    # TODO: Implement when Incogni integration is added
    pass


# Scheduled task wrappers for Celery Beat
@celery_app.task
def scheduled_full_scan():
    """Scheduled full scan - runs daily via Celery Beat."""
    with get_sync_db() as db:
        # Create scan record
        scan = Scan(
            scan_type=ScanType.FULL,
            status=ScanStatus.PENDING,
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)
        scan_id = scan.id

    # Run both scans
    run_breach_scan.delay(None, scan_id)
    run_data_broker_scan.delay(None, scan_id)

    return {"scan_id": scan_id, "scheduled": True}


@celery_app.task
def scheduled_breach_scan():
    """Scheduled breach scan - runs every 6 hours via Celery Beat."""
    with get_sync_db() as db:
        # Create scan record
        scan = Scan(
            scan_type=ScanType.BREACH,
            status=ScanStatus.PENDING,
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)
        scan_id = scan.id

    # Run breach scan only
    run_breach_scan.delay(None, scan_id)

    return {"scan_id": scan_id, "scheduled": True}
