---

# 223. RAG Memory
# हिंदी में: RAG Memory (RAG की याददाश्त)

---

## 🔵 Simple Definition (English)
RAG memory is how a RAG assistant remembers things. **Short-term memory** is the current chat (recent messages). **Long-term memory** is facts saved across sessions (user preferences, past decisions) in a store, often a vector database, and retrieved when relevant, just like documents.

## 🔵 सरल परिभाषा (Hindi)
RAG memory यानी RAG assistant कैसे याद रखता है। **Short-term memory** = मौजूदा chat के हाल के messages। **Long-term memory** = sessions के पार saved facts (user की पसंद, पुराने फ़ैसले), जो किसी store (अक्सर vector DB) में रहते हैं और ज़रूरत पर documents की तरह retrieve होते हैं।

---

## 🔴 Problem it Solves
- LLMs are stateless: every call starts blank.
- Keeping all history in the prompt is costly and hits the context limit.
- Users hate repeating themselves ("I import only from Vietnam").
- Plain chat history has no notion of which facts matter.

## 🔴 यह क्यों बना? (Hindi)
- LLM stateless है: हर call खाली शुरू होती है।
- पूरी history prompt में रखना महंगा है और context limit तोड़ता है।
- User को बार-बार वही बताना पड़ता है ("मैं सिर्फ़ Vietnam से import करता हूँ")।
- सादी chat history को नहीं पता कौन सा fact ज़रूरी है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Short-term: keep last N messages of this session in the prompt
Step 2 → After each turn, extract durable facts ("user imports from Vietnam")
Step 3 → Save facts in a long-term store with user_id, timestamp, embedding
Step 4 → On a new question, retrieve top-k memories similar to the question
Step 5 → Inject memories + document chunks into the prompt (separate sections)
Step 6 → Generate answer
Step 7 → Update, merge, or expire memories (avoid duplicates and stale facts)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Short-term: इस session के आख़िरी N messages prompt में
Step 2 → हर turn के बाद पक्के facts निकालो ("user Vietnam से import करता है")
Step 3 → Facts को long-term store में user_id, timestamp, embedding के साथ save करो
Step 4 → नए सवाल पर उससे मिलती-जुलती top-k memories retrieve करो
Step 5 → Memories + document chunks को अलग sections में prompt में डालो
Step 6 → Answer generate करो
Step 7 → Memories update/merge/expire करो (duplicate और पुराने facts से बचो)
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs broker says once: "My client ships only cotton garments from Bangladesh." The system stores that as a memory. Next week, "What duty applies?" is answered with Bangladesh and cotton garments in mind, with no repeat. Tariff documents are the **knowledge** (shared by all); memories are **personal** (per user).
**Amazon AI**: remembers your size and preferred brands across visits.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs broker एक बार कहता है: "मेरा client सिर्फ़ Bangladesh से cotton garments भेजता है।" System इसे memory में रखता है। अगले हफ़्ते "कौन सी duty लगेगी?" का जवाब Bangladesh और cotton garments को ध्यान में रखकर मिलता है। Tariff documents = **knowledge** (सबके लिए), memories = **personal** (हर user की)।
**Amazon AI**: आपकी size और पसंदीदा brands अगली visit पर भी याद रखता है।

---

## 💻 Code Example — Basic
```python
# Pure Python: short-term window + long-term fact store (keyword retrieval, no API key)
from dataclasses import dataclass, field
from typing import List

@dataclass
class Memory:
    user_id: str          # whose memory
    fact: str             # the saved fact

@dataclass
class RagMemory:
    window: int = 4                                   # short-term size
    short: List[str] = field(default_factory=list)    # recent messages
    long: List[Memory] = field(default_factory=list)  # durable facts

    def add_message(self, text: str) -> None:
        self.short.append(text)                       # push new message
        self.short = self.short[-self.window:]        # keep only last N

    def remember(self, user_id: str, fact: str) -> None:
        # Avoid duplicates: do not store the same fact twice
        if not any(m.user_id == user_id and m.fact == fact for m in self.long):
            self.long.append(Memory(user_id, fact))

    def recall(self, user_id: str, query: str, k: int = 2) -> List[str]:
        words = set(query.lower().split())            # crude relevance: shared words
        scored = [(len(words & set(m.fact.lower().split())), m.fact)
                  for m in self.long if m.user_id == user_id]
        scored.sort(reverse=True)                     # best match first
        return [fact for score, fact in scored[:k] if score > 0]

if __name__ == "__main__":
    mem = RagMemory()
    mem.remember("u1", "client ships cotton garments from bangladesh")
    mem.remember("u1", "client ships cotton garments from bangladesh")  # ignored duplicate
    mem.remember("u2", "prefers electronics")
    for i in range(6):
        mem.add_message(f"message {i}")
    print("short-term:", mem.short)                   # only last 4
    print("recall u1:", mem.recall("u1", "duty on garments from bangladesh"))
    print("recall u2:", mem.recall("u2", "duty on garments"))  # [] (no overlap)
```

## 💻 Code Example — Advanced
```python
# Production-style long-term memory with embeddings (async, typed, error handling)
import asyncio
import math
import time
from dataclasses import dataclass, field

from openai import AsyncOpenAI, APIError  # openai>=1

client = AsyncOpenAI()
EMBED_MODEL = "text-embedding-3-small"

@dataclass
class MemoryItem:
    user_id: str
    fact: str
    vector: list[float]
    created: float = field(default_factory=time.time)

def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0

class LongTermMemory:
    """In-memory demo; swap the list for pgvector / Qdrant / Chroma in production."""

    def __init__(self, dedupe_threshold: float = 0.95) -> None:
        self.items: list[MemoryItem] = []
        self.dedupe_threshold = dedupe_threshold

    async def _embed(self, text: str) -> list[float]:
        resp = await client.embeddings.create(model=EMBED_MODEL, input=text)
        return resp.data[0].embedding

    async def save(self, user_id: str, fact: str) -> bool:
        try:
            vec = await self._embed(fact)
        except APIError:
            return False                                   # memory is optional: fail soft
        for it in self.items:                              # semantic dedupe
            if it.user_id == user_id and cosine(it.vector, vec) >= self.dedupe_threshold:
                it.fact, it.vector, it.created = fact, vec, time.time()  # refresh, don't duplicate
                return True
        self.items.append(MemoryItem(user_id, fact, vec))
        return True

    async def search(self, user_id: str, query: str, k: int = 3,
                     min_score: float = 0.3, max_age_days: int = 180) -> list[str]:
        try:
            qv = await self._embed(query)
        except APIError:
            return []                                      # answer without memory
        cutoff = time.time() - max_age_days * 86400        # expire old facts
        scored = [(cosine(qv, it.vector), it.fact) for it in self.items
                  if it.user_id == user_id and it.created >= cutoff]
        scored.sort(reverse=True)
        return [f for s, f in scored[:k] if s >= min_score]

async def extract_facts(chat_turn: str) -> list[str]:
    """Ask a small LLM to pull durable facts out of a turn (one per line)."""
    resp = await client.chat.completions.create(
        model="gpt-4o-mini", temperature=0, max_tokens=100,
        messages=[
            {"role": "system", "content": "List durable user facts, one per line. "
                                           "If none, reply NONE. Never store secrets."},
            {"role": "user", "content": chat_turn},
        ],
    )
    text = (resp.choices[0].message.content or "NONE").strip()
    return [] if text == "NONE" else [ln.strip("- ").strip() for ln in text.splitlines() if ln.strip()]

async def demo() -> None:
    ltm = LongTermMemory()
    for fact in await extract_facts("I only import cotton garments from Bangladesh."):
        await ltm.save("u1", fact)
    print(await ltm.search("u1", "What duty applies to my shipment?"))

if __name__ == "__main__":
    asyncio.run(demo())  # needs OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
Scope every memory by authenticated `user_id`, never a client-supplied one without auth. Save memories in the background so the user does not wait.

```python
from fastapi import BackgroundTasks, Depends, FastAPI
from pydantic import BaseModel

app = FastAPI()
ltm = LongTermMemory()  # from the advanced example

def current_user() -> str:          # replace with real auth (JWT) dependency
    return "u1"

class Ask(BaseModel):
    question: str

async def learn(user_id: str, text: str) -> None:
    for fact in await extract_facts(text):   # extraction costs tokens, so run after response
        await ltm.save(user_id, fact)

@app.post("/ask")
async def ask(body: Ask, bg: BackgroundTasks, user: str = Depends(current_user)) -> dict:
    memories = await ltm.search(user, body.question)         # retrieve personal facts
    bg.add_task(learn, user, body.question)                  # save without blocking
    return {"memories_used": memories}
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph separates the two types cleanly: a **checkpointer** (e.g. `MemorySaver`, Postgres saver) stores short-term thread state; a **Store** (`InMemoryStore`, or a DB-backed store) holds cross-thread long-term memories with optional semantic search.

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

checkpointer = MemorySaver()          # short-term: per thread_id conversation state
store = InMemoryStore()               # long-term: shared across threads
store.put(("memories", "u1"), "fact-1", {"fact": "ships cotton garments from Bangladesh"})
items = store.search(("memories", "u1"))     # list of items in that namespace
# graph = builder.compile(checkpointer=checkpointer, store=store)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Storing the raw chat as memory.
✅ Correct: Store extracted, durable facts.

```python
# Wrong: bloated, noisy, expensive to retrieve
await ltm.save(user, "hi, thanks, ok, I import cotton from Bangladesh, bye")
# Right
await ltm.save(user, "imports cotton garments from Bangladesh")
```

❌ Mistake 2: One shared memory list for all users (privacy leak).
✅ Correct: Filter by `user_id` on every read and write.

❌ Mistake 3: Never updating or expiring memories (stale facts).
✅ Correct: Dedupe, refresh timestamps, and expire old items.

---

## 🧠 Tricky Interview Question
**Q**: "A user changed their mind: earlier they said 'I ship from Vietnam', now 'I switched to Thailand'. Your bot still answers for Vietnam. Why, and how do you fix it?"

**Answer**: Both facts sit in the store and retrieval returns the older one (or both). Memory needs **conflict resolution**: when saving, retrieve similar existing memories, ask the LLM whether the new fact updates or contradicts them, then update or delete the old one. Keep timestamps and prefer newer facts at read time. Pure append-only memory always drifts.

---

## ⚫ Interview Questions + Answers

Q1: Short-term vs long-term memory in RAG?
A1: Short-term is the current conversation window inside the prompt. Long-term is stored outside the prompt (DB/vector store) and retrieved on demand across sessions.

Q2: Is RAG memory the same as RAG documents?
A2: Same mechanism (embed, store, retrieve), different content. Documents are shared knowledge; memory is per-user, changes often, and needs update/expiry logic.

Q3: What should you NOT store in memory?
A3: Secrets, passwords, card numbers, sensitive personal data without consent, and one-off chatter. Add PII filters and let users view and delete their memories.

Q4: How do you decide what is worth remembering?
A4: Use an extraction prompt (durable, user-specific, likely reusable), plus rules (min length, no PII). Score importance and only store above a threshold.

Q5: Design memory for 1 million users without blowing up cost and latency.
A5: Namespace by user_id in a vector DB with metadata filter, cap memories per user (merge and summarize old ones), extract facts asynchronously in a queue, embed with a cheap model, cache recent retrievals, retrieve only top 3 with a score threshold, and add TTL/consolidation jobs at night.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Personalisation matters (preferences, past choices)
- Sessions repeat over days and weeks
- Users are tired of re-explaining context

❌ Avoid when:
- Anonymous one-shot queries
- Strict privacy rules forbid storing user data
- Facts change so fast that memory would mostly be wrong

---

## 📊 Visual Diagram
```
            ┌────────────────────── Prompt ──────────────────────┐
 Question ─►│ system │ KNOWLEDGE chunks │ MEMORIES │ last N msgs │
            └───────────────▲──────────────▲──────────▲──────────┘
                            │              │          │
                     Doc vector DB   Memory store   Session window
                    (shared, static) (per user,     (short-term)
                                      updated)
 After answer ──► extract facts ──► dedupe/merge ──► Memory store
```

---

## 💰 Cost Impact
- Retrieval adds one embedding call per question (tiny: text-embedding-3-small is about $0.02 per 1M tokens).
- Injecting 3 memories adds ~60-150 input tokens, far cheaper than replaying 20 old turns (~2000 tokens).
- Fact extraction is an extra LLM call: run it only when the turn looks informative, use a small model, run it in the background.
- Optimise: cap memories per user, consolidate, set a min score.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Short-term memory | Recent messages in the prompt | हाल की बातचीत |
| Long-term memory | Facts stored across sessions | sessions के पार saved facts |
| Checkpointer | LangGraph store of thread state | thread की state save करने वाला |
| Store | LangGraph cross-thread memory store | सब threads का साझा memory store |
| Consolidation | Merging/summarising old memories | पुरानी memories को मिलाना |
| TTL | Time after which data expires | data की expiry अवधि |

---

## ⚡ 3-Line Summary
English: RAG memory = short-term window plus long-term fact store retrieved like documents. Save extracted facts per user, dedupe and expire them. Keep it private, small, and cheap.
Hindi: RAG memory = short-term window + long-term fact store, जिसे documents की तरह retrieve किया जाता है। हर user के extracted facts save करो, duplicate हटाओ और expire करो। इसे private, छोटा और सस्ता रखो।

---

## ➡️ Next Topic
**224. Agentic RAG**: instead of a fixed retrieve-then-answer pipeline, an agent decides when and what to retrieve.
