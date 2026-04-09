# LocalPulse — Week 1 Handoff Context

## Project Overview
LocalPulse is a multi-agent web application for AI 3300 (Agent-ML) at Ohio University.
- **Professor:** Ziyang Song
- **Due:** April 24, 2026
- **Submission subject line:** "AI3300 - Course Project - Skyler Fokine"
- **Email:** ziyangs@ohio.edu

---

## The Four Agents
1. **Scraper Agent** — Selenium + BeautifulSoup + requests, fetches raw HTML from Athens, OH event sources
2. **Parser Agent** — Google Gemini API (free student tier), extracts structured fields from raw HTML
3. **Validator Agent** — deduplication, date validation, required field checks before DB insertion
4. **Chat Agent** — natural language event queries, runs on-demand from frontend

Pipeline scheduled by **APScheduler** (not an agent — it's infrastructure).
Flow: Scraper → Parser → Validator → PostgreSQL → FastAPI → React + FullCalendar.js

---

## Tech Stack
| Layer | Technology |
|---|---|
| Language | Python 3.14 |
| Scraping | requests, BeautifulSoup, Selenium (if needed) |
| Agent LLM | Google Gemini API (free student tier) |
| Backend | FastAPI + uvicorn |
| Database | PostgreSQL |
| Scheduler | APScheduler |
| Frontend | React + FullCalendar.js |
| Environment | WSL on Windows (laptop + desktop, both set up) |

---

## Folder Structure
```
localpulse/
├── client/                  # React frontend
│   └── .env
├── server/
│   ├── app/
│   │   ├── main.py          # FastAPI entry point
│   │   ├── core/            # Config & settings
│   │   ├── db/              # DB connection & migrations
│   │   ├── models/          # ORM models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routers/         # API endpoints
│   │   ├── agents/
│   │   │   ├── scraper.py   # ← CURRENTLY BUILDING
│   │   │   ├── parser.py
│   │   │   ├── validator.py
│   │   │   └── chat.py
│   │   ├── pipeline/
│   │   │   └── scheduler.py
│   │   └── logs/
│   │       └── artifacts/
│   ├── tests/
│   │   ├── gold_standard/   # 20 hand-labeled JSON events
│   │   └── results/         # gitignored, generated at eval time
│   ├── .env
│   └── requirements.txt
├── .gitignore
└── README.md
```

---

## Setup Status (Both Machines Complete ✅)
- Python 3.14 venv created and activated
- Installed: `requests`, `selenium`, `beautifulsoup4`, `fastapi`, `uvicorn`, `psycopg2-binary`, `apscheduler`
- `requirements.txt` populated via `pip freeze`
- PostgreSQL installed, running, `localpulse` database created
- Both `events` and `users` tables created (see schema below)
- `.gitignore` covers `.venv`, `.env`, `server/tests/results/`
- Project on GitHub, cloned to desktop

---

## Database Schema

### events table
```sql
CREATE TABLE events (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    date DATE NOT NULL,
    time TIME,
    location TEXT,
    description TEXT,
    cost_free BOOLEAN,
    cost_amount NUMERIC,
    category TEXT,
    source_url TEXT NOT NULL,
    scraped_at TIMESTAMP
);
```

### users table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email TEXT,
    preferences JSONB,
    created_at TIMESTAMP
);
```

---

## Week 1 Progress
- ✅ Folder structure created
- ✅ Python venv + dependencies (both machines)
- ✅ `.gitignore` configured
- ✅ PostgreSQL — both tables created
- ⬜ Scraper Agent (in progress)
- ⬜ Scraper log file

---

## Scraper Agent — Current Design

### Sources (Eventbrite dropped — search API deprecated since 2020)
1. **Ohio University Events Calendar** — `https://calendar.ohio.edu/calendar`
2. **Stuart's Opera House** — `https://www.stuartsoperahouse.org`

### scraper.py location
`server/app/agents/scraper.py`

### Imports written so far
```python
import requests
from bs4 import BeautifulSoup
```

### OU Events Calendar Scraping Plan
- Start URL: `https://calendar.ohio.edu/calendar` (already sorted from current date)
- Pagination: `/calendar/2`, `/calendar/3`, etc.
- **Events container div:** `class="em-card-group em-card-group--small"`
- **Each event card:** any div with class `em-card`
- **Event link:** anchor tag inside `em-card-image`
- **Pagination container:** `class="em-search-pagination"`
- **Stopping condition:** after scraping each page, the scraper does a minimal date check — it looks at the event dates on that page to see if the month has flipped (e.g. April → May). If it has, stop paginating and return everything collected so far. The Validator then trims any events that fall past the last day of the current month. The scraper does NOT do deep field extraction — just enough date inspection to know when to stop.

### Scraper function breakdown (planned)
1. `get_event_links(page_url)` — loads a listing page, returns list of event detail URLs
2. `get_event_html(event_url)` — fetches raw HTML of a single event page
3. `scrape_ohio_events()` — paginates through listing pages, calls above two functions, returns list of raw HTML strings
4. `scrape(url)` — dispatcher function: routes to `scrape_ohio_events()` or `scrape_stuarts()` based on URL

### What the Scraper returns
A list of raw HTML strings — one per event page. The Parser Agent handles all field extraction from that HTML.

### Key architectural decision
The Scraper does NOT extract fields like title, date, price — that is the Parser Agent's job. Scraper just fetches and hands off raw HTML.

### HTML fields the Parser will target (OU Calendar)
- **Title:** `<h1 class="em-header-card_title">`
- **Date:** `<p class="em-date">` inside `class="em-list_dates__container"`
- **Price:** `<span class="em-price-tag">` inside `class="em-about_info"`
- **Description:** paragraph tags inside `class="em-about_description"`

---

## Log File Design (Scraper Agent)
Format: `YYYY-MM-DD HH:MM | Scraper Agent | [PASS/FAIL] | message`

Examples:
```
2026-04-07 06:02 | Scraper Agent | [PASS] | https://calendar.ohio.edu/calendar
2026-04-07 06:02 | Scraper Agent | [FAIL] | https://calendar.ohio.edu/calendar | Connection timeout
```

Log files live at: `server/app/logs/` — one file per agent per run.

---

## Parser Evaluation Plan (for later)
- **Metric:** exact match rate across `title`, `date`, `time`, `cost`
- **Gold standard:** 20 hand-labeled JSON events in `tests/gold_standard/`
- **Success threshold:** ≥ 80% (16/20 events)
- **Baseline:** BeautifulSoup rule-based extractor (no LLM)
- **Output normalization** applied before comparison (e.g. dates → ISO format)
- **Cost field:** `N/A` is valid, not a failure

---

## Learning Preferences
- Socratic guidance preferred — ask guiding questions, let Skyler reason toward answers
- Direct answers preferred when the question requires knowledge Skyler couldn't reasonably infer
- Always provide direct links to official documentation when helping with code
- Python comfortable, new to FastAPI, React, Selenium, PostgreSQL

---

## Next Step
Write the first function in `scraper.py`:
```python
def get_event_links(page_url):
    # Takes a listing page URL
    # Returns a list of event detail URLs
```
Relevant docs:
- requests: https://docs.python-requests.org/en/latest/
- BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
