from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_escalation_flow_creates_pending():
    r = client.post("/agent/simulate_call", json={
        "caller_id": "+10000000000", "question": "Do you offer bridal makeup at home?"
    }, headers={"X-API-KEY":"dev-secret"})
    assert r.status_code == 200
    data = r.json()
    assert data["handled"] is False
    assert data["request_id"] is not None

def test_supervisor_reply_resolves_and_learns():
    r = client.post("/agent/simulate_call", json={
        "caller_id": "+10000000001", "question": "Do you have keratin treatment?"
    }, headers={"X-API-KEY":"dev-secret"})
    req_id = r.json()["request_id"]

    r2 = client.post(f"/help_requests/{req_id}/reply", json={
        "answer_text": "Yes, keratin treatment is available. Pricing starts at $120."
    }, headers={"X-API-KEY":"dev-secret"})
    assert r2.status_code == 200
    body = r2.json()
    assert body["status"] == "RESOLVED"
    assert body["supervisor_answer"].startswith("Yes, keratin")
