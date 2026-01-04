#!/usr/bin/env python3
"""
Main refresh script for neXco Chapter Dashboard.
Orchestrates data fetching, processing, and output generation.
"""

import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Add bin directory to path for imports
BIN_DIR = Path(__file__).parent
sys.path.insert(0, str(BIN_DIR))

from config import load_all_configs, extract_spreadsheet_id, ChapterConfig
from logger import setup_logger, log_chapter_start, log_chapter_success, log_chapter_error
from sheets_fetcher import fetch_sheet_csv, FetchError
from roster_scraper import scrape_roster, build_roster_lookup, ScrapeError
from rsvp_processor import parse_rsvps, dedupe_rsvps, filter_historical as filter_rsvps
from guest_tracker_processor import parse_guest_tracker, filter_historical as filter_gt
from data_merger import merge_data
from aggregator import aggregate_meetings
from name_matcher import NameMatcher
from followup_widget import calculate_followups
from json_builder import build_data_json
from file_writer import atomic_write_json
from index_generator import generate_index_html


# Configuration
CONFIG_DIR = "/home/adam/nexco-dashboard/config/chapters"
LOG_DIR = "/home/adam/nexco-dashboard/logs"
PUBLIC_DIR = "/home/adam/public_html/leadershipshape/nexco-dashboard"


@dataclass
class RefreshResult:
    """Result of refreshing a single chapter."""
    chapter_slug: str
    success: bool
    error: Optional[str]
    duration_seconds: float


def refresh_chapter(config: ChapterConfig, logger) -> RefreshResult:
    """
    Refresh data for a single chapter.

    Args:
        config: Chapter configuration
        logger: Logger instance

    Returns:
        RefreshResult with success/error info
    """
    start_time = time.time()
    log_chapter_start(logger, config.chapter_slug)

    try:
        # Fetch sheet data
        spreadsheet_id = extract_spreadsheet_id(config.sheet_url)

        rsvp_rows = fetch_sheet_csv(spreadsheet_id, config.tab_names["rsvps"])
        gt_rows = fetch_sheet_csv(spreadsheet_id, config.tab_names["guest_tracker"])
        open_seats_rows = fetch_sheet_csv(spreadsheet_id, config.tab_names["open_seats"])

        # Try to fetch roster (non-fatal if fails)
        roster = []
        try:
            roster = scrape_roster(config.roster_url)
            logger.debug(f"Scraped {len(roster)} names from roster")
        except ScrapeError as e:
            logger.warning(f"Roster scrape failed: {e.message}")

        # Process RSVPs
        rsvps = parse_rsvps(rsvp_rows)
        rsvps = dedupe_rsvps(rsvps)
        rsvps = filter_rsvps(rsvps)
        logger.debug(f"Processed {len(rsvps)} historical RSVPs")

        # Process Guest Tracker
        gt_records = parse_guest_tracker(gt_rows)
        gt_records = filter_gt(gt_records)
        logger.debug(f"Processed {len(gt_records)} historical GT records")

        # Merge data
        merged = merge_data(rsvps, gt_records)
        logger.debug(f"Merged: {len(merged['attended'])} attended, "
                     f"{len(merged['no_show'])} no-show, "
                     f"{len(merged['without_rsvp'])} without RSVP")

        # Aggregate meetings
        meetings = aggregate_meetings(merged, rsvps)
        logger.debug(f"Aggregated {len(meetings)} meeting dates")

        # Calculate follow-ups
        roster_lookup = build_roster_lookup(roster)
        matcher = NameMatcher(roster, config.aliases)
        all_attended = merged["attended"] + merged["without_rsvp"]
        followups = calculate_followups(all_attended, matcher)
        logger.debug(f"Calculated {len(followups)} follow-up buckets")

        # Build JSON
        data_json = build_data_json(
            config=config,
            merged=merged,
            meetings=meetings,
            open_seats=open_seats_rows,
            followups=followups,
            refresh_success=True
        )

        # Write output
        output_path = Path(PUBLIC_DIR) / config.chapter_slug / "data.json"
        atomic_write_json(data_json, str(output_path))
        logger.info(f"Wrote data to: {output_path}")

        duration = time.time() - start_time
        log_chapter_success(logger, config.chapter_slug, duration)

        return RefreshResult(
            chapter_slug=config.chapter_slug,
            success=True,
            error=None,
            duration_seconds=duration
        )

    except FetchError as e:
        duration = time.time() - start_time
        log_chapter_error(logger, config.chapter_slug, e)
        return RefreshResult(
            chapter_slug=config.chapter_slug,
            success=False,
            error=e.message,
            duration_seconds=duration
        )

    except Exception as e:
        duration = time.time() - start_time
        log_chapter_error(logger, config.chapter_slug, e)
        return RefreshResult(
            chapter_slug=config.chapter_slug,
            success=False,
            error=str(e),
            duration_seconds=duration
        )


def main():
    """Main entry point."""
    # Setup logging
    logger = setup_logger(LOG_DIR)
    logger.info("Starting neXco Dashboard refresh")

    # Load all configs
    try:
        configs = load_all_configs(CONFIG_DIR)
        logger.info(f"Loaded {len(configs)} chapter configurations")
    except Exception as e:
        logger.error(f"Failed to load configs: {e}")
        sys.exit(1)

    if not configs:
        logger.warning("No chapter configurations found")
        sys.exit(0)

    # Process each chapter
    results = []
    for config in configs:
        result = refresh_chapter(config, logger)
        results.append(result)

    # Generate index page
    try:
        index_path = Path(PUBLIC_DIR) / "index.html"
        generate_index_html(configs, str(index_path))
        logger.info(f"Generated index page: {index_path}")
    except Exception as e:
        logger.error(f"Failed to generate index page: {e}")

    # Print summary
    print("\n" + "=" * 50)
    print("Refresh completed:")
    print("=" * 50)

    success_count = 0
    for result in results:
        if result.success:
            status = f"SUCCESS ({result.duration_seconds:.1f}s)"
            success_count += 1
        else:
            status = f"FAILED - {result.error}"
        print(f"  - {result.chapter_slug}: {status}")

    print("=" * 50)
    print(f"Total: {success_count}/{len(results)} chapters refreshed successfully")

    # Exit with error code if any failed
    if success_count < len(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
