from app.tasks import celery_app


@celery_app.task
def run_full_scan(family_member_ids: list[int] | None = None):
    """Run a full scan for data exposures."""
    # TODO: Implement
    # 1. Check HIBP for breaches
    # 2. Check data broker sites
    # 3. Store new exposures
    # 4. Update scan status
    pass


@celery_app.task
def run_breach_scan(family_member_ids: list[int] | None = None):
    """Scan Have I Been Pwned for breaches."""
    # TODO: Implement
    pass


@celery_app.task
def sync_incogni_status():
    """Sync removal request status from Incogni."""
    # TODO: Implement
    pass
