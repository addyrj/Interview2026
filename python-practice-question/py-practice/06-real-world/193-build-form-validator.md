---

# Q193. Build Form Validator
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a `validate(data, schema)` where `schema` maps each field to a list of rule functions. Each rule returns an error message or `None`. Return a dict of `field -> [all error messages]`; an empty dict means valid.

```python
validate({"email": "bad"}, {"email": [required, pattern(...)]})
```

---

## 💡 Quick Concept (2 lines only)
Rules are small functions (closures) composed in a list per field. Collect ALL failures, not just the first, so users fix everything in one go.
हिंदी: हर rule एक छोटा function है जो error message या None देता है; सारी errors इकट्ठी करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import re  # regex rules
from typing import Any, Callable  # type hints

Rule = Callable[[Any], str | None]  # returns error message or None

def required(v: Any) -> str | None:
    return "required" if v in (None, "", [], {}) else None  # empty check
def min_len(n: int) -> Rule:
    return lambda v: None if v is None or len(str(v)) >= n else f"min length {n}"  # length rule
def pattern(rx: str, msg: str) -> Rule:
    return lambda v: None if v is None or re.fullmatch(rx, str(v)) else msg  # regex rule
def between(lo: int, hi: int) -> Rule:
    def rule(v: Any) -> str | None:
        try:
            return None if lo <= int(v) <= hi else f"must be {lo}-{hi}"  # range
        except (TypeError, ValueError):
            return "must be a number"  # not numeric
    return rule

def validate(data: dict[str, Any], schema: dict[str, list[Rule]]) -> dict[str, list[str]]:
    errors: dict[str, list[str]] = {}  # field -> messages
    for field, rules in schema.items():  # each field
        msgs = [m for r in rules if (m := r(data.get(field))) is not None]  # collect all failures (walrus)
        if msgs:
            errors[field] = msgs  # record
    return errors  # empty dict == valid

# ============================================
# TEST CASES
# ============================================
schema = {
    "email": [required, pattern(r"[^@\s]+@[^@\s]+\.\w+", "invalid email")],  # email rules
    "password": [required, min_len(8)],  # password rules
    "age": [between(18, 99)],  # age rule
}
print(validate({"email": "a@b.com", "password": "secret123", "age": "25"}, schema))  # Expected: {}
print(validate({"email": "bad", "password": "123", "age": "5"}, schema))  # Expected: {'email': ['invalid email'], 'password': ['min length 8'], 'age': ['must be 18-99']}
print(validate({}, schema))  # Expected: {'email': ['required'], 'password': ['required'], 'age': ['must be a number']}
```

---

## 🔍 Why This Works (3 lines max)
Rule factories (`min_len(8)`) return closures that capture their config, so rules are reusable and composable. The list comprehension with the walrus `:=` calls each rule once and keeps only real messages.
हिंदी: Rule factories closures लौटाते हैं; walrus `:=` से हर rule एक बार चलता है और सिर्फ असली errors बचती हैं।

---

## ⚡ Alternative Solution
```python
from pydantic import BaseModel, Field, ValidationError  # declarative validation

class Signup(BaseModel):
    email: str = Field(pattern=r"[^@\s]+@[^@\s]+\.\w+")  # regex check
    password: str = Field(min_length=8)  # length check
    age: int = Field(ge=18, le=99)  # range check

try:
    Signup(email="bad", password="123", age=5)  # invalid
except ValidationError as e:
    for err in e.errors():
        print(err["loc"][0], "->", err["msg"])  # Expected (3 lines, messages below)
        # email -> String should match pattern '[^@\s]+@[^@\s]+\.\w+'
        # password -> String should have at least 8 characters
        # age -> Input should be greater than or equal to 18
print(Signup(email="a@b.com", password="secret123", age="25"))  # Expected: email='a@b.com' password='secret123' age=25  (age coerced to int)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: stop at the first error, or validate with if/elif chains scattered everywhere (not run)
# if not email: return "required"
# elif "@" not in email: return "invalid"      # user fixes one error at a time

# ✅ Correct: data-driven rules, collect every error per field, return structured errors (field -> list)
# Also: validate on the server even if the frontend validates — never trust the client.
```

---

## 🎯 Interview Tip (1 line)
Say: "Rules as composable functions, collect all errors, and in real projects use Pydantic — same idea, declarative."

---

## 🔗 Related Questions
→ Q223 (Pydantic validation) | Q244 (walrus operator) | Q161 (closures) | Q232 (global error handlers)
