from langchain_openai import ChatOpenAI

from src.llm.base import BaseLLM


class OpenAiProvider(BaseLLM):
    def __init__(self, model: str, temperature: float = 0.2):
        self.llm = ChatOpenAI(model=model, temperature=temperature)

    async def generate(self, input, **kwargs) -> str:
        response = await self.llm.ainvoke(input, **kwargs)
        return response.content

    async def generate_stream(self, input, **kwargs):
        async for chunk in self.llm.astream(input, **kwargs):
            yield chunk.content
