"""Debug high token usage: analyse request logs, find the offenders, suggest fixes. Offline."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

PRICE_IN, PRICE_OUT = 3.00, 15.00  # illustrative USD per 1M tokens


@dataclass(frozen=True)
class Call:
    endpoint: str
    system_tokens: int
    history_tokens: int
    context_tokens: int
    user_tokens: int
    output_tokens: int

    @property
    def input_tokens(self) -> int:
        return self.system_tokens + self.history_tokens + self.context_tokens + self.user_tokens

    @property
    def cost(self) -> float:
        return (self.input_tokens * PRICE_IN + self.output_tokens * PRICE_OUT) / 1e6


LOGS = [
    Call("/classify", 900, 0, 300, 40, 60),
    Call("/classify", 900, 0, 320, 35, 70),
    Call("/chat", 400, 6000, 1500, 50, 400),
    Call("/chat", 400, 9000, 1500, 60, 500),
    Call("/summarize", 200, 0, 12000, 30, 800),
]


def analyse(calls: list[Call]) -> dict[str, dict[str, float]]:
    if not calls:
        raise ValueError("no logs")
    agg: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for c in calls:
        a = agg[c.endpoint]
        a["calls"] += 1
        a["cost"] += c.cost
        for part in ("system_tokens", "history_tokens", "context_tokens", "user_tokens", "output_tokens"):
            a[part] += getattr(c, part)
    return {k: dict(v) for k, v in agg.items()}


def advise(stats: dict[str, dict[str, float]]) -> list[str]:
    tips = []
    for ep, a in stats.items():
        inp = a["system_tokens"] + a["history_tokens"] + a["context_tokens"] + a["user_tokens"]
        if a["history_tokens"] / inp > 0.5:
            tips.append(f"{ep}: history is >50% of input -> summarise/trim old turns")
        if a["system_tokens"] / inp > 0.5:
            tips.append(f"{ep}: long system prompt dominates -> shorten or use prompt caching")
        if a["context_tokens"] / inp > 0.7:
            tips.append(f"{ep}: retrieved context huge -> lower top-k, rerank, compress")
        if a["output_tokens"] / a["calls"] > 500:
            tips.append(f"{ep}: long outputs -> set max_tokens, ask for concise format")
    return tips


if __name__ == "__main__":
    stats = analyse(LOGS)
    for ep, a in sorted(stats.items(), key=lambda kv: -kv[1]["cost"]):
        print(f"{ep:<11} calls={int(a['calls'])} cost=${a['cost']:.4f}")
    print("\n".join(advise(stats)))
