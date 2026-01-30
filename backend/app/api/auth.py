"""OAuth authentication endpoints."""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy import select

from app.core.database import async_session_maker
from app.models.oauth_token import OAuthToken
from app.services.microsoft_oauth import (
    get_authorization_url,
    exchange_code_for_tokens,
    get_user_profile,
    calculate_expiry,
    MicrosoftOAuthError,
)
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


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

        return {
            "microsoft": microsoft_status,
            "smtp_configured": all([
                settings.smtp_host,
                settings.smtp_user,
                settings.smtp_password,
            ]),
        }


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
