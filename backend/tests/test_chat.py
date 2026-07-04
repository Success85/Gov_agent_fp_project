"""
test_chat.py
------------
LANE 5 - Step 3.
This tests the text chat path: it sends a Kinyarwanda question to the /chat
endpoint and checks that we get a successful, non-empty reply back.

It uses FastAPI's TestClient, which lets us call the endpoint WITHOUT starting
a live server. This test needs the Lane 1 /chat endpoint to exist to pass.

Run from the backend/ folder with:  pytest
"""

from fastapi.testclient import TestClient
from app.main import app

# Wrap our app in the test client so we can send requests to it in tests.
client = TestClient(app)


def test_root_health_check():
    """The server should be alive and respond at the root URL."""
    response = client.get("/")
    assert response.status_code == 200


def test_chat_returns_a_reply():
    """
    Sending a Kinyarwanda question to /chat should return status 200
    and a non-empty text reply.
    """
    # The request shape must match Lane 1's ChatRequest: a "question" field.
    payload = {"question": "Ni ibihe byangombwa nsaba indangamuntu?"}

    response = client.post("/chat", json=payload)

    # 1. The request should succeed.
    assert response.status_code == 200

    # 2. The response should contain a "reply" field.
    data = response.json()
    assert "reply" in data

    # 3. The reply should not be empty.
    assert isinstance(data["reply"], str)
    assert len(data["reply"]) > 0