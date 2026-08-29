import json

from src.llm.provider.openai_provider import OpenAiProvider

class LLM:

    providers = {
        "openai":OpenAiProvider
    }

    def __init__(self, provider:str, model:str):

        self.model = model
        self.provider_cls = self.providers[provider]
        self.provider = self.provider_cls(model=model)


    def generate(self, messages, **kwargs):
        return self.provider.generate(input=messages, **kwargs)

    async def generate_stream(self, messages, **kwargs):
        async for chunk in self.provider.generate_stream(input=messages, **kwargs):
            yield chunk

    async def generate_json(self, messages, **kwargs):
        text = await self.generate(messages, **kwargs)

        text = text.strip()

        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
            text = text.strip()

        return json.loads(text)