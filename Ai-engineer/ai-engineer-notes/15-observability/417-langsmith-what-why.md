---

# 417. LangSmith — What + Why
# हिंदी में: LangSmith — क्या है और क्यों

---

## 🔵 Simple Definition (English)
LangSmith is a platform from the LangChain team to see, debug, test and monitor LLM apps. It records every step of a request (a trace): prompts, model calls, tools, tokens, cost, latency, errors. It also stores datasets, runs evaluations and hosts prompts. It works with any framework, not only LangChain.

## 🔵 सरल परिभाषा (Hindi)
LangSmith, LangChain team का platform है जिससे LLM apps को देखा, debug, test और monitor किया जाता है। यह request के हर step (trace) को record करता है: prompts, model calls, tools, tokens, cost, latency, errors। इसमें datasets, evaluations और prompts भी रहते हैं। यह किसी भी framework के साथ चलता है, सिर्फ़ LangChain के साथ नहीं।

---

## 🔴 Problem it Solves
- LLM apps are black boxes: the answer is wrong but you cannot see which prompt was sent, what the retriever returned or which tool failed.
- `print()` debugging does not scale to multi-step agents and thousands of users.
- Nobody knows the real cost per request or which step is slow.
- No shared place to keep test datasets and compare prompt versions.

## 🔴 यह क्यों बना? (Hindi)
- LLM apps black box हैं: answer गलत है पर दिखता नहीं कि कौन सा prompt गया, retriever ने क्या दिया, कौन सा tool fail हुआ।
- Multi-step agents और हज़ारों users पर `print()` debugging नहीं चलती।
- असली cost per request और कौन सा step धीमा है, पता नहीं चलता।
- Test datasets रखने और prompt versions compare करने की साझा जगह नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Set env vars (API key, tracing on, project name)
Step 2 → Your app runs normally (LangChain/LangGraph auto-traces; others use @traceable)
Step 3 → SDK sends each step as a "run" to LangSmith in a background thread
Step 4 → Runs are grouped: one request = one trace (tree of runs)
Step 5 → UI shows inputs, outputs, tokens, cost, latency, errors per run
Step 6 → You add feedback, save bad traces into a dataset
Step 7 → Run evaluations on the dataset and compare experiments
Step 8 → Dashboards/alerts monitor production
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Env vars set करो (API key, tracing on, project name)
Step 2 → App सामान्य चलता है (LangChain/LangGraph अपने-आप trace; बाकी @traceable)
Step 3 → SDK हर step को "run" बनाकर background thread में LangSmith भेजता है
Step 4 → Runs group होते हैं: एक request = एक trace (runs का tree)
Step 5 → UI में हर run का input, output, tokens, cost, latency, error दिखता है
Step 6 → Feedback जोड़ो, खराब traces को dataset में सहेजो
Step 7 → Dataset पर evaluation चलाओ और experiments compare करो
Step 8 → Dashboards/alerts से production monitor करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs broker reports "HS code for ceramic tiles is wrong". In LangSmith you open the trace, see: query rewrite -> retriever returned 4 chunks (none from Chapter 69) -> LLM answered with Chapter 68. Root cause is retrieval, not the LLM. You save the trace to the dataset "tariff-failures", fix the chunking, re-run the evaluation and see accuracy go from 81% to 88%. Total debug time: 10 minutes instead of a day.

**Amazon-style support bot**: Dashboards show p95 latency per step and cost per ticket, so the team finds that the reranker is 60% of the latency.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs broker कहता है "ceramic tiles का HS code गलत है"। LangSmith में trace खोलने पर दिखता है: query rewrite -> retriever ने 4 chunks दिए (Chapter 69 का एक भी नहीं) -> LLM ने Chapter 68 बताया। कारण retrieval है, LLM नहीं। Trace को dataset "tariff-failures" में सहेजा, chunking ठीक की, evaluation दोबारा चलाया और accuracy 81% से 88% हुई। Debug में 10 मिनट लगे, एक दिन नहीं।

**Amazon-style support bot**: Dashboard में हर step की p95 latency और cost per ticket दिखती है, इसलिए पता चलता है कि reranker कुल latency का 60% है।

---

## 💻 Code Example — Basic
```python
# Basic: a tiny "tracer" that mimics what LangSmith records (pure Python, offline)
import time                                                   # timing each step
import uuid                                                   # unique run ids
from typing import Any, Callable                              # typing

TRACE: list[dict[str, Any]] = []                              # in-memory list of runs

def traceable_demo(name: str) -> Callable:                    # decorator factory, like @traceable
    def deco(fn: Callable) -> Callable:                       # takes the function
        def wrapper(*args: Any, **kwargs: Any) -> Any:        # replaces the function
            run = {"id": str(uuid.uuid4())[:8], "name": name, "inputs": args}  # start a run record
            start = time.perf_counter()                       # start timer
            try:
                run["output"] = fn(*args, **kwargs)           # call real function
                return run["output"]                          # give result back
            except Exception as exc:                          # record the error too
                run["error"] = repr(exc)
                raise                                         # do not hide the error
            finally:
                run["latency_ms"] = round((time.perf_counter() - start) * 1000, 2)  # duration
                TRACE.append(run)                             # save the run
        return wrapper
    return deco

@traceable_demo("retrieve")                                   # step 1
def retrieve(q: str) -> list[str]:
    return ["Chapter 85: electrical machinery"]               # fake chunk

@traceable_demo("answer")                                     # step 2
def answer(q: str) -> str:
    return f"8507 ({len(retrieve(q))} chunk)"                 # fake LLM answer

answer("power bank")                                          # run the app
for r in TRACE:                                               # print the trace like a UI would
    print(r["name"], r["latency_ms"], "ms", r.get("output"))
```

## 💻 Code Example — Advanced
```python
# Real LangSmith usage: @traceable, metadata, async, safe fallback when no key
# pip install langsmith openai
import asyncio                                                # async runtime
import os                                                     # env access
from langsmith import traceable                               # decorator that sends runs
from langsmith.wrappers import wrap_openai                    # auto-trace OpenAI calls
from openai import AsyncOpenAI                                # async OpenAI client

# Tracing is controlled by env vars (set in .env / secrets, never in code):
#   LANGSMITH_TRACING=true
#   LANGSMITH_API_KEY=lsv2_...
#   LANGSMITH_PROJECT=tariff-prod

client = wrap_openai(AsyncOpenAI()) if os.getenv("OPENAI_API_KEY") else None  # wrapped client

@traceable(run_type="retriever", name="retrieve_tariff_notes")  # appears as a retriever run
async def retrieve(query: str) -> list[str]:
    await asyncio.sleep(0)                                    # replace with vector DB call
    return ["Chapter 85 note: batteries and accumulators"]

@traceable(run_type="chain", name="classify_hs", metadata={"version": "v3"})  # parent run
async def classify(product: str) -> str:
    docs = await retrieve(product)                            # child run is nested automatically
    if client is None:                                        # offline fallback for local tests
        return "8507.60 (mock)"
    try:
        resp = await client.chat.completions.create(          # child LLM run (tokens auto-logged)
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=100,
            messages=[{"role": "system", "content": "Return only the HS code."},
                      {"role": "user", "content": f"Product: {product}\nNotes: {docs}"}],
        )
        return resp.choices[0].message.content or ""         # final text
    except Exception as exc:                                  # trace keeps the error automatically
        return f"ERROR: {type(exc).__name__}"

if __name__ == "__main__":
    print(asyncio.run(classify("lithium power bank")))        # one request = one trace tree
```

---

## 🟠 FastAPI Integration
Wrap the route's core logic with `@traceable` and return the run id so a front end can attach user feedback to the exact trace later. Use `langsmith.run_helpers.get_current_run_tree()` to read the id.

```python
from fastapi import FastAPI                                   # framework
from pydantic import BaseModel                                # validation
from langsmith import traceable                               # tracing decorator
from langsmith.run_helpers import get_current_run_tree        # access current run

app = FastAPI()                                               # app

class Q(BaseModel):                                           # request
    product: str

@traceable(name="api_classify")                               # one trace per request
async def handle(product: str) -> dict[str, str]:
    rt = get_current_run_tree()                               # run tree of this request
    return {"hs_code": "8507.60", "run_id": str(rt.id) if rt else ""}  # return id for feedback

@app.post("/classify")                                        # public route
async def classify_route(q: Q) -> dict[str, str]:
    return await handle(q.product)                            # traced call
```

---

## 🔗 LangChain / LangGraph Connection
If env vars are set, every LCEL chain and LangGraph graph is traced automatically with no code change. Each node becomes a child run, so you can see graph paths, loops and tool calls. Tags and metadata can be passed via `config`.

```python
from langchain_core.prompts import ChatPromptTemplate         # prompt
from langchain_openai import ChatOpenAI                       # model

chain = ChatPromptTemplate.from_template("HS code for {p}?") | ChatOpenAI(model="gpt-4o-mini")
# result = chain.invoke({"p": "power bank"},
#                       config={"tags": ["tariff"], "metadata": {"user_tier": "pro"}})
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Hard-coding the API key in source.
✅ Correct: environment variables or a secrets manager.

```python
# Wrong
os.environ["LANGSMITH_API_KEY"] = "lsv2_secret_in_git"
# Right
# export LANGSMITH_API_KEY=... in the deployment environment
```

❌ Mistake 2: Tracing raw PII (customer names, card numbers) to a third-party service.
✅ Correct: mask or hide inputs/outputs for sensitive runs.

```python
# Wrong
@traceable
def f(card_number: str): ...
# Right
@traceable(process_inputs=lambda inp: {"card_number": "***"})
def f(card_number: str): ...
```

---

## 🧠 Tricky Interview Question
**Q**: "Does turning on LangSmith tracing slow down or break your production API?"

**Answer**: Tracing is sent asynchronously from a background thread, so the request path is almost unaffected. If LangSmith is unreachable, the SDK logs a warning and the app continues. Still, at high volume you should sample traces, avoid giant payloads, and ensure the process flushes on shutdown (in short-lived serverless functions, wait for the tracer to finish, e.g. `LANGSMITH_TRACING_BACKGROUND=false` or call the client's flush). Never put tracing outcome in the critical path.

---

## ⚫ Interview Questions + Answers

Q1: What is a trace and what is a run? (Easy)
A1: A run is one step (LLM call, retriever, tool). A trace is the tree of all runs for one request.

Q2: Is LangSmith only for LangChain apps? (Easy)
A2: No. It works with any code through `@traceable`, `wrap_openai`, OpenTelemetry and its REST API.

Q3: What three things do you check first when an answer is wrong? (Medium)
A3: (1) The exact prompt that reached the model, (2) the retrieved context, (3) tool inputs/outputs and errors. This separates prompt bugs, retrieval bugs and tool bugs.

Q4: How do you use LangSmith to improve quality over time? (Medium)
A4: Collect feedback, save failing traces into a dataset, run offline evaluations on prompt/model variants as experiments, compare, ship the winner, monitor online.

Q5: What are the privacy and cost concerns of tracing at scale? (Hard)
A5: Traces contain user data, so mask PII, choose region/self-hosted deployment if required, set retention limits, and sample (e.g. 10%) because trace volume is billed. Large retrieved contexts inflate payload size, so truncate or hide them. Keep keys in secrets and give least-privilege API keys per environment.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multi-step chains, RAG or agents that are hard to debug
- You need cost and latency per step
- You want datasets and evals tied to real traces

❌ Avoid when:
- Strict data rules forbid sending data to a SaaS (use self-hosted or Langfuse self-host)
- A trivial single-call script

---

## 📊 Visual Diagram
```
 User ─► FastAPI ─► Chain / Graph
                      │  (each step emits a run, async)
                      ▼
   ┌──────────── LangSmith ────────────┐
   │ Trace: classify_hs        1.8s    │
   │  ├─ retrieve_tariff_notes 0.4s    │
   │  └─ ChatOpenAI   620 tok  1.3s    │
   │ Feedback 👍/👎  ► Dataset ► Evals │
   │ Dashboards / Alerts               │
   └───────────────────────────────────┘
```

---

## 💰 Cost Impact
- Tracing itself uses no LLM tokens, but it shows token usage per run, which is how you find waste (e.g. a 3,000-token system prompt on every call). Free tier covers small projects; paid plans bill by trace volume and retention.
- Optimise: sample production traces, short retention for routine traces and long for flagged ones, trim big payloads, and use the token and cost columns to find the top 3 expensive steps.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Trace | All steps of one request | एक request के सभी steps |
| Run | One step in a trace | Trace का एक step |
| Project | Folder grouping traces | Traces का group/folder |
| Dataset | Saved test examples | सहेजे हुए test examples |
| Feedback | Score/comment on a run | Run पर score/comment |
| @traceable | Decorator that logs a function | Function को log करने वाला decorator |

---

## ⚡ 3-Line Summary
English: LangSmith records every step of an LLM request as a trace, with tokens, cost, latency and errors. It also holds datasets, evaluations, prompts and monitoring. Set three env vars for LangChain apps, or use `@traceable` for any other code.
Hindi: LangSmith LLM request के हर step को trace के रूप में record करता है, tokens, cost, latency और errors के साथ। इसमें datasets, evaluations, prompts और monitoring भी हैं। LangChain apps में तीन env vars काफ़ी हैं, बाकी code में `@traceable` लगाओ।

---

## ➡️ Next Topic
**418. LangSmith Setup** — account, API key, environment variables and a first traced call.
