"""OAuth authentication and email settings endpoints."""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy import select

from app.core.database import async_session_maker
from app.models.oauth_token import OAuthToken
from app.models.app_settings import AppSettings
from app.services.microsoft_oauth import (
    get_authorization_url,
    exchange_code_for_tokens,
    get_user_profile,
    calculate_expiry,
    MicrosoftOAuthError,
)
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


class SmtpSettings(BaseModel):
    """SMTP configuration for email notifications."""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str  # Gmail address
    smtp_password: str  # App password
    notification_email: str  # Where to send alerts


async def get_setting(db, key: str) -> str | None:
    """Get a setting value from database."""
    result = await db.execute(
        select(AppSettings).where(AppSettings.key == key)
    )
    setting = result.scalar_one_or_none()
    return setting.value if setting else None


async def set_setting(db, key: str, value: str) -> None:
    """Set a setting value in database."""
    result = await db.execute(
        select(AppSettings).where(AppSettings.key == key)
    )
    setting = result.scalar_one_or_none()
    if setting:
        setting.value = value
    else:
        setting = AppSettings(key=key, value=value)
        db.add(setting)


@router.get("/microsoft/connect")
async def microsoft_connect():
    """
    Initiate Microsoft OAuth flow.

    Redirects to Microsoft login page.
    """
    try:
        auth_url = get_authorization_url()
        return RedirectResponse(url=auth_url)
    except MicrosoftOAuthError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/microsoft/callback")
async def microsoft_callback(
    code: str | None = Query(None),
    error: str | None = Query(None),
    error_description: str | None = Query(None),
):
    """
    Handle Microsoft OAuth callback.

    Exchanges code for tokens and stores them.
    """
    # Handle error from Microsoft
    if error:
        # Redirect to frontend with error
        error_msg = error_description or error
        return RedirectResponse(
            url=f"http://localhost:3000/settings?error={error_msg}"
        )

    if not code:
        return RedirectResponse(
            url="http://localhost:3000/settings?error=No authorization code received"
        )

    try:
        # Exchange code for tokens
        token_data = await exchange_code_for_tokens(code)

        # Get user profile to get email
        access_token = token_data["access_token"]
        profile = await get_user_profile(access_token)
        email = profile.get("mail") or profile.get("userPrincipalName")

        # Store tokens in database
        async with async_session_maker() as db:
            # Delete any existing Microsoft tokens
            existing = await db.execute(
                select(OAuthToken).where(OAuthToken.provider == "microsoft")
            )
            for token in existing.scalars().all():
                await db.delete(token)

            # Create new token record
            oauth_token = OAuthToken(
                provider="microsoft",
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                token_type=token_data.get("token_type", "Bearer"),
                expires_at=calculate_expiry(token_data.get("expires_in", 3600)),
                scope=token_data.get("scope"),
                email=email,
            )
            db.add(oauth_token)
            await db.commit()

        # Redirect to frontend with success
        return RedirectResponse(
            url=f"http://localhost:3000/settings?connected=microsoft&email={email}"
        )

    except MicrosoftOAuthError as e:
        return RedirectResponse(
            url=f"http://localhost:3000/settings?error={str(e)}"
        )
    except Exception as e:
        return RedirectResponse(
            url=f"http://localhost:3000/settings?error=Failed to connect: {str(e)}"
        )


@router.get("/status")
async def auth_status():
    """
    Get current OAuth connection status.

    Returns info about connected email providers.
    """
    async with async_session_maker() as db:
        result = await db.execute(
            select(OAuthToken).where(OAuthToken.provider == "microsoft")
        )
        microsoft_token = result.scalar_one_or_none()

        microsoft_status = None
        if microsoft_token:
            microsoft_status = {
                "connected": True,
                "email": microsoft_token.email,
                "expires_at": microsoft_token.expires_at.isoformat() if microsoft_token.expires_at else None,
            }

        # Check for SMTP settings in database
        smtp_user = await get_setting(db, "smtp_user")
        smtp_password = await get_setting(db, "smtp_password")
        notification_email = await get_setting(db, "notification_email")

        smtp_configured = bool(smtp_user and smtp_password)

        return {
            "microsoft": microsoft_status,
            "smtp_configured": smtp_configured,
            "smtp_email": smtp_user if smtp_configured else None,
            "notification_email": notification_email if smtp_configured else None,
        }


@router.post("/smtp/configure")
async def configure_smtp(smtp_settings: SmtpSettings):
    """
    Configure SMTP settings for email notifications.

    For Gmail, use an App Password (not your regular password).
    """
    async with async_session_maker() as db:
        await set_setting(db, "smtp_host", smtp_settings.smtp_host)
        await set_setting(db, "smtp_port", str(smtp_settings.smtp_port))
        await set_setting(db, "smtp_user", smtp_settings.smtp_user)
        await set_setting(db, "smtp_password", smtp_settings.smtp_password)
        await set_setting(db, "notification_email", smtp_settings.notification_email)
        await db.commit()

    return {
        "status": "configured",
        "smtp_email": smtp_settings.smtp_user,
        "notification_email": smtp_settings.notification_email,
    }


@router.post("/smtp/test")
async def test_smtp():
    """Send a test email to verify SMTP configuration."""
    from app.services.notifications import send_email, NotificationError

    try:
        result = send_email(
            subject="[Fibertap] Test Email",
            body_text="This is a test email from Fibertap. If you received this, your email notifications are working!",
            body_html="""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Fibertap Test Email</h2>
                <p>If you received this, your email notifications are working!</p>
            </body>
            </html>
            """,
        )
        if result:
            return {"status": "success", "message": "Test email sent!"}
        else:
            return {"status": "not_configured", "message": "Email is not configured"}
    except NotificationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/smtp/disconnect")
async def disconnect_smtp():
    """Remove SMTP configuration."""
    async with async_session_maker() as db:
        for key in ["smtp_host", "smtp_port", "smtp_user", "smtp_password", "notification_email"]:
            result = await db.execute(
                select(AppSettings).where(AppSettings.key == key)
            )
            setting = result.scalar_one_or_none()
            if setting:
                await db.delete(setting)
        await db.commit()

    return {"status": "disconnected"}


@router.delete("/microsoft/disconnect")
async def microsoft_disconnect():
    """
    Disconnect Microsoft OAuth.

    Removes stored tokens.
    """
    async with async_session_maker() as db:
        result = await db.execute(
            select(OAuthToken).where(OAuthToken.provider == "microsoft")
        )
        for token in result.scalars().all():
            await db.delete(token)
        await db.commit()

    return {"status": "disconnected"}
