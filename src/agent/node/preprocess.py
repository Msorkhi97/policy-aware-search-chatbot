from src.agent.state import ChatState
from src.services.normalizer import PersianTextNormalizer

async def run(state: ChatState) -> dict:
    normalizer = PersianTextNormalizer()
    normalized_question = normalizer.normalize(state["question"])
    return {"normalized_question": normalized_question}