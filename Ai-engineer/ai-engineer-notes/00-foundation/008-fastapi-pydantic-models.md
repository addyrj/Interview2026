---

# 008. FastAPI Pydantic Models
# हिंदी में: FastAPI Pydantic Models

---

## 🔵 Simple Definition (English)
A Pydantic model is a Python class whose fields have types. When you create it from data (JSON from a client or an LLM), Pydantic checks and converts every field, or raises a clear error. FastAPI uses models for request bodies, response shapes and docs. This note uses Pydantic v2.

## 🔵 सरल परिभाषा (Hindi)
Pydantic model एक Python class है जिसके fields के types होते हैं। जब आप इससे data (client या LLM का JSON) बनाते हैं, Pydantic हर field check और convert करता है, या साफ़ error देता है। FastAPI request body, response shape और docs के लिए models use करता है। यह note Pydantic v2 पर है।

---

## 🔴 Problem it Solves
Clients send missing fields, strings instead of numbers, or 10 MB of text; LLMs return JSON with wrong keys. Hand-written `if` checks are long and inconsistent. Models give one declarative place to define rules, and they produce JSON Schema so the same model can describe the API and an LLM tool.

## 🔴 यह क्यों बना? (Hindi)
Clients missing fields, numbers की जगह strings या 10 MB text भेजते हैं; LLMs गलत keys वाला JSON देते हैं। हाथ से लिखे `if` checks लंबे और असंगत होते हैं। Models नियम तय करने की एक declarative जगह देते हैं, और JSON Schema भी बनाते हैं जिससे वही model API और LLM tool दोनों का वर्णन करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define class Item(BaseModel) with typed fields and Field(...) constraints
Step 2 → Data arrives (dict or JSON) from client or LLM
Step 3 → Item.model_validate(data) / model_validate_json(text) runs validation
Step 4 → Types are coerced (lax mode: "12" -> 12) and constraints checked (min_length, ge, pattern)
Step 5 → Valid: you get a typed object. Invalid: ValidationError listing every problem
Step 6 → FastAPI turns ValidationError into HTTP 422 with details automatically
Step 7 → item.model_dump() / model_dump_json() serialises back; model_json_schema() gives the schema
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → class Item(BaseModel) में typed fields और Field(...) constraints लिखो
Step 2 → Client या LLM से data (dict या JSON) आता है
Step 3 → Item.model_validate(data) / model_validate_json(text) validation चलाता है
Step 4 → Types coerce होते हैं (lax mode: "12" -> 12) और constraints check (min_length, ge, pattern)
Step 5 → सही: typed object मिलता है। गलत: हर समस्या की list के साथ ValidationError
Step 6 → FastAPI ValidationError को अपने आप HTTP 422 बना देता है
Step 7 → item.model_dump() / model_dump_json() वापस serialise; model_json_schema() schema देता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: `ClassifyRequest` (description 3-2000 chars, country code, optional declared value), `ClassifyResponse` (hs_code regex, confidence 0-1, alternatives list), and the same `ClassifyResponse` is used as the LLM structured-output schema, so one definition protects both the API and the model output.

**Amazon AI**: A `ProductListing` model validates seller uploads (title length, price > 0, at most 10 images) before any AI enrichment is paid for.

## 🟡 Real Example Hindi mein
**Tariff System**: `ClassifyRequest` (description 3-2000 chars, country code, optional declared value), `ClassifyResponse` (hs_code regex, confidence 0-1, alternatives list), और वही `ClassifyResponse` LLM के structured-output schema के रूप में भी use होता है, यानी एक definition API और model output दोनों की रक्षा करती है।

**Amazon AI**: `ProductListing` model seller uploads (title length, price > 0, अधिकतम 10 images) AI enrichment पर पैसा खर्च होने से पहले validate करता है।

---

## 💻 Code Example — Basic
```python
# Basic Pydantic v2 model - needs: pip install pydantic
from pydantic import BaseModel, Field, ValidationError  # core pieces


class ClassifyRequest(BaseModel):  # request model
    description: str = Field(min_length=3, max_length=2000)  # length limits
    country: str = Field(default="IN", pattern=r"^[A-Z]{2}$")  # 2 capital letters
    declared_value: float | None = Field(default=None, ge=0)  # optional, not negative


ok = ClassifyRequest(description="Android phone", declared_value="199.5")  # string coerced to float
print(ok)  # description='Android phone' country='IN' declared_value=199.5
print(ok.model_dump())  # plain dict
print(ok.model_dump_json())  # JSON text

try:  # invalid data
    ClassifyRequest(description="x", country="india", declared_value=-5)  # three problems
except ValidationError as exc:  # collect all errors
    print(exc.error_count(), "errors")  # 3 errors
    for e in exc.errors():  # list each
        print(e["loc"], e["type"])  # which field, which rule

print(list(ClassifyRequest.model_json_schema()["properties"]))  # fields in JSON schema
```

## 💻 Code Example — Advanced
```python
# Production models: nesting, validators, computed field, reuse for LLM output, async parse + errors
import asyncio  # async runtime
from typing import Literal  # restricted values

from pydantic import BaseModel, ConfigDict, Field, ValidationError, computed_field, field_validator, model_validator


class Candidate(BaseModel):  # nested model
    hs_code: str = Field(pattern=r"^\d{4}(\.\d{2}){0,2}$")  # HS format
    score: float = Field(ge=0, le=1)  # similarity score


class ClassifyResponse(BaseModel):  # response and LLM output schema
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)  # reject unknown keys, trim strings

    hs_code: str = Field(pattern=r"^\d{4}(\.\d{2}){0,2}$", description="Best HS code")  # description helps the LLM
    confidence: float = Field(ge=0, le=1)  # probability
    duty_type: Literal["ad_valorem", "specific"] = "ad_valorem"  # restricted
    alternatives: list[Candidate] = Field(default_factory=list, max_length=3)  # at most 3, safe default

    @field_validator("hs_code")  # single-field validator
    @classmethod
    def chapter_not_zero(cls, v: str) -> str:  # business rule
        if v.startswith("00"):  # chapter 00 does not exist
            raise ValueError("invalid chapter 00")  # message goes in the error
        return v  # accepted

    @model_validator(mode="after")  # cross-field validator
    def alternatives_not_better(self) -> "ClassifyResponse":  # check logic across fields
        if any(a.score > self.confidence for a in self.alternatives):  # alternative better than winner?
            raise ValueError("alternative score exceeds main confidence")  # inconsistent output
        return self  # valid

    @computed_field  # derived value included in output
    @property
    def chapter(self) -> str:  # first two digits
        return self.hs_code[:2]  # chapter number


async def parse_llm_output(raw: str) -> ClassifyResponse | None:  # safe parsing helper
    try:  # try to validate
        return ClassifyResponse.model_validate_json(raw)  # parse + validate JSON text
    except ValidationError as exc:  # LLM produced bad data
        print("invalid LLM output:", exc.errors()[0]["msg"])  # log first problem
        return None  # caller can retry or fall back


async def main() -> None:  # demo
    good = '{"hs_code":" 8517.13 ","confidence":0.9,"alternatives":[{"hs_code":"8471","score":0.5}]}'  # valid JSON
    bad = '{"hs_code":"0012","confidence":0.9}'  # chapter 00
    print(await parse_llm_output(good))  # parsed (whitespace trimmed) incl. chapter
    print(await parse_llm_output(bad))  # prints reason, then None
    print(ClassifyResponse.model_json_schema()["required"])  # ['hs_code', 'confidence']


if __name__ == "__main__":  # entry
    asyncio.run(main())  # run
```

---

## 🟠 FastAPI Integration
Declare models as the body parameter and as `response_model`. FastAPI validates input (422 on failure), filters output (secrets in the internal object never leak), and shows examples in Swagger. Use separate `In`, `Out` and `DB` models so internal fields do not leak.

```python
# FastAPI + separate input/output models
from fastapi import FastAPI  # framework
from pydantic import BaseModel, Field  # models

app = FastAPI()  # app


class UserIn(BaseModel):  # what the client sends
    email: str  # email
    password: str = Field(min_length=8)  # secret input


class UserOut(BaseModel):  # what the client gets back
    email: str  # email only, no password


@app.post("/signup", response_model=UserOut)  # response is filtered through UserOut
async def signup(user: UserIn) -> UserIn:  # we even return the full object...
    return user  # ...but FastAPI strips the password because of response_model
```

---

## 🔗 LangChain / LangGraph Connection
`llm.with_structured_output(Model)` uses the model's JSON Schema (field names, types, descriptions) to make the LLM return that shape, and returns a validated object. Tool inputs use `args_schema` models. LangGraph state can be a Pydantic model.

```python
# Same model for API and LLM (needs OPENAI_API_KEY to run the last lines)
from pydantic import BaseModel, Field  # models


class HSAnswer(BaseModel):  # LangChain reads this schema
    hs_code: str = Field(description="HS code, for example 8517.13")  # description is sent to the LLM
    confidence: float = Field(ge=0, le=1, description="0 to 1")  # numeric


# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4o-mini").with_structured_output(HSAnswer)
# answer: HSAnswer = await llm.ainvoke("HS code for a smartphone")
print(HSAnswer.model_json_schema()["properties"]["hs_code"]["description"])  # what the LLM will see
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mutable default values and using v1 syntax
✅ Correct: `default_factory`, and v2 methods (`model_dump`, `model_validate`).

```python
# Wrong: v1 API (deprecated in v2) and shared default
class A(BaseModel):
    tags: list = []
a.dict()
# Right
class A(BaseModel):
    tags: list[str] = Field(default_factory=list)
a.model_dump()
```

❌ Mistake 2: Returning the DB/internal model directly (leaks hashes, internal ids).
✅ Correct: set `response_model` to a separate Out model.

```python
# Wrong
@app.get("/user")
async def user() -> UserDB: ...
# Right
@app.get("/user", response_model=UserOut)
async def user() -> UserDB: ...
```

❌ Mistake 3: Trusting lax coercion for money or ids ("12abc" fails but `True` becomes 1 in some fields). Use `strict=True` or `StrictInt` where exact types matter.

---

## 🧠 Tricky Interview Question

**Q**: "Your endpoint accepts `amount: float`. A client sends `"amount": "1e9999"` and the server logs show `inf`, then totals go wrong. How do you prevent this?"

**Answer**: Lax mode accepts strings that parse as floats, including very large values or special values like `inf`/`nan`. Use constraints: `Field(gt=0, le=1_000_000, allow_inf_nan=False)`, or `Decimal` for money, and `strict=True` if you want to reject strings entirely. Add `max_length` for text fields too. Models are your first line of defence, so set bounds on every numeric and string field.

---

## ⚫ Interview Questions + Answers

Q1: What does Pydantic do that a dataclass does not? (Easy)
A1: Pydantic validates and coerces data at runtime, parses JSON, serialises, and generates JSON Schema. A dataclass only generates `__init__` and does not check types.

Q2: How does FastAPI respond to invalid data? (Easy)
A2: It returns HTTP 422 with a JSON body listing each error (`loc`, `msg`, `type`). No handler code runs, so no LLM tokens are spent.

Q3: Difference between `field_validator` and `model_validator`? (Medium)
A3: `field_validator` checks or transforms one field. `model_validator` (mode "before" or "after") sees the whole model, so it can check relationships between fields (for example start < end).

Q4: Why create separate request, response and DB models? (Medium)
A4: They have different jobs. Request models validate input, response models control what is exposed, DB models mirror storage with internal fields. One shared model leaks private fields and makes API changes break the database layer.

Q5: How do you handle LLM output that sometimes violates the schema? (Hard)
A5: Use provider structured output / JSON schema mode to reduce errors, then always validate with `model_validate_json`. On failure, retry once with the validation error message added to the prompt ("fix these errors"), cap retries, and fall back to a default or human review. Log failure rates by prompt version. Use `extra="forbid"` to detect hallucinated fields, and keep schemas small because the schema itself is sent as input tokens.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Defining request and response bodies
- Validating LLM JSON output and tool arguments
- Loading settings (`pydantic-settings`)

❌ Avoid when:
- Millions of tiny internal objects in a hot loop (plain dataclass or tuple is lighter)
- Data is already trusted and typed
- You would put business logic that needs I/O into validators (keep validators pure)

---

## 📊 Visual Diagram
```
 JSON in ──► Model.model_validate_json()
               │
               ├─ coerce types ("12" → 12)
               ├─ check Field rules (len, ge, regex)
               ├─ run validators (field / model)
               │
        ┌──────┴───────┐
   valid│              │invalid
        ▼              ▼
  typed object    ValidationError ──► FastAPI 422  (or LLM retry)
        │
        ▼
 model_dump() / JSON out      model_json_schema() ──► OpenAPI / LLM tool schema
```

---

## 💰 Cost Impact
Validation is cheap CPU work and saves tokens by rejecting bad requests before the LLM. Limits like `max_length=2000` bound input tokens (about 500). Using a Pydantic model as an LLM schema adds schema tokens to each call (roughly 100-300 tokens), so keep field descriptions short and avoid optional fields you never use. Failed validation of LLM output causes retries that double the call cost; structured-output modes cut failures. Example: 100K daily calls with a 200-token schema is 20M tokens, about $3 on gpt-4o-mini input pricing; shrink it by 40 percent to save about $1.2 per day.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BaseModel | Pydantic model base class | Pydantic model की base class |
| Field | Adds constraints and metadata | constraints और metadata जोड़ता है |
| Validator | Custom check function | custom जाँच function |
| Coercion | Auto type conversion | अपने आप type बदलना |
| ValidationError | Raised for invalid data | गलत data पर error |
| response_model | Filters API output | API output filter |
| model_dump | Convert model to dict | model से dict |
| JSON Schema | Machine description of data | data का machine वर्णन |

---

## ⚡ 3-Line Summary
English: Pydantic models validate and convert data for requests, responses and LLM output. FastAPI returns 422 on bad input and filters output with `response_model`. Keep separate In/Out models, bound every field, and reuse models as LLM schemas.
Hindi: Pydantic models requests, responses और LLM output का data validate और convert करते हैं। गलत input पर FastAPI 422 देता है और `response_model` से output filter करता है। In/Out models अलग रखो, हर field की सीमा तय करो, और models को LLM schema के रूप में reuse करो।

---

## ➡️ Next Topic
**009. FastAPI Dependency Injection** — models validate data; dependencies provide shared resources like LLM clients, DB sessions and the current user.
