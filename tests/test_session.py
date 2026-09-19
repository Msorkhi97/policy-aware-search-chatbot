from fastapi.testclient import TestClient

from src.api.app import app, sessions
from src.services.session import SessionStore


def test_creates_session_when_id_is_missing():
    store = SessionStore(ttl_seconds=60)

    session = store.get_or_create(None)

    assert session.question_count == 0
    assert store.get_or_create(session.session_id) is session


def test_unknown_session_id_gets_a_new_session():
    store = SessionStore(ttl_seconds=60)

    session = store.get_or_create("forged-id")

    assert session.session_id != "forged-id"


def test_expired_sessions_are_removed():
    store = SessionStore(ttl_seconds=60)
    session = store.get_or_create(None)
    session.last_active -= 120

    store.remove_expired()

    assert session.session_id not in store.sessions


def test_chat_stops_after_question_limit():
    session = sessions.get_or_create(None)
    session.question_count = 5

    client = TestClient(app)
    response = client.post("/chat", json={"question": "سلام", "session_id": session.session_id})

    assert '"limit_reached": true' in response.text
    assert session.question_count == 5


def test_chat_rejects_empty_question():
    client = TestClient(app)

    assert client.post("/chat", json={"question": ""}).status_code == 422
