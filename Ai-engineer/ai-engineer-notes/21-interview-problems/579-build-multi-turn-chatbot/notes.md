---

# 579. Build Multi-turn Chatbot
# हिंदी में: Multi-turn Chatbot बनाना

---

## 🔵 Simple Definition (English)
A multi-turn chatbot remembers earlier messages so a follow-up like "and for its charger?" makes sense. LLM APIs are stateless, so your app stores the history per session and re-sends the right part of it on every call.

## 🔵 सरल परिभाषा (Hindi)
Multi-turn chatbot पिछली बातें याद रखता है, ताकि "और उसके charger का?" जैसे follow-up समझ आएं। LLM API stateless होती है, इसलिए आपका app हर session की history store करता है और हर call में सही हिस्सा दोबारा भेजता है।

---

## 🔴 Problem it Solves
Without memory every message is a fresh start. With naive memory (send everything) the prompt grows each turn, cost grows quadratically across a conversation, and you eventually hit the context limit. Also, mixing two users' histories leaks data.

## 🔴 यह क्यों बना? (Hindi)
Memory के बिना हर message नया होता है। सब कुछ भेजने पर prompt हर turn बढ़ता है, पूरी conversation का cost तेज़ी से बढ़ता है और context limit टूट जाती है। दो users की history मिल जाए तो data leak होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client sends session_id + new message
Step 2 → Load that session's history (dict, Redis, or DB)
Step 3 → Build prompt = system + summary + newest turns within token budget
Step 4 → Call LLM
Step 5 → Append user + assistant turns to history
Step 6 → If history is long, fold old turns into a summary
Step 7 → Return reply (and usage) to client
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Client session_id + नया message भेजता है
Step 2 → उस session की history load करो (dict, Redis, DB)
Step 3 → Prompt = system + summary + token budget में fit होने वाले नए turns
Step 4 → LLM call
Step 5 → User + assistant turns history में जोड़ो
Step 6 → History लंबी हो तो पुराने turns का summary बनाओ
Step 7 → Reply client को लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: User: "HS code for a laptop?" Bot: "8471.30". User: "And its charger?" The bot must know "its" = laptop context. After 20 turns, old turns become a summary like "User is classifying consumer electronics for import to India". **Zomato-style**: "Show veg options" then "under 300" then "which is fastest?" each depends on earlier turns. **Amazon-style**: support chat that remembers the order number from turn 1.

## 🟡 Real Example Hindi mein
**Tariff System**: User: "Laptop का HS code?" Bot: "8471.30"। User: "और उसके charger का?" Bot को पता होना चाहिए कि "उसके" = laptop। 20 turns के बाद पुराने turns का summary बन जाता है। **Zomato**: "Veg options दिखाओ" → "300 के अंदर" → "सबसे तेज़ कौन सा?" हर सवाल पिछले पर टिका है। **Amazon**: support chat जो turn 1 का order number याद रखे।

---

## 💻 Code Example — Basic
Full solution: `main.py` (Session, token-budget trimming, summary compaction, rollback on error).

```python
# Basic: keep history in a list and send it every time
history: list[dict[str, str]] = [{"role": "system", "content": "You are a tariff bot."}]  # start with system

def fake_llm(messages: list[dict[str, str]]) -> str:  # stand-in for a real API
    return f"I can see {len(messages)} messages"  # proves history is sent

def chat(text: str) -> str:  # one turn
    history.append({"role": "user", "content": text})  # remember user turn
    reply = fake_llm(history)  # call the model with full history
    history.append({"role": "assistant", "content": reply})  # remember reply
    return reply  # return to caller

print(chat("HS code for laptop?"))  # 2 messages visible
print(chat("and its charger?"))  # 4 messages visible
```

## 💻 Code Example — Advanced
`main.py` shows: per-session store (`dict[str, Session]`), `build_prompt(budget)` that keeps the newest turns that fit, `compact()` that summarises old turns, rollback of the user turn when the LLM call fails, and an async `chat`.

```python
# Production shape: Redis-backed session with TTL and per-user lock (illustrative)
import asyncio
import json
from typing import Any

class RedisSession:  # wraps an async redis client passed in
    def __init__(self, r: Any, session_id: str, ttl: int = 3600) -> None:  # r: redis.asyncio.Redis
        self.r, self.key, self.ttl = r, f"chat:{session_id}", ttl  # store config
        self.lock = asyncio.Lock()  # serialise turns of one session in this process

    async def load(self) -> list[dict[str, str]]:  # read history
        raw = await self.r.get(self.key)  # fetch JSON string
        return json.loads(raw) if raw else []  # empty list for new session

    async def save(self, history: list[dict[str, str]]) -> None:  # write history
        await self.r.set(self.key, json.dumps(history), ex=self.ttl)  # expire idle chats
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from main import Chatbot  # class from main.py

app = FastAPI()  # app
bot = Chatbot(budget=2000)  # shared bot (use Redis for multi-worker)

class ChatIn(BaseModel):  # request
    session_id: str = Field(min_length=1, max_length=64)  # who is talking
    message: str = Field(min_length=1, max_length=4000)  # what they said

@app.post("/chat")  # route
async def chat(body: ChatIn) -> dict[str, str]:  # handler
    try:  # protect against LLM errors
        reply = await bot.chat(body.session_id, body.message)  # run a turn
    except ValueError as exc:  # empty message
        raise HTTPException(422, str(exc))  # client error
    return {"reply": reply}  # response
```

---

## 🔗 LangChain / LangGraph Connection
Modern LangChain uses `RunnableWithMessageHistory`; LangGraph uses a checkpointer (`MemorySaver`, Postgres, etc.) keyed by `thread_id`, which is the production-recommended way to persist state.

```python
# Illustrative LangGraph persistence (pip install langgraph langchain-openai)
from langgraph.checkpoint.memory import MemorySaver  # in-memory checkpointer
from langgraph.graph import StateGraph, MessagesState, START, END  # graph pieces

def build(llm):  # llm: any chat model
    def call(state: MessagesState) -> dict:  # one node
        return {"messages": [llm.invoke(state["messages"])]}  # append reply
    g = StateGraph(MessagesState)  # state holds the message list
    g.add_node("llm", call)  # add node
    g.add_edge(START, "llm")  # entry
    g.add_edge("llm", END)  # exit
    return g.compile(checkpointer=MemorySaver())  # memory per thread_id

# usage: app.invoke({"messages": [("user", "hi")]}, config={"configurable": {"thread_id": "u1"}})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: One global history for all users
✅ Correct: Key by session_id.

```python
# Wrong: everyone shares one list
history = []
# Right: one list per session
sessions: dict[str, list[dict[str, str]]] = {}
sessions.setdefault("user-1", []).append({"role": "user", "content": "hi"})
```

❌ Mistake 2: Unlimited history
✅ Correct: Trim by tokens and summarise.

```python
# Wrong: prompt grows forever
prompt = history
# Right: keep newest turns within budget (see build_prompt in main.py)
budget, used, kept = 200, 0, []
for m in reversed(history if 'history' in dir() else []):
    used += len(m["content"]) // 4
    if used > budget:
        break
    kept.append(m)
```

---

## 🧠 Tricky Interview Question
**Q**: "After 30 turns the bot forgets the user's country, mentioned in turn 2, and gives wrong duty rates. You trim to the last 10 turns. How do you fix it?"

**Answer**: Sliding windows drop facts that matter. Separate durable facts from chat: extract key entities (country, product, currency) into a structured "profile" stored outside the window and injected into the system prompt each turn, and summarise the rest. This is memory layering: short-term window, rolling summary, long-term facts. Test with a "recall turn 2 at turn 30" evaluation.

---

## ⚫ Interview Questions + Answers

Q1: Why are LLM APIs "stateless"? (Easy)
A1: Each request is independent; the model keeps nothing between calls. You must resend context you want it to use.

Q2: Why key memory by session_id? (Easy)
A2: To isolate users, prevent data leakage and allow concurrent conversations.

Q3: Sliding window vs summary memory? (Medium)
A3: Window keeps recent turns verbatim (cheap, loses old facts). Summary compresses old turns (keeps gist, may lose detail and costs an extra LLM call). Combine both, plus a facts store.

Q4: How do you handle concurrent messages in one session? (Medium)
A4: Use a per-session lock or a queue so turns are processed in order; otherwise history can interleave and responses answer the wrong question.

Q5: How do you scale the chatbot to many workers and keep latency low? (Hard)
A5: Store sessions in Redis/Postgres (not process memory), stream tokens (SSE/WebSocket) for perceived speed, use prompt caching for the stable system prompt, summarise asynchronously off the request path, set TTLs, and use sticky routing or optimistic versioning to avoid lost updates.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Users ask follow-ups that reference earlier answers
- Support, onboarding or guided workflows

❌ Avoid when:
- Requests are independent (classification API): stateless is cheaper and simpler
- Privacy rules forbid retaining user text

---

## 📊 Visual Diagram
```
 user msg + session_id
        │
        ▼
 ┌───────────────┐   load    ┌─────────────┐
 │  Chat service │◄─────────►│ Session store│
 └──────┬────────┘   save    └─────────────┘
        │ prompt = system + summary + recent turns (<= budget)
        ▼
      LLM  ──► reply ──► append to history ──► compact if long
```

---

## 💰 Cost Impact
Input tokens per turn = system + summary + history. Resending full history makes total tokens across n turns grow roughly like n squared. Example (illustrative): 20 turns x 150 tokens each means turn 20 re-sends about 3,000 tokens. Optimise: token-budget trimming, summaries, prompt caching on the stable prefix (check your provider's caching discount), small model for summarising, and `max_tokens` on replies.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Stateless | No memory between calls | कोई याददाश्त नहीं |
| Session | One user's conversation | एक user की बातचीत |
| Context window | Max tokens per call | एक call में max tokens |
| Sliding window | Keep newest N turns | नए N turns रखना |
| Rolling summary | Compressed old turns | पुराने turns का सार |
| Checkpointer | Saves graph state | State save करने वाला |

---

## ⚡ 3-Line Summary
English: LLMs forget, so your app stores history per session. Trim by token budget and summarise old turns. Keep key facts outside the window.
Hindi: LLM भूल जाता है, इसलिए app हर session की history रखता है। Token budget से trim करो और पुराने turns का summary बनाओ। ज़रूरी facts window के बाहर रखो।

---

## ➡️ Next Topic
**580. Build Agent with Tools** — let the bot act (look up codes, calculate duty) instead of only talking.
