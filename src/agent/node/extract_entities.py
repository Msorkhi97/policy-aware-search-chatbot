from src.agent.state import ChatState
from src.llm.llm import LLM
from src.services.history import format_history
from src.services.topic_classifier import classify_topic


async def run(state: ChatState) -> dict:
    text = state.get("normalized_question", state["question"])
    history = format_history(state.get("history", []))

    llm = LLM(provider="openai", model="gpt-4o-mini")
    result = await classify_topic(text, history, llm)

    return {"topic_result": result, "entities": result.entities}
