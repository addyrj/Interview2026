---

# 362. Multi-Agent Memory
# हिंदी में: Multi-Agent Memory

---

## 🔵 Simple Definition (English)
Multi-agent memory is how a group of agents **stores and recalls information** across steps, runs and users. It has layers: private working memory per agent, shared team memory (state), and long-term memory (database or vector store) with clear rules about who can read and write what.

## 🔵 सरल परिभाषा (Hindi)
Multi-agent memory वह तरीका है जिससे agents का समूह steps, runs और users के बीच **जानकारी सहेजता और याद करता है**। इसकी परतें होती हैं: हर agent की निजी working memory, साझा team memory (state), और long-term memory (database या vector store), जिसमें साफ़ नियम होते हैं कि कौन क्या पढ़-लिख सकता है।

---

## 🔴 Problem it Solves
LLMs are stateless. In a multi-agent system, each agent has its own prompt and no automatic knowledge of what others learned. Without memory design, agents repeat work, contradict earlier decisions, forget user preferences between sessions, or leak one user's data to another. Memory must be scoped, searchable and bounded.

## 🔴 यह क्यों बना? (Hindi)
LLMs stateless होते हैं। Multi-agent system में हर agent का अपना prompt होता है और दूसरों ने क्या सीखा, यह अपने आप नहीं पता। Memory design न हो तो agents काम दोहराते हैं, पुराने फैसलों से टकराते हैं, sessions के बीच user की पसंद भूल जाते हैं, या एक user का data दूसरे को दिख जाता है। Memory का दायरा तय, खोजने योग्य और सीमित होना चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decide memory layers: private (agent), shared (run), long-term (user/org)
Step 2 → Each memory item gets metadata: owner, scope, user_id, timestamp
Step 3 → During a run, agents write facts/decisions to the right layer
Step 4 → Before each LLM call, retrieve only relevant memories (search + filter)
Step 5 → Inject a few memories into the prompt, not the whole store
Step 6 → At run end, consolidate: summarise, dedupe, promote important facts
Step 7 → Apply TTL / size limits and delete outdated items
Step 8 → Enforce access control and per-user isolation
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Memory की परतें तय करो: private (agent), shared (run), long-term (user/org)
Step 2 → हर item में metadata: owner, scope, user_id, timestamp
Step 3 → Run के दौरान agents facts/decisions सही परत में लिखते हैं
Step 4 → हर LLM call से पहले सिर्फ relevant memories खोजो (search + filter)
Step 5 → Prompt में कुछ ही memories डालो, पूरा store नहीं
Step 6 → Run के अंत में consolidate: summarise, dedupe, ज़रूरी facts को ऊपर उठाओ
Step 7 → TTL / size limits लगाओ और पुराने items हटाओ
Step 8 → Access control और हर user का अलगाव लागू करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: An importer, ABC Traders, always ships "LED lighting" and prefers duty drawback reports. Long-term memory stores: `{user: abc, fact: "ships LED lighting", scope: org}`. During a run, the Classifier writes its decision to shared memory (`hs_code=9405.42`); the DutyAgent reads it. The Compliance agent keeps private notes. Next month, the Classifier recalls past rulings for ABC and stays consistent. Another importer never sees ABC's data.

**Swiggy-style**: Remember a user's veg preference (long-term), the current cart (shared), and an agent's scratch calculations (private).

## 🟡 Real Example Hindi mein
**Tariff System**: Importer ABC Traders हमेशा "LED lighting" भेजता है और duty drawback reports पसंद करता है। Long-term memory में रखा जाता है: `{user: abc, fact: "ships LED lighting", scope: org}`। Run के दौरान Classifier अपना फैसला shared memory में लिखता है (`hs_code=9405.42`); DutyAgent उसे पढ़ता है। Compliance agent अपने निजी notes रखता है। अगले महीने Classifier ABC के पुराने फैसले याद करके एकरूप रहता है। दूसरे importer को ABC का data कभी नहीं दिखता।

**Swiggy-style**: User की veg पसंद (long-term), मौजूदा cart (shared) और agent की अस्थायी गणनाएँ (private) याद रखना।

---

## 💻 Code Example — Basic
```python
# Layered memory store with scopes and keyword recall (runs offline)
from dataclasses import dataclass, field  # light data containers
import time  # timestamps for TTL

@dataclass
class MemoryItem:
    text: str                      # the fact
    scope: str                     # "private" | "shared" | "long_term"
    owner: str                     # agent that wrote it
    user_id: str                   # whose data this is
    ts: float = field(default_factory=time.time)  # creation time

class MemoryStore:
    def __init__(self) -> None:
        self.items: list[MemoryItem] = []  # in-memory list (use a DB in production)

    def write(self, item: MemoryItem) -> None:
        self.items.append(item)  # store the item

    def recall(self, agent: str, user_id: str, query: str, k: int = 3) -> list[str]:
        words = set(query.lower().split())  # query words
        visible = [
            m for m in self.items
            if m.user_id == user_id                                   # per-user isolation
            and (m.scope != "private" or m.owner == agent)            # private only to owner
        ]
        scored = sorted(visible, key=lambda m: len(words & set(m.text.lower().split())), reverse=True)  # keyword score
        return [m.text for m in scored[:k] if words & set(m.text.lower().split())]  # top-k that match

if __name__ == "__main__":
    mem = MemoryStore()
    mem.write(MemoryItem("abc ships LED lighting", "long_term", "classifier", "abc"))
    mem.write(MemoryItem("hs_code 9405.42 chosen", "shared", "classifier", "abc"))
    mem.write(MemoryItem("unsure about LED driver", "private", "compliance", "abc"))
    mem.write(MemoryItem("xyz ships toys", "long_term", "classifier", "xyz"))
    print(mem.recall("duty", "abc", "LED hs_code"))        # sees shared + long_term, not private, not xyz
    print(mem.recall("compliance", "abc", "LED driver"))   # sees its own private note
```

## 💻 Code Example — Advanced
```python
# Async memory manager: embedding recall (stubbed), TTL, size cap and consolidation
import asyncio  # async runtime
import math  # cosine similarity
import time  # TTL

Vector = list[float]  # embedding type alias

async def embed(text: str) -> Vector:
    await asyncio.sleep(0)  # real code: await client.embeddings.create(...)
    return [float(text.count(c)) for c in "aeiou "]  # tiny fake embedding

def cosine(a: Vector, b: Vector) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0

class VectorMemory:
    def __init__(self, ttl_s: float = 86400, max_items: int = 1000) -> None:
        self.rows: list[dict] = []   # {text, vec, user_id, scope, owner, ts}
        self.ttl_s, self.max_items = ttl_s, max_items
        self._lock = asyncio.Lock()  # safe concurrent writes

    async def add(self, text: str, user_id: str, scope: str, owner: str) -> None:
        vec = await embed(text)      # compute outside the lock
        async with self._lock:
            self.rows.append({"text": text, "vec": vec, "user_id": user_id, "scope": scope, "owner": owner, "ts": time.time()})
            self.rows.sort(key=lambda r: r["ts"])           # oldest first
            self.rows = self.rows[-self.max_items:]          # size cap

    async def search(self, query: str, user_id: str, agent: str, k: int = 3) -> list[str]:
        qv = await embed(query)
        now = time.time()
        async with self._lock:
            pool = [r for r in self.rows
                    if r["user_id"] == user_id                                  # isolation
                    and now - r["ts"] < self.ttl_s                              # TTL
                    and (r["scope"] != "private" or r["owner"] == agent)]       # privacy
        pool.sort(key=lambda r: cosine(qv, r["vec"]), reverse=True)
        return [r["text"] for r in pool[:k]]

async def main() -> None:
    vm = VectorMemory()
    await vm.add("abc ships LED lighting", "abc", "long_term", "classifier")
    await vm.add("prefers duty drawback report", "abc", "long_term", "reporter")
    print(await vm.search("what does abc ship", "abc", "duty"))

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Always derive `user_id` from the authenticated session, never from the request body, to prevent cross-user leaks.

```python
from fastapi import Depends, FastAPI, Header, HTTPException  # framework pieces
from pydantic import BaseModel  # models

app = FastAPI()
memory = VectorMemory()  # one per process; use Redis/Postgres + pgvector in production

async def current_user(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "missing token")
    return authorization.removeprefix("Bearer ").split(":")[0]  # demo only: decode a real JWT instead

class Fact(BaseModel):
    text: str    # fact to remember

@app.post("/memory")
async def remember(fact: Fact, user_id: str = Depends(current_user)) -> dict:
    await memory.add(fact.text, user_id, "long_term", "api")
    return {"ok": True}

@app.get("/memory/search")
async def search(q: str, user_id: str = Depends(current_user)) -> dict:
    return {"results": await memory.search(q, user_id, "api")}
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph separates **short-term memory** (graph state, saved by a checkpointer per `thread_id`) from **long-term memory** (a `Store` shared across threads, organised by namespaces such as `("memories", user_id)`).

```python
from langgraph.checkpoint.memory import MemorySaver  # short-term (per thread)
from langgraph.store.memory import InMemoryStore  # long-term store (use a DB-backed store in production)
from langgraph.graph import StateGraph, MessagesState, START, END  # graph

store = InMemoryStore()  # shared across threads

def classifier(state: MessagesState, *, store) -> dict:  # store is injected when compiled with store=
    ns = ("memories", "abc")  # namespace = per user isolation
    store.put(ns, "pref1", {"text": "ships LED lighting"})  # write a long-term memory
    past = store.search(ns)  # read all (or pass query= with an embedding index)
    return {"messages": [("assistant", f"I recall {len(past)} facts about this importer.")]}

g = StateGraph(MessagesState)
g.add_node("classifier", classifier)
g.add_edge(START, "classifier")
g.add_edge("classifier", END)
app_graph = g.compile(checkpointer=MemorySaver(), store=store)
# app_graph.invoke({"messages": [("user", "hi")]}, {"configurable": {"thread_id": "t1"}})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: One global memory for all users
✅ Correct: always filter by `user_id` (or namespace).

```python
# Wrong
results = store.search(query)
# Right
results = store.search(query, user_id=session_user)
```

❌ Mistake 2: Dumping all memories into every prompt
✅ Correct: retrieve top-k relevant memories only.

```python
# Wrong
prompt = "Memories:\n" + "\n".join(all_memories)
# Right
prompt = "Memories:\n" + "\n".join(await memory.search(question, user_id, agent, k=3))
```

---

## 🧠 Tricky Interview Question
**Q**: "A user corrected a fact two weeks ago, but the agent keeps using the old fact. Why, and how do you design memory to prevent it?"

**Answer**: Memory is append-only and the old fact still ranks high in retrieval. Fix with update semantics: store facts under stable keys and overwrite, keep `updated_at` and prefer newer, mark superseded items as inactive, run a consolidation job that resolves contradictions, and let user corrections have higher priority. Add tests where a fact changes.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Why do agents need memory?
A1: LLMs are stateless, so memory carries facts, decisions and preferences across steps and sessions.

Q2: [Easy] Name three memory scopes.
A2: Private (one agent), shared (team or run), long-term (user or organisation).

Q3: [Medium] Short-term vs long-term memory in LangGraph?
A3: Short-term is graph state saved by a checkpointer per thread. Long-term is a Store shared across threads, organised by namespaces.

Q4: [Medium] How do you stop memory leaks between users?
A4: Namespace every item by user or tenant, take identity from authentication, filter at query time, and test isolation.

Q5: [Hard] How do you keep memory from growing forever and filling prompts with junk?
A5: TTLs, size caps, importance scoring, summarisation and dedupe jobs, retrieval limited to top-k with a similarity threshold, and periodic evaluation of recall quality.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Agents repeat across sessions or users return
- Several agents must stay consistent
- Personalisation matters

❌ Avoid when:
- One-shot tasks
- Data is sensitive and not allowed to be stored (compliance)

---

## 📊 Visual Diagram
```
                 LONG-TERM (DB / vector store, per user namespace)
                 +-------------------------------------------+
                 | "abc ships LED"   "prefers drawback"       |
                 +----------------------^--------------------+
                       recall top-k     | consolidate at end
   +-----------+     +------------------+------------+     +-----------+
   | Agent A   |<--->|  SHARED (run state)           |<--->| Agent B   |
   | private   |     |  hs_code, decisions           |     | private   |
   +-----------+     +-------------------------------+     +-----------+
```

---

## 💰 Cost Impact
- Memory injection adds input tokens to every call: 10 memories x 50 tokens = 500 tokens per call.
- Embedding calls cost little (text-embedding-3-small is about $0.02 per 1M tokens) but add latency.
- Optimise: top-3 retrieval with threshold, short normalised memories, summarise before storing, cache embeddings, put stable memories at the prompt start for prompt caching, delete stale items.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Working memory | Current run scratchpad | मौजूदा run की अस्थायी memory |
| Long-term memory | Persistent across sessions | सत्रों के पार टिकने वाली memory |
| Namespace | Partition per user/tenant | हर user/tenant का अलग हिस्सा |
| Consolidation | Summarise and dedupe memories | Memories का सार और दोहराव हटाना |
| TTL | Time to live before deletion | हटने से पहले की अवधि |
| Checkpointer | Saves short-term state | Short-term state सेव करने वाला |

---

## ⚡ 3-Line Summary
English: Multi-agent memory has private, shared and long-term layers with strict scoping. Retrieve only what is relevant and consolidate regularly. Isolate users and expire old data.
Hindi: Multi-agent memory में private, shared और long-term परतें होती हैं और दायरा सख़्त रहता है। सिर्फ relevant चीज़ें निकालो और नियमित रूप से consolidate करो। Users को अलग रखो और पुराना data हटाओ।

---

## ➡️ Next Topic
**363. Multi-Agent Tools** — which agent gets which tools, and how to share them safely.
