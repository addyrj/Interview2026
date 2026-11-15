---

# 399. Pydantic for AI Apps
# हिंदी में: AI Apps के लिए Pydantic (LLM output को validate करना)

---

## 🔵 Simple Definition (English)
Pydantic v2 turns data into typed Python objects and rejects bad data with clear errors. In AI apps it defines the shape of what an LLM must return (a JSON schema) and checks the reply before your code trusts it.

## 🔵 सरल परिभाषा (Hindi)
Pydantic v2 data को typed Python objects में बदलता है और गलत data को साफ error के साथ reject करता है। AI apps में यह तय करता है कि LLM को कैसा JSON लौटाना है (JSON schema) और reply पर भरोसा करने से पहले उसे check करता है।

---

## 🔴 Problem it Solves
An LLM returns text. Even when you ask for JSON it may add "Sure! Here you go", use single quotes, send `"priority": "high"` instead of a number, or skip a field. If your code does `json.loads(reply)["priority"] + 1` it crashes in production at 2 AM. Pydantic gives one place to define the contract, generate the schema for the prompt, parse, coerce and validate.

## 🔴 यह क्यों बना? (Hindi)
LLM सिर्फ text देता है। JSON माँगने पर भी वह "Sure! Here you go" जोड़ सकता है, single quotes दे सकता है, number की जगह `"high"` भेज सकता है या कोई field भूल सकता है। `json.loads(reply)["priority"] + 1` जैसा code रात 2 बजे production में crash होता है। Pydantic contract एक जगह define करता है, prompt के लिए schema बनाता है, parse + coerce + validate करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define a BaseModel with types, Field constraints and Literal choices
Step 2 → model_json_schema() makes a JSON schema you paste into the prompt
Step 3 → LLM replies with text
Step 4 → Cut the JSON part out of the text (strip ```json fences, chatter)
Step 5 → model_validate_json() parses + coerces ("2" -> 2) + validates
Step 6 → On ValidationError, send the error back to the LLM and retry
Step 7 → After N retries raise a clear error (never pass bad data on)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → BaseModel में types, Field constraints और Literal choices लिखें
Step 2 → model_json_schema() से JSON schema बनता है, उसे prompt में डालें
Step 3 → LLM text में reply देता है
Step 4 → text में से JSON वाला हिस्सा काटें (```json fences, extra बातें हटाएँ)
Step 5 → model_validate_json() parse + coerce ("2" -> 2) + validate करता है
Step 6 → ValidationError आए तो error LLM को वापस भेजकर retry करें
Step 7 → N retries के बाद साफ error उठाएँ (गलत data आगे कभी न भेजें)
```

---

## 🟡 Real World Example
A support tool at a company like Swiggy sends a customer complaint to an LLM and needs `{category, priority, summary}` back to route the ticket. Pydantic guarantees `category` is one of `billing/bug/other` and `priority` is 1 to 5. A Razorpay-style invoice extractor reads a PDF's text and must return `total > 0` and `currency` in `INR/USD` before saving to the database. OpenAI "structured outputs" and the Anthropic tool-use flow both take a Pydantic-generated JSON schema.

## 🟡 Real Example Hindi mein
Swiggy जैसी company का support tool customer की complaint LLM को भेजता है और ticket route करने के लिए `{category, priority, summary}` चाहता है। Pydantic पक्का करता है कि `category` सिर्फ `billing/bug/other` हो और `priority` 1 से 5 हो। Razorpay जैसा invoice extractor PDF का text पढ़कर database में save करने से पहले `total > 0` और `currency` `INR/USD` में होना check करता है। OpenAI "structured outputs" और Anthropic tool-use दोनों Pydantic से बना JSON schema लेते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: validate an LLM-style JSON reply (pip install pydantic)
from typing import Literal, Optional  # type helpers
from pydantic import BaseModel, Field, ValidationError, field_validator  # pydantic v2 tools


class Ticket(BaseModel):  # the contract the LLM must follow
    category: Literal["billing", "bug", "other"]  # only these three strings allowed
    priority: int = Field(ge=1, le=5)  # integer between 1 and 5
    summary: str = Field(min_length=5, max_length=80)  # length limits
    order_id: Optional[str] = None  # optional field, default None

    @field_validator("summary")  # custom check on one field
    @classmethod
    def strip(cls, v: str) -> str:  # clean the value
        return v.strip()  # remove extra spaces


raw: str = '{"category": "billing", "priority": "2", "summary": "  Refund not received  "}'  # note "2" is a string
t: Ticket = Ticket.model_validate_json(raw)  # parse JSON text + validate
print(t)  # priority was coerced from "2" to 2, summary was stripped
# Output: category='billing' priority=2 summary='Refund not received' order_id=None

bad: str = '{"category": "refund", "priority": 9, "summary": "hi"}'  # three mistakes
try:  # catch validation failure
    Ticket.model_validate_json(bad)  # will raise
except ValidationError as e:  # pydantic's error type
    print(e.error_count())  # how many problems
    # Output: 3
    for er in e.errors():  # list of dicts
        print(er["loc"], er["type"])  # which field, what rule
    # Output:
    # ('category',) literal_error
    # ('priority',) less_than_equal
    # ('summary',) string_too_short

schema: dict = Ticket.model_json_schema()  # JSON schema to paste in the prompt
print(list(schema["properties"]), schema["required"])  # field names and required ones
# Output: ['category', 'priority', 'summary', 'order_id'] ['category', 'priority', 'summary']
print(schema["properties"]["priority"])  # constraints became schema keywords
# Output: {'maximum': 5, 'minimum': 1, 'title': 'Priority', 'type': 'integer'}
print(t.model_dump(exclude_none=True))  # back to a plain dict without None values
# Output: {'category': 'billing', 'priority': 2, 'summary': 'Refund not received'}
```

## 💻 Code Example — Advanced
```python
# Production style: structured call with JSON extraction + validation retry loop
import json  # to dump the schema
from typing import Callable, List, Literal, Type, TypeVar  # type hints
from pydantic import BaseModel, Field, ValidationError  # pydantic v2

T = TypeVar("T", bound=BaseModel)  # any pydantic model class


class Invoice(BaseModel):  # what we want from the LLM
    vendor: str  # required text
    total: float = Field(gt=0)  # must be positive
    currency: Literal["INR", "USD"] = "INR"  # limited choices with default
    items: List[str] = []  # pydantic copies mutable defaults safely


def fake_llm(prompt: str, attempt: int) -> str:  # stand-in for a real API call
    if attempt == 0:  # first try: invalid JSON (single quotes) plus chatter
        return "Sure! Here you go: {'vendor': 'Zomato', total: -5}"  # broken
    if attempt == 1:  # second try: valid JSON but total is negative
        return '```json\n{"vendor": "Zomato", "total": -5}\n```'  # rule violation
    return '```json\n{"vendor": "Zomato", "total": 499.5, "items": ["biryani"]}\n```'  # good


def extract_json(text: str) -> str:  # cut out the {...} part
    start, end = text.find("{"), text.rfind("}")  # first { and last }
    if start == -1 or end == -1:  # nothing found
        raise ValueError("no JSON object found")  # let the retry loop handle it
    return text[start:end + 1]  # only the JSON text


def structured_call(model: Type[T], llm: Callable[[str, int], str], prompt: str, retries: int = 3) -> T:
    schema: str = json.dumps(model.model_json_schema())  # schema goes in the prompt
    full: str = f"{prompt}\nReturn ONLY JSON matching: {schema}"  # final prompt
    last_error: str = ""  # remember the last problem
    for attempt in range(retries):  # bounded retries, never loop forever
        hint: str = f"\nFix this error: {last_error}" if last_error else ""  # feed error back
        reply: str = llm(full + hint, attempt)  # call the model
        try:  # parse + validate
            return model.model_validate_json(extract_json(reply))  # success path
        except (ValidationError, ValueError) as exc:  # bad output
            last_error = str(exc).splitlines()[0]  # short error for the next prompt
            print(f"attempt {attempt} failed: {last_error}")  # log it
    raise RuntimeError(f"LLM never produced valid {model.__name__}")  # give up loudly


print(structured_call(Invoice, fake_llm, "Extract the invoice"))  # runs the loop
# Output:
# attempt 0 failed: 1 validation error for Invoice
# attempt 1 failed: 1 validation error for Invoice
# vendor='Zomato' total=499.5 currency='INR' items=['biryani']
```

---

## 🟠 JavaScript vs Python Comparison
In JavaScript the same job is done with Zod (`z.object({...}).parse(data)`). Pydantic is the Python equivalent, but the model is a class, and the type hints are real validators at runtime.

```python
# Python (Pydantic v2)
from pydantic import BaseModel, Field  # import
class User(BaseModel):  # define schema as a class
    name: str  # required string
    age: int = Field(ge=0)  # non-negative integer
u = User.model_validate({"name": "Asha", "age": "30"})  # "30" coerced to 30
print(u.age + 1)  # 31
```
```javascript
// JavaScript (Zod)
import { z } from "zod";
const User = z.object({ name: z.string(), age: z.coerce.number().min(0) });
const u = User.parse({ name: "Asha", age: "30" });
console.log(u.age + 1); // 31
```

Key differences: Zod separates schema and TypeScript type (`z.infer`); Pydantic's class is both. Pydantic v2 core is written in Rust so it is very fast. Pydantic is lax by default ("30" becomes 30); use `strict=True` or `ConfigDict(strict=True)` to forbid coercion.

---

## 🟠 FastAPI Connection
FastAPI is built on Pydantic: request bodies, response models and the OpenAPI docs all come from `BaseModel`. For AI endpoints, use one model for the HTTP request and another for the LLM's structured reply, then return only the safe fields with `response_model`.

```python
# FastAPI + Pydantic for an AI ticket classifier (pip install fastapi httpx)
from typing import Literal  # literal choices
from fastapi import FastAPI  # app
from fastapi.testclient import TestClient  # to test without a server
from pydantic import BaseModel, Field  # models

app: FastAPI = FastAPI()  # create app


class ComplaintIn(BaseModel):  # request body
    text: str = Field(min_length=3)  # reject empty complaints with 422


class TicketOut(BaseModel):  # response body and also LLM contract
    category: Literal["billing", "bug", "other"]  # fixed labels
    priority: int = Field(ge=1, le=5)  # 1..5


@app.post("/classify", response_model=TicketOut)  # response is validated too
def classify(body: ComplaintIn) -> TicketOut:  # body is already validated
    llm_json: str = '{"category": "billing", "priority": 2}'  # pretend LLM reply
    return TicketOut.model_validate_json(llm_json)  # validate model output


client: TestClient = TestClient(app)  # in-process client
print(client.post("/classify", json={"text": "refund?"}).json())  # good request
# Output: {'category': 'billing', 'priority': 2}
print(client.post("/classify", json={"text": ""}).status_code)  # bad request
# Output: 422
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trusting `json.loads` on LLM text
✅ Correct: Extract the JSON, then validate with a model

```python
# Wrong - crashes on fences or missing keys
# data = json.loads(reply); total = data["total"] * 2

# Right - one validated object or a clear error
# inv = Invoice.model_validate_json(extract_json(reply))
```

❌ Mistake 2: Using Pydantic v1 names in v2
✅ Correct: use `model_validate`, `model_dump`, `field_validator`

```python
# Wrong (v1, deprecated in v2): Model.parse_obj(d), m.dict(), @validator
# Right (v2): Model.model_validate(d), m.model_dump(), @field_validator("x")
```

❌ Mistake 3: Retrying forever or with no feedback
✅ Correct: cap retries and send the validation error back to the model

```python
# Wrong: while True: ask again with the same prompt
# Right: for attempt in range(3): include the last error in the next prompt
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from pydantic import BaseModel
class M(BaseModel):
    n: int
    ok: bool = False
print(M(n="5"))
print(M(n=5.0))
print(M(n="1", ok="yes"))
try:
    M(n=5.7)
except Exception as e:
    print(type(e).__name__)
```

**Answer**:
```
n=5 ok=False
n=5 ok=False
n=1 ok=True
ValidationError
```
Pydantic v2 in default (lax) mode coerces `"5"` and `5.0` to `5`, and `"yes"` to `True`. But `5.7` has a fractional part, so converting to int would lose data and it raises `ValidationError`.

---

## ⚫ Interview Questions + Answers

Q1: Why validate LLM output at all?
A1: LLMs are probabilistic. Output can have wrong types, missing keys or invented labels. Validation turns "maybe valid text" into a typed object or a clear error.

Q2: What is the difference between `model_validate` and `model_validate_json`?
A2: `model_validate` takes Python objects (dict). `model_validate_json` takes a JSON string and parses plus validates in one Rust step, which is faster and gives better errors for invalid JSON.

Q3: How do you give the schema to the LLM?
A3: `Model.model_json_schema()`. Providers also accept it directly: OpenAI structured outputs (`response_format`) and tool/function definitions.

Q4: Lax vs strict mode?
A4: Lax coerces compatible types (`"5"` to 5). Strict refuses (`ConfigDict(strict=True)` or `Field(strict=True)`). Use strict for money or IDs.

Q5: How do you handle a bad reply?
A5: Catch `ValidationError`, put the error text in the next prompt, retry a few times, then fail with a clear exception.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Parsing LLM JSON, tool arguments or function calls
- Defining API request and response bodies in FastAPI
- Loading settings (`pydantic-settings`) and config files

❌ Avoid when:
- You need maximum speed on millions of tiny rows (use dataclasses or plain dicts)
- Data is already trusted and typed internally

---

## 📊 Visual Diagram

```
 prompt + schema ──► LLM ──► raw text
                               │ extract_json()
                               ▼
                     model_validate_json()
                      │               │
                   valid           ValidationError
                      │               │
                typed object     error -> next prompt (retry <= N)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BaseModel | Class that validates its fields | Validation वाली base class |
| Field | Adds constraints (ge, le, min_length) | Field पर नियम लगाना |
| Literal | Only fixed values allowed | सिर्फ तय values |
| Coercion | Auto type conversion ("5" to 5) | अपने-आप type बदलना |
| ValidationError | Error listing every bad field | गलत fields की सूची वाला error |
| JSON schema | Machine-readable description of the shape | Data के ढाँचे का विवरण |

---

## ⚡ 3-Line Summary
English: Pydantic defines the typed contract for LLM output. Generate the schema for the prompt, parse with `model_validate_json`, and retry with the error message on failure. FastAPI uses the same models for requests and responses.
Hindi: Pydantic LLM output का typed contract बनाता है। Prompt के लिए schema बनाएँ, `model_validate_json` से parse करें, और fail होने पर error के साथ retry करें। FastAPI requests और responses के लिए यही models इस्तेमाल करता है।

---

## ➡️ Next Topic
**400. FastAPI for AI APIs** — streaming, async LLM calls, timeouts and rate limits.
