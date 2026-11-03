"""571. Basic LLM chat API with FastAPI.

Run offline demo:   python main.py
Run server:         uvicorn main:app --reload   (needs: pip install fastapi uvicorn)
Set OPENAI_API_KEY to use a real model; without it a mock LLM answers.
"""
from __future__ import annotations

import asyncio  # async runtime for the demo
import os  # read env vars
import uuid  # session ids
from typing import Literal, Protocol  # type hints

Role = Literal["system", "user", "assistant"]  # allowed message roles
Message = dict[str, str]  # {"role": ..., "content": ...}

SYSTEM_PROMPT = "You are a concise tariff classification assistant."  # behaviour
MAX_HISTORY = 10  # keep only the last N messages (cost control)
MAX_INPUT_CHARS = 4000  # reject huge inputs early


class LLM(Protocol):
    """Anything that can turn messages into a reply."""

    async def complete(self, messages: list[Message]) -> tuple[str, int, int]:
        """Return (text, input_tokens, output_tokens)."""
        ...


class MockLLM:
    """Offline model so the demo and tests need no API key."""

    async def complete(self, messages: list[Message]) -> tuple[str, int, int]:
        last = messages[-1]["content"]  # latest user text
        reply = f"[mock] You asked: {last[:60]}"  # canned answer
        tin = sum(len(m["content"]) for m in messages) // 4  # rough token estimate
        return reply, tin, len(reply) // 4  # (text, in, out)


class OpenAILLM:
    """Real model via the official openai SDK (pip install openai)."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        from openai import AsyncOpenAI  # imported lazily so mock mode needs no SDK

        self.client = AsyncOpenAI()  # reads OPENAI_API_KEY from env
        self.model = model  # model id

    async def complete(self, messages: list[Message]) -> tuple[str, int, int]:
        resp = await self.client.chat.completions.create(
            model=self.model, messages=messages, max_tokens=300, temperature=0.2
        )  # one chat completion call
        text = resp.choices[0].message.content or ""  # may be None
        usage = resp.usage  # token usage (may be None in odd cases)
        return text, (usage.prompt_tokens if usage else 0), (usage.completion_tokens if usage else 0)


def make_llm() -> LLM:
    """Pick the real model when a key exists, otherwise the mock."""
    return OpenAILLM() if os.getenv("OPENAI_API_KEY") else MockLLM()


class ChatService:
    """Holds per-session history in memory (use Redis in production)."""

    def __init__(self, llm: LLM) -> None:
        self.llm = llm  # injected model
        self.sessions: dict[str, list[Message]] = {}  # session_id -> history

    async def chat(self, session_id: str | None, text: str) -> dict[str, object]:
        if not text.strip():
            raise ValueError("message is empty")  # validate input
        if len(text) > MAX_INPUT_CHARS:
            raise ValueError("message too long")  # protect cost
        sid = session_id or uuid.uuid4().hex  # new session if none given
        history = self.sessions.setdefault(sid, [])  # fetch or create
        history.append({"role": "user", "content": text})  # add user turn
        window = history[-MAX_HISTORY:]  # trim old turns
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, *window]  # build prompt
        try:
            reply, tin, tout = await asyncio.wait_for(self.llm.complete(messages), timeout=30)
        except asyncio.TimeoutError as exc:
            history.pop()  # drop the unanswered turn
            raise RuntimeError("model timed out") from exc
        history.append({"role": "assistant", "content": reply})  # remember answer
        return {"session_id": sid, "reply": reply, "tokens_in": tin, "tokens_out": tout}


def create_app() -> object:
    """Build the FastAPI app (only if fastapi is installed)."""
    from fastapi import FastAPI, HTTPException  # lazy import
    from pydantic import BaseModel, Field

    class ChatIn(BaseModel):
        session_id: str | None = None  # optional existing session
        message: str = Field(min_length=1, max_length=MAX_INPUT_CHARS)  # user text

    app = FastAPI(title="Basic LLM Chat")  # app instance
    service = ChatService(make_llm())  # one service per process

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}  # liveness

    @app.post("/chat")
    async def chat(body: ChatIn) -> dict[str, object]:
        try:
            return await service.chat(body.session_id, body.message)  # delegate
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc  # bad input
        except RuntimeError as exc:
            raise HTTPException(status_code=504, detail=str(exc)) from exc  # upstream timeout

    return app


try:
    app = create_app()  # module-level `app` for uvicorn
except ImportError:  # fastapi not installed: demo still works
    app = None


async def demo() -> None:
    service = ChatService(MockLLM())  # offline service
    first = await service.chat(None, "HS code for a smartphone?")  # new session
    print(first)  # show response
    second = await service.chat(str(first["session_id"]), "And for a laptop?")  # same session
    print(second["reply"], "| history size:", len(service.sessions[str(first["session_id"])]))
    try:
        await service.chat(None, "   ")  # invalid input
    except ValueError as exc:
        print("rejected:", exc)  # error handling demo


if __name__ == "__main__":
    asyncio.run(demo())  # run the offline demo
