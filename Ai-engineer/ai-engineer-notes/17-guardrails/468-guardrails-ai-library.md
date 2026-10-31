---

# 468. Guardrails AI Library
# हिंदी में: Guardrails AI Library

---

## 🔵 Simple Definition (English)
`guardrails-ai` is an open-source Python library that wraps LLM calls with validators. A `Guard` checks inputs or outputs (valid JSON, no PII, no toxic words, regex match) and can reask the model, fix, filter or raise an exception when a validator fails. Many validators come from the Guardrails Hub.

## 🔵 सरल परिभाषा (Hindi)
`guardrails-ai` एक open-source Python library है जो LLM calls को validators से घेरती है। `Guard` inputs या outputs जाँचता है (valid JSON, PII नहीं, toxic शब्द नहीं, regex match) और validator fail होने पर model से दोबारा पूछ सकता है, ठीक कर सकता है, filter कर सकता है या exception raise कर सकता है। कई validators Guardrails Hub से आते हैं।

---

## 🔴 Problem it Solves
Teams hand-write the same checks again and again: parse JSON, retry on bad format, validate ranges. A library gives a tested, reusable structure for validation, retries (reask) and on-fail policies.

## 🔴 यह क्यों बना? (Hindi)
Teams वही checks बार-बार हाथ से लिखती हैं: JSON parse, bad format पर retry, ranges validate। Library validation, retries (reask) और on-fail policies के लिए tested, reusable structure देती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install guardrails-ai
Step 2 → (optional) guardrails hub install hub://guardrails/regex_match etc.
Step 3 → Define a Pydantic model for the structured output
Step 4 → Guard.for_pydantic(Model)  or  Guard().use(Validator(..., on_fail=...))
Step 5 → Call guard(llm_api, ...) or guard.parse(llm_output)
Step 6 → Validators run; on_fail = exception | fix | reask | filter | noop
Step 7 → Result: validated_output, validation_passed, raw_llm_output
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → pip install guardrails-ai
Step 2 → (optional) guardrails hub install hub://guardrails/regex_match आदि
Step 3 → Structured output के लिए Pydantic model बनाओ
Step 4 → Guard.for_pydantic(Model)  या  Guard().use(Validator(..., on_fail=...))
Step 5 → guard(llm_api, ...) या guard.parse(llm_output) चलाओ
Step 6 → Validators चलते हैं; on_fail = exception | fix | reask | filter | noop
Step 7 → Result: validated_output, validation_passed, raw_llm_output
```

---

## 🟡 Real World Example
**Tariff Classification System**: Output must be `{hs_code: "dddd.dd", confidence: 0..1}`. A regex validator enforces the HS format; a range validator enforces confidence between 0 and 1. If the model returns "61.09", the guard reasks once with an error message. If it still fails, an exception goes to the fallback (human review).

**Zomato AI**: A review-summary guard blocks profanity and checks that summaries are under 200 characters.

## 🟡 Real Example Hindi mein
**Tariff System**: Output `{hs_code: "dddd.dd", confidence: 0..1}` होना चाहिए। Regex validator HS format लागू करता है; range validator confidence 0 से 1 के बीच रखता है। Model "61.09" लौटाए तो guard error message के साथ एक बार reask करता है। फिर भी fail हो तो exception fallback (human review) को जाता है।

**Zomato AI**: Review-summary guard गाली-गलौज block करता है और जाँचता है कि summary 200 अक्षरों से कम हो।

---

## 💻 Code Example — Basic
```python
# Basic: the idea behind Guard, implemented in pure Python so it runs without installs.
# The real library API is shown in the Advanced block.
import json  # parse output
import re  # regex validator
from typing import Callable  # types


class SimpleGuard:
    """Tiny Guard clone: run validators, then apply on_fail policy."""

    def __init__(self, on_fail: str = "exception") -> None:
        self.validators: list[Callable[[dict], str | None]] = []  # each returns error or None
        self.on_fail = on_fail  # policy

    def use(self, v: Callable[[dict], str | None]) -> "SimpleGuard":
        self.validators.append(v)  # register validator
        return self

    def parse(self, raw: str) -> dict:
        data = json.loads(raw)  # may raise ValueError on bad JSON
        for v in self.validators:  # run each validator
            err = v(data)
            if err and self.on_fail == "exception":
                raise ValueError(err)  # strict mode
        return data


hs_format = lambda d: None if re.fullmatch(r"\d{4}\.\d{2}", d.get("hs_code", "")) else "bad hs_code"
conf_range = lambda d: None if 0 <= d.get("confidence", -1) <= 1 else "bad confidence"

guard = SimpleGuard().use(hs_format).use(conf_range)
print(guard.parse('{"hs_code": "6109.10", "confidence": 0.9}'))  # passes
try:
    guard.parse('{"hs_code": "61.09", "confidence": 0.9}')  # fails
except ValueError as e:
    print("blocked:", e)
```

## 💻 Code Example — Advanced
```python
# Production: real guardrails-ai usage (pip install guardrails-ai). Hub validators need
# "guardrails hub install hub://guardrails/regex_match" and a free API token setup.
# Not executed in these notes (needs install); syntax-checked only.
import asyncio  # async runtime
import logging  # logs
from typing import Optional  # types

from guardrails import Guard  # core class
from pydantic import BaseModel, Field  # pydantic models

log = logging.getLogger("guards")


class Classification(BaseModel):
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$", description="HS code like 6109.10")
    confidence: float = Field(ge=0.0, le=1.0, description="0 to 1")
    reason: Optional[str] = Field(default=None, max_length=300)


guard = Guard.for_pydantic(output_class=Classification)  # schema-based validation


def validate_text(raw_llm_output: str) -> Optional[Classification]:
    """Validate an already-produced model output."""
    try:
        outcome = guard.parse(raw_llm_output)  # runs validators
    except Exception as exc:  # parse or validation failure
        log.warning("guard failed: %s", exc)
        return None  # caller falls back to human review
    if not outcome.validation_passed:  # explicit flag
        return None
    return Classification(**outcome.validated_output)  # typed result


async def classify(description: str) -> Optional[Classification]:
    # Calling the model through the guard enables automatic reask on failure.
    # litellm-style model names are supported by Guardrails.
    try:
        result = await asyncio.to_thread(  # run sync API in a thread
            guard,
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Classify: {description}. Reply JSON."}],
            num_reasks=1,  # one retry with error feedback
        )
    except Exception as exc:
        log.error("llm/guard error: %s", exc)
        return None
    return Classification(**result.validated_output) if result.validation_passed else None
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # request

app = FastAPI()


class Req(BaseModel):
    description: str  # product text


@app.post("/classify")
async def classify_route(body: Req) -> dict[str, object]:
    result = await classify(body.description)  # guarded call from advanced example
    if result is None:
        raise HTTPException(status_code=422, detail="Could not produce a valid classification")
    return result.model_dump()  # validated and typed
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has its own structured output (`with_structured_output`) and `OutputFixingParser`-style retries. Guardrails AI can be used as a node: call `guard.parse(...)` on the LLM text inside a LangGraph node and route to `retry` or `human` depending on `validation_passed`. Use Guardrails when you want Hub validators (PII, toxicity, competitor check) rather than only schema validation.

```python
def guard_node(state: dict) -> dict:
    outcome = guard.parse(state["llm_text"])  # validate
    return {"valid": outcome.validation_passed, "data": outcome.validated_output}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `on_fail="noop"` and ignoring the flag
✅ Correct: Always check `validation_passed`.

```python
# Wrong
data = guard.parse(text).validated_output
# Right
o = guard.parse(text)
if not o.validation_passed:
    handle_failure()
```

❌ Mistake 2: Unlimited reasks
✅ Correct: Cap reasks (`num_reasks=1`) to avoid token and latency blow-up.

```python
# Wrong
guard(model=..., num_reasks=10)
# Right
guard(model=..., num_reasks=1)
```

---

## 🧠 Tricky Interview Question
**Q**: "Guard reask makes accuracy better but your bill grows 40%. Why, and what next?"

**Answer**: Each reask repeats the prompt plus the invalid output plus the error message, so tokens roughly double for failing requests. Reduce failures at the source: simpler schema, JSON mode or `with_structured_output`, few-shot example, lower temperature. Keep reask for rare cases and limit to one.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does a Guard do?
A1: Runs validators on LLM input or output and applies an on-fail action.

Q2: [Easy] Name two on_fail actions.
A2: exception, reask (also fix, filter, noop).

Q3: [Medium] Guardrails AI vs Pydantic alone?
A3: Pydantic validates structure and types. Guardrails adds reusable semantic validators (PII, toxicity, regex, competitor mentions), reask loops and a hub of ready checks.

Q4: [Medium] What is the Guardrails Hub?
A4: A registry of installable validators, e.g. regex match, detect PII, toxic language.

Q5: [Hard] How would you use it in a latency-sensitive service?
A5: Use cheap validators only (regex, schema), run LLM-based validators asynchronously or on a sample, set `num_reasks` to 0 or 1, set timeouts, and fail to a safe default.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need structured output with retries
- You want ready-made validators

❌ Avoid when:
- Native structured outputs already solve your need
- You want zero extra dependencies

---

## 📊 Visual Diagram
```
Prompt ─► LLM ─► raw output ─► [Guard: validator 1 → 2 → 3]
                                   │pass              │fail
                              validated_output   on_fail: reask ─► LLM (1x)
                                                  fix / filter / exception
```

---

## 💰 Cost Impact
Validators themselves are mostly free (regex, schema). Reasks cost extra tokens: a 600-token call that reasks once becomes roughly 1,300 tokens (prompt + bad output + error + new output), about $0.0002 instead of $0.0001 on gpt-4o-mini. If 5% of calls reask, total cost rises about 5%. Optimise with clear schemas, structured outputs and `num_reasks=1`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Guard | Validation wrapper | validation का wrapper |
| Validator | One check | एक जाँच |
| on_fail | Action on failure | fail पर कार्रवाई |
| Reask | Ask model again with error | error के साथ दोबारा पूछना |
| Hub | Validator registry | validators का भंडार |
| validated_output | Clean result | जाँचा हुआ नतीजा |

---

## ⚡ 3-Line Summary
English: Guardrails AI wraps LLM calls with validators and policies like reask, fix and exception. Use Pydantic schemas plus Hub validators. Cap reasks to control cost.
Hindi: Guardrails AI LLM calls को validators और reask, fix, exception जैसी policies से घेरती है। Pydantic schemas और Hub validators use करो। लागत नियंत्रित रखने के लिए reasks सीमित करो।

---

## ➡️ Next Topic
**469. NeMo Guardrails** - NVIDIA's toolkit that controls conversation flow with a dedicated language (Colang).
