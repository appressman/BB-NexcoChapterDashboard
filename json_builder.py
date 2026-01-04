#!/usr/bin/env python3
"""
JSON builder for neXco Chapter Dashboard.
Builds the data.json structure.
"""

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Optional


def get_utc_now_iso() -> str:
    """
    Get current UTC time in ISO 8601 format.

    Returns:
        String like "2026-01-03T16:02:00Z"
    """
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%SZ")


def merged_guest_to_dict(guest) -> dict:
    """Convert MergedGuest to dict with date as string."""
    d = asdict(guest)
    d["meeting_date"] = str(guest.meeting_date)
    return d


def meeting_stats_to_dict(stats) -> dict:
    """Convert MeetingStats to dict with date as string."""
    d = asdict(stats)
    d["date"] = str(stats.date)
    return d


def followup_to_dict(followup) -> dict:
    """Convert FollowUpCount to dict, including all fields."""
    d = asdict(followup)
    # Ensure is_section_header is included (default False for backwards compat)
    if 'is_section_header' not in d:
        d['is_section_header'] = False
    return d


def build_data_json(
    config,
    merged: dict,
    meetings: list,
    open_seats: list,
    followups: list,
    refresh_success: bool,
    error_message: Optional[str] = None
) -> dict:
    """
    Build the complete data.json structure.

    Args:
        config: ChapterConfig object
        merged: Dict with attended, no_show, without_rsvp lists
        meetings: List of MeetingStats
        open_seats: Raw list of dicts from sheet
        followups: List of FollowUpCount
        refresh_success: Whether refresh completed successfully
        error_message: Error message if refresh failed

    Returns:
        Complete data.json structure as dict
    """
    from aggregator import get_available_months, build_chart_data, build_rsvp_counts

    available_months = get_available_months(meetings)
    latest_month = available_months[0] if available_months else None

    # Build chart data for latest month
    chart_data = {}
    rsvp_counts = []
    if latest_month:
        chart_data = build_chart_data(meetings, latest_month)
        rsvp_counts = build_rsvp_counts(meetings, latest_month)

    now_iso = get_utc_now_iso()

    return {
        "metadata": {
            "chapter_slug": config.chapter_slug,
            "display_name": config.display_name,
            "page_title": config.page_title,
            "last_updated": now_iso if refresh_success else None,
            "last_refresh_attempt": now_iso,
            "refresh_status": "ok" if refresh_success else "error",
            "refresh_error": error_message
        },
        "available_months": available_months,
        "meetings": [meeting_stats_to_dict(m) for m in meetings],
        "chart_data": chart_data,
        "rsvp_counts": rsvp_counts,
        "open_seats": open_seats,
        "follow_up_counts": [followup_to_dict(f) for f in followups],
        "guests": {
            "attended": [merged_guest_to_dict(g) for g in merged["attended"]],
            "no_show": [merged_guest_to_dict(g) for g in merged["no_show"]],
            "without_rsvp": [merged_guest_to_dict(g) for g in merged["without_rsvp"]]
        }
    }


if __name__ == "__main__":
    print(f"Current UTC: {get_utc_now_iso()}")
