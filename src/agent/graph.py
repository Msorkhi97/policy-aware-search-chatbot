from langgraph.graph import END, START, StateGraph

from src.agent.node import (
    direct_reply,
    extract_entities,
    gate,
    generate,
    moderate,
    preprocess,
    refuse,
    retrieve,
    screen_context,
)
from src.agent.state import ChatState

NODES = [
    ("preprocess", preprocess.run),
    ("moderate", moderate.run),
    ("extract_entities", extract_entities.run),
    ("gate", gate.run),
    ("refuse", refuse.run),
    ("direct_reply", direct_reply.run),
    ("retrieve", retrieve.run),
    ("screen_context", screen_context.run),
    ("generate", generate.run),
]


def build_graph():
    graph = StateGraph(ChatState)
    for name, node_fn in NODES:
        graph.add_node(name, node_fn)

    graph.add_edge(START, "preprocess")

    graph.add_edge("preprocess", "moderate")
    graph.add_edge("preprocess", "extract_entities")
    graph.add_edge("moderate", "gate")
    graph.add_edge("extract_entities", "gate")

    graph.add_conditional_edges(
        "gate",
        gate.route_after_gate,
        {"refuse": "refuse", "direct_reply": "direct_reply", "retrieve": "retrieve"},
    )

    graph.add_edge("retrieve", "screen_context")
    graph.add_edge("screen_context", "generate")

    graph.add_edge("refuse", END)
    graph.add_edge("direct_reply", END)
    graph.add_edge("generate", END)

    return graph.compile()
