---

# 437. Token Usage Monitoring
# हिंदी में: Token Usage Monitoring

---

## 🔵 Simple Definition (English)
Token usage monitoring means continuously measuring input, output and cached tokens per request, per feature and per prompt version, and watching for anomalies (prompt bloat, runaway generation, context near limit). Tokens drive both cost and latency, so they are the earliest warning signal.

## 🔵 सरल परिभाषा (Hindi)
Token usage monitoring का मतलब है हर request, feature और prompt version के input, output और cached tokens लगातार नापना और असामान्य बदलाव (prompt bloat, बेकाबू generation, context limit के पास) पर नज़र रखना। Tokens cost और latency दोनों तय करते हैं, इसलिए ये सबसे पहली चेतावनी हैं।

---

## 🔴 Problem it Solves
- Prompts grow silently: someone adds 5 examples, RAG returns 10 chunks instead of 5, chat history is never trimmed.
- A request that reaches the context limit fails or gets truncated.
- Output can run away (model rambles for 4,000 tokens) with no error.

## 🔴 यह क्यों बना? (Hindi)
- Prompts चुपचाप बढ़ते हैं: किसी ने 5 examples जोड़ दिए, RAG 5 की जगह 10 chunks लौटाने लगा, chat history कभी trim नहीं हुई।
- Context limit तक पहुँचने पर request fail या truncate होती है।
- Output बेकाबू हो सकता है (model 4,000 tokens बोलता रहे) और कोई error नहीं आता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Read usage from every response: prompt_tokens, completion_tokens, cached tokens
Step 2 → Break input into parts: system / history / retrieved context / user (tiktoken estimate)
Step 3 → Emit histograms per feature + prompt_version + model
Step 4 → Track ratios: context_used / context_limit, output / max_tokens, cache_hit_ratio
Step 5 → Baseline: rolling median and p95 of tokens per feature
Step 6 → Alert: p95 input tokens > baseline x 1.3, or output hits max_tokens often (truncation)
Step 7 → Act: trim history, reduce top_k, compress prompt, enable prompt caching
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → हर response से usage पढ़ो: prompt_tokens, completion_tokens, cached tokens
Step 2 → Input को हिस्सों में बाँटो: system / history / retrieved context / user (tiktoken अनुमान)
Step 3 → Feature + prompt_version + model के हिसाब से histogram भेजो
Step 4 → Ratios track करो: context_used / limit, output / max_tokens, cache_hit_ratio
Step 5 → Baseline: हर feature के tokens का rolling median और p95
Step 6 → Alert: p95 input baseline x 1.3 से ऊपर, या output बार-बार max_tokens छुए
Step 7 → कदम: history trim, top_k घटाओ, prompt compress, prompt caching चालू करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Median input tokens were 480. After a release, p95 jumps to 3,100. Breakdown shows retrieved context grew from 3 to 12 chunks because someone changed `top_k` in config. Output tokens: 8% of answers end with `finish_reason="length"` (hit `max_tokens=60`), meaning JSON was cut and parsing failed. Fixes: restore `top_k=4`, raise `max_tokens` to 120 and use structured output.

**Zomato-style**: multi-turn chat history keeps all turns; monitoring shows tokens per turn grow linearly, so the team adds a rolling summary after 6 turns.

## 🟡 Real Example Hindi mein
**Tariff System**: Median input 480 tokens था। Release के बाद p95 3,100 हो गया। Breakdown बताता है retrieved context 3 से 12 chunks हो गया क्योंकि किसी ने config में `top_k` बदल दिया। Output में 8% जवाब `finish_reason="length"` पर खत्म हुए (`max_tokens=60`), JSON कट गया और parsing fail हुई। Fix: `top_k=4` वापस, `max_tokens` 120 और structured output।

---

## 💻 Code Example — Basic
Rolling baseline and anomaly check on token counts (pure Python, run directly).

```python
# Detect prompt bloat by comparing recent tokens to a baseline
from collections import deque                          # fixed-size window
from statistics import median                          # robust centre

WINDOW: deque[int] = deque(maxlen=50)                  # last 50 input-token counts
BASELINE: list[int] = []                               # baseline values


def record(in_tokens: int) -> None:
    WINDOW.append(in_tokens)                           # add newest value


def is_bloated(factor: float = 1.3) -> bool:
    if len(BASELINE) < 20 or len(WINDOW) < 20:         # need enough data
        return False
    return median(WINDOW) > median(BASELINE) * factor  # recent median much higher?


for t in [480, 500, 470, 510, 490] * 6:                # normal traffic -> baseline
    BASELINE.append(t)
    record(t)
print("bloated?", is_bloated())                        # False

for t in [900, 950, 1000, 980] * 8:                    # after bad release
    record(t)
print("bloated?", is_bloated())                        # True
print("recent median:", median(WINDOW), "baseline:", median(BASELINE))
```

## 💻 Code Example — Advanced
Part-by-part prompt budgeting with tiktoken, usage metrics (including cached tokens and truncation), async.

```python
# Production token monitor: per-part accounting + truncation detection
import logging                                                    # logs
from dataclasses import dataclass                                 # record
from typing import Optional                                       # hints

import tiktoken                                                   # exact token counts for OpenAI models
from openai import AsyncOpenAI                                    # client
from prometheus_client import Histogram, Counter                  # metrics

log = logging.getLogger("tokens")
enc = tiktoken.get_encoding("o200k_base")                         # encoding used by gpt-4o family
client = AsyncOpenAI()

IN_TOK = Histogram("llm_input_tokens", "Input tokens", ["feature", "version"],
                   buckets=(100, 250, 500, 1000, 2000, 4000, 8000, 16000))
OUT_TOK = Histogram("llm_output_tokens", "Output tokens", ["feature", "version"],
                    buckets=(10, 25, 50, 100, 250, 500, 1000))
CACHED = Counter("llm_cached_input_tokens_total", "Cached input tokens", ["feature"])
TRUNC = Counter("llm_truncated_total", "finish_reason=length", ["feature"])

MAX_INPUT_BUDGET = 3_000                                          # our own budget per request


def count(text: str) -> int:
    return len(enc.encode(text))                                  # token count of a string


@dataclass
class PromptParts:                                                # parts to account separately
    system: str
    history: str
    context: str
    user: str

    def sizes(self) -> dict[str, int]:
        return {k: count(v) for k, v in vars(self).items()}       # tokens per part


async def monitored_call(parts: PromptParts, feature: str, version: str) -> Optional[str]:
    sizes = parts.sizes()                                         # pre-call estimate by part
    if sum(sizes.values()) > MAX_INPUT_BUDGET:                    # warn before paying
        log.warning("prompt over budget %s %s", feature, sizes)
    resp = await client.chat.completions.create(
        model="gpt-4o-mini", max_tokens=120, temperature=0,
        messages=[{"role": "system", "content": parts.system},
                  {"role": "user", "content": f"{parts.history}\n{parts.context}\n{parts.user}"}],
    )
    u = resp.usage
    if u:                                                         # record real usage
        IN_TOK.labels(feature, version).observe(u.prompt_tokens)
        OUT_TOK.labels(feature, version).observe(u.completion_tokens)
        details = getattr(u, "prompt_tokens_details", None)       # cached tokens info
        cached = getattr(details, "cached_tokens", 0) or 0
        CACHED.labels(feature).inc(cached)
    if resp.choices[0].finish_reason == "length":                 # answer was cut off
        TRUNC.labels(feature).inc()
        log.error("truncated output %s", feature)
        return None                                               # caller must handle
    return resp.choices[0].message.content
```

---

## 🟠 FastAPI Integration
Reject oversized inputs before paying, and return token usage to the client.

```python
# FastAPI: reject oversized inputs, return usage to the client
import tiktoken
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()
enc = tiktoken.get_encoding("o200k_base")
MAX_USER_TOKENS = 2_000                                        # per-request cap


class Req(BaseModel):
    description: str = Field(min_length=3, max_length=20_000)  # char cap first (cheap)


@app.post("/classify")
async def classify(req: Req) -> dict:
    n = len(enc.encode(req.description))                       # exact tokens
    if n > MAX_USER_TOKENS:
        raise HTTPException(status_code=413, detail=f"input too long: {n} tokens, max {MAX_USER_TOKENS}")
    # ... call LLM here; fill from response.usage ...
    return {"hs_code": "8518.22", "usage": {"input_tokens": n, "output_tokens": 12}}
```

---

## 🔗 LangChain / LangGraph Connection
Messages carry `usage_metadata`; `trim_messages` keeps history inside a token budget; LangGraph state can store a running token total.

```python
# LangChain: trim history to a token budget, then read usage
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, trim_messages
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
history = [SystemMessage("You classify goods."), HumanMessage("a"), AIMessage("b"), HumanMessage("HS for speaker?")]

trimmed = trim_messages(history, max_tokens=500, token_counter=llm,     # use the model to count
                        strategy="last", include_system=True)           # keep latest + system
msg = llm.invoke(trimmed)
print(msg.usage_metadata)        # {'input_tokens': ..., 'output_tokens': ..., 'total_tokens': ...}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Unlimited chat history
✅ Correct: window or summarise.

```python
# Wrong: history grows every turn; cost per turn grows linearly (total cost quadratic)
messages = all_turns
# Right: keep last N turns or a rolling summary
messages = [system] + summary + all_turns[-6:]
```

❌ Mistake 2: Ignoring `finish_reason`
✅ Correct: treat `"length"` as an error.

```python
# Wrong
data = json.loads(resp.choices[0].message.content)   # JSONDecodeError on truncated output
# Right
if resp.choices[0].finish_reason == "length":
    raise TruncatedOutput()
```

---

## 🧠 Tricky Interview Question
**Q**: "Same prompt, same model, but billed input tokens are 30% higher than your tiktoken count. Why?"

**Answer**: Chat formatting adds overhead tokens per message and for the reply primer; function/tool definitions and the JSON schema for structured outputs are serialised into the prompt and billed; images count by size; frameworks add system text (LangChain agents add tool descriptions); and tiktoken may use the wrong encoding for the model. Use `response.usage` as the source of truth and tiktoken only for pre-call estimates, calibrating the offset.

---

## ⚫ Interview Questions + Answers

Q1 (Easy): What are the two main token counters in usage?
A1: `prompt_tokens` (input) and `completion_tokens` (output); total is their sum.

Q2 (Easy): What does `finish_reason="length"` mean?
A2: Generation stopped because `max_tokens` (or context) was reached; the answer is incomplete.

Q3 (Medium): What are cached tokens?
A3: Input tokens served from the provider's prompt cache (repeated prefix). They are billed at a discount and processed faster. Monitor cache-hit ratio; keep static content at the start of the prompt.

Q4 (Medium): How do you set token alert thresholds?
A4: Use a baseline per feature (median, p95) and alert on relative change (for example +30% for an hour) plus absolute limits (80% of context window). Avoid one global threshold.

Q5 (Hard): How do you control tokens in a long-running agent?
A5: Budget per run (max steps, max total tokens), summarise or truncate tool outputs before they re-enter context, keep a scratchpad summary instead of full history, store large artifacts outside the prompt and pass references, and abort with a clear status when the budget is hit.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- RAG (variable context size), chat (growing history), agents (loops)
- Cost control and capacity planning

❌ Avoid when:
- Tiny fixed prompts where tokens never vary; simple cost totals suffice

---

## 📊 Visual Diagram
```
 Input tokens per request (feature=classify)
 system   ████ 120
 history  ██ 60
 context  ████████████████████ 1,900   <-- grew from 400 (top_k 3 -> 12)
 user     █ 30
          ─────────────────────────────
 total 2,110     baseline median 480   -> ALERT (+340%)

 Output: 118 / max_tokens 120  ->  finish_reason=length in 8%  -> ALERT
```

---

## 💰 Cost Impact
- Input tokens are usually the bulk of RAG spend. Going from 480 to 2,110 input tokens at 1M requests/month on gpt-4o-mini adds about 1.63B tokens, roughly $245/month (at $0.15 per 1M).
- Output tokens cost 4x more per token; capping `max_tokens` and requesting terse JSON saves money and time.
- Optimise: trim history, lower `top_k`, compress instructions, use prompt caching for static prefixes, and pick smaller models for easy steps.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Input tokens | Tokens sent to model | Model को भेजे tokens |
| Output tokens | Tokens generated | Model द्वारा बनाए tokens |
| Cached tokens | Discounted repeated-prefix tokens | Cache से मिले सस्ते tokens |
| Prompt bloat | Prompt growing unnoticed | Prompt का चुपचाप बढ़ना |
| finish_reason | Why generation stopped | Generation क्यों रुका |
| Context window | Max tokens model can see | Model कितने tokens देख सकता है |
| Baseline | Normal reference level | सामान्य संदर्भ स्तर |

---

## ⚡ 3-Line Summary
English: Monitor input, output and cached tokens by feature and prompt version, with part-wise breakdown. Alert on relative jumps and on truncation (`finish_reason=length`). Fix bloat by trimming history, reducing top_k and caching prefixes.
Hindi: Feature और prompt version के हिसाब से input, output और cached tokens को part-wise नापो। Relative उछाल और truncation (`finish_reason=length`) पर alert लगाओ। History trim, top_k कम और prefix caching से bloat ठीक करो।

---

## ➡️ Next Topic
**438. Model Performance Monitoring** — tracking accuracy, groundedness and regressions of the model's answers over time.
