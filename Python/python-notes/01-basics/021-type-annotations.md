---

# 021. Type Annotations
# हिंदी में: Type Annotations — annotation का syntax और अंदर की बात

---

## 🔵 Simple Definition (English)
An annotation is the `: Type` or `-> Type` syntax attached to a variable, parameter, return value or class attribute. Python evaluates it and stores it in `__annotations__`, but does nothing else with it. Annotation is the syntax; "type hint" is the meaning people give it.

## 🔵 सरल परिभाषा (Hindi)
Annotation वो `: Type` या `-> Type` syntax है जो variable, parameter, return value या class attribute के साथ लगता है। Python इसे evaluate करके `__annotations__` में रखता है, इसके अलावा कुछ नहीं करता। Annotation syntax है; "type hint" उसका मतलब है।

---

## 🔴 Problem it Solves
Python 2 had no standard place to attach metadata to names. Every library invented its own way (decorators, docstrings). PEP 3107 (2006) added annotation syntax for functions and PEP 526 (2016) for variables, giving one standard place that tools can read.

## 🔴 यह क्यों बना? (Hindi)
Python 2 में names पर metadata लगाने की कोई standard जगह नहीं थी। हर library अपना तरीका बनाती थी (decorators, docstrings)। PEP 3107 (2006) ने functions के लिए और PEP 526 (2016) ने variables के लिए annotation syntax दिया — एक standard जगह जिसे tools पढ़ सकें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python parses:  x: int = 5
Step 2 → It evaluates the annotation expression (int) at that moment
Step 3 → Stores it:  __annotations__["x"] = int  (module/class level)
Step 4 → Local variable annotations inside functions are NOT stored
Step 5 → With `from __future__ import annotations` they stay as strings
Step 6 → Tools call typing.get_type_hints() to resolve strings to types
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Python parse करता है:  x: int = 5
Step 2 → Annotation expression (int) को उसी समय evaluate करता है
Step 3 → Store करता है:  __annotations__["x"] = int  (module/class level)
Step 4 → Function के अंदर local variable annotations store नहीं होते
Step 5 → `from __future__ import annotations` से वे strings रहते हैं
Step 6 → Tools typing.get_type_hints() से strings को types में बदलते हैं
```

---

## 🟡 Real World Example
Dataclasses and Pydantic models are built purely from class annotations: `class Order: id: int; amount: float` — the library reads `__annotations__` to generate `__init__`, validation and JSON schema. FastAPI reads function annotations to know which parameter is a path param, query param or body.

## 🟡 Real Example Hindi mein
Dataclasses और Pydantic models पूरी तरह class annotations से बनते हैं: `class Order: id: int; amount: float` — library `__annotations__` पढ़कर `__init__`, validation और JSON schema बनाती है। FastAPI function annotations पढ़कर तय करता है कि कौन सा parameter path, query या body है।

---

## 💻 Code Example — Basic
```python
# Type annotations basics

# Annotate with value:
count: int = 0                         # annotated and assigned
print(count)                           # 0

# Annotate WITHOUT value (declares only, no variable created):
total: float                           # no assignment
print("total" in globals())             # False  (variable does not exist yet)
print(__annotations__["total"])         # <class 'float'>

# Module-level annotations dictionary:
print(__annotations__)                  # {'count': <class 'int'>, 'total': <class 'float'>}


# Function annotations:
def area(width: float, height: float = 1.0) -> float:   # params + return
    return width * height                                # multiply

print(area(2, 3))                       # 6
print(area.__annotations__)             # {'width': <class 'float'>, 'height': <class 'float'>, 'return': <class 'float'>}


# Class attribute annotations:
class Product:
    name: str                           # declared, not assigned
    price: float = 0.0                  # declared with default

print(Product.__annotations__)          # {'name': <class 'str'>, 'price': <class 'float'>}
print(hasattr(Product, "name"))         # False (annotation alone creates nothing)
print(Product.price)                    # 0.0
```

## 💻 Code Example — Advanced
```python
# Advanced annotations — forward refs, Annotated, get_type_hints, dataclass
from __future__ import annotations      # annotations become lazy strings

from dataclasses import dataclass, field, fields
from typing import Annotated, ClassVar, get_type_hints


@dataclass
class Node:
    value: int                                    # payload
    next: Node | None = None                      # forward reference to own class (works lazily)
    registry: ClassVar[int] = 0                   # ClassVar: NOT an instance field
    tags: list[str] = field(default_factory=list) # safe mutable default


Positive = Annotated[int, "must be > 0"]          # type + extra metadata


def charge(amount: Positive, note: str = "") -> str:
    """Annotated attaches metadata that frameworks (Pydantic, FastAPI) can read."""
    return f"charged {amount} {note}".strip()      # simple message


def main() -> None:
    # With the __future__ import, raw annotations are STRINGS:
    print(Node.__annotations__["next"])            # Node | None
    print(type(Node.__annotations__["next"]))      # <class 'str'>

    # get_type_hints() resolves them to real types:
    hints = get_type_hints(Node)                   # evaluates the strings
    print(hints["value"])                          # <class 'int'>

    # dataclass fields come from annotations (ClassVar is skipped):
    print([f.name for f in fields(Node)])          # ['value', 'next', 'tags']

    n = Node(1, Node(2))                           # build a linked pair
    print(n.next.value)                            # 2

    # Annotated metadata:
    hints = get_type_hints(charge, include_extras=True)   # keep Annotated extras
    print(hints["amount"])                         # typing.Annotated[int, 'must be > 0']
    print(hints["amount"].__metadata__)            # ('must be > 0',)

    print(charge(50, "INR"))                       # charged 50 INR

    # Annotations never validate:
    print(charge(-5))                              # charged -5


if __name__ == "__main__":
    main()
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python — annotation is real syntax, stored at runtime
class User:
    id: int
    name: str

def get(id: int) -> User: ...

print(User.__annotations__)   # {'id': <class 'int'>, 'name': <class 'str'>}
```
```typescript
// TypeScript — annotations are erased at compile time
class User {
  id: number;
  name: string;
}

function get(id: number): User { return new User(); }

// After compile -> plain JS, no type info remains at runtime.
// console.log(User.__annotations__)  // does not exist
```

Key differences: Python annotations survive at runtime (`__annotations__`), so libraries can build behavior from them. TS types vanish after compiling. Python uses `name: type`, same order as TS, but its return arrow is `->` instead of `:`.

---

## 🟠 FastAPI Connection
FastAPI reads the annotations of your function to decide where each value comes from. `Annotated[...]` is the modern way to attach `Query`, `Path`, `Depends` metadata.

```python
# FastAPI example (needs: pip install fastapi)
from typing import Annotated

from fastapi import Depends, FastAPI, Query

app = FastAPI()                                          # create app


def get_token() -> str:
    return "secret-token"                                # fake dependency


@app.get("/search")
def search(
    q: Annotated[str, Query(min_length=2, max_length=20)],   # query param with rules
    token: Annotated[str, Depends(get_token)],               # injected dependency
    limit: int = 10,                                         # plain annotated query param
) -> dict[str, str | int]:
    return {"q": q, "limit": limit, "token_len": len(token)}  # JSON response
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Thinking an annotation creates the variable
```python
# Wrong:
x: int
# print(x)      # NameError: name 'x' is not defined

# Correct — assign too:
x: int = 0
print(x)
```

❌ Mistake 2: Forward reference without quotes or __future__
```python
# Wrong — Node is not defined yet inside its own body:
class Node:
    next: Node | None = None    # NameError on Python < 3.14 without future import

# Correct (either one):
class Node:
    next: "Node | None" = None  # string annotation

# or put at top of file:
# from __future__ import annotations
```

❌ Mistake 3: Expecting dataclass to validate annotations
```python
from dataclasses import dataclass

@dataclass
class P:
    x: int

print(P("hello").x)    # hello  - no validation!
# Correct: use pydantic.BaseModel when you need validation
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
def f():
    y: int = 5
    z: str
    return f.__annotations__

print(f())
print(f.__annotations__)
```
Answer: `{}` and `{}`. Annotations of local variables inside a function are evaluated only if they have a value (and not stored anywhere); they never appear in `f.__annotations__`, which holds only parameter and return annotations. Since `f` has none, it is empty. Module and class level annotations are stored; function-local ones are not.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a type hint and an annotation?
A1: Annotation is the syntax (`x: int`, `-> str`) and the storage (`__annotations__`). A type hint is the use of an annotation to describe a type. Annotations could hold any expression (even a string like `x: "meaning"`), but PEP 484 made types the standard use.

Q2: What does `from __future__ import annotations` do?
A2: It makes all annotations lazily stored as strings instead of evaluated immediately. This allows forward references (`next: Node`) and speeds up import. Use `typing.get_type_hints()` to resolve them. Note: Python 3.14 makes lazy evaluation the default (PEP 649), but the import is still seen in many codebases.

Q3: What is `ClassVar` and why use it?
A3: `ClassVar[int]` marks an attribute as shared by the class, not a per-instance field. Dataclasses and Pydantic skip ClassVar when building fields. Without it, `counter: int = 0` in a dataclass becomes an `__init__` parameter.

Q4: What is `Annotated`?
A4: `Annotated[int, meta1, meta2]` is the type `int` plus extra metadata that type checkers ignore but frameworks read. FastAPI uses it for `Query(...)`, `Depends(...)`; Pydantic for `Field(gt=0)`. It keeps the real type clean and reusable: `PositiveInt = Annotated[int, Field(gt=0)]`.

Q5: How do you read annotations safely at runtime?
A5: Use `typing.get_type_hints(obj)` — it resolves string annotations and forward references and merges inherited class annotations. Reading `obj.__annotations__` directly can give raw strings. On 3.14+, `annotationlib.get_annotations()` is the recommended tool.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Declaring dataclass / Pydantic / SQLAlchemy model fields
- Public function signatures
- Attaching metadata with `Annotated`
- Forward references to the same class

❌ Avoid when:
- You think it will validate values (it will not)
- Annotating every trivial local (`i: int = 0`) — noise
- Using annotation as free-form comments

---

## 📊 Visual Diagram
```
 count: int = 0          def f(a: int) -> str:
   |                           |
   v                           v
 module.__annotations__   f.__annotations__
 {'count': int}           {'a': int, 'return': str}

 class P:                 def g():
     x: int                   y: int = 1   <- NOT stored
        |
        v
 P.__annotations__ = {'x': int}
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Annotation | `: Type` syntax stored by Python | Python में store होने वाला `: Type` |
| `__annotations__` | Dict of annotations | Annotations का dict |
| Forward reference | Type used before it's defined | Define होने से पहले use हुआ type |
| `ClassVar` | Class-level, not per-instance | Class-level attribute |
| `Annotated` | Type + extra metadata | Type के साथ extra metadata |
| `get_type_hints` | Resolve annotations to types | Annotations को types में बदलना |

---

## ⚡ 3-Line Summary
English: Annotations (`x: int`, `-> str`) are stored in `__annotations__` and never enforced. An annotation alone does not create a variable. Frameworks (dataclasses, Pydantic, FastAPI) read them to build behavior.
Hindi: Annotations (`x: int`, `-> str`) `__annotations__` में store होते हैं और enforce नहीं होते। सिर्फ annotation से variable नहीं बनता। Frameworks (dataclasses, Pydantic, FastAPI) इन्हें पढ़कर behavior बनाते हैं।

---

## ➡️ Next Topic
**022. print() — Complete Guide** — output formatting with sep, end, file, flush and f-strings.
