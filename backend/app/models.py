from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field

class RequestStatus(str, Enum):
    PENDING = "PENDING"
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"

class KnowledgeAnswer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_text: str
    answer_text: str
    source: str = Field(default="supervisor")  # seed/supervisor/import/manual
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(default="system")
    usage_count: int = Field(default=0)

class HelpRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    caller_id: str
    question_text: str
    status: RequestStatus = Field(default=RequestStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    supervisor_answer: Optional[str] = None
    kb_entry_id: Optional[int] = Field(default=None, foreign_key="knowledgeanswer.id")

    
