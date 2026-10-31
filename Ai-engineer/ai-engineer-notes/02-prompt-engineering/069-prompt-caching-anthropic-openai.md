---

# 069. Prompt Caching (Anthropic + OpenAI)
# हिंदी में: Prompt Caching — दोहराए जाने वाले prefix पर कम पैसा

---

## 🔵 Simple Definition (English)
Prompt caching lets the provider reuse the already-processed beginning (prefix) of a prompt across requests. If many requests start with the same long system prompt or documents, cache hits are cheaper and faster. OpenAI does it automatically for long prompts; Anthropic needs explicit `cache_control` markers.

## 🔵 सरल परिभाषा (Hindi)
Prompt caching में provider prompt के शुरुआती हिस्से (prefix) की पहले हो चुकी processing को अलग-अलग requests में दोबारा इस्तेमाल करता है। कई requests एक ही लंबे system prompt या documents से शुरू हों तो cache hit सस्ता और तेज़ होता है। OpenAI लंबे prompts के लिए यह अपने आप करता है; Anthropic में `cache_control` markers लगाने पड़ते हैं।

---

## 🔴 Problem it Solves
A tariff assistant sends the same 6,000-token rule book with every question. Without caching you pay full price for those 6,000 tokens and wait for the model to process them each time.

Caching stores the processed prefix for a short time (minutes). Later requests with an identical prefix read it at a discount and lower latency.

## 🔴 यह क्यों बना? (Hindi)
Tariff assistant हर सवाल के साथ वही 6,000-token rule book भेजता है। Caching के बिना हर बार उन 6,000 tokens का पूरा पैसा और processing का इंतज़ार। Caching processed prefix को कुछ मिनट रखता है। बाद की requests में identical prefix discount और कम latency पर मिलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Put STATIC content first (system rules, tools, big documents)
Step 2 → Put DYNAMIC content last (user question, timestamps, IDs)
Step 3 → Anthropic: mark the end of the static part with cache_control {"type": "ephemeral"}
         OpenAI: nothing to mark; prompts >= 1,024 tokens are cached automatically
Step 4 → First request: cache WRITE (Anthropic charges extra for writes)
Step 5 → Next requests inside the TTL (about 5 min, refreshed on use) with the SAME prefix: cache READ (cheaper)
Step 6 → Read usage fields to confirm hits
Step 7 → Any change in the prefix (even one character) = cache miss
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → STATIC content पहले रखो (system rules, tools, बड़े documents)
Step 2 → DYNAMIC content आख़िर में (user question, timestamps, IDs)
Step 3 → Anthropic: static हिस्से के अंत पर cache_control {"type": "ephemeral"} लगाओ
         OpenAI: कुछ लगाना नहीं; >= 1,024 tokens के prompts अपने आप cache होते हैं
Step 4 → पहली request: cache WRITE (Anthropic में write पर extra charge)
Step 5 → TTL (लगभग 5 मिनट, use पर refresh) में SAME prefix वाली requests: cache READ (सस्ता)
Step 6 → Usage fields देखकर hit confirm करो
Step 7 → Prefix में एक character भी बदला = cache miss
```

---

## 🟡 Real World Example
**Tariff Classification System**: The system prompt contains the classification rules and 40 worked examples (about 6,000 tokens). All 100K daily requests share it. With caching, only the user's product description (about 50 tokens) is new input at full price. Cached reads on Anthropic are billed at a small fraction of base input price (verify current numbers in the pricing page); OpenAI gives a discount on cached input tokens too.

**Zomato-style**: A support bot with a long policy handbook as a cached prefix.

## 🟡 Real Example Hindi mein
**Tariff System**: System prompt में classification rules और 40 worked examples हैं (लगभग 6,000 tokens)। रोज़ की 1 लाख requests सब इसे share करती हैं। Caching से सिर्फ user का product description (लगभग 50 tokens) पूरे दाम पर नया input है। Anthropic में cached reads base input price के छोटे हिस्से पर बिल होते हैं (current numbers pricing page पर देखें); OpenAI भी cached input tokens पर discount देता है।

**Zomato-style**: लंबी policy handbook को cached prefix बनाकर support bot।

---

## 💻 Code Example — Basic
```python
# Basic: build request payloads for both providers (pure Python, no network)
import json  # to print the payloads

RULES = "TARIFF RULES: " + ("Rule text. " * 600)       # pretend this is a long static prefix

def anthropic_payload(question: str) -> dict:
    return {
        "model": "claude-sonnet-4-5",                    # example model id; use a current one
        "max_tokens": 300,                               # cap output
        "system": [                                      # system can be a list of blocks
            {"type": "text", "text": RULES,
             "cache_control": {"type": "ephemeral"}},    # cache everything up to here
        ],
        "messages": [{"role": "user", "content": question}],   # dynamic part last
    }

def openai_payload(question: str) -> dict:
    return {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": RULES},        # static first = cacheable automatically
            {"role": "user", "content": question},       # dynamic last
        ],
    }

print(json.dumps(anthropic_payload("earbuds?"))[:120])   # show the start of the payload
print(len(openai_payload("earbuds?")["messages"]))       # 2 messages
```

## 💻 Code Example — Advanced
```python
# Production: Anthropic caching with usage tracking + OpenAI cached-token reading (async)
from __future__ import annotations

import asyncio                                    # async runner
from dataclasses import dataclass                 # stats container

from anthropic import AsyncAnthropic              # pip install anthropic
from openai import AsyncOpenAI                    # pip install openai>=1

@dataclass
class CacheStats:
    reads: int = 0                                # tokens read from cache
    writes: int = 0                               # tokens written to cache
    uncached: int = 0                             # normal input tokens

async def ask_anthropic(client: AsyncAnthropic, rules: str, question: str, stats: CacheStats) -> str:
    try:
        resp = await client.messages.create(
            model="claude-sonnet-4-5", max_tokens=300,           # example model id
            system=[{"type": "text", "text": rules,
                     "cache_control": {"type": "ephemeral"}}],   # cache breakpoint
            messages=[{"role": "user", "content": question}],
        )
    except Exception as exc:                                     # network / rate limit / auth
        raise RuntimeError(f"anthropic call failed: {exc}") from exc
    u = resp.usage                                               # usage object
    stats.reads += getattr(u, "cache_read_input_tokens", 0) or 0           # cache hits
    stats.writes += getattr(u, "cache_creation_input_tokens", 0) or 0      # cache writes
    stats.uncached += u.input_tokens                                       # tokens after the breakpoint
    return resp.content[0].text if resp.content else ""

async def ask_openai(client: AsyncOpenAI, rules: str, question: str) -> tuple[str, int]:
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini", temperature=0, max_tokens=300,
            messages=[{"role": "system", "content": rules},
                      {"role": "user", "content": question}],
        )
    except Exception as exc:
        raise RuntimeError(f"openai call failed: {exc}") from exc
    details = getattr(resp.usage, "prompt_tokens_details", None)   # may be None
    cached = getattr(details, "cached_tokens", 0) or 0             # cached input tokens
    return resp.choices[0].message.content or "", cached

async def main() -> None:
    rules = "TARIFF RULES: " + ("Rule text. " * 1500)              # long static prefix
    stats = CacheStats()
    a = AsyncAnthropic()                                           # needs ANTHROPIC_API_KEY
    for q in ("earbuds?", "usb cable?"):                           # 2nd call should read the cache
        print(await ask_anthropic(a, rules, q, stats))
    print(stats)

# asyncio.run(main())   # needs real API keys, so it is not run here
```
Token usage: Anthropic has a minimum cacheable size (about 1,024 tokens for most models; check docs), cache writes cost more than normal input, reads cost much less. OpenAI caching starts at 1,024 tokens and has no write surcharge.

---

## 🟠 FastAPI Integration
Create the client once at startup, keep the static prefix in a module constant (byte-identical on every call), and expose cache stats on a metrics endpoint.

```python
from fastapi import FastAPI                       # framework
from pydantic import BaseModel                    # models
from anthropic import AsyncAnthropic              # anthropic client

app = FastAPI()                                   # app
client = AsyncAnthropic()                         # one shared client
stats = CacheStats()                              # from the advanced block
RULES = "TARIFF RULES: " + ("Rule text. " * 1500) # constant prefix, never changes per request

class Q(BaseModel):
    question: str                                 # dynamic part

@app.post("/ask")
async def ask(q: Q) -> dict[str, str]:
    answer = await ask_anthropic(client, RULES, q.question, stats)   # cached prefix
    return {"answer": answer}

@app.get("/metrics/cache")
async def cache_metrics() -> dict[str, int]:
    return {"reads": stats.reads, "writes": stats.writes, "uncached": stats.uncached}
```

---

## 🔗 LangChain / LangGraph Connection
With `ChatAnthropic` you can pass content blocks that include `cache_control`; with `ChatOpenAI` caching is automatic when the prefix is stable. In LangGraph keep the static system message identical across nodes that share a prefix, and put per-run data at the end.

```python
from langchain_anthropic import ChatAnthropic                  # pip install langchain-anthropic
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatAnthropic(model="claude-sonnet-4-5", max_tokens=300)  # example model id
messages = [
    SystemMessage(content=[{"type": "text", "text": RULES,
                            "cache_control": {"type": "ephemeral"}}]),   # cached block
    HumanMessage(content="HS code for earbuds?"),                        # dynamic
]
# reply = await llm.ainvoke(messages)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Putting dynamic data at the start (breaks the prefix)
✅ Correct: Static first, dynamic last.
```python
# Wrong: timestamp at the top changes every request -> cache miss
system = f"Now: {now()}\n{RULES}"

# Right
system = RULES
user = f"Now: {now()}\n{question}"
```

❌ Mistake 2: Assuming cache hits without checking
✅ Correct: Read usage fields.
```python
# Wrong: just trust it
# Right
print(resp.usage.cache_read_input_tokens)   # Anthropic
print(resp.usage.prompt_tokens_details.cached_tokens)   # OpenAI
```

❌ Mistake 3: Caching a prompt that is used once or rarely (Anthropic write cost is higher than normal input). Cache only prefixes reused within the TTL.

---

## 🧠 Tricky Interview Question
**Q**: "You enabled caching but the hit rate is 0%. The prefix 'looks identical'. What do you check?"

**Answer**: (1) Hidden changes: timestamps, request ids, random ordering of examples or tools, dict key order, whitespace. (2) Prefix shorter than the minimum cacheable length. (3) Requests spread over time longer than the TTL. (4) Different model, tools, or parameters between calls (these are part of the cached prefix on some providers). (5) Cache breakpoint placed before the big static part. Fix by canonicalising the prefix, logging a hash of it, and checking usage fields.

---

## ⚫ Interview Questions + Answers

Q1: What is prompt caching?
A1: Reusing the processed prefix of a prompt across requests to cut cost and latency.

Q2: What goes first in a cacheable prompt?
A2: Static content: system rules, tool definitions, large documents, few-shot examples. Dynamic content (user question) goes last.

Q3: How does Anthropic caching differ from OpenAI's?
A3: Anthropic uses explicit `cache_control` breakpoints, charges extra for cache writes and discounts reads. OpenAI caches automatically for prompts of 1,024+ tokens and discounts cached input tokens, with no explicit marker. Always check current docs for exact limits and prices.

Q4: How long does a cache live?
A4: Short: Anthropic's default is about 5 minutes (refreshed on each hit, longer options exist). OpenAI keeps entries for minutes of inactivity. So it suits steady traffic, not rare calls.

Q5 (Hard): Compute whether caching pays off for an Anthropic prefix of 6,000 tokens with 1 request per 10 minutes.
A5: With a 5-minute TTL each request would be a cache write (more expensive than normal input) and never a read, so caching loses money. Options: use the longer TTL if offered, batch requests so several arrive within the TTL, or skip caching. Break-even needs roughly 2 or more reads per write, depending on the write premium and read discount (check current pricing).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Large static prefix (rules, docs, few-shot examples, tools)
- Steady traffic (many requests within minutes)
- Multi-turn chats where history grows

❌ Avoid when:
- Prompts are short (under the minimum)
- Prefix changes every request
- Traffic is rare (cache expires before reuse)

---

## 📊 Visual Diagram
```
 Request 1                          Request 2 (within TTL)
 +-------------------------+        +-------------------------+
 | STATIC prefix (6,000)   |        | STATIC prefix (6,000)   |
 |  -> cache WRITE         |        |  -> cache READ (cheap)  |
 +-------------------------+        +-------------------------+
 | question A (50)         |        | question B (60)         |
 |  -> normal price        |        |  -> normal price        |
 +-------------------------+        +-------------------------+

 Rule: anything that changes in the prefix = MISS
```

---

## 💰 Cost Impact
Example (illustrative; verify current prices): 6,000-token prefix, 100K requests/day at $3 per 1M normal input tokens. Without caching: 600M prefix tokens/day = $1,800/day. With a high hit rate and reads priced at about 10% of normal, prefix cost drops to roughly $180/day plus small write costs. Latency also falls (time-to-first-token).

Optimisation: order the prompt static-to-dynamic, normalise the prefix, keep traffic steady, monitor `cache_read` vs `cache_creation` tokens, and combine with prompt compression for the dynamic part.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Prefix | Start of the prompt | Prompt का शुरुआती हिस्सा |
| Cache hit | Prefix found in cache | Prefix cache में मिल गया |
| Cache write | Storing the prefix | Prefix को cache में रखना |
| TTL | How long cache lives | Cache कितनी देर रहता है |
| cache_control | Anthropic marker for caching | Anthropic का caching marker |
| Breakpoint | End of the cached part | Cached हिस्से का अंत |

---

## ⚡ 3-Line Summary
English: Prompt caching reuses a processed prompt prefix, making repeated long prefixes cheaper and faster. Put static content first, dynamic content last, and verify hits in usage fields. Anthropic needs cache_control; OpenAI caches automatically from 1,024 tokens.
Hindi: Prompt caching processed prefix को दोबारा इस्तेमाल करके दोहराए लंबे prefix को सस्ता और तेज़ बनाता है। Static पहले, dynamic बाद में रखो और usage fields में hits जाँचो। Anthropic में cache_control चाहिए; OpenAI 1,024 tokens से अपने आप cache करता है।

---

## ➡️ Next Topic
**070. Prompt Versioning** — track prompt changes like code so you can compare, roll back and audit.
