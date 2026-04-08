# BabyTracker API

FastAPI backend for BabyTracker — a mobile-first baby care tracking application. Tracks feeding, sleep, diaper changes, tummy time, growth, medications, and milestones for one or more babies.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.111 |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (via aiosqlite) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Server | Uvicorn |

## Prerequisites

- Python 3.11+

## Quick Start

```bash
# 1. Clone and enter the project
cd baby-gael-backend

# 2. Run the start script (creates venv, installs deps, seeds data, starts server)
./start.sh
```

Or manually:

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy env file
cp .env.example .env

# 4. Run migrations
alembic upgrade head

# 5. (Optional) Seed sample data — creates baby "Gael" with logs
python seed.py

# 6. Start the server
uvicorn app.main:app --reload --port 8000
```

Interactive API docs: http://localhost:8000/docs  
ReDoc: http://localhost:8000/redoc  
Health check: http://localhost:8000/health

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ALLOWED_ORIGINS` | `http://localhost:3000` | Comma-separated list of allowed CORS origins |

## Project Structure

```
baby-gael-backend/
├── app/
│   ├── main.py          # FastAPI app, CORS middleware, router registration
│   ├── database.py      # SQLAlchemy engine and session factory
│   ├── models/
│   │   ├── baby.py      # Baby model
│   │   └── logs.py      # All log models (feeding, sleep, diaper, etc.) + enums
│   ├── schemas/
│   │   ├── baby.py      # Pydantic v2 request/response schemas for babies
│   │   └── logs.py      # Pydantic v2 schemas for all log types
│   ├── routers/
│   │   ├── babies.py    # CRUD for babies
│   │   ├── feeding.py   # Feeding logs + start/stop timer
│   │   ├── sleep.py     # Sleep logs + start/stop timer
│   │   ├── diaper.py    # Diaper change logs
│   │   ├── tummy_time.py # Tummy time logs + start/stop timer
│   │   ├── growth.py    # Weight, height, head circumference logs
│   │   ├── medication.py # Medication administration logs
│   │   ├── milestone.py  # Developmental milestone logs
│   │   └── dashboard.py  # Dashboard summary, daily timeline, and stats
│   └── services/        # Business logic layer
├── alembic/             # Database migration scripts
├── alembic.ini          # Alembic configuration
├── requirements.txt
├── seed.py              # Sample data seeder
└── start.sh             # One-command dev startup script
```

## API Reference

All endpoints are prefixed with `/api`.

### Babies

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/babies/` | List all babies |
| `POST` | `/api/babies/` | Create a baby |
| `GET` | `/api/babies/{id}` | Get a baby by ID |
| `PATCH` | `/api/babies/{id}` | Update a baby |
| `DELETE` | `/api/babies/{id}` | Delete a baby (cascades all logs) |

**Baby fields:** `name`, `birth_date`, `birth_weight_grams`, `birth_height_cm`, `photo_url`

### Dashboard & Timeline

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/babies/{id}/dashboard` | Today's summary (last events, active sessions, daily counts) |
| `GET` | `/api/babies/{id}/timeline?date=YYYY-MM-DD` | All events for a given day, sorted by time |

### Feeding

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/babies/{id}/feeding/` | List feeding logs |
| `POST` | `/api/babies/{id}/feeding/` | Create a feeding log |
| `GET` | `/api/babies/{id}/feeding/stats?days=7` | Aggregated stats (counts, duration, breast vs bottle) |
| `GET` | `/api/babies/{id}/feeding/{log_id}` | Get a feeding log |
| `PATCH` | `/api/babies/{id}/feeding/{log_id}` | Update a feeding log |
| `DELETE` | `/api/babies/{id}/feeding/{log_id}` | Delete a feeding log |
| `POST` | `/api/babies/{id}/feeding/start?feeding_type=breast_left` | Start a feeding timer |
| `POST` | `/api/babies/{id}/feeding/{session_id}/stop` | Stop timer and save feeding log |

**Feeding types:** `breast_left`, `breast_right`, `bottle`, `formula`

### Sleep

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/babies/{id}/sleep/` | List sleep logs |
| `POST` | `/api/babies/{id}/sleep/` | Create a sleep log |
| `GET` | `/api/babies/{id}/sleep/stats?days=7` | Aggregated stats (total hours, naps vs night) |
| `GET` | `/api/babies/{id}/sleep/{log_id}` | Get a sleep log |
| `PATCH` | `/api/babies/{id}/sleep/{log_id}` | Update a sleep log |
| `DELETE` | `/api/babies/{id}/sleep/{log_id}` | Delete a sleep log |
| `POST` | `/api/babies/{id}/sleep/start` | Start a sleep timer |
| `POST` | `/api/babies/{id}/sleep/{session_id}/stop` | Stop timer and save sleep log |

**Sleep types:** `nap`, `night`  
**Sleep locations:** `crib`, `stroller`, `arms`, `carrier`, `other`

### Diaper

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/babies/{id}/diaper/` | List diaper logs |
| `POST` | `/api/babies/{id}/diaper/` | Create a diaper log |
| `GET` | `/api/babies/{id}/diaper/{log_id}` | Get a diaper log |
| `PATCH` | `/api/babies/{id}/diaper/{log_id}` | Update a diaper log |
| `DELETE` | `/api/babies/{id}/diaper/{log_id}` | Delete a diaper log |

**Diaper types:** `wet`, `dirty`, `both`, `dry`

### Tummy Time

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/babies/{id}/tummy_time/` | List tummy time logs |
| `POST` | `/api/babies/{id}/tummy_time/` | Create a tummy time log |
| `GET` | `/api/babies/{id}/tummy_time/{log_id}` | Get a tummy time log |
| `PATCH` | `/api/babies/{id}/tummy_time/{log_id}` | Update a tummy time log |
| `DELETE` | `/api/babies/{id}/tummy_time/{log_id}` | Delete a tummy time log |
| `POST` | `/api/babies/{id}/tummy_time/start` | Start a tummy time timer |
| `POST` | `/api/babies/{id}/tummy_time/{session_id}/stop` | Stop timer and save log |

### Growth

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/babies/{id}/growth/` | List growth records |
| `POST` | `/api/babies/{id}/growth/` | Create a growth record |
| `GET` | `/api/babies/{id}/growth/chart` | Data formatted for a growth chart |
| `GET` | `/api/babies/{id}/growth/{log_id}` | Get a growth record |
| `PATCH` | `/api/babies/{id}/growth/{log_id}` | Update a growth record |
| `DELETE` | `/api/babies/{id}/growth/{log_id}` | Delete a growth record |

**Growth fields:** `date`, `weight_grams`, `height_cm`, `head_circumference_cm`

### Medication

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/babies/{id}/medication/` | List medication logs |
| `POST` | `/api/babies/{id}/medication/` | Create a medication log |
| `GET` | `/api/babies/{id}/medication/{log_id}` | Get a medication log |
| `PATCH` | `/api/babies/{id}/medication/{log_id}` | Update a medication log |
| `DELETE` | `/api/babies/{id}/medication/{log_id}` | Delete a medication log |

**Medication units:** `ml`, `mg`, `drops`

### Milestones

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/babies/{id}/milestone/` | List milestones |
| `POST` | `/api/babies/{id}/milestone/` | Create a milestone |
| `GET` | `/api/babies/{id}/milestone/{log_id}` | Get a milestone |
| `PATCH` | `/api/babies/{id}/milestone/{log_id}` | Update a milestone |
| `DELETE` | `/api/babies/{id}/milestone/{log_id}` | Delete a milestone |

**Milestone categories:** `motor`, `social`, `cognitive`, `language`, `other`

## Active Sessions (Timers)

Feeding, sleep, and tummy time support live timers via the `active_sessions` table. Calling `/start` creates an `ActiveSession` record. Calling `/stop` calculates the duration, creates the corresponding log entry, and deletes the session.

## Database Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "description"

# Downgrade one step
alembic downgrade -1
```

The SQLite database file is `babytracker.db` in the project root.
