---

# D033. Merge Two Sorted Lists
# Category: DSA — Linked List
# Difficulty: ⭐ Easy | LeetCode #21

---

## ❓ Problem
Given the heads of two sorted linked lists, merge them into one sorted list by splicing together the existing nodes. Return the head of the merged list.

```
Input:  l1 = 1 → 2 → 4, l2 = 1 → 3 → 4
Output: 1 → 1 → 2 → 3 → 4 → 4
```

---

## 💡 Quick Concept (2 lines only)
Use a dummy head and a tail pointer. Compare the two current nodes, attach the smaller to tail, advance that list. When one ends, attach the rest of the other.
हिंदी: Dummy node बनाओ, दोनों heads compare करो, छोटा वाला जोड़ते जाओ, बचा हुआ हिस्सा सीधे attach कर दो।

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
# APPROACH 1: Brute force — collect, sort, rebuild
# O(n log n) time, O(n) space (ignores that lists are sorted)
# ============================================
def merge_brute(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    vals: list[int] = []                       # all values together
    for node in (l1, l2):                      # process both lists
        while node:                            # walk each list
            vals.append(node.val)              # collect value
            node = node.next                   # advance
    return create_list(sorted(vals))           # sort and rebuild


# ============================================
# APPROACH 2: Iterative two-pointer with dummy — O(n+m) time, O(1) space  PREFERRED
# ============================================
def merge_two_lists(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    dummy = ListNode(-1)                       # dummy avoids special-casing the head
    tail = dummy                               # tail of merged list
    while l1 and l2:                           # both lists still have nodes
        if l1.val <= l2.val:                   # <= keeps the merge stable
            tail.next = l1                     # attach l1 node
            l1 = l1.next                       # advance l1
        else:
            tail.next = l2                     # attach l2 node
            l2 = l2.next                       # advance l2
        tail = tail.next                       # move tail to the attached node
    tail.next = l1 or l2                       # attach whichever list has leftovers
    return dummy.next                          # skip dummy


# ============================================
# APPROACH 3: Recursive — O(n+m) time, O(n+m) stack
# ============================================
def merge_recursive(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    if l1 is None:                             # l1 empty -> rest is l2
        return l2                              # return l2
    if l2 is None:                             # l2 empty -> rest is l1
        return l1                              # return l1
    if l1.val <= l2.val:                       # l1 head is smaller
        l1.next = merge_recursive(l1.next, l2) # merge the rest after l1
        return l1                              # l1 heads this merge
    l2.next = merge_recursive(l1, l2.next)     # else l2 head is smaller
    return l2                                  # l2 heads this merge


# ============================================
# TEST CASES
# ============================================
print(print_list(merge_brute(create_list([1, 2, 4]), create_list([1, 3, 4]))))      # 1 → 1 → 2 → 3 → 4 → 4
print(print_list(merge_two_lists(create_list([1, 2, 4]), create_list([1, 3, 4]))))  # 1 → 1 → 2 → 3 → 4 → 4
print(print_list(merge_recursive(create_list([1, 2, 4]), create_list([1, 3, 4]))))  # 1 → 1 → 2 → 3 → 4 → 4
print(print_list(merge_two_lists(create_list([]), create_list([]))))                # None
print(print_list(merge_two_lists(create_list([]), create_list([0]))))               # 0
print(print_list(merge_two_lists(create_list([5, 6]), create_list([1, 2, 3]))))     # 1 → 2 → 3 → 5 → 6
```

---

## 🔍 Why It Works
```
l1: 1→2→4   l2: 1→3→4   dummy→
Step 1: 1(l1) <= 1(l2)  -> dummy→1(l1)
Step 2: 2(l1) >  1(l2)  -> dummy→1→1(l2)
Step 3: 2(l1) <= 3(l2)  -> ...→2
Step 4: 4(l1) >  3(l2)  -> ...→3
Step 5: 4(l1) <= 4(l2)  -> ...→4(l1); l1 ends
Leftover l2 (4) attached directly.
```
हिंदी: हर step में छोटा node चुनो; एक list खत्म होते ही दूसरी को सीधे जोड़ दो क्योंकि वो पहले से sorted है।

---

## 📊 Complexity
```
Brute force: Time O((n+m) log(n+m)) | Space O(n+m)
Iterative:   Time O(n+m)            | Space O(1)  <- preferred
Recursive:   Time O(n+m)            | Space O(n+m) — call stack
```

---

## ⚡ Variations

```python
# VARIANT 1: Merge K sorted lists (D041) — heap of heads, or merge pairwise
# VARIANT 2: Merge into a descending list — compare with >= or reverse the result
# VARIANT 3: Remove duplicates while merging — skip a node equal to tail.val
```

---

## ⚠️ Common Mistake
```python
# Wrong: no dummy node -> messy head handling
#   head = l1 if l1.val < l2.val else l2     # AttributeError if either is None
# Wrong: forgetting leftovers -> loop ends but tail.next never set, nodes lost
# Right: dummy node + `tail.next = l1 or l2`
```

---

## 🎯 Interview Tip
Say: "I'll use a dummy node so I never special-case the head, then a tail pointer. At the end I attach the non-empty remainder in O(1). Nodes are reused, so space is O(1)." Follow-up: merge K lists (D041).

---

## 🔗 Related Problems
→ D041 (Merge K Sorted Lists) | D039 (Add Two Numbers) | D032 (Reverse Linked List)
