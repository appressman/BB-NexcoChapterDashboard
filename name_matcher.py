#!/usr/bin/env python3
"""
Name matcher for neXco Chapter Dashboard.
Matches follow-up tokens to roster names and aliases.
"""

from typing import Optional, Tuple

import name_normalizer


class NameMatcher:
    """
    Matches follow-up name tokens to canonical names.

    Match types returned:
    - "alias": Matched via alias configuration
    - "roster": Matched exact full name in roster
    - "first_name": Matched unique first name in roster
    - "ambiguous": Multiple first-name matches possible
    - "unmatched": No match found
    """

    def __init__(self, roster: list, aliases: dict):
        """
        Initialize the matcher.

        Args:
            roster: List of canonical full names from roster
            aliases: Dict mapping short names to full names
        """
        self.roster = roster
        self.aliases = aliases

        # Build lookup structures
        self._aliases_lower = {k.casefold(): v for k, v in aliases.items()}
        self._roster_lower = {n.casefold(): n for n in roster}

        # Build first name lookup
        self._first_name_counts = {}
        self._first_name_to_full = {}
        for name in roster:
            parts = name.split()
            if parts:
                first = parts[0].casefold()
                self._first_name_counts[first] = self._first_name_counts.get(first, 0) + 1
                self._first_name_to_full[first] = name  # Will be overwritten if multiple

    def match(self, token: str) -> Tuple[Optional[str], str]:
        """
        Match a follow-up token to a canonical name.

        Args:
            token: Raw follow-up token

        Returns:
            Tuple of (canonical_name or None, match_type)
        """
        # Get normalized versions
        light, heavy = name_normalizer.normalize_name(token)

        # Try light normalization first
        result = self._try_match(light)
        if result[0] is not None or result[1] == "ambiguous":
            return result

        # Try heavy normalization
        if heavy != light:
            result = self._try_match(heavy)
            if result[0] is not None or result[1] == "ambiguous":
                return result

        return (None, "unmatched")

    def _try_match(self, name: str) -> Tuple[Optional[str], str]:
        """
        Try to match a normalized name.

        Args:
            name: Normalized name to match

        Returns:
            Tuple of (canonical_name or None, match_type)
        """
        name_lower = name.casefold()

        # 1. Check aliases first
        if name_lower in self._aliases_lower:
            return (self._aliases_lower[name_lower], "alias")

        # 2. Check exact roster match
        if name_lower in self._roster_lower:
            return (self._roster_lower[name_lower], "roster")

        # 3. Check unique first name
        if name_lower in self._first_name_counts:
            count = self._first_name_counts[name_lower]
            if count == 1:
                return (self._first_name_to_full[name_lower], "first_name")
            else:
                return (None, "ambiguous")

        return (None, "unmatched")


if __name__ == "__main__":
    # Test the matcher
    roster = ["Adam Pressman", "Daniel Lyon", "Anne-Marie Smith", "Dan Brown"]
    aliases = {"AP": "Adam Pressman"}

    matcher = NameMatcher(roster, aliases)

    test_tokens = [
        "Adam",
        "Dan",  # Ambiguous - Daniel Lyon and Dan Brown
        "AP",
        "Adam (VP)",
        "Anne-Marie",
        "Unknown Person"
    ]

    for token in test_tokens:
        canonical, match_type = matcher.match(token)
        print(f"{token!r} -> {canonical!r} ({match_type})")
