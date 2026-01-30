"""Have I Been Pwned API integration for breach detection."""

import httpx
from typing import Any

from app.core.config import settings


HIBP_API_BASE = "https://haveibeenpwned.com/api/v3"
HIBP_USER_AGENT = "Fibertap-Privacy-Monitor"


class HIBPError(Exception):
    """Error from HIBP API."""
    pass


class HIBPRateLimited(HIBPError):
    """Rate limited by HIBP API."""
    pass


class HIBPUnauthorized(HIBPError):
    """Invalid or missing API key."""
    pass


async def check_email_breaches(email: str) -> list[dict[str, Any]]:
    """
    Check if an email address appears in any known data breaches.

    Requires a HIBP API key (https://haveibeenpwned.com/API/Key).

    Returns a list of breach records, each containing:
    - Name: breach name (e.g., "LinkedIn")
    - Title: display title
    - Domain: affected domain
    - BreachDate: when the breach occurred
    - DataClasses: list of data types exposed (e.g., ["Email addresses", "Passwords"])
    - Description: HTML description of the breach
    """
    if not settings.hibp_api_key:
        raise HIBPError("HIBP API key not configured. Set HIBP_API_KEY environment variable.")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{HIBP_API_BASE}/breachedaccount/{email}",
            params={"truncateResponse": "false"},
            headers={
                "hibp-api-key": settings.hibp_api_key,
                "user-agent": HIBP_USER_AGENT,
            },
            timeout=30.0,
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            # No breaches found - this is good!
            return []
        elif response.status_code == 401:
            raise HIBPUnauthorized("Invalid HIBP API key")
        elif response.status_code == 429:
            raise HIBPRateLimited("HIBP rate limit exceeded. Wait before retrying.")
        else:
            raise HIBPError(f"HIBP API error: {response.status_code} - {response.text}")


async def get_breach_info(breach_name: str) -> dict[str, Any] | None:
    """Get detailed information about a specific breach."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{HIBP_API_BASE}/breach/{breach_name}",
            headers={"user-agent": HIBP_USER_AGENT},
            timeout=30.0,
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            raise HIBPError(f"HIBP API error: {response.status_code}")


def format_breach_for_exposure(breach: dict[str, Any], email: str) -> dict[str, Any]:
    """Format HIBP breach data for storage as an Exposure."""
    data_classes = breach.get("DataClasses", [])

    return {
        "source": "BREACH",
        "source_name": breach.get("Title", breach.get("Name", "Unknown Breach")),
        "source_url": f"https://haveibeenpwned.com/PwnedWebsites#{breach.get('Name', '')}",
        "data_exposed": ", ".join(data_classes) if data_classes else "Unknown data",
        "breach_date": breach.get("BreachDate"),
        "breach_description": breach.get("Description", ""),
    }
