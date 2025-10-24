from sqlmodel import Session
from backend.app.database import engine, init_db
from backend.app.models import KnowledgeAnswer
from backend.app.kb_matcher import find_best_answer

def setup_module():
    init_db()

def test_find_best_answer_seed():
    with Session(engine) as s:
        s.add(KnowledgeAnswer(question_text="what are your hours", answer_text="9-6"))
        s.commit()
        ans = find_best_answer(s, "Can you tell me your hours?")
        assert ans is not None
        assert "6" in ans.answer_text
