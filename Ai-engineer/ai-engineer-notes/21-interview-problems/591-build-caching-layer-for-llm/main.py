"""LLM caching: exact-match cache + semantic cache + TTL + hit/miss stats.

Offline: `fake_embed` is a hashed bag-of-words (illustrative); `mock_llm` counts calls.
"""
from __future__ import annotations

import asyncio
import hashlib
import math
import re
import time
from dataclasses import dataclass, field


def norm(text: str) -> str:
    """Normalise so trivial differences hit the same key."""
    return " ".join(re.findall(r"\w+", text.lower()))


def fake_embed(text: str, dim: int = 128) -> list[float]:
    vec = [0.0] * dim
    for w in norm(text).split():
        idx = int(hashlib.md5(w.encode()).hexdigest(), 16) % dim  # stable across runs
        vec[idx] += 1.0
    n = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / n for v in vec]


def cos(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


@dataclass
class Entry:
    answer: str
    expires: float
    vec: list[float]


@dataclass
class LLMCache:
    ttl: float = 3600.0
    threshold: float = 0.8
    store: dict[str, Entry] = field(default_factory=dict)
    hits_exact: int = 0
    hits_semantic: int = 0
    misses: int = 0

    def get(self, prompt: str, now: float | None = None) -> str | None:
        now = time.time() if now is None else now
        key = norm(prompt)
        e = self.store.get(key)
        if e and e.expires > now:
            self.hits_exact += 1
            return e.answer
        qv = fake_embed(prompt)
        live = [x for x in self.store.values() if x.expires > now]
        best = max(live, key=lambda x: cos(qv, x.vec), default=None)
        if best and cos(qv, best.vec) >= self.threshold:
            self.hits_semantic += 1
            return best.answer
        self.misses += 1
        return None

    def put(self, prompt: str, answer: str, now: float | None = None) -> None:
        now = time.time() if now is None else now
        self.store[norm(prompt)] = Entry(answer, now + self.ttl, fake_embed(prompt))


CALLS = {"llm": 0}


async def mock_llm(prompt: str) -> str:
    CALLS["llm"] += 1
    await asyncio.sleep(0.01)
    return "HS 8517.13"


async def cached_ask(cache: LLMCache, prompt: str) -> str:
    """Cache-aside: lookup, else call LLM and store. Never cache failures."""
    hit = cache.get(prompt)
    if hit is not None:
        return hit
    ans = await mock_llm(prompt)
    cache.put(prompt, ans)
    return ans


async def main() -> None:
    c = LLMCache()
    for q in ["HS code for smartphone?", "hs code for smartphone", "HS code for a smartphone please", "HS code for laptop"]:
        print(q, "->", await cached_ask(c, q))
    print("llm calls:", CALLS["llm"], "| exact:", c.hits_exact, "semantic:", c.hits_semantic, "miss:", c.misses)


if __name__ == "__main__":
    asyncio.run(main())
