from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_generate():
    payload = {
        "document_type": "NDA",
        "parties": "Jane Doe (Disclosing Party), ABC Ltd (Receiving Party)",
        "terms": "Confidentiality must be maintained; Use information only for evaluation",
        "dates": "October 1, 2026"
    }
    response = client.post("/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["document"]) > 100
