"""Data broker and people-search site scanner."""

from urllib.parse import quote_plus
from dataclasses import dataclass


@dataclass
class DataBrokerSite:
    """Known data broker / people-search site."""
    name: str
    domain: str
    search_url_template: str  # Use {first}, {last}, {city}, {state} placeholders
    opt_out_url: str | None = None
    notes: str | None = None


# List of known data broker and people-search sites
DATA_BROKER_SITES: list[DataBrokerSite] = [
    DataBrokerSite(
        name="Spokeo",
        domain="spokeo.com",
        search_url_template="https://www.spokeo.com/{first}-{last}",
        opt_out_url="https://www.spokeo.com/optout",
        notes="Major people-search site. Requires email verification for opt-out.",
    ),
    DataBrokerSite(
        name="BeenVerified",
        domain="beenverified.com",
        search_url_template="https://www.beenverified.com/people/{first}-{last}/",
        opt_out_url="https://www.beenverified.com/app/optout/search",
        notes="Requires account creation for opt-out.",
    ),
    DataBrokerSite(
        name="Whitepages",
        domain="whitepages.com",
        search_url_template="https://www.whitepages.com/name/{first}-{last}/{state}",
        opt_out_url="https://www.whitepages.com/suppression-requests",
        notes="One of the largest people-search sites.",
    ),
    DataBrokerSite(
        name="TruePeopleSearch",
        domain="truepeoplesearch.com",
        search_url_template="https://www.truepeoplesearch.com/results?name={first}%20{last}",
        opt_out_url="https://www.truepeoplesearch.com/removal",
        notes="Free people search. Relatively easy opt-out.",
    ),
    DataBrokerSite(
        name="FastPeopleSearch",
        domain="fastpeoplesearch.com",
        search_url_template="https://www.fastpeoplesearch.com/name/{first}-{last}",
        opt_out_url="https://www.fastpeoplesearch.com/removal",
        notes="Free people search with opt-out form.",
    ),
    DataBrokerSite(
        name="That's Them",
        domain="thatsthem.com",
        search_url_template="https://thatsthem.com/name/{first}-{last}",
        opt_out_url="https://thatsthem.com/optout",
        notes="Aggregates data from multiple sources.",
    ),
    DataBrokerSite(
        name="Intelius",
        domain="intelius.com",
        search_url_template="https://www.intelius.com/people-search/{first}-{last}/",
        opt_out_url="https://www.intelius.com/opt-out",
        notes="Paid service but still lists people publicly.",
    ),
    DataBrokerSite(
        name="US Search",
        domain="ussearch.com",
        search_url_template="https://www.ussearch.com/search/results?firstName={first}&lastName={last}",
        opt_out_url="https://www.ussearch.com/opt-out/submit/",
    ),
    DataBrokerSite(
        name="PeopleFinder",
        domain="peoplefinder.com",
        search_url_template="https://www.peoplefinder.com/results?firstName={first}&lastName={last}",
        opt_out_url="https://www.peoplefinder.com/optout.php",
    ),
    DataBrokerSite(
        name="Radaris",
        domain="radaris.com",
        search_url_template="https://radaris.com/p/{first}/{last}/",
        opt_out_url="https://radaris.com/control/privacy",
        notes="Requires account to opt-out.",
    ),
    DataBrokerSite(
        name="MyLife",
        domain="mylife.com",
        search_url_template="https://www.mylife.com/search?firstName={first}&lastName={last}",
        opt_out_url="https://www.mylife.com/ccpa/index.pubview",
        notes="Known for reputation scores. CCPA request for removal.",
    ),
    DataBrokerSite(
        name="PeopleLooker",
        domain="peoplelooker.com",
        search_url_template="https://www.peoplelooker.com/people-search/{first}-{last}",
        opt_out_url="https://www.peoplelooker.com/f/optout/search",
    ),
    DataBrokerSite(
        name="Instant Checkmate",
        domain="instantcheckmate.com",
        search_url_template="https://www.instantcheckmate.com/people/{first}-{last}/",
        opt_out_url="https://www.instantcheckmate.com/opt-out/",
    ),
    DataBrokerSite(
        name="Nuwber",
        domain="nuwber.com",
        search_url_template="https://nuwber.com/search?name={first}%20{last}",
        opt_out_url="https://nuwber.com/removal/link",
    ),
    DataBrokerSite(
        name="Clustrmaps",
        domain="clustrmaps.com",
        search_url_template="https://clustrmaps.com/persons/{first}-{last}",
        opt_out_url="https://clustrmaps.com/bl/opt-out",
    ),
    DataBrokerSite(
        name="CyberBackgroundChecks",
        domain="cyberbackgroundchecks.com",
        search_url_template="https://www.cyberbackgroundchecks.com/people/{first}-{last}",
        opt_out_url="https://www.cyberbackgroundchecks.com/removal",
    ),
    DataBrokerSite(
        name="Addresses.com",
        domain="addresses.com",
        search_url_template="https://www.addresses.com/people/{first}+{last}",
        opt_out_url="https://www.addresses.com/optout.php",
    ),
    DataBrokerSite(
        name="Advanced Background Checks",
        domain="advancedbackgroundchecks.com",
        search_url_template="https://www.advancedbackgroundchecks.com/names/{first}-{last}",
        opt_out_url="https://www.advancedbackgroundchecks.com/removal",
    ),
    DataBrokerSite(
        name="Public Records Now",
        domain="publicrecordsnow.com",
        search_url_template="https://www.publicrecordsnow.com/name/{first}+{last}",
        opt_out_url=None,
        notes="May require direct contact for removal.",
    ),
]


def generate_search_urls(
    first_name: str,
    last_name: str,
    city: str | None = None,
    state: str | None = None,
) -> list[dict]:
    """
    Generate search URLs for all known data broker sites.

    Returns a list of dicts with site info and search URL.
    """
    results = []

    # Clean and format names
    first = quote_plus(first_name.strip().lower())
    last = quote_plus(last_name.strip().lower())
    city_clean = quote_plus(city.strip().lower()) if city else ""
    state_clean = quote_plus(state.strip().upper()[:2]) if state else ""

    for site in DATA_BROKER_SITES:
        try:
            # Generate search URL with available data
            url = site.search_url_template.format(
                first=first,
                last=last,
                city=city_clean,
                state=state_clean,
            )

            results.append({
                "site_name": site.name,
                "domain": site.domain,
                "search_url": url,
                "opt_out_url": site.opt_out_url,
                "notes": site.notes,
            })
        except KeyError:
            # Template requires fields we don't have, skip or use simpler URL
            # Try without city/state
            try:
                url = site.search_url_template.format(
                    first=first,
                    last=last,
                    city="",
                    state="",
                )
                results.append({
                    "site_name": site.name,
                    "domain": site.domain,
                    "search_url": url,
                    "opt_out_url": site.opt_out_url,
                    "notes": site.notes,
                })
            except KeyError:
                continue

    return results


def parse_address_for_location(address: str | None) -> tuple[str | None, str | None]:
    """
    Try to extract city and state from an address string.

    Returns (city, state) tuple.
    """
    if not address:
        return None, None

    # Simple parsing - look for common patterns
    # "123 Main St, City, ST 12345" or "City, ST"
    parts = [p.strip() for p in address.split(",")]

    if len(parts) >= 2:
        # Last part might be "ST 12345" or just "ST"
        last_part = parts[-1].strip()
        state_zip = last_part.split()

        if state_zip:
            state = state_zip[0][:2].upper() if len(state_zip[0]) == 2 else None
        else:
            state = None

        # Second to last is usually city
        city = parts[-2].strip() if len(parts) >= 2 else None

        return city, state

    return None, None
