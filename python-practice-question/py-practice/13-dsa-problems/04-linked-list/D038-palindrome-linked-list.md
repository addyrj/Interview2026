---

# D038. Palindrome Linked List
# Category: DSA — Linked List
# Difficulty: ⭐ Easy | LeetCode #234

---

## ❓ Problem
Given the head of a singly linked list, return `True` if it is a palindrome (reads the same forwards and backwards), else `False`.

```
Input:  1 → 2 → 2 → 1   Output: True
Input:  1 → 2           Output: False
```

---

## 💡 Quick Concept (2 lines only)
Find the middle with slow/fast, reverse the second half, then compare it with the first half node by node.
हिंदी: बीच का node खोजो, दूसरी आधी list को उलट दो, फिर दोनों हिस्सों को साथ-साथ compare करो।

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


# ============================================
# APPROACH 1: Brute force — copy values to a list, compare with reverse
# O(n) time, O(n) space
# ============================================
def is_palindrome_list(head: Optional[ListNode]) -> bool:
    vals: list[int] = []                       # all values
    while head:                                # read the list
        vals.append(head.val)                  # store value
        head = head.next                       # advance
    return vals == vals[::-1]                  # palindrome check on the array


# ============================================
# APPROACH 2: Reverse second half in place — O(n) time, O(1) space  PREFERRED
# ============================================
def is_palindrome(head: Optional[ListNode]) -> bool:
    slow = fast = head                         # find the middle
    while fast and fast.next:                  # fast jumps two nodes
        slow = slow.next                       # slow moves 1
        fast = fast.next.next                  # fast moves 2
    prev: Optional[ListNode] = None            # reverse from slow onward
    while slow:                                # standard reversal
        nxt = slow.next                        # save next
        slow.next = prev                       # flip pointer
        prev = slow                            # advance prev
        slow = nxt                             # advance slow
    left, right = head, prev                   # compare first half and reversed second half
    while right:                               # second half is the shorter-or-equal one
        if left.val != right.val:              # mismatch -> not a palindrome
            return False                       # early exit
        left = left.next                       # advance left
        right = right.next                     # advance right
    return True                                # all pairs matched


# ============================================
# TEST CASES
# ============================================
print(is_palindrome_list(create_list([1, 2, 2, 1])))   # True
print(is_palindrome(create_list([1, 2, 2, 1])))        # True
print(is_palindrome(create_list([1, 2, 3, 2, 1])))     # True
print(is_palindrome(create_list([1, 2])))              # False
print(is_palindrome(create_list([1])))                 # True
print(is_palindrome(create_list([])))                  # True
```

---

## 🔍 Why It Works
```
1 → 2 → 2 → 1
slow ends at the 3rd node (value 2). Reverse from there: second half 2 → 1 becomes 1 → 2
left: 1,2   right: 1,2  -> all equal -> True
(The first half still points into the reversed part, but we stop when right ends.)
```
हिंदी: दूसरी आधी list उलटने के बाद दोनों हिस्से एक ही दिशा में पढ़े जा सकते हैं, इसलिए सीधे compare हो जाता है।

---

## 📊 Complexity
```
Copy to array:    Time O(n) | Space O(n)
Reverse 2nd half: Time O(n) | Space O(1)  <- preferred (modifies the list)
```

---

## ⚡ Variations

```python
# VARIANT 1: Restore the list after checking -> reverse the second half again
# VARIANT 2: Palindrome with a stack -> push first half, pop while walking the second half
# VARIANT 3: Palindrome Number (LeetCode #9) -> reverse half of the digits instead
```

---

## ⚠️ Common Mistake
```python
# Wrong: comparing node objects, not values
#   if left != right: ...        # nodes are different objects even with equal values
# Wrong: forgetting to handle odd length — for odd n slow lands on the center; the center pairs with itself, which is fine
# Right: compare .val and loop while right is not None
```

---

## 🎯 Interview Tip
Say: "The easy way is copying to a list, O(n) space. To get O(1) space, I find the middle, reverse the second half and compare." Mention that it mutates the list and offer to restore it.

---

## 🔗 Related Problems
→ D032 (Reverse Linked List) | D036 (Middle of the Linked List) | D016 (Valid Palindrome)
