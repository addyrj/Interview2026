---

# 020. Type Hints (Python 3.5+)
# हिंदी में: Type Hints — types की सलाह (hints)

---

## 🔵 Simple Definition (English)
Type hints are optional labels that say what type a variable, parameter or return value is expected to have: `def add(a: int, b: int) -> int`. Python does NOT enforce them at runtime. Tools like mypy, IDEs, Pydantic and FastAPI read them to catch bugs, auto-complete code, and validate data.

## 🔵 सरल परिभाषा (Hindi)
Type hints optional labels हैं जो बताते हैं कि variable, parameter या return value का type क्या होना चाहिए: `def add(a: int, b: int) -> int`। Python इन्हें runtime पर enforce नहीं करता। mypy, IDE, Pydantic और FastAPI इन्हें पढ़कर bugs पकड़ते हैं, auto-complete देते हैं और data validate करते हैं।

---

## 🔴 Problem it Solves
In a large dynamic codebase you can't tell what a function expects without reading its body. Bugs like passing a string where a number was needed show up only at runtime — in production. Type hints give documentation that tools can check before the code runs.

## 🔴 यह क्यों बना? (Hindi)
बड़े dynamic codebase में function क्या मांगता है, यह body पढ़े बिना पता नहीं चलता। String की जगह number देने जैसे bugs सिर्फ runtime पर — production में — दिखते हैं। Type hints ऐसा documentation देते हैं जिसे tools code चलने से पहले check कर सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write hints: def f(x: int) -> str
Step 2 → Python stores them in f.__annotations__ (just a dict)
Step 3 → At runtime Python IGNORES them (no checking)
Step 4 → mypy / pyright read the hints BEFORE running -> report errors
Step 5 → IDE uses hints for autocomplete and warnings
Step 6 → Pydantic / FastAPI read hints AT runtime to validate data
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप hints लिखते हैं: def f(x: int) -> str
Step 2 → Python उन्हें f.__annotations__ (सिर्फ dict) में रखता है
Step 3 → Runtime पर Python इन्हें IGNORE करता है (कोई checking नहीं)
Step 4 → mypy / pyright code चलने से पहले hints पढ़कर errors बताते हैं
Step 5 → IDE autocomplete और warnings के लिए hints use करता है
Step 6 → Pydantic / FastAPI runtime पर hints पढ़कर data validate करते हैं
```

---

## 🟡 Real World Example
Razorpay's Python SDK style code: `def create_order(amount: int, currency: str = "INR") -> dict[str, str]`. Your editor warns if you pass `"500"` as amount. In a FastAPI service at Swiggy-scale, hints define request/response schemas, so the docs page (/docs) is generated automatically.

## 🟡 Real Example Hindi mein
Razorpay SDK style code: `def create_order(amount: int, currency: str = "INR") -> dict[str, str]`। अगर आप amount में `"500"` दें तो editor warning देता है। Swiggy-scale FastAPI service में hints ही request/response schema तय करते हैं, इसलिए /docs page अपने-आप बन जाता है।

---

## 💻 Code Example — Basic
```python
# Type hints basics

# Variable hints:
name: str = "Asha"                       # a string
age: int = 28                            # an int
price: float = 99.5                      # a float
active: bool = True                      # a bool

# Collections (Python 3.9+ built-in generics):
tags: list[str] = ["a", "b"]             # list of strings
scores: dict[str, int] = {"math": 90}    # str -> int
point: tuple[int, int] = (1, 2)          # fixed-size tuple
unique: set[int] = {1, 2, 3}             # set of ints

# Optional / union (Python 3.10+ syntax):
nickname: str | None = None              # str or None
id_value: int | str = 42                 # int or str


# Function hints: parameters and return type
def add(a: int, b: int = 0) -> int:      # takes ints, returns int
    return a + b                         # sum

def log(msg: str) -> None:               # returns nothing
    print(msg)                           # side effect only


print(add(2, 3))                         # 5
log("hello")                             # hello

# Hints are NOT enforced at runtime:
print(add("a", "b"))                     # ab  (no error!)

# Hints are stored here:
print(add.__annotations__)               # {'a': <class 'int'>, 'b': <class 'int'>, 'return': <class 'int'>}
```

## 💻 Code Example — Advanced
```python
# Advanced hints — Callable, TypeVar, Protocol, TypedDict, Literal
from collections.abc import Callable, Sequence
from typing import Literal, Protocol, TypedDict, TypeVar

T = TypeVar("T")                                  # generic placeholder type


class Order(TypedDict):                           # dict with known keys
    id: int                                       # order id
    status: Literal["new", "paid", "shipped"]     # only these strings allowed


class SupportsClose(Protocol):                    # structural typing (duck typing + hints)
    def close(self) -> None: ...                  # anything with close() matches


def first(items: Sequence[T]) -> T | None:
    """Return first item or None; return type follows input type."""
    return items[0] if items else None            # works for list, tuple, str


def apply(fn: Callable[[int], int], value: int) -> int:
    """Call a function that takes int and returns int."""
    return fn(value)                              # delegate


def shutdown(resource: SupportsClose) -> None:
    """Accept any object that has a close() method."""
    resource.close()                              # no inheritance needed


class Conn:                                       # note: does NOT inherit Protocol
    def close(self) -> None:
        print("closed")                           # simple close


def main() -> None:
    order: Order = {"id": 1, "status": "paid"}    # valid TypedDict
    print(order["status"])                        # paid

    print(first([10, 20]))                        # 10
    print(first("xyz"))                           # x
    print(first([]))                              # None

    print(apply(lambda n: n * 2, 21))             # 42
    shutdown(Conn())                              # closed

    # Runtime does not enforce - mypy would flag this:
    bad: Order = {"id": 2, "status": "lost"}      # type: ignore[typeddict-item]
    print(bad["status"])                          # lost

    # Inspect hints at runtime (what FastAPI does):
    from typing import get_type_hints
    print(get_type_hints(apply))                  # {'fn': collections.abc.Callable[[int], int], 'value': <class 'int'>, 'return': <class 'int'>}


if __name__ == "__main__":
    main()
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python — hints are optional, checked by external tools (mypy)
def greet(name: str, times: int = 1) -> str:
    return (f"Hi {name} " * times).strip()

users: list[dict[str, str | int]] = [{"name": "A", "age": 3}]
# Runs even with wrong types; mypy would warn.
```
```typescript
// TypeScript — types are part of the language, checked at compile time
function greet(name: string, times: number = 1): string {
  return `Hi ${name} `.repeat(times).trim();
}

const users: Array<Record<string, string | number>> = [{ name: "A", age: 3 }];
// Wrong types -> compile error. Types are erased in the output JS.
```

Key differences: TypeScript needs a compile step that refuses wrong types. Python hints are metadata — the program still runs. Python uses `list[str]`, `X | None`; TS uses `string[]`, `X | null`. Python hints can be read at runtime (Pydantic uses this); TS types disappear after compile.

---

## 🟠 FastAPI Connection
FastAPI is built on type hints. Path/query params are validated and converted using their hints; the body is validated using Pydantic models; the response is filtered with `response_model`; and OpenAPI docs come from the same hints.

```python
# FastAPI example (needs: pip install fastapi)
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()                                    # create app


class Item(BaseModel):
    name: str                                      # required string
    price: float                                   # required float
    tags: list[str] = []                           # optional list


@app.get("/items/{item_id}")
def read_item(item_id: int, verbose: bool = False) -> dict[str, int | bool]:
    # /items/5?verbose=true -> item_id=5 (int), verbose=True (bool)
    # /items/abc -> automatic 422 error, because "abc" is not int
    return {"id": item_id, "verbose": verbose}     # JSON response


@app.post("/items")
def create_item(item: Item) -> Item:
    return item                                    # body validated by hints
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Thinking hints are enforced
```python
# Wrong assumption:
def total(x: int) -> int:
    return x * 2

print(total("ab"))        # abab - no error

# Correct: validate at runtime with Pydantic or isinstance, check statically with mypy
```

❌ Mistake 2: Mutable default with a hint
```python
# Wrong — hint does not fix the shared list:
def add(item: str, bucket: list[str] = []) -> list[str]:
    bucket.append(item)
    return bucket

# Correct:
def add(item: str, bucket: list[str] | None = None) -> list[str]:
    bucket = [] if bucket is None else bucket
    bucket.append(item)
    return bucket
```

❌ Mistake 3: Using `List`/`Optional` from typing in new code
```python
# Old style (still works, but noisy):
from typing import List, Optional
def f(x: Optional[List[int]]) -> None: ...

# Modern (3.10+):
def f(x: list[int] | None) -> None: ...
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
def f(x: int) -> str:
    return x

result = f(5)
print(result, type(result))
print(f.__annotations__)
```
Answer: `5 <class 'int'>` then `{'x': <class 'int'>, 'return': <class 'str'>}`. The hint says it returns `str`, but it returns an int and Python does not complain. mypy would report "Incompatible return value type". Hints are stored in `__annotations__` and are metadata only.

---

## ⚫ Interview Questions + Answers

Q1: Does Python enforce type hints?
A1: No. They are ignored by the interpreter at runtime. Static checkers (mypy, pyright) verify them before running; libraries like Pydantic and FastAPI read them at runtime to validate data. So hints give safety only when something actively uses them.

Q2: What is the difference between `Optional[int]` and `int = None`?
A2: `Optional[int]` (same as `int | None`) means the value may be an int or None — it says nothing about a default. `x: int = None` is wrong typing (None is not int; mypy flags it). Correct optional-with-default: `x: int | None = None`.

Q3: What is `Any` and when is it used?
A3: `typing.Any` disables type checking for that value: anything is allowed and any attribute is accepted. Use for truly dynamic data (parsed JSON). Overusing `Any` removes the benefit of hints; prefer `object`, `TypedDict`, or Pydantic models.

Q4: What is a `TypeVar` / generics?
A4: `T = TypeVar("T")` lets a function say "the output type depends on the input type": `def first(items: Sequence[T]) -> T`. Passing `list[int]` gives `int`, passing `list[str]` gives `str`. Python 3.12+ has shorter syntax: `def first[T](items: Sequence[T]) -> T`.

Q5: What is `Protocol`?
A5: Structural (duck) typing: a class matches a Protocol if it has the required methods — no inheritance needed. `SupportsClose` accepts any object with `close()`. It brings duck typing into the static type system and is used for dependency injection and testing with fakes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every public function signature (parameters + return)
- FastAPI endpoints and Pydantic models (required)
- Large teams and long-lived code
- Complex data: `dict[str, list[int]]`, `TypedDict`

❌ Avoid when:
- Quick throwaway scripts and notebooks (low value)
- Hints that become unreadable — introduce a type alias instead
- Expecting runtime safety without Pydantic/isinstance

---

## 📊 Visual Diagram
```
  def f(x: int) -> str:
                |
   +------------+---------------------------+
   |            |                           |
 Python       mypy / pyright            Pydantic / FastAPI
 runtime      (static, before run)      (runtime, reads hints)
   |            |                           |
 ignores     reports errors            validates + converts
 hints       in editor / CI            + builds /docs
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Type hint | Expected type label | Type की सलाह/label |
| Static checker | Tool checking before run | Run से पहले check करने वाला tool |
| Union | One of several types (`A \| B`) | कई types में से एक |
| Generic | Type with parameter (`list[int]`) | Parameter वाला type |
| Protocol | Structural typing interface | Methods के आधार पर matching |
| `__annotations__` | Dict storing hints | Hints का dict |

---

## ⚡ 3-Line Summary
English: Type hints label expected types (`x: int`, `-> str`) but Python does not enforce them. Tools like mypy check them statically, and Pydantic/FastAPI use them at runtime. Use modern syntax: `list[int]`, `str | None`.
Hindi: Type hints expected types बताते हैं (`x: int`, `-> str`) पर Python उन्हें enforce नहीं करता। mypy static check करता है, और Pydantic/FastAPI runtime पर use करते हैं। Modern syntax लिखें: `list[int]`, `str | None`।

---

## ➡️ Next Topic
**021. Type Annotations** — the annotation syntax itself: variables, class attributes, `__annotations__`, and forward references.
