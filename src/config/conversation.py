from pydantic import BaseModel


class ConversationConfig(BaseModel):
    max_questions: int = 5
    session_ttl_seconds: int = 3600
