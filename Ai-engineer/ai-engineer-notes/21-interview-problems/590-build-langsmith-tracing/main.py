"""Tracing: a tiny span tracer (decorator + context) showing what LangSmith captures.

Offline and stdlib-only. If `langsmith` is installed AND LANGSMITH_API_KEY is set, the same
functions could simply be decorated with `langsmith.traceable` (shown in notes.md).
"""
from __future__ import annotations

import asyncio
import functools
import time
import uuid
from contextvars import ContextVar
from typing import Any, Awaitable, Callable

_current: ContextVar[str | None] = ContextVar("current_span", default=None)
SPANS: list[dict[str, Any]] = []


def trace(name: str, run_type: str = "chain") -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """Decorator for async functions: records parent/child, latency, io, errors."""
    def deco(fn: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            span = {"id": uuid.uuid4().hex[:6], "parent": _current.get(), "name": name,
                    "type": run_type, "inputs": args, "error": None}
            token = _current.set(span["id"])  # children will see us as parent
            start = time.perf_counter()
            try:
                out = await fn(*args, **kwargs)
                span["outputs"] = out
                return out
            except Exception as exc:
                span["error"] = repr(exc)
                raise
            finally:
                span["ms"] = round((time.perf_counter() - start) * 1000, 1)
                _current.reset(token)
                SPANS.append(span)
        return wrapper
    return deco


@trace("retrieve", "retriever")
async def retrieve(q: str) -> list[str]:
    await asyncio.sleep(0.01)
    return ["8517.13 smartphones"]


@trace("llm", "llm")
async def llm(prompt: str) -> str:
    await asyncio.sleep(0.02)
    return "HS 8517.13"


@trace("classify_pipeline")
async def pipeline(q: str) -> str:
    docs = await retrieve(q)
    return await llm(f"{docs} | {q}")


def print_tree(parent: str | None = None, depth: int = 0) -> None:
    """Render spans as a tree (what the LangSmith UI shows)."""
    for s in sorted((s for s in SPANS if s["parent"] == parent), key=lambda s: s["ms"], reverse=True):
        print("  " * depth + f"{s['name']} [{s['type']}] {s['ms']}ms err={s['error']}")
        print_tree(s["id"], depth + 1)


if __name__ == "__main__":
    asyncio.run(pipeline("smartphone HS code?"))
    print_tree()
