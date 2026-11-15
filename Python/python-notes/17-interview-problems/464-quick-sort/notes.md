---

# 464. Quick Sort
# हिंदी में: Quick Sort (Pivot से तेज़ sorting)

Full runnable solution (simple + in-place random-pivot version, tests): `main.py`. Run: `python3 main.py`.

---

## 🔵 Simple Definition (English)
Quick sort picks a pivot, puts smaller items on its left and bigger items on its right, then sorts each side the same way (recursion). Average time is O(n log n).

## 🔵 सरल परिभाषा (Hindi)
Quick sort एक pivot चुनता है, छोटे items उसके बाएँ और बड़े दाएँ रखता है, फिर दोनों तरफ यही प्रक्रिया दोहराता है (recursion)। Average time O(n log n)।

---

## 🔴 Problem it Solves
Bubble sort is O(n^2). Quick sort is much faster in practice, sorts in place with little extra memory and is cache friendly. It is the classic divide and conquer example and a favourite interview question.

## 🔴 यह क्यों बना? (Hindi)
Bubble sort O(n^2) है। Quick sort practice में बहुत तेज़ है, in place चलता है और cache के लिए अच्छा है। यह divide and conquer का क्लासिक उदाहरण है और interview में बहुत पूछा जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Base case: 0 or 1 items are already sorted
Step 2 → Choose a pivot (middle or random)
Step 3 → Partition: smaller | equal | larger
Step 4 → Recursively sort the smaller and larger parts
Step 5 → Join: sorted(smaller) + equal + sorted(larger)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → 0 या 1 item हो तो पहले से sorted
Step 2 → pivot चुनो (बीच का या random)
Step 3 → partition: छोटे | बराबर | बड़े
Step 4 → छोटे और बड़े हिस्से को recursively sort करो
Step 5 → जोड़ो: sorted(छोटे) + बराबर + sorted(बड़े)
```

---

## 🟡 Real World Example
Sorting a day's UPI transactions by amount before generating a report. C's `qsort` and many language runtimes use quick sort variants (introsort). Python's `sorted()` uses Timsort, but the pivot/partition idea also powers `quickselect`, which finds the median or top-k in O(n).

## 🟡 Real Example Hindi mein
दिन भर के UPI transactions को amount से sort करके report बनाना। C का `qsort` और कई runtimes quick sort के variants (introsort) इस्तेमाल करते हैं। Python का `sorted()` Timsort है, पर pivot/partition का idea `quickselect` में काम आता है जो median या top-k O(n) में निकालता है।

---

## 💻 Code Example — Basic
```python
# Basic readable quick sort (uses extra lists)
def quick_sort(arr: list[int]) -> list[int]:  # returns a new sorted list
    if len(arr) <= 1:  # base case
        return arr  # nothing to sort
    pivot: int = arr[len(arr) // 2]  # middle item as pivot
    left: list[int] = [x for x in arr if x < pivot]  # smaller than pivot
    mid: list[int] = [x for x in arr if x == pivot]  # equal to pivot (handles duplicates)
    right: list[int] = [x for x in arr if x > pivot]  # larger than pivot
    return quick_sort(left) + mid + quick_sort(right)  # sort sides and join


print(quick_sort([3, 6, 8, 10, 1, 2, 1]))  # classic sample
# Output: [1, 1, 2, 3, 6, 8, 10]
print(quick_sort([]))  # empty list
# Output: []
print(quick_sort([2, 2, 2]))  # all equal
# Output: [2, 2, 2]
```

## 💻 Code Example — Advanced
```python
# Production style: in-place Lomuto partition, random pivot, bounded recursion
import random  # random pivot avoids the sorted-input worst case
from typing import List  # type hints


def quick_sort(arr: List[int]) -> List[int]:
    """Sort a copy in place. Average O(n log n), worst O(n^2), O(log n) stack."""
    data: List[int] = list(arr)  # do not mutate the caller's list

    def partition(lo: int, hi: int) -> int:
        p: int = random.randint(lo, hi)  # random pivot index
        data[p], data[hi] = data[hi], data[p]  # move pivot to the end
        pivot: int = data[hi]  # pivot value
        store: int = lo  # boundary of the "< pivot" zone
        for i in range(lo, hi):  # scan the range
            if data[i] < pivot:  # belongs on the left
                data[i], data[store] = data[store], data[i]  # swap into the zone
                store += 1  # grow the zone
        data[store], data[hi] = data[hi], data[store]  # put pivot in final place
        return store  # pivot position

    def sort(lo: int, hi: int) -> None:
        while lo < hi:  # loop on the larger side
            p: int = partition(lo, hi)  # split
            if p - lo < hi - p:  # left side is smaller
                sort(lo, p - 1)  # recurse on the smaller side
                lo = p + 1  # iterate on the larger side
            else:  # right side is smaller
                sort(p + 1, hi)  # recurse on the smaller side
                hi = p - 1  # iterate on the larger side

    sort(0, len(data) - 1)  # start with the whole list
    return data  # sorted copy


original: List[int] = [9, 4, 7, 3, 10, 3]  # input
print(quick_sort(original))  # sorted copy
# Output: [3, 3, 4, 7, 9, 10]
print(original)  # input untouched
# Output: [9, 4, 7, 3, 10, 3]
print(quick_sort(list(range(3000))) == list(range(3000)))  # sorted input: random pivot keeps it fast
# Output: True
print(quick_sort([2] * 5000) == [2] * 5000)  # all duplicates do not blow the stack
# Output: True
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: comprehensions make the simple version 5 lines
def qs(a):
    if len(a) <= 1: return a
    p = a[len(a) // 2]
    return qs([x for x in a if x < p]) + [x for x in a if x == p] + qs([x for x in a if x > p])
```

```javascript
// JavaScript
const qs = (a) => {
  if (a.length <= 1) return a;
  const p = a[Math.floor(a.length / 2)];
  return [...qs(a.filter(x => x < p)), ...a.filter(x => x === p), ...qs(a.filter(x => x > p))];
};
```

Key difference: Python's default recursion limit is about 1000 (`sys.getrecursionlimit()`), so a naive recursive quick sort on a bad input can raise `RecursionError`. JS fails by stack size instead. Python has no tail-call optimisation either.

---

## 🟠 FastAPI Connection
You almost never code quick sort in an API, but the idea matters for "top-k" endpoints. Use `heapq.nlargest` instead of sorting everything.

```python
# FastAPI: top-k endpoint (pip install fastapi)
import heapq  # heap based top-k
from fastapi import FastAPI, Query  # app and validation

app: FastAPI = FastAPI()  # create app
SCORES: list[int] = [50, 91, 77, 13, 88, 64]  # fake data


@app.get("/top")  # GET /top?k=3
def top(k: int = Query(3, ge=1, le=100)) -> list[int]:
    return heapq.nlargest(k, SCORES)  # O(n log k), cheaper than a full sort
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Always taking the first item as pivot
```python
# Wrong - sorted input gives O(n^2) and deep recursion:
# pivot = arr[0]

# Correct - random or median-of-three pivot
```

❌ Mistake 2: Dropping duplicates
```python
# Wrong - items equal to pivot vanish:
# left = [x for x in arr if x < pivot]; right = [x for x in arr if x > pivot]
# return qs(left) + [pivot] + qs(right)

# Correct - keep a `mid` list of all equal items
```

❌ Mistake 3: Sorting with `sort()` and using the return value
```python
# Wrong:
# result = arr.sort()   # None

# Correct:
# result = sorted(arr)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
def qs(a):
    if len(a) <= 1:
        return a
    p = a[0]
    return qs([x for x in a[1:] if x < p]) + [p] + qs([x for x in a[1:] if x >= p])

print(qs([3, 1, 3, 2]))
import sys
try:
    qs(list(range(2000)))
except RecursionError:
    print("RecursionError")
```

**Answer**:
```
[1, 2, 3, 3]
RecursionError
```
The first pivot choice is correct for duplicates (`>=` keeps them). But the first element as pivot on already sorted input recurses 2000 levels deep, which crosses Python's default limit of 1000, so it raises `RecursionError`. A random pivot avoids this.

---

## ⚫ Interview Questions + Answers

Q1: Time complexity?
A1: Average O(n log n), worst O(n^2) when pivots are always the smallest or largest item.

Q2: Is it stable?
A2: The in-place version is not stable. The list-comprehension version keeps equal items together but is not guaranteed to be stable in general.

Q3: Space complexity?
A3: In-place with smaller-side recursion: O(log n) stack. The simple version: O(n) extra lists.

Q4: Quick sort vs merge sort?
A4: Merge sort is always O(n log n) and stable but needs O(n) extra space. Quick sort is in place and usually faster in practice but has a bad worst case.

Q5: What is quickselect?
A5: Partition like quick sort but recurse only into the side containing the k-th item. Average O(n).

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Learning divide and conquer
- Arrays in languages without a good built-in sort

❌ Avoid when:
- You are in Python production code (use `sorted()`)
- You need a stable sort (use merge sort or Timsort)
- Adversarial input is possible and you cannot randomise the pivot

---

## 📊 Visual Diagram

```
[3, 6, 8, 10, 1, 2, 1]   pivot = 10 (middle index 3)

 left  (<10): [3, 6, 8, 1, 2, 1]
 mid   (==10): [10]
 right (>10): []

 recurse on left ... -> [1, 1, 2, 3, 6, 8] + [10] + []
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pivot | Item used to split the list | बँटवारे का आधार item |
| Partition | Move smaller left, larger right | छोटे-बड़े को अलग करना |
| Divide and conquer | Solve smaller parts, then combine | बाँटो और जीतो |
| Quickselect | Find k-th item in O(n) average | k-वाँ item खोजना |
| Recursion limit | Max call depth (default 1000) | recursion की अधिकतम गहराई |

---

## ⚡ 3-Line Summary
English: Pick a pivot, partition into smaller, equal and larger, recurse on the sides. Average O(n log n), worst O(n^2). Use a random pivot and handle duplicates; in real Python use `sorted()`.
Hindi: Pivot चुनो, छोटे, बराबर और बड़े में बाँटो, दोनों तरफ recursion। Average O(n log n), worst O(n^2)। Random pivot लो और duplicates संभालो; असली Python में `sorted()` इस्तेमाल करो।

---

## ➡️ Next Topic
**465. Merge Sort** — a stable O(n log n) sort that always splits in the middle.
