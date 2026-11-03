"""RAG evaluation: retrieval metrics (hit@k, recall@k, MRR) + generation metrics (faithfulness,
answer match) over a labelled golden set. LLM-as-judge is mocked by token overlap (illustrative).
"""
from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass


@dataclass
class Case:
    question: str
    relevant: set[str]        # gold doc ids
    gold_answer: str
    retrieved: list[str]      # what our retriever returned (ranked)
    context: str              # text given to the LLM
    answer: str               # what the LLM said


GOLDEN = [
    Case("duty on smartphones", {"d1"}, "20 percent", ["d1", "d4"], "smartphones duty is 20 percent", "The duty is 20 percent"),
    Case("duty on laptops", {"d2"}, "0 percent", ["d4", "d2"], "laptops 0 percent", "The duty is 0 percent"),
    Case("origin rules", {"d5"}, "certificate of origin", ["d3", "d4"], "apparel duty 12 percent", "You need a visa"),
]


def hit_at_k(c: Case, k: int) -> float:
    return float(bool(set(c.retrieved[:k]) & c.relevant))


def recall_at_k(c: Case, k: int) -> float:
    return len(set(c.retrieved[:k]) & c.relevant) / len(c.relevant)


def mrr(c: Case) -> float:
    for rank, d in enumerate(c.retrieved, 1):
        if d in c.relevant:
            return 1 / rank
    return 0.0


def toks(s: str) -> set[str]:
    return set(re.findall(r"\w+", s.lower()))


def faithfulness(c: Case) -> float:
    """Share of answer words supported by the context (mock for an LLM judge)."""
    a = toks(c.answer) - {"the", "is", "you", "a"}
    return len(a & toks(c.context)) / max(1, len(a))


def answer_match(c: Case) -> float:
    return float(toks(c.gold_answer) <= toks(c.answer))


async def evaluate(cases: list[Case], k: int = 2) -> dict[str, float]:
    """Aggregate metrics; empty set raises so CI never silently passes."""
    if not cases:
        raise ValueError("golden set is empty")
    n = len(cases)
    return {
        f"hit@{k}": sum(hit_at_k(c, k) for c in cases) / n,
        f"recall@{k}": sum(recall_at_k(c, k) for c in cases) / n,
        "mrr": sum(mrr(c) for c in cases) / n,
        "faithfulness": sum(faithfulness(c) for c in cases) / n,
        "answer_match": sum(answer_match(c) for c in cases) / n,
    }


if __name__ == "__main__":
    report = asyncio.run(evaluate(GOLDEN))
    for name, val in report.items():
        print(f"{name:14s} {val:.2f}")
    threshold = 0.6
    failed = [m for m, v in report.items() if v < threshold]
    print("CI gate:", "FAIL " + str(failed) if failed else "PASS")
