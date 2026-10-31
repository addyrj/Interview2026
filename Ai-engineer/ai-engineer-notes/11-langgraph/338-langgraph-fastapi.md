---

# 338. LangGraph + FastAPI
# हिंदी में: LangGraph + FastAPI

---

## 🔵 Simple Definition (English)
FastAPI is the web layer and LangGraph is the brain. You compile the graph once when the server starts (using FastAPI's `lifespan`), keep it on `app.state`, and each HTTP request calls `ainvoke` or `astream` with its own `thread_id`. The API validates input with Pydantic, handles errors and auth, and returns clean JSON.

## 🔵 सरल परिभाषा (Hindi)
FastAPI web layer है और LangGraph दिमाग। Server शुरू होते समय graph को एक बार compile करते हैं (FastAPI के `lifespan` से), उसे `app.state` में रखते हैं, और हर HTTP request अपने `thread_id` के साथ `ainvoke` या `astream` call करती है। API Pydantic से input validate करती है, errors और auth संभालती है, और साफ़ JSON लौटाती है।

---

## 🔴 Problem it Solves
A graph in a notebook is not a product. Teams build the graph inside each request (slow, loses memory), share one global mutable state between users (data leaks), block the event loop with sync calls, or return raw stack traces. A clear integration pattern solves lifecycle (build once), isolation (one thread per user), concurrency (async) and safety (validation, timeouts, error mapping).

## 🔴 यह क्यों बना? (Hindi)
Notebook में चलने वाला graph product नहीं है। Teams हर request में graph बना देती हैं (धीमा, memory खो जाती है), users के बीच एक global mutable state share करती हैं (data leak), sync calls से event loop block कर देती हैं, या raw stack trace लौटा देती हैं। साफ़ integration pattern lifecycle (एक बार build), isolation (हर user का अलग thread), concurrency (async) और safety (validation, timeout, error mapping) हल करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define State + nodes + build the graph in a function build_graph(checkpointer)
Step 2 → In lifespan(): create the checkpointer, compile, store in app.state.graph
Step 3 → Request arrives -> Pydantic validates the body
Step 4 → Auth gives user_id -> thread_id = f"{user_id}:{session_id}"
Step 5 → await graph.ainvoke(input, config={"configurable": {"thread_id": ...}, "recursion_limit": N})
Step 6 → Map exceptions: timeout -> 504, bad input -> 422, recursion -> 508, other -> 500
Step 7 → Return a small response model (answer + usage), never the whole raw state
Step 8 → On shutdown, lifespan closes DB pools
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → State + nodes + graph को build_graph(checkpointer) function में बनाओ
Step 2 → lifespan() में checkpointer बनाओ, compile करो, app.state.graph में रखो
Step 3 → Request आती है -> Pydantic body validate करता है
Step 4 → Auth से user_id मिलता है -> thread_id = f"{user_id}:{session_id}"
Step 5 → await graph.ainvoke(input, config={"configurable": {"thread_id": ...}, "recursion_limit": N})
Step 6 → Exceptions map करो: timeout -> 504, bad input -> 422, recursion -> 508, बाकी -> 500
Step 7 → छोटा response model लौटाओ (answer + usage), पूरी raw state नहीं
Step 8 → Shutdown पर lifespan DB pools बंद करता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: `POST /classify` takes `{product, session_id}`, runs the classification graph for the authenticated officer, and returns `{hs_code, confidence}`. `POST /classify/stream` streams progress. `GET /sessions/{id}` reads the saved state with `get_state`. **Zomato AI**: `POST /support/chat` with `thread_id = user_id:order_id`, so a customer's refund chat survives app restarts.

## 🟡 Real Example Hindi mein
**Tariff System**: `POST /classify` में `{product, session_id}` आता है, authenticated officer के लिए classification graph चलता है, और `{hs_code, confidence}` लौटता है। `POST /classify/stream` progress stream करता है। `GET /sessions/{id}` `get_state` से saved state पढ़ता है। **Zomato AI**: `POST /support/chat` में `thread_id = user_id:order_id`, इसलिए customer की refund chat app restart के बाद भी बनी रहती है।

---

## 💻 Code Example — Basic
```python
# FastAPI + LangGraph in one file - runs offline with TestClient (pip install fastapi httpx langgraph)
from typing import TypedDict  # state typing

from fastapi import FastAPI  # web framework
from fastapi.testclient import TestClient  # in-process HTTP client for demo/tests
from langgraph.graph import END, START, StateGraph  # graph API
from pydantic import BaseModel  # request/response models


class State(TypedDict):  # graph state
    product: str  # input
    hs_code: str  # output


def classify(state: State) -> dict[str, str]:  # sync node (LLM call would go here)
    return {"hs_code": "8517.13" if "phone" in state["product"].lower() else "0000.00"}  # fake rule


builder = StateGraph(State)  # builder
builder.add_node("classify", classify)  # node
builder.add_edge(START, "classify")  # entry
builder.add_edge("classify", END)  # exit
graph = builder.compile()  # compile ONCE at import time (module level)

app = FastAPI()  # app


class In(BaseModel):  # request body
    product: str


class Out(BaseModel):  # response body
    hs_code: str


@app.post("/classify", response_model=Out)  # route
async def classify_route(body: In) -> Out:  # async handler
    result = await graph.ainvoke({"product": body.product, "hs_code": ""})  # ainvoke runs sync nodes in a thread
    return Out(hs_code=result["hs_code"])  # small typed response


client = TestClient(app)  # call the app without starting a server
resp = client.post("/classify", json={"product": "Apple Phone"})  # HTTP POST
print(resp.status_code, resp.json())  # 200 {'hs_code': '8517.13'}
print(client.post("/classify", json={}).status_code)  # 422 -> Pydantic rejected the bad body
```

## 💻 Code Example — Advanced
```python
# Production shape: lifespan, checkpointer, thread isolation, timeout, error mapping
import asyncio  # timeout
import logging  # logs
from contextlib import asynccontextmanager  # lifespan helper
from typing import Annotated, AsyncIterator, TypedDict  # typing

from fastapi import Depends, FastAPI, Header, HTTPException  # web
from fastapi.testclient import TestClient  # demo client
from langgraph.checkpoint.memory import MemorySaver  # swap for Postgres in production
from langgraph.errors import GraphRecursionError  # loop protection error
from langgraph.graph import END, START, StateGraph  # graph API
from pydantic import BaseModel, Field  # validation

log = logging.getLogger("tariff.api")  # logger


class State(TypedDict):  # state
    product: str
    hs_code: str
    calls: int


async def classify(state: State) -> dict[str, object]:  # async node
    await asyncio.sleep(0)  # LLM placeholder
    if state["product"] == "boom":  # simulate an upstream failure
        raise RuntimeError("llm exploded")
    return {"hs_code": "8517.13", "calls": state.get("calls", 0) + 1}


def build_graph(checkpointer: MemorySaver):  # factory keeps tests easy
    b = StateGraph(State)
    b.add_node("classify", classify)
    b.add_edge(START, "classify")
    b.add_edge("classify", END)
    return b.compile(checkpointer=checkpointer)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # runs at startup and shutdown
    app.state.graph = build_graph(MemorySaver())  # build once, share across requests
    yield  # app serves requests here
    log.info("shutdown: close pools here")  # cleanup hook


app = FastAPI(lifespan=lifespan)  # attach lifespan


class In(BaseModel):  # validated input
    product: str = Field(min_length=2, max_length=200)  # bounds protect tokens and cost
    session_id: str = Field(min_length=1, max_length=64)


async def current_user(x_user: Annotated[str | None, Header()] = None) -> str:  # toy auth dependency
    if not x_user:
        raise HTTPException(status_code=401, detail="missing X-User")  # real apps verify a JWT here
    return x_user


@app.post("/classify")
async def classify_route(body: In, user: Annotated[str, Depends(current_user)]) -> dict[str, object]:
    cfg = {"configurable": {"thread_id": f"{user}:{body.session_id}"}, "recursion_limit": 10}  # isolate per user
    try:
        out = await asyncio.wait_for(  # hard timeout
            app.state.graph.ainvoke({"product": body.product, "hs_code": "", "calls": 0}, cfg), timeout=20
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="graph timed out")
    except GraphRecursionError:
        raise HTTPException(status_code=508, detail="graph loop detected")
    except Exception:  # never leak internals
        log.exception("graph failure")
        raise HTTPException(status_code=500, detail="internal error")
    return {"hs_code": out["hs_code"], "calls": out["calls"]}


if __name__ == "__main__":
    with TestClient(app) as c:  # context manager triggers lifespan
        h = {"X-User": "officer1"}
        print(c.post("/classify", json={"product": "phone", "session_id": "s1"}, headers=h).json())
        print(c.post("/classify", json={"product": "phone", "session_id": "s1"}).status_code)  # 401
        print(c.post("/classify", json={"product": "boom", "session_id": "s1"}, headers=h).status_code)  # 500
```

---

## 🟠 FastAPI Integration
The whole topic is the integration; the key rules:

```python
# 1. Compile once (lifespan), never per request.
# 2. Use async nodes + ainvoke/astream so the event loop is never blocked.
# 3. thread_id = authenticated user + session (never trust a raw client id).
# 4. Validate input size (max_length) to cap tokens.
# 5. Return a response_model, not the raw state.
# 6. Stream with StreamingResponse (see topic 337) and stop on disconnect.
# 7. Keep secrets (API keys) in environment variables, not in code.
@app.get("/sessions/{session_id}")  # read saved state of a thread
async def get_session(session_id: str, user: Annotated[str, Depends(current_user)]) -> dict[str, object]:
    snap = await app.state.graph.aget_state({"configurable": {"thread_id": f"{user}:{session_id}"}})  # only this user's thread
    return {"values": snap.values}  # state values saved by the checkpointer
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph graphs are LangChain `Runnable`s, so they plug into `langserve`-style serving or any custom FastAPI route. LangSmith tracing turns on with environment variables (`LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY`) and traces every request automatically; add `config={"tags": [...], "metadata": {"user": user}}` to make traces searchable. For production persistence use `AsyncPostgresSaver` created inside `lifespan`.

```python
# Pass tags and metadata so each API call is traceable in LangSmith
cfg = {
    "configurable": {"thread_id": "officer1:s1"},  # memory key
    "tags": ["tariff-api"],  # searchable tag
    "metadata": {"user": "officer1", "route": "/classify"},  # extra trace info
}
# result = await app.state.graph.ainvoke(inp, cfg)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Building the graph inside the request handler
✅ Correct: Build in `lifespan`/module scope and reuse.

```python
# Wrong - recompiles on every request, and MemorySaver() is new each time so memory is lost
@app.post("/chat")
async def chat(body: In):
    graph = build_graph(MemorySaver())
    return await graph.ainvoke(...)

# Right
@app.post("/chat")
async def chat(body: In):
    return await app.state.graph.ainvoke(...)
```

❌ Mistake 2: Blocking the event loop with sync `invoke` in an `async def` route
✅ Correct: Use `ainvoke`/`astream`.

```python
# Wrong - freezes ALL requests while one LLM call runs
@app.post("/chat")
async def chat(body: In):
    return graph.invoke(...)

# Right
@app.post("/chat")
async def chat(body: In):
    return await graph.ainvoke(...)
```

---

## 🧠 Tricky Interview Question

**Q**: "You deploy with 4 uvicorn workers and `MemorySaver`. Users complain the bot sometimes remembers them and sometimes doesn't. Why?"

**Answer**: Each worker is a separate process with its own in-RAM `MemorySaver`. A user's first request may land on worker 1 (memory saved there) and the next on worker 3 (no memory). Restarts also wipe memory. Use a shared persistent checkpointer (Postgres or Redis), keep the app stateless, and keep `thread_id` stable per user session. Sticky sessions would be a fragile workaround.

---

## ⚫ Interview Questions + Answers

Q1: Where should you compile the graph in a FastAPI app? (Easy)
A1: Once at startup (lifespan or module level), stored on `app.state`, and reused for all requests.

Q2: Why use `ainvoke` instead of `invoke` in async routes? (Easy)
A2: `invoke` is blocking and freezes the event loop; `ainvoke` awaits without blocking, so other requests continue.

Q3: How do you isolate users' conversations? (Medium)
A3: Build `thread_id` from the authenticated user id plus a session id, never from an unchecked client field, and optionally verify ownership before `get_state`.

Q4: How do you protect the endpoint from runaway cost? (Medium)
A4: Input length limits, `max_tokens` on the LLM, `recursion_limit`, `asyncio.wait_for` timeouts, per-user rate limiting, and budget alerts based on token usage logged per request.

Q5: Design a production deployment for the tariff API handling 200 requests/second. (Hard)
A5: Stateless FastAPI pods behind a load balancer (several workers each), `AsyncPostgresSaver` with a connection pool (or Redis for hot threads), async nodes, a global semaphore to respect LLM rate limits, retries with backoff for 429/5xx, response caching for repeated product queries, streaming endpoint for UX, structured logs + LangSmith tracing, readiness probes that check the DB, and autoscaling on queue depth/latency. Load test to find the LLM provider rate-limit ceiling first, because that is usually the real bottleneck.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Serving graphs to web/mobile clients
- You need custom auth, validation and business logic around the graph
- You want your own deployment control

❌ Avoid when:
- You only need a prototype with built-in endpoints (LangGraph Platform/`langgraph dev` gives a server for free, see 339-342)
- The graph is a one-off batch script (just run it)

---

## 📊 Visual Diagram
```
 Client ──HTTPS──► FastAPI
                     │ 1. Pydantic validate
                     │ 2. Auth -> user_id
                     │ 3. thread_id = user:session
                     ▼
              app.state.graph  (compiled once in lifespan)
                     │ ainvoke / astream
                     ▼
        ┌─ nodes (async) ─► LLM / tools / DB
        └─ checkpointer ──► Postgres (shared by all workers)
                     │
                     ▼
        response_model JSON  (+ errors mapped to 4xx/5xx)
```

---

## 💰 Cost Impact
- The API layer is free; cost comes from graph runs. Validation (`max_length=200`) caps input tokens: 200 chars is about 50 tokens.
- A retry storm is a cost bug: a client that retries a 504 three times triples the bill. Use idempotency keys and caching.
- Optimise: cache identical requests (hit rate of 30% cuts that share of LLM spend), set `max_tokens`, rate-limit per user, use a cheap model for simple routes, log `usage_metadata` per request to build per-user cost dashboards.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| lifespan | Startup/shutdown hook in FastAPI | Startup/shutdown hook |
| app.state | Place to keep shared objects | साझा objects रखने की जगह |
| ainvoke | Async run of a graph | Graph का async run |
| thread_id | Conversation key | Conversation की key |
| response_model | Typed response schema | Typed response schema |
| Idempotency key | Prevents duplicate processing | Duplicate रोकने की key |

---

## ⚡ 3-Line Summary
English: Compile the graph once in `lifespan`, call it with `ainvoke`/`astream`, and give each user their own `thread_id`. Validate input, set timeouts and a recursion limit, and map errors to proper HTTP codes. Use a shared database checkpointer when running several workers.
Hindi: Graph को `lifespan` में एक बार compile करो, `ainvoke`/`astream` से चलाओ, और हर user को अलग `thread_id` दो। Input validate करो, timeout और recursion limit लगाओ, और errors को सही HTTP codes में बदलो। कई workers हों तो shared database checkpointer use करो।

---

## ➡️ Next Topic
**339. LangGraph Deployment** — Docker, `langgraph.json`, environments, scaling and persistence in production.
