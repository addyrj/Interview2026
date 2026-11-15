---

# 110. Pydantic Models
# हिंदी में: Pydantic Models (Validation वाले Data Models)

---

## 🔵 Simple Definition (English)
Pydantic is a library where you declare a class with type hints (`class User(BaseModel)`) and it validates and converts incoming data to those types at runtime. Bad data raises a clear `ValidationError`. This note uses Pydantic v2 (current). FastAPI is built on it.

## 🔵 सरल परिभाषा (Hindi)
Pydantic एक library है जिसमें आप type hints वाली class (`class User(BaseModel)`) declare करते हो और वह आने वाले data को runtime पर उन्हीं types में validate और convert करती है। गलत data पर साफ `ValidationError` आता है। यह note Pydantic v2 (current) पर है। FastAPI इसी पर बना है।

---

## 🔴 Problem it Solves
Python type hints are NOT enforced at runtime: `age: int = "abc"` runs without complaint. Data from outside (JSON from a mobile app, environment variables, a database row) is untrusted and often has wrong types, missing keys or bad values. Writing `if not isinstance(...)` checks by hand for every field is long and error-prone. Pydantic turns the type hints into real validation, with conversion (`"42"` becomes `42`) and clear error messages that tell the client exactly what is wrong.

## 🔴 यह क्यों बना? (Hindi)
Python type hints runtime पर enforce नहीं होते: `age: int = "abc"` बिना शिकायत चल जाता है। बाहर से आने वाला data (mobile app का JSON, environment variables, database row) untrusted होता है और अक्सर गलत type, missing keys या गलत values वाला होता है। हर field के लिए हाथ से `if not isinstance(...)` लिखना लंबा और गलती-प्रवण है। Pydantic type hints को असली validation बना देता है, conversion (`"42"` से `42`) के साथ, और साफ error messages जो client को बताते हैं कि क्या गलत है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You subclass BaseModel and annotate fields (name: str, age: int)
Step 2 → At class creation Pydantic builds a validator (Rust core: pydantic-core)
Step 3 → User(**data) or User.model_validate(data) runs the validator
Step 4 → Each field is checked and coerced (lax mode): "42" -> 42
Step 5 → Failures are collected, then ONE ValidationError lists all of them
Step 6 → On success you get a typed object; use model_dump() to get a dict back

Key v2 names: model_validate, model_dump, model_dump_json,
              field_validator, model_validator, ConfigDict
(v1 names parse_obj, dict, validator are deprecated.)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप BaseModel को subclass करते हो और fields annotate करते हो (name: str, age: int)
Step 2 → Class बनते समय Pydantic validator बनाता है (Rust core: pydantic-core)
Step 3 → User(**data) या User.model_validate(data) validator चलाता है
Step 4 → हर field check और coerce होता है (lax mode): "42" -> 42
Step 5 → Failures जमा होते हैं, फिर एक ही ValidationError सबकी list देता है
Step 6 → Success पर typed object मिलता है; dict वापस पाने को model_dump() use करें

मुख्य v2 नाम: model_validate, model_dump, model_dump_json,
              field_validator, model_validator, ConfigDict
(v1 के नाम parse_obj, dict, validator deprecated हैं।)
```

---

## 🟡 Real World Example
Razorpay-style webhook: the payment gateway posts JSON `{"order_id": "ord_1", "amount": "49900", "currency": "inr"}`. A Pydantic model checks that `amount` is a positive integer, uppercases the currency and rejects unknown shapes before any money logic runs. A signup API validates email format and password length. An AI app uses Pydantic models to validate the JSON that an LLM returns (structured output) before using it.

## 🟡 Real Example Hindi mein
Razorpay जैसा webhook: payment gateway JSON `{"order_id": "ord_1", "amount": "49900", "currency": "inr"}` भेजता है। Pydantic model check करता है कि `amount` positive integer है, currency को uppercase करता है और पैसे वाला logic चलने से पहले गलत shape reject करता है। Signup API email format और password length validate करती है। AI app LLM के लौटाए JSON (structured output) को use करने से पहले Pydantic से validate करती है।

---

## 💻 Code Example — Basic
```python
# Basic Pydantic v2 examples
from pydantic import BaseModel, ValidationError   # core pieces


class User(BaseModel):                            # a model is a class with type hints
    name: str                                     # required string
    age: int                                      # required integer
    email: str | None = None                      # optional, default None
    is_active: bool = True                        # default value


u: User = User(name="Amit", age="25")             # "25" (str) is converted to 25 (int)
print(u)                                          # readable repr
print(u.age, type(u.age).__name__)                # 25 int
print(u.model_dump())                             # object -> dict
print(u.model_dump_json())                        # object -> JSON string

data: dict = {"name": "Neha", "age": 30, "is_active": False}   # dict from outside
print(User.model_validate(data))                  # dict -> validated object
print(User.model_validate_json('{"name": "Ravi", "age": 41}')) # JSON string -> object

try:                                              # invalid data
    User(name="Bad", age="abc")                   # age is not a number
except ValidationError as e:                      # collect all errors
    print(e.error_count(), "error")               # how many problems
    print(e.errors()[0]["loc"], e.errors()[0]["type"])   # where and what kind

try:                                              # missing field
    User(age=5)                                   # name is required
except ValidationError as e:
    print(e.errors()[0]["msg"])                   # Field required

# Output:
# name='Amit' age=25 email=None is_active=True
# 25 int
# {'name': 'Amit', 'age': 25, 'email': None, 'is_active': True}
# {"name":"Amit","age":25,"email":null,"is_active":true}
# name='Neha' age=30 email=None is_active=False
# name='Ravi' age=41 email=None is_active=True
# 1 error
# ('age',) int_parsing
# Field required
```

## 💻 Code Example — Advanced
```python
# Production style: Field constraints, validators, nested models, config, serialization
from decimal import Decimal                       # money type, avoids float errors
from enum import Enum                             # fixed set of values
from typing import Annotated                      # attach constraints to a type

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

PositiveInt = Annotated[int, Field(gt=0)]         # reusable constrained type


class Currency(str, Enum):                        # allowed currencies only
    INR = "INR"                                   # Indian rupee
    USD = "USD"                                   # US dollar


class Address(BaseModel):                         # nested model
    city: str = Field(min_length=2)               # at least 2 characters
    pincode: str = Field(pattern=r"^\d{6}$")      # exactly 6 digits


class Payment(BaseModel):
    model_config = ConfigDict(                    # model-wide behaviour
        str_strip_whitespace=True,                # trim spaces in strings
        extra="forbid",                           # unknown keys -> error
        frozen=False,                             # allow changes after creation
    )

    order_id: str = Field(min_length=3, max_length=40)       # length limits
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)   # positive money
    currency: Currency = Currency.INR             # enum with default
    quantity: PositiveInt = 1                     # reuse the constrained type
    address: Address                              # nested validation
    note: str | None = Field(default=None, max_length=100)

    @field_validator("order_id")                  # runs on one field
    @classmethod
    def must_start_with_ord(cls, v: str) -> str:  # v is already a str here
        if not v.startswith("ord_"):              # business rule
            raise ValueError("order_id must start with 'ord_'")
        return v                                  # return the (possibly changed) value

    @model_validator(mode="after")                # runs after all fields are valid
    def check_usd_limit(self) -> "Payment":
        if self.currency is Currency.USD and self.amount > 1000:   # cross-field rule
            raise ValueError("USD payments above 1000 need manual review")
        return self                               # must return the model


good = Payment.model_validate({
    "order_id": "  ord_77 ", "amount": "499.50", "currency": "INR",
    "address": {"city": "Pune", "pincode": "411001"},
})
print(good.order_id, good.amount, good.currency)
print(good.model_dump())
print(good.model_dump(mode="json", exclude={"address"}))
print(Payment.model_json_schema()["required"])

def show(data: dict) -> None:
    try:
        Payment.model_validate(data)
    except ValidationError as e:
        for err in e.errors():
            print(".".join(str(p) for p in err["loc"]) or "<model>", "->", err["msg"])

show({"order_id": "x1", "amount": "-5", "address": {"city": "P", "pincode": "12"}, "hack": 1})
show({"order_id": "ord_1", "amount": "2000", "currency": "USD", "address": {"city": "NYC", "pincode": "100010"}})

# Output:
# ord_77 499.50 Currency.INR
# {'order_id': 'ord_77', 'amount': Decimal('499.50'), 'currency': <Currency.INR: 'INR'>, 'quantity': 1, 'address': {'city': 'Pune', 'pincode': '411001'}, 'note': None}
# {'order_id': 'ord_77', 'amount': '499.50', 'currency': 'INR', 'quantity': 1, 'note': None}
# ['order_id', 'amount', 'address']
# order_id -> String should have at least 3 characters
# amount -> Input should be greater than 0
# address.city -> String should have at least 2 characters
# address.pincode -> String should match pattern '^\d{6}$'
# hack -> Extra inputs are not permitted
# <model> -> Value error, USD payments above 1000 need manual review
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (Pydantic) | JavaScript |
|---------|-------------------|-----------|
| Runtime validation | `BaseModel` | Zod / Joi / Yup |
| Static types only | type hints (not enforced) | TypeScript (erased at runtime) |
| Parse + coerce | `"42"` -> `42` in lax mode | `z.coerce.number()` |
| Schema to JSON Schema | `model_json_schema()` | `zod-to-json-schema` |
| Errors | one `ValidationError` with all issues | `ZodError` with `issues` |

```python
# Python way - Pydantic
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    name: str                                 # required string
    age: int                                  # required integer

try:
    User(name="A", age="x")                   # bad age
except ValidationError as e:
    print(e.errors()[0]["loc"])               # ('age',)
```
```javascript
// JavaScript way - Zod (TypeScript projects)
import { z } from "zod";
const User = z.object({ name: z.string(), age: z.number() });   // schema, separate from the TS type
const result = User.safeParse({ name: "A", age: "x" });         // no throw, returns result
console.log(result.success, result.error?.issues[0].path);      // false [ 'age' ]
```

Key difference: in TypeScript the types vanish at runtime, so you need a second schema (Zod) and then infer the type from it. In Python the class itself is both the type and the validator.

---

## 🟠 FastAPI Connection
Pydantic is the heart of FastAPI. A parameter annotated with a model is read from the JSON body and validated automatically; `response_model` filters the output (for example hides `password`); and invalid input becomes an HTTP 422 response with the error list. OpenAPI docs (`/docs`) are generated from the same models.

```python
# FastAPI example - request model, response model, automatic 422
from fastapi import FastAPI                       # app
from fastapi.testclient import TestClient         # testing without a server
from pydantic import BaseModel, Field            # models and constraints


class SignupIn(BaseModel):                        # what the client sends
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.\w+$")   # simple email check
    password: str = Field(min_length=8)           # minimum length


class UserOut(BaseModel):                         # what we send back (no password!)
    id: int
    email: str


app: FastAPI = FastAPI()                          # create app


@app.post("/signup", response_model=UserOut, status_code=201)
def signup(body: SignupIn) -> dict:               # body is validated before this runs
    return {"id": 1, "email": body.email, "password": body.password}   # password is dropped


client: TestClient = TestClient(app)              # client
r = client.post("/signup", json={"email": "a@b.com", "password": "secret123"})
print(r.status_code, r.json())                    # password not leaked
r = client.post("/signup", json={"email": "bad", "password": "123"})
print(r.status_code, [e["loc"] for e in r.json()["detail"]])   # 422 with locations

# Output:
# 201 {'id': 1, 'email': 'a@b.com'}
# 422 [['body', 'email'], ['body', 'password']]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using v1 method names (`.dict()`, `.parse_obj()`, `@validator`)
✅ Correct: v2 names `model_dump()`, `model_validate()`, `@field_validator`

```python
from pydantic import BaseModel
class A(BaseModel):
    x: int
a = A(x=1)
# Wrong (deprecated in v2, emits a warning, removed in a later major version)
# a.dict()
# Right
print(a.model_dump())            # {'x': 1}
```

❌ Mistake 2: Assuming a model validates when you assign later
✅ Correct: turn on `validate_assignment=True` if you mutate models

```python
from pydantic import BaseModel, ConfigDict
class A(BaseModel):
    x: int
a = A(x=1)
a.x = "not a number"             # Wrong: accepted silently, no validation
print(repr(a.x))                 # 'not a number'
class B(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    x: int
b = B(x=1)
try:
    b.x = "not a number"         # Right: now it raises
except Exception as e:
    print(type(e).__name__)      # ValidationError
```

❌ Mistake 3: Mutable default confusion / expecting `None` to be allowed
✅ Correct: `x: int = None` does NOT make None valid for validation of explicit input; declare `int | None`

```python
from pydantic import BaseModel, ValidationError
class A(BaseModel):
    x: int = None                # Wrong: default None is not validated, but explicit None fails
try:
    A(x=None)
except ValidationError as e:
    print("A rejects None")      # A rejects None
class B(BaseModel):
    x: int | None = None         # Right
print(B(x=None))                 # x=None
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from pydantic import BaseModel

class M(BaseModel):
    a: int
    b: list[int] = []

m1, m2 = M(a="1"), M(a=2)
m1.b.append(9)
print(m1.a, m2.b)
print(M(a=True).a, M(a="  7 ").a)
try:
    M(a=1.5)
except Exception as e:
    print(type(e).__name__)
```
Answer: `1 []` then `1 7` then `ValidationError`. Unlike a plain class, Pydantic copies mutable defaults for each instance, so `m1.b.append(9)` does not leak into `m2` (m2.b is `[]`) - this is safe in Pydantic although it is a bug in normal classes and in dataclasses (which refuse it). In lax mode `"1"` becomes `1`, `True` becomes `1` (bool is an int subclass), and a string with whitespace like `"  7 "` is parsed as `7`. A float with a fractional part such as `1.5` is rejected for an `int` field, because converting would lose data.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between Pydantic v1 and v2?
A1: v2 has a Rust core (`pydantic-core`) that is roughly 5-50x faster, renamed API (`model_dump`, `model_validate`, `field_validator`, `ConfigDict`), stricter and more consistent validation, and `Annotated`-style constraints. v1 names still work with deprecation warnings in v2 but are being removed.

Q2: Pydantic vs dataclass vs TypedDict?
A2: Dataclass has no validation. TypedDict is only for static checkers (plain dict at runtime). Pydantic validates, converts types, parses JSON and generates schemas, at some performance and import cost. Use Pydantic at system boundaries.

Q3: What are lax mode and strict mode?
A3: Lax (default) converts compatible types: `"5"` to `5`. Strict mode (`strict=True` on the model/field or `StrictInt`) refuses conversion, so `"5"` fails for an int. Use strict for money or identifiers where silent conversion is dangerous.

Q4: How do you write custom validation?
A4: `@field_validator("name")` for one field (a classmethod; use `mode="before"` to run before parsing), `@model_validator(mode="after")` for cross-field rules. Raise `ValueError` (or `AssertionError`) and Pydantic wraps it into a `ValidationError`.

Q5: How do Pydantic models relate to FastAPI?
A5: FastAPI uses them for request body parsing, query/header validation, response filtering (`response_model`), and OpenAPI docs. Invalid input never reaches your function: FastAPI returns 422 automatically.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Validating external input (API bodies, webhooks, config, LLM JSON output)
- You need settings from environment variables (`pydantic-settings`)
- You want auto-generated JSON Schema / OpenAPI docs

❌ Avoid when:
- Millions of tiny internal objects in a hot loop (use dataclass with `slots=True`)
- Data is already trusted and typed
- You need a simple tuple-like record (use `NamedTuple`)
- You cannot afford the extra dependency in a tiny script

---

## 📊 Visual Diagram
```
 Raw input (JSON / dict / env)
         |
         v
  +------------------+     fail     +-------------------------+
  |  BaseModel       |------------->|  ValidationError        |
  |  type hints +    |              |  (all errors, with loc) |
  |  Field + validators|            +-------------------------+
  +------------------+                  FastAPI -> HTTP 422
         | ok
         v
  typed object  --model_dump()-->  dict  --model_dump_json()-->  JSON

 order inside a field:  before-validators -> type parse/coerce -> constraints -> after-validators
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BaseModel | Base class for Pydantic models | Pydantic models की base class |
| Validation | Checking data against rules | data को rules से जांचना |
| Coercion | Auto-converting types ("5" to 5) | type अपने-आप बदलना |
| `Field()` | Add constraints/defaults/metadata | constraints/defaults जोड़ना |
| Validator | Custom check function | अपनी check करने वाला function |
| ValidationError | Exception listing all problems | सभी समस्याएं बताने वाला exception |

---

## ⚡ 3-Line Summary
English: Pydantic turns type hints into real runtime validation and conversion. Bad input raises one `ValidationError` listing every problem. FastAPI uses it for request bodies, responses (`response_model`) and docs.
Hindi: Pydantic type hints को असली runtime validation और conversion बना देता है। गलत input पर एक `ValidationError` आता है जो हर समस्या बताता है। FastAPI इसे request body, responses (`response_model`) और docs के लिए use करता है।

---

## ➡️ Next Topic
**111. NamedTuple vs Dataclass** - when an immutable, tuple-like record is better than a mutable dataclass, and how to choose between them.
