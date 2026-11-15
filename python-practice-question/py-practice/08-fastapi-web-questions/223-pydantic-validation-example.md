---

# Q223. Pydantic validation example
# Category: FASTAPI + WEB QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Create a `SignUp` model with length/range constraints, a single-field validator, and a cross-field password check. Show the 422 response FastAPI returns for bad input.

```python
@app.post('/signup')
def signup(data: SignUp): ...
```

---

## 💡 Quick Concept (2 lines only)
Pydantic v2: `Field(...)` for constraints, `@field_validator` for one field, `@model_validator` for several fields; FastAPI turns failures into a 422 with a list of errors.
हिंदी: Field से constraints, field_validator से एक field, model_validator से कई fields; fail पर 422।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

from typing import Annotated                      # Annotated
from fastapi import FastAPI                       # app
from fastapi.testclient import TestClient         # test client
from pydantic import BaseModel, Field, field_validator, model_validator  # validation


class SignUp(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=12)]  # length rules
    age: Annotated[int, Field(ge=18, le=120)]     # numeric range
    tags: list[str] = Field(default_factory=list, max_length=3)  # at most 3 tags
    password: str                                 # raw password
    confirm: str                                  # must match

    @field_validator("username")                  # check ONE field
    @classmethod
    def no_spaces(cls, v: str) -> str:
        if " " in v:                              # business rule
            raise ValueError("no spaces allowed") # becomes a 422 error
        return v.lower()                          # may also transform the value

    @model_validator(mode="after")                # check fields TOGETHER
    def passwords_match(self) -> "SignUp":
        if self.password != self.confirm:         # cross-field rule
            raise ValueError("passwords do not match")
        return self                               # must return the model


app = FastAPI()                                   # create app


@app.post("/signup")
def signup(data: SignUp) -> dict:
    return {"ok": True, "username": data.username, "age": data.age}  # reached only if valid


# ---------- TEST CASES ----------
c = TestClient(app)                               # test client
good = {"username": "Aditya", "age": "25", "password": "x", "confirm": "x"}  # "25" is coerced to int
print(c.post("/signup", json=good).json())        # valid
bad = {"username": "a b", "age": 10, "tags": list("abcd"), "password": "x", "confirm": "y"}
r = c.post("/signup", json=bad)                   # many errors
print(r.status_code)                              # 422
for e in r.json()["detail"]:                      # one entry per problem
    print(e["loc"], "->", e["msg"])               # where + why
mismatch = {"username": "ok_user", "age": 30, "password": "x", "confirm": "y"}  # only cross-field problem
print(c.post("/signup", json=mismatch).json()["detail"][0]["msg"])  # model_validator runs only if fields are valid

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# {'ok': True, 'username': 'aditya', 'age': 25}
# 422
# ['body', 'username'] -> Value error, no spaces allowed
# ['body', 'age'] -> Input should be greater than or equal to 18
# ['body', 'tags'] -> List should have at most 3 items after validation, not 4
# Value error, passwords do not match
```

---

## 🔍 Why This Works (3 lines max)
Lax mode coerces `"25"` to `25`. All field errors are collected together (`loc` shows where). The `model_validator(mode='after')` runs only if the individual fields passed - that is why the mismatch error is missing in the first bad request.
हिंदी: Fields की सारी errors एक साथ आती हैं; model_validator तभी चलता है जब fields valid हों।

---

## ⚡ Alternative Solution
```python
from pydantic import BaseModel, TypeAdapter, ValidationError  # pydantic v2


class User(BaseModel):
    id: int                                       # int (lax mode coerces "7")
    name: str                                     # required string


print(User(id="7", name="A"))                     # lax coercion: "7" -> 7
print(User.model_validate({"id": 1, "name": "B"}).model_dump())  # dict -> model -> dict

try:
    User(id="abc")                                # bad id AND missing name
except ValidationError as e:
    print(e.error_count(), "errors")              # count
    for err in e.errors():                        # structured errors
        print(err["loc"], err["type"])            # location + error code

ta = TypeAdapter(list[int])                       # validate non-model types
print(ta.validate_python(["1", 2, 3.0]))          # coerces to [1, 2, 3]
print(User.model_validate_json('{"id": 5, "name": "C"}'))  # straight from JSON string

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# id=7 name='A'
# {'id': 1, 'name': 'B'}
# 2 errors
# ('id',) int_parsing
# ('name',) missing
# [1, 2, 3]
# id=5 name='C'
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: Pydantic v1 syntax in v2
from pydantic import validator        # deprecated in v2
@validator("username")                # use @field_validator + @classmethod

# ❌ Wrong: validating by hand inside the endpoint
if len(data.username) < 3:
    raise HTTPException(422, "too short")   # duplicates what the model can declare

# ✅ Correct: declare rules on the model
```

---

## 🎯 Interview Tip (1 line)
Say: "Validate at the edge with Pydantic models; field_validator for one field, model_validator for cross-field; FastAPI returns structured 422s."

---

## 🔗 Related Questions
→ Q221 (CRUD) | Q192 (config loader) | Q193 (form validator) | Q233 (response models)
