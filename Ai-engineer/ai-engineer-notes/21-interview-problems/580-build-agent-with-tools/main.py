"""Tool-calling agent loop: LLM picks a tool (JSON), we validate + run it, feed result back.

Offline: `mock_llm` is a scripted policy standing in for a real function-calling model.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any, Callable

TARIFF_DB = {"smartphone": ("8517.13", 0.20), "laptop": ("8471.30", 0.0), "tshirt": ("6109.10", 0.12)}


def lookup_hs_code(product: str) -> dict[str, Any]:
    """Tool 1: find the HS code for a product."""
    if product not in TARIFF_DB:
        raise KeyError(f"unknown product {product!r}")
    return {"product": product, "hs_code": TARIFF_DB[product][0]}


def calc_duty(product: str, value_usd: float) -> dict[str, Any]:
    """Tool 2: compute duty = value * rate."""
    if value_usd < 0:
        raise ValueError("value must be >= 0")
    rate = TARIFF_DB[product][1]
    return {"duty_usd": round(value_usd * rate, 2), "rate": rate}


TOOLS: dict[str, Callable[..., dict[str, Any]]] = {"lookup_hs_code": lookup_hs_code, "calc_duty": calc_duty}


def mock_llm(messages: list[dict[str, Any]]) -> dict[str, Any]:
    """Scripted policy: call tool 1, then tool 2, then answer. Returns tool call or final text."""
    tool_msgs = [m for m in messages if m["role"] == "tool"]
    if len(tool_msgs) == 0:
        return {"tool": "lookup_hs_code", "args": {"product": "smartphone"}}
    if len(tool_msgs) == 1:
        return {"tool": "calc_duty", "args": {"product": "smartphone", "value_usd": 1000}}
    hs, duty = json.loads(tool_msgs[0]["content"]), json.loads(tool_msgs[1]["content"])
    return {"final": f"HS {hs['hs_code']}, duty ${duty['duty_usd']}"}


def run_tool(name: str, args: dict[str, Any]) -> str:
    """Validate the call and run it; errors become observations so the model can recover."""
    if name not in TOOLS:
        return json.dumps({"error": f"no such tool {name}"})
    try:
        return json.dumps(TOOLS[name](**args))
    except (KeyError, ValueError, TypeError) as exc:
        return json.dumps({"error": str(exc)})


def run_agent(question: str, max_steps: int = 5) -> str:
    """The agent loop with a hard step cap (prevents infinite tool loops)."""
    messages: list[dict[str, Any]] = [{"role": "user", "content": question}]
    for _ in range(max_steps):
        decision = mock_llm(messages)
        if "final" in decision:
            return decision["final"]
        result = run_tool(decision["tool"], decision["args"])
        messages.append({"role": "tool", "content": result})
    return "stopped: max_steps reached"


async def arun_agent(question: str) -> str:
    """Async wrapper so FastAPI does not block."""
    return await asyncio.to_thread(run_agent, question)


if __name__ == "__main__":
    print(asyncio.run(arun_agent("Duty on a $1000 smartphone?")))
    print(run_tool("calc_duty", {"product": "laptop", "value_usd": -5}))  # error becomes data
    print(run_tool("delete_db", {}))
