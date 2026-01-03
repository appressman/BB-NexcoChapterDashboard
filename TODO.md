# neXco Chapter Dashboard - Implementation Checklist

Use this file to track implementation progress. Mark items with `[x]` when complete.

---

## Phase 1: Project Foundation

### Step 1: Directory Structure
- [ ] Create public web directory structure at `/home/adam/public_html/leadershipshape/nexco-dashboard/`
- [ ] Create non-public working directory at `/home/adam/nexco-dashboard/`
- [ ] Create `setup-dirs.sh` script
- [ ] Execute and verify directories exist

### Step 2: Config Schema and Loader
- [ ] Create `/home/adam/nexco-dashboard/bin/config.py`
- [ ] Implement `ChapterConfig` dataclass
- [ ] Implement `load_config()` function
- [ ] Implement `load_all_configs()` function
- [ ] Implement `extract_spreadsheet_id()` helper
- [ ] Create `/home/adam/nexco-dashboard/tests/test_config.py`
- [ ] All tests passing

### Step 3: Logging Infrastructure
- [ ] Create `/home/adam/nexco-dashboard/bin/logger.py`
- [ ] Implement `setup_logger()` with file and console handlers
- [ ] Implement weekly log rotation (keep 12 weeks)
- [ ] Create helper functions for chapter logging
- [ ] Create `/home/adam/nexco-dashboard/tests/test_logger.py`
- [ ] All tests passing

### Step 4: Example Chapter Config
- [ ] Create `/home/adam/nexco-dashboard/config/chapters/nexco-novacore.json`
- [ ] Create `/home/adam/nexco-dashboard/bin/validate_config.py`
- [ ] Verify config loads correctly

---

## Phase 2: Data Fetching

### Step 5: Google Sheets CSV Fetcher
- [ ] Create `/home/adam/nexco-dashboard/bin/sheets_fetcher.py`
- [ ] Implement `fetch_sheet_csv()` function
- [ ] Implement `FetchError` exception
- [ ] Implement `fetch_chapter_tabs()` convenience function
- [ ] Create `/home/adam/nexco-dashboard/tests/test_sheets_fetcher.py`
- [ ] All tests passing

### Step 6: Roster Page Scraper
- [ ] Create `/home/adam/nexco-dashboard/bin/roster_scraper.py`
- [ ] Implement `scrape_roster()` function
- [ ] Implement `ScrapeError` exception
- [ ] Implement `build_roster_lookup()` function
- [ ] Create `/home/adam/nexco-dashboard/tests/test_roster_scraper.py`
- [ ] All tests passing

---

## Phase 3: Data Processing

### Step 7: Date Utilities
- [ ] Create `/home/adam/nexco-dashboard/bin/date_utils.py`
- [ ] Implement `parse_meeting_date()` function
- [ ] Implement `format_display_date()` function
- [ ] Implement `get_today_eastern()` function
- [ ] Implement `is_historical()` function
- [ ] Implement `get_month_key()` function
- [ ] Implement `get_display_month()` function
- [ ] Create `/home/adam/nexco-dashboard/tests/test_date_utils.py`
- [ ] All tests passing

### Step 8: RSVP Processor
- [ ] Create `/home/adam/nexco-dashboard/bin/rsvp_processor.py`
- [ ] Implement `RSVPRecord` dataclass
- [ ] Implement `parse_rsvps()` function
- [ ] Implement `dedupe_rsvps()` function
- [ ] Implement `filter_historical()` function
- [ ] Implement `split_by_attendance()` function
- [ ] Create `/home/adam/nexco-dashboard/tests/test_rsvp_processor.py`
- [ ] All tests passing

### Step 9: Guest Tracker Processor
- [ ] Create `/home/adam/nexco-dashboard/bin/guest_tracker_processor.py`
- [ ] Implement `GuestTrackerRecord` dataclass
- [ ] Implement `parse_guest_tracker()` function
- [ ] Implement `filter_historical()` function
- [ ] Implement `build_lookup()` function
- [ ] Create `/home/adam/nexco-dashboard/tests/test_guest_tracker_processor.py`
- [ ] All tests passing

### Step 10: Data Merger
- [ ] Create `/home/adam/nexco-dashboard/bin/data_merger.py`
- [ ] Implement `MergedGuest` dataclass
- [ ] Implement `merge_data()` function with all edge cases
- [ ] Create `/home/adam/nexco-dashboard/tests/test_data_merger.py`
- [ ] All tests passing

### Step 11: Meeting Aggregator
- [ ] Create `/home/adam/nexco-dashboard/bin/aggregator.py`
- [ ] Implement `MeetingStats` dataclass
- [ ] Implement `aggregate_meetings()` function
- [ ] Implement `get_available_months()` function
- [ ] Implement `build_chart_data()` function
- [ ] Implement `build_rsvp_counts()` function
- [ ] Create `/home/adam/nexco-dashboard/tests/test_aggregator.py`
- [ ] All tests passing

---

## Phase 4: Follow-Up Widget

### Step 12: Name Tokenizer and Normalizer
- [ ] Create `/home/adam/nexco-dashboard/bin/name_normalizer.py`
- [ ] Implement `tokenize_followups()` function
- [ ] Implement `normalize_name()` with two-pass logic
- [ ] Implement `casefold_normalize()` function
- [ ] Create `/home/adam/nexco-dashboard/tests/test_name_normalizer.py`
- [ ] All tests passing

### Step 13: Name Matcher
- [ ] Create `/home/adam/nexco-dashboard/bin/name_matcher.py`
- [ ] Implement `NameMatcher` class
- [ ] Implement matching logic (alias → roster → first name → ambiguous)
- [ ] Create `/home/adam/nexco-dashboard/tests/test_name_matcher.py`
- [ ] All tests passing

### Step 14: Follow-Up Widget Calculator
- [ ] Create `/home/adam/nexco-dashboard/bin/followup_widget.py`
- [ ] Implement `FollowUpCount` dataclass
- [ ] Implement `calculate_followups()` function
- [ ] Implement sorting logic (canonical → special → raw)
- [ ] Create `/home/adam/nexco-dashboard/tests/test_followup_widget.py`
- [ ] All tests passing

---

## Phase 5: Output Generation

### Step 15: JSON Builder
- [ ] Create `/home/adam/nexco-dashboard/bin/json_builder.py`
- [ ] Implement `build_data_json()` function
- [ ] Implement timestamp helpers
- [ ] Implement dataclass → dict conversion
- [ ] Create `/home/adam/nexco-dashboard/tests/test_json_builder.py`
- [ ] All tests passing

### Step 16: Atomic File Writer
- [ ] Create `/home/adam/nexco-dashboard/bin/file_writer.py`
- [ ] Implement `atomic_write_json()` function
- [ ] Implement `atomic_write_text()` function
- [ ] Implement `WriteError` exception
- [ ] Create `/home/adam/nexco-dashboard/tests/test_file_writer.py`
- [ ] All tests passing

### Step 17: Index Page Generator
- [ ] Create `/home/adam/nexco-dashboard/bin/index_generator.py`
- [ ] Implement `generate_index_html()` function
- [ ] Verify alphabetical sorting
- [ ] Verify HTML escaping
- [ ] Create `/home/adam/nexco-dashboard/tests/test_index_generator.py`
- [ ] All tests passing

### Step 18: Main Refresh Script
- [ ] Create `/home/adam/nexco-dashboard/bin/refresh.py`
- [ ] Implement main orchestration logic
- [ ] Implement per-chapter error handling
- [ ] Implement `RefreshResult` tracking
- [ ] Implement summary output
- [ ] Create `/home/adam/nexco-dashboard/tests/test_refresh.py`
- [ ] All tests passing

---

## Phase 6: Frontend Foundation

### Step 19: Vendor Chart.js
- [ ] Download Chart.js v4.5.1 UMD build
- [ ] Save to `/home/adam/public_html/leadershipshape/nexco-dashboard/assets/vendor/chartjs/4.5.1/`
- [ ] Create LICENSE.md with MIT license
- [ ] Verify file is valid JavaScript

### Step 20: CSS Theme File
- [ ] Create `/home/adam/public_html/leadershipshape/nexco-dashboard/assets/css/styles.css`
- [ ] Define CSS custom properties (neXco colors)
- [ ] Implement base styles (reset, fonts)
- [ ] Implement header styles
- [ ] Implement table styles
- [ ] Implement filter input styles
- [ ] Implement badge styles
- [ ] Implement chart container styles
- [ ] Implement status notice styles
- [ ] Implement month selector styles
- [ ] Implement responsive styles

### Step 21: Chapter Dashboard HTML
- [ ] Create `/home/adam/public_html/leadershipshape/nexco-dashboard/nexco-novacore/index.html`
- [ ] Implement semantic HTML structure
- [ ] Add accessibility attributes (ARIA)
- [ ] Verify script loading order

---

## Phase 7: Frontend Core

### Step 22: Data Loader (JavaScript)
- [ ] Create `/home/adam/public_html/leadershipshape/nexco-dashboard/assets/js/dashboard.js`
- [ ] Implement `loadDashboardData()` function
- [ ] Implement `DashboardState` object
- [ ] Implement `initDashboard()` function
- [ ] Implement `updatePageTitle()` function
- [ ] Implement `formatLastUpdated()` function
- [ ] Implement `checkStaleData()` function
- [ ] Implement `showError()` function

### Step 23: Month Selector
- [ ] Implement `supportsMonthInput()` feature detection
- [ ] Implement `initMonthSelector()` function
- [ ] Implement `initNativeMonthPicker()` function
- [ ] Implement `initFallbackDropdowns()` function
- [ ] Implement `handleMonthChange()` with auto-jump
- [ ] Implement `formatMonthDisplay()` helper

### Step 24: Chart Rendering
- [ ] Implement `initChart()` function
- [ ] Implement `updateChart()` function
- [ ] Configure Chart.js options (stacked, tooltips)
- [ ] Wire to `renderForMonth()`

---

## Phase 8: Frontend Tables & Widgets

### Step 25: Table Rendering
- [ ] Implement `renderGuestTable()` function
- [ ] Implement `escapeHtml()` helper
- [ ] Implement `initTableFilters()` function
- [ ] Implement `handleFilter()` function
- [ ] Implement `filterGuests()` with AND logic
- [ ] Implement `parseFilterTerms()` for quoted phrases
- [ ] Implement `renderFilteredTable()` function

### Step 26: Widgets
- [ ] Implement `renderRsvpCounts()` function
- [ ] Implement `renderFollowUpWidget()` function
- [ ] Implement `renderOpenSeats()` function
- [ ] Implement `renderGuestTables()` function
- [ ] Wire to `renderForMonth()`

### Step 27: Final Integration
- [ ] Verify all functions are connected
- [ ] Add loading state handling
- [ ] Add error boundaries
- [ ] Manual testing checklist:
  - [ ] Data loads correctly
  - [ ] Page title updates
  - [ ] Stale warning shows when appropriate
  - [ ] Month selector works (native)
  - [ ] Month selector works (Firefox fallback)
  - [ ] Auto-jump works for invalid months
  - [ ] Chart renders and updates
  - [ ] Attended table renders
  - [ ] No-Show table renders
  - [ ] Without RSVPs table renders
  - [ ] Table filters work with AND logic
  - [ ] Table filters work with quoted phrases
  - [ ] RSVP counts update by month
  - [ ] Follow-up widget displays
  - [ ] Open seats table displays

---

## Phase 9: Deployment

### Step 28: Testing & Scripts
- [ ] Create `/home/adam/nexco-dashboard/tests/fixtures/sample_data.json`
- [ ] Create `/home/adam/nexco-dashboard/bin/test_local.py`
- [ ] Create `/home/adam/nexco-dashboard/bin/deploy.sh`
- [ ] Create `/home/adam/nexco-dashboard/bin/install_cron.sh`
- [ ] Run all unit tests
- [ ] Run integration test with live data
- [ ] Install cron job
- [ ] Verify cron runs correctly

---

## Final Verification

- [ ] Public URL accessible: `https://leadershipshape.com/nexco-dashboard/`
- [ ] Chapter URL accessible: `https://leadershipshape.com/nexco-dashboard/nexco-novacore/`
- [ ] Dashboard displays correctly
- [ ] No JavaScript errors in console
- [ ] Mobile responsive
- [ ] Accessibility check (screen reader basics)

---

## Post-Launch

- [ ] Monitor first Thursday cron run
- [ ] Verify data.json updates correctly
- [ ] Check logs for any errors
- [ ] Document any issues found

---

**Total Steps: 28 prompts / ~75 checkboxes**

Last Updated: 2026-01-03
