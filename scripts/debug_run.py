import asyncio
import logging

from src.agent.graph import build_graph
from src.config.settings import get_settings
from src.contracts.models import ChatRequest
from src.llm.llm import LLM

QUESTION = "بهترین رژیم برای لاغری چیه؟"


async def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    graph = build_graph()
    request = ChatRequest(question=QUESTION)
    state = {
        "request_id": request.request_id,
        "question": request.question,
        "history": [],
    }

    final = await graph.ainvoke(state)

    prompt = final.get("generate_prompt")
    if prompt:
        llm_config = get_settings().llm
        llm = LLM(provider=llm_config.provider, model=llm_config.model)
        final["answer"] = await llm.generate(prompt)

    print("refused:", final.get("refused"))
    print("moderation:", final.get("moderation"))
    print("entities:", final.get("entities"))
    print("sources:", [d.title for d in final.get("documents", [])])
    print("answer:", final.get("answer"))


if __name__ == "__main__":
    asyncio.run(run())
