---

# 418. Lazy Evaluation
# हिंदी में: Lazy Evaluation (ज़रूरत पड़ने पर ही गणना)

---

## 🔵 Simple Definition (English)
Lazy evaluation means a value is computed only at the moment it is needed, not when it is defined. Generators, `map`, `filter`, `range`, `itertools`, and `functools.cached_property` are lazy. You save memory and avoid work that is never used.

## 🔵 सरल परिभाषा (Hindi)
Lazy evaluation का मतलब है कि कोई value तभी calculate होती है जब उसकी ज़रूरत पड़ती है, define करते समय नहीं। Generators, `map`, `filter`, `range`, `itertools` और `functools.cached_property` lazy हैं। इससे memory बचती है और बेकार का काम नहीं होता।

---

## 🔴 Problem it Solves
Eager code builds everything up front: reading a 10 GB log into a list crashes the program, computing an expensive attribute that nobody reads wastes CPU, and importing a heavy library at startup slows every launch. Lazy evaluation does the work on demand, one item at a time, and sometimes never.

## 🔴 यह क्यों बना? (Hindi)
Eager code सब कुछ पहले ही बना लेता है: 10 GB की log को list में पढ़ने पर program crash हो जाता है, जिस attribute को कोई पढ़ता नहीं उसे calculate करना CPU बर्बाद करता है, और भारी library को startup पर import करने से हर launch धीमा होता है। Lazy evaluation काम माँग पर, एक-एक item करके, और कभी-कभी बिल्कुल नहीं करता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You create a lazy object (generator, map, cached_property): no real work yet
Step 2 → It remembers HOW to compute (function + current state), not the results
Step 3 → A consumer asks for a value (for loop, next(), list(), attribute access)
Step 4 → Only then is that one value computed (generator pauses at yield after it)
Step 5 → Consumers that stop early (any, islice, break) leave the rest uncomputed
Step 6 → cached_property stores the result after the first access, so it is computed once
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप lazy object बनाते हैं (generator, map, cached_property): अभी असली काम नहीं
Step 2 → वह सिर्फ याद रखता है कि calculate कैसे करना है (function + state), नतीजे नहीं
Step 3 → Consumer value माँगता है (for loop, next(), list(), attribute access)
Step 4 → तभी वही एक value calculate होती है (generator yield पर रुक जाता है)
Step 5 → जल्दी रुकने वाले consumers (any, islice, break) बाकी को uncomputed छोड़ देते हैं
Step 6 → cached_property पहली बार के बाद नतीजा रखता है, इसलिए एक ही बार calculate होता है
```

---

## 🟡 Real World Example
A Swiggy analytics job streams a 20 GB order log line by line through a generator pipeline (read, filter, parse, aggregate) using a few MB of memory. A FastAPI CSV export streams a million rows with `StreamingResponse` instead of building one huge string. A CLI tool imports `pandas` only when the `report` command is used, so `--help` starts in milliseconds.

## 🟡 Real Example Hindi mein
Swiggy का analytics job 20 GB की order log को generator pipeline (read, filter, parse, aggregate) से line-by-line stream करता है और कुछ MB memory लेता है। FastAPI CSV export दस लाख rows को एक विशाल string बनाने की बजाय `StreamingResponse` से stream करता है। CLI tool `pandas` को सिर्फ `report` command पर import करता है, इसलिए `--help` milliseconds में शुरू होता है।

---

## 💻 Code Example — Basic
```python
# Basic lazy evaluation: values are computed only when someone asks for them
import itertools  # lazy tools
import sys  # memory size
from typing import Iterator, List  # type hints

calls: List[int] = []  # record which values were computed


def square(x: int) -> int:
    calls.append(x)  # remember that we did the work
    return x * x  # the computation


eager: List[int] = [square(x) for x in range(5)]  # list comprehension: computes ALL 5 now
print(calls)  # all five were computed
# Output: [0, 1, 2, 3, 4]

calls.clear()  # reset the log
lazy: Iterator[int] = (square(x) for x in range(5))  # generator expression: computes NOTHING yet
print(calls)  # still empty
# Output: []
print(next(lazy), next(lazy))  # ask for two values -> only two computed
# Output: 0 1
print(calls)  # proof: only 0 and 1 were evaluated
# Output: [0, 1]

# map and filter are lazy in Python 3
m = map(square, range(1000))  # nothing happens yet
print(type(m).__name__)  # a lazy iterator object
# Output: map

# Infinite sequences are possible because nothing is built up front
evens = (n for n in itertools.count() if n % 2 == 0)  # infinite generator of even numbers
print(list(itertools.islice(evens, 5)))  # take only the first 5
# Output: [0, 2, 4, 6, 8]

# Memory: lazy objects are tiny, lists grow with the data
print(sys.getsizeof([x for x in range(100_000)]) > 100 * sys.getsizeof((x for x in range(100_000))))  # list is far bigger
# Output: True

# Short-circuit: any() stops at the first True, so later items are never computed
calls.clear()  # reset
print(any(square(x) > 10 for x in range(100)))  # stops once 4*4=16 > 10
# Output: True
print(calls)  # only 0..4 were evaluated, not 100 values
# Output: [0, 1, 2, 3, 4]
```

## 💻 Code Example — Advanced
```python
# Advanced: cached_property, lazy module attributes, lazy file pipeline, one-shot iterators
import io  # in-memory file for the demo
import itertools  # islice
from functools import cached_property  # compute once, on first access
from typing import Iterator, List


class Report:
    """Heavy attributes are computed only if someone reads them (and then cached)."""

    loads: int = 0  # how many times the expensive step ran

    def __init__(self, rows: List[int]) -> None:
        self.rows: List[int] = rows  # cheap: just store a reference

    @cached_property  # computed lazily on first access, then stored in the instance
    def total(self) -> int:
        Report.loads += 1  # record that real work happened
        return sum(self.rows)  # pretend this is expensive


r = Report([1, 2, 3])  # creating the object does no heavy work
print(Report.loads)  # nothing computed yet
# Output: 0
print(r.total, r.total, r.total)  # three reads...
# Output: 6 6 6
print(Report.loads)  # ...but only ONE computation
# Output: 1


# Lazy pipeline: read -> filter -> transform, one line at a time, constant memory
def read_lines(f: io.StringIO) -> Iterator[str]:
    for line in f:  # files yield one line at a time
        yield line.rstrip("\n")  # strip newline


def only_errors(lines: Iterator[str]) -> Iterator[str]:
    for line in lines:  # pull lazily from the previous stage
        if line.startswith("ERROR"):  # keep errors only
            yield line  # pass downstream


def to_codes(lines: Iterator[str]) -> Iterator[int]:
    for line in lines:  # pull lazily
        yield int(line.split()[1])  # "ERROR 500 timeout" -> 500


log = io.StringIO("INFO 200 ok\nERROR 500 timeout\nINFO 200 ok\nERROR 404 missing\nERROR 503 busy\n")  # fake log
pipeline: Iterator[int] = to_codes(only_errors(read_lines(log)))  # nothing has been read yet
print(list(itertools.islice(pipeline, 2)))  # pull just the first two error codes
# Output: [500, 404]
print(log.tell() < len(log.getvalue()))  # the rest of the log was never read
# Output: True


# Lazy module attributes (PEP 562): import a heavy module only when first used
import types  # module type for the demo

lazy_mod = types.ModuleType("lazy_mod")  # fake module for the demo
imported: List[str] = []  # track imports


def _getattr(name: str):  # called only when the attribute is missing
    if name == "decimal_ctx":  # a "heavy" attribute
        import decimal  # imported on first access only
        imported.append("decimal")  # record it
        value = decimal.getcontext().prec  # use it
        setattr(lazy_mod, name, value)  # cache so __getattr__ is not called again
        return value  # result
    raise AttributeError(name)  # normal behaviour for unknown names


lazy_mod.__getattr__ = _getattr  # type: ignore[attr-defined]  # module-level __getattr__
print(imported)  # not imported yet
# Output: []
print(lazy_mod.decimal_ctx, lazy_mod.decimal_ctx, imported)  # second access is cached
# Output: 28 28 ['decimal']

# Gotcha: a generator is one-shot
gen: Iterator[int] = (x for x in range(3))  # lazy sequence
print(list(gen), list(gen))  # second pass is empty
# Output: [0, 1, 2] []
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: generators are lazy
def naturals():
    n = 0
    while True:
        yield n
        n += 1

import itertools
print(list(itertools.islice(naturals(), 3)))   # [0, 1, 2]
squares = (x * x for x in range(1_000_000))    # lazy, nothing computed
```
```javascript
// JavaScript: generators are lazy; array methods (map/filter) are EAGER
function* naturals() { let n = 0; while (true) yield n++; }
const it = naturals();
console.log([it.next().value, it.next().value, it.next().value]);   // [0, 1, 2]
const squares = Array.from({ length: 1_000_000 }, (_, i) => i * i); // eager: all computed now
// Newer runtimes: iterator helpers  naturals().map(x => x * x).take(3).toArray()
```

Key differences: Python's `map` and `filter` are lazy iterators, while JavaScript's `Array.prototype.map/filter` are eager and build whole arrays. Both languages have lazy generators. Python generator expressions `(...)` are lazy and list comprehensions `[...]` are eager.

---

## 🟠 FastAPI Connection
Use lazy evaluation for big responses (`StreamingResponse` with a generator), for dependency results you only compute when an endpoint needs them, and for pagination instead of loading everything. Also, FastAPI itself resolves `Depends` only for endpoints that declare them, and heavy imports can be done inside the function that needs them.

```python
# FastAPI: stream a large response lazily instead of building it in memory (pip install fastapi httpx)
from typing import Iterator

from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.testclient import TestClient

app: FastAPI = FastAPI()  # create app


def csv_rows(n: int) -> Iterator[str]:
    yield "id,amount\n"  # header first
    for i in range(1, n + 1):  # rows are produced one at a time
        yield f"{i},{i * 10}\n"  # nothing is kept after it is sent


@app.get("/export.csv")  # GET /export.csv?rows=3
def export(rows: int = Query(3, ge=1, le=1_000_000)) -> StreamingResponse:
    return StreamingResponse(csv_rows(rows), media_type="text/csv")  # FastAPI pulls the generator lazily


client: TestClient = TestClient(app)  # test client
print(client.get("/export.csv", params={"rows": 3}).text)  # whole body, produced lazily
# Output:
# id,amount
# 1,10
# 2,20
# 3,30
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Consuming a one-shot generator twice
```python
# Wrong - the second pass is empty:
gen = (x for x in range(3))
print(list(gen), list(gen))      # [0, 1, 2] []

# Correct - recreate it, or store a list if you need multiple passes:
data = list(range(3))
print(sum(data), max(data))
```

❌ Mistake 2: Expecting side effects to run immediately
```python
# Wrong - nothing is printed or saved, because map is lazy and never consumed:
map(print, ["a", "b"])
map(save_to_db, rows)

# Correct - use a for loop for side effects (or consume the iterator):
for row in rows:
    save_to_db(row)
```

❌ Mistake 3: Lazy values that capture variables late
```python
# Wrong - the generator reads x when it runs, not when it was written:
x = 1
g = (x * i for i in range(3))
x = 10
print(list(g))      # [0, 10, 20]

# Correct - bind the value explicitly when you need today's value:
x = 1
g = (v * i for v in [x] for i in range(3))
x = 10
print(list(g))      # [0, 1, 2]
```

---

## 🧠 Tricky Interview Question

**Q**: What does this print?

```python
x = 1
g = (x * i for i in range(3))
x = 10
print(list(g))

y = [1, 2, 3]
g2 = (v for v in y)
y.append(4)
print(list(g2))

y2 = [1, 2, 3]
g3 = (v for v in y2)
y2 = [9]
print(list(g3))

m = map(print, ["a", "b"])
print("before")
list(m)
```

**Answer**:
```
[0, 10, 20]
[1, 2, 3, 4]
[1, 2, 3]
before
a
b
```
In a generator expression only the outermost iterable (`range(3)`, `y`, `y2`) is evaluated immediately; everything else, such as `x`, is looked up when the values are consumed, so `x = 10` is seen. `g2` keeps a reference to the same list, so the append is visible. Rebinding `y2` to a new list does not affect `g3`, which holds the old object. `map` does nothing until it is consumed, so "before" prints first.

---

## ⚫ Interview Questions + Answers

Q1: Lazy vs eager evaluation?
A1: Eager computes everything immediately and stores it (list comprehension). Lazy computes each value when requested and usually stores nothing (generator). Lazy saves memory and supports infinite or very large streams; eager allows indexing, `len()` and repeated iteration.

Q2: What is `functools.cached_property`?
A2: A decorator that runs the method once on first access and stores the result in the instance `__dict__`, so later accesses are plain attribute reads. Use it for expensive derived values. (It does not work on classes using `__slots__` without a `__dict__`.)

Q3: Are `map`, `filter`, `zip`, `range`, `dict.items()` lazy in Python 3?
A3: `map`, `filter`, `zip` return one-shot lazy iterators. `range` is a lazy sequence that can be iterated repeatedly. `dict.items()` is a live view, not a copy. In Python 2 `map`/`filter`/`zip` returned lists.

Q4: How do you lazily import a heavy module?
A4: Import inside the function that needs it, or use module `__getattr__` (PEP 562), or `importlib.util.LazyLoader`. Python 3.15 is expected to add explicit lazy imports (PEP 810); check your version before relying on it.

Q5: What are the dangers of lazy evaluation?
A5: One-shot iterators, late binding of variables, errors appearing far from where the code was written (an exception surfaces when consumed), side effects that never run, and resources (files, DB cursors) closing before the generator is consumed.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Data is large or unbounded (logs, streams, exports)
- You may stop early (first match, top N)
- Computing a value is expensive and might never be needed

❌ Avoid when:
- You need `len()`, indexing, sorting or several passes over the data
- The data is small and clarity matters more
- The source (file, DB cursor, connection) might be closed before consumption

---

## 📊 Visual Diagram

```
Eager list:       [ compute all N values ] ──► stored in memory ──► use some
                    cost: N computations + N values in RAM

Lazy generator:   consumer asks ──► compute ONE value ──► hand over ──► forget
                    next()            (pauses at yield)
                    cost: only the values actually requested

Pipeline:  read_lines ──► only_errors ──► to_codes ──► islice(2)
            each stage pulls one item from the stage before it
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Lazy evaluation | Compute only when needed | ज़रूरत पड़ने पर ही गणना |
| Eager evaluation | Compute everything immediately | सब कुछ तुरंत गणना |
| Generator | Function using yield, produces values on demand | माँग पर values देने वाला function |
| Iterator | Object giving one item per next() | हर next() पर एक item देने वाला object |
| cached_property | Lazy attribute computed once | एक बार calculate होने वाला lazy attribute |
| Short-circuit | Stop as soon as the answer is known | उत्तर मिलते ही रुक जाना |

---

## ⚡ 3-Line Summary
English: Lazy evaluation computes values only when they are requested, using generators, `map`, `filter`, `itertools` and `cached_property`. It saves memory, enables infinite streams and skips unused work. Remember that iterators are one-shot and variables are read late.
Hindi: Lazy evaluation में values तभी calculate होती हैं जब माँगी जाएँ, generators, `map`, `filter`, `itertools` और `cached_property` के साथ। इससे memory बचती है, infinite streams संभव होते हैं और बेकार काम नहीं होता। याद रखें कि iterators एक बार ही चलते हैं और variables देर से पढ़े जाते हैं।

---

## ➡️ Next Topic
**419. Profiling Python Code** — measure where time actually goes before optimizing anything.
