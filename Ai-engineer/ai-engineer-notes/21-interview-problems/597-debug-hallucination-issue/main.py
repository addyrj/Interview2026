"""Debug hallucination: check whether answer claims are grounded in retrieved context.

Offline. Lexical overlap is a cheap first-pass detector; real systems add an
NLI model or LLM-judge on top.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

STOP = {"the", "a", "an", "is", "are", "of", "for", "to", "in", "and", "under", "falls", "it"}

CONTEXT = [
    "HS code 8517.13 covers smartphones. Duty rate is 0 percent.",
    "HS code 8471.30 covers portable computers such as laptops.",
]


def words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+(?:\.[0-9]+)*", s.lower()) if w not in STOP}


def sentences(s: str) -> list[str]:
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+", s) if x.strip()]


@dataclass
class ClaimCheck:
    sentence: str
    support: float  # fraction of claim words found in context
    grounded: bool


def check_answer(answer: str, context: list[str], threshold: float = 0.6) -> list[ClaimCheck]:
    if not context:
        raise ValueError("empty context: any answer is ungrounded")
    ctx_words = set().union(*(words(c) for c in context))
    results = []
    for s in sentences(answer):
        w = words(s)
        support = len(w & ctx_words) / len(w) if w else 1.0
        results.append(ClaimCheck(s, round(support, 2), support >= threshold))
    return results


def diagnose(checks: list[ClaimCheck]) -> str:
    bad = [c for c in checks if not c.grounded]
    if not bad:
        return "OK: all claims grounded"
    return (f"{len(bad)}/{len(checks)} claims ungrounded. Check: retrieval recall, "
            "prompt allows outside knowledge, temperature, missing 'say I don't know' rule.")


if __name__ == "__main__":
    answer = ("Smartphones fall under HS code 8517.13. "
              "The import duty is 25 percent plus a special luxury surcharge.")
    checks = check_answer(answer, CONTEXT)
    for c in checks:
        print(f"{c.support:.2f} {'OK ' if c.grounded else 'BAD'} {c.sentence}")
    print(diagnose(checks))
