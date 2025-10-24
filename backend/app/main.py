from __future__ import annotations
import os
import asyncio
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from .database import init_db, get_session, engine
from .schemas import CallIn, AgentResponse
from .kb_matcher import ensure_seed_data
from .agent.simulator import SimulatorAgent
from .agent.livekit_agent import LiveKitAgent
from .routers import help_requests, knowledge_base
from .notifications import Notifier
from .background import sla_watcher

app = FastAPI(title="Frontdesk HITL Supervisor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

def require_admin(x_api_key: str | None = Header(default=None)):
    if ADMIN_API_KEY and x_api_key != ADMIN_API_KEY:
        raise HTTPException(401, "Unauthorized")

@app.on_event("startup")
async def startup_event():
    init_db()
    with Session(engine) as s:
        ensure_seed_data(s)
    asyncio.create_task(sla_watcher(engine))

AGENT_MODE = os.getenv("AGENT_MODE", "simulator").lower()

def get_agent(session: Session):
    if AGENT_MODE == "livekit":
        return LiveKitAgent(session)
    return SimulatorAgent(session)

@app.post("/agent/simulate_call", response_model=AgentResponse, dependencies=[Depends(require_admin)])
async def simulate_call(payload: CallIn, session: Session = Depends(get_session)):
    agent = get_agent(session)
    result = agent.handle_call(payload.caller_id, payload.question)

    if not result["handled"] and result.get("request_id"):
        notifier = Notifier()
        await notifier.notify_supervisor(f"Hey, I need help answering: '{payload.question}' (request #{result['request_id']})")

    return AgentResponse(**result)

app.include_router(help_requests.router)
app.include_router(knowledge_base.router)

@app.get("/health")
def health():
    return {"ok": True}
