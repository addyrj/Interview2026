---

# 59. Parallelism in SDK
# हिंदी में: SDK में Parallelism (एक साथ कई agents/tools)
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline with a scripted model (`fake.py`, full listing in note #57), so no API key was needed. Real model calls were NOT run - they need OPENAI_API_KEY. Token counts shown come from the fake model (10 in / 5 out per call), not from a real LLM. Measured overlap uses real wall-clock time with `asyncio.sleep(0.2)` tools; no latency figures from real models are claimed.

---

## 🔵 Simple Definition (2-3 lines)
The SDK has no special 'parallel' switch for agents. You get parallelism from asyncio: run several `Runner.run(...)` calls with `asyncio.gather`, and when one model turn asks for several tool calls the SDK runs async tools concurrently. Your job is to keep tools async and to bound concurrency.

## 🔵 सरल परिभाषा (Hindi)
Agents के लिए SDK में कोई अलग 'parallel' switch नहीं है। Parallelism asyncio से मिलता है: कई `Runner.run(...)` को `asyncio.gather` से चलाओ, और जब एक model turn कई tool calls माँगता है तो SDK async tools को एक साथ चलाता है। आपका काम tools को async रखना और concurrency पर सीमा लगाना है।

---

## 🔴 Problem it Solves
Independent work done one after another wastes time: classifying 50 invoice lines sequentially, or checking rates + rules + sanctions one by one. Latency adds up (sum of all steps) when it could be the slowest single step. But unlimited parallelism hits provider rate limits and one failure can cancel everything.

## 🔴 यह क्यों बना? (Hindi)
स्वतंत्र काम को एक के बाद एक करना समय बर्बाद है: 50 invoice lines को क्रम से classify करना, या rates + rules + sanctions एक-एक करके जाँचना। Latency सभी steps का जोड़ बन जाती है जबकि वह सबसे धीमे step जितनी हो सकती थी। पर असीमित parallelism provider की rate limits तोड़ देता है और एक failure सब कुछ रद्द कर सकता है।

---

## 🟢 How it Works

```
Pattern 1: many runs at once
  results = await asyncio.gather(Runner.run(a1, x), Runner.run(a2, x), ...)
Pattern 2: one model turn -> several tool calls
  LLM returns [tool_call A, tool_call B]
  SDK awaits both tools concurrently (async tools overlap)
Pattern 3: bounded fan-out for N items
  sem = asyncio.Semaphore(3)
  async with sem: await asyncio.wait_for(Runner.run(...), timeout)
Pattern 4: partial failure
  catch exceptions PER item, return ok/error rows
  (or gather(..., return_exceptions=True))
```

## 🟢 कैसे काम करता है? (Hindi)

```
Pattern 1: कई runs एक साथ
  results = await asyncio.gather(Runner.run(a1, x), Runner.run(a2, x), ...)
Pattern 2: एक model turn -> कई tool calls
  LLM [tool_call A, tool_call B] लौटाता है
  SDK दोनों tools को एक साथ await करता है (async tools overlap होते हैं)
Pattern 3: N items के लिए सीमित fan-out
  sem = asyncio.Semaphore(3)
  async with sem: await asyncio.wait_for(Runner.run(...), timeout)
Pattern 4: आंशिक failure
  हर item पर अलग exception पकड़ो, ok/error rows लौटाओ
  (या gather(..., return_exceptions=True))
```

**What we measured offline (b59):** three agent runs with a 0.2 s async tool finished in well under 0.5 s total (overlap = True, instead of about 0.6 s sequential), and a single model turn with two `slow_lookup` calls also overlapped (True). A *sync* `def` tool would block differently - write I/O tools as `async def`.

**Related knobs:** `ModelSettings(parallel_tool_calls=False)` tells the model not to emit several tool calls in one turn (we used it in #61). Parallel tool calls change ordering: do not write tools that depend on each other's side effects.

**Hindi नोट:** तीन चीज़ें याद रखो: (1) कई agents = `asyncio.gather`; (2) एक turn के कई tool calls = SDK खुद concurrent चलाता है (अगर tools `async def` हैं); (3) बिना `Semaphore` के 500 items भेजोगे तो rate limit (HTTP 429) मिलेगा।

---

## 🟡 Real World Example
**Tariff Agent.** A customs broker uploads a declaration with 40 lines. The service classifies all lines in parallel (max 3 at once), returns a row per line with `ok` or `error`, and one refused line does not kill the other 39.

**Research Agent:** run `web_searcher`, `paper_searcher`, `news_searcher` concurrently and merge.

## 🟡 Real Example Hindi mein
**Tariff Agent.** Customs broker 40 lines वाली declaration upload करता है। Service सभी lines को parallel में (एक समय में अधिकतम 3) classify करती है, हर line के लिए `ok` या `error` वाली row लौटाती है, और एक line fail होने पर बाकी 39 प्रभावित नहीं होतीं।

**Research Agent:** `web_searcher`, `paper_searcher`, `news_searcher` को साथ चलाकर नतीजे मिलाओ।

---

## 💻 Code Example — Basic
Runs offline (timing is real wall-clock; the model is scripted). Pattern 1 and pattern 2 from the diagram.

```python
# Basic: run several agents in parallel with asyncio.gather (offline).
# verified against openai-agents 0.24.0
import asyncio, time                                              # concurrency + timing
from agents import Agent, Runner, function_tool, set_tracing_disabled
from fake import ScriptedModel, tool_call, text

set_tracing_disabled(True)

@function_tool
async def slow_lookup(name: str) -> str:                          # async tool => can overlap with others
    """Pretend network call (0.2 s)."""
    await asyncio.sleep(0.2)                                      # simulated I/O
    return f"{name} ok"

def make(name: str) -> Agent:                                     # each agent has its own scripted model
    m = ScriptedModel([[tool_call("slow_lookup", '{"name":"%s"}' % name)], [text(f"{name} done")]])
    return Agent(name=name, instructions="x", tools=[slow_lookup], model=m)

async def main() -> None:
    t0 = time.perf_counter()
    # Pattern 1: three independent agent runs at once
    results = await asyncio.gather(*[Runner.run(make(n), "go") for n in ("Rates", "Rules", "Sanctions")])
    print([r.final_output for r in results])                      # ['Rates done', 'Rules done', 'Sanctions done']
    print("three runs overlapped:", time.perf_counter() - t0 < 0.5)   # ~0.2 s, not ~0.6 s

    # Pattern 2: ONE model turn that asks for two tool calls -> SDK runs them concurrently
    m = ScriptedModel([[tool_call("slow_lookup", '{"name":"a"}'), tool_call("slow_lookup", '{"name":"b"}')], [text("both")]])
    t1 = time.perf_counter()
    r = await Runner.run(Agent(name="Multi", instructions="x", tools=[slow_lookup], model=m), "go")
    print(r.final_output, "tools overlapped:", time.perf_counter() - t1 < 0.35)

asyncio.run(main())
```

Expected output: `['Rates done', 'Rules done', 'Sanctions done']`, `three runs overlapped: True`, `both tools overlapped: True`.

## 💻 Code Example — Advanced
FastAPI batch endpoint: `Semaphore(3)` for bounded concurrency, `asyncio.wait_for` per item, per-item error rows, results in the same order as the input.

```python
# Advanced: bounded parallel fan-out with timeout, partial failure handling and FastAPI.
# verified against openai-agents 0.24.0 + fastapi 0.163.0 (TestClient); real model: not run - needs OPENAI_API_KEY
import asyncio                                                    # gather, Semaphore, wait_for
from fastapi import FastAPI                                       # web layer
from pydantic import BaseModel
from agents import Agent, Runner, set_tracing_disabled
from fake import ScriptedModel, text

set_tracing_disabled(True)
SEM = asyncio.Semaphore(3)                                        # at most 3 concurrent LLM runs (rate-limit protection)

class Item(BaseModel):                                            # one line of a customs declaration
    sku: str

class LineResult(BaseModel):
    sku: str
    ok: bool
    answer: str | None = None
    error: str | None = None

def agent_for(sku: str) -> Agent:                                 # new agent per item (scripted offline)
    reply = "FAIL" if sku == "bad" else f"HS for {sku}"
    return Agent(name=f"Classify-{sku}", instructions="classify", model=ScriptedModel([[text(reply)]]))

async def classify_one(sku: str, timeout_s: float = 20.0) -> LineResult:
    async with SEM:                                               # wait for a free slot
        try:
            res = await asyncio.wait_for(Runner.run(agent_for(sku), sku, max_turns=3), timeout=timeout_s)
            if res.final_output == "FAIL":                        # simulate a domain failure
                raise ValueError("classifier refused")
            return LineResult(sku=sku, ok=True, answer=str(res.final_output))
        except asyncio.TimeoutError:
            return LineResult(sku=sku, ok=False, error="timeout")
        except Exception as e:                                    # one bad line must not kill the batch
            return LineResult(sku=sku, ok=False, error=f"{type(e).__name__}: {e}")

app = FastAPI()

@app.post("/classify-batch", response_model=list[LineResult])
async def classify_batch(items: list[Item]) -> list[LineResult]:
    return list(await asyncio.gather(*(classify_one(i.sku) for i in items)))   # order of results == order of items

if __name__ == "__main__":
    from fastapi.testclient import TestClient
    for row in TestClient(app).post("/classify-batch", json=[{"sku": "a"}, {"sku": "bad"}, {"sku": "c"}]).json():
        print(row)
```

Output: three rows - `a` ok, `bad` with `error: 'ValueError: classifier refused'`, `c` ok.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Run branches concurrently | Parallel edges / `Send` fan-out | `async_execution=True` on tasks | `asyncio.gather` over `Runner.run` | `asyncio.gather` / parallel team runs |
| Parallel tool calls in one turn | Tool node runs them | Depends on version | Yes, async tools run concurrently | Yes (`parallel_tool_calls` model setting) |
| Concurrency limit | `max_concurrency` in config | Manual | Your `Semaphore` | Your `Semaphore` |
| Merge results | Reducers in state | Task context | Your code | Your code |
| Partial failure | Per-node handling | Per-task | try/except per item | try/except per item |

_OpenAI SDK column verified in openai-agents 0.24.0; the other columns are from general knowledge of those libraries (not installed or re-verified here) - check their docs before quoting in an interview._

---

## ⚠️ Common Mistakes
❌ Mistake: `for sku in skus: await Runner.run(...)` for 50 items.
✅ Correct: `gather` with a `Semaphore` so it is parallel but bounded.

❌ Mistake: Sync `def` tools that call `requests.get`.
✅ Correct: Use `async def` and `httpx.AsyncClient`, otherwise the event loop blocks and nothing overlaps.

❌ Mistake: `gather` without error handling - one exception cancels the caller's whole request.
✅ Correct: Catch per item or use `return_exceptions=True`; return partial results.

❌ Mistake: Sharing one mutable Agent/context across parallel runs.
✅ Correct: Give each run its own context object; Agents themselves are safe to reuse if you do not mutate them.

---

## 🧠 Tricky Interview Question
Batch endpoint with 200 lines is slower in parallel than expected and sometimes returns 429 from the provider. What do you do?

**Answer:** Parallelism is limited by the provider's requests-per-minute and tokens-per-minute, not by asyncio. Fixes: (1) bound concurrency with a Semaphore tuned to your quota, (2) add retry with jittered exponential backoff on rate-limit errors, (3) batch small items into one prompt where accuracy allows, (4) use a smaller model for classification, (5) cache repeated SKUs, (6) move the job to a background queue and return a job id instead of holding the HTTP request, (7) measure queue time vs model time with tracing. Also check that tools are really async - one blocking call serialises everything.

---

## ⚫ Interview Questions + Answers

**Q1:** How do you run two agents in parallel in the SDK?

**A1:** `await asyncio.gather(Runner.run(a, x), Runner.run(b, x))`.

**Q2:** Does the SDK run multiple tool calls from one turn concurrently?

**A2:** Yes for async tools; we measured overlap offline.

**Q3:** Why use a Semaphore?

**A3:** To cap concurrent LLM calls so you stay under rate limits and memory.

**Q4:** `gather` vs `return_exceptions=True`?

**A4:** Default `gather` raises the first exception; with `return_exceptions=True` you get exceptions as values and can build partial results.

**Q5:** Design: 10k invoices per night.

**A5:** Queue (Celery/RQ/Cloud tasks), worker pool with bounded concurrency per worker, idempotent job per invoice, retries with backoff, dead-letter queue, per-job token/cost logging, and a status API. Do not do it inside one HTTP request.

---

## 💰 Cost Impact
Parallelism does not reduce tokens; it reduces wall time. N parallel runs cost N times a single run, and bursts can trigger rate limits (retries add cost). Formula: total cost = sum of per-run tokens x price. Tips: Semaphore, cache duplicates, cheaper model for per-line work. Prices are approximate - verify.

---

## 🔷 When to Use
✅ Use when:
- Independent subtasks (per line, per source)
- Several tool calls that do not depend on each other
- Latency matters more than strict ordering

❌ Avoid when:
- Steps depend on earlier results
- Your quota is tiny and bursts cause 429s
- Tools are sync/blocking (no overlap)

---

## 📊 Visual Diagram
```
  request: 3 lines
     |
     v
  Semaphore(3)  ----------------------------+
     |            |             |            |
     v            v             v            |
  Runner.run   Runner.run    Runner.run      |  each: own agent loop
  (line a)     (line bad)    (line c)        |
     |            |             |            |
     v            v             v            |
   ok row     error row       ok row  <------+  per-item try/except
     \___________|____________/
                  v
          gather -> ordered list -> response
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| asyncio.gather | Run awaitables together | कई awaitables साथ चलाना |
| Semaphore | Concurrency limiter | एक साथ चलने वालों की सीमा |
| Fan-out / fan-in | Split work, then merge | बाँटना फिर जोड़ना |
| wait_for | Timeout wrapper | समय-सीमा wrapper |
| parallel_tool_calls | Model setting for multi tool calls | एक turn में कई tool calls |
| Rate limit (429) | Provider says slow down | provider की गति-सीमा |

---

## ⚡ 3-Line Summary
English: Parallelism in the SDK is plain asyncio: gather runs, async tools overlap inside one turn.
Bound it with a Semaphore, add timeouts and per-item error handling.
It cuts wall time, not token cost.

Hindi: SDK में parallelism सीधा asyncio है: runs को gather करें, एक turn के async tools overlap होते हैं।
Semaphore से सीमा लगाएँ, timeouts और per-item error handling जोड़ें।
इससे wall time घटता है, token cost नहीं।

---

## ➡️ Next Topic
**#60 Cloning Agents** - when you run the same agent shape per country or per tenant, you need `clone()` to make variants safely.

---
