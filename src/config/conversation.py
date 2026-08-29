from pydantic import BaseModel


class ConversationConfig(BaseModel):
    max_questions: int = 5
