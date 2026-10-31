---

# 447. Prompt Caching (Anthropic Native)
# हिंदी में: Prompt Caching (Anthropic Native)

---

## 🔵 Simple Definition (English)
Anthropic prompt caching lets Claude reuse the already-processed beginning (prefix) of your prompt. You mark a block with `cache_control`. Later requests with the same prefix read it at about 10 percent of the normal input price and with lower latency. The model still generates a fresh answer every time.

## 🔵 सरल परिभाषा (Hindi)
Anthropic prompt caching में Claude आपके prompt के शुरुआती हिस्से (prefix) को दोबारा इस्तेमाल करता है जो पहले process हो चुका है। आप किसी block पर `cache_control` लगाते हो। बाद की requests में वही prefix सामान्य input price के लगभग 10 प्रतिशत पर और कम latency के साथ पढ़ा जाता है। जवाब हर बार model नया बनाता है।

---

## 🔴 Problem it Solves
- Apps resend a huge static prefix on every call: long system prompt, tariff manual, tool definitions, few-shot examples.
- You pay full input price for the same 20,000 tokens again and again, and wait for them to be processed again.
- Answer-caching cannot help because each user question is different.

## 🔴 यह क्यों बना? (Hindi)
- Apps हर call में एक बड़ा static prefix दोबारा भेजते हैं: लंबा system prompt, tariff manual, tool definitions, few-shot examples।
- वही 20,000 tokens के लिए बार-बार पूरा input price देना पड़ता है और process होने का इंतज़ार भी।
- Answer-caching यहाँ काम नहीं करती क्योंकि हर user का सवाल अलग है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Put stable content FIRST (tools, system, documents), changing content LAST (user question)
Step 2 → Add "cache_control": {"type": "ephemeral"} to the last block of the stable prefix
Step 3 → First call: prefix is processed and WRITTEN to cache (write costs about 1.25x input price for the 5-min TTL)
Step 4 → Next call within TTL with a byte-identical prefix: cache READ (about 0.1x input price)
Step 5 → Each read refreshes the TTL (default 5 minutes; optional 1 hour with "ttl": "1h" at higher write price)
Step 6 → Check usage: cache_creation_input_tokens, cache_read_input_tokens, input_tokens
Step 7 → Minimum cacheable prefix is about 1024 tokens (higher for some models); shorter prefixes are not cached
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → स्थिर content पहले रखो (tools, system, documents), बदलने वाला content आख़िर में (user सवाल)
Step 2 → स्थिर prefix के आख़िरी block पर "cache_control": {"type": "ephemeral"} लगाओ
Step 3 → पहली call: prefix process होकर cache में WRITE होता है (5 मिनट TTL के लिए लगभग 1.25x input price)
Step 4 → TTL के अंदर अगली call, byte-बराबर prefix: cache READ (लगभग 0.1x input price)
Step 5 → हर read TTL नया कर देता है (default 5 मिनट; "ttl": "1h" से 1 घंटा, write महंगा)
Step 6 → usage देखो: cache_creation_input_tokens, cache_read_input_tokens, input_tokens
Step 7 → न्यूनतम cacheable prefix लगभग 1024 tokens (कुछ models में ज़्यादा); उससे छोटा cache नहीं होता
```
(Exact multipliers and minimums can change; always confirm on the current Anthropic pricing page.)

---

## 🟡 Real World Example
**Tariff Classification System**: The system prompt plus a 30,000-token excerpt of the customs tariff schedule is identical for every request. Mark it cached. Each classification then only pays full price for the 50-token product description. With 1,000 requests inside a busy hour, 999 reads cost roughly 10 percent for the 30K prefix.
**Amazon-style assistant**: A long catalogue policy and tool list is cached; each customer message is new.

## 🟡 Real Example Hindi mein
**Tariff System**: System prompt और customs tariff schedule के 30,000 tokens हर request में एक जैसे हैं। इन्हें cached mark करो। फिर हर classification में सिर्फ़ 50-token product description का पूरा दाम लगता है। व्यस्त घंटे में 1,000 requests में से 999 reads में 30K prefix लगभग 10 प्रतिशत दाम पर आता है।
**Amazon-style assistant**: लंबी catalogue policy और tool list cached रहती है; हर customer message नया होता है।

---

## 💻 Code Example — Basic
```python
# Basic: build the request body and compute cost WITHOUT calling the network, so it runs offline.
# The real call is shown in the comment: client.messages.create(**request)
LONG_MANUAL = "TARIFF MANUAL SECTION ... " * 400  # pretend this is >1024 tokens of stable text


def build_request(question: str) -> dict:
    return {
        "model": "claude-sonnet-4-5",  # use a current model id from the docs
        "max_tokens": 300,  # cap output tokens
        "system": [  # system as a list of blocks
            {"type": "text", "text": "You classify goods into HS codes."},  # short instruction
            {
                "type": "text",
                "text": LONG_MANUAL,  # big stable document
                "cache_control": {"type": "ephemeral"},  # cache everything up to and including this block
            },
        ],
        "messages": [{"role": "user", "content": question}],  # changing part comes after the cached prefix
    }


def cost(usage: dict, price_in: float = 3.0) -> float:
    # price_in = USD per 1M input tokens; write ~1.25x, read ~0.1x (check current pricing)
    return (
        usage["input_tokens"] * price_in
        + usage["cache_creation_input_tokens"] * price_in * 1.25
        + usage["cache_read_input_tokens"] * price_in * 0.10
    ) / 1_000_000


if __name__ == "__main__":
    req = build_request("steel water bottle")  # build request
    print(list(req.keys()))  # show request shape
    first = {"input_tokens": 20, "cache_creation_input_tokens": 8000, "cache_read_input_tokens": 0}  # call 1 usage
    later = {"input_tokens": 20, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 8000}  # call 2 usage
    print(f"first call  ${cost(first):.5f}")  # pays the write premium
    print(f"later calls ${cost(later):.5f}")  # pays about 10 percent for the prefix
```

## 💻 Code Example — Advanced
```python
# Production: async Anthropic client, usage tracking, error handling, 1-hour TTL option.
# pip install anthropic
from __future__ import annotations

import logging  # logging
from dataclasses import dataclass  # tidy result type

import anthropic  # official SDK
from anthropic import AsyncAnthropic  # async client

log = logging.getLogger("anthropic_cache")  # logger


@dataclass
class CacheStats:
    created: int  # tokens written to cache
    read: int  # tokens read from cache
    fresh: int  # uncached input tokens
    output: int  # output tokens


class TariffClassifier:
    def __init__(self, manual: str, ttl: str = "5m") -> None:
        self.client = AsyncAnthropic()  # reads ANTHROPIC_API_KEY
        cc: dict = {"type": "ephemeral"}  # default 5-minute cache
        if ttl == "1h":
            cc["ttl"] = "1h"  # longer TTL, higher write price
        self.system = [
            {"type": "text", "text": "Return JSON: {hs_code, reason}."},
            {"type": "text", "text": manual, "cache_control": cc},  # cache breakpoint
        ]

    async def classify(self, product: str) -> tuple[str, CacheStats]:
        try:
            resp = await self.client.messages.create(
                model="claude-sonnet-4-5",  # choose a current model
                max_tokens=300,
                system=self.system,  # identical prefix every time
                messages=[{"role": "user", "content": product}],
            )
        except anthropic.RateLimitError:  # 429
            log.warning("rate limited")
            raise
        except anthropic.APIStatusError as exc:  # other HTTP errors
            log.error("api error %s", exc.status_code)
            raise
        u = resp.usage  # usage object
        stats = CacheStats(
            created=getattr(u, "cache_creation_input_tokens", 0) or 0,
            read=getattr(u, "cache_read_input_tokens", 0) or 0,
            fresh=u.input_tokens,
            output=u.output_tokens,
        )
        text = resp.content[0].text if resp.content else ""  # first text block
        return text, stats
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # schema

MANUAL = open("tariff_manual.txt", encoding="utf-8").read()  # large static text loaded once
app = FastAPI()  # app
clf = TariffClassifier(MANUAL, ttl="1h")  # one instance keeps the prefix byte-identical


class In(BaseModel):
    product: str  # user input


@app.post("/classify")
async def classify(body: In) -> dict:
    text, s = await clf.classify(body.product)  # call Claude
    return {"answer": text, "cache_read_tokens": s.read, "cache_write_tokens": s.created}  # expose metrics
```
A background "keep-warm" ping every 4 minutes can keep the 5-minute cache alive during quiet periods, but only if the saved cost beats the ping cost.

---

## 🔗 LangChain / LangGraph Connection
`langchain-anthropic` passes `cache_control` through content blocks, so you can use it inside a LangChain message.

```python
from langchain_anthropic import ChatAnthropic  # Claude chat model
from langchain_core.messages import HumanMessage, SystemMessage  # message types

llm = ChatAnthropic(model="claude-sonnet-4-5")  # model
messages = [
    SystemMessage(content=[{"type": "text", "text": MANUAL, "cache_control": {"type": "ephemeral"}}]),  # cached block
    HumanMessage(content="steel water bottle"),  # dynamic part
]
resp = llm.invoke(messages)  # usage_metadata shows input_token_details.cache_read
print(resp.usage_metadata)  # token breakdown
```
In LangGraph, keep the cached system prefix identical in every node that needs it.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Putting dynamic text (timestamp, user name) before the cached block
✅ Correct: Anything before the breakpoint must be byte-identical; put changing text after it.

```python
# Wrong: prefix changes every call -> 0 cache reads
system = f"Today is {now}. " + MANUAL
# Right: static first, dynamic in the user turn
system = MANUAL ; user = f"Today is {now}. Product: {p}"
```

❌ Mistake 2: Caching a prefix that is too short or never reused
✅ Correct: Cache only prefixes above the model minimum that will be reused several times in the TTL, otherwise you pay the write premium for nothing.

```python
# Wrong: 300-token prompt, used once -> no benefit
# Right: 8,000-token manual used by hundreds of calls per hour
```

---

## 🧠 Tricky Interview Question
**Q**: "You added cache_control but `cache_read_input_tokens` is always 0 and `cache_creation_input_tokens` is large every time. Why?"

**Answer**: The prefix is not identical between calls. Common causes: a timestamp or request id in the system prompt, tools listed in a different order, JSON serialised with unstable key order, changing the model or tool choice between calls, or calls arriving more than the TTL apart. Order of cache levels is tools, then system, then messages, so a change early invalidates everything after it. Fix by freezing the prefix and logging a hash of it.

---

## ⚫ Interview Questions + Answers

Q1: What is prompt caching? (Easy)
A1: The provider stores the processed prefix of your prompt and reuses it for later calls, charging much less for those tokens and reducing latency.

Q2: How do you enable it on Anthropic? (Easy)
A2: Add `cache_control: {"type": "ephemeral"}` to a content block (tool, system or message block). Everything up to that block is the cached prefix.

Q3: How do I know it worked? (Medium)
A3: The `usage` object shows `cache_creation_input_tokens` and `cache_read_input_tokens`. Reads greater than 0 mean a hit.

Q4: Prompt caching vs response caching? (Medium)
A4: Prompt caching reuses the input prefix but the model still generates a new answer (works for different questions with the same context). Response caching returns a stored answer and skips the model completely (works only for repeated or similar questions).

Q5: Design caching for a RAG app where retrieved chunks change each query. (Hard)
A5: Cache only what is stable: system prompt, tool definitions and few-shot examples at the front with a breakpoint. Retrieved chunks vary, so they go after the breakpoint. If a few documents are queried repeatedly, group by document: one prefix per document with its text cached, so many questions on that document hit. Use the 1-hour TTL if requests are spaced, and verify using usage metrics that read tokens dominate.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Large static prefix (docs, tools, examples) reused many times within minutes
- Multi-turn chat (the growing history prefix repeats)
- Agents with long tool definitions

❌ Avoid when:
- Prompt is below the minimum cacheable length
- Prefix changes every call or calls are rare (idle more than the TTL)
- You need identical answers without calling the model (use response cache)

---

## 📊 Visual Diagram
```
 Request 1:  [tools][system+manual ★cache_control][question A]
                 └─── processed + WRITTEN (1.25x) ───┘   └ normal price
 Request 2:  [tools][system+manual ★cache_control][question B]
                 └───── READ from cache (0.1x) ──────┘   └ normal price
 Anything before ★ changes ─► cache MISS for the whole prefix
```

---

## 💰 Cost Impact
**Token usage**: Example with an 8,000-token prefix, $3 per 1M input tokens. Uncached: $0.024 per call. First cached call: about $0.030. Later calls: about $0.0024 (90 percent saving on the prefix). After about 2 calls the write premium is repaid.
**Optimisation**: put stable content first, keep the prefix byte-identical, route traffic so calls land within the TTL, use 1-hour TTL for sparse traffic, and monitor `cache_read_input_tokens / total input`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Prefix | Start of prompt that stays the same | prompt का स्थिर शुरुआती हिस्सा |
| cache_control | Marker for a cache breakpoint | cache breakpoint का निशान |
| Ephemeral | Short-lived cache type | थोड़े समय का cache |
| Cache write | First processing and storing | पहली बार process और store |
| Cache read | Reuse of stored prefix | stored prefix का दोबारा उपयोग |
| TTL | How long the cache lives | cache कितनी देर रहे |

---

## ⚡ 3-Line Summary
English: Anthropic prompt caching reuses a static prompt prefix at about 10 percent of input price. Put stable content first, mark it with cache_control, and keep it byte-identical. Check cache_read_input_tokens to confirm savings.
Hindi: Anthropic prompt caching स्थिर prompt prefix को input price के लगभग 10 प्रतिशत पर दोबारा इस्तेमाल करता है। स्थिर content पहले रखो, cache_control लगाओ और उसे byte-identical रखो। बचत जाँचने के लिए cache_read_input_tokens देखो।

---

## ➡️ Next Topic
**448. Prompt Caching (OpenAI Native)** — OpenAI does the same automatically, with no code marker, and a few different rules.
