---

# D037. Remove Nth Node From End
# Category: DSA — Linked List
# Difficulty: ⭐⭐ Medium | LeetCode #19

---

## ❓ Problem
Given the head of a linked list, remove the `n`-th node from the end of the list and return the head.

```
Input:  head = 1 → 2 → 3 → 4 → 5, n = 2
Output: 1 → 2 → 3 → 5
```

---

## 💡 Quick Concept (2 lines only)
Use a dummy head and two pointers. Move `fast` n+1 steps ahead, then move both until fast is None; `slow` now sits just before the node to delete.
हिंदी: Fast को n+1 कदम आगे भेजो, फिर दोनों साथ चलाओ; fast के अंत पर पहुँचते ही slow हटाए जाने वाले node से ठीक पहले होगा।

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
# APPROACH 1: Brute force — two passes (count length, then delete index len-n)
# O(n) time, O(1) space
# ============================================
def remove_two_pass(head: Optional[ListNode], n: int) -> Optional[ListNode]:
    length = 0                                 # total nodes
    node = head                                # walker
    while node:                                # first pass: count
        length += 1                            # one more node
        node = node.next                       # advance
    dummy = ListNode(0, head)                  # dummy handles removing the head
    prev = dummy                               # will stop before the target
    for _ in range(length - n):                # walk to node just before target
        prev = prev.next                       # advance
    prev.next = prev.next.next                 # unlink the target
    return dummy.next                          # real head


# ============================================
# APPROACH 2: One pass with gap of n between two pointers — O(n) time, O(1) space  PREFERRED
# ============================================
def remove_nth_from_end(head: Optional[ListNode], n: int) -> Optional[ListNode]:
    dummy = ListNode(0, head)                  # dummy handles removing the head
    slow = fast = dummy                        # both start at dummy
    for _ in range(n + 1):                     # open a gap of n+1 between them
        fast = fast.next                       # advance fast (n is guaranteed valid)
    while fast:                                # move both until fast falls off the end
        slow = slow.next                       # slow follows
        fast = fast.next                       # fast leads
    slow.next = slow.next.next                 # unlink the target node
    return dummy.next                          # real head


# ============================================
# TEST CASES
# ============================================
print(print_list(remove_two_pass(create_list([1, 2, 3, 4, 5]), 2)))       # 1 → 2 → 3 → 5
print(print_list(remove_nth_from_end(create_list([1, 2, 3, 4, 5]), 2)))   # 1 → 2 → 3 → 5
print(print_list(remove_nth_from_end(create_list([1]), 1)))               # None
print(print_list(remove_nth_from_end(create_list([1, 2]), 1)))            # 1
print(print_list(remove_nth_from_end(create_list([1, 2]), 2)))            # 2
print(print_list(remove_nth_from_end(create_list([1, 2, 3]), 3)))         # 2 → 3
```

---

## 🔍 Why It Works
```
dummy→1→2→3→4→5  n=2
fast moves 3 steps: fast=3, slow=dummy
move both: (fast=4,slow=1) (fast=5,slow=2) (fast=None,slow=3)
slow=3, target=slow.next=4 -> 3.next = 5 -> 1→2→3→5
```
हिंदी: दोनों pointers के बीच fixed gap रहता है, इसलिए fast के अंत पर होने पर slow अंत से n+1 जगह पीछे होता है।

---

## 📊 Complexity
```
Two pass:  Time O(n) | Space O(1)
One pass:  Time O(n) | Space O(1)  <- preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Remove the middle node (LeetCode #2095) — slow/fast, stop one before slow
# VARIANT 2: Find the nth node from the end (no deletion) — same gap trick, return slow
# VARIANT 3: Rotate list right by k (LeetCode #61) — find new tail with the same gap idea
```

---

## ⚠️ Common Mistake
```python
# Wrong: no dummy node -> removing the head (n == length) crashes
#   slow = fast = head ; slow.next = slow.next.next   # slow.next is None
# Wrong: gap of n instead of n+1 -> slow lands ON the target, cannot unlink it
# Right: start both at a dummy and open a gap of n+1
```

---

## 🎯 Interview Tip
Say: "A dummy node removes the edge case where the head itself is deleted, and a gap of n+1 leaves slow right before the target in a single pass." Mention you would validate n if it was not guaranteed.

---

## 🔗 Related Problems
→ D036 (Middle of the Linked List) | D033 (Merge Two Sorted Lists) | D040 (Reorder List)
