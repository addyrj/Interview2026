---

# 096. Streaming + Structured Output
# हिंदी में: Streaming + Structured Output

---

## 🔵 Simple Definition (English)
Streaming sends the reply token by token instead of waiting for the whole answer. With structured output the stream is JSON text that is incomplete until the very end, so you must handle **partial JSON**: either wait and parse at the end, or parse incrementally to show fields as they appear. OpenAI offers `client.beta.chat.completions.stream(...)` with a final parsed result; Instructor offers `create_partial`.

## 🔵 सरल परिभाषा (Hindi)
Streaming में reply पूरा बनने का इंतज़ार किए बिना token-by-token आता है। Structured output में stream JSON text होता है जो अंत तक अधूरा रहता है, इसलिए **partial JSON** संभालना पड़ता है: या तो अंत में parse करो, या incrementally parse करके fields दिखाओ। OpenAI `client.beta.chat.completions.stream(...)` देता है जिसमें अंत में parsed result मिलता है; Instructor `create_partial` देता है।

---

## 🔴 Problem it Solves
A long structured answer (a 20-item declaration) can take 8-10 seconds. Users staring at a spinner leave. Streaming shows the first fields after ~300 ms, which feels fast, and long operations stay under proxy timeouts.

## 🔴 यह क्यों बना? (Hindi)
लंबा structured जवाब (20-item declaration) 8-10 seconds ले सकता है। Spinner देखता user चला जाता है। Streaming पहले fields ~300 ms में दिखा देती है, जो तेज़ लगता है, और लंबे operations proxy timeouts के अंदर रहते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Call the API with stream=True (or the .stream() helper)
Step 2 → Receive chunks: delta.content = '{"ite', 'ms": [{"hs', ...
Step 3 → Append each delta to a buffer
Step 4 → Try a tolerant parse of the buffer (close open strings/brackets)
Step 5 → Send the partial object to the UI (SSE / WebSocket)
Step 6 → When the stream ends: strict parse + Pydantic validation
Step 7 → Send a final "done" event with the validated object (or an error event)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → API को stream=True (या .stream() helper) के साथ call करो
Step 2 → Chunks आते हैं: delta.content = '{"ite', 'ms": [{"hs', ...
Step 3 → हर delta को buffer में जोड़ो
Step 4 → Buffer का tolerant parse try करो (खुले strings/brackets बंद करके)
Step 5 → Partial object UI को भेजो (SSE / WebSocket)
Step 6 → Stream खत्म होने पर: strict parse + Pydantic validation
Step 7 → Validated object के साथ अंतिम "done" event (या error event) भेजो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The dashboard shows "Product: Earbuds" the moment `name` arrives, then the HS code a moment later, and finally a green tick when validation finishes. Duty is calculated only after the final validated object.

**Zomato-style**: A chat assistant streams the recommended dish list one card at a time.

## 🟡 Real Example Hindi mein
**Tariff System**: Dashboard में `name` आते ही "Product: Earbuds" दिखता है, फिर कुछ क्षण बाद HS code, और validation खत्म होने पर हरा tick। Duty सिर्फ अंतिम validated object के बाद calculate होती है।

**Zomato-style**: Chat assistant recommended dishes एक-एक card करके stream करता है।

---

## 💻 Code Example — Basic
```python
# Basic: tolerant partial-JSON parsing of a simulated stream. Pure Python, offline.
import json
from typing import Any, Iterator, Optional

def close_json(buffer: str) -> str:
    """Append missing quotes/brackets so a partial JSON string can be parsed."""
    stack: list[str] = []                               # expected closers
    in_str = False                                      # inside a string?
    esc = False                                         # previous char was backslash?
    for ch in buffer:
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False                          # string closed
        else:
            if ch == '"':
                in_str = True
            elif ch in "{[":
                stack.append("}" if ch == "{" else "]")
            elif ch in "}]" and stack:
                stack.pop()
    tail = '"' if in_str else ""                        # close an open string
    return buffer + tail + "".join(reversed(stack))     # close open containers

def try_parse(buffer: str) -> Optional[dict[str, Any]]:
    """Return a partial dict or None if it cannot be parsed yet."""
    try:
        return json.loads(close_json(buffer.rstrip(", \n")))
    except json.JSONDecodeError:
        return None                                     # e.g. buffer ends after a key with no value

def fake_stream() -> Iterator[str]:
    full = '{"name": "Earbuds", "hs_code": "8518.30", "duty_percent": 0.0}'
    for i in range(0, len(full), 7):                    # 7-char chunks like token deltas
        yield full[i:i + 7]

buffer = ""
for delta in fake_stream():
    buffer += delta                                     # accumulate
    partial = try_parse(buffer)
    print(repr(delta).ljust(12), "->", partial)         # UI would update here
final = json.loads(buffer)                              # strict parse at the end
print("FINAL:", final)
```

## 💻 Code Example — Advanced
```python
# Production: OpenAI stream() helper with final Pydantic parse, async generator for SSE.
import asyncio
from typing import AsyncIterator
from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel

client = AsyncOpenAI()

class TariffResult(BaseModel):
    name: str
    hs_code: str
    duty_percent: float

async def stream_classification(product: str) -> AsyncIterator[str]:
    """Yield SSE lines: partial JSON text events, then a final validated event."""
    try:
        async with client.beta.chat.completions.stream(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "Classify the product."},
                      {"role": "user", "content": product}],
            response_format=TariffResult, max_tokens=300, temperature=0,
        ) as stream:
            async for event in stream:                          # typed events
                if event.type == "content.delta":               # new text piece
                    yield f"event: delta\ndata: {event.delta}\n\n"
            final = await stream.get_final_completion()         # waits for the end + parses
        parsed = final.choices[0].message.parsed
        if parsed is None:                                      # refusal
            yield "event: error\ndata: refused\n\n"
        else:
            yield f"event: done\ndata: {parsed.model_dump_json()}\n\n"
    except OpenAIError as exc:
        yield f"event: error\ndata: {exc.__class__.__name__}\n\n"   # never leak internals

async def main() -> None:
    async for line in stream_classification("Wireless earbuds"):    # needs API key
        print(line, end="")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.get("/classify/stream")
async def classify_stream(product: str) -> StreamingResponse:
    # text/event-stream = Server-Sent Events; browsers read it with EventSource
    return StreamingResponse(stream_classification(product), media_type="text/event-stream")
# Tip: send heartbeat comments (": ping\n\n") for long streams behind proxies.
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chain = llm | JsonOutputParser()                        # JsonOutputParser streams PARTIAL dicts
async def run() -> None:
    async for partial in chain.astream("Return JSON {name, hs_code} for earbuds"):
        print(partial)                                  # {} -> {'name': 'Ear'} -> {'name': 'Earbuds', ...}
# with_structured_output(...).astream() yields partial objects for supported models.
# LangGraph: graph.astream(..., stream_mode="updates" | "messages") streams node outputs/tokens.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Acting on partial data (e.g. charging duty from the first partial value)
✅ Correct: Display partials, but act only on the final validated object.

```python
# Wrong: if partial.get("duty_percent"): charge(partial["duty_percent"])  # could be "1" of "10"
# Right: wait for event "done" and the validated model
```

❌ Mistake 2: Calling `json.loads` on every chunk and crashing
✅ Correct: Use tolerant parsing and ignore failures until the end.

```python
# Wrong: for d in stream: data = json.loads(d)   # JSONDecodeError
# Right: buffer += d; partial = try_parse(buffer)
```

---

## 🧠 Tricky Interview Question

**Q**: "With streaming, the user saw `hs_code: 8518` and then the final answer was `8518.30`. A downstream system used the first value. What went wrong?"

**Answer**: Partial values are prefixes, not facts. Strings and numbers are still growing when partially parsed, so `"8518"` was only a prefix of `"8518.30"`. Rule: UI may render partials; business logic consumes only the final, fully validated object (or fields explicitly marked complete, e.g. when the next key starts). Also handle stream errors and disconnects: treat an unfinished stream as failed.

---

## ⚫ Interview Questions + Answers

Q1: Why stream LLM output?
A1: Lower perceived latency: users see output after the first tokens rather than waiting for the full answer.

Q2: Why is streaming JSON harder than streaming text?
A2: JSON is invalid until it is complete, so normal parsers fail on partial text.

Q3: What is SSE?
A3: Server-Sent Events: a one-way HTTP stream (`text/event-stream`) from server to browser; simple and works through most proxies.

Q4: How do you validate a streamed response?
A4: Accumulate the full text (or use the SDK final helper), then parse and validate with Pydantic once the stream ends.

Q5: What happens to token usage and errors in streaming?
A5: Usage is sent at the end only if you ask (`stream_options={"include_usage": True}` for raw streams; the helper collects it). Errors can happen mid-stream, after HTTP 200 was already sent, so send an explicit error event and make the client handle incomplete streams.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Long outputs and interactive UIs
- Chat-like experiences

❌ Avoid when:
- Backend batch jobs (no human watching)
- Small outputs (<1s) where complexity is not worth it

---

## 📊 Visual Diagram
```
 LLM tokens:  {"na | me":"Ear | buds","hs | _code":"85 | 18.30"}
                │       │          │
 buffer ───────►┴───────┴──────────┴──► tolerant parse ─► UI partial
                                        (name: "Ear" -> "Earbuds" ...)
 end of stream ─► strict parse + Pydantic ─► event: done  ─► business logic
```

---

## 💰 Cost Impact
Streaming does not change token cost; you pay the same input and output tokens. It can reduce wasted cost: users can cancel early (closing the connection stops generation, so you stop paying for the rest). Extra cost is server connections held open.
Optimise: allow cancel, set `max_tokens`, include usage in the final event for tracking, stream only for human-facing endpoints.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Streaming | Token-by-token delivery | Token-दर-token delivery |
| Partial JSON | Incomplete JSON text | अधूरा JSON |
| SSE | Server-Sent Events | Server से events की धारा |
| Delta | New piece of text | नया टुकड़ा |
| Time to first token | Wait until first output | पहले token तक का समय |

---

## ⚡ 3-Line Summary
English: Streaming shows structured output early but JSON is incomplete until the end. Display partial data, act only on the final validated object. Use SSE in FastAPI and the SDK helpers.
Hindi: Streaming structured output जल्दी दिखाती है पर JSON अंत तक अधूरा रहता है। Partial data दिखाओ, पर काम सिर्फ अंतिम validated object पर करो। FastAPI में SSE और SDK helpers use करो।

---

## ➡️ Next Topic
**097. Structured Output in FastAPI** — putting everything together in production API design.
