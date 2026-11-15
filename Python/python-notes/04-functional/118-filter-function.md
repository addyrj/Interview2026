---

# 118. filter() Function
# हिंदी में: filter() Function (शर्त पूरी करने वाले items चुनना)

---

## 🔵 Simple Definition (English)
`filter(func, iterable)` keeps only the items for which `func(item)` is truthy and returns them as a lazy iterator. If `func` is `None`, it keeps the items that are themselves truthy (removes `0`, `""`, `None`, `[]`, `False`).

## 🔵 सरल परिभाषा (Hindi)
`filter(func, iterable)` सिर्फ वे items रखता है जिनके लिए `func(item)` truthy हो, और उन्हें lazy iterator में लौटाता है। अगर `func` `None` हो, तो वे items रखता है जो खुद truthy हों (`0`, `""`, `None`, `[]`, `False` हट जाते हैं)।

---

## 🔴 Problem it Solves
Selecting items by a rule normally needs a loop with an `if` and an `append`. With `filter`, the selection rule is a separate, reusable, testable function, and the result is lazy, so a 10 GB log file can be filtered line by line without loading it. Cleaning data (removing empty strings and `None` values) is the most common use: `filter(None, values)`.

## 🔴 यह क्यों बना? (Hindi)
किसी rule से items चुनने के लिए आमतौर पर loop, `if` और `append` चाहिए। `filter` में चुनने का rule अलग, reusable और test करने योग्य function होता है, और result lazy होता है, इसलिए 10 GB की log file को बिना load किए line-by-line filter कर सकते हैं। Data साफ करना (खाली strings और `None` हटाना) सबसे आम use है: `filter(None, values)`।

---

## 🟢 How it Works — Step by Step

```
Step 1 → filter(pred, data) returns a filter OBJECT (iterator). pred is not called yet
Step 2 → On each request, it takes the next item x from data
Step 3 → It calls pred(x)
Step 4 → If the result is truthy -> yield x. If falsy -> skip and take the next
Step 5 → filter(None, data) skips the predicate and tests x itself
Step 6 → Like map, it can be consumed only once

Related: itertools.filterfalse(pred, data) keeps the items where pred is FALSY
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → filter(pred, data) एक filter OBJECT (iterator) लौटाता है। pred अभी call नहीं होता
Step 2 → हर request पर यह data से अगला item x लेता है
Step 3 → यह pred(x) call करता है
Step 4 → नतीजा truthy हो तो x दे देता है। falsy हो तो छोड़कर अगला लेता है
Step 5 → filter(None, data) predicate छोड़कर x को खुद test करता है
Step 6 → map की तरह, यह भी सिर्फ एक बार consume हो सकता है

संबंधित: itertools.filterfalse(pred, data) वे items रखता है जहां pred FALSY हो
```

---

## 🟡 Real World Example
A Zomato-like app filters restaurants: only those open now, with rating >= 4. A payments service keeps only transactions with status `"FAILED"` for a retry job. An API cleans user input by removing empty tags: `filter(None, tags)`. A log monitor scans a huge log lazily and keeps only the `ERROR` lines: `filter(lambda l: "ERROR" in l, file)`.

## 🟡 Real Example Hindi mein
Zomato जैसा app restaurants filter करता है: सिर्फ अभी खुले हुए, rating >= 4 वाले। Payments service retry job के लिए सिर्फ `"FAILED"` status वाले transactions रखती है। API user input से खाली tags `filter(None, tags)` से हटाती है। Log monitor बड़ी log file lazily scan करके सिर्फ `ERROR` lines रखता है: `filter(lambda l: "ERROR" in l, file)`।

---

## 💻 Code Example — Basic
```python
# Basic filter() examples
nums: list[int] = [1, 2, 3, 4, 5, 6]              # sample numbers

evens = filter(lambda x: x % 2 == 0, nums)        # lazy, nothing tested yet
print(list(evens))                                # [2, 4, 6]
print(list(evens))                                # [] -> iterator is used up

def is_adult(age: int) -> bool:                   # a named predicate is easy to test
    return age >= 18

print(list(filter(is_adult, [12, 18, 25, 7])))    # [18, 25]

mixed: list = [0, 1, "", "hi", None, [], [0], False, True]   # many falsy values
print(list(filter(None, mixed)))                  # None as func keeps only truthy items

words: list[str] = ["apple", "", "  ", "kiwi"]    # strings, some empty
print(list(filter(str.strip, words)))             # str.strip returns "" for blank strings

import itertools                                  # for filterfalse
print(list(itertools.filterfalse(lambda x: x % 2 == 0, nums)))   # keeps the ODD ones

print([x for x in nums if x % 2 == 0])            # the comprehension equivalent

# Output:
# [2, 4, 6]
# []
# [18, 25]
# [1, 'hi', [0], True]
# ['apple', 'kiwi']
# [1, 3, 5]
# [2, 4, 6]
```

## 💻 Code Example — Advanced
```python
# Production style: composable predicates, lazy log scanning, filter + map pipeline
from dataclasses import dataclass                 # simple record
from functools import partial                     # pre-fill predicate arguments
from typing import Callable, Iterable, Iterator   # type hints

Predicate = Callable[["Order"], bool]             # a predicate takes an Order, returns bool


@dataclass(frozen=True)
class Order:
    id: int                                       # order id
    status: str                                   # NEW / PAID / FAILED
    amount: float                                 # order value
    city: str                                     # delivery city


ORDERS: list[Order] = [
    Order(1, "PAID", 500.0, "Pune"),
    Order(2, "FAILED", 1200.0, "Delhi"),
    Order(3, "PAID", 80.0, "Pune"),
    Order(4, "FAILED", 300.0, "Pune"),
    Order(5, "NEW", 999.0, "Delhi"),
]


def has_status(status: str, order: Order) -> bool:   # generic predicate
    return order.status == status


def min_amount(limit: float, order: Order) -> bool:  # another generic predicate
    return order.amount >= limit


def all_of(*preds: Predicate) -> Predicate:       # combine predicates with AND
    def combined(order: Order) -> bool:
        return all(p(order) for p in preds)       # every rule must pass
    return combined


def any_of(*preds: Predicate) -> Predicate:       # combine predicates with OR
    def combined(order: Order) -> bool:
        return any(p(order) for p in preds)       # one passing rule is enough
    return combined


failed: Predicate = partial(has_status, "FAILED")           # reusable building blocks
big: Predicate = partial(min_amount, 250.0)
in_pune: Predicate = lambda o: o.city == "Pune"

retry_candidates = filter(all_of(failed, big), ORDERS)       # FAILED and >= 250
print([o.id for o in retry_candidates])                      # [2, 4]

print([o.id for o in filter(any_of(failed, in_pune), ORDERS)])   # [1, 2, 3, 4]

# Lazy log scanning: only matching lines are ever kept
log_lines: Iterator[str] = iter([
    "INFO start", "ERROR db timeout", "INFO ok", "ERROR disk full", "WARN slow",
])
errors: Iterable[str] = filter(lambda l: l.startswith("ERROR"), log_lines)
print(next(iter(errors)))                         # stops after the first match: ERROR db timeout
print(list(errors))                               # the rest of the matches: ['ERROR disk full']

# filter + map pipeline: total value of PAID orders
paid_total = sum(map(lambda o: o.amount, filter(partial(has_status, "PAID"), ORDERS)))
print(paid_total)                                 # 580.0

# Removing duplicates while filtering (stateful predicate via closure, with a set)
def first_seen() -> Callable[[str], bool]:
    seen: set[str] = set()                        # remembers what we have returned
    def check(x: str) -> bool:
        if x in seen:                             # duplicate -> reject
            return False
        seen.add(x)                               # first time -> accept
        return True
    return check

print(list(filter(first_seen(), ["a", "b", "a", "c", "b"])))   # ['a', 'b', 'c']

# Output:
# [2, 4]
# [1, 2, 3, 4]
# ERROR db timeout
# ['ERROR disk full']
# 580.0
# ['a', 'b', 'c']
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Keep matching items | `filter(f, items)` | `items.filter(f)` |
| Result | lazy iterator | new array |
| No predicate | `filter(None, items)` | `items.filter(Boolean)` |
| Opposite | `itertools.filterfalse` | `items.filter(x => !f(x))` |
| Callback args | `f(item)` | `f(item, index, array)` |
| Falsy values | `0, "", None, [], {}, False` | `0, "", null, undefined, NaN, false` (`[]` and `{}` are truthy!) |

```python
# Python way
nums: list[int] = [0, 1, 2, 3]
print(list(filter(lambda x: x > 1, nums)))  # [2, 3]
print(list(filter(None, [0, 1, [], [1]])))  # [1, [1]]  - empty list is falsy
```
```javascript
// JavaScript way
const nums = [0, 1, 2, 3];
console.log(nums.filter(x => x > 1));       // [ 2, 3 ]
console.log([0, 1, [], [1]].filter(Boolean));  // [ 1, [], [ 1 ] ]  - [] is truthy in JS!
```

Key difference: truthiness rules differ. In Python empty containers are falsy, so `filter(None, ...)` removes them; in JavaScript `[]` and `{}` are truthy, so `filter(Boolean)` keeps them. Also, Python's `filter` is lazy, JS returns a new array immediately.

---

## 🟠 FastAPI Connection
Query-parameter filtering is the most common use: an endpoint receives `?city=Pune&min_amount=250` and applies only the filters that were provided. Build a list of predicates from the optional parameters, then apply them with `filter` (or push the filter into the SQL query for large data, which is the right choice in production).

```python
# FastAPI example - optional filters built from query parameters
from dataclasses import dataclass                 # simple record
from typing import Callable                       # type hints
from fastapi import FastAPI                       # app
from fastapi.testclient import TestClient         # tests


@dataclass
class Order:
    id: int
    city: str
    amount: float


DB: list[Order] = [Order(1, "Pune", 500), Order(2, "Delhi", 120), Order(3, "Pune", 90)]

app: FastAPI = FastAPI()                          # create app


@app.get("/orders")                               # GET /orders?city=Pune&min_amount=100
def list_orders(city: str | None = None, min_amount: float = 0) -> list[dict]:
    rules: list[Callable[[Order], bool]] = []     # collect only the filters that were given
    if city is not None:
        rules.append(lambda o: o.city == city)
    rules.append(lambda o: o.amount >= min_amount)
    selected = filter(lambda o: all(r(o) for r in rules), DB)   # apply all rules lazily
    return [vars(o) for o in selected]            # dataclass -> dict


client: TestClient = TestClient(app)              # client
print(client.get("/orders", params={"city": "Pune", "min_amount": 100}).json())
print(len(client.get("/orders").json()))

# Output:
# [{'id': 1, 'city': 'Pune', 'amount': 500}]
# 3
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `filter(None, ...)` when `0` or `False` are valid values
✅ Correct: filter explicitly with `is not None`

```python
scores = [0, 5, None, 8]
# Wrong - drops the valid score 0
print(list(filter(None, scores)))                      # [5, 8]
# Right
print(list(filter(lambda s: s is not None, scores)))   # [0, 5, 8]
```

❌ Mistake 2: Using `len()` or indexing on a filter object
✅ Correct: convert to a list first

```python
f = filter(lambda x: x > 1, [1, 2, 3])
# Wrong
try:
    len(f)
except TypeError as e:
    print(e)                  # object of type 'filter' has no len()
# Right
print(len(list(f)))           # 2
```

❌ Mistake 3: Believing `filter` returns a truthy/falsy value or the predicate result
✅ Correct: it returns the ORIGINAL items, not the values returned by the predicate

```python
# Wrong expectation: [True, True]
print(list(filter(lambda x: x > 1, [1, 2, 3])))   # [2, 3]
# If you need the booleans, use map
print(list(map(lambda x: x > 1, [1, 2, 3])))      # [False, True, True]
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
data = [0, 1, 2, 3]
f = filter(lambda x: x, data)
data.append(0)
data.append(4)
print(list(f))

g = filter(lambda x: x > 1, [1, 2, 3])
print(2 in g, 2 in g, list(g))

print(list(filter(lambda x: print(x) or x > 1, [1, 2])))
```
Answer: `[1, 2, 3, 4]`, then `True False []`, then `1`, `2`, `[2]`. `filter` is lazy and keeps a reference to the list, not a copy, so items appended before consumption are included (`0` is dropped, `4` is kept). `in` on an iterator consumes it: the first `2 in g` reads `1`, then `2` and returns True; the second `2 in g` reads `3`, reaches the end and returns False, so `list(g)` is empty. In the last line the predicate runs only when `list` consumes the filter, so `1` and `2` are printed first and then the result `[2]`.

---

## ⚫ Interview Questions + Answers

Q1: What does `filter` return and why is that useful?
A1: A lazy iterator of the original items for which the predicate is truthy. Lazy means constant memory and the ability to stop early (for example `next(filter(...), None)` to find the first match).

Q2: `filter` vs list comprehension?
A2: Comprehensions with `if` are generally more readable and let you transform at the same time (`[f(x) for x in a if cond(x)]`). Use `filter` with an existing named predicate or when you want laziness (or use a generator expression). Performance is similar; `filter` with a built-in function is slightly faster.

Q3: What does `filter(None, items)` do and when is it dangerous?
A3: It removes all falsy items: `0`, `0.0`, `""`, `None`, `[]`, `{}`, `False`. It is dangerous when `0` or an empty string is a valid value. Use an explicit predicate then.

Q4: How do you find the first matching item efficiently?
A4: `next(filter(pred, items), default)` or `next((x for x in items if pred(x)), default)`. It stops at the first match and does not scan the rest.

Q5: How can you split items into matching and non-matching groups?
A5: Use `filter` and `itertools.filterfalse` (iterates twice, so the source must be re-iterable), or loop once and append to two lists. For streaming data, use `itertools.tee` or a single loop.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have a ready predicate function
- You clean data with `filter(None, ...)` (when falsy values are never valid)
- You scan large streams lazily and stop early
- You compose filters with `map` in a pipeline

❌ Avoid when:
- You also need to transform items (use a comprehension)
- The rule is a long multi-line lambda
- Filtering a big dataset that sits in a database (filter in SQL instead)
- You need the result more than once without storing it

---

## 📊 Visual Diagram
```
data:   [ 1 ,  2 ,  3 ,  4 ,  5 ,  6 ]
pred:     F     T     F     T     F     T      (x % 2 == 0)
          |     |     |     |     |     |
          x    keep   x    keep   x    keep
                 \         \          \
result (lazy):    2         4          6      -> list(...) = [2, 4, 6]

filter(None, [0, 1, "", "a", None])  ->  1, "a"     (truthy items only)
filterfalse(pred, data)              ->  1, 3, 5    (items where pred is False)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Predicate | Function returning True/False | True/False लौटाने वाला function |
| Truthy / Falsy | Treated as True / False in a condition | condition में True / False माना जाना |
| `filterfalse` | Keeps items failing the predicate | predicate fail करने वाले items रखता है |
| Lazy iterator | Produces items only on demand | मांगने पर ही items देता है |
| Short-circuit | Stop work as soon as possible | जल्दी से जल्दी रुक जाना |
| Pipeline | Chain of map/filter steps | map/filter steps की श्रृंखला |

---

## ⚡ 3-Line Summary
English: `filter(pred, items)` lazily keeps the original items for which the predicate is truthy; `filter(None, items)` drops falsy values. It returns a one-use iterator, so wrap it in `list()` when you need the data. Use comprehensions when you also transform values.
Hindi: `filter(pred, items)` उन्हीं original items को lazily रखता है जिनके लिए predicate truthy हो; `filter(None, items)` falsy values हटा देता है। यह एक बार use होने वाला iterator लौटाता है, इसलिए data चाहिए तो `list()` लगाएं। Values बदलनी भी हों तो comprehension चुनें।

---

## ➡️ Next Topic
**119. reduce() Function** - fold a whole iterable into a single value (sum, product, merged dict) with `functools.reduce`.
