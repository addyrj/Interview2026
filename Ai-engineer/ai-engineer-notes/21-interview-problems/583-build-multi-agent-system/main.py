"""Supervisor + worker multi-agent system (classifier, duty calculator, compliance checker).

Offline: each agent's "LLM" is a deterministic function. The supervisor routes, collects
results into shared state, and stops when all required work is done.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Awaitable, Callable


@dataclass
class Shared:
    """Blackboard that every agent reads/writes."""

    request: dict[str, object]
    results: dict[str, object] = field(default_factory=dict)
    log: list[str] = field(default_factory=list)


async def classifier_agent(s: Shared) -> None:
    """Worker 1: product -> HS code."""
    await asyncio.sleep(0)
    s.results["hs_code"] = "8517.13" if "phone" in str(s.request["product"]).lower() else "9999.99"


async def duty_agent(s: Shared) -> None:
    """Worker 2: needs hs_code, computes duty."""
    rate = {"8517.13": 0.20}.get(str(s.results["hs_code"]), 0.10)
    s.results["duty_usd"] = round(float(s.request["value_usd"]) * rate, 2)  # type: ignore[arg-type]


async def compliance_agent(s: Shared) -> None:
    """Worker 3: flags restricted codes."""
    s.results["needs_license"] = s.results["hs_code"] == "9999.99"


AGENTS: dict[str, Callable[[Shared], Awaitable[None]]] = {
    "classifier": classifier_agent, "duty": duty_agent, "compliance": compliance_agent,
}
PREREQ = {"classifier": set(), "duty": {"hs_code"}, "compliance": {"hs_code"}}


async def supervisor(request: dict[str, object], max_rounds: int = 5) -> Shared:
    """Pick every agent whose prerequisites are satisfied; run ready agents in parallel."""
    s = Shared(request)
    done: set[str] = set()
    for _ in range(max_rounds):
        ready = [n for n in AGENTS if n not in done and PREREQ[n] <= set(s.results)]
        if not ready:
            break
        s.log.append(f"round: {ready}")
        outcomes = await asyncio.gather(*(AGENTS[n](s) for n in ready), return_exceptions=True)
        for name, out in zip(ready, outcomes):
            if isinstance(out, Exception):  # one failing worker must not kill the system
                s.log.append(f"{name} failed: {out!r}")
            done.add(name)
    return s


if __name__ == "__main__":
    out = asyncio.run(supervisor({"product": "Smartphone X", "value_usd": 1000}))
    print(out.results)
    print(out.log)
