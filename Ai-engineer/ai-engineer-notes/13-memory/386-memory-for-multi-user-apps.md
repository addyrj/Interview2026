---

# 386. Memory for Multi-User Apps
# हिंदी में: Multi-User Apps के लिए Memory

---

## 🔵 Simple Definition (English)
Multi-user memory means every user (and every conversation of that user) gets its own isolated memory. The app stores memory under keys like `tenant_id + user_id + thread_id`, so User A's chat history never leaks into User B's prompt. One server, many users, zero mixing.

## 🔵 सरल परिभाषा (Hindi)
Multi-user memory का मतलब है कि हर user (और उसकी हर conversation) की अपनी अलग memory हो। App memory को `tenant_id + user_id + thread_id` जैसी key के नीचे store करता है, ताकि User A की chat User B के prompt में कभी न जाए। एक server, बहुत सारे users, कोई mixing नहीं।

---

## 🔴 Problem it Solves
A beginner stores chat history in a global Python list. It works on a laptop with one tester. In production, 500 customs brokers use the Tariff Classification System at once, and the global list mixes their conversations. Broker A sees Broker B's shipment details in the answer. Also, a server restart wipes everything, and two server replicas do not share the list.

## 🔴 यह क्यों बना? (Hindi)
Beginner chat history को एक global Python list में रखता है। Laptop पर एक tester के साथ ये चलता है। Production में 500 customs brokers एक साथ Tariff System use करते हैं और global list सबकी बातें mix कर देती है। Broker A को Broker B की shipment details दिख जाती हैं। Server restart पर सब मिट जाता है और दो replicas एक list share नहीं करते।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Request arrives with auth token (JWT) → server extracts user_id + tenant_id
Step 2 → Build memory key: f"{tenant_id}:{user_id}:{thread_id}"
Step 3 → Load only that key's messages from the store (Redis / Postgres / in-memory dict)
Step 4 → Trim to a token budget (last N messages or last N tokens)
Step 5 → Send [system + trimmed history + new question] to the LLM
Step 6 → Append the new user + assistant messages back under the SAME key
Step 7 → Set a TTL (expiry) so old threads do not grow forever
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Request में auth token आता है → server user_id + tenant_id निकालता है
Step 2 → Memory key बनाओ: f"{tenant_id}:{user_id}:{thread_id}"
Step 3 → Store (Redis / Postgres / dict) से सिर्फ उसी key के messages load करो
Step 4 → Token budget के हिसाब से trim करो (last N messages)
Step 5 → [system + trimmed history + नया सवाल] LLM को भेजो
Step 6 → नए user + assistant messages उसी key में वापस जोड़ो
Step 7 → TTL लगाओ ताकि पुराने threads हमेशा न बढ़ें
```

---

## 🟡 Real World Example
**Tariff Classification System**: Broker Ravi asks "HS code for lithium batteries?" in thread `t1`. Later he asks "and for the 5 kg pack?". Because memory is keyed by `acme:ravi:t1`, the model knows "the 5 kg pack" means lithium batteries. At the same moment broker Sara (tenant `globex`) classifies textiles. Her memory key is `globex:sara:t9`, so nothing crosses over.

**Zomato AI**: The food assistant remembers "I am vegetarian" for each customer separately. If memory were shared, one user's allergy would change recommendations for everybody.

## 🟡 Real Example Hindi mein
**Tariff System**: Broker रवि thread `t1` में पूछता है "lithium batteries का HS code?" फिर पूछता है "और 5 kg pack का?"। Memory key `acme:ravi:t1` होने से model समझ जाता है कि "5 kg pack" का मतलब lithium batteries है। उसी समय सारा (tenant `globex`) textiles classify कर रही है। उसकी key `globex:sara:t9` है, इसलिए कुछ भी आपस में नहीं मिलता।

**Zomato AI**: Food assistant हर customer के लिए अलग याद रखता है कि "मैं vegetarian हूँ"। Memory shared होती तो एक user की allergy सबकी recommendations बदल देती।

---

## 💻 Code Example — Basic
```python
# Basic: per-user memory using a plain dict (no external libraries needed)
from collections import defaultdict            # dict that creates missing keys automatically
from typing import TypedDict                   # type hints for message shape


class Message(TypedDict):                      # one chat message
    role: str                                  # "user" or "assistant"
    content: str                               # the text


# store maps memory_key -> list of messages
store: dict[str, list[Message]] = defaultdict(list)


def make_key(tenant_id: str, user_id: str, thread_id: str) -> str:
    """Build the isolation key. Every part is required."""
    if not tenant_id or not user_id or not thread_id:      # empty part = leak risk
        raise ValueError("tenant_id, user_id and thread_id are all required")
    return f"{tenant_id}:{user_id}:{thread_id}"            # unique per conversation


def add_message(key: str, role: str, content: str) -> None:
    """Append a message to one user's history."""
    store[key].append({"role": role, "content": content})  # only touches this key


def get_history(key: str, last_n: int = 6) -> list[Message]:
    """Return the last N messages for one key (simple trimming)."""
    return store[key][-last_n:]                            # slice keeps newest N


# --- demo: two users, no mixing ---
k1 = make_key("acme", "ravi", "t1")                        # Ravi's thread
k2 = make_key("globex", "sara", "t9")                      # Sara's thread
add_message(k1, "user", "HS code for lithium batteries?")  # Ravi asks
add_message(k2, "user", "HS code for cotton shirts?")      # Sara asks
print(get_history(k1))                                     # only Ravi's message
print(get_history(k2))                                     # only Sara's message
assert get_history(k1) != get_history(k2)                  # isolation check
```

## 💻 Code Example — Advanced
```python
# Advanced: async memory manager with token budget, TTL and per-key locks
import asyncio                                  # async primitives (Lock, sleep)
import time                                     # for TTL timestamps
from dataclasses import dataclass, field        # compact data classes
from typing import Protocol                     # interface for swappable stores


@dataclass
class Thread:
    """One conversation thread with expiry metadata."""
    messages: list[dict[str, str]] = field(default_factory=list)   # chat history
    updated_at: float = field(default_factory=time.time)           # last write time


class MemoryStore(Protocol):
    """Any backend (Redis, Postgres) must implement these two async methods."""
    async def load(self, key: str) -> Thread | None: ...
    async def save(self, key: str, thread: Thread) -> None: ...


class InMemoryStore:
    """Dev backend. In production replace with Redis/Postgres, same interface."""

    def __init__(self) -> None:
        self._data: dict[str, Thread] = {}      # key -> Thread

    async def load(self, key: str) -> Thread | None:
        return self._data.get(key)              # None when key is new

    async def save(self, key: str, thread: Thread) -> None:
        self._data[key] = thread                # overwrite with latest state


def approx_tokens(text: str) -> int:
    """Cheap token estimate: ~4 characters per token (use tiktoken in prod)."""
    return max(1, len(text) // 4)


class MultiUserMemory:
    """Isolated, bounded, expiring memory for many users."""

    def __init__(self, store: MemoryStore, max_tokens: int = 1500, ttl_s: int = 3600) -> None:
        self.store = store                              # backend
        self.max_tokens = max_tokens                    # history budget per call
        self.ttl_s = ttl_s                              # expiry in seconds
        self._locks: dict[str, asyncio.Lock] = {}       # one lock per key

    def _lock(self, key: str) -> asyncio.Lock:
        return self._locks.setdefault(key, asyncio.Lock())   # create on first use

    async def history(self, key: str) -> list[dict[str, str]]:
        """Load history, drop it if expired, trim to token budget."""
        thread = await self.store.load(key)             # fetch this key only
        if thread is None:                              # new conversation
            return []
        if time.time() - thread.updated_at > self.ttl_s:  # expired -> forget
            await self.store.save(key, Thread())
            return []
        kept: list[dict[str, str]] = []                 # newest-first accumulation
        used = 0                                        # tokens used so far
        for msg in reversed(thread.messages):           # walk from newest to oldest
            cost = approx_tokens(msg["content"])        # tokens of this message
            if used + cost > self.max_tokens:           # budget exceeded -> stop
                break
            kept.append(msg)                            # keep it
            used += cost                                # update budget
        return list(reversed(kept))                     # restore chronological order

    async def append(self, key: str, role: str, content: str) -> None:
        """Safely append a message (lock prevents lost updates on same thread)."""
        async with self._lock(key):                     # serialise writes per key
            thread = await self.store.load(key) or Thread()
            thread.messages.append({"role": role, "content": content})
            thread.updated_at = time.time()             # refresh TTL
            await self.store.save(key, thread)


async def main() -> None:
    mem = MultiUserMemory(InMemoryStore(), max_tokens=50)       # tiny budget for demo
    key = "acme:ravi:t1"                                        # isolation key
    try:
        await asyncio.gather(                                   # concurrent writes, no loss
            mem.append(key, "user", "HS code for lithium batteries?"),
            mem.append(key, "assistant", "8507.60 - lithium-ion accumulators."),
        )
        print(await mem.history(key))                           # trimmed history
    except Exception as exc:                                    # backend failure must not crash chat
        print(f"memory error, continuing stateless: {exc}")


asyncio.run(main())                                             # run the demo
```

---

## 🟠 FastAPI Integration
The user id must come from the authenticated token, never from the request body (otherwise anyone can pass `user_id=ravi` and read his memory).

```python
# FastAPI route: memory scoped by authenticated identity
from fastapi import Depends, FastAPI, Header, HTTPException   # web framework pieces
from pydantic import BaseModel                                 # request validation

app = FastAPI()                                                # app instance
memory = MultiUserMemory(InMemoryStore())                      # from the advanced example


class AskBody(BaseModel):
    question: str                                              # user's question
    thread_id: str = "default"                                 # conversation id


def current_user(authorization: str = Header(...)) -> tuple[str, str]:
    """Decode token -> (tenant, user). Demo parser; use real JWT verification in prod."""
    try:
        tenant, user = authorization.removeprefix("Bearer ").split(":")   # "acme:ravi"
    except ValueError:
        raise HTTPException(status_code=401, detail="bad token")
    return tenant, user


@app.post("/ask")
async def ask(body: AskBody, who: tuple[str, str] = Depends(current_user)) -> dict:
    key = f"{who[0]}:{who[1]}:{body.thread_id}"                # identity from token only
    history = await memory.history(key)                        # this user's history
    answer = f"(LLM answer using {len(history)} past messages)"  # replace with real LLM call
    await memory.append(key, "user", body.question)            # save question
    await memory.append(key, "assistant", answer)              # save answer
    return {"answer": answer, "history_used": len(history)}
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph has this built in. A checkpointer saves state per `thread_id`; add `user_id` into the thread id (or use the Store API for cross-thread user facts).

```python
# LangGraph: per-thread memory with a checkpointer
from langgraph.graph import StateGraph, MessagesState, START   # graph building blocks
from langgraph.checkpoint.memory import MemorySaver            # in-memory checkpointer (dev)


def chatbot(state: MessagesState) -> dict:
    # a real node would call an LLM; here we echo to keep it runnable offline
    return {"messages": [("assistant", f"I have {len(state['messages'])} messages")]}


builder = StateGraph(MessagesState)                            # state = list of messages
builder.add_node("chatbot", chatbot)                           # one node
builder.add_edge(START, "chatbot")                             # entry point
graph = builder.compile(checkpointer=MemorySaver())            # attach memory

cfg_ravi = {"configurable": {"thread_id": "acme:ravi:t1"}}     # Ravi's thread
cfg_sara = {"configurable": {"thread_id": "globex:sara:t9"}}   # Sara's thread
graph.invoke({"messages": [("user", "hi")]}, cfg_ravi)         # Ravi talks
graph.invoke({"messages": [("user", "hello")]}, cfg_sara)      # Sara talks, separate state
# In production use PostgresSaver / RedisSaver instead of MemorySaver.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Global history list shared by all users
✅ Correct: One list per `tenant:user:thread` key.

```python
# Wrong - everyone shares one list
history = []
def chat(q): history.append(q); return history

# Right - isolated by key
store: dict[str, list[str]] = {}
def chat_safe(key: str, q: str) -> list[str]:
    store.setdefault(key, []).append(q)
    return store[key]
```

❌ Mistake 2: Trusting `user_id` sent by the client
✅ Correct: Derive identity from the verified token on the server.

```python
# Wrong - attacker sends {"user_id": "ravi"}
key = f"{body.user_id}:{body.thread_id}"
# Right - identity comes from auth dependency
key = f"{who[0]}:{who[1]}:{body.thread_id}"
```

❌ Mistake 3: Unlimited history (cost grows every turn, eventually context overflow)
✅ Correct: Trim by token budget and set a TTL.

---

## 🧠 Tricky Interview Question

**Q**: "Your chatbot runs on 4 server pods behind a load balancer. Users complain the bot forgets context randomly. Memory is a Python dict. Why, and how do you fix it without sticky sessions?"

**Answer**: Each pod has its own dict, so a request that lands on a different pod sees empty memory. Fix: move memory to a shared external store (Redis for fast TTL-based chat memory, Postgres for durable memory), keyed by `tenant:user:thread`. Then any pod can serve any request, which is stateless compute with stateful storage. Sticky sessions are a fragile workaround: they break on pod restarts and uneven load.

---

## ⚫ Interview Questions + Answers

Q1: Why do we need a thread_id as well as user_id?
A1: One user can have many separate conversations. `thread_id` separates them so a question about lithium batteries does not pollute a separate chat about textiles. `user_id` groups threads for long-term facts.

Q2: Why not store chat history in the browser only?
A2: The client can tamper with it, and it is lost on device change. Server-side memory is trusted, shareable across devices, and can be audited. Small apps may still send the history from the client but must validate it.

Q3: How do you choose between Redis and Postgres for chat memory?
A3: Redis: very fast, native TTL, good for short-term session memory. Postgres: durable, queryable, good for long-term profile facts and audit. Many systems use both: Redis for the active window, Postgres for summaries and facts.

Q4: How do you handle two requests from the same thread at the same time?
A4: Use a per-key lock or optimistic versioning so appends do not overwrite each other (lost update). LangGraph checkpointers handle this per thread. Without it, messages can disappear or reorder.

Q5 (Hard): Design memory for 1M users where each user has 50 threads. What do you store and how do you control cost?
A5: Keep only a recent window per active thread in Redis with TTL. Run background summarization that compresses old turns into a short summary stored in Postgres. Store durable user facts (preferences) separately as small records. On each call send: system prompt + user facts + thread summary + last few messages, all under a token cap. This keeps prompt size flat instead of growing with each turn, so cost per request stays roughly constant. Add per-tenant partitioning, encryption at rest, and a delete-by-user job for privacy requests.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- More than one user can hit the app at the same time
- Conversations continue across several requests
- You run multiple server replicas

❌ Avoid when:
- Each request is fully independent (one-shot classification API); memory only adds cost
- You cannot guarantee identity (anonymous traffic with no session id)

---

## 📊 Visual Diagram
```
 Ravi (acme) ──┐                       ┌─────────────────────────────┐
 Sara (globex)─┼─► Load Balancer ─► Pod 1/2/3 ─►│  Shared Store (Redis/PG)    │
 Amit (acme) ──┘        │                       │ acme:ravi:t1   [msgs...]    │
                        │ JWT -> tenant,user    │ globex:sara:t9 [msgs...]    │
                        ▼                       │ acme:amit:t2   [msgs...]    │
                 key = tenant:user:thread       └─────────────────────────────┘
                        │
                        ▼
        [system + trimmed history of THAT key + question] ─► LLM
```

---

## 💰 Cost Impact
- Every stored message you resend is billed as input tokens on EVERY turn. A 20-turn thread of ~100 tokens per message resends ~2000 tokens per call.
- With gpt-4o-mini at $0.15 per 1M input tokens, 2000 extra tokens x 100K calls/day = 200M tokens = about $30/day just for history.
- Optimise: trim to a token budget (e.g. 1500), summarise old turns, set TTL, and cache the stable system prompt (provider prompt caching reduces repeated-prefix cost).
- Storage cost (Redis/Postgres) is tiny compared with the token cost of resending history.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tenant | A customer organisation using your app | आपके app का customer organisation |
| thread_id | Id of one conversation | एक conversation की id |
| Isolation | Users cannot see each other's data | Users एक दूसरे का data नहीं देख सकते |
| TTL | Time after which memory expires | Memory कब खत्म होगी |
| Checkpointer | LangGraph component that saves state | State save करने वाला component |
| Token budget | Max history tokens per call | History के लिए token limit |

---

## ⚡ 3-Line Summary
English: Key memory by tenant, user and thread so users never see each other's data. Take identity from the verified token and keep memory in a shared store, not in process RAM. Trim and expire history to control token cost.
Hindi: Memory को tenant, user और thread की key से रखो ताकि users का data कभी न मिले। Identity verified token से लो और memory को shared store में रखो, process RAM में नहीं। History trim और expire करो ताकि token cost कंट्रोल में रहे।

---

## ➡️ Next Topic
**387. Memory Security + Privacy** — now that memory is isolated, protect it: PII redaction, encryption, prompt-injection into memory, and the right to delete.
