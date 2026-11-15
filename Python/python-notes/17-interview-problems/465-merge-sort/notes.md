---

# 465. Merge Sort
# हिंदी में: Merge Sort (बाँटो, सॉर्ट करो, मिलाओ)

Full runnable solution (merge, merge_sort, inversion counting, tests): `main.py`. Run: `python3 main.py`.

---

## 🔵 Simple Definition (English)
Merge sort splits the list in half, sorts each half recursively, then merges the two sorted halves. It is always O(n log n) and it is stable.

## 🔵 सरल परिभाषा (Hindi)
Merge sort list को आधा-आधा बाँटता है, हर आधे को recursively sort करता है, फिर दो sorted हिस्सों को merge करता है। यह हमेशा O(n log n) है और stable है।

---

## 🔴 Problem it Solves
Quick sort can degrade to O(n^2). Merge sort guarantees O(n log n) in every case and keeps equal items in their original order. It also works well on linked lists and on data too big for memory (external sort), because it reads data sequentially.

## 🔴 यह क्यों बना? (Hindi)
Quick sort O(n^2) तक बिगड़ सकता है। Merge sort हर हाल में O(n log n) की गारंटी देता है और समान items का क्रम बनाए रखता है। यह linked list और memory से बड़े data (external sort) पर भी अच्छा है क्योंकि data क्रम से पढ़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Base case: length 0 or 1 is already sorted
Step 2 → Split at the middle: left half, right half
Step 3 → Sort the left half recursively
Step 4 → Sort the right half recursively
Step 5 → Merge the two sorted halves with two pointers (<= keeps stability)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → लंबाई 0 या 1 हो तो पहले से sorted
Step 2 → बीच से दो हिस्से: बायाँ और दायाँ
Step 3 → बाएँ हिस्से को recursively sort करो
Step 4 → दाएँ हिस्से को recursively sort करो
Step 5 → दोनों sorted हिस्सों को two pointers से merge करो (<= से stability बनी रहती है)
```

---

## 🟡 Real World Example
Sorting a 50 GB log file on a machine with 8 GB RAM: sort chunks, write them to disk, then merge them (external merge sort). Python's own `sorted()` (Timsort) is built on merge sort plus insertion sort. Databases use merge sort for `ORDER BY` on big tables.

## 🟡 Real Example Hindi mein
8 GB RAM वाली machine पर 50 GB की log file sort करना: chunks sort करके disk पर लिखो, फिर merge करो (external merge sort)। Python का `sorted()` (Timsort) भी merge sort और insertion sort पर बना है। Databases बड़ी tables के `ORDER BY` में merge sort इस्तेमाल करते हैं।

---

## 💻 Code Example — Basic
```python
# Basic merge sort, every line commented
def merge(left: list[int], right: list[int]) -> list[int]:  # merge two sorted lists
    out: list[int] = []  # result
    i: int = 0  # pointer in left
    j: int = 0  # pointer in right
    while i < len(left) and j < len(right):  # both have items
        if left[i] <= right[j]:  # <= keeps equal items in original order
            out.append(left[i])  # take from left
            i += 1  # advance left
        else:  # right is smaller
            out.append(right[j])  # take from right
            j += 1  # advance right
    out.extend(left[i:])  # leftover left items
    out.extend(right[j:])  # leftover right items
    return out  # merged list


def merge_sort(arr: list[int]) -> list[int]:  # returns a new sorted list
    if len(arr) <= 1:  # base case
        return list(arr)  # copy of 0 or 1 item
    mid: int = len(arr) // 2  # split point
    return merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))  # sort halves, then merge


print(merge_sort([38, 27, 43, 3, 9, 82, 10]))  # classic sample
# Output: [3, 9, 10, 27, 38, 43, 82]
print(merge_sort([]), merge_sort([7]))  # edges
# Output: [] [7]
```

## 💻 Code Example — Advanced
```python
# Production style: count inversions (how unsorted is the data?) + stability proof
from typing import List, Tuple  # type hints


def sort_and_count(a: List[int]) -> Tuple[List[int], int]:
    """Return (sorted list, number of inversions). O(n log n)."""
    if len(a) <= 1:  # base case
        return list(a), 0  # nothing out of order
    m: int = len(a) // 2  # middle
    left, x = sort_and_count(a[:m])  # sort left, count inside it
    right, y = sort_and_count(a[m:])  # sort right, count inside it
    out: List[int] = []  # merged result
    i = j = 0  # pointers
    count: int = x + y  # inversions found so far
    while i < len(left) and j < len(right):  # merge
        if left[i] <= right[j]:  # in order
            out.append(left[i]); i += 1  # take left
        else:  # right item jumps over all remaining left items
            out.append(right[j]); j += 1  # take right
            count += len(left) - i  # each remaining left item forms an inversion
    out += left[i:] + right[j:]  # leftovers
    return out, count  # result


print(sort_and_count([2, 4, 1, 3, 5]))  # inversions: (2,1) (4,1) (4,3)
# Output: ([1, 2, 3, 4, 5], 3)
print(sort_and_count([5, 4, 3, 2, 1])[1])  # fully reversed: n*(n-1)/2
# Output: 10
print(sort_and_count([1, 2, 3])[1])  # already sorted
# Output: 0

# Stability: Python's sorted() is stable, equal keys keep input order
pairs = [(1, "b"), (0, "x"), (1, "a")]  # (key, label)
print(sorted(pairs, key=lambda p: p[0]))  # (1,'b') stays before (1,'a')
# Output: [(0, 'x'), (1, 'b'), (1, 'a')]
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: slicing makes the split trivial
mid = len(arr) // 2
left, right = arr[:mid], arr[mid:]   # new lists (O(n) copy)
```

```javascript
// JavaScript
const mid = Math.floor(arr.length / 2);
const left = arr.slice(0, mid), right = arr.slice(mid);
```

Key difference: Both copy on slicing. In Python, `arr[:mid]` never fails for out-of-range indexes, and `list.sort()` / `sorted()` are guaranteed stable. JS `Array.prototype.sort` became guaranteed stable only in ES2019.

---

## 🟠 FastAPI Connection
`sorted()` (merge-sort based, stable) enables multi-field sorting: sort by the secondary key first, then by the primary key.

```python
# FastAPI: multi-level sort using stability (pip install fastapi)
from fastapi import FastAPI  # app

app: FastAPI = FastAPI()  # create app
USERS: list[dict[str, object]] = [
    {"name": "Asha", "city": "Pune", "age": 30},
    {"name": "Ravi", "city": "Delhi", "age": 25},
    {"name": "Sita", "city": "Pune", "age": 22},
]  # fake data


@app.get("/users")  # GET /users
def users() -> list[dict[str, object]]:
    step1 = sorted(USERS, key=lambda u: u["age"])  # secondary key first
    return sorted(step1, key=lambda u: u["city"])  # primary key last: city, then age inside each city
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `<` in merge
```python
# Wrong - equal items from the right half jump ahead, stability is lost:
# if left[i] < right[j]: take left

# Correct - use <=
```

❌ Mistake 2: Forgetting leftovers
```python
# Wrong - drops items when one half ends first:
# return out

# Correct - out.extend(left[i:]); out.extend(right[j:])
```

❌ Mistake 3: Slicing inside every recursive call on huge data
```python
# Wrong for very large lists - copies cost extra memory/time:
# merge_sort(arr[:mid])

# Better - pass index ranges (lo, hi) with one shared buffer, or just use sorted()
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
data = [("b", 2), ("a", 1), ("c", 2), ("d", 1)]
print(sorted(data, key=lambda t: t[1]))
print(sorted(data, key=lambda t: t[1], reverse=True))
```

**Answer**:
```
[('a', 1), ('d', 1), ('b', 2), ('c', 2)]
[('b', 2), ('c', 2), ('a', 1), ('d', 1)]
```
Python's sort is stable. Even with `reverse=True`, equal items keep their original relative order (`b` before `c`, `a` before `d`). `reverse=True` is not the same as reversing the stable result.

---

## ⚫ Interview Questions + Answers

Q1: Time and space complexity?
A1: O(n log n) in best, average and worst case. O(n) extra space for the merge buffers.

Q2: Why is it stable?
A2: When items are equal, the merge takes from the left half first (`<=`), keeping the original order.

Q3: Merge sort vs quick sort?
A3: Merge sort: guaranteed O(n log n), stable, extra space. Quick sort: in place, usually faster, worst case O(n^2), not stable.

Q4: What is an inversion?
A4: A pair `i < j` with `a[i] > a[j]`. Merge sort counts them in O(n log n); brute force is O(n^2).

Q5: Why is it good for linked lists?
A5: Merging relinks nodes with O(1) extra space, and it does not need random access.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You need stable sorting with guaranteed O(n log n)
- Sorting linked lists or huge files (external sort)
- Counting inversions

❌ Avoid when:
- Memory is very tight (use in-place heap sort or quick sort)
- In normal Python code (use `sorted()`)

---

## 📊 Visual Diagram

```
            [38, 27, 43, 3]
           /               \
     [38, 27]             [43, 3]
     /     \              /     \
   [38]   [27]         [43]     [3]
     \     /              \     /
     [27, 38]             [3, 43]
           \               /
           [3, 27, 38, 43]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Merge | Combine two sorted lists | दो sorted lists को मिलाना |
| Stable | Equal items keep order | समान items का क्रम सुरक्षित |
| Inversion | Pair that is out of order | उल्टे क्रम की जोड़ी |
| External sort | Sort data bigger than RAM | RAM से बड़े data की sorting |
| Timsort | Python's merge+insertion hybrid | Python का hybrid sort |

---

## ⚡ 3-Line Summary
English: Split in half, sort both halves, merge them. It is always O(n log n), stable, and needs O(n) extra space. Merge also counts inversions.
Hindi: आधा बाँटो, दोनों हिस्से sort करो, merge करो। हमेशा O(n log n), stable, और O(n) extra space। Merge से inversions भी गिने जा सकते हैं।

---

## ➡️ Next Topic
**466. Find Missing Number** — find the one missing value in 0..n using math and XOR.
