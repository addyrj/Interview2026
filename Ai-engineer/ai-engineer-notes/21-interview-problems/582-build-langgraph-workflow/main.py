"""A tiny state-graph engine mirroring LangGraph concepts (state, nodes, conditional edges).

Runs offline with stdlib only. At the bottom, `build_langgraph()` shows the same graph with
the real `langgraph` package; it is only used if that package is installed.
"""
from __future__ import annotations

import asyncio
from typing import Any, Callable, TypedDict

END = "__end__"


class State(TypedDict, total=False):
    """Shared state passed between nodes."""

    product: str
    hs_code: str
    confidence: float
    attempts: int
    answer: str


def classify(state: State) -> State:
    """Node 1: (mock) LLM classification; confidence improves on retry."""
    attempts = state.get("attempts", 0) + 1
    conf = 0.5 if attempts == 1 else 0.9
    return {"hs_code": "8517.13", "confidence": conf, "attempts": attempts}


def review(state: State) -> State:
    """Node 2: human/LLM review placeholder that finalises the answer."""
    return {"answer": f"{state['product']} -> {state['hs_code']} (conf {state['confidence']})"}


def route(state: State) -> str:
    """Conditional edge: low confidence loops back to classify (max 3 tries)."""
    if state["confidence"] < 0.8 and state["attempts"] < 3:
        return "classify"
    return "review"


class Graph:
    """Minimal graph runner."""

    def __init__(self) -> None:
        self.nodes: dict[str, Callable[[State], State]] = {}
        self.edges: dict[str, Callable[[State], str] | str] = {}
        self.entry = ""

    def add_node(self, name: str, fn: Callable[[State], State]) -> None:
        self.nodes[name] = fn

    def add_edge(self, src: str, dst: Callable[[State], str] | str) -> None:
        self.edges[src] = dst

    def run(self, state: State, max_steps: int = 20) -> State:
        """Execute from entry; each node returns a partial update merged into state."""
        cur = self.entry
        for _ in range(max_steps):
            state = {**state, **self.nodes[cur](state)}  # type: ignore[typeddict-item]
            nxt = self.edges[cur]
            cur = nxt(state) if callable(nxt) else nxt
            if cur == END:
                return state
        raise RuntimeError("graph exceeded max_steps (cycle?)")

    async def arun(self, state: State) -> State:
        return await asyncio.to_thread(self.run, state)


def build() -> Graph:
    g = Graph()
    g.add_node("classify", classify)
    g.add_node("review", review)
    g.entry = "classify"
    g.add_edge("classify", route)
    g.add_edge("review", END)
    return g


def build_langgraph() -> Any:
    """Same workflow with the real library (only if installed)."""
    from langgraph.graph import StateGraph, END as LG_END  # imported lazily

    sg = StateGraph(State)
    sg.add_node("classify", classify)
    sg.add_node("review", review)
    sg.set_entry_point("classify")
    sg.add_conditional_edges("classify", route, {"classify": "classify", "review": "review"})
    sg.add_edge("review", LG_END)
    return sg.compile()


if __name__ == "__main__":
    print(asyncio.run(build().arun({"product": "smartphone"})))
    try:
        print("langgraph:", build_langgraph().invoke({"product": "smartphone"}))
    except ImportError:
        print("langgraph not installed - skipped (mini engine above is the offline demo)")
