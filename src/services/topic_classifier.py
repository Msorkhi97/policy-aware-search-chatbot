from src.contracts.models import Entity, TopicResult
from src.prompts.entities import ENTITIES_PROMPT


async def classify_topic(text: str, history: str, llm) -> TopicResult:

    try:
        data = await llm.generate_json(ENTITIES_PROMPT.format(text=text, history=history))

        entities = [
            Entity(
                text=entity["text"],
                type=entity.get("type", "other"),
                sensitivity=bool(entity.get("sensitivity", False)),
            )
            for entity in data.get("entities", [])
            if entity.get("text")
        ]

        return TopicResult(
            needs_search=bool(data.get("needs_search", True)),
            entities=entities,
        )

    except Exception as exc:

        print(f"استخراج موجودیت با مدل زبانی شکست خورد: {exc}")
        return TopicResult(needs_search=True, entities=[])
