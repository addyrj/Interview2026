---

# 327. SqliteSaver
# हिंदी में: SqliteSaver (File पर Checkpoint Save करना)

---

## 🔵 Simple Definition (English)
`SqliteSaver` is a LangGraph checkpointer that writes graph state into a SQLite database file. Memory survives process restarts, and no separate database server is needed. It is the natural step after `MemorySaver` for local apps, small internal tools and single-server deployments. Package: `langgraph-checkpoint-sqlite`.

## 🔵 सरल परिभाषा (Hindi)
`SqliteSaver` LangGraph का checkpointer है जो graph state को SQLite database file में लिखता है। Process restart होने पर भी memory बची रहती है, और अलग database server की ज़रूरत नहीं होती। Local apps, छोटे internal tools और single-server deployment के लिए `MemorySaver` के बाद यही अगला कदम है। Package: `langgraph-checkpoint-sqlite`।

---

## 🔴 Problem it Solves
`MemorySaver` loses everything when Python exits. A tariff officer who closed the laptop on Friday expects the case to be open on Monday. Running Postgres just for a small tool is too much work. SQLite gives durable storage in one file, with ACID guarantees, and Python already ships the `sqlite3` module.

## 🔴 यह क्यों बना? (Hindi)
`MemorySaver` Python बंद होते ही सब खो देता है। Tariff officer ने शुक्रवार को laptop बंद किया, तो सोमवार को case खुला मिलना चाहिए। छोटे tool के लिए Postgres चलाना ज़्यादा मेहनत है। SQLite एक file में durable storage देता है, ACID guarantee के साथ, और Python में `sqlite3` पहले से मौजूद है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install langgraph-checkpoint-sqlite  (async also needs aiosqlite)
Step 2 → with SqliteSaver.from_conn_string("tariff.db") as saver:   (opens the file, creates tables)
Step 3 → app = graph.compile(checkpointer=saver)
Step 4 → app.invoke(input, {"configurable": {"thread_id": "case-1"}})
Step 5 → After every super-step a row is INSERTed into the `checkpoints` table (state blob) and
         the `writes` table (pending writes of nodes)
Step 6 → Process restarts → open the same file → same thread_id → state is loaded and continues
Step 7 → Async apps use AsyncSqliteSaver + `async with` + ainvoke/astream
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → pip install langgraph-checkpoint-sqlite  (async के लिए aiosqlite भी चाहिए)
Step 2 → with SqliteSaver.from_conn_string("tariff.db") as saver:   (file खुलती है, tables बनते हैं)
Step 3 → app = graph.compile(checkpointer=saver)
Step 4 → app.invoke(input, {"configurable": {"thread_id": "case-1"}})
Step 5 → हर super-step के बाद `checkpoints` table में state की row और
         `writes` table में nodes के pending writes insert होते हैं
Step 6 → Restart के बाद वही file + वही thread_id = state वापस load होकर आगे चलती है
Step 7 → Async apps में AsyncSqliteSaver + `async with` + ainvoke/astream
```

---

## 🟡 Real World Example
**Tariff Classification System**: An internal tool for 5 customs analysts runs on one VM. Each case is a `thread_id` like `case-4021`. The analyst classifies an item, closes the browser, the service restarts after a patch, and on Monday the case is still there with its full history. One file `tariff_checkpoints.db` is easy to back up with a simple `cp`.

**Amazon-style**: A seller-support assistant on an on-prem box keeps each ticket conversation in SQLite so the agent can continue the next day.

## 🟡 Real Example Hindi mein
**Tariff System**: 5 customs analysts का internal tool एक VM पर चलता है। हर case एक `thread_id` है जैसे `case-4021`। Analyst item classify करके browser बंद करता है, patch के बाद service restart होती है, फिर भी सोमवार को case पूरी history के साथ मौजूद है। एक file `tariff_checkpoints.db` को `cp` से backup करना आसान है।

**Amazon-style**: On-prem box पर seller-support assistant हर ticket की बातचीत SQLite में रखता है ताकि agent अगले दिन वहीं से शुरू करे।

---

## 💻 Code Example — Basic
```python
# Basic: SqliteSaver persists memory in a file (offline, no API key)
import operator                                        # list reducer
import os                                              # to delete the demo db afterwards
import tempfile                                        # safe temp folder for the demo file
from typing import Annotated, TypedDict                # type hints

from langgraph.checkpoint.sqlite import SqliteSaver    # sync SQLite checkpointer
from langgraph.graph import END, START, StateGraph    # graph API


class State(TypedDict):                                # state schema
    log: Annotated[list[str], operator.add]            # appended on every run
    count: int                                         # how many runs so far


def step(state: State) -> dict:                        # one simple node
    n = len(state.get("log", [])) + 1                  # compute the run number from stored history
    return {"log": [f"run-{n}"], "count": n}           # update state


builder = StateGraph(State)                            # builder
builder.add_node("step", step)                         # node
builder.add_edge(START, "step")                        # entry
builder.add_edge("step", END)                          # exit

db_path = os.path.join(tempfile.mkdtemp(), "demo.db")  # a throw-away db file
cfg = {"configurable": {"thread_id": "case-1"}}        # the conversation key

# "Process 1": open the file, run twice, close.
with SqliteSaver.from_conn_string(db_path) as saver:   # context manager closes the connection
    app = builder.compile(checkpointer=saver)          # compile with the saver
    app.invoke({"log": []}, cfg)                       # first run
    print(app.invoke({"log": []}, cfg)["log"])         # ['run-1', 'run-2']

# "Process 2": new saver object on the SAME file == simulated restart.
with SqliteSaver.from_conn_string(db_path) as saver2:  # re-open the file
    app2 = builder.compile(checkpointer=saver2)        # compile again
    print(app2.get_state(cfg).values["log"])           # memory survived: ['run-1', 'run-2']

os.remove(db_path)                                     # clean up the demo file
```

## 💻 Code Example — Advanced
```python
# Production-style: async SQLite saver + app lifespan + error handling + type hints
import asyncio                                         # async runtime
import logging                                         # logs
import operator                                        # reducer
from contextlib import asynccontextmanager             # for lifespan style helpers
from typing import Annotated, Any, AsyncIterator, TypedDict   # type hints

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver  # async checkpointer (needs aiosqlite)
from langgraph.graph import END, START, StateGraph     # graph API

logger = logging.getLogger("tariff.sqlite")            # logger


class CaseState(TypedDict):                            # state of one tariff case
    notes: Annotated[list[str], operator.add]          # analyst notes (append only)
    hs_code: str                                       # current HS code


async def classify(state: CaseState) -> dict[str, Any]:   # async node
    await asyncio.sleep(0)                             # stand-in for `await llm.ainvoke(...)`
    return {"hs_code": "8517.13", "notes": ["auto-classified"]}  # fake result


def build(saver: AsyncSqliteSaver):                    # builds a compiled graph
    b = StateGraph(CaseState)                          # builder
    b.add_node("classify", classify)                   # node
    b.add_edge(START, "classify")                      # entry
    b.add_edge("classify", END)                        # exit
    return b.compile(checkpointer=saver)               # attach the durable saver


@asynccontextmanager                                   # reusable "open db, yield graph, close db"
async def open_graph(path: str) -> AsyncIterator[Any]: # returns an async iterator of one graph
    async with AsyncSqliteSaver.from_conn_string(path) as saver:  # opens + closes the connection
        yield build(saver)                             # caller uses the graph inside the block


async def run_case(graph: Any, case_id: str, note: str) -> dict[str, Any]:  # one request
    cfg = {"configurable": {"thread_id": case_id}}     # key for this case
    try:                                               # error handling
        return await graph.ainvoke({"notes": [note]}, cfg)   # run + auto-save checkpoint
    except Exception:                                  # DB locked, disk full, node failure...
        logger.exception("case %s failed", case_id)    # log with traceback
        raise                                          # let the API layer map it to HTTP 500


async def main() -> None:                              # demo
    async with open_graph("tariff_demo.db") as graph:  # open file-backed graph
        out = await run_case(graph, "case-1", "first look")   # run
        print(out["hs_code"], out["notes"])            # show result
        async for snap in graph.aget_state_history({"configurable": {"thread_id": "case-1"}}):
            print(snap.config["configurable"]["checkpoint_id"])  # list checkpoints, newest first
            break                                      # only the newest one


if __name__ == "__main__":                             # entry
    asyncio.run(main())                                # run (creates tariff_demo.db in cwd)
```

---

## 🟠 FastAPI Integration
Open the saver once in FastAPI's `lifespan` (startup) and close it on shutdown. Store the compiled graph on `app.state`. Run a single worker, because SQLite allows many readers but only one writer at a time. For many workers or servers choose Postgres or Redis.

```python
# FastAPI + AsyncSqliteSaver using lifespan
import operator                                               # reducer
from contextlib import asynccontextmanager                    # lifespan helper
from typing import Annotated, TypedDict                       # type hints

from fastapi import FastAPI, HTTPException, Request           # web framework
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver  # async saver
from langgraph.graph import END, START, StateGraph            # graph API
from pydantic import BaseModel, Field                         # models


class S(TypedDict):                                           # state
    notes: Annotated[list[str], operator.add]                 # notes list
    answer: str                                               # latest answer


async def node(state: S) -> dict:                             # node
    return {"answer": f"{len(state['notes'])} notes so far"}  # simple logic


@asynccontextmanager                                          # lifespan = startup + shutdown
async def lifespan(app: FastAPI):                             # FastAPI calls this
    async with AsyncSqliteSaver.from_conn_string("tariff.db") as saver:  # open ONCE
        b = StateGraph(S)                                     # build graph
        b.add_node("n", node)                                 # node
        b.add_edge(START, "n")                                # entry
        b.add_edge("n", END)                                  # exit
        app.state.graph = b.compile(checkpointer=saver)       # share via app.state
        yield                                                 # app serves requests here
    # leaving the `async with` closes the SQLite connection cleanly


app = FastAPI(title="Tariff Cases", lifespan=lifespan)        # attach lifespan


class NoteIn(BaseModel):                                      # request body
    note: str = Field(min_length=1, max_length=2000)          # analyst note


@app.post("/cases/{case_id}/notes")                           # route
async def add_note(case_id: str, body: NoteIn, request: Request) -> dict[str, str]:
    cfg = {"configurable": {"thread_id": case_id}}            # case = thread
    try:                                                      # error handling
        out = await request.app.state.graph.ainvoke({"notes": [body.note]}, cfg)  # run
    except Exception as exc:                                  # failure
        raise HTTPException(500, "could not save note") from exc  # clean error
    return {"answer": out["answer"]}                          # response
```

---

## 🔗 LangChain / LangGraph Connection
SqliteSaver implements `BaseCheckpointSaver`, so it plugs into `StateGraph.compile`, `create_react_agent`, and LangGraph Studio's local dev server in the same way as MemorySaver. LangChain's older chat message history classes (`SQLChatMessageHistory`) store only messages. A LangGraph checkpointer stores the whole graph state, plus the next nodes, so interrupts can resume.

```python
# ReAct agent with persistent memory in SQLite (needs OPENAI_API_KEY to run)
from langchain_openai import ChatOpenAI                       # model
from langgraph.checkpoint.sqlite import SqliteSaver           # saver
from langgraph.prebuilt import create_react_agent             # prebuilt agent

with SqliteSaver.from_conn_string("agent.db") as saver:       # open file
    agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), tools=[], checkpointer=saver)
    cfg = {"configurable": {"thread_id": "officer-7"}}        # thread
    agent.invoke({"messages": [("user", "Remember: my product is a drone.")]}, cfg)
    # restart the program later, open agent.db again, and the drone is still remembered
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the sync `SqliteSaver` with `ainvoke` / `astream`
✅ Correct: use `AsyncSqliteSaver` (with `aiosqlite`) for async code.

```python
# Wrong — sync saver does not support async methods (NotImplementedError)
with SqliteSaver.from_conn_string("t.db") as saver:
    app = builder.compile(checkpointer=saver)
    await app.ainvoke(...)

# Right
async with AsyncSqliteSaver.from_conn_string("t.db") as saver:
    app = builder.compile(checkpointer=saver)
    await app.ainvoke(...)
```

❌ Mistake 2: Using the graph after the `with` block has closed the connection
✅ Correct: keep all graph calls inside the block (or manage the lifetime in FastAPI lifespan).

```python
# Wrong
with SqliteSaver.from_conn_string("t.db") as saver:
    app = builder.compile(checkpointer=saver)
app.invoke(...)                     # connection is closed -> error

# Right
with SqliteSaver.from_conn_string("t.db") as saver:
    app = builder.compile(checkpointer=saver)
    app.invoke(...)
```

❌ Mistake 3: Running many uvicorn workers or pods on one SQLite file
✅ Correct: single worker, or switch to Postgres/Redis for concurrent writers and network access.

---

## 🧠 Tricky Interview Question

**Q**: "You switched from MemorySaver to SqliteSaver, but your API now throws `database is locked` under load. What is happening and what do you do?"

**Answer**: SQLite allows only one writer at a time. Every graph step writes a checkpoint, so many concurrent requests (or several worker processes) compete for the write lock. Fixes: (1) run a single process with async code so the connection is serialised by one event loop, (2) enable WAL mode and a busy timeout, (3) reduce checkpoint frequency by using fewer nodes or coarser steps, (4) most importantly, move to PostgresSaver or RedisSaver when you need multiple workers or hosts. SQLite is a great single-node choice, not a horizontally scalable one.

---

## ⚫ Interview Questions + Answers

Q1: When do you choose SqliteSaver over MemorySaver? (Easy)
A1: When memory must survive restarts but you do not want to run a database server. Typical cases are local apps, CLIs, internal tools and small single-VM deployments.

Q2: What is the difference between `SqliteSaver` and `AsyncSqliteSaver`? (Easy)
A2: `SqliteSaver` uses the blocking `sqlite3` driver and works with `invoke`/`stream`. `AsyncSqliteSaver` uses `aiosqlite` and works with `ainvoke`/`astream`. Mixing them causes errors.

Q3: Which tables does the saver create and why? (Medium)
A3: `checkpoints` stores the serialised state snapshots with thread id, checkpoint id and parent id, which forms a linked history. `writes` stores intermediate writes from nodes that finished inside a super-step, so a crashed step can resume without re-running successful nodes.

Q4: How do you inspect or roll back a case? (Medium)
A4: `get_state_history(config)` lists the checkpoints (newest first). Pick a `checkpoint_id` and call `invoke(None, config_with_checkpoint_id)` to replay from that point, or `update_state` to edit and fork. This is time travel and is useful for debugging bad classifications.

Q5: Design persistence for a tariff assistant that grows from 5 internal users to 5,000 users on several servers. (Hard)
A5: Start with SqliteSaver for the pilot. When traffic grows, move to PostgresSaver (or RedisSaver) because checkpoints must be shared by all pods. Use connection pooling, call `.setup()` in a migration job, set a retention policy that deletes old checkpoints, keep large documents outside the state (store a reference id), and add monitoring on checkpoint size and write latency. Graph code is unchanged because the saver is a one-line swap.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need persistence with zero infrastructure
- Single server, single process, low write concurrency
- Desktop tools, CLIs, prototypes that must survive restarts

❌ Avoid when:
- Multiple workers, pods or regions need the same memory
- High write throughput (many parallel conversations)
- Database file would be on a network drive (SQLite locking is unreliable there)

---

## 📊 Visual Diagram
```
 app.invoke(input, thread_id="case-1")
        │
        ▼
 ┌─────────────┐  read latest  ┌───────────────────────────┐
 │  LangGraph  │ ────────────► │ tariff.db  (one file)     │
 │  runtime    │ ◄──────────── │  ├─ checkpoints (state)   │
 └──────┬──────┘     state     │  └─ writes (pending)      │
        │ run node             └───────────────────────────┘
        ▼                                  ▲
   update state ── INSERT checkpoint ──────┘

 Restart process ─► open same file ─► same thread_id ─► state is back
 Limit: ONE writer at a time (SQLite lock)
```

---

## 💰 Cost Impact
SQLite is free and adds only small disk I/O (usually a few milliseconds per step). The real cost is indirect: persistent threads live for days, so if you feed the whole stored history into the LLM each turn, input tokens keep growing. A 40-turn case at about 300 tokens per turn means about 12,000 input tokens on turn 40 (about $0.0018 on gpt-4o-mini input pricing, but 80x that at 100K cases).

Optimise: summarise old turns and store the summary in state, use `trim_messages` to cap prompt size, keep documents out of state, vacuum or delete checkpoints older than your retention window (`DELETE` by thread), and cache the static system prompt.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SqliteSaver | Checkpointer backed by a SQLite file | SQLite file वाला checkpointer |
| AsyncSqliteSaver | Async version using aiosqlite | Async वाला version |
| Persistence | State survives restarts | Restart के बाद भी state बची रहना |
| WAL mode | SQLite journal mode for better concurrency | बेहतर concurrency वाला mode |
| from_conn_string | Factory that opens the DB | DB खोलने वाला method |
| Time travel | Replay or fork from an old checkpoint | पुराने checkpoint से दोबारा चलाना |
| Lifespan | FastAPI startup/shutdown hook | App शुरू/बंद होने का hook |

---

## ⚡ 3-Line Summary
English: SqliteSaver stores LangGraph checkpoints in a SQLite file, so memory survives restarts with no extra server. Use the async version for async code and open it once in FastAPI lifespan. It has a single writer, so for many workers move to Postgres or Redis.
Hindi: SqliteSaver LangGraph checkpoints को SQLite file में रखता है, इसलिए बिना extra server के restart के बाद भी memory बची रहती है। Async code के लिए async version लें और FastAPI lifespan में एक बार खोलें। इसमें एक समय पर एक ही writer होता है, इसलिए कई workers हों तो Postgres या Redis लें।

---

## ➡️ Next Topic
**328. RedisSaver** — a fast, network-shared checkpointer for multi-worker production deployments.
