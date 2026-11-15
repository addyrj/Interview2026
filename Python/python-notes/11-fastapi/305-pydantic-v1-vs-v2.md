---

# 305. Pydantic v1 vs v2
# हिंदी में: Pydantic v1 बनाम v2 (क्या बदला और कैसे migrate करें)

---

## 🔵 Simple Definition (English)
Pydantic v2 (2023) is a rewrite of the data validation library. Its core is written in Rust (`pydantic-core`), so it is 5-50x faster than v1. It also renamed many methods (`.dict()` became `.model_dump()`), changed how `Optional` works, and replaced `@validator` with `@field_validator`.

## 🔵 सरल परिभाषा (Hindi)
Pydantic v2 (2023) data validation library का नया संस्करण है। इसका core Rust (`pydantic-core`) में लिखा है, इसलिए यह v1 से 5-50 गुना तेज़ है। इसमें कई methods के नाम बदले (`.dict()` अब `.model_dump()`), `Optional` का व्यवहार बदला, और `@validator` की जगह `@field_validator` आया।

---

## 🔴 Problem it Solves
v1 was pure Python, slow for large payloads, had unclear rules about type coercion and `Optional`, and used confusing names (`parse_obj`, `.dict()`, `class Config`). v2 gives speed, stricter and documented behaviour, a clear `model_` naming prefix (avoiding clashes with your field names) and better JSON schema. Old code and many tutorials still show v1, so you must recognise both.

## 🔴 यह क्यों बना? (Hindi)
v1 pure Python में था, बड़े payloads पर धीमा था, type coercion और `Optional` के नियम अस्पष्ट थे, और नाम भ्रमित करने वाले थे (`parse_obj`, `.dict()`, `class Config`)। v2 तेज़ी, ज़्यादा कड़ा और documented व्यवहार, साफ `model_` prefix (ताकि आपके field नामों से टकराव न हो) और बेहतर JSON schema देता है। पुराना code और कई tutorials अब भी v1 दिखाते हैं, इसलिए दोनों पहचानना ज़रूरी है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → v2 validation engine = Rust library pydantic-core; Python class only describes the schema
Step 2 → Model build time: Pydantic turns your type hints into a "core schema"
Step 3 → Validation time: Rust walks the schema and checks the data (very fast)
Step 4 → Old v1 method names still exist but warn: PydanticDeprecatedSince20
Step 5 → v1 code can run inside v2 through the namespace:  from pydantic.v1 import BaseModel
Step 6 → Migrate: run the codemod "bump-pydantic", fix warnings, run tests
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → v2 का validation engine = Rust library pydantic-core; Python class सिर्फ schema बताती है
Step 2 → model बनते समय: Pydantic आपके type hints को "core schema" में बदलता है
Step 3 → validation के समय: Rust schema पर चलकर data जाँचता है (बहुत तेज़)
Step 4 → पुराने v1 method नाम अब भी हैं पर warning देते हैं: PydanticDeprecatedSince20
Step 5 → v1 code को v2 के अंदर चला सकते हैं:  from pydantic.v1 import BaseModel
Step 6 → Migrate: "bump-pydantic" codemod चलाएँ, warnings ठीक करें, tests चलाएँ
```

---

## 🟡 Real World Example
A company has a 3-year-old FastAPI service with 200 models written for Pydantic v1. They want FastAPI's new releases (which require v2) and 5x faster JSON validation for a batch endpoint receiving 10,000-row payloads. They run `bump-pydantic`, replace `.dict()` with `.model_dump()`, add explicit `= None` to `Optional` fields, and re-run tests.

## 🟡 Real Example Hindi mein
एक कंपनी की 3 साल पुरानी FastAPI service में 200 models Pydantic v1 के लिए लिखे हैं। उन्हें FastAPI के नए releases चाहिए (जिन्हें v2 चाहिए) और 10,000 rows वाले batch endpoint के लिए 5 गुना तेज़ validation चाहिए। वे `bump-pydantic` चलाते हैं, `.dict()` को `.model_dump()` से बदलते हैं, `Optional` fields में स्पष्ट `= None` जोड़ते हैं और tests दोबारा चलाते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: v2 style (verified: pydantic 2.14.3, Python 3.13)
# pip install pydantic
from pydantic import BaseModel, ConfigDict, Field, ValidationError, TypeAdapter  # v2 imports
import pydantic  # to show the version

print(pydantic.VERSION[:1])  # major version number
# Output: 2


class U(BaseModel):  # a v2 model
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)  # replaces "class Config"
    id: int  # required int
    name: str  # required str
    email: str | None  # v2: REQUIRED but may be None (no implicit default)
    tags: list[str] = Field(default_factory=list)  # safe default list


try:  # email is not provided
    U(id=1, name=" x ")  # v1 would have accepted this (Optional meant default None)
except ValidationError as e:  # v2 raises
    print(e.errors()[0]["type"], e.errors()[0]["loc"])  # what failed
# Output: missing ('email',)

u = U(id="5", name="  Ria ", email=None)  # "5" -> 5, name stripped by config
print(u.model_dump(), u.model_dump_json())  # v2 names: model_dump / model_dump_json
# Output: {'id': 5, 'name': 'Ria', 'email': None, 'tags': []} {"id":5,"name":"Ria","email":null,"tags":[]}
print(U.model_validate({"id": 1, "name": "a", "email": "a@b.c"}))  # replaces parse_obj
# Output: id=1 name='a' email='a@b.c' tags=[]
print(U.model_validate_json('{"id": 2, "name": "b", "email": null}'))  # replaces parse_raw
# Output: id=2 name='b' email=None tags=[]
print(list(U.model_json_schema()["properties"]))  # replaces .schema()
# Output: ['id', 'name', 'email', 'tags']
print(TypeAdapter(list[int]).validate_python(["1", 2]))  # v2: validate ANY type, not only models
# Output: [1, 2]
print(u.model_copy(update={"name": "Z"}).name)  # replaces .copy(update=...)
# Output: Z
```

## 💻 Code Example — Advanced
```python
# Production style: coercion rules, ORM mode, deprecated API, and v1 compatibility layer (verified)
import warnings  # to capture the deprecation warning
from pydantic import BaseModel, ConfigDict, ValidationError  # v2 API


class U(BaseModel):  # v2 model with ORM support
    model_config = ConfigDict(from_attributes=True)  # v1 name was orm_mode = True
    id: int
    name: str
    email: str | None
    tags: list[str] = []


class Obj:  # pretend this is a SQLAlchemy row object
    id = 9
    name = "orm"
    email = "o@o.o"
    tags: list[str] = []


print(U.model_validate(Obj()).id)  # from_attributes lets you read plain objects (v1: from_orm)
# Output: 9


class A(BaseModel):  # to show the coercion rules
    n: int


for v in ("12", 12.0, 12.5, True):  # try 4 inputs
    try:
        print(repr(v), "->", A(n=v).n)  # lax mode conversion
    except ValidationError as e:
        print(repr(v), "-> error", e.errors()[0]["type"])  # lossy conversion rejected
# Output:
# '12' -> 12
# 12.0 -> 12
# 12.5 -> error int_from_float
# True -> 1

u = U(id=5, name="Ria", email=None)  # a model instance
with warnings.catch_warnings(record=True) as w:  # collect warnings
    warnings.simplefilter("always")  # show every warning
    print(u.dict())  # v1 name still works in v2...
    print(U.parse_obj({"id": 1, "name": "a", "email": None}).id)  # ...for now
    print(w[0].category.__name__)  # ...but warns
# Output:
# {'id': 5, 'name': 'Ria', 'email': None, 'tags': []}
# 1
# PydanticDeprecatedSince20

# Running real v1 code inside v2 (compat namespace, handy during migration)
from pydantic.v1 import BaseModel as B1, validator  # the whole v1 API


class Old(B1):  # a v1 model
    n: int
    opt: int | None  # v1: Optional => default None (no error when missing)

    @validator("n")  # v1 decorator
    def pos(cls, v: int) -> int:
        assert v > 0  # v1 style
        return v


print(Old(n=1).dict())  # v1 model works as before
# Output: {'n': 1, 'opt': None}
# Note: pydantic.v1 is only a bridge; the Pydantic docs say it is not supported on newer Pythons (3.14+), so plan to finish migration.
```

---

## 🟠 JavaScript vs Python Comparison
A close JS analogy: zod v3 vs v4 (or Ajv). The library is the same idea, but the new major version is faster and renamed methods. Migration needs a checklist, not a rewrite.

| Task | Pydantic v1 | Pydantic v2 |
|---|---|---|
| Model to dict | `.dict()` | `.model_dump()` |
| Model to JSON | `.json()` | `.model_dump_json()` |
| Parse dict | `Model.parse_obj(d)` | `Model.model_validate(d)` |
| Parse JSON | `Model.parse_raw(s)` | `Model.model_validate_json(s)` |
| Copy | `.copy()` | `.model_copy()` |
| Schema | `.schema()` | `.model_json_schema()` |
| Config | `class Config:` | `model_config = ConfigDict(...)` |
| ORM mode | `orm_mode = True` | `from_attributes=True` |
| Field validator | `@validator("x")` | `@field_validator("x")` + `@classmethod` |
| Whole-model | `@root_validator` | `@model_validator` |
| Regex | `Field(regex=...)` | `Field(pattern=...)` |
| Optional | `Optional[int]` = default None | `int | None` = required, add `= None` |

```python
# Python v2
user = User.model_validate(data)
payload = user.model_dump(exclude_none=True)
```
```javascript
// JavaScript (zod)
const user = UserSchema.parse(data);
const payload = JSON.parse(JSON.stringify(user));   // drop undefined
```

Key differences: Pydantic also converts types ("5" -> 5) in lax mode, while zod only checks unless you use `z.coerce`.

---

## 🟠 FastAPI Connection
FastAPI supports v2 (current releases require Pydantic v2; old releases before 0.100 supported only v1). Behaviour that you will notice in a FastAPI app: required-but-nullable fields, `response_model` serialization through Pydantic's Rust serializer, and error `type` strings like `missing` or `int_parsing` in 422 responses.

```python
# FastAPI + Pydantic v2: Optional needs an explicit default
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # client
from pydantic import BaseModel  # model

app: FastAPI = FastAPI()  # app


class Profile(BaseModel):  # request body
    name: str
    bio: str | None = None  # v2: "= None" makes it optional; without it the field is required


@app.post("/profile")  # endpoint
def save(p: Profile) -> dict[str, str | None]:
    return {"name": p.name, "bio": p.bio}  # attribute access


c: TestClient = TestClient(app)  # client
print(c.post("/profile", json={"name": "Asha"}).json())  # bio omitted -> OK because of "= None"
# Output: {'name': 'Asha', 'bio': None}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assuming `Optional[X]` / `X | None` means "may be missing"
✅ Correct: In v2 it only means "may be None". Add `= None` to make it optional.

```python
# Wrong (v2): email is REQUIRED -> error "missing"
email: str | None
# Right
email: str | None = None
```

❌ Mistake 2: Using v1 names and ignoring warnings
✅ Correct: Switch to `model_dump`, `model_validate`, `ConfigDict`, `field_validator`. Run tests with `-W error::DeprecationWarning` (`PydanticDeprecatedSince20` is a DeprecationWarning subclass) to find them all.

```python
# Wrong
data = user.dict()
# Right
data = user.model_dump()
```

❌ Mistake 3: Mixing `pydantic.v1` and v2 models
✅ Correct: A v1 model cannot be nested inside a v2 model (verified: UserWarning "Mixing V1 models and V2 models ... is not supported", then a TypeError). Migrate whole groups of related models together; use `pydantic.v1` only as a temporary bridge.

---

## 🧠 Tricky Interview Question

**Q**: What does each line print in Pydantic v2?

```python
class A(BaseModel):
    n: int

for v in ("12", 12.0, 12.5, True):
    try: print(A(n=v).n)
    except ValidationError as e: print("error")
```

**Answer**:
```
12
12
error      (12.5 would lose the .5, type: int_from_float)
1
```
Lax mode converts when no information is lost: the string `"12"` and the float `12.0` are fine. `12.5` is rejected. `True` becomes `1` in lax mode (bool is an int subclass); with `ConfigDict(strict=True)` the string, both floats and the bool are all rejected (`int_type`; verified), and only a real `int` passes. In v1, `12.5` would be silently truncated to `12`. (Verified by running.)

---

## ⚫ Interview Questions + Answers

Q1: Why is v2 faster?
A1: The core validation and serialization logic is written in Rust (`pydantic-core`). Python only builds the schema once at class creation. Typical speed-ups are 5-50x depending on the model.

Q2: What is the most dangerous behaviour change?
A2: `Optional[X]` no longer implies a default of `None`. Code that relied on omitted fields now fails with `missing`. Also the stricter int/float coercion (no silent truncation).

Q3: How do you migrate step by step?
A3: Pin Pydantic to the latest 1.10, fix warnings, upgrade FastAPI and Pydantic to v2, run `bump-pydantic`, replace renamed methods, add `= None` defaults, fix validators, run tests, and use `pydantic.v1` only for leftovers.

Q4: What is `TypeAdapter`?
A4: A v2 tool to validate or serialize any type (not just models), e.g. `TypeAdapter(list[int]).validate_python(data)`. Replaces v1's `parse_obj_as`.

Q5: What replaced `Config` and `orm_mode`?
A5: `model_config = ConfigDict(...)` and `from_attributes=True`.

---

## 🔷 When to Use + When Not to Use

✅ Use v2 when:
- Starting any new project (it is the maintained version)
- You use current FastAPI, SQLModel, LangChain (all moved to v2)
- You need speed with large JSON payloads

❌ Stay on v1 (temporarily) when:
- A dependency you cannot upgrade still needs v1 (use `pydantic.v1` as a bridge)
- You are mid-migration with no test coverage (add tests first)

---

## 📊 Visual Diagram

```
 v1:  Python class ──► pure-Python validation loop                     (slower)
 v2:  Python class ──► core schema ──► Rust pydantic-core validates    (5-50x faster)

 Migration path
 v1.10 ──► fix warnings ──► v2 + bump-pydantic ──► rename methods ──► add "= None" ──► tests green
                               └── bridge: from pydantic.v1 import BaseModel
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| pydantic-core | Rust engine of v2 | v2 का Rust engine |
| model_dump | v2 name for `.dict()` | `.dict()` का v2 नाम |
| model_validate | v2 name for `parse_obj` | `parse_obj` का v2 नाम |
| ConfigDict | v2 way to configure a model | model configure करने का v2 तरीका |
| TypeAdapter | Validate any type | कोई भी type validate करना |
| Lax mode | Converts compatible values | संगत मानों को बदल देना |
| Deprecated | Still works but will be removed | अभी चलता है पर हटेगा |

---

## ⚡ 3-Line Summary
English: Pydantic v2 is a Rust-powered rewrite that is much faster and renames methods (`model_dump`, `model_validate`, `ConfigDict`, `field_validator`). The biggest gotchas are required-but-nullable `Optional` fields and stricter number coercion. Use `pydantic.v1` only as a temporary bridge.
Hindi: Pydantic v2 Rust से चलने वाला नया संस्करण है जो बहुत तेज़ है और methods के नाम बदलता है (`model_dump`, `model_validate`, `ConfigDict`, `field_validator`)। सबसे बड़े फर्क हैं: `Optional` fields अब ज़रूरी पर None-योग्य हैं, और संख्याओं का कड़ा coercion। `pydantic.v1` को सिर्फ अस्थायी पुल की तरह इस्तेमाल करें।

---

## ➡️ Next Topic
**306. Response Models** — filter and shape API output with `response_model`, using these Pydantic v2 models.
