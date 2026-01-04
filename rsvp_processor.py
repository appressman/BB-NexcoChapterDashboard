#!/usr/bin/env python3
"""
RSVP processor for neXco Chapter Dashboard.
Parses, deduplicates, and filters RSVP data.
"""

from dataclasses import dataclass
from datetime import date
from typing import Tuple

import date_utils
import meeting_calendar


@dataclass
class RSVPRecord:
    """A single RSVP record."""
    email: str
    first_name: str
    last_name: str
    meeting_date: date
    attended: bool
    company: str
    referring_member: str
    profession: str
    row_index: int  # For "last row wins" deduplication


def parse_rsvps(rows: list) -> list:
    """
    Parse raw CSV rows into RSVPRecord objects.

    Args:
        rows: List of dicts from sheets_fetcher

    Returns:
        List of RSVPRecord objects
    """
    records = []

    for idx, row in enumerate(rows):
        # Get required fields
        email = row.get("Email", "").strip()
        date_str = row.get("Chapter meeting date", "").strip()

        # Skip rows without email or date
        if not email or not date_str:
            continue

        try:
            raw_date = date_utils.parse_meeting_date(date_str)
            # Snap to actual meeting date (2nd or 4th Wednesday)
            meeting_date = meeting_calendar.snap_to_meeting_date(raw_date)
        except ValueError:
            continue

        # Parse attendance
        attended_str = row.get("Did they attend?", "").strip().upper()
        attended = attended_str == "TRUE"

        record = RSVPRecord(
            email=email,
            first_name=row.get("First Name", "").strip(),
            last_name=row.get("Last Name", "").strip(),
            meeting_date=meeting_date,
            attended=attended,
            company=row.get("Company", "").strip(),
            referring_member=row.get("Name of referring member", "").strip(),
            profession=row.get("Profession", "").strip(),
            row_index=idx
        )
        records.append(record)

    return records


def dedupe_rsvps(records: list) -> list:
    """
    Deduplicate RSVPs by (email, meeting_date).
    Last row wins when duplicates exist.

    Args:
        records: List of RSVPRecord objects

    Returns:
        Deduplicated list
    """
    seen = {}

    for record in records:
        key = (record.email.casefold(), record.meeting_date)
        # Always update - last row wins
        seen[key] = record

    return list(seen.values())


def filter_historical(records: list) -> list:
    """
    Filter to only historical meetings.

    Args:
        records: List of RSVPRecord objects

    Returns:
        Filtered list with only past meetings
    """
    return [r for r in records if date_utils.is_historical(r.meeting_date)]


def split_by_attendance(records: list) -> Tuple[list, list]:
    """
    Split records by attendance status.

    Args:
        records: List of RSVPRecord objects

    Returns:
        Tuple of (attended_list, no_show_list)
    """
    attended = [r for r in records if r.attended]
    no_show = [r for r in records if not r.attended]
    return attended, no_show


if __name__ == "__main__":
    # Quick test with sample data
    sample_rows = [
        {
            "Email": "test@example.com",
            "First Name": "John",
            "Last Name": "Doe",
            "Chapter meeting date": "1/10/2024",
            "Did they attend?": "TRUE",
            "Company": "Acme Inc",
            "Name of referring member": "Jane Smith",
            "Profession": "Engineer"
        }
    ]
    records = parse_rsvps(sample_rows)
    print(f"Parsed {len(records)} records")
    if records:
        print(f"First record: {records[0]}")
