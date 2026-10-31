---

# 326. MemorySaver
# हिंदी में: MemorySaver (In-Memory Checkpointer)

---

## 🔵 Simple Definition (English)
`MemorySaver` is LangGraph's simplest checkpointer. After every step (super-step) of a graph it saves a snapshot of the state in the Python process RAM, keyed by a `thread_id`. This gives the graph short-term memory across calls. When the process stops, everything is lost. (In newer versions it is also exported as `InMemorySaver`.)

## 🔵 सरल परिभाषा (Hindi)
`MemorySaver` LangGraph का सबसे simple checkpointer है। Graph के हर step के बाद यह state का snapshot Python process की RAM में `thread_id` के नाम से save करता है। इससे graph को calls के बीच short-term memory मिलती है। Process बंद होते ही सब कुछ गायब हो जाता है।

---

## 🔴 Problem it Solves
A compiled LangGraph is stateless by default. Each `invoke()` starts from scratch, so a chatbot forgets the previous question. You also cannot pause a graph, inspect old states, or replay a run. A checkpointer fixes all of this. `MemorySaver` is the zero-setup version used in development, notebooks and unit tests.

## 🔴 यह क्यों बना? (Hindi)
Default में compiled graph stateless होता है। हर `invoke()` नए सिरे से शुरू होता है, इसलिए chatbot पिछला सवाल भूल जाता है। Graph को pause करना, पुरानी states देखना या run replay करना भी संभव नहीं होता। Checkpointer यह सब ठीक करता है। `MemorySaver` बिना setup वाला version है, जो development, notebooks और tests में काम आता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create saver:         checkpointer = MemorySaver()
Step 2 → Compile the graph:    app = graph.compile(checkpointer=checkpointer)
Step 3 → Call with a thread:   app.invoke(input, {"configurable": {"thread_id": "user-1"}})
Step 4 → After each super-step LangGraph writes a checkpoint (state + next nodes + metadata)
Step 5 → Next call with the SAME thread_id loads the latest checkpoint and continues from it
Step 6 → A DIFFERENT thread_id gets a fresh, isolated state
Step 7 → app.get_state(config) / app.get_state_history(config) let you inspect or time-travel
Step 8 → Process exits → the dict in RAM is garbage collected → all memory is gone
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Saver बनाओ:           checkpointer = MemorySaver()
Step 2 → Graph compile करो:      app = graph.compile(checkpointer=checkpointer)
Step 3 → thread_id के साथ call:  app.invoke(input, {"configurable": {"thread_id": "user-1"}})
Step 4 → हर super-step के बाद checkpoint (state + अगले nodes + metadata) लिखा जाता है
Step 5 → उसी thread_id से अगली call पर latest checkpoint load होकर आगे चलता है
Step 6 → अलग thread_id = नई और अलग state
Step 7 → get_state / get_state_history से state देख सकते हैं या time-travel कर सकते हैं
Step 8 → Process खत्म → RAM की dict साफ़ → memory खत्म
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs officer chats with the assistant: "Classify a Bluetooth speaker", then "What about the one with a built-in battery?". Without a checkpointer the second question has no context. With `MemorySaver` and `thread_id="case-4021"`, the graph remembers the first answer (HS 8518.22) and refines it. This is perfect for the dev laptop and for tests. In production you swap in SqliteSaver or a Postgres/Redis saver because RAM is lost on restart.

**Zomato-style**: A food-ordering bot keeps "veg only, under 300 rupees" inside the thread, so the next message "show desserts" respects it.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs officer पूछता है "Bluetooth speaker classify करो", फिर "जिसमें built-in battery है उसका क्या?"। Checkpointer के बिना दूसरे सवाल का context नहीं मिलता। `MemorySaver` और `thread_id="case-4021"` के साथ graph पहला जवाब (HS 8518.22) याद रखता है। Dev और tests के लिए यह सही है। Production में SqliteSaver या Postgres/Redis saver लगाते हैं क्योंकि restart पर RAM खाली हो जाती है।

**Zomato-style**: Food bot thread में "veg only, 300 से कम" याद रखता है, इसलिए अगला message "desserts दिखाओ" उसी filter के साथ चलता है।

---

## 💻 Code Example — Basic
```python
# Basic: a tiny graph with MemorySaver (no API key needed, runs offline)
import operator                                   # operator.add is used as a list reducer
from typing import Annotated, TypedDict           # type hints for the state

from langgraph.checkpoint.memory import MemorySaver   # in-RAM checkpointer
from langgraph.graph import END, START, StateGraph    # graph building blocks


class TariffState(TypedDict):                     # the shared state of the graph
    query: str                                    # latest user question
    history: Annotated[list[str], operator.add]   # reducer: new items are APPENDED, not replaced
    answer: str                                   # latest answer


def classify(state: TariffState) -> dict:         # a node: reads state, returns a partial update
    seen = len(state.get("history", []))          # how many questions were stored before
    answer = f"HS-8518.22 (this is question #{seen + 1} in this thread)"  # fake LLM answer
    return {"answer": answer, "history": [state["query"]]}  # history gets appended via reducer


builder = StateGraph(TariffState)                 # create the builder with our state schema
builder.add_node("classify", classify)            # register the node
builder.add_edge(START, "classify")               # entry point
builder.add_edge("classify", END)                 # exit point

memory = MemorySaver()                            # create the in-memory checkpointer
app = builder.compile(checkpointer=memory)        # attach it while compiling

cfg_a = {"configurable": {"thread_id": "case-A"}}  # thread A config
cfg_b = {"configurable": {"thread_id": "case-B"}}  # thread B config

print(app.invoke({"query": "bluetooth speaker"}, cfg_a)["answer"])  # question #1 in A
print(app.invoke({"query": "with battery"}, cfg_a)["answer"])       # question #2 in A (memory works)
print(app.invoke({"query": "laptop"}, cfg_b)["answer"])             # question #1 in B (isolated)

snapshot = app.get_state(cfg_a)                   # read the saved state of thread A
print(snapshot.values["history"])                 # ['bluetooth speaker', 'with battery']
```

## 💻 Code Example — Advanced
```python
# Production-style dev server: MemorySaver + async + error handling + type hints
import asyncio                                    # to run the async demo
import logging                                    # structured logs instead of print
import operator                                   # list reducer
from typing import Annotated, Any, TypedDict      # type hints

from langgraph.checkpoint.memory import MemorySaver   # in-memory checkpointer
from langgraph.graph import END, START, StateGraph    # graph API

logger = logging.getLogger("tariff.memory")       # module logger


class ChatState(TypedDict):                       # state schema
    messages: Annotated[list[dict[str, str]], operator.add]  # chat log, append-only
    hs_code: str                                  # last predicted HS code


async def classify_node(state: ChatState) -> dict[str, Any]:   # async node
    last = state["messages"][-1]["content"]       # newest user message
    await asyncio.sleep(0)                        # placeholder for a real `await llm.ainvoke(...)`
    code = "8517.13" if "phone" in last.lower() else "9999.00"  # fake classification rule
    reply = {"role": "assistant", "content": f"HS code: {code}"}   # assistant message
    return {"messages": [reply], "hs_code": code} # partial state update


def build_app(saver: MemorySaver | None = None):   # factory so tests can inject a saver
    builder = StateGraph(ChatState)               # new graph
    builder.add_node("classify", classify_node)   # add node
    builder.add_edge(START, "classify")           # START -> classify
    builder.add_edge("classify", END)             # classify -> END
    return builder.compile(checkpointer=saver or MemorySaver())  # compile with memory


async def chat(app: Any, thread_id: str, text: str) -> str:   # one chat turn
    config = {"configurable": {"thread_id": thread_id}}       # identifies the conversation
    try:                                                      # protect against node failures
        result = await app.ainvoke(                           # async invoke
            {"messages": [{"role": "user", "content": text}]}, config
        )
    except Exception:                                         # never leak a stack trace to users
        logger.exception("graph failed for thread %s", thread_id)  # log full error
        return "Sorry, classification failed. Please retry."  # safe fallback
    return result["messages"][-1]["content"]                  # last assistant message


async def main() -> None:                         # demo runner
    app = build_app()                             # build graph
    print(await chat(app, "t1", "Classify a smartphone"))     # turn 1
    print(await chat(app, "t1", "And a charger?"))            # turn 2, same thread
    state = await app.aget_state({"configurable": {"thread_id": "t1"}})  # async state read
    print(len(state.values["messages"]), "messages stored")   # 4 messages (2 user + 2 bot)
    async for snap in app.aget_state_history({"configurable": {"thread_id": "t1"}}):  # time travel
        print(snap.metadata.get("step"), snap.next)           # step number + next nodes
        break                                                 # only show the newest one


if __name__ == "__main__":                        # script entry
    asyncio.run(main())                           # run the demo
```

---

## 🟠 FastAPI Integration
Create ONE `MemorySaver` at module level (shared by all requests) and use the user's session id as `thread_id`. Never create a new saver per request, otherwise memory is lost on every call. Remember: with several uvicorn workers each process has its own RAM, so use MemorySaver only with a single worker.

```python
# FastAPI + MemorySaver (single-process dev/demo server)
from typing import Annotated, TypedDict                       # type hints
import operator                                               # reducer

from fastapi import FastAPI, HTTPException                    # web framework
from langgraph.checkpoint.memory import MemorySaver           # checkpointer
from langgraph.graph import END, START, StateGraph            # graph API
from pydantic import BaseModel, Field                         # request/response models


class S(TypedDict):                                           # graph state
    log: Annotated[list[str], operator.add]                   # appended history
    answer: str                                               # last answer


def node(state: S) -> dict:                                   # sample node
    return {"answer": f"seen {len(state['log'])} msgs", "log": ["ok"]}  # tiny fake logic


builder = StateGraph(S)                                       # graph
builder.add_node("n", node)                                   # node
builder.add_edge(START, "n")                                  # entry
builder.add_edge("n", END)                                    # exit
graph = builder.compile(checkpointer=MemorySaver())           # ONE shared saver

app = FastAPI(title="Tariff Chat (MemorySaver)")              # the API


class ChatIn(BaseModel):                                      # request body
    session_id: str = Field(min_length=1, max_length=64)      # becomes thread_id
    message: str = Field(min_length=1, max_length=2000)       # user text


@app.post("/chat")                                            # route
async def chat(body: ChatIn) -> dict[str, str]:               # async handler
    cfg = {"configurable": {"thread_id": body.session_id}}    # per-user memory key
    try:                                                      # error handling
        out = await graph.ainvoke({"log": [body.message]}, cfg)   # run graph
    except Exception as exc:                                  # any failure
        raise HTTPException(status_code=500, detail="graph error") from exc  # clean 500
    return {"answer": out["answer"]}                          # JSON response


@app.get("/chat/{session_id}/history")                        # inspect memory
async def history(session_id: str) -> dict[str, list[str]]:   # handler
    snap = await graph.aget_state({"configurable": {"thread_id": session_id}})  # read state
    return {"log": snap.values.get("log", [])}                # empty list for unknown thread
```

---

## 🔗 LangChain / LangGraph Connection
`MemorySaver` is the base class family of `BaseCheckpointSaver`. SqliteSaver, PostgresSaver and RedisSaver all share the same interface, so switching is a one-line change. The prebuilt `create_react_agent` also accepts `checkpointer=`. Note: the checkpointer stores per-thread (short-term) memory. For long-term, cross-thread memory (user preferences) LangGraph uses a separate `Store` (e.g. `InMemoryStore`).

```python
# create_react_agent with MemorySaver (needs an API key to actually run)
from langchain_openai import ChatOpenAI                       # chat model wrapper
from langgraph.checkpoint.memory import MemorySaver           # in-RAM checkpointer
from langgraph.prebuilt import create_react_agent             # ready-made agent

agent = create_react_agent(                                   # build the agent
    ChatOpenAI(model="gpt-4o-mini"),                          # cheap model
    tools=[],                                                 # no tools for this demo
    checkpointer=MemorySaver(),                               # enable per-thread memory
)
cfg = {"configurable": {"thread_id": "officer-7"}}            # conversation id
agent.invoke({"messages": [("user", "My product is a drone.")]}, cfg)      # turn 1
agent.invoke({"messages": [("user", "What did I say it was?")]}, cfg)      # turn 2 remembers
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `thread_id` in the config
✅ Correct: always pass `{"configurable": {"thread_id": ...}}` when a checkpointer exists. Without it LangGraph raises an error.

```python
# Wrong — checkpointer exists but no thread_id
app.invoke({"query": "hi"})                                   # ValueError: thread_id is required

# Right
app.invoke({"query": "hi"}, {"configurable": {"thread_id": "u1"}})
```

❌ Mistake 2: Creating a new `MemorySaver()` for every request
✅ Correct: create it once and share it.

```python
# Wrong — memory is thrown away each request
@app.post("/chat")
async def chat(b: ChatIn):
    g = builder.compile(checkpointer=MemorySaver())           # fresh RAM each time!
    return await g.ainvoke(...)

# Right — module-level graph, compiled once
graph = builder.compile(checkpointer=MemorySaver())
```

❌ Mistake 3: Using MemorySaver in production with many workers or restarts
✅ Correct: use SqliteSaver (single node) or Postgres/Redis savers (multi node).

---

## 🧠 Tricky Interview Question

**Q**: "Your chatbot works in testing with `MemorySaver`, but in production on Kubernetes users randomly lose their conversation. Logs show no errors. Why?"

**Answer**: `MemorySaver` keeps data in the RAM of one process. In production you have several pods and several workers, and a load balancer sends each request to a random one. A thread created in pod A does not exist in pod B, and pods restart on deploys. The fix is a shared, durable checkpointer (Postgres, Redis or a managed LangGraph deployment), or sticky sessions as a weak workaround. Also set a TTL or cleanup policy, because a durable store grows forever.

---

## ⚫ Interview Questions + Answers

Q1: What does a checkpointer do in LangGraph? (Easy)
A1: It saves a snapshot of the graph state after each super-step under a `thread_id`. This enables memory across calls, pause/resume (human in the loop), time travel and fault tolerance.

Q2: What is `thread_id`? (Easy)
A2: A key in `config["configurable"]` that identifies one conversation. Same id means the same saved state. A new id means a clean state. It is usually the session or case id.

Q3: What is the difference between a checkpointer and a Store? (Medium)
A3: A checkpointer holds the state of one thread (short-term memory). A `Store` holds data shared across threads, such as user profile facts (long-term memory). Both can be backed by RAM, SQL or Redis.

Q4: What exactly is saved in a checkpoint? (Medium)
A4: Channel values (the state), the checkpoint id and timestamp, the `next` nodes to run, pending writes and metadata (step number, source). That is why you can resume mid-graph after an interrupt.

Q5: How would you migrate from MemorySaver to a durable saver without changing graph logic, and what pitfalls exist? (Hard)
A5: Graph code does not change because every saver implements `BaseCheckpointSaver`. Only the saver object passed to `compile()` changes. Pitfalls: (1) state must be serialisable, so custom classes need to be msgpack/JSON friendly, (2) sync vs async savers (use AsyncSqliteSaver or AsyncPostgresSaver with `ainvoke`), (3) schema setup (`.setup()`), (4) connection lifecycle (context manager or pool), (5) growth of old checkpoints needs pruning, (6) previously saved states are not migrated automatically.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Local development, notebooks, demos
- Unit tests that need deterministic, isolated memory
- Short-lived single-process scripts

❌ Avoid when:
- Production APIs with multiple workers or pods
- Conversations must survive restarts
- Memory use is unbounded (every thread stays in RAM)

---

## 📊 Visual Diagram
```
 invoke(input, thread_id="case-A")
          │
          ▼
   ┌──────────────┐   load latest    ┌────────────────────────┐
   │  LangGraph   │ ───────────────► │ MemorySaver (RAM dict) │
   │  runtime     │ ◄─────────────── │ "case-A": [cp1,cp2,..] │
   └──────┬───────┘   state          │ "case-B": [cp1,..]     │
          │ run node                  └────────────────────────┘
          ▼                                      ▲
   node returns update ── save checkpoint ───────┘
          │
          ▼
        result            Process dies  ==>  dict gone  ==>  all threads lost
```

---

## 💰 Cost Impact
MemorySaver itself costs nothing, but memory changes LLM cost. If your node sends the full saved `messages` list to the model each turn, input tokens grow with every turn (turn 10 may send 10x the tokens of turn 1). Example: 300 tokens per turn, 20 turns means turn 20 sends about 6,000 input tokens. With gpt-4o-mini ($0.15 per 1M input) this is small, but at 100K chats/day it is noticeable.

Optimise: (1) trim or summarise old messages (`trim_messages`), (2) keep only the last N turns in the prompt but all in the checkpoint, (3) store IDs and short facts (HS code) instead of full documents in state, (4) use prompt caching for the fixed system prompt.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Checkpointer | Saves graph state after each step | State save करने वाला component |
| MemorySaver / InMemorySaver | Checkpointer in process RAM | RAM में चलने वाला saver |
| thread_id | Key of one conversation | एक conversation की पहचान |
| Super-step | One round of node execution | Nodes के चलने का एक round |
| Checkpoint | Snapshot of state at a point | किसी पल की state का snapshot |
| Reducer | Rule to merge state updates | Updates जोड़ने का नियम |
| Store | Cross-thread long-term memory | Threads के बीच long-term memory |

---

## ⚡ 3-Line Summary
English: MemorySaver stores graph checkpoints in RAM, keyed by `thread_id`, giving a graph short-term memory. It needs zero setup, so it is ideal for dev and tests. It disappears on restart and is not shared across workers, so use a durable saver in production.
Hindi: MemorySaver graph के checkpoints RAM में `thread_id` के साथ रखता है, जिससे short-term memory मिलती है। Setup शून्य है, इसलिए dev और tests के लिए बढ़िया है। Restart पर सब मिट जाता है और workers में share नहीं होता, इसलिए production में durable saver लगाओ।

---

## ➡️ Next Topic
**327. SqliteSaver** — persist checkpoints to a file so memory survives restarts, the next step up from MemorySaver.
