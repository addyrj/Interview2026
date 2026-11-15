---

# 461. Merge Two Sorted Lists
# हिंदी में: दो Sorted Lists को मिलाना

Full runnable solution with asserts (linked list + plain lists + `heapq.merge`): `main.py`. Run: `python3 main.py`.

---

## 🔵 Simple Definition (English)
Take two already sorted sequences and produce one sorted sequence. Use two pointers and always take the smaller front item. It is O(n + m) time.

## 🔵 सरल परिभाषा (Hindi)
दो पहले से sorted sequences से एक sorted sequence बनानी है। दो pointers रखो और हमेशा छोटा front item लो। Time O(n + m) लगता है।

---

## 🔴 Problem it Solves
Concatenating and calling `sort()` costs O(n log n) and ignores the fact that both inputs are already sorted. Merging uses that order and needs only one pass. It is the core step of merge sort and of merging sorted database results or log files.

## 🔴 यह क्यों बना? (Hindi)
दोनों lists जोड़कर `sort()` करने में O(n log n) लगता है और यह तथ्य बेकार जाता है कि lists पहले से sorted हैं। Merge एक ही pass में काम करता है। यही merge sort का मुख्य step है और sorted DB results या log files मिलाने में भी काम आता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pointers i, j at the start of both lists
Step 2 → Compare a[i] and b[j]
Step 3 → Append the smaller one, move that pointer
Step 4 → Repeat until one list is finished
Step 5 → Append the rest of the other list (already sorted)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → दोनों lists की शुरुआत पर pointers i, j
Step 2 → a[i] और b[j] की तुलना
Step 3 → छोटा वाला output में डालो, उसका pointer आगे बढ़ाओ
Step 4 → जब तक एक list खत्म न हो, दोहराओ
Step 5 → दूसरी list का बचा हिस्सा जोड़ दो (वह पहले से sorted है)
```

---

## 🟡 Real World Example
Swiggy order feeds come from two regional databases, each sorted by time. The API merges them into one timeline with a two-pointer merge. In LeetCode, the same idea is applied to linked lists by relinking nodes with no new memory.

## 🟡 Real Example Hindi mein
Swiggy के order feeds दो regional databases से आते हैं, दोनों time से sorted। API दोनों को two-pointer merge से एक timeline में जोड़ती है। LeetCode में यही idea linked list पर nodes जोड़कर बिना नई memory के चलता है।

---

## 💻 Code Example — Basic
```python
# Basic two-pointer merge on plain lists
def merge(a: list[int], b: list[int]) -> list[int]:  # both inputs sorted
    i: int = 0  # pointer into a
    j: int = 0  # pointer into b
    out: list[int] = []  # result list
    while i < len(a) and j < len(b):  # both still have items
        if a[i] <= b[j]:  # <= keeps the merge stable
            out.append(a[i])  # take from a
            i += 1  # advance a
        else:  # b is smaller
            out.append(b[j])  # take from b
            j += 1  # advance b
    out.extend(a[i:])  # leftover of a (may be empty)
    out.extend(b[j:])  # leftover of b (may be empty)
    return out  # merged sorted list


print(merge([1, 2, 4], [1, 3, 4]))  # normal case
# Output: [1, 1, 2, 3, 4, 4]
print(merge([], [5, 6]))  # one list empty
# Output: [5, 6]
print(merge([1, 2], [7, 8]))  # no interleaving
# Output: [1, 2, 7, 8]
```

## 💻 Code Example — Advanced
```python
# Production style: linked list merge in O(1) extra space + stdlib heapq.merge
from __future__ import annotations  # node refers to itself
from dataclasses import dataclass  # small node class
from heapq import merge as heap_merge  # lazy k-way merge from stdlib
from typing import Iterator, List, Optional  # type hints


@dataclass
class ListNode:  # singly linked node
    val: int  # value
    next: Optional[ListNode] = None  # next node


def build(values: List[int]) -> Optional[ListNode]:  # helper
    dummy = ListNode(0)  # placeholder head
    tail = dummy  # last node
    for v in values:  # each value
        tail.next = ListNode(v)  # new node
        tail = tail.next  # advance
    return dummy.next  # real head


def to_list(head: Optional[ListNode]) -> List[int]:  # helper
    out: List[int] = []  # result
    while head:  # walk
        out.append(head.val)  # collect
        head = head.next  # advance
    return out  # list form


def merge_lists(a: Optional[ListNode], b: Optional[ListNode]) -> Optional[ListNode]:
    dummy = ListNode(0)  # dummy avoids head special-case
    tail = dummy  # last node of merged list
    while a and b:  # both have nodes
        if a.val <= b.val:  # stable
            tail.next, a = a, a.next  # relink node from a
        else:  # b smaller
            tail.next, b = b, b.next  # relink node from b
        tail = tail.next  # advance tail
    tail.next = a or b  # attach whichever list is left
    return dummy.next  # merged head


print(to_list(merge_lists(build([1, 2, 4]), build([1, 3, 4]))))  # linked merge
# Output: [1, 1, 2, 3, 4, 4]
print(to_list(merge_lists(None, build([0]))))  # one side None
# Output: [0]

lazy: Iterator[int] = heap_merge([1, 4, 9], [2, 3, 10], [0, 5])  # merges any number of sorted inputs lazily
print(list(lazy))  # consume the iterator
# Output: [0, 1, 2, 3, 4, 5, 9, 10]
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: tuple swap makes pointer moves short
i = j = 0
out = []
while i < len(a) and j < len(b):
    if a[i] <= b[j]:
        out.append(a[i]); i += 1
    else:
        out.append(b[j]); j += 1
out += a[i:] + b[j:]
```

```javascript
// JavaScript
let i = 0, j = 0;
const out = [];
while (i < a.length && j < b.length) {
  if (a[i] <= b[j]) out.push(a[i++]);
  else out.push(b[j++]);
}
return [...out, ...a.slice(i), ...b.slice(j)];
```

Key difference: Python has `heapq.merge` in the standard library, JS has no built-in merge. Also, `out += a[i:] + b[j:]` and slicing never raise errors when the start index is past the end.

---

## 🟠 FastAPI Connection
Merge two sorted result streams (for example from two shards) before returning a page.

```python
# FastAPI: merge two sorted shards (pip install fastapi)
from heapq import merge  # stdlib merge
from fastapi import FastAPI  # app

app: FastAPI = FastAPI()  # create app
SHARD_A: list[int] = [100, 105, 130]  # timestamps from shard A
SHARD_B: list[int] = [101, 120, 140]  # timestamps from shard B


@app.get("/timeline")  # GET /timeline
def timeline(limit: int = 4) -> list[int]:
    merged = merge(SHARD_A, SHARD_B)  # lazy, nothing computed yet
    return [x for _, x in zip(range(limit), merged)]  # take only `limit` items
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Concatenate and sort
```python
# Wrong - O(n log n), ignores sorted input:
result = sorted(a + b)

# Correct - O(n + m) two pointers or heapq.merge(a, b)
```

❌ Mistake 2: Forgetting the leftover items
```python
# Wrong - loses [7, 8] when a finishes first:
# while i < len(a) and j < len(b): ...
# return out

# Correct - out.extend(a[i:]); out.extend(b[j:])
```

❌ Mistake 3: Using `<` and breaking stability
```python
# Wrong - equal items from b come first:
# if a[i] < b[j]: take a  else: take b

# Correct - use <= so equal items from a stay first
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from heapq import merge

m = merge([1, 3], [2, 4])
print(list(m), list(m))
print(sorted([3, 1] + [2]) == list(merge([1, 3], [2])))
print(list(merge([3, 1], [2, 4])))
```

**Answer**:
```
[1, 2, 3, 4] []
True
[2, 3, 1, 4]
```
`merge` returns an iterator, so the second `list(m)` is empty. The result is correct only when each input is sorted. With the unsorted input `[3, 1]` the algorithm still runs but the output order is wrong.

---

## ⚫ Interview Questions + Answers

Q1: Time and space complexity?
A1: O(n + m) time. Plain list version uses O(n + m) space for the output. Linked list version uses O(1) extra space because it relinks nodes.

Q2: Why a dummy head node?
A2: It removes the special case for the first node, so the loop body is the same every time.

Q3: How do you merge k sorted lists?
A3: Use a min-heap of the k current heads (`heapq.merge`), O(N log k).

Q4: Is the merge stable?
A4: Yes when you use `<=` and take from the first list on ties.

Q5: When is `sorted(a + b)` acceptable?
A5: For small inputs. Python's Timsort detects the two sorted runs and merges them in about O(n) anyway, but the explicit merge is what the interviewer wants to see.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Both inputs are already sorted
- You merge sorted streams, files or shard results
- You implement merge sort

❌ Avoid when:
- Inputs are not sorted (sort first or use another method)
- The data is tiny and clarity matters more (just use `sorted`)

---

## 📊 Visual Diagram

```
a = [1, 2, 4]   b = [1, 3, 4]

i=0 j=0   1 <= 1  take a -> [1]
i=1 j=0   2 >  1  take b -> [1, 1]
i=1 j=1   2 <= 3  take a -> [1, 1, 2]
i=2 j=1   4 >  3  take b -> [1, 1, 2, 3]
i=2 j=2   4 <= 4  take a -> [1, 1, 2, 3, 4]
a done    append rest of b -> [1, 1, 2, 3, 4, 4]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Two pointers | Two indexes moving through data | दो pointers |
| Stable | Equal items keep their order | समान items का क्रम सुरक्षित |
| Dummy node | Fake head to simplify code | नकली head node |
| Linked list | Nodes joined by `next` | जुड़ी हुई nodes की list |
| k-way merge | Merge k sorted inputs | k sorted inputs का merge |

---

## ⚡ 3-Line Summary
English: Compare the front items of two sorted lists, take the smaller, and append the leftover at the end. It runs in O(n + m). For linked lists use a dummy node and relink nodes for O(1) space.
Hindi: दोनों sorted lists के front items की तुलना करो, छोटा लो और अंत में बचा हिस्सा जोड़ दो। Time O(n + m)। Linked list में dummy node और relinking से extra space O(1)।

---

## ➡️ Next Topic
**462. Binary Search** — find an item in a sorted list by halving the search window.
