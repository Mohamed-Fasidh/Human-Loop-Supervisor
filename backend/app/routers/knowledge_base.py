from __future__ import annotations
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..models import KnowledgeAnswer
from ..schemas import KnowledgeIn, KnowledgeOut
import os

router = APIRouter(prefix="/kb", tags=["knowledge_base"])

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
async def require_admin(x_api_key: str | None = Header(default=None)):
    if ADMIN_API_KEY and x_api_key != ADMIN_API_KEY:
        raise HTTPException(401, "Unauthorized")

@router.get("/", response_model=list[KnowledgeOut], dependencies=[Depends(require_admin)])
def list_kb(session: Session = Depends(get_session)):
    return session.exec(select(KnowledgeAnswer).order_by(KnowledgeAnswer.created_at.desc())).all()

@router.post("/", response_model=KnowledgeOut, dependencies=[Depends(require_admin)])
def create_kb(entry: KnowledgeIn, session: Session = Depends(get_session)):
    ka = KnowledgeAnswer(question_text=entry.question_text.lower().strip(), answer_text=entry.answer_text, source="manual", created_by="admin")
    session.add(ka)
    session.commit()
    session.refresh(ka)
    return ka
