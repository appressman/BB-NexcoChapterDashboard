#!/usr/bin/env python3
"""
Config validation utility for neXco Chapter Dashboard.
"""

import sys
from pathlib import Path

# Add bin directory to path for imports
BIN_DIR = Path(__file__).parent
sys.path.insert(0, str(BIN_DIR))

from config import load_config, extract_spreadsheet_id, ConfigError


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_config.py <config_file>")
        print("Example: validate_config.py /home/adam/nexco-dashboard/config/chapters/nexco-novacore.json")
        sys.exit(1)

    config_path = sys.argv[1]

    print(f"Validating: {config_path}")
    print("-" * 50)

    try:
        config = load_config(config_path)

        print(f"✓ Chapter slug: {config.chapter_slug}")
        print(f"✓ Display name: {config.display_name}")
        print(f"✓ Page title: {config.page_title}")
        print(f"✓ Sheet URL: {config.sheet_url}")
        print(f"✓ Spreadsheet ID: {extract_spreadsheet_id(config.sheet_url)}")
        print(f"✓ Roster URL: {config.roster_url}")
        print(f"✓ Tab names:")
        for key, tab in config.tab_names.items():
            print(f"    - {key}: {tab}")
        print(f"✓ Aliases: {len(config.aliases)} defined")

        print("-" * 50)
        print("✓ Configuration is valid!")
        sys.exit(0)

    except ConfigError as e:
        print(f"✗ Configuration error: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
