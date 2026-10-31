---

# 090. Output Validation
# हिंदी में: Output Validation

---

## 🔵 Simple Definition (English)
Output validation is checking that an LLM's structured answer is acceptable before your system uses it. There are three layers: (1) syntax (is it valid JSON), (2) schema (right keys and types) and (3) semantics (is the value actually correct, e.g. the HS code exists and the duty is in range).

## 🔵 सरल परिभाषा (Hindi)
Output validation का मतलब है कि LLM का structured जवाब use करने से पहले check करना कि वह स्वीकार्य है। तीन layers हैं: (1) syntax (valid JSON है?), (2) schema (सही keys और types?) और (3) semantics (value सच में सही है? जैसे HS code मौजूद है और duty range में है)।

---

## 🔴 Problem it Solves
Structured output guarantees shape, not truth. An LLM may output `{"hs_code": "0000.00", "duty_percent": 9000}`: valid JSON, valid types, nonsense meaning. Without validation, bad data reaches databases, invoices and customers.

## 🔴 यह क्यों बना? (Hindi)
Structured output shape की guarantee देता है, सच की नहीं। LLM `{"hs_code": "0000.00", "duty_percent": 9000}` दे सकता है: valid JSON, valid types, पर बेतुका मतलब। Validation के बिना गलत data database, invoice और customers तक पहुँच जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Syntax check: json.loads (or SDK parse)
Step 2 → Schema check: Pydantic types, required, Literal/Enum
Step 3 → Field rules: ranges (ge/le), regex patterns, lengths
Step 4 → Cross-field rules: model_validator (e.g. confidence low -> needs_review True)
Step 5 → External checks: HS code exists in DB, currency is supported
Step 6 → Safety checks: no PII leakage, no prompt-injection text in fields
Step 7 → Decide: accept | retry | fallback | human review
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Syntax check: json.loads (या SDK parse)
Step 2 → Schema check: Pydantic types, required, Literal/Enum
Step 3 → Field rules: ranges (ge/le), regex patterns, lengths
Step 4 → Cross-field rules: model_validator (जैसे confidence कम -> needs_review True)
Step 5 → External checks: HS code DB में है?, currency supported है?
Step 6 → Safety checks: PII leak नहीं, fields में prompt-injection text नहीं
Step 7 → Decision: accept | retry | fallback | human review
```

---

## 🟡 Real World Example
**Tariff Classification System**: After the LLM returns a result, we check: code format `NNNN.NN`, code exists in the official tariff table, duty equals the table's duty (the LLM must not invent duties — we override it from the table), and confidence >= 0.7 else send to a human reviewer.

**Zomato-style**: A parsed order must have items that exist in the restaurant menu and a total that equals the sum of item prices.

## 🟡 Real Example Hindi mein
**Tariff System**: LLM के result के बाद हम check करते हैं: code format `NNNN.NN`, code official tariff table में है, duty table की duty के बराबर है (LLM duty invent नहीं करेगा — हम table से override करते हैं), और confidence >= 0.7 वरना human reviewer को भेजो।

**Zomato-style**: Parse किए गए order के items restaurant menu में होने चाहिए और total = items की कीमत का जोड़।

---

## 💻 Code Example — Basic
```python
# Basic: three layers of validation on a fake LLM reply. Needs: pip install pydantic
import json                                                       # syntax layer
from pydantic import BaseModel, Field, ValidationError, model_validator   # schema layer

TARIFF_TABLE: dict[str, float] = {"8518.30": 0.0, "8517.13": 0.0, "6403.99": 20.0}   # truth source

class TariffResult(BaseModel):
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$")               # format rule
    duty_percent: float = Field(ge=0, le=100)                     # range rule
    confidence: float = Field(ge=0, le=1)
    needs_review: bool = False                                    # set by us, not by LLM

    @model_validator(mode="after")                                # cross-field rule
    def flag_low_confidence(self) -> "TariffResult":
        if self.confidence < 0.7:                                 # low confidence
            self.needs_review = True                              # send to a human
        return self

def validate_reply(raw: str) -> TariffResult:
    """Run syntax -> schema -> semantic checks; raise on any failure."""
    data = json.loads(raw)                                        # layer 1: syntax
    result = TariffResult.model_validate(data)                    # layer 2: schema
    if result.hs_code not in TARIFF_TABLE:                        # layer 3: semantics
        raise ValueError(f"unknown HS code {result.hs_code}")
    result.duty_percent = TARIFF_TABLE[result.hs_code]            # override LLM duty with truth
    return result

replies = [
    '{"hs_code": "8518.30", "duty_percent": 5, "confidence": 0.95}',   # fine, duty fixed to 0
    '{"hs_code": "9999.99", "duty_percent": 5, "confidence": 0.95}',   # unknown code
    '{"hs_code": "8518.30", "duty_percent": 5, "confidence": 0.4}',    # low confidence
    '{"hs_code": "ABC", "duty_percent": 5, "confidence": 0.9}',        # bad format
    'not json',                                                        # syntax error
]
for r in replies:
    try:
        out = validate_reply(r)
        print("OK", out.hs_code, out.duty_percent, "review" if out.needs_review else "auto")
    except (json.JSONDecodeError, ValidationError, ValueError) as exc:
        print("REJECT:", type(exc).__name__)
```

## 💻 Code Example — Advanced
```python
# Production: async validator pipeline with DB lookup, result object and metrics.
import asyncio
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel, Field, ValidationError

class Verdict(str, Enum):                              # decision after validation
    ACCEPT = "accept"
    RETRY = "retry"
    REVIEW = "review"

class TariffResult(BaseModel):
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$")
    confidence: float = Field(ge=0, le=1)

@dataclass
class ValidationReport:                                # structured outcome
    verdict: Verdict
    errors: list[str] = field(default_factory=list)    # messages to feed back to the LLM

async def code_exists(code: str) -> bool:
    """Pretend async DB lookup (replace with real query)."""
    await asyncio.sleep(0)                             # yield control like real I/O
    return code in {"8518.30", "8517.13"}

async def validate(raw: dict) -> tuple[TariffResult | None, ValidationReport]:
    """Return parsed object (if any) and a report with a verdict."""
    try:
        result = TariffResult.model_validate(raw)      # schema layer
    except ValidationError as exc:                     # collect readable messages
        msgs = [f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors()]
        return None, ValidationReport(Verdict.RETRY, msgs)
    if not await code_exists(result.hs_code):          # semantic layer
        return None, ValidationReport(Verdict.RETRY, [f"{result.hs_code} not in tariff table"])
    if result.confidence < 0.7:                        # business layer
        return result, ValidationReport(Verdict.REVIEW, ["low confidence"])
    return result, ValidationReport(Verdict.ACCEPT)

async def main() -> None:
    for sample in [{"hs_code": "8518.30", "confidence": 0.9},
                   {"hs_code": "1234.56", "confidence": 0.9},
                   {"hs_code": "8518.30", "confidence": 0.5},
                   {"hs_code": "bad", "confidence": 2}]:
        _, report = await validate(sample)
        print(sample, "->", report.verdict.value, report.errors)

if __name__ == "__main__":
    asyncio.run(main())                                # runs offline
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/validate-llm")
async def validate_llm(payload: dict) -> dict:
    result, report = await validate(payload)           # reuse pipeline
    if report.verdict is Verdict.RETRY:
        raise HTTPException(status_code=422, detail=report.errors)   # 422 = unprocessable
    return {"verdict": report.verdict.value,
            "data": result.model_dump() if result else None}
```

---

## 🔗 LangChain / LangGraph Connection
```python
# LangGraph pattern: validate node + conditional edge
from langgraph.graph import StateGraph, END
from typing import TypedDict

class S(TypedDict):
    raw: dict
    verdict: str

async def validate_node(state: S) -> dict:
    _, report = await validate(state["raw"])           # reuse validator
    return {"verdict": report.verdict.value}

def route(state: S) -> str:
    return "classify" if state["verdict"] == "retry" else END   # loop back on retry

g = StateGraph(S)
g.add_node("validate", validate_node)
# g.add_node("classify", classify_node) ... then add_conditional_edges("validate", route)
# LangChain: RunnableLambda(fn) can wrap a validator inside an LCEL chain.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trusting LLM-provided facts (duty, price)
✅ Correct: Look facts up from your source of truth; use the LLM only to choose/extract.

```python
# Wrong: charge = result.duty_percent * value   # LLM's duty
# Right: charge = TARIFF_TABLE[result.hs_code] * value
```

❌ Mistake 2: Raising raw exceptions to the user
✅ Correct: Convert to a verdict (accept/retry/review) and a safe message.

```python
# Wrong: data = TariffResult(**raw)   # unhandled ValidationError -> 500
# Right: try/except -> ValidationReport(Verdict.RETRY, msgs)
```

---

## 🧠 Tricky Interview Question

**Q**: "Your validation rejects 15% of LLM outputs, mostly 'HS code not in table'. Is raising the retry limit the right fix?"

**Answer**: No. Retries treat the symptom. Investigate the cause: the table might be outdated, the prompt does not give valid options, or the product text is ambiguous. Better: retrieve candidate HS codes first (RAG) and restrict the output to those with an `Enum`/`Literal`, so invalid codes cannot be produced. Then validation failures become rare, and the retry budget stays small.

---

## ⚫ Interview Questions + Answers

Q1: What are the layers of output validation?
A1: Syntax, schema, semantics (and business/safety rules).

Q2: Why validate if I use strict structured output?
A2: Strict output guarantees shape only; values can still be wrong or unsafe.

Q3: What is a `model_validator`?
A3: A Pydantic v2 hook (`@model_validator(mode="after")`) to check rules involving several fields at once.

Q4: How do you give feedback to the LLM on a failure?
A4: Convert validation errors to short, precise messages and append them to the conversation (this is what Instructor does).

Q5: How do you measure validation quality in production?
A5: Track metrics: validation failure rate per rule, retry rate, review rate, final acceptance accuracy against labelled samples, and alert on drift after prompt/model changes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Output affects money, compliance or customers
- Values must match a database

❌ Avoid when:
- Throwaway prototypes (still add basic schema checks)
- Don't validate subjective text quality with brittle rules; use evals instead

---

## 📊 Visual Diagram
```
 LLM reply
   │
   ▼  1 syntax   ── fail ─┐
   ▼  2 schema   ── fail ─┤
   ▼  3 semantic ── fail ─┼─► RETRY (with error text)
   ▼  4 business ── low  ─┼─► HUMAN REVIEW
   ▼                      │
 ACCEPT ─► DB / invoice   │
```

---

## 💰 Cost Impact
Validation code is free, but failures trigger retries (each retry = another full call). A 10% failure rate with one retry adds roughly 10% to cost; multi-retry loops add more.
Optimise: constrain outputs with Enums, validate cheaply before expensive steps, override facts from the DB, and use a cheap model for retries only when needed.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Validation | Checking correctness | सही होने की जाँच |
| Semantic check | Value is meaningful/true | मतलब की जाँच |
| model_validator | Multi-field rule | कई fields का rule |
| Verdict | Accept / retry / review | फैसला |
| Source of truth | Trusted data (DB/table) | भरोसेमंद data |

---

## ⚡ 3-Line Summary
English: Validate in layers: syntax, schema, semantics and business rules. Never trust LLM facts; verify against your source of truth. Decide accept, retry or human review.
Hindi: Layers में validate करो: syntax, schema, semantics और business rules। LLM के facts पर भरोसा मत करो; अपने source of truth से जाँचो। फैसला: accept, retry या human review।

---

## ➡️ Next Topic
**091. Retry on Invalid Output** — designing safe, bounded retry loops with feedback and backoff.
