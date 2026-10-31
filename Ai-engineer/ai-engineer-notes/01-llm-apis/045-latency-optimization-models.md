---

# 045. Latency Optimization — Models
# हिंदी में: Models की Latency Optimization

---

## 🔵 Simple Definition (English)
Latency is how long a user waits for an answer. For LLMs there are two numbers: time to first token (TTFT) and total time. Latency optimisation reduces both using streaming, smaller models, shorter outputs, parallel calls and caching.

## 🔵 सरल परिभाषा (Hindi)
Latency यानी user को जवाब के लिए कितना इंतज़ार करना पड़ता है। LLM में दो numbers होते हैं: पहला token कब आया (TTFT) और कुल समय। Streaming, छोटे models, छोटे outputs, parallel calls और caching से दोनों घटाए जाते हैं।

---

## 🔴 Problem it Solves
- LLMs generate token by token; a 500-token answer can take 5-15 seconds.
- Users leave if a chat shows nothing for several seconds.
- Chains of several LLM calls add up: 4 calls x 3 s = 12 s.
- Slow responses hold server connections open and reduce throughput.

## 🔴 यह क्यों बना? (Hindi)
- LLM token-by-token generate करता है; 500 tokens के जवाब में 5-15 seconds लग सकते हैं।
- Chat में कई seconds कुछ न दिखे तो user चला जाता है।
- कई LLM calls की chain जुड़ती जाती है: 4 calls x 3 s = 12 s।
- धीमे responses connections को देर तक रोके रखते हैं और throughput घटता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Measure: record TTFT, total latency, tokens/second (p50 and p95, not just average)
Step 2 → Stream the response so users see text immediately (improves perceived speed)
Step 3 → Reduce output tokens: output generation is the slowest part (time ~ output tokens)
Step 4 → Use a smaller/faster model for simple steps
Step 5 → Run independent calls in parallel (asyncio.gather)
Step 6 → Shrink input: long prompts increase prefill time
Step 7 → Cache and prompt-cache repeated prefixes
Step 8 → Set timeouts and fallbacks so one slow call cannot block the user
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Measure करो: TTFT, total latency, tokens/second (सिर्फ़ average नहीं, p50 और p95)
Step 2 → Response stream करो ताकि user को text तुरंत दिखे (perceived speed बढ़ती है)
Step 3 → Output tokens घटाओ: generation सबसे धीमा हिस्सा है (समय ~ output tokens)
Step 4 → आसान steps के लिए छोटा/तेज़ model लो
Step 5 → Independent calls parallel चलाओ (asyncio.gather)
Step 6 → Input छोटा करो: लंबा prompt prefill time बढ़ाता है
Step 7 → Cache और repeated prefix का prompt cache इस्तेमाल करो
Step 8 → Timeout और fallback लगाओ ताकि एक slow call user को block न करे
```

---

## 🟡 Real World Example
**Tariff Classification System**: One request needs: (a) extract product attributes, (b) retrieve similar HS codes, (c) check country-specific duty notes, (d) write explanation. Sequentially this took 11 s. Steps (a), (b), (c) are independent, so running them in parallel and using a small model for (a) cut the time to 4.5 s. Streaming the explanation (d) shows the first words in under 1 s.

**Zomato-style**: A delivery-support chatbot must answer in about 2 s. It uses a small fast model, streams text, and keeps replies under 60 words.

## 🟡 Real Example Hindi mein
**Tariff System**: एक request में: (a) product attributes निकालना, (b) similar HS codes retrieve करना, (c) country-specific duty notes जाँचना, (d) explanation लिखना। Sequential में 11 s लगते थे। (a), (b), (c) independent हैं, इसलिए parallel चलाने और (a) के लिए small model से समय 4.5 s हो गया। (d) stream करने से पहले शब्द 1 s से कम में दिखते हैं।

**Zomato-style**: Delivery-support chatbot को लगभग 2 s में जवाब देना होता है। वह fast small model, streaming और 60 words से कम replies इस्तेमाल करता है।

---

## 💻 Code Example — Basic
```python
# Basic: compare sequential vs parallel calls with a fake slow LLM (runs offline)
import asyncio  # async library
import time  # timer

async def fake_llm(task: str, seconds: float) -> str:
    await asyncio.sleep(seconds)  # pretend the model is thinking
    return f"{task}: done"  # fake answer

async def sequential() -> float:
    start = time.perf_counter()  # start timer
    await fake_llm("extract", 1.0)  # call 1
    await fake_llm("retrieve", 1.0)  # call 2
    await fake_llm("duty-notes", 1.0)  # call 3
    return time.perf_counter() - start  # elapsed

async def parallel() -> float:
    start = time.perf_counter()  # start timer
    await asyncio.gather(  # run all three at the same time
        fake_llm("extract", 1.0),
        fake_llm("retrieve", 1.0),
        fake_llm("duty-notes", 1.0),
    )
    return time.perf_counter() - start  # elapsed

async def main() -> None:
    print(f"Sequential: {await sequential():.1f}s")  # about 3.0s
    print(f"Parallel:   {await parallel():.1f}s")  # about 1.0s

asyncio.run(main())  # run the demo
```

## 💻 Code Example — Advanced
```python
# Production-style: streaming with TTFT measurement, timeout and fallback model
import asyncio  # timeouts and gather
import time  # latency measurement
from dataclasses import dataclass  # result container
from typing import AsyncIterator  # streaming type
from openai import AsyncOpenAI, APIError, APITimeoutError  # openai>=1

client = AsyncOpenAI(timeout=20.0, max_retries=1)  # global client timeout

@dataclass
class StreamStats:
    ttft_s: float = 0.0  # time to first token
    total_s: float = 0.0  # total time
    chars: int = 0  # streamed characters

async def stream_answer(prompt: str, model: str, stats: StreamStats) -> AsyncIterator[str]:
    start = time.perf_counter()  # start timer
    first = True  # flag for first token
    stream = await client.chat.completions.create(  # stream=True returns async iterator
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=250,  # shorter output = faster
        stream=True,
    )
    async for chunk in stream:  # each chunk has a small delta
        if not chunk.choices:  # some chunks carry no choices
            continue
        piece = chunk.choices[0].delta.content or ""  # new text
        if piece and first:  # first visible token
            stats.ttft_s = time.perf_counter() - start
            first = False
        stats.chars += len(piece)  # count output
        yield piece  # send to caller
    stats.total_s = time.perf_counter() - start  # final time

async def stream_with_fallback(prompt: str) -> AsyncIterator[str]:
    stats = StreamStats()  # per-request stats
    try:
        # Try the strong model, but cancel if first token takes too long
        agen = stream_answer(prompt, "gpt-4o", stats)  # async generator
        first = await asyncio.wait_for(agen.__anext__(), timeout=3.0)  # TTFT guard
        yield first  # forward first piece
        async for piece in agen:  # rest of the stream
            yield piece
    except (asyncio.TimeoutError, APITimeoutError, APIError):  # slow or failing
        async for piece in stream_answer(prompt, "gpt-4o-mini", stats):  # faster model
            yield piece

# async for part in stream_with_fallback("Explain HS code 8517"): print(part, end="")
```

---

## 🟠 FastAPI Integration
Use `StreamingResponse` so the browser gets tokens as they arrive. Server-Sent Events (SSE) is the common format for chat UIs.

```python
from fastapi import FastAPI  # framework
from fastapi.responses import StreamingResponse  # streaming support
from pydantic import BaseModel  # request validation

app = FastAPI()  # app instance

class Ask(BaseModel):
    question: str  # user question

async def sse(question: str):
    async for piece in stream_with_fallback(question):  # from advanced example
        # SSE format: "data: <text>\n\n" ; escape newlines in real apps
        yield f"data: {piece.replace(chr(10), ' ')}\n\n"
    yield "data: [DONE]\n\n"  # end marker

@app.post("/ask/stream")
async def ask_stream(body: Ask) -> StreamingResponse:
    return StreamingResponse(sse(body.question), media_type="text/event-stream")
```

---

## 🔗 LangChain / LangGraph Connection
LCEL chains support `astream` for token streaming and `abatch` for parallel inputs. `RunnableParallel` runs independent branches concurrently. LangGraph streams node updates with `astream` (`stream_mode="updates"` or `"messages"`), and nodes with no dependency run in parallel supersteps.

```python
from langchain_core.runnables import RunnableParallel  # parallel branches
from langchain_core.prompts import ChatPromptTemplate  # prompts
from langchain_core.output_parsers import StrOutputParser  # parser
from langchain_openai import ChatOpenAI  # model

llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=200)  # fast model
attrs = ChatPromptTemplate.from_template("Attributes of: {item}") | llm | StrOutputParser()
notes = ChatPromptTemplate.from_template("Duty notes for: {item}") | llm | StrOutputParser()
both = RunnableParallel(attributes=attrs, duty=notes)  # runs concurrently

# result = await both.ainvoke({"item": "cotton shirt"})  # one wall-clock wait
# async for tok in attrs.astream({"item": "cotton shirt"}): print(tok, end="")
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Waiting for the full answer before showing anything
✅ Correct: Stream tokens.

```python
# Wrong: resp = await client.chat.completions.create(..., stream=False)  # user waits 8s
# Right: stream=True and forward chunks to the UI  # user sees text in under 1s
```

❌ Mistake 2: Running independent calls one after another
✅ Correct: Use `asyncio.gather`.

```python
# Wrong:
# a = await f(); b = await g()
# Right:
# a, b = await asyncio.gather(f(), g())
```

---

## 🧠 Tricky Interview Question
**Q**: "You switch to a model with higher tokens-per-second but users say it feels slower. Why?"

**Answer**: Perceived latency depends on TTFT, not only throughput. A model may have higher tokens/s but a long queue or long prefill (big prompt, reasoning tokens), so the first token arrives later. Also non-streaming UIs show nothing until the end. Measure TTFT and total separately, at p95, and check hidden "thinking" tokens that add delay before visible text.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is TTFT?
A1: Time to first token: delay between sending a request and receiving the first generated token. It controls how responsive a chat feels.

Q2: [Easy] Why does streaming help?
A2: Total time stays similar, but users start reading immediately, so waiting feels much shorter.

Q3: [Medium] What increases LLM latency the most?
A3: Output length (tokens are generated one by one), model size, long inputs (prefill), queueing under load, and sequential multi-call chains.

Q4: [Medium] How do you cut latency in a multi-step chain?
A4: Run independent steps in parallel, merge steps into one prompt when safe, use small models for easy steps, cache repeated results, and stream the final step.

Q5: [Hard] How would you set a latency SLO for an LLM feature?
A5: Define SLOs on p95 TTFT and p95 total time per feature (for example TTFT under 1.5 s, total under 8 s). Add per-call timeouts, a fallback to a faster model, circuit breakers, and alerts. Track by model, prompt version and token count to find regressions. Load test, because latency grows under rate limits and queueing.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Interactive chat or voice features
- Chains with many LLM steps
- Strict SLA targets

❌ Avoid when:
- Offline batch jobs (optimise cost, not latency)
- Streaming makes validation hard (for example you need full JSON before using it)

---

## 📊 Visual Diagram
```
Sequential:  [extract 1s][retrieve 1s][notes 1s][explain 3s]  = 6s

Parallel:    [extract 1s]
             [retrieve 1s]  -> wait for slowest (1s) -> [explain 3s] = 4s
             [notes    1s]

Streaming:   [explain] ---> first words at ~0.5s, user reads while it generates
```

---

## 💰 Cost Impact
- Token usage: shorter outputs reduce both latency and cost (output tokens are the priciest and slowest).
- Parallel calls keep the same token cost but reduce wall-clock time. Hedged requests (sending a duplicate call to a fallback model) can raise cost, so use them only on rare slow cases.
- Fast small models are usually cheaper and faster; test that quality is still acceptable.
- Provider prompt caching reduces both prefill latency and input cost for repeated prefixes.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Latency | Wait time for a response | जवाब के लिए इंतज़ार |
| TTFT | Time to first token | पहला token आने का समय |
| Streaming | Send tokens as generated | Tokens बनते ही भेजना |
| p95 | 95% requests are faster | 95% requests इससे तेज़ |
| Prefill | Model reads input before output | Output से पहले input पढ़ना |
| SSE | Server-Sent Events | Server से लगातार events |

---

## ⚡ 3-Line Summary
English: Latency depends mostly on output tokens, model size and sequential steps. Stream, parallelise independent calls, use smaller models and cap output. Measure TTFT and p95, not only averages.
Hindi: Latency ज़्यादातर output tokens, model size और sequential steps से बनती है। Stream करो, independent calls parallel चलाओ, छोटे model और output cap लगाओ। सिर्फ़ average नहीं, TTFT और p95 measure करो।

---

## ➡️ Next Topic
**046. OpenAI Responses API (new)** — OpenAI's newer API that unifies chat, tools and state in one interface.
