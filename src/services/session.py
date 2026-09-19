import time
import uuid

from src.contracts.models import ChatMessage


class Session:
    def __init__(self):
        self.session_id = uuid.uuid4().hex
        self.history: list[ChatMessage] = []
        self.question_count = 0
        self.last_active = time.time()


class SessionStore:
    def __init__(self, ttl_seconds: int):
        self.ttl_seconds = ttl_seconds
        self.sessions: dict[str, Session] = {}

    def remove_expired(self) -> None:
        now = time.time()

        expired = [
            session_id
            for session_id, session in self.sessions.items()
            if now - session.last_active > self.ttl_seconds
        ]

        for session_id in expired:
            del self.sessions[session_id]

    def get_or_create(self, session_id: str | None) -> Session:
        self.remove_expired()

        session = self.sessions.get(session_id) if session_id else None

        if session is None:
            session = Session()
            self.sessions[session.session_id] = session

        session.last_active = time.time()
        return session
