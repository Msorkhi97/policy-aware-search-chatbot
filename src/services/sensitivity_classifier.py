import json
import re
from pathlib import Path

from src.contracts.models import ModerationResult
from src.prompts.sensitivity import SENSITIVITY_PROMPT


LEXICON_DIR = Path(__file__).resolve().parent.parent / "config" / "lexicons"


def load_lexicon() -> dict:
    with open(LEXICON_DIR / "political_char.json", encoding="utf-8") as f:
        people = json.load(f)

    with open(LEXICON_DIR / "political_terms.json", encoding="utf-8") as f:
        terms = json.load(f)

    with open(LEXICON_DIR / "countries.json", encoding="utf-8") as f:
        countries = json.load(f)

    return {
        "people": people["figures"],
        "terms": terms["terms"],
        "countries": countries["countries"],
    }



def contains_word(text: str, word: str) -> bool:
    return bool(re.search(rf"\b{re.escape(word)}\b", text))


def find_sensitive_term(text: str) -> tuple[str, str] | None:

    lexicon = load_lexicon()

    for person in lexicon["people"]:
        names = [person["name"], *person.get("aliases", [])]

        for name in names:
            if contains_word(text, name.lower()):
                return "person", name

    for term in lexicon["terms"]:
        names = [term["name"], *term.get("aliases", [])]

        for name in names:
            if contains_word(text, name.lower()) and term.get("hard", False):
                return "term", name

    for country in lexicon["countries"]:
        names = [country["name"], *country.get("aliases", [])]

        for name in names:
            if contains_word(text, name.lower()):
                return "country", name

    return None


async def classify_sensitivity(text: str, history: str, llm) -> ModerationResult:

    # Rule-based
    match = find_sensitive_term(text)

    if match:
        category, term = match

        return ModerationResult(
            is_political=True,
            category=category,
            reason=f"عبارت حساس شناسایی شد: {term}",
            source="rule",
        )

    # without llm
    if llm is None:
        return ModerationResult(
            is_political=False,
            category="none",
            reason="عبارت حساس شناخته‌شده‌ای پیدا نشد",
            source="rule",
        )

    # LLM
    try:

        data = await llm.generate_json(
            SENSITIVITY_PROMPT.format(
                text=text,
                history=history,
            )
        )

        return ModerationResult(
            is_political=bool(data.get("is_political", True)),
            category=str(data.get("category", "other")),
            reason=str(data.get("reason", "")),
            source="llm",
        )

    except Exception:
        return ModerationResult(
            is_political=True,
            category="error",
            reason="خطا در ارتباط با سرویس مدل زبانی",
            source="llm",
        )