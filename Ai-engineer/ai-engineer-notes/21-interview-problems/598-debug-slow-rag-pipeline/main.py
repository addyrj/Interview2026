"""Debug a slow RAG pipeline: stage timing profiler + parallelism fix. Offline (simulated)."""
from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator


class Profiler:
    def __init__(self) -> None:
        self.stages: dict[str, float] = {}

    @asynccontextmanager
    async def stage(self, name: str) -> AsyncIterator[None]:
        t0 = time.perf_counter()
        try:
            yield
        finally:  # record even if the stage raises
            self.stages[name] = time.perf_counter() - t0

    def report(self) -> str:
        total = sum(self.stages.values()) or 1e-9
        rows = sorted(self.stages.items(), key=lambda kv: -kv[1])
        return "\n".join(f"{n:<14}{s*1000:7.0f} ms {s/total:5.0%}" for n, s in rows)


# Simulated stages (sleep = fake latency)
async def embed(q: str) -> list[float]:
    await asyncio.sleep(0.05); return [0.1]

async def vector_search(v: list[float]) -> list[str]:
    await asyncio.sleep(0.08); return ["chunk1", "chunk2"]

async def keyword_search(q: str) -> list[str]:
    await asyncio.sleep(0.07); return ["chunk3"]

async def rerank(q: str, docs: list[str]) -> list[str]:
    await asyncio.sleep(0.15); return docs

async def llm(q: str, docs: list[str]) -> str:
    await asyncio.sleep(0.4); return "answer"


async def slow_pipeline(q: str, p: Profiler) -> str:
    async with p.stage("embed"):
        v = await embed(q)
    async with p.stage("vector"):
        a = await vector_search(v)
    async with p.stage("keyword"):  # independent, yet run sequentially (bug)
        b = await keyword_search(q)
    async with p.stage("rerank"):
        docs = await rerank(q, a + b)
    async with p.stage("llm"):
        return await llm(q, docs)


async def fast_pipeline(q: str, p: Profiler) -> str:
    async with p.stage("retrieve"):  # keyword search overlaps embed+vector
        (v_docs, k_docs) = await asyncio.gather(
            _dense(q), keyword_search(q))
    async with p.stage("rerank"):
        docs = await rerank(q, (v_docs + k_docs)[:3])  # rerank fewer docs
    async with p.stage("llm"):
        return await llm(q, docs)


async def _dense(q: str) -> list[str]:
    return await vector_search(await embed(q))


async def main() -> None:
    for fn in (slow_pipeline, fast_pipeline):
        p = Profiler()
        t0 = time.perf_counter()
        await fn("hs code laptop", p)
        print(f"--- {fn.__name__}: {(time.perf_counter()-t0)*1000:.0f} ms total")
        print(p.report())


if __name__ == "__main__":
    asyncio.run(main())
