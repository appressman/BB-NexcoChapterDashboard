#!/usr/bin/env python3
"""
Name matcher for neXco Chapter Dashboard.
Matches follow-up tokens to roster names and aliases.
"""

from typing import Optional, Tuple

import name_normalizer


# Common nickname mappings (nickname -> formal name)
NICKNAMES = {
    "dan": "daniel",
    "danny": "daniel",
    "mike": "michael",
    "mick": "michael",
    "bob": "robert",
    "rob": "robert",
    "bobby": "robert",
    "bill": "william",
    "will": "william",
    "billy": "william",
    "jim": "james",
    "jimmy": "james",
    "joe": "joseph",
    "joey": "joseph",
    "tom": "thomas",
    "tommy": "thomas",
    "dick": "richard",
    "rick": "richard",
    "rich": "richard",
    "tony": "anthony",
    "steve": "stephen",
    "steven": "stephen",
    "chris": "christopher",
    "ed": "edward",
    "eddie": "edward",
    "ted": "theodore",
    "teddy": "theodore",
    "alex": "alexander",
    "al": "albert",
    "beth": "elizabeth",
    "liz": "elizabeth",
    "lizzy": "elizabeth",
    "betty": "elizabeth",
    "kate": "katherine",
    "kathy": "katherine",
    "katie": "katherine",
    "sam": "samuel",
    "sammy": "samuel",
    "dave": "david",
    "davy": "david",
    "matt": "matthew",
    "matty": "matthew",
    "nick": "nicholas",
    "nicky": "nicholas",
    "pat": "patrick",
    "patty": "patricia",
    "sue": "susan",
    "susie": "susan",
    "jen": "jennifer",
    "jenny": "jennifer",
    "becky": "rebecca",
    "becca": "rebecca",
    "mandy": "amanda",
    "andy": "andrew",
    "drew": "andrew",
    "charlie": "charles",
    "chuck": "charles",
    "doug": "douglas",
    "greg": "gregory",
    "jeff": "jeffrey",
    "jerry": "gerald",
    "larry": "lawrence",
    "len": "leonard",
    "lenny": "leonard",
    "ron": "ronald",
    "ronnie": "ronald",
    "russ": "russell",
    "terry": "terrence",
    "tim": "timothy",
    "timmy": "timothy",
    "vince": "vincent",
    "vinny": "vincent",
    "wally": "walter",
    "walt": "walter",
}


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

        # Build first name lookup (both formal and nickname variants)
        self._first_name_counts = {}
        self._first_name_to_full = {}
        self._nickname_to_full = {}  # Maps nicknames to roster entries

        for name in roster:
            parts = name.split()
            if parts:
                first = parts[0].casefold()
                self._first_name_counts[first] = self._first_name_counts.get(first, 0) + 1
                self._first_name_to_full[first] = name  # Will be overwritten if multiple

                # Also index by nicknames that map to this first name
                for nickname, formal in NICKNAMES.items():
                    if formal == first:
                        # This roster member's first name matches this nickname's formal form
                        if nickname not in self._nickname_to_full:
                            self._nickname_to_full[nickname] = []
                        self._nickname_to_full[nickname].append(name)

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

        # 3. Check unique first name (single word)
        if " " not in name_lower and name_lower in self._first_name_counts:
            count = self._first_name_counts[name_lower]
            if count == 1:
                return (self._first_name_to_full[name_lower], "first_name")
            else:
                return (None, "ambiguous")

        # 4. Check nickname match (e.g., "Dan" -> "Daniel Lyon")
        if " " not in name_lower and name_lower in self._nickname_to_full:
            matches = self._nickname_to_full[name_lower]
            if len(matches) == 1:
                return (matches[0], "nickname")
            else:
                return (None, "ambiguous")

        # 5. Check partial name match (e.g., "Adam P" or "Adam P." for "Adam Pressman")
        partial_result = self._try_partial_match(name_lower)
        if partial_result[0] is not None or partial_result[1] == "ambiguous":
            return partial_result

        return (None, "unmatched")

    def _try_partial_match(self, name_lower: str) -> Tuple[Optional[str], str]:
        """
        Try to match partial names like "Adam P" or "Adam P." to "Adam Pressman".
        Also handles nicknames like "Dan L" -> "Daniel Lyon".

        Args:
            name_lower: Casefolded name with potential partial last name

        Returns:
            Tuple of (canonical_name or None, match_type)
        """
        import re

        # Remove trailing periods and clean up
        name_clean = re.sub(r'\.+$', '', name_lower).strip()

        # Look for pattern: "FirstName LastInitial" or "FirstName LastPartial"
        parts = name_clean.split()
        if len(parts) < 2:
            return (None, "unmatched")

        first_part = parts[0]
        last_part = parts[-1].rstrip('.')  # "P" or "P." -> "P"

        # Build list of first names to try (original + formal version if nickname)
        first_names_to_try = [first_part]
        if first_part in NICKNAMES:
            first_names_to_try.append(NICKNAMES[first_part])

        # Find all roster names that match
        candidates = []
        for roster_name in self.roster:
            roster_lower = roster_name.casefold()
            roster_parts = roster_lower.split()
            if len(roster_parts) >= 2:
                roster_first = roster_parts[0]
                roster_last = roster_parts[-1]

                # Check if first name matches (or nickname matches) and last name starts with partial
                if roster_first in first_names_to_try and roster_last.startswith(last_part):
                    candidates.append(roster_name)

        if len(candidates) == 1:
            return (candidates[0], "partial")
        elif len(candidates) > 1:
            return (None, "ambiguous")

        return (None, "unmatched")


if __name__ == "__main__":
    # Test the matcher
    roster = ["Adam Pressman", "Daniel Lyon", "Anne-Marie Smith", "Dan Brown", "Adam Parker"]
    aliases = {"AP": "Adam Pressman"}

    matcher = NameMatcher(roster, aliases)

    test_tokens = [
        "Adam",       # Ambiguous - Adam Pressman and Adam Parker
        "Dan",        # Ambiguous - Daniel Lyon and Dan Brown
        "AP",         # Alias
        "Adam (VP)",  # Heavy normalization needed
        "Anne-Marie", # First name match
        "Unknown Person",
        "Adam P",     # Partial match - should match Adam Pressman or Adam Parker?
        "Adam P.",    # Partial match with period
        "Adam Pre",   # Partial match - more specific
        "Adam Par",   # Partial match - Adam Parker
        "Dan L",      # Partial match - Daniel Lyon
        "Dan B",      # Partial match - Dan Brown
    ]

    print("Name matching tests:")
    for token in test_tokens:
        canonical, match_type = matcher.match(token)
        print(f"  {token!r} -> {canonical!r} ({match_type})")

    # Test tokenizer with slash-delimited names
    print("\nTokenizer tests:")
    from name_normalizer import tokenize_followups
    test_strings = [
        "Dan/Luanne",
        "Dan/Adam/Jasleen/Rohini",
        "Dan, Adam, Jane",
        "Dan & Luanne",
    ]
    for s in test_strings:
        tokens = tokenize_followups(s)
        print(f"  {s!r} -> {tokens}")
