#!/usr/bin/env python3
"""
Date utilities for neXco Chapter Dashboard.
Handles date parsing, formatting, and validation.
"""

from datetime import date, datetime
from typing import Optional
import re


def parse_meeting_date(date_str: str) -> date:
    """
    Parse a meeting date string into a date object.
    Handles various formats and ensures 4-digit year (Y2K fix).

    Supported formats:
    - "1/10/2024" (M/D/YYYY)
    - "01/10/2024" (MM/DD/YYYY)
    - "1/10/24" (M/D/YY) - assumes 2000s
    - "2024-01-10" (ISO format)
    - "Jan 10, 2024" (display format)

    Args:
        date_str: Date string to parse

    Returns:
        date object

    Raises:
        ValueError: If date cannot be parsed
    """
    date_str = date_str.strip()

    if not date_str:
        raise ValueError("Empty date string")

    # Try ISO format first (YYYY-MM-DD)
    iso_match = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})$', date_str)
    if iso_match:
        year, month, day = map(int, iso_match.groups())
        return date(year, month, day)

    # Try M/D/YYYY or M/D/YY format
    slash_match = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{2,4})$', date_str)
    if slash_match:
        month, day, year = map(int, slash_match.groups())
        # Fix 2-digit year (Y2K handling)
        if year < 100:
            # Assume 2000s for 2-digit years (00-99 -> 2000-2099)
            year += 2000
        return date(year, month, day)

    # Try "Jan 10, 2024" format
    text_match = re.match(r'^([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})$', date_str)
    if text_match:
        month_name, day, year = text_match.groups()
        month_names = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'sept': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12
        }
        month = month_names.get(month_name.lower())
        if month:
            return date(int(year), month, int(day))

    raise ValueError(f"Cannot parse date: {date_str}")


def format_display_date(d: date) -> str:
    """
    Format a date for display.

    Args:
        d: date object

    Returns:
        String like "Aug 28, 2024"
    """
    return d.strftime("%b %d, %Y").replace(" 0", " ")


def get_month_key(d: date) -> str:
    """
    Get the month key for a date.

    Args:
        d: date object

    Returns:
        String like "2024-08"
    """
    return d.strftime("%Y-%m")


def is_historical(d: date) -> bool:
    """
    Check if a date is in the past (historical meeting).

    Args:
        d: date object

    Returns:
        True if date is before today
    """
    return d < date.today()


def get_year_range(start_year: int = 2023) -> list:
    """
    Get a list of years from start_year to current year.

    Args:
        start_year: First year to include (default 2023)

    Returns:
        List of years in descending order
    """
    current_year = date.today().year
    return list(range(current_year, start_year - 1, -1))


if __name__ == "__main__":
    # Test cases
    test_dates = [
        "1/10/2024",      # M/D/YYYY
        "01/10/2024",     # MM/DD/YYYY
        "8/28/24",        # M/D/YY (Y2K test)
        "12/10/25",       # M/D/YY (Y2K test)
        "2024-01-10",     # ISO format
        "Aug 28, 2024",   # Text format
    ]

    print("Date parsing tests:")
    for ds in test_dates:
        try:
            d = parse_meeting_date(ds)
            print(f"  '{ds}' -> {d} -> '{format_display_date(d)}' (month_key: {get_month_key(d)})")
        except ValueError as e:
            print(f"  '{ds}' -> ERROR: {e}")

    print(f"\nYear range (2023 to now): {get_year_range()}")
