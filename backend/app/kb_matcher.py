from __future__ import annotations
from sqlmodel import Session, select
from .models import KnowledgeAnswer
from rapidfuzz import fuzz

SEED_QA = [
    ("what are your hours", "We're open Tue–Sun, 9:00 AM to 6:00 PM."),
    ("do you do hair coloring", "Yes! We offer hair coloring and highlights. Call us to book."),
    ("where are you located", "We're at 123 Blossom Street, Springfield.")
]

def ensure_seed_data(session: Session):
    exists = session.exec(select(KnowledgeAnswer)).all()
    if exists:
        return
    for q, a in SEED_QA:
        session.add(KnowledgeAnswer(question_text=q, answer_text=a, source="seed", created_by="seed"))
    session.commit()

def find_best_answer(session: Session, question: str, threshold: int = 72):
    question_norm = question.lower().strip()
    best = None
    best_score = -1
    for ka in session.exec(select(KnowledgeAnswer)).all():
        score = max(
            fuzz.token_set_ratio(question_norm, ka.question_text.lower()),
            fuzz.partial_ratio(question_norm, ka.question_text.lower())
        )
        if score > best_score:
            best_score, best = score, ka
    if best and best_score >= threshold:
        best.usage_count += 1
        session.add(best)
        session.commit()
        return best
    return None
