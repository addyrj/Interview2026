---

# 032. Identity Operators (is, is not)
# हिंदी में: Identity Operators (is, is not) — एक ही object है या नहीं

---

## 🔵 Simple Definition (English)
`is` checks whether two names point to the exact same object in memory. `is not` is the opposite. It does not compare values — that is the job of `==`. Think of it as "same house" versus "same-looking house".

## 🔵 सरल परिभाषा (Hindi)
`is` check करता है कि दो variables memory में बिल्कुल एक ही object को point कर रहे हैं या नहीं। `is not` इसका उल्टा है। यह value compare नहीं करता — वह `==` का काम है। `is` = "एक ही घर", `==` = "एक जैसे दिखने वाले घर"।

---

## 🔴 Problem it Solves
Sometimes you must know if two references are the same object, not just equal. Example: a function default of `None` versus an empty list `[]` — both are "empty" but different. Also, `==` can be overridden by a class (`__eq__`) and can lie; `is` cannot be overridden, so it is the safe way to test for singletons like `None`.

## 🔴 यह क्यों बना? (Hindi)
कभी-कभी जानना जरूरी होता है कि दो references एक ही object हैं, सिर्फ बराबर नहीं। `==` को class में override (`__eq__`) किया जा सकता है, पर `is` को नहीं। इसलिए `None` जैसे singleton को check करने का सबसे safe तरीका `is` है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python creates objects in memory; each has a unique id() (address in CPython)
Step 2 → Variables are just names (labels) pointing to those objects
Step 3 → `a is b` compares id(a) == id(b)  — no value comparison
Step 4 → Returns True only if both names point to the SAME object
Step 5 → `a is not b` is the same as `not (a is b)`
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर object का एक unique id() होता है
Step 2 → Variable सिर्फ एक label है जो object को point करता है
Step 3 → `a is b` मतलब id(a) == id(b)
Step 4 → एक ही object हो तो True, वरना False
```

---

## 🟡 Real World Example
Zomato backend: `if coupon is None:` decides "no coupon applied". Razorpay SDK style code: `if response is not None:` before reading the payment status. A cache layer uses a unique `MISSING = object()` sentinel so that a cached value of `None` can be told apart from "key not found" — only `is` can do that reliably.

## 🟡 Real Example Hindi mein
Zomato में `if coupon is None:` से तय होता है कि coupon लगा या नहीं। Cache में `MISSING = object()` sentinel रखते हैं ताकि cached `None` और "key मिली ही नहीं" में फर्क हो सके — यह सिर्फ `is` से भरोसेमंद तरीके से होता है।

---

## 💻 Code Example — Basic
```python
# Identity operators: is, is not
from typing import Optional                      # import Optional for type hints

a: list[int] = [1, 2, 3]                         # create a list object
b: list[int] = [1, 2, 3]                         # create ANOTHER list with same values
c: list[int] = a                                 # c points to the SAME object as a

print(a == b)                                    # True  -> values are equal
print(a is b)                                    # False -> different objects
print(a is c)                                    # True  -> same object
print(a is not b)                                # True  -> not the same object
print(id(a) == id(c))                            # True  -> is compares ids

c.append(4)                                      # mutate through c
print(a)                                         # [1, 2, 3, 4] -> a changed too (same object)

value: Optional[str] = None                      # a variable that may be None
if value is None:                                # correct way to test None
    print("value is missing")                    # runs because value is None
if value is not None:                            # opposite check
    print("value present")                       # does not run

flag: bool = True                                # a boolean
print(flag is True)                              # True -> True is a singleton
```
Output:
```
True
False
True
True
True
[1, 2, 3, 4]
value is missing
True
```

## 💻 Code Example — Advanced
```python
# Sentinel pattern + interning + __eq__ override trap
from typing import Any, Optional                 # typing helpers

MISSING: object = object()                       # unique sentinel, nobody else can create it

cache: dict[str, Optional[int]] = {"a": None}    # cache where None is a VALID stored value


def get(key: str) -> Any:                        # look up a key in cache
    value = cache.get(key, MISSING)              # default is the sentinel
    if value is MISSING:                         # identity check, never fooled by None
        return "cache miss"                      # key truly absent
    return f"hit:{value}"                        # key present (value may be None)


print(get("a"))                                  # hit:None  (None stored, still a hit)
print(get("b"))                                  # cache miss


class AlwaysEqual:                               # class that lies about equality
    def __eq__(self, other: object) -> bool:     # override ==
        return True                              # claims to equal everything


x: AlwaysEqual = AlwaysEqual()                   # create instance
print(x == None)                                 # True  -> == is fooled   # noqa: E711
print(x is None)                                 # False -> is cannot be fooled

# Small int cache: CPython reuses ints from -5 to 256
n1: int = int("256")                             # built at runtime
n2: int = int("256")                             # built at runtime
print(n1 is n2)                                  # True  -> cached small int
m1: int = int("1000")                            # outside the cache range
m2: int = int("1000")                            # another object
print(m1 is m2)                                  # False -> different objects
print(m1 == m2)                                  # True  -> equal values
```
Output:
```
hit:None
cache miss
True
False
True
False
True
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: is = identity, == = value equality
a = [1, 2]                      # list object
b = [1, 2]                      # another list object
print(a == b)                   # True  (value equality)
print(a is b)                   # False (different objects)
print(None is None)             # True
```
```javascript
// JavaScript: === on objects is identity; on primitives it is value
const a = [1, 2];               // array object
const b = [1, 2];               // another array object
console.log(a === b);           // false (identity for objects)
console.log(1 === 1);           // true  (value for primitives)
console.log(null === null);     // true
```
Key difference: JS `===` mixes identity (objects) and value (primitives). Python separates them cleanly: `==` is value, `is` is identity. Python has no `===`.

---

## 🟠 FastAPI Connection
In FastAPI, optional query parameters default to `None`. You must test them with `is None`, not truthiness, because `0` or `""` are valid user values.

```python
from typing import Optional                      # Optional type
from fastapi import FastAPI                      # FastAPI class

app: FastAPI = FastAPI()                         # create app


@app.get("/items")                               # GET /items
async def items(min_price: Optional[int] = None) -> dict:   # optional param
    if min_price is None:                        # not sent by client
        return {"filter": "none"}                # no filtering
    return {"filter": min_price}                 # 0 is valid, so `is None` matters
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `is` to compare strings or numbers
```python
# Wrong — works by accident for small values, fails for others:
x = int("1000")
y = int("1000")
# if x is y:  ...      # False! Different objects

# Correct — use == for values:
if x == y:               # True
    print("equal")
```

❌ Mistake 2: Using `== None` instead of `is None`
```python
# Wrong — can be fooled by __eq__ and linters flag it (E711):
# if value == None: ...

# Correct:
value = None
if value is None:        # identity check on a singleton
    print("none")
```

---

## 🧠 Tricky Interview Question

```python
a = "hello"
b = "hello"
print(a is b)

c = "hello world!"
d = "hello world!"
print(c is d)

e = 257
f = 257
print(e is f)
```
Answer: Results depend on context. String literals that look like identifiers ("hello") are interned, so `True`. In a single script/module, the compiler also often merges identical constants, so even `c is d` and `e is f` can print `True` when run as a file but `False` in the interactive REPL. Lesson: never rely on `is` for strings/ints; it is an implementation detail. Use `==`.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `==` and `is`?
A1: `==` compares values by calling `__eq__`. `is` compares object identity (`id(a) == id(b)`). Use `==` for values, `is` for singletons.

Q2: Why `is None` instead of `== None`?
A2: `None` is a singleton, so identity is exact and fast. `__eq__` can be overridden to return True for None, giving wrong results. PEP 8 mandates `is None`.

Q3: Can `is` be overloaded?
A3: No. There is no `__is__` method. That is why it is trusted for sentinel checks.

Q4: Why does `256 is 256` give True but `1000 is 1000` may not?
A4: CPython pre-creates small ints from -5 to 256 and reuses them. Larger ints are created fresh (unless the compiler merges constants). It is an implementation detail.

Q5: What is a sentinel object?
A5: A unique object like `MISSING = object()` used to mean "no value given", distinct from `None`. Checked with `is`. Used in `dataclasses.MISSING`, `functools`, caches.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Checking `None`, `True`, `False`
- Sentinel objects
- Checking if two references share one mutable object

❌ Avoid when:
- Comparing numbers, strings, lists by value (use `==`)
- You depend on interning or small-int caching

---

## 📊 Visual Diagram
```
a = [1,2]   b = [1,2]   c = a

 a ──┐
     ├──► [1,2]  (id 1001)      a is c  -> True
 c ──┘
 b ─────► [1,2]  (id 2002)      a is b  -> False,  a == b -> True
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Identity | Same object in memory | एक ही object |
| Equality | Same value | बराबर value |
| id() | Unique object identifier | Object की पहचान |
| Singleton | Only one instance exists | सिर्फ एक instance |
| Sentinel | Special marker object | Special निशान object |
| Interning | Reusing identical objects | Same object reuse करना |

---

## ⚡ 3-Line Summary
English: `is` tests same object; `==` tests same value. Use `is` only for None, True, False and sentinels. Never use `is` on numbers or strings.
Hindi: `is` = एक ही object, `==` = एक जैसी value। `is` सिर्फ None, True, False और sentinel के लिए use करें। Numbers/strings पर `is` कभी नहीं।

---

## ➡️ Next Topic
**033. Membership Operators (in, not in)** — checking if an item exists inside a list, string, dict or set.
