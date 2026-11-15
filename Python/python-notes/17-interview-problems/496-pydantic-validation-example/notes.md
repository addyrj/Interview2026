---

# 496. Pydantic Validation Example
# हिंदी में: Pydantic Validation का Example (data को सही और साफ़ करना)

Full runnable solution: [main.py](main.py) (Pydantic v2: constraints, validators, nested models, error list, JSON parsing).

---

## 🔵 Simple Definition (English)
Pydantic turns a class with type hints into a validator: you pass raw data (dict/JSON) and get either a clean, typed object or a detailed `ValidationError`.

## 🔵 सरल परिभाषा (Hindi)
Pydantic type hints वाली class को validator बना देता है: आप raw data (dict/JSON) देते हैं और या तो साफ़, typed object मिलता है या विस्तृत `ValidationError`।

---

## 🔴 Problem it Solves
Data from users and other services is untrusted: strings instead of ints, missing keys, bad emails. Hand-written `if` checks are long, inconsistent and give poor error messages. Pydantic centralises rules in one declarative model.

## 🔴 यह क्यों बना? (Hindi)
Users और दूसरी services का data भरोसे लायक नहीं होता: int की जगह string, गायब keys, गलत emails। हाथ से लिखे `if` checks लंबे, असंगत होते हैं और error messages कमज़ोर। Pydantic सारे rules एक declarative model में रखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define BaseModel with typed fields and Field(...) constraints
Step 2 → Call Model(**data) or Model.model_validate(data) / model_validate_json(text)
Step 3 → Lax mode coerces ("29" -> 29); then constraints (ge, min_length, pattern) run
Step 4 → @field_validator runs per field; @model_validator(mode="after") sees whole model
Step 5 → All problems collected -> one ValidationError (e.errors() = list of dicts)
Step 6 → model_dump()/model_dump_json() export clean data (exclude secrets)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → typed fields और Field(...) constraints के साथ BaseModel बनाओ
Step 2 → Model(**data) या model_validate(data) / model_validate_json(text) बुलाओ
Step 3 → Lax mode बदलता है ("29" -> 29); फिर constraints (ge, min_length, pattern) चलते हैं
Step 4 → @field_validator हर field पर; @model_validator(mode="after") पूरे model पर
Step 5 → सारी गलतियाँ इकट्ठी -> एक ValidationError (e.errors() = dicts की list)
Step 6 → model_dump()/model_dump_json() साफ़ data निकालते हैं (secrets हटाकर)
```

---

## 🟡 Real World Example
A Razorpay-style signup/checkout API: the request body (name, email, amount, pincode) is validated before any DB or payment call. Wrong input returns a precise 422 listing every bad field, so the mobile app can highlight each one.

## 🟡 Real Example Hindi mein
Razorpay जैसी signup/checkout API: DB या payment call से पहले request body (name, email, amount, pincode) validate होती है। गलत input पर 422 आता है जिसमें हर गलत field दिखती है, ताकि mobile app हर एक को highlight कर सके।

---

## 💻 Code Example — Basic
```python
# Basic Pydantic v2 validation
from pydantic import BaseModel, Field, ValidationError  # core tools

class User(BaseModel):  # a validated record
    name: str  # required string
    age: int = Field(ge=18)  # integer, at least 18

u = User(name="Asha", age="29")  # "29" is coerced to int 29 in lax mode
print(u.age, type(u.age).__name__)  # value and its real type
try:
    User(name="Ravi", age=10)  # violates ge=18
except ValidationError as e:  # pydantic collects errors here
    print(e.errors()[0]["type"])  # machine-readable error type
# Output:
# 29 int
# greater_than_equal
```

## 💻 Code Example — Advanced
```python
# Excerpt from main.py: validators, nested model, strict config
class SignupRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")  # strip + reject unknown keys
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr  # needs `pip install email-validator`
    age: int = Field(ge=18, le=120)
    password: str = Field(min_length=8)
    confirm_password: str
    role: Literal["user", "admin"] = "user"
    address: Address | None = None  # nested model
    tags: list[str] = Field(default_factory=list)

    @field_validator("password")
    @classmethod
    def strong(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("password must contain a digit")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "SignupRequest":
        if self.password != self.confirm_password:
            raise ValueError("passwords do not match")
        return self
```
Real output of `python main.py` (Python 3.13.3, pydantic 2.14.3, email-validator installed):
```
Asha Rao 29 int Pune
user {'city': 'Pune', 'pincode': '411001'}
{"name":"Asha Rao","email":"asha@example.com","age":29,"role":"user","tags":[]}
7 errors
('name',) string_too_short
('email',) value_error
('age',) greater_than_equal
('password',) string_too_short
('address', 'city') string_too_short
('address', 'pincode') string_pattern_mismatch
('extra_field',) extra_forbidden
value_error | Value error, passwords do not match
42
all ok
```

---

## 🟠 JavaScript vs Python Comparison
JS validates with libraries like Zod/Joi/Yup; Pydantic is the Python equivalent but driven by type hints, so one class gives validation, parsing and docs.

```python
class User(BaseModel):  # schema + types in one
    age: int = Field(ge=18)
User.model_validate({"age": "20"})  # coerces and validates
```
```javascript
const User = z.object({ age: z.coerce.number().min(18) });  // Zod schema
User.parse({ age: "20" });  // coerces and validates
```

---

## 🟠 FastAPI Connection
FastAPI uses Pydantic for every request body and `response_model`. A failed validation automatically becomes HTTP 422 with the same `errors()` list.

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel, Field  # schema tools

app = FastAPI()  # app

class Payment(BaseModel):
    amount: int = Field(gt=0)  # must be positive
    upi: str = Field(pattern=r"^[\w.-]+@\w+$")  # simple UPI id check

@app.post("/pay")
def pay(p: Payment) -> dict[str, int]:  # invalid body -> 422 automatically
    return {"charged": p.amount}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using v1 names (`@validator`, `.dict()`, `Config` class) in v2 code.
✅ Correct: `@field_validator` + `@classmethod`, `model_dump()`, `model_config = ConfigDict(...)`.

```python
# Wrong (v1)
@validator("name")
def f(cls, v): ...
# Right (v2)
@field_validator("name")
@classmethod
def f(cls, v: str) -> str: ...
```

❌ Mistake 2: Forgetting to return the value in a validator (field becomes `None`).
✅ Correct: always `return v`.

❌ Mistake 3: Returning the password in the response.
✅ Correct: separate response model or `model_dump(exclude={"password"})`.

❌ Mistake 4: Assuming `EmailStr` works without `email-validator` installed (ImportError).
✅ Correct: `pip install "pydantic[email]"`.

---

## 🧠 Tricky Interview Question
```python
from pydantic import BaseModel

class M(BaseModel):
    n: int

print(M(n="5").n, M(n=5.0).n)
try:
    M(n=5.5)
except Exception as e:
    print(type(e).__name__)
```
Answer: Prints `5 5` then `ValidationError`. Lax mode coerces `"5"` and the whole float `5.0` to int, but refuses `5.5` because it would lose data. Use `strict=True` (model or Field) to forbid even `"5"`.

---

## ⚫ Interview Questions + Answers

Q1: Validation vs serialization in Pydantic?
A1: Validation turns input into typed objects (`model_validate`); serialization turns objects into dict/JSON (`model_dump`, `model_dump_json`).

Q2: Lax vs strict mode?
A2: Lax coerces compatible types (`"29"` to 29); strict requires exact types. Set per model with `ConfigDict(strict=True)` or per field.

Q3: `field_validator` vs `model_validator`?
A3: Field validators check/transform one field; model validators (`mode="before"` or `"after"`) see multiple fields, e.g. password match.

Q4: How do you reject unknown keys?
A4: `ConfigDict(extra="forbid")`; default is `ignore`.

Q5: Mutable defaults like `[]`?
A5: Pydantic copies defaults safely, but `Field(default_factory=list)` is the clearer, preferred style.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Validating external input (API bodies, config, env, LLM JSON output)
- You want one source of truth for types, rules and docs

❌ Avoid when:
- Hot loops with millions of tiny internal objects (use `dataclass`/`slots`)
- Data is already trusted and typed internally

---

## 📊 Visual Diagram
```
raw JSON/dict ──► coerce types ──► constraints ──► field_validators ──► model_validator
                                                                   │
                                          ok ◄─────────────────────┴──► ValidationError(list of errors)
   typed model ──► model_dump() / model_dump_json() ──► response
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Validation | Check data against rules | सत्यापन |
| Coercion | Auto type conversion | अपने-आप type बदलना |
| Validator | Custom check function | जाँच function |
| Constraint | Rule like ge, max_length | शर्त |
| Serialization | Object to dict/JSON | object से dict/JSON |
| Strict mode | No type conversion | कड़ा mode |

---

## ⚡ 3-Line Summary
English: Pydantic validates and cleans data from type hints.
English: Constraints, validators and nested models express rules declaratively.
English: Errors arrive together as one `ValidationError`; FastAPI maps it to 422.
Hindi: Pydantic type hints से data validate और साफ़ करता है।
Hindi: Constraints, validators और nested models से rules declarative लिखे जाते हैं।
Hindi: सारी errors एक `ValidationError` में आती हैं; FastAPI इसे 422 बना देता है।

---

## ➡️ Next Topic
497. SQLAlchemy Query Example: after validating data, we persist and query it in a database.

---
