---

# 571. Build Basic LLM Chat (FastAPI)
# हिंदी में: Basic LLM Chat बनाना (FastAPI)

---

## 🔵 Simple Definition (English)
A basic LLM chat service is a FastAPI app with a `/chat` route. It keeps each user's conversation history, sends the recent messages to an LLM, and returns the reply plus token counts. The model is hidden behind a small interface so you can swap a real model for a mock.

## 🔵 सरल परिभाषा (Hindi)
Basic LLM chat service एक FastAPI app है जिसमें `/chat` route होता है। यह हर user की conversation history रखता है, हाल के messages LLM को भेजता है और reply के साथ token counts लौटाता है। Model एक छोटे interface के पीछे रहता है ताकि real model की जगह mock लगाया जा सके।

---

## 🔴 Problem it Solves
LLM APIs are stateless: each call forgets earlier turns. The interviewer wants to see that you can (1) add memory, (2) validate input, (3) limit cost, (4) handle timeouts and errors, and (5) keep the code testable without an API key.

## 🔴 यह क्यों बना? (Hindi)
LLM APIs stateless हैं: हर call पिछली बातें भूल जाती है। Interviewer देखना चाहता है कि आप (1) memory जोड़ सकते हैं, (2) input validate कर सकते हैं, (3) cost सीमित कर सकते हैं, (4) timeout/errors संभाल सकते हैं, (5) code API key के बिना testable रख सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client POSTs {"session_id": optional, "message": "..."}
Step 2 → Pydantic validates length (422 if bad)
Step 3 → Service loads history by session_id (or creates a new session)
Step 4 → Append the user turn, keep only the last N messages (cost control)
Step 5 → Build messages = [system] + window, call LLM with a timeout
Step 6 → On success append the assistant turn; on timeout drop the user turn and return 504
Step 7 → Return {session_id, reply, tokens_in, tokens_out}
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Client {"session_id": optional, "message": "..."} POST करता है
Step 2 → Pydantic length validate करता है (गलत हो तो 422)
Step 3 → Service session_id से history लाती है (या नया session बनाती है)
Step 4 → User turn जोड़ो, सिर्फ आखिरी N messages रखो
Step 5 → messages = [system] + window बनाकर timeout के साथ LLM call
Step 6 → सफल: assistant turn जोड़ो; timeout: user turn हटाओ और 504 दो
Step 7 → {session_id, reply, tokens_in, tokens_out} लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs officer chats: "HS code for a smartphone?" then "And for a laptop?". The second question works because history is sent. The service logs tokens per session so finance can see cost per officer.

**Zomato-style**: "Suggest dinner" then "make it vegetarian" relies on the same memory mechanism.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs officer पूछता है "Smartphone का HS code?" फिर "और laptop का?"। दूसरा सवाल इसलिए काम करता है क्योंकि history भेजी जाती है। Service हर session के tokens log करती है ताकि finance cost per officer देख सके।

---

## 💻 Code Example — Basic
Full runnable file: `main.py` in this folder (`python main.py` runs an offline demo with a mock model; I ran it and it printed a session id, a mock reply, history size 4, and the rejection of an empty message).

Core idea (simplified from `main.py`):
```python
# Keep history, trim it, call the model, store the reply
from typing import Protocol  # interface typing


class LLM(Protocol):
    async def complete(self, messages: list[dict[str, str]]) -> str: ...  # model contract


async def chat(llm: LLM, history: list[dict[str, str]], text: str) -> str:
    history.append({"role": "user", "content": text})            # remember user turn
    window = history[-10:]                                       # only the last 10 messages
    reply = await llm.complete([{"role": "system", "content": "Be concise."}, *window])  # call model
    history.append({"role": "assistant", "content": reply})      # remember answer
    return reply                                                 # return to caller
```

## 💻 Code Example — Advanced
`main.py` contains the production-style version: `ChatService` (validation, session store, trimming, `asyncio.wait_for` timeout, rollback of the failed turn), `OpenAILLM` using `AsyncOpenAI`, `MockLLM`, and token counts from `response.usage`.

```python
# Excerpt: the error-handling core of ChatService.chat in main.py
try:
    reply, tin, tout = await asyncio.wait_for(self.llm.complete(messages), timeout=30)  # bounded call
except asyncio.TimeoutError as exc:
    history.pop()                          # drop the unanswered user turn (keeps history consistent)
    raise RuntimeError("model timed out") from exc   # route maps this to HTTP 504
```
Production notes: store sessions in Redis with a TTL (the in-memory dict is lost on restart and not shared between workers), add per-user rate limits, and summarise old turns instead of just dropping them.

---

## 🟠 FastAPI Integration
```python
# From main.py: thin route, logic in the service, errors mapped to HTTP codes
@app.post("/chat")
async def chat(body: ChatIn) -> dict[str, object]:
    try:
        return await service.chat(body.session_id, body.message)   # delegate to service
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc   # client mistake
    except RuntimeError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc   # upstream timeout
```
Run: `pip install fastapi uvicorn` then `uvicorn main:app --reload` (not run in this environment: FastAPI was not installed, so only the offline demo was executed).

---

## 🔗 LangChain / LangGraph Connection
The same service in LangChain uses `ChatOpenAI` plus message history (`RunnableWithMessageHistory` in current LangChain, or LangGraph's checkpointer with a `thread_id`, which is the recommended modern approach). `thread_id` plays the role of `session_id`.

```python
# LangGraph: memory via checkpointer, thread_id == session_id (illustrative; verify API in docs)
# from langgraph.checkpoint.memory import MemorySaver
# from langgraph.prebuilt import create_react_agent
# agent = create_react_agent("openai:gpt-4o-mini", tools=[], checkpointer=MemorySaver())
# agent.invoke({"messages": [("user", "HS code for a phone?")]},
#              config={"configurable": {"thread_id": "officer-1"}})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Sending the full, ever-growing history
✅ Correct: Trim or summarise so cost stays bounded.
```python
# Wrong
messages = history                 # grows forever -> cost and latency explode, context overflow
# Right
messages = history[-10:]           # sliding window (or summary + last few turns)
```

❌ Mistake 2: Blocking call inside an async route
✅ Correct: Use the async client or `asyncio.to_thread`.
```python
# Wrong
@app.post("/chat")
async def c():
    return OpenAI().chat.completions.create(...)     # blocks the event loop for every user
# Right
    return await AsyncOpenAI().chat.completions.create(...)
```

---

## 🧠 Tricky Interview Question
**Q**: "You run uvicorn with 4 workers and a user's second message sometimes forgets the first. Why?"

**Answer**: Sessions live in each worker process's memory. Requests land on different workers, so the history is missing. Fix: external store (Redis/Postgres) keyed by session id, or sticky routing as a stopgap. Also set a TTL and guard against concurrent writes to the same session (use an atomic append or a lock).

---

## ⚫ Interview Questions + Answers

Q1: Why are LLM APIs "stateless"?
A1: Each request is independent; the model only sees the messages you send, so you must resend history.

Q2: What does `max_tokens` do?
A2: Caps output length, so it caps output cost and latency.

Q3: How would you stop one user from draining your budget?
A3: Per-user rate limits and daily token quotas, input size caps, and `max_tokens`; track `usage` per user.

Q4: Where should the system prompt live and why?
A4: In the service layer, added server-side on each call, so clients cannot override it; version it in config.

Q5: How do you handle provider outages?
A5: Timeouts, retries with exponential backoff and jitter on 429/5xx only, circuit breaker, fallback model, and a clear 503/504 to the client.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Simple assistant with short conversations
- Prototype or interview baseline

❌ Avoid when:
- Long conversations (need summarisation) or tools/RAG (need an agent/RAG design)
- Multi-instance deployments with in-memory sessions

---

## 📊 Visual Diagram
```
Client ──POST /chat──► FastAPI route (Pydantic validation)
                           │
                           ▼
                     ChatService
        ┌──────────────────┼───────────────────┐
        ▼                  ▼                   ▼
   session store     trim to last N      LLM (real|mock)
   (Redis in prod)   + system prompt     timeout 30s
        └──────────────────┴─────► reply + tokens ──► Client
```

---

## 💰 Cost Impact
Every turn resends the window, so input tokens grow with history. Example: 10 messages x ~80 tokens + system 30 = ~830 input tokens and ~150 output per turn. At illustrative `gpt-4o-mini` prices ($0.15/M input, $0.60/M output) that is about $0.00021 per turn. Optimise: smaller window, summarise old turns, cap `max_tokens`, cache identical questions, route trivial questions to a cheaper model.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Stateless | No memory between calls | कोई याददाश्त नहीं |
| Session | One user's conversation | एक user की बातचीत |
| Sliding window | Keep last N messages | आखिरी N messages रखना |
| Timeout | Max wait time | अधिकतम इंतज़ार |
| Protocol | Interface type | Interface का type |
| TTL | Auto-expiry time | अपने आप खत्म होने का समय |

---

## ⚡ 3-Line Summary
English: A chat API stores per-session history, trims it, calls the model with a timeout, and returns reply plus tokens. Hide the model behind an interface so tests run offline. Use Redis for sessions in production.
Hindi: Chat API per-session history रखती है, उसे trim करती है, timeout के साथ model call करती है और reply + tokens लौटाती है। Model को interface के पीछे रखें ताकि tests offline चलें। Production में sessions के लिए Redis इस्तेमाल करें।

---

## ➡️ Next Topic
**572. Build RAG from Scratch** — add retrieval so the chat answers from your own documents.
