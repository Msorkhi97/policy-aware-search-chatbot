import asyncio
import logging

from src.agent.graph import build_graph
from src.contracts.models import ChatRequest

QUESTION = "بهترین رژیم برای لاغری چیه؟"


async def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    graph = build_graph()
    request = ChatRequest(question=QUESTION)
    state = {
        "request_id": request.request_id,
        "question": request.question,
        "history": request.history,
    }

    final = await graph.ainvoke(state)

    print("refused:", final.get("refused"))
    print("moderation:", final.get("moderation"))
    print("entities:", final.get("entities"))
    print("sources:", [d.title for d in final.get("documents", [])])
    print("answer:", final.get("answer"))


if __name__ == "__main__":
    asyncio.run(run())
