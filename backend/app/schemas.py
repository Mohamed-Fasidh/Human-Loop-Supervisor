from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .models import RequestStatus

class CallIn(BaseModel):
    caller_id: str
    question: str

class AgentResponse(BaseModel):
    handled: bool
    message: str
    request_id: Optional[int] = None

class HelpRequestOut(BaseModel):
    id: int
    caller_id: str
    question_text: str
    status: RequestStatus
    created_at: datetime
    resolved_at: Optional[datetime]
    supervisor_answer: Optional[str]

class SupervisorReplyIn(BaseModel):
    answer_text: str

class KnowledgeIn(BaseModel):
    question_text: str
    answer_text: str

class KnowledgeOut(BaseModel):
    id: int
    question_text: str
    answer_text: str
    source: str
    usage_count: int
