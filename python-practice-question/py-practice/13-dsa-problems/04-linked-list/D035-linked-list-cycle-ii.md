---

# D035. Linked List Cycle II
# Category: DSA — Linked List
# Difficulty: ⭐⭐ Medium | LeetCode #142

---

## ❓ Problem
Given the head of a linked list, return the node where the cycle begins. If there is no cycle, return `None`. Do not modify the list.

```
Input:  3 → 2 → 0 → -4, with -4.next pointing back to index 1
Output: the node with value 2 (cycle starts at index 1)
```

---

## 💡 Quick Concept (2 lines only)
Run Floyd's slow/fast until they meet. Then put one pointer back at head and move both one step at a time; they meet exactly at the cycle entrance.
हिंदी: पहले slow/fast से meeting point खोजो, फिर एक pointer को head पर रखकर दोनों को एक-एक कदम चलाओ; जहाँ मिलें वही cycle की शुरुआत है।

---

## ✅ Solution

```python
from __future__ import annotations             # allow ListNode self-reference in hints
from typing import Optional                    # for Optional[ListNode]


class ListNode:
    def __init__(self, val: int = 0, next: Optional[ListNode] = None) -> None:
        self.val = val                         # value stored in node
        self.next = next                       # pointer to next node


def create_list(arr: list[int], pos: int = -1) -> tuple[Optional[ListNode], Optional[ListNode]]:
    dummy = ListNode()                         # dummy head simplifies building
    curr = dummy                               # tail pointer
    nodes: list[ListNode] = []                 # keep nodes so we can link a cycle
    for v in arr:                              # go through each value
        curr.next = ListNode(v)                # append new node
        curr = curr.next                       # move tail forward
        nodes.append(curr)                     # remember it
    entry = None                               # expected cycle entrance (for tests)
    if pos >= 0 and nodes:                     # pos = index the tail links back to
        nodes[-1].next = nodes[pos]            # create the cycle
        entry = nodes[pos]                     # remember the entrance
    return dummy.next, entry                   # head and expected entrance


# ============================================
# APPROACH 1: Brute force — hash set, first repeated node is the entrance
# O(n) time, O(n) space
# ============================================
def detect_cycle_set(head: Optional[ListNode]) -> Optional[ListNode]:
    seen: set[int] = set()                     # ids of visited nodes
    while head:                                # walk the list
        if id(head) in seen:                   # first node we see twice
            return head                        # that is the cycle entrance
        seen.add(id(head))                     # mark visited
        head = head.next                       # advance
    return None                                # no cycle


# ============================================
# APPROACH 2: Floyd phase 1 + phase 2 — O(n) time, O(1) space  PREFERRED
# ============================================
def detect_cycle(head: Optional[ListNode]) -> Optional[ListNode]:
    slow = fast = head                         # both start at head
    while fast and fast.next:                  # phase 1: find a meeting point
        slow = slow.next                       # slow moves 1
        fast = fast.next.next                  # fast moves 2
        if slow is fast:                       # met inside the cycle
            ptr = head                         # phase 2: restart one pointer at head
            while ptr is not slow:             # move both at the same speed
                ptr = ptr.next                 # from head
                slow = slow.next               # from meeting point
            return ptr                         # they meet at the entrance
    return None                                # no cycle


# ============================================
# TEST CASES
# ============================================
h, e = create_list([3, 2, 0, -4], pos=1)
print(detect_cycle_set(h) is e)                # True
print(detect_cycle(h) is e)                    # True
print(detect_cycle(h).val)                     # 2
h, e = create_list([1, 2], pos=0)
print(detect_cycle(h) is e)                    # True
h, e = create_list([1], pos=0)
print(detect_cycle(h).val)                     # 1
h, e = create_list([1, 2, 3])
print(detect_cycle(h))                         # None
```

---

## 🔍 Why It Works
```
Let a = head -> entrance, b = entrance -> meeting point, c = meeting point -> entrance.
slow walked a+b, fast walked 2(a+b) = a+b + k*(b+c)  =>  a = k*(b+c) - b = (k-1)*(b+c) + c
So walking a from head and walking c from the meeting point (plus full laps) land on the entrance together.
```
हिंदी: गणित से a = c + (पूरे चक्कर) निकलता है, इसलिए head और meeting point से बराबर चलने पर दोनों entrance पर मिलते हैं।

---

## 📊 Complexity
```
Hash set: Time O(n) | Space O(n)
Floyd:    Time O(n) | Space O(1)  <- preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Find duplicate number (LeetCode #287) — treat array values as next pointers
# VARIANT 2: Length of the cycle — after meeting, loop until you return to the meeting node
# VARIANT 3: Remove the cycle — walk to the node whose next is the entrance and set it to None
```

---

## ⚠️ Common Mistake
```python
# Wrong: returning the meeting point as the entrance
#   if slow is fast: return slow        # meeting point is usually somewhere inside the loop
# Wrong: moving the second pointer 2 steps in phase 2
# Right: restart at head, move BOTH one step at a time
```

---

## 🎯 Interview Tip
Say: "Phase 1 detects the cycle, phase 2 finds the entrance because the distance from head to entrance equals the distance from the meeting point to entrance modulo cycle length." Quote the equation a = c + (k-1)*(b+c).

---

## 🔗 Related Problems
→ D034 (Linked List Cycle) | D036 (Middle of the Linked List) | D003 (Contains Duplicate)
