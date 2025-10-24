from __future__ import annotations
from sqlmodel import Session
from ..kb_matcher import find_best_answer
from ..models import HelpRequest

class SimulatorAgent:
    """A minimal in-process agent for local testing."""
    def __init__(self, session: Session):
        self.session = session

    def handle_call(self, caller_id: str, question: str):
        kb = find_best_answer(self.session, question)
        if kb:
            return {"handled": True, "message": kb.answer_text, "request_id": None}
        hr = HelpRequest(caller_id=caller_id, question_text=question)
        self.session.add(hr)
        self.session.commit()
        return {
            "handled": False,
            "message": "Let me check with my supervisor and get back to you.",
            "request_id": hr.id,
        }
