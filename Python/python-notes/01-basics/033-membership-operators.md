---

# 033. Membership Operators (in, not in)
# हिंदी में: Membership Operators (in, not in) — मौजूद है या नहीं

---

## 🔵 Simple Definition (English)
`in` returns `True` if a value exists inside a container (list, tuple, set, dict keys, string, range). `not in` returns `True` if it does not. It reads like plain English: `"a" in "cat"`.

## 🔵 सरल परिभाषा (Hindi)
`in` बताता है कि कोई value container (list, tuple, set, dict की keys, string, range) के अंदर है या नहीं। `not in` इसका उल्टा है। English जैसा पढ़ा जाता है: `"a" in "cat"`।

---

## 🔴 Problem it Solves
In other languages you write loops or call `indexOf(...) !== -1` to test existence. That is noisy and error-prone. Python gives one readable operator that works on every container, and the container decides how to search efficiently (hash lookup for set/dict, scan for list).

## 🔴 यह क्यों बना? (Hindi)
दूसरी languages में existence check के लिए loop या `indexOf(...) !== -1` लिखना पड़ता है। Python में एक ही readable operator हर container पर चलता है, और container खुद तय करता है कि कैसे search करना है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python sees `x in container`
Step 2 → It calls container.__contains__(x) if defined
Step 3 → Otherwise it iterates the container and compares with ==
Step 4 → set / dict: hash lookup  -> O(1) average
Step 5 → list / tuple / str: linear scan -> O(n)
Step 6 → Result is bool; `not in` negates it
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `x in container` देखने पर Python __contains__ call करती है
Step 2 → न हो तो container को iterate करके == से compare करती है
Step 3 → set/dict में hash lookup (तेज़, O(1))
Step 4 → list/tuple/string में एक-एक करके scan (O(n))
```

---

## 🟡 Real World Example
Swiggy: `if pincode in SERVICEABLE_PINCODES:` (a set) decides whether delivery is possible. An AI app: `if "password" in user_prompt.lower():` flags risky prompts. FastAPI: `if role not in {"admin", "editor"}:` rejects unauthorised users.

## 🟡 Real Example Hindi mein
Swiggy में `pincode in SERVICEABLE_PINCODES` (set) से तय होता है कि delivery हो सकती है या नहीं। AI app में prompt में खास शब्द ढूँढने के लिए `in` use होता है।

---

## 💻 Code Example — Basic
```python
# Membership operators: in, not in
fruits: list[str] = ["apple", "mango", "banana"]     # a list of strings
print("mango" in fruits)                             # True  -> exists in list
print("grape" in fruits)                             # False -> not in list
print("grape" not in fruits)                         # True  -> negation

text: str = "Python is fun"                          # a string
print("fun" in text)                                 # True  -> substring check
print("Fun" in text)                                 # False -> case sensitive

user: dict[str, int] = {"id": 7, "age": 30}          # a dictionary
print("id" in user)                                  # True  -> checks KEYS
print(7 in user)                                     # False -> 7 is a value, not a key
print(7 in user.values())                            # True  -> check values explicitly

print(5 in range(1, 10))                             # True  -> range supports in efficiently
print(3 in (1, 2, 3))                                # True  -> tuple works too

name: str = "Aditya"                                 # variable to test
if name not in ["Riya", "Aman"]:                     # not in with list literal
    print("not in guest list")                       # runs
```
Output:
```
True
False
True
True
False
True
False
True
True
True
not in guest list
```

## 💻 Code Example — Advanced
```python
# Performance, custom __contains__, and chained usage
import time                                          # for timing
from typing import Iterable                          # type hint


class Whitelist:                                     # custom container
    def __init__(self, items: Iterable[str]) -> None:        # constructor
        self._items: frozenset[str] = frozenset(i.lower() for i in items)   # normalise

    def __contains__(self, item: object) -> bool:    # called by `in`
        return isinstance(item, str) and item.lower() in self._items   # case-insensitive


wl: Whitelist = Whitelist(["Admin", "Editor"])       # create whitelist
print("ADMIN" in wl)                                 # True  -> uses __contains__
print("guest" in wl)                                 # False
print(42 in wl)                                      # False -> not a str

# List vs set speed:
data_list: list[int] = list(range(100_000))          # 100k items in a list
data_set: set[int] = set(data_list)                  # same items in a set
target: int = 99_999                                 # worst case for the list

start = time.perf_counter()                          # start timer
for _ in range(200):                                 # repeat to measure
    target in data_list                              # linear scan
list_time: float = time.perf_counter() - start       # elapsed

start = time.perf_counter()                          # start timer
for _ in range(200):                                 # repeat to measure
    target in data_set                               # hash lookup
set_time: float = time.perf_counter() - start        # elapsed
print("set faster:", set_time < list_time)           # True (set is far faster)

# Gotchas:
print("" in "abc")                                   # True  -> empty string is in every string
print("ab" in ["abc"])                               # False -> list checks whole items
print([1, 2] in [[1, 2], [3]])                       # True  -> compares with ==
print(1 in {1: "a"})                                 # True  -> dict key
```
Output:
```
True
False
False
set faster: True
True
False
True
True
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
fruits = ["apple", "mango"]       # list
print("mango" in fruits)          # True
print("an" in "mango")            # True  (substring)
d = {"id": 1}                     # dict
print("id" in d)                  # True  (key check)
```
```javascript
// JavaScript
const fruits = ["apple", "mango"];    // array
console.log(fruits.includes("mango")); // true
console.log("mango".includes("an"));   // true (substring)
const d = { id: 1 };                   // object
console.log("id" in d);                // true  (JS `in` checks keys too!)
console.log(new Set([1]).has(1));      // true  (Set uses .has)
```
Key difference: JS `in` works only on object keys (and on arrays it checks INDEXES: `1 in ["a","b"]` is true). Python `in` checks the actual values for list/tuple/set and keys for dict.

---

## 🟠 FastAPI Connection
Use `in` with a set for fast validation of roles, allowed origins or API keys.

```python
from fastapi import FastAPI, HTTPException       # FastAPI + error class

app: FastAPI = FastAPI()                         # create app
ALLOWED_ROLES: set[str] = {"admin", "editor"}    # set -> O(1) lookup


@app.post("/publish")                            # POST /publish
async def publish(role: str) -> dict[str, str]:  # role comes from query
    if role not in ALLOWED_ROLES:                # membership check
        raise HTTPException(status_code=403, detail="Forbidden")   # reject
    return {"status": "published"}               # allowed
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting `in` on a dict to search values
```python
# Wrong:
d = {"a": 1}
print(1 in d)            # False! checks keys

# Correct:
print(1 in d.values())   # True
```

❌ Mistake 2: Using a big list for repeated lookups
```python
# Wrong — O(n) every time:
BLOCKED = ["u1", "u2", "u3"]   # imagine 1 million entries

# Correct — O(1) average:
BLOCKED_SET = {"u1", "u2", "u3"}
print("u2" in BLOCKED_SET)     # True
```

---

## 🧠 Tricky Interview Question

```python
print("a" in "abc" in "xabcx")
```
Answer: Comparison operators chain! `in` is a comparison operator, so this is `("a" in "abc") and ("abc" in "xabcx")`, which is `True and True`, so `True`. It is NOT `("a" in "abc") in "xabcx"` (that would raise TypeError: `True` is not a string). Same chaining applies to `is`, `<`, `==`.

---

## ⚫ Interview Questions + Answers

Q1: What does `in` check on a dictionary?
A1: Keys only. Use `.values()` or `.items()` for values or pairs.

Q2: Time complexity of `in` for list, set, dict?
A2: list/tuple/str: O(n). set/dict: O(1) average (hash), O(n) worst case with many collisions. range: O(1) for ints.

Q3: How does `in` work on a custom class?
A3: Python calls `__contains__`. If missing, it falls back to `__iter__`, then to `__getitem__` with indexes 0, 1, 2... until IndexError.

Q4: Is `"" in "abc"` True?
A4: Yes. The empty string is a substring of every string.

Q5: Why does `x in [1, 2, float("nan")]` fail for NaN?
A5: `in` checks identity first, then equality. NaN != NaN, but `nan in [nan]` is True if it is the same object. A fresh `float("nan")` is a different object, so it returns False. Edge case worth knowing.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Checking if a key, item or substring exists
- Validating against allowed values (use a set)

❌ Avoid when:
- You need the position (use `.index()` or `.find()`)
- Looking up in a huge list repeatedly (convert to set first)

---

## 📊 Visual Diagram
```
x in container
      │
      ▼
 has __contains__? ──yes──► call it
      │ no
      ▼
 iterate & compare (==) ──► True / False

 set / dict  : hash  → O(1)
 list / str  : scan  → O(n)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Membership | Presence in a container | Container में मौजूद होना |
| Container | Object holding items | Items रखने वाला object |
| __contains__ | Method behind `in` | `in` के पीछे का method |
| Hashing | Fast key lookup | तेज़ lookup तकनीक |
| Substring | Part of a string | String का हिस्सा |
| Chaining | a < b < c style comparisons | जुड़े हुए comparisons |

---

## ⚡ 3-Line Summary
English: `in` and `not in` test presence in lists, strings, sets, dict keys and ranges. Sets and dicts are O(1); lists are O(n). Custom classes support it through `__contains__`.
Hindi: `in` / `not in` से container में मौजूदगी check होती है। Set/dict तेज़ (O(1)), list धीमी (O(n))। Custom class में `__contains__` से काम करता है।

---

## ➡️ Next Topic
**034. Operator Precedence** — which operator runs first when many are mixed in one expression.
