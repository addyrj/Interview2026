---

# 068. frozenset
# हिंदी में: frozenset (अपरिवर्तनीय set)

---

## 🔵 Simple Definition (English)
`frozenset` is an immutable (unchangeable) version of `set`. It stores unique, unordered items, but you cannot add or remove anything after creation. Because it is immutable, it is hashable — so it can be a dict key or an element of another set.

## 🔵 सरल परिभाषा (Hindi)
`frozenset`, `set` का immutable version है। इसमें unique और unordered items होते हैं, लेकिन बनने के बाद add/remove नहीं कर सकते। Immutable होने की वजह से यह hashable है — इसलिए dict का key या दूसरे set का element बन सकता है।

---

## 🔴 Problem it Solves
A normal `set` is mutable, so it is NOT hashable. That means `{ {1,2}, {3} }` fails with `TypeError: unhashable type: 'set'`, and `{ {1,2}: "x" }` fails too. Sometimes you need "a group of unique items" as a key: permissions of a role, a pair of users in a friendship, a visited state in a graph search. Also, shared constants (like allowed roles) can be accidentally modified if stored in a normal set.

## 🔴 यह क्यों बना? (Hindi)
Normal `set` mutable है, इसलिए hashable नहीं। `{ {1,2}: "x" }` error देता है। कई बार "unique items का group" key बनाना होता है — role की permissions, दो users की friendship pair, graph का visited state। साथ ही shared constants गलती से बदल न जाएँ — इसलिए frozenset।

---

## 🟢 How it Works — Step by Step

```
Step 1 → frozenset([1, 2, 2, 3]) iterates the input
Step 2 → Duplicates are removed (hash + equality check), like set
Step 3 → Contents are locked: no add(), remove(), discard(), pop(), clear()
Step 4 → Since contents never change, hash(fs) is computed from items
Step 5 → Hashable → usable as dict key / set element
Step 6 → Read operations still work: in, len, |, &, -, ^, issubset...
         (these return a NEW frozenset, never modify the original)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → frozenset(iterable) input पर iterate करता है
Step 2 → Duplicates हट जाते हैं (set की तरह)
Step 3 → Contents lock — add/remove/pop कुछ नहीं चलेगा
Step 4 → Contents fixed हैं, इसलिए hash बन सकता है
Step 5 → Hashable → dict key / set element बन सकता है
Step 6 → |, &, -, ^ चलते हैं, पर हमेशा NEW frozenset return करते हैं
```

---

## 🟡 Real World Example
Razorpay-style permission system: each role has a fixed set of permissions (`frozenset({"read", "refund"})`). Cache keys: a FastAPI service caches results per "set of filters" — `frozenset(filters.items())` is a hashable cache key. Swiggy: a delivery graph where each state is "set of orders already picked" — stored in a `visited` set as frozensets.

## 🟡 Real Example Hindi mein
Razorpay जैसे system में हर role की fixed permissions होती हैं — `frozenset({"read","refund"})`। FastAPI में filters के आधार पर cache करना हो तो `frozenset(filters.items())` hashable cache key बनता है। Swiggy जैसे graph search में "कौन-से orders pick हो चुके" का state frozenset में `visited` set में रखते हैं।

---

## 💻 Code Example — Basic
```python
# Basic frozenset example
from typing import FrozenSet                      # type hint for frozenset

nums: FrozenSet[int] = frozenset([1, 2, 2, 3])    # duplicates removed
print(len(nums))                                  # 3
print(2 in nums)                                  # True  (fast O(1) lookup)

# Set operations return NEW frozensets
a: FrozenSet[int] = frozenset({1, 2, 3})          # first frozenset
b: FrozenSet[int] = frozenset({3, 4})             # second frozenset
print(sorted(a | b))                              # [1, 2, 3, 4]  union
print(sorted(a & b))                              # [3]           intersection
print(sorted(a - b))                              # [1, 2]        difference
print(sorted(a ^ b))                              # [1, 2, 4]     symmetric diff
print(a.issubset({1, 2, 3, 4}))                   # True

# Mutation is NOT allowed
try:
    nums.add(10)                                  # no add() method exists
except AttributeError as e:
    print("Error:", e)                            # Error: 'frozenset' object has no attribute 'add'

# Hashable -> can be dict key
perms: dict[FrozenSet[str], str] = {
    frozenset({"read", "write"}): "editor",       # frozenset as key
}
print(perms[frozenset({"write", "read"})])        # editor  (order does not matter)

# Normal set cannot be a key
try:
    bad = {{1, 2}: "x"}                           # set inside dict key
except TypeError as e:
    print("Error:", e)                            # Error: unhashable type: 'set'
```

## 💻 Code Example — Advanced
```python
# Production style: immutable role permissions + hashable cache key
from __future__ import annotations                # allow modern hints
from dataclasses import dataclass                 # simple data class
from typing import FrozenSet, Mapping             # type hints
from functools import lru_cache                   # memoization


@dataclass(frozen=True)                           # frozen dataclass -> hashable
class Role:
    name: str                                     # role name
    permissions: FrozenSet[str]                   # immutable permissions

    def can(self, action: str) -> bool:           # check one permission
        return action in self.permissions         # O(1) membership


ADMIN = Role("admin", frozenset({"read", "write", "delete"}))   # constant
VIEWER = Role("viewer", frozenset({"read"}))                    # constant


def merge_roles(*roles: Role) -> FrozenSet[str]:
    """Union of all permissions across roles."""
    result: FrozenSet[str] = frozenset()          # start empty
    for role in roles:                            # loop every role
        result = result | role.permissions        # new frozenset each time
    return result                                 # immutable result


@lru_cache(maxsize=128)                           # args must be hashable!
def expensive_report(filters: FrozenSet[tuple[str, str]]) -> str:
    # pretend this is a heavy DB query
    return f"report for {sorted(filters)}"        # deterministic output


def make_key(params: Mapping[str, str]) -> FrozenSet[tuple[str, str]]:
    return frozenset(params.items())              # dict -> hashable key


if __name__ == "__main__":
    print(merge_roles(ADMIN, VIEWER) == ADMIN.permissions)   # True
    print(VIEWER.can("delete"))                              # False

    key1 = make_key({"city": "Pune", "type": "veg"})         # call 1
    key2 = make_key({"type": "veg", "city": "Pune"})         # same, diff order
    print(key1 == key2)                                      # True
    print(expensive_report(key1))                            # report for [('city', 'Pune'), ('type', 'veg')]
    expensive_report(key2)                                   # served from cache
    print(expensive_report.cache_info().hits)                # 1

    # Set of sets (graph "visited" states)
    visited: set[FrozenSet[int]] = set()                     # outer set
    visited.add(frozenset({1, 2}))                           # inner frozenset
    print(frozenset({2, 1}) in visited)                      # True

    try:
        ADMIN.permissions.add("x")                           # type: ignore[attr-defined]
    except AttributeError:
        print("permissions are read-only")                   # permissions are read-only
```

---

## 🟠 JavaScript vs Python Comparison
JS has `Set` (mutable) and no native frozen Set. `Object.freeze(new Set())` does NOT stop `.add()` because freeze only locks object properties, not internal slots. Also JS Sets compare by reference, so a Set cannot be a "value-equal" Map key. Python's `frozenset` gives value-based hashing: two frozensets with the same items are equal and have the same hash.

```python
# Python way
a = frozenset({1, 2})
b = frozenset({2, 1})
print(a == b)            # True  — value equality
d = {a: "ok"}
print(d[b])              # ok    — works as key
```
```javascript
// JavaScript way
const a = Object.freeze(new Set([1, 2]));
a.add(3);                                  // STILL works! freeze doesn't protect Set
const m = new Map([[new Set([1, 2]), "ok"]]);
console.log(m.get(new Set([1, 2])));       // undefined — reference comparison
// workaround: use JSON.stringify([...set].sort()) as a string key
```

---

## 🟠 FastAPI Connection
In FastAPI you can use `frozenset` for constants like allowed scopes or allowed HTTP methods, so nobody mutates them at runtime. It also works as an `lru_cache` argument for dependencies. Pydantic accepts `frozenset[str]` fields too.

```python
from fastapi import FastAPI, HTTPException, Depends   # FastAPI imports
from pydantic import BaseModel                        # request models

app = FastAPI()                                       # app instance
ALLOWED_SCOPES: frozenset[str] = frozenset({"read", "write"})   # constant

class TokenRequest(BaseModel):
    scopes: frozenset[str]                            # pydantic converts list -> frozenset

@app.post("/token")
def create_token(req: TokenRequest) -> dict[str, list[str]]:
    invalid = req.scopes - ALLOWED_SCOPES             # frozenset difference
    if invalid:                                       # unknown scopes found
        raise HTTPException(400, f"Invalid scopes: {sorted(invalid)}")
    return {"scopes": sorted(req.scopes)}             # JSON needs list
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trying to modify a frozenset
```python
# Wrong
fs = frozenset({1, 2})
fs.add(3)                 # AttributeError: no attribute 'add'

# Right — build a new one
fs = fs | {3}             # new frozenset({1, 2, 3})
```

❌ Mistake 2: Putting a mutable item (list) inside a frozenset
```python
# Wrong
fs = frozenset([[1, 2], [3]])     # TypeError: unhashable type: 'list'

# Right — use tuples
fs = frozenset([(1, 2), (3,)])    # works
```

❌ Mistake 3: Expecting `{}` to make an empty set / frozenset
```python
# Wrong
empty = {}                # this is a dict!
# Right
empty = frozenset()       # empty frozenset
```

---

## 🧠 Tricky Interview Question

```python
a = {1, 2}
b = frozenset({1, 2})
print(a == b)
print(type(a | b), type(b | a))
d = {a: 1}
```
Answer: `a == b` is `True` (set and frozenset compare by value). `a | b` returns the type of the LEFT operand: `set`; `b | a` returns `frozenset`. So output is `True <class 'set'> <class 'frozenset'>`. The last line raises `TypeError: unhashable type: 'set'` because `a` is a plain set. Equal value does not make a plain set hashable.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between set and frozenset?
A1: Both store unique unordered items with O(1) membership. `set` is mutable (add/remove) and unhashable. `frozenset` is immutable and hashable, so it can be a dict key or a set element. Both support union, intersection, difference.

Q2: Why can't a set contain another set?
A2: Set elements must be hashable. A `set` is mutable, so its hash could change; Python refuses (`unhashable type: 'set'`). Use `frozenset` for the inner sets.

Q3: What type does `frozenset | set` return?
A3: The type of the left operand. `frozenset({1}) | {2}` -> `frozenset`; `{2} | frozenset({1})` -> `set`.

Q4: Is frozenset ordered? How is its hash computed?
A4: No, it is unordered. Its hash is order-independent (computed from the hashes of elements using a commutative mix), so `frozenset({1,2})` and `frozenset({2,1})` have equal hashes.

Q5: When would you use frozenset in a backend?
A5: Constant permission/scope lists, cache keys for filter combinations (`lru_cache` needs hashable args), graph-search visited states, and dict keys for "unordered pairs" like `frozenset({user_a, user_b})`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need a set as a dict key or inside another set
- You want constants that must never change (roles, scopes)
- You need hashable arguments for `lru_cache`

❌ Avoid when:
- You need to add/remove items often (use `set`)
- Order matters (use list/tuple)
- You need duplicates (use list/Counter)

---

## 📊 Visual Diagram
```
 set (mutable)                     frozenset (immutable)
 +--------------+                  +--------------+
 | 1  2  3      |  add/remove OK   | 1  2  3      |  add/remove X
 +--------------+                  +--------------+
 hash(): TypeError                 hash(): works
 dict key: NO                      dict key: YES
 inside set: NO                    inside set: YES

 frozenset({1,2}) | {3}  ──►  NEW frozenset({1,2,3})   (original untouched)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Immutable | Cannot change after creation | बनने के बाद बदल नहीं सकता |
| Hashable | Has a stable hash, usable as dict key | Hash हो सकता है, key बन सकता है |
| Union | All items from both sets | दोनों के सभी items |
| Intersection | Items common to both | दोनों में common items |
| Symmetric difference | In one but not both | किसी एक में, दोनों में नहीं |
| Memoization | Caching function results | Function results को cache करना |

---

## ⚡ 3-Line Summary
English: `frozenset` is an immutable, hashable set. Use it as a dict key, set element, constant, or `lru_cache` argument. Operations return new frozensets; the type follows the left operand.
Hindi: `frozenset` immutable और hashable set है। इसे dict key, set element, constant या `lru_cache` argument की तरह use करें। Operations नया frozenset देते हैं; type left operand जैसा होता है।

---

## ➡️ Next Topic
**069. String — Complete Guide** — strings are immutable sequences too; learn how Python stores and handles text.
