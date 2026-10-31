---

# 038. Claude — Streaming
# हिंदी में: Claude — Streaming

---

## 🔵 Simple Definition (English)
Claude streaming sends the reply as a series of Server-Sent Events while the model is still generating. The Python SDK gives a helper, `client.messages.stream(...)`, with a `text_stream` iterator for text and `get_final_message()` for the complete message with usage. You can also pass `stream=True` to `messages.create` to get raw events.

## 🔵 सरल परिभाषा (Hindi)
Claude streaming में model के generate करते समय ही reply Server-Sent Events की series के रूप में आता है। Python SDK helper देता है, `client.messages.stream(...)`, जिसमें text के लिए `text_stream` iterator और usage सहित पूरे message के लिए `get_final_message()` है। Raw events के लिए `messages.create` में `stream=True` भी दे सकते हैं।

---

## 🔴 Problem it Solves
Long answers take many seconds, and users think the app is frozen. Also, very long outputs with non-streaming requests can hit HTTP timeouts (the SDK may even refuse non-streaming requests with very large `max_tokens`). Streaming gives fast time-to-first-token and keeps the connection healthy for long generations.

## 🔴 यह क्यों बना? (Hindi)
लंबे जवाब में कई seconds लगते हैं और user को लगता है app अटक गया। साथ ही non-streaming requests में बहुत लंबे outputs HTTP timeout पर अटक सकते हैं (बहुत बड़े `max_tokens` पर SDK non-streaming request मना भी कर सकता है)। Streaming से पहला token जल्दी दिखता है और लंबी generation में connection ठीक रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Open the stream: with client.messages.stream(...) as stream:
Step 2 → Server sends event: message_start (message id, input usage)
Step 3 → Then content_block_start for each block (text, tool_use, ...)
Step 4 → Then many content_block_delta events (text_delta, input_json_delta)
Step 5 → Then content_block_stop, then message_delta (stop_reason, output usage)
Step 6 → Finally message_stop
Step 7 → The helper's text_stream yields only the text pieces for you
Step 8 → stream.get_final_message() returns the assembled Message with usage
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Stream खोलो: with client.messages.stream(...) as stream:
Step 2 → Server event भेजता है: message_start (message id, input usage)
Step 3 → फिर हर block के लिए content_block_start (text, tool_use, ...)
Step 4 → फिर कई content_block_delta events (text_delta, input_json_delta)
Step 5 → फिर content_block_stop, फिर message_delta (stop_reason, output usage)
Step 6 → आख़िर में message_stop
Step 7 → Helper का text_stream सिर्फ़ text के टुकड़े देता है
Step 8 → stream.get_final_message() usage सहित पूरा Message लौटाता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: A "Why this code?" panel streams Claude's explanation of the General Rules of Interpretation as it is written. When the stream ends, the backend calls `get_final_message()` to store the full text and token usage in the audit table.

**Zomato AI**: Chat replies stream to the phone token by token, so even a long meal plan starts appearing immediately.

## 🟡 Real Example Hindi mein
**Tariff Classification System**: "यह code क्यों?" panel में Claude की General Rules of Interpretation वाली explanation लिखी जाते ही stream होती है। Stream ख़त्म होने पर backend `get_final_message()` से पूरा text और token usage audit table में save करता है।

**Zomato AI**: Chat replies phone पर token-दर-token stream होते हैं, इसलिए लंबा meal plan भी तुरंत दिखना शुरू हो जाता है।

---

## 💻 Code Example — Basic
```python
# Basic Claude streaming (needs ANTHROPIC_API_KEY)
import os                                        # env access
import anthropic                                 # SDK

client = anthropic.Anthropic()                   # reads key from env
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")   # check docs for current ids

# The context manager opens and closes the HTTP stream for us
with client.messages.stream(
    model=MODEL,                                 # model id
    max_tokens=300,                              # required
    messages=[{"role": "user", "content": "Explain HS codes in 3 short lines."}],
) as stream:
    for text in stream.text_stream:              # yields only text pieces
        print(text, end="", flush=True)          # show immediately
    final = stream.get_final_message()           # complete Message after the stream ends

print()                                          # newline
print("stop_reason:", final.stop_reason)         # why it ended
print("usage:", final.usage.input_tokens, final.usage.output_tokens)
```

## 💻 Code Example — Advanced
```python
# Production async streaming generator with error handling and usage capture
import asyncio                                           # async runner
import logging                                           # logs
import os                                                # env
from dataclasses import dataclass                        # result container
from typing import AsyncIterator, Optional               # type hints

import anthropic                                         # SDK

logger = logging.getLogger(__name__)                     # logger
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")   # configurable model id
client = anthropic.AsyncAnthropic(max_retries=2, timeout=120.0)


@dataclass
class StreamMeta:
    input_tokens: Optional[int] = None                   # filled at the end
    output_tokens: Optional[int] = None                  # filled at the end
    stop_reason: Optional[str] = None                    # filled at the end
    text: str = ""                                       # accumulated text
    interrupted: bool = False                            # True on mid-stream failure


async def stream_claude(prompt: str, meta: StreamMeta, system: str = "Be concise.") -> AsyncIterator[str]:
    try:
        async with client.messages.stream(               # async context manager
            model=MODEL, max_tokens=500, system=system,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for piece in stream.text_stream:       # async iteration over text deltas
                meta.text += piece                       # keep a full copy
                yield piece                              # forward to caller
            final = await stream.get_final_message()     # assembled message
            meta.input_tokens = final.usage.input_tokens
            meta.output_tokens = final.usage.output_tokens
            meta.stop_reason = final.stop_reason
    except anthropic.RateLimitError:                     # 429 before/while streaming
        meta.interrupted = True
        logger.warning("rate limited")
        yield "\n[busy, please retry]"
    except anthropic.APIError as exc:                    # connection or API failure
        meta.interrupted = True
        logger.error("stream failed after %d chars: %s", len(meta.text), exc)
        yield "\n[stream interrupted]"


async def main() -> None:
    meta = StreamMeta()
    async for piece in stream_claude("Why do we need HS codes?", meta):
        print(piece, end="", flush=True)
    print("\n", meta.input_tokens, meta.output_tokens, meta.stop_reason, meta.interrupted)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Return a `StreamingResponse` that wraps the async generator. Use SSE framing so browsers can parse events.

```python
import os                                              # env
import anthropic                                       # SDK
from fastapi import FastAPI                            # framework
from fastapi.responses import StreamingResponse        # streaming response
from pydantic import BaseModel                         # models

app = FastAPI()                                        # app
client = anthropic.AsyncAnthropic(max_retries=2, timeout=120.0)
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")


class Ask(BaseModel):
    question: str


async def sse(question: str):
    try:
        async with client.messages.stream(
            model=MODEL, max_tokens=500,
            messages=[{"role": "user", "content": question}],
        ) as stream:
            async for piece in stream.text_stream:
                safe = piece.replace("\n", "\\n")                         # keep SSE frame on one line
                yield f"data: {safe}\n\n"                                # SSE frame
            yield "event: done\ndata: ok\n\n"                           # completion marker
    except anthropic.APIError:
        yield "event: error\ndata: upstream failure\n\n"                # tell the client


@app.post("/ask-stream")
async def ask_stream(body: Ask) -> StreamingResponse:
    return StreamingResponse(sse(body.question), media_type="text/event-stream",
                             headers={"X-Accel-Buffering": "no"})       # stop nginx buffering
```

---

## 🔗 LangChain / LangGraph Connection
`ChatAnthropic` supports `.stream()` and `.astream()`, which yield `AIMessageChunk` objects. LangGraph's `stream_mode="messages"` streams LLM tokens from inside nodes, regardless of provider.

```python
import asyncio
from langchain_anthropic import ChatAnthropic          # Claude wrapper

llm = ChatAnthropic(model="claude-sonnet-4-5", max_tokens=300)

async def main() -> None:
    async for chunk in llm.astream("Explain HS codes in 2 lines."):
        # chunk.content can be a string, or a list of blocks when tools/thinking are on
        text = chunk.content if isinstance(chunk.content, str) else "".join(
            b.get("text", "") for b in chunk.content if isinstance(b, dict))
        print(text, end="", flush=True)
    print()

# asyncio.run(main())    # needs ANTHROPIC_API_KEY
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Not using the context manager
✅ Correct: `with` / `async with` closes the connection even on errors.

```python
# Wrong — leaks the connection if you break early
stream = client.messages.stream(...)
# Right
with client.messages.stream(...) as stream:
    ...
```

❌ Mistake 2: Using the sync helper inside `async def`
✅ Correct: Use `AsyncAnthropic` with `async with ... as stream` and `async for`.

❌ Mistake 3: Parsing partial JSON tool input mid-stream
✅ Correct: Tool input arrives as `input_json_delta` fragments; wait for the block to finish (or use `get_final_message()`) before `json.loads`.

❌ Mistake 4: Ignoring the final message
✅ Correct: Call `get_final_message()` for `stop_reason` and `usage`; log them for billing.

---

## 🧠 Tricky Interview Question

**Q**: "A user closes the browser tab mid-answer. Does Claude keep generating (and billing) the rest?"

**Answer**: It depends on whether your server cancels the upstream request. If your FastAPI generator keeps consuming the Claude stream after the client disconnects, you keep paying for tokens nobody reads. Fix: detect disconnects (`await request.is_disconnected()` or handle `asyncio.CancelledError` / `GeneratorExit`), leave the `async with client.messages.stream(...)` block so the HTTP connection closes, and record partial usage. Billing is for tokens generated up to the point the stream ends, so promptly closing the stream limits the cost.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] How do you stream with the Anthropic SDK?
A1: `with client.messages.stream(...) as stream: for text in stream.text_stream:`.

Q2: [Easy] How do you get token usage after streaming?
A2: `stream.get_final_message().usage` (input and output tokens).

Q3: [Medium] What event types appear in a Claude stream?
A3: `message_start`, `content_block_start`, `content_block_delta`, `content_block_stop`, `message_delta`, `message_stop` (and `ping`, `error`).

Q4: [Medium] How do tool calls stream?
A4: As a `tool_use` content block whose `input` arrives in `input_json_delta` fragments. Assemble the JSON after the block stops; the SDK helper does this in the final message.

Q5: [Hard] How do you handle errors that occur after streaming has begun?
A5: HTTP status is already 200, so the error arrives as an `error` event or a broken connection. Keep partial output, mark the response as incomplete, show a clear message, log request id and partial usage, and decide whether to retry from scratch (cost and duplicate side effects) or ask the user to resubmit.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chat UIs, long outputs, very large `max_tokens`
- You want a responsive feel

❌ Avoid when:
- Backend-only short classification calls
- You must validate the full output before showing anything

---

## 📊 Visual Diagram
```
Client <--SSE-- FastAPI <--text_stream-- Claude
                    |
   events:  message_start
            content_block_start (text)
            content_block_delta  "The"
            content_block_delta  " HS"
            content_block_delta  " code..."
            content_block_stop
            message_delta (stop_reason, output_tokens)
            message_stop
                    |
          get_final_message() --> usage for billing
```

---

## 💰 Cost Impact
- Streaming costs the same per token as non-streaming; usage arrives in `message_start` (input) and `message_delta` (output).
- Wasted spend appears when disconnected clients do not cancel the upstream stream.
- Optimise: cap `max_tokens`, request concise outputs, cancel on disconnect, cache static prompts, log final usage on every stream.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Stream | Reply sent in pieces | Reply टुकड़ों में |
| text_stream | Iterator of text deltas | Text टुकड़ों का iterator |
| Delta | Small incremental update | छोटा incremental update |
| SSE | Server-Sent Events | Server से events भेजना |
| get_final_message | Assembled message with usage | Usage सहित पूरा message |
| Disconnect | Client closes connection | Client का connection बंद करना |

---

## ⚡ 3-Line Summary
English: Use `client.messages.stream()` and iterate `text_stream` to show Claude's reply as it is generated. Call `get_final_message()` for usage and stop_reason, and handle errors that appear mid-stream. Cancel the upstream stream when the client disconnects to avoid wasted tokens.
Hindi: Claude का reply generate होते ही दिखाने के लिए `client.messages.stream()` और `text_stream` iterate करो। Usage और stop_reason के लिए `get_final_message()` बुलाओ और बीच stream में आने वाले errors संभालो। Client disconnect होने पर upstream stream cancel करो ताकि tokens बर्बाद न हों।

---

## ➡️ Next Topic
**039. Gemini API Basics** — Google's model API and its differences from OpenAI and Claude.
