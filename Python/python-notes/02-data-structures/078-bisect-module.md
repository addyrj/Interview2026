---

# 078. bisect Module
# हिंदी में: bisect Module (Sorted List में Binary Search)

---

## 🔵 Simple Definition (English)
`bisect` does binary search on a list that is already sorted. It tells you WHERE a value belongs (`bisect_left`, `bisect_right`) and can insert it there while keeping the list sorted (`insort`). Finding the position takes O(log n) instead of O(n).

## 🔵 सरल परिभाषा (Hindi)
`bisect` पहले से sorted list पर binary search करता है। यह बताता है कि value कहाँ फिट होगी (`bisect_left`, `bisect_right`) और उसे सही जगह insert करके list को sorted रखता है (`insort`)। Position ढूँढने में O(log n) लगता है, O(n) नहीं।

---

## 🔴 Problem it Solves
Searching a sorted list with `in` or `index()` checks items one by one — O(n). Inserting a new value and calling `sort()` again is O(n log n). Writing binary search by hand is famous for off-by-one bugs. `bisect` gives a tested, C-speed implementation. It also solves "which range/slab does this number fall in?" problems cleanly, replacing long if/elif chains.

## 🔴 यह क्यों बना? (Hindi)
Sorted list में `in` या `index()` से search करना item-by-item होता है — O(n)। नई value डालकर फिर `sort()` करना O(n log n) है। हाथ से binary search लिखने में off-by-one bugs आम हैं। `bisect` tested और तेज (C speed) implementation देता है। "यह number किस range/slab में आता है?" जैसे सवाल भी लंबे if/elif की जगह साफ तरीके से हल होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Input list MUST already be sorted (bisect does not check)
Step 2 → Look at the middle item and compare with the target
Step 3 → Target smaller -> keep left half; larger -> keep right half
Step 4 → Repeat until the range is empty -> that is the insertion point
Step 5 → bisect_left: position BEFORE equal items; bisect_right: AFTER them
Step 6 → insort = find position + list.insert (insert itself is O(n))

a = [10, 20, 20, 30]
bisect_left(a, 20)  -> 1   (before the 20s)
bisect_right(a, 20) -> 3   (after the 20s)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Input list पहले से sorted होनी चाहिए (bisect check नहीं करता)
Step 2 → बीच का item देखो और target से compare करो
Step 3 → Target छोटा -> बायाँ आधा रखो; बड़ा -> दायाँ आधा
Step 4 → तब तक दोहराओ जब तक range खाली न हो -> वही insertion point है
Step 5 → bisect_left: बराबर items से पहले; bisect_right: उनके बाद
Step 6 → insort = position ढूँढना + list.insert (insert खुद O(n) है)
```

---

## 🟡 Real World Example
A Razorpay-style pricing engine has slabs: 0% fee below Rs 1000, 1% up to 5000, 1.5% up to 20000, 2% above. Instead of if/elif, `bisect` maps the amount to a rate in one line. A school app converts marks to grades (A/B/C) with bisect. A log service keeps timestamps sorted and uses bisect to count events between two times.

## 🟡 Real Example Hindi mein
Razorpay जैसे pricing engine में slabs होते हैं: Rs 1000 से कम पर 0% fee, 5000 तक 1%, 20000 तक 1.5%, उसके ऊपर 2%। if/elif की जगह `bisect` amount को एक line में rate से जोड़ देता है। School app marks को grade (A/B/C) में `bisect` से बदलती है। Log service timestamps sorted रखती है और दो समय के बीच events गिनने के लिए bisect इस्तेमाल करती है।

---

## 💻 Code Example — Basic
```python
# Basic bisect examples
import bisect                                       # binary search helpers

a: list[int] = [10, 20, 20, 30]                     # sorted list with a duplicate
print(bisect.bisect_left(a, 20), bisect.bisect_right(a, 20), bisect.bisect(a, 25))   # 1 3 3
bisect.insort(a, 25)                                # insert 25 and stay sorted
print(a)                                            # [10, 20, 20, 25, 30]
bisect.insort_left(a, 20)                           # insert 20 before existing 20s
print(a)                                            # [10, 20, 20, 20, 25, 30]
print(bisect.bisect_left(a, 5), bisect.bisect_left(a, 99))   # before all, after all


def grade(score: int) -> str:
    cuts: list[int] = [60, 70, 80, 90]              # grade boundaries
    return "FDCBA"[bisect.bisect(cuts, score)]      # index picks the letter


print([grade(s) for s in (55, 60, 75, 90, 100)])    # grades for sample scores

# Output:
# 1 3 3
# [10, 20, 20, 25, 30]
# [10, 20, 20, 20, 25, 30]
# 0 6
# ['F', 'D', 'C', 'A', 'A']
```

## 💻 Code Example — Advanced
```python
# Production style: membership, range count, floor lookup, slabs, key= (Python 3.10+)
import bisect                                       # binary search helpers
from typing import Optional                         # for "value or None"


def contains(sorted_list: list[int], x: int) -> bool:
    """O(log n) membership test on a sorted list."""
    i: int = bisect.bisect_left(sorted_list, x)     # candidate position
    return i < len(sorted_list) and sorted_list[i] == x   # check bounds, then value


def count_in_range(sorted_list: list[int], lo: int, hi: int) -> int:
    """Count items with lo <= item <= hi."""
    return bisect.bisect_right(sorted_list, hi) - bisect.bisect_left(sorted_list, lo)


def floor_value(sorted_list: list[int], x: int) -> Optional[int]:
    """Largest item <= x, or None if there is no such item."""
    i: int = bisect.bisect_right(sorted_list, x)    # items <= x are before i
    return sorted_list[i - 1] if i else None        # i == 0 means none qualify


def rate_slab(amount: int) -> float:
    """Fee percent for a payment amount."""
    limits: list[int] = [1000, 5000, 20000]         # slab upper edges
    rates: list[float] = [0.0, 1.0, 1.5, 2.0]       # one more rate than limits
    return rates[bisect.bisect_right(limits, amount)]   # edge value goes to next slab


data: list[int] = [1, 3, 5, 7, 9, 11]               # sorted input
print(contains(data, 7), contains(data, 8))         # True False
print(count_in_range(data, 3, 9))                   # 3, 5, 7, 9 -> 4
print(floor_value(data, 6), floor_value(data, 0))   # 5 None
print([rate_slab(a) for a in (500, 1000, 4999, 5000, 25000)])   # slab lookups

records: list[tuple[str, int]] = [("amit", 30), ("neha", 25), ("ravi", 35)]   # (name, age)
records.sort(key=lambda r: r[1])                    # sort by age first
print(bisect.bisect_left(records, 30, key=lambda r: r[1]))   # search by age -> index 1
bisect.insort(records, ("zoya", 28), key=lambda r: r[1])     # insert keeping age order
print(records)                                      # zoya sits between neha and amit

# Output:
# True False
# 4
# 5 None
# [0.0, 1.0, 1.0, 1.5, 2.0]
# 1
# [('neha', 25), ('zoya', 28), ('amit', 30), ('ravi', 35)]
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Binary search | `bisect.bisect_left` | write it yourself |
| Insert into sorted | `bisect.insort` | find index + `splice` |
| Linear search | `x in list` | `arr.includes(x)` |
| Sorted check | not done (your job) | not done |

```python
# Python way — one call
import bisect                                    # stdlib
nums: list[int] = [1, 3, 5, 7]                   # sorted
print(bisect.bisect_left(nums, 5))               # 2
bisect.insort(nums, 4)                           # keeps sorted
print(nums)                                      # [1, 3, 4, 5, 7]
```
```javascript
// JavaScript way — hand written binary search
const nums = [1, 3, 5, 7];                       // sorted
function lowerBound(arr, x) {                    // you must write this
  let lo = 0, hi = arr.length;                   // search window
  while (lo < hi) {                              // until window is empty
    const mid = (lo + hi) >> 1;                  // middle index
    if (arr[mid] < x) lo = mid + 1; else hi = mid;   // shrink window
  }
  return lo;                                     // insertion point
}
console.log(lowerBound(nums, 5));                // 2
nums.splice(lowerBound(nums, 4), 0, 4);          // insert at position
console.log(nums);                               // [1, 3, 4, 5, 7]
```

Key difference: JavaScript has no built-in binary search. In Python it is a one-line import. JS's `Array.sort()` also sorts as strings by default, a trap Python does not have.

---

## 🟠 FastAPI Connection
FastAPI services use `bisect` for rate/price slabs, finding the correct version in a sorted list of releases, and range queries on sorted timestamps (for example "events in the last hour") held in memory.

```python
# FastAPI example — fee slab lookup endpoint
import bisect                                    # binary search
from fastapi import FastAPI, Query               # FastAPI + validation

app: FastAPI = FastAPI()                         # create app
LIMITS: list[int] = [1000, 5000, 20000]          # slab edges (sorted!)
RATES: list[float] = [0.0, 1.0, 1.5, 2.0]        # percent for each slab


@app.get("/fee")                                 # GET /fee?amount=6000
def get_fee(amount: int = Query(..., ge=0)) -> dict[str, float]:
    rate: float = RATES[bisect.bisect_right(LIMITS, amount)]   # O(log n) slab lookup
    return {"rate_percent": rate, "fee": amount * rate / 100}  # compute fee
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using bisect on an unsorted list
✅ Correct: sort first (or keep the list sorted always)

```python
import bisect
# Wrong — no error, but the answer is garbage
print(bisect.bisect_left([30, 10, 20], 20))   # 2 — wrong, 20 is at index 1 after sorting
# Right
print(bisect.bisect_left(sorted([30, 10, 20]), 20))   # 1 — correct (list is [10,20,30])
```

❌ Mistake 2: Thinking `bisect_left` returns the item or -1
✅ Correct: it returns an insertion POINT; check the value yourself

```python
import bisect
a = [1, 3, 5]
i = bisect.bisect_left(a, 4)        # 2 — position where 4 would go
# Wrong: assuming a[i] == 4
# Right:
found = i < len(a) and a[i] == 4    # False
```

❌ Mistake 3: Using `insort` for millions of inserts
✅ Correct: `insort` is O(n) per insert (items shift); use `heapq`, or collect and `sort()` once

```python
import bisect
# Wrong for huge data — each insort shifts many items
# for x in million_values: bisect.insort(lst, x)
# Right
values = [5, 2, 9]
values.sort()          # one sort at the end, O(n log n)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import bisect
a = [1, 2, 2, 2, 3]
print(bisect.bisect_left(a, 2), bisect.bisect_right(a, 2))
print(bisect.bisect_right(a, 2) - bisect.bisect_left(a, 2))
print(bisect.bisect([1, 3], 3))
```
Answer: `1 4`, then `3`, then `2`. `bisect_left` returns the first spot where 2 can go (index 1), `bisect_right` the spot after the last 2 (index 4). The difference is how many times 2 appears (3). `bisect` is an alias of `bisect_right`, so for an existing 3 in `[1, 3]` it returns 2 (after the 3), not 1.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `bisect_left` and `bisect_right`?
A1: Both give the insertion point for sorted order. With duplicates, `bisect_left` returns the position BEFORE equal items and `bisect_right` (same as `bisect`) returns the position AFTER them. For a value not in the list they return the same index.

Q2: What is the time complexity of `bisect` and `insort`?
A2: `bisect_*` is O(log n). `insort` is O(log n) to find the spot but O(n) to insert because the list shifts elements. Overall `insort` is O(n). A balanced tree or `sortedcontainers.SortedList` gives O(log n) inserts.

Q3: How do you check if a value exists using `bisect`?
A3: `i = bisect_left(a, x)`; the value exists if `i < len(a) and a[i] == x`. This is O(log n), versus `x in a` which is O(n) for lists.

Q4: How do you use `bisect` with objects or tuples?
A4: From Python 3.10, pass `key=`: `bisect_left(records, 30, key=lambda r: r[1])` (the key is applied to list items, not the search value). In older versions keep a parallel list of keys and search that.

Q5: Why use `bisect` for grade or tax slabs?
A5: Put the boundaries in a sorted list and the results in a parallel list (one longer). `results[bisect_right(bounds, value)]` replaces a long if/elif chain, is easy to change (data not code) and runs in O(log n).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The data is sorted and you need fast lookup
- Mapping a number to a slab, grade, or bucket
- Range counts on sorted timestamps or IDs
- Keeping a small list sorted while adding items

❌ Avoid when:
- The list is unsorted — results are wrong without error
- Very frequent inserts into a big list — use `sortedcontainers` or a heap
- Exact key lookup only — a `dict` or `set` is O(1)
- The list is tiny — plain `in` is fine

---

## 📊 Visual Diagram
```
a = [10, 20, 20, 30]
index: 0   1   2   3   4
       |10 |20 |20 |30 |
        ^   ^       ^   ^
        0   1       3   4        <- insertion points (the gaps)

bisect_left(a, 20)  -> 1  (gap before the first 20)
bisect_right(a, 20) -> 3  (gap after the last 20)
bisect_left(a, 25)  -> 3
bisect_left(a, 5)   -> 0   |   bisect_left(a, 99) -> 4

Binary search steps for 25:  mid=20 (<25, go right) -> mid=30 (>=25, go left) -> done
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Binary search | Halve the search range each step | हर step में range आधी करना |
| Insertion point | Index where a value would go | वह index जहाँ value डलेगी |
| bisect_left | Position before equal items | बराबर items से पहले की position |
| bisect_right | Position after equal items | बराबर items के बाद की position |
| insort | Insert and keep list sorted | Sorted रखते हुए insert करना |
| Slab | Value range with its own rate | Rate वाली value range |

---

## ⚡ 3-Line Summary
English: `bisect` does O(log n) binary search on an already sorted list and returns an insertion point, not a found item. `bisect_left` goes before duplicates, `bisect_right` after them, and `insort` inserts while keeping order. Great for slabs, grades and range counts, but the list must be sorted.
Hindi: `bisect` पहले से sorted list पर O(log n) binary search करता है और insertion point देता है, मिला हुआ item नहीं। `bisect_left` duplicates से पहले, `bisect_right` बाद में, और `insort` order रखते हुए insert करता है। Slabs, grades, range counts के लिए बढ़िया, पर list sorted होनी चाहिए।

---

## ➡️ Next Topic
**080. Choosing Right Data Structure** — list, tuple, set, dict, deque, heap, array: a decision guide to pick the right one in interviews and in production.
