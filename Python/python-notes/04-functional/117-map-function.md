---

# 117. map() Function
# हिंदी में: map() Function (हर item पर function लगाना)

---

## 🔵 Simple Definition (English)
`map(func, iterable, ...)` applies a function to every item of one or more iterables and returns a lazy iterator of the results. Nothing is computed until you loop over it or convert it with `list()`. It is Python's built-in way to "transform every element".

## 🔵 सरल परिभाषा (Hindi)
`map(func, iterable, ...)` एक या ज्यादा iterables के हर item पर function लगाता है और results का lazy iterator लौटाता है। जब तक आप उस पर loop नहीं करते या `list()` नहीं बनाते, कुछ compute नहीं होता। "हर element को बदलने" का यह Python का built-in तरीका है।

---

## 🔴 Problem it Solves
Transforming every item of a list needs a loop: create an empty list, loop, call the function, append. That is four lines for one idea. `map` states the idea in one expression, and because it is lazy it can process huge or infinite streams (such as lines of a 10 GB file) one item at a time, using almost no memory. It also works with any callable: built-ins like `int` and `str.strip`, lambdas, and your own functions.

## 🔴 यह क्यों बना? (Hindi)
List के हर item को बदलने के लिए loop चाहिए: खाली list बनाओ, loop चलाओ, function call करो, append करो। एक idea के लिए चार lines। `map` वही idea एक expression में कहता है, और lazy होने से यह बहुत बड़े या infinite streams (जैसे 10 GB file की lines) को एक-एक item करके लगभग बिना memory के process कर सकता है। यह हर callable के साथ चलता है: `int` और `str.strip` जैसे built-ins, lambdas और आपके अपने functions।

---

## 🟢 How it Works — Step by Step

```
Step 1 → map(f, data) creates a map OBJECT (an iterator). f is NOT called yet
Step 2 → When you ask for the next item (for loop, next(), list()),
         map takes one item from data and returns f(item)
Step 3 → With several iterables: map(f, a, b) calls f(a[i], b[i])
Step 4 → It stops when the SHORTEST iterable ends
Step 5 → The map object can be consumed only ONCE (then it is empty)
Step 6 → Python 3.14 adds map(..., strict=True) to raise if lengths differ;
         not available in 3.13

list(map(str.upper, ["a", "b"]))  ->  ["A", "B"]
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → map(f, data) एक map OBJECT (iterator) बनाता है। f अभी call नहीं होता
Step 2 → जब आप अगला item मांगते हो (for loop, next(), list()),
         map data से एक item लेता है और f(item) लौटाता है
Step 3 → कई iterables हों तो: map(f, a, b) f(a[i], b[i]) call करता है
Step 4 → सबसे छोटी iterable खत्म होते ही रुक जाता है
Step 5 → map object सिर्फ एक बार consume हो सकता है (फिर खाली)
Step 6 → Python 3.14 में map(..., strict=True) आया है जो लंबाई अलग होने पर error देता है;
         3.13 में उपलब्ध नहीं

list(map(str.upper, ["a", "b"]))  ->  ["A", "B"]
```

---

## 🟡 Real World Example
An e-commerce backend receives prices as strings from a CSV: `["499", "1299", "89.5"]` and converts them with `map(float, prices)`. An order service calculates GST for every item: `map(add_gst, items)`. A data pipeline cleans a 5 GB log file with `map(str.strip, open("app.log"))` without loading it in memory. An AI app converts every document into an embedding in a batch: `map(embed, documents)`.

## 🟡 Real Example Hindi mein
E-commerce backend को CSV से prices strings में मिलते हैं: `["499", "1299", "89.5"]` और वह उन्हें `map(float, prices)` से बदलता है। Order service हर item का GST `map(add_gst, items)` से निकालती है। Data pipeline 5 GB की log file को memory में लोड किए बिना `map(str.strip, open("app.log"))` से साफ करती है। AI app हर document का embedding batch में `map(embed, documents)` से बनाता है।

---

## 💻 Code Example — Basic
```python
# Basic map() examples
nums: list[int] = [1, 2, 3, 4]                    # sample data

squares = map(lambda x: x * x, nums)              # nothing is computed yet
print(squares)                                    # a map object, not a list
print(list(squares))                              # now the values are produced
print(list(squares))                              # empty! the iterator is already used up

prices: list[str] = ["499", "1299", "89.5"]       # strings from a CSV
print(list(map(float, prices)))                   # built-in as the function
print(list(map(str.upper, ["amit", "neha"])))     # method as the function
print(list(map(len, ["python", "go", "rust"])))   # len works too

a: list[int] = [1, 2, 3]                          # two iterables
b: list[int] = [10, 20, 30, 40]                   # longer than a
print(list(map(lambda x, y: x + y, a, b)))        # pairs up items; stops at shortest
print(list(map(pow, [2, 3, 4], [1, 2, 3])))       # pow(2,1), pow(3,2), pow(4,3)

it = map(int, ["1", "2", "3"])                    # lazy iterator
print(next(it), next(it))                         # take items one by one

print([x * x for x in nums])                      # list comprehension does the same job

# Output:
# <map object at 0x...>   (address varies)
# [1, 4, 9, 16]
# []
# [499.0, 1299.0, 89.5]
# ['AMIT', 'NEHA']
# [6, 2, 4]
# [11, 22, 33]
# [2, 9, 64]
# 1 2
# [1, 4, 9, 16]
```

## 💻 Code Example — Advanced
```python
# Production style: error-safe parsing, lazy pipelines, parallel map, functools.partial
import itertools                                  # islice, starmap
from concurrent.futures import ThreadPoolExecutor  # parallel map
from functools import partial                     # fix some arguments of a function
from typing import Callable, Iterable, Iterator, TypeVar

T = TypeVar("T")                                  # input item type
R = TypeVar("R")                                  # output item type


def safe_map(func: Callable[[T], R], items: Iterable[T], default: R) -> Iterator[R]:
    """Like map, but a failing item becomes `default` instead of crashing everything."""
    for item in items:                            # one item at a time (lazy)
        try:
            yield func(item)                      # normal case
        except (ValueError, TypeError):           # bad input
            yield default                         # replace with the default


raw: list[str] = ["10", "x", "30", "", "50"]      # messy input
print(list(safe_map(int, raw, default=-1)))       # [10, -1, 30, -1, 50]


def add_gst(price: float, rate: float) -> float:  # business function with 2 args
    return round(price * (1 + rate), 2)


gst18: Callable[[float], float] = partial(add_gst, rate=0.18)   # fix the rate
print(list(map(gst18, [100.0, 250.0, 999.0])))    # [118.0, 295.0, 1178.82]

# Lazy pipeline: nothing runs until the final list()
lines: Iterator[str] = iter(["  a,1 ", " b,2", "c,x ", "d,4  "])   # pretend file lines
stripped = map(str.strip, lines)                  # step 1: clean
parsed = map(lambda s: s.split(","), stripped)    # step 2: split
valid = filter(lambda p: p[1].isdigit(), parsed)  # step 3: keep valid rows
totals = map(lambda p: (p[0], int(p[1]) * 10), valid)   # step 4: convert
print(list(totals))                               # [('a', 10), ('b', 20), ('d', 40)]

# starmap: when each item is already a tuple of arguments
pairs: list[tuple[int, int]] = [(2, 3), (4, 5)]
print(list(itertools.starmap(pow, pairs)))        # [8, 1024]
# map(pow, pairs) would fail: pow gets ONE tuple argument

# Parallel map for I/O-bound work (e.g. HTTP calls)
def slow_square(n: int) -> int:                   # pretend to be a network call
    return n * n

with ThreadPoolExecutor(max_workers=4) as pool:   # 4 worker threads
    print(list(pool.map(slow_square, range(6))))  # order of results is preserved

# Process a huge stream lazily: only the first 3 items are ever computed
big = map(lambda n: n * 2, itertools.count(1))    # infinite stream
print(list(itertools.islice(big, 3)))             # [2, 4, 6]

# Output:
# [10, -1, 30, -1, 50]
# [118.0, 295.0, 1178.82]
# [('a', 10), ('b', 20), ('d', 40)]
# [8, 1024]
# [0, 1, 4, 9, 16, 25]
# [2, 4, 6]
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Transform items | `map(f, items)` | `items.map(f)` |
| Result | lazy iterator | new array (eager) |
| Style | function taking an iterable | method on arrays only |
| Callback args | `f(item)` only | `f(item, index, array)` |
| Multiple lists | `map(f, a, b)` | manual with index |
| Common alternative | list comprehension | for-of / `Array.from` |

```python
# Python way
nums: list[int] = [1, 2, 3]
doubled = list(map(lambda x: x * 2, nums))   # must wrap in list() to see values
print(doubled)                               # [2, 4, 6]
print([x * 2 for x in nums])                 # the more Pythonic form
```
```javascript
// JavaScript way
const nums = [1, 2, 3];
const doubled = nums.map(x => x * 2);        // already an array
console.log(doubled);                        // [ 2, 4, 6 ]
console.log(["1", "2", "3"].map(parseInt)); // [1, NaN, NaN] - famous JS trap (index passed as radix)
console.log(["1", "2", "3"].map(Number));  // [ 1, 2, 3 ]
```

Key difference: JS `map` is eager and returns an array; Python `map` is lazy and returns a one-use iterator. Python passes only the item, so the JS `parseInt` index trap does not exist: `list(map(int, ["1","2","3"]))` just works.

---

## 🟠 FastAPI Connection
Inside endpoints, list comprehensions are usually preferred, but `map` shines for converting query strings, e.g. `?ids=1,2,3` to ints, and for applying a conversion function (`ORM object -> response model`) to many rows. FastAPI's `run_in_threadpool` and `ThreadPoolExecutor.map` help when each item needs blocking work.

```python
# FastAPI example - parse comma separated ids and convert rows to response dicts
from fastapi import FastAPI, HTTPException        # app and errors
from fastapi.testclient import TestClient         # tests

app: FastAPI = FastAPI()                          # create app
PRODUCTS: dict[int, str] = {1: "Pen", 2: "Book", 3: "Bag"}   # fake database


def to_view(pid: int) -> dict[str, object]:       # row -> response dict
    return {"id": pid, "name": PRODUCTS[pid]}


@app.get("/products")                             # GET /products?ids=1,3
def products(ids: str) -> list[dict[str, object]]:
    try:
        parsed = list(map(int, ids.split(",")))   # "1,3" -> [1, 3]
    except ValueError:                            # e.g. "1,x"
        raise HTTPException(422, "ids must be integers")
    missing = [i for i in parsed if i not in PRODUCTS]   # validate
    if missing:
        raise HTTPException(404, f"not found: {missing}")
    return list(map(to_view, parsed))             # transform every id


client: TestClient = TestClient(app)              # client
print(client.get("/products", params={"ids": "1,3"}).json())
print(client.get("/products", params={"ids": "1,x"}).status_code)

# Output:
# [{'id': 1, 'name': 'Pen'}, {'id': 3, 'name': 'Bag'}]
# 422
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Printing or indexing a `map` object as if it were a list
✅ Correct: wrap with `list()` (or loop over it)

```python
m = map(str, [1, 2, 3])
# Wrong
try:
    print(m[0])
except TypeError as e:
    print(e)                 # 'map' object is not subscriptable
# Right
print(list(m)[0])            # 1
```

❌ Mistake 2: Consuming the iterator twice
✅ Correct: store the list if you need the data again

```python
m = map(lambda x: x + 1, [1, 2])
print(list(m))               # [2, 3]
# Wrong
print(list(m))               # []  (already consumed)
# Right
result = list(map(lambda x: x + 1, [1, 2]))
print(result, result)        # [2, 3] [2, 3]
```

❌ Mistake 3: Using `map` only for side effects (never runs because it is lazy)
✅ Correct: use a `for` loop for side effects

```python
log: list[str] = []
# Wrong - nothing happens, map is never consumed
map(log.append, ["a", "b"])
print(log)                   # []
# Right
for item in ["a", "b"]:
    log.append(item)
print(log)                   # ['a', 'b']
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
funcs = map(lambda i: (lambda: i), range(3))
print([f() for f in funcs])

m = map(lambda x: print("called", x) or x, [1, 2, 3])
print("created")
print(next(m))

print(list(map(int, "123")))
print(list(map(lambda x, y: (x, y), "ab", [1, 2, 3])))
```
Answer: `[0, 1, 2]`, then `created`, then `called 1` and `1`, then `[1, 2, 3]`, then `[('a', 1), ('b', 2)]`. In the first line each lambda gets its own `i` as an argument of the outer lambda, so there is no late-binding problem (unlike `[lambda: i for i in range(3)]`, which gives `[2, 2, 2]`). `map` is lazy: "called" is not printed when `m` is created, only when `next(m)` asks for the first item, and only that one item is processed. `map(int, "123")` iterates over the string characters. With unequal lengths, `map` stops at the shortest iterable (here 2 items).

---

## ⚫ Interview Questions + Answers

Q1: What does `map` return in Python 3?
A1: A lazy `map` object (an iterator). In Python 2 it returned a list. Items are computed one at a time when requested, and the object can be iterated only once.

Q2: `map` vs list comprehension: which is better?
A2: Comprehensions are usually more readable, especially with conditions or lambdas (`[x*2 for x in a if x > 0]`). `map` is concise when the function already exists (`map(int, data)`) and is lazy, whereas a list comprehension builds the full list; use a generator expression `(f(x) for x in a)` for lazy comprehension. Speed: `map` with a built-in function is slightly faster; with a lambda it is slower.

Q3: How does `map` behave with multiple iterables of different lengths?
A3: It stops at the shortest one and silently drops extra items. In Python 3.14+, `strict=True` raises `ValueError` on mismatch; on 3.13 use `zip(..., strict=True)` (3.10+) with `starmap`.

Q4: What is the difference between `map` and `starmap`?
A4: `map(f, iterable)` passes each item as ONE argument. `itertools.starmap(f, iterable)` unpacks each item as arguments: `starmap(pow, [(2,3)])` equals `pow(2, 3)`.

Q5: How would you run `map` in parallel?
A5: For I/O-bound work use `ThreadPoolExecutor().map(func, items)`. For CPU-bound work use `ProcessPoolExecutor().map` or `multiprocessing.Pool.map`. They keep result order, and the function must be picklable for processes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You already have a named function (`map(int, values)`, `map(str.strip, lines)`)
- You want lazy processing of big or infinite streams
- You combine items from several iterables
- You build lazy pipelines with `filter`, `islice`

❌ Avoid when:
- You need a condition as well (use a comprehension)
- The function is a complicated lambda (readability suffers)
- You only want side effects (use `for`)
- You need the data more than once or random access (build a list)

---

## 📊 Visual Diagram
```
data:  [ 1 ,  2 ,  3 ,  4 ]
         |     |     |     |        map(f, data)  -> lazy iterator
         v     v     v     v        (nothing runs yet)
       f(1)  f(2)  f(3)  f(4)
         |     |     |     |        list(...) / for / next()
         v     v     v     v        pulls ONE value at a time
result: [f1 ,  f2 ,  f3 ,  f4 ]

map(f, a, b):  a=[1,2,3]  b=[10,20,30,40]
               f(1,10)  f(2,20)  f(3,30)   <- stops at shortest (40 ignored)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `map` | Apply a function to each item | हर item पर function लगाना |
| Lazy evaluation | Compute only when needed | जरूरत पड़ने पर ही compute |
| Iterator | Object giving items one by one | एक-एक item देने वाला object |
| `starmap` | `map` that unpacks argument tuples | tuple को arguments में खोलने वाला map |
| Higher-order function | Function taking/returning functions | function लेने/लौटाने वाला function |
| `partial` | Pre-fill some arguments | कुछ arguments पहले से भरना |

---

## ⚡ 3-Line Summary
English: `map(func, iterable)` lazily applies a function to every item and returns a one-use iterator. Wrap it in `list()` to see the results, and note that it stops at the shortest iterable. Prefer comprehensions for conditions or complex logic, `map` for existing functions and big streams.
Hindi: `map(func, iterable)` हर item पर function lazily लगाता है और एक बार use होने वाला iterator लौटाता है। नतीजे देखने के लिए `list()` लगाएं, और याद रखें कि यह सबसे छोटी iterable पर रुकता है। Conditions या जटिल logic के लिए comprehension, मौजूदा functions और बड़े streams के लिए `map` चुनें।

---

## ➡️ Next Topic
**118. filter() Function** - keep only the items that pass a test, also lazily.
