# neXco Chapter Dashboard - Technical Specification

**Version:** 1.0
**Last Updated:** 2026-01-03
**Project Path:** `/home/adam/pai/projects/BB-NexcoChapterDashboard`

---

## 1. Overview

### 1.1 Purpose
A public, standalone dashboard for neXco networking chapters that displays weekly metrics from Google Sheets data, including:
- Guest attendance tracking (attended vs. no-show)
- RSVP counts per meeting
- Follow-up assignments per member
- Open seat availability

### 1.2 Key Design Principles
- **Config-driven multi-tenancy**: Same code serves all chapters; only config differs
- **Weekly caching**: Data refreshed once weekly, served from static JSON
- **No authentication required**: Public dashboard, public data sources
- **Modern browser support only**: Chrome, Edge, Safari, Firefox (current versions)

---

## 2. Architecture

### 2.1 System Components

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
│   Open Seats  │   │     tab       │   │               │
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

### 2.2 Technology Stack
- **Backend**: Python 3 (standard library only - no external packages)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Charting**: Chart.js v4.5.1 (vendored locally)
- **Scheduling**: System cron (user `adam`)

---

## 3. File System Layout

### 3.1 Public Web Directory
```
/home/adam/public_html/leadershipshape/nexco-dashboard/
├── index.html                           # Chapter list/index page
├── assets/
│   ├── css/
│   │   └── styles.css                   # Shared styles (neXco theme)
│   ├── js/
│   │   └── dashboard.js                 # Shared dashboard logic
│   ├── img/
│   │   └── nexco-logo.png               # Vendored neXco logo
│   └── vendor/
│       └── chartjs/
│           └── 4.5.1/
│               ├── chart.umd.min.js     # Chart.js UMD build
│               └── LICENSE.md           # MIT license
└── nexco-novacore/                      # Chapter-specific folder
    ├── index.html                       # Chapter dashboard (same code)
    └── data.json                        # Generated weekly
```

### 3.2 Non-Public Working Directory
```
/home/adam/nexco-dashboard/
├── bin/
│   └── refresh.py                       # Weekly refresh script
├── config/
│   └── chapters/
│       └── nexco-novacore.json          # Per-chapter config
└── logs/
    └── refresh-YYYY-WW.log              # Weekly rotating logs (keep 12)
```

### 3.3 URL Mapping
| Filesystem Path | Public URL |
|-----------------|------------|
| `/home/adam/public_html/leadershipshape/nexco-dashboard/` | `https://leadershipshape.com/nexco-dashboard/` |
| `.../nexco-dashboard/nexco-novacore/` | `https://leadershipshape.com/nexco-dashboard/nexco-novacore/` |

---

## 4. Data Sources

### 4.1 Google Sheets

**Spreadsheet URL (NOVA Core):**
`https://docs.google.com/spreadsheets/d/16yJn474Z4QrlgCdz2pL0yfPgzBHAa4ZKLE-yxZJqd3E`

**Access Method:** Public CSV export via gviz URL pattern:
```
https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={TAB_NAME}
```

Note: Tab names with spaces must be URL-encoded (e.g., `Guest%20Tracker`)

#### 4.1.1 RSVPs Tab
**Tab Name:** `RSVPs`

**Required Columns (exact header strings):**
| Column Header | Type | Description |
|---------------|------|-------------|
| `Did they attend?` | Boolean | Checkbox; exports as `TRUE`/`FALSE` (all caps) |
| `First Name` | String | Guest first name |
| `Last Name` | String | Guest last name |
| `Email` | String | Guest email (always present, form-filled) |
| `Chapter meeting date` | String | Format: `M/D/YYYY` (e.g., `1/10/2024`) |
| `Profession` | String | Guest profession |
| `Company` | String | Guest company |
| `LinkedIn URL` | String | LinkedIn profile URL |
| `Lead Source` | String | How guest found chapter |
| `Name of referring member` | String | Member who invited guest |
| `Revenue Size of Clients` | String | Business metric |
| `Employee Count of Clients` | String | Business metric |

#### 4.1.2 Guest Tracker Tab
**Tab Name:** `Guest Tracker`

**Required Columns (exact header strings):**
| Column Header | Type | Description |
|---------------|------|-------------|
| `Consider for Membership` | String | Yes/No (ignored in v1) |
| `Who's Following Up` | String | Comma-separated member names |
| `Notes` | String | Free-form notes |
| `First Name` | String | Guest first name |
| `Last Name` | String | Guest last name |
| `Email` | String | Guest email (may be blank) |
| `Chapter meeting date` | String | Format: `M/D/YYYY` |
| `Profession` | String | Guest profession |
| `Company` | String | Guest company |
| `LinkedIn URL` | String | LinkedIn profile URL |
| `Lead Source` | String | How guest found chapter |
| `Name of Referring Member` | String | Member who invited guest |
| `Revenue Size of Clients` | String | Business metric |
| `Employee Count of Clients` | String | Business metric |
| `Phone` | String | Phone number |

#### 4.1.3 Top 3 Open Seats Tab
**Tab Name:** `Top 3 Open Seats`

Render all rows and columns exactly as they appear in the sheet. No filtering, no transformation.

### 4.2 neXco Roster Page

**URL (NOVA Core):** `https://members.nexconational.com/nova-core/`

**Scraping Approach:**
- Scrape the chapter listing page only (not individual profile pages)
- Extract member names from the member cards displayed on the page
- Build canonical roster for name normalization
- Respect rate limits (single request per chapter per week)
- Use clear User-Agent header

---

## 5. Per-Chapter Configuration

### 5.1 Config File Location
`/home/adam/nexco-dashboard/config/chapters/{chapter_slug}.json`

### 5.2 Config Schema
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
  "aliases": {
    "dan": "Daniel Lyon",
    "terrie": "Terrie Smith"
  }
}
```

### 5.3 Field Descriptions
| Field | Required | Description |
|-------|----------|-------------|
| `chapter_slug` | Yes | URL-safe identifier (e.g., `nexco-novacore`) |
| `display_name` | Yes | Human-readable name for index page (e.g., `NOVA Core (B2C)`) |
| `page_title` | Yes | H1/title for the dashboard page |
| `sheet_url` | Yes | Full Google Sheets URL |
| `roster_url` | Yes | neXco chapter roster page URL |
| `tab_names` | Yes | Object mapping logical names to exact sheet tab names |
| `aliases` | No | Object mapping short names to canonical roster names |

### 5.4 Alias Matching Rules
1. Matching is **case-insensitive** and **whitespace-tolerant** (uses Python `casefold()` + `strip()`)
2. **Two-pass normalization** to protect hyphenated names:
   - Pass 1: Try raw token match against aliases, then roster
   - Pass 2: If no match, apply normalization (strip parentheses, brackets, trailing annotations with `-`, `—`, `–`, `:`) then retry
3. If token matches multiple roster members (ambiguous), an explicit alias override is required

---

## 6. Data Processing Rules

### 6.1 Date Handling

| Aspect | Rule |
|--------|------|
| Input format | `M/D/YYYY` (US format, e.g., `1/10/2024`) |
| Display format | `Jan 10, 2024` |
| Timezone | All dates interpreted as America/New_York |
| Historical filter | Only show meetings where `meeting_date < today` (excludes today and future) |
| Sort order | Newest to oldest |

### 6.2 RSVP Deduplication

**Key:** `Email` + `Chapter meeting date`
**Rule:** Last row wins (form submissions append as new rows)
**Scope:** Per-meeting deduplication (same person can RSVP for multiple meetings)

### 6.3 Attendance Determination

| Source | Condition | Classification |
|--------|-----------|----------------|
| RSVPs tab | `Did they attend?` = `TRUE` | Attended |
| RSVPs tab | `Did they attend?` = `FALSE` | No-Show |
| Guest Tracker only | No matching RSVP row | "Guests without RSVPs" |

### 6.4 Data Merge Logic

**Join Key:** `Email` + `Chapter meeting date`

**Field Precedence (Guest Tracker wins):**
- `Who's Following Up` → Guest Tracker
- `Notes` → Guest Tracker
- `Referring Member` → Guest Tracker's `Name of Referring Member`

**Edge Cases:**

| Scenario | Behavior |
|----------|----------|
| RSVP exists, no Guest Tracker match | Show in Attended/No-Show with blank follow-up/notes; add "Missing in Guest Tracker" badge |
| Guest Tracker exists, no RSVP match | Show in "Guests without RSVPs" section; include in follow-up counts; count as "Attended" in chart |
| Guest Tracker row with blank email | Never auto-merge; show in "Guests without RSVPs"; include in follow-up counts |

### 6.5 Follow-Up Widget Calculation

**Input Set:**
- All Attended RSVPs (`Did they attend?` = `TRUE`)
- All "Guests without RSVPs" rows (historical only)

**Token Parsing:**
1. Split `Who's Following Up` cell on commas
2. For each token:
   - Trim whitespace
   - Apply two-pass normalization (see Section 5.4)
   - Match against: aliases → exact roster match → unique first-name/prefix match

**Output Buckets:**
| Bucket | Condition |
|--------|-----------|
| `{Canonical Name}` | Matched to roster/alias |
| `Unassigned` | Blank/empty follow-up field |
| `Ambiguous` | Multiple possible matches, no alias override |
| `{Raw Token}` | No match found, display original text |

**Display Order:** Alphabetical by name; special buckets (Unassigned, Ambiguous, raw tokens) at bottom

### 6.6 RSVP Counts

- Computed from RSVPs tab only
- Deduped by `Email` + `Chapter meeting date`
- Include `0` for historical meeting dates that appear in Guest Tracker but have no RSVPs
- Display as simple list (newest → oldest)

---

## 7. User Interface Specification

### 7.1 Branding

**Color Palette:**
| Name | Hex | Usage |
|------|-----|-------|
| Navy (Primary) | `#102048` | Headers, section titles, table headers |
| Gold (Accent) | `#d0a848` | Attended bar segments, accents |
| Gray (Neutral) | `#9ca3af` | No-Show bar segments |
| White | `#ffffff` | Background |

**Logo:**
- Provided neXco logo image stored locally
- Location: `/assets/img/nexco-logo.png`
- Header placement: Top-left
- Link behavior: Opens `https://nexconational.com/` in new window
- Link attributes: `target="_blank" rel="noopener noreferrer"`

### 7.2 Index Page (`/nexco-dashboard/`)

**Purpose:** List all available chapter dashboards

**Elements:**
1. neXco-branded header (same as chapter pages)
2. Semantic navigation list (`<nav>` element)
3. Chapter entries sorted alphabetically by `display_name`
4. Each entry links to chapter dashboard path

**Example Entry:** "NOVA Core (B2C)" → `/nexco-dashboard/nexco-novacore/`

### 7.3 Chapter Dashboard Page Layout

**Order of Components:**

1. **Header**
   - neXco logo (links to nexconational.com, new window)
   - H1: Page title from config (e.g., "neXco NOVA Core Dashboard")

2. **Month Selector Row**
   - Month selector control (see Section 7.4)
   - "Last updated" timestamp (see Section 7.5)
   - Stale warning (if applicable, see Section 7.6)

3. **Status Notice Area**
   - `role="status"` with `aria-live="polite"`
   - Shows auto-jump notice when user selects invalid month

4. **Stacked Bar Chart**
   - Attendance by meeting date (see Section 7.7)

5. **RSVP Counts**
   - Simple list format: "Meeting Date → Count"

6. **Follow-Ups Assigned Per Member Widget**
   - Counts only, alphabetically sorted

7. **Top 3 Open Seats**
   - Static table, all rows/columns from sheet
   - Ignores month selector (always current snapshot)

8. **Guest Tables (3 sections)**
   - Attended Guests
   - No-Shows
   - Guests without RSVPs

### 7.4 Month Selector

**Primary Control:** `<input type="month">`
- Value format: `YYYY-MM`
- Updates dashboard immediately on change
- No query string persistence
- No localStorage persistence
- Default: Most recent month with historical meetings

**Firefox Fallback:**
- Two `<select>` dropdowns: Month + Year
- Feature detection: Create `<input type="month">`, check if browser honors it
- Year range: Current year down to 2023 (newest → oldest)
- Month order: January → December
- Hidden when native month picker is supported

**Auto-Jump Behavior:**
- If user selects month with no historical meetings, auto-jump to most recent valid month
- Show notice: "No historical meetings in **{selected month}** — showing **{valid month}** instead."
- Notice uses `role="status"` for accessibility

### 7.5 Last Updated Display

**Format:** `Jan 3, 2026 11:02 AM ET`

**Implementation:**
- Source: `last_updated` field in `data.json` (UTC ISO 8601)
- Display timezone: America/New_York
- Clock format: 12-hour with AM/PM
- Timezone label: "ET" (not EST/EDT)
- Use `Intl.DateTimeFormat` with `timeZone: "America/New_York"` and `hour12: true`

### 7.6 Stale Warning

**Trigger:** `now_utc - last_updated_utc > 8 days`

**Text:** "Data may be stale (last updated more than 8 days ago)"

**Placement:** Near month selector / last updated timestamp

### 7.7 Stacked Bar Chart

**Library:** Chart.js v4.5.1 (vendored UMD build)

**Type:** Stacked bar chart

**X-Axis:** Meeting dates (newest → oldest, formatted as `Jan 10, 2024`)

**Datasets:**
| Dataset | Color | Data Source |
|---------|-------|-------------|
| Attended | Gold (`#d0a848`) | RSVPs with `TRUE` + Guest Tracker-only rows |
| No-Show | Gray (`#9ca3af`) | RSVPs with `FALSE` |

**Configuration:**
- Legend: Hidden
- Inline labels: Text with color squares above chart ("Attended ■", "No-Show ■")
- Tooltip: Custom format showing breakdown (e.g., "Attended: 7, No-Show: 2")
- Data labels on bars: None (axis + tooltip only)

### 7.8 Guest Tables

**Sections:**
1. Attended Guests
2. No-Shows
3. Guests without RSVPs

**Columns (in order):**
| Column | Source | Notes |
|--------|--------|-------|
| Guest Name | `First Name` + `Last Name` | Concatenated |
| Company | Sheet | |
| Email | Sheet | Full email displayed |
| Referring Member | Guest Tracker preferred | |
| Who's Following Up | Guest Tracker | |
| Meeting Date | Sheet | Formatted as `Jan 10, 2024` |
| Notes | Guest Tracker | |

**Badges:**
- "Missing in Guest Tracker" — Inline badge next to Guest Name when RSVP has no matching Guest Tracker row

**Default Sort:** Meeting Date (desc), then Guest Name (A→Z)

**Filter Box (per table):**
- Case-insensitive partial match
- AND logic across terms (all terms must match)
- Supports single and double quoted phrases
- Ignores unclosed quotes (falls back to whitespace split)
- Searches only: Guest Name, Who's Following Up, Meeting Date, Referring Member
- Updates on `input` event (live filtering)

### 7.9 Accessibility

| Element | Requirement |
|---------|-------------|
| Status notices | `role="status"` with implicit `aria-live="polite"` |
| Tables | Proper `<th>` headers |
| Logo image | Descriptive `alt` text |
| Color contrast | Meet WCAG 2.1 AA minimum |

---

## 8. Refresh Job Specification

### 8.1 Schedule

**Timing:** Thursday 11:00 AM America/New_York
**User:** `adam`
**Timezone handling:** Set `CRON_TZ=America/New_York` in crontab

**Crontab Entry:**
```cron
CRON_TZ=America/New_York
0 11 * * 4 /usr/bin/python3 /home/adam/nexco-dashboard/bin/refresh.py
```

### 8.2 Execution Flow

```
1. Read all config files from /home/adam/nexco-dashboard/config/chapters/*.json

2. For each chapter:
   a. Fetch RSVPs tab CSV (via gviz URL)
   b. Fetch Guest Tracker tab CSV
   c. Fetch Top 3 Open Seats tab CSV
   d. If ANY tab fetch fails → FULL FAILURE for this chapter
      - Keep existing data.json
      - Log error
      - Update metadata (last_refresh_attempt, refresh_status, refresh_error)

   e. Fetch roster page HTML
   f. If roster fetch fails → PARTIAL SUCCESS
      - Continue with data processing
      - Skip roster-based name normalization
      - Follow-up widget shows raw tokens
      - Log roster error

   g. Parse and process data (apply all rules from Section 6)

   h. Generate data.json using ATOMIC WRITE:
      - Write to temp file on same filesystem
      - Rename temp file to data.json
      - Ensures readers never see partial/corrupt data

   i. Log success/failure for chapter

3. Generate index.html at /nexco-dashboard/

4. Write to log file: /home/adam/nexco-dashboard/logs/refresh-{YYYY}-{WW}.log
```

### 8.3 Error Handling

| Failure Type | Behavior |
|--------------|----------|
| Tab fetch fails | Full failure: Keep last good `data.json`, update error metadata |
| Roster scrape fails | Partial success: Publish fresh data, skip roster mapping, log error |
| Parse error | Full failure: Keep last good `data.json`, log details |
| Write error | Full failure: Keep last good `data.json`, log details |

### 8.4 Logging

**Log Location:** `/home/adam/nexco-dashboard/logs/`
**Filename Pattern:** `refresh-YYYY-WW.log` (ISO week number)
**Rotation:** Self-managed by Python script
**Retention:** Keep last 12 weeks

**Log Content:**
- Timestamp (ISO 8601 UTC)
- Chapter being processed
- Success/failure status
- Error messages and stack traces
- Fetch timing (for debugging slow requests)

---

## 9. data.json Schema

### 9.1 Top-Level Structure

```json
{
  "metadata": {
    "chapter_slug": "nexco-novacore",
    "display_name": "NOVA Core (B2C)",
    "page_title": "neXco NOVA Core Dashboard",
    "last_updated": "2026-01-03T16:02:00Z",
    "last_refresh_attempt": "2026-01-03T16:02:00Z",
    "refresh_status": "ok",
    "refresh_error": null
  },
  "available_months": ["2026-01", "2025-12", "2025-11"],
  "meetings": [...],
  "chart_data": {...},
  "rsvp_counts": [...],
  "open_seats": [...],
  "follow_up_counts": [...],
  "guests": {
    "attended": [...],
    "no_show": [...],
    "without_rsvp": [...]
  }
}
```

### 9.2 Metadata Object

| Field | Type | Description |
|-------|------|-------------|
| `chapter_slug` | string | Chapter identifier |
| `display_name` | string | Human-readable chapter name |
| `page_title` | string | Dashboard page title |
| `last_updated` | string | ISO 8601 UTC timestamp of last successful refresh |
| `last_refresh_attempt` | string | ISO 8601 UTC timestamp of most recent attempt |
| `refresh_status` | string | `"ok"` or `"error"` |
| `refresh_error` | string|null | Error message if status is error |

### 9.3 Meetings Array

```json
{
  "date": "2026-01-08",
  "display_date": "Jan 8, 2026",
  "attended_count": 7,
  "no_show_count": 2,
  "rsvp_count": 12
}
```

### 9.4 Chart Data Object

```json
{
  "labels": ["Jan 22, 2026", "Jan 8, 2026"],
  "datasets": [
    {
      "label": "Attended",
      "data": [5, 7],
      "backgroundColor": "#d0a848"
    },
    {
      "label": "No-Show",
      "data": [1, 2],
      "backgroundColor": "#9ca3af"
    }
  ]
}
```

### 9.5 RSVP Counts Array

```json
[
  { "date": "Jan 22, 2026", "count": 15 },
  { "date": "Jan 8, 2026", "count": 12 },
  { "date": "Dec 11, 2025", "count": 0 }
]
```

### 9.6 Open Seats Array

Array of objects with keys matching exact column headers from sheet.

### 9.7 Follow-Up Counts Array

```json
[
  { "name": "Adam Pressman", "count": 3 },
  { "name": "Daniel Lyon", "count": 5 },
  { "name": "Unassigned", "count": 2, "special": true },
  { "name": "Dan?", "count": 1, "raw_token": true }
]
```

### 9.8 Guest Objects

```json
{
  "name": "John Smith",
  "company": "Acme Corp",
  "email": "john@acme.com",
  "referring_member": "Adam Pressman",
  "following_up": "Daniel Lyon, Terrie Smith",
  "meeting_date": "2026-01-08",
  "display_date": "Jan 8, 2026",
  "notes": "Interested in marketing services",
  "flags": ["missing_guest_tracker"]
}
```

**Flags:**
- `missing_guest_tracker` — RSVP row with no Guest Tracker match

---

## 10. Deployment Checklist

### 10.1 Initial Setup

- [ ] Create directory structure (Section 3)
- [ ] Install Python 3 (verify with `python3 --version`)
- [ ] Download Chart.js 4.5.1 UMD build and MIT license
- [ ] Copy neXco logo to assets directory
- [ ] Create first chapter config file
- [ ] Deploy refresh.py script
- [ ] Deploy HTML/CSS/JS files
- [ ] Set up cron job with correct timezone

### 10.2 Adding a New Chapter

1. Create new config file: `/home/adam/nexco-dashboard/config/chapters/{slug}.json`
2. Ensure Google Sheet is publicly accessible
3. Wait for next Thursday refresh OR run manual refresh
4. Verify chapter appears on index page
5. Verify data displays correctly on chapter dashboard

### 10.3 Testing

- [ ] Verify CSV fetch works for all tabs
- [ ] Verify roster scrape extracts names correctly
- [ ] Verify atomic write works (check for temp files)
- [ ] Verify cron runs at correct time (check logs)
- [ ] Test Firefox fallback month selector
- [ ] Test filter box functionality
- [ ] Verify chart renders correctly
- [ ] Check accessibility with screen reader

---

## 11. Future Considerations (Not in v1)

The following were explicitly deferred:
- Print-friendly styling
- Manual refresh CLI command
- Raw CSV snapshot caching for debugging
- Query string / localStorage for month selection
- "Consider for Membership" field display
- Cross-chapter rollup dashboard

---

## Appendix A: Example Chapter Config

**File:** `/home/adam/nexco-dashboard/config/chapters/nexco-novacore.json`

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

---

## Appendix B: Crontab Configuration

```cron
# neXco Dashboard Weekly Refresh
# Runs every Thursday at 11:00 AM Eastern Time
CRON_TZ=America/New_York
0 11 * * 4 /usr/bin/python3 /home/adam/nexco-dashboard/bin/refresh.py >> /home/adam/nexco-dashboard/logs/cron.log 2>&1
```

---

## Appendix C: CSS Custom Properties (Theme)

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
}
```
