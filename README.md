# 📅 LocalPulse
### A Multi-Agent System for Local Event Discovery

> *"I never know what's happening around me, and finding local events is scattered across a dozen different websites."*

LocalPulse is a multi-agent application that automatically aggregates, cleans, enriches, and displays local events in a personalized calendar interface. Built with LLM-powered agents, it transforms raw, messy web data into a structured, user-friendly event feed.

---

## 🧠 How It Works

Four specialized AI agents collaborate in a pipeline to take events from the web to your calendar:

| Agent | Role |
|---|---|
| 🕷️ **Scraper** | Fetches raw HTML from target sources using Selenium; uses screenshot OCR for dynamic pages |
| 🔍 **Parser** | Extracts structured fields (name, date, time, cost, location, description, link) via LLM |
| ✅ **Validator** | Deduplicates, cleans, and checks data before writing to the database |
| 💬 **Chat Agent** | Answers natural language queries like *"what's free this Saturday?"* |

Pipeline scheduling is handled by **APScheduler** (runs daily at a configured time) — treated as infrastructure, not an agent.

---

## 🗂️ Event Categories

- 🎓 Campus (Ohio University events)
- 🏘️ Community (local Athens area events)
- 🎭 Theater & Arts
- 🎵 Concerts & Music

---

## 🖥️ Frontend Views

- **Monthly Calendar** — event density per day, click to drill down
- **Day Detail View** — all events for a selected date with full details
- **Event Feed** — scrollable, filterable list of upcoming events
- **Chat Interface** — natural language event queries
- **User Event Submission** — community members can submit events directly

---

## 🔄 Pipeline Flow

```
APScheduler (daily trigger)
    ↓
Scraper → raw HTML / screenshots
    ↓
Parser → structured event dict
    ↓
Validator → clean, deduplicated record
    ↓
PostgreSQL Database
    ↓
React Frontend (Calendar + Feed views)
    ↕
Chat Agent (available anytime for user queries)
```

---

## 🌐 Data Sources

- Ohio University Events Calendar (public)
- Athens Messenger event listings
- Eventbrite API (ticketed events)
- Local Facebook Groups via Selenium *(ToS risk acknowledged — scoped to public listings)*
- Venue websites (Casa Nueva, Stuart's Opera House, etc.)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Scraping | Python, Selenium, BeautifulSoup, Vision/OCR model |
| Agent LLM | Claude API (Anthropic) |
| Backend | FastAPI + PostgreSQL |
| Scheduler | APScheduler |
| Frontend | React + FullCalendar.js |

---

## 🚀 Getting Started

> *Setup instructions coming soon as development begins.*

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/localpulse.git
cd localpulse

# Backend setup
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
npm run dev
```

---

## 🔭 Potential Extensions

- **MCP Memory** — persist agent context across runs to improve extraction quality over time
- **Location Configurability** — support any city, not just Athens
- **Notification Agent** — daily digest emails or push notifications based on user preferences
- **Explainability** — surface why an event was recommended

---

## 📌 Project Status

🟡 **In Development** — Proposal approved, architecture phase starting.

---

*Built for Agent-ML Course · Spring 2026*
