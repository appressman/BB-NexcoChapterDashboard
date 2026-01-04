#!/usr/bin/env python3
"""
Meeting calendar for neXco Chapter Dashboard.
Handles 2nd and 4th Wednesday meeting schedule.
"""

from datetime import date, timedelta
from typing import List, Tuple


def get_nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """
    Get the nth occurrence of a weekday in a month.

    Args:
        year: Year
        month: Month (1-12)
        weekday: Day of week (0=Monday, 2=Wednesday, 6=Sunday)
        n: Which occurrence (1=first, 2=second, etc.)

    Returns:
        The date of the nth weekday
    """
    # Find first day of month
    first_day = date(year, month, 1)

    # Find first occurrence of the weekday
    days_until_weekday = (weekday - first_day.weekday()) % 7
    first_occurrence = first_day + timedelta(days=days_until_weekday)

    # Add weeks to get nth occurrence
    return first_occurrence + timedelta(weeks=n - 1)


def get_meeting_dates_for_month(year: int, month: int) -> Tuple[date, date]:
    """
    Get the 2nd and 4th Wednesday of a month.

    Args:
        year: Year
        month: Month (1-12)

    Returns:
        Tuple of (2nd_wednesday, 4th_wednesday)
    """
    wednesday = 2  # Wednesday is weekday 2 (Monday=0)
    second_wed = get_nth_weekday(year, month, wednesday, 2)
    fourth_wed = get_nth_weekday(year, month, wednesday, 4)
    return second_wed, fourth_wed


def get_upcoming_meetings(from_date: date, count: int = 4) -> List[date]:
    """
    Get the next N meeting dates from a given date.

    Args:
        from_date: Starting date
        count: Number of meetings to return

    Returns:
        List of upcoming meeting dates
    """
    meetings = []
    year = from_date.year
    month = from_date.month

    while len(meetings) < count:
        second_wed, fourth_wed = get_meeting_dates_for_month(year, month)

        if second_wed >= from_date and len(meetings) < count:
            meetings.append(second_wed)
        if fourth_wed >= from_date and len(meetings) < count:
            meetings.append(fourth_wed)

        # Move to next month
        month += 1
        if month > 12:
            month = 1
            year += 1

    return meetings


def snap_to_meeting_date(rsvp_date: date) -> date:
    """
    Snap an RSVP date to the meeting date they would have attended.

    Logic:
    - If the date IS a valid meeting date, return it
    - If the date is BEFORE the next meeting, return the next meeting
    - This handles RSVPs submitted between meetings

    Args:
        rsvp_date: The date from the RSVP record

    Returns:
        The actual meeting date this RSVP is for
    """
    # Check if this is already a valid meeting date
    year = rsvp_date.year
    month = rsvp_date.month
    second_wed, fourth_wed = get_meeting_dates_for_month(year, month)

    if rsvp_date == second_wed or rsvp_date == fourth_wed:
        return rsvp_date

    # Find the next meeting date
    # Check current month first
    if rsvp_date < second_wed:
        return second_wed
    elif rsvp_date < fourth_wed:
        return fourth_wed
    else:
        # Past the 4th Wednesday, next meeting is in next month
        next_month = month + 1
        next_year = year
        if next_month > 12:
            next_month = 1
            next_year += 1

        next_second_wed, _ = get_meeting_dates_for_month(next_year, next_month)
        return next_second_wed


def is_valid_meeting_date(check_date: date) -> bool:
    """
    Check if a date is a valid meeting date (2nd or 4th Wednesday).

    Args:
        check_date: Date to check

    Returns:
        True if it's a valid meeting date
    """
    second_wed, fourth_wed = get_meeting_dates_for_month(check_date.year, check_date.month)
    return check_date == second_wed or check_date == fourth_wed


if __name__ == "__main__":
    # Test the functions
    from datetime import date

    # Test September 2025
    second, fourth = get_meeting_dates_for_month(2025, 9)
    print(f"September 2025 meetings: {second} and {fourth}")

    # Test snapping
    test_dates = [
        date(2025, 9, 1),   # Should snap to Sep 10
        date(2025, 9, 10),  # Should stay Sep 10
        date(2025, 9, 15),  # Should snap to Sep 24
        date(2025, 9, 24),  # Should stay Sep 24
        date(2025, 9, 26),  # Should snap to Oct 8
    ]

    for d in test_dates:
        snapped = snap_to_meeting_date(d)
        print(f"{d} -> {snapped}")
