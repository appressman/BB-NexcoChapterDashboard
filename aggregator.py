#!/usr/bin/env python3
"""
Meeting aggregator for neXco Chapter Dashboard.
Aggregates meeting-level statistics.
"""

from dataclasses import dataclass
from datetime import date
from collections import defaultdict

import date_utils


@dataclass
class MeetingStats:
    """Statistics for a single meeting date."""
    date: date
    display_date: str
    month_key: str  # "YYYY-MM"
    attended_count: int
    no_show_count: int
    rsvp_count: int  # Deduplicated RSVP count


def aggregate_meetings(merged: dict, rsvps: list) -> list:
    """
    Aggregate meeting-level statistics.

    Args:
        merged: Dict with "attended", "no_show", "without_rsvp" lists
        rsvps: List of RSVPRecord objects (deduped)

    Returns:
        List of MeetingStats sorted by date DESC
    """
    # Collect all unique dates
    all_dates = set()
    for guest in merged["attended"]:
        all_dates.add(guest.meeting_date)
    for guest in merged["no_show"]:
        all_dates.add(guest.meeting_date)
    for guest in merged["without_rsvp"]:
        all_dates.add(guest.meeting_date)

    # Count attended per date (from attended + without_rsvp)
    attended_counts = defaultdict(int)
    for guest in merged["attended"]:
        attended_counts[guest.meeting_date] += 1
    for guest in merged["without_rsvp"]:
        attended_counts[guest.meeting_date] += 1

    # Count no-shows per date
    no_show_counts = defaultdict(int)
    for guest in merged["no_show"]:
        no_show_counts[guest.meeting_date] += 1

    # Count RSVPs per date
    rsvp_counts = defaultdict(int)
    for rsvp in rsvps:
        rsvp_counts[rsvp.meeting_date] += 1

    # Build stats list
    stats = []
    for d in all_dates:
        stats.append(MeetingStats(
            date=d,
            display_date=date_utils.format_display_date(d),
            month_key=date_utils.get_month_key(d),
            attended_count=attended_counts[d],
            no_show_count=no_show_counts[d],
            rsvp_count=rsvp_counts[d]
        ))

    # Sort by date DESC (newest first)
    stats.sort(key=lambda s: s.date, reverse=True)

    return stats


def get_available_months(meetings: list) -> list:
    """
    Get unique months with data.

    Args:
        meetings: List of MeetingStats

    Returns:
        List of month keys sorted DESC (newest first)
    """
    months = set(m.month_key for m in meetings)
    return sorted(months, reverse=True)


def build_chart_data(meetings: list, month_key: str) -> dict:
    """
    Build Chart.js-compatible data structure.

    Args:
        meetings: List of MeetingStats
        month_key: Month to filter by (e.g., "2026-01")

    Returns:
        Dict with labels and datasets for Chart.js
    """
    # Filter to selected month and sort by date (oldest first for chart)
    filtered = [m for m in meetings if m.month_key == month_key]
    filtered.sort(key=lambda m: m.date)

    labels = [m.display_date for m in filtered]
    attended_data = [m.attended_count for m in filtered]
    no_show_data = [m.no_show_count for m in filtered]

    return {
        "labels": labels,
        "datasets": [
            {
                "label": "Attended",
                "data": attended_data,
                "backgroundColor": "#d0a848"
            },
            {
                "label": "No-Show",
                "data": no_show_data,
                "backgroundColor": "#9ca3af"
            }
        ]
    }


def build_rsvp_counts(meetings: list, month_key: str) -> list:
    """
    Build RSVP counts for a month.

    Args:
        meetings: List of MeetingStats
        month_key: Month to filter by

    Returns:
        List of {"date": "Jan 8, 2026", "count": 12}
    """
    filtered = [m for m in meetings if m.month_key == month_key]
    filtered.sort(key=lambda m: m.date, reverse=True)

    return [{"date": m.display_date, "count": m.rsvp_count} for m in filtered]


if __name__ == "__main__":
    print("Aggregator module loaded successfully")
