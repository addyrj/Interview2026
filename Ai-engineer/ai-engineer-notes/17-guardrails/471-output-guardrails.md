---

# 471. Output Guardrails
# हिंदी में: Output Guardrails

---

## 🔵 Simple Definition (English)
Output guardrails inspect the model's response before it reaches the user or a downstream system. They check format and schema, leaked secrets or PII, toxicity, policy violations, groundedness and length, then allow, repair, redact, retry or block.

## 🔵 सरल परिभाषा (Hindi)
Output guardrails model के response को user या अगले system तक पहुँचने से पहले जाँचते हैं। वे format और schema, leak हुए secrets या PII, toxicity, policy violations, groundedness और length देखते हैं, फिर allow, repair, redact, retry या block करते हैं।

---

## 🔴 Problem it Solves
Even with good input checks and prompts, a model can emit a malformed JSON that crashes your parser, include a customer's phone number, invent a legal claim or output an API key it saw in context. The output layer is the last line of defence.

## 🔴 यह क्यों बना? (Hindi)
अच्छे input checks और prompts के बावजूद model टूटा हुआ JSON दे सकता है जो आपका parser crash कर दे, किसी customer का फोन नंबर शामिल कर सकता है, कानूनी दावा गढ़ सकता है या context में देखी API key output कर सकता है। Output layer सुरक्षा की आखिरी दीवार है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Receive raw model output (and the context used)
Step 2 → Structure: parse JSON, validate schema (pydantic)
Step 3 → Secrets / PII scan -> redact
Step 4 → Toxicity / policy scan
Step 5 → Grounding check (claims vs sources) for risky intents
Step 6 → Decide: pass | repair (redact, trim) | retry (once) | block with safe message
Step 7 → Log decision; return final output
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Raw model output (और इस्तेमाल हुआ context) लो
Step 2 → Structure: JSON parse, schema validate (pydantic)
Step 3 → Secrets / PII scan -> redact
Step 4 → Toxicity / policy scan
Step 5 → जोखिम वाले intents के लिए grounding check (claims बनाम sources)
Step 6 → निर्णय: pass | repair (redact, trim) | retry (एक बार) | सुरक्षित message के साथ block
Step 7 → निर्णय log करो; final output लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: The model returns `{"hs_code":"6109.10","duty":"10%","note":"Contact John at 9876543210"}`. The output guard validates the schema, redacts the phone number from `note`, checks `hs_code` exists, and returns a clean object. If JSON is invalid, it retries once with the error; if still invalid it returns "needs human review".

**Zomato AI**: The bot's reply must never include another customer's address or an internal discount code.

## 🟡 Real Example Hindi mein
**Tariff System**: Model लौटाता है `{"hs_code":"6109.10","duty":"10%","note":"Contact John at 9876543210"}`। Output guard schema validate करता है, `note` से फोन नंबर redact करता है, `hs_code` की मौजूदगी जाँचता है और साफ object लौटाता है। JSON invalid हो तो error के साथ एक बार retry; फिर भी invalid तो "needs human review"।

**Zomato AI**: Bot के reply में किसी दूसरे customer का address या internal discount code कभी नहीं होना चाहिए।

---

## 💻 Code Example — Basic
```python
# Basic output guard - pure Python, runs directly
import json  # parse
import re  # regex

SECRET = re.compile(r"(sk-[A-Za-z0-9]{10,}|AKIA[0-9A-Z]{16})")  # API key shapes
PHONE = re.compile(r"\b\d{10}\b")  # 10-digit phone
VALID_CODES = {"6109.10", "8471.30"}  # known HS codes


def guard_output(raw: str) -> dict:
    try:
        data = json.loads(raw)  # must be JSON
    except json.JSONDecodeError:
        return {"status": "retry", "reason": "invalid json"}
    if data.get("hs_code") not in VALID_CODES:
        return {"status": "block", "reason": "unknown hs_code"}
    note = str(data.get("note", ""))
    note = SECRET.sub("[SECRET]", PHONE.sub("[PHONE]", note))  # redact
    data["note"] = note
    return {"status": "ok", "data": data}


print(guard_output('{"hs_code":"6109.10","note":"call 9876543210"}'))
print(guard_output('{"hs_code":"9999.99"}'))
print(guard_output("not json"))
```

## 💻 Code Example — Advanced
```python
# Production: output guard with retry loop, pydantic v2, async, safe fallback
import asyncio  # async runtime
import logging  # logs
import re  # regex
from typing import Awaitable, Callable, Optional  # types

from pydantic import BaseModel, Field, ValidationError  # pydantic v2

log = logging.getLogger("output_guard")
PII = re.compile(r"\b\d{10}\b|\b[\w.+-]+@[\w-]+\.[\w.]+\b")  # phone or email


class Answer(BaseModel):
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$")  # strict format
    duty_percent: float = Field(ge=0, le=100)  # sane range
    note: str = Field(default="", max_length=300)


async def guarded_generate(
    generate: Callable[[str], Awaitable[str]], prompt: str, retries: int = 1
) -> Optional[Answer]:
    feedback = ""
    for attempt in range(retries + 1):  # initial try + retries
        try:
            raw = await asyncio.wait_for(generate(prompt + feedback), timeout=30)
        except Exception as exc:  # API or timeout
            log.error("generate failed: %s", exc)
            return None
        try:
            ans = Answer.model_validate_json(raw)  # parse + validate
        except ValidationError as exc:
            feedback = f"\nYour last output was invalid: {exc.errors()[0]['msg']}. Return valid JSON."
            log.info("invalid output attempt=%d", attempt)
            continue  # retry with feedback
        ans.note = PII.sub("[REDACTED]", ans.note)  # repair: redact PII
        return ans
    return None  # caller shows safe message


async def fake_llm(prompt: str) -> str:
    return '{"hs_code":"6109.10","duty_percent":10,"note":"mail a@b.com"}'


if __name__ == "__main__":
    print(asyncio.run(guarded_generate(fake_llm, "Classify cotton t-shirt")))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException  # framework

app = FastAPI()


@app.get("/classify", response_model=Answer)  # response_model is itself an output guard
async def classify(q: str) -> Answer:
    ans = await guarded_generate(fake_llm, q)  # advanced function
    if ans is None:
        raise HTTPException(status_code=502, detail="Could not produce a safe answer")
    return ans  # FastAPI validates and filters fields again
```

---

## 🔗 LangChain / LangGraph Connection
Use `llm.with_structured_output(Answer)` for schema, and add a `RunnableLambda` after it for redaction. In LangGraph, add a `validate_output` node with conditional edges: `ok -> END`, `retry -> generate` (max 1), `fail -> human_review`.

```python
from langchain_core.runnables import RunnableLambda  # runnable


def redact(a: Answer) -> Answer:
    a.note = PII.sub("[REDACTED]", a.note)  # remove PII
    return a


# chain = prompt | llm.with_structured_output(Answer) | RunnableLambda(redact)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Parsing output with string slicing
✅ Correct: Use structured output and validation.

```python
# Wrong
code = text.split("HS:")[1][:7]
# Right
ans = Answer.model_validate_json(text)
```

❌ Mistake 2: Infinite retry loop
✅ Correct: Limit retries and have a safe fallback.

```python
# Wrong
while True:
    out = llm()
    if valid(out):
        break
# Right
for _ in range(2):
    ...
return fallback
```

---

## 🧠 Tricky Interview Question
**Q**: "You stream tokens to the user. How do output guardrails work when the user has already seen half the answer?"

**Answer**: Stream-time guards are hard: bad content may already be displayed. Options: buffer by sentence and release after checking, run lightweight checks on partial text (regex for secrets), or stream only for low-risk intents and use full buffering for risky ones. Accept slightly higher time-to-first-token for safety.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What do output guardrails check?
A1: Format, PII/secrets, toxicity, policy, and grounding.

Q2: [Easy] Why validate JSON?
A2: Malformed output breaks downstream code.

Q3: [Medium] Redact vs block?
A3: Redact when only a small part is bad and the rest is useful; block when the whole answer is unsafe or unreliable.

Q4: [Medium] Why is `response_model` in FastAPI useful?
A4: It validates and filters the response fields so extra internal fields never leave the API.

Q5: [Hard] How do you guard streaming output?
A5: Sentence-level buffering with fast checks, a rolling window for secret patterns, abort the stream on violation with a replacement message, and full checks before persisting.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Output goes to users or other systems
- Outputs may contain private data

❌ Avoid heavy guards when:
- Internal drafts reviewed by a human anyway

---

## 📊 Visual Diagram
```
LLM raw output
   │
   ├─► schema valid? ──no──► retry once ─► fallback
   ├─► secrets/PII?  ──yes─► redact
   ├─► toxic/policy? ──yes─► block
   └─► grounded?     ──no──► warn / human
   │ all ok
   ▼
 User / downstream system
```

---

## 💰 Cost Impact
Schema and regex checks are free. A retry doubles tokens for that request (prompt + new output, plus error text). If 3% of requests retry, cost rises about 3%. An LLM judge on output adds ~300 tokens (about $0.00005 on gpt-4o-mini). Optimise: native structured output to cut retries, cheap checks first, judge only risky intents, and set `max_tokens` so outputs stay short.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Output guard | Check before delivery | भेजने से पहले जाँच |
| Redaction | Mask sensitive parts | संवेदनशील भाग छुपाना |
| Schema validation | Check structure | ढाँचे की जाँच |
| Fallback | Safe default reply | सुरक्षित डिफ़ॉल्ट जवाब |
| Retry with feedback | Re-ask using error | error बताकर दोबारा पूछना |
| response_model | FastAPI output schema | FastAPI का output schema |

---

## ⚡ 3-Line Summary
English: Output guardrails validate structure, redact PII and secrets, and check policy and grounding before delivery. Retry once with feedback, then fall back safely. They are the last line of defence.
Hindi: Output guardrails delivery से पहले structure validate करते हैं, PII और secrets redact करते हैं, और policy व grounding जाँचते हैं। एक बार feedback के साथ retry करो, फिर सुरक्षित fallback। यह सुरक्षा की आखिरी दीवार है।

---

## ➡️ Next Topic
**472. PII Detection + Redaction** - the most common output and input check, in depth.
