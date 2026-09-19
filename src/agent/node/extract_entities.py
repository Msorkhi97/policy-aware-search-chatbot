import logging

from src.agent.state import ChatState
from src.config.settings import get_settings
from src.contracts.models import TopicResult
from src.llm.llm import LLM
from src.services.history import format_history
from src.services.topic_classifier import classify_topic

logger = logging.getLogger(__name__)


async def run(state: ChatState) -> dict:
    llm_config = get_settings().llm

    text = state.get("normalized_question", state["question"])
    history = format_history(state.get("history", []))

    try:
        llm = LLM(provider=llm_config.provider, model=llm_config.model)
        result = await classify_topic(text, history, llm)

    except Exception as exc:
        logger.error(f"استخراج موجودیت با مدل زبانی شکست خورد: {exc}")

        result = TopicResult(needs_search=True, entities=[])

    return {"topic_result": result, "entities": result.entities}
