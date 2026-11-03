---

# 576. Build Structured Output API
# हिंदी में: Structured Output API बनाओ

---

## 🔵 Simple Definition (English)
A Structured Output API is an endpoint that always returns data in a fixed, validated shape (JSON that matches a schema), even though an LLM wrote it. The LLM's free text is parsed, validated, and retried if wrong, so the caller can trust the fields.

## 🔵 सरल परिभाषा (Hindi)
Structured Output API ऐसा endpoint है जो हमेशा fixed और validated shape में data लौटाता है (schema से match करने वाला JSON), भले ही उसे LLM ने लिखा हो। LLM का free text parse और validate होता है, गलत हो तो retry होता है, ताकि caller fields पर भरोसा कर सके।

---

## 🔴 Problem it Solves
LLMs return text. Text may have markdown fences, extra sentences, missing keys, or wrong types ("confidence": "high"). A downstream service doing `result["hs_code"]` then crashes in production. Before structured outputs, teams used regex and hope. We need a contract between the LLM and the rest of the system.

## 🔴 यह क्यों बना? (Hindi)
LLM text लौटाता है। उसमें markdown fences, extra sentences, missing keys या गलत types हो सकते हैं। Downstream service `result["hs_code"]` करे तो production में crash होती है। पहले लोग regex और उम्मीद पर चलते थे। LLM और बाकी system के बीच एक contract चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define a schema (Pydantic model / JSON Schema)
Step 2 → Send prompt + schema to the LLM (provider structured-output / tool-call feature)
Step 3 → Receive raw text (may be messy)
Step 4 → Extract JSON (strip fences, find braces)
Step 5 → Validate against schema (types, ranges, patterns)
Step 6 → If invalid: feed the error back and retry (bounded, e.g. 3 times)
Step 7 → Return typed object or a clear 502 error
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Schema define करो (Pydantic model / JSON Schema)
Step 2 → Prompt + schema LLM को भेजो (provider की structured-output / tool-call सुविधा)
Step 3 → Raw text मिलता है (गंदा हो सकता है)
Step 4 → JSON निकालो (fences हटाओ, braces ढूँढो)
Step 5 → Schema से validate करो (types, ranges, pattern)
Step 6 → Invalid हो तो error वापस prompt में डालकर retry करो (सीमित, जैसे 3 बार)
Step 7 → Typed object लौटाओ या साफ़ 502 error दो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs officer posts "Apple iPhone 15, 128GB". The API must return `{"hs_code": "8517.13", "description": "Smartphone", "confidence": 0.93}`. The billing service later stores `hs_code` in a database column with format `NNNN.NN`. If the LLM answers `85171` the validator rejects it and the retry prompt says why.

**Zomato-style**: An order-parsing API turns "2 paneer tikka, no onion" into `{"items": [{"name": "paneer tikka", "qty": 2, "notes": "no onion"}]}` for the kitchen system.

## 🟡 Real Example Hindi mein
**Tariff System**: Officer "Apple iPhone 15, 128GB" भेजता है। API को `{"hs_code": "8517.13", ...}` लौटाना है। Billing service `hs_code` को `NNNN.NN` format में DB में रखती है। LLM `85171` दे तो validator reject करता है और retry prompt में कारण बताया जाता है।

**Zomato-style**: Order-parsing API "2 paneer tikka, no onion" को kitchen system के लिए structured JSON में बदलती है।

---

## 💻 Code Example — Basic
Full runnable file: `main.py` (offline, mocked LLM). Observed output when I ran it: attempt 1 rejected `'85171'`, retry returned a valid `TariffResult`.

```python
import json  # parse JSON text
import re  # regex for the HS code pattern

raw = '{"hs_code": "8517.13", "description": "Smartphone", "confidence": 0.93}'  # fake LLM output
data = json.loads(raw)  # text -> dict (raises ValueError if broken)

if not re.match(r"^\d{4}\.\d{2}$", data["hs_code"]):  # check the HS code format
    raise ValueError("bad hs_code")  # reject wrong format
if not 0 <= data["confidence"] <= 1:  # check the range
    raise ValueError("bad confidence")  # reject out-of-range value

print(data["hs_code"])  # safe to use now
```

## 💻 Code Example — Advanced
Uses Pydantic v2 (needs `pip install pydantic`; not run here, so treat as reference). The tested stdlib version is in `main.py`.

```python
from __future__ import annotations

import asyncio  # async retry loop
from typing import Awaitable, Callable  # type hints

from pydantic import BaseModel, Field, ValidationError  # validation library


class TariffResult(BaseModel):
    """Schema = contract with the LLM."""

    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$")  # format NNNN.NN
    description: str = Field(min_length=1)  # non-empty text
    confidence: float = Field(ge=0, le=1)  # between 0 and 1


class StructuredOutputError(Exception):
    """Raised after all retries fail."""


async def classify(
    product: str,
    llm: Callable[[str], Awaitable[str]],  # any async function returning text
    max_retries: int = 3,  # bounded retries
) -> TariffResult:
    prompt = f"Return JSON for HS classification of: {product}"  # base prompt
    error = ""  # last error text
    for _ in range(max_retries):  # try a few times
        raw = await llm(prompt)  # call the model
        try:
            return TariffResult.model_validate_json(raw)  # parse + validate in one step
        except ValidationError as exc:  # schema failed
            error = exc.errors()[0]["msg"]  # first problem, short
            prompt += f"\nInvalid output: {error}. Return only valid JSON."  # tell the model
    raise StructuredOutputError(error)  # give up cleanly
```

---

## 🟠 FastAPI Integration
FastAPI already uses Pydantic, so `response_model` guarantees the response shape even if your code returns extra keys. Map exhaustion of retries to HTTP 502 (upstream model problem), not 500.

```python
from fastapi import FastAPI, HTTPException  # web framework
from pydantic import BaseModel  # request model

app = FastAPI()  # app instance


class ClassifyRequest(BaseModel):
    product: str  # product text from the officer


@app.post("/classify", response_model=TariffResult)  # output is validated again by FastAPI
async def classify_route(req: ClassifyRequest) -> TariffResult:
    try:
        return await classify(req.product, llm=my_llm)  # my_llm: your async LLM wrapper
    except StructuredOutputError as exc:  # model never produced valid data
        raise HTTPException(status_code=502, detail=str(exc))  # upstream failure
```

---

## 🔗 LangChain / LangGraph Connection
LangChain chat models expose `with_structured_output(Schema)`, which uses the provider's native tool-calling or JSON mode and returns a Pydantic object. In LangGraph, put this in a node so every node passes typed state.

```python
from langchain_openai import ChatOpenAI  # needs an API key to run

llm = ChatOpenAI(model="gpt-4o-mini")  # any chat model that supports tools
structured_llm = llm.with_structured_output(TariffResult)  # returns TariffResult objects
result = structured_llm.invoke("Classify: Apple iPhone 15")  # sync call
# result.hs_code is a validated str; use ainvoke(...) for async
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trusting `json.loads` without validating
✅ Correct: validate types, ranges and patterns too.

```python
# Wrong: valid JSON, but confidence can be 1.4 or "high"
data = json.loads(raw)
save(data["hs_code"], data["confidence"])

# Right: validate after parsing
result = TariffResult.model_validate_json(raw)  # raises ValidationError on bad data
save(result.hs_code, result.confidence)
```

❌ Mistake 2: Unlimited retries
✅ Correct: cap retries and return 502, otherwise one bad prompt burns money forever.

```python
# Wrong
while True:
    raw = await llm(prompt)

# Right
for _ in range(3):  # bounded
    raw = await llm(prompt)
```

---

## 🧠 Tricky Interview Question
**Q**: "You use native structured output (constrained decoding), so the JSON is always schema-valid. Do you still need validation code?"

**Answer**: Yes. Constrained decoding guarantees syntax and (mostly) types, but not business meaning. The model can return `hs_code: "9999.99"` which matches the pattern but does not exist in the tariff table. Refusals and truncated output (hit `max_tokens`) can also break the shape. So: schema for shape, then semantic checks (lookup in the real table), then retry or fallback. Also note provider schema subsets differ, so some constraints like `pattern` may not be enforced by the provider.

---

## ⚫ Interview Questions + Answers

Q1: Why not just ask the LLM "reply in JSON" in the prompt?
A1: Prompts are suggestions, not guarantees. Models add prose or fences and sometimes drop fields. You need parsing and validation, and ideally provider-level structured output.

Q2: What is a schema in this context?
A2: A formal description of fields, types and constraints, written as a Pydantic model or JSON Schema. It is sent to the LLM and also used to validate the reply.

Q3: How do you design the retry loop?
A3: Bounded attempts (2-3), feed the exact validation error back to the model, keep temperature low, log each failure, and raise a typed error at the end so the API can return 502 or a fallback.

Q4: Native structured output vs prompt + validate: trade-offs?
A4: Native (tool-calling / constrained decoding) gives far fewer failures and fewer retries, but ties you to provider features and schema subsets. Prompt + validate works with any model but costs more retries. Best: native when available, plus validation anyway.

Q5 (Hard): How do you evolve the schema without breaking clients?
A5: Version the schema (`/v2/classify`), add only optional fields with defaults, never change meaning of existing fields, and keep a contract test suite with recorded LLM outputs. Pin the prompt version with the schema, because a prompt change can change output distribution even if the schema is the same.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Output feeds code, a database or another service
- Extraction tasks (entities, forms, classification)
- Tool/function calling arguments

❌ Avoid when:
- The output is only shown to a human as prose (chat answer)
- Creative writing where rigid fields hurt quality
- Very deep, huge schemas that make the model slower and less accurate

---

## 📊 Visual Diagram
```
 Client ──POST /classify──▶ FastAPI
                              │
                              ▼
                    ┌──────────────────┐
                    │ prompt + schema  │
                    └────────┬─────────┘
                             ▼
                          [ LLM ]
                             │ raw text
                             ▼
                  extract_json ─▶ validate
                             │          │ invalid
                             │ valid    └──▶ add error to prompt ──┐
                             ▼                                     │
                      typed result  ◀───── retry (max 3) ◀─────────┘
                             │
                             ▼
                 200 JSON   or   502 error
```

---

## 💰 Cost Impact
Token usage: input = system prompt + schema + product text (roughly 150-400 tokens); output = the JSON (roughly 40-80 tokens). Every retry repeats the whole input plus the error message, so one retry about doubles the cost of that request. Prices change often; the figures below are illustrative only.

| Case | Input tokens | Output tokens | Relative cost |
|------|--------------|---------------|---------------|
| First-try success | 300 | 60 | 1x |
| One retry | 650 | 120 | ~2x |
| Three failures | 1000+ | 180 | ~3x+ |

Optimise: use native structured output (fewer retries), keep schemas small, short field names and descriptions, cap `max_tokens` (e.g. 150), use a small model first and escalate only on failure, and cache identical product strings.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Structured output | LLM reply in a fixed schema | निश्चित schema में LLM जवाब |
| Schema | Description of fields and types | Fields और types का विवरण |
| Pydantic | Python validation library | Python validation library |
| Constrained decoding | Decoder limited to valid tokens | सिर्फ valid tokens चुनने वाला decoding |
| Retry with feedback | Re-ask with the error | Error बताकर दोबारा पूछना |
| Contract test | Test that schema still holds | Schema सही है या नहीं जाँचने वाला test |

---

## ⚡ 3-Line Summary
English: Structured output turns messy LLM text into a validated, typed contract. Parse, validate, retry with the error, and cap retries. Native structured output reduces failures, but you still need semantic checks.
Hindi: Structured output गंदे LLM text को validated, typed contract में बदलता है। Parse करो, validate करो, error के साथ retry करो और retries सीमित रखो। Native structured output failures घटाता है, फिर भी semantic checks ज़रूरी हैं।

---

## ➡️ Next Topic
**577. Build Semantic Search** — now that outputs are reliable, we build the retrieval side: embed documents and find the closest meaning.
