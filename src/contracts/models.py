import uuid

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    history: list[ChatMessage] = Field(default_factory=list)
    request_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])


class ModerationResult(BaseModel):
    is_political: bool
    category: str = ""
    reason: str = ""
    source: str = ""


class Entity(BaseModel):
    text: str
    type: str = "other"
    sensitivity: bool = False


class TopicResult(BaseModel):
    needs_search: bool = True
    entities: list[Entity] = Field(default_factory=list)


class SearchDocument(BaseModel):
    title: str
    content: str
    url: str | None = None


class ChatResponse(BaseModel):
    request_id: str
    answer: str
    refused: bool = False
    moderation: ModerationResult | None = None
    entities: list[Entity] = Field(default_factory=list)
    sources: list[SearchDocument] = Field(default_factory=list)
    limit_reached: bool = False
