from pydantic import BaseModel


class LLMConfig(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4o-mini"
