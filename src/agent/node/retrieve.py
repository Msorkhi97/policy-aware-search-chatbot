from src.agent.state import ChatState
from src.config.settings import get_settings
from src.contracts.models import TopicResult
from src.services.search import keep_relevant, simplify_query, wikipedia_search


MIN_DOCUMENTS = 4


async def search(query: str, config, seen: set) -> list:
    documents = []

    results = await wikipedia_search(
        query,
        config=config,
    )

    for document in keep_relevant(results, query):
        if document.title in seen:
            continue

        seen.add(document.title)
        documents.append(document)

    return documents


async def run(state: ChatState) -> dict:
    config = get_settings().search
    topic_result = state.get("topic_result") or TopicResult()

    entities = [
        entity.text
        for entity in topic_result.entities
        if not entity.sensitivity
    ]

    question = state.get(
        "normalized_question",
        state["question"],
    )

    query = " ".join(entities) or simplify_query(question)

    seen = set()
    documents = await search(query, config, seen)

    if len(documents) < MIN_DOCUMENTS and len(entities) > 1:
        documents += await search(
            entities[0],
            config,
            seen,
        )

    return {
        "documents": documents
    }