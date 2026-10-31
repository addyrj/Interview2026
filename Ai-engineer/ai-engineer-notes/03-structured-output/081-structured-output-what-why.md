---

# 081. Structured Output — What + Why
# हिंदी में: Structured Output — क्या है और क्यों ज़रूरी है

---

## 🔵 Simple Definition (English)
Structured output means the LLM returns data in a predefined, machine-readable shape (JSON that matches a schema) instead of free text. Providers now support this natively: the decoding process is constrained so that the output follows your JSON Schema. Your code receives typed objects, not strings to guess at.

## 🔵 सरल परिभाषा (Hindi)
Structured output का मतलब है कि LLM free text की जगह पहले से तय, machine-readable रूप में data लौटाए (JSON जो schema से मेल खाए)। Providers अब इसे natively support करते हैं: decoding को इस तरह सीमित किया जाता है कि output आपके JSON Schema का पालन करे। आपके code को typed objects मिलते हैं, अंदाज़ा लगाने वाली strings नहीं।

---

## 🔴 Problem it Solves
LLMs write prose. Software needs fields. Before structured output teams used regex, "please return JSON" prompts and retries (topic 063). Failure modes: missing keys, wrong types, extra commentary, invalid JSON, a made-up enum value. Each failure means a retry, an exception or a silent bug.

Structured output moves the guarantee from "the model usually follows the format" to "the format is enforced by the system".

## 🔴 यह क्यों बना? (Hindi)
LLM गद्य लिखते हैं। Software को fields चाहिए। Structured output से पहले teams regex, "please return JSON" prompts और retries इस्तेमाल करती थीं (topic 063)। Failure modes: missing keys, गलत types, अतिरिक्त टिप्पणी, invalid JSON, गढ़ी हुई enum value। हर failure का मतलब retry, exception या चुपचाप bug। Structured output गारंटी को "model आमतौर पर format मानता है" से "format system द्वारा लागू होता है" पर ले जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define the shape: a Pydantic model / JSON Schema (fields, types, enums, required)
Step 2 → Send the schema with the request (response_format / tool schema / output config)
Step 3 → Provider compiles the schema into a grammar
Step 4 → During generation, tokens that would break the grammar are masked out
Step 5 → Output is valid JSON matching the schema (syntax and structure)
Step 6 → Parse into a typed object (Pydantic)
Step 7 → STILL validate meaning: enum membership is guaranteed, but correctness is not
Step 8 → Handle refusals / truncation (max_tokens) explicitly

Ways to get structure:
  1) Prompting only (weakest)           2) JSON mode (valid JSON, no schema)
  3) Function/tool calling              4) Schema-enforced structured outputs (strongest)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Shape तय करो: Pydantic model / JSON Schema (fields, types, enums, required)
Step 2 → Request के साथ schema भेजो (response_format / tool schema / output config)
Step 3 → Provider schema को grammar में compile करता है
Step 4 → Generation के दौरान grammar तोड़ने वाले tokens mask कर दिए जाते हैं
Step 5 → Output valid JSON होता है जो schema से मेल खाता है (syntax और structure)
Step 6 → Typed object में parse करो (Pydantic)
Step 7 → अर्थ की validation फिर भी करो: enum membership की गारंटी है, पर सही होने की नहीं
Step 8 → Refusals / truncation (max_tokens) को साफ़ तौर पर संभालो

Structure पाने के तरीके:
  1) सिर्फ prompting (सबसे कमज़ोर)   2) JSON mode (valid JSON, schema नहीं)
  3) Function/tool calling           4) Schema-enforced structured outputs (सबसे मज़बूत)
```

---

## 🟡 Real World Example
**Tariff Classification System**: The model must return `{hs_code, confidence, needs_review, reasons[]}`. With schema enforcement, `needs_review` is always a boolean and `hs_code` is always a string; with an enum of valid headings, an invented code is impossible. The pipeline writes the object directly to the database and routes `needs_review=true` to humans. But the model can still choose the wrong valid heading, so confidence thresholds and eval tests remain.

**Zomato-style**: Order-intent extraction returns `{intent: "refund"|"status"|"complaint", order_id: string|null}` for routing.

## 🟡 Real Example Hindi mein
**Tariff System**: Model को `{hs_code, confidence, needs_review, reasons[]}` लौटाना है। Schema enforcement से `needs_review` हमेशा boolean और `hs_code` हमेशा string; valid headings के enum के साथ गढ़ा हुआ code असंभव है। Pipeline object सीधे database में लिखता है और `needs_review=true` को humans के पास भेजता है। पर model फिर भी गलत valid heading चुन सकता है, इसलिए confidence thresholds और eval tests ज़रूरी रहते हैं।

**Zomato-style**: Order-intent extraction routing के लिए `{intent: "refund"|"status"|"complaint", order_id: string|null}` लौटाता है।

---

## 💻 Code Example — Basic
```python
# Basic: define a schema with Pydantic v2 and validate a model reply (offline, needs: pip install pydantic)
import json                                              # parse JSON text
from typing import Literal                               # enum-like field
from pydantic import BaseModel, Field, ValidationError   # pydantic v2

class TariffResult(BaseModel):
    hs_code: Literal["8518.30", "8517.13", "3926.90"]    # only these values are allowed
    confidence: float = Field(ge=0, le=1)                # between 0 and 1
    needs_review: bool                                   # must be a boolean
    reasons: list[str] = Field(default_factory=list)     # list of strings

print(json.dumps(TariffResult.model_json_schema(), indent=1)[:300])   # the JSON Schema you send to the API

good = '{"hs_code": "8518.30", "confidence": 0.92, "needs_review": false, "reasons": ["worn on ear"]}'
bad = '{"hs_code": "0000.00", "confidence": 1.4, "needs_review": "no"}'

print(TariffResult.model_validate_json(good))            # works
try:
    TariffResult.model_validate_json(bad)                # raises: enum and range errors (pydantic lax mode accepts "no" as False)
except ValidationError as exc:
    print(exc.error_count(), "errors")                   # 2 errors
```

## 💻 Code Example — Advanced
```python
# Production: a provider-agnostic structured-output wrapper with validation, refusal handling,
# and repair retry (async). The provider call is injected, so this runs offline.
from __future__ import annotations

import asyncio                                           # async runner
import json                                              # parse
from typing import Awaitable, Callable, TypeVar         # generics

from pydantic import BaseModel, ValidationError          # pydantic v2

T = TypeVar("T", bound=BaseModel)                        # any Pydantic model type

class StructuredOutputError(RuntimeError):
    """Raised when we cannot get a valid object after retries."""

# (messages, json_schema) -> raw JSON text. Real code would use native structured outputs here.
Provider = Callable[[list[dict[str, str]], dict], Awaitable[str]]

async def structured(provider: Provider, schema_model: type[T], messages: list[dict[str, str]],
                     retries: int = 1) -> T:
    schema = schema_model.model_json_schema()                    # schema derived from the model
    msgs = list(messages)                                        # copy so we can append repairs
    last = ""
    for _ in range(retries + 1):
        try:
            raw = await provider(msgs, schema)                   # provider call
        except Exception as exc:                                 # network/API error
            raise StructuredOutputError(f"provider failed: {exc}") from exc
        try:
            return schema_model.model_validate(json.loads(raw))  # parse + validate
        except (json.JSONDecodeError, ValidationError) as exc:
            last = str(exc)[:300]                                # keep a short error
            msgs += [{"role": "assistant", "content": raw},
                     {"role": "user", "content": f"Output did not match the schema: {last}. Return corrected JSON."}]
    raise StructuredOutputError(f"invalid after retries: {last}")

class Item(BaseModel):
    hs_code: str
    confidence: float

async def _demo() -> None:
    calls = {"n": 0}
    async def provider(msgs: list[dict[str, str]], schema: dict) -> str:
        calls["n"] += 1
        return '{"hs_code": "8518.30"}' if calls["n"] == 1 else '{"hs_code": "8518.30", "confidence": 0.9}'
    print(await structured(provider, Item, [{"role": "user", "content": "earbuds"}]))

if __name__ == "__main__":
    asyncio.run(_demo())
```
Token usage: the schema is sent as part of the request (about 50-300 tokens, depending on size) and counts as input. Verbose field names and descriptions cost tokens on every call; keep them short but clear.

---

## 🟠 FastAPI Integration
FastAPI + Pydantic is a natural fit: the same model defines the LLM output schema and the API `response_model`. Using native structured outputs with the OpenAI SDK:

```python
from fastapi import FastAPI, HTTPException           # framework
from openai import AsyncOpenAI                       # openai>=1 (structured outputs via parse)
from pydantic import BaseModel                       # models

app = FastAPI()                                      # app
client = AsyncOpenAI()                               # client

class In(BaseModel):
    product: str                                     # request body

@app.post("/classify", response_model=TariffResult)  # TariffResult from the basic block
async def classify(body: In) -> TariffResult:
    completion = await client.beta.chat.completions.parse(   # SDK helper for schema-enforced output
        model="gpt-4o-mini", temperature=0, max_tokens=200,
        messages=[{"role": "system", "content": "Classify the product into an HS code."},
                  {"role": "user", "content": body.product}],
        response_format=TariffResult,                        # Pydantic class becomes the JSON Schema
    )
    msg = completion.choices[0].message
    if msg.refusal:                                          # the model refused for safety reasons
        raise HTTPException(status_code=422, detail="request refused")
    if msg.parsed is None:                                   # truncated or otherwise unparsed
        raise HTTPException(status_code=502, detail="no structured output")
    return msg.parsed                                        # already a TariffResult
```
(The `beta.chat.completions.parse` location may move to a stable path in newer SDK versions; check the installed SDK.)

---

## 🔗 LangChain / LangGraph Connection
`llm.with_structured_output(PydanticModel)` is the standard LangChain API; it uses the provider's native method when available (tool calling or JSON schema). In LangGraph, structured outputs make state updates predictable: a node returns a typed object that is stored in the state, and conditional edges read fields like `needs_review`.

```python
from typing import Literal                                # enum-like
from pydantic import BaseModel, Field                     # schema
from langchain_openai import ChatOpenAI                   # model

class Route(BaseModel):
    needs_review: bool = Field(description="True if confidence is low")
    hs_code: Literal["8518.30", "8517.13", "UNKNOWN"]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Route)
# route = await llm.ainvoke("HS code for earbuds?")   # returns a Route object
# LangGraph: add_conditional_edges("classify", lambda s: "human" if s["route"].needs_review else "end")
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assuming schema-valid means correct
✅ Correct: Structure is guaranteed; truth is not. Add validators and evals.
```python
# Wrong
db.save(result)             # trust it

# Right
if result.confidence < 0.7 or result.hs_code not in OFFICIAL_CODES:
    send_to_human(result)
```

❌ Mistake 2: Over-complicated schemas (deep nesting, dozens of optional fields)
✅ Correct: Keep schemas flat and small; split into steps when needed.
```python
# Wrong: one 60-field nested model
# Right: 5-8 fields per call, chain several calls
```

❌ Mistake 3: Ignoring refusals and truncation. If `max_tokens` is too small the JSON is cut off; check `finish_reason` and the `refusal` field.

---

## 🧠 Tricky Interview Question
**Q**: "You use schema-enforced structured output, yet accuracy of the `hs_code` field did not improve versus plain prompting. Why? Did structured output fail?"

**Answer**: No. Structured output guarantees format, not factual correctness or reasoning quality. It removes parse errors and retries, but the model's knowledge is unchanged. Improving accuracy needs better context (RAG), examples, reasoning fields before the answer (e.g. a `reasons` field generated first), constrained enums from the official list, verification steps and evals. Also, forcing the answer format can slightly hurt reasoning on hard tasks if the model has no room to think; add a short rationale field before the final answer.

---

## ⚫ Interview Questions + Answers

Q1: What is structured output?
A1: LLM output that follows a fixed schema (typically JSON) so code can consume it directly.

Q2: Name the levels of getting structured data from an LLM.
A2: Prompt-only JSON, JSON mode (valid JSON), function/tool calling, and schema-enforced structured outputs.

Q3: Why use Pydantic?
A3: It defines the schema in Python, generates JSON Schema for the API, validates the reply, and gives typed objects. FastAPI uses the same models.

Q4: What does constrained decoding do?
A4: It masks tokens that would violate the grammar at each step, so output always matches the schema's structure.

Q5 (Hard): What are the limits and trade-offs of structured outputs?
A5: Only a subset of JSON Schema is supported by providers (e.g. limits on recursion, required fields, nesting depth); the first call with a new schema may have extra latency for grammar compilation; truncation by `max_tokens` can still break JSON; refusals return a different shape; the format does not guarantee correct content; and overly rigid schemas can reduce answer quality. Mitigate with simple schemas, `finish_reason` checks, semantic validators, and evals.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Output feeds code (DB, API, workflow)
- Classification, extraction, routing, tool arguments
- You want fewer retries and parse errors

❌ Avoid when:
- The answer is prose for humans (chat, essays)
- The schema would be huge or highly dynamic
- You need a provider feature that is not supported for your schema

---

## 📊 Visual Diagram
```
 Pydantic model ──► JSON Schema ──► API request (response_format)
                                         |
                                         v
                          +-----------------------------+
                          | LLM with constrained decode |
                          | (invalid tokens masked)     |
                          +-----------------------------+
                                         |
                                         v
                     {"hs_code":"8518.30","confidence":0.92,...}
                                         |
                                  Pydantic parse
                                         |
                      typed object ──► validators ──► DB / API / graph state
                                         |
                              (meaning errors still possible)
```

---

## 💰 Cost Impact
- Schema tokens add to input on every request (keep names and descriptions concise).
- Fewer retries: schema enforcement removes most invalid-JSON retries, which saves tokens versus prompt-only JSON.
- JSON syntax adds output tokens (braces, quotes, keys); short keys lower cost for high-volume jobs.
- Cache the static schema/system prefix with prompt caching.

Optimisation: flat small schemas, short field names with clear descriptions, `max_tokens` sized to the schema, cheap model for extraction, and measuring retry rate before and after.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Structured output | Output following a schema | Schema का पालन करने वाला output |
| JSON Schema | Standard way to describe JSON shape | JSON की बनावट बताने का मानक तरीका |
| Constrained decoding | Only valid tokens allowed | सिर्फ valid tokens की अनुमति |
| Pydantic | Python data validation library | Python data validation library |
| Refusal | Model declines the request | Model का इनकार |
| Typed object | Python object with known fields | ज्ञात fields वाला Python object |

---

## ⚡ 3-Line Summary
English: Structured output makes the LLM return schema-shaped data that code can use directly, enforced by the provider instead of hoped for in a prompt. It guarantees structure, not truth, so keep validators and evals. Use Pydantic as the single schema for the LLM, FastAPI and LangChain.
Hindi: Structured output LLM से schema के आकार का data दिलाता है जिसे code सीधे इस्तेमाल करे; यह prompt की उम्मीद नहीं, provider द्वारा लागू होता है। यह structure की गारंटी देता है, सच की नहीं, इसलिए validators और evals रखो। LLM, FastAPI और LangChain के लिए Pydantic को एक ही schema बनाओ।

---

## ➡️ Next Topic
**082. JSON Mode in OpenAI** — the simpler `response_format={"type": "json_object"}` option, what it guarantees and what it does not.
