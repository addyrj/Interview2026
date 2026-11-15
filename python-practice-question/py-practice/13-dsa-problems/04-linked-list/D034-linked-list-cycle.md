---

# D034. Linked List Cycle
# Category: DSA — Linked List
# Difficulty: ⭐ Easy | LeetCode #141

---

## ❓ Problem
Given the head of a linked list, return `True` if the list has a cycle (some node's `next` points back to an earlier node), else `False`.

```
Input:  3 → 2 → 0 → -4, with -4.next pointing back to 2
Output: True
```

---

## 💡 Quick Concept (2 lines only)
Floyd's tortoise and hare: slow moves 1 step, fast moves 2. In a cycle the fast pointer eventually laps the slow one and they meet; without a cycle fast hits None.
हिंदी: Slow एक कदम, fast दो कदम चलता है; अगर cycle है तो दोनों कभी न कभी मिलेंगे, वरना fast None तक पहुँच जाएगा।

---

## ✅ Solution

```python
from __future__ import annotations             # allow ListNode self-reference in hints
from typing import Optional                    # for Optional[ListNode]


class ListNode:
    def __init__(self, val: int = 0, next: Optional[ListNode] = None) -> None:
        self.val = val                         # value stored in node
        self.next = next                       # pointer to next node


def create_list(arr: list[int], pos: int = -1) -> Optional[ListNode]:
    dummy = ListNode()                         # dummy head simplifies building
    curr = dummy                               # tail pointer
    nodes: list[ListNode] = []                 # keep nodes so we can link a cycle
    for v in arr:                              # go through each value
        curr.next = ListNode(v)                # append new node
        curr = curr.next                       # move tail forward
        nodes.append(curr)                     # remember it
    if pos >= 0 and nodes:                     # pos = index the tail links back to
        nodes[-1].next = nodes[pos]            # create the cycle
    return dummy.next                          # real head


# ============================================
# APPROACH 1: Brute force — hash set of visited nodes
# O(n) time, O(n) space
# ============================================
def has_cycle_set(head: Optional[ListNode]) -> bool:
    seen: set[int] = set()                     # ids of visited nodes
    while head:                                # walk until the end
        if id(head) in seen:                   # seen this node before -> cycle
            return True                        # cycle found
        seen.add(id(head))                     # mark visited
        head = head.next                       # advance
    return False                               # reached None -> no cycle


# ============================================
# APPROACH 2: Floyd's slow/fast pointers — O(n) time, O(1) space  PREFERRED
# ============================================
def has_cycle(head: Optional[ListNode]) -> bool:
    slow = fast = head                         # both start at head
    while fast and fast.next:                  # fast needs two safe steps
        slow = slow.next                       # slow moves 1
        fast = fast.next.next                  # fast moves 2
        if slow is fast:                       # they met inside the cycle
            return True                        # cycle exists
    return False                               # fast fell off the end


# ============================================
# TEST CASES
# ============================================
print(has_cycle_set(create_list([3, 2, 0, -4], pos=1)))  # True
print(has_cycle(create_list([3, 2, 0, -4], pos=1)))      # True
print(has_cycle(create_list([1, 2], pos=0)))             # True
print(has_cycle(create_list([1], pos=-1)))               # False
print(has_cycle(create_list([1, 2, 3])))                 # False
print(has_cycle(create_list([])))                        # False
```

---

## 🔍 Why It Works
```
3 → 2 → 0 → -4 ─┐
    ↑___________|
slow: 3, 2, 0, 2, 0 ...
fast: 3, 0, 2, -4, 0 ... they land on the same node
Each step the gap changes by 1, so fast cannot jump over slow.
```
हिंदी: Cycle में fast हर round में slow से 1 कदम करीब आता है, इसलिए वो उसे "पार" नहीं कर सकता, मिलना तय है।

---

## 📊 Complexity
```
Hash set: Time O(n) | Space O(n)
Floyd:    Time O(n) | Space O(1)  <- preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Find where the cycle begins (D035) — reset one pointer to head after meeting
# VARIANT 2: Find the cycle length — after meeting, count steps until you return to the same node
# VARIANT 3: Happy Number (LeetCode #202) — same cycle detection on a number sequence
```

---

## ⚠️ Common Mistake
```python
# Wrong: comparing values instead of nodes
#   if slow.val == fast.val: return True     # duplicates give false positives
# Wrong: while fast.next: ...                # fast may be None -> AttributeError
# Right: compare identity (slow is fast) and guard `while fast and fast.next`
```

---

## 🎯 Interview Tip
Say: "I could use a visited set for O(n) space, but Floyd's two pointers do it in O(1)." Compare nodes by identity, not value. Be ready for the follow-up: find the cycle start (D035).

---

## 🔗 Related Problems
→ D035 (Linked List Cycle II) | D036 (Middle of the Linked List) | D003 (Contains Duplicate)
