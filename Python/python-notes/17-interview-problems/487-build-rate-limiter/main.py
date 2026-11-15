"""Build Rate Limiter: token bucket + sliding window + FastAPI dependency. Run: python main.py"""
from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Callable

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.testclient import TestClient


class TokenBucket:
    def __init__(self, capacity: int, refill_per_sec: float, clock: Callable[[], float] = time.monotonic) -> None:
        self.capacity, self.rate, self.clock = capacity, refill_per_sec, clock
        self.tokens = float(capacity)
        self.last = clock()

    def allow(self, cost: int = 1) -> bool:
        now = self.clock()
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)  # refill
        self.last = now
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False


class SlidingWindowLimiter:
    def __init__(self, limit: int, window: float, clock: Callable[[], float] = time.monotonic) -> None:
        self.limit, self.window, self.clock = limit, window, clock
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = self.clock()
        q = self.hits[key]
        while q and q[0] <= now - self.window:
            q.popleft()  # forget old requests
        if len(q) >= self.limit:
            return False
        q.append(now)
        return True


limiter = SlidingWindowLimiter(limit=3, window=60)
app = FastAPI()


def rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    if not limiter.allow(ip):
        raise HTTPException(status_code=429, detail="Too Many Requests", headers={"Retry-After": "60"})


@app.get("/ping", dependencies=[Depends(rate_limit)])
def ping() -> dict[str, str]:
    return {"msg": "pong"}


if __name__ == "__main__":
    t = [0.0]
    tb = TokenBucket(capacity=3, refill_per_sec=1, clock=lambda: t[0])
    print([tb.allow() for _ in range(5)])  # burst of 3 then blocked
    t[0] = 2  # 2 seconds later: 2 tokens refilled
    print([tb.allow() for _ in range(3)])
    assert [tb.allow() for _ in range(1)] == [False]

    c = TestClient(app)
    codes = [c.get("/ping").status_code for _ in range(5)]
    print(codes)
    assert codes == [200, 200, 200, 429, 429]
    print("all ok")
