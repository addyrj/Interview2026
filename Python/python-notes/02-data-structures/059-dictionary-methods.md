---

# 059. Dictionary Methods (get, keys, values, items, update, pop, setdefault)
# हिंदी में: Dictionary के Methods

---

## 🔵 Simple Definition (English)
Dictionary methods are built-in tools to read, change and loop over key-value data safely. `get` reads without crashing, `keys/values/items` give views for looping, `update` merges, `pop` removes and returns, `setdefault` reads or creates a default in one step.

## 🔵 सरल परिभाषा (Hindi)
Dictionary methods key-value data को safely पढ़ने, बदलने और loop करने के built-in tools हैं। `get` crash के बिना पढ़ता है, `keys/values/items` loop के लिए views देते हैं, `update` merge करता है, `pop` हटाकर value लौटाता है, `setdefault` पढ़ता या default बनाता है।

---

## 🔴 Problem it Solves
`d["missing"]` raises `KeyError` and crashes your program. Without methods you would write `if key in d: ... else: ...` everywhere. Merging two dicts, removing a key and returning it, or creating a default list only if missing, all needed long code. Methods make these one-liners that are clear and safe.

## 🔴 यह क्यों बना? (Hindi)
`d["missing"]` से `KeyError` आता है और program crash होता है। Methods के बिना हर जगह `if key in d` लिखना पड़ता। Merge, remove+return, और default बनाना — सब एक line में हो जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → d.get(k, default)       → returns d[k] if key exists else default (None if not given); never raises
Step 2 → d.keys()/values()/items() → return LIVE views (they reflect later changes in d)
Step 3 → d.update(other)         → copies every key of other into d; existing keys are overwritten
Step 4 → d.pop(k, default)       → removes k and returns its value; KeyError if missing and no default
Step 5 → d.setdefault(k, v)      → if k missing: sets d[k]=v; always returns d[k]
Step 6 → d.popitem()             → removes and returns the LAST inserted pair (LIFO)
```

## 🟢 कैसे काम करता है? (Hindi)
```
get(k, default)   → key न मिले तो default, error नहीं
keys/values/items → live view, d बदले तो view भी बदलता है
update(other)     → other की सब keys d में, पुरानी overwrite
pop(k, default)   → key हटाकर value लौटाता है
setdefault(k, v)  → key नहीं है तो set करता है, और value लौटाता है
```

---

## 🟡 Real World Example
Swiggy order summary: `order.get("coupon", "NONE")` reads an optional coupon safely. `order.update(delivery_info)` merges delivery fields into the order. `order.pop("internal_note", None)` removes a private field before sending JSON to the app. In FastAPI, `request.headers.get("authorization")` and `query_params.get("page", "1")` use exactly this pattern.

## 🟡 Real Example Hindi mein
Swiggy order में `order.get("coupon", "NONE")` optional coupon safely पढ़ता है। `order.update(delivery_info)` delivery fields merge करता है। `order.pop("internal_note", None)` app को JSON भेजने से पहले private field हटाता है। FastAPI में `request.headers.get("authorization")` यही pattern है।

---

## 💻 Code Example — Basic
```python
# Basic: the main dict methods
user: dict[str, object] = {"name": "Priya", "age": 25}   # starting dictionary

print(user.get("name"))                      # Output: Priya
print(user.get("city"))                      # Output: None  (no KeyError)
print(user.get("city", "Unknown"))           # Output: Unknown (custom default)

print(list(user.keys()))                     # Output: ['name', 'age']
print(list(user.values()))                   # Output: ['Priya', 25]
print(list(user.items()))                    # Output: [('name', 'Priya'), ('age', 25)]

for key, value in user.items():              # best way to loop key + value
    print(key, "->", value)                  # Output: name -> Priya  then  age -> 25

user.update({"age": 26, "city": "Pune"})     # change age, add city
print(user)                                  # Output: {'name': 'Priya', 'age': 26, 'city': 'Pune'}
user.update(country="India")                 # update also accepts keyword arguments
print(user["country"])                       # Output: India

removed = user.pop("city")                   # remove and get the value
print(removed)                               # Output: Pune
print(user.pop("zip", "no zip"))             # Output: no zip (default, no error)

print(user.setdefault("role", "student"))    # Output: student (key was missing, so it is set)
print(user.setdefault("role", "admin"))      # Output: student (key exists, value unchanged)

print(user.popitem())                        # Output: ('role', 'student')  (last inserted)
user.clear()                                 # remove everything
print(user)                                  # Output: {}
```

## 💻 Code Example — Advanced
```python
# Advanced: safe config handling, merging, grouping and view behaviour
from __future__ import annotations           # modern hints
from typing import Any                       # for flexible value type

Config = dict[str, Any]                      # type alias for readability


def merge_config(defaults: Config, overrides: Config) -> Config:
    """Return NEW dict: defaults updated by overrides (inputs untouched)."""
    result: Config = defaults.copy()         # copy so we do not mutate the caller's dict
    result.update(overrides)                 # overrides win on duplicate keys
    return result                            # return merged copy


def pop_required(data: Config, key: str) -> Any:
    """Pop a key or raise a clear error."""
    try:                                     # pop raises KeyError when missing
        return data.pop(key)                 # remove and return value
    except KeyError:                         # convert to friendlier error
        raise ValueError(f"Missing required field: {key}") from None


defaults: Config = {"debug": False, "port": 8000, "host": "0.0.0.0"}   # default settings
env: Config = {"port": 9000, "debug": True}                              # environment overrides
settings: Config = merge_config(defaults, env)                           # merge safely
print(settings)                              # Output: {'debug': True, 'port': 9000, 'host': '0.0.0.0'}
print(defaults["port"])                      # Output: 8000 (original unchanged)

# Python 3.9+ merge operators:
print(defaults | env == settings)            # Output: True  (| creates a new merged dict)
defaults |= {"port": 1}                      # in-place update operator (like update)
print(defaults["port"])                      # Output: 1

# setdefault for grouping (classic pattern):
words: list[str] = ["apple", "avocado", "banana", "blueberry", "cherry"]
groups: dict[str, list[str]] = {}            # first letter -> words
for w in words:                              # walk all words
    groups.setdefault(w[0], []).append(w)    # create list if missing, then append
print(groups)                                # Output: {'a': ['apple', 'avocado'], 'b': ['banana', 'blueberry'], 'c': ['cherry']}

# Views are LIVE:
stock: dict[str, int] = {"pen": 10}          # small stock dict
keys_view = stock.keys()                     # view, not a copy
stock["book"] = 5                            # change dict afterwards
print(list(keys_view))                       # Output: ['pen', 'book'] (view saw the change)

# Never change size while looping:
try:                                         # dict changed during iteration
    for k in stock:                          # iterate over dict
        stock["new_" + k] = 0                # adding keys while looping
except RuntimeError as err:                  # Python protects us
    print("Error:", err)                     # Output: Error: dictionary changed size during iteration

safe_copy: list[str] = list(stock)           # fix: loop over a snapshot
for k in safe_copy:                          # now modification is safe
    stock.pop(k)                             # remove while looping the snapshot
print(stock)                                 # Output: {}

try:                                         # required field handling
    pop_required({"a": 1}, "token")          # key not present
except ValueError as err:                    # catch friendly error
    print("Error:", err)                     # Output: Error: Missing required field: token
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
d = {"a": 1, "b": 2}
print(d.get("c", 0))                 # safe read with default
d.update({"b": 3, "c": 4})           # merge
for k, v in d.items():               # loop pairs
    print(k, v)
val = d.pop("a", None)               # delete and return
merged = {**d, "z": 9}               # spread-style merge
```

```javascript
// JavaScript
const d = { a: 1, b: 2 };
console.log(d.c ?? 0);               // safe read with default (undefined if missing)
Object.assign(d, { b: 3, c: 4 });   // merge
for (const [k, v] of Object.entries(d)) { console.log(k, v); }
const val = d.a; delete d.a;         // delete does NOT return the value
const merged = { ...d, z: 9 };       // spread merge
```

Key difference: Python raises `KeyError` on a missing key (JS gives `undefined`), and Python `pop` removes and returns in one step. FastAPI link: `dict.get` is used for headers, query params and optional JSON keys; `model.model_dump()` gives a dict you then modify with `update` / `pop`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `d[key]` for optional keys
```python
# Wrong:
# d["email"]                  # KeyError if missing
# Correct:
# d.get("email")              # None if missing
```

❌ Mistake 2: `get()` default hides a stored `None` / falsy value
```python
d = {"count": 0}
value = d.get("count") or 10     # Wrong: 0 is falsy, so we get 10
value = d.get("count", 10)       # Correct: default used ONLY if key missing -> 0
```

❌ Mistake 3: Changing a dict while looping over it
```python
# Wrong:
# for k in d: del d[k]           # RuntimeError: dictionary changed size during iteration
# Correct:
# for k in list(d): del d[k]     # loop over a copy of the keys
```

---

## 🧠 Tricky Interview Question

**Q**: "What is the difference between `d.get(k, f())` and `d.setdefault(k, f())`? When is `f()` called?"

**Answer**: In BOTH, `f()` is evaluated eagerly, before the method runs, even if the key exists. So an expensive default like `get(k, load_from_db())` runs the DB call every time. The difference: `get` only returns the default and does not store it, while `setdefault` also stores it in the dict. To avoid wasted work use `if k not in d: d[k] = f()`, or `defaultdict(f)` (which calls `f` lazily only for missing keys).

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `d[key]` and `d.get(key)`?
A1: `d[key]` raises `KeyError` if the key is missing. `d.get(key)` returns `None` (or your default) and never raises. Use `[]` when the key must exist (a missing key is a bug you want to see), and `get` for optional data such as optional JSON fields or headers.

Q2: What do `keys()`, `values()`, `items()` return?
A2: Dynamic view objects, not lists. They are iterable, support `len` and `in`, and reflect later changes to the dict. `keys()` and `items()` also behave like sets (you can do `d1.keys() & d2.keys()`). Wrap in `list()` if you need a snapshot or indexing.

Q3: How does `update()` work and what are the other ways to merge dicts?
A3: `d.update(other)` modifies `d` in place; same keys are overwritten by `other`. Other ways: `{**a, **b}` (new dict), `a | b` (new dict, Python 3.9+), `a |= b` (in place). Later dict wins on conflicts. All of these are shallow: nested dicts are not merged deeply.

Q4: What is the difference between `pop`, `popitem` and `del`?
A4: `pop(k[, default])` removes key k and returns its value. `popitem()` removes and returns the last inserted `(key, value)` pair (LIFO since 3.7), raising `KeyError` on an empty dict. `del d[k]` removes the key and returns nothing, raising `KeyError` if missing.

Q5: What does `setdefault` do and when is it useful?
A5: `d.setdefault(k, v)` returns `d[k]` if it exists; otherwise sets `d[k] = v` and returns `v`. It is useful for grouping: `d.setdefault(key, []).append(x)`. For heavy grouping, `collections.defaultdict(list)` is cleaner and faster because it does not build a new default every call.

---

## 🔷 When to Use These Methods

✅ Use:
- `get` for optional keys (headers, query params, optional JSON)
- `items()` when you need both key and value
- `update` / `|` to apply overrides on defaults
- `pop(k, None)` to safely remove fields (like passwords) before responding
- `setdefault` for simple grouping

❌ Avoid:
- `d[k]` on untrusted input (can crash with `KeyError`)
- `get(k) or default` when 0 / "" / False are valid values
- Modifying a dict while iterating it

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| View object | Live window over keys/values/items | Live view, copy नहीं |
| KeyError | Error for a missing key | Key न मिलने पर error |
| Default value | Fallback when key missing | Key न होने पर fallback |
| Shallow merge | Merge top level only | सिर्फ ऊपरी level merge |
| LIFO | Last in, first out | आख़िरी आया, पहले निकला |
| In-place | Changes the same object | उसी object में बदलाव |

---

## ⚡ 3-Line Summary
English: Use `get` for safe reads, `items()` for loops, `update` or `|` for merging, `pop(k, default)` for safe removal and `setdefault` to create-if-missing. Views are live, defaults are evaluated eagerly, and you must not change dict size while iterating.
Hindi: Safe read के लिए `get`, loop के लिए `items()`, merge के लिए `update`/`|`, safe removal के लिए `pop(k, default)`, और create-if-missing के लिए `setdefault`। Views live होते हैं, default पहले evaluate होता है, और iteration में dict का size न बदलें।

---

## ➡️ Next Topic
**060. Dictionary Comprehension** — build and transform dicts in one line, filters, inversion, nested comprehensions.
