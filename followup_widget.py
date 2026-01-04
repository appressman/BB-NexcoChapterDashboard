#!/usr/bin/env python3
"""
Follow-up widget calculator for neXco Chapter Dashboard.
Calculates follow-up assignments per member.
"""

from dataclasses import dataclass
from collections import defaultdict

import name_normalizer
from name_matcher import NameMatcher


@dataclass
class FollowUpCount:
    """Follow-up count for a single name."""
    name: str
    count: int
    is_special: bool  # True for Unassigned, Ambiguous
    is_raw_token: bool  # True for unmatched names


def calculate_followups(guests: list, matcher: NameMatcher) -> list:
    """
    Calculate follow-up counts from guest data.

    Args:
        guests: Combined list of attended guests + guests_without_rsvp
        matcher: NameMatcher instance for resolving names

    Returns:
        List of FollowUpCount objects, sorted appropriately
    """
    counts = defaultdict(int)
    raw_tokens = set()
    has_ambiguous = False
    has_unassigned = False

    for guest in guests:
        tokens = name_normalizer.tokenize_followups(guest.following_up)

        if not tokens:
            has_unassigned = True
            counts["Unassigned"] += 1
            continue

        for token in tokens:
            canonical, match_type = matcher.match(token)

            if match_type == "ambiguous":
                has_ambiguous = True
                counts["Ambiguous"] += 1
            elif match_type == "unmatched":
                raw_tokens.add(token)
                counts[token] += 1
            else:
                counts[canonical] += 1

    # Build result list
    result = []

    # Canonical names (matched to roster)
    canonical_names = []
    for name, count in counts.items():
        if name not in ("Unassigned", "Ambiguous") and name not in raw_tokens:
            canonical_names.append(FollowUpCount(
                name=name,
                count=count,
                is_special=False,
                is_raw_token=False
            ))

    # Sort canonical names alphabetically
    canonical_names.sort(key=lambda x: x.name.lower())
    result.extend(canonical_names)

    # Special buckets
    if has_unassigned:
        result.append(FollowUpCount(
            name="Unassigned",
            count=counts["Unassigned"],
            is_special=True,
            is_raw_token=False
        ))

    if has_ambiguous:
        result.append(FollowUpCount(
            name="Ambiguous",
            count=counts["Ambiguous"],
            is_special=True,
            is_raw_token=False
        ))

    # Raw tokens (unmatched) - sorted alphabetically
    raw_list = []
    for token in raw_tokens:
        raw_list.append(FollowUpCount(
            name=token,
            count=counts[token],
            is_special=False,
            is_raw_token=True
        ))
    raw_list.sort(key=lambda x: x.name.lower())
    result.extend(raw_list)

    return result


if __name__ == "__main__":
    print("Follow-up widget module loaded successfully")
