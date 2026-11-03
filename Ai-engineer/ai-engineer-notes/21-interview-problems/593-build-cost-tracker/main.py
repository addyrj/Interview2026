"""Cost tracker: records LLM usage, computes cost, enforces per-user budgets.

Runs offline. Prices are ILLUSTRATIVE (USD per 1M tokens) - check provider pages.
"""
from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone

# Illustrative prices per 1M tokens: (input, output, cached_input)
PRICES: dict[str, tuple[float, float, float]] = {
    "small-model": (0.15, 0.60, 0.075),
    "large-model": (3.00, 15.00, 0.30),
}


class BudgetExceeded(Exception):
    """Raised when a user would go over their budget."""


@dataclass(frozen=True)
class UsageRecord:
    user: str
    model: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    cost_usd: float
    ts: datetime


@dataclass
class CostTracker:
    budgets: dict[str, float] = field(default_factory=dict)  # per-user USD limit
    records: list[UsageRecord] = field(default_factory=list)
    _spent: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    @staticmethod
    def compute_cost(model: str, inp: int, out: int, cached: int = 0) -> float:
        if model not in PRICES:
            raise KeyError(f"unknown model: {model}")
        if min(inp, out, cached) < 0 or cached > inp:
            raise ValueError("invalid token counts")
        p_in, p_out, p_cache = PRICES[model]
        fresh = inp - cached  # cached tokens are billed at the cheaper rate
        return (fresh * p_in + cached * p_cache + out * p_out) / 1_000_000

    async def record(self, user: str, model: str, inp: int, out: int,
                     cached: int = 0) -> UsageRecord:
        cost = self.compute_cost(model, inp, out, cached)
        async with self._lock:  # keep read-check-write atomic
            limit = self.budgets.get(user)
            if limit is not None and self._spent[user] + cost > limit:
                raise BudgetExceeded(f"{user} would exceed ${limit:.4f}")
            self._spent[user] += cost
            rec = UsageRecord(user, model, inp, out, cached, cost,
                              datetime.now(timezone.utc))
            self.records.append(rec)
            return rec

    def report(self) -> dict[str, dict[str, float]]:
        out: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        for r in self.records:
            out[r.user][r.model] += r.cost_usd
        return {u: dict(m) for u, m in out.items()}


async def main() -> None:
    t = CostTracker(budgets={"amit": 0.001})
    await t.record("amit", "small-model", 500, 200)
    await t.record("zomato-svc", "large-model", 2000, 500, cached=1500)
    try:
        for _ in range(10):
            await t.record("amit", "large-model", 400, 100)
    except BudgetExceeded as e:
        print("blocked:", e)
    print(t.report())


if __name__ == "__main__":
    asyncio.run(main())
