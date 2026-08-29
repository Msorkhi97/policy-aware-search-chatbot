from src.agent.state import ChatState
from src.config.settings import get_settings


async def run(state: ChatState) -> dict:
    settings = get_settings()
    moderation = state.get("moderation")

    if moderation and moderation.category == "error":
        return {
            "answer": settings.moderation.error_message,
            "refused": True,
        }

    return {
        "answer": settings.moderation.refusal_message,
        "refused": True,
    }