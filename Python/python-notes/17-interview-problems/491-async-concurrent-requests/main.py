"""Async Concurrent Requests: gather + Semaphore + timeout + per-task errors. pip install httpx"""
from __future__ import annotations

import asyncio
import time

import httpx


def handler(request: httpx.Request) -> httpx.Response:
    """Fake server so the demo runs offline."""
    n = int(request.url.path.strip("/"))
    if n == 3:
        return httpx.Response(500, json={"error": "server"})
    return httpx.Response(200, json={"id": n})


async def fetch(client: httpx.AsyncClient, sem: asyncio.Semaphore, n: int) -> dict:
    async with sem:  # at most N requests in flight
        await asyncio.sleep(0.1)  # pretend network latency
        r = await client.get(f"http://api.test/{n}")
        r.raise_for_status()
        return r.json()


async def main() -> None:
    sem = asyncio.Semaphore(5)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), timeout=5) as client:
        t0 = time.perf_counter()
        results = await asyncio.gather(*(fetch(client, sem, n) for n in range(1, 11)),
                                       return_exceptions=True)  # one failure doesn't cancel the rest
        elapsed = time.perf_counter() - t0
    ok = [r for r in results if isinstance(r, dict)]
    bad = [r for r in results if isinstance(r, Exception)]
    print(len(ok), "ok;", len(bad), "failed:", type(bad[0]).__name__)
    print("elapsed ~", round(elapsed, 1), "s (sequential would be ~1.0s)")
    assert len(ok) == 9 and len(bad) == 1 and elapsed < 0.6

    async def slow() -> None:
        await asyncio.sleep(5)
    try:
        await asyncio.wait_for(slow(), timeout=0.1)
    except TimeoutError:  # 3.11+: asyncio.TimeoutError is TimeoutError
        print("timeout handled")

    async with asyncio.TaskGroup() as tg:  # 3.11+: structured concurrency
        t1 = tg.create_task(asyncio.sleep(0.01, "a"))
        t2 = tg.create_task(asyncio.sleep(0.01, "b"))
    print(t1.result(), t2.result())
    print("all ok")


if __name__ == "__main__":
    asyncio.run(main())
