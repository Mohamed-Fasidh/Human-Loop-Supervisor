# Frontdesk — Human-in-the-Loop AI Supervisor

## 🧠 Overview

This project implements **Phase-1** of Frontdesk’s *Human-in-the-Loop AI System* — an AI receptionist that can escalate unknown customer questions to a human supervisor, follow up with the customer, and learn automatically from new information.

When the AI doesn’t know something, it:
1. Escalates the question to a human supervisor.
2. Waits for a response.
3. Texts back the original caller (simulated via console/webhook).
4. Updates its own knowledge base so it won’t need to ask again.

---

## 🚀 Features

| Module | Description |
|---------|-------------|
| 🤖 **AI Agent** | Simulated LiveKit agent (stub) that answers known questions or escalates when unsure. |
| 🧍 **Supervisor Dashboard** | Simple HTML + JavaScript admin panel to view pending requests, reply, and review history. |
| 💾 **Knowledge Base** | Stores learned Q/A pairs; auto-updates after supervisor replies. |
| 🔁 **Lifecycle Management** | Request states: `PENDING → RESOLVED / UNRESOLVED` (auto timeout). |
| ⚙️ **Background Watcher** | Auto-marks overdue requests as `UNRESOLVED` after SLA timeout. |
| 🧩 **Extensible Design** | Ready for real LiveKit audio integration in Phase-2. |

---

## 🏗️ Tech Stack

| Layer | Tools |
|--------|-------|
| **Backend** | FastAPI · SQLModel · SQLite (easy to swap for Postgres) |
| **Frontend** | Plain HTML + JavaScript (no build step) |
| **Architecture** | Modular — Agent / KB / Notifier / Background / Routers |
| **Environment** | `.env` config |
| **Deployment** | Dockerfile + docker-compose |
| **Testing** | pytest |

---

## ⚙️ Setup Instructions

### 1️⃣ Clone & Enter Folder
```bash
git clone https://github.com/<your-username>/frontdesk-hitl.git
cd frontdesk-hitl


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
