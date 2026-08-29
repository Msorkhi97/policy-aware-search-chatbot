from typing import Literal

from src.agent.state import ChatState


async def run(state: ChatState) -> dict:
    return {}


def route_after_gate(state: ChatState) -> Literal["refuse", "direct_reply", "retrieve"]:
    moderation = state.get("moderation")

    topic_result = state.get("topic_result")

    if moderation is None:
        return "refuse"

    if moderation.is_political:
        return "refuse"

    if topic_result is None or topic_result.needs_search:
        return "retrieve"

    return "direct_reply"
