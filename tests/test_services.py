import json

from src.contracts.models import SearchDocument
from src.services.analytics import count_entities
from src.services.search import keep_relevant, simplify_query
from src.services.sensitivity_classifier import find_sensitive_term


def test_simplify_query_removes_filler_words():
    assert simplify_query("فتوسنتز چیست؟") == "فتوسنتز"


def test_simplify_query_keeps_question_when_nothing_left():
    assert simplify_query("چیست") == "چیست"


def test_keep_relevant_always_keeps_first_document():
    documents = [
        SearchDocument(title="فتوسنتز", content="..."),
        SearchDocument(title="گیاه", content="..."),
    ]

    result = keep_relevant(documents, "فتوسنتز")

    assert [document.title for document in result] == ["فتوسنتز"]


def test_find_sensitive_term_detects_hard_term():
    assert find_sensitive_term("کودتا چیست") == ("term", "کودتا")


def test_find_sensitive_term_ignores_safe_text():
    assert find_sensitive_term("فتوسنتز چیست") is None


def test_find_sensitive_term_leaves_country_names_to_the_llm():
    assert find_sensitive_term("جمعیت ژاپن چقدر است") is None
    assert find_sensitive_term("پایتخت ایران کجاست") is None


def test_count_entities_without_file(tmp_path):
    counts = count_entities(tmp_path / "missing.jsonl")

    assert all(len(counter) == 0 for counter in counts.values())


def test_count_entities_counts_relevant_types_only(tmp_path):
    path = tmp_path / "interactions.jsonl"
    records = [
        {"entities": [{"text": "ژاپن", "type": "country"}, {"text": "سیب", "type": "other"}]},
        {"entities": [{"text": "ژاپن", "type": "country"}]},
    ]
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records), encoding="utf-8")

    counts = count_entities(path)

    assert counts["country"]["ژاپن"] == 2
    assert "سیب" not in counts["person"]
