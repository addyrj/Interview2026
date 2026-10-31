---

# 060. Dictionary Comprehension
# हिंदी में: Dictionary Comprehension

---

## 🔵 Simple Definition (English)
A dictionary comprehension builds a new dict in one expression: `{key: value for item in iterable if condition}`. It replaces the "create empty dict, loop, assign" pattern with a single readable line.

## 🔵 सरल परिभाषा (Hindi)
Dictionary comprehension एक ही expression में नया dict बनाता है: `{key: value for item in iterable if condition}`। यह "खाली dict बनाओ, loop चलाओ, assign करो" वाले pattern को एक line में बदल देता है।

---

## 🔴 Problem it Solves
Transforming or filtering a dict with loops takes 4-5 lines and is easy to get wrong (forgetting to create the dict, wrong indentation). Typical needs: invert a dict, filter by value, convert types, build a lookup table from a list. Comprehension does each in one clear line, and it is also a little faster than the equivalent loop with repeated `d[k] = v`.

## 🔴 यह क्यों बना? (Hindi)
Loop से dict transform/filter करने में 4-5 lines लगती हैं और गलती आसान है। Invert, value से filter, type convert, list से lookup table — सब एक line में हो जाता है, और loop से थोड़ा तेज़ भी है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python creates a new empty dict
Step 2 → Takes the next item from the iterable (for part)
Step 3 → Checks the optional `if` filter; skips the item if False
Step 4 → Evaluates the key expression and the value expression
Step 5 → Stores key: value in the new dict (a duplicate key overwrites the earlier one)
Step 6 → Repeats until the iterable ends, then returns the dict
```

## 🟢 कैसे काम करता है? (Hindi)
```
नया खाली dict → अगला item → `if` filter check → key और value निकालो → dict में store
Duplicate key आए तो पुरानी value overwrite हो जाती है
```

---

## 🟡 Real World Example
Zomato: you have a list of restaurants and need a fast lookup by id: `{r.id: r for r in restaurants}`. Or apply a 10% discount only to items above 500: `{name: price * 0.9 for name, price in menu.items() if price > 500}`. In FastAPI, you turn a list of DB rows into an `id -> object` map to avoid repeated searches (O(1) instead of O(n)).

## 🟡 Real Example Hindi mein
Zomato में restaurants की list से id-based lookup चाहिए: `{r.id: r for r in restaurants}`। या 500 से ऊपर के items पर 10% discount: `{name: price * 0.9 for name, price in menu.items() if price > 500}`। FastAPI में DB rows की list को `id -> object` map बनाते हैं ताकि search O(1) हो।

---

## 💻 Code Example — Basic
```python
# Basic: dict comprehension patterns
names: list[str] = ["apple", "kiwi", "banana"]          # sample input list

lengths: dict[str, int] = {n: len(n) for n in names}    # word -> its length
print(lengths)                                           # Output: {'apple': 5, 'kiwi': 4, 'banana': 6}

squares: dict[int, int] = {x: x * x for x in range(1, 6)}   # number -> square
print(squares)                                           # Output: {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

menu: dict[str, int] = {"pizza": 300, "burger": 150, "pasta": 450}   # name -> price
cheap: dict[str, int] = {k: v for k, v in menu.items() if v < 400}  # filter by value
print(cheap)                                             # Output: {'pizza': 300, 'burger': 150}

discounted: dict[str, float] = {k: v * 0.9 for k, v in menu.items()}  # transform values
print(discounted["pizza"])                               # Output: 270.0

inverted: dict[int, str] = {v: k for k, v in menu.items()}   # swap keys and values
print(inverted)                                          # Output: {300: 'pizza', 150: 'burger', 450: 'pasta'}

keys: list[str] = ["a", "b", "c"]                        # keys list
vals: list[int] = [1, 2, 3]                              # values list
combined: dict[str, int] = {k: v for k, v in zip(keys, vals)}   # join two lists
print(combined)                                          # Output: {'a': 1, 'b': 2, 'c': 3}

labels: dict[str, str] = {n: ("long" if len(n) > 4 else "short") for n in names}   # conditional value
print(labels)                                            # Output: {'apple': 'long', 'kiwi': 'short', 'banana': 'long'}
```

## 💻 Code Example — Advanced
```python
# Advanced: realistic data cleaning, indexing and nested comprehension
from __future__ import annotations           # modern hints
from dataclasses import dataclass            # simple record class


@dataclass(frozen=True)                      # immutable record
class Product:
    id: int                                  # unique id
    name: str                                # display name
    price: float                             # price in INR
    in_stock: bool                           # availability flag


products: list[Product] = [
    Product(1, "Keyboard", 1500.0, True),
    Product(2, "Mouse", 700.0, False),
    Product(3, "Monitor", 9000.0, True),
]

# 1. Build id -> Product index for O(1) lookup (instead of searching the list)
by_id: dict[int, Product] = {p.id: p for p in products}
print(by_id[3].name)                         # Output: Monitor

# 2. Only in-stock products as name -> price
available: dict[str, float] = {p.name: p.price for p in products if p.in_stock}
print(available)                             # Output: {'Keyboard': 1500.0, 'Monitor': 9000.0}

# 3. Clean raw query params: strip keys, drop empty values, convert numbers
raw: dict[str, str] = {" page ": "2", "size": "10", "q": "", "sort": "price"}
clean: dict[str, str | int] = {
    k.strip(): (int(v) if v.isdigit() else v)   # convert digit strings to int
    for k, v in raw.items()
    if v                                        # skip empty values
}
print(clean)                                 # Output: {'page': 2, 'size': 10, 'sort': 'price'}

# 4. Nested comprehension: matrix -> row index map
matrix: list[list[int]] = [[1, 2], [3, 4]]
row_sums: dict[int, int] = {i: sum(row) for i, row in enumerate(matrix)}
print(row_sums)                              # Output: {0: 3, 1: 7}

# 5. Dict of dicts: group each product into a summary
summary: dict[str, dict[str, object]] = {
    p.name: {"price": p.price, "tax": round(p.price * 0.18, 2)}
    for p in products
}
print(summary["Mouse"])                      # Output: {'price': 700.0, 'tax': 126.0}

# 6. Duplicate keys: last one wins (data loss if you are not careful)
dup: dict[str, int] = {w: i for i, w in enumerate(["a", "b", "a"])}
print(dup)                                   # Output: {'a': 2, 'b': 1}

# 7. Error handling: convert safely using a helper (comprehension has no try/except)
def to_int(value: str) -> int | None:
    """Return int or None if invalid."""
    try:                                     # attempt conversion
        return int(value)                    # success
    except ValueError:                       # bad text
        return None                          # signal failure

parsed: dict[str, int | None] = {k: to_int(v) for k, v in {"a": "1", "b": "x"}.items()}
print(parsed)                                # Output: {'a': 1, 'b': None}
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
prices = {"pizza": 300, "pasta": 450}
doubled = {k: v * 2 for k, v in prices.items() if v > 300}   # filter + transform
inverted = {v: k for k, v in prices.items()}                  # swap
```

```javascript
// JavaScript
const prices = { pizza: 300, pasta: 450 };
const doubled = Object.fromEntries(
  Object.entries(prices)
    .filter(([k, v]) => v > 300)         // filter step
    .map(([k, v]) => [k, v * 2])         // transform step
);
const inverted = Object.fromEntries(
  Object.entries(prices).map(([k, v]) => [v, k])
);
```

Key difference: JS needs `Object.entries -> filter -> map -> Object.fromEntries` (4 steps); Python does it in one expression. FastAPI link: use it to index DB rows by id and to clean or reshape response dictionaries before returning.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `[ ]` or forgetting `key: value`
```python
# Wrong:
# {k for k, v in d.items()}       # this is a SET comprehension (no colon)
# Correct:
# {k: v for k, v in d.items()}    # colon makes it a dict
```

❌ Mistake 2: Forgetting `.items()`
```python
# Wrong:
# {k: v for k, v in d}            # iterates keys only -> unpack error
# Correct:
# {k: v for k, v in d.items()}
```

❌ Mistake 3: Writing a huge unreadable comprehension
```python
# Wrong: 3 loops + 3 conditions in one line
# Correct: when it needs more than 2 loops/conditions, use a normal for loop or a helper function
```

---

## 🧠 Tricky Interview Question

**Q**: "What does `{x: y for x in range(2) for y in range(2)}` return?"

**Answer**: `{0: 1, 1: 1}`. The loops run as nested: for x=0 the pairs (0,0) then (0,1) are stored, the second overwrites the first so `0: 1`; same for x=1 → `1: 1`. Because dict keys are unique, a later pair with the same key replaces the earlier one, so only 2 entries remain, not 4. Always check that your key is unique.

---

## ⚫ Interview Questions + Answers

Q1: What is the syntax of a dict comprehension?
A1: `{key_expr: value_expr for item in iterable if condition}`. The `if` is optional. You can also use several `for` clauses (nested loops). It returns a new dict; the original data is not modified.

Q2: How do you invert a dictionary, and what is the risk?
A2: `{v: k for k, v in d.items()}`. The risk: values may repeat or be unhashable. If two keys share a value, only the last one survives. Lists as values raise `TypeError: unhashable type`. For repeated values group them: `defaultdict(list)` and append keys.

Q3: Dict comprehension vs `dict()` + loop: which is better?
A3: Comprehension is shorter, usually faster (it avoids repeated method lookups) and shows intent. A normal loop is better when you need `try/except`, many branches, logging or side effects. Never use a comprehension just for side effects.

Q4: How do you build a dict from two lists?
A4: `dict(zip(keys, values))` is the simplest; `{k: v for k, v in zip(keys, values)}` is the comprehension form, useful when you also want to filter or transform. `zip` stops at the shorter list.

Q5: Is there a scope difference with comprehensions?
A5: Yes. A comprehension has its own scope (since Python 3), so the loop variables `k, v` do not leak into the surrounding code. The outermost iterable is evaluated in the enclosing scope. This avoids the old bug where loop variables overwrote outer names.

---

## 🔷 When to Use Dict Comprehension

✅ Use when:
- Building lookup tables (`id -> object`)
- Filtering or transforming a dict
- Inverting a dict with unique values
- Cleaning request params or config

❌ Avoid when:
- Logic needs `try/except` or multiple statements
- The line gets longer than about 80-100 characters
- Keys may repeat and you cannot lose data

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Comprehension | Compact way to build a collection | Collection बनाने का compact तरीका |
| Filter clause | `if` part that skips items | Items skip करने वाला `if` |
| Lookup table | Dict for fast search by key | Key से तेज़ search वाला dict |
| Inversion | Swap keys and values | Keys और values की अदला-बदली |
| `zip` | Pair items from iterables | Iterables के items को जोड़ी में बाँधना |
| Hashable key | Key that can be hashed | जिसका hash बन सके |

---

## ⚡ 3-Line Summary
English: `{k: v for ... if ...}` builds a dict in one expression, ideal for lookup tables, filtering and cleaning. Remember `.items()`, unique keys (last wins) and keep it readable. Use a loop when you need error handling.
Hindi: `{k: v for ... if ...}` एक expression में dict बनाता है — lookup table, filter और cleaning के लिए बढ़िया। `.items()` न भूलें, duplicate key में आख़िरी जीतती है, और readable रखें। Error handling चाहिए तो loop।

---

## ➡️ Next Topic
**061. defaultdict** — dictionary with automatic default values, grouping and counting without `KeyError`.
