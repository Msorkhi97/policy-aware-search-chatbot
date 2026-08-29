from pathlib import Path

from pydantic import BaseModel


class AnalyticsConfig(BaseModel):
    analytics_path: Path = Path("data/analytics/interactions.jsonl")
