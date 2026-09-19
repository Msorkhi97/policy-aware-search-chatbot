import logging

from src.agent.state import ChatState
from src.config.settings import get_settings
from src.llm.llm import LLM
from src.prompts.direct_reply import DIRECT_REPLY_PROMPT
from src.services.history import format_history

logger = logging.getLogger(__name__)


async def run(state: ChatState) -> dict:
    settings = get_settings()

    question = state.get(
        "normalized_question",
        state["question"],
    )

    history = format_history(state.get("history", []))

    prompt = DIRECT_REPLY_PROMPT.format(
        question=question,
        history=history,
    )

    try:
        llm = LLM(
            provider=settings.llm.provider,
            model=settings.llm.model,
        )

        answer = await llm.generate(prompt)

    except Exception as exc:
        logger.error(f"پاسخ مستقیم شکست خورد: {exc}")

        return {
            "answer": settings.moderation.no_search_message,
        }

    answer = answer.strip()

    if not answer:
        answer = settings.moderation.no_search_message

    if answer == settings.moderation.refusal_message:
        return {
            "answer": answer,
            "refused": True,
        }

    return {
        "answer": answer,
    }
