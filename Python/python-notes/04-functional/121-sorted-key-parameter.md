---

# 121. sorted() + key parameter
# हिंदी में: sorted() और key parameter (किसी भी rule से sort करना)

---

## 🔵 Simple Definition (English)
`sorted(iterable, key=..., reverse=...)` returns a NEW sorted list. The `key` function is called once per item and the result is what gets compared. This lets you sort by length, by a dict field, by several fields, or any custom rule.

## 🔵 सरल परिभाषा (Hindi)
`sorted(iterable, key=..., reverse=...)` एक NEW sorted list लौटाता है। `key` function हर item पर एक बार चलता है और उसका result compare होता है। इससे आप length, dict के field, कई fields या किसी भी custom rule से sort कर सकते हैं।

---

## 🔴 Problem it Solves
Old Python 2 used `cmp` functions that compared two items at a time and were slow and confusing. Real data is records (dicts, objects), not plain numbers. `key=` says "compare using this value" and runs the function only n times (not n log n times). Sorting is also stable, so you can sort by several columns in steps.

## 🔴 यह क्यों बना? (Hindi)
पुराने Python 2 में `cmp` function था जो दो items को एक बार में compare करता था और धीमा व confusing था। असली data records (dict, objects) होता है, सिर्फ numbers नहीं। `key=` कहता है "इस value से compare करो" और function सिर्फ n बार चलता है (n log n बार नहीं)। Sorting stable भी है, इसलिए कई columns से step-by-step sort हो सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → sorted() copies the iterable into a new list
Step 2 → It calls key(item) ONCE per item and stores the results
Step 3 → It sorts using Timsort, comparing the stored keys (not the items)
Step 4 → Equal keys keep their original order (stable sort)
Step 5 → reverse=True flips the order but keeps stability
Step 6 → Tuples as keys compare left to right: (a, b) sorts by a, then b

sorted(["bb","a","ccc"], key=len)  ->  keys 2,1,3 -> ["a","bb","ccc"]
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → sorted() iterable की नई list बनाता है
Step 2 → हर item पर key(item) एक बार चलाकर results रख लेता है
Step 3 → Timsort से keys (items नहीं) compare करके sort करता है
Step 4 → बराबर keys अपना पुराना order रखती हैं (stable sort)
Step 5 → reverse=True order पलटता है पर stability बनी रहती है
Step 6 → Tuple key बाएं से दाएं compare होती है: (a, b) पहले a, फिर b से sort
```

---

## 🟡 Real World Example
Swiggy lists restaurants by rating (high to low), then by delivery time (low to high). A Razorpay dashboard shows the latest payments first by sorting on `created_at`. A leaderboard sorts users by score descending and name ascending for ties. A search results page sorts case-insensitively with `key=str.lower`.

## 🟡 Real Example Hindi mein
Swiggy restaurants को rating (ज्यादा से कम) और फिर delivery time (कम से ज्यादा) से sort करता है। Razorpay dashboard `created_at` पर sort करके नए payments पहले दिखाता है। Leaderboard score घटते क्रम में और बराबर score पर नाम बढ़ते क्रम में sort करता है। Search results `key=str.lower` से case-insensitive sort होते हैं।

---

## 💻 Code Example — Basic
```python
# Basic sorted() and key
words: list[str] = ["banana", "Apple", "cherry", "fig"]    # sample data

print(sorted([3, 1, 2]))                           # default ascending order
print(sorted([3, 1, 2], reverse=True))             # descending order
print(sorted(words))                               # uppercase sorts before lowercase
print(sorted(words, key=str.lower))                # case-insensitive
print(sorted(words, key=len))                      # by length; ties keep original order

nums: list[int] = [5, 2, 9]                        # a list we want to keep unchanged
result: list[int] = sorted(nums)                   # returns a NEW list
print(nums, result)                                # original untouched

other: list[int] = [5, 2, 9]                       # another list
print(other.sort())                                # .sort() sorts in place, returns None
print(other)                                       # now sorted

pairs: list[tuple[str, int]] = [("a", 3), ("b", 1), ("c", 2)]   # name, score
print(sorted(pairs, key=lambda p: p[1]))           # by score using lambda
print(sorted({"x": 2, "y": 1}))                    # sorting a dict gives sorted KEYS

# Output:
# [1, 2, 3]
# [3, 2, 1]
# ['Apple', 'banana', 'cherry', 'fig']
# ['Apple', 'banana', 'cherry', 'fig']
# ['fig', 'Apple', 'banana', 'cherry']
# [5, 2, 9] [2, 5, 9]
# None
# [2, 5, 9]
# [('b', 1), ('c', 2), ('a', 3)]
# ['x', 'y']
```

## 💻 Code Example — Advanced
```python
# Production style: multi-level sort, itemgetter, null-safe keys, top-N
from dataclasses import dataclass                  # record type
from operator import attrgetter, itemgetter        # fast key functions
from typing import Optional                        # for nullable fields


@dataclass
class Restaurant:
    name: str                                      # display name
    rating: float                                  # 0-5
    eta: Optional[int]                             # delivery minutes, may be unknown


shops: list[Restaurant] = [
    Restaurant("Biryani House", 4.5, 30),
    Restaurant("Pizza Hub", 4.5, 20),
    Restaurant("Dosa Corner", 4.8, None),
    Restaurant("Chai Point", 4.0, 10),
]

# 1) multi-level with a tuple key: rating DESC (negate), eta ASC
by_rating = sorted(shops, key=lambda r: (-r.rating, r.eta if r.eta is not None else 10**9))
print([r.name for r in by_rating])                 # unknown eta goes last

# 2) attrgetter is faster than a lambda and reads clearly
print([r.name for r in sorted(shops, key=attrgetter("name"))])   # alphabetical

# 3) stable multi-pass: sort by the minor key first, then the major key
step1 = sorted(shops, key=lambda r: r.name)        # minor: name ascending
step2 = sorted(step1, key=attrgetter("rating"), reverse=True)    # major: rating descending
print([r.name for r in step2])                     # ties stay name-sorted (stability)

# 4) dict records with itemgetter
rows: list[dict[str, int]] = [{"id": 3, "qty": 5}, {"id": 1, "qty": 5}, {"id": 2, "qty": 9}]
print(sorted(rows, key=itemgetter("qty", "id")))   # qty then id

# 5) top-N without sorting everything: heapq.nlargest uses the same key idea
import heapq                                       # standard heap module
print([r.name for r in heapq.nlargest(2, shops, key=attrgetter("rating"))])

# 6) natural sort: "file10" after "file2"
def natural_key(s: str) -> tuple[str, int]:
    """Split trailing digits so numbers compare as numbers."""
    head = s.rstrip("0123456789")                  # text part
    tail = s[len(head):]                           # digits part
    return head, int(tail) if tail else 0          # tuple compares text, then number


print(sorted(["file10", "file2", "file1"], key=natural_key))

# Output:
# ['Dosa Corner', 'Pizza Hub', 'Biryani House', 'Chai Point']
# ['Biryani House', 'Chai Point', 'Dosa Corner', 'Pizza Hub']
# ['Dosa Corner', 'Biryani House', 'Pizza Hub', 'Chai Point']
# [{'id': 1, 'qty': 5}, {'id': 3, 'qty': 5}, {'id': 2, 'qty': 9}]
# ['Dosa Corner', 'Biryani House']
# ['file1', 'file2', 'file10']
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Returns | new list (`sorted`) or in place (`.sort()`) | in place (`arr.sort`); `toSorted()` is new (ES2023) |
| Custom rule | `key=func` (one value per item) | comparator `(a, b) => a - b` |
| Default order | natural order of types | converts to STRING first |
| Stable | always | stable since ES2019 |
| Descending | `reverse=True` | swap `b - a` |

```python
# Python way
nums = [10, 9, 1]                                  # numbers
print(sorted(nums))                                # [1, 9, 10]
print(sorted(["bb", "a"], key=len))                # ['a', 'bb']
```
```javascript
// JavaScript way
const nums = [10, 9, 1];                           // numbers
console.log([...nums].sort());                     // [1, 10, 9]  <- string sort bug!
console.log([...nums].sort((a, b) => a - b));      // [1, 9, 10]  <- need a comparator
console.log(["bb", "a"].sort((a, b) => a.length - b.length));
```

Key difference: JS default `.sort()` compares as strings (a famous trap), and you write two-argument comparators. Python sorts numbers correctly by default and you give a one-argument `key`.

---

## 🟠 FastAPI Connection
Most list endpoints support `?sort=price&order=desc`. When data is already in memory (cached or small), `sorted(..., key=...)` implements it. For big tables, sort in SQL with `ORDER BY` instead. Always whitelist the allowed sort fields.

```python
# FastAPI example — sortable list endpoint with a whitelist
from fastapi import FastAPI, HTTPException         # app and errors
from operator import itemgetter                    # fast key getter

app: FastAPI = FastAPI()                           # create app
PRODUCTS: list[dict[str, int | str]] = [           # pretend DB
    {"name": "pen", "price": 10}, {"name": "book", "price": 99}, {"name": "bag", "price": 50},
]


@app.get("/products")                              # GET /products?sort=price&desc=true
def list_products(sort: str = "name", desc: bool = False) -> list[dict[str, int | str]]:
    if sort not in {"name", "price"}:              # never sort by unknown fields
        raise HTTPException(status_code=400, detail="sort must be name or price")
    return sorted(PRODUCTS, key=itemgetter(sort), reverse=desc)   # apply the rule
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting `.sort()` to return the list
✅ Correct: `.sort()` returns `None`; use `sorted()` for a value

```python
nums = [3, 1, 2]
# Wrong
result = nums.sort()
print(result)                      # None
# Right
result = sorted(nums)
print(result)                      # [1, 2, 3]
```

❌ Mistake 2: Passing a comparison function as `key`
✅ Correct: `key` takes ONE argument; use `functools.cmp_to_key` for comparators

```python
from functools import cmp_to_key
# Wrong
# sorted([3, 1], key=lambda a, b: a - b)   # TypeError: missing 1 required positional argument
# Right
print(sorted([3, 1, 2], key=cmp_to_key(lambda a, b: b - a)))   # [3, 2, 1]
```

❌ Mistake 3: Mixing types / None in the data
✅ Correct: make the key return comparable values

```python
data = [3, None, 1]
# Wrong
# sorted(data)       # TypeError: '<' not supported between 'NoneType' and 'int'
# Right
print(sorted(data, key=lambda x: (x is None, x or 0)))   # [1, 3, None]
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
words = ["bb", "a", "cc", "d"]
print(sorted(words, key=len, reverse=True))
print(sorted(words, key=lambda w: -len(w)))
print(sorted("hello"))
print(sorted([(1, "b"), (1, "a"), (0, "z")]))
```
Answer: `['bb', 'cc', 'a', 'd']` for both of the first two lines. With `reverse=True`, equal items still keep their ORIGINAL order (stability is preserved), so `bb` comes before `cc` and `a` before `d`. `sorted("hello")` returns a list of characters: `['e', 'h', 'l', 'l', 'o']`. The last line is `[(0, 'z'), (1, 'a'), (1, 'b')]` because tuples compare left to right.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `sorted()` and `list.sort()`?
A1: `sorted()` works on any iterable and returns a new list. `list.sort()` works only on lists, sorts in place and returns `None`. In-place saves memory; `sorted` keeps the original.

Q2: What algorithm does Python use and what is its complexity?
A2: Timsort (merge sort + insertion sort hybrid). O(n log n) worst case, O(n) for already-sorted data, and it is stable. It needs up to O(n) extra memory.

Q3: What does "stable" mean and why does it matter?
A3: Items with equal keys keep their original relative order. This allows multi-column sorts: sort by the secondary key first, then by the primary key.

Q4: How do you sort descending by one field and ascending by another?
A4: Negate numeric fields in a tuple key: `key=lambda r: (-r.score, r.name)`. For strings, do two stable passes (name ascending first, then score with `reverse=True`).

Q5: How many times is the key function called?
A5: Exactly once per item (the results are cached during the sort). That is why `key` is faster than the old `cmp` approach, which was called for every comparison.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need a sorted copy and want to keep the original
- Sorting records by one or more fields
- Case-insensitive or natural ordering
- Sorting any iterable (dict keys, sets, generators)

❌ Avoid when:
- You need only the top K of a big dataset (`heapq.nlargest`)
- The data lives in a database (use `ORDER BY` with an index)
- The list is already sorted and you only insert (use `bisect.insort`)

---

## 📊 Visual Diagram
```
items:   "bb"   "a"   "ccc"
key=len:   2     1      3        <- key called once per item
sort keys:       1  <  2  <  3
result:  "a"   "bb"  "ccc"

multi-level key (-rating, eta):
  Dosa   (-4.8, inf)
  Pizza  (-4.5, 20 )   <- smaller tuple comes first
  Biryani(-4.5, 30 )
  Chai   (-4.0, 10 )
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| key | Function giving the comparison value | Compare की value देने वाला function |
| Stable sort | Equal items keep order | बराबर items का order नहीं बदलता |
| Timsort | Python's sorting algorithm | Python का sorting algorithm |
| In-place | Modify the same list | उसी list में बदलाव |
| itemgetter | Fast key for dict/tuple | dict/tuple के लिए तेज key |
| cmp_to_key | Convert old comparator | पुराने comparator को key में बदलना |

---

## ⚡ 3-Line Summary
English: `sorted(it, key=f, reverse=...)` returns a new stable-sorted list using `f(item)` as the comparison value. Use tuple keys for multi-level sorts and `itemgetter`/`attrgetter` for speed. `.sort()` is in place and returns `None`.
Hindi: `sorted(it, key=f, reverse=...)` `f(item)` की value से नई stable sorted list देता है। Multi-level sort के लिए tuple key और speed के लिए `itemgetter`/`attrgetter` use करें। `.sort()` उसी list में sort करता है और `None` लौटाता है।

---

## ➡️ Next Topic
**122. List Comprehension vs map/filter** — which style is faster, clearer and more Pythonic.
