---

# 122. List Comprehension vs map/filter
# हिंदी में: List Comprehension बनाम map/filter

---

## 🔵 Simple Definition (English)
A list comprehension `[f(x) for x in data if cond]` builds a new list in one readable line. `map(f, data)` applies a function to every item and `filter(cond, data)` keeps items that pass a test; both return lazy iterators. They solve the same problem in different styles.

## 🔵 सरल परिभाषा (Hindi)
List comprehension `[f(x) for x in data if cond]` एक पढ़ने लायक line में नई list बनाती है। `map(f, data)` हर item पर function लगाता है और `filter(cond, data)` test पास करने वाले items रखता है; दोनों lazy iterators लौटाते हैं। दोनों एक ही समस्या अलग style में हल करते हैं।

---

## 🔴 Problem it Solves
Without them you write a 4-line loop: create an empty list, loop, check a condition, append. Functional tools shrink this to one expression. The question is which one to choose: comprehensions are usually clearer and faster with lambdas, while `map`/`filter` shine when you already have a named function (like `str.strip` or `int`) and want laziness.

## 🔴 यह क्यों बना? (Hindi)
इनके बिना 4 line का loop लिखना पड़ता है: खाली list बनाओ, loop चलाओ, condition जाँचो, append करो। Functional tools इसे एक expression में बदल देते हैं। सवाल यह है कि कौन सा चुनें: lambda के साथ comprehension आमतौर पर साफ और तेज़ है, जबकि पहले से named function (जैसे `str.strip` या `int`) हो और laziness चाहिए तो `map`/`filter` अच्छे हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → [expr for x in it if cond]: loop over it, skip items failing cond
Step 2 → Python evaluates expr for each kept item and builds the list at once
Step 3 → map(f, it): returns a lazy iterator; f runs only when you consume it
Step 4 → filter(p, it): lazy iterator that yields items where p(item) is truthy
Step 5 → filter(None, it) drops all falsy items (0, "", None, [])
Step 6 → Comprehension has its own scope: loop variable does not leak (Python 3)

[x*x for x in range(5) if x % 2 == 0]  ->  [0, 4, 16]
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → [expr for x in it if cond]: it पर loop, cond फेल वाले items skip
Step 2 → Python हर रखे गए item पर expr निकालता है और list एक साथ बनाता है
Step 3 → map(f, it): lazy iterator लौटाता है; f तभी चलता है जब आप consume करें
Step 4 → filter(p, it): lazy iterator जो वही items देता है जिनके लिए p(item) truthy है
Step 5 → filter(None, it) सारे falsy items (0, "", None, []) हटा देता है
Step 6 → Comprehension का अपना scope है: loop variable बाहर leak नहीं होता (Python 3)
```

---

## 🟡 Real World Example
A Razorpay reconciliation job takes a list of payment dicts, keeps only `status == "captured"` and extracts the amounts: a comprehension. A log pipeline maps `str.strip` and `json.loads` over lines of a huge file lazily so memory stays flat. A cleaner for form input uses `filter(None, ...)` to drop empty fields.

## 🟡 Real Example Hindi mein
Razorpay reconciliation job payment dicts की list से सिर्फ `status == "captured"` रखकर amounts निकालता है: comprehension। Log pipeline बड़ी file की lines पर `str.strip` और `json.loads` lazily `map` करता है ताकि memory स्थिर रहे। Form cleaner खाली fields हटाने के लिए `filter(None, ...)` use करता है।

---

## 💻 Code Example — Basic
```python
# Basic: the same task three ways
nums: list[int] = [1, 2, 3, 4, 5, 6]               # sample data

squares_loop: list[int] = []                       # classic loop
for n in nums:                                     # visit each number
    if n % 2 == 0:                                 # keep evens only
        squares_loop.append(n * n)                 # add the square

squares_lc: list[int] = [n * n for n in nums if n % 2 == 0]    # comprehension
squares_mf: list[int] = list(map(lambda n: n * n, filter(lambda n: n % 2 == 0, nums)))   # map+filter
print(squares_loop == squares_lc == squares_mf)    # all three agree
print(squares_lc)                                  # the result

m = map(str, nums)                                 # map is lazy: nothing computed yet
print(m)                                           # a map object, not a list
print(list(m))                                     # consuming it computes values
print(list(m))                                     # exhausted: empty now

print(list(filter(None, [0, 1, "", "a", None, [], [2]])))      # drops falsy values
print(list(map(int, ["1", "2", "3"])))             # map with a named function: neat
print([c.upper() for c in "abc"])                  # comprehension over a string
print({k: v for k, v in zip("ab", [1, 2])})        # dict comprehension
print({x % 3 for x in range(10)})                  # set comprehension

# Output:
# True
# [4, 16, 36]
# <map object at 0x...>   (address varies)
# ['1', '2', '3', '4', '5', '6']
# []
# [1, 'a', [2]]
# [1, 2, 3]
# ['A', 'B', 'C']
# {'a': 1, 'b': 2}
# {0, 1, 2}
```

## 💻 Code Example — Advanced
```python
# Production style: clean pipeline, nested comprehension, speed check
import timeit                                      # tiny benchmark tool
from typing import Iterable, Iterator              # type hints for iterables

Payment = dict[str, str | int]                     # alias for readability


def captured_amounts(payments: Iterable[Payment]) -> list[int]:
    """Return rupee amounts of captured payments (comprehension: clear and fast)."""
    return [int(p["amount"]) for p in payments if p.get("status") == "captured"]


def clean_lines(lines: Iterable[str]) -> Iterator[str]:
    """Lazy pipeline: strip, then drop empty lines. Works on a huge file."""
    stripped = map(str.strip, lines)               # named function -> map is neat
    return filter(None, stripped)                  # drop empty strings lazily


def flatten(matrix: list[list[int]]) -> list[int]:
    """Nested comprehension: read left to right like nested for loops."""
    return [x for row in matrix for x in row]      # outer loop first, inner second


payments: list[Payment] = [
    {"id": "p1", "status": "captured", "amount": 500},
    {"id": "p2", "status": "failed", "amount": 700},
    {"id": "p3", "status": "captured", "amount": "250"},    # amount as string!
]
print(captured_amounts(payments))                  # only captured ones
print(list(clean_lines(["  a ", "", "  ", "b\n"])))    # blank lines vanish
print(flatten([[1, 2], [3], [4, 5]]))              # one flat list

big: range = range(1000)                           # data for the benchmark
t_lc = timeit.timeit(lambda: [x * 2 for x in big], number=2000)         # comprehension
t_map = timeit.timeit(lambda: list(map(lambda x: x * 2, big)), number=2000)   # map + lambda
t_map_fn = timeit.timeit(lambda: list(map(abs, big)), number=2000)     # map + builtin
t_lc_fn = timeit.timeit(lambda: [abs(x) for x in big], number=2000)   # comprehension + builtin
print("lambda: comprehension faster:", t_lc < t_map)    # typically True
print("builtin: map at least as fast:", t_map_fn <= t_lc_fn * 1.2)    # usually True (CPython)

# Output:
# [500, 250]
# ['a', 'b']
# [1, 2, 3, 4, 5]
# lambda: comprehension faster: True
# builtin: map at least as fast: True
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Transform | `[f(x) for x in a]` / `map(f, a)` | `a.map(f)` |
| Filter | `[x for x in a if c(x)]` / `filter(c, a)` | `a.filter(c)` |
| Laziness | `map`/`filter` lazy | arrays eager (each step makes a new array) |
| Chaining | nest or pipeline | `a.filter(...).map(...)` fluent |
| Style preferred | comprehension | method chaining |

```python
# Python way
nums = [1, 2, 3, 4]                                # numbers
print([n * n for n in nums if n % 2 == 0])         # [4, 16]
```
```javascript
// JavaScript way
const nums = [1, 2, 3, 4];                         // numbers
console.log(nums.filter(n => n % 2 === 0).map(n => n * n));   // [4, 16]
```

Key difference: JS puts `map`/`filter` on the array and chains them; the order reads "filter then map". Python's comprehension reads "map expression first, then loop, then filter", and Python's `map`/`filter` are functions on iterators, not methods.

---

## 🟠 FastAPI Connection
Response shaping is everywhere in FastAPI: convert DB rows into response models, drop inactive items, extract IDs. A comprehension in the route handler (or a service function) is the idiomatic way. For very large exports, return a generator so `StreamingResponse` does not hold everything in memory.

```python
# FastAPI example — shape DB rows into response items
from fastapi import FastAPI                        # app
from pydantic import BaseModel                     # response schema

app: FastAPI = FastAPI()                           # create app


class UserOut(BaseModel):
    id: int                                        # user id
    name: str                                      # display name


DB: list[dict[str, int | str | bool]] = [          # pretend table
    {"id": 1, "name": "asha", "active": True},
    {"id": 2, "name": "ravi", "active": False},
]


@app.get("/users", response_model=list[UserOut])   # list of UserOut
def active_users() -> list[UserOut]:
    return [UserOut(id=int(r["id"]), name=str(r["name"])) for r in DB if r["active"]]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Printing or reusing a `map` object as if it were a list
✅ Correct: wrap in `list()` and consume once

```python
m = map(int, ["1", "2"])
# Wrong
print(m)               # <map object at 0x...>
print(len(m) if hasattr(m, "__len__") else "no len")   # no len
# Right
vals = list(m)
print(vals, len(vals)) # [1, 2] 2
```

❌ Mistake 2: Writing a comprehension only for side effects
✅ Correct: use a plain `for` loop

```python
# Wrong — builds a useless list of None
[print(x) for x in range(3)]
# Right
for x in range(3):
    print(x)
```

❌ Mistake 3: Cramming too much into one comprehension
✅ Correct: split into a helper function or loop when it passes two levels

```python
# Wrong — hard to read
r = [y for x in [[1, 2], [3]] if len(x) > 1 for y in x if y % 2]
# Right
rows = [x for x in [[1, 2], [3]] if len(x) > 1]
r = [y for row in rows for y in row if y % 2]
print(r)               # [1]
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])
m = map(lambda x: x + 1, [1, 2, 3])
print(2 in m, list(m))
print([i for i in range(3)], end=" ")
```
Answer: `[2, 2, 2]`: each lambda looks up `i` when it is CALLED, and by then the comprehension finished with `i = 2` (late binding; fix with `lambda i=i: i`). Second line: `True [3, 4]`. The `in` test consumes the map up to 2 (the value `2` is produced by the first item 1+1), so the remaining items are `[3, 4]`. The last line prints `[0, 1, 2] ` (no newline). Note that `i` is NOT visible after the comprehension in Python 3.

---

## ⚫ Interview Questions + Answers

Q1: Which is faster, comprehension or `map`?
A1: With a lambda, the comprehension is usually faster because it avoids a function call per item. With a built-in or C function (`map(int, xs)`, `map(str.strip, xs)`), `map` is often equal or slightly faster. Pick for readability first; measure with `timeit` if it matters.

Q2: Why does Guido prefer comprehensions?
A2: They are more readable, handle filter and transform in one place, and don't need `lambda`. He once proposed removing `map`/`filter`/`reduce`; comprehensions replaced most use cases.

Q3: What is the memory difference?
A3: A list comprehension builds the full list immediately (O(n) memory). `map`/`filter` and generator expressions are lazy and use O(1) memory until consumed.

Q4: Does a comprehension variable leak in Python 3?
A4: No. It has its own scope. In Python 2, list comprehension variables leaked into the enclosing scope. In 3.12+ (PEP 709) comprehensions are inlined for speed but the variable is still isolated.

Q5: What does `filter(None, data)` do?
A5: It removes every item whose truth value is False: `0`, `0.0`, `""`, `None`, `[]`, `{}`. Be careful: it also removes legitimate zeros.

---

## 🔷 When to Use + When Not to Use
✅ Use comprehension when:
- You transform and/or filter with an inline expression
- You need a list, dict or set result
- Readability matters (almost always)

✅ Use `map`/`filter` when:
- You already have a named function (`int`, `str.strip`, `len`)
- You want lazy processing of large streams
- You pass the iterator straight to `sum`, `max`, `join`

❌ Avoid when:
- Logic needs several statements or `try/except` (write a loop or function)
- Only side effects are needed (use `for`)

---

## 📊 Visual Diagram
```
data: [1, 2, 3, 4]

filter(even)  ->  2, 4         (lazy)
map(square)   ->  4, 16        (lazy)
list(...)     ->  [4, 16]      (consume, computed now)

[n*n for n in data if n % 2 == 0]   -> same result, one pass, list built eagerly
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Comprehension | Build a collection from a loop expression | Loop expression से collection बनाना |
| map | Apply function to every item | हर item पर function लगाना |
| filter | Keep items passing a test | Test पास करने वाले items रखना |
| Lazy | Computed only when needed | जरूरत पड़ने पर ही compute |
| Late binding | Variable looked up at call time | Variable call के समय खोजा जाता है |
| Falsy | Value treated as False | जो False माना जाए |

---

## ⚡ 3-Line Summary
English: Comprehensions are the clear, usually faster way to transform and filter; they build the full collection. `map` and `filter` are lazy and shine with named functions. Choose by readability and by whether you need laziness.
Hindi: Comprehension transform और filter का साफ और आमतौर पर तेज़ तरीका है; यह पूरा collection बना देती है। `map` और `filter` lazy हैं और named functions के साथ अच्छे हैं। Readability और laziness की जरूरत देखकर चुनें।

---

## ➡️ Next Topic
**123. Generator Expressions** — comprehension syntax with parentheses that never builds the list.
