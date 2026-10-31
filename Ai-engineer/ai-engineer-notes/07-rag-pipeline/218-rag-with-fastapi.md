---

# 218. RAG with FastAPI
# हिंदी में: RAG with FastAPI

---

## 🔵 Simple Definition (English)
This topic puts the whole RAG pipeline (retrieve, rerank, build prompt, generate) behind a FastAPI service with typed requests and responses, shared clients created at startup, timeouts, error handling, health checks and token usage reporting.

## 🔵 सरल परिभाषा (Hindi)
इस topic में पूरी RAG pipeline (retrieve, rerank, prompt बनाना, generate) को FastAPI service के पीछे रखा जाता है: typed requests/responses, startup पर बने shared clients, timeouts, error handling, health checks और token usage reporting के साथ।

---

## 🔴 Problem it Solves
A notebook RAG demo is not a service. Real traffic needs concurrency (async), validation, one shared DB/LLM client instead of one per request, graceful failures (502/504 instead of crashes), auth, rate limits and observability. FastAPI provides these building blocks.

## 🔴 यह क्यों बना? (Hindi)
Notebook का RAG demo service नहीं है। असली traffic को concurrency (async), validation, हर request पर नए की जगह एक shared DB/LLM client, graceful failures (crash की जगह 502/504), auth, rate limits और observability चाहिए। FastAPI ये building blocks देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Startup (lifespan): create AsyncOpenAI client, vector DB client, reranker
Step 2 → Request model validates input (pydantic: length limits, top_k bounds)
Step 3 → Dependency injection gives the route its shared services
Step 4 → Route runs: embed query -> vector search -> rerank -> pack context
Step 5 → LLM call with timeout; map errors to proper HTTP codes
Step 6 → Response model: answer, sources, usage, latency_ms, request_id
Step 7 → Shutdown (lifespan): close clients; /health and /ready endpoints exist
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Startup (lifespan): AsyncOpenAI client, vector DB client, reranker बनाओ
Step 2 → Request model input validate करता है (pydantic: length limit, top_k bounds)
Step 3 → Dependency injection route को shared services देता है
Step 4 → Route चलता है: query embed -> vector search -> rerank -> context pack
Step 5 → Timeout के साथ LLM call; errors को सही HTTP codes में map करो
Step 6 → Response model: answer, sources, usage, latency_ms, request_id
Step 7 → Shutdown (lifespan): clients बंद करो; /health और /ready endpoints
```

---

## 🟡 Real World Example
**Tariff Classification System**: `POST /v1/classify` receives `{product_description, country}`. The service retrieves tariff chunks filtered by country, reranks, generates the HS code with citations, logs tokens per request, and returns in under 3 seconds. A gateway in front adds auth and rate limits. **Zomato**: support-bot API with per-user rate limit. **Amazon**: "ask about product" endpoint with caching by product id.

## 🟡 Real Example Hindi mein
**Tariff System**: `POST /v1/classify` को `{product_description, country}` मिलता है। Service country के filter से tariff chunks लाती है, rerank करती है, citations के साथ HS code बनाती है, हर request के tokens log करती है और 3 सेकंड से कम में जवाब देती है। आगे का gateway auth और rate limit देता है। **Zomato**: per-user rate limit वाला support-bot API। **Amazon**: product id से cache होने वाला "product के बारे में पूछो" endpoint।

---

## 💻 Code Example — Basic
```python
# Basic RAG API with an in-memory retriever and a fake LLM (needs: pip install fastapi uvicorn).
# Run: uvicorn main:app --reload   |   Test: POST /ask {"question": "smartphone duty"}
from fastapi import FastAPI  # web framework
from pydantic import BaseModel, Field  # validation

app = FastAPI(title="Tariff RAG (basic)")  # app

KB: list[str] = [  # tiny knowledge base
    "Smartphones HS 8517.13 duty 20 percent.",
    "Laptops HS 8471.30 duty 0 percent.",
]


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)  # validated input


class AskResponse(BaseModel):
    answer: str  # answer text
    sources: list[str]  # chunks used


def retrieve(question: str, k: int = 1) -> list[str]:
    """Rank KB by word overlap."""
    q = set(question.lower().split())  # query words
    ranked = sorted(KB, key=lambda d: len(q & set(d.lower().split())), reverse=True)  # best first
    return ranked[:k]  # top-k


def fake_generate(question: str, chunks: list[str]) -> str:
    """Pretend LLM."""
    return f"Based on the tariff: {chunks[0]}" if chunks else "NOT_FOUND"  # simple


@app.post("/ask", response_model=AskResponse)  # route
async def ask(req: AskRequest) -> AskResponse:
    chunks = retrieve(req.question)  # retrieve
    return AskResponse(answer=fake_generate(req.question, chunks), sources=chunks)  # respond
```

## 💻 Code Example — Advanced
```python
# Production skeleton: lifespan-managed clients, DI, timeouts, error mapping, usage + request id.
import asyncio  # timeouts
import logging  # logs
import time  # latency
import uuid  # request ids
from contextlib import asynccontextmanager  # lifespan
from typing import Annotated, AsyncIterator  # typing

from fastapi import Depends, FastAPI, HTTPException, Request  # fastapi
from openai import APIConnectionError, AsyncOpenAI, RateLimitError  # openai errors
from pydantic import BaseModel, Field  # models

logger = logging.getLogger("rag_api")  # logger


class Services:
    """Holds shared, long-lived clients."""
    def __init__(self) -> None:
        self.llm = AsyncOpenAI(max_retries=2, timeout=20.0)  # shared client with SDK retries + timeout


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.services = Services()  # create once
    yield  # serve requests
    await app.state.services.llm.close()  # clean shutdown


app = FastAPI(title="Tariff RAG", lifespan=lifespan)  # app


def get_services(request: Request) -> Services:
    return request.app.state.services  # dependency provider


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)  # input limits
    top_k: int = Field(default=4, ge=1, le=10)  # bounded


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int


class AskResponse(BaseModel):
    request_id: str
    answer: str
    sources: list[str]
    usage: Usage
    latency_ms: int


async def retrieve_and_rerank(q: str, k: int) -> list[str]:
    await asyncio.sleep(0)  # replace with vector DB + reranker calls
    return ["Smartphones HS 8517.13 duty 20 percent."][:k]  # demo chunk


@app.get("/health")  # liveness
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/ask", response_model=AskResponse)  # main route
async def ask(req: AskRequest, svc: Annotated[Services, Depends(get_services)]) -> AskResponse:
    t0, rid = time.perf_counter(), uuid.uuid4().hex[:12]  # start timer + id
    chunks = await retrieve_and_rerank(req.question, req.top_k)  # retrieval
    if not chunks:  # nothing relevant
        raise HTTPException(status_code=404, detail="No relevant context found")  # clean 404
    ctx = "\n".join(f"[S{i}] {c}" for i, c in enumerate(chunks, 1))  # context
    try:  # LLM call
        resp = await asyncio.wait_for(svc.llm.chat.completions.create(
            model="gpt-4o-mini", temperature=0, max_tokens=300,
            messages=[{"role": "system", "content": "Answer only from context. Cite [S#]."},
                      {"role": "user", "content": f"<context>\n{ctx}\n</context>\nQ: {req.question}"}],
        ), timeout=25)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="LLM timeout")  # gateway timeout
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Upstream rate limit")  # pass the signal on
    except APIConnectionError:
        raise HTTPException(status_code=502, detail="LLM unreachable")  # bad gateway
    u = resp.usage  # usage
    logger.info("rid=%s tokens=%d", rid, u.total_tokens)  # log tokens
    return AskResponse(request_id=rid, answer=resp.choices[0].message.content or "", sources=chunks,
                       usage=Usage(prompt_tokens=u.prompt_tokens, completion_tokens=u.completion_tokens),
                       latency_ms=int((time.perf_counter() - t0) * 1000))
```

---

## 🟠 FastAPI Integration
This whole topic is the FastAPI integration. Key patterns to remember: `lifespan` for shared clients, `Depends` for injection, pydantic models for validation, `async def` for I/O, `BackgroundTasks` for logging, and `StreamingResponse` for streaming (topic 217).

```python
from fastapi import BackgroundTasks  # run work after the response


def log_usage(rid: str, tokens: int) -> None:
    print(f"usage rid={rid} tokens={tokens}")  # replace with DB/metrics write


# inside the route: background.add_task(log_usage, rid, u.total_tokens)  # does not delay the response
```

---

## 🔗 LangChain / LangGraph Connection
Compile the chain or graph once at startup and call `ainvoke` in the route. `langserve` and LangGraph Platform offer ready servers, but plain FastAPI gives full control.

```python
# At startup: app.state.graph = build_graph().compile()          # LangGraph compiled once
# In route:   result = await app.state.graph.ainvoke({"question": req.question})
# Per-user memory: config={"configurable": {"thread_id": user_id}} with a checkpointer
# Streaming:  async for ev in graph.astream(inputs, stream_mode="messages"): ...
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Creating a new client in every request
✅ Correct: Create once in lifespan.

```python
# Wrong: new connection pool per call
@app.post("/ask")
async def ask(q: str):
    client = AsyncOpenAI()
    ...

# Right: use app.state / Depends
async def ask(q: str, svc: Services = Depends(get_services)): ...
```

❌ Mistake 2: Blocking calls inside `async def`
✅ Correct: Use async clients or `asyncio.to_thread`.

```python
# Wrong: requests.post(...) or a sync vector DB call blocks every user
docs = sync_db.search(q)

# Right
docs = await asyncio.to_thread(sync_db.search, q)
```

---

## 🧠 Tricky Interview Question
**Q**: "Your RAG endpoint handles 5 req/s fine, but at 50 req/s latency explodes and 429s appear. Where do you look?"

**Answer**: Check (1) upstream LLM rate limits (TPM/RPM) because token budget, not CPU, is usually the bottleneck; add a queue/semaphore and retries with jitter; (2) blocking sync calls that stall the event loop; (3) too few workers or an undersized vector DB connection pool; (4) large contexts increasing tokens per request; (5) missing caches. Fixes: concurrency limits (semaphore), request-level caching, smaller context, model tiering, horizontal scaling with multiple Uvicorn workers, and backpressure via 429/Retry-After to clients.

---

## ⚫ Interview Questions + Answers

Q1: Why use `async def` for a RAG endpoint?
A1: Most of the time is spent waiting on network calls (vector DB, LLM). Async lets one worker serve many requests during those waits.

Q2: What is lifespan used for?
A2: Startup and shutdown logic: create and close shared resources like clients and models.

Q3: How do you validate input?
A3: Pydantic models with `Field` constraints (min/max length, bounds).

Q4: Which HTTP status codes do you map for LLM failures?
A4: 429 for upstream rate limits, 502 for connection failures, 504 for timeouts, 422 for invalid input, 404/200 with NOT_FOUND for no context.

Q5: How would you secure and observe a production RAG API?
A5: API key or JWT auth, per-tenant rate limits, input length caps and prompt-injection defences, PII redaction in logs, request ids and structured logs, metrics (latency per stage, tokens, cost, refusal rate), tracing (OpenTelemetry/LangSmith), health and readiness probes, and per-tenant data filtering at retrieval so users only see documents they may access.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Serving RAG to apps, UIs or other services
- You need typed contracts and docs (OpenAPI)
- High concurrency with I/O-bound calls

❌ Avoid when:
- A one-off script or batch job (run it directly)
- Heavy CPU/GPU inference inside the same process (separate it into a worker service)

---

## 📊 Visual Diagram
```
 Client ──► [Gateway: auth, rate limit] ──► FastAPI
                                             │ lifespan: shared clients
                                             ▼
                  ┌─ validate (pydantic) ─► retrieve ─► rerank ─► pack ─┐
                  │                                                     ▼
                  │                                              LLM (timeout)
                  ▼                                                     │
          400/422 errors      ◄── 429/502/504 mapping ◄─────────────────┘
                                             │
                          response {answer, sources, usage, latency_ms}
```

---

## 💰 Cost Impact
- API cost = LLM tokens per request x traffic. The service layer enables controls: input length caps, `max_tokens`, response caching, model routing, and per-tenant quotas.
- Example: 100K requests/day x 1,400 in + 150 out tokens on gpt-4o-mini = about $30 per day; a 30 percent cache hit rate saves about $9 per day.
- Optimise: log tokens per request, set budgets and alerts, cache by normalised question + corpus version, return 429 before spending tokens when a tenant is over quota.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Lifespan | Startup/shutdown hooks | शुरू/बंद होने की hooks |
| Dependency injection | Provide shared objects to routes | Routes को shared objects देना |
| Pydantic | Data validation library | Data validation library |
| Timeout | Max wait time | अधिकतम इंतज़ार |
| Request ID | Unique id per call for tracing | हर call की unique पहचान |

---

## ⚡ 3-Line Summary
English: Wrap the RAG pipeline in FastAPI with lifespan-managed clients, validated models, timeouts and clear HTTP error codes. Return answer, sources and token usage. Keep everything async and observable.
Hindi: RAG pipeline को FastAPI में लपेटो: lifespan से बने clients, validated models, timeouts और साफ़ HTTP error codes के साथ। Answer, sources और token usage लौटाओ। सब कुछ async और observable रखो।

---

## ➡️ Next Topic
**219. RAG with LangChain** — build the same pipeline with LCEL building blocks.
