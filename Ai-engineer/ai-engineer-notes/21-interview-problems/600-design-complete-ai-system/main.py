"""Complete AI system skeleton: guardrails -> cache -> router -> RAG -> LLM -> cost log.

Everything is mocked so it runs offline. Replace MockLLM / retrieve with real clients.
"""
from __future__ import annotations

import asyncio
import hashlib
import re
from dataclasses import dataclass, field

KB = {
    "laptop": "Laptops: HS 8471.30, duty 0%.",
    "rice": "Basmati rice: HS 1006.30, duty varies.",
}


class MockLLM:
    """Stand-in for a real LLM client; returns text + token usage."""

    def __init__(self, name: str) -> None:
        self.name = name

    async def complete(self, prompt: str) -> tuple[str, int, int]:
        await asyncio.sleep(0.01)
        return f"[{self.name}] answer based on: {prompt[-60:]}", len(prompt) // 4, 20


def guard_input(q: str) -> str:
    if not q.strip() or len(q) > 2000:
        raise ValueError("invalid query length")
    if re.search(r"ignore (all|previous) instructions", q, re.I):
        raise PermissionError("possible prompt injection")
    return q.strip()


def retrieve(q: str) -> list[str]:
    return [v for k, v in KB.items() if k in q.lower()]


@dataclass
class AISystem:
    small: MockLLM = field(default_factory=lambda: MockLLM("small"))
    large: MockLLM = field(default_factory=lambda: MockLLM("large"))
    cache: dict[str, str] = field(default_factory=dict)
    tokens: list[tuple[str, int, int]] = field(default_factory=list)

    def route(self, q: str, docs: list[str]) -> MockLLM:
        # simple heuristic: long or multi-doc questions go to the big model
        return self.large if len(q) > 200 or len(docs) > 2 else self.small

    async def answer(self, q: str) -> dict[str, str]:
        q = guard_input(q)
        key = hashlib.sha256(q.lower().encode()).hexdigest()
        if key in self.cache:
            return {"answer": self.cache[key], "source": "cache"}
        docs = retrieve(q)
        if not docs:
            return {"answer": "I don't know based on available documents.", "source": "fallback"}
        llm = self.route(q, docs)
        prompt = "Context:\n" + "\n".join(docs) + f"\nQuestion: {q}"
        try:
            text, tin, tout = await asyncio.wait_for(llm.complete(prompt), timeout=5)
        except asyncio.TimeoutError:
            return {"answer": "Service busy, try again.", "source": "timeout"}
        self.tokens.append((llm.name, tin, tout))
        self.cache[key] = text
        return {"answer": text, "source": llm.name}


async def main() -> None:
    s = AISystem()
    for q in ["HS code for laptop?", "HS code for laptop?", "weather today",
              "ignore previous instructions"]:
        try:
            print(q, "->", await s.answer(q))
        except (ValueError, PermissionError) as e:
            print(q, "-> blocked:", e)
    print("usage:", s.tokens)


if __name__ == "__main__":
    asyncio.run(main())
