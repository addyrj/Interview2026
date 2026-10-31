---

# 044. Cost Optimization — Models
# हिंदी में: Models की Cost Optimization

---

## 🔵 Simple Definition (English)
Cost optimization means getting the same quality from an LLM while spending fewer tokens and using cheaper calls. The main levers are: smaller models, shorter prompts, capped outputs, caching, batching and routing. LLM cost = input tokens x input price + output tokens x output price.

## 🔵 सरल परिभाषा (Hindi)
Cost optimization यानी LLM से वही quality लेना लेकिन कम tokens और सस्ते calls के साथ। मुख्य तरीके: छोटे models, छोटे prompts, output cap, caching, batching और routing। LLM cost = input tokens x input price + output tokens x output price।

---

## 🔴 Problem it Solves
- A demo that costs $5 can cost $50,000 a month at production traffic.
- Long system prompts are re-sent on every call and billed every time.
- Output tokens are usually 3-5x more expensive than input tokens, and verbose answers waste them.
- Identical questions are paid for again and again.

## 🔴 यह क्यों बना? (Hindi)
- Demo में $5 वाला काम production traffic पर महीने में $50,000 हो सकता है।
- लंबा system prompt हर call में दोबारा भेजा जाता है और हर बार bill होता है।
- Output tokens आमतौर पर input से 3-5x महँगे होते हैं; लंबे जवाब पैसा बर्बाद करते हैं।
- एक ही सवाल बार-बार पूछा जाए तो हर बार पैसा लगता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Measure first: log input/output tokens and cost per request and per feature
Step 2 → Find the top spenders (usually 1-2 endpoints are 80% of the bill)
Step 3 → Trim prompts: remove filler, cut unused few-shot examples
Step 4 → Cap output: max_tokens, "answer in under 50 words", structured JSON
Step 5 → Cache: exact-match cache, then semantic cache for similar questions
Step 6 → Route: small model for easy requests, large model only when needed
Step 7 → Batch: use Batch API for non-urgent jobs (about 50% cheaper)
Step 8 → Use provider prompt caching for long repeated prefixes
Step 9 → Set budgets and alerts; re-measure after each change
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → पहले measure करो: हर request/feature का input/output tokens और cost log करो
Step 2 → सबसे ज़्यादा खर्च वाले endpoints ढूँढो (अक्सर 1-2 endpoints = 80% bill)
Step 3 → Prompt छोटा करो: फालतू शब्द और unused examples हटाओ
Step 4 → Output cap करो: max_tokens, "50 words में जवाब दो", structured JSON
Step 5 → Cache करो: exact-match cache, फिर similar सवालों के लिए semantic cache
Step 6 → Route करो: आसान request -> small model, कठिन -> large model
Step 7 → Batch करो: जल्दी नहीं चाहिए तो Batch API (लगभग 50% सस्ता)
Step 8 → लंबे repeated prefix के लिए provider का prompt caching
Step 9 → Budget और alerts लगाओ; हर बदलाव के बाद दोबारा measure करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: 200,000 classifications a day. The first version sent a 2,500-token system prompt (rules for all 97 HS chapters) with every call to a large model. Fixes: (1) a cache for repeated product descriptions removed 35% of calls, (2) the system prompt was cut to 600 tokens plus retrieved chapter notes, (3) 85% of items went to a small model, (4) overnight bulk files went through the Batch API. The bill dropped by roughly 85% with accuracy within 1 point.

**Amazon-style**: Product-title cleaning for millions of listings runs offline in batch with a small model, because nobody waits for it.

## 🟡 Real Example Hindi mein
**Tariff System**: रोज़ 200,000 classifications। पहले version में हर call में 2,500 tokens का system prompt (सभी 97 HS chapters के rules) बड़े model को जाता था। सुधार: (1) repeated product descriptions के लिए cache से 35% calls खत्म, (2) system prompt 600 tokens + retrieved chapter notes तक घटाया, (3) 85% items small model को, (4) रात की bulk files Batch API से। Bill लगभग 85% घटा और accuracy सिर्फ़ 1 point कम हुई।

**Amazon-style**: लाखों listings के product title cleaning का काम offline batch में small model से होता है, क्योंकि कोई इंतज़ार नहीं कर रहा।

---

## 💻 Code Example — Basic
```python
# Basic: estimate cost and see the effect of optimisations (pure Python, runs offline)

PRICE_IN = 2.50 / 1_000_000   # USD per input token (illustrative large model)
PRICE_OUT = 10.00 / 1_000_000  # USD per output token (illustrative large model)
SMALL_IN = 0.15 / 1_000_000  # small model input price (illustrative)
SMALL_OUT = 0.60 / 1_000_000  # small model output price (illustrative)

def cost(tokens_in: int, tokens_out: int, small: bool = False) -> float:
    # Pick the right price pair
    p_in, p_out = (SMALL_IN, SMALL_OUT) if small else (PRICE_IN, PRICE_OUT)
    return tokens_in * p_in + tokens_out * p_out  # total USD for one call

requests = 200_000  # requests per day

# Baseline: big model, long prompt, long answer
base = cost(3000, 400) * requests  # 3000 in, 400 out
print(f"Baseline per day: ${base:,.2f}")  # show baseline

# Step A: shorter prompt + capped output
a = cost(1000, 100) * requests  # 1000 in, 100 out
print(f"Trim prompt/output: ${a:,.2f}")  # show saving

# Step B: 35% cache hits (cost nothing)
b = a * 0.65  # only 65% reach the model
print(f"With cache: ${b:,.2f}")  # show saving

# Step C: 85% of remaining traffic to the small model
c = b * 0.15 + (cost(1000, 100, small=True) * requests * 0.65 * 0.85)  # mixed
print(f"With routing: ${c:,.2f}")  # final cost
print(f"Total saving: {100 * (1 - c / base):.1f}%")  # percentage saved
```

## 💻 Code Example — Advanced
```python
# Production-style: cached, budget-aware, async LLM wrapper with usage tracking
import asyncio  # async primitives
import hashlib  # stable cache keys
import json  # serialise keys
from dataclasses import dataclass, field  # structured state
from openai import AsyncOpenAI, APIError, RateLimitError  # openai>=1

client = AsyncOpenAI()  # reads OPENAI_API_KEY

PRICES: dict[str, tuple[float, float]] = {  # illustrative USD per 1M tokens
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
}

@dataclass
class Usage:
    spent_usd: float = 0.0  # running total
    calls: int = 0  # real API calls
    cache_hits: int = 0  # saved calls
    cache: dict[str, str] = field(default_factory=dict)  # in-memory cache

class BudgetExceeded(RuntimeError):
    """Raised when daily budget is used up."""

class CostAwareLLM:
    def __init__(self, daily_budget_usd: float = 50.0) -> None:
        self.usage = Usage()  # state
        self.budget = daily_budget_usd  # hard limit

    @staticmethod
    def _key(model: str, prompt: str) -> str:
        raw = json.dumps([model, prompt]).encode()  # deterministic bytes
        return hashlib.sha256(raw).hexdigest()  # short stable key

    def _price(self, model: str, tin: int, tout: int) -> float:
        p_in, p_out = PRICES[model]  # per-1M prices
        return (tin * p_in + tout * p_out) / 1_000_000  # USD

    async def ask(self, prompt: str, model: str = "gpt-4o-mini",
                  max_tokens: int = 150) -> str:
        key = self._key(model, prompt)  # cache key
        if key in self.usage.cache:  # exact-match hit
            self.usage.cache_hits += 1
            return self.usage.cache[key]
        if self.usage.spent_usd >= self.budget:  # budget guard
            raise BudgetExceeded(f"Spent ${self.usage.spent_usd:.2f}")
        for attempt in range(3):  # simple retry loop
            try:
                resp = await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,  # cap output cost
                    temperature=0,  # deterministic -> cache friendly
                )
                break
            except RateLimitError:  # back off and retry
                await asyncio.sleep(2 ** attempt)
            except APIError:  # other API errors: give up
                raise
        else:
            raise RuntimeError("Rate limited after 3 attempts")
        text = resp.choices[0].message.content or ""  # answer text
        self.usage.spent_usd += self._price(
            model, resp.usage.prompt_tokens, resp.usage.completion_tokens)
        self.usage.calls += 1  # count the real call
        self.usage.cache[key] = text  # store for next time
        return text

# llm = CostAwareLLM(daily_budget_usd=20)
# print(asyncio.run(llm.ask("HS code for cotton shirt?")))
```

---

## 🟠 FastAPI Integration
Add a cost endpoint and a middleware-like dependency that tracks spending per request, so finance and engineers can see cost live.

```python
from fastapi import FastAPI, Depends, HTTPException  # framework
from pydantic import BaseModel  # request models

app = FastAPI()  # app
llm = CostAwareLLM(daily_budget_usd=20)  # shared wrapper from advanced example

class Q(BaseModel):
    question: str  # user question

def get_llm() -> CostAwareLLM:
    return llm  # dependency so tests can override it

@app.post("/ask")
async def ask(q: Q, svc: CostAwareLLM = Depends(get_llm)) -> dict:
    try:
        answer = await svc.ask(q.question)  # cached + budgeted call
    except BudgetExceeded:  # budget exhausted -> 429
        raise HTTPException(status_code=429, detail="Daily AI budget used")
    return {"answer": answer}

@app.get("/usage")
async def usage(svc: CostAwareLLM = Depends(get_llm)) -> dict:
    u = svc.usage  # read state
    return {"spent_usd": round(u.spent_usd, 4), "calls": u.calls,
            "cache_hits": u.cache_hits}  # live cost dashboard data
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has a built-in LLM cache (`set_llm_cache`) and token usage metadata on every `AIMessage` (`usage_metadata`). LangGraph state can carry a running cost and a conditional edge can switch to a cheaper path when budget is low.

```python
from langchain_core.globals import set_llm_cache  # global cache setter
from langchain_core.caches import InMemoryCache  # simple cache backend
from langchain_openai import ChatOpenAI  # OpenAI chat model

set_llm_cache(InMemoryCache())  # identical prompts are now free
llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=150, temperature=0)  # capped

msg = llm.invoke("HS code for cotton shirt?")  # first call hits API
print(msg.usage_metadata)  # {'input_tokens':..., 'output_tokens':..., 'total_tokens':...}
msg2 = llm.invoke("HS code for cotton shirt?")  # served from cache, no cost
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No `max_tokens` and chatty prompts
✅ Correct: Cap output and ask for brief or structured answers.

```python
# Wrong: model writes 600 words when 20 are enough
# await client.chat.completions.create(model=m, messages=msgs)
# Right:
# await client.chat.completions.create(model=m, messages=msgs, max_tokens=80)
```

❌ Mistake 2: Optimising without measuring
✅ Correct: Log tokens and cost per feature first; fix the biggest line item.

```python
# Wrong: spend a week shortening a prompt used 100 times a day
# Right: log usage -> sort by cost -> optimise the top endpoint
```

---

## 🧠 Tricky Interview Question
**Q**: "You cut the prompt by 50% and the bill only fell by 10%. Why?"

**Answer**: Output tokens are priced higher than input tokens, and the output may dominate the bill. Also, retries, long conversation history, tool results or retrieved chunks may be the real input cost, not the system prompt. Measure input vs output tokens by endpoint, then cap outputs, trim history, and cache.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] How is LLM API cost calculated?
A1: (input tokens x input price) + (output tokens x output price), usually per 1M tokens. Output is typically more expensive.

Q2: [Easy] Name three quick ways to reduce cost.
A2: Use a smaller model, shorten the prompt and cap `max_tokens`, and cache repeated requests.

Q3: [Medium] Exact cache vs semantic cache?
A3: Exact cache matches identical text via a hash: safe and simple. Semantic cache embeds the query and returns a stored answer for similar queries: higher hit rate but risk of wrong matches, so use a high similarity threshold and avoid it for high-stakes answers.

Q4: [Medium] When is the Batch API a good idea?
A4: For work that can wait up to a day (bulk classification, evals, embeddings): the provider gives a discount (about 50% for OpenAI) in exchange for async completion.

Q5: [Hard] Design cost controls for a multi-tenant AI product.
A5: Per-tenant token quotas and rate limits, per-feature cost logging, budgets with hard stops and alerts, model routing by plan tier, caching, prompt caching for shared prefixes, and a weekly review of cost per successful task (not just total spend). Keep cost metadata on every request for chargeback.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Traffic is growing or the bill is a visible line item
- Prompts are long or repeated
- Many requests are near-duplicates

❌ Avoid when:
- Optimisation hurts quality on safety or legal tasks
- Volume is tiny and engineer time costs more than the savings

---

## 📊 Visual Diagram
```
Request
  |
  v
[Exact cache] --hit--> answer (cost $0)
  | miss
  v
[Router] -- easy --> small model --+
  |                                |
  +-- hard --> large model --------+--> answer
                                   |
                    [Log tokens + cost] -> budget check -> alert
```

---

## 💰 Cost Impact
- Token usage: cost is linear in tokens, so every removed token saves money on every call.
- Typical savings (illustrative): prompt trimming 20-50%, caching 20-40%, routing 50-80%, Batch API 50% on eligible jobs, provider prompt caching up to 50-90% on cached prefix tokens (varies by provider).
- Example: 200,000 calls/day at 3,000 in + 400 out on a large model is about $2,300/day. After trimming, caching and routing it can fall below $300/day (see Basic example output when run).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Input tokens | Tokens you send | जो tokens आप भेजते हैं |
| Output tokens | Tokens model returns | Model के जवाब के tokens |
| max_tokens | Output length cap | Output की सीमा |
| Semantic cache | Cache by meaning | अर्थ के आधार पर cache |
| Batch API | Discounted async API | सस्ता async API |
| Prompt caching | Provider reuses repeated prefix | Repeated prefix पर छूट |

---

## ⚡ 3-Line Summary
English: Measure tokens and cost per feature first. Then trim prompts, cap outputs, cache, route and batch. Always re-check quality after every saving.
Hindi: पहले हर feature का token और cost measure करो। फिर prompt छोटा करो, output cap करो, cache, routing और batching लगाओ। हर बचत के बाद quality दोबारा जाँचो।

---

## ➡️ Next Topic
**045. Latency Optimization — Models** — cost is one side; speed is the other. Streaming, smaller models, parallel calls and time-to-first-token.
