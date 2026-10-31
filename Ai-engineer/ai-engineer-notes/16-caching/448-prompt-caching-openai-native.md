---

# 448. Prompt Caching (OpenAI Native)
# हिंदी में: Prompt Caching (OpenAI Native)

---

## 🔵 Simple Definition (English)
OpenAI prompt caching is automatic. If your prompt is 1,024 tokens or longer and its beginning (prefix) matches a recent request, OpenAI reuses the processed prefix. You pay a discounted price for those cached input tokens and get lower latency. You do not add any special flag; you only structure the prompt well.

## 🔵 सरल परिभाषा (Hindi)
OpenAI का prompt caching अपने-आप होता है। अगर prompt 1,024 tokens या उससे लंबा है और उसका शुरुआती हिस्सा (prefix) किसी हाल की request से मिलता है, तो OpenAI processed prefix दोबारा इस्तेमाल करता है। उन cached input tokens पर discount मिलता है और latency कम होती है। कोई special flag नहीं लगाना; बस prompt की बनावट सही रखनी है।

---

## 🔴 Problem it Solves
- Long system prompts, tool schemas and few-shot examples are resent on every call and charged at full input price.
- Developers needed a no-code way to cut that cost without building their own cache layer.
- Unlike response caching, the model still answers the new question freshly.

## 🔴 यह क्यों बना? (Hindi)
- लंबे system prompts, tool schemas और few-shot examples हर call में दोबारा भेजे और पूरे input price पर charge होते हैं।
- Developers को बिना अपना cache layer बनाए यह खर्च कम करने का no-code तरीका चाहिए था।
- Response caching से अलग, model नए सवाल का जवाब फिर भी ताज़ा बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You send a request with prompt >= 1024 tokens
Step 2 → OpenAI routes it to a machine and checks if the prompt prefix was recently processed
         (matching happens in chunks after the first 1024 tokens, in 128-token steps)
Step 3 → Match found → cached prefix tokens are reused (cache HIT)
Step 4 → No match → full processing, prefix is stored for later (MISS)
Step 5 → Response usage shows prompt_tokens_details.cached_tokens
Step 6 → Cached entries live for a short time (minutes of inactivity; always cleared within about an hour; some models offer longer retention)
Step 7 → Optional prompt_cache_key helps route similar requests to the same cache
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → आप >= 1024 tokens वाले prompt के साथ request भेजते हो
Step 2 → OpenAI देखता है कि prompt का prefix हाल में process हुआ है या नहीं
         (पहले 1024 tokens के बाद 128-token के steps में match होता है)
Step 3 → Match मिला → cached prefix tokens दोबारा इस्तेमाल (cache HIT)
Step 4 → Match नहीं → पूरा processing, prefix आगे के लिए store (MISS)
Step 5 → Response के usage में prompt_tokens_details.cached_tokens दिखता है
Step 6 → Cache entries थोड़ी देर रहती हैं (निष्क्रियता के कुछ मिनट; लगभग एक घंटे में हट जाती हैं; कुछ models में लंबी retention)
Step 7 → वैकल्पिक prompt_cache_key से मिलते-जुलते requests एक ही cache तक पहुँचते हैं
```
(Discount size and retention differ by model and change over time; verify on the current OpenAI pricing page.)

---

## 🟡 Real World Example
**Tariff Classification System**: A 3,000-token system prompt (rules + 20 few-shot HS examples) comes first; the product text goes last. After the first request, every other request in the next few minutes gets the first 3,000 tokens as cached tokens at a discount.
**Zomato AI**: The restaurant-assistant instructions and menu schema (2,000 tokens) sit at the start; the customer message is at the end, so most traffic hits cache.

## 🟡 Real Example Hindi mein
**Tariff System**: 3,000-token system prompt (rules + 20 few-shot HS examples) सबसे पहले, product text सबसे आख़िर में। पहली request के बाद अगले कुछ मिनट की हर request के पहले 3,000 tokens discount पर cached tokens बनते हैं।
**Zomato AI**: Restaurant-assistant के निर्देश और menu schema (2,000 tokens) शुरू में, customer message आख़िर में, इसलिए ज़्यादातर traffic cache hit करता है।

---

## 💻 Code Example — Basic
```python
# Basic: simulate how OpenAI decides the cacheable part of a prompt (offline, pure Python).
# Real OpenAI does this on the server; here we only compute the shared prefix of two prompts.
def rough_tokens(text: str) -> int:
    return max(1, len(text) // 4)  # rough rule: 1 token ~ 4 characters


def shared_prefix_len(a: str, b: str) -> int:
    n = 0  # count equal characters from the start
    for x, y in zip(a, b):  # walk both strings together
        if x != y:  # first difference ends the prefix
            break
        n += 1
    return n


SYSTEM = "You are a tariff expert. Rules: ... " * 150  # long static part (> 1024 tokens)

good_1 = SYSTEM + "Product: steel bottle"  # static first, dynamic last
good_2 = SYSTEM + "Product: copper wire"
bad_1 = "Time 10:01 " + SYSTEM + "Product: steel bottle"  # dynamic first
bad_2 = "Time 10:02 " + SYSTEM + "Product: copper wire"

for name, a, b in [("good", good_1, good_2), ("bad", bad_1, bad_2)]:
    p = rough_tokens(a[: shared_prefix_len(a, b)])  # tokens in shared prefix
    print(f"{name}: shared prefix ~ {p} tokens, cacheable = {p >= 1024}")  # eligibility check
```

## 💻 Code Example — Advanced
```python
# Production: async openai>=1.x, read cached_tokens, compute real cost, handle errors.
# pip install openai
from __future__ import annotations

import logging  # logging
from dataclasses import dataclass

from openai import APIError, AsyncOpenAI, RateLimitError  # SDK classes

log = logging.getLogger("openai_cache")  # logger

PRICE_IN = 0.15  # USD per 1M input tokens (gpt-4o-mini example; check current price)
PRICE_CACHED = 0.075  # cached input price (50 percent discount for this example model)
PRICE_OUT = 0.60  # USD per 1M output tokens

STATIC_SYSTEM = open("tariff_rules.txt", encoding="utf-8").read()  # stable prefix, >1024 tokens


@dataclass
class Result:
    answer: str
    prompt_tokens: int
    cached_tokens: int
    cost_usd: float


async def classify(client: AsyncOpenAI, product: str, tenant_key: str = "tariff-v1") -> Result:
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": STATIC_SYSTEM},  # static FIRST
                {"role": "user", "content": f"Product: {product}"},  # dynamic LAST
            ],
            temperature=0,
            max_tokens=200,
            extra_body={"prompt_cache_key": tenant_key},  # routing hint; same key for same prefix
        )
    except RateLimitError:  # 429
        log.warning("rate limit")
        raise
    except APIError as exc:  # other API failures
        log.error("api error: %s", exc)
        raise
    u = resp.usage  # usage block
    details = getattr(u, "prompt_tokens_details", None)  # may be None on old SDK/models
    cached = (details.cached_tokens if details else 0) or 0  # cached portion
    fresh = u.prompt_tokens - cached  # uncached portion
    cost = (fresh * PRICE_IN + cached * PRICE_CACHED + u.completion_tokens * PRICE_OUT) / 1_000_000
    return Result(resp.choices[0].message.content or "", u.prompt_tokens, cached, cost)
```
(`prompt_cache_key` is passed via `extra_body` so it works even on SDK versions without a typed parameter.)

---

## 🟠 FastAPI Integration
```python
from contextlib import asynccontextmanager  # lifespan
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # schema

client: AsyncOpenAI | None = None  # shared client


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    client = AsyncOpenAI()  # create once
    yield
    await client.close()  # close connections


app = FastAPI(lifespan=lifespan)


class In(BaseModel):
    product: str


@app.post("/classify")
async def classify_route(body: In) -> dict:
    r = await classify(client, body.product)  # call helper above
    return {
        "answer": r.answer,
        "cached_tokens": r.cached_tokens,  # visible to dashboards
        "cache_ratio": round(r.cached_tokens / max(1, r.prompt_tokens), 2),
        "cost_usd": round(r.cost_usd, 8),
    }
```

---

## 🔗 LangChain / LangGraph Connection
Nothing special is needed: `ChatOpenAI` sends the messages as they are, so OpenAI's automatic caching applies. LangChain exposes the numbers in `usage_metadata["input_token_details"]["cache_read"]`.

```python
from langchain_openai import ChatOpenAI  # chat model
from langchain_core.messages import HumanMessage, SystemMessage  # messages

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # model
msg = llm.invoke([SystemMessage(content=STATIC_SYSTEM), HumanMessage(content="steel bottle")])  # static first
print(msg.usage_metadata)  # includes input_token_details with cache_read when hit
```
In LangGraph keep the system prompt and tool list identical across nodes and put per-run state at the end.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Dynamic data at the start of the prompt
✅ Correct: Static first, dynamic last. One changed character early breaks the prefix match.

```python
# Wrong
messages = [{"role": "system", "content": f"User {uid} at {now}. " + RULES}]
# Right
messages = [{"role": "system", "content": RULES}, {"role": "user", "content": f"User {uid} at {now}. {q}"}]
```

❌ Mistake 2: Reordering tools or JSON schema keys between calls
✅ Correct: Build tools/schemas once and reuse the same object; tools are part of the prefix.

```python
# Wrong: tools=list(set(tools)) -> random order
# Right: tools=TOOLS  (module-level constant, fixed order)
```

---

## 🧠 Tricky Interview Question
**Q**: "A teammate says OpenAI prompt caching will make your answers cheaper AND identical. Correct?"

**Answer**: Only cheaper, not identical. Prompt caching reuses the processed input; generation still happens, so with temperature above 0 answers still vary. It is also not guaranteed: it is best effort, depends on prefix match, traffic and timing, and the first request after idle is always a miss. For identical answers you need a response cache (topic 444).

---

## ⚫ Interview Questions + Answers

Q1: Do I need to change code to use OpenAI prompt caching? (Easy)
A1: No, it is automatic for supported models when the prompt is at least 1,024 tokens. You just structure the prompt so the static part is first.

Q2: How can I see cache usage? (Easy)
A2: `response.usage.prompt_tokens_details.cached_tokens`.

Q3: What breaks the cache? (Medium)
A3: Any change in the prefix: different system text, reordered tools, timestamps or user data early in the prompt, different images, or a different model. Also idle time beyond retention.

Q4: Compare OpenAI and Anthropic prompt caching. (Medium)
A4: OpenAI: automatic, no write surcharge, discount on reads, 1,024-token minimum. Anthropic: explicit `cache_control` breakpoints, write premium, steeper read discount, configurable TTL (5 minutes or 1 hour). Anthropic gives you more control; OpenAI is simpler.

Q5: You see low cached_tokens despite a long identical system prompt. Debug it. (Hard)
A5: Check (1) prompt is above 1,024 tokens, (2) the first message is truly byte-identical (log a hash), (3) tools and response_format are identical and ordered, (4) traffic spacing versus retention, (5) many servers: use `prompt_cache_key` to improve routing, (6) rate of requests per key is not so high that it overflows one machine, (7) the model supports caching. Then compare cached_tokens before and after fixes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Prompt has a long static prefix (rules, examples, tools)
- Many requests arrive within minutes of each other
- You want savings with zero extra infrastructure

❌ Avoid when (do not rely on it alone):
- Prompts are under 1,024 tokens
- You need guaranteed identical outputs
- Traffic is rare, so the cache expires between calls

---

## 📊 Visual Diagram
```
 Prompt = [ static system + tools + examples ][ dynamic user text ]
            └──── same prefix, >=1024 tokens ───┘
 Request 1: all tokens processed, prefix stored
 Request 2: prefix tokens -> cached_tokens (discount), rest normal
 usage.prompt_tokens_details.cached_tokens = prefix size (in 128-token steps)
```

---

## 💰 Cost Impact
**Token usage**: Example gpt-4o-mini, 3,000-token prefix + 100 dynamic tokens. Uncached input: 3,100 x $0.15/1M = $0.000465. With the prefix cached at half price: 3,000 x $0.075/1M + 100 x $0.15/1M = $0.00024, about 48 percent less on input. Models with a larger discount save more.
**Optimisation**: static first, fixed tool order, `prompt_cache_key`, keep traffic steady, track the ratio cached_tokens / prompt_tokens.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Prompt cache | Reused processed prefix | दोबारा इस्तेमाल हुआ prefix |
| cached_tokens | Input tokens served from cache | cache से आए input tokens |
| Prefix match | Same start of prompt | prompt की एक जैसी शुरुआत |
| prompt_cache_key | Hint to improve cache routing | cache routing का hint |
| Automatic caching | No code flag needed | बिना flag के अपने-आप |
| Retention | How long cache stays | cache कितनी देर रहता है |

---

## ⚡ 3-Line Summary
English: OpenAI caches long prompt prefixes automatically (1,024 tokens or more) and discounts the cached input tokens. Put static content first and dynamic content last, and keep tools stable. Watch cached_tokens in usage to measure savings.
Hindi: OpenAI लंबे prompt prefix (1,024 tokens या ज़्यादा) अपने-आप cache करता है और cached input tokens पर discount देता है। स्थिर content पहले, बदलने वाला आख़िर में रखो और tools का क्रम न बदलो। बचत नापने के लिए usage में cached_tokens देखो।

---

## ➡️ Next Topic
**449. Cache Invalidation Strategy** — how to remove or refresh cached answers when data, prompts or models change.
