---

# 366. Memory in AI Apps — Types
# हिंदी में: AI Apps में Memory — प्रकार

---

## 🔵 Simple Definition (English)
An LLM is stateless: every API call starts from zero. "Memory" is the code *around* the LLM that stores past information and puts the useful part back into the next prompt. Main types: in-context (inside the prompt), external (database), episodic (past events), semantic (facts), procedural (how-to rules).

## 🔵 सरल परिभाषा (Hindi)
LLM stateless होता है: हर API call शून्य से शुरू होती है। "Memory" वह code है जो LLM के आसपास पुरानी जानकारी store करता है और काम की जानकारी अगले prompt में वापस डालता है। मुख्य प्रकार: in-context (prompt के अंदर), external (database), episodic (पुरानी घटनाएँ), semantic (facts), procedural (कैसे करना है के rules)।

---

## 🔴 Problem it Solves
- User says "My product is a leather wallet" and next message asks "What is its HS code?" — a stateless LLM has no idea what "its" means.
- Context windows are finite and tokens cost money, so we cannot resend everything forever.
- Users expect the assistant to remember them across days, not only inside one chat.

## 🔴 यह क्यों बना? (Hindi)
- User ने कहा "मेरा product leather wallet है", फिर पूछा "इसका HS code?" — stateless LLM को "इसका" समझ नहीं आएगा।
- Context window सीमित है और tokens के पैसे लगते हैं, इसलिए सब कुछ बार-बार नहीं भेज सकते।
- User चाहता है कि assistant दिनों बाद भी उसे याद रखे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → User sends a message
Step 2 → Memory layer LOADS relevant memory (recent turns, summary, facts, past events)
Step 3 → Prompt = system rules + loaded memory + new message
Step 4 → LLM answers (it only "knows" what is in this prompt)
Step 5 → Memory layer SAVES the new turn (and may extract facts / update summary)
Step 6 → Repeat. Quality of memory = quality of what you load in Step 2
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → User message भेजता है
Step 2 → Memory layer काम की memory LOAD करती है (recent turns, summary, facts)
Step 3 → Prompt = system rules + memory + नया message
Step 4 → LLM जवाब देता है (उसे सिर्फ prompt की जानकारी पता है)
Step 5 → नया turn SAVE होता है (facts extract / summary update भी हो सकता है)
Step 6 → दोहराओ। Memory की quality = Step 2 में क्या load किया
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs broker chats: "I import cotton t-shirts from Bangladesh" (episodic + semantic fact), "always show duty in INR" (procedural preference), later "what is the duty?" — the bot must combine the product (semantic), the country (semantic), the INR rule (procedural), and the last 3 messages (in-context).
**Zomato AI**: remembers "vegetarian, no onion" (semantic), "ordered biryani last Friday" (episodic).

## 🟡 Real Example Hindi mein
**Tariff System**: Broker कहता है "मैं Bangladesh से cotton t-shirts import करता हूँ" (fact), "duty हमेशा INR में दिखाओ" (preference/rule)। बाद में "duty कितनी?" पूछे तो bot को product, country, INR rule और पिछले 3 messages सब मिलाने होंगे।
**Zomato AI**: "veg, बिना प्याज" याद रखता है (semantic) और "पिछले शुक्रवार biryani मंगाई" (episodic)।

---

## 💻 Code Example — Basic
```python
# Pure Python, runs offline: shows the 5 memory types as plain data structures
from dataclasses import dataclass, field          # dataclass gives us tidy containers

@dataclass                                         # one object holding all memory kinds
class AppMemory:
    in_context: list[dict[str, str]] = field(default_factory=list)   # recent chat turns (short-term)
    semantic: dict[str, str] = field(default_factory=dict)           # stable facts about user
    episodic: list[str] = field(default_factory=list)                # past events with time
    procedural: list[str] = field(default_factory=list)              # rules: how the bot should act
    external_store: dict[str, str] = field(default_factory=dict)     # stand-in for a database

    def build_prompt(self, question: str) -> str:                    # assemble the final prompt text
        parts: list[str] = []                                        # collect prompt pieces
        parts.append("RULES: " + "; ".join(self.procedural))         # procedural memory first
        parts.append("FACTS: " + str(self.semantic))                 # semantic memory next
        parts.append("PAST: " + "; ".join(self.episodic[-2:]))       # last 2 episodes only
        for turn in self.in_context[-4:]:                            # last 4 turns only
            parts.append(f"{turn['role']}: {turn['content']}")       # replay the turn
        parts.append(f"user: {question}")                            # the new question
        return "\n".join(parts)                                      # one string prompt

mem = AppMemory()                                                    # create empty memory
mem.semantic["product"] = "cotton t-shirt"                           # store a fact
mem.semantic["origin"] = "Bangladesh"                                # store another fact
mem.procedural.append("Show duty in INR")                            # store a rule
mem.episodic.append("2025-01-10: classified HS 6109 for t-shirts")   # store an event
mem.in_context.append({"role": "user", "content": "Hello"})          # store a turn
print(mem.build_prompt("What is the duty?"))                         # see the assembled prompt
```

## 💻 Code Example — Advanced
```python
# Production-style: a MemoryManager interface + async implementation with error handling
import asyncio                                                       # for the async demo
from abc import ABC, abstractmethod                                  # to define an interface
from typing import Protocol                                          # structural typing for the LLM


class LLM(Protocol):                                                 # anything with async generate()
    async def generate(self, prompt: str) -> str: ...                # returns the model text


class MemoryStore(ABC):                                              # every memory type implements this
    @abstractmethod
    async def load(self, user_id: str, query: str) -> str: ...       # return text to put in prompt

    @abstractmethod
    async def save(self, user_id: str, user_msg: str, bot_msg: str) -> None: ...  # persist the turn


class BufferStore(MemoryStore):                                      # simplest: keep last N turns
    def __init__(self, max_turns: int = 6) -> None:                  # N is a token-cost knob
        self.max_turns = max_turns                                   # remember the limit
        self._data: dict[str, list[tuple[str, str]]] = {}            # user_id -> list of turns

    async def load(self, user_id: str, query: str) -> str:           # build the history text
        turns = self._data.get(user_id, [])[-self.max_turns:]        # slice to the window
        return "\n".join(f"U: {u}\nA: {a}" for u, a in turns)        # flatten to text

    async def save(self, user_id: str, user_msg: str, bot_msg: str) -> None:  # append turn
        self._data.setdefault(user_id, []).append((user_msg, bot_msg))        # create list if needed


class FakeLLM:                                                       # offline stand-in for an API
    async def generate(self, prompt: str) -> str:                    # pretend to answer
        return f"(echo {len(prompt)//4} prompt tokens)"              # ~4 chars per token


async def chat(llm: LLM, store: MemoryStore, user_id: str, msg: str) -> str:  # one chat turn
    try:                                                             # guard memory + LLM failures
        history = await store.load(user_id, msg)                     # step 2: load memory
    except Exception:                                                # memory down must not kill chat
        history = ""                                                 # degrade gracefully
    prompt = f"{history}\nU: {msg}\nA:"                              # step 3: build prompt
    answer = await llm.generate(prompt)                              # step 4: call the model
    try:                                                             # saving can also fail
        await store.save(user_id, msg, answer)                       # step 5: persist the turn
    except Exception:                                                # log in real code
        pass                                                         # do not lose the answer
    return answer                                                    # return to caller


async def main() -> None:                                            # demo runner
    store, llm = BufferStore(), FakeLLM()                            # wire the pieces
    for m in ["I sell wallets", "HS code?", "Duty in INR?"]:         # three turns
        print(await chat(llm, store, "u1", m))                       # prompt grows each turn


if __name__ == "__main__":                                           # script entry point
    asyncio.run(main())                                              # run the async demo
```

---

## 🟠 FastAPI Integration
Memory is keyed by `user_id` / `session_id`. The route loads memory, calls the LLM, saves the turn. Never keep memory in a Python global in production (multiple workers = different memory) — use Redis/Postgres.

```python
# FastAPI route using the MemoryStore + LLM from the advanced example
from fastapi import FastAPI, HTTPException        # web framework + HTTP errors
from pydantic import BaseModel, Field             # request validation (pydantic v2)

app = FastAPI()                                   # create the app
store = BufferStore(max_turns=6)                  # swap for RedisStore in production
llm = FakeLLM()                                   # swap for AsyncOpenAI wrapper

class ChatIn(BaseModel):                          # request schema
    user_id: str = Field(min_length=1)            # who is chatting
    message: str = Field(min_length=1, max_length=4000)  # limit input size = limit cost

@app.post("/chat")                                # POST /chat
async def chat_route(body: ChatIn) -> dict[str, str]:   # typed response
    try:                                          # catch unexpected errors
        answer = await chat(llm, store, body.user_id, body.message)  # reuse our function
    except Exception as exc:                      # LLM/network failure
        raise HTTPException(status_code=502, detail="LLM error") from exc  # clean error
    return {"answer": answer}                     # JSON response
```

---

## 🔗 LangChain / LangGraph Connection
LangChain: `RunnableWithMessageHistory` + a chat history class = short-term memory. LangGraph: a **checkpointer** (`MemorySaver`, Postgres saver) = per-thread short-term memory, and a **Store** (`InMemoryStore`) = cross-thread long-term memory.

```python
# LangGraph: short-term (checkpointer, per thread) + long-term (store, per user)
from langgraph.checkpoint.memory import MemorySaver    # in-RAM checkpointer (dev only)
from langgraph.store.memory import InMemoryStore       # in-RAM long-term store (dev only)

checkpointer = MemorySaver()                           # saves graph state per thread_id
store = InMemoryStore()                                # saves facts per namespace
store.put(("users", "u1"), "profile", {"origin": "Bangladesh"})  # long-term fact
# graph = builder.compile(checkpointer=checkpointer, store=store)   # attach both
# graph.invoke(input, config={"configurable": {"thread_id": "t1"}})  # thread = short-term scope
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Assuming the LLM remembers by itself
✅ Correct: send history yourself.

```python
# Wrong: second call has no idea about the first
client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "Its HS code?"}])
# Right: include earlier turns
messages = history + [{"role": "user", "content": "Its HS code?"}]
```

❌ Mistake 2: Storing everything forever and sending all of it
✅ Correct: window, summarize, or retrieve only what is relevant.

```python
# Wrong: prompt grows each turn -> cost and latency explode, finally context error
prompt = "\n".join(all_turns_ever)
# Right: bounded memory
prompt = "\n".join(all_turns_ever[-6:])
```

---

## 🧠 Tricky Interview Question
**Q**: "Your bot remembers the user's name inside one chat but forgets it tomorrow. You added a bigger context window. Does it fix it?"

**Answer**: No. A bigger window only holds more of the *current* prompt; it does not persist anything between sessions. Persistence needs external (long-term) memory: save facts (e.g. name) in a DB keyed by user_id, and load them at the start of every new session. Context window = RAM; external memory = disk.

---

## ⚫ Interview Questions + Answers

Q1: Why are LLMs called stateless?
A1: Each API call is independent; the model keeps nothing between calls. All "memory" is text you resend in the prompt.

Q2: Name the main memory types.
A2: In-context (short-term), external/long-term, episodic (events), semantic (facts), procedural (rules/skills).

Q3: Difference between short-term and long-term memory in LangGraph?
A3: Short-term = checkpointer state scoped to a `thread_id`. Long-term = Store scoped by namespace (e.g. user) and shared across threads.

Q4: How does memory change token cost?
A4: Every remembered token that you place in the prompt is billed as input on every call. Cost per turn grows with memory size, so you must bound it (window/summary/retrieval).

Q5: Design memory for a multi-tenant support bot with 1M users.
A5: Redis for hot recent turns (TTL), Postgres/vector DB for long-term facts per user, async background job to extract facts and summaries after the response (not in the request path), per-user namespaces for isolation and GDPR delete, token budget per prompt section, and metrics on memory hit-rate and cost per turn.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multi-turn chat, follow-up questions ("its", "that one")
- Personalisation across sessions
- Long agent tasks that exceed one context window

❌ Avoid when:
- Single-shot tasks (classify one text) — memory only adds cost
- Sensitive data you are not allowed to store

---

## 📊 Visual Diagram
```
            ┌──────────── Memory Layer ─────────────┐
 User msg ─▶│ in-context │ semantic │ episodic │ rules│
            └───────┬───────────────────────────────┘
                    │ load (bounded by token budget)
                    ▼
        [system + memory + question] ──▶ LLM ──▶ answer
                    ▲                               │
                    └────── save / extract ◀────────┘
```

---

## 💰 Cost Impact
- Input tokens are billed every call: 2,000 tokens of memory x 100K calls/day x $0.15/1M = $30/day on gpt-4o-mini; same on gpt-4o ($2.50/1M, check current pricing) is far more.
- Optimise: bound the window, summarise old turns, retrieve only relevant facts, use prompt caching for the static part (rules + facts first, changing part last), run fact-extraction with a cheap model in the background.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Stateless | No memory between calls | कॉल के बीच कोई याद नहीं |
| In-context memory | History inside the prompt | Prompt के अंदर की memory |
| External memory | DB outside the model | Model के बाहर database |
| Episodic | Past events | पुरानी घटनाएँ |
| Semantic | Stable facts | स्थायी facts |
| Procedural | Rules / how-to | नियम / कैसे करना है |
| Thread | One conversation scope | एक बातचीत का scope |

---

## ⚡ 3-Line Summary
English: LLMs forget everything between calls, so memory is code that re-injects useful past info. Types: in-context, external, episodic, semantic, procedural. Always bound memory size because every token costs money.
Hindi: LLM हर call के बाद भूल जाता है, इसलिए memory वह code है जो पुरानी जानकारी वापस prompt में डालता है। प्रकार: in-context, external, episodic, semantic, procedural। Memory का size सीमित रखो क्योंकि हर token का पैसा लगता है।

---

## ➡️ Next Topic
**367. In-Context Memory** — the simplest memory: keep the history directly in the prompt, and where it breaks.
