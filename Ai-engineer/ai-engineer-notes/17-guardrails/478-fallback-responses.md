
---

# 478. Fallback Responses
# हिंदी में: Fallback Responses (विकल्प जवाब)

---

## 🔵 Simple Definition (English)
A fallback response is what the system returns when the normal path cannot be trusted or fails: low confidence, blocked content, provider outage, timeout, or empty retrieval. Good fallbacks are **safe, honest and useful**: they say what happened and offer a next step (ask for details, use a cheaper path, hand to a human), instead of a raw error or a guess.

## 🔵 सरल परिभाषा (Hindi)
Fallback response वह जवाब है जो तब मिलता है जब normal रास्ता भरोसेमंद नहीं या fail हो: कम confidence, blocked content, provider outage, timeout या खाली retrieval। अच्छे fallback **सुरक्षित, ईमानदार और उपयोगी** होते हैं: बताते हैं क्या हुआ और अगला कदम देते हैं (और details माँगो, सस्ता रास्ता, human को भेजो), न कि raw error या अंदाज़ा।

---

## 🔴 Problem it Solves
Without fallbacks, failures leak as 500 errors, hallucinated guesses, or blank screens. A tariff bot that guesses an HS code when unsure creates compliance risk; one that crashes when the LLM API is down loses trust. Fallbacks turn failures into controlled, predictable behaviour.

## 🔴 यह क्यों बना? (Hindi)
Fallback के बिना failures 500 errors, hallucinated अंदाज़ों या blank screens के रूप में बाहर आते हैं। Tariff bot अनिश्चित होने पर HS code का अंदाज़ा लगाए तो compliance risk है; LLM API down होने पर crash हो तो भरोसा टूटता है। Fallback failures को नियंत्रित, अनुमानित व्यवहार में बदलते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define failure types: low_confidence, blocked, no_context, timeout, provider_error
Step 2 → For each type, define a fallback ladder (try next rung on failure):
         a) retry (transient) → b) backup model/provider → c) cached/similar answer
         d) rule-based or keyword lookup → e) honest "I don't know" + next step → f) human handoff
Step 3 → Enforce timeouts so the ladder moves quickly (e.g. 8 s for primary)
Step 4 → Mark the response with a `fallback` reason (for the UI and metrics)
Step 5 → Never present a fallback guess as a confident answer
Step 6 → Log every fallback; alert if the rate exceeds a threshold
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Failure types तय करो: low_confidence, blocked, no_context, timeout, provider_error
Step 2 → हर type के लिए ladder: retry → backup model → cached answer
         → rule-based lookup → ईमानदार "पता नहीं" + अगला कदम → human handoff
Step 3 → Timeouts लगाओ ताकि ladder तेज़ी से आगे बढ़े
Step 4 → Response पर `fallback` reason mark करो
Step 5 → Fallback guess को कभी confident answer की तरह मत दिखाओ
Step 6 → हर fallback log करो; rate बढ़े तो alert
```

---

## 🟡 Real World Example
**Tariff Classification System**: Primary model times out, so we retry once, then try a backup model. If it fails too, we look up the product in the keyword index of common goods and return "Likely chapter 85 (electrical machinery), please confirm with a customs broker" marked `fallback: rule_based`. When confidence is below 0.5, the answer is "I need more details: material, intended use, and whether it is assembled." **Zomato-style**: if the recommendation LLM is down, show popular restaurants nearby (non-LLM fallback).

## 🟡 Real Example Hindi mein
**Tariff System**: Primary model timeout हो तो एक retry, फिर backup model। वह भी fail हो तो common goods की keyword index से "संभवतः chapter 85 (electrical machinery), कृपया customs broker से confirm करें" `fallback: rule_based` के साथ। Confidence 0.5 से कम हो तो "मुझे और details चाहिए: material, उपयोग, assembled है या नहीं।" **Zomato-style**: recommendation LLM down हो तो nearby popular restaurants दिखाओ।

---

## 💻 Code Example — Basic
```python
# Basic: fallback ladder with simple functions (pure Python, runs offline)
def primary(q: str) -> str:
    raise TimeoutError("primary model timed out")          # simulate an outage

def backup(q: str) -> str:
    raise ConnectionError("backup model unavailable")      # simulate a second failure

KEYWORDS = {"phone": "85 (electrical machinery)", "shirt": "62 (apparel)"}   # tiny rule table

def rules(q: str) -> str | None:
    for word, chapter in KEYWORDS.items():                 # search known keywords
        if word in q.lower():
            return f"Likely chapter {chapter}. Please confirm with a customs broker."
    return None                                            # nothing matched

def answer(q: str) -> dict:
    for name, fn in [("primary", primary), ("backup", backup)]:   # try models in order
        try:
            return {"text": fn(q), "fallback": None}       # success, no fallback
        except Exception as e:                             # any failure moves to next rung
            print(f"{name} failed: {e}")
    rule = rules(q)                                        # rule-based rung
    if rule:
        return {"text": rule, "fallback": "rule_based"}
    return {"text": "I could not classify this. Please share material and use.", "fallback": "ask_user"}

print(answer("smart phone cover"))                         # falls to rule-based
print(answer("unknown widget"))                            # falls to ask_user
```

## 💻 Code Example — Advanced
```python
# Production: async fallback ladder with timeouts, retries and structured reasons
import asyncio                                             # timeouts and sleep
from dataclasses import dataclass                          # result type
from typing import Awaitable, Callable, Optional           # type hints
from openai import AsyncOpenAI                             # client

client = AsyncOpenAI()                                     # shared client

@dataclass
class Reply:
    text: str                                              # message for the user
    fallback: Optional[str] = None                         # None = normal path
    confidence: Optional[float] = None                     # carry confidence if known

async def call_model(model: str, q: str, timeout: float) -> str:
    async def _go() -> str:
        r = await client.chat.completions.create(
            model=model, max_tokens=200,
            messages=[{"role": "user", "content": q}],
        )
        return r.choices[0].message.content or ""
    return await asyncio.wait_for(_go(), timeout=timeout)  # raises TimeoutError when slow

async def with_retry(fn: Callable[[], Awaitable[str]], tries: int = 2) -> str:
    last: Exception | None = None
    for i in range(tries):
        try:
            return await fn()                              # success
        except Exception as e:                             # transient error
            last = e
            await asyncio.sleep(0.3 * (2 ** i))            # exponential backoff
    raise last or RuntimeError("retry failed")

async def answer(q: str, confidence: float | None = None) -> Reply:
    if confidence is not None and confidence < 0.5:
        return Reply("I need more details (material, use, whether assembled) to classify this.",
                     "low_confidence", confidence)          # honest low-confidence reply
    for model, to in (("gpt-4o-mini", 8.0), ("gpt-4o", 15.0)):   # primary then backup
        try:
            return Reply(await with_retry(lambda m=model, t=to: call_model(m, q, t)),
                         None if model == "gpt-4o-mini" else "backup_model", confidence)
        except Exception:
            continue                                       # next rung
    rule = rules(q)                                        # non-LLM rung (from basic example)
    if rule:
        return Reply(rule, "rule_based")
    return Reply("The service is busy. Your request was saved and an expert will respond.", "human_handoff")
```

---

## 🟠 FastAPI Integration
Return 200 with a `fallback` field for degraded answers, and use 503 only when you truly cannot help. Add a global exception handler as the last rung.

```python
from fastapi import FastAPI, Request                       # framework
from fastapi.responses import JSONResponse                 # custom response
from pydantic import BaseModel                             # schema

app = FastAPI()

class Q(BaseModel):
    question: str                                          # user text

@app.post("/classify")
async def classify(body: Q) -> dict:
    reply = await answer(body.question)                    # ladder from advanced example
    return {"text": reply.text, "fallback": reply.fallback}   # UI shows a banner when fallback is set

@app.exception_handler(Exception)
async def last_resort(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=503,
        content={"text": "Something went wrong. Please try again shortly.", "fallback": "system_error"})
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has `Runnable.with_fallbacks([...])` that tries alternatives when the first raises. In LangGraph, model failures and low confidence become conditional edges to fallback nodes.

```python
from langchain_openai import ChatOpenAI                    # chat models

primary = ChatOpenAI(model="gpt-4o-mini", timeout=8, max_retries=1)   # fast model
backup = ChatOpenAI(model="gpt-4o", timeout=15, max_retries=1)        # stronger backup
llm = primary.with_fallbacks([backup])                     # auto-switch on exceptions
result = await llm.ainvoke("HS code for a laptop?")        # tries primary, then backup
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Guessing instead of admitting uncertainty
```python
# Wrong — low confidence but still returns the code as fact
return {"hs_code": code}

# Correct — mark it and ask for more info
return {"message": "Not sure; need more details", "fallback": "low_confidence"}
```

❌ Mistake 2: Retrying forever
```python
# Wrong — while True: retry; hangs the user and hammers the provider
# Correct — bounded retries with backoff and timeouts, then the next rung
```

❌ Mistake 3: Returning raw exceptions
```python
# Wrong — "openai.RateLimitError: ..." shown to users, may leak internals
# Correct — friendly message + internal logging with request id
```

---

## 🧠 Tricky Interview Question
**Q**: "Your primary provider has a regional outage. Failover to the backup model works, but answers now differ in format and quality. How do you design for this?"

**Answer**: Treat the backup as a first-class path: keep prompts and output schemas model-agnostic (JSON schema validation), run the backup on a regular evaluation set so you know its quality, and test failover in staging (chaos drills). Use a circuit breaker so you stop calling the failing provider quickly and resume with half-open probes. Mark answers from the backup (`fallback: backup_model`) and apply stricter confidence thresholds on it. Watch for rate limits on the backup, since traffic suddenly doubles.

---

## ⚫ Interview Questions + Answers

Q1: What is a fallback response?
A1: A safe alternative reply or path used when the normal LLM path fails or cannot be trusted.

Q2: Give three fallback types.
A2: Backup model, cached/rule-based answer, and an honest "need more info" or human handoff.

Q3: What is a circuit breaker?
A3: A pattern that stops calling a failing dependency after repeated errors for a cooling period, then probes it again, so failures are fast and do not pile up.

Q4: Should a fallback be hidden from the user?
A4: No. Be transparent where accuracy matters; mark degraded answers and offer next steps.

Q5: (Hard) Design fallbacks for a multi-step LangGraph agent.
A5: Per-node timeouts and retries; node-level fallbacks (cheaper tool, cached result); a graph-level error edge to a "safe summary" node that returns partial results with what failed; checkpointing so retries resume instead of restarting; budget guards (max steps, max tokens); and metrics per fallback reason.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production LLM feature (always)
- High-risk domains where a wrong answer is worse than no answer

❌ Avoid when:
- Fallback would hide real bugs: always log and alert on rates
- A generic fallback gives the false impression the task is done

---

## 📊 Visual Diagram
```
 request
    │
    ▼
 primary model ──ok──► answer
    │ fail/timeout
    ▼
 retry (backoff) ──ok──► answer
    │ fail
    ▼
 backup model ──ok──► answer (fallback: backup_model)
    │ fail
    ▼
 cache / rules ──ok──► answer (fallback: rule_based)
    │ none
    ▼
 "need more info" / human handoff
```

---

## 💰 Cost Impact
- Retries and backup calls add tokens: a failed-then-retried request may cost 2x. Cap retries (1-2) and use timeouts so you do not pay for hung requests.
- Backup models may be pricier (illustratively 10-30x for a flagship vs a mini model), so route only failures to them and watch the fallback rate.
- Non-LLM fallbacks (rules, cache) cost almost nothing and protect the budget during incidents.
- Token usage: a canned fallback uses 0 tokens.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fallback | Backup behaviour on failure | failure पर वैकल्पिक व्यवहार |
| Circuit breaker | Stop calling a failing service | failing service पर calls रोकना |
| Backoff | Increasing wait between retries | retries के बीच बढ़ती प्रतीक्षा |
| Timeout | Max wait time | अधिकतम प्रतीक्षा समय |
| Degraded mode | Reduced but working service | सीमित पर चालू सेवा |
| Handoff | Pass to a human | human को सौंपना |

---

## ⚡ 3-Line Summary
English: Fallbacks give safe, honest replies when the normal path fails or is unsure. Use a ladder: retry, backup model, cache or rules, ask for details, human. Always mark and log fallbacks and never present guesses as facts.
Hindi: Fallbacks तब सुरक्षित, ईमानदार जवाब देते हैं जब normal रास्ता fail या अनिश्चित हो। Ladder बनाओ: retry, backup model, cache या rules, और details माँगना, human। Fallback हमेशा mark और log करो और अंदाज़े को तथ्य की तरह मत दिखाओ।

---

## ➡️ Next Topic
**479. Content Filtering** — blocking harmful, unsafe or policy-violating text on input and output.
