# neXco Chapter Dashboard - Implementation Blueprint

## High-Level Architecture

This project has two main components:
1. **Python Backend** - Weekly refresh script that fetches data and generates JSON
2. **Static Frontend** - HTML/CSS/JS dashboard that reads the JSON

## Implementation Phases

### Phase 1: Project Foundation & Configuration
- Directory structure creation
- Config file schema and loading
- Logging infrastructure

### Phase 2: Data Fetching Layer
- Google Sheets CSV fetcher
- Roster page HTML scraper

### Phase 3: Data Processing Core
- Date parsing and formatting utilities
- RSVP deduplication logic
- Guest Tracker processing
- Data merge (RSVP + Guest Tracker)

### Phase 4: Follow-Up Widget Logic
- Name tokenization
- Two-pass normalization
- Alias/roster matching
- Bucket assignment

### Phase 5: Output Generation
- data.json schema implementation
- Atomic file writing
- Index page generation

### Phase 6: Frontend Foundation
- HTML structure and templates
- CSS theming (neXco brand)
- Asset setup (Chart.js, logo)

### Phase 7: Frontend Core Features
- Data loading from JSON
- Month selector with Firefox fallback
- Chart rendering

### Phase 8: Frontend Tables & Widgets
- Guest tables with filtering
- RSVP counts display
- Follow-up widget
- Open seats table

### Phase 9: Integration & Deployment
- Main refresh script orchestration
- Error handling
- Cron setup

---

## Detailed Step Breakdown

### Phase 1: Project Foundation (Steps 1-4)

| Step | Description | Output |
|------|-------------|--------|
| 1.1 | Create directory structure | Folders created |
| 1.2 | Define config schema with validation | `config.py` |
| 1.3 | Implement logging with weekly rotation | `logger.py` |
| 1.4 | Create example chapter config | `nexco-novacore.json` |

### Phase 2: Data Fetching (Steps 5-7)

| Step | Description | Output |
|------|-------------|--------|
| 2.1 | Build Google Sheets CSV fetcher | `sheets_fetcher.py` |
| 2.2 | Build roster page scraper | `roster_scraper.py` |
| 2.3 | Integration tests for fetchers | `test_fetchers.py` |

### Phase 3: Data Processing (Steps 8-13)

| Step | Description | Output |
|------|-------------|--------|
| 3.1 | Date parsing utilities | `date_utils.py` |
| 3.2 | RSVP parser and deduplicator | `rsvp_processor.py` |
| 3.3 | Guest Tracker parser | `guest_tracker_processor.py` |
| 3.4 | Data merger (RSVP + GT join) | `data_merger.py` |
| 3.5 | Meeting aggregator (counts, chart data) | `aggregator.py` |
| 3.6 | Unit tests for processors | `test_processors.py` |

### Phase 4: Follow-Up Widget (Steps 14-17)

| Step | Description | Output |
|------|-------------|--------|
| 4.1 | Name tokenizer (comma split, trim) | `name_tokenizer.py` |
| 4.2 | Two-pass normalizer | `name_normalizer.py` |
| 4.3 | Roster/alias matcher | `name_matcher.py` |
| 4.4 | Follow-up counter with buckets | `followup_widget.py` |

### Phase 5: Output Generation (Steps 18-21)

| Step | Description | Output |
|------|-------------|--------|
| 5.1 | data.json schema builder | `json_builder.py` |
| 5.2 | Atomic file writer | `file_writer.py` |
| 5.3 | Index page generator | `index_generator.py` |
| 5.4 | Main orchestrator script | `refresh.py` |

### Phase 6: Frontend Foundation (Steps 22-25)

| Step | Description | Output |
|------|-------------|--------|
| 6.1 | Download and vendor Chart.js | `assets/vendor/` |
| 6.2 | Create CSS theme file | `styles.css` |
| 6.3 | Create HTML template structure | `index.html` (chapter) |
| 6.4 | Create index page template | `index.html` (root) |

### Phase 7: Frontend Core (Steps 26-29)

| Step | Description | Output |
|------|-------------|--------|
| 7.1 | Data loader module | `dashboard.js` (partial) |
| 7.2 | Month selector with fallback | `month-selector.js` |
| 7.3 | Chart rendering module | `chart.js` |
| 7.4 | Wire month selector to data | Integration |

### Phase 8: Frontend Tables (Steps 30-34)

| Step | Description | Output |
|------|-------------|--------|
| 8.1 | Table renderer with filtering | `tables.js` |
| 8.2 | RSVP counts list renderer | Integration |
| 8.3 | Follow-up widget renderer | Integration |
| 8.4 | Open seats table renderer | Integration |
| 8.5 | Final dashboard.js integration | `dashboard.js` |

### Phase 9: Integration (Steps 35-37)

| Step | Description | Output |
|------|-------------|--------|
| 9.1 | End-to-end test with sample data | Test suite |
| 9.2 | Deployment script | `deploy.sh` |
| 9.3 | Cron configuration | Crontab entry |

---

## Right-Sizing Analysis

After reviewing the steps above, here's the refined breakdown:

**Too granular (combined):**
- Steps 4.1-4.3 combined into single "Name Matching" module
- Steps 7.1 + 7.4 combined (data loading always needs wiring)

**Right-sized steps:**
- Each Python module is ~50-150 lines
- Each JS module is ~100-200 lines
- Each step builds on previous work
- Each step is independently testable

**Final count: 28 implementation prompts**

---

## Implementation Prompts

Each prompt below is designed to be self-contained, building incrementally on prior work. Use these with a code-generating LLM in sequence.

---

### Prompt 1: Create Directory Structure

```text
Create the directory structure for the neXco Chapter Dashboard project.

**Project Context:**
This is a dashboard that displays weekly metrics for neXco networking chapters. It has a Python backend that generates JSON data and a static HTML/CSS/JS frontend.

**Requirements:**

1. Create the following PUBLIC web directory structure at `/home/adam/public_html/leadershipshape/nexco-dashboard/`:
   ```
   nexco-dashboard/
   ├── assets/
   │   ├── css/
   │   ├── js/
   │   ├── img/
   │   └── vendor/
   │       └── chartjs/
   │           └── 4.5.1/
   └── nexco-novacore/
   ```

2. Create the following NON-PUBLIC working directory at `/home/adam/nexco-dashboard/`:
   ```
   nexco-dashboard/
   ├── bin/
   ├── config/
   │   └── chapters/
   ├── logs/
   └── tests/
   ```

3. Create placeholder `.gitkeep` files in empty directories so git tracks them.

4. Create a simple shell script `setup-dirs.sh` that creates all these directories idempotently (using `mkdir -p`).

**Output:**
- `setup-dirs.sh` script
- Execute the script to create all directories
- Verify the structure exists
```

---

### Prompt 2: Config Schema and Loader

```text
Create a Python configuration module for loading and validating chapter configs.

**Project Context:**
Each neXco chapter has its own JSON config file that specifies:
- Chapter slug (URL-safe identifier)
- Display name for UI
- Google Sheets URL
- Roster page URL
- Tab names for the three sheets
- Optional alias mappings for name normalization

**File Location:** `/home/adam/nexco-dashboard/bin/config.py`

**Requirements:**

1. Define a `ChapterConfig` dataclass or TypedDict with these fields:
   - `chapter_slug: str` (required) - e.g., "nexco-novacore"
   - `display_name: str` (required) - e.g., "NOVA Core (B2C)"
   - `page_title: str` (required) - e.g., "neXco NOVA Core Dashboard"
   - `sheet_url: str` (required) - full Google Sheets URL
   - `roster_url: str` (required) - neXco chapter page URL
   - `tab_names: dict` (required) - keys: "rsvps", "guest_tracker", "open_seats"
   - `aliases: dict` (optional, default {}) - maps short names to full names

2. Create a `load_config(config_path: str) -> ChapterConfig` function that:
   - Reads JSON from the given path
   - Validates all required fields are present
   - Validates `tab_names` has all three required keys
   - Returns typed config object
   - Raises `ConfigError` with helpful message if validation fails

3. Create a `load_all_configs(config_dir: str) -> list[ChapterConfig]` function that:
   - Scans directory for `*.json` files
   - Loads each config
   - Returns list sorted alphabetically by `display_name`

4. Create a `extract_spreadsheet_id(sheet_url: str) -> str` helper that:
   - Extracts the spreadsheet ID from URL (between `/d/` and next `/`)
   - Raises `ConfigError` if URL format is invalid

5. Use only Python standard library (json, dataclasses, pathlib, re).

**Testing Requirements:**
Write unit tests in `/home/adam/nexco-dashboard/tests/test_config.py`:
- Test loading valid config
- Test missing required field
- Test invalid tab_names
- Test spreadsheet ID extraction

**Example Config:**
```json
{
  "chapter_slug": "nexco-novacore",
  "display_name": "NOVA Core (B2C)",
  "page_title": "neXco NOVA Core Dashboard",
  "sheet_url": "https://docs.google.com/spreadsheets/d/16yJn474Z4QrlgCdz2pL0yfPgzBHAa4ZKLE-yxZJqd3E",
  "roster_url": "https://members.nexconational.com/nova-core/",
  "tab_names": {
    "rsvps": "RSVPs",
    "guest_tracker": "Guest Tracker",
    "open_seats": "Top 3 Open Seats"
  },
  "aliases": {}
}
```
```

---

### Prompt 3: Logging Infrastructure

```text
Create a logging module with weekly log rotation for the neXco Dashboard refresh script.

**File Location:** `/home/adam/nexco-dashboard/bin/logger.py`

**Requirements:**

1. Create a `setup_logger(log_dir: str, name: str = "refresh") -> logging.Logger` function that:
   - Creates log directory if it doesn't exist
   - Creates a logger with both console and file handlers
   - Console: INFO level, simple format
   - File: DEBUG level, detailed format with timestamps

2. Log file naming:
   - Pattern: `refresh-YYYY-WW.log` where WW is ISO week number
   - Example: `refresh-2026-01.log` for first week of 2026
   - Use Python's `datetime.isocalendar()` for week number

3. Log rotation:
   - On each run, check for log files older than 12 weeks
   - Delete old log files automatically
   - Log a message when deleting old files

4. Log format for file:
   ```
   2026-01-03T11:02:15-05:00 | INFO | Processing chapter: nexco-novacore
   2026-01-03T11:02:16-05:00 | ERROR | Failed to fetch RSVPs tab: HTTP 404
   ```

5. Create helper functions:
   - `log_chapter_start(logger, chapter_slug: str)`
   - `log_chapter_success(logger, chapter_slug: str, duration_seconds: float)`
   - `log_chapter_error(logger, chapter_slug: str, error: Exception)`

6. Use only Python standard library (logging, datetime, pathlib, glob).

**Testing Requirements:**
Write tests in `/home/adam/nexco-dashboard/tests/test_logger.py`:
- Test log file is created with correct name
- Test old log cleanup (mock 13+ week old files)
- Test log format matches expected pattern
```

---

### Prompt 4: Create Example Chapter Config

```text
Create the first chapter configuration file for NOVA Core.

**File Location:** `/home/adam/nexco-dashboard/config/chapters/nexco-novacore.json`

**Requirements:**

1. Create a valid JSON config file with these exact values:
   ```json
   {
     "chapter_slug": "nexco-novacore",
     "display_name": "NOVA Core (B2C)",
     "page_title": "neXco NOVA Core Dashboard",
     "sheet_url": "https://docs.google.com/spreadsheets/d/16yJn474Z4QrlgCdz2pL0yfPgzBHAa4ZKLE-yxZJqd3E",
     "roster_url": "https://members.nexconational.com/nova-core/",
     "tab_names": {
       "rsvps": "RSVPs",
       "guest_tracker": "Guest Tracker",
       "open_seats": "Top 3 Open Seats"
     },
     "aliases": {}
   }
   ```

2. Verify the config loads correctly using the `config.py` module from Prompt 2.

3. Create a simple validation script `/home/adam/nexco-dashboard/bin/validate_config.py` that:
   - Takes a config file path as argument
   - Loads and validates the config
   - Prints success message or detailed error
   - Exit code 0 for success, 1 for error

**Verification:**
Run the validation script against the created config and confirm it passes.
```

---

### Prompt 5: Google Sheets CSV Fetcher

```text
Create a module to fetch CSV data from public Google Sheets.

**File Location:** `/home/adam/nexco-dashboard/bin/sheets_fetcher.py`

**Requirements:**

1. Create a `fetch_sheet_csv(spreadsheet_id: str, tab_name: str) -> list[dict]` function that:
   - Constructs the gviz CSV URL:
     `https://docs.google.com/spreadsheets/d/{id}/gviz/tq?tqx=out:csv&sheet={tab}`
   - URL-encodes tab names with spaces (e.g., "Guest Tracker" → "Guest%20Tracker")
   - Fetches CSV with urllib.request
   - Sets a User-Agent header: "NexcoDashboard/1.0"
   - Parses CSV using csv.DictReader
   - Returns list of row dictionaries
   - Raises `FetchError` on HTTP errors or timeouts

2. Create a `FetchError` custom exception with:
   - `url: str` - the URL that failed
   - `status_code: int | None` - HTTP status if available
   - `message: str` - human-readable error

3. Handle edge cases:
   - Empty sheet (return empty list)
   - Missing columns (return what's available)
   - HTTP 404 (raise FetchError with clear message)
   - Timeout after 30 seconds

4. Create a convenience function `fetch_chapter_tabs(config: ChapterConfig) -> dict`:
   - Fetches all three tabs (rsvps, guest_tracker, open_seats)
   - Returns dict with keys matching tab_names keys
   - If ANY tab fails, raise FetchError (don't return partial data)

5. Use only Python standard library (urllib.request, csv, io).

**Testing Requirements:**
Write tests in `/home/adam/nexco-dashboard/tests/test_sheets_fetcher.py`:
- Test URL construction with spaces in tab name
- Test CSV parsing with sample data
- Test error handling (mock HTTP errors)
- Use unittest.mock for network calls
```

---

### Prompt 6: Roster Page Scraper

```text
Create a module to scrape member names from neXco chapter roster pages.

**File Location:** `/home/adam/nexco-dashboard/bin/roster_scraper.py`

**Requirements:**

1. Create a `scrape_roster(roster_url: str) -> list[str]` function that:
   - Fetches the HTML page with urllib.request
   - Sets User-Agent header: "NexcoDashboard/1.0"
   - Parses HTML to extract member names
   - Returns list of full names (e.g., ["Adam Pressman", "Daniel Lyon"])
   - Raises `ScrapeError` on fetch or parse failure

2. HTML parsing approach (no external libraries):
   - Use regex or string parsing to find member name elements
   - The neXco page structure has member cards with names
   - Look for patterns like `<h4>` or `<div class="member-name">` containing names
   - Extract text content, strip whitespace
   - Deduplicate names (some may appear twice)

3. Create a `ScrapeError` custom exception with:
   - `url: str`
   - `message: str`

4. Name normalization:
   - Strip leading/trailing whitespace
   - Collapse multiple internal spaces
   - Return names sorted alphabetically

5. Build a canonical roster dictionary:
   ```python
   def build_roster_lookup(names: list[str]) -> dict[str, str]:
       """
       Returns dict mapping:
       - full name (casefolded) -> canonical name
       - first name (casefolded) -> canonical name (only if unique)
       """
   ```

6. Use only Python standard library (urllib.request, re, html.parser if needed).

**Testing Requirements:**
Write tests in `/home/adam/nexco-dashboard/tests/test_roster_scraper.py`:
- Test name extraction from sample HTML
- Test deduplication
- Test roster lookup building
- Test unique vs ambiguous first names
```

---

### Prompt 7: Date Utilities

```text
Create a date utilities module for parsing and formatting meeting dates.

**File Location:** `/home/adam/nexco-dashboard/bin/date_utils.py`

**Requirements:**

1. Create a `parse_meeting_date(date_str: str) -> date` function that:
   - Parses US format dates like "1/10/2024" (M/D/YYYY)
   - Handles single-digit months and days (no leading zeros)
   - Returns Python date object
   - Raises `ValueError` for invalid formats

2. Create a `format_display_date(d: date) -> str` function that:
   - Returns format like "Jan 10, 2024"
   - Uses abbreviated month names

3. Create a `get_today_eastern() -> date` function that:
   - Returns today's date in America/New_York timezone
   - Use datetime with timezone-aware approach
   - Handle DST correctly

4. Create a `is_historical(meeting_date: date) -> bool` function that:
   - Returns True if meeting_date < today (Eastern time)
   - Returns False for today or future dates

5. Create a `get_month_key(d: date) -> str` function that:
   - Returns "YYYY-MM" format (e.g., "2026-01")

6. Create a `get_display_month(month_key: str) -> str` function that:
   - Takes "YYYY-MM" and returns "January 2026"

7. Use only Python standard library (datetime, zoneinfo for Python 3.9+).

**Testing Requirements:**
Write tests in `/home/adam/nexco-dashboard/tests/test_date_utils.py`:
- Test parsing various date formats ("1/5/2024", "12/31/2025")
- Test display formatting
- Test historical detection
- Test month key generation
```

---

### Prompt 8: RSVP Processor

```text
Create a module to process and deduplicate RSVP data.

**File Location:** `/home/adam/nexco-dashboard/bin/rsvp_processor.py`

**Requirements:**

1. Create a dataclass `RSVPRecord`:
   ```python
   @dataclass
   class RSVPRecord:
       email: str
       first_name: str
       last_name: str
       meeting_date: date
       attended: bool
       company: str
       referring_member: str
       profession: str
       row_index: int  # for "last row wins" logic
   ```

2. Create a `parse_rsvps(rows: list[dict]) -> list[RSVPRecord]` function that:
   - Takes raw CSV rows from sheets_fetcher
   - Parses each row into RSVPRecord
   - Handles column names exactly: "Did they attend?", "First Name", "Last Name", "Email", "Chapter meeting date", "Company", "Name of referring member", "Profession"
   - Parses "TRUE"/"FALSE" strings to boolean
   - Parses date using date_utils
   - Skips rows with missing email or date
   - Tracks row index (0-based)

3. Create a `dedupe_rsvps(records: list[RSVPRecord]) -> list[RSVPRecord]` function that:
   - Deduplicates by composite key: (email.casefold(), meeting_date)
   - When duplicates exist, keeps the one with highest row_index ("last row wins")
   - Returns deduplicated list

4. Create a `filter_historical(records: list[RSVPRecord]) -> list[RSVPRecord]` function that:
   - Filters to only historical meetings (meeting_date < today)
   - Uses date_utils.is_historical()

5. Create a `split_by_attendance(records: list[RSVPRecord]) -> tuple[list, list]` function that:
   - Returns (attended_list, no_show_list)

6. Import from: `date_utils`

**Testing Requirements:**
Write tests in `/home/adam/nexco-dashboard/tests/test_rsvp_processor.py`:
- Test parsing valid rows
- Test handling missing fields
- Test deduplication (last row wins)
- Test attendance splitting
```

---

### Prompt 9: Guest Tracker Processor

```text
Create a module to process Guest Tracker data.

**File Location:** `/home/adam/nexco-dashboard/bin/guest_tracker_processor.py`

**Requirements:**

1. Create a dataclass `GuestTrackerRecord`:
   ```python
   @dataclass
   class GuestTrackerRecord:
       email: str | None  # Can be blank
       first_name: str
       last_name: str
       meeting_date: date
       company: str
       referring_member: str
       following_up: str  # Raw comma-separated string
       notes: str
       profession: str
       has_email: bool  # Computed field
   ```

2. Create a `parse_guest_tracker(rows: list[dict]) -> list[GuestTrackerRecord]` function that:
   - Takes raw CSV rows from sheets_fetcher
   - Parses each row into GuestTrackerRecord
   - Handles column names: "First Name", "Last Name", "Email", "Chapter meeting date", "Company", "Name of Referring Member", "Who's Following Up", "Notes", "Profession"
   - Sets `has_email = True` if email is non-empty after strip
   - Parses date using date_utils
   - Skips rows with missing date (email can be blank)

3. Create a `filter_historical(records: list[GuestTrackerRecord]) -> list[GuestTrackerRecord]` function that:
   - Filters to only historical meetings
   - Uses date_utils.is_historical()

4. Create a `build_lookup(records: list[GuestTrackerRecord]) -> dict` function that:
   - Returns dict keyed by (email.casefold(), meeting_date) for records with email
   - Used for merging with RSVP data

5. Import from: `date_utils`

**Testing Requirements:**
Write tests in `/home/adam/nexco-dashboard/tests/test_guest_tracker_processor.py`:
- Test parsing valid rows
- Test handling blank email
- Test lookup building
- Test historical filtering
```

---

### Prompt 10: Data Merger

```text
Create a module to merge RSVP and Guest Tracker data.

**File Location:** `/home/adam/nexco-dashboard/bin/data_merger.py`

**Requirements:**

1. Create a dataclass `MergedGuest`:
   ```python
   @dataclass
   class MergedGuest:
       name: str  # "First Last"
       email: str
       company: str
       referring_member: str
       following_up: str
       meeting_date: date
       display_date: str
       notes: str
       source: str  # "rsvp", "guest_tracker_only"
       attended: bool | None  # None for guest_tracker_only
       flags: list[str]  # ["missing_guest_tracker"] if applicable
   ```

2. Create a `merge_data(rsvps: list[RSVPRecord], guest_tracker: list[GuestTrackerRecord]) -> dict` function that returns:
   ```python
   {
       "attended": list[MergedGuest],
       "no_show": list[MergedGuest],
       "without_rsvp": list[MergedGuest]
   }
   ```

3. Merge logic:
   - Join key: (email.casefold(), meeting_date)
   - For each RSVP record:
     - Look up matching Guest Tracker record
     - If found: use GT's following_up, notes, referring_member
     - If not found: use RSVP data, add "missing_guest_tracker" flag
     - Place in "attended" or "no_show" based on RSVP.attended
   - For Guest Tracker records with no matching RSVP:
     - Only include if historical
     - Place in "without_rsvp"
     - These count as "attended" for chart purposes
   - Guest Tracker records with blank email:
     - Never merge (no key match possible)
     - Always go to "without_rsvp" if historical

4. Create `name` field by combining first_name + " " + last_name

5. Sort each list by: meeting_date DESC, then name ASC

6. Import from: `rsvp_processor`, `guest_tracker_processor`, `date_utils`

**Testing Requirements:**
Write tests in `/home/adam/nexco-dashboard/tests/test_data_merger.py`:
- Test successful merge
- Test RSVP without GT match (flag added)
- Test GT without RSVP match
- Test GT with blank email
- Test sorting order
```

---

### Prompt 11: Meeting Aggregator

```text
Create a module to aggregate meeting-level statistics.

**File Location:** `/home/adam/nexco-dashboard/bin/aggregator.py`

**Requirements:**

1. Create a dataclass `MeetingStats`:
   ```python
   @dataclass
   class MeetingStats:
       date: date
       display_date: str
       month_key: str  # "YYYY-MM"
       attended_count: int
       no_show_count: int
       rsvp_count: int  # Deduplicated RSVP count
   ```

2. Create a `aggregate_meetings(merged: dict, rsvps: list[RSVPRecord]) -> list[MeetingStats]` function that:
   - Collects all unique meeting dates from merged data
   - For each date:
     - Count attended (from "attended" + "without_rsvp" lists)
     - Count no-shows (from "no_show" list)
     - Count RSVPs (from deduplicated RSVP records for that date)
   - Sort by date DESC (newest first)
   - Return list of MeetingStats

3. Create a `get_available_months(meetings: list[MeetingStats]) -> list[str]` function that:
   - Returns unique month_key values
   - Sorted DESC (newest first)

4. Create a `build_chart_data(meetings: list[MeetingStats], month_key: str) -> dict` function that:
   - Filters meetings to the specified month
   - Returns Chart.js-compatible data structure:
   ```python
   {
       "labels": ["Jan 22, 2026", "Jan 8, 2026"],
       "datasets": [
           {"label": "Attended", "data": [5, 7], "backgroundColor": "#d0a848"},
           {"label": "No-Show", "data": [1, 2], "backgroundColor": "#9ca3af"}
       ]
   }
   ```

5. Create a `build_rsvp_counts(meetings: list[MeetingStats], month_key: str) -> list[dict]` function that:
   - Filters to specified month
   - Returns list of {"date": "Jan 8, 2026", "count": 12}
   - Include 0 counts for dates with no RSVPs

6. Import from: `date_utils`

**Testing Requirements:**
Write tests in `/home/adam/nexco-dashboard/tests/test_aggregator.py`:
- Test meeting aggregation
- Test month filtering
- Test chart data structure
- Test RSVP counts with zeros
```

---

### Prompt 12: Name Tokenizer and Normalizer

```text
Create a module for tokenizing and normalizing follow-up names.

**File Location:** `/home/adam/nexco-dashboard/bin/name_normalizer.py`

**Requirements:**

1. Create a `tokenize_followups(followup_str: str) -> list[str]` function that:
   - Splits on commas
   - Strips whitespace from each token
   - Removes empty tokens
   - Returns list of raw tokens
   - Example: "Dan, Adam (VP), " → ["Dan", "Adam (VP)"]

2. Create a `normalize_name(token: str) -> str` function that applies two-pass normalization:

   **Pass 1 (light):**
   - Strip leading/trailing whitespace
   - Collapse multiple internal spaces
   - Return result for matching attempt

   **Pass 2 (heavy, only if Pass 1 didn't match):**
   - Remove parenthetical content: `Dan (VP)` → `Dan`
   - Remove bracketed content: `Dan [VP]` → `Dan`
   - Remove trailing annotations after `-`, `—`, `–`, `:`
     - `Dan - VP` → `Dan`
     - `Terrie: follow up` → `Terrie`
   - Strip whitespace again
   - Return result

3. Use regex patterns:
   - Parentheses: `\([^()]*\)`
   - Brackets: `\[[^\[\]]*\]`
   - Trailing annotations: `[-—–:].+$`

4. Create a `casefold_normalize(name: str) -> str` function that:
   - Applies casefold() for case-insensitive matching
   - Strips whitespace

**Testing Requirements:**
Write tests in `/home/adam/nexco-dashboard/tests/test_name_normalizer.py`:
- Test tokenization
- Test light normalization
- Test heavy normalization (parentheses, brackets, annotations)
- Test hyphenated names preserved in Pass 1
```

---

### Prompt 13: Name Matcher

```text
Create a module for matching follow-up names to roster/aliases.

**File Location:** `/home/adam/nexco-dashboard/bin/name_matcher.py`

**Requirements:**

1. Create a `NameMatcher` class:
   ```python
   class NameMatcher:
       def __init__(self, roster: list[str], aliases: dict[str, str]):
           # Build lookup structures
           pass

       def match(self, token: str) -> tuple[str | None, str]:
           # Returns (canonical_name, match_type)
           # match_type: "alias", "roster", "first_name", "ambiguous", "unmatched"
           pass
   ```

2. Matching logic (in order):
   1. Check aliases first (casefolded key match)
   2. Check roster for exact full name match (casefolded)
   3. Check roster for unique first-name match (casefolded)
   4. If multiple first-name matches, return (None, "ambiguous")
   5. If no match, apply heavy normalization and retry steps 1-4
   6. If still no match, return (None, "unmatched")

3. The matcher should handle:
   - `"Dan"` → matches "Daniel Lyon" if Dan is unique first name
   - `"dan"` → same match (case-insensitive)
   - `"Dan (VP)"` → normalizes to "Dan", then matches
   - `"Anne-Marie"` → preserves hyphen in Pass 1, matches if in roster

4. Import from: `name_normalizer`

**Testing Requirements:**
Write tests in `/home/adam/nexco-dashboard/tests/test_name_matcher.py`:
- Test alias matching
- Test exact roster match
- Test unique first-name match
- Test ambiguous first-name (multiple matches)
- Test two-pass normalization
- Test unmatched token
```

---

### Prompt 14: Follow-Up Widget Calculator

```text
Create a module to calculate follow-up assignments per member.

**File Location:** `/home/adam/nexco-dashboard/bin/followup_widget.py`

**Requirements:**

1. Create a dataclass `FollowUpCount`:
   ```python
   @dataclass
   class FollowUpCount:
       name: str
       count: int
       is_special: bool  # True for Unassigned, Ambiguous
       is_raw_token: bool  # True for unmatched names
   ```

2. Create a `calculate_followups(guests: list[MergedGuest], matcher: NameMatcher) -> list[FollowUpCount]` function that:
   - Takes attended guests + guests_without_rsvp (combined)
   - For each guest, tokenize the `following_up` field
   - For each token, use matcher to get canonical name
   - Count occurrences per canonical name
   - Handle special cases:
     - Empty/blank following_up → increment "Unassigned"
     - Ambiguous match → increment "Ambiguous"
     - Unmatched → create bucket with raw token as name

3. Sorting:
   - Canonical names: alphabetically A-Z
   - At bottom (in order): Unassigned, Ambiguous, raw tokens (alphabetically)

4. Import from: `name_normalizer`, `name_matcher`, `data_merger`

**Testing Requirements:**
Write tests in `/home/adam/nexco-dashboard/tests/test_followup_widget.py`:
- Test normal counting
- Test unassigned bucket
- Test ambiguous bucket
- Test raw token bucket
- Test sorting order
```

---

### Prompt 15: JSON Builder

```text
Create a module to build the data.json structure.

**File Location:** `/home/adam/nexco-dashboard/bin/json_builder.py`

**Requirements:**

1. Create a `build_data_json(config: ChapterConfig, merged: dict, meetings: list[MeetingStats], open_seats: list[dict], followups: list[FollowUpCount], refresh_success: bool, error_message: str | None = None) -> dict` function that builds:

```python
{
    "metadata": {
        "chapter_slug": str,
        "display_name": str,
        "page_title": str,
        "last_updated": str,  # ISO 8601 UTC with Z
        "last_refresh_attempt": str,
        "refresh_status": "ok" | "error",
        "refresh_error": str | None
    },
    "available_months": list[str],  # ["2026-01", "2025-12"]
    "meetings": list[dict],  # MeetingStats as dicts
    "chart_data": dict,  # For current/latest month
    "rsvp_counts": list[dict],
    "open_seats": list[dict],  # Raw from sheet
    "follow_up_counts": list[dict],
    "guests": {
        "attended": list[dict],
        "no_show": list[dict],
        "without_rsvp": list[dict]
    }
}
```

2. Create timestamp helpers:
   - `get_utc_now_iso() -> str` - returns "2026-01-03T16:02:00Z"
   - Use datetime.now(timezone.utc)

3. Convert dataclasses to dicts using `asdict()` or manual conversion

4. Ensure all date objects are converted to strings

5. Import from: all processor modules, `config`

**Testing Requirements:**
Write tests in `/home/adam/nexco-dashboard/tests/test_json_builder.py`:
- Test full structure generation
- Test metadata fields
- Test timestamp format
- Test error state
```

---

### Prompt 16: Atomic File Writer

```text
Create a module for safely writing files atomically.

**File Location:** `/home/adam/nexco-dashboard/bin/file_writer.py`

**Requirements:**

1. Create an `atomic_write_json(data: dict, filepath: str) -> None` function that:
   - Creates parent directories if they don't exist
   - Writes to a temporary file in the same directory
   - Uses a unique temp filename (e.g., `.data.json.tmp.{pid}`)
   - Writes JSON with indent=2 for readability
   - Renames temp file to final filename atomically
   - This ensures readers never see partial/corrupt data

2. Create an `atomic_write_text(content: str, filepath: str) -> None` function that:
   - Same atomic pattern as above
   - For writing HTML files

3. Error handling:
   - If write fails, clean up temp file
   - Raise `WriteError` with details

4. Use only Python standard library (json, os, tempfile, pathlib).

**Testing Requirements:**
Write tests in `/home/adam/nexco-dashboard/tests/test_file_writer.py`:
- Test successful atomic write
- Test directory creation
- Test temp file cleanup on error
- Test atomic rename (file appears complete or not at all)
```

---

### Prompt 17: Index Page Generator

```text
Create a module to generate the chapter index HTML page.

**File Location:** `/home/adam/nexco-dashboard/bin/index_generator.py`

**Requirements:**

1. Create a `generate_index_html(chapters: list[ChapterConfig], output_path: str) -> None` function that:
   - Takes list of chapter configs
   - Generates HTML for the index page at /nexco-dashboard/
   - Writes using atomic_write_text

2. HTML structure:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>neXco Chapter Dashboards</title>
    <link rel="stylesheet" href="assets/css/styles.css">
</head>
<body>
    <header class="dashboard-header">
        <a href="https://nexconational.com/" target="_blank" rel="noopener noreferrer">
            <img src="assets/img/nexco-logo.png" alt="neXco National" class="logo">
        </a>
        <h1>neXco Chapter Dashboards</h1>
    </header>
    <main>
        <nav class="chapter-list">
            <ul>
                <!-- For each chapter, sorted alphabetically by display_name -->
                <li><a href="nexco-novacore/">NOVA Core (B2C)</a></li>
            </ul>
        </nav>
    </main>
</body>
</html>
```

3. Chapters must be sorted alphabetically by display_name

4. Import from: `config`, `file_writer`

**Testing Requirements:**
Write tests in `/home/adam/nexco-dashboard/tests/test_index_generator.py`:
- Test HTML structure
- Test alphabetical sorting
- Test proper escaping of display names
```

---

### Prompt 18: Main Refresh Script

```text
Create the main orchestrator script that ties all modules together.

**File Location:** `/home/adam/nexco-dashboard/bin/refresh.py`

**Requirements:**

1. Create the main refresh script that:
   - Loads all chapter configs from `/home/adam/nexco-dashboard/config/chapters/`
   - Sets up logging
   - For each chapter:
     - Fetches all three sheet tabs
     - Fetches roster page
     - Processes data through all modules
     - Builds data.json
     - Writes to public directory
   - Generates index.html
   - Logs results

2. Error handling per chapter:
   - If ANY sheet tab fails → full failure for that chapter
     - Keep existing data.json
     - Log error
   - If roster scrape fails → partial success
     - Continue processing
     - Skip name matching (use raw tokens)
     - Log warning

3. Public paths:
   - Base: `/home/adam/public_html/leadershipshape/nexco-dashboard/`
   - Chapter: `{base}/{chapter_slug}/data.json`
   - Index: `{base}/index.html`

4. Script should be executable:
   ```python
   #!/usr/bin/env python3
   if __name__ == "__main__":
       main()
   ```

5. Create a `RefreshResult` to track per-chapter results:
   ```python
   @dataclass
   class RefreshResult:
       chapter_slug: str
       success: bool
       error: str | None
       duration_seconds: float
   ```

6. Print summary at end:
   ```
   Refresh completed:
   - nexco-novacore: SUCCESS (2.3s)
   - nexco-reston: FAILED - HTTP 404 on RSVPs tab
   ```

7. Import from: all modules created so far

**Testing Requirements:**
Write integration tests in `/home/adam/nexco-dashboard/tests/test_refresh.py`:
- Test full pipeline with mocked network calls
- Test error handling (tab fetch failure)
- Test partial success (roster failure)
```

---

### Prompt 19: Download and Vendor Chart.js

```text
Download Chart.js and set up the vendor directory.

**Requirements:**

1. Download Chart.js v4.5.1 from npm/CDN:
   - Get `chart.umd.min.js` from the official distribution
   - URL: `https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js`

2. Save to: `/home/adam/public_html/leadershipshape/nexco-dashboard/assets/vendor/chartjs/4.5.1/chart.umd.min.js`

3. Create a LICENSE.md file in the same directory with Chart.js MIT license:
```markdown
# Chart.js License

MIT License

Copyright (c) 2014-2024 Chart.js Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

4. Verify the file is valid JavaScript by checking it starts with expected content.

**Output:**
- chart.umd.min.js (minified JS)
- LICENSE.md (MIT license text)
```

---

### Prompt 20: Create CSS Theme File

```text
Create the CSS stylesheet with neXco branding.

**File Location:** `/home/adam/public_html/leadershipshape/nexco-dashboard/assets/css/styles.css`

**Requirements:**

1. Define CSS custom properties (variables):
```css
:root {
    /* neXco Brand Colors */
    --color-navy: #102048;
    --color-gold: #d0a848;

    /* Chart Colors */
    --color-attended: #d0a848;
    --color-no-show: #9ca3af;

    /* UI Colors */
    --color-background: #ffffff;
    --color-text: #1f2937;
    --color-text-muted: #6b7280;
    --color-border: #e5e7eb;
    --color-warning: #f59e0b;
    --color-error: #ef4444;

    /* Spacing */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
}
```

2. Base styles:
   - Modern CSS reset
   - System font stack
   - Box-sizing border-box

3. Header styles:
   - Logo max-height: 50px
   - H1 uses navy color
   - Flexbox layout

4. Table styles:
   - Striped rows
   - Navy header background with white text
   - Hover states
   - Border styling

5. Filter input styles:
   - Full width
   - Padding
   - Border with focus state

6. Badge styles:
   - Small pill-shaped badges
   - "Missing in Guest Tracker" badge style

7. Chart container styles:
   - Max-width constraint
   - Centered

8. Status notice styles:
   - Warning background for stale data
   - Info style for month auto-jump

9. Month selector styles:
   - Native input styling
   - Fallback dropdown styling

10. Responsive considerations:
    - Mobile-friendly tables (horizontal scroll)
    - Readable font sizes

**Output:**
Complete, production-ready CSS file.
```

---

### Prompt 21: Create Chapter Dashboard HTML Template

```text
Create the HTML template for individual chapter dashboards.

**File Location:** `/home/adam/public_html/leadershipshape/nexco-dashboard/nexco-novacore/index.html`

**Requirements:**

1. HTML5 structure with proper semantic elements:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>neXco NOVA Core Dashboard</title>
    <link rel="stylesheet" href="../assets/css/styles.css">
</head>
<body>
    <header class="dashboard-header">
        <a href="https://nexconational.com/" target="_blank" rel="noopener noreferrer">
            <img src="../assets/img/nexco-logo.png" alt="neXco National" class="logo">
        </a>
        <h1 id="page-title">Loading...</h1>
    </header>

    <main>
        <!-- Month Selector Row -->
        <section class="controls-row">
            <div class="month-selector-container">
                <!-- Primary: native month input -->
                <input type="month" id="month-picker" aria-label="Select month">
                <!-- Fallback: dropdowns for Firefox -->
                <div id="month-fallback" class="hidden">
                    <select id="month-select" aria-label="Month"></select>
                    <select id="year-select" aria-label="Year"></select>
                </div>
            </div>
            <div class="meta-info">
                <span id="last-updated"></span>
                <span id="stale-warning" class="warning hidden"></span>
            </div>
        </section>

        <!-- Status Notice -->
        <div id="status-notice" role="status" aria-live="polite" class="hidden"></div>

        <!-- Chart Section -->
        <section class="chart-section">
            <div class="chart-legend">
                <span class="legend-item"><span class="color-box attended"></span> Attended</span>
                <span class="legend-item"><span class="color-box no-show"></span> No-Show</span>
            </div>
            <canvas id="attendance-chart"></canvas>
        </section>

        <!-- RSVP Counts -->
        <section class="rsvp-counts-section">
            <h2>RSVP Counts</h2>
            <ul id="rsvp-counts-list"></ul>
        </section>

        <!-- Follow-Up Widget -->
        <section class="followup-section">
            <h2>Follow-Ups Assigned</h2>
            <ul id="followup-list"></ul>
        </section>

        <!-- Open Seats -->
        <section class="open-seats-section">
            <h2>Top Open Seats</h2>
            <table id="open-seats-table"></table>
        </section>

        <!-- Guest Tables -->
        <section class="guests-section">
            <h2>Attended Guests</h2>
            <input type="text" id="attended-filter" placeholder="Filter..." class="table-filter">
            <table id="attended-table"></table>
        </section>

        <section class="guests-section">
            <h2>No-Shows</h2>
            <input type="text" id="no-show-filter" placeholder="Filter..." class="table-filter">
            <table id="no-show-table"></table>
        </section>

        <section class="guests-section">
            <h2>Guests without RSVPs</h2>
            <input type="text" id="without-rsvp-filter" placeholder="Filter..." class="table-filter">
            <table id="without-rsvp-table"></table>
        </section>
    </main>

    <script src="../assets/vendor/chartjs/4.5.1/chart.umd.min.js"></script>
    <script src="../assets/js/dashboard.js"></script>
</body>
</html>
```

2. Accessibility requirements:
   - Proper ARIA labels
   - role="status" for notices
   - Semantic HTML elements

3. Script loading:
   - Chart.js loaded before dashboard.js
   - Scripts at end of body

**Output:**
Complete HTML file ready for JavaScript hydration.
```

---

### Prompt 22: Data Loader Module (JavaScript)

```text
Create the JavaScript module for loading and managing dashboard data.

**File Location:** `/home/adam/public_html/leadershipshape/nexco-dashboard/assets/js/dashboard.js`

**Requirements for this prompt:**
Focus ONLY on data loading. Other features will be added in subsequent prompts.

1. Create a data loading function:
```javascript
async function loadDashboardData() {
    const response = await fetch('data.json');
    if (!response.ok) {
        throw new Error(`Failed to load data: ${response.status}`);
    }
    return response.json();
}
```

2. Create a global state object:
```javascript
const DashboardState = {
    data: null,
    selectedMonth: null,
    chart: null
};
```

3. Create initialization function:
```javascript
async function initDashboard() {
    try {
        DashboardState.data = await loadDashboardData();
        updatePageTitle();
        checkStaleData();
        initMonthSelector();
        // Other init functions will be added
    } catch (error) {
        showError('Failed to load dashboard data');
        console.error(error);
    }
}
```

4. Create helper functions:
```javascript
function updatePageTitle() {
    document.getElementById('page-title').textContent =
        DashboardState.data.metadata.page_title;
    document.title = DashboardState.data.metadata.page_title;
}

function formatLastUpdated(isoString) {
    // Convert UTC ISO string to "Jan 3, 2026 11:02 AM ET"
    const date = new Date(isoString);
    return new Intl.DateTimeFormat('en-US', {
        timeZone: 'America/New_York',
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    }).format(date) + ' ET';
}

function checkStaleData() {
    const lastUpdated = new Date(DashboardState.data.metadata.last_updated);
    const now = new Date();
    const daysDiff = (now - lastUpdated) / (1000 * 60 * 60 * 24);

    if (daysDiff > 8) {
        const warning = document.getElementById('stale-warning');
        warning.textContent = 'Data may be stale (last updated more than 8 days ago)';
        warning.classList.remove('hidden');
    }

    document.getElementById('last-updated').textContent =
        'Last updated: ' + formatLastUpdated(DashboardState.data.metadata.last_updated);
}

function showError(message) {
    // Display error to user
    const notice = document.getElementById('status-notice');
    notice.textContent = message;
    notice.classList.add('error');
    notice.classList.remove('hidden');
}
```

5. Initialize on DOM ready:
```javascript
document.addEventListener('DOMContentLoaded', initDashboard);
```

**Output:**
Partial dashboard.js with data loading functionality. Will be extended in subsequent prompts.
```

---

### Prompt 23: Month Selector with Firefox Fallback (JavaScript)

```text
Extend dashboard.js with month selector functionality including Firefox fallback.

**File Location:** `/home/adam/public_html/leadershipshape/nexco-dashboard/assets/js/dashboard.js`

**Requirements:**

1. Add feature detection for month input:
```javascript
function supportsMonthInput() {
    const input = document.createElement('input');
    input.setAttribute('type', 'month');
    return input.type === 'month';
}
```

2. Create month selector initialization:
```javascript
function initMonthSelector() {
    const availableMonths = DashboardState.data.available_months;

    if (availableMonths.length === 0) {
        showError('No historical meeting data available');
        return;
    }

    // Default to most recent month
    DashboardState.selectedMonth = availableMonths[0];

    if (supportsMonthInput()) {
        initNativeMonthPicker(availableMonths);
    } else {
        initFallbackDropdowns(availableMonths);
    }

    // Initial render
    renderForMonth(DashboardState.selectedMonth);
}
```

3. Native month picker:
```javascript
function initNativeMonthPicker(availableMonths) {
    const picker = document.getElementById('month-picker');
    document.getElementById('month-fallback').classList.add('hidden');

    // Set min/max based on available data
    const years = [...new Set(availableMonths.map(m => m.split('-')[0]))];
    picker.min = `${Math.min(...years)}-01`;
    picker.max = availableMonths[0]; // Most recent
    picker.value = DashboardState.selectedMonth;

    picker.addEventListener('change', handleMonthChange);
}
```

4. Firefox fallback dropdowns:
```javascript
function initFallbackDropdowns(availableMonths) {
    document.getElementById('month-picker').classList.add('hidden');
    document.getElementById('month-fallback').classList.remove('hidden');

    const monthSelect = document.getElementById('month-select');
    const yearSelect = document.getElementById('year-select');

    // Populate months (Jan-Dec)
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                        'July', 'August', 'September', 'October', 'November', 'December'];
    monthNames.forEach((name, i) => {
        const opt = document.createElement('option');
        opt.value = String(i + 1).padStart(2, '0');
        opt.textContent = name;
        monthSelect.appendChild(opt);
    });

    // Populate years (current down to 2023, newest first)
    const currentYear = new Date().getFullYear();
    for (let year = currentYear; year >= 2023; year--) {
        const opt = document.createElement('option');
        opt.value = year;
        opt.textContent = year;
        yearSelect.appendChild(opt);
    }

    // Set initial values
    const [year, month] = DashboardState.selectedMonth.split('-');
    yearSelect.value = year;
    monthSelect.value = month;

    monthSelect.addEventListener('change', handleFallbackChange);
    yearSelect.addEventListener('change', handleFallbackChange);
}

function handleFallbackChange() {
    const month = document.getElementById('month-select').value;
    const year = document.getElementById('year-select').value;
    handleMonthChange({ target: { value: `${year}-${month}` }});
}
```

5. Month change handler with auto-jump:
```javascript
function handleMonthChange(event) {
    const selectedMonth = event.target.value;
    const availableMonths = DashboardState.data.available_months;

    if (!availableMonths.includes(selectedMonth)) {
        // Auto-jump to most recent valid month
        const validMonth = availableMonths[0];
        DashboardState.selectedMonth = validMonth;

        // Show notice
        const notice = document.getElementById('status-notice');
        notice.textContent = `No historical meetings in ${formatMonthDisplay(selectedMonth)} — showing ${formatMonthDisplay(validMonth)} instead.`;
        notice.classList.remove('hidden');

        // Update picker to show valid month
        if (supportsMonthInput()) {
            document.getElementById('month-picker').value = validMonth;
        } else {
            const [year, month] = validMonth.split('-');
            document.getElementById('year-select').value = year;
            document.getElementById('month-select').value = month;
        }
    } else {
        DashboardState.selectedMonth = selectedMonth;
        document.getElementById('status-notice').classList.add('hidden');
    }

    renderForMonth(DashboardState.selectedMonth);
}

function formatMonthDisplay(monthKey) {
    const [year, month] = monthKey.split('-');
    const date = new Date(year, parseInt(month) - 1, 1);
    return new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric' }).format(date);
}
```

6. Placeholder for render function (to be implemented):
```javascript
function renderForMonth(monthKey) {
    // Will render chart, tables, etc.
    console.log('Rendering for month:', monthKey);
}
```

**Output:**
Extended dashboard.js with complete month selector functionality.
```

---

### Prompt 24: Chart Rendering (JavaScript)

```text
Extend dashboard.js with Chart.js bar chart rendering.

**File Location:** `/home/adam/public_html/leadershipshape/nexco-dashboard/assets/js/dashboard.js`

**Requirements:**

1. Create chart initialization function:
```javascript
function initChart() {
    const ctx = document.getElementById('attendance-chart').getContext('2d');

    DashboardState.chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Attended',
                    data: [],
                    backgroundColor: '#d0a848',
                    stack: 'stack0'
                },
                {
                    label: 'No-Show',
                    data: [],
                    backgroundColor: '#9ca3af',
                    stack: 'stack0'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false  // We use custom inline labels
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw}`;
                        },
                        afterBody: function(tooltipItems) {
                            const attended = tooltipItems[0]?.raw || 0;
                            const noShow = tooltipItems[1]?.raw || 0;
                            return `Attended: ${attended}, No-Show: ${noShow}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    stacked: true,
                    grid: {
                        display: false
                    }
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}
```

2. Create chart update function:
```javascript
function updateChart(monthKey) {
    // Filter meetings for selected month
    const meetings = DashboardState.data.meetings.filter(m =>
        m.month_key === monthKey
    );

    // Sort by date (newest first - reversed for chart display)
    meetings.sort((a, b) => new Date(b.date) - new Date(a.date));

    // Build chart data
    const labels = meetings.map(m => m.display_date);
    const attendedData = meetings.map(m => m.attended_count);
    const noShowData = meetings.map(m => m.no_show_count);

    // Update chart
    DashboardState.chart.data.labels = labels;
    DashboardState.chart.data.datasets[0].data = attendedData;
    DashboardState.chart.data.datasets[1].data = noShowData;
    DashboardState.chart.update();
}
```

3. Update initDashboard to call initChart:
```javascript
// Add after checkStaleData():
initChart();
```

4. Update renderForMonth to call updateChart:
```javascript
function renderForMonth(monthKey) {
    updateChart(monthKey);
    // Other render functions will be added
}
```

**Output:**
Extended dashboard.js with Chart.js integration.
```

---

### Prompt 25: Table Rendering with Filtering (JavaScript)

```text
Extend dashboard.js with table rendering and filtering functionality.

**File Location:** `/home/adam/public_html/leadershipshape/nexco-dashboard/assets/js/dashboard.js`

**Requirements:**

1. Create table renderer:
```javascript
function renderGuestTable(tableId, guests, filterId) {
    const table = document.getElementById(tableId);

    // Build header
    const headers = ['Guest Name', 'Company', 'Email', 'Referring Member',
                     "Who's Following Up", 'Meeting Date', 'Notes'];

    let html = '<thead><tr>';
    headers.forEach(h => html += `<th>${h}</th>`);
    html += '</tr></thead><tbody>';

    // Build rows
    guests.forEach(guest => {
        const nameWithBadge = guest.flags?.includes('missing_guest_tracker')
            ? `${guest.name} <span class="badge warning">Missing in Guest Tracker</span>`
            : guest.name;

        html += '<tr>';
        html += `<td>${nameWithBadge}</td>`;
        html += `<td>${escapeHtml(guest.company || '')}</td>`;
        html += `<td>${escapeHtml(guest.email || '')}</td>`;
        html += `<td>${escapeHtml(guest.referring_member || '')}</td>`;
        html += `<td>${escapeHtml(guest.following_up || '')}</td>`;
        html += `<td>${guest.display_date}</td>`;
        html += `<td>${escapeHtml(guest.notes || '')}</td>`;
        html += '</tr>';
    });

    html += '</tbody>';
    table.innerHTML = html;

    // Store original data for filtering
    table.dataset.guests = JSON.stringify(guests);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

2. Create filter functionality:
```javascript
function initTableFilters() {
    const filterConfigs = [
        { filterId: 'attended-filter', tableId: 'attended-table' },
        { filterId: 'no-show-filter', tableId: 'no-show-table' },
        { filterId: 'without-rsvp-filter', tableId: 'without-rsvp-table' }
    ];

    filterConfigs.forEach(({ filterId, tableId }) => {
        const filter = document.getElementById(filterId);
        filter.addEventListener('input', () => handleFilter(filterId, tableId));
    });
}

function handleFilter(filterId, tableId) {
    const filterValue = document.getElementById(filterId).value;
    const table = document.getElementById(tableId);
    const guests = JSON.parse(table.dataset.guests || '[]');

    const filtered = filterGuests(guests, filterValue);
    renderFilteredTable(tableId, filtered);
}

function filterGuests(guests, query) {
    if (!query.trim()) return guests;

    // Parse query into terms (handle quoted phrases)
    const terms = parseFilterTerms(query);

    return guests.filter(guest => {
        const searchText = [
            guest.name,
            guest.following_up,
            guest.display_date,
            guest.referring_member
        ].join(' ').toLowerCase();

        // AND logic: all terms must match
        return terms.every(term => searchText.includes(term.toLowerCase()));
    });
}

function parseFilterTerms(query) {
    const terms = [];
    // Match quoted phrases (single or double) and unquoted words
    const regex = /["']([^"']+)["']|(\S+)/g;
    let match;

    while ((match = regex.exec(query)) !== null) {
        terms.push(match[1] || match[2]);
    }

    return terms;
}

function renderFilteredTable(tableId, guests) {
    const table = document.getElementById(tableId);
    const tbody = table.querySelector('tbody');

    if (!tbody) return;

    const headers = ['name', 'company', 'email', 'referring_member',
                     'following_up', 'display_date', 'notes'];

    let html = '';
    guests.forEach(guest => {
        const nameWithBadge = guest.flags?.includes('missing_guest_tracker')
            ? `${guest.name} <span class="badge warning">Missing in Guest Tracker</span>`
            : guest.name;

        html += '<tr>';
        html += `<td>${nameWithBadge}</td>`;
        html += `<td>${escapeHtml(guest.company || '')}</td>`;
        html += `<td>${escapeHtml(guest.email || '')}</td>`;
        html += `<td>${escapeHtml(guest.referring_member || '')}</td>`;
        html += `<td>${escapeHtml(guest.following_up || '')}</td>`;
        html += `<td>${guest.display_date}</td>`;
        html += `<td>${escapeHtml(guest.notes || '')}</td>`;
        html += '</tr>';
    });

    tbody.innerHTML = html;
}
```

3. Add to initDashboard:
```javascript
initTableFilters();
```

**Output:**
Extended dashboard.js with table rendering and filtering.
```

---

### Prompt 26: RSVP Counts and Follow-Up Widget Renderers (JavaScript)

```text
Extend dashboard.js with RSVP counts list and follow-up widget rendering.

**File Location:** `/home/adam/public_html/leadershipshape/nexco-dashboard/assets/js/dashboard.js`

**Requirements:**

1. Create RSVP counts renderer:
```javascript
function renderRsvpCounts(monthKey) {
    const list = document.getElementById('rsvp-counts-list');

    // Get meetings for selected month
    const meetings = DashboardState.data.meetings.filter(m =>
        m.month_key === monthKey
    );

    // Sort newest first
    meetings.sort((a, b) => new Date(b.date) - new Date(a.date));

    let html = '';
    meetings.forEach(meeting => {
        html += `<li><strong>${meeting.display_date}</strong>: ${meeting.rsvp_count} RSVPs</li>`;
    });

    if (meetings.length === 0) {
        html = '<li>No meetings in selected month</li>';
    }

    list.innerHTML = html;
}
```

2. Create follow-up widget renderer:
```javascript
function renderFollowUpWidget() {
    const list = document.getElementById('followup-list');
    const counts = DashboardState.data.follow_up_counts;

    let html = '';
    counts.forEach(item => {
        let className = '';
        if (item.is_special) className = 'special';
        if (item.is_raw_token) className = 'raw-token';

        html += `<li class="${className}"><strong>${escapeHtml(item.name)}</strong>: ${item.count}</li>`;
    });

    if (counts.length === 0) {
        html = '<li>No follow-up data available</li>';
    }

    list.innerHTML = html;
}
```

3. Create open seats table renderer:
```javascript
function renderOpenSeats() {
    const table = document.getElementById('open-seats-table');
    const seats = DashboardState.data.open_seats;

    if (!seats || seats.length === 0) {
        table.innerHTML = '<tr><td>No open seats data available</td></tr>';
        return;
    }

    // Get headers from first row keys
    const headers = Object.keys(seats[0]);

    let html = '<thead><tr>';
    headers.forEach(h => html += `<th>${escapeHtml(h)}</th>`);
    html += '</tr></thead><tbody>';

    seats.forEach(row => {
        html += '<tr>';
        headers.forEach(h => html += `<td>${escapeHtml(row[h] || '')}</td>`);
        html += '</tr>';
    });

    html += '</tbody>';
    table.innerHTML = html;
}
```

4. Update renderForMonth to include all renderers:
```javascript
function renderForMonth(monthKey) {
    updateChart(monthKey);
    renderRsvpCounts(monthKey);
    renderGuestTables(monthKey);
}

function renderGuestTables(monthKey) {
    const guests = DashboardState.data.guests;

    // Filter by month
    const filterByMonth = (list) => list.filter(g => {
        const guestMonth = g.meeting_date.substring(0, 7); // "YYYY-MM"
        return guestMonth === monthKey;
    });

    renderGuestTable('attended-table', filterByMonth(guests.attended), 'attended-filter');
    renderGuestTable('no-show-table', filterByMonth(guests.no_show), 'no-show-filter');
    renderGuestTable('without-rsvp-table', filterByMonth(guests.without_rsvp), 'without-rsvp-filter');
}
```

5. Update initDashboard to render static widgets:
```javascript
// Add after initMonthSelector():
renderFollowUpWidget();
renderOpenSeats();
```

**Output:**
Extended dashboard.js with all widget renderers.
```

---

### Prompt 27: Complete Dashboard Integration (JavaScript)

```text
Finalize dashboard.js ensuring all components work together.

**File Location:** `/home/adam/public_html/leadershipshape/nexco-dashboard/assets/js/dashboard.js`

**Requirements:**

1. Review and ensure all functions are properly ordered and connected.

2. Final initDashboard function:
```javascript
async function initDashboard() {
    try {
        // Load data
        DashboardState.data = await loadDashboardData();

        // Update page metadata
        updatePageTitle();
        checkStaleData();

        // Initialize interactive components
        initChart();
        initMonthSelector();
        initTableFilters();

        // Render static components (not month-dependent)
        renderFollowUpWidget();
        renderOpenSeats();

        // Initial render for default month (handled by initMonthSelector)

    } catch (error) {
        showError('Failed to load dashboard data. Please try again later.');
        console.error('Dashboard initialization error:', error);
    }
}
```

3. Add loading state handling:
```javascript
function showLoading() {
    document.body.classList.add('loading');
}

function hideLoading() {
    document.body.classList.remove('loading');
}
```

4. Add CSS for loading state to styles.css:
```css
.loading main {
    opacity: 0.5;
    pointer-events: none;
}
```

5. Ensure proper error boundaries:
```javascript
function safeRender(fn, errorMsg) {
    try {
        fn();
    } catch (error) {
        console.error(errorMsg, error);
    }
}
```

6. Final verification checklist:
   - [ ] Data loads correctly
   - [ ] Page title updates
   - [ ] Stale warning shows when appropriate
   - [ ] Month selector works (both native and fallback)
   - [ ] Auto-jump works for invalid months
   - [ ] Chart renders and updates
   - [ ] All three guest tables render
   - [ ] Table filters work with AND logic and quotes
   - [ ] RSVP counts update by month
   - [ ] Follow-up widget displays
   - [ ] Open seats table displays

**Output:**
Complete, production-ready dashboard.js file.
```

---

### Prompt 28: End-to-End Testing and Deployment

```text
Create test fixtures and deployment scripts.

**Requirements:**

1. Create sample test data at `/home/adam/nexco-dashboard/tests/fixtures/sample_data.json`:
   - Include realistic data for all sections
   - Include edge cases (blank emails, missing GT matches)

2. Create a manual testing script at `/home/adam/nexco-dashboard/bin/test_local.py`:
   - Loads sample data
   - Runs through all processors
   - Outputs to a test directory
   - Useful for local development

3. Create deployment script at `/home/adam/nexco-dashboard/bin/deploy.sh`:
```bash
#!/bin/bash
set -e

# Paths
PROJECT_DIR="/home/adam/nexco-dashboard"
PUBLIC_DIR="/home/adam/public_html/leadershipshape/nexco-dashboard"

echo "Running refresh..."
python3 "$PROJECT_DIR/bin/refresh.py"

echo "Verifying output..."
for chapter_dir in "$PUBLIC_DIR"/nexco-*/; do
    if [ -f "$chapter_dir/data.json" ]; then
        echo "  ✓ $(basename $chapter_dir)/data.json exists"
    else
        echo "  ✗ $(basename $chapter_dir)/data.json MISSING"
        exit 1
    fi
done

echo "Deployment complete!"
```

4. Create cron installation script at `/home/adam/nexco-dashboard/bin/install_cron.sh`:
```bash
#!/bin/bash

CRON_LINE='CRON_TZ=America/New_York
0 11 * * 4 /usr/bin/python3 /home/adam/nexco-dashboard/bin/refresh.py >> /home/adam/nexco-dashboard/logs/cron.log 2>&1'

# Check if already installed
if crontab -l 2>/dev/null | grep -q "nexco-dashboard"; then
    echo "Cron job already exists"
else
    (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
    echo "Cron job installed"
fi

echo "Current crontab:"
crontab -l
```

5. Verify all unit tests pass:
```bash
python3 -m pytest /home/adam/nexco-dashboard/tests/ -v
```

**Output:**
- Test fixtures
- Local testing script
- Deployment script
- Cron installation script
- All tests passing
```



