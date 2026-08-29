import io
import json

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from src.agent.graph import build_graph
from src.config.settings import get_settings
from src.contracts.models import ChatRequest, ChatResponse
from src.llm.llm import LLM
from src.services.analytics import build_entity_report, log_interaction

app = FastAPI()
graph = build_graph()


async def stream_chat(request: ChatRequest):
    settings = get_settings()
    max_questions = settings.conversation.max_questions

    current_turn = len(request.history) // 2 + 1

    if current_turn > max_questions:
        response = ChatResponse(
            request_id=request.request_id,
            answer="به سقفِ سؤال‌های این گفت‌وگو رسیدی؛ صفحه رو رفرش کن.",
            limit_reached=True,
        )
        yield json.dumps({"done": True, **response.model_dump()}, ensure_ascii=False) + "\n"
        return

    state = {
        "request_id": request.request_id,
        "question": request.question,
        "history": request.history,
    }
    final = await graph.ainvoke(state)

    prompt = final.get("generate_prompt")

    if prompt:
        answer = ""

        try:
            llm = LLM(provider="openai", model="gpt-4o-mini")

            async for chunk in llm.generate_stream(prompt):
                answer += chunk
                yield json.dumps({"chunk": chunk}, ensure_ascii=False) + "\n"

        except Exception as exc:
            print(f"تولید پاسخ شکست خورد: {exc}")
            answer = settings.moderation.no_source_message

        answer = answer.strip() or settings.moderation.no_source_message

        final["answer"] = answer
        final["refused"] = answer == settings.moderation.refusal_message

    response = ChatResponse(
        request_id=request.request_id,
        answer=final.get("answer", settings.moderation.refusal_message),
        refused=bool(final.get("refused")),
        moderation=final.get("moderation"),
        entities=final.get("entities", []),
        sources=[] if final.get("refused") else final.get("documents", []),
        limit_reached=current_turn >= max_questions,
    )
    log_interaction(settings.analytics.analytics_path, request.question, response)

    yield json.dumps({"done": True, **response.model_dump()}, ensure_ascii=False) + "\n"


@app.post("/chat")
async def chat(request: ChatRequest):
    return StreamingResponse(stream_chat(request), media_type="application/x-ndjson")


@app.get("/entity-report.xlsx")
async def entity_report():
    settings = get_settings()
    workbook = build_entity_report(settings.analytics.analytics_path)

    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=entity-report.xlsx"},
    )


app.mount("/", StaticFiles(directory="web", html=True), name="web")
