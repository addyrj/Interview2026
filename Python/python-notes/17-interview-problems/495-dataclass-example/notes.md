---

# 495. Dataclass Example
# हिंदी में: Dataclass का Example (कम code में data class)

Full runnable solution: [main.py](main.py) (defaults, `field()`, `frozen`, `slots`, `__post_init__`, ordering, `asdict`, `replace`).

---

## 🔵 Simple Definition (English)
`@dataclass` auto-generates `__init__`, `__repr__` and `__eq__` (and more on request) for a class from its annotated fields, so you write only the data, not the boilerplate.

## 🔵 सरल परिभाषा (Hindi)
`@dataclass` class के annotated fields से `__init__`, `__repr__` और `__eq__` (और माँगने पर और भी) अपने-आप बना देता है, इसलिए आप सिर्फ़ data लिखते हैं, boilerplate नहीं।

---

## 🔴 Problem it Solves
Plain classes that only hold data need 15 lines of `__init__`, `__repr__` and `__eq__` that are easy to get wrong. Tuples and dicts lose names and types. Dataclasses give named, typed, comparable records with almost no code.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ़ data रखने वाली साधारण classes में `__init__`, `__repr__`, `__eq__` की 15 lines लिखनी पड़ती हैं जिनमें गलती आसान है। Tuples और dicts में नाम और types खो जाते हैं। Dataclass लगभग बिना code के नाम, type और तुलना वाले records देती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decorate a class with @dataclass
Step 2 → It reads annotated attributes in order: price: float, name: str = ""
Step 3 → Generates __init__(self, price, name=""), __repr__, __eq__
Step 4 → Options: order=True (<,>), frozen=True (immutable+hashable), slots=True (less memory)
Step 5 → field(default_factory=list) for mutable defaults; field(init=False) for computed
Step 6 → __post_init__ runs right after __init__ for validation/derived values
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → class पर @dataclass लगाओ
Step 2 → वह annotated attributes क्रम से पढ़ता है: price: float, name: str = ""
Step 3 → __init__(self, price, name=""), __repr__, __eq__ बनाता है
Step 4 → Options: order=True (<,>), frozen=True (बदल नहीं सकते + hashable), slots=True (कम memory)
Step 5 → mutable default के लिए field(default_factory=list); computed के लिए field(init=False)
Step 6 → __post_init__ __init__ के ठीक बाद चलता है (validation/derived values)
```

---

## 🟡 Real World Example
An e-commerce backend: `Product`, `Order`, `Money` as dataclasses inside the domain layer; `frozen=True` for `Money` so nobody mutates an amount in place. Config objects (`Settings`), parsed API results and ML experiment configs are typical too. For input validation from outside, use Pydantic; dataclasses do not validate types.

## 🟡 Real Example Hindi mein
E-commerce backend में `Product`, `Order`, `Money` domain layer की dataclasses होती हैं; `Money` पर `frozen=True` ताकि कोई amount जगह पर बदल न सके। Config objects (`Settings`), parsed API results और ML experiment configs भी आम उदाहरण हैं। बाहर से आए input की validation के लिए Pydantic लें; dataclass types validate नहीं करती।

---

## 💻 Code Example — Basic
```python
# Basic dataclass: no boilerplate
from dataclasses import dataclass, field  # tools

@dataclass  # generates __init__, __repr__, __eq__
class User:  # a record
    name: str  # required field
    age: int = 0  # field with default
    tags: list[str] = field(default_factory=list)  # separate list per instance

u = User("Asha", 30)  # positional args work
print(u)  # readable repr for free
print(u == User("Asha", 30))  # compares field by field
print(User("Ravi").tags is User("Zoya").tags)  # not shared
# Output:
# User(name='Asha', age=30, tags=[])
# True
# False
```

## 💻 Code Example — Advanced
```python
# Excerpt from main.py: ordering, derived field, validation, frozen value object
@dataclass(order=True, slots=True)
class Product:
    price: float
    name: str = field(compare=False)  # order only by price
    tags: list[str] = field(default_factory=list, compare=False)
    sku: str = field(init=False, default="", compare=False, repr=False)

    def __post_init__(self) -> None:
        if self.price < 0:
            raise ValueError("price must be >= 0")
        self.sku = self.name.upper().replace(" ", "-")  # derived

@dataclass(frozen=True, slots=True)
class Money:
    amount: int  # paise
    currency: str = "INR"
```
Real output of `python main.py` (Python 3.13.3):
```
Product(price=99.0, name='Mouse pad', tags=[]) MOUSE-PAD
True Mouse pad
598.0 Keyboard
Money(amount=750, currency='INR')
FrozenInstanceError
79.0 99.0
hashable because frozen
ValueError: price must be >= 0
all ok
```

---

## 🟠 JavaScript vs Python Comparison
JS has object literals and TypeScript `interface`/`type`, but no auto `equals`/`toString`; `Object.freeze` mirrors `frozen=True`; spread `{...a, price: 79}` mirrors `replace(a, price=79)`.

```python
from dataclasses import replace
b = replace(a, price=79.0)   # copy with one change
```
```javascript
const b = { ...a, price: 79 };   // copy with one change
```

---

## 🟠 FastAPI Connection
FastAPI request/response models are normally Pydantic, but it also accepts stdlib dataclasses as bodies and `response_model`, converting them to Pydantic internally. Use dataclasses for internal domain objects and Pydantic at the API edge, converting with `asdict` or `model_validate`.

```python
from dataclasses import dataclass  # stdlib
from fastapi import FastAPI  # framework

app = FastAPI()  # app

@dataclass  # FastAPI understands this as a body model
class Item:
    name: str  # required
    price: float  # required

@app.post("/items")
def create(item: Item) -> Item:  # validated from JSON, returned as JSON
    return item
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Mutable default value.
✅ Correct: `field(default_factory=list)`.

```python
# Wrong
@dataclass
class A:
    tags: list[str] = []      # ValueError: mutable default <class 'list'> ... use default_factory
# Right
@dataclass
class A:
    tags: list[str] = field(default_factory=list)
```

❌ Mistake 2: Non-default field after a default field.
✅ Correct: put required fields first, or use `kw_only=True` (3.10+).

❌ Mistake 3: Expecting type validation: `User("x", "abc")` happily accepts a string for `age`.
✅ Correct: use Pydantic when you need validation, or validate in `__post_init__`.

---

## 🧠 Tricky Interview Question
```python
from dataclasses import dataclass
@dataclass
class P:
    x: int
p = P(1)
print({p})
```
Answer: `TypeError: unhashable type: 'P'`. With the default `eq=True` and `frozen=False`, dataclass sets `__hash__` to `None`. Use `frozen=True` (hashable) or `unsafe_hash=True`. The `Money` class in main.py is frozen so it can be a dict key.

---

## ⚫ Interview Questions + Answers

Q1: dataclass vs namedtuple vs Pydantic?
A1: namedtuple: immutable tuple. dataclass: mutable by default, light, no validation. Pydantic: parsing and validation, slower, great at API boundaries.

Q2: What does `slots=True` do?
A2: Uses `__slots__`: less memory, faster attribute access, no arbitrary new attributes (3.10+). Note: it creates a new class, so `super()` without arguments in methods works but zero-arg tricks can surprise.

Q3: `field(default_factory=...)` why?
A3: A default is evaluated once at class creation; a factory is called per instance, avoiding shared mutable state.

Q4: `__post_init__` use?
A4: Validation, derived fields, normalisation right after init.

Q5: Inheritance with defaults?
A5: Parent defaults force child fields to have defaults too; use `kw_only=True` to avoid the ordering problem.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Internal records, value objects, configs with few behaviours

❌ Avoid when:
- You need runtime type validation or JSON schema (Pydantic)
- A simple tuple or dict is enough

---

## 📊 Visual Diagram
```
 @dataclass class Product:        generated for you
   price: float          ──►  __init__(self, price, name, tags=[...])
   name: str                  __repr__  -> Product(price=..., ...)
   tags: list = field(...)    __eq__    -> field-by-field
 order=True  ─► <, <=, >, >=      frozen=True ─► immutable + __hash__
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| dataclass | Auto-generated data class | अपने-आप बनी data class |
| field() | Per-field settings | हर field की सेटिंग |
| frozen | Immutable instance | बदला न जा सकने वाला |
| slots | Fixed attribute storage | तय attributes, कम memory |
| __post_init__ | Hook after init | init के बाद का hook |

---

## ⚡ 3-Line Summary
English: @dataclass writes __init__, __repr__ and __eq__ for you.
Use default_factory for mutable defaults and frozen for value objects.
It does not validate types; use Pydantic at API edges.
Hindi: @dataclass आपके लिए __init__, __repr__ और __eq__ लिख देता है।
mutable defaults के लिए default_factory और value objects के लिए frozen इस्तेमाल करो।
यह types validate नहीं करता; API की सीमा पर Pydantic लो।

---

## ➡️ Next Topic
496. Pydantic Validation Example: dataclasses hold data; Pydantic validates and parses data coming from outside.

---
