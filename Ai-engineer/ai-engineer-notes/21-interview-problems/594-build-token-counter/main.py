"""Token counter: exact via tiktoken if installed, else a heuristic fallback.

Offline. The fallback is an ESTIMATE only; Devanagari is counted heavier.
"""
from __future__ import annotations

import asyncio
import re

try:  # tiktoken is optional
    import tiktoken
    _ENC = tiktoken.get_encoding("o200k_base")  # may need network on first use
except Exception:  # ImportError or download failure
    _ENC = None

_DEVANAGARI = re.compile(r"[ऀ-ॿ]")


def count_text(text: str) -> int:
    """Count tokens in text (exact if tiktoken works, else estimate)."""
    if _ENC is not None:
        return len(_ENC.encode(text))
    hindi = len(_DEVANAGARI.findall(text))  # ~1 token per 1.5 Devanagari chars
    other = len(text) - hindi  # ~1 token per 4 other chars
    return max(1, round(hindi / 1.5 + other / 4)) if text else 0


def count_messages(messages: list[dict[str, str]]) -> int:
    """Chat messages: text tokens + small per-message overhead (approximate)."""
    total = 3  # reply priming (approximate; varies by model)
    for m in messages:
        if "content" not in m or "role" not in m:
            raise ValueError("message needs role and content")
        total += 4 + count_text(m["role"]) + count_text(m["content"])
    return total


def truncate_to_tokens(text: str, max_tokens: int) -> str:
    """Cut text so it fits max_tokens."""
    if max_tokens < 0:
        raise ValueError("max_tokens must be >= 0")
    if _ENC is not None:
        return _ENC.decode(_ENC.encode(text)[:max_tokens])
    # Fallback: shrink by characters until the estimate fits
    while text and count_text(text) > max_tokens:
        text = text[: int(len(text) * 0.9)]
    return text


def fits_context(messages: list[dict[str, str]], window: int,
                 reserve_output: int = 1000) -> bool:
    return count_messages(messages) + reserve_output <= window


async def acount(text: str) -> int:
    """Async wrapper: keep CPU-bound counting off the event loop."""
    return await asyncio.to_thread(count_text, text)


if __name__ == "__main__":
    msgs = [{"role": "system", "content": "You classify tariffs."},
            {"role": "user", "content": "HS code for iPhone 15?"}]
    print("engine:", "tiktoken" if _ENC else "heuristic")
    print("messages:", count_messages(msgs))
    print("hindi vs english:", count_text("टैरिफ वर्गीकरण"), count_text("tariff classification"))
    print("fits 128k:", fits_context(msgs, 128_000))
    print("truncated:", repr(truncate_to_tokens("word " * 100, 5)))
    print("async:", asyncio.run(acount("hello world")))
