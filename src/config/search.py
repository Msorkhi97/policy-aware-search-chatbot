from pydantic import BaseModel


class SearchConfig(BaseModel):
    search_language: str = "fa"
    search_top_k: int = 3

    search_user_agent: str = "PolicyAwareSearchChatbot/1.0 (contact: you@example.com)"
