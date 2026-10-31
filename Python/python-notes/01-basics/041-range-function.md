---

# 041. range() Function
# हिंदी में: range() Function (संख्याओं की sequence)

---

## 🔵 Simple Definition (English)
`range()` produces an immutable sequence of integers: `range(stop)`, `range(start, stop)` or `range(start, stop, step)`. It does not build a list in memory. It stores only start, stop and step and calculates each number when asked.

## 🔵 सरल परिभाषा (Hindi)
`range()` integers की एक immutable sequence बनाता है: `range(stop)`, `range(start, stop)` या `range(start, stop, step)`। यह memory में list नहीं बनाता, सिर्फ start, stop, step याद रखता है और हर number माँगने पर calculate करता है।

---

## 🔴 Problem it Solves
Looping "N times" or over index positions needed a list of numbers like `[0, 1, 2, ... 999999]`, which wastes memory. `range()` gives the same numbers lazily, so `range(10**9)` costs a few bytes. It also supports `len()`, indexing, slicing and fast `in` checks.

## 🔴 यह क्यों बना? (Hindi)
"N बार चलाओ" के लिए पहले numbers की पूरी list बनानी पड़ती थी, जिससे memory बर्बाद होती थी। `range()` वही numbers lazily देता है, इसलिए `range(10**9)` बस कुछ bytes लेता है। इसमें `len()`, indexing, slicing और तेज़ `in` check भी चलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → range(start, stop, step) stores only 3 integers
Step 2 → Loop asks for the next value
Step 3 → value = start + index * step
Step 4 → Stop when value reaches stop (stop is EXCLUDED)
Step 5 → step > 0 counts up, step < 0 counts down, step = 0 → ValueError
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → सिर्फ 3 integers store होते हैं (start, stop, step)
Step 2 → हर बार value = start + index * step निकलती है
Step 3 → stop वाली value शामिल नहीं होती (exclusive)
Step 4 → step negative हो तो उल्टी गिनती; step 0 → ValueError
```

---

## 🟡 Real World Example
Razorpay batch job: process 1 million payments in pages of 1000 using `range(0, total, 1000)` to get each page offset. An AI app splits a long document into chunks with `range(0, len(text), chunk_size)` to embed them. A pagination API computes page numbers with `range(1, pages + 1)`.

## 🟡 Real Example Hindi mein
Razorpay batch job में 10 लाख payments को 1000-1000 के pages में `range(0, total, 1000)` से process करते हैं। AI app में लंबे document को `range(0, len(text), chunk_size)` से chunks में बाँटकर embed करते हैं। Pagination में page numbers `range(1, pages + 1)` से बनते हैं।

---

## 💻 Code Example — Basic
```python
# Basic range() examples - every line commented
print(list(range(5)))  # one argument: 0 up to 4
# Output: [0, 1, 2, 3, 4]

print(list(range(2, 6)))  # two arguments: start=2, stop=6 (6 excluded)
# Output: [2, 3, 4, 5]

print(list(range(0, 10, 3)))  # three arguments: step of 3
# Output: [0, 3, 6, 9]

print(list(range(5, 0, -1)))  # negative step counts down
# Output: [5, 4, 3, 2, 1]

for i in range(3):  # classic "do this 3 times"
    print("hello", i)  # i is 0, 1, 2
# Output:
# hello 0
# hello 1
# hello 2

r: range = range(1, 10, 2)  # a range object, not a list
print(r)  # Output: range(1, 10, 2)
print(len(r), r[0], r[-1])  # supports len and indexing
# Output: 5 1 9
print(7 in r, 8 in r)  # fast membership test (math, no scanning)
# Output: True False

print(sum(range(1, 101)))  # sum of 1..100
# Output: 5050

print(list(range(5, 5)), list(range(5, 1)))  # empty ranges are fine
# Output: [] []
```

## 💻 Code Example — Advanced
```python
# Production style: pagination, chunking, memory, slicing, equality
import sys  # to measure memory
from typing import Iterator, List  # type hints


def page_offsets(total: int, page_size: int) -> Iterator[int]:
    """Yield the starting offset of every page."""
    yield from range(0, total, page_size)  # lazy offsets: 0, 25, 50...


print(list(page_offsets(101, 25)))  # 101 rows, 25 per page
# Output: [0, 25, 50, 75, 100]


def chunk_text(text: str, size: int, overlap: int = 0) -> List[str]:
    """Split text into chunks (used before embedding in RAG)."""
    step: int = size - overlap  # how far to move each time
    if step <= 0:  # protect against an infinite/invalid setup
        raise ValueError("overlap must be smaller than size")  # clear message
    return [text[i:i + size] for i in range(0, len(text), step)]  # slice per offset


print(chunk_text("abcdefghij", 4))  # no overlap
# Output: ['abcd', 'efgh', 'ij']
print(chunk_text("abcdefghij", 4, overlap=2))  # chunks share 2 characters
# Output: ['abcd', 'cdef', 'efgh', 'ghij', 'ij']

# Memory: range is tiny, list is huge
big_range: range = range(10_000_000)  # ten million numbers, lazily
print(sys.getsizeof(big_range))  # same size regardless of length
# Output: 48
print(sys.getsizeof(list(range(1000))) > 8000)  # a real list grows with n
# Output: True

# Slicing a range returns another range
r: range = range(0, 20, 2)  # 0, 2, 4 ... 18
print(r[2:5])  # slice -> new range object
# Output: range(4, 10, 2)
print(list(r[::-1])[:3])  # reversed view, first three
# Output: [18, 16, 14]

# Equality compares the values produced, not the arguments
print(range(0, 3) == range(0, 3, 1), range(0) == range(5, 5))
# Output: True True

# Floats are not allowed - build them from integers
try:  # catch the TypeError
    range(0.5, 3)  # type: ignore[arg-type]
except TypeError as exc:  # floats rejected
    print("TypeError:", exc)  # explain
# Output: TypeError: 'float' object cannot be interpreted as an integer
print([i / 10 for i in range(0, 5)])  # float steps via division
# Output: [0.0, 0.1, 0.2, 0.3, 0.4]
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
for i in range(5):                 # 0..4
    print(i)
nums = list(range(1, 6))           # [1, 2, 3, 4, 5]
evens = list(range(0, 10, 2))      # [0, 2, 4, 6, 8]
down = list(range(5, 0, -1))       # [5, 4, 3, 2, 1]
```

```javascript
// JavaScript (no built-in range)
for (let i = 0; i < 5; i++) { console.log(i); }
const nums = Array.from({ length: 5 }, (_, i) => i + 1);     // [1..5]
const evens = Array.from({ length: 5 }, (_, i) => i * 2);    // [0,2,4,6,8]
const down = Array.from({ length: 5 }, (_, i) => 5 - i);     // [5..1]
// lodash: _.range(5)
```

Key differences: JavaScript has no native `range`; you write a C-style loop or `Array.from`. Python's `range` is lazy, its `stop` is exclusive, and it only accepts integers.

---

## 🟠 FastAPI Connection
FastAPI list endpoints use pagination (`skip`, `limit`), and background jobs often batch work with `range(0, total, batch)`. Use `Query` to validate limits so a user cannot request a giant range.

```python
# FastAPI: page numbers using range (needs: pip install fastapi)
from typing import Dict, List  # type hints
from fastapi import FastAPI, Query  # app and query validation

app: FastAPI = FastAPI()  # create app
TOTAL_ITEMS: int = 95  # pretend DB size


@app.get("/pages")  # GET /pages?size=10
def pages(size: int = Query(10, ge=1, le=50)) -> Dict[str, List[int]]:
    offsets: List[int] = list(range(0, TOTAL_ITEMS, size))  # start of each page
    return {"offsets": offsets}  # JSON: {"offsets": [0, 10, ..., 90]}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting that `stop` is excluded
```python
# Wrong - wanted 1..10 but got 1..9:
print(list(range(1, 10)))     # [1, 2, ..., 9]

# Correct:
print(list(range(1, 11)))     # [1, 2, ..., 10]
```

❌ Mistake 2: Wrong step direction gives an empty range
```python
# Wrong - counting down without a negative step:
print(list(range(5, 0)))      # []  (no error, just empty!)

# Correct:
print(list(range(5, 0, -1)))  # [5, 4, 3, 2, 1]
```

❌ Mistake 3: Using floats or `range(len(x))` everywhere
```python
# Wrong - TypeError for floats:
# range(0, 1, 0.1)

# Correct - scale integers, or use numpy.arange(0, 1, 0.1):
print([i / 10 for i in range(10)])

# Also avoid range(len(items)) just to read items - use enumerate(items)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
r = range(3)
it = iter(r)
print(list(it), list(it))
print(list(r), list(r))
print(range(10)[3], range(10)[-1], 3 in range(10), 3.0 in range(10))
print(type(range(3)), range(3) is range(3))
```

**Answer**:
```
[0, 1, 2] []
[0, 1, 2] [0, 1, 2]
3 9 True True
<class 'range'> False
```
An iterator is used up after one pass, so the second `list(it)` is empty. The `range` object itself is re-iterable, creating a fresh iterator each time. `3.0 in range(10)` is `True` because the membership test falls back to comparing values (`3.0 == 3`).

---

## ⚫ Interview Questions + Answers

Q1: Is `range` a list or a generator in Python 3?
A1: Neither. It is its own immutable sequence type. It is lazy like a generator but it supports `len()`, indexing, slicing, `in`, and can be iterated many times. A generator supports none of those and is single-use.

Q2: What is the time complexity of `x in range(n)`?
A2: O(1) for integers. Python checks the bounds and `(x - start) % step == 0` instead of scanning. For a list the same check is O(n).

Q3: How do you loop backwards?
A3: `range(n - 1, -1, -1)` or `reversed(range(n))`. The second is easier to read.

Q4: How do you produce float steps?
A4: `range` rejects floats. Use `[i * 0.1 for i in range(10)]` or `numpy.arange` / `numpy.linspace`. Beware float rounding errors.

Q5: What happens with `range(0, 10, 0)`?
A5: `ValueError: range() arg 3 must not be zero`. A zero step would never move forward.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You need to repeat something N times
- You need offsets, page numbers or index positions
- You want a memory-cheap number sequence (even for huge sizes)

❌ Avoid when:
- You only read items from a list (loop over the list directly)
- You need both index and item (use `enumerate`)
- You need floats (use NumPy or a comprehension)

---

## 📊 Visual Diagram

```
range(2, 12, 3)
 start=2  step=3  stop=12 (excluded)

 2 ──► 5 ──► 8 ──► 11 ──✖ 14 (>= stop, stop)
 idx0   idx1   idx2   idx3

value = start + index * step    (nothing stored in memory)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| start | First number (default 0) | पहली संख्या |
| stop | End value, not included | अंतिम सीमा (शामिल नहीं) |
| step | Gap between numbers | दो संख्याओं के बीच अंतर |
| Lazy | Computed only when needed | ज़रूरत पड़ने पर ही बनना |
| Immutable | Cannot be changed | बदला नहीं जा सकता |
| Pagination | Splitting data into pages | डेटा को pages में बाँटना |

---

## ⚡ 3-Line Summary
English: `range(start, stop, step)` is a lazy, immutable sequence of integers where stop is excluded. It uses tiny memory, supports `len`, indexing, slicing and O(1) `in`. It only accepts integers; use comprehensions or NumPy for floats.
Hindi: `range(start, stop, step)` integers की lazy, immutable sequence है जिसमें stop शामिल नहीं होता। Memory बहुत कम, `len`, indexing, slicing और O(1) `in` चलता है। Floats के लिए comprehension या NumPy इस्तेमाल करें।

---

## ➡️ Next Topic
**042. enumerate()** — get the index and the item together without `range(len(x))`.
