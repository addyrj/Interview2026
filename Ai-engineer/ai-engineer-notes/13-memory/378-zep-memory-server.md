---

# 378. Zep Memory Server
# हिंदी में: Zep Memory Server

---

## 🔵 Simple Definition (English)
Zep is a memory service for AI apps. You send it chat messages; it builds a knowledge graph of facts about each user, keeps threads, and returns a ready-to-use "context block" for your prompt. You do not write extraction or retrieval code yourself.

## 🔵 सरल परिभाषा (Hindi)
Zep AI apps के लिए memory service है। आप इसे chat messages भेजते हैं; ये हर user के facts का knowledge graph बनाती है, threads रखती है, और prompt के लिए तैयार "context block" लौटाती है। Extraction या retrieval code आपको खुद नहीं लिखना पड़ता।

---

## 🔴 Problem it Solves
Building long-term memory yourself means: extraction prompts, embeddings, dedupe, conflict handling, temporal facts, summaries, scaling. That is weeks of work and easy to get wrong. Zep packages this as a service with an SDK.

## 🔴 यह क्यों बना? (Hindi)
खुद long-term memory बनाने का मतलब: extraction prompts, embeddings, dedupe, conflict handling, temporal facts, summaries, scaling। इसमें हफ़्ते लगते हैं और गलती आसान है। Zep इसे SDK वाली service के रूप में देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a user (user_id) and a thread (thread_id) in Zep
Step 2 → After each turn, add messages (user + assistant) to the thread
Step 3 → Zep ingests them asynchronously into a temporal knowledge graph
Step 4 → Facts get valid-from / invalid-at times, conflicts are resolved
Step 5 → Before the next LLM call, fetch the thread's context block
Step 6 → Paste the context string into the system prompt
Step 7 → LLM answers with personalised memory
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Zep में user (user_id) और thread (thread_id) बनाओ
Step 2 → हर turn के बाद messages (user + assistant) thread में add करो
Step 3 → Zep उन्हें asynchronously temporal knowledge graph में डालता है
Step 4 → Facts को valid-from / invalid-at time मिलता है, conflicts हल होते हैं
Step 5 → अगले LLM call से पहले thread का context block लो
Step 6 → Context string को system prompt में लगाओ
Step 7 → LLM personalised memory के साथ जवाब देता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: A broker's company ships mostly electronics from Vietnam. Zep learns "Acme Ltd imports electronics; prefers FOB terms; last query was about 8507 batteries". Next session, the assistant already knows this. **Zomato-style**: remembers "orders biryani on Fridays, avoids spicy" across months.

## 🟡 Real Example Hindi mein
**Tariff System**: Broker की company ज़्यादातर Vietnam से electronics मँगाती है। Zep सीखता है "Acme Ltd electronics import करती है; FOB terms पसंद; पिछला query 8507 batteries पर था"। अगले session में assistant को पहले से पता होता है। **Zomato-style**: "शुक्रवार को biryani order करता है, spicy नहीं" महीनों तक याद रहता है।

---

## 💻 Code Example — Basic
```python
# Basic: a tiny local "Zep-like" client so the flow runs offline without an account.
# Real Zep calls are shown in the Advanced block.
class FakeZep:
    """Mimics: add messages -> get context."""

    def __init__(self) -> None:
        self.threads: dict[str, list[tuple[str, str]]] = {}      # thread_id -> [(role, text)]

    def add_messages(self, thread_id: str, role: str, text: str) -> None:
        self.threads.setdefault(thread_id, []).append((role, text))   # append the message

    def get_context(self, thread_id: str, last_n: int = 3) -> str:
        msgs = self.threads.get(thread_id, [])[-last_n:]              # most recent messages
        return "\n".join(f"{r}: {t}" for r, t in msgs)                # context block string

zep = FakeZep()                                                       # create client
zep.add_messages("t1", "user", "I import electronics from Vietnam")   # turn 1
zep.add_messages("t1", "assistant", "Noted. Which product?")          # turn 1 reply
print(zep.get_context("t1"))                                          # context for next prompt
```

## 💻 Code Example — Advanced
```python
# Production: Zep Cloud SDK (pip install zep-cloud). Async, typed, error handling.
# SDK surface changes between versions - check the Zep docs for your version.
import asyncio                                            # async runtime
import os                                                 # env variables
from zep_cloud.client import AsyncZep                     # async Zep client
from zep_cloud.types import Message                       # message type

async def remember_and_recall(user_id: str, thread_id: str, text: str) -> str:
    """Store a user message and return the memory context for the next prompt."""
    zep = AsyncZep(api_key=os.environ["ZEP_API_KEY"])     # KeyError if missing: fail fast
    try:
        await zep.user.add(user_id=user_id, first_name="Broker")          # create user (once)
    except Exception:                                      # already exists -> fine
        pass
    try:
        await zep.thread.create(thread_id=thread_id, user_id=user_id)     # create thread (once)
    except Exception:
        pass
    await zep.thread.add_messages(                         # send the new message
        thread_id=thread_id,
        messages=[Message(role="user", name="Broker", content=text)],
    )
    memory = await zep.thread.get_user_context(thread_id=thread_id)       # fetch context block
    return memory.context or ""                            # string for the system prompt

async def main() -> None:
    ctx = await remember_and_recall("u1", "t1", "I import 48V batteries from Vietnam")
    print(ctx)                                             # shows learned facts

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
import os                                                  # env access
from fastapi import FastAPI, HTTPException                 # app + errors
from pydantic import BaseModel                             # request model

app = FastAPI()                                            # app

class ChatIn(BaseModel):
    user_id: str                                           # Zep user
    thread_id: str                                         # Zep thread
    message: str                                           # user text

@app.post("/chat")
async def chat(body: ChatIn) -> dict[str, str]:
    try:
        ctx = await remember_and_recall(body.user_id, body.thread_id, body.message)   # from Advanced block
    except Exception as exc:                               # network / auth problems
        raise HTTPException(status_code=502, detail="memory service unavailable") from exc
    prompt = f"Memory:\n{ctx}\n\nUser: {body.message}"     # build prompt
    return {"prompt_preview": prompt[:200]}                # call your LLM with `prompt` here
```
Tip: if Zep is down, continue without memory instead of failing the chat.

---

## 🔗 LangChain / LangGraph Connection
Zep has a LangGraph/LangChain integration (`zep-cloud` ships helpers). The simplest pattern is a "recall" node that fetches the context string and a "save" node that adds messages.

```python
from typing import TypedDict                               # state schema
from langgraph.graph import StateGraph, START, END        # graph API

class S(TypedDict):
    user_id: str                                           # who
    thread_id: str                                         # which thread
    message: str                                           # input
    memory: str                                            # recalled context
    answer: str                                            # output

async def recall(s: S) -> dict:
    return {"memory": await remember_and_recall(s["user_id"], s["thread_id"], s["message"])}   # Zep call

def answer(s: S) -> dict:
    return {"answer": f"[uses memory: {s['memory'][:40]}]"}   # replace with LLM call

g = StateGraph(S)                                          # build graph
g.add_node("recall", recall); g.add_node("answer", answer) # nodes
g.add_edge(START, "recall"); g.add_edge("recall", "answer"); g.add_edge("answer", END)   # edges
graph = g.compile()                                        # run with await graph.ainvoke({...})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Hard-coding the API key
✅ Correct: read from environment / secret manager.

```python
# Wrong
zep = AsyncZep(api_key="z_abc123")
# Right
zep = AsyncZep(api_key=os.environ["ZEP_API_KEY"])
```

❌ Mistake 2: Blocking the answer on memory writes
✅ Correct: add messages in a background task; read context with a timeout.

```python
# Wrong - user waits for ingestion
await zep.thread.add_messages(...)
# Right
bg.add_task(zep.thread.add_messages, thread_id=tid, messages=msgs)
```

---

## 🧠 Tricky Interview Question
**Q**: "Right after saving a message, the context doesn't contain it. Bug?"

**Answer**: Not necessarily. Zep ingests into the graph asynchronously, so new facts can appear after a short delay. Keep the last few raw turns in your own prompt (short-term) and use Zep context for long-term facts. Do not rely on read-your-write consistency for the graph.

---

## ⚫ Interview Questions + Answers

Q1: What does Zep do? (Easy)
A1: Managed long-term memory: stores messages, builds a temporal knowledge graph, returns a context block.

Q2: Why use Zep over a raw vector store? (Easy)
A2: It handles extraction, dedupe, time and conflicts for you; a vector store only does similarity search.

Q3: What is a temporal knowledge graph? (Medium)
A3: Facts as graph edges with validity times, so "lives in Delhi (until 2024)" and "lives in Pune (from 2024)" can coexist and the current one is preferred.

Q4: How do you handle Zep downtime? (Medium)
A4: Timeout, catch errors, answer without long-term memory, queue writes for retry.

Q5: Compare Zep, mem0 and a DIY stack. (Hard)
A5: Zep: strong temporal graph and thread model, managed or self-hosted. mem0: simple add/search API, flexible stores. DIY: full control, most work. Choose by data-residency needs, team size, and how much temporal reasoning you need. Evaluate recall quality and cost on your own data.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multi-session personalisation
- Small team, no time for a memory stack
- Need temporal facts

❌ Avoid when:
- Strict data residency you cannot meet
- Tiny single-session bots
- You need total control of extraction logic

---

## 📊 Visual Diagram
```
 App ──messages──► [ Zep thread ] ──ingest──► [ Knowledge graph ]
  ▲                                              │ facts + time
  └────── context block ◄──── retrieve ◄────────┘
  │
  └─► system prompt ─► LLM
```

---

## 💰 Cost Impact
Zep adds a service fee (or hosting cost) but removes your own extraction LLM calls. In-prompt cost is the context block, typically a few hundred tokens - far below full history. Optimise: request a smaller context, keep only the last 2-4 raw turns beside it, skip memory for trivial messages.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Thread | One conversation | एक बातचीत |
| User | Owner of memories | memory का मालिक |
| Knowledge graph | Entities and relations | entities और रिश्तों का graph |
| Context block | Ready prompt text | prompt के लिए तैयार text |
| Temporal fact | Fact with validity time | समय वाला fact |

---

## ⚡ 3-Line Summary
English: Zep is managed memory: send messages, get a context block. It builds a temporal graph so facts stay current. Always handle failures and keep a few raw turns too.
Hindi: Zep managed memory है: messages भेजो, context block लो। ये temporal graph बनाता है ताकि facts current रहें। Failures handle करो और कुछ raw turns भी रखो।

---

## ➡️ Next Topic
**379. mem0 Library** - an open-source alternative with a simple add/search memory API.
