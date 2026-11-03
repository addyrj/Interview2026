"""Multi-turn chatbot with session memory, token-budget trimming and rolling summary.

The LLM is mocked so this runs offline. Swap `mock_llm` for a real client call.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

Message = dict[str, str]


def count_tokens(text: str) -> int:
    """Rough estimate: ~4 characters per token (illustrative, use tiktoken in prod)."""
    return max(1, len(text) // 4)


async def mock_llm(messages: list[Message]) -> str:
    """Pretend LLM: echoes what it can see so we can prove memory works."""
    await asyncio.sleep(0)  # yield to the event loop like a real network call
    last_user = next(m["content"] for m in reversed(messages) if m["role"] == "user")
    seen = sum(1 for m in messages if m["role"] == "user")
    return f"[sees {seen} user turns] You said: {last_user}"


@dataclass
class Session:
    """One user's conversation state."""

    system: str = "You are a tariff assistant."
    history: list[Message] = field(default_factory=list)
    summary: str = ""

    def build_prompt(self, budget: int) -> list[Message]:
        """System + summary + newest turns that fit inside the token budget."""
        head: list[Message] = [{"role": "system", "content": self.system}]
        if self.summary:
            head.append({"role": "system", "content": f"Summary so far: {self.summary}"})
        used = sum(count_tokens(m["content"]) for m in head)
        kept: list[Message] = []
        for msg in reversed(self.history):  # newest first
            cost = count_tokens(msg["content"])
            if used + cost > budget:
                break
            kept.append(msg)
            used += cost
        return head + list(reversed(kept))

    def compact(self, keep_last: int = 4) -> None:
        """Fold old turns into a summary (here: naive join; in prod ask a cheap LLM)."""
        if len(self.history) <= keep_last:
            return
        old, self.history = self.history[:-keep_last], self.history[-keep_last:]
        self.summary = (self.summary + " " + " | ".join(m["content"][:30] for m in old)).strip()


class Chatbot:
    """Holds many sessions keyed by session_id."""

    def __init__(self, budget: int = 200) -> None:
        self.sessions: dict[str, Session] = {}
        self.budget = budget

    async def chat(self, session_id: str, text: str) -> str:
        """Add the user turn, call the LLM, store the reply. Errors do not corrupt history."""
        if not text.strip():
            raise ValueError("empty message")
        s = self.sessions.setdefault(session_id, Session())
        s.history.append({"role": "user", "content": text})
        try:
            reply = await mock_llm(s.build_prompt(self.budget))
        except Exception:
            s.history.pop()  # roll back so a retry does not duplicate the turn
            raise
        s.history.append({"role": "assistant", "content": reply})
        s.compact()
        return reply


async def main() -> None:
    bot = Chatbot()
    for text in ["HS code for laptop?", "And for its charger?", "What was my first question?"]:
        print(await bot.chat("u1", text))
    print("other user isolated:", await bot.chat("u2", "hi"))


if __name__ == "__main__":
    asyncio.run(main())
