---

# D040. Reorder List
# Category: DSA — Linked List
# Difficulty: ⭐⭐ Medium | LeetCode #143

---

## ❓ Problem
Reorder `L0 → L1 → … → Ln-1 → Ln` into `L0 → Ln → L1 → Ln-1 → L2 → Ln-2 → …` in place, without changing node values.

```
Input:  1 → 2 → 3 → 4 → 5
Output: 1 → 5 → 2 → 4 → 3
```

---

## 💡 Quick Concept (2 lines only)
Three steps: find the middle, reverse the second half, then interleave the two halves.
हिंदी: बीच का node खोजो, दूसरी आधी को उलटो, फिर पहली और दूसरी आधी के nodes को बारी-बारी से जोड़ दो।

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
# APPROACH 1: Brute force — store nodes in a list, relink with two indexes
# O(n) time, O(n) space
# ============================================
def reorder_brute(head: Optional[ListNode]) -> None:
    if not head:                               # empty list: nothing to do
        return                                 # exit
    nodes: list[ListNode] = []                 # all nodes in order
    node: Optional[ListNode] = head            # walker
    while node:                                # collect nodes
        nodes.append(node)                     # store node
        node = node.next                       # advance
    i, j = 0, len(nodes) - 1                   # front and back indexes
    while i < j:                               # until they meet
        nodes[i].next = nodes[j]               # front -> back
        i += 1                                 # move front
        if i == j:                             # odd length: stop to avoid a cycle
            break                              # done
        nodes[j].next = nodes[i]               # back -> next front
        j -= 1                                 # move back
    nodes[i].next = None                       # terminate the list


# ============================================
# APPROACH 2: Middle + reverse + merge — O(n) time, O(1) space  PREFERRED
# ============================================
def reorder_list(head: Optional[ListNode]) -> None:
    if not head or not head.next:              # 0 or 1 node: already ordered
        return                                 # exit
    slow, fast = head, head                    # find middle
    while fast.next and fast.next.next:        # stop so slow is the end of first half
        slow = slow.next                       # slow moves 1
        fast = fast.next.next                  # fast moves 2
    second = slow.next                         # head of second half
    slow.next = None                           # cut the list in two
    prev: Optional[ListNode] = None            # reverse the second half
    while second:                              # standard reversal
        nxt = second.next                      # save next
        second.next = prev                     # flip pointer
        prev = second                          # advance prev
        second = nxt                           # advance second
    first, second = head, prev                 # first half and reversed second half
    while second:                              # second half is the same length or shorter
        n1, n2 = first.next, second.next       # save next pointers
        first.next = second                    # first -> second
        second.next = n1                       # second -> next of first
        first, second = n1, n2                 # advance both


# ============================================
# TEST CASES
# ============================================
h = create_list([1, 2, 3, 4, 5]); reorder_brute(h); print(print_list(h))   # 1 → 5 → 2 → 4 → 3
h = create_list([1, 2, 3, 4, 5]); reorder_list(h); print(print_list(h))    # 1 → 5 → 2 → 4 → 3
h = create_list([1, 2, 3, 4]); reorder_list(h); print(print_list(h))       # 1 → 4 → 2 → 3
h = create_list([1, 2]); reorder_list(h); print(print_list(h))             # 1 → 2
h = create_list([1]); reorder_list(h); print(print_list(h))                # 1
h = create_list([1, 2, 3, 4, 5, 6]); reorder_brute(h); print(print_list(h))  # 1 → 6 → 2 → 5 → 3 → 4
```

---

## 🔍 Why It Works
```
1 → 2 → 3 → 4 → 5
Step 1: middle = 3        first: 1→2→3   second: 4→5
Step 2: reverse second    5→4
Step 3: interleave        1→5 , 2→4 , 3  =>  1 → 5 → 2 → 4 → 3
```
हिंदी: पीछे वाले nodes तक सीधे पहुँचना मुश्किल है, इसलिए दूसरी आधी को उलटकर आगे-पीछे के nodes को बारी-बारी जोड़ते हैं।

---

## 📊 Complexity
```
Node array:        Time O(n) | Space O(n)
Mid+reverse+merge: Time O(n) | Space O(1)  <- preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Odd-Even Linked List (LeetCode #328) — group odd-index then even-index nodes
# VARIANT 2: Reverse only the second half and return a new list (no in-place)
# VARIANT 3: Reorder with a deque -> popleft / pop alternately into a new list (O(n) space)
```

---

## ⚠️ Common Mistake
```python
# Wrong: forgetting slow.next = None -> first half still links into the second half -> cycle
# Wrong: returning the head — the function must modify in place (returns None)
# Right: cut the list at the middle before reversing and merging
```

---

## 🎯 Interview Tip
Say: "This is three classic list moves combined: middle (slow/fast), reverse, merge. I'll cut the list at the middle first to avoid cycles." Interviewers love this because it tests composing simple subroutines.

---

## 🔗 Related Problems
→ D032 (Reverse Linked List) | D036 (Middle of the Linked List) | D038 (Palindrome Linked List)
