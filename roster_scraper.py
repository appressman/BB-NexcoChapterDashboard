#!/usr/bin/env python3
"""
Roster page scraper for neXco Chapter Dashboard.
Scrapes member names from neXco chapter pages for name normalization.
"""

import re
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class ScrapeError(Exception):
    """Raised when roster scraping fails."""

    def __init__(self, url: str, message: str):
        self.url = url
        self.message = message
        super().__init__(message)


def scrape_roster(roster_url: str, timeout: int = 30) -> list:
    """
    Scrape member names from a neXco chapter roster page.

    Args:
        roster_url: URL of the chapter roster page
        timeout: Request timeout in seconds

    Returns:
        List of full names, sorted alphabetically

    Raises:
        ScrapeError: On fetch or parse failure
    """
    request = Request(roster_url, headers={"User-Agent": "NexcoDashboard/1.0"})

    try:
        with urlopen(request, timeout=timeout) as response:
            html = response.read().decode("utf-8")
    except HTTPError as e:
        raise ScrapeError(
            url=roster_url,
            message=f"HTTP {e.code} fetching roster: {e.reason}"
        )
    except URLError as e:
        raise ScrapeError(
            url=roster_url,
            message=f"Network error fetching roster: {e.reason}"
        )
    except TimeoutError:
        raise ScrapeError(
            url=roster_url,
            message=f"Timeout fetching roster after {timeout}s"
        )

    # Extract names from HTML
    names = set()

    # Pattern 1: Names in h4 tags
    h4_pattern = r"<h4[^>]*>([^<]+)</h4>"
    for match in re.finditer(h4_pattern, html, re.IGNORECASE):
        name = match.group(1).strip()
        if name and looks_like_name(name):
            names.add(normalize_scraped_name(name))

    # Pattern 2: Names in specific class divs
    class_patterns = [
        r'class="member-name"[^>]*>([^<]+)<',
        r'class="name"[^>]*>([^<]+)<',
        r'class="team-member-name"[^>]*>([^<]+)<',
    ]
    for pattern in class_patterns:
        for match in re.finditer(pattern, html, re.IGNORECASE):
            name = match.group(1).strip()
            if name and looks_like_name(name):
                names.add(normalize_scraped_name(name))

    # Pattern 2b: AccessAlly directory format - names in <strong> inside directory items
    # e.g., <div class="accessally-user-directory-description-item..."><strong>Name Here</strong></div>
    accessally_pattern = r'class="accessally-user-directory-description-item[^"]*"[^>]*>\s*<strong>([^<]+)</strong>'
    for match in re.finditer(accessally_pattern, html, re.IGNORECASE):
        name = match.group(1).strip()
        if name and looks_like_name(name):
            names.add(normalize_scraped_name(name))

    # Pattern 3: Look for capitalized name patterns in link text
    link_pattern = r'<a[^>]+>([A-Z][a-z]+ [A-Z][a-z]+[^<]*)</a>'
    for match in re.finditer(link_pattern, html):
        name = match.group(1).strip()
        if looks_like_name(name):
            names.add(normalize_scraped_name(name))

    return sorted(names)


def looks_like_name(text: str) -> bool:
    """Check if text looks like a person name."""
    parts = text.split()
    if len(parts) < 2:
        return False
    if len(parts) > 5:
        return False

    non_name_patterns = [r"\d", r"@", r"http", r"\.com", r"click", r"here", r"read more", r"calendar", r"event"]
    for pattern in non_name_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False

    return True


def normalize_scraped_name(name: str) -> str:
    """Normalize a scraped name."""
    name = " ".join(name.split())
    return name


def build_roster_lookup(names: list) -> dict:
    """
    Build a lookup dictionary for name matching.

    Returns:
        Dict mapping casefolded names to canonical names.
    """
    lookup = {}
    first_name_counts = {}

    for name in names:
        first = name.split()[0].casefold() if name.split() else ""
        first_name_counts[first] = first_name_counts.get(first, 0) + 1

    for name in names:
        lookup[name.casefold()] = name
        parts = name.split()
        if parts:
            first = parts[0].casefold()
            if first_name_counts.get(first, 0) == 1:
                lookup[first] = name

    return lookup


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
        names = scrape_roster(url)
        print(f"Found {len(names)} names:")
        for name in names[:10]:
            print(f"  - {name}")
