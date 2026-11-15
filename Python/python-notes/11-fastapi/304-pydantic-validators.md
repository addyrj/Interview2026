---

# 304. Pydantic Validators
# हिंदी में: Pydantic Validators (अपने नियम से data जाँचना)

---

## 🔵 Simple Definition (English)
Validators are your own functions that Pydantic runs while building a model. `@field_validator` checks or changes one field, `@model_validator` checks several fields together, and `AfterValidator` / `BeforeValidator` attach reusable rules to a type. If a validator raises `ValueError`, the data is rejected with a clear error.

## 🔵 सरल परिभाषा (Hindi)
Validators आपके अपने functions हैं जिन्हें Pydantic model बनाते समय चलाता है। `@field_validator` एक field को जाँचता या बदलता है, `@model_validator` कई fields को साथ में जाँचता है, और `AfterValidator` / `BeforeValidator` किसी type से दोबारा इस्तेमाल होने वाले नियम जोड़ते हैं। Validator `ValueError` उठाए तो data साफ error के साथ अस्वीकार हो जाता है।

---

## 🔴 Problem it Solves
Built-in constraints (`min_length`, `ge`, `pattern`) cover simple checks. Real business rules need more: phone must have exactly 10 digits after removing spaces, `end_date` must be after `start_date`, password and confirm password must match, usernames must be lower-cased. Without validators these checks leak into every endpoint.

## 🔴 यह क्यों बना? (Hindi)
Built-in constraints (`min_length`, `ge`, `pattern`) सरल जाँच के लिए हैं। असली business नियमों को ज़्यादा चाहिए: spaces हटाने के बाद phone में ठीक 10 अंक हों, `end_date`, `start_date` के बाद हो, password और confirm password मेल खाएँ, username lowercase हो। Validators के बिना ये जाँचें हर endpoint में बिखर जाती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client data arrives: dict / JSON
Step 2 → mode="before" validators run first on the RAW value (can clean: strip, parse)
Step 3 → Pydantic does its own type conversion and constraints (int, str, Field rules)
Step 4 → mode="after" (default) field validators run on the converted, typed value
Step 5 → If every field is OK, model validators (mode="after") run on the whole object
Step 6 → raise ValueError("message") -> collected into ValidationError (422 in FastAPI)
Step 7 → Return the (possibly changed) value; Pydantic stores it in the model
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Client का data आता है: dict / JSON
Step 2 → mode="before" validators कच्चे मान पर पहले चलते हैं (strip, parse जैसी सफाई)
Step 3 → Pydantic अपना type conversion और constraints (int, str, Field नियम) करता है
Step 4 → mode="after" (default) field validators बदले हुए, typed मान पर चलते हैं
Step 5 → हर field ठीक हो तो model validators (mode="after") पूरे object पर चलते हैं
Step 6 → raise ValueError("message") -> ValidationError में जमा होता है (FastAPI में 422)
Step 7 → मान लौटाएँ (बदला हुआ भी चलेगा); Pydantic उसे model में रखता है
```

---

## 🟡 Real World Example
A Razorpay-like signup form: username is trimmed and lower-cased, the phone number is normalised to 10 digits, seats must be even for a table booking, the end date cannot be earlier than the start date, and the two password fields must match. All of that lives in one model, so every endpoint that uses `Signup` gets the same rules.

## 🟡 Real Example Hindi mein
Razorpay जैसे signup form में: username trim और lowercase होता है, phone number 10 अंकों में normalise होता है, table booking में seats सम (even) होनी चाहिए, end date, start date से पहले नहीं हो सकती, और दोनों password fields मेल खाने चाहिए। यह सब एक model में रहता है, इसलिए `Signup` इस्तेमाल करने वाला हर endpoint वही नियम पाता है।

---

## 💻 Code Example — Basic
```python
# Basic validators (verified: pydantic 2.14, Python 3.13)
from pydantic import BaseModel, ValidationError, field_validator  # core pieces


class User(BaseModel):  # model with one custom rule
    name: str  # plain string field
    age: int  # integer field

    @field_validator("name")  # run for the field "name"
    @classmethod  # field validators are classmethods in Pydantic v2
    def name_not_blank(cls, v: str) -> str:  # receives the value, returns the value
        v = v.strip()  # clean the value
        if not v:  # business rule
            raise ValueError("name must not be blank")  # reject with a message
        return v.title()  # returned value replaces the original

    @field_validator("age")  # second rule on age
    @classmethod
    def age_in_range(cls, v: int) -> int:
        if not 0 <= v <= 120:  # allowed range
            raise ValueError("age must be between 0 and 120")  # reject
        return v  # accept unchanged


print(User(name="  asha  ", age="30"))  # cleaned name, "30" -> 30
# Output: name='Asha' age=30
try:  # try invalid data
    User(name="   ", age=200)  # both fields are bad
except ValidationError as e:  # Pydantic collects ALL field errors
    for err in e.errors():  # each error is a dict
        print(err["loc"], "|", err["msg"])  # location and message
# Output:
# ('name',) | Value error, name must not be blank
# ('age',) | Value error, age must be between 0 and 120
```

## 💻 Code Example — Advanced
```python
# Production style: before/after, reusable Annotated validators, model validator (verified)
from datetime import date  # date type
from typing import Annotated, Any, Self  # Self needs Python 3.11+
from pydantic import (  # imports for validators
    AfterValidator, BeforeValidator, BaseModel, Field, ValidationError,
    field_validator, model_validator,
)


def strip_str(v: Any) -> Any:  # BEFORE validator: runs on raw input
    return v.strip() if isinstance(v, str) else v  # only touch strings


def must_be_even(v: int) -> int:  # AFTER validator: runs on a real int
    if v % 2:  # odd number
        raise ValueError("must be even")  # reject
    return v  # accept


class Signup(BaseModel):  # one model, many rules
    username: Annotated[str, BeforeValidator(strip_str), Field(min_length=3)]  # trim, then length
    password: str
    confirm: str
    phone: str
    seats: Annotated[int, AfterValidator(must_be_even)] = 2  # reusable rule via Annotated
    start: date  # "2026-01-01" string converted to date
    end: date

    @field_validator("phone")  # normalise phone number
    @classmethod
    def phone_ok(cls, v: str) -> str:
        digits: str = "".join(ch for ch in v if ch.isdigit())  # keep digits only
        if len(digits) != 10:  # Indian mobile number length
            raise ValueError("phone must have 10 digits")  # reject
        return digits  # store the clean version

    @field_validator("username", mode="after")  # runs after the constraints above
    @classmethod
    def lower(cls, v: str) -> str:
        return v.lower()  # usernames are case-insensitive

    @model_validator(mode="after")  # runs after ALL fields are valid
    def check(self) -> Self:  # gets the full model instance
        if self.password != self.confirm:  # cross-field rule 1
            raise ValueError("passwords do not match")
        if self.end < self.start:  # cross-field rule 2
            raise ValueError("end before start")
        return self  # must return the instance


ok = Signup(  # valid data with messy input
    username="  Aditya ", password="s3cret", confirm="s3cret",
    phone="98765-43210", start="2026-01-01", end="2026-01-05",
)
print(ok.model_dump())  # all values cleaned and typed
# Output: {'username': 'aditya', 'password': 's3cret', 'confirm': 's3cret', 'phone': '9876543210', 'seats': 2, 'start': datetime.date(2026, 1, 1), 'end': datetime.date(2026, 1, 5)}

try:  # field errors first
    Signup(username="ab", password="a", confirm="b", phone="12", seats=3,
           start="2026-02-01", end="2026-01-01")
except ValidationError as e:
    print(e.error_count())  # field errors stop the model validator
    # Output: 3
    for x in e.errors():  # list them
        print(x["loc"], x["type"], "|", x["msg"])
    # Output:
    # ('username',) too_short | Value should have at least 3 items after validation, not 2
    # ('phone',) value_error | Value error, phone must have 10 digits
    # ('seats',) value_error | Value error, must be even

try:  # fields are fine, the model validator now runs
    Signup(username="abc", password="a", confirm="b", phone="1234567890",
           start="2026-02-01", end="2026-01-01")
except ValidationError as e:
    for x in e.errors():
        print(x["loc"], x["type"], "|", x["msg"])
    # Output: () value_error | Value error, passwords do not match
```

---

## 🟠 JavaScript vs Python Comparison
In zod you attach rules with `.refine()` and `.transform()`. Pydantic's `field_validator` ~ `refine` on one field, `model_validator` ~ `superRefine` on the whole object, and `BeforeValidator` ~ `z.preprocess`.

```python
# Python (Pydantic)
class Signup(BaseModel):
    password: str
    confirm: str

    @model_validator(mode="after")
    def match(self) -> Self:
        if self.password != self.confirm:
            raise ValueError("passwords do not match")
        return self
```
```javascript
// JavaScript (zod)
const Signup = z.object({ password: z.string(), confirm: z.string() })
  .refine(d => d.password === d.confirm, {
    message: 'passwords do not match',
    path: ['confirm'],
  });
```

Key differences: zod gives the error a `path` you choose; Pydantic reports a model-level error with empty `loc` `()` unless you raise from a field validator. In Pydantic you may also return a changed value (`transform`) from the same function.

---

## 🟠 FastAPI Connection
FastAPI request models are Pydantic models, so validators run automatically before your endpoint. A `ValueError` inside a validator becomes a 422 response, with the message in `detail[].msg`. Keep validators pure (no database calls); do database checks (like "email already exists") in the endpoint or a dependency, returning 409.

```python
# FastAPI: validator error becomes a 422 (needs: pip install fastapi httpx pydantic)
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # client
from pydantic import BaseModel, field_validator  # validators

app: FastAPI = FastAPI()  # app


class Booking(BaseModel):  # request body
    seats: int

    @field_validator("seats")  # business rule
    @classmethod
    def max_ten(cls, v: int) -> int:
        if v > 10:  # group bookings need a call
            raise ValueError("max 10 seats online")
        return v


@app.post("/book")  # endpoint
def book(b: Booking) -> dict[str, int]:
    return {"seats": b.seats}  # reached only when valid


r = TestClient(app).post("/book", json={"seats": 11})  # violates the rule
print(r.status_code, r.json()["detail"][0]["msg"])  # 422 Value error, max 10 seats online
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `@classmethod` or forgetting to return the value
✅ Correct: Always `@field_validator(...)` then `@classmethod`, and `return v`.

```python
# Wrong: no return -> the field becomes None
@field_validator("name")
@classmethod
def check(cls, v): 
    if not v: raise ValueError("blank")
# Right
    return v
```

❌ Mistake 2: Raising `ValidationError` or using `assert`
✅ Correct: Raise `ValueError` (or `AssertionError`) only. Pydantic wraps it. Asserts disappear under `python -O`, so prefer `ValueError`.

```python
# Wrong
assert v > 0, "must be positive"           # removed with python -O
# Right
if v <= 0: raise ValueError("must be positive")
```

❌ Mistake 3: Cross-field checks inside a field validator that depend on a field not yet validated
✅ Correct: Use `@model_validator(mode="after")` for rules involving several fields. Note it will NOT run if any field already failed (shown above: 3 field errors, no model-level error).

---

## 🧠 Tricky Interview Question

**Q**: A model has a field validator that strips the name and a `min_length=3` constraint. In which order do things run for `Annotated[str, BeforeValidator(strip_str), Field(min_length=3)]` with input `"  ab  "`?

```python
class M(BaseModel):
    username: Annotated[str, BeforeValidator(strip_str), Field(min_length=3)]

M(username="  ab  ")
```

**Answer**:
```
BeforeValidator strips -> "ab"
Field(min_length=3) is checked on "ab" -> fails: too_short
```
So `"  ab  "` (6 characters raw) is rejected, because the before-validator runs first and cleans the value before constraints apply. Order matters: `before` -> Pydantic type/constraint checks -> `after` validators -> model validators. (From the run above, input `"ab"` gave `too_short`.) A common follow-up: the model-level validator never runs when any field fails.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `mode="before"` and `mode="after"`?
A1: `before` receives the raw input (any type) and runs before Pydantic's conversion. `after` receives the already converted and constrained value, so it is type safe and the usual choice.

Q2: field_validator vs model_validator?
A2: `field_validator` handles one field. `model_validator` sees the whole model (after mode: the instance; before mode: the raw dict) and is used for cross-field rules like password matching.

Q3: How do you reuse a rule across many models?
A3: Put it in a function and attach with `Annotated[int, AfterValidator(fn)]`, or define a type alias once (`EvenInt = Annotated[int, AfterValidator(must_be_even)]`).

Q4: How does Pydantic v2 differ from v1 here?
A4: v1 used `@validator` and `@root_validator`; v2 uses `@field_validator` (with `@classmethod`) and `@model_validator`. The v1 names still exist but are deprecated.

Q5: Should validators call the database?
A5: Avoid it. Validators should be fast, pure and testable. Do uniqueness checks in the service layer and return 409 Conflict.

---

## 🔷 When to Use + When Not to Use

✅ Use validators for:
- Normalising input (strip, lower, digits only)
- Business rules on one or several fields (date ranges, matching passwords)
- Reusing the same rule across models with `Annotated`

❌ Avoid validators for:
- Simple rules that `Field(ge=, le=, min_length=, pattern=)` already handles
- Database or network checks
- Heavy computation (runs on every request)

---

## 📊 Visual Diagram

```
 raw input
    │
    ▼
 BeforeValidator / field_validator(mode="before")   clean raw value
    │
    ▼
 Pydantic type conversion + Field constraints        "30" -> 30, min_length ...
    │
    ▼
 AfterValidator / field_validator(mode="after")      rule on typed value
    │
    ▼  (all fields passed?)
 model_validator(mode="after")                       cross-field rules
    │
    ▼
 valid model   (any ValueError above ─► ValidationError ─► 422 in FastAPI)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| field_validator | Rule for one field | एक field का नियम |
| model_validator | Rule for the whole model | पूरे model का नियम |
| mode before/after | Runs before/after type conversion | conversion से पहले/बाद |
| ValidationError | Collected errors from Pydantic | Pydantic के जमा किए errors |
| Annotated | Attach rules to a type | type के साथ नियम जोड़ना |
| Normalise | Convert to one standard form | एक मानक रूप में बदलना |

---

## ⚡ 3-Line Summary
English: Use `@field_validator` for one field, `@model_validator(mode="after")` for cross-field rules and `Annotated[..., AfterValidator(fn)]` for reusable rules. Raise `ValueError`, return the value, and remember model validators run only after all fields pass.
Hindi: एक field के लिए `@field_validator`, कई fields के नियम के लिए `@model_validator(mode="after")`, और दोबारा इस्तेमाल के लिए `Annotated[..., AfterValidator(fn)]` इस्तेमाल करें। `ValueError` उठाएँ, मान लौटाएँ, और याद रखें कि model validators तभी चलते हैं जब सभी fields पास हो जाएँ।

---

## ➡️ Next Topic
**305. Pydantic v1 vs v2** — what changed, the new method names and how to migrate.
