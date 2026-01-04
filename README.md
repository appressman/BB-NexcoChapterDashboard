# neXco Chapter Dashboard

A public dashboard for neXco networking chapters that displays weekly metrics from Google Sheets data, including guest attendance tracking, RSVP counts, follow-up assignments, and open seat availability.

## Overview

This system provides config-driven multi-tenancy where the same code serves all chapters with only configuration differences. Data is refreshed weekly via cron job and served from static JSON files.

### Key Features
- Guest attendance tracking (attended vs. no-show)
- RSVP counts per meeting
- Follow-up assignments per member with intelligent name matching
- Open seat availability display
- Meeting date snapping to 2nd/4th Wednesdays
- Nickname and partial name matching (e.g., "Dan" → "Daniel Lyon")

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Weekly Cron Job                          │
│                    (Thursday 11:00 AM ET)                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Google Sheets │   │ Google Sheets │   │  neXco Roster │
│  (CSV export) │   │  (CSV export) │   │  (HTML scrape)│
│   RSVPs tab   │   │ Guest Tracker │   │  Chapter page │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
                ┌───────────────────────┐
                │   Python Refresh      │
                │   Script (refresh.py) │
                └───────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │     data.json         │
                │  (atomic write)       │
                └───────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │   Static HTML App     │
                │   (index.html)        │
                └───────────────────────┘
```

## Data Pipeline

### Module Flow

```
refresh.py (orchestrator)
    │
    ├── sheets_fetcher.py      → Fetch CSV from Google Sheets
    ├── roster_scraper.py      → Scrape member names from chapter pages
    │
    ├── rsvp_processor.py      → Parse, dedupe, filter RSVPs
    ├── guest_tracker_processor.py → Parse Guest Tracker records
    │       └── meeting_calendar.py → Snap dates to 2nd/4th Wednesdays
    │       └── date_utils.py       → Parse dates with Y2K fix
    │
    ├── data_merger.py         → Join RSVP + Guest Tracker data
    ├── aggregator.py          → Aggregate meetings for charts
    │
    ├── name_matcher.py        → Match follow-up names to roster
    │       └── name_normalizer.py → Tokenize and normalize names
    ├── followup_widget.py     → Calculate follow-up counts
    │
    ├── json_builder.py        → Build data.json structure
    └── file_writer.py         → Atomic write to output
```

### Key Processing Steps

1. **Data Fetching**: CSV export from Google Sheets via gviz URL
2. **Date Handling**: Dates snap to actual meeting dates (2nd/4th Wednesdays)
3. **RSVP Deduplication**: Key = Email + Meeting Date (last row wins)
4. **Data Merge**: Join RSVPs with Guest Tracker (Guest Tracker wins for follow-up/notes)
5. **Name Matching**: Two-pass normalization with nickname support

## Name Matching

The system uses sophisticated name matching to resolve follow-up assignments:

### Match Types
- **Alias**: Configured alias override (e.g., "Ron" → "Suzanne Parisi")
- **Roster**: Exact full name match
- **First Name**: Unique first name in roster
- **Nickname**: Common nickname expansion (e.g., "Dan" → "Daniel")
- **Partial**: Partial last name match (e.g., "Adam P" → "Adam Pressman")

### Two-Pass Normalization
1. **Light**: Strip/collapse whitespace
2. **Heavy**: Remove parentheticals, brackets, trailing annotations (`:`, `-`, etc.)

### Supported Delimiters
Follow-up strings can use: comma (`,`), slash (`/`), or ampersand (`&`)

Example: `"Dan/Luanne"` → `["Dan", "Luanne"]`

## Directory Structure

### Source Code (this repo)
```
BB-NexcoChapterDashboard/
├── refresh.py              # Main orchestrator
├── date_utils.py           # Date parsing with Y2K fix
├── meeting_calendar.py     # 2nd/4th Wednesday calculation
├── rsvp_processor.py       # RSVP parsing/deduplication
├── guest_tracker_processor.py
├── data_merger.py          # Join RSVP + Guest Tracker
├── aggregator.py           # Meeting aggregation
├── name_normalizer.py      # Tokenize/normalize names
├── name_matcher.py         # Match names to roster
├── followup_widget.py      # Follow-up count calculation
├── json_builder.py         # Build output JSON
├── file_writer.py          # Atomic file writes
├── roster_scraper.py       # Scrape member names
└── frontend/
    ├── index.html          # Dashboard HTML
    ├── dashboard.js        # Dashboard logic
    └── styles.css          # neXco-branded styles
```

### Production (InMotion server)
```
/home/adam/nexco-dashboard/
├── bin/                    # Python scripts
├── config/chapters/        # Per-chapter JSON configs
└── logs/                   # Weekly rotating logs

/home/adam/public_html/leadershipshape/nexco-dashboard/
├── index.html              # Chapter index
├── assets/                 # Shared CSS/JS/images
└── nexco-novacore/         # Chapter folder
    ├── index.html
    └── data.json           # Generated weekly
```

## Configuration

### Chapter Config Example
```json
{
  "chapter_slug": "nexco-novacore",
  "display_name": "NOVA Core (B2C)",
  "page_title": "neXco NOVA Core Dashboard",
  "sheet_url": "https://docs.google.com/spreadsheets/d/...",
  "roster_url": "https://members.nexconational.com/nova-core/",
  "tab_names": {
    "rsvps": "RSVPs",
    "guest_tracker": "Guest Tracker",
    "open_seats": "Top 3 Open Seats"
  },
  "aliases": {
    "Ron": "Suzanne Parisi"
  }
}
```

### Alias Configuration
Use aliases to:
- Map nicknames to full names
- Handle non-roster members (e.g., partners)
- Resolve ambiguous first names

## Deployment

### Requirements
- Python 3.12+ (dataclasses required)
- No external Python packages (stdlib only)
- Google Sheets must be publicly accessible

### Manual Refresh
```bash
ssh eve@inmotion
sudo -u adam /usr/bin/python3.12 /home/adam/nexco-dashboard/bin/refresh.py
```

### Cron Schedule
```cron
CRON_TZ=America/New_York
0 11 * * 4 /usr/bin/python3.12 /home/adam/nexco-dashboard/bin/refresh.py
```

## Frontend

### Technology
- Vanilla HTML/CSS/JavaScript
- Chart.js v4.5.1 (vendored)
- neXco brand colors (Navy #102048, Gold #d0a848)

### Features
- Month selector with Firefox fallback (dual dropdowns)
- Stacked bar chart (Attended vs No-Show)
- Follow-up counts widget with Prior Members section
- Guest tables with live filtering
- Stale data warning (>8 days old)

## URL

Production: `https://leadershipshape.com/nexco-dashboard/nexco-novacore/`

## License

Proprietary - Business Builders / neXco National
