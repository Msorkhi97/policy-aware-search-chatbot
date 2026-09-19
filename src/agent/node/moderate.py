import logging

from src.agent.state import ChatState
from src.config.settings import get_settings
from src.contracts.models import ModerationResult
from src.llm.llm import LLM
from src.services.history import format_history
from src.services.sensitivity_classifier import classify_sensitivity

logger = logging.getLogger(__name__)


async def run(state: ChatState) -> dict:
    llm_config = get_settings().llm

    text = state.get("normalized_question", state["question"])
    history = format_history(state.get("history", []))

    try:
        llm = LLM(provider=llm_config.provider, model=llm_config.model)
        result = await classify_sensitivity(text, history, llm)

    except Exception as exc:
        logger.error(f"بررسی حساسیت با مدل زبانی شکست خورد: {exc}")

        result = ModerationResult(
            is_political=True,
            category="error",
            reason="خطا در ارتباط با سرویس مدل زبانی",
            source="llm",
        )

    return {"moderation": result}
