---

# 382. Token Budget Management
# हिंदी में: Token Budget Management

---

## 🔵 Simple Definition (English)
Token budget management means setting explicit token limits: per prompt section (system, memory, docs, history), per request, per user per day, and per month. You measure usage and enforce limits so cost and latency stay predictable.

## 🔵 सरल परिभाषा (Hindi)
Token budget management का मतलब है explicit token limits तय करना: prompt के हर हिस्से (system, memory, docs, history), हर request, हर user के daily और monthly लिए। Usage measure करके limits enforce की जाती हैं ताकि cost और latency predictable रहें।

---

## 🔴 Problem it Solves
Without budgets, one user pasting a huge document or a runaway agent loop can burn the monthly bill in an hour. Prompts also grow silently after each feature release.

## 🔴 यह क्यों बना? (Hindi)
Budget के बिना एक user का बड़ा document paste करना या agent का infinite loop एक घंटे में महीने का bill खत्म कर सकता है। हर feature release के बाद prompts चुपचाप बड़े भी होते जाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define budgets: per request (e.g. 6K in / 500 out), per user/day
Step 2 → Split the request budget across sections (percentages)
Step 3 → Count tokens before calling the LLM (tiktoken)
Step 4 → If over budget: trim by priority, or reject with a clear error
Step 5 → Set max_tokens on the call to cap the output
Step 6 → After the call, read response.usage and record real tokens
Step 7 → Update the user's counters; alert at 80 percent, block at 100 percent
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Budgets तय करो: per request (जैसे 6K in / 500 out), per user/day
Step 2 → Request budget को sections में percentage से बाँटो
Step 3 → LLM call से पहले tokens गिनो (tiktoken)
Step 4 → Budget से ज़्यादा हो: priority से trim करो, या साफ़ error दो
Step 5 → Output cap करने के लिए call पर max_tokens लगाओ
Step 6 → Call के बाद response.usage से असली tokens record करो
Step 7 → User के counters update करो; 80 percent पर alert, 100 percent पर block
```

---

## 🟡 Real World Example
**Tariff Classification System**: Free tier users get 20K tokens/day; paid get 500K. A user uploads a 200-page PDF: request budget 8K input, so only top chunks are sent and the answer is capped at 400 tokens. **Zomato-style**: support bot has a 3K-token budget per ticket; beyond it, hand over to a human.

## 🟡 Real Example Hindi mein
**Tariff System**: Free users को 20K tokens/day, paid को 500K मिलते हैं। User 200-page PDF upload करता है: request budget 8K input है, इसलिए सिर्फ़ top chunks जाते हैं और जवाब 400 tokens पर cap होता है। **Zomato-style**: support bot का हर ticket पर 3K-token budget है; उसके बाद human को handover।

---

## 💻 Code Example — Basic
```python
# Pure Python budget allocator. Runs offline. Word count approximates tokens.
SECTION_SHARE = {"system": 0.10, "memory": 0.10, "docs": 0.55, "history": 0.25}   # must sum to 1.0

def allocate(total: int) -> dict[str, int]:
    return {name: int(total * share) for name, share in SECTION_SHARE.items()}    # tokens per section

def trim_to(text: str, limit: int) -> str:
    words = text.split()                                   # crude tokenizer
    return " ".join(words[:limit])                         # keep first `limit` words

budget = allocate(1000)                                    # 1000-token request budget
print(budget)                                              # {'system': 100, 'memory': 100, 'docs': 550, 'history': 250}
doc = "tariff " * 900                                      # oversized document
print(len(trim_to(doc, budget["docs"]).split()))           # 550
```

## 💻 Code Example — Advanced
```python
# Production: per-user daily budget with async lock, pre-check, and real usage accounting.
import asyncio                                             # locks + async
import time                                                # day bucket
import tiktoken                                            # token counting
from openai import AsyncOpenAI, OpenAIError                # LLM client

enc = tiktoken.get_encoding("o200k_base")                  # encoding

class BudgetExceeded(Exception):
    """Raised when a user would exceed the allowed tokens."""

class TokenBudget:
    def __init__(self, daily_limit: int) -> None:
        self.daily_limit = daily_limit                     # tokens per user per day
        self.used: dict[tuple[str, int], int] = {}         # (user, day) -> tokens used
        self.lock = asyncio.Lock()                         # avoid race conditions

    @staticmethod
    def _day() -> int:
        return int(time.time() // 86_400)                  # day number

    async def reserve(self, user: str, estimate: int) -> None:
        async with self.lock:                              # atomic check
            key = (user, self._day())
            if self.used.get(key, 0) + estimate > self.daily_limit:
                raise BudgetExceeded(f"{user} over daily limit")
            self.used[key] = self.used.get(key, 0) + estimate   # reserve estimate

    async def settle(self, user: str, estimate: int, actual: int) -> None:
        async with self.lock:
            key = (user, self._day())
            self.used[key] = self.used.get(key, 0) - estimate + actual   # replace estimate by truth

budget = TokenBudget(daily_limit=20_000)                   # free-tier limit
client = AsyncOpenAI()                                     # needs OPENAI_API_KEY

async def guarded_call(user: str, prompt: str, max_out: int = 400) -> str:
    estimate = len(enc.encode(prompt)) + max_out           # worst case for this call
    await budget.reserve(user, estimate)                   # may raise BudgetExceeded
    try:
        r = await client.chat.completions.create(
            model="gpt-4o-mini", max_tokens=max_out,
            messages=[{"role": "user", "content": prompt}])
    except OpenAIError:
        await budget.settle(user, estimate, 0)             # refund on failure
        raise
    used = r.usage.total_tokens if r.usage else estimate   # real usage
    await budget.settle(user, estimate, used)              # correct the counter
    return r.choices[0].message.content or ""
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException, Header         # app, errors, headers
from pydantic import BaseModel                             # model

app = FastAPI()                                            # app

class Q(BaseModel):
    prompt: str                                            # user text

@app.post("/ask")
async def ask(q: Q, x_user: str = Header(...)) -> dict[str, str]:
    try:
        return {"answer": await guarded_call(x_user, q.prompt)}   # budgeted call
    except BudgetExceeded as exc:
        raise HTTPException(status_code=429, detail=str(exc))     # too many tokens -> 429
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.callbacks import BaseCallbackHandler   # callback base
from langchain_openai import ChatOpenAI                    # model

class UsageHandler(BaseCallbackHandler):
    def __init__(self) -> None:
        self.total = 0                                     # tokens seen

    def on_llm_end(self, response, **kwargs) -> None:
        usage = (response.llm_output or {}).get("token_usage", {})   # OpenAI usage dict
        self.total += usage.get("total_tokens", 0)         # accumulate

h = UsageHandler()                                         # handler
llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=300)      # cap output
# llm.invoke("hi", config={"callbacks": [h]}); print(h.total)
# LangGraph: keep `tokens_used` in state and add a conditional edge to END when it exceeds the limit
# (this also stops agent loops).
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No `max_tokens` on output
✅ Correct: always cap it.

```python
# Wrong
client.chat.completions.create(model=m, messages=msgs)
# Right
client.chat.completions.create(model=m, messages=msgs, max_tokens=400)
```

❌ Mistake 2: Counting only input tokens
✅ Correct: budget input + output (output costs 4x more on many models).

```python
# Wrong
cost = in_tokens * in_price
# Right
cost = in_tokens * in_price + out_tokens * out_price
```

---

## 🧠 Tricky Interview Question
**Q**: "Two concurrent requests from one user both pass the budget check, and the user exceeds the limit. Why, and how to fix?"

**Answer**: Check-then-act race: both read the same counter before either writes. Fix with an atomic reserve step (lock, or Redis `INCRBY` then compare), reserving the worst-case estimate before the call and settling with real usage afterwards.

---

## ⚫ Interview Questions + Answers

Q1: Where do you read real token usage? (Easy)
A1: `response.usage` (prompt_tokens, completion_tokens, total_tokens); streaming needs `stream_options={"include_usage": True}`.

Q2: Why set `max_tokens`? (Easy)
A2: Caps output cost and latency and stops runaway answers.

Q3: How to split a request budget? (Medium)
A3: By section share (system, memory, docs, history), trimming low-priority sections first.

Q4: How to enforce per-user limits at scale? (Medium)
A4: Redis counters with daily TTL keys, atomic increments, reserve then settle, return HTTP 429 with reset time.

Q5: How do you prevent agent loops from overspending? (Hard)
A5: Graph-level token and step counters in state, hard stop via conditional edge, per-run budget, recursion limit, alerts, and cost dashboards per run id.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Public-facing apps, multi-tenant SaaS
- Agents and loops

❌ Avoid strict hard blocks when:
- Internal tools where cutting answers is worse than cost (use alerts instead)

---

## 📊 Visual Diagram
```
 Request budget 6000
 ├─ system   10%  600
 ├─ memory   10%  600
 ├─ docs     55% 3300
 └─ history  25% 1500      + output cap 500 (max_tokens)

 user/day: [########--] 80% -> alert     100% -> HTTP 429
```

---

## 💰 Cost Impact
Budgets bound worst-case spend: 1000 users x 20K tokens/day x 30 days = 600M tokens/month, about $90 input on gpt-4o-mini at $0.15/M (more with output). Optimise by tiering models, trimming docs, using prompt caching, and alerting at 80 percent.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Token budget | Allowed tokens | अनुमत tokens |
| Quota | Per-user limit | per-user सीमा |
| max_tokens | Output cap | output की सीमा |
| Reserve/settle | Hold estimate, then correct | पहले estimate रोको, फिर सही करो |
| 429 | Too many requests | बहुत ज़्यादा requests |

---

## ⚡ 3-Line Summary
English: Set token limits per section, request, user and month. Count before the call, cap output, record real usage after. Reserve atomically to avoid races.
Hindi: Section, request, user और month हर level पर token limits रखो। Call से पहले गिनो, output cap करो, बाद में असली usage record करो। Race से बचने के लिए atomic reserve करो।

---

## ➡️ Next Topic
**383. Memory Compression** - shrink what you store so the budget goes further.
