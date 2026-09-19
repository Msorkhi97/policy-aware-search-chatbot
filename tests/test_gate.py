from src.agent.node.gate import route_after_gate
from src.contracts.models import ModerationResult, TopicResult


def safe_moderation() -> ModerationResult:
    return ModerationResult(is_political=False, category="none")


def test_routes_to_refuse_without_moderation():
    assert route_after_gate({}) == "refuse"


def test_routes_to_refuse_when_political():
    state = {"moderation": ModerationResult(is_political=True, category="person")}

    assert route_after_gate(state) == "refuse"


def test_routes_to_direct_reply_when_search_not_needed():
    state = {
        "moderation": safe_moderation(),
        "topic_result": TopicResult(needs_search=False),
    }

    assert route_after_gate(state) == "direct_reply"


def test_routes_to_retrieve_when_search_needed():
    state = {
        "moderation": safe_moderation(),
        "topic_result": TopicResult(needs_search=True),
    }

    assert route_after_gate(state) == "retrieve"
