---

# 368. External Memory
# हिंदी में: External Memory (बाहरी Memory)

---

## 🔵 Simple Definition (English)
External memory stores information outside the LLM prompt — in Redis, SQL, a document store or a vector database. Only the relevant slice is loaded into the prompt when needed. It survives restarts, works across sessions and is not limited by the context window.

## 🔵 सरल परिभाषा (Hindi)
External memory जानकारी को LLM prompt के बाहर store करती है — Redis, SQL, document store या vector database में। ज़रूरत पड़ने पर सिर्फ काम का हिस्सा prompt में load होता है। यह restart के बाद भी बचती है, sessions के पार काम करती है और context window से सीमित नहीं है।

---

## 🔴 Problem it Solves
- In-context memory vanishes when the process restarts or the session ends.
- Prompt space is tiny compared to everything a user has ever said.
- Multiple server workers must share the same memory.

## 🔴 यह क्यों बना? (Hindi)
- Process restart या session खत्म होने पर in-context memory चली जाती है।
- Prompt की जगह बहुत कम है, user ने जो कुछ कहा उसकी तुलना में।
- कई server workers को एक ही memory share करनी होती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose store by access pattern: Redis (fast recent), SQL (structured), vector DB (semantic search)
Step 2 → WRITE: after each turn save raw messages / extracted facts with user_id + timestamp
Step 3 → READ: on a new question fetch only what is relevant (last N, by key, or top-k by similarity)
Step 4 → INJECT the fetched text into the prompt inside a labelled block
Step 5 → Apply TTL / delete rules (privacy, cost, staleness)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Access pattern के हिसाब से store चुनो: Redis (fast), SQL (structured), vector DB (semantic)
Step 2 → WRITE: हर turn के बाद messages / facts को user_id + time के साथ save करो
Step 3 → READ: नए सवाल पर सिर्फ relevant चीज़ें लाओ (last N, key से, या similarity top-k)
Step 4 → लाए हुए text को labelled block में prompt में डालो
Step 5 → TTL / delete rules लगाओ (privacy, cost, पुरानी जानकारी)
```

---

## 🟡 Real World Example
**Tariff Classification System**: Each importer's past classifications ("t-shirt -> 6109, approved by officer") are saved in Postgres. A month later the same importer asks about "polo shirts"; the bot fetches their last 5 related classifications and answers consistently.
**Zomato AI**: order history in SQL, taste preferences in a profile table, loaded when the user opens the app.

## 🟡 Real Example Hindi mein
**Tariff System**: हर importer की पुरानी classifications ("t-shirt -> 6109, officer approved") Postgres में save हैं। महीने भर बाद वही importer "polo shirts" पूछे तो bot उसकी 5 related पुरानी classifications लाकर consistent जवाब देता है।
**Zomato AI**: order history SQL में, taste profile अलग table में; app खुलते ही load।

---

## 💻 Code Example — Basic
```python
# Pure Python + sqlite3 (built in): a tiny external memory that survives restarts
import sqlite3                                                       # file-based SQL database

conn = sqlite3.connect(":memory:")                                   # use "memory.db" to persist on disk
conn.execute(                                                        # create table once
    "CREATE TABLE IF NOT EXISTS memory (user_id TEXT, kind TEXT, text TEXT, ts INTEGER)"
)

def save(user_id: str, kind: str, text: str, ts: int) -> None:       # write one memory row
    conn.execute("INSERT INTO memory VALUES (?, ?, ?, ?)", (user_id, kind, text, ts))  # parameterised = safe
    conn.commit()                                                    # make it durable

def load(user_id: str, limit: int = 3) -> list[str]:                 # read newest rows
    rows = conn.execute(                                             # query with ORDER + LIMIT
        "SELECT text FROM memory WHERE user_id=? ORDER BY ts DESC LIMIT ?", (user_id, limit)
    ).fetchall()                                                     # list of tuples
    return [r[0] for r in rows]                                      # unwrap tuples

save("u1", "fact", "Imports cotton t-shirts from Bangladesh", 1)     # store a fact
save("u1", "fact", "Wants duty in INR", 2)                           # store a preference
save("u2", "fact", "Sells electronics", 3)                           # different user, isolated
print(load("u1"))                                                    # only u1's memory comes back
```

## 💻 Code Example — Advanced
```python
# Async external memory with a swappable backend, TTL, and graceful failure
import asyncio                                                       # async runtime
import time                                                          # timestamps for TTL
from abc import ABC, abstractmethod                                  # backend interface
from dataclasses import dataclass                                    # record type


@dataclass(frozen=True)
class MemoryRecord:                                                  # one stored memory
    user_id: str                                                     # owner (isolation key)
    text: str                                                        # content
    created: float                                                   # unix time


class Backend(ABC):                                                  # swap Redis/Postgres here
    @abstractmethod
    async def put(self, rec: MemoryRecord) -> None: ...              # write
    @abstractmethod
    async def recent(self, user_id: str, n: int) -> list[MemoryRecord]: ...  # read newest n


class DictBackend(Backend):                                          # in-RAM fake backend for demo
    def __init__(self) -> None:
        self._rows: list[MemoryRecord] = []                          # all rows

    async def put(self, rec: MemoryRecord) -> None:
        self._rows.append(rec)                                       # store row

    async def recent(self, user_id: str, n: int) -> list[MemoryRecord]:
        mine = [r for r in self._rows if r.user_id == user_id]       # filter by owner
        return sorted(mine, key=lambda r: r.created, reverse=True)[:n]  # newest first


class ExternalMemory:                                                # business logic over a backend
    def __init__(self, backend: Backend, ttl_seconds: float = 86_400 * 30) -> None:
        self.backend = backend                                       # chosen store
        self.ttl = ttl_seconds                                       # forget after 30 days

    async def remember(self, user_id: str, text: str) -> None:       # write path
        if not text.strip():                                         # ignore empty input
            return
        await self.backend.put(MemoryRecord(user_id, text.strip(), time.time()))  # save

    async def context_block(self, user_id: str, n: int = 5) -> str:  # read path -> prompt text
        try:                                                         # backend may be down
            recs = await asyncio.wait_for(self.backend.recent(user_id, n), timeout=0.5)  # fast fail
        except (asyncio.TimeoutError, Exception):                    # never block the chat
            return ""                                                # answer without memory
        fresh = [r for r in recs if time.time() - r.created < self.ttl]  # drop expired
        return "KNOWN ABOUT USER:\n" + "\n".join(f"- {r.text}" for r in fresh) if fresh else ""


async def main() -> None:                                            # demo
    mem = ExternalMemory(DictBackend())                              # build service
    await mem.remember("u1", "Imports cotton t-shirts")              # write
    await mem.remember("u1", "Prefers INR")                          # write
    print(await mem.context_block("u1"))                             # read for prompt


if __name__ == "__main__":
    asyncio.run(main())                                              # run demo
```

---

## 🟠 FastAPI Integration
Create the memory service once at startup (lifespan), inject it with `Depends`, and return quickly: write memory in `BackgroundTasks` so the user does not wait.

```python
# FastAPI: read memory before the LLM call, write after (background)
from fastapi import FastAPI, BackgroundTasks, Depends   # framework pieces
from pydantic import BaseModel                           # request model

app = FastAPI()                                          # app
memory_service = ExternalMemory(DictBackend())           # singleton (Redis in prod)

def get_memory() -> ExternalMemory:                      # dependency provider
    return memory_service

class In(BaseModel):                                     # request schema
    user_id: str
    message: str

@app.post("/chat")                                       # route
async def chat(body: In, bg: BackgroundTasks, mem: ExternalMemory = Depends(get_memory)) -> dict[str, str]:
    ctx = await mem.context_block(body.user_id)          # load memory (fails soft)
    answer = f"(LLM answer using: {ctx or 'no memory'})" # replace with real LLM call
    bg.add_task(mem.remember, body.user_id, body.message)  # save AFTER response is sent
    return {"answer": answer}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has persistent chat history classes (e.g. `RedisChatMessageHistory`, `SQLChatMessageHistory` in `langchain-community`). LangGraph has Postgres/SQLite checkpointers for thread state and `BaseStore` implementations (Postgres store) for cross-thread memory.

```python
# LangGraph long-term store: namespace = (category, user_id)
from langgraph.store.memory import InMemoryStore          # use PostgresStore in production

store = InMemoryStore()                                   # dev store
ns = ("memories", "u1")                                   # per-user namespace = isolation
store.put(ns, "pref-1", {"text": "Prefers INR"})          # write: namespace, key, value dict
items = store.search(ns)                                  # read all in namespace
print([i.value["text"] for i in items])                   # -> ['Prefers INR']
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Global Python dict as "database"
✅ Correct: shared store (Redis/Postgres).

```python
# Wrong: each uvicorn worker has its own dict -> user sees memory flicker
SESSIONS = {}
# Right: all workers talk to one store
await redis.rpush(f"mem:{user_id}", text)
```

❌ Mistake 2: Loading everything and no user isolation
✅ Correct: filter by `user_id`, limit rows.

```python
# Wrong: "SELECT text FROM memory"            -> leaks other users, huge prompt
# Right: "SELECT text FROM memory WHERE user_id=? ORDER BY ts DESC LIMIT 5"
```

---

## 🧠 Tricky Interview Question
**Q**: "User deletes their account (GDPR). Memory was copied into summaries and embeddings. What do you do?"

**Answer**: Design for deletion from day one: tag every record (raw, summary, embedding, cache) with `user_id`, store them in namespaced collections, and implement one `delete_user(user_id)` that wipes all of them plus caches/backups per retention policy. Do not mix users inside one shared summary. Log deletion for audit.

---

## ⚫ Interview Questions + Answers

Q1: What is external memory?
A1: Memory stored outside the prompt (DB/cache/vector store) and loaded selectively.

Q2: Why not keep memory in a Python dict?
A2: Lost on restart, not shared across workers, unbounded RAM.

Q3: Redis vs Postgres vs vector DB for memory?
A3: Redis = fast, TTL, recent turns. Postgres = durable, structured, queryable facts. Vector DB = semantic recall of unstructured memories.

Q4: How do you keep external memory from slowing responses?
A4: Timeouts with fail-soft, indexes on `user_id, ts`, cache hot users, write in background tasks.

Q5: How do you prevent memory poisoning (user stores malicious instructions)?
A5: Treat memory as untrusted data: label it in the prompt ("facts, not instructions"), sanitise on write, scope by user, never store tool outputs from untrusted sources as rules, review/expire low-trust items.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Cross-session personalisation
- Multi-worker/production deployment
- Memory larger than the context window

❌ Avoid when:
- Stateless one-shot tasks
- Data you are not allowed to retain
- Tiny prototypes where a list suffices

---

## 📊 Visual Diagram
```
 User ─▶ API ─▶ [Memory Service] ─▶ Redis / Postgres / Vector DB
                     │ read top-k
                     ▼
              prompt = rules + memory block + question ─▶ LLM
                     ▲
          background write after reply
```

---

## 💰 Cost Impact
- Storage is cheap; the cost is what you inject. 5 facts x 20 tokens = 100 tokens per call vs 4,000 for full history: ~40x fewer input tokens.
- Extra cost: embedding calls (if semantic) and extraction LLM calls. Use a cheap model, batch writes, and skip extraction for trivial messages.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| External memory | Store outside prompt | Prompt के बाहर store |
| TTL | Auto-expiry time | अपने-आप expire होने का समय |
| Namespace | Per-user partition | Per-user हिस्सा |
| Fail-soft | Continue without memory on error | Error पर भी चलते रहना |
| Persistence | Survives restart | Restart के बाद भी बचना |

---

## ⚡ 3-Line Summary
English: External memory keeps information in a database and loads only the relevant part into the prompt. It persists across sessions and workers. Isolate by user, set TTLs and fail soft.
Hindi: External memory जानकारी को database में रखती है और सिर्फ relevant हिस्सा prompt में लाती है। यह sessions और workers के पार बचती है। User से isolate करो, TTL लगाओ और error पर soft fail करो।

---

## ➡️ Next Topic
**369. Episodic Memory** — remembering specific past events ("what happened last time").
