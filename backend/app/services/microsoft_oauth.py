"""Microsoft OAuth service for Outlook email integration."""

import httpx
from datetime import datetime, timedelta
from urllib.parse import urlencode
from typing import Any

from app.core.config import settings


class MicrosoftOAuthError(Exception):
    """Error with Microsoft OAuth flow."""
    pass


# Microsoft OAuth endpoints
AUTHORITY = "https://login.microsoftonline.com/common"
AUTHORIZE_URL = f"{AUTHORITY}/oauth2/v2.0/authorize"
TOKEN_URL = f"{AUTHORITY}/oauth2/v2.0/token"
GRAPH_API_URL = "https://graph.microsoft.com/v1.0"

# Scopes needed for sending email
SCOPES = [
    "offline_access",  # For refresh token
    "User.Read",  # Get user profile/email
    "Mail.Send",  # Send email
]


def get_authorization_url(state: str | None = None) -> str:
    """
    Generate the Microsoft OAuth authorization URL.

    Args:
        state: Optional state parameter for CSRF protection

    Returns:
        The authorization URL to redirect the user to
    """
    if not settings.microsoft_client_id:
        raise MicrosoftOAuthError("Microsoft OAuth not configured: missing client_id")

    params = {
        "client_id": settings.microsoft_client_id,
        "response_type": "code",
        "redirect_uri": settings.microsoft_redirect_uri,
        "scope": " ".join(SCOPES),
        "response_mode": "query",
    }

    if state:
        params["state"] = state

    return f"{AUTHORIZE_URL}?{urlencode(params)}"


async def exchange_code_for_tokens(code: str) -> dict[str, Any]:
    """
    Exchange authorization code for access and refresh tokens.

    Args:
        code: The authorization code from Microsoft

    Returns:
        Token response with access_token, refresh_token, expires_in, etc.
    """
    if not settings.microsoft_client_id or not settings.microsoft_client_secret:
        raise MicrosoftOAuthError("Microsoft OAuth not configured")

    data = {
        "client_id": settings.microsoft_client_id,
        "client_secret": settings.microsoft_client_secret,
        "code": code,
        "redirect_uri": settings.microsoft_redirect_uri,
        "grant_type": "authorization_code",
        "scope": " ".join(SCOPES),
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(TOKEN_URL, data=data)

        if response.status_code != 200:
            error_data = response.json()
            raise MicrosoftOAuthError(
                f"Token exchange failed: {error_data.get('error_description', error_data.get('error', 'Unknown error'))}"
            )

        return response.json()


async def refresh_access_token(refresh_token: str) -> dict[str, Any]:
    """
    Refresh an expired access token.

    Args:
        refresh_token: The refresh token

    Returns:
        New token response with fresh access_token
    """
    if not settings.microsoft_client_id or not settings.microsoft_client_secret:
        raise MicrosoftOAuthError("Microsoft OAuth not configured")

    data = {
        "client_id": settings.microsoft_client_id,
        "client_secret": settings.microsoft_client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
        "scope": " ".join(SCOPES),
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(TOKEN_URL, data=data)

        if response.status_code != 200:
            error_data = response.json()
            raise MicrosoftOAuthError(
                f"Token refresh failed: {error_data.get('error_description', error_data.get('error', 'Unknown error'))}"
            )

        return response.json()


async def get_user_profile(access_token: str) -> dict[str, Any]:
    """
    Get the user's profile from Microsoft Graph.

    Args:
        access_token: Valid access token

    Returns:
        User profile including email address
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GRAPH_API_URL}/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if response.status_code != 200:
            raise MicrosoftOAuthError(f"Failed to get user profile: {response.status_code}")

        return response.json()


async def send_email(
    access_token: str,
    to_email: str,
    subject: str,
    body_text: str,
    body_html: str | None = None,
) -> bool:
    """
    Send an email via Microsoft Graph API.

    Args:
        access_token: Valid access token with Mail.Send scope
        to_email: Recipient email address
        subject: Email subject
        body_text: Plain text body
        body_html: Optional HTML body

    Returns:
        True if sent successfully
    """
    # Build email message
    message = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML" if body_html else "Text",
                "content": body_html if body_html else body_text,
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": to_email,
                    }
                }
            ],
        },
        "saveToSentItems": "true",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{GRAPH_API_URL}/me/sendMail",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json=message,
        )

        if response.status_code == 202:
            return True

        error_msg = response.text
        try:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", error_msg)
        except Exception:
            pass

        raise MicrosoftOAuthError(f"Failed to send email: {error_msg}")


def calculate_expiry(expires_in: int) -> datetime:
    """Calculate token expiry datetime from expires_in seconds."""
    return datetime.utcnow() + timedelta(seconds=expires_in - 60)  # 60s buffer
