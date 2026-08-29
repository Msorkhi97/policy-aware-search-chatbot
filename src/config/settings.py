from functools import lru_cache

from dotenv import load_dotenv

from src.config.analytics import AnalyticsConfig
from src.config.conversation import ConversationConfig
from src.config.moderation import ModerationConfig
from src.config.search import SearchConfig


class Settings:
    def __init__(self):
        self.moderation = ModerationConfig()
        self.search = SearchConfig()
        self.analytics = AnalyticsConfig()
        self.conversation = ConversationConfig()


@lru_cache
def get_settings() -> Settings:
    load_dotenv()
    return Settings()
