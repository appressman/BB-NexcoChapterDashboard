#!/usr/bin/env python3
"""
Data merger for neXco Chapter Dashboard.
Merges RSVP and Guest Tracker data.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List

import date_utils
from rsvp_processor import RSVPRecord
from guest_tracker_processor import GuestTrackerRecord


@dataclass
class MergedGuest:
    """A merged guest record combining RSVP and Guest Tracker data."""
    name: str  # "First Last"
    email: str
    company: str
    referring_member: str
    following_up: str
    meeting_date: date
    display_date: str
    notes: str
    source: str  # "rsvp", "guest_tracker_only"
    attended: Optional[bool]  # None for guest_tracker_only
    flags: List[str] = field(default_factory=list)


def merge_data(rsvps: list, guest_tracker: list) -> dict:
    """
    Merge RSVP and Guest Tracker data.

    Args:
        rsvps: List of RSVPRecord objects (already deduped and filtered)
        guest_tracker: List of GuestTrackerRecord objects (already filtered)

    Returns:
        Dict with keys: "attended", "no_show", "without_rsvp"
    """
    from guest_tracker_processor import build_lookup

    # Build GT lookup
    gt_lookup = build_lookup(guest_tracker)
    gt_matched_keys = set()

    attended = []
    no_show = []

    # Process RSVPs
    for rsvp in rsvps:
        key = (rsvp.email.casefold(), rsvp.meeting_date)
        gt_record = gt_lookup.get(key)

        if gt_record:
            gt_matched_keys.add(key)
            merged = MergedGuest(
                name=f"{rsvp.first_name} {rsvp.last_name}".strip(),
                email=rsvp.email,
                company=gt_record.company or rsvp.company,
                referring_member=gt_record.referring_member or rsvp.referring_member,
                following_up=gt_record.following_up,
                meeting_date=rsvp.meeting_date,
                display_date=date_utils.format_display_date(rsvp.meeting_date),
                notes=gt_record.notes,
                source="rsvp",
                attended=rsvp.attended,
                flags=[]
            )
        else:
            # No GT match - use RSVP data only
            merged = MergedGuest(
                name=f"{rsvp.first_name} {rsvp.last_name}".strip(),
                email=rsvp.email,
                company=rsvp.company,
                referring_member=rsvp.referring_member,
                following_up="",
                meeting_date=rsvp.meeting_date,
                display_date=date_utils.format_display_date(rsvp.meeting_date),
                notes="",
                source="rsvp",
                attended=rsvp.attended,
                flags=["missing_guest_tracker"]
            )

        if merged.attended:
            attended.append(merged)
        else:
            no_show.append(merged)

    # Process GT records without matching RSVPs
    without_rsvp = []
    for gt_record in guest_tracker:
        if not gt_record.has_email:
            # No email - can't match, always goes to without_rsvp
            merged = MergedGuest(
                name=f"{gt_record.first_name} {gt_record.last_name}".strip(),
                email="",
                company=gt_record.company,
                referring_member=gt_record.referring_member,
                following_up=gt_record.following_up,
                meeting_date=gt_record.meeting_date,
                display_date=date_utils.format_display_date(gt_record.meeting_date),
                notes=gt_record.notes,
                source="guest_tracker_only",
                attended=None,
                flags=[]
            )
            without_rsvp.append(merged)
        else:
            key = (gt_record.email.casefold(), gt_record.meeting_date)
            if key not in gt_matched_keys:
                # GT record with email but no RSVP
                merged = MergedGuest(
                    name=f"{gt_record.first_name} {gt_record.last_name}".strip(),
                    email=gt_record.email,
                    company=gt_record.company,
                    referring_member=gt_record.referring_member,
                    following_up=gt_record.following_up,
                    meeting_date=gt_record.meeting_date,
                    display_date=date_utils.format_display_date(gt_record.meeting_date),
                    notes=gt_record.notes,
                    source="guest_tracker_only",
                    attended=None,
                    flags=[]
                )
                without_rsvp.append(merged)

    # Sort each list: date DESC, then name ASC
    def sort_key(g):
        return (-g.meeting_date.toordinal(), g.name.lower())

    attended.sort(key=sort_key)
    no_show.sort(key=sort_key)
    without_rsvp.sort(key=sort_key)

    return {
        "attended": attended,
        "no_show": no_show,
        "without_rsvp": without_rsvp
    }


if __name__ == "__main__":
    print("Data merger module loaded successfully")
