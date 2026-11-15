---

# D089. Merge K Sorted Lists (heap)
# Category: DSA — Binary Search, Heap & Backtracking
# Difficulty: ⭐⭐⭐ Hard | LeetCode #23

---

## ❓ Problem
Given an array of `k` sorted linked lists, merge them into one sorted linked list and return its head.

```
Input:  lists = [1→4→5, 1→3→4, 2→6]
Output: 1 → 1 → 2 → 3 → 4 → 4 → 5 → 6
```

---

## 💡 Quick Concept (2 lines only)
Keep a min-heap with the current head of each list. Pop the smallest, append it to the result, and push that node's `next`.
हिंदी: हर list का पहला node heap में रखो, सबसे छोटा निकालो, result में जोड़ो और उसका next heap में डाल दो।

---

## ✅ Solution

```python
from __future__ import annotations  # allow ListNode self-reference in hints
import heapq  # min-heap
from dataclasses import dataclass  # compact node class


@dataclass
class ListNode:
    val: int  # value stored in node
    next: ListNode | None = None  # pointer to next node


def create_list(arr: list[int]) -> ListNode | None:
    dummy = ListNode(0)  # dummy head for easy building
    curr = dummy  # tail pointer
    for v in arr:  # for each value
        curr.next = ListNode(v)  # append new node
        curr = curr.next  # move tail
    return dummy.next  # real head (None if empty)


def to_string(head: ListNode | None) -> str:
    vals: list[str] = []  # collected values
    while head:  # walk the list
        vals.append(str(head.val))  # record value
        head = head.next  # advance
    return " → ".join(vals) if vals else "None"  # readable output


# ============================================
# APPROACH 1: Brute force — collect all, sort, rebuild — O(N log N)
# ============================================
def merge_brute(lists: list[ListNode | None]) -> ListNode | None:
    vals: list[int] = []  # every value from every list
    for head in lists:  # each list
        while head:  # walk it
            vals.append(head.val)  # collect value
            head = head.next  # advance
    return create_list(sorted(vals))  # sort and rebuild


# ============================================
# APPROACH 2: Min-heap — O(N log k) time, O(k) space ✅ PREFERRED
# ============================================
def merge_k_lists(lists: list[ListNode | None]) -> ListNode | None:
    heap: list[tuple[int, int, ListNode]] = []  # (value, list index, node)
    for i, head in enumerate(lists):  # seed heap with each list's head
        if head:  # skip empty lists
            heapq.heappush(heap, (head.val, i, head))  # index breaks ties (nodes aren't comparable)
    dummy = ListNode(0)  # dummy head of result
    tail = dummy  # tail pointer
    while heap:  # until all lists are consumed
        _, i, node = heapq.heappop(heap)  # smallest current node
        tail.next = node  # splice it in
        tail = node  # move tail
        if node.next:  # list still has nodes
            heapq.heappush(heap, (node.next.val, i, node.next))  # push its successor
    return dummy.next  # skip dummy


# ============================================
# APPROACH 3: Divide and conquer — pairwise merge, O(N log k), O(1) extra
# ============================================
def merge_two(a: ListNode | None, b: ListNode | None) -> ListNode | None:
    dummy = ListNode(0)  # dummy head
    tail = dummy  # tail pointer
    while a and b:  # both have nodes
        if a.val <= b.val:  # a is smaller
            tail.next, a = a, a.next  # attach a, advance a
        else:  # b is smaller
            tail.next, b = b, b.next  # attach b, advance b
        tail = tail.next  # move tail
    tail.next = a or b  # attach leftovers
    return dummy.next  # real head


def merge_divide(lists: list[ListNode | None]) -> ListNode | None:
    if not lists:  # nothing to merge
        return None  # empty result
    while len(lists) > 1:  # until one list remains
        merged = [  # merge neighbours pairwise
            merge_two(lists[i], lists[i + 1] if i + 1 < len(lists) else None)  # odd one pairs with None
            for i in range(0, len(lists), 2)  # step by 2
        ]
        lists = merged  # next round has half as many lists
    return lists[0]  # fully merged


# ============================================
# TEST CASES
# ============================================
def build() -> list[ListNode | None]:
    return [create_list([1, 4, 5]), create_list([1, 3, 4]), create_list([2, 6])]  # fresh lists each time


print(to_string(merge_brute(build())))     # 1 → 1 → 2 → 3 → 4 → 4 → 5 → 6
print(to_string(merge_k_lists(build())))   # 1 → 1 → 2 → 3 → 4 → 4 → 5 → 6
print(to_string(merge_divide(build())))    # 1 → 1 → 2 → 3 → 4 → 4 → 5 → 6
print(to_string(merge_k_lists([])))        # None
print(to_string(merge_k_lists([None])))    # None
print(to_string(merge_k_lists([None, create_list([0])])))  # 0
```

---

## 🔍 Why It Works
```
heap starts: (1,L0) (1,L1) (2,L2)
pop 1(L0) -> push 4  | pop 1(L1) -> push 3 | pop 2(L2) -> push 6
pop 3 -> push 4 | pop 4(L0) -> push 5 | pop 4(L1) | pop 5 | pop 6
Heap never holds more than k nodes -> each pop/push costs O(log k).
```
हिंदी: Heap में हमेशा सिर्फ k nodes होते हैं, इसलिए हर operation O(log k) है और कुल N nodes के लिए O(N log k)।

---

## 📊 Complexity
```
Brute force: Time O(N log N) | Space O(N)
Heap:        Time O(N log k) | Space O(k)   ← preferred
Divide&Conq: Time O(N log k) | Space O(1) extra (iterative)
N = total nodes, k = number of lists
```

---

## ⚡ Variations

```python
# VARIANT 1: Merge K sorted arrays — heap of (value, array index, element index)
# VARIANT 2: Smallest range covering elements from K lists — heap + track current max
# VARIANT 3: Sequential merge (merge into result one by one) — O(N*k), slower
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: pushing (node.val, node) -> equal values compare ListNode objects -> TypeError
# heapq.heappush(heap, (head.val, head))   # TypeError: '<' not supported between 'ListNode' and 'ListNode'

# ✅ Correct: add a unique tie-breaker: (node.val, i, node)
```

---

## 🎯 Interview Tip
Say: "Min-heap of size k gives O(N log k). I add the list index as a tie-breaker because nodes aren't comparable. Divide and conquer reaches the same time with O(1) extra space." 

---

## 🔗 Related Problems
→ D087 (Kth Largest Element) | D088 (Top K Frequent Elements) | D084 (Binary Search)
