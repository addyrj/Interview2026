---

# 136. Iterators — Complete Guide
# हिंदी में: Iterators (एक-एक करके values देने वाले objects)

---

## 🔵 Simple Definition (English)
An iterator is an object that gives you values one at a time through `next()` and raises `StopIteration` when it has no more. Every `for` loop, list comprehension, `sum()` and `zip()` uses iterators behind the scenes. Iterators are lazy: they produce a value only when asked.

## 🔵 सरल परिभाषा (Hindi)
Iterator ऐसा object है जो `next()` से एक-एक value देता है और values खत्म होने पर `StopIteration` raise करता है। हर `for` loop, list comprehension, `sum()` और `zip()` अंदर से iterators ही इस्तेमाल करते हैं। Iterators lazy होते हैं: value तभी बनती है जब माँगी जाए।

---

## 🔴 Problem it Solves
Reading a 10 GB log file or a never-ending stream of Kafka messages into a list would crash the program. Iterators process one item at a time using constant memory, and they give one common way to loop over lists, files, dicts, database cursors and network streams.

## 🔴 यह क्यों बना? (Hindi)
10 GB की log file या कभी न खत्म होने वाली Kafka messages की stream को list में भरने से program crash हो जाता। Iterators एक समय में एक item process करते हैं और memory बहुत कम लगती है। साथ ही list, file, dict, database cursor और network stream, सबको loop करने का एक ही तरीका मिलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → for x in obj:  Python calls iter(obj) and gets an iterator
Step 2 → Python calls next(iterator) to get the first value
Step 3 → The value is assigned to x and the loop body runs
Step 4 → Repeat step 2 and 3
Step 5 → When next() raises StopIteration, the loop ends quietly
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → for x in obj: में Python iter(obj) call करके iterator लेता है
Step 2 → Python next(iterator) से पहली value लेता है
Step 3 → value x में जाती है और loop body चलती है
Step 4 → step 2 और 3 दोहराए जाते हैं
Step 5 → next() जब StopIteration raise करे तो loop चुपचाप खत्म हो जाता है
```

---

## 🟡 Real World Example
An Amazon-style data job reads a huge `orders.csv` with `for row in csv.reader(f)`, so only one row is in memory at a time. A Razorpay settlement script uses `itertools.islice` to take the first 1000 pending payments from an infinite stream. A RAG pipeline streams embedding batches with `itertools.batched` (Python 3.12+) instead of loading all documents.

## 🟡 Real Example Hindi mein
Amazon जैसा data job बहुत बड़ी `orders.csv` को `for row in csv.reader(f)` से पढ़ता है, इसलिए memory में एक समय पर सिर्फ एक row रहती है। Razorpay settlement script `itertools.islice` से अनंत stream से पहले 1000 pending payments लेती है। RAG pipeline सारे documents load करने की जगह `itertools.batched` (Python 3.12+) से embedding batches stream करती है।

---

## 💻 Code Example — Basic
```python
# Basic iterator usage - every line commented
nums: list[int] = [10, 20, 30]  # a list is iterable, not an iterator

it = iter(nums)  # iter() asks the list for a fresh iterator
print(type(it).__name__)  # what kind of object did we get?
# Output: list_iterator

print(next(it))  # first value
# Output: 10
print(next(it))  # second value
# Output: 20
print(next(it))  # third value
# Output: 30

try:  # fourth call has nothing left
    next(it)  # raises StopIteration
except StopIteration:  # this is how a for loop knows to stop
    print("exhausted")  # tell the user
# Output: exhausted

print(next(it, "default"))  # next() can take a default instead of raising
# Output: default

# What a for loop really does:
it2 = iter(nums)  # step 1: get iterator
while True:  # step 2: keep asking
    try:  # catch the end signal
        value = next(it2)  # step 3: next value
    except StopIteration:  # step 4: finished
        break  # leave the loop
    print("got", value)  # loop body
# Output:
# got 10
# got 20
# got 30

# Many built-ins return iterators (lazy)
print(iter(nums) is iter(nums))  # every iter() call gives a NEW object
# Output: False
m = map(str, nums)  # map is lazy
print(m)  # only an object, nothing computed yet
# Output: <map object at 0x...>   (address varies)
print(list(m), list(m))  # second time it is empty - used up
# Output: ['10', '20', '30'] []
```

## 💻 Code Example — Advanced
```python
# Production style: streaming files and itertools without loading all data
import io  # in-memory file for the demo
import itertools  # tools that work on iterators
from collections.abc import Iterable, Iterator  # abstract types for hints


def read_lines(f: io.StringIO) -> Iterator[str]:  # file objects are iterators
    for line in f:  # one line at a time, no f.read()
        yield line.rstrip("\n")  # clean the newline


log = io.StringIO("ok 1\nerror 2\nok 3\nerror 4\nok 5\n")  # fake log file
errors: Iterator[str] = (l for l in read_lines(log) if l.startswith("error"))  # lazy filter
print(next(errors))  # only the first error was processed
# Output: error 2
print(list(errors))  # the rest
# Output: ['error 4']


def take(n: int, source: Iterable[int]) -> list[int]:  # first n items
    return list(itertools.islice(source, n))  # works even on infinite sources


counter: Iterator[int] = itertools.count(100, 5)  # infinite 100,105,110...
print(take(4, counter))  # safe because islice stops
# Output: [100, 105, 110, 115]
print(take(2, counter))  # counter continues where it stopped
# Output: [120, 125]

# chain joins iterables, zip pairs them, enumerate numbers them
print(list(itertools.chain([1, 2], (3, 4), "ab")))  # one long stream
# Output: [1, 2, 3, 4, 'a', 'b']
print(list(zip("abc", itertools.count(1))))  # zip stops at the shortest
# Output: [('a', 1), ('b', 2), ('c', 3)]

# batching: Python 3.12+ has itertools.batched
batches = [list(b) for b in itertools.batched(range(7), 3)]  # chunks of 3
print(batches)  # last chunk is smaller
# Output: [[0, 1, 2], [3, 4, 5], [6]]

# Iterators can be consumed only once - tee makes independent copies
a, b = itertools.tee(iter([1, 2, 3]))  # two iterators from one
print(sum(a), list(b))  # each has its own position
# Output: 6 [1, 2, 3]

# Peeking safely using a sentinel
def first_or_none(source: Iterable[str]) -> str | None:  # safe first element
    return next(iter(source), None)  # no exception on empty input


print(first_or_none([]), first_or_none(["x", "y"]))  # empty and non-empty
# Output: None x

# Memory proof: a generator expression stays tiny even for 10 million items
import sys  # to measure object size
gen = (i * i for i in range(10_000_000))  # nothing computed yet
print(sys.getsizeof(gen) < 1000)  # small, fixed-size object
# Output: True
print(sum(1 for _ in itertools.islice(gen, 5)))  # consume five items only
# Output: 5
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript has the same idea with `Symbol.iterator`, `next()` returning `{value, done}`, and `for...of`. Python signals the end with an exception (`StopIteration`) instead of a `done` flag.

```python
# Python way
it = iter([1, 2])
print(next(it))              # 1
print(next(it))              # 2
print(next(it, None))        # None  (exhausted, default given)
for ch in "hi":              # strings are iterable too
    print(ch)
```
```javascript
// JavaScript way
const it = [1, 2][Symbol.iterator]();
console.log(it.next());      // { value: 1, done: false }
console.log(it.next());      // { value: 2, done: false }
console.log(it.next());      // { value: undefined, done: true }
for (const ch of "hi") console.log(ch);
```

Key differences: JS returns `{value, done}` objects, Python raises `StopIteration`. In Python `for x in dict` loops keys; in JS `for...of` on an object fails (objects are not iterable) and `for...in` loops keys.

---

## 🟠 FastAPI Connection
FastAPI can stream large responses using an iterator or generator with `StreamingResponse`, so a million-row export never sits fully in memory. SQLAlchemy result cursors are iterators too.

```python
# FastAPI: stream rows lazily (pip install fastapi httpx)
from collections.abc import Iterator  # type hint
from fastapi import FastAPI  # app
from fastapi.responses import StreamingResponse  # streaming response
from fastapi.testclient import TestClient  # in-process test

app: FastAPI = FastAPI()  # create app


def csv_rows(n: int) -> Iterator[str]:  # lazy producer
    yield "id,name\n"  # header line
    for i in range(1, n + 1):  # one row per loop
        yield f"{i},user{i}\n"  # produced only when the client reads


@app.get("/export")  # GET /export
def export() -> StreamingResponse:  # return an iterator-backed response
    return StreamingResponse(csv_rows(3), media_type="text/csv")  # stream it


client = TestClient(app)  # test client
print(client.get("/export").text)  # whole body after streaming
# Output:
# id,name
# 1,user1
# 2,user2
# 3,user3
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Reusing an exhausted iterator
```python
# Wrong - second pass gets nothing
squares = map(lambda x: x * x, [1, 2, 3])
print(list(squares), list(squares))   # [1, 4, 9] []

# Right - recreate it, or store the result in a list when reuse is needed
squares = [x * x for x in [1, 2, 3]]
print(squares, squares)               # [1, 4, 9] [1, 4, 9]
```

❌ Mistake 2: Calling `next()` on an iterable (not an iterator)
```python
# Wrong - lists are iterable but have no __next__
# next([1, 2, 3])        # TypeError: 'list' object is not an iterator

# Right - wrap with iter() first
print(next(iter([1, 2, 3])))          # 1
```

❌ Mistake 3: `list()` on an infinite iterator
```python
# Wrong - never finishes and eats all memory
# import itertools; list(itertools.count())

# Right - bound it with islice
import itertools
print(list(itertools.islice(itertools.count(), 3)))   # [0, 1, 2]
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
it = iter([1, 2, 3, 4])
print(2 in it)
print(list(it))
data = iter("abc")
print(list(zip(data, data)))
```

**Answer**:
```
True
[3, 4]
[('a', 'b')]
```
`2 in it` consumes the iterator up to and including `2`, so only `[3, 4]` remains. In `zip(data, data)` both arguments are the same iterator, so values are taken alternately: `a` and `b` form a pair, then `c` is taken but `data` has nothing for the second slot, so it is dropped (and `c` is lost).

---

## ⚫ Interview Questions + Answers

Q1: What methods make an object an iterator?
A1: `__iter__()` (returning itself) and `__next__()` (returning the next value or raising `StopIteration`).

Q2: How does `for` end without an error?
A2: The loop catches `StopIteration` internally and exits cleanly.

Q3: Why use iterators instead of lists?
A3: Memory (constant instead of O(n)), laziness (compute only what you need) and ability to model infinite streams.

Q4: Are iterators reusable?
A4: No. Once exhausted they stay exhausted. Call `iter()` on the original iterable again for a fresh one, or use `itertools.tee`.

Q5: Name useful `itertools` functions.
A5: `count`, `cycle`, `islice`, `chain`, `groupby`, `tee`, `product`, `permutations`, and `batched` (3.12+).

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Data is big or unbounded (files, logs, streams, DB cursors)
- You process items one by one in a pipeline
- You want to stop early without computing everything

❌ Avoid when:
- You need random access (`items[5]`), `len()` or multiple passes (use a list)
- The data is tiny and clarity matters more
- You must read the same data twice and cannot recreate it

---

## 📊 Visual Diagram

```
 iterable ──iter()──► iterator ──next()──► 10
 [10,20,30]              │       next()──► 20
                         │       next()──► 30
                         └─────next()──► StopIteration  → for loop ends

 position pointer moves forward only, never back, never resets
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Iterator | Object with `__next__` | एक-एक value देने वाला object |
| Iterable | Object that can give an iterator | जिससे iterator मिल सके |
| `StopIteration` | Signal that values are finished | values खत्म होने का संकेत |
| Lazy evaluation | Compute only when needed | ज़रूरत पर ही गणना |
| Exhausted | Iterator with no values left | जिसकी values खत्म हो गई |
| `itertools` | Standard library of iterator tools | iterator tools की library |

---

## ⚡ 3-Line Summary
English: An iterator gives values one by one via `next()` and signals the end with `StopIteration`. `for` loops, comprehensions and many built-ins rely on this protocol. Iterators are lazy, memory-friendly and single-use.
Hindi: Iterator `next()` से एक-एक value देता है और अंत में `StopIteration` से बताता है। `for` loop, comprehension और कई built-ins इसी protocol पर चलते हैं। Iterators lazy, कम memory वाले और सिर्फ एक बार इस्तेमाल होने वाले होते हैं।

---

## ➡️ Next Topic
**137. Iterables vs Iterators** — the exact difference between `__iter__` on a container and `__next__` on a cursor.
