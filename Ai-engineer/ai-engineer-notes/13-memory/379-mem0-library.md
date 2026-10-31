---

# 379. mem0 Library
# हिंदी में: mem0 Library

---

## 🔵 Simple Definition (English)
mem0 is an open-source memory layer for LLM apps. You call `m.add(messages, user_id=...)` and it uses an LLM to extract facts, dedupe and store them (vector store). You call `m.search(query, user_id=...)` to get relevant memories back.

## 🔵 सरल परिभाषा (Hindi)
mem0 LLM apps के लिए open-source memory layer है। `m.add(messages, user_id=...)` बुलाते ही ये LLM से facts निकालता है, duplicates हटाता है और vector store में रखता है। `m.search(query, user_id=...)` से relevant memories वापस मिलती हैं।

---

## 🔴 Problem it Solves
Developers keep re-writing the same loop: extract facts, compare with old ones, add/update/delete, embed, search. mem0 gives this as two calls, so personalisation takes minutes, not weeks.

## 🔴 यह क्यों बना? (Hindi)
Developers वही loop बार-बार लिखते हैं: facts निकालो, पुराने से compare करो, add/update/delete, embed, search। mem0 इसे दो calls में देता है, इसलिए personalisation हफ़्तों की जगह मिनटों में होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → app calls m.add(messages, user_id)
Step 2 → LLM extracts candidate facts ("prefers FOB terms")
Step 3 → Each fact is compared with existing memories (similarity)
Step 4 → LLM decides ADD / UPDATE / DELETE / NONE
Step 5 → Memory is embedded and saved in the vector store
Step 6 → Later: m.search(query, user_id) embeds the query
Step 7 → Top matches returned; you inject them into the prompt
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → app m.add(messages, user_id) बुलाता है
Step 2 → LLM candidate facts निकालता है ("FOB terms पसंद")
Step 3 → हर fact की पुरानी memories से similarity देखी जाती है
Step 4 → LLM तय करता है ADD / UPDATE / DELETE / NONE
Step 5 → Memory embed होकर vector store में save होती है
Step 6 → बाद में: m.search(query, user_id) query को embed करता है
Step 7 → Top matches मिलते हैं; आप उन्हें prompt में डालते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: User says "I always ship to Mumbai port" in week 1; in week 3 asks "estimate landing cost". `search` returns "ships to Mumbai port", so the answer uses Indian duty rules automatically. If the user later says "now Chennai port", mem0 UPDATEs instead of storing a contradiction. **Zomato-style**: "vegetarian" stays remembered; "now eats chicken" updates it.

## 🟡 Real Example Hindi mein
**Tariff System**: User हफ़्ते 1 में कहता है "मैं हमेशा Mumbai port भेजता हूँ"; हफ़्ते 3 में पूछता है "landing cost estimate करो"। `search` "Mumbai port" लौटाता है, इसलिए जवाब अपने-आप भारतीय duty rules से बनता है। बाद में "अब Chennai port" कहने पर mem0 contradiction रखने की जगह UPDATE करता है। **Zomato-style**: "vegetarian" याद रहता है; "अब chicken खाता है" पर update हो जाता है।

---

## 💻 Code Example — Basic
```python
# Basic: offline mimic of mem0's add/search/update behaviour (no API key).
class MiniMem0:
    """Keeps one value per (user, topic) so new info replaces old (UPDATE)."""

    def __init__(self) -> None:
        self.data: dict[str, dict[str, str]] = {}          # user_id -> {topic: value}

    def add(self, user_id: str, topic: str, value: str) -> str:
        user = self.data.setdefault(user_id, {})           # get/create the user's memories
        if topic not in user:                              # new topic
            action = "ADD"
        elif user[topic] != value:                         # changed value
            action = "UPDATE"
        else:                                              # same value
            action = "NONE"
        user[topic] = value                                # store latest
        return action                                      # what happened

    def search(self, user_id: str, query: str) -> list[str]:
        user = self.data.get(user_id, {})                  # this user's memories
        return [f"{t}: {v}" for t, v in user.items() if t in query.lower()]   # topic in query

m = MiniMem0()                                             # create
print(m.add("u1", "port", "Mumbai"))                       # ADD
print(m.add("u1", "port", "Chennai"))                      # UPDATE
print(m.search("u1", "which port do I use?"))              # ['port: Chennai']
```

## 💻 Code Example — Advanced
```python
# Production: real mem0 (pip install mem0ai) wrapped in an async-safe, defensive service.
# mem0's API evolves; results may be a list or {"results": [...]} depending on version.
import asyncio                                             # to offload sync calls
import logging                                             # logging
from typing import Any                                     # typing
from mem0 import Memory                                    # mem0 open-source class

log = logging.getLogger("mem0_service")                    # logger

class MemoryService:
    def __init__(self) -> None:
        self.m = Memory()                                  # default config uses OpenAI (OPENAI_API_KEY)

    async def remember(self, user_id: str, user_msg: str, assistant_msg: str) -> None:
        messages = [
            {"role": "user", "content": user_msg},         # what user said
            {"role": "assistant", "content": assistant_msg},   # what we replied
        ]
        try:
            await asyncio.to_thread(self.m.add, messages, user_id=user_id)   # sync lib -> thread
        except Exception as exc:                           # network / LLM errors
            log.warning("mem0 add failed: %s", exc)        # never break the chat

    async def recall(self, user_id: str, query: str, limit: int = 3) -> list[str]:
        try:
            res: Any = await asyncio.to_thread(self.m.search, query, user_id=user_id, limit=limit)   # search
        except Exception as exc:
            log.warning("mem0 search failed: %s", exc)
            return []                                      # degrade gracefully
        items = res["results"] if isinstance(res, dict) else res   # handle both shapes
        return [i["memory"] for i in items]                # just the text

async def main() -> None:
    svc = MemoryService()                                  # needs API key
    await svc.remember("u1", "I ship via Mumbai port", "Noted!")   # save
    print(await svc.recall("u1", "which port?"))           # recall

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, BackgroundTasks               # app + background jobs
from pydantic import BaseModel                             # request model

app = FastAPI()                                            # app
svc = MemoryService()                                      # shared service

class ChatIn(BaseModel):
    user_id: str                                           # owner
    message: str                                           # text

@app.post("/chat")
async def chat(body: ChatIn, bg: BackgroundTasks) -> dict[str, object]:
    memories = await svc.recall(body.user_id, body.message)        # relevant memories
    answer = f"(LLM answer using {len(memories)} memories)"        # call LLM with memories here
    bg.add_task(svc.remember, body.user_id, body.message, answer)  # save after reply
    return {"answer": answer, "memories": memories}                # respond fast
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.prompts import ChatPromptTemplate      # prompt template
from langchain_openai import ChatOpenAI                    # chat model

prompt = ChatPromptTemplate.from_messages([
    ("system", "Known user facts:\n{memories}"),           # inject mem0 results
    ("human", "{question}"),                               # user question
])
chain = prompt | ChatOpenAI(model="gpt-4o-mini")           # LCEL chain

async def answer(user_id: str, q: str) -> str:
    mems = await svc.recall(user_id, q)                    # step 1: recall
    msg = await chain.ainvoke({"memories": "\n".join(mems), "question": q})   # step 2: answer
    return msg.content                                     # text
# In LangGraph: make recall and remember separate nodes around the LLM node.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `user_id` - memories mix between users
✅ Correct: always pass `user_id` (and `agent_id`/`run_id` when needed).

```python
# Wrong
m.add(messages)
# Right
m.add(messages, user_id="u1")
```

❌ Mistake 2: Calling the blocking client directly in an async route
✅ Correct: `asyncio.to_thread` or the async client variant if your version has one.

```python
# Wrong - blocks the event loop
m.search(q, user_id=uid)
# Right
await asyncio.to_thread(m.search, q, user_id=uid)
```

---

## 🧠 Tricky Interview Question
**Q**: "Your mem0 bill is high even though users send short messages. Why?"

**Answer**: Every `add` triggers extra LLM calls (fact extraction + update decision) plus embeddings, independent of message length. Fix: call `add` only for informative turns, batch several turns per add, use a cheaper model for mem0's internal LLM, and skip add for greetings.

---

## ⚫ Interview Questions + Answers

Q1: What are mem0's two main calls? (Easy)
A1: `add` to store and `search` to retrieve memories for a user.

Q2: Why does mem0 need an LLM? (Easy)
A2: To extract clean facts and decide add/update/delete against existing memories.

Q3: How does mem0 avoid duplicate memories? (Medium)
A3: It searches similar existing memories and lets the LLM choose UPDATE or NONE instead of ADD.

Q4: How do you keep memories private between tenants? (Medium)
A4: Scope by `user_id`, use per-tenant collections or metadata filters, encrypt storage, and add deletion endpoints for GDPR.

Q5: When prefer mem0 over a custom vector memory? (Hard)
A5: When you want add/update/delete semantics and fact extraction out of the box; use custom if you need strict control of schema, cost, or latency. Measure recall quality and per-add cost first.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Personalisation across sessions
- Quick prototype of long-term memory

❌ Avoid when:
- Ultra-low latency writes
- Need deterministic structured fields (use a database)
- Cost-sensitive high-volume chat without filtering

---

## 📊 Visual Diagram
```
 add(): messages ─► [LLM extract] ─► facts ─► [compare] ─► ADD/UPDATE/DELETE
                                                   │
                                            [ vector store ]
 search(): query ─► embed ─► nearest memories ──────┘ ─► prompt
```

---

## 💰 Cost Impact
Each `add` = 1-2 LLM calls (about 300-800 tokens) + embeddings; each `search` = 1 embedding. With gpt-4o-mini that is roughly $0.0002-0.0005 per add. Optimise: add only meaningful turns, batch, cheap internal model, cache searches, limit `limit` to 3.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Memory layer | Storage+retrieval for memories | memory की परत |
| add / search | Store / retrieve API | store / खोज API |
| UPDATE | Replace changed fact | बदला fact replace |
| user_id | Scope key | user का scope |
| Fact extraction | LLM pulls facts from chat | chat से facts निकालना |

---

## ⚡ 3-Line Summary
English: mem0 gives `add` and `search` for long-term memory. An LLM extracts facts and decides add, update or delete. Scope by user and control add cost.
Hindi: mem0 long-term memory के लिए `add` और `search` देता है। LLM facts निकालता है और add, update या delete तय करता है। User से scope करो और add का cost control करो।

---

## ➡️ Next Topic
**380. Memory + RAG Together** - combine personal memory with document retrieval in one prompt.
