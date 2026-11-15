---

# 463. Bubble Sort
# हिंदी में: Bubble Sort (बुलबुला क्रम)

Full runnable solution (early exit, pass counter, random tests vs `sorted`): `main.py`. Run: `python3 main.py`.

---

## 🔵 Simple Definition (English)
Bubble sort repeatedly compares neighbouring items and swaps them if they are in the wrong order. After each pass the largest remaining item "bubbles up" to its final place at the end.

## 🔵 सरल परिभाषा (Hindi)
Bubble sort पास-पास के items की बार-बार तुलना करता है और गलत क्रम में हों तो swap करता है। हर pass के बाद सबसे बड़ा बचा item बुलबुले की तरह अपनी अंतिम जगह (अंत) पर पहुँच जाता है।

---

## 🔴 Problem it Solves
It is not used in production. It exists to teach sorting basics: comparing, swapping, passes, stability and Big-O. Interviewers ask it to check that you can explain O(n^2), the early-exit optimisation and why `list.sort()` is better.

## 🔴 यह क्यों बना? (Hindi)
Production में इसका इस्तेमाल नहीं होता। यह sorting की बुनियाद सिखाता है: तुलना, swap, pass, stability और Big-O। Interview में पूछा जाता है ताकि आप O(n^2), early-exit optimisation और `list.sort()` की श्रेष्ठता समझा सकें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pass over the list, compare arr[i] and arr[i+1]
Step 2 → If arr[i] > arr[i+1], swap them
Step 3 → After pass 1 the largest item is at the end
Step 4 → Repeat on the shorter unsorted part
Step 5 → If a whole pass makes no swap, the list is sorted, stop early
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → list पर pass चलाओ, arr[i] और arr[i+1] की तुलना
Step 2 → arr[i] बड़ा हो तो swap
Step 3 → पहले pass के बाद सबसे बड़ा item अंत में
Step 4 → बचे हुए छोटे हिस्से पर दोहराओ
Step 5 → किसी pass में कोई swap न हो तो list sorted है, रुक जाओ
```

---

## 🟡 Real World Example
A teacher sorts 8 student marks on a whiteboard by swapping neighbours. For a FastAPI endpoint sorting 1 million orders, bubble sort would take about 10^12 steps, so production code always uses `sorted()` (Timsort, O(n log n)).

## 🟡 Real Example Hindi mein
Teacher whiteboard पर 8 students के marks पास-पास swap करके sort करती है। FastAPI endpoint में 10 लाख orders के लिए bubble sort में करीब 10^12 steps लगते, इसलिए production में हमेशा `sorted()` (Timsort, O(n log n)) चलता है।

---

## 💻 Code Example — Basic
```python
# Basic bubble sort, every line commented
def bubble_sort(items: list[int]) -> list[int]:  # returns a sorted copy
    arr: list[int] = list(items)  # copy so the input is not changed
    n: int = len(arr)  # number of items
    for end in range(n - 1, 0, -1):  # last unsorted index shrinks each pass
        for i in range(end):  # compare neighbours up to `end`
            if arr[i] > arr[i + 1]:  # wrong order
                arr[i], arr[i + 1] = arr[i + 1], arr[i]  # swap in one line
    return arr  # sorted copy


print(bubble_sort([5, 1, 4, 2, 8]))  # unsorted input
# Output: [1, 2, 4, 5, 8]
print(bubble_sort([3, 3, 1]))  # duplicates
# Output: [1, 3, 3]
print(bubble_sort([]))  # empty
# Output: []
```

## 💻 Code Example — Advanced
```python
# Production style: early exit, generic key, and counting work done
from typing import Callable, List, Tuple, TypeVar  # type hints

T = TypeVar("T")  # element type


def bubble_sort_counted(
    items: List[T], key: Callable[[T], object] = lambda x: x
) -> Tuple[List[T], int, int]:
    """Return (sorted copy, passes, swaps). Stable, O(1) extra space."""
    arr: List[T] = list(items)  # copy
    passes: int = 0  # how many passes ran
    swaps: int = 0  # how many swaps happened
    for end in range(len(arr) - 1, 0, -1):  # shrinking window
        passes += 1  # one more pass
        swapped: bool = False  # did this pass change anything?
        for i in range(end):  # compare neighbours
            if key(arr[i]) > key(arr[i + 1]):  # strict > keeps equal items in order (stable)
                arr[i], arr[i + 1] = arr[i + 1], arr[i]  # swap
                swaps += 1  # count it
                swapped = True  # remember
        if not swapped:  # nothing moved: already sorted
            break  # early exit
    return arr, passes, swaps  # result and stats


print(bubble_sort_counted([1, 2, 3, 4, 5]))  # already sorted: best case
# Output: ([1, 2, 3, 4, 5], 1, 0)
print(bubble_sort_counted([5, 4, 3, 2, 1]))  # reversed: worst case
# Output: ([1, 2, 3, 4, 5], 4, 10)

rows = [("b", 2), ("a", 1), ("c", 2), ("d", 1)]  # (name, score)
sorted_rows, _, _ = bubble_sort_counted(rows, key=lambda r: r[1])  # sort by score only
print(sorted_rows)  # equal scores keep original order
# Output: [('a', 1), ('d', 1), ('b', 2), ('c', 2)]
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: swap with tuple unpacking, built-in sort
arr[i], arr[i + 1] = arr[i + 1], arr[i]
arr.sort()                 # in place, Timsort
sorted(arr, reverse=True)  # new list
```

```javascript
// JavaScript: swap needs destructuring or a temp variable
[arr[i], arr[i + 1]] = [arr[i + 1], arr[i]];
arr.sort();                 // WARNING: sorts as STRINGS by default!
arr.sort((a, b) => a - b);  // numeric sort needs a comparator
```

Key difference: JS `[10, 9, 1].sort()` gives `[1, 10, 9]` (string order). Python sorts numbers numerically by default.

---

## 🟠 FastAPI Connection
Never hand-write a sort in an endpoint. Use `sorted()` with a `key`, and validate the sort field.

```python
# FastAPI: sorted endpoint (pip install fastapi)
from typing import Literal  # restrict allowed values
from fastapi import FastAPI  # app

app: FastAPI = FastAPI()  # create app
ORDERS: list[dict[str, int]] = [{"id": 1, "amount": 500}, {"id": 2, "amount": 120}]  # fake data


@app.get("/orders")  # GET /orders?sort_by=amount
def orders(sort_by: Literal["id", "amount"] = "id") -> list[dict[str, int]]:
    return sorted(ORDERS, key=lambda o: o[sort_by])  # O(n log n), stable
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No early exit
```python
# Wrong - always does n*(n-1)/2 comparisons, even on sorted input

# Correct - track `swapped` and break when a pass makes no swap
```

❌ Mistake 2: Comparing beyond the unsorted part
```python
# Wrong - IndexError at arr[i + 1]:
# for i in range(len(arr)): ... arr[i + 1]

# Correct - for i in range(end) where end <= len(arr) - 1
```

❌ Mistake 3: Using `>=` and breaking stability
```python
# Wrong - swaps equal items, so their original order is lost:
# if arr[i] >= arr[i + 1]: swap

# Correct - use strict `>`
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
a = [3, 1, 2]
b = a.sort()
print(a, b)
c = sorted(a, reverse=True)
print(a, c)
```

**Answer**:
```
[1, 2, 3] None
[1, 2, 3] [3, 2, 1]
```
`list.sort()` sorts in place and returns `None`, so `b` is `None`. `sorted()` returns a new list and leaves the original alone. This is the most common sort bug in real code (`a = a.sort()` destroys the data).

---

## ⚫ Interview Questions + Answers

Q1: What is the time complexity?
A1: Worst and average O(n^2). Best case O(n) with the early-exit flag on sorted input.

Q2: Is it stable? In place?
A2: Yes, stable (with strict `>`) and in place with O(1) extra space.

Q3: Why is it rarely used?
A3: It does O(n^2) swaps and comparisons. Even insertion sort is faster on average.

Q4: What sort does Python use?
A4: Timsort: a hybrid of merge sort and insertion sort, O(n log n) worst case, O(n) on nearly sorted data, and stable.

Q5: How many passes does reversed `[5, 4, 3, 2, 1]` need?
A5: n - 1 = 4 passes and 10 swaps (see the advanced example).

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Teaching or interviews
- Tiny, almost-sorted lists where simplicity matters

❌ Avoid when:
- Real data of any size (use `sorted()` / `list.sort()`)
- You need O(n log n) guarantees (use merge sort or Timsort)

---

## 📊 Visual Diagram

```
[5, 1, 4, 2, 8]
pass 1: 5>1 swap [1,5,4,2,8] | 5>4 swap [1,4,5,2,8] | 5>2 swap [1,4,2,5,8] | 5<8 ok
        -> 8 is in place
pass 2: [1,4,2,5 | 8] -> 4>2 swap [1,2,4,5 | 8]
pass 3: no swap -> sorted, stop
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pass | One full scan of the list | एक पूरा चक्कर |
| Swap | Exchange two items | दो items की अदला-बदली |
| Stable | Equal items keep order | समान items का क्रम नहीं बदलता |
| In place | No big extra memory | बिना ज़्यादा extra memory |
| Timsort | Python's built-in sort | Python का built-in sort |

---

## ⚡ 3-Line Summary
English: Bubble sort swaps neighbours until the list is ordered. It is O(n^2), stable and in place, with an O(n) best case when you add an early exit. Use `sorted()` in real code.
Hindi: Bubble sort पास-पास के items swap करके list sort करता है। यह O(n^2), stable और in place है, early exit के साथ best case O(n)। असली code में `sorted()` इस्तेमाल करो।

---

## ➡️ Next Topic
**464. Quick Sort** — divide and conquer with a pivot, O(n log n) on average.
