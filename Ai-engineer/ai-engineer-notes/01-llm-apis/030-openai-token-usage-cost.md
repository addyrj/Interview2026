---

# 030. OpenAI API — Token Usage + Cost
# हिंदी में: OpenAI API — Token Usage + Cost

---

## 🔵 Simple Definition (English)
Every OpenAI response includes a `usage` object with `prompt_tokens`, `completion_tokens`, and `total_tokens`. Cost equals input tokens times the input price plus output tokens times the output price. Tracking this per request, per user, and per feature is how you control your AI bill.

## 🔵 सरल परिभाषा (Hindi)
हर OpenAI response में `usage` object होता है: `prompt_tokens`, `completion_tokens` और `total_tokens`। Cost = input tokens x input price + output tokens x output price। इसे हर request, user और feature के हिसाब से track करना ही AI bill control करने का तरीका है।

---

## 🔴 Problem it Solves
LLM bills surprise teams: a prompt bug that doubles context, a loop that retries forever, or one heavy user can multiply costs overnight. Without per-call tracking you cannot find which feature or customer is expensive, cannot set budgets, and cannot prove ROI.

## 🔴 यह क्यों बना? (Hindi)
LLM के bills चौंकाते हैं: prompt bug से context दोगुना, retry loop, या एक भारी user रातों-रात cost कई गुना कर सकता है। Per-call tracking के बिना पता नहीं चलता कौन सा feature या customer महंगा है, budgets नहीं लग सकते और ROI साबित नहीं होता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Make the API call
Step 2 → Read response.usage (prompt_tokens, completion_tokens, total_tokens)
Step 3 → Look up the price per 1M tokens for the model used (response.model)
Step 4 → cost = in * p_in/1e6 + out * p_out/1e6
Step 5 → Subtract cached tokens if the response reports them (usage.prompt_tokens_details.cached_tokens)
Step 6 → Store a row: time, user, feature, model, tokens, cost
Step 7 → Aggregate per day/user/feature, compare against budgets
Step 8 → Alert or throttle when a budget is crossed
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → API call करो
Step 2 → response.usage पढ़ो (prompt_tokens, completion_tokens, total_tokens)
Step 3 → इस्तेमाल हुए model की price per 1M tokens देखो (response.model)
Step 4 → cost = in * p_in/1e6 + out * p_out/1e6
Step 5 → Response में cached tokens हों तो उनका discount गिनो (usage.prompt_tokens_details.cached_tokens)
Step 6 → एक row store करो: time, user, feature, model, tokens, cost
Step 7 → दिन/user/feature के हिसाब से aggregate करो, budgets से compare करो
Step 8 → Budget पार होने पर alert या throttle करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Each classification averages 900 input and 40 output tokens. At 50,000 classifications per day on an illustrative $0.15 / $0.60 per 1M price, the daily cost is about $7.9. A bug that adds the full chapter text (6,000 tokens) to each prompt would raise it to about $46 per day. Per-feature tracking shows the jump the same day.

**Amazon-style AI**: Cost per conversation is tracked by product team, so the "review summary" feature can be compared against its revenue impact.

## 🟡 Real Example Hindi mein
**Tariff Classification System**: हर classification में औसतन 900 input और 40 output tokens लगते हैं। रोज़ 50,000 classifications पर, illustrative $0.15 / $0.60 per 1M price से, daily cost लगभग $7.9 है। अगर bug से पूरा chapter text (6,000 tokens) हर prompt में जुड़ जाए तो cost लगभग $46 प्रतिदिन हो जाएगी। Per-feature tracking उसी दिन यह उछाल दिखा देती है।

**Amazon-style AI**: Product team के हिसाब से cost per conversation track होती है, ताकि "review summary" feature की cost उसके revenue impact से compare हो सके।

---

## 💻 Code Example — Basic
```python
# Basic cost calculator from a usage object (runs offline using a fake usage)
from dataclasses import dataclass               # simple data holder

@dataclass
class Usage:
    prompt_tokens: int                          # input tokens
    completion_tokens: int                      # output tokens

# Illustrative USD per 1M tokens (input, output). Verify on the official pricing page.
PRICES = {"gpt-4o-mini": (0.15, 0.60), "gpt-4o": (2.50, 10.00)}

def cost_usd(model: str, u: Usage) -> float:
    p_in, p_out = PRICES[model]                 # unpack prices for this model
    # cost = tokens / 1,000,000 * price per million
    return u.prompt_tokens / 1e6 * p_in + u.completion_tokens / 1e6 * p_out

fake = Usage(prompt_tokens=900, completion_tokens=40)    # what response.usage would hold
c = cost_usd("gpt-4o-mini", fake)                        # cost of one call
print(f"one call: ${c:.6f}")                             # per-call cost
print(f"50k calls/day: ${c * 50_000:.2f}")               # daily cost
print(f"30 days: ${c * 50_000 * 30:,.2f}")               # monthly cost

# With the real API, the object comes from the response:
# r = client.chat.completions.create(...)
# cost_usd(r.model, r.usage)    # r.usage has prompt_tokens and completion_tokens
```

## 💻 Code Example — Advanced
```python
# Production cost tracker with budgets, per-feature totals, sync + async capture
import asyncio                                           # async runner
import logging                                           # logs
import threading                                         # lock for thread safety
from collections import defaultdict                      # grouped totals
from typing import DefaultDict, Optional                 # type hints

from openai import AsyncOpenAI, OpenAIError              # client + base error

logger = logging.getLogger(__name__)                     # logger

PRICES = {"gpt-4o-mini": (0.15, 0.60), "gpt-4o": (2.50, 10.00)}   # illustrative


class BudgetExceeded(RuntimeError):
    """Raised when a feature passes its daily budget."""


class CostTracker:
    def __init__(self, daily_budget_usd: float = 10.0) -> None:
        self.budget = daily_budget_usd                   # per feature per day
        self.spent: DefaultDict[str, float] = defaultdict(float)   # feature -> USD
        self.tokens: DefaultDict[str, int] = defaultdict(int)      # feature -> tokens
        self._lock = threading.Lock()                    # protect shared dicts

    @staticmethod
    def price(model: str, prompt: int, completion: int) -> float:
        # Match dated names like gpt-4o-mini-2024-07-18 by longest known prefix
        key = max((k for k in PRICES if model.startswith(k)), key=len, default=None)
        if key is None:
            logger.warning("unknown model price: %s", model)
            return 0.0
        p_in, p_out = PRICES[key]
        return prompt / 1e6 * p_in + completion / 1e6 * p_out

    def record(self, feature: str, model: str, prompt: int, completion: int) -> float:
        c = self.price(model, prompt, completion)        # cost of this call
        with self._lock:                                 # thread-safe update
            self.spent[feature] += c
            self.tokens[feature] += prompt + completion
            if self.spent[feature] > self.budget:        # over budget?
                raise BudgetExceeded(f"{feature} spent ${self.spent[feature]:.2f}")
        return c


tracker = CostTracker(daily_budget_usd=5.0)              # shared tracker
client = AsyncOpenAI(timeout=30.0)                       # shared client


async def tracked_chat(feature: str, prompt: str, model: str = "gpt-4o-mini") -> Optional[str]:
    try:
        r = await client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}], max_tokens=200)
    except OpenAIError as exc:
        logger.error("call failed: %s", exc)
        return None
    cost = tracker.record(feature, r.model, r.usage.prompt_tokens, r.usage.completion_tokens)
    logger.info("feature=%s cost=$%.6f", feature, cost)
    return r.choices[0].message.content


if __name__ == "__main__":
    print(asyncio.run(tracked_chat("classify", "HS code for power bank?")))
    print(dict(tracker.spent))
```

---

## 🟠 FastAPI Integration
Return usage and cost in every response (or headers) and write them to your metrics system.

```python
from fastapi import FastAPI, HTTPException, Response   # framework
from pydantic import BaseModel                         # models
from openai import AsyncOpenAI                         # client

app = FastAPI()                                        # app
client = AsyncOpenAI()                                 # shared client
PRICE_IN, PRICE_OUT = 0.15, 0.60                       # illustrative gpt-4o-mini prices


class Q(BaseModel):
    text: str                                          # question


@app.post("/ask")
async def ask(q: Q, response: Response) -> dict:
    r = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": q.text}],
        max_tokens=200,
    )
    u = r.usage                                        # token usage
    cost = u.prompt_tokens / 1e6 * PRICE_IN + u.completion_tokens / 1e6 * PRICE_OUT
    response.headers["X-LLM-Tokens"] = str(u.total_tokens)         # expose to monitoring
    response.headers["X-LLM-Cost-USD"] = f"{cost:.6f}"
    return {"answer": r.choices[0].message.content,
            "usage": {"in": u.prompt_tokens, "out": u.completion_tokens},
            "cost_usd": round(cost, 6)}
```

---

## 🔗 LangChain / LangGraph Connection
Modern LangChain exposes `usage_metadata` on every `AIMessage`. For many calls, `UsageMetadataCallbackHandler` (in `langchain_core.callbacks`) aggregates usage per model. LangSmith also records tokens and cost per run.

```python
from langchain_openai import ChatOpenAI                      # wrapper
from langchain_core.callbacks import UsageMetadataCallbackHandler   # aggregates usage

llm = ChatOpenAI(model="gpt-4o-mini")                        # model
cb = UsageMetadataCallbackHandler()                          # collects usage by model name

# llm.invoke("HS code for power bank?", config={"callbacks": [cb]})
# print(cb.usage_metadata)    # {'gpt-4o-mini-...': {'input_tokens': .., 'output_tokens': .., 'total_tokens': ..}}

# Single call:
# msg = llm.invoke("hi"); print(msg.usage_metadata)   # input_tokens, output_tokens, total_tokens
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Estimating cost from characters or word counts
✅ Correct: Use `response.usage` (exact, billed numbers).

```python
# Wrong
est_tokens = len(prompt) / 4
# Right
tokens = response.usage.total_tokens
```

❌ Mistake 2: Forgetting output tokens cost more than input tokens
✅ Correct: Calculate both sides and cap `max_tokens`.

❌ Mistake 3: Hard-coding prices forever
✅ Correct: Keep prices in config, with a date, and review them; they change.

❌ Mistake 4: Ignoring retries
✅ Correct: Failed or retried calls may still consume tokens. Count every attempt that returns usage.

---

## 🧠 Tricky Interview Question

**Q**: "Your dashboard shows 30 percent less spend than the OpenAI invoice. Where could the gap come from?"

**Answer**: Common causes: (1) streaming calls without `include_usage`, so usage was never logged; (2) calls that errored or timed out client-side but still ran on the server; (3) retries inside the SDK that your wrapper never saw; (4) embeddings, moderation, and audio calls not tracked; (5) hidden reasoning tokens on reasoning models, counted as output; (6) outdated price table; (7) other services or notebooks using the same key. Fix by reconciling with the usage API per project key and tagging each service with its own key.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Where do you find token counts for a call?
A1: In `response.usage`: `prompt_tokens`, `completion_tokens`, `total_tokens`.

Q2: [Easy] Why are output tokens priced higher?
A2: Generating each token needs a full model pass one at a time, while input tokens are processed in parallel, so output is more expensive.

Q3: [Medium] How do you count tokens before sending?
A3: With `tiktoken` (`encoding_for_model`), adding small per-message overhead. It is an estimate for planning; `usage` is the truth.

Q4: [Medium] What is prompt caching?
A4: For long repeated prompt prefixes, the provider can reuse computed work and bill cached input tokens at a discount. Put static content (system prompt, instructions) first and dynamic content last. Check `usage.prompt_tokens_details.cached_tokens`.

Q5: [Hard] Design a cost-control system for a multi-tenant AI product.
A5: Per-request logging of tokens and cost with tenant and feature tags; per-tenant quotas and soft/hard limits; `max_tokens` caps; model routing; semantic and exact-match caching; Batch API for offline work; alerts on anomaly (cost per request, tokens per request); monthly reconciliation against invoices; and kill switches per feature.

---

## 🔷 When to Use + When Not to Use
✅ Track cost always when:
- Production traffic, multiple features, multiple tenants
- You need budgets, alerts, or pricing for customers

❌ Skip heavy tracking when:
- A tiny prototype (still log `usage` in one line)

---

## 📊 Visual Diagram
```
 request ---> OpenAI ---> response.usage
                              |
              +---------------+----------------+
              | prompt_tokens: 900   x $0.15/1M |  = $0.000135
              | completion:     40   x $0.60/1M |  = $0.000024
              +---------------+----------------+
                              v
                   total = $0.000159 per call
                              |
         log (user, feature, model, tokens, cost) --> dashboard --> alerts
```

---

## 💰 Cost Impact
- Formula: `cost = in/1e6*p_in + out/1e6*p_out`. Output is often 4x the input price.
- Biggest levers, in order: model choice, prompt length, output length, call count (caching, batching), retries.
- Illustrative: cutting prompts from 900 to 400 tokens saves about 55 percent of input cost; routing 80 percent of traffic to a model 15x cheaper saves most of the bill.
- Use Batch API for non-urgent jobs (about 50 percent discount) and prompt caching for repeated prefixes.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| prompt_tokens | Input tokens billed | Input tokens जिनका bill बनता है |
| completion_tokens | Output tokens billed | Output tokens |
| usage | Token counts in response | Response में token गिनती |
| Cached tokens | Reused prefix tokens at a discount | दोबारा use हुए prefix tokens, कम price पर |
| Budget | Spend limit | खर्च की सीमा |
| Reasoning tokens | Hidden thinking tokens | छिपे हुए सोचने वाले tokens |

---

## ⚡ 3-Line Summary
English: Read `response.usage` on every call and compute cost with current per-model prices. Log it by user and feature, set budgets and alerts, and cap `max_tokens`. Include streaming, retries, and non-chat endpoints so your numbers match the invoice.
Hindi: हर call में `response.usage` पढ़ो और मौजूदा model prices से cost निकालो। User और feature के हिसाब से log करो, budgets और alerts लगाओ, `max_tokens` cap करो। Streaming, retries और non-chat endpoints भी गिनो ताकि numbers invoice से मिलें।

---

## ➡️ Next Topic
**031. OpenAI API — Error Handling** — which errors happen, which to retry, and how to respond.
