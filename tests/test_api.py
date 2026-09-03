from fastapi.testclient import TestClient

from api import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "AI Delivery Intelligence Copilot",
        "version": "0.2.0",
    }


def test_ask_endpoint_rejects_short_question():
    response = client.post(
        "/ask",
        json={"question": "Hi"},
    )

    assert response.status_code == 422