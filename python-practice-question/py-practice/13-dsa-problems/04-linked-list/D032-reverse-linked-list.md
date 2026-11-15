---

# D032. Reverse Linked List
# Category: DSA — Linked List
# Difficulty: ⭐ Easy | LeetCode #206

---

## ❓ Problem
Given the head of a singly linked list, reverse the list and return the new head.

```
Input:  1 → 2 → 3 → 4 → 5
Output: 5 → 4 → 3 → 2 → 1
```

---

## 💡 Quick Concept (2 lines only)
Walk the list keeping `prev` and `curr`. For each node, save `next`, point `curr.next` back to `prev`, then step both forward.
हिंदी: हर node का next pointer पीछे की तरफ मोड़ते जाओ; मोड़ने से पहले आगे वाला node सेव कर लो वरना list खो जाएगी।

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
    return dummy.next                          # real head (None if arr empty)


def print_list(head: Optional[ListNode]) -> str:
    vals: list[str] = []                       # collect values as text
    while head:                                # walk the list
        vals.append(str(head.val))             # store current value
        head = head.next                       # advance
    return " → ".join(vals) if vals else "None"  # readable output


# ============================================
# APPROACH 1: Brute force — copy values to a list, rebuild reversed
# O(n) time, O(n) space
# ============================================
def reverse_brute(head: Optional[ListNode]) -> Optional[ListNode]:
    vals: list[int] = []                       # all values
    while head:                                # read the list
        vals.append(head.val)                  # store value
        head = head.next                       # advance
    return create_list(vals[::-1])             # build new list from reversed values


# ============================================
# APPROACH 2: Iterative pointer flip — O(n) time, O(1) space  PREFERRED
# ============================================
def reverse_list(head: Optional[ListNode]) -> Optional[ListNode]:
    prev: Optional[ListNode] = None            # new tail will point to None
    curr = head                                # node being processed
    while curr:                                # until the end
        nxt = curr.next                        # save next before breaking the link
        curr.next = prev                       # reverse the pointer
        prev = curr                            # prev moves to current
        curr = nxt                             # curr moves to saved next
    return prev                                # prev is the new head


# ============================================
# APPROACH 3: Recursive — O(n) time, O(n) call stack
# ============================================
def reverse_recursive(head: Optional[ListNode]) -> Optional[ListNode]:
    if head is None or head.next is None:      # empty or single node: already reversed
        return head                            # nothing to do
    new_head = reverse_recursive(head.next)    # reverse the rest; returns its new head
    head.next.next = head                      # make the next node point back to head
    head.next = None                           # head becomes the tail
    return new_head                            # new head bubbles up unchanged


# ============================================
# TEST CASES
# ============================================
print(print_list(reverse_brute(create_list([1, 2, 3, 4, 5]))))      # 5 → 4 → 3 → 2 → 1
print(print_list(reverse_list(create_list([1, 2, 3, 4, 5]))))       # 5 → 4 → 3 → 2 → 1
print(print_list(reverse_recursive(create_list([1, 2, 3, 4, 5]))))  # 5 → 4 → 3 → 2 → 1
print(print_list(reverse_list(create_list([1, 2]))))                # 2 → 1
print(print_list(reverse_list(create_list([7]))))                   # 7
print(print_list(reverse_list(create_list([]))))                    # None
```

---

## 🔍 Why It Works
```
None  1→2→3
prev=None curr=1: nxt=2, 1.next=None, prev=1, curr=2
prev=1    curr=2: nxt=3, 2.next=1,    prev=2, curr=3
prev=2    curr=3: nxt=None, 3.next=2, prev=3, curr=None
return prev -> 3→2→1→None
```
हिंदी: `nxt` में आगे का node सुरक्षित रखकर link पलटते हैं; आखिर में `prev` ही नया head होता है।

---

## 📊 Complexity
```
Brute force: Time O(n) | Space O(n)
Iterative:   Time O(n) | Space O(1)  <- preferred
Recursive:   Time O(n) | Space O(n) — call stack (Python limit ~1000 frames!)
```

---

## ⚡ Variations

```python
# VARIANT 1: Reverse between positions left..right (LeetCode #92) — reverse only a sub-segment
# VARIANT 2: Reverse nodes in k-group (LeetCode #25) — reverse each block of k, link blocks
# VARIANT 3: Reverse a doubly linked list — swap prev/next of every node
```

---

## ⚠️ Common Mistake
```python
# Wrong: overwriting next before saving it -> rest of the list is lost
#   curr.next = prev
#   curr = curr.next      # now curr is prev, infinite loop / lost nodes
# Wrong: recursive version on a 10_000-node list -> RecursionError (default limit 1000)
# Right: save nxt first, and prefer the iterative version in Python
```

---

## 🎯 Interview Tip
Say: "Three pointers: prev, curr, next. I save next, flip the link, and advance. O(n) time, O(1) space." Mention that Python's recursion limit makes the iterative version safer. This is the base of many list problems (D038, D040).

---

## 🔗 Related Problems
→ D038 (Palindrome Linked List) | D040 (Reorder List) | D033 (Merge Two Sorted Lists)
