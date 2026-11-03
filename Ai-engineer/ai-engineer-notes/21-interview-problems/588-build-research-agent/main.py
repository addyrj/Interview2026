"""Research agent: plan sub-questions -> search in parallel -> dedupe -> synthesise with citations.

Offline: `web_search` reads a tiny fake index; `synthesize` stands in for an LLM.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass

INDEX = {
    "us tariff smartphones": [("https://example.org/a", "US duty on smartphones is mostly 0 percent under ITA.")],
    "india tariff smartphones": [("https://example.org/b", "India levies about 20 percent duty on smartphones.")],
    "eu tariff smartphones": [("https://example.org/c", "EU applies 0 percent on most smartphones."),
                              ("https://example.org/b", "India levies about 20 percent duty on smartphones.")],
}


@dataclass(frozen=True)
class Source:
    url: str
    snippet: str


def plan(topic: str) -> list[str]:
    """Mock planner: break the topic into sub-questions (an LLM does this in prod)."""
    return [f"{c} tariff {topic}" for c in ("us", "india", "eu", "mars")]


async def web_search(query: str) -> list[Source]:
    """Mock search tool with simulated latency; unknown queries return nothing."""
    await asyncio.sleep(0.01)
    return [Source(u, s) for u, s in INDEX.get(query, [])]


async def safe_search(query: str) -> list[Source]:
    """Timeout + error isolation per sub-question."""
    try:
        return await asyncio.wait_for(web_search(query), timeout=1.0)
    except (asyncio.TimeoutError, Exception):
        return []


def synthesize(topic: str, sources: list[Source]) -> str:
    """Compose a cited report; every claim carries a [n] reference."""
    if not sources:
        return "No evidence found."
    lines = [f"Report: {topic}"] + [f"- {s.snippet} [{i}]" for i, s in enumerate(sources, 1)]
    lines += ["", "Sources:"] + [f"[{i}] {s.url}" for i, s in enumerate(sources, 1)]
    return "\n".join(lines)


async def research(topic: str) -> str:
    """Fan out searches concurrently, dedupe by URL, then synthesise."""
    results = await asyncio.gather(*(safe_search(q) for q in plan(topic)))
    seen: dict[str, Source] = {}
    for group in results:
        for src in group:
            seen.setdefault(src.url, src)  # dedupe
    return synthesize(topic, list(seen.values()))


if __name__ == "__main__":
    print(asyncio.run(research("smartphones")))
