import httpx

from src.config.search import SearchConfig
from src.contracts.models import SearchDocument

FILLER_PHRASES = [
    "چگونه به وجود می‌آید",
    "چطوری به وجود میاد",
    "چطور به وجود میاد",
    "چگونه کار می‌کند",
    "چطوری کار میکنه",
    "چطور کار میکنه",
    "انجام می‌شود",
    "توضیح بده",
]
FILLER_WORDS = [
    "بهترین",
    "چیست",
    "چیه",
    "چگونه",
    "چطور",
    "چطوری",
    "کیست",
    "کجاست",
    "آیا",
    "لطفا",
    "لطفاً",
    "بگو",
    "برای",
    "را",
    "؟",
    "?",
]


def simplify_query(question: str) -> str:
    text = question
    for phrase in FILLER_PHRASES:
        text = text.replace(phrase, " ")
    for word in FILLER_WORDS:
        text = text.replace(word, " ")
    return " ".join(text.split()) or question


def keep_relevant(documents: list[SearchDocument], query: str) -> list[SearchDocument]:
    tokens = {token for token in query.split() if len(token) > 2}
    return [
        document
        for index, document in enumerate(documents)
        if index == 0 or any(token in document.title for token in tokens)
    ]


async def wikipedia_search(query: str, config: SearchConfig) -> list[SearchDocument]:
    params = {
        "action": "query",
        "format": "json",
        "formatversion": 2,
        "generator": "search",
        "gsrsearch": query,
        "gsrlimit": config.search_top_k,
        "prop": "extracts|info",
        "inprop": "url",
        "exintro": 1,
        "explaintext": 1,
        "exlimit": "max",
    }

    url = f"https://{config.search_language}.wikipedia.org/w/api.php"

    headers = {"User-Agent": config.search_user_agent}

    payload = None
    for attempt in range(2):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                payload = response.json()
            break
        except httpx.HTTPError as exc:
            if attempt == 1:
                print(f"جست‌وجوی ویکی‌پدیا برای «{query}» شکست خورد: {exc}")
                return []

    pages = payload.get("query", {}).get("pages", [])

    pages.sort(key=lambda page: page.get("index", 10**6))

    documents = []
    for page in pages:
        extract = (page.get("extract") or "").strip()
        if not extract:
            continue

        documents.append(
            SearchDocument(
                title=page.get("title", ""),
                content=extract[:2000],
                url=page.get("fullurl"),
            )
        )

    return documents
