---

# 328. RedisSaver
# हिंदी में: RedisSaver (Network पर Shared Fast Checkpointer)

---

## 🔵 Simple Definition (English)
`RedisSaver` is a LangGraph checkpointer that keeps graph state in Redis, a fast in-memory database that many servers can reach over the network. All pods share the same memory, reads and writes take about a millisecond, and keys can expire automatically with a TTL. Package: `langgraph-checkpoint-redis`. It needs a Redis with the JSON and Search modules (Redis Stack, or Redis 8+).

## 🔵 सरल परिभाषा (Hindi)
`RedisSaver` LangGraph का checkpointer है जो graph state को Redis में रखता है। Redis एक तेज़ in-memory database है जिसे कई servers network से use कर सकते हैं। सभी pods की memory एक ही होती है, read/write लगभग 1 millisecond में होता है, और TTL से keys अपने आप expire हो सकती हैं। Package: `langgraph-checkpoint-redis`। इसके लिए JSON और Search modules वाला Redis (Redis Stack या Redis 8+) चाहिए।

---

## 🔴 Problem it Solves
MemorySaver is lost on restart and is not shared. SqliteSaver is durable but has one writer and lives on one machine. A scaled API with 10 pods behind a load balancer needs one shared store with low latency. Chat memory is also temporary by nature (nobody needs a casual chat after 30 days), so automatic expiry (TTL) is a big plus. Redis fits this exactly.

## 🔴 यह क्यों बना? (Hindi)
MemorySaver restart पर खो जाता है और share नहीं होता। SqliteSaver durable है लेकिन एक ही writer और एक ही machine तक सीमित है। Load balancer के पीछे 10 pods वाली scaled API को कम latency वाला एक shared store चाहिए। Chat memory वैसे भी temporary होती है (30 दिन बाद किसी को पुरानी casual chat नहीं चाहिए), इसलिए automatic expiry (TTL) बड़ा फ़ायदा है। Redis इसी के लिए सही है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Run Redis Stack (docker run -p 6379:6379 redis/redis-stack-server)
Step 2 → pip install langgraph-checkpoint-redis
Step 3 → with RedisSaver.from_conn_string("redis://localhost:6379") as saver: saver.setup()
          (setup() creates the search indices ONCE)
Step 4 → app = graph.compile(checkpointer=saver)
Step 5 → app.invoke(input, {"configurable": {"thread_id": "case-1"}})
Step 6 → Each super-step stores the checkpoint as JSON keys in Redis, indexed by thread_id
Step 7 → ANY pod can load the same thread_id and continue
Step 8 → Optional TTL: ttl={"default_ttl": 60, "refresh_on_read": True} (minutes) deletes idle threads
Step 9 → Async code uses AsyncRedisSaver with `await saver.asetup()`
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Redis Stack चलाओ (docker run -p 6379:6379 redis/redis-stack-server)
Step 2 → pip install langgraph-checkpoint-redis
Step 3 → with RedisSaver.from_conn_string("redis://localhost:6379") as saver: saver.setup()
          (setup() search indices एक बार बनाता है)
Step 4 → app = graph.compile(checkpointer=saver)
Step 5 → app.invoke(input, {"configurable": {"thread_id": "case-1"}})
Step 6 → हर super-step में checkpoint Redis में JSON keys के रूप में thread_id के साथ save होता है
Step 7 → कोई भी pod वही thread_id load करके आगे चल सकता है
Step 8 → Optional TTL: ttl={"default_ttl": 60, "refresh_on_read": True} (minutes) idle threads हटा देता है
Step 9 → Async code में AsyncRedisSaver और `await saver.asetup()`
```

---

## 🟡 Real World Example
**Tariff Classification System**: The public "Check my product's duty" chat is served by 8 FastAPI pods. A visitor's first message hits pod 2 and the follow-up hits pod 5. With RedisSaver both pods read the same `thread_id`, so the conversation continues. A TTL of 24 hours removes abandoned chats, so Redis memory stays small. Long-lived analyst cases go to Postgres instead (a common hybrid).

**Zomato-style**: During lunch peak, a cart assistant needs sub-5 ms memory reads for millions of short sessions, and old sessions should vanish after an hour.

## 🟡 Real Example Hindi mein
**Tariff System**: Public "मेरे product की duty चेक करो" chat 8 FastAPI pods से चलती है। Visitor का पहला message pod 2 पर और अगला pod 5 पर जाता है। RedisSaver से दोनों pods वही `thread_id` पढ़ते हैं, इसलिए बातचीत चलती रहती है। 24 घंटे का TTL छोड़ी हुई chats हटा देता है, इसलिए Redis की memory छोटी रहती है। लंबे समय वाले analyst cases Postgres में रखे जाते हैं (आम hybrid)।

**Zomato-style**: Lunch peak में cart assistant को लाखों छोटे sessions के लिए 5 ms से कम में memory पढ़नी है, और पुराने sessions एक घंटे बाद अपने आप हट जाने चाहिए।

---

## 💻 Code Example — Basic
```python
# Basic: RedisSaver if Redis Stack is running, otherwise fall back to MemorySaver
# (so this file runs anywhere). Needs: pip install langgraph langgraph-checkpoint-redis
import operator                                           # list reducer
from contextlib import ExitStack                          # lets us keep the saver open conditionally
from typing import Annotated, Any, TypedDict              # type hints

from langgraph.checkpoint.memory import MemorySaver       # fallback saver
from langgraph.graph import END, START, StateGraph        # graph API


class State(TypedDict):                                   # state schema
    log: Annotated[list[str], operator.add]               # append-only history
    count: int                                            # number of runs


def step(state: State) -> dict:                           # one node
    n = len(state.get("log", [])) + 1                     # run number from stored history
    return {"log": [f"run-{n}"], "count": n}              # partial update


def make_saver(stack: ExitStack, url: str) -> Any:        # try Redis, else memory
    try:                                                  # Redis packages or server may be missing
        from langgraph.checkpoint.redis import RedisSaver     # import lazily
        saver = stack.enter_context(RedisSaver.from_conn_string(url))   # open connection
        saver.setup()                                     # create indices (safe to repeat)
        print("Using RedisSaver")                         # tell the user
        return saver                                      # real Redis saver
    except Exception as exc:                              # ImportError, ConnectionError, module missing
        print(f"Redis not available ({type(exc).__name__}); using MemorySaver")
        return MemorySaver()                              # same interface, in RAM


builder = StateGraph(State)                               # build graph
builder.add_node("step", step)                            # node
builder.add_edge(START, "step")                           # entry
builder.add_edge("step", END)                             # exit

with ExitStack() as stack:                                # closes Redis on exit
    saver = make_saver(stack, "redis://localhost:6379")   # choose saver
    app = builder.compile(checkpointer=saver)             # compile
    cfg = {"configurable": {"thread_id": "case-redis-1"}}  # thread key
    app.invoke({"log": []}, cfg)                          # first run
    print(app.invoke({"log": []}, cfg)["log"])            # ['run-1', 'run-2'] (with Redis: also after restart)
```

## 💻 Code Example — Advanced
```python
# Production style: AsyncRedisSaver + TTL + error handling + type hints
import asyncio                                            # async runtime
import logging                                            # logging
import operator                                           # reducer
import os                                                 # read REDIS_URL from the environment
from typing import Annotated, Any, TypedDict              # type hints

from langgraph.graph import END, START, StateGraph        # graph API

logger = logging.getLogger("tariff.redis")                # logger
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")   # 12-factor config

TTL_CONFIG: dict[str, Any] = {                            # expiry rules
    "default_ttl": 24 * 60,                               # minutes: delete idle threads after 24 hours
    "refresh_on_read": True,                              # each read extends the life of the thread
}


class ChatState(TypedDict):                               # state
    messages: Annotated[list[dict[str, str]], operator.add]   # chat messages
    hs_code: str                                          # last predicted code


async def classify(state: ChatState) -> dict[str, Any]:   # async node
    await asyncio.sleep(0)                                # placeholder for `await llm.ainvoke(...)`
    return {"hs_code": "8517.13",                         # fake HS code
            "messages": [{"role": "assistant", "content": "HS 8517.13"}]}   # fake reply


async def run_turn(app: Any, thread_id: str, text: str, retries: int = 2) -> dict[str, Any]:
    cfg = {"configurable": {"thread_id": thread_id}}      # key for this chat
    for attempt in range(retries + 1):                    # simple retry loop for network blips
        try:                                              # error handling
            return await app.ainvoke(                     # run graph + save checkpoint in Redis
                {"messages": [{"role": "user", "content": text}]}, cfg)
        except (ConnectionError, TimeoutError) as exc:    # transient Redis errors
            logger.warning("redis hiccup (%s), attempt %d", exc, attempt + 1)  # log
            await asyncio.sleep(0.2 * (attempt + 1))      # linear back-off
    raise RuntimeError("checkpoint store unavailable")    # give up after retries


async def main() -> None:                                 # demo (needs a running Redis Stack)
    from langgraph.checkpoint.redis.aio import AsyncRedisSaver   # async saver
    async with AsyncRedisSaver.from_conn_string(REDIS_URL, ttl=TTL_CONFIG) as saver:  # open + TTL
        await saver.asetup()                              # create indices once
        b = StateGraph(ChatState)                         # builder
        b.add_node("classify", classify)                  # node
        b.add_edge(START, "classify")                     # entry
        b.add_edge("classify", END)                       # exit
        app = b.compile(checkpointer=saver)               # compile
        out = await run_turn(app, "visitor-42", "Classify a smartphone")   # turn 1
        print(out["hs_code"])                             # 8517.13


if __name__ == "__main__":                                # entry
    asyncio.run(main())                                   # run
```

---

## 🟠 FastAPI Integration
Open `AsyncRedisSaver` once in the lifespan, run `asetup()`, and share the compiled graph through `app.state`. Because Redis is shared, you can scale uvicorn workers and pods freely. Use the session id as `thread_id` and give anonymous sessions a TTL.

```python
# FastAPI + AsyncRedisSaver (lifespan)
import operator                                                  # reducer
import os                                                        # env config
from contextlib import asynccontextmanager                       # lifespan helper
from typing import Annotated, TypedDict                          # type hints

from fastapi import FastAPI, HTTPException, Request              # web framework
from langgraph.checkpoint.redis.aio import AsyncRedisSaver       # async Redis saver
from langgraph.graph import END, START, StateGraph               # graph API
from pydantic import BaseModel, Field                            # models


class S(TypedDict):                                              # state
    log: Annotated[list[str], operator.add]                      # history
    answer: str                                                  # answer


async def node(state: S) -> dict:                                # node
    return {"answer": f"{len(state['log'])} messages in this chat"}   # fake logic


@asynccontextmanager                                             # startup/shutdown
async def lifespan(app: FastAPI):                                # FastAPI lifespan
    url = os.getenv("REDIS_URL", "redis://localhost:6379")       # config
    async with AsyncRedisSaver.from_conn_string(url, ttl={"default_ttl": 1440}) as saver:
        await saver.asetup()                                     # indices
        b = StateGraph(S)                                        # graph
        b.add_node("n", node)                                    # node
        b.add_edge(START, "n")                                   # entry
        b.add_edge("n", END)                                     # exit
        app.state.graph = b.compile(checkpointer=saver)          # share
        yield                                                    # serve


app = FastAPI(title="Tariff Chat (Redis)", lifespan=lifespan)    # app


class ChatIn(BaseModel):                                         # body
    session_id: str = Field(min_length=8, max_length=64)         # thread id
    message: str = Field(min_length=1, max_length=2000)          # text


@app.post("/chat")                                               # route
async def chat(body: ChatIn, request: Request) -> dict[str, str]:   # handler
    cfg = {"configurable": {"thread_id": body.session_id}}       # key
    try:                                                         # errors
        out = await request.app.state.graph.ainvoke({"log": [body.message]}, cfg)   # run
    except Exception as exc:                                     # failure
        raise HTTPException(503, "memory store unavailable") from exc   # 503 = try later
    return {"answer": out["answer"]}                             # response
```

---

## 🔗 LangChain / LangGraph Connection
RedisSaver is one of several `BaseCheckpointSaver` implementations (Memory, Sqlite, Postgres, Redis, plus managed LangGraph Platform storage). The package also contains `RedisStore` for long-term cross-thread memory with optional vector search. Graph code never changes between savers.

```python
# Swap the saver without touching graph logic
from langgraph.checkpoint.redis import RedisSaver             # Redis saver

with RedisSaver.from_conn_string("redis://localhost:6379") as saver:   # open
    saver.setup()                                             # one-time indices
    agent = builder.compile(checkpointer=saver)               # same compile call as other savers
    agent.invoke({"log": ["hello"]}, {"configurable": {"thread_id": "t1"}})   # run
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using plain Redis without the JSON and Search modules
✅ Correct: use Redis Stack (or Redis 8+) otherwise `setup()` fails.

```python
# Wrong — vanilla redis:7 image has no RedisJSON / RediSearch
#   docker run -p 6379:6379 redis:7     -> setup() raises "unknown command"

# Right
#   docker run -p 6379:6379 redis/redis-stack-server:latest
```

❌ Mistake 2: Forgetting `setup()` / `asetup()`
✅ Correct: call it once at startup (or in a migration job).

```python
# Wrong
with RedisSaver.from_conn_string(url) as saver:
    app = builder.compile(checkpointer=saver)       # indices missing -> errors on first use

# Right
with RedisSaver.from_conn_string(url) as saver:
    saver.setup()                                   # create indices
    app = builder.compile(checkpointer=saver)
```

❌ Mistake 3: No TTL, no memory limit
✅ Correct: set a TTL and a Redis `maxmemory` policy, or Redis grows until it crashes.

---

## 🧠 Tricky Interview Question

**Q**: "After a Redis restart, half of your users' chats are gone, even though you used RedisSaver. Is this a LangGraph bug?"

**Answer**: No. Redis is an in-memory store. Unless persistence is configured (RDB snapshots and/or AOF), a restart loses data, and an eviction policy such as `allkeys-lru` can also remove checkpoints under memory pressure. Decide what is acceptable: for casual chats it is fine (with TTL); for legal or audit trails use Postgres or enable AOF with `appendfsync everysec` and replicas. Also check that TTL with `refresh_on_read` is not deleting threads you expected to keep.

---

## ⚫ Interview Questions + Answers

Q1: Why choose RedisSaver for production? (Easy)
A1: It is shared across pods, very fast, and supports automatic expiry. Good for high-traffic chat where memory is temporary.

Q2: What does `setup()` do? (Easy)
A2: It creates the Redis search indices the saver needs to find checkpoints by thread and checkpoint id. It is run once at startup or migration, not per request.

Q3: RedisSaver vs PostgresSaver, how do you choose? (Medium)
A3: Redis: lowest latency, TTL, ephemeral conversations, but memory is expensive and durability must be configured. Postgres: durable by default, easy backup, SQL queries and audit, slightly slower. Many teams use Redis for hot chat sessions and Postgres for long-lived or regulated cases.

Q4: How does TTL work, and what is `refresh_on_read`? (Medium)
A4: `default_ttl` (minutes) sets an expiry on checkpoint keys. With `refresh_on_read=True` each read of a thread resets the timer, so only truly idle threads expire. This stops the store growing forever.

Q5: A pod crashes in the middle of a graph run. What does Redis give you and what must you design for? (Hard)
A5: Checkpoints are saved after each super-step, and nodes that finished in a step have their writes stored. Another pod can resume the same `thread_id` from the last checkpoint with `invoke(None, config)`. You must make nodes idempotent (an LLM call or payment may run twice), add a request id for deduplication, use a distributed lock or one-request-per-thread rule so two pods do not advance the same thread at once, and set client timeouts and retries for Redis itself.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many pods or workers need shared memory
- Low latency matters (chat, assistants)
- Conversations can expire (TTL)

❌ Avoid when:
- You need strict durability or audit history (prefer Postgres)
- You cannot run Redis Stack / Redis 8 modules
- Very large states make RAM too expensive

---

## 📊 Visual Diagram
```
   Load Balancer
   ┌────┬────┬────┐
   ▼    ▼    ▼    ▼
 Pod1 Pod2 Pod3 Pod4      (FastAPI + same compiled graph)
   └────┴──┬─┴────┘
           │  thread_id="visitor-42"
           ▼
   ┌──────────────────────────┐
   │  Redis Stack             │
   │  checkpoint:visitor-42:* │  <- JSON docs + search index
   │  TTL: 24h (refresh read) │
   └──────────────────────────┘
 Any pod can continue any thread. Redis down => no memory (use retries/fallback)
```

---

## 💰 Cost Impact
Redis costs infrastructure money, not tokens: RAM is the expensive resource. A checkpoint of 20 KB per thread times 1 million active threads is about 20 GB. Managed Redis at that size can cost hundreds of dollars a month. Optimise by keeping state small (store ids and short summaries, not full PDFs), setting TTL, compressing large fields, and trimming message history.

Token side: persistent memory makes it easy to re-send long history to the LLM. Example: 30 turns at 300 tokens means about 9,000 input tokens per call. Use `trim_messages` or rolling summaries so each call stays near 1,500 tokens, saving about 80 percent of input cost.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RedisSaver | Checkpointer storing state in Redis | Redis में state रखने वाला saver |
| AsyncRedisSaver | Async variant | Async variant |
| TTL | Time before a key auto-deletes | Key अपने आप हटने का समय |
| Redis Stack | Redis with JSON + Search modules | JSON + Search वाला Redis |
| setup() | One-time index creation | एक बार index बनाना |
| AOF / RDB | Redis persistence methods | Redis की durability के तरीके |
| Idempotent | Safe to run twice | दो बार चलने पर भी सुरक्षित |

---

## ⚡ 3-Line Summary
English: RedisSaver stores LangGraph checkpoints in Redis so every pod shares one fast memory. Run `setup()` once and set a TTL so old chats expire. Redis is in-memory, so configure persistence or use Postgres if you need strict durability.
Hindi: RedisSaver LangGraph checkpoints को Redis में रखता है, जिससे सभी pods एक तेज़ shared memory use करते हैं। `setup()` एक बार चलाओ और TTL लगाओ ताकि पुरानी chats हट जाएँ। Redis in-memory है, इसलिए पक्की durability चाहिए तो persistence configure करो या Postgres लो।

---

## ➡️ Next Topic
**329. Human in the Loop (HITL)** — now that state is saved, we can pause a graph for human approval and resume it later.
