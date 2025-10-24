from __future__ import annotations
from sqlmodel import Session
from ..kb_matcher import find_best_answer
from ..models import HelpRequest

class LiveKitAgent:
    """Thin wrapper stub. Replace with real LiveKit integration as needed."""
    def __init__(self, session: Session):
        self.session = session

    def handle_call(self, caller_id: str, question: str):
        print(f"[LiveKit Stub] Incoming call from {caller_id}: {question}")
        kb = find_best_answer(self.session, question)
        if kb:
            print(f"[LiveKit Stub] Found KB match: {kb.answer_text}")
            return {"handled": True, "message": kb.answer_text, "request_id": None}
        hr = HelpRequest(caller_id=caller_id, question_text=question)
        self.session.add(hr)
        self.session.commit()
        print(f"[LiveKit Stub] Escalated to supervisor, request_id={hr.id}")
        return {
        "handled": False,
        "message": "Let me check with my supervisor and get back to you.",
        "request_id": hr.id,
       }
