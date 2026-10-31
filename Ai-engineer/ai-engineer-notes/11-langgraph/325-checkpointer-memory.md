---

# 325. Checkpointer — Memory
# हिंदी में: Checkpointer — Memory (याददाश्त)

---

## 🔵 Simple Definition (English)
A checkpointer saves a snapshot of the graph state after every step. You pass a `thread_id` when you run the graph, and LangGraph loads the last snapshot for that thread before running. This gives the graph short-term memory across calls (a conversation), plus the ability to resume, replay and time-travel.

## 🔵 सरल परिभाषा (Hindi)
Checkpointer हर step के बाद graph state का snapshot save करता है। Graph चलाते समय आप `thread_id` देते हैं और LangGraph उस thread का last snapshot load करके आगे बढ़ता है। इससे graph को calls के बीच short-term memory (conversation) मिलती है, साथ ही resume, replay और time-travel भी संभव होता है।

---

## 🔴 Problem it Solves
By default a compiled graph is stateless: each `invoke` starts from the input you pass. A chatbot would forget the previous question ("what about its duty rate?" has no meaning without the earlier "iPhone"). Developers had to store and resend the whole history manually. Also, if a server crashed mid-workflow, all progress was lost, and human-in-the-loop pauses were impossible.

## 🔴 यह क्यों बना? (Hindi)
Default रूप में compiled graph stateless होता है: हर `invoke` आपके दिए input से शुरू होता है। Chatbot पिछला सवाल भूल जाता ("इसका duty rate?" का मतलब पिछले "iPhone" के बिना नहीं निकलता)। Developers को पूरी history खुद store करके दोबारा भेजनी पड़ती थी। Server crash होने पर सारी progress खो जाती थी, और human-in-the-loop pause संभव नहीं था।

---

## 🟢 How it Works — Step by Step

```
Step 1 → compile(checkpointer=saver) attaches storage to the graph
Step 2 → invoke(input, config={"configurable": {"thread_id": "t1"}})
Step 3 → LangGraph loads the latest checkpoint for thread "t1" (if any)
Step 4 → Input is merged into that state via reducers (messages are appended)
Step 5 → After each super-step the new state is saved as a checkpoint
Step 6 → Next call with the same thread_id continues; a new thread_id starts fresh
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → compile(checkpointer=saver) graph से storage जोड़ता है
Step 2 → invoke(input, config={"configurable": {"thread_id": "t1"}})
Step 3 → LangGraph thread "t1" का latest checkpoint load करता है (अगर हो)
Step 4 → Input reducers के ज़रिए उस state में merge होता है (messages append होते हैं)
Step 5 → हर super-step के बाद नई state checkpoint के रूप में save होती है
Step 6 → उसी thread_id से अगली call continue करती है; नया thread_id fresh शुरू करता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: An officer asks "HS code for a Bluetooth speaker?", the bot answers 8518.22. The next message is "and the import duty?". Because the thread has memory, the bot knows "and the import duty" refers to the speaker. A second officer uses a different `thread_id` and sees none of this. **Zomato AI**: the support chat keeps `order_id` in state across messages using `thread_id = user_id + order_id`.

## 🟡 Real Example Hindi mein
**Tariff System**: Officer पूछता है "Bluetooth speaker का HS code?", bot 8518.22 बताता है। अगला message "और import duty?"। Thread में memory है, इसलिए bot समझता है कि यह speaker के बारे में है। दूसरा officer अलग `thread_id` use करता है और उसे यह सब नहीं दिखता। **Zomato AI**: support chat में `thread_id = user_id + order_id` से `order_id` हर message में state में बना रहता है।

---

## 💻 Code Example — Basic
```python
# Checkpointer memory - runs offline (pip install langgraph)
from langchain_core.messages import AIMessage  # message class
from langgraph.checkpoint.memory import MemorySaver  # in-RAM checkpointer (dev/test only)
from langgraph.graph import END, START, MessagesState, StateGraph  # graph API


def bot(state: MessagesState) -> dict:  # fake chat node
    count = len(state["messages"])  # how many messages the graph remembers
    return {"messages": [AIMessage(content=f"I remember {count} messages")]}  # report memory size


builder = StateGraph(MessagesState)  # builder
builder.add_node("bot", bot)  # node
builder.add_edge(START, "bot")  # entry
builder.add_edge("bot", END)  # exit

memory = MemorySaver()  # create the saver
graph = builder.compile(checkpointer=memory)  # attach it at compile time

cfg_a = {"configurable": {"thread_id": "officer-A"}}  # conversation key A
cfg_b = {"configurable": {"thread_id": "officer-B"}}  # conversation key B

print(graph.invoke({"messages": [("user", "speaker HS code?")]}, cfg_a)["messages"][-1].content)  # 1 message
print(graph.invoke({"messages": [("user", "and duty?")]}, cfg_a)["messages"][-1].content)  # 3 messages (memory!)
print(graph.invoke({"messages": [("user", "hello")]}, cfg_b)["messages"][-1].content)  # fresh thread: 1 message

snap = graph.get_state(cfg_a)  # read the saved state of thread A
print(len(snap.values["messages"]))  # 4 saved messages
```

## 💻 Code Example — Advanced
```python
# Inspect history, edit state, async usage, error handling, thread helpers
import asyncio  # async runner
import uuid  # unique thread ids
from typing import TypedDict  # typing

from langgraph.checkpoint.memory import MemorySaver  # swap for Postgres/Redis in production
from langgraph.graph import END, START, StateGraph  # graph API


class State(TypedDict):  # state
    product: str  # last product
    runs: int  # how many times a node ran in this thread


async def count_runs(state: State) -> dict[str, int]:  # async node
    return {"runs": state.get("runs", 0) + 1}  # increment the persisted counter


builder = StateGraph(State)  # builder
builder.add_node("count", count_runs)  # node
builder.add_edge(START, "count")  # entry
builder.add_edge("count", END)  # exit
graph = builder.compile(checkpointer=MemorySaver())  # compile with memory


def new_thread() -> dict:  # helper: config for a brand-new conversation
    return {"configurable": {"thread_id": str(uuid.uuid4())}}


async def main() -> None:
    cfg = new_thread()  # fresh thread
    try:
        await graph.ainvoke({"product": "speaker"}, cfg)  # run 1
        out = await graph.ainvoke({"product": "speaker"}, cfg)  # run 2 on same thread
        print(out["runs"])  # 2 -> counter persisted

        history = [s async for s in graph.aget_state_history(cfg)]  # every checkpoint, newest first
        print(len(history), "checkpoints")  # one per step + input checkpoints

        await graph.aupdate_state(cfg, {"runs": 100})  # manually edit state (e.g. human correction)
        print((await graph.aget_state(cfg)).values["runs"])  # 100
    except ValueError as exc:  # raised if thread_id is missing while checkpointer is set
        print("config problem:", exc)

    try:
        await graph.ainvoke({"product": "x"})  # forgot config
    except ValueError as exc:
        print("expected error:", str(exc)[:60])


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Use one compiled graph per process and let the client send a `session_id`. Map it to `thread_id`. Never put real user ids from untrusted input directly without authentication, or one user could read another's thread.

```python
from fastapi import FastAPI, Header  # web
from pydantic import BaseModel  # validation

app = FastAPI()  # app


class Msg(BaseModel):  # request
    text: str


@app.post("/chat")
async def chat(msg: Msg, x_session_id: str = Header(...)) -> dict[str, str]:  # session id from header
    cfg = {"configurable": {"thread_id": f"user:{x_session_id}"}}  # namespaced thread id
    out = await graph.ainvoke({"messages": [("user", msg.text)]}, cfg)  # graph compiled with a checkpointer
    return {"reply": out["messages"][-1].content}  # return last AI message
```

---

## 🔗 LangChain / LangGraph Connection
Checkpointers are the LangGraph replacement for old LangChain `ConversationBufferMemory`. They save *the whole graph state*, not just messages. Savers: `MemorySaver` (RAM), `SqliteSaver`, `PostgresSaver`, `RedisSaver` (next topics 326-328). Checkpoints are also the foundation of human-in-the-loop (`interrupt`), time-travel, and fault tolerance. Short-term memory = checkpointer (per thread). Long-term memory across threads = a `Store`.

```python
from langgraph.checkpoint.memory import MemorySaver  # saver
from langgraph.prebuilt import create_react_agent  # prebuilt agent (LangGraph); newer LangChain has create_agent
from langchain_openai import ChatOpenAI  # model

agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), tools=[], checkpointer=MemorySaver())  # memory-enabled agent
agent.invoke({"messages": [("user", "My product is a speaker")]}, {"configurable": {"thread_id": "1"}})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `thread_id`
✅ Correct: Always pass `config={"configurable": {"thread_id": ...}}`.

```python
# Wrong - raises ValueError because the checkpointer needs a thread_id
graph.invoke({"messages": [("user", "hi")]})

# Right
graph.invoke({"messages": [("user", "hi")]}, {"configurable": {"thread_id": "t1"}})
```

❌ Mistake 2: Using `MemorySaver` in production
✅ Correct: Use a database-backed saver; RAM memory is lost on restart and not shared between workers.

```python
# Wrong - 4 uvicorn workers = 4 separate memories, restart wipes everything
graph = builder.compile(checkpointer=MemorySaver())

# Right
from langgraph.checkpoint.postgres import PostgresSaver   # persistent, shared
# with PostgresSaver.from_conn_string(DB_URL) as saver: saver.setup(); graph = builder.compile(checkpointer=saver)
```

---

## 🧠 Tricky Interview Question

**Q**: "Your chatbot remembers history, but after two hours of chatting each reply takes longer and costs 10x more. The checkpointer is working fine. What is wrong?"

**Answer**: The checkpointer is *too* good: the full `messages` list is persisted and sent to the LLM every turn, so input tokens grow every turn. Memory is not the bug; unbounded history is. Fix: trim (`trim_messages`), summarise old turns and remove them with `RemoveMessage`, or send only the last N messages plus a running summary. Also prune old checkpoints in the DB, because every step stores a snapshot and the table grows quickly.

---

## ⚫ Interview Questions + Answers

Q1: What does a checkpointer do? (Easy)
A1: It saves graph state after each step, keyed by `thread_id`, so later runs continue from the saved state.

Q2: What is a `thread_id`? (Easy)
A2: A string in `config["configurable"]` that identifies one conversation. Same id = same memory; different id = separate memory.

Q3: What other features depend on checkpointers? (Medium)
A3: Human-in-the-loop (`interrupt` needs a saved state to resume from), time-travel (replay or fork from an old checkpoint), fault tolerance (resume after crash), and `get_state` / `update_state` inspection.

Q4: Checkpointer vs Store - difference? (Medium)
A4: A checkpointer holds per-thread state (short-term memory). A `Store` holds data shared across threads, such as user preferences or learned facts (long-term memory), usually namespaced by user id.

Q5: How would you design memory for 100k daily users on a tariff chatbot? (Hard)
A5: Use `PostgresSaver` (or Redis for speed) with connection pooling, namespaced thread ids bound to the authenticated user, a TTL/cleanup job for old checkpoints, message trimming plus summarisation to cap tokens, and a `Store` for durable user facts. Keep the app stateless so any worker can serve any thread. Encrypt sensitive data and avoid storing raw PII in state.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multi-turn chat or multi-step workflows
- Human approval pauses and resume
- Resume after failure; debugging with time-travel

❌ Avoid when:
- Single stateless request (a one-shot classify call)
- Very high-throughput jobs where per-step writes add latency and you do not need resume
- State contains secrets you must not persist

---

## 📊 Visual Diagram
```
Call 1 (thread A)        Call 2 (thread A)         Call 3 (thread B)
   │                        │                          │
   ▼                        ▼                          ▼
[load: none]             [load: ckpt#3]             [load: none]
   │                        │                          │
 run graph                run graph                  run graph
   │                        │                          │
[save ckpt#1,2,3] ──────► [save ckpt#4,5,6]          [save ckpt#1..]
          └────────────────────┘
        Checkpoint store (key = thread_id)
```

---

## 💰 Cost Impact
- The checkpointer makes no LLM calls, so it costs no tokens itself. Storage cost is small (KBs per step), but it grows with steps x threads.
- Hidden cost: persistent `messages` are replayed to the LLM each turn. A 30-turn chat at ~200 tokens per turn sends ~6,000 input tokens on the last turn.
- Optimise: `trim_messages(max_tokens=2000)`, rolling summary, store facts in typed fields, delete old checkpoints, and use prompt caching for the stable system prompt.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Checkpointer | Saves state snapshots | State snapshot save करने वाला |
| Checkpoint | One saved snapshot | एक saved snapshot |
| thread_id | Conversation identifier | Conversation की पहचान |
| MemorySaver | In-RAM saver for dev | RAM वाला saver |
| Time-travel | Replay/fork from old checkpoint | पुराने checkpoint से दोबारा चलाना |
| Store | Cross-thread long-term memory | थ्रेड्स के पार long-term memory |

---

## ⚡ 3-Line Summary
English: A checkpointer saves state after each step, keyed by `thread_id`, giving the graph memory across calls. It also powers resume, human-in-the-loop and time-travel. Use a DB saver in production and cap the history sent to the LLM.
Hindi: Checkpointer हर step के बाद `thread_id` के साथ state save करता है, जिससे graph को calls के बीच memory मिलती है। इसी पर resume, human-in-the-loop और time-travel चलते हैं। Production में DB saver लो और LLM को जाने वाली history सीमित रखो।

---

## ➡️ Next Topic
**333. Multi-Agent with LangGraph** — several specialised agents cooperating in one graph (topics 326-332 on savers, HITL and subgraphs are covered in their own notes).
