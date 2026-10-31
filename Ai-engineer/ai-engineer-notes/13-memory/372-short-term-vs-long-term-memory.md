---

# 372. Short-term vs Long-term Memory
# हिंदी में: Short-term बनाम Long-term Memory

---

## 🔵 Simple Definition (English)
**Short-term memory** lives for one conversation/thread (recent messages, working state). **Long-term memory** lives across conversations (facts, preferences, past events) and is stored externally. Short-term answers "what are we talking about now?"; long-term answers "what do I know about this user?".

## 🔵 सरल परिभाषा (Hindi)
**Short-term memory** एक बातचीत/thread तक रहती है (हाल के messages, working state)। **Long-term memory** बातचीतों के पार रहती है (facts, preferences, पुरानी घटनाएँ) और बाहर store होती है। Short-term बताती है "अभी क्या बात हो रही है?"; long-term बताती है "इस user के बारे में मुझे क्या पता है?"।

---

## 🔴 Problem it Solves
- Mixing everything in one place: either the prompt overflows (too much) or the bot forgets (too little).
- Need different lifetimes, storage and cost for different information.

## 🔴 यह क्यों बना? (Hindi)
- सब कुछ एक जगह मिलाने पर या तो prompt भर जाता है या bot भूल जाता है।
- अलग जानकारी की अलग उम्र, storage और cost चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Request has thread_id (conversation) and user_id (person)
Step 2 → SHORT-TERM: load messages/state for thread_id (checkpointer, Redis)
Step 3 → LONG-TERM: search store by user_id namespace for relevant facts/episodes
Step 4 → Prompt = rules + long-term snippets + short-term window + question
Step 5 → After reply: update short-term (append) ; maybe write long-term (extract facts)
Step 6 → Thread ends: short-term may expire, long-term stays
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Request में thread_id (बातचीत) और user_id (व्यक्ति) होता है
Step 2 → SHORT-TERM: thread_id के messages/state load (checkpointer, Redis)
Step 3 → LONG-TERM: user_id namespace में relevant facts/episodes search
Step 4 → Prompt = rules + long-term snippets + short-term window + सवाल
Step 5 → Reply के बाद: short-term में append; ज़रूरत हो तो long-term में लिखो
Step 6 → Thread खत्म: short-term expire हो सकती है, long-term रहती है
```

---

## 🟡 Real World Example
**Tariff Classification System**: Short-term: the current classification session ("we are classifying this shipment's 3 items; item 2 done"). Long-term: "this importer prefers INR; last quarter we classified similar items under 6109". Next week a new thread starts; short-term is empty but long-term still personalises.
**Amazon AI**: current shopping chat = short-term; purchase history = long-term.

## 🟡 Real Example Hindi mein
**Tariff System**: Short-term: मौजूदा session ("इस shipment के 3 items classify कर रहे हैं; item 2 हो गया")। Long-term: "यह importer INR पसंद करता है; पिछली तिमाही में ऐसे items 6109 में classify हुए"। अगले हफ्ते नया thread: short-term खाली, पर long-term फिर भी personalise करती है।

---

## 💻 Code Example — Basic
```python
# Pure Python (offline): two scopes. thread_id -> short-term, user_id -> long-term
short_term: dict[str, list[str]] = {}                                # thread_id -> recent messages
long_term: dict[str, dict[str, str]] = {}                            # user_id -> facts

def remember_message(thread_id: str, text: str, window: int = 4) -> None:   # short-term write
    msgs = short_term.setdefault(thread_id, [])                      # get/create the list
    msgs.append(text)                                                # add message
    del msgs[:-window]                                               # keep only last `window`

def remember_fact(user_id: str, key: str, value: str) -> None:       # long-term write
    long_term.setdefault(user_id, {})[key] = value                   # upsert fact

def build_context(user_id: str, thread_id: str) -> str:              # combine both scopes
    facts = long_term.get(user_id, {})                               # long-term facts
    recent = short_term.get(thread_id, [])                           # short-term messages
    return f"FACTS: {facts}\nRECENT: {recent}"                       # prompt block

remember_fact("u1", "currency", "INR")                               # persists across threads
remember_message("t1", "classify cotton shirt")                      # thread 1 only
print(build_context("u1", "t1"))                                     # both visible
print(build_context("u1", "t2"))                                     # new thread: facts yes, recent empty
```

## 💻 Code Example — Advanced
```python
# Async two-tier memory: hot short-term (TTL) + durable long-term + promotion rule
import asyncio                                                       # async runtime
import time                                                          # clocks for TTL
from collections import deque                                        # bounded window
from dataclasses import dataclass, field                             # data classes


@dataclass
class ShortTerm:                                                     # per-thread buffer
    window: int = 6                                                  # max messages
    ttl: float = 1800.0                                              # 30 minutes idle -> expire
    buf: deque[str] = field(default_factory=deque)                   # messages
    touched: float = field(default_factory=time.time)                # last use

    def add(self, text: str) -> None:
        self.buf.append(text)                                        # add new
        while len(self.buf) > self.window:                           # enforce window
            self.buf.popleft()
        self.touched = time.time()                                   # refresh TTL

    def expired(self) -> bool:
        return time.time() - self.touched > self.ttl


class TwoTierMemory:
    def __init__(self) -> None:
        self.threads: dict[str, ShortTerm] = {}                      # thread_id -> buffer
        self.facts: dict[str, dict[str, str]] = {}                   # user_id -> facts
        self._lock = asyncio.Lock()                                  # protect shared dicts

    async def add_message(self, thread_id: str, text: str) -> None:
        async with self._lock:                                       # one writer at a time
            st = self.threads.get(thread_id)
            if st is None or st.expired():                           # new/expired thread
                st = self.threads[thread_id] = ShortTerm()
            st.add(text)

    async def promote(self, user_id: str, key: str, value: str) -> None:
        if not key or not value:                                     # validate
            raise ValueError("key and value required")
        async with self._lock:
            self.facts.setdefault(user_id, {})[key] = value          # persist long-term

    async def context(self, user_id: str, thread_id: str) -> str:
        async with self._lock:
            st = self.threads.get(thread_id)
            recent = list(st.buf) if st and not st.expired() else []
            facts = dict(self.facts.get(user_id, {}))
        return f"FACTS: {facts}\nRECENT: {recent}"


async def main() -> None:
    mem = TwoTierMemory()
    await mem.promote("u1", "currency", "INR")                       # long-term
    await mem.add_message("t1", "classify cotton shirt")             # short-term
    print(await mem.context("u1", "t1"))

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Headers/body carry `user_id` (from auth, never from a client-writable field) and `thread_id`. Thread = short-term key. User = long-term key.

```python
# FastAPI: scope memory with user_id (long-term) and thread_id (short-term)
from fastapi import FastAPI, Header                 # framework
from pydantic import BaseModel                      # schema

app = FastAPI()                                     # app
mem = TwoTierMemory()                               # singleton

class In(BaseModel):
    thread_id: str
    message: str

@app.post("/chat")
async def chat(body: In, x_user_id: str = Header(...)) -> dict[str, str]:   # user from auth layer
    ctx = await mem.context(x_user_id, body.thread_id)       # both scopes
    await mem.add_message(body.thread_id, body.message)      # update short-term
    return {"context_used": ctx}
```

---

## 🔗 LangChain / LangGraph Connection
This split is LangGraph's official model: **checkpointer** = short-term (state per `thread_id`), **Store** = long-term (shared across threads, namespaced by user).

```python
# LangGraph: both scopes in one compiled graph
from langgraph.graph import StateGraph, MessagesState, START   # graph pieces
from langgraph.checkpoint.memory import MemorySaver            # short-term
from langgraph.store.memory import InMemoryStore               # long-term
from langgraph.store.base import BaseStore                     # type for node param
from langchain_core.runnables import RunnableConfig            # config type

def node(state: MessagesState, config: RunnableConfig, *, store: BaseStore) -> dict:
    user_id = config["configurable"]["user_id"]                # who
    items = store.search(("facts", user_id))                   # long-term read
    return {"messages": [("ai", f"I know {len(items)} facts about you")]}

builder = StateGraph(MessagesState)                            # graph with message state
builder.add_node("respond", node)                              # add node
builder.add_edge(START, "respond")                             # entry
graph = builder.compile(checkpointer=MemorySaver(), store=InMemoryStore())
# graph.invoke({"messages": [("user", "hi")]}, {"configurable": {"thread_id": "t1", "user_id": "u1"}})
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using thread_id for user facts
✅ Correct: user facts keyed by user_id.

```python
# Wrong: facts[thread_id] = ...   # new chat -> facts lost
# Right: facts[user_id] = ...
```

❌ Mistake 2: Taking user_id from the request body
✅ Correct: derive from authenticated token.

```python
# Wrong: user_id = body.user_id          # attacker reads someone else's memory
# Right: user_id = current_user.id       # from JWT/session
```

---

## 🧠 Tricky Interview Question
**Q**: "Same user opens the app on phone and laptop at the same time. Which memory is shared and which is not?"

**Answer**: Two threads (one per device chat) = two separate short-term memories, so recent messages are not shared. Long-term memory is keyed by user, so facts are shared. Concurrent writes to the same facts need locking/upsert or optimistic versioning to avoid lost updates.

---

## ⚫ Interview Questions + Answers

Q1: Define short-term memory.
A1: Context for the current conversation: recent messages and working state, scoped to a thread.

Q2: Define long-term memory.
A2: Information kept across conversations in external storage, scoped to a user/org.

Q3: Which LangGraph component is which?
A3: Checkpointer = short-term (thread state). Store = long-term (cross-thread).

Q4: How does information move from short-term to long-term?
A4: A "promotion" step extracts durable facts/events (often in the background) and writes them to the long-term store, deduplicated.

Q5: What are the failure modes of each?
A5: Short-term: overflow, lost-in-the-middle, cost growth. Long-term: stale or wrong facts, privacy leaks, retrieval noise, unbounded growth. Mitigate with trimming, summaries, TTL, validation, namespaces and consolidation jobs.

---

## 🔷 When to Use + When Not to Use
✅ Use both when:
- Product has returning users and multi-turn tasks
- You need personalisation without huge prompts

❌ Avoid long-term when:
- Anonymous one-off usage
- Regulation prevents retention

---

## 📊 Visual Diagram
```
 user_id ──▶ LONG-TERM (facts, episodes)  ─┐
                                           ├─▶ prompt ─▶ LLM
 thread_id ─▶ SHORT-TERM (recent turns)   ─┘
                 │ expires with thread       ▲ persists across threads
                 └──── promote durable info ─┘
```

---

## 💰 Cost Impact
- Short-term tokens are the main cost driver (resent every turn). Long-term adds only retrieved snippets (e.g. 150 tokens).
- Optimise: small window + summary, retrieve top-3 long-term items, promote facts in a background cheap-model job, set TTL on idle threads.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Short-term | Per-thread memory | Thread-स्तर की memory |
| Long-term | Cross-thread memory | Threads के पार की memory |
| Thread | One conversation | एक बातचीत |
| Checkpointer | Saves thread state | Thread state save करने वाला |
| Store | Long-term key-value store | Long-term store |
| Promotion | Move info to long-term | Long-term में डालना |

---

## ⚡ 3-Line Summary
English: Short-term memory is per conversation; long-term memory is per user across conversations. Key them differently (thread_id vs user_id). Promote durable facts from short-term to long-term in the background.
Hindi: Short-term memory हर बातचीत की होती है; long-term हर user की, बातचीतों के पार। इन्हें अलग keys से रखो (thread_id बनाम user_id)। टिकाऊ facts को background में short-term से long-term में promote करो।

---

## ➡️ Next Topic
**373. Conversation History Management** — practical techniques to keep the short-term history healthy.
