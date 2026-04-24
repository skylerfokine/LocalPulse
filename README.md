# OnLo

> *On Location — a multi-agent event aggregation app for Athens, Ohio.*

**AI 3300 — Agent-ML Course Project**
**Student:** Skyler Fokine
**Professor:** Ziyang Song
**Date:** April 24, 2026

---

## What Is OnLo?

OnLo is a multi-agent web application that aggregates local events from Athens, Ohio, processes them through an LLM-based agent pipeline, stores them in a PostgreSQL database, and displays them in a React calendar interface with a natural-language chat assistant.

The project started as "LocalPulse" during development and was rebranded to OnLo (short for **On Lo**cation) for release.

---

## The Four Agents

| Agent | File | Role |
|---|---|---|
| Scraper Agent | `server/app/agents/scraper.py` | Fetches raw HTML from OU Calendar and Stuart's Opera House |
| Parser Agent | `server/app/agents/parser.py` | Extracts structured fields from raw HTML using Qwen 2.5 Coder 7B via Ollama |
| Validator Agent | `server/app/agents/validator.py` | Deduplicates, validates required fields, rejects past events |
| Chat Agent | `server/app/agents/chat.py` | Answers natural-language event queries using the database + Qwen |

**APScheduler** runs the Scraper → Parser → Validator → DB pipeline daily at 6am. It is intentionally infrastructure, not an agent.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.14 |
| Scraping | requests, BeautifulSoup4 |
| Agent LLM | Qwen 2.5 Coder 7B via Ollama (local) |
| Backend | FastAPI + uvicorn |
| Database | PostgreSQL |
| Scheduler | APScheduler |
| Frontend | React + FullCalendar.js |
| Environment | WSL on Windows |

---

## Prerequisites

1. **Python 3.14** with pip
2. **PostgreSQL** installed and running
3. **Ollama** installed with `qwen2.5-coder:7b` model pulled
4. **Node.js + npm** for the React frontend

Install Ollama:
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5-coder:7b
```

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone <github-url>
cd OnLo
```

### 2. Backend setup
```bash
cd server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment variables
Create `server/.env`:
```
DB_NAME=localpulse
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

> Note: the database name is still `localpulse` internally from the project's earlier working title. Renaming is a future cleanup task.

### 4. Set up PostgreSQL database
```bash
sudo service postgresql start
psql -U postgres
```
Then in psql:
```sql
CREATE DATABASE localpulse;
\c localpulse

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

CREATE TABLE users (
    id UUID PRIMARY KEY,
    email TEXT,
    preferences JSONB,
    created_at TIMESTAMP
);
```

### 5. Create logs directory
```bash
mkdir -p server/app/logs
```

### 6. Frontend setup
```bash
cd client
npm install
```

The frontend uses FullCalendar.js. If you are scaffolding the `client/` folder from scratch, also run:
```bash
npx create-react-app .
npm install @fullcalendar/react @fullcalendar/daygrid @fullcalendar/interaction
```

---

## Running the Project

### Start all services (4 terminals):

**Terminal 1 — Ollama:**
```bash
ollama serve
```

**Terminal 2 — PostgreSQL:**
```bash
sudo service postgresql start
```

**Terminal 3 — FastAPI backend:**
```bash
cd server
source .venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 4 — React frontend:**
```bash
cd client
npm start
```

### Run the pipeline manually (populate the database):
```bash
cd server
source .venv/bin/activate
python -m app.pipeline.scheduler
```

### Access the app:
- Frontend: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/events` | All events ordered by date |
| GET | `/events/{date}` | Events for a specific date (YYYY-MM-DD) |
| POST | `/chat` | Natural-language event query |

**Chat endpoint example:**
```json
POST /chat
{ "question": "What's free this weekend?" }
```

Returns:
```json
{ "response": "This weekend you have..." }
```

---

## Frontend Views

The React frontend has three top-level tabs:

1. **Calendar** — FullCalendar.js monthly grid; click any day to see that day's events.
2. **All Events** — scrollable feed of every upcoming event.
3. **Chat** — ask natural-language questions about upcoming events.

---

## Running the Evaluation

The Parser Agent evaluation compares Qwen's structured output against 20 hand-labeled gold-standard events.

```bash
cd server
source .venv/bin/activate
ollama serve   # must be running
python -m tests.eval
```

**Results:** 19 / 20 events matched — 95% exact match rate (threshold: ≥ 80%).

---

## Project Structure
```
OnLo/
├── client/                      # React frontend
│   ├── public/
│   └── src/
│       ├── App.js
│       ├── Calendar.jsx         # FullCalendar.js monthly view
│       ├── DayDetail.jsx        # Per-day event detail view
│       ├── EventFeed.jsx        # All upcoming events
│       └── Chat.jsx             # Chat interface
├── server/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── agents/
│   │   │   ├── scraper.py       # Scraper Agent
│   │   │   ├── parser.py        # Parser Agent
│   │   │   ├── validator.py     # Validator Agent
│   │   │   └── chat.py          # Chat Agent
│   │   ├── db/
│   │   │   ├── connection.py    # DB connection
│   │   │   └── insert.py        # DB insertion
│   │   ├── routers/
│   │   │   └── events.py        # API routes
│   │   ├── pipeline/
│   │   │   └── scheduler.py     # APScheduler pipeline
│   │   └── logs/                # Per-agent log files
│   └── tests/
│       ├── eval.py              # Parser evaluation script
│       └── gold_standard/
│           ├── input/           # 20 raw HTML input samples
│           └── expected/        # 20 hand-labeled expected outputs
└── README.md
```

---

## Log Files

Each agent writes a plain-text log file per run:
- `server/app/logs/scraper.log`
- `server/app/logs/parser.log`
- `server/app/logs/validator.log`
- `server/app/logs/chat.log`

Format:
```
YYYY-MM-DD HH:MM | Agent Name | [PASS/FAIL] | details
```

---

## Future Work

- Expand scraping to additional Athens venues (Casa Nueva, Passion Works Studio).
- Swap the Parser from local Qwen to the Google Gemini free student API.
- User onboarding and personalization (the `users` table already reserves a JSONB `preferences` column).
- Event-submission form for community members.
- Self-host OnLo on a home server for public access.
- Generalize the city beyond Athens by making source configuration data-driven.

---

## License

Academic project — AI 3300 at Ohio University, Spring 2026.
