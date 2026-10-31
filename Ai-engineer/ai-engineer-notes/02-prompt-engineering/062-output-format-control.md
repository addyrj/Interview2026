---

# 062. Output Format Control
# हिंदी में: Output Format Control

---

## 🔵 Simple Definition (English)
Output format control means making the model return answers in a fixed, machine-readable shape (JSON, enum labels, tables, XML tags) so code can use it directly. Methods from weak to strong: instructions in the prompt, JSON mode, structured outputs with a JSON schema, and tool/function calling.

## 🔵 सरल परिभाषा (Hindi)
Output format control यानी model से जवाब एक तय, machine-readable shape (JSON, enum labels, table, XML tags) में लेना ताकि code सीधे इस्तेमाल कर सके। कमज़ोर से मज़बूत तरीके: prompt में instructions, JSON mode, JSON schema वाले structured outputs, और tool/function calling।

---

## 🔴 Problem it Solves
- Free text is hard to parse: "Sure! Here is the JSON: ```json ..." breaks `json.loads`.
- Missing fields, wrong types and invented keys crash downstream code.
- Different runs give slightly different layouts.

## 🔴 यह क्यों बना? (Hindi)
- Free text parse करना मुश्किल है: "Sure! Here is the JSON: ```json ..." से `json.loads` टूटता है।
- गायब fields, गलत types और गढ़े हुए keys downstream code को crash करते हैं।
- अलग-अलग runs में layout थोड़ा अलग आता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define the target shape as a pydantic model / JSON schema
Step 2 → Choose the strongest method your model supports:
         (a) structured outputs with schema  (b) JSON mode  (c) tool calling  (d) prompt only
Step 3 → In the prompt, describe each field and allowed values (enums)
Step 4 → Set temperature low and max_tokens high enough (truncated JSON is invalid)
Step 5 → Parse and validate with pydantic
Step 6 → On failure: retry with the validation error, or fallback/review
Step 7 → Log the failure rate; a rising rate means prompt/model drift
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Target shape को pydantic model / JSON schema के रूप में define करो
Step 2 → Model जो सबसे मज़बूत तरीका support करे वह चुनो:
         (a) schema वाले structured outputs  (b) JSON mode  (c) tool calling  (d) सिर्फ़ prompt
Step 3 → Prompt में हर field और allowed values (enums) समझाओ
Step 4 → Temperature कम रखो और max_tokens इतना दो कि JSON कटे नहीं (कटा JSON invalid होता है)
Step 5 → pydantic से parse और validate करो
Step 6 → Fail हो तो validation error के साथ retry करो, या fallback/review
Step 7 → Failure rate log करो; बढ़ता rate prompt/model drift का संकेत है
```

---

## 🟡 Real World Example
**Tariff Classification System**: The API must return `{"hs_code": "85182200", "confidence": 0.91, "needs_review": false, "alternatives": ["85183000"]}`. With prompt-only JSON, 3% of responses had markdown fences or missing fields. With structured outputs (JSON schema, strict) the invalid rate went to about 0%, and the 8-digit code is additionally checked by a regex in pydantic.

**Zomato-style**: Extracting `{dish, quantity, spice_level}` from a voice-note order into a strict schema before creating the cart.

## 🟡 Real Example Hindi mein
**Tariff System**: API को `{"hs_code": "85182200", "confidence": 0.91, "needs_review": false, "alternatives": ["85183000"]}` लौटाना है। सिर्फ़ prompt वाले JSON में 3% responses में markdown fences या missing fields थे। Structured outputs (JSON schema, strict) से invalid rate लगभग 0% हुआ, और 8-digit code की जाँच pydantic में regex से भी होती है।

**Zomato-style**: Voice-note order से `{dish, quantity, spice_level}` को strict schema में निकालना, cart बनाने से पहले।

---

## 💻 Code Example — Basic
```python
# Basic: robust parsing of "messy" model output into a validated object (needs pydantic v2)
import json  # parse JSON
import re  # find JSON inside text
from pydantic import BaseModel, Field, ValidationError  # pydantic v2

class Result(BaseModel):
    hs_code: str = Field(pattern=r"^\d{8}$")  # exactly 8 digits
    confidence: float = Field(ge=0, le=1)  # 0..1
    needs_review: bool  # flag

def extract_json(text: str) -> dict:
    tick = "`" * 3  # triple backtick built at runtime
    fenced = re.search(tick + r"(?:json)?\s*(\{.*?\})\s*" + tick, text, re.S)  # JSON inside code fence
    raw = fenced.group(1) if fenced else text[text.find("{"): text.rfind("}") + 1]  # or first {..last }
    return json.loads(raw)  # may raise JSONDecodeError

messy = 'Sure! Here you go:\n' + "`" * 3 + 'json\n{"hs_code": "85182200", "confidence": 0.91, "needs_review": false}\n' + "`" * 3
try:
    obj = Result.model_validate(extract_json(messy))  # parse + validate
    print("OK:", obj)  # validated object
except (json.JSONDecodeError, ValidationError) as exc:  # bad output
    print("Invalid:", type(exc).__name__)
bad = '{"hs_code": "8518", "confidence": 2, "needs_review": "maybe"}'  # wrong everywhere
try:
    Result.model_validate(json.loads(bad))
except ValidationError as exc:
    print("Validation errors:", exc.error_count())  # shows why validation matters
```

## 💻 Code Example — Advanced
```python
# Production-style: structured outputs with a pydantic schema (openai>=1), async, repair fallback
import asyncio  # async runtime
import json  # fallback parsing
from typing import Literal  # enum-like values
from pydantic import BaseModel, Field, ValidationError  # pydantic v2
from openai import AsyncOpenAI, APIError  # openai>=1

client = AsyncOpenAI(timeout=25.0)  # shared client

class Classification(BaseModel):
    hs_code: str = Field(pattern=r"^\d{8}$", description="8-digit HS code")
    confidence: float = Field(ge=0, le=1)
    category: Literal["electronics", "apparel", "food", "other"]  # fixed set
    needs_review: bool
    alternatives: list[str] = Field(default_factory=list, max_length=3)

SYSTEM = "Classify the product into an HS code. Fill every field."

async def classify(product: str) -> Classification | None:
    try:
        # Preferred: structured outputs via the SDK's parse helper with a pydantic model.
        # Note: in some SDK versions this lives at client.beta.chat.completions.parse.
        resp = await client.beta.chat.completions.parse(
            model="gpt-4o-mini", temperature=0, max_tokens=300,
            messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": product}],
            response_format=Classification)  # schema enforced by the API
        msg = resp.choices[0].message
        if msg.refusal:  # model refused (safety)
            return None
        return msg.parsed  # already a Classification instance
    except (APIError, ValidationError) as exc:
        print("structured call failed:", exc.__class__.__name__)
    # Fallback: plain JSON mode + manual validation
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini", temperature=0, max_tokens=300,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": SYSTEM + " Return JSON with keys: "
                       + ", ".join(Classification.model_fields)},
                      {"role": "user", "content": product}])
        return Classification.model_validate(json.loads(resp.choices[0].message.content or "{}"))
    except (APIError, ValidationError, json.JSONDecodeError):
        return None  # caller handles None as "needs review"

# print(asyncio.run(classify("Bluetooth speaker with FM radio")))
```

---

## 🟠 FastAPI Integration
FastAPI + pydantic is a natural match: reuse the same model as `response_model`, so the API contract and the LLM contract are one definition.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel, Field  # validation

app = FastAPI()  # app

class In(BaseModel):
    product: str = Field(min_length=3, max_length=500)  # input text

@app.post("/classify", response_model=Classification)  # output validated by FastAPI too
async def classify_route(body: In) -> Classification:
    result = await classify(body.product)  # structured LLM call
    if result is None:  # all attempts failed
        raise HTTPException(status_code=422, detail="Could not produce valid classification")
    return result  # FastAPI serialises the pydantic object
```

---

## 🔗 LangChain / LangGraph Connection
`llm.with_structured_output(PydanticModel)` is the standard way: LangChain picks the provider's best mechanism (JSON schema or tool calling) and returns a typed object. `PydanticOutputParser` and `JsonOutputParser` work with plain prompts. LangGraph states can use the same pydantic models for node outputs.

```python
from langchain_openai import ChatOpenAI  # model

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # base model
structured = llm.with_structured_output(Classification)  # returns Classification objects
# result = structured.invoke("Classify: Bluetooth speaker with FM radio")
# print(result.hs_code, result.confidence)
# For raw dicts: llm.with_structured_output(schema_dict) or JsonOutputParser
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Asking for JSON in the prompt and calling `json.loads` directly
✅ Correct: Use structured outputs or JSON mode, then validate.

```python
# Wrong: data = json.loads(resp.choices[0].message.content)   # fails on fences/extra text
# Right: Classification.model_validate_json(content) or structured outputs
```

❌ Mistake 2: Too small `max_tokens` which cuts JSON in the middle
✅ Correct: Leave room; check `finish_reason`.

```python
# Wrong: max_tokens=20 for a 60-token object -> '{"hs_code": "8518'
# Right: max_tokens=300 and if choice.finish_reason == "length": retry with a larger limit
```

---

## 🧠 Tricky Interview Question
**Q**: "You use strict structured outputs, so every response is valid JSON. Yet some answers are still wrong. What does the schema guarantee and what does it not?"

**Answer**: The schema guarantees shape (fields, types, enums), not truth. The model can still put a wrong but well-formed HS code in the field. So add semantic validation: regex or lookup that the code exists in the tariff database, confidence thresholds, cross-field checks (category matches the chapter), retrieval grounding, and human review for low confidence. Also note that very restrictive schemas may reduce reasoning quality; consider a `reasoning` field placed before the answer.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Why do we need structured output?
A1: So code can parse and use model answers reliably without fragile string handling.

Q2: [Easy] What is JSON mode?
A2: An API setting (`response_format={"type": "json_object"}`) that makes the model return valid JSON; you must still mention JSON in the prompt and validate the fields yourself.

Q3: [Medium] JSON mode vs structured outputs?
A3: JSON mode guarantees syntactically valid JSON only. Structured outputs (`json_schema`, strict) guarantee the JSON follows your schema (fields, types, enums).

Q4: [Medium] How do you handle a model refusal or truncated output?
A4: Check the `refusal` field and `finish_reason`. For refusal, return a safe error/review. For `length`, raise `max_tokens` or shorten the request, then retry.

Q5: [Hard] How do you design schemas for good quality and low cost?
A5: Keep schemas small and flat; use enums and clear descriptions; short field names reduce tokens; put free-text `reasoning` before the final fields if reasoning helps; avoid deep nesting and optional-everything; version schemas and keep backward compatibility; validate semantically after parsing.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Output feeds code, DBs or APIs
- Extraction and classification tasks

❌ Avoid when:
- Pure creative writing for humans (free text is fine)
- Streaming partial JSON to users without a strategy to handle incomplete objects

---

## 📊 Visual Diagram
```
 Pydantic model ──► JSON schema ──► API (structured outputs)
        ▲                                   │
        │                                   ▼
   validate  ◄──────── JSON text ◄──── LLM answer
        │
   ok ──► typed object ──► DB / FastAPI response
   fail ─► repair retry ──► fallback / human review
```

---

## 💰 Cost Impact
- Schema and field descriptions are input tokens on every call; JSON keys and punctuation add output tokens (verbose keys cost more).
- Example: a response with 8 long keys may be 80 tokens vs 40 with short keys. At 100,000 calls/day: 4M tokens/day difference (about $2.40/day at $0.60/1M output).
- Failed parses cost retries; structured outputs reduce retries to near zero.
- Optimise: short keys, enums instead of free text, concise descriptions, `max_tokens` tuned to the schema, small model.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| JSON mode | Guarantees valid JSON syntax | Valid JSON syntax की गारंटी |
| Structured outputs | JSON follows your schema | Schema के अनुसार JSON |
| Schema | Description of fields and types | Fields और types का ढाँचा |
| Enum | Fixed list of allowed values | तय allowed values |
| Refusal | Model declines to answer | Model का मना करना |
| finish_reason | Why generation stopped | Generation क्यों रुका |

---

## ⚡ 3-Line Summary
English: Use structured outputs (schema) or JSON mode, then validate with pydantic; prompts alone are fragile. A schema guarantees shape, not truth, so add semantic checks. Watch `max_tokens` and refusals.
Hindi: Structured outputs (schema) या JSON mode इस्तेमाल करो और pydantic से validate करो; सिर्फ़ prompt कमज़ोर है। Schema shape की गारंटी देता है, सच की नहीं, इसलिए semantic checks जोड़ो। `max_tokens` और refusals पर नज़र रखो।

---

## ➡️ Next Topic
**063. Prompt Templates** — reusable, parameterised prompts with variables, the basis for maintainable prompt code.
