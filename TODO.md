# neXco Chapter Dashboard - Implementation Checklist

Use this file to track implementation progress. Mark items with `[x]` when complete.

---

## Phase 1: Project Foundation

### Step 1: Directory Structure
- [x] Create public web directory structure at `/home/adam/public_html/leadershipshape/nexco-dashboard/`
- [x] Create non-public working directory at `/home/adam/nexco-dashboard/`
- [x] Execute and verify directories exist

### Step 2: Config Schema and Loader
- [x] Create `/home/adam/nexco-dashboard/bin/config.py`
- [x] Implement `ChapterConfig` dataclass
- [x] Implement `load_config()` function
- [x] Implement `load_all_configs()` function
- [x] Implement `extract_spreadsheet_id()` helper

### Step 3: Logging Infrastructure
- [x] Create `/home/adam/nexco-dashboard/bin/logger.py`
- [x] Implement `setup_logger()` with file and console handlers
- [x] Implement weekly log rotation (keep 12 weeks)
- [x] Create helper functions for chapter logging

### Step 4: Example Chapter Config
- [x] Create `/home/adam/nexco-dashboard/config/chapters/nexco-novacore.json`
- [x] Create `/home/adam/nexco-dashboard/bin/validate_config.py`
- [x] Verify config loads correctly

---

## Phase 2: Data Fetching

### Step 5: Google Sheets CSV Fetcher
- [x] Create `/home/adam/nexco-dashboard/bin/sheets_fetcher.py`
- [x] Implement `fetch_sheet_csv()` function
- [x] Implement `FetchError` exception
- [x] Implement `fetch_chapter_tabs()` convenience function

### Step 6: Roster Page Scraper
- [x] Create `/home/adam/nexco-dashboard/bin/roster_scraper.py`
- [x] Implement `scrape_roster()` function
- [x] Implement `ScrapeError` exception
- [x] Implement `build_roster_lookup()` function

---

## Phase 3: Data Processing

### Step 7: Date Utilities
- [x] Create `/home/adam/nexco-dashboard/bin/date_utils.py`
- [x] Implement `parse_meeting_date()` function
- [x] Implement `format_display_date()` function
- [x] Implement `get_today_eastern()` function
- [x] Implement `is_historical()` function
- [x] Implement `get_month_key()` function
- [x] Implement `get_display_month()` function

### Step 8: RSVP Processor
- [x] Create `/home/adam/nexco-dashboard/bin/rsvp_processor.py`
- [x] Implement `RSVPRecord` dataclass
- [x] Implement `parse_rsvps()` function
- [x] Implement `dedupe_rsvps()` function
- [x] Implement `filter_historical()` function
- [x] Implement `split_by_attendance()` function

### Step 9: Guest Tracker Processor
- [x] Create `/home/adam/nexco-dashboard/bin/guest_tracker_processor.py`
- [x] Implement `GuestTrackerRecord` dataclass
- [x] Implement `parse_guest_tracker()` function
- [x] Implement `filter_historical()` function
- [x] Implement `build_lookup()` function

### Step 10: Data Merger
- [x] Create `/home/adam/nexco-dashboard/bin/data_merger.py`
- [x] Implement `MergedGuest` dataclass
- [x] Implement `merge_data()` function with all edge cases

### Step 11: Meeting Aggregator
- [x] Create `/home/adam/nexco-dashboard/bin/aggregator.py`
- [x] Implement `MeetingStats` dataclass
- [x] Implement `aggregate_meetings()` function
- [x] Implement `get_available_months()` function
- [x] Implement `build_chart_data()` function
- [x] Implement `build_rsvp_counts()` function

---

## Phase 4: Follow-Up Widget

### Step 12: Name Tokenizer and Normalizer
- [x] Create `/home/adam/nexco-dashboard/bin/name_normalizer.py`
- [x] Implement `tokenize_followups()` function
- [x] Implement `normalize_name()` with two-pass logic
- [x] Implement `casefold_normalize()` function

### Step 13: Name Matcher
- [x] Create `/home/adam/nexco-dashboard/bin/name_matcher.py`
- [x] Implement `NameMatcher` class
- [x] Implement matching logic (alias -> roster -> first name -> ambiguous)

### Step 14: Follow-Up Widget Calculator
- [x] Create `/home/adam/nexco-dashboard/bin/followup_widget.py`
- [x] Implement `FollowUpCount` dataclass
- [x] Implement `calculate_followups()` function
- [x] Implement sorting logic (canonical -> special -> raw)

---

## Phase 5: Output Generation

### Step 15: JSON Builder
- [x] Create `/home/adam/nexco-dashboard/bin/json_builder.py`
- [x] Implement `build_data_json()` function
- [x] Implement timestamp helpers
- [x] Implement dataclass to dict conversion

### Step 16: Atomic File Writer
- [x] Create `/home/adam/nexco-dashboard/bin/file_writer.py`
- [x] Implement `atomic_write_json()` function
- [x] Implement `atomic_write_text()` function
- [x] Implement `WriteError` exception
- [x] Set web-accessible permissions (644) on output files

### Step 17: Index Page Generator
- [x] Create `/home/adam/nexco-dashboard/bin/index_generator.py`
- [x] Implement `generate_index_html()` function
- [x] Verify alphabetical sorting
- [x] Verify HTML escaping

### Step 18: Main Refresh Script
- [x] Create `/home/adam/nexco-dashboard/bin/refresh.py`
- [x] Implement main orchestration logic
- [x] Implement per-chapter error handling
- [x] Implement `RefreshResult` tracking
- [x] Implement summary output

---

## Phase 6: Frontend Foundation

### Step 19: Vendor Chart.js
- [x] Download Chart.js v4.5.1 UMD build
- [x] Save to `/home/adam/public_html/leadershipshape/nexco-dashboard/assets/vendor/chartjs/4.5.1/`
- [x] Create LICENSE.md with MIT license
- [x] Verify file is valid JavaScript

### Step 20: CSS Theme File
- [x] Create `/home/adam/public_html/leadershipshape/nexco-dashboard/assets/css/styles.css`
- [x] Define CSS custom properties (neXco colors)
- [x] Implement base styles (reset, fonts)
- [x] Implement header styles
- [x] Implement table styles
- [x] Implement filter input styles
- [x] Implement badge styles
- [x] Implement chart container styles
- [x] Implement status notice styles
- [x] Implement month selector styles
- [x] Implement responsive styles

### Step 21: Chapter Dashboard HTML
- [x] Create `/home/adam/public_html/leadershipshape/nexco-dashboard/nexco-novacore/index.html`
- [x] Implement semantic HTML structure
- [x] Add accessibility attributes (ARIA)
- [x] Verify script loading order

---

## Phase 7: Frontend Core

### Step 22: Data Loader (JavaScript)
- [x] Create `/home/adam/public_html/leadershipshape/nexco-dashboard/assets/js/dashboard.js`
- [x] Implement `loadDashboardData()` function
- [x] Implement `DashboardState` object
- [x] Implement `initDashboard()` function
- [x] Implement `updatePageTitle()` function
- [x] Implement `formatLastUpdated()` function
- [x] Implement `checkStaleData()` function
- [x] Implement `showError()` function

### Step 23: Month Selector
- [x] Implement `supportsMonthInput()` feature detection
- [x] Implement `initMonthSelector()` function
- [x] Implement `initNativeMonthPicker()` function
- [x] Implement `initFallbackDropdowns()` function
- [x] Implement `handleMonthChange()` with auto-jump
- [x] Implement `formatMonthDisplay()` helper

### Step 24: Chart Rendering
- [x] Implement `initChart()` function
- [x] Implement `updateChart()` function
- [x] Configure Chart.js options (stacked, tooltips)
- [x] Wire to `renderForMonth()`

---

## Phase 8: Frontend Tables & Widgets

### Step 25: Table Rendering
- [x] Implement `renderGuestTable()` function
- [x] Implement `escapeHtml()` helper
- [x] Implement `initTableFilters()` function
- [x] Implement `handleFilter()` function
- [x] Implement `filterGuests()` with AND logic
- [x] Implement `parseFilterTerms()` for quoted phrases
- [x] Implement `renderFilteredTable()` function

### Step 26: Widgets
- [x] Implement `renderRsvpCounts()` function
- [x] Implement `renderFollowUpWidget()` function
- [x] Implement `renderOpenSeats()` function
- [x] Implement `renderGuestTables()` function
- [x] Wire to `renderForMonth()`

### Step 27: Final Integration
- [x] Verify all functions are connected
- [x] Add loading state handling
- [x] Add error boundaries
- [x] Manual testing checklist:
  - [x] Data loads correctly
  - [x] Page title updates
  - [x] Month selector works
  - [x] Chart renders and updates
  - [x] Tables render

---

## Phase 9: Deployment

### Step 28: Testing & Scripts
- [x] Run integration test with live data
- [x] Install cron job (Thursday 11 AM ET)
- [x] Verify cron configuration

---

## Final Verification

- [x] Public URL accessible: `https://leadershipshape.com/nexco-dashboard/`
- [x] Chapter URL accessible: `https://leadershipshape.com/nexco-dashboard/nexco-novacore/`
- [x] Dashboard displays correctly
- [x] data.json generated with real data

---

## Post-Launch

- [ ] Monitor first Thursday cron run
- [ ] Verify data.json updates correctly
- [ ] Check logs for any errors
- [ ] Add neXco logo image (currently missing)
- [ ] Document any issues found

---

**Implementation Status: COMPLETE**

Python Backend: 13 modules implemented
Frontend: HTML, CSS, JS fully functional
Cron: Configured for Thursday 11 AM Eastern
Live URLs:
- Index: https://leadershipshape.com/nexco-dashboard/
- NOVA Core: https://leadershipshape.com/nexco-dashboard/nexco-novacore/

Last Updated: 2026-01-03
