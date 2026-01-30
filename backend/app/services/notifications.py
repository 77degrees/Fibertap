"""Email notification service for alerting on new exposures."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any

from app.core.config import settings


class NotificationError(Exception):
    """Error sending notification."""
    pass


def is_email_configured() -> bool:
    """Check if email notifications are configured."""
    return all([
        settings.smtp_host,
        settings.smtp_user,
        settings.smtp_password,
        settings.smtp_from_email,
        settings.notification_email,
    ])


def send_email(subject: str, body_text: str, body_html: str | None = None) -> bool:
    """
    Send an email notification.

    Returns True if sent successfully, False if not configured.
    Raises NotificationError on failure.
    """
    if not is_email_configured():
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from_email
    msg["To"] = settings.notification_email

    # Attach text version
    msg.attach(MIMEText(body_text, "plain"))

    # Attach HTML version if provided
    if body_html:
        msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(
                settings.smtp_from_email,
                settings.notification_email,
                msg.as_string(),
            )
        return True
    except Exception as e:
        raise NotificationError(f"Failed to send email: {e}")


def send_new_exposures_alert(
    exposures: list[dict[str, Any]],
    member_name: str,
    scan_type: str = "scan",
) -> bool:
    """
    Send alert about newly detected exposures.

    Args:
        exposures: List of new exposure dicts with source_name, source_url, data_exposed
        member_name: Name of the family member affected
        scan_type: Type of scan that found them
    """
    if not exposures:
        return False

    count = len(exposures)
    subject = f"[Fibertap] {count} new exposure(s) detected for {member_name}"

    # Build text body
    lines = [
        f"Fibertap detected {count} new data exposure(s) for {member_name}.",
        "",
        "New exposures:",
        "",
    ]

    for exp in exposures[:10]:  # Limit to 10 in email
        lines.append(f"- {exp.get('source_name', 'Unknown')}")
        if exp.get('source_url'):
            lines.append(f"  Link: {exp['source_url']}")
        if exp.get('data_exposed'):
            lines.append(f"  Data: {exp['data_exposed'][:100]}")
        lines.append("")

    if count > 10:
        lines.append(f"... and {count - 10} more.")
        lines.append("")

    lines.append("Log in to your Fibertap dashboard to review and request removals.")

    body_text = "\n".join(lines)

    # Build HTML body
    exposure_rows = ""
    for exp in exposures[:10]:
        url = exp.get('source_url', '')
        link = f'<a href="{url}">View</a>' if url else ''
        exposure_rows += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{exp.get('source_name', 'Unknown')}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{exp.get('data_exposed', '')[:50] if exp.get('data_exposed') else ''}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{link}</td>
        </tr>
        """

    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #dc2626;">New Data Exposures Detected</h2>
        <p>Fibertap detected <strong>{count} new data exposure(s)</strong> for <strong>{member_name}</strong>.</p>

        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <thead>
                <tr style="background: #f3f4f6;">
                    <th style="padding: 8px; text-align: left;">Source</th>
                    <th style="padding: 8px; text-align: left;">Data Exposed</th>
                    <th style="padding: 8px; text-align: left;">Link</th>
                </tr>
            </thead>
            <tbody>
                {exposure_rows}
            </tbody>
        </table>

        {f'<p><em>...and {count - 10} more exposures.</em></p>' if count > 10 else ''}

        <p style="margin-top: 20px;">
            <a href="http://localhost:3000" style="background: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                View Dashboard
            </a>
        </p>

        <hr style="margin-top: 30px; border: none; border-top: 1px solid #eee;">
        <p style="color: #666; font-size: 12px;">
            This alert was sent by Fibertap Privacy Monitor.
        </p>
    </body>
    </html>
    """

    return send_email(subject, body_text, body_html)


def send_scan_complete_alert(
    scan_type: str,
    total_members: int,
    new_exposures: int,
    errors: list[str] | None = None,
) -> bool:
    """Send alert when a scheduled scan completes."""
    subject = f"[Fibertap] {scan_type.title()} scan complete - {new_exposures} new exposures"

    status = "with errors" if errors else "successfully"
    body_text = f"""
Fibertap {scan_type} scan completed {status}.

Summary:
- Family members scanned: {total_members}
- New exposures found: {new_exposures}
"""

    if errors:
        body_text += f"\nErrors:\n" + "\n".join(f"- {e}" for e in errors[:5])

    body_text += "\n\nLog in to your dashboard to review results."

    return send_email(subject, body_text)
