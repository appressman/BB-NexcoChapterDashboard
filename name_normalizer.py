#!/usr/bin/env python3
"""
Name tokenizer and normalizer for neXco Chapter Dashboard.
Handles parsing and normalizing follow-up names.
"""

import re


def tokenize_followups(followup_str: str) -> list:
    """
    Split follow-up string into individual name tokens.

    Supports multiple delimiters:
    - Comma: "Dan, Adam"
    - Slash: "Dan/Luanne" or "Dan/Adam/Jasleen/Rohini"
    - Ampersand: "Dan & Luanne"

    Args:
        followup_str: Delimited follow-up names

    Returns:
        List of trimmed, non-empty tokens
    """
    if not followup_str or not followup_str.strip():
        return []

    # Split on comma, slash, or ampersand
    tokens = re.split(r'[,/&]', followup_str)
    return [t.strip() for t in tokens if t.strip()]


def normalize_name_light(token: str) -> str:
    """
    Light normalization pass.

    - Strip leading/trailing whitespace
    - Collapse multiple internal spaces

    Args:
        token: Raw name token

    Returns:
        Lightly normalized name
    """
    return " ".join(token.split())


def normalize_name_heavy(token: str) -> str:
    """
    Heavy normalization pass.
    Only applied if light normalization didn't match.

    - Remove parenthetical content: "Dan (VP)" -> "Dan"
    - Remove bracketed content: "Dan [VP]" -> "Dan"
    - Remove trailing annotations after -, —, –, :

    Args:
        token: Name token after light normalization

    Returns:
        Heavily normalized name
    """
    result = token

    # Remove parenthetical content
    result = re.sub(r"\([^()]*\)", "", result)

    # Remove bracketed content
    result = re.sub(r"\[[^\[\]]*\]", "", result)

    # Remove trailing annotations after -, —, –, :
    # Use .* instead of .+ to also strip bare trailing colons like "Adam:"
    result = re.sub(r"[-—–:].*$", "", result)

    # Final cleanup
    return " ".join(result.split())


def normalize_name(token: str) -> tuple:
    """
    Two-pass name normalization.

    Args:
        token: Raw name token

    Returns:
        Tuple of (light_normalized, heavy_normalized)
    """
    light = normalize_name_light(token)
    heavy = normalize_name_heavy(light)
    return light, heavy


def casefold_normalize(name: str) -> str:
    """
    Case-insensitive normalization for matching.

    Args:
        name: Name string

    Returns:
        Casefolded, stripped string
    """
    return name.strip().casefold()


if __name__ == "__main__":
    # Test cases
    test_cases = [
        "Dan, Adam (VP), ",
        "Anne-Marie",
        "Dan (VP)",
        "Terrie: follow up",
        "Bob - needs callback",
        "Jane [Marketing]"
    ]

    for tc in test_cases:
        tokens = tokenize_followups(tc)
        print(f"Input: {tc!r}")
        print(f"  Tokens: {tokens}")
        for t in tokens:
            light, heavy = normalize_name(t)
            print(f"    {t!r} -> light: {light!r}, heavy: {heavy!r}")
