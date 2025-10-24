from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlmodel import Session, select
from ..database import get_session
from ..models import HelpRequest, RequestStatus, KnowledgeAnswer
from ..schemas import HelpRequestOut, SupervisorReplyIn
from ..notifications import Notifier
from datetime import datetime
import os

router = APIRouter(prefix="/help_requests", tags=["help_requests"])

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
async def require_admin(x_api_key: str | None = Header(default=None)):
    if ADMIN_API_KEY and x_api_key != ADMIN_API_KEY:
        raise HTTPException(401, "Unauthorized")

@router.get("/", response_model=list[HelpRequestOut], dependencies=[Depends(require_admin)])
def list_help_requests(session: Session = Depends(get_session)):
    return session.exec(select(HelpRequest).order_by(HelpRequest.created_at.desc())).all()

@router.get("/pending", response_model=list[HelpRequestOut], dependencies=[Depends(require_admin)])
def list_pending(session: Session = Depends(get_session)):
    q = select(HelpRequest).where(HelpRequest.status == RequestStatus.PENDING).order_by(HelpRequest.created_at.desc())
    return session.exec(q).all()

@router.post("/{request_id}/reply", response_model=HelpRequestOut, dependencies=[Depends(require_admin)])
async def supervisor_reply(request_id: int, payload: SupervisorReplyIn, session: Session = Depends(get_session)):
    hr = session.get(HelpRequest, request_id)
    if not hr:
        raise HTTPException(404, "Help request not found")
    if hr.status != RequestStatus.PENDING:
        raise HTTPException(400, "Request is not pending")

    kb = KnowledgeAnswer(
        question_text=hr.question_text.lower().strip(),
        answer_text=payload.answer_text,
        source="supervisor",
        created_by="supervisor"
    )
    session.add(kb)
    session.commit()
    session.refresh(kb)

    hr.kb_entry_id = kb.id
    hr.supervisor_answer = payload.answer_text
    hr.status = RequestStatus.RESOLVED
    hr.resolved_at = datetime.utcnow()
    session.add(hr)
    session.commit()
    session.refresh(hr)

    notifier = Notifier()
    await notifier.message_caller(hr.caller_id, payload.answer_text)

    return hr
