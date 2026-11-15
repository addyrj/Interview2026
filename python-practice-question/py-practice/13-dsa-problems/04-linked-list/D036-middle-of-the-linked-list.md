---

# D036. Middle of the Linked List
# Category: DSA — Linked List
# Difficulty: ⭐ Easy | LeetCode #876

---

## ❓ Problem
Given the head of a singly linked list, return the middle node. If there are two middle nodes, return the **second** one.

```
Input:  1 → 2 → 3 → 4 → 5        Output: node 3  (3 → 4 → 5)
Input:  1 → 2 → 3 → 4 → 5 → 6    Output: node 4  (4 → 5 → 6)
```

---

## 💡 Quick Concept (2 lines only)
Slow moves 1 step, fast moves 2. When fast reaches the end, slow is at the middle.
हिंदी: Fast जब तक अंत पर पहुँचेगा, slow ठीक आधे रास्ते पर होगा क्योंकि fast दोगुनी रफ्तार से चलता है।

---

## ✅ Solution

```python
from __future__ import annotations             # allow ListNode self-reference in hints
from typing import Optional                    # for Optional[ListNode]


class ListNode:
    def __init__(self, val: int = 0, next: Optional[ListNode] = None) -> None:
        self.val = val                         # value stored in node
        self.next = next                       # pointer to next node


def create_list(arr: list[int]) -> Optional[ListNode]:
    dummy = ListNode()                         # dummy head simplifies building
    curr = dummy                               # tail pointer
    for v in arr:                              # go through each value
        curr.next = ListNode(v)                # append new node
        curr = curr.next                       # move tail forward
    return dummy.next                          # real head


def print_list(head: Optional[ListNode]) -> str:
    vals: list[str] = []                       # collect values as text
    while head:                                # walk the list
        vals.append(str(head.val))             # store current value
        head = head.next                       # advance
    return " → ".join(vals) if vals else "None"  # readable output


# ============================================
# APPROACH 1: Brute force — count nodes, then walk n//2 steps
# O(n) time (two passes), O(1) space
# ============================================
def middle_two_pass(head: Optional[ListNode]) -> Optional[ListNode]:
    n = 0                                      # node count
    node = head                                # walker
    while node:                                # first pass: count
        n += 1                                 # one more node
        node = node.next                       # advance
    node = head                                # restart
    for _ in range(n // 2):                    # second pass: n//2 steps = second middle
        node = node.next                       # advance
    return node                                # middle node


# ============================================
# APPROACH 2: Slow/fast pointers — O(n) time, O(1) space, one pass  PREFERRED
# ============================================
def middle_node(head: Optional[ListNode]) -> Optional[ListNode]:
    slow = fast = head                         # both start at head
    while fast and fast.next:                  # fast can still jump two nodes
        slow = slow.next                       # slow moves 1
        fast = fast.next.next                  # fast moves 2
    return slow                                # slow is the (second) middle


# ============================================
# TEST CASES
# ============================================
print(print_list(middle_two_pass(create_list([1, 2, 3, 4, 5]))))     # 3 → 4 → 5
print(print_list(middle_node(create_list([1, 2, 3, 4, 5]))))         # 3 → 4 → 5
print(print_list(middle_node(create_list([1, 2, 3, 4, 5, 6]))))      # 4 → 5 → 6
print(print_list(middle_node(create_list([1]))))                     # 1
print(print_list(middle_node(create_list([1, 2]))))                  # 2
print(print_list(middle_node(create_list([]))))                      # None
```

---

## 🔍 Why It Works
```
1 → 2 → 3 → 4 → 5
s,f=1
s=2 f=3
s=3 f=5   (f.next is None -> stop)  -> middle = 3

1 → 2 → 3 → 4
s=2 f=3 ; s=3 f=None (f is None -> stop) -> second middle = 3
```
हिंदी: Fast दोगुना चलता है, इसलिए जब वो खत्म हो, slow आधी दूरी तय कर चुका होता है।

---

## 📊 Complexity
```
Two pass:      Time O(n) | Space O(1)
Slow/fast:     Time O(n) | Space O(1)  <- preferred (single pass)
```

---

## ⚡ Variations

```python
# VARIANT 1: Return the FIRST middle on even length -> loop `while fast.next and fast.next.next`
# VARIANT 2: Split list into two halves -> cut with prev.next = None (used in D038, D040)
# VARIANT 3: Delete the middle node (LeetCode #2095) -> keep a prev pointer behind slow
```

---

## ⚠️ Common Mistake
```python
# Wrong: while fast.next.next:        # crashes when fast is None / list has 1 node
# Wrong: converting to a Python list just to index len//2 (works, but O(n) extra space)
# Right: while fast and fast.next
```

---

## 🎯 Interview Tip
Say: "Slow/fast pointers find the middle in one pass and O(1) space; the loop condition decides which middle I get on even length." This is the first step of D038 and D040.

---

## 🔗 Related Problems
→ D034 (Linked List Cycle) | D038 (Palindrome Linked List) | D040 (Reorder List)
