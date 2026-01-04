#!/usr/bin/env python3
"""
Guest Tracker processor for neXco Chapter Dashboard.
Parses and processes Guest Tracker data.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

import date_utils
import meeting_calendar


@dataclass
class GuestTrackerRecord:
    """A single Guest Tracker record."""
    email: Optional[str]
    first_name: str
    last_name: str
    meeting_date: date
    company: str
    referring_member: str
    following_up: str  # Raw comma-separated string
    notes: str
    profession: str
    has_email: bool = field(init=False)

    def __post_init__(self):
        self.has_email = bool(self.email and self.email.strip())


def parse_guest_tracker(rows: list) -> list:
    """
    Parse raw CSV rows into GuestTrackerRecord objects.

    Args:
        rows: List of dicts from sheets_fetcher

    Returns:
        List of GuestTrackerRecord objects
    """
    records = []

    for row in rows:
        # Get date (required)
        date_str = row.get("Chapter meeting date", "").strip()
        if not date_str:
            continue

        try:
            raw_date = date_utils.parse_meeting_date(date_str)
            # Snap to actual meeting date (2nd or 4th Wednesday)
            meeting_date = meeting_calendar.snap_to_meeting_date(raw_date)
        except ValueError:
            continue

        # Email can be blank
        email = row.get("Email", "").strip() or None

        record = GuestTrackerRecord(
            email=email,
            first_name=row.get("First Name", "").strip(),
            last_name=row.get("Last Name", "").strip(),
            meeting_date=meeting_date,
            company=row.get("Company", "").strip(),
            referring_member=row.get("Name of Referring Member", "").strip(),
            following_up=row.get("Who's Following Up", "").strip(),
            notes=row.get("Notes", "").strip(),
            profession=row.get("Profession", "").strip()
        )
        records.append(record)

    return records


def filter_historical(records: list) -> list:
    """
    Filter to only historical meetings.

    Args:
        records: List of GuestTrackerRecord objects

    Returns:
        Filtered list with only past meetings
    """
    return [r for r in records if date_utils.is_historical(r.meeting_date)]


def build_lookup(records: list) -> dict:
    """
    Build a lookup dictionary for merging with RSVP data.
    Only includes records with email addresses.

    Args:
        records: List of GuestTrackerRecord objects

    Returns:
        Dict keyed by (email.casefold(), meeting_date)
    """
    lookup = {}
    for record in records:
        if record.has_email:
            key = (record.email.casefold(), record.meeting_date)
            lookup[key] = record
    return lookup


if __name__ == "__main__":
    # Quick test with sample data
    sample_rows = [
        {
            "First Name": "John",
            "Last Name": "Doe",
            "Email": "john@example.com",
            "Chapter meeting date": "1/10/2024",
            "Company": "Acme Inc",
            "Name of Referring Member": "Jane Smith",
            "Who's Following Up": "Dan, Adam",
            "Notes": "Great conversation",
            "Profession": "Engineer"
        }
    ]
    records = parse_guest_tracker(sample_rows)
    print(f"Parsed {len(records)} records")
    if records:
        print(f"First record: {records[0]}")
