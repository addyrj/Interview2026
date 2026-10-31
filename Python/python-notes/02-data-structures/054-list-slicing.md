---

# 054. List Slicing
# हिंदी में: List Slicing (list का टुकड़ा काटना)

---

## 🔵 Simple Definition (English)
Slicing takes a part of a list using `my_list[start:stop:step]`. `start` is included, `stop` is excluded, and `step` is the gap. A slice returns a NEW list (a shallow copy of that part). Slicing never raises `IndexError` for out-of-range bounds.

## 🔵 सरल परिभाषा (Hindi)
Slicing `my_list[start:stop:step]` से list का एक हिस्सा लेती है। `start` शामिल, `stop` शामिल नहीं, `step` बीच का अंतर। Slice एक नई list (उस हिस्से की shallow copy) लौटाती है। Out-of-range bounds पर slicing कभी `IndexError` नहीं देती।

---

## 🔴 Problem it Solves
Without slicing you write loops to pick the first 10 items, the last 3, every second item, or to reverse a list. Slicing does each in one expression. It also lets you replace, delete or insert whole ranges in place (`a[1:3] = [...]`), and makes copying a list a one-liner (`a[:]`).

## 🔴 यह क्यों बना? (Hindi)
Slicing के बिना पहले 10 items, आखिरी 3, हर दूसरा item या list उलटने के लिए loops लिखने पड़ते। Slicing यह सब एक expression में करती है। साथ ही in-place range बदलना, हटाना, जोड़ना (`a[1:3] = [...]`) और list copy करना (`a[:]`) आसान हो जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python builds a slice object: slice(start, stop, step)
Step 2 → Missing start/stop default by direction
           step > 0: start=0, stop=len     step < 0: start=len-1, stop=before 0
Step 3 → Negative numbers count from the end (-1 = last item)
Step 4 → Out-of-range numbers are clamped to the list bounds
Step 5 → Items start, start+step, ... while before stop are copied
Step 6 → A new list is returned (original unchanged)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Python slice(start, stop, step) object बनाता है
Step 2 → न दिए गए start/stop direction के हिसाब से default होते हैं
Step 3 → Negative index पीछे से गिनते हैं (-1 = आखिरी)
Step 4 → Out-of-range numbers अपने आप list की सीमा में आ जाते हैं
Step 5 → चुने गए items की नई list बनती है, original वैसी ही रहती है
```

---

## 🟡 Real World Example
Swiggy home screen shows only the top 5 restaurants: `restaurants[:5]`. Pagination: `rows[(page-1)*size : page*size]`. A chat app keeps only the last 20 messages as context for the LLM: `messages[-20:]`. A log viewer shows the last 100 lines.

## 🟡 Real Example Hindi mein
Swiggy की home screen सिर्फ top 5 restaurants दिखाती है: `restaurants[:5]`. Pagination: `rows[(page-1)*size : page*size]`. Chat app LLM के context के लिए सिर्फ आखिरी 20 messages रखता है: `messages[-20:]`. Log viewer आखिरी 100 lines दिखाता है।

---

## 💻 Code Example — Basic
```python
# Basic list slicing - every line commented
from typing import List  # type hint helper

nums: List[int] = [10, 20, 30, 40, 50, 60]  # indexes 0..5, or -6..-1

print(nums[1:4])  # items at index 1, 2, 3 (4 excluded)
# Output: [20, 30, 40]
print(nums[:3])  # from the start up to index 3
# Output: [10, 20, 30]
print(nums[3:])  # from index 3 to the end
# Output: [40, 50, 60]
print(nums[-2:])  # last two items
# Output: [50, 60]
print(nums[:-1])  # everything except the last
# Output: [10, 20, 30, 40, 50]
print(nums[::2])  # every second item
# Output: [10, 30, 50]
print(nums[1::2])  # every second item, starting at index 1
# Output: [20, 40, 60]
print(nums[::-1])  # reversed copy
# Output: [60, 50, 40, 30, 20, 10]
print(nums[4:1:-1])  # backwards from index 4 down to 2
# Output: [50, 40, 30]

print(nums[2:100])  # stop is clamped, no IndexError
# Output: [30, 40, 50, 60]
print(nums[10:20])  # completely out of range gives an empty list
# Output: []

copy: List[int] = nums[:]  # full slice = shallow copy
copy[0] = 999  # change the copy only
print(nums[0], copy[0])  # original is untouched
# Output: 10 999

# Assignment to a slice
letters: List[str] = ["a", "b", "c", "d", "e"]  # sample list
letters[1:3] = ["X", "Y", "Z"]  # replace 2 items with 3 (length may change)
print(letters)  # Output: ['a', 'X', 'Y', 'Z', 'd', 'e']
del letters[::2]  # delete every second item
print(letters)  # Output: ['X', 'Z', 'e']
```

## 💻 Code Example — Advanced
```python
# Production style: pagination, sliding window, chunking, slice objects, shallow copy
from typing import Any, Iterator, List, Sequence, TypeVar  # type hints

T = TypeVar("T")  # generic item type


def paginate(items: Sequence[T], page: int, size: int) -> List[T]:
    """Return one page (1-based) of items."""
    if page < 1 or size < 1:  # validate input
        raise ValueError("page and size must be >= 1")  # clear error
    start: int = (page - 1) * size  # first index of the page
    return list(items[start:start + size])  # slice the page


data: List[int] = list(range(1, 11))  # 1..10
print(paginate(data, 1, 4), paginate(data, 3, 4), paginate(data, 4, 4))
# Output: [1, 2, 3, 4] [9, 10] []


def chunks(items: Sequence[T], size: int) -> Iterator[Sequence[T]]:
    """Yield consecutive chunks (batching for API calls)."""
    for i in range(0, len(items), size):  # jump by size
        yield items[i:i + size]  # last chunk may be shorter


print(list(chunks(data, 4)))  # Output: [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10]]


def moving_average(values: List[float], window: int) -> List[float]:
    """Sliding window using slices."""
    return [sum(values[i:i + window]) / window for i in range(len(values) - window + 1)]


print(moving_average([1, 2, 3, 4, 5], 3))  # Output: [2.0, 3.0, 4.0]

# Keep only the latest N messages (LLM context window)
history: List[str] = [f"msg{i}" for i in range(1, 8)]  # 7 messages
history = history[-3:]  # keep last 3
print(history)  # Output: ['msg5', 'msg6', 'msg7']

# slice objects can be named and reused
FIRST_TWO: slice = slice(0, 2)  # same as [0:2]
print([1, 2, 3][FIRST_TWO], "hello"[FIRST_TWO])  # works on any sequence
# Output: [1, 2] he

# Slicing is a SHALLOW copy: nested objects are shared
matrix: List[List[int]] = [[1, 2], [3, 4]]  # list of lists
shallow: List[List[int]] = matrix[:]  # copies the outer list only
shallow[0].append(99)  # mutate an inner list
print(matrix)  # the original sees the change!
# Output: [[1, 2, 99], [3, 4]]
print(shallow is matrix, shallow[0] is matrix[0])  # different outer, same inner
# Output: False True

# Extended slice assignment needs equal length
evens: List[int] = [0, 1, 2, 3, 4, 5]  # sample
evens[::2] = [100, 200, 300]  # replace indexes 0, 2, 4
print(evens)  # Output: [100, 1, 200, 3, 300, 5]
try:  # wrong size
    evens[::2] = [1, 2]  # 2 values for 3 slots
except ValueError as exc:  # error
    print("ValueError:", exc)  # explain
# Output: ValueError: attempt to assign sequence of size 2 to extended slice of size 3
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
a = [10, 20, 30, 40, 50]
a[1:3]      # [20, 30]
a[-2:]      # [40, 50]   negative index works
a[::-1]     # [50, 40, 30, 20, 10]
a[::2]      # [10, 30, 50]
a[:]        # shallow copy
```

```javascript
// JavaScript
const a = [10, 20, 30, 40, 50];
a.slice(1, 3);            // [20, 30]
a.slice(-2);              // [40, 50]  negative works in slice()
[...a].reverse();         // reversed copy (a.reverse() mutates!)
a.filter((_, i) => i % 2 === 0);   // every second item - no step argument
[...a];                   // shallow copy  (or a.slice())
a.splice(1, 2);           // MUTATES (do not confuse with slice)
```

Key differences: Python has dedicated slice syntax with a `step`; JS uses `slice(start, end)` with no step. Python slices work with `[]` on lists, strings and tuples. JS `a[-1]` is `undefined`, while Python `a[-1]` is the last item. JS `splice` mutates; Python slice assignment mutates; a plain Python slice never does.

---

## 🟠 FastAPI Connection
Slicing is how you paginate in-memory results and trim chat history before sending it to an LLM. With a database you prefer `LIMIT/OFFSET` in SQL, but slicing is common for cached lists, search results and tests.

```python
# FastAPI: pagination with list slicing (needs: pip install fastapi)
from typing import Dict, List, Union  # type hints
from fastapi import FastAPI, Query  # framework + validation

app: FastAPI = FastAPI()  # create app
PRODUCTS: List[str] = [f"product-{i}" for i in range(1, 51)]  # 50 fake products


@app.get("/products")  # GET /products?page=2&size=10
def list_products(
    page: int = Query(1, ge=1),  # page number starting at 1
    size: int = Query(10, ge=1, le=50),  # items per page, capped at 50
) -> Dict[str, Union[int, List[str]]]:
    start: int = (page - 1) * size  # first index
    return {"page": page, "total": len(PRODUCTS), "items": PRODUCTS[start:start + size]}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Off-by-one because `stop` is excluded
```python
a = [1, 2, 3, 4, 5]

# Wrong - expected first 3 items to include index 3:
print(a[0:3])    # [1, 2, 3]  (index 3 not included)

# Correct: stop = last index + 1
print(a[1:4])    # [2, 3, 4]
```

❌ Mistake 2: Thinking `b = a` or `a[:]` makes a deep copy
```python
a = [[1], [2]]

b = a            # same list object (alias)
c = a[:]         # new outer list, SAME inner lists
c[0].append(9)
print(a)         # [[1, 9], [2]]  - changed through the copy!

# Correct for nested data:
import copy
d = copy.deepcopy(a)
```

❌ Mistake 3: Expecting `IndexError` from slices, or forgetting a slice makes a copy
```python
a = [1, 2, 3]
print(a[5:10])   # []  - no error (but a[5] would raise IndexError)

# Slicing a huge list in a loop copies each time (O(k) memory/time):
# Use itertools.islice or indexes when you only need to iterate.
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
a = [0, 1, 2, 3, 4, 5]
a[1:3] = [9]
print(a)
b = a[::-2]
print(b)
a[len(a):] = [7, 8]
print(a)
print([1, 2, 3][::-1][0:2], "python"[-3:-1])
```

**Answer**:
```
[0, 9, 3, 4, 5]
[5, 3, 0]
[0, 9, 3, 4, 5, 7, 8]
[3, 2] ho
```
Replacing two items with one shrinks the list. `[::-2]` starts at the end and takes every second item backwards. Assigning at `[len(a):]` appends (an empty slice at the end), like `extend`. `"python"[-3:-1]` is indexes -3 and -2: "ho".

---

## ⚫ Interview Questions + Answers

Q1: What is the syntax and rule for `a[start:stop:step]`?
A1: `start` inclusive, `stop` exclusive, `step` the stride (default 1). Negative values count from the end. Omitted values default by direction. With negative step, start is higher than stop.

Q2: Does slicing copy the list?
A2: Yes, it creates a new list, but a SHALLOW copy: the new list holds references to the same inner objects. Use `copy.deepcopy` for nested mutable data.

Q3: How do you reverse a list?
A3: `a[::-1]` returns a reversed copy. `a.reverse()` reverses in place and returns `None`. `reversed(a)` gives a lazy iterator.

Q4: Why does `a[10:20]` not raise `IndexError`?
A4: Slice bounds are clamped to the list length, so out-of-range slices return an empty or shortened list. Only single-index access `a[10]` raises.

Q5: What is the time complexity of slicing?
A5: O(k) where k is the number of items in the result, because it copies references. For huge data where you only iterate, use `itertools.islice` (no copy) or a `memoryview` for bytes.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Taking first/last N items, pages or chunks
- Reversing or stepping (`[::-1]`, `[::2]`)
- Quick shallow copy (`a[:]`) or replacing a range in place

❌ Avoid when:
- Data is nested and you need an independent copy (use deepcopy)
- Very large lists in tight loops (copies cost time; use islice)
- A named helper (`paginate`) would make intent clearer than a complex slice

---

## 📊 Visual Diagram

```
 index:     0    1    2    3    4    5
 value:   [ 10 , 20 , 30 , 40 , 50 , 60 ]
 neg idx:  -6   -5   -4   -3   -2   -1
 cuts:    ^0   ^1   ^2   ^3   ^4   ^5   ^6

 a[1:4]   → 20 30 40          (cut 1 up to cut 4)
 a[-2:]   → 50 60
 a[::2]   → 10 30 50
 a[::-1]  → 60 50 40 30 20 10
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Slice | Part of a sequence | sequence का हिस्सा |
| start / stop / step | Begin, end (excluded), stride | शुरू, अंत (शामिल नहीं), कदम |
| Negative index | Counts from the end | पीछे से गिनती |
| Shallow copy | Copies outer list only | सिर्फ बाहरी list की copy |
| Slice assignment | Replace a range in place | range को जगह पर बदलना |
| Clamping | Bounds cut to valid range | सीमा को valid range में लाना |

---

## ⚡ 3-Line Summary
English: `a[start:stop:step]` returns a new shallow-copied list; start is included, stop is excluded, and out-of-range bounds never raise. Use `[::-1]`, `[-n:]`, `[:]` for reverse, tail and copy. Slice assignment can change a list's length in place.
Hindi: `a[start:stop:step]` नई shallow-copy list लौटाता है; start शामिल, stop शामिल नहीं, और out-of-range पर error नहीं आता। `[::-1]`, `[-n:]`, `[:]` से reverse, tail और copy मिलती है। Slice assignment list की लंबाई बदल सकता है।

---

## ➡️ Next Topic
**055. Tuple Complete Guide** — immutable sequences, packing/unpacking and why tuples are hashable.
