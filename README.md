# Alfred

A public NYC crime dashboard. Alfred shows an interactive map of the five boroughs — click a borough to see reported crimes as pins, filtered by time range (day/week/month), and click a pin to see full case details alongside a plain-language AI-generated summary.

Project covering a full stack: data ingestion, a Postgres-backed API, and a React/Leaflet frontend.

## How it's built

```
alfred/
├── ingestion/     Pulls NYPD complaint data from NYC Open Data, stores it in
│                  Postgres, and generates AI case summaries via the Claude API.
│                  Runs on a schedule (daily), not continuously.
│
├── backend/       FastAPI service that reads from Postgres and serves crime
│                  data as JSON. Runs continuously.
│
└── frontend/      React + Leaflet map. Calls the backend, renders boroughs,
                   pins, and the case detail panel. Runs continuously (dev server).
```

Data flows in one direction: **NYC Open Data → ingestion → Postgres → backend → frontend**. Nothing downstream ever talks to Socrata or the Claude API directly — only `ingestion/` does.

## Data source

[NYC Open Data — NYPD Complaint Data (Year to Date)](https://data.cityofnewyork.us/resource/5uac-w243.json), accessed via the Socrata Open Data API (SODA).

**Caveat:** this is *reported* crime, not verified crime. Complaints can later be reclassified or unfounded. Locations are approximate for privacy reasons (midblock incidents are geocoded to the middle of the block, not the exact address).

## Prerequisites

- Python 3.12 (not 3.14 — several dependencies, notably `psycopg2-binary`, don't yet have prebuilt wheels for 3.14)
- Node.js + npm
- Postgres (local via Docker/OrbStack, or hosted via Neon/Supabase)
- Docker or OrbStack, if running Postgres locally
- API keys: a free Socrata app token, and an Anthropic API key with billing enabled

## Setup

Each of the three folders has its own `.env.example` — copy it to `.env` and fill in real values before running anything.

### 1. Database

Local, via Docker:
```bash
docker run --name alfred-db -e POSTGRES_PASSWORD=devpassword -e POSTGRES_DB=alfred -p 5432:5432 -d postgres
```

Or use a hosted free-tier Postgres (Neon, Supabase) and skip Docker entirely — either way you end up with a `DATABASE_URL` connection string.

### 2. Ingestion

```bash
cd ingestion
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in SOCRATA_APP_TOKEN, DATABASE_URL, ANTHROPIC_API_KEY
python run_daily.py
```

This creates the `crimes` table on first run, pulls recent records, and generates AI summaries for anything new (capped at 50 per run — re-run to work through a larger backlog).

### 3. Backend

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # same DATABASE_URL as above
uvicorn main:app --reload
```

Confirm it's up at `http://localhost:8000` (should return `{"status": "ok"}`), and browse the interactive API docs at `http://localhost:8000/docs`.

### 4. Frontend

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_URL=http://localhost:8000
npm run dev
```

Open the printed local URL (typically `http://localhost:5173`).

## Environment variables

| Variable | Location | Purpose |
|---|---|---|
| `SOCRATA_APP_TOKEN` | `ingestion/.env` | Auth for NYC Open Data API |
| `DATABASE_URL` | `ingestion/.env`, `backend/.env` | Postgres connection string |
| `ANTHROPIC_API_KEY` | `ingestion/.env` | Generates case summaries via the Claude API |
| `VITE_API_URL` | `frontend/.env` | Points the frontend at the backend's URL |

