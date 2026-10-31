---

# 066. Set Methods (add, remove, discard, union, intersection, difference)
# हिंदी में: Set के Methods

---

## 🔵 Simple Definition (English)
A set is an unordered collection of unique, hashable items. Set methods let you change it (`add`, `remove`, `discard`, `pop`, `clear`) and combine sets with math-style operations: `union` (all), `intersection` (common), `difference` (only in first), `symmetric_difference` (in one but not both), plus checks like `issubset`.

## 🔵 सरल परिभाषा (Hindi)
Set unique, hashable items का unordered collection है। Set methods से आप इसे बदल सकते हैं (`add`, `remove`, `discard`, `pop`, `clear`) और math जैसे operations कर सकते हैं: `union` (सब), `intersection` (common), `difference` (सिर्फ पहले में), `symmetric_difference` (किसी एक में, दोनों में नहीं), और `issubset` जैसे checks।

---

## 🔴 Problem it Solves
Finding "users who bought A and B", "emails in list 1 but not list 2" or removing duplicates with lists needs nested loops (O(n*m)). Sets use hashing, so membership tests are O(1) and these operations run in about O(n + m). The code is also shorter and mirrors Venn diagrams.

## 🔴 यह क्यों बना? (Hindi)
"A और B दोनों खरीदने वाले users", "list 1 में पर list 2 में नहीं emails" या duplicates हटाने के लिए lists में nested loops (O(n*m)) लगते हैं। Set hashing use करता है, इसलिए membership O(1) और operations लगभग O(n + m) में होते हैं। Code छोटा और Venn diagram जैसा।

---

## 🟢 How it Works — Step by Step

```
Step 1 → s = {1, 2, 3}              → hash table of unique items
Step 2 → s.add(4)                   → hash 4, insert if absent (duplicates ignored)
Step 3 → s.remove(9) / s.discard(9) → remove raises KeyError if missing; discard stays silent
Step 4 → a | b  or a.union(b)       → new set with items in a OR b
Step 5 → a & b  or a.intersection(b)→ items in BOTH
Step 6 → a - b  or a.difference(b)  → items in a but NOT in b;  a ^ b = in exactly one
```

## 🟢 कैसे काम करता है? (Hindi)
```
add(x) → नया हो तो जुड़ता है, duplicate ignore
remove(x) → नहीं मिला तो KeyError;  discard(x) → चुपचाप
union / | → a या b में;   intersection / & → दोनों में
difference / - → a में पर b में नहीं;   ^ → किसी एक में
```

---

## 🟡 Real World Example
Swiggy marketing: `ordered_pizza & ordered_burger` finds customers who ordered both; `all_users - active_users` finds inactive users to re-engage. In FastAPI, permission checks use sets: `required_scopes <= user_scopes` (subset) tells whether a token has all needed scopes.

## 🟡 Real Example Hindi mein
Swiggy marketing में `ordered_pizza & ordered_burger` दोनों खरीदने वाले users देता है; `all_users - active_users` inactive users देता है। FastAPI में permissions के लिए sets: `required_scopes <= user_scopes` (subset) बताता है कि token के पास सारे scopes हैं या नहीं।

---

## 💻 Code Example — Basic
```python
# Basic: set methods and set algebra
s: set[int] = {1, 2, 3}                      # create a set
s.add(4)                                     # add one item
s.add(2)                                     # duplicate: ignored silently
print(sorted(s))                             # Output: [1, 2, 3, 4]

s.remove(4)                                  # remove existing item
s.discard(99)                                # missing item: no error
try:                                         # remove of a missing item must fail
    s.remove(99)                             # raises KeyError
except KeyError as err:                      # handle it
    print("KeyError:", err)                  # Output: KeyError: 99

a: set[int] = {1, 2, 3, 4}                   # first set
b: set[int] = {3, 4, 5}                      # second set
print(sorted(a.union(b)))                    # Output: [1, 2, 3, 4, 5]
print(sorted(a.intersection(b)))             # Output: [3, 4]
print(sorted(a.difference(b)))               # Output: [1, 2]
print(sorted(a.symmetric_difference(b)))     # Output: [1, 2, 5]

print(sorted(a | b), sorted(a & b), sorted(a - b), sorted(a ^ b))   # operator forms
# Output: [1, 2, 3, 4, 5] [3, 4] [1, 2] [1, 2, 5]

print({1, 2}.issubset(a))                    # Output: True   ({1,2} is inside a)
print(a.issuperset({1, 2}))                  # Output: True
print(a.isdisjoint({10, 11}))                # Output: True   (nothing in common)

a.update({7, 8})                             # in-place union with another iterable
a.difference_update({7})                     # in-place remove of items found in other
print(sorted(a))                             # Output: [1, 2, 3, 4, 8]

print(sorted(set([3, 1, 3, 2, 1])))          # Output: [1, 2, 3]  (remove duplicates)
```

## 💻 Code Example — Advanced
```python
# Advanced: permissions, de-duplication keeping order, and user segmentation
from __future__ import annotations           # modern hints
from typing import Hashable, Iterable, TypeVar   # typing helpers

T = TypeVar("T", bound=Hashable)             # any hashable item type


def has_permissions(required: set[str], granted: set[str]) -> bool:
    """True when the user has ALL required scopes."""
    return required <= granted               # subset test


def missing_permissions(required: set[str], granted: set[str]) -> set[str]:
    """Return scopes the user is missing."""
    return required - granted                # required but not granted


def unique_in_order(items: Iterable[T]) -> list[T]:
    """Remove duplicates but keep first-seen order (set alone loses order)."""
    seen: set[T] = set()                     # items already added
    out: list[T] = []                        # ordered result
    for item in items:                       # walk items
        if item not in seen:                 # O(1) membership check
            seen.add(item)                   # remember it
            out.append(item)                 # keep it
    return out                               # ordered unique list


granted: set[str] = {"read", "write"}        # scopes in token
print(has_permissions({"read"}, granted))    # Output: True
print(has_permissions({"read", "admin"}, granted))   # Output: False
print(missing_permissions({"read", "admin"}, granted))   # Output: {'admin'}

print(unique_in_order([3, 1, 3, 2, 1]))      # Output: [3, 1, 2]

# User segmentation (Venn diagram thinking):
pizza: set[int] = {1, 2, 3, 4}               # user ids who ordered pizza
burger: set[int] = {3, 4, 5}                 # user ids who ordered burger
print(sorted(pizza & burger))                # Output: [3, 4]   both
print(sorted(pizza | burger))                # Output: [1, 2, 3, 4, 5]   either
print(sorted(pizza - burger))                # Output: [1, 2]   only pizza
print(sorted(pizza ^ burger))                # Output: [1, 2, 5]   exactly one

# Multi-set operations in one call:
a, b, c = {1, 2, 3}, {2, 3, 4}, {3, 4, 5}
print(set.intersection(a, b, c))             # Output: {3}
print(sorted(set.union(a, b, c)))            # Output: [1, 2, 3, 4, 5]

# Method vs operator: methods accept any iterable, operators need sets
print(sorted({1, 2}.union([2, 3])))          # Output: [1, 2, 3]
try:                                         # operator with a list fails
    {1, 2} | [2, 3]                          # type: ignore
except TypeError as err:                     # expected error
    print("Error:", err)                     # Output: Error: unsupported operand type(s) for |: 'set' and 'list'

# Sets can hold only hashable items:
try:                                         # list inside set
    {[1, 2]}                                 # type: ignore
except TypeError as err:                     # unhashable
    print("Error:", err)                     # Output: Error: unhashable type: 'list'

# pop() removes an ARBITRARY element; on empty set it raises
empty: set[int] = set()                      # NOTE: {} would be an empty dict
try:                                         # nothing to pop
    empty.pop()                              # raises KeyError
except KeyError as err:                      # handle it
    print("KeyError:", err)                  # Output: KeyError: 'pop from an empty set'
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
a, b = {1, 2, 3}, {2, 3, 4}
print(a | b, a & b, a - b)           # union, intersection, difference: one operator each
a.add(9); a.discard(1)
print(2 in a)                        # O(1) membership
```

```javascript
// JavaScript
const a = new Set([1, 2, 3]), b = new Set([2, 3, 4]);
const union = new Set([...a, ...b]);                    // no operator
const inter = new Set([...a].filter(x => b.has(x)));    // manual
const diff = new Set([...a].filter(x => !b.has(x)));    // manual
// Newer engines: a.union(b), a.intersection(b), a.difference(b)
a.add(9); a.delete(1);               // delete == discard (never throws)
console.log(a.has(2));
```

Key difference: Python has operators `| & - ^` since forever; JS needs spread + filter (or new Set methods in recent engines). Python `{}` is an empty DICT, use `set()`. FastAPI link: query params like `?tag=a&tag=b` can be received as `set[str]` and Pydantic removes duplicates; scopes and roles are handled as sets.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Creating an empty set with `{}`
```python
x = {}            # Wrong: this is a dict
x = set()         # Correct
```

❌ Mistake 2: Using `remove` when the item may not exist
```python
s = {1}
# s.remove(5)      # Wrong: KeyError
s.discard(5)       # Correct: no error
```

❌ Mistake 3: Expecting order or indexing
```python
s = {3, 1, 2}
# s[0]             # TypeError: 'set' object is not subscriptable
# Correct: sorted(s)  (returns a list), or keep order with dict.fromkeys(items)
```

---

## 🧠 Tricky Interview Question

**Q**: "What is the difference between `a.union(b)` and `a.update(b)`, and what is `{1,2,3} - {2}` vs `{1,2,3}.remove(2)`?"

**Answer**: `union` returns a NEW set and leaves `a` unchanged; `update` changes `a` in place and returns `None`. Same pattern: `a - b` / `difference` returns a new set, `difference_update` mutates. `{1,2,3} - {2}` creates a new set `{1, 3}` and the original stays `{1, 2, 3}`, while `.remove(2)` changes the original and returns `None`. A common bug is `a = a.update(b)`, which sets `a` to `None`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `remove()`, `discard()` and `pop()`?
A1: `remove(x)` deletes x and raises `KeyError` if it is absent. `discard(x)` deletes x if present and does nothing otherwise. `pop()` removes and returns an arbitrary element, raising `KeyError` on an empty set. Use `discard` when absence is fine, `remove` when absence is a bug.

Q2: What is the time complexity of set operations?
A2: `add`, `remove`, `discard` and `in` are O(1) on average (hash table). `union`, `intersection`, `difference` are O(len(a) + len(b)) (intersection is O(min) in practice). Compare with a list where `in` is O(n), which is why converting a list to a set for repeated lookups is a standard optimization.

Q3: Operator vs method form: which should I use?
A3: Operators (`| & - ^`) need both sides to be sets. Methods (`union`, `intersection`...) accept any iterable, e.g. a list or a generator, and can take several arguments. In-place versions: `update`, `intersection_update`, `difference_update`, `symmetric_difference_update` (or `|= &= -= ^=`).

Q4: How do you remove duplicates from a list and keep order?
A4: `list(dict.fromkeys(items))` is the shortest (dicts keep insertion order). Or loop with a `seen` set as in the advanced example. `list(set(items))` removes duplicates but the order is arbitrary.

Q5: How does a set check if two lists share an element fast?
A5: Convert one to a set and test the other: `not set(a).isdisjoint(b)` is O(len(a) + len(b)). The nested loop version is O(n*m). `isdisjoint` stops as soon as it finds a common element.

---

## 🔷 When to Use Set Methods

✅ Use when:
- Removing duplicates, fast membership tests
- Venn-style logic (common, only-in-A, either)
- Permission / tag / role checks (subset, superset)

❌ Avoid when:
- Order or duplicates matter (use list or dict)
- Items are unhashable (lists, dicts)
- You need indexing or slicing

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Union | All items of both | दोनों के सब items |
| Intersection | Items common to both | दोनों में common items |
| Difference | In first, not in second | पहले में, दूसरे में नहीं |
| Symmetric difference | In exactly one set | ठीक एक में |
| Subset / superset | Fully contained / contains all | पूरी तरह अंदर / सब शामिल |
| Disjoint | No common items | कोई common नहीं |

---

## ⚡ 3-Line Summary
English: Sets store unique hashable items with O(1) membership. Use `add/discard/remove` to change them and `| & - ^` (or methods) for union, intersection, difference. `{}` is a dict, so create empty sets with `set()`.
Hindi: Set unique hashable items रखता है, membership O(1)। बदलने के लिए `add/discard/remove`, और union/intersection/difference के लिए `| & - ^` (या methods)। `{}` dict है, खाली set के लिए `set()`।

---

## ➡️ Next Topic
**067. Set Comprehension** — build sets in one line, filtering, uniqueness, and set vs list comprehension.
