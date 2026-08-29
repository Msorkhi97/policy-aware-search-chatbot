from src.agent.state import ChatState
from src.services.sensitivity_classifier import contains_word, load_lexicon
from src.services.normalizer import PersianTextNormalizer


normalizer = PersianTextNormalizer()


def contains_term(text: str, terms: list[str]) -> bool:
    text = normalizer.normalize(text).lower()

    for term in terms:
        if contains_word(text, term.lower()):
            return True

    return False


def is_sensitive_document(document) -> bool:
    lexicon = load_lexicon()

    title = document.title
    content = document.content

    if contains_term(
        title,
        [
            item["name"]
            for item in lexicon["people"]
        ],
    ):
        return True

    if contains_term(
        title,
        [
            item["name"]
            for item in lexicon["terms"]
            if item.get("hard", False)
        ],
    ):
        return True

    hard_terms = [
        item["name"]
        for item in lexicon["terms"]
        if item.get("hard", False)
    ]

    return contains_term(content, hard_terms)


async def run(state: ChatState) -> dict:
    documents = state.get("documents", [])

    safe_documents = [
        document
        for document in documents
        if not is_sensitive_document(document)
    ]

    return {
        "documents": safe_documents
    }