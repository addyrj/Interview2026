---

# 264. Built-in Exceptions
# हिंदी में: Built-in Exceptions (Python की बनी-बनाई errors)

---

## 🔵 Simple Definition (English)
Python ships with ready-made exception classes for common failures: `ValueError`, `TypeError`, `KeyError`, `IndexError`, `AttributeError`, `FileNotFoundError`, `ZeroDivisionError` and more. Each name tells you what went wrong.

## 🔵 सरल परिभाषा (Hindi)
Python में आम failures के लिए पहले से exception classes मिलती हैं: `ValueError`, `TypeError`, `KeyError`, `IndexError`, `AttributeError`, `FileNotFoundError`, `ZeroDivisionError` आदि। हर नाम बताता है कि क्या गलत हुआ।

---

## 🔴 Problem it Solves
Returning `-1` or `None` for errors is easy to ignore and the bug appears far away. Built-in exceptions make failures loud and specific, so callers can handle exactly the problem they expect. Raising the right built-in type is also the best documentation of your function's contract.

## 🔴 यह क्यों बना? (Hindi)
Error पर `-1` या `None` लौटाना आसानी से अनदेखा हो जाता है और bug कहीं दूर दिखता है। Built-in exceptions failure को साफ़ और specific बनाती हैं, ताकि caller वही problem संभाले जिसकी उसे उम्मीद है। सही built-in type raise करना function के contract का सबसे अच्छा documentation भी है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python or your code detects a problem
Step 2 → The matching built-in class is instantiated with a message
Step 3 → raise stops normal flow and unwinds the call stack
Step 4 → The first except that matches the type handles it
Step 5 → If none matches, the traceback prints and the program exits
Step 6 → Choose: TypeError = wrong type, ValueError = right type wrong value, KeyError/IndexError = lookup failed
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Python या आपका code problem पकड़ता है
Step 2 → message के साथ सही built-in class का object बनता है
Step 3 → raise normal flow रोककर call stack में ऊपर जाता है
Step 4 → पहला matching except उसे संभालता है
Step 5 → कोई match न हुआ तो traceback छपता है और program बंद होता है
Step 6 → चुनाव: TypeError = गलत type, ValueError = सही type पर गलत value, KeyError/IndexError = lookup fail
```

---

## 🟡 Real World Example
A Swiggy cart API raises `ValueError` for quantity 0, `TypeError` when price is a string, `KeyError` for an unknown dish id. An AI app reading `config.json` handles `FileNotFoundError` and `json.JSONDecodeError` (a `ValueError`) separately, and `PermissionError` when the file is locked.

## 🟡 Real Example Hindi mein
Swiggy cart API quantity 0 पर `ValueError`, price के string होने पर `TypeError`, अनजान dish id पर `KeyError` raise करती है। AI app `config.json` पढ़ते समय `FileNotFoundError`, `json.JSONDecodeError` (जो `ValueError` है) और file locked होने पर `PermissionError` अलग-अलग संभालती है।

---

## 💻 Code Example — Basic
```python
# Basic: trigger the most common built-in exceptions on purpose
from typing import Callable  # type hint for the helper


def show(label: str, fn: Callable[[], object]) -> None:  # run fn and print the error
    try:  # guard the call
        fn()  # trigger the error
    except Exception as exc:  # catch any normal error
        print(f"{label:<18} {type(exc).__name__}: {exc}")  # name + message


show("int('abc')", lambda: int("abc"))  # bad value for a valid type
show("'a' + 1", lambda: "a" + 1)  # wrong type for operation
show("{}['k']", lambda: {}["k"])  # missing dict key
show("[][0]", lambda: [][0])  # list index out of range
show("None.upper()", lambda: None.upper())  # attribute missing
show("1 / 0", lambda: 1 / 0)  # division by zero
show("undefined_name", lambda: undefined_name)  # type: ignore[name-defined]
show("open('nofile')", lambda: open("nofile.txt"))  # missing file
show("import nomod", lambda: __import__("nomod_xyz"))  # missing module
show("next(iter([]))", lambda: next(iter([])))  # exhausted iterator

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# int('abc')         ValueError: invalid literal for int() with base 10: 'abc'
# 'a' + 1            TypeError: can only concatenate str (not "int") to str
# {}['k']            KeyError: 'k'
# [][0]              IndexError: list index out of range
# None.upper()       AttributeError: 'NoneType' object has no attribute 'upper'
# 1 / 0              ZeroDivisionError: division by zero
# undefined_name     NameError: name 'undefined_name' is not defined
# open('nofile')     FileNotFoundError: [Errno 2] No such file or directory: 'nofile.txt'
# import nomod       ModuleNotFoundError: No module named 'nomod_xyz'
# next(iter([]))     StopIteration: 
```

## 💻 Code Example — Advanced
```python
# Production style: raise the RIGHT built-in exception in your own functions
from typing import Any  # type hint


def set_discount(percent: Any) -> float:  # validate input
    if not isinstance(percent, (int, float)):  # wrong TYPE
        raise TypeError(f"percent must be a number, got {type(percent).__name__}")  # TypeError
    if not 0 <= percent <= 100:  # right type, wrong VALUE
        raise ValueError(f"percent must be 0..100, got {percent}")  # ValueError
    return percent / 100  # valid fraction


def get_setting(cfg: dict[str, str], key: str) -> str:  # lookup helper
    try:  # try dict lookup
        return cfg[key]  # may raise KeyError
    except KeyError:  # translate for the caller
        raise KeyError(f"missing setting: {key}") from None  # clean message, no chained noise


class Stack:  # tiny container
    def __init__(self) -> None:  # constructor
        self._items: list[int] = []  # storage

    def pop(self) -> int:  # remove top
        if not self._items:  # empty stack
            raise IndexError("pop from empty stack")  # container error
        return self._items.pop()  # normal path


def not_ready() -> None:  # abstract-ish hook
    raise NotImplementedError("subclass must implement")  # placeholder


for bad in ("10", 150, 20):  # three inputs
    try:  # try each
        print("ok", set_discount(bad))  # valid case prints
    except (TypeError, ValueError) as exc:  # both validation errors
        print(type(exc).__name__, "->", exc)  # show error type

try:  # missing key
    get_setting({"a": "1"}, "b")  # call
except KeyError as exc:  # catch
    print("KeyError ->", exc)  # note quotes around KeyError text

try:  # empty stack
    Stack().pop()  # call
except IndexError as exc:  # catch
    print("IndexError ->", exc)  # message

try:  # not implemented
    not_ready()  # call
except NotImplementedError as exc:  # catch
    print("NotImplementedError ->", exc)  # message
print(issubclass(NotImplementedError, RuntimeError))  # it is a RuntimeError

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# TypeError -> percent must be a number, got str
# ValueError -> percent must be 0..100, got 150
# ok 0.2
# KeyError -> 'missing setting: b'
# IndexError -> pop from empty stack
# NotImplementedError -> subclass must implement
# True
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript has few built-in error classes (`Error`, `TypeError`, `RangeError`, `ReferenceError`, `SyntaxError`). Missing keys give `undefined`, bad math gives `NaN` or `Infinity`, so many failures are silent. Python raises for them.

```python
d = {}
# d['x']          -> KeyError (loud)
# 1 / 0           -> ZeroDivisionError
# int('abc')      -> ValueError
print(d.get('x'))  # None - explicit opt-in to silence
```
```javascript
const o = {};
o.x;            // undefined (silent)
1 / 0;          // Infinity (silent)
parseInt('abc');// NaN (silent)
null.x;         // TypeError (loud)
```

Key differences: JS silently returns `undefined`, `NaN` or `Infinity` in many cases; Python raises a specific exception. In Python, silence is opt-in (`dict.get`, `suppress`).

---

## 🟠 FastAPI Connection
FastAPI already converts invalid request data into `RequestValidationError` (HTTP 422) before your code runs. Inside your code, translate built-ins (`KeyError` -> 404, `ValueError` -> 400) with `HTTPException`. Uncaught built-ins become HTTP 500.

```python
# FastAPI: built-in exceptions mapped to HTTP status codes
from fastapi import FastAPI, HTTPException  # app + HTTP error
from fastapi.testclient import TestClient  # in-process client

app: FastAPI = FastAPI()  # app
PRICES: dict[str, float] = {"pen": 10.0}  # fake catalogue


@app.get("/price/{item}")  # GET /price/pen
def price(item: str, qty: int = 1) -> dict[str, float]:
    try:  # business logic
        if qty <= 0:  # bad value
            raise ValueError("qty must be positive")  # ValueError -> 422/400
        return {"total": PRICES[item] * qty}  # KeyError if item missing
    except KeyError:  # missing item
        raise HTTPException(404, f"item '{item}' not found")  # 404
    except ValueError as exc:  # bad value
        raise HTTPException(400, str(exc))  # 400


c = TestClient(app)  # client
print(c.get("/price/pen?qty=3").json())  # ok
print(c.get("/price/car").status_code)  # 404
print(c.get("/price/pen?qty=0").status_code)  # 400
print(c.get("/price/pen?qty=abc").status_code)  # 422 from FastAPI type validation

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# {'total': 30.0}
# 404
# 400
# 422
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `Exception` or `ValueError` for everything
```python
# Wrong
def age(x):
    if x < 0:
        raise Exception('bad')  # caller cannot tell what failed

# Right
def age(x: int) -> int:
    if x < 0:
        raise ValueError(f'age must be >= 0, got {x}')
    return x
```

❌ Mistake 2: Confusing `TypeError` and `ValueError`
```python
# Wrong
int([1])  # TypeError (wrong type)
int('x')  # ValueError (right type, wrong content)

# Right
# Catch both only when you really mean both:
try:
    n = int(raw)
except (TypeError, ValueError):
    n = 0
```

❌ Mistake 3: Using `assert` to validate user input
```python
# Wrong
assert age >= 0  # removed with python -O

# Right
if age < 0:
    raise ValueError('age must be >= 0')
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
d: dict[str, int] = {"a": 1}  # sample dict
try:  # KeyError message
    d["b"]  # missing
except KeyError as e:  # catch
    print(str(e), repr(e.args))  # note the extra quotes

print(isinstance(KeyError(), LookupError), isinstance(StopIteration(), Exception))  # True True
try:  # int vs float strings
    int("3.5")  # ValueError (not 3)
except ValueError as e:  # catch
    print("ValueError:", e)  # message

try:  # unpack error
    a, b = [1, 2, 3]  # too many values
except ValueError as e:  # ValueError, not TypeError
    print(e)  # message

try:  # TypeError for non-iterables
    for _ in 5:  # int is not iterable
        pass  # nothing
except TypeError as e:  # catch
    print(e)  # message
print(ZeroDivisionError.__mro__[1].__name__)  # parent is ArithmeticError
```

**Answer**:
```
'b' ('b',)
True True
ValueError: invalid literal for int() with base 10: '3.5'
too many values to unpack (expected 2)
'int' object is not iterable
ArithmeticError
```
`str(KeyError('b'))` keeps the quotes because KeyError shows `repr` of the key. `StopIteration` is a normal `Exception`. `int('3.5')` raises `ValueError` (it does not truncate). Unpacking the wrong number of items is `ValueError`, while iterating an int is `TypeError`. `ZeroDivisionError` inherits from `ArithmeticError`.

---

## ⚫ Interview Questions + Answers

Q1: `KeyError` vs `IndexError`?
A1: Both are `LookupError`. `KeyError` is for dict/mapping keys, `IndexError` for sequence positions.

Q2: `TypeError` vs `ValueError`?
A2: `TypeError`: object has the wrong type for the operation. `ValueError`: type is fine but the value is not acceptable.

Q3: What does `NotImplementedError` mean?
A3: A method placeholder that a subclass must override. It is not the same as `NotImplemented` (a return value used by operators).

Q4: Which errors come from the OS?
A4: `OSError` and children: `FileNotFoundError`, `PermissionError`, `FileExistsError`, `TimeoutError`, `ConnectionError`.

Q5: What is `StopIteration`?
A5: Raised by `next()` when an iterator is exhausted. `for` loops catch it for you. Inside generators it becomes `RuntimeError` (PEP 479).

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Raise the closest built-in type for argument problems
- Catch built-ins you can actually recover from
- Translate built-ins into HTTP status codes at the API edge

❌ Avoid when:
- Raising bare `Exception` for business rules (create a custom class)
- Catching `AttributeError`/`NameError` to hide programming bugs
- Using `assert` for runtime input checks

---

## 📊 Visual Diagram

```
Wrong TYPE ──────────► TypeError
Right type, bad value ► ValueError
Missing dict key ──────► KeyError      ┐
Bad list index ────────► IndexError    ┴► LookupError
Missing attribute ─────► AttributeError
Unknown variable ──────► NameError
File/OS problem ───────► OSError (FileNotFoundError...)
Math problem ──────────► ArithmeticError (ZeroDivisionError)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ValueError | Right type, wrong value | सही type, गलत value |
| TypeError | Wrong type | गलत type |
| KeyError | Missing dict key | dict में key नहीं |
| IndexError | Bad sequence index | गलत index |
| OSError | Operating system failure | OS से जुड़ी error |
| StopIteration | Iterator finished | iterator खत्म |

---

## ⚡ 3-Line Summary
English: Built-in exceptions name the failure: `TypeError` for wrong type, `ValueError` for bad value, `KeyError`/`IndexError` for failed lookups, `OSError` family for files and network. Raise the closest built-in and catch only what you can handle.
Hindi: Built-in exceptions failure का नाम बताती हैं: गलत type पर `TypeError`, गलत value पर `ValueError`, lookup fail पर `KeyError`/`IndexError`, files और network के लिए `OSError` परिवार। सबसे नज़दीकी built-in raise करें और वही पकड़ें जिसे संभाल सकें।

---

## ➡️ Next Topic
**265. Custom Exceptions** is already written; continue with **268. contextlib.suppress** (selective ignoring of errors).

Verification: all code blocks above were executed on Python 3.13 and the "Real output" comments are the real output.
