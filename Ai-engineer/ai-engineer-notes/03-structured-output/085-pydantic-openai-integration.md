---

# 085. Pydantic + OpenAI Integration
# हिंदी में: Pydantic + OpenAI Integration

---

## 🔵 Simple Definition (English)
Pydantic is a Python library that defines data shapes as classes and validates them. The OpenAI SDK can take a Pydantic class as `response_format`, turn it into a JSON Schema for the model, and give you back a validated Pydantic object. One class does three jobs: schema, validation and typing.

## 🔵 सरल परिभाषा (Hindi)
Pydantic एक Python library है जो data की shape को class के रूप में define और validate करती है। OpenAI SDK Pydantic class को `response_format` में ले सकता है, उसे JSON Schema में बदलकर model को देता है और validated Pydantic object वापस देता है। एक class तीन काम करती है: schema, validation और typing।

---

## 🔴 Problem it Solves
Writing JSON Schema by hand is long and error-prone, and you must keep it in sync with the Python code that reads the result. Change one, forget the other, and you get bugs. Pydantic removes that duplication: the class is the single source of truth.

## 🔴 यह क्यों बना? (Hindi)
JSON Schema हाथ से लिखना लंबा और error-prone है, और उसे result पढ़ने वाले Python code के साथ sync रखना पड़ता है। एक बदला और दूसरा भूले तो bug। Pydantic duplication हटाता है: class ही single source of truth है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a BaseModel with typed fields (+ Field descriptions)
Step 2 → Pass the class: client.beta.chat.completions.parse(response_format=Model)
Step 3 → SDK calls Model.model_json_schema() and makes it strict-compatible
Step 4 → Model replies with JSON text
Step 5 → SDK runs Model.model_validate_json(text)
Step 6 → You read completion.choices[0].message.parsed (a Model instance)
Step 7 → If validation fails, pydantic.ValidationError (or LengthFinishReasonError) is raised
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → typed fields (+ Field descriptions) के साथ BaseModel लिखो
Step 2 → class पास करो: client.beta.chat.completions.parse(response_format=Model)
Step 3 → SDK Model.model_json_schema() बुलाकर उसे strict-compatible बनाता है
Step 4 → Model JSON text लौटाता है
Step 5 → SDK Model.model_validate_json(text) चलाता है
Step 6 → आप completion.choices[0].message.parsed पढ़ते हो (Model instance)
Step 7 → Validation fail हो तो pydantic.ValidationError (या LengthFinishReasonError) आता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: `TariffResult` has `hs_code` (must match regex `^\d{4}\.\d{2}$`), `duty_percent` (0 to 100) and `confidence` (0 to 1). Pydantic validators reject nonsense like duty 450 or code "ABC" even if the JSON shape was right.

**Zomato-style**: `OrderItem` with `quantity: int = Field(ge=1, le=20)` so "order 500 biryanis" is caught.

## 🟡 Real Example Hindi mein
**Tariff System**: `TariffResult` में `hs_code` (regex `^\d{4}\.\d{2}$` से match), `duty_percent` (0 से 100) और `confidence` (0 से 1)। JSON की shape सही हो तब भी Pydantic validators duty 450 या code "ABC" जैसी बकवास reject करते हैं।

**Zomato-style**: `OrderItem` में `quantity: int = Field(ge=1, le=20)` ताकि "500 biryani" पकड़ा जाए।

---

## 💻 Code Example — Basic
```python
# Basic: Pydantic model -> JSON Schema -> validate a fake LLM reply.
# Needs: pip install pydantic   (v2)
import json                                              # to print schema nicely
from pydantic import BaseModel, Field, ValidationError   # core pieces

class TariffResult(BaseModel):                           # our data contract
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$", description="HS code like 8518.30")
    duty_percent: float = Field(ge=0, le=100, description="Duty in percent")
    confidence: float = Field(ge=0, le=1)                # probability-like number

schema = TariffResult.model_json_schema()                # what the SDK sends to OpenAI
print(json.dumps(schema["properties"]["hs_code"]))       # peek at one field

good = '{"hs_code": "8518.30", "duty_percent": 0, "confidence": 0.9}'   # valid reply
bad = '{"hs_code": "ABC", "duty_percent": 450, "confidence": 0.9}'      # invalid reply

for raw in (good, bad):                                  # test both
    try:
        obj = TariffResult.model_validate_json(raw)      # parse + validate in one step
        print("OK:", obj.hs_code, obj.duty_percent)      # typed attributes
    except ValidationError as exc:                       # pydantic collects all errors
        print("Rejected:", exc.error_count(), "error(s)")   # count of problems
```

## 💻 Code Example — Advanced
```python
# Production: validators, refusal handling, async, usage tracking.
import asyncio                                           # async runner
from typing import Optional                              # optional return
from openai import AsyncOpenAI, OpenAIError, LengthFinishReasonError   # SDK + errors
from pydantic import BaseModel, Field, ValidationError, field_validator

client = AsyncOpenAI()                                   # env key

class TariffResult(BaseModel):
    hs_code: str = Field(description="HS code, format 8518.30")
    description: str = Field(description="Short product description")
    duty_percent: float = Field(description="Duty percent 0-100")
    confidence: float = Field(description="0 to 1")

    @field_validator("hs_code")                          # custom business rule
    @classmethod
    def check_code(cls, v: str) -> str:
        digits = v.replace(".", "")                      # strip the dot
        if not (digits.isdigit() and len(digits) == 6):  # must be 6 digits
            raise ValueError("HS code must be 6 digits")
        return v                                         # accept

    @field_validator("duty_percent")
    @classmethod
    def check_duty(cls, v: float) -> float:
        if not 0 <= v <= 100:                            # sanity range
            raise ValueError("duty out of range")
        return v

async def classify(product: str) -> Optional[TariffResult]:
    """Classify a product; None means refusal or failure."""
    try:
        completion = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "Classify the product for customs."},
                      {"role": "user", "content": product}],
            response_format=TariffResult,                # Pydantic class
            temperature=0,
            max_tokens=300,
        )
    except LengthFinishReasonError:                      # JSON cut by max_tokens
        print("Output truncated")
        return None
    except ValidationError as exc:                       # validator rejected the value
        print("Semantic validation failed:", exc.errors()[0]["msg"])
        return None
    except OpenAIError as exc:                           # network / rate limit
        print("API error:", exc)
        return None
    msg = completion.choices[0].message                  # first choice
    if msg.refusal:                                      # model declined
        return None
    return msg.parsed                                    # TariffResult instance

if __name__ == "__main__":
    print(asyncio.run(classify("Wireless earbuds")))     # needs API key
```

---

## 🟠 FastAPI Integration
FastAPI is built on Pydantic, so the same class works for the request, the LLM and the response.

```python
from fastapi import FastAPI, HTTPException               # framework
from pydantic import BaseModel                           # request model

app = FastAPI()

class ClassifyRequest(BaseModel):
    product: str

@app.post("/classify", response_model=TariffResult)      # docs show the same schema
async def classify_route(req: ClassifyRequest) -> TariffResult:
    result = await classify(req.product)                 # LLM call
    if result is None:
        raise HTTPException(status_code=422, detail="Could not classify product")
    return result                                        # validated twice: LLM + API
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify the product for customs."),
    ("human", "{product}"),
])
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chain = prompt | llm.with_structured_output(TariffResult)   # LCEL chain -> Pydantic
result = chain.invoke({"product": "Wireless earbuds"})      # TariffResult
# LangGraph: define a TypedDict/BaseModel state with `tariff: TariffResult | None`.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Putting range constraints only in Pydantic and expecting the LLM to obey
✅ Correct: Constraints like `ge/le/pattern` may not be enforced by strict decoding; validate after parsing and describe limits in `Field(description=...)`.

```python
# Wrong: assume duty_percent <= 100 because Field(le=100)
# Right: catch ValidationError, retry or fallback
```

❌ Mistake 2: Using Pydantic v1 syntax (`@validator`, `.parse_raw`)
✅ Correct: v2 syntax.

```python
# Wrong: @validator("hs_code");  Model.parse_raw(text)
# Right: @field_validator("hs_code");  Model.model_validate_json(text)
```

---

## 🧠 Tricky Interview Question

**Q**: "Pydantic says `duty_percent` must be `le=100`, but OpenAI strict mode sometimes returned 150 and your API crashed with 500. Why, and how do you fix it?"

**Answer**: Strict constrained decoding enforces structure and types; numeric bounds and regex patterns are often not part of the supported schema subset, so they are checked only when the SDK validates after the response. Fix: wrap the call, catch `ValidationError`, retry once with the error message in the prompt (topic 091), or fall back to human review. Never let a validation error become an unhandled 500.

---

## ⚫ Interview Questions + Answers

Q1: How do you pass a Pydantic model to OpenAI?
A1: `client.beta.chat.completions.parse(..., response_format=MyModel)` and read `message.parsed`.

Q2: What is the benefit over writing JSON Schema by hand?
A2: Single source of truth, less code, automatic validation, editor type hints.

Q3: Where do field descriptions go and why?
A3: `Field(description="...")`. They become schema `description` entries that guide the model on what each field means, like mini prompts.

Q4: How do you add business rules (HS code must exist)?
A4: Use `@field_validator` or `@model_validator` for local rules; for database lookups validate after parsing in service code.

Q5: How do you handle a Pydantic model that is not strict-compatible (e.g. `dict[str, Any]`, defaults)?
A5: Strict mode needs all fields required and no free-form objects. Replace dicts with explicit models or lists of key/value models, represent optional as `Optional[T]` with no default, or fall back to tool calling / Instructor for looser schemas.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Python backend with FastAPI
- You need validation plus typed results
- Many fields or nested data

❌ Avoid when:
- Schema is dynamic at runtime (build raw JSON Schema instead)
- Non-Python client

---

## 📊 Visual Diagram
```
 class TariffResult(BaseModel)
        │  model_json_schema()
        ▼
   JSON Schema ───────► OpenAI (strict)
                              │ JSON text
        ┌─────────────────────┘
        ▼
   model_validate_json()  ──► TariffResult instance ──► FastAPI response
        │ fails
        ▼
   ValidationError ──► retry / fallback
```

---

## 💰 Cost Impact
The generated schema, including every field description, is billed as input tokens each request. Verbose descriptions on 20 fields can add 500+ tokens. Validation runs locally and is free.
Optimise: concise descriptions, remove unused fields, reuse a stable prompt prefix for prompt caching, validate locally instead of asking the LLM to "double check".

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BaseModel | Pydantic class for data | Data की class |
| Field | Adds constraints and description | Constraints और description |
| model_json_schema | Class to JSON Schema | Class से schema |
| model_validate_json | Parse and validate | Parse + validate |
| field_validator | Custom rule for a field | Field का custom rule |
| parsed | SDK attribute with the object | तैयार object |

---

## ⚡ 3-Line Summary
English: Pass a Pydantic class as `response_format` to `parse()` and get a typed object back. The class is schema, validator and type hints in one. Always handle ValidationError, refusal and truncation.
Hindi: Pydantic class को `parse()` के `response_format` में दो और typed object पाओ। Class एक साथ schema, validator और type hints है। ValidationError, refusal और truncation हमेशा handle करो।

---

## ➡️ Next Topic
**086. Instructor Library** — a wrapper that adds automatic retries and works with many providers.
