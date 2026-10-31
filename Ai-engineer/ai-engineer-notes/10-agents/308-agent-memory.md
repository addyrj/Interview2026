---

# 308. Agent Memory
# हिंदी में: Agent Memory (Agent की याददाश्त)

---

## 🔵 Simple Definition (English)
Agent memory is how an agent keeps information beyond one LLM call. **Short-term memory** is the message history of the current conversation. **Long-term memory** is stored outside the prompt (database, vector store) and fetched when needed, such as user preferences or past decisions.

## 🔵 सरल परिभाषा (Hindi)
Agent memory वह तरीका है जिससे agent एक LLM call के बाद भी जानकारी याद रखता है। **Short-term memory** मौजूदा बातचीत की message history है। **Long-term memory** prompt के बाहर (database, vector store) रखी जाती है और ज़रूरत पर वापस लाई जाती है, जैसे user की पसंद या पुराने फैसले।

---

## 🔴 Problem it Solves
LLMs are stateless: every API call starts blank. Without memory, the user must repeat "I import electronics from China" in every message. Stuffing all history into the prompt hits the context limit and costs a lot. Memory solves both with trimming, summarising and retrieval.

## 🔴 यह क्यों बना? (Hindi)
LLM stateless है: हर call खाली शुरू होती है। Memory के बिना user को हर बार दोहराना पड़ेगा। पूरी history prompt में डालने से context limit और cost बढ़ती है। Memory में trimming, summary और retrieval से यह हल होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Identify the session (thread_id) and user (user_id)
Step 2 → Load short-term history for that thread
Step 3 → Search long-term store for relevant facts (by user_id / similarity)
Step 4 → Build prompt = system + facts + trimmed history + new question
Step 5 → LLM answers (maybe with tools)
Step 6 → Save the new turn to history
Step 7 → Extract durable facts ("user ships from CN") and write to long-term store
Step 8 → When history is too long: summarise old turns, keep recent ones
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Session (thread_id) और user (user_id) पहचानो
Step 2 → उस thread की short-term history load करो
Step 3 → Long-term store से relevant facts खोजो
Step 4 → Prompt = system + facts + trimmed history + नया सवाल
Step 5 → LLM जवाब देता है
Step 6 → नया turn history में save करो
Step 7 → Durable facts निकालकर long-term store में लिखो
Step 8 → History लंबी हो तो पुराने turns का summary बनाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: An importer chats: "I mainly import consumer electronics from Vietnam." Next day: "Classify this charger." The agent loads the saved fact (origin = VN, category = electronics) and applies the right duty schedule without asking again. Within a session, "and what about the cable?" works because the history holds the charger context.

**Zomato-style**: remembers "vegetarian, no onion" across orders.

## 🟡 Real Example Hindi mein
**Tariff System**: Importer कहता है "मैं मुख्य रूप से Vietnam से electronics import करता हूँ।" अगले दिन: "इस charger को classify करो।" Agent saved fact (origin = VN) load करके बिना दोबारा पूछे सही duty schedule लगाता है। Session के अंदर "और cable?" इसलिए चलता है क्योंकि history में charger का context है।
**Zomato**: "veg, बिना प्याज" हर order में याद रखता है।

---

## 💻 Code Example — Basic
```python
# Basic: short-term buffer + long-term fact store, pure Python (runs offline).
from typing import Any                          # type hints

class ShortTermMemory:                          # recent messages, bounded
    def __init__(self, max_messages: int = 6) -> None:
        self.max_messages = max_messages        # window size
        self.messages: list[dict[str, str]] = []  # stored turns

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})  # append turn
        self.messages = self.messages[-self.max_messages:]        # keep only last N

class LongTermMemory:                           # durable facts per user
    def __init__(self) -> None:
        self.facts: dict[str, dict[str, str]] = {}   # user_id -> {key: value}

    def remember(self, user_id: str, key: str, value: str) -> None:
        self.facts.setdefault(user_id, {})[key] = value   # upsert fact

    def recall(self, user_id: str) -> dict[str, str]:
        return self.facts.get(user_id, {})      # empty dict if unknown user

def build_prompt(user_id: str, st: ShortTermMemory, lt: LongTermMemory, question: str) -> list[dict[str, Any]]:
    facts = "; ".join(f"{k}={v}" for k, v in lt.recall(user_id).items()) or "none"  # facts line
    system = {"role": "system", "content": f"Known user facts: {facts}"}             # inject facts
    return [system, *st.messages, {"role": "user", "content": question}]            # full prompt

if __name__ == "__main__":
    st, lt = ShortTermMemory(max_messages=4), LongTermMemory()   # create stores
    lt.remember("u1", "origin", "VN")           # save a durable fact
    for i in range(6):                          # add 6 turns; only last 4 survive
        st.add("user", f"msg {i}")
    print(build_prompt("u1", st, lt, "Classify charger"))  # inspect prompt
```

## 💻 Code Example — Advanced
```python
# Production-style: async memory manager with summarisation, TTL-less store, error handling.
import asyncio                                  # async
import logging                                  # logs
from dataclasses import dataclass, field        # light data containers
from typing import Awaitable, Callable          # type hints

log = logging.getLogger("memory")               # logger
LLM = Callable[[list[dict[str, str]]], Awaitable[str]]   # async llm(messages) -> text

@dataclass
class ThreadMemory:                             # state for one conversation thread
    summary: str = ""                           # rolling summary of old turns
    messages: list[dict[str, str]] = field(default_factory=list)  # recent turns

class MemoryManager:
    def __init__(self, llm: LLM, max_recent: int = 8) -> None:
        self.llm = llm                          # summariser model (cheap one)
        self.max_recent = max_recent            # when to compact
        self.threads: dict[str, ThreadMemory] = {}   # thread_id -> memory
        self.facts: dict[str, dict[str, str]] = {}   # user_id -> durable facts
        self._lock = asyncio.Lock()             # avoid concurrent write races

    async def add_turn(self, thread_id: str, role: str, content: str) -> None:
        async with self._lock:                  # safe concurrent writes
            mem = self.threads.setdefault(thread_id, ThreadMemory())
            mem.messages.append({"role": role, "content": content})
            if len(mem.messages) > self.max_recent:        # compact when too long
                await self._compact(mem)

    async def _compact(self, mem: ThreadMemory) -> None:
        old, mem.messages = mem.messages[:-4], mem.messages[-4:]   # keep last 4 raw
        prompt = [{"role": "system", "content": "Summarise briefly, keep facts and decisions."},
                  {"role": "user", "content": mem.summary + "\n" + "\n".join(m["content"] for m in old)}]
        try:
            mem.summary = await self.llm(prompt)    # new summary
        except Exception as exc:                    # on failure keep old summary, do not lose data
            log.warning("summary failed: %s", exc)
            mem.messages = old + mem.messages       # restore

    async def context(self, thread_id: str, user_id: str) -> list[dict[str, str]]:
        mem = self.threads.get(thread_id, ThreadMemory())
        facts = ", ".join(f"{k}={v}" for k, v in self.facts.get(user_id, {}).items())
        system = f"User facts: {facts or 'none'}\nConversation summary: {mem.summary or 'none'}"
        return [{"role": "system", "content": system}, *mem.messages]

async def fake_llm(messages: list[dict[str, str]]) -> str:   # offline summariser
    return "Summary: " + messages[-1]["content"][:40]

async def main() -> None:
    mm = MemoryManager(fake_llm, max_recent=4)
    mm.facts["u1"] = {"origin": "VN"}
    for i in range(7):
        await mm.add_turn("t1", "user", f"question {i}")
    print(await mm.context("t1", "u1"))

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI                    # framework
from pydantic import BaseModel                 # validation

app = FastAPI()
mm = MemoryManager(fake_llm)                   # one shared manager (use Redis/DB in real life)

class ChatReq(BaseModel):
    thread_id: str                             # which conversation
    user_id: str                               # which user
    message: str

@app.post("/chat")
async def chat(req: ChatReq) -> dict:
    ctx = await mm.context(req.thread_id, req.user_id)       # load memory
    # answer = await llm_with_tools(ctx + [{"role": "user", "content": req.message}])
    answer = f"(echo) {req.message}"           # placeholder answer
    await mm.add_turn(req.thread_id, "user", req.message)    # save user turn
    await mm.add_turn(req.thread_id, "assistant", answer)    # save assistant turn
    return {"answer": answer}
```
In production, keep memory in Redis or Postgres, not process RAM, because several FastAPI workers do not share Python variables.

---

## 🔗 LangChain / LangGraph Connection
LangGraph gives short-term memory through a **checkpointer** keyed by `thread_id`, and long-term memory through a **store**.

```python
from langgraph.checkpoint.memory import MemorySaver          # short-term (per thread)
from langgraph.prebuilt import create_react_agent             # agent
from langchain_openai import ChatOpenAI                       # model

agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), tools=[],
                           checkpointer=MemorySaver())        # enable thread memory
cfg = {"configurable": {"thread_id": "t1"}}                   # thread key
agent.invoke({"messages": [("user", "I import from Vietnam")]}, cfg)
out = agent.invoke({"messages": [("user", "Where do I import from?")]}, cfg)   # remembers
print(out["messages"][-1].content)
```
For cross-thread facts use `langgraph.store` (e.g. `InMemoryStore`, or a database-backed store in production).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Sending the entire history forever.
✅ Correct: window + summary.

```python
# Wrong
messages = all_history
# Right
messages = [summary_message, *all_history[-6:]]
```

❌ Mistake 2: Saving everything as long-term memory (noise, privacy risk).
✅ Correct: store only durable, useful facts, with user consent and a delete option.

❌ Mistake 3: Global Python dict in a multi-worker server.
✅ Correct: external store (Redis/Postgres) keyed by thread_id.

---

## 🧠 Tricky Interview Question
**Q**: "The agent remembers a user's old wrong HS code and keeps reusing it even after correction. Why, and how do you fix it?"

**Answer**: The old fact is stored in long-term memory (or in an old summary) and was never updated or invalidated. Fixes: use keyed upserts so a correction overwrites the old value, add timestamps and confidence, let newer facts win, delete stale items, and put the memory in the prompt as "may be outdated, verify when critical". Also, summaries can freeze errors, so keep the raw recent turns that contain the correction.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between short-term and long-term memory?
A1: Short-term is the current conversation history (thread scope). Long-term persists across sessions in external storage and is retrieved when relevant.

Q2: Why are LLMs called stateless?
A2: The API remembers nothing between requests. You resend whatever context you want the model to see.

Q3: What are the main ways to manage long history?
A3: Sliding window (last N messages), token-based trimming, rolling summary, and retrieval of relevant past turns from a vector store.

Q4: Summary memory vs vector memory?
A4: Summary compresses everything into a short text (cheap, but lossy). Vector memory stores many items and retrieves the most similar ones (precise, but needs embeddings and may miss context).

Q5: (Hard) How do you design memory for multi-tenant production with privacy needs?
A5: Namespace every record by tenant and user, encrypt at rest, use TTL and delete APIs (right to erasure), avoid storing PII in summaries, apply access control on retrieval, log memory writes, and never let one user's memory enter another user's prompt.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Conversations span many turns or days
- Personalisation matters (preferences, past orders)
- Tasks continue across sessions

❌ Avoid when:
- One-shot, stateless queries
- Data is highly sensitive and not needed later
- Memory would add stale or wrong context

---

## 📊 Visual Diagram
```
            ┌────────── Long-term store (DB / vectors) ◄── extract facts
            │ retrieve                                          ▲
 question ─►├─► Prompt builder ─► LLM ─► answer ─► save turn ───┘
            │        ▲
            └─ Short-term: [summary] + [last N messages]
```

---

## 💰 Cost Impact
Memory directly changes input tokens. A raw history of 20 turns at 150 tokens each adds about 3,000 input tokens to every call. A summary of 200 tokens plus the last 4 turns may be about 800 tokens, so roughly 70% cheaper per call. Summarising has its own cost, so use a small model and compact only occasionally. Retrieval adds embedding cost, but keeps prompts short.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Short-term memory | Current thread history | मौजूदा बातचीत की history |
| Long-term memory | Persistent facts across sessions | Sessions के पार स्थायी facts |
| thread_id | Conversation key | Conversation की key |
| Checkpointer | LangGraph state saver | State save करने वाला |
| Summary buffer | Compressed old turns | पुराने turns का सार |
| Stateless | Remembers nothing per request | हर request पर कुछ याद नहीं |

---

## ⚡ 3-Line Summary
English: LLMs are stateless, so agents add short-term history and long-term stored facts. Trim, summarise and retrieve to control tokens. Store memory externally, namespaced per user.
Hindi: LLM stateless है, इसलिए agent में short-term history और long-term facts जोड़ते हैं। Tokens कम रखने के लिए trim, summary और retrieval करो। Memory को बाहरी store में, user के हिसाब से अलग रखो।

---

## ➡️ Next Topic
**309. Agent with Human in Loop** — pausing the agent for human approval before risky actions.
