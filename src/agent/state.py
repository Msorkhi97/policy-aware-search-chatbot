from typing import TypedDict

from src.contracts.models import ChatMessage, Entity, ModerationResult, SearchDocument, TopicResult


class ChatState(TypedDict, total=False):
    request_id: str
    question: str
    history: list[ChatMessage]
    normalized_question: str
    moderation: ModerationResult | None
    entities: list[Entity]
    topic_result: TopicResult
    documents: list[SearchDocument]
    generate_prompt: str
    answer: str
    refused: bool
