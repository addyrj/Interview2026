---

# D039. Add Two Numbers
# Category: DSA — Linked List
# Difficulty: ⭐⭐ Medium | LeetCode #2

---

## ❓ Problem
Two non-empty linked lists represent two non-negative integers with digits stored in **reverse order** (one digit per node). Add the numbers and return the sum as a linked list in the same format.

```
Input:  l1 = 2 → 4 → 3 (342), l2 = 5 → 6 → 4 (465)
Output: 7 → 0 → 8 (807)
```

---

## 💡 Quick Concept (2 lines only)
Walk both lists together, adding digits plus a carry. Store `total % 10` in a new node, carry `total // 10` forward. Keep going while either list or the carry remains.
हिंदी: दोनों lists के digits और carry जोड़ते जाओ, `% 10` node में रखो और `// 10` आगे carry करो।

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
# APPROACH 1: Brute force — convert to ints, add, convert back
# O(n+m) time, O(n+m) space (Python ints are arbitrary precision, so this works)
# ============================================
def add_via_int(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    def to_int(node: Optional[ListNode]) -> int:
        digits: list[str] = []                 # digits in stored (reversed) order
        while node:                            # walk the list
            digits.append(str(node.val))       # collect digit
            node = node.next                   # advance
        return int("".join(reversed(digits)))  # reverse to normal order and parse
    total = to_int(l1) + to_int(l2)            # add as integers
    return create_list([int(c) for c in reversed(str(total))])  # back to reversed list


# ============================================
# APPROACH 2: Digit-by-digit with carry — O(max(n,m)) time, O(1) extra space  PREFERRED
# ============================================
def add_two_numbers(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    dummy = ListNode()                         # dummy head for the result
    tail = dummy                               # tail pointer
    carry = 0                                  # carry between digits
    while l1 or l2 or carry:                   # continue while digits or carry remain
        total = carry                          # start with the carry
        if l1:                                 # add digit from l1 if present
            total += l1.val                    # add digit
            l1 = l1.next                       # advance l1
        if l2:                                 # add digit from l2 if present
            total += l2.val                    # add digit
            l2 = l2.next                       # advance l2
        carry, digit = divmod(total, 10)       # new carry and the digit to store
        tail.next = ListNode(digit)            # append result digit
        tail = tail.next                       # move tail
    return dummy.next                          # real head


# ============================================
# TEST CASES
# ============================================
print(print_list(add_via_int(create_list([2, 4, 3]), create_list([5, 6, 4]))))        # 7 → 0 → 8
print(print_list(add_two_numbers(create_list([2, 4, 3]), create_list([5, 6, 4]))))    # 7 → 0 → 8
print(print_list(add_two_numbers(create_list([0]), create_list([0]))))                # 0
print(print_list(add_two_numbers(create_list([9, 9, 9, 9, 9, 9, 9]), create_list([9, 9, 9, 9]))))  # 8 → 9 → 9 → 9 → 0 → 0 → 0 → 1
print(print_list(add_two_numbers(create_list([5]), create_list([5]))))                # 0 → 1
print(print_list(add_two_numbers(create_list([1, 8]), create_list([0]))))             # 1 → 8
```

---

## 🔍 Why It Works
```
  2 4 3      (342)
+ 5 6 4      (465)
digit0: 2+5=7  carry 0 -> 7
digit1: 4+6=10 carry 1 -> 0
digit2: 3+4+1=8 carry 0 -> 8
Result 7 → 0 → 8 = 807
```
हिंदी: Reverse order में digits होने से सबसे छोटा digit पहले आता है, इसलिए school वाले addition की तरह left से right carry के साथ जोड़ना आसान है।

---

## 📊 Complexity
```
Via int:      Time O(n+m) | Space O(n+m)
Carry method: Time O(max(n,m)) | Space O(1) extra (output list excluded)  <- preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Digits stored in forward order (LeetCode #445) — use two stacks or reverse both lists
# VARIANT 2: Multiply Strings (LeetCode #43) — same digit/carry idea
# VARIANT 3: Add Binary (LeetCode #67) — carry with base 2
```

---

## ⚠️ Common Mistake
```python
# Wrong: loop ends when both lists end -> final carry dropped (5 + 5 gives 0 instead of 0 → 1)
#   while l1 or l2:
# Wrong: assuming lists have equal length
# Right: while l1 or l2 or carry, and treat a missing digit as 0
```

---

## 🎯 Interview Tip
Say: "I simulate grade-school addition with a carry; the loop condition includes `carry` so a final carry creates an extra node." Note that the int-conversion trick works in Python but defeats the purpose in interviews.

---

## 🔗 Related Problems
→ D033 (Merge Two Sorted Lists) | D032 (Reverse Linked List) | D041 (Merge K Sorted Lists)
