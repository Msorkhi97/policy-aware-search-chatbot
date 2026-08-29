import json
from collections import Counter
from pathlib import Path

from openpyxl import Workbook

from src.contracts.models import ChatResponse

RELEVANT_ENTITY_TYPES = {"country", "person", "politician"}


def log_interaction(path: Path, question: str, response: ChatResponse) -> None:
    record = {
        "request_id": response.request_id,
        "question": question,
        "refused": response.refused,
        "category": response.moderation.category if response.moderation else "none",
        "entities": [{"text": e.text, "type": e.type} for e in response.entities],
    }

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"ثبت رکورد تحلیلی شکست خورد: {exc}")


def count_entities(path: Path) -> dict:
    counts = {entity_type: Counter() for entity_type in RELEVANT_ENTITY_TYPES}

    with path.open(encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)

            for entity in record["entities"]:
                if entity["type"] in RELEVANT_ENTITY_TYPES:
                    counts[entity["type"]][entity["text"]] += 1

    return counts


def build_entity_report(path: Path) -> Workbook:
    counts = count_entities(path)

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "گزارش موجودیت‌ها"
    sheet.append(["نوع", "نام", "تعداد"])

    for entity_type, type_counts in counts.items():
        for name, count in type_counts.most_common():
            sheet.append([entity_type, name, count])

    return workbook
