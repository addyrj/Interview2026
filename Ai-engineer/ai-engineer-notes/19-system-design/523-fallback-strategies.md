---

# 523. Fallback Strategies
# हिंदी में: Fallback Strategies

---

## 🔵 Simple Definition (English)
A fallback is a "plan B" that runs when the primary path fails or is too slow: another model, another provider, a cached answer, a rule-based result, or a human. The goal is to return something safe and useful instead of an error.

## 🔵 सरल परिभाषा (Hindi)
Fallback एक "plan B" है जो primary path fail या बहुत slow होने पर चलता है: दूसरा model, दूसरा provider, cached answer, rule-based result या human। मकसद error की जगह कुछ safe और काम का जवाब देना है।

---

## 🔴 Problem it Solves
Retries do not help when the provider is down for 20 minutes, a model is deprecated, a safety filter refuses, or the answer fails validation. A single path means a single point of failure, so the product goes down with one vendor.

## 🔴 यह क्यों बना? (Hindi)
Provider 20 मिनट down हो, model deprecate हो जाए, safety filter मना कर दे या answer validation में fail हो, तो retries काम नहीं आते। Single path का मतलब single point of failure है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → List failure modes: outage, 429, timeout, refusal, invalid output, low confidence
Step 2 → Order fallbacks by quality and cost: primary model -> backup model -> other provider
        -> cache (stale answer) -> rules/keyword engine -> human queue -> honest error
Step 3 → Define a trigger per failure mode (error class, timeout, validation fail, confidence)
Step 4 → Try each level with its own timeout and the shared deadline
Step 5 → Tag the response with which level answered (fallback_level, degraded=true)
Step 6 → Keep prompts/schemas portable so a different model can take over
Step 7 → Test fallbacks regularly (chaos drills); untested fallbacks do not work
Step 8 → Monitor fallback rate; high rate = fix the primary
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Failure modes लिखो: outage, 429, timeout, refusal, invalid output, low confidence
Step 2 → Quality और cost से order: primary -> backup model -> दूसरा provider
        -> cache (पुराना answer) -> rules -> human queue -> साफ error
Step 3 → हर failure mode का trigger तय करो
Step 4 → हर level अपने timeout और shared deadline के साथ
Step 5 → Response पर लिखो कौन-सा level answer दिया (fallback_level, degraded=true)
Step 6 → Prompts/schemas portable रखो ताकि दूसरा model संभाल सके
Step 7 → Fallbacks की नियमित testing (chaos drill)
Step 8 → Fallback rate monitor करो; ज़्यादा हो तो primary ठीक करो
```

---

## 🟡 Real World Example
**Tariff Classification System** fallback ladder: (1) primary LLM; (2) backup model from another provider; (3) exact-match cache of past classifications for the same description; (4) keyword rules mapping common products to chapters (lower confidence, flagged "approximate"); (5) human broker queue. Customs filings need correct codes, so levels 3-4 can show a suggestion but must not auto-file.

**Zomato-style**: If the AI "recommend dishes" call fails, show the restaurant's popular items list instead.

## 🟡 Real Example Hindi mein
**Tariff System** fallback ladder: (1) primary LLM; (2) दूसरे provider का backup model; (3) पुरानी classifications का exact cache; (4) keyword rules (कम confidence, "approximate" flag); (5) human broker queue। Customs filing में सही code ज़रूरी है, इसलिए level 3-4 सिर्फ suggestion दिखाएँ, auto-file नहीं।
**Zomato-style**: AI dish recommendation fail हो तो restaurant की popular items list दिखाओ।

---

## 💻 Code Example — Basic
```python
# Simple fallback chain (pure Python, runs offline)
from typing import Callable                         # type hint for handlers

def primary(text: str) -> str:
    """Primary model: pretend it is down."""
    raise ConnectionError("primary model unavailable")   # simulate outage

def backup(text: str) -> str:
    """Backup model: pretend it times out."""
    raise TimeoutError("backup timed out")           # simulate slowness

CACHE: dict[str, str] = {"smart phone": "8517.13"}   # past answers

def from_cache(text: str) -> str:
    """Return a cached answer or raise KeyError."""
    return CACHE[text]                               # KeyError if missing

def rules(text: str) -> str:
    """Last-resort keyword rules."""
    if "shirt" in text:                              # clothing rule
        return "6109.10"
    raise LookupError("no rule matched")             # nothing matched

LADDER: list[tuple[str, Callable[[str], str]]] = [   # order = priority
    ("primary", primary), ("backup", backup), ("cache", from_cache), ("rules", rules),
]

def classify(text: str) -> dict[str, str]:
    """Try each level until one works."""
    for name, fn in LADDER:                          # go down the ladder
        try:
            return {"code": fn(text), "level": name}   # first success wins
        except Exception as exc:                     # catch any failure
            print(f"{name} failed: {exc!r}")         # log it
    return {"code": "UNKNOWN", "level": "human_review"}   # final fallback

print(classify("smart phone"))                       # served from cache
print(classify("cotton shirt"))                      # served from rules
print(classify("quantum widget"))                    # goes to human
```

## 💻 Code Example — Advanced
```python
# Async fallback chain with per-level timeout, validation, and metrics
import asyncio                                         # async runtime
import time                                            # latency tracking
from collections import Counter                        # fallback counters
from dataclasses import dataclass                      # result type
from typing import Awaitable, Callable                 # type hints

@dataclass
class Level:
    """One rung of the ladder."""
    name: str                                          # label for metrics
    fn: Callable[[str], Awaitable[dict]]               # async handler returning {code, confidence}
    timeout_s: float                                   # per-level timeout
    auto_file_ok: bool                                 # can this level's answer be used without review?

@dataclass
class Outcome:
    code: str | None                                   # answer
    level: str                                         # who answered
    degraded: bool                                     # True if not the primary
    needs_review: bool                                 # True if a human must confirm

class FallbackChain:
    def __init__(self, levels: list[Level], valid_codes: set[str], min_conf: float = 0.7) -> None:
        self.levels = levels                           # ordered ladder
        self.valid = valid_codes                       # trusted code table
        self.min_conf = min_conf                       # confidence gate
        self.counts: Counter[str] = Counter()          # how often each level answered

    def _ok(self, r: dict) -> bool:
        """Validate a level's answer (schema + business rule + confidence)."""
        return r.get("code") in self.valid and float(r.get("confidence", 0)) >= self.min_conf

    async def run(self, text: str, total_s: float = 5.0) -> Outcome:
        """Walk the ladder under one total deadline."""
        start = time.monotonic()                       # start clock
        for i, lv in enumerate(self.levels):           # each rung
            left = total_s - (time.monotonic() - start)   # remaining time
            if left <= 0:                              # out of time
                break
            try:
                r = await asyncio.wait_for(lv.fn(text), min(lv.timeout_s, left))   # run with timeout
                if self._ok(r):                        # good answer?
                    self.counts[lv.name] += 1          # metric
                    return Outcome(r["code"], lv.name, i > 0, not lv.auto_file_ok)
            except Exception as exc:                   # failure -> next rung
                self.counts[f"{lv.name}_error"] += 1   # error metric
        self.counts["human"] += 1                      # nobody could answer
        return Outcome(None, "human_review", True, True)

async def demo() -> None:
    async def primary(t: str) -> dict:                 # down
        raise ConnectionError("503")
    async def backup(t: str) -> dict:                  # works but unsure
        await asyncio.sleep(0.01)
        return {"code": "8517.13", "confidence": 0.9}
    chain = FallbackChain(
        [Level("primary", primary, 2, True), Level("backup", backup, 2, True)],
        valid_codes={"8517.13"},
    )
    print(await chain.run("smart phone"), dict(chain.counts))   # answered by backup

if __name__ == "__main__":
    asyncio.run(demo())                                # run
```

---

## 🟠 FastAPI Integration
Return the fallback level in the response body and a header so clients and dashboards can see degraded answers. Use status 200 for acceptable degraded answers and 202/409-style flows when a human must confirm.

```python
# FastAPI: expose degradation transparently
from fastapi import FastAPI, Response                       # framework
from pydantic import BaseModel                              # validation

app = FastAPI()                                             # app
chain = FallbackChain(levels=my_levels, valid_codes=my_codes)   # from the advanced block (my_* are your own)

class Req(BaseModel):
    description: str                                        # product text

@app.post("/classify")
async def classify(req: Req, resp: Response) -> dict[str, object]:
    out = await chain.run(req.description, total_s=4.0)     # run ladder
    resp.headers["X-Fallback-Level"] = out.level            # visible to clients and logs
    return {"code": out.code, "level": out.level,
            "degraded": out.degraded, "needs_review": out.needs_review}
```

---

## 🔗 LangChain / LangGraph Connection
`Runnable.with_fallbacks([...])` is built for this, and it can limit which exceptions trigger fallback via `exceptions_to_handle`. In LangGraph, use conditional edges: a validator node routes to a `backup_model` node, then a `human_review` node (with `interrupt` for human-in-the-loop and a checkpointer).

```python
# LangChain: model fallback chain
from langchain_openai import ChatOpenAI                       # primary
from langchain_anthropic import ChatAnthropic                 # backup provider

primary = ChatOpenAI(model="gpt-4o-mini", timeout=5, max_retries=1)       # fast and cheap
backup = ChatAnthropic(model="claude-3-5-haiku-latest", timeout=8)        # model name illustrative; use a current one

llm = primary.with_fallbacks([backup])                        # on error, use backup
# result = await llm.ainvoke("HS code for smartphone")        # transparent to callers
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: A fallback that shares the same failure
✅ Correct: Use a truly independent path (other provider/region/method).

```python
# Wrong — "backup" is the same provider and same outage
backup = ChatOpenAI(model="gpt-4o-mini")        # primary is also OpenAI

# Right — different vendor or non-LLM path
backup = ChatAnthropic(model="<current-model>")
```

❌ Mistake 2: Silent degradation
✅ Correct: Mark degraded answers and never auto-act on low-trust ones.

```python
# Wrong — user thinks it is a verified answer
return {"code": rules(text)}

# Right
return {"code": rules(text), "degraded": True, "needs_review": True}
```

---

## 🧠 Tricky Interview Question

**Q**: "Your fallback to a cheaper model works during an outage. After the outage, the cost drops but customer complaints rise for weeks. Why?"

**Answer**: The system kept serving a lower-quality path, or the circuit breaker never closed, or quality was never measured per fallback level. Also, fallback models respond differently to the same prompt (format, tone, accuracy), so they need their own evals and possibly prompt variants. Add per-level quality metrics, make failback automatic (probe the primary and return to it), alert on high fallback share, and run regression evals on every fallback model.

---

## ⚫ Interview Questions + Answers

Q1: Retry vs fallback? (Easy)
A1: Retry repeats the same path for transient errors. Fallback switches to a different path when the primary keeps failing or is unsuitable.

Q2: Give three fallback options for an LLM call. (Easy)
A2: Backup model/provider, cached answer, rule-based or template response, human review, or an honest error message.

Q3: When should the fallback NOT answer? (Medium)
A3: When a wrong answer is harmful or irreversible (legal filings, payments, medical). Then fail safe: queue for a human, show "try later", or give a clearly labelled suggestion without taking action.

Q4: How do you make prompts portable across models? (Medium)
A4: Keep prompts simple and model-agnostic, use structured output with a shared schema, put model-specific tweaks in config, and run the same eval set on every model so you know the quality gap.

Q5: Design failover for a multi-region, multi-provider LLM gateway. (Hard)
A5: Health-check each provider/region, route by weights, use circuit breakers per target, fail over on error class and latency, keep quotas separate per provider, replicate the cache, and normalise request/response formats in the gateway. Prevent cascade overload (the backup gets 100% traffic) with load shedding and priority tiers. Auto-fail back gradually with canary percentages, and drill it quarterly.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Users depend on the feature and downtime is costly
- Multiple viable providers or methods exist
- A stale or approximate answer is better than none

❌ Avoid when:
- A wrong answer is worse than no answer (then fail safe)
- You cannot test or monitor the fallback path

---

## 📊 Visual Diagram
```
Request
  ▼
[Primary LLM] ──ok──▶ answer
  │fail/slow/invalid
  ▼
[Backup model/provider] ──ok──▶ answer (degraded)
  │fail
  ▼
[Cache: previous answer] ──hit──▶ answer (stale, flagged)
  │miss
  ▼
[Rules / keywords] ──match──▶ approximate (needs review)
  │none
  ▼
[Human queue / friendly error]
```

---

## 💰 Cost Impact
- Fallbacks to cheaper tiers (cache, rules) lower cost; fallbacks to a more expensive model raise it. Illustrative: if 2% of 1M calls fall back to a $3/1M-input model with 700 tokens each, extra cost is 14M tokens x $3 = about $42 per million calls, small versus lost revenue from downtime.
- Failed attempts still bill input tokens if the provider processed them (partial streams too), so use short timeouts and cancel abandoned calls.
- Cache fallbacks cost nothing in tokens; keep a longer-lived "stale" cache specifically for outages.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fallback | Alternative path on failure | Failure पर वैकल्पिक रास्ता |
| Failover | Switch to a standby system | Standby system पर switch |
| Failback | Return to primary after recovery | Recovery के बाद primary पर वापसी |
| Degraded mode | Reduced-quality service | कम quality में सेवा |
| Stale cache | Old but usable answer | पुराना पर काम का answer |
| Human-in-the-loop | Person confirms the result | इंसान से confirmation |
| Provider diversity | Using multiple vendors | कई vendors का उपयोग |

---

## ⚡ 3-Line Summary
English: A fallback ladder (backup model, cache, rules, human) lets the system answer when the primary path fails. Mark degraded answers and never auto-act on low-trust ones. Test and monitor fallbacks, because untested plan B fails when needed.
Hindi: Fallback ladder (backup model, cache, rules, human) से primary fail होने पर भी system जवाब देता है। Degraded answers को mark करो और low-trust पर auto-action मत लो। Fallbacks test और monitor करो, वरना ज़रूरत पर plan B fail होगा।

---

## ➡️ Next Topic
**524. Multi-model Strategy** — fallbacks use a second model; next we plan using several models on purpose for cost, quality and speed.
