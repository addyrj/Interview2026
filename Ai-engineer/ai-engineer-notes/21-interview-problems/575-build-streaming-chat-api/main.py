"""575. Streaming chat API with Server-Sent Events (SSE).

Run offline demo:  python main.py
Run server:        uvicorn main:app --reload     (pip install fastapi uvicorn)
Test:              curl -N -X POST localhost:8000/chat/stream -H 'content-type: application/json' \
                        -d '{"message":"HS code for a phone?"}'
Mock token stream is used without OPENAI_API_KEY.
"""
from __future__ import annotations

import asyncio  # async generators
import json  # SSE payloads
import os  # env
from typing import AsyncIterator  # types

SYSTEM_PROMPT = "You are a concise tariff assistant."  # system message
FIRST_TOKEN_TIMEOUT = 15.0  # fail fast if model never starts
IDLE_TIMEOUT = 30.0  # max silence between tokens


async def mock_stream(message: str) -> AsyncIterator[str]:
    """Yield words one by one like a real model would."""
    for word in f"Smartphones are classified under HS 8517 for: {message}".split():
        await asyncio.sleep(0.02)  # simulate latency
        yield word + " "  # one token-ish chunk


async def openai_stream(message: str) -> AsyncIterator[str]:
    from openai import AsyncOpenAI  # lazy import

    client = AsyncOpenAI()  # key from env
    stream = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": message}],
        stream=True,  # ask for chunks
        max_tokens=300,
    )
    async for part in stream:  # iterate chunks
        if part.choices and part.choices[0].delta.content:
            yield part.choices[0].delta.content  # text piece


def token_source(message: str) -> AsyncIterator[str]:
    return openai_stream(message) if os.getenv("OPENAI_API_KEY") else mock_stream(message)


def sse(event: str, data: object) -> str:
    """Format one SSE frame: event + JSON data + blank line."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def sse_events(message: str, is_disconnected=None) -> AsyncIterator[str]:  # type: ignore[no-untyped-def]
    """Wrap the token stream in SSE frames, with timeouts and error events."""
    count = 0  # chunks sent
    source = token_source(message).__aiter__()  # manual iteration for timeouts
    try:
        while True:
            if is_disconnected is not None and await is_disconnected():
                break  # client left: stop paying for tokens
            timeout = FIRST_TOKEN_TIMEOUT if count == 0 else IDLE_TIMEOUT
            try:
                piece = await asyncio.wait_for(source.__anext__(), timeout=timeout)
            except StopAsyncIteration:
                yield sse("done", {"chunks": count})  # normal end
                break
            except asyncio.TimeoutError:
                yield sse("error", {"detail": "model timeout"})  # tell client
                break
            count += 1
            yield sse("token", {"text": piece})  # send chunk
    except Exception as exc:  # provider error mid-stream (headers already sent)
        yield sse("error", {"detail": type(exc).__name__})  # in-band error
    finally:
        aclose = getattr(source, "aclose", None)  # release upstream connection
        if aclose:
            await aclose()


def create_app():  # type: ignore[no-untyped-def]
    from fastapi import FastAPI, Request
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel, Field

    class ChatIn(BaseModel):
        message: str = Field(min_length=1, max_length=4000)  # validated input

    app = FastAPI(title="Streaming Chat")

    @app.post("/chat/stream")
    async def chat_stream(body: ChatIn, request: Request) -> StreamingResponse:
        return StreamingResponse(
            sse_events(body.message, request.is_disconnected),  # generator
            media_type="text/event-stream",  # SSE content type
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},  # stop Nginx buffering
        )

    return app


try:
    app = create_app()
except ImportError:
    app = None


async def demo() -> None:
    async for frame in sse_events("a phone"):
        print(frame.strip().replace("\n", " | "))  # show frames


if __name__ == "__main__":
    asyncio.run(demo())
