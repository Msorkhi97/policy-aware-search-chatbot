# Policy-Aware Search Chatbot

A Persian-language chatbot that answers encyclopedic questions **only from retrieved Wikipedia sources** and refuses politically sensitive topics. Every question passes through a moderation and topic-analysis pipeline built as a [LangGraph](https://langchain-ai.github.io/langgraph/) state graph, and answers are streamed to a lightweight web UI together with the sources that were used.

## Features

- **Source-grounded answers**: the model answers strictly from Persian Wikipedia extracts, never from its own memory. If the sources don't contain the answer, it says so.
- **Two-layer political moderation**: a rule-based lexicon of political figures and hard terms runs first, then an LLM classifier judges the rest in context (mentioning a country is fine, political questions about it are not). Any failure in the moderation step fails closed (the question is refused).
- **Source screening**: retrieved documents are filtered against the same lexicon before they ever reach the model.
- **Entity extraction & routing**: an LLM extracts entities and decides whether a question needs search at all. Greetings and small talk are answered directly instead of triggering a search.
- **Conversation awareness**: follow-up questions are resolved using the previous turns.
- **Persian text normalization** with [hazm](https://github.com/roshan-research/hazm).
- **Streaming responses** over newline-delimited JSON.
- **Analytics**: every interaction is logged as JSONL (entities and moderation outcome only, never the raw question text) and an Excel report of the most requested people and countries is available for download.
- **Server-side sessions**: conversation history and the per-conversation question limit are tracked on the server, so clients can neither forge history nor bypass the limit within a session. Sessions expire after inactivity.

## Architecture

```
                     ┌── moderate ──────┐
START → preprocess ──┤                  ├─→ gate ─┬─ political / error ─→ refuse ─────────→ END
                     └── extract_entities ┘        ├─ no search needed ──→ direct_reply ────→ END
                                                    └─ search needed ─────→ retrieve → screen_context → generate → END
```

| Node               | Responsibility                                                                 |
| ------------------ | ------------------------------------------------------------------------------ |
| `preprocess`       | Normalizes the Persian question                                                |
| `moderate`         | Lexicon rules, then LLM classification of political sensitivity                |
| `extract_entities` | Extracts entities and decides whether the question needs search (runs in parallel with `moderate`) |
| `gate`             | Routes to refusal, direct reply, or retrieval                                  |
| `retrieve`         | Queries Wikipedia using the non-sensitive entities                             |
| `screen_context`   | Drops retrieved documents that match sensitive figures or terms                |
| `generate`         | Builds the grounded prompt; the final answer is streamed by the API layer      |

### Project layout

```
├── src/
│   ├── api/            FastAPI app (chat stream, Excel report, static UI)
│   ├── agent/          LangGraph graph, state and nodes
│   ├── services/       Classifiers, Wikipedia search, normalizer, sessions, analytics
│   ├── llm/            Provider-agnostic LLM wrapper and OpenAI provider
│   ├── prompts/        Prompt templates
│   ├── config/         Settings and the political lexicons (JSON)
│   └── contracts/      Pydantic request/response models
├── web/                Chat UI (HTML, CSS, vanilla JS)
├── scripts/            Debug runner for the graph
└── tests/              Unit tests
```

## Getting started

### Prerequisites

- Python 3.10+
- An OpenAI API key

### Installation

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

Copy the example environment file and add your key:

```bash
cp .env.example .env
```

| Variable          | Description                                              |
| ----------------- | -------------------------------------------------------- |
| `OPENAI_API_KEY`  | Your OpenAI API key                                      |
| `OPENAI_BASE_URL` | Optional. Custom endpoint for proxies or compatible APIs |

Application settings live in `src/config/`:

| File              | What it controls                                     |
| ----------------- | ---------------------------------------------------- |
| `llm.py`          | LLM provider and model                               |
| `search.py`       | Wikipedia language, number of results, user agent    |
| `conversation.py` | Question limit per conversation and session lifetime |
| `moderation.py`   | Refusal and fallback messages                        |
| `analytics.py`    | Location of the interaction log                      |

### Run

```bash
uvicorn --reload src.api.app:app
```

Open <http://127.0.0.1:8000> in your browser.

To run the graph once without the server:

```bash
python -m scripts.debug_run
```

### Tests

```bash
pytest
```

## API

### `POST /chat`

Request body:

```json
{
  "question": "فتوسنتز چیست؟",
  "session_id": null
}
```

Send `session_id: null` for the first question; the server creates the session and returns its id in the final event. Send that id with every following question of the same conversation. Reloading the page starts a new conversation.

The response is a stream of newline-delimited JSON. Text arrives as `{"chunk": "..."}` events, followed by a final event:

```json
{
  "done": true,
  "request_id": "a1b2c3d4e5f6",
  "session_id": "0f8e...",
  "answer": "...",
  "refused": false,
  "moderation": { "is_political": false, "category": "none", "reason": "...", "source": "llm" },
  "entities": [{ "text": "فتوسنتز", "type": "scientific_concept", "sensitivity": false }],
  "sources": [{ "title": "...", "content": "...", "url": "..." }],
  "limit_reached": false
}
```

### `GET /entity-report.xlsx`

Downloads an Excel report with the number of times each person and country was mentioned.

## Tech stack

Python · FastAPI · LangGraph · LangChain · OpenAI · hazm · httpx · openpyxl · vanilla JS
