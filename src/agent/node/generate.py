from src.agent.state import ChatState
from src.config.settings import get_settings
from src.prompts.generate import GENERATE_PROMPT
from src.services.history import format_history


async def run(state: ChatState) -> dict:
    settings = get_settings()

    question = state.get(
        "normalized_question",
        state["question"],
    )

    documents = state.get("documents", [])

    if not documents:
        return {
            "answer": settings.moderation.no_source_message,
        }

    context = "\n\n".join(
        f"عنوان: {document.title}\n"
        f"محتوا: {document.content}"
        for document in documents
    )

    history = format_history(state.get("history", []))

    prompt = GENERATE_PROMPT.format(
        question=question,
        context=context,
        history=history,
    )

    return {
        "generate_prompt": prompt,
    }
