# Frontdesk HITL Supervisor (Phase 1)

A minimal, clean human-in-the-loop system for AI receptionists. Built for local demo using FastAPI and a no-build admin UI.

## Features
- Receive “calls” via HTTP (stand-in for LiveKit voice) and answer from a KB.
- If unknown, create a PENDING help request, notify supervisor (console/webhook).
- Supervisor admin UI to respond; on reply, caller is texted back immediately.
- Learned answers are persisted to KB and visible in the UI.
- SLA watcher marks stale PENDING requests as UNRESOLVED.

## Run (Local)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
# open frontend/index.html in your browser
```

## Run (Docker)
```bash
docker compose up --build
```

## API
- `POST /agent/simulate_call` `{ caller_id, question }` → `{ handled, message, request_id? }`
- `GET /help_requests/` all; `GET /help_requests/pending` pending only
- `POST /help_requests/{id}/reply` `{ answer_text }` → resolves + texts back
- `GET /kb/` list KB; `POST /kb/` add KB entries

See the repository for architecture notes.
