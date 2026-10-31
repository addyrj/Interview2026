---

# 046. Default Parameters
# हिंदी में: Default Parameters (डिफ़ॉल्ट मान वाले parameters)

---

## 🔵 Simple Definition (English)
A default parameter is a parameter with a fallback value written in the function definition: `def greet(name="friend")`. If the caller skips that argument, Python uses the default. Defaults are evaluated ONCE, when the `def` line runs, not on every call.

## 🔵 सरल परिभाषा (Hindi)
Default parameter वह parameter है जिसकी fallback value function की definition में लिखी होती है: `def greet(name="friend")`. Caller वह argument न दे तो Python default इस्तेमाल करता है। Default सिर्फ एक बार evaluate होता है, जब `def` line चलती है, हर call पर नहीं।

---

## 🔴 Problem it Solves
Many arguments are optional: timeout, page size, language, retries. Without defaults you either force every caller to pass them or write many overloaded versions. Defaults make common calls short (`fetch(url)`) while still allowing full control (`fetch(url, timeout=5, retries=3)`).

## 🔴 यह क्यों बना? (Hindi)
कई arguments optional होते हैं: timeout, page size, language, retries। Defaults के बिना हर caller को सब कुछ देना पड़ता या कई overloaded versions लिखने पड़ते। Defaults से आम call छोटी रहती है (`fetch(url)`) और पूरा control भी मिलता है (`fetch(url, timeout=5, retries=3)`).

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python reaches the 'def' line while loading the module
Step 2 → It evaluates every default expression ONCE
Step 3 → Results are stored on the function (func.__defaults__)
Step 4 → On each call: missing arguments are filled from those stored values
Step 5 → Mutable defaults (list, dict) are the SAME object on every call → bug
Step 6 → Fix: default None, create a fresh object inside the function
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → def line चलते ही default expressions एक बार evaluate होते हैं
Step 2 → नतीजे func.__defaults__ में रखे जाते हैं
Step 3 → हर call पर missing arguments वहीं से भरे जाते हैं
Step 4 → list/dict जैसे mutable default हर call में वही object रहते हैं → bug
Step 5 → हल: default None रखो, function के अंदर नया object बनाओ
```

---

## 🟡 Real World Example
Razorpay-style client: `create_payment(amount, currency="INR", capture=True)`. Most calls only pass `amount`. A search API: `search(q, page=1, page_size=20)`. An AI helper: `ask(prompt, model="gpt-4o-mini", temperature=0.2)` so teams get a safe default model but can override per call.

## 🟡 Real Example Hindi mein
Razorpay जैसा client: `create_payment(amount, currency="INR", capture=True)`. ज़्यादातर calls में सिर्फ `amount` देना होता है। Search API: `search(q, page=1, page_size=20)`. AI helper: `ask(prompt, model="gpt-4o-mini", temperature=0.2)` ताकि default safe model चले पर ज़रूरत पर override हो सके।

---

## 💻 Code Example — Basic
```python
# Basic default parameters - every line commented
from typing import List, Optional  # type hints


def greet(name: str = "friend", punctuation: str = "!") -> str:  # two defaults
    return f"Hello, {name}{punctuation}"  # build the greeting


print(greet())  # no arguments: both defaults used
# Output: Hello, friend!
print(greet("Asha"))  # name given, punctuation default
# Output: Hello, Asha!
print(greet("Asha", "?"))  # both given
# Output: Hello, Asha?
print(greet(punctuation="."))  # skip name, set punctuation by keyword
# Output: Hello, friend.


def power(base: float, exp: int = 2) -> float:  # exp defaults to square
    return base ** exp  # raise to the power


print(power(5), power(2, 10))  # default and custom exponent
# Output: 25 1024

print(greet.__defaults__)  # defaults are stored on the function object
# Output: ('friend', '!')


# THE CLASSIC TRAP: mutable default shared between calls
def add_item_bad(item: str, bucket: List[str] = []) -> List[str]:  # one list forever
    bucket.append(item)  # modifies the shared list
    return bucket  # returns the shared list


print(add_item_bad("a"))  # first call
# Output: ['a']
print(add_item_bad("b"))  # second call sees leftovers from the first!
# Output: ['a', 'b']


# THE FIX: None as a sentinel, create a new list inside
def add_item(item: str, bucket: Optional[List[str]] = None) -> List[str]:
    if bucket is None:  # caller did not pass a list
        bucket = []  # make a NEW list for this call
    bucket.append(item)  # safe to modify
    return bucket  # return it


print(add_item("a"), add_item("b"))  # independent lists
# Output: ['a'] ['b']
```

## 💻 Code Example — Advanced
```python
# Production style: evaluation time, sentinel objects, dataclass factories, config
import time  # to show when defaults are evaluated
from dataclasses import dataclass, field  # safe mutable defaults for classes
from typing import Any, Dict, List, Optional  # type hints

# 1. Defaults are evaluated ONCE (at def time), not per call
def log_bad(msg: str, when: float = time.time()) -> float:  # time frozen at definition
    return when  # always the same value


t1: float = log_bad("a")  # first call
time.sleep(0.01)  # wait a little
t2: float = log_bad("b")  # second call
print(t1 == t2)  # Output: True  (bug: timestamp never changes)


def log_good(msg: str, when: Optional[float] = None) -> float:  # evaluate at call time
    return time.time() if when is None else when  # fresh time each call


a: float = log_good("a")  # first
time.sleep(0.01)  # wait
b: float = log_good("b")  # second
print(a == b)  # Output: False

# 2. Sentinel object when None is a valid value
_MISSING: Any = object()  # unique marker nobody else can pass by accident


def get_setting(key: str, default: Any = _MISSING) -> Any:
    settings: Dict[str, Any] = {"timeout": None}  # None is a real value here
    if key in settings:  # key exists
        return settings[key]  # may legitimately return None
    if default is _MISSING:  # caller gave no default
        raise KeyError(key)  # so missing keys are an error
    return default  # caller's fallback


print(get_setting("timeout"))  # Output: None
print(get_setting("retries", 3))  # Output: 3
try:  # missing key without default
    get_setting("nope")  # raises
except KeyError as exc:  # catch it
    print("KeyError:", exc)  # Output: KeyError: 'nope'


# 3. Dataclass: use field(default_factory=...) for mutable defaults
@dataclass  # generates __init__
class Job:
    name: str  # required field
    tags: List[str] = field(default_factory=list)  # new list per instance
    retries: int = 3  # immutable default is fine


j1, j2 = Job("a"), Job("b")  # two jobs
j1.tags.append("urgent")  # change only j1
print(j1.tags, j2.tags)  # Output: ['urgent'] []


# 4. A default can use an earlier parameter only via None logic
def make_range(start: int, stop: Optional[int] = None) -> List[int]:
    if stop is None:  # make_range(3) behaves like range(3)
        start, stop = 0, start  # shift arguments
    return list(range(start, stop))  # build list


print(make_range(3), make_range(2, 5))  # Output: [0, 1, 2] [2, 3, 4]
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: default evaluated ONCE at definition
def add(item, bucket=[]):
    bucket.append(item)
    return bucket
add(1); add(2)         # [1] then [1, 2]  <- shared list!

def safe(item, bucket=None):
    bucket = [] if bucket is None else bucket
    bucket.append(item)
    return bucket
```

```javascript
// JavaScript: default evaluated on EVERY call
function add(item, bucket = []) {   // new [] each call, no trap
  bucket.push(item);
  return bucket;
}
add(1); add(2);                     // [1] then [2]

function f(a, b = a * 2) {}         // may use earlier params
```

Key differences: JS re-evaluates defaults on every call, so mutable defaults are safe and defaults can reference earlier parameters. Python evaluates once, so mutable defaults are shared and a default cannot reference earlier parameters. Also JS applies defaults for `undefined` only; Python applies them only when the argument is missing (passing `None` does NOT trigger the default).

---

## 🟠 FastAPI Connection
FastAPI reads default values to decide if a query parameter is required or optional, and shows them in the OpenAPI docs. A default of `None` means optional; no default means required. Pydantic models use `Field(default_factory=list)` for mutable defaults.

```python
# FastAPI: defaults make parameters optional (needs: pip install fastapi pydantic)
from typing import List, Optional  # type hints
from fastapi import FastAPI  # the framework
from pydantic import BaseModel, Field  # validation models

app: FastAPI = FastAPI()  # create app


class Order(BaseModel):  # request body model
    item: str  # required field
    qty: int = 1  # optional, default 1
    notes: List[str] = Field(default_factory=list)  # safe mutable default


@app.get("/search")  # GET /search?q=pizza&page=2
def search(q: str, page: int = 1, size: int = 20, city: Optional[str] = None) -> dict:
    # q has no default -> required; page, size, city are optional
    return {"q": q, "page": page, "size": size, "city": city}  # echo the values
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mutable default argument
```python
# Wrong - one shared list for all calls:
def add(x, items=[]):
    items.append(x)
    return items

# Correct:
def add(x, items=None):
    items = [] if items is None else items
    items.append(x)
    return items
```

❌ Mistake 2: Non-default parameter after a default one
```python
# Wrong - SyntaxError: non-default argument follows default argument
# def f(a=1, b): ...

# Correct - required first, defaults last (or make b keyword-only):
def f(b, a=1):
    return a + b

def g(a=1, *, b):      # b is keyword-only and required
    return a + b
```

❌ Mistake 3: Expecting `None` to trigger the default
```python
def greet(name="friend"):
    return f"Hi {name}"

print(greet(None))   # Hi None   <- default NOT used, None was passed
# Correct: handle it explicitly
def greet2(name=None):
    name = name or "friend"   # careful: "" and 0 also become "friend"
    return f"Hi {name}"
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
def f(n, acc=[]):
    acc.append(n)
    return len(acc)

print(f(1), f(2), f(3, []), f(4))
```

**Answer**: `1 2 1 3`. The first, second and fourth calls share the default list, which grows: sizes 1, 2, then 3. The third call passes its own fresh list, so its length is 1 and the shared list is untouched. Arguments are evaluated left to right, so the order of the prints matches.

---

## ⚫ Interview Questions + Answers

Q1: Why is a mutable default argument dangerous?
A1: Defaults are created once when `def` runs and stored in `func.__defaults__`. A list or dict default is the same object on every call, so changes in one call leak into the next. Use `None` and create the object inside.

Q2: When are default values evaluated?
A2: At function definition time, once. That is why `time.time()` or `datetime.now()` as a default stays frozen. Use `None` and compute inside the function.

Q3: How do you give a dataclass a mutable default?
A3: `field(default_factory=list)`. A plain `= []` raises `ValueError` in dataclasses; Pydantic copies mutable defaults for you but `default_factory` is still the clear way.

Q4: Is it fine to use immutable defaults like numbers, strings, tuples, `None`?
A4: Yes. They cannot be modified in place, so sharing them is harmless.

Q5: How can you tell if the caller passed `None` explicitly or nothing at all?
A5: Use a private sentinel: `_MISSING = object()` as the default and compare with `is`. That distinguishes "not passed" from "passed None".

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Parameters have a sensible common value (timeouts, page size, flags)
- You want short calls for the common case
- Declaring optional API query parameters

❌ Avoid when:
- The default is a list, dict, set or object (use `None` + create inside)
- The default depends on the current time or random value (compute inside)
- A wrong silent default would hide a bug (make the parameter required)

---

## 📊 Visual Diagram

```
 def f(x, acc=[]):         ← acc created ONCE here
          │
          ▼
   f.__defaults__ = ([],)  ─────────────┐
                                        │ same object
 call 1: f(1) → acc is that list ◄──────┤
 call 2: f(2) → acc is that list ◄──────┤  (grows: [1, 2])
 call 3: f(3, []) → new list (no sharing)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Default value | Fallback when argument is missing | argument न मिलने पर fallback |
| `__defaults__` | Tuple storing the defaults | defaults रखने वाला tuple |
| Mutable | Can be changed in place | जिसे बदला जा सकता है |
| Sentinel | Special marker value | खास marker value |
| default_factory | Builds a fresh default per instance | हर instance के लिए नया default |
| Optional | Value or None | value या None |

---

## ⚡ 3-Line Summary
English: Default parameters give optional arguments a fallback and are evaluated once at definition time. Never use a mutable default; use `None` and create the object inside, or `default_factory` in dataclasses. Passing `None` explicitly does not trigger the default.
Hindi: Default parameters optional arguments को fallback देते हैं और definition के समय एक बार evaluate होते हैं। Mutable default कभी न रखें; `None` रखकर अंदर object बनाएँ, या dataclass में `default_factory`। `None` देने पर default नहीं लगता।

---

## ➡️ Next Topic
**047. Keyword Arguments** — call functions by parameter name for clear, order-independent calls.
