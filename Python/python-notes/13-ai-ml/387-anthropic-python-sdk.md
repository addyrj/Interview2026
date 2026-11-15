---

# 387. Anthropic Python SDK
# हिंदी में: Anthropic Python SDK (Python से Claude को call करना)

---

## 🔵 Simple Definition (English)
The `anthropic` package is the official Python SDK for the Claude API. You create a client, call `client.messages.create(...)` with a model, `max_tokens` and a list of messages, and get back a typed response object. It also handles streaming, tool use, retries and typed errors.

## 🔵 सरल परिभाषा (Hindi)
`anthropic` package Claude API का official Python SDK है। आप एक client बनाते हैं, model, `max_tokens` और messages की list के साथ `client.messages.create(...)` call करते हैं, और typed response object मिलता है। यह streaming, tool use, retries और typed errors भी संभालता है।

---

## 🔴 Problem it Solves
Calling an LLM over raw HTTP means hand-writing headers, JSON, retries on 429/5xx, SSE parsing for streaming, and error classes. The SDK does all this, validates your arguments, and gives autocomplete through type hints, so you focus on your product instead of plumbing.

## 🔴 यह क्यों बना? (Hindi)
Raw HTTP से LLM call करने का मतलब है headers, JSON, 429/5xx पर retries, streaming के लिए SSE parsing और error classes खुद लिखना। SDK यह सब करता है, arguments validate करता है और type hints से autocomplete देता है, ताकि आप plumbing की जगह अपने product पर ध्यान दें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install anthropic ; set ANTHROPIC_API_KEY (never hardcode the key)
Step 2 → client = anthropic.Anthropic()   (reads the key from the environment)
Step 3 → client.messages.create(model=..., max_tokens=..., messages=[{"role":"user","content":"..."}])
Step 4 → Optional: system="..." (top-level, NOT a message), tools=[...], thinking, etc.
Step 5 → Response: response.content is a LIST of blocks (text, tool_use, thinking...)
         check block.type before reading block.text; check response.stop_reason
Step 6 → Streaming: with client.messages.stream(...) as s: for t in s.text_stream
Step 7 → Errors: RateLimitError, APIConnectionError, APIStatusError... (auto-retry x2 by default)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → pip install anthropic ; ANTHROPIC_API_KEY set करें (key कभी hardcode न करें)
Step 2 → client = anthropic.Anthropic()   (key environment से पढ़ता है)
Step 3 → client.messages.create(model=..., max_tokens=..., messages=[{"role":"user","content":"..."}])
Step 4 → Optional: system="..." (top-level, message नहीं), tools=[...], thinking आदि
Step 5 → Response: response.content blocks की LIST है (text, tool_use, thinking...)
         block.text पढ़ने से पहले block.type जांचें; response.stop_reason भी देखें
Step 6 → Streaming: with client.messages.stream(...) as s: for t in s.text_stream
Step 7 → Errors: RateLimitError, APIConnectionError, APIStatusError... (default में 2 बार auto-retry)
```

---

## 🟡 Real World Example
A support chatbot for an e-commerce app: the system prompt sets the tone, the user's message goes in `messages`, and Claude can call a `get_order_status` tool backed by your database. The answer is streamed to the browser so text appears word by word. A summarizer job processes thousands of reviews overnight. A FastAPI `/ask` endpoint wraps the SDK.

## 🟡 Real Example Hindi mein
E-commerce app का support chatbot: system prompt tone तय करता है, user का message `messages` में जाता है, और Claude आपके database वाले `get_order_status` tool को call कर सकता है। जवाब browser में streaming से शब्द-दर-शब्द दिखता है। Summarizer job रात भर हजारों reviews process करती है। FastAPI `/ask` endpoint SDK को wrap करता है।

---

## 💻 Code Example — Basic
```python
# Basic Anthropic SDK usage. A mock HTTP transport is used so this runs offline with no API key.
# With a real key, just write: client = anthropic.Anthropic()  (reads ANTHROPIC_API_KEY)
import json                                           # build fake JSON responses
import httpx2 as httpx                                # anthropic 1.x+ uses httpx2 (not httpx)
import anthropic                                      # the SDK


def msg(text: str) -> dict:                           # helper: a fake API response
    return {"id": "msg_01", "type": "message", "role": "assistant", "model": "claude-opus-5-5",
            "content": [{"type": "text", "text": text}], "stop_reason": "end_turn",
            "stop_sequence": None, "usage": {"input_tokens": 12, "output_tokens": 7}}


def handler(request: httpx.Request) -> httpx.Response:   # fake server
    body: dict = json.loads(request.content)          # what the SDK sent
    if body.get("stream"):                            # streaming request -> Server-Sent Events
        events = [                                    # the real wire format
            ("message_start", {"type": "message_start", "message": {**msg(""), "content": [], "stop_reason": None}}),
            ("content_block_start", {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}),
            ("content_block_delta", {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Hel"}}),
            ("content_block_delta", {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "lo!"}}),
            ("content_block_stop", {"type": "content_block_stop", "index": 0}),
            ("message_delta", {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": None}, "usage": {"output_tokens": 3}}),
            ("message_stop", {"type": "message_stop"}),
        ]
        sse: str = "".join(f"event: {e}\ndata: {json.dumps(d)}\n\n" for e, d in events)   # SSE text
        return httpx.Response(200, content=sse.encode(), headers={"content-type": "text/event-stream"})
    return httpx.Response(200, json=msg("Namaste!"))  # normal reply


client: anthropic.Anthropic = anthropic.Anthropic(    # build the client
    api_key="test-key", max_retries=0,                # fake key, no retries for the demo
    http_client=anthropic.DefaultHttpxClient(transport=httpx.MockTransport(handler)),   # plug the fake server
)
r = client.messages.create(                           # one normal request
    model="claude-opus-5-5", max_tokens=1024,         # max_tokens is REQUIRED
    messages=[{"role": "user", "content": "hi"}],     # conversation so far
)
print(r.content[0].text, r.stop_reason, r.usage.input_tokens, r.usage.output_tokens)   # text, why it stopped, tokens
with client.messages.stream(model="claude-opus-5-5", max_tokens=1024,       # streaming helper
                            messages=[{"role": "user", "content": "hi"}]) as s:
    print([t for t in s.text_stream])                 # text arrives in pieces
    print(s.get_final_message().content[0].text)      # full message after the stream

# Output:
# Namaste! end_turn 12 7
# ['Hel', 'lo!']
# Hello!
```

## 💻 Code Example — Advanced
```python
# Production style: tool-use loop with typed error handling (mock transport = runs offline)
from __future__ import annotations                    # modern hints
import json                                           # tool results are JSON strings
from typing import Any                                # loose typing for dict payloads
import anthropic                                      # SDK
import httpx2 as httpx                                # transport for the offline fake

MODEL: str = "claude-opus-5-5"                        # exact model id, no date suffix
TOOLS: list[dict[str, Any]] = [{                      # tool schema the model can call
    "name": "get_weather", "description": "Get current temperature for a city",
    "input_schema": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
}]


def get_weather(city: str) -> str:                    # our real function (fake data here)
    return json.dumps({"city": city, "temp_c": 31})   # tool results are strings


class Assistant:
    """Small chat assistant that can call tools."""

    def __init__(self, client: anthropic.Anthropic) -> None:
        self.client = client                          # injected client (easy to test)

    def ask(self, question: str, max_turns: int = 5) -> str:
        messages: list[dict[str, Any]] = [{"role": "user", "content": question}]   # history
        for _ in range(max_turns):                    # cap the loop: never loop forever
            try:                                      # typed error handling, most specific first
                resp = self.client.messages.create(model=MODEL, max_tokens=1024, tools=TOOLS, messages=messages)
            except anthropic.RateLimitError as e:     # 429
                return f"busy, retry after {e.response.headers.get('retry-after', '60')}s"
            except anthropic.APIConnectionError:      # network down
                return "network error"
            except anthropic.APIStatusError as e:     # any other 4xx/5xx
                return f"api error {e.status_code}"
            if resp.stop_reason == "refusal":         # model declined: handle explicitly
                return "request declined"
            if resp.stop_reason != "tool_use":        # final answer reached
                return "".join(b.text for b in resp.content if b.type == "text")   # join text blocks
            messages.append({"role": "assistant", "content": resp.content})   # keep the tool_use turn
            results = [{"type": "tool_result", "tool_use_id": b.id, "content": get_weather(**b.input)}
                       for b in resp.content if b.type == "tool_use"]         # run each requested tool
            messages.append({"role": "user", "content": results})             # return ALL results in one message
        return "too many turns"                       # safety exit


def fake(request: httpx.Request) -> httpx.Response:   # fake Claude API for the demo
    body = json.loads(request.content)                # request the SDK sent
    base = {"id": "m", "type": "message", "role": "assistant", "model": MODEL, "stop_sequence": None,
            "usage": {"input_tokens": 1, "output_tokens": 1}}
    q = body["messages"][0]["content"]                # first user text
    if q == "limit":                                  # simulate rate limit
        return httpx.Response(429, headers={"retry-after": "7"}, json={"type": "error", "error": {"type": "rate_limit_error", "message": "x"}})
    if q == "boom":                                   # simulate server error
        return httpx.Response(500, json={"type": "error", "error": {"type": "api_error", "message": "x"}})
    if isinstance(body["messages"][-1]["content"], list):   # last turn holds tool results -> final answer
        return httpx.Response(200, json={**base, "stop_reason": "end_turn", "content": [{"type": "text", "text": "31C in Delhi"}]})
    return httpx.Response(200, json={**base, "stop_reason": "tool_use", "content": [{"type": "tool_use", "id": "tu_1", "name": "get_weather", "input": {"city": "Delhi"}}]})


client = anthropic.Anthropic(api_key="test", max_retries=0, http_client=anthropic.DefaultHttpxClient(transport=httpx.MockTransport(fake)))
bot: Assistant = Assistant(client)                    # build the assistant
print(bot.ask("weather in Delhi?"))                   # tool loop: tool_use -> result -> answer
print(bot.ask("limit"))                               # 429 path
print(bot.ask("boom"))                                # 500 path

# Output:
# 31C in Delhi
# busy, retry after 7s
# api error 500
```
Note: model names and defaults change over time. Check the current model list in Anthropic's docs. Version-dependent: this was run with `anthropic` 2.8.0 on Python 3.13; the package uses `httpx2` for its HTTP layer in recent releases (older releases used `httpx`).

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript / TypeScript |
|---------|--------|------------------------|
| Package | `anthropic` | `@anthropic-ai/sdk` |
| Client | `anthropic.Anthropic()` | `new Anthropic()` |
| Call | `client.messages.create(...)` | `await client.messages.create(...)` |
| Stream | `client.messages.stream(...)` | `client.messages.stream(...)` |
| Errors | `anthropic.RateLimitError` | `Anthropic.RateLimitError` |
| Async | `AsyncAnthropic` + `await` | all calls are promises |

```python
# Python way
import anthropic                                           # SDK
client = anthropic.Anthropic()                             # key from ANTHROPIC_API_KEY
r = client.messages.create(model="claude-opus-5-5", max_tokens=1024,
                           messages=[{"role": "user", "content": "Hi"}])   # blocking call
print(r.content[0].text)                                   # first text block
```
```javascript
// JavaScript way
import Anthropic from "@anthropic-ai/sdk";                 // SDK
const client = new Anthropic();                            // key from env
const r = await client.messages.create({                   // promise-based
  model: "claude-opus-5-5", max_tokens: 1024,
  messages: [{ role: "user", content: "Hi" }],
});
console.log(r.content[0].text);                            // first text block
```

Key difference: the API shape is the same. Python uses keyword arguments and a sync client by default (use `AsyncAnthropic` for async code), JavaScript is always async. In both, `max_tokens` is required and `system` is a top-level field, not a message.

---

## 🟠 FastAPI Connection
Create ONE client at startup and reuse it (it pools connections). Use `AsyncAnthropic` with `async def` endpoints so a slow LLM call does not block the event loop, or a sync client with a plain `def` endpoint (runs in the thread pool). Stream with `StreamingResponse`. Map SDK errors to HTTP codes (429 -> 429, connection -> 503). Verified below with the offline fake and TestClient.

```python
# FastAPI example — POST /ask (verified: {'answer': '31C in Delhi'})
from fastapi import FastAPI                                # FastAPI
from pydantic import BaseModel                             # request body

app: FastAPI = FastAPI()                                   # create app
# bot = Assistant(anthropic.Anthropic())                   # one shared client; use the class from above


class Q(BaseModel):                                        # request schema
    question: str                                          # user question


@app.post("/ask")                                          # POST /ask
def ask(q: Q) -> dict[str, str]:                           # sync def -> thread pool, fine for a blocking SDK
    return {"answer": bot.ask(q.question)}                 # tool loop + error handling inside
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Hardcoding the API key in source code
✅ Correct: environment variable (or secret manager)

```python
import anthropic
# Wrong
# client = anthropic.Anthropic(api_key="sk-ant-...")   # ends up in git history
# Right
client = anthropic.Anthropic()                         # reads ANTHROPIC_API_KEY (or a login profile)
```

❌ Mistake 2: Putting the system prompt inside `messages`
✅ Correct: use the top-level `system=` argument

```python
# Wrong: messages=[{"role": "system", "content": "Be brief"}, ...]   # not how the Messages API works
# Right
# client.messages.create(model=..., max_tokens=512, system="Be brief",
#                        messages=[{"role": "user", "content": "Hi"}])
```

❌ Mistake 3: Assuming `response.content[0]` is text
✅ Correct: loop over blocks and check `type` (thinking and tool_use blocks may come first)

```python
# Wrong: text = response.content[0].text        # AttributeError if it is a tool_use or thinking block
# Right
# text = "".join(b.text for b in response.content if b.type == "text")
```

❌ Mistake 4: Forgetting `max_tokens`, or setting it too low
✅ Correct: it is required; too low truncates (`stop_reason == "max_tokens"`)

```python
# Wrong: client.messages.create(model=..., messages=[...])   # TypeError: missing max_tokens
# Right: set a realistic value (e.g. 1024 for chat, much higher for long outputs, with streaming)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output? (no network needed)
import anthropic
c = anthropic.Anthropic(api_key="k")
print(c.max_retries, c.timeout.read)
```
Answer: `2 600`. By default the SDK retries failed requests twice (connection errors, 408, 409, 429 and 5xx) with exponential backoff, and the default timeout is 10 minutes (600 seconds). So with timeouts and retries a single slow call can take up to about 3 x 600 seconds. In production set a shorter `timeout=` and decide `max_retries=` on purpose.

---

## ⚫ Interview Questions + Answers

Q1: How is conversation memory handled?
A1: The API is stateless. You resend the full `messages` list (user and assistant turns) on every call. You can reduce cost with prompt caching and long-context tools such as compaction.

Q2: How do you stream a response?
A2: `with client.messages.stream(...) as s: for text in s.text_stream`. Use `s.get_final_message()` to get the complete message. For long outputs, streaming is recommended to avoid HTTP timeouts.

Q3: How does tool use work?
A3: You send tool schemas. If Claude decides to call one, the response has `stop_reason == "tool_use"` and `tool_use` blocks with `id`, `name`, `input`. You run the function, then send a user message with `tool_result` blocks (matching `tool_use_id`), and loop until the stop reason is not `tool_use`.

Q4: Which errors should you handle?
A4: `RateLimitError` (429, honor `retry-after`), `APIConnectionError`, `APITimeoutError`, `AuthenticationError` (401), `BadRequestError` (400), and the general `APIStatusError`. Catch the specific ones first. Also check `stop_reason` for `refusal` and `max_tokens`.

Q5: Sync vs async client?
A5: `Anthropic` blocks the thread; `AsyncAnthropic` is for `async def` code (FastAPI, many concurrent calls). Never call the blocking client inside `async def` endpoints.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chatbots, summarization, extraction, classification, code help
- Agents that call your tools
- You want typed responses, retries and streaming for free

❌ Avoid when:
- A regex or simple rule solves it: no need for an LLM
- Strict low-latency (<50 ms) paths: LLM calls take seconds
- Sensitive data you may not send to a third party: check your policy first

---

## 📊 Visual Diagram
```
 your code                SDK                         Claude API
 ─────────                ───                         ──────────
 messages.create() ─────> build JSON + headers ─────> POST /v1/messages
                          retry 429/5xx (x2)  <─────  response / SSE stream
 response.content  <───── parse into typed objects
      │
      ├─ text block       -> show to user
      └─ tool_use block   -> run function -> tool_result -> call again (loop)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| messages | Conversation turns (user/assistant) | बातचीत के turns |
| system | Top-level instructions for the model | Model के लिए top-level निर्देश |
| max_tokens | Upper limit on output length (required) | Output की अधिकतम लंबाई |
| stop_reason | Why generation ended | Generation क्यों रुका |
| tool_use | Model asks you to run a function | Model का function चलाने का अनुरोध |
| Streaming | Receive text in pieces | टुकड़ों में text पाना |

---

## ⚡ 3-Line Summary
English: `anthropic.Anthropic().messages.create(model, max_tokens, messages)` is the core call. Handle content as a list of blocks, stream long answers, run a tool loop on `stop_reason == "tool_use"`, and catch typed errors. Keep the key in the environment and reuse one client.
Hindi: `anthropic.Anthropic().messages.create(model, max_tokens, messages)` मुख्य call है। Content को blocks की list की तरह संभालें, लंबे जवाब stream करें, `stop_reason == "tool_use"` पर tool loop चलाएं और typed errors पकड़ें। Key environment में रखें और एक ही client बार-बार इस्तेमाल करें।

---

## ➡️ Next Topic
**388. LangChain in Python** — chains, prompts, output parsers and tools that connect LLMs to your data.
