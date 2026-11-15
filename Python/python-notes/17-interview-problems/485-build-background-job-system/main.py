"""Build Background Job System: in-memory queue + async workers + retries. Run: python main.py"""
from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable


@dataclass
class Job:
    name: str
    payload: dict[str, Any]
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    status: str = "queued"  # queued -> running -> done | failed
    attempts: int = 0
    result: Any = None
    error: str | None = None


class JobQueue:
    def __init__(self, workers: int = 2, max_retries: int = 2) -> None:
        self.queue: asyncio.Queue[Job] = asyncio.Queue()
        self.jobs: dict[str, Job] = {}
        self.handlers: dict[str, Callable[[dict[str, Any]], Awaitable[Any]]] = {}
        self.workers = workers
        self.max_retries = max_retries
        self._tasks: list[asyncio.Task[None]] = []

    def register(self, name: str):
        def deco(fn: Callable[[dict[str, Any]], Awaitable[Any]]):
            self.handlers[name] = fn  # map job name -> coroutine function
            return fn
        return deco

    def enqueue(self, name: str, **payload: Any) -> Job:
        job = Job(name, payload)
        self.jobs[job.id] = job  # status lookup by id (like a /jobs/{id} endpoint)
        self.queue.put_nowait(job)
        return job

    async def _worker(self) -> None:
        while True:
            job = await self.queue.get()  # block until a job arrives
            job.status = "running"
            job.attempts += 1
            try:
                job.result = await self.handlers[job.name](job.payload)
                job.status = "done"
            except Exception as exc:
                if job.attempts <= self.max_retries:
                    job.status = "queued"
                    await asyncio.sleep(0.01 * 2 ** job.attempts)  # exponential backoff
                    self.queue.put_nowait(job)  # retry
                else:
                    job.status, job.error = "failed", repr(exc)
            finally:
                self.queue.task_done()

    def start(self) -> None:
        self._tasks = [asyncio.create_task(self._worker()) for _ in range(self.workers)]

    async def join(self) -> None:
        await self.queue.join()  # wait until every job is finished

    async def stop(self) -> None:
        for t in self._tasks:
            t.cancel()  # workers loop forever, so cancel them
        await asyncio.gather(*self._tasks, return_exceptions=True)


async def main() -> None:
    q = JobQueue(workers=2, max_retries=2)
    calls = {"flaky": 0}

    @q.register("square")
    async def square(p: dict[str, Any]) -> int:
        await asyncio.sleep(0.01)
        return p["n"] ** 2

    @q.register("flaky")
    async def flaky(p: dict[str, Any]) -> str:
        calls["flaky"] += 1
        if calls["flaky"] < 3:
            raise RuntimeError("temporary failure")
        return "ok after retries"

    @q.register("broken")
    async def broken(p: dict[str, Any]) -> None:
        raise ValueError("always fails")

    q.start()
    j1, j2, j3 = q.enqueue("square", n=7), q.enqueue("flaky"), q.enqueue("broken")
    await q.join()
    await q.stop()
    for j in (j1, j2, j3):
        print(j.name, j.status, j.attempts, j.result, j.error)
    assert (j1.status, j1.result) == ("done", 49)
    assert (j2.status, j2.attempts) == ("done", 3)
    assert (j3.status, j3.attempts) == ("failed", 3)
    print("all ok")


if __name__ == "__main__":
    asyncio.run(main())
