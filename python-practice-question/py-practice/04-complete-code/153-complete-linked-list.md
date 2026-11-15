---

# Q153. Complete Linked List
# Category: Complete The Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Complete a singly linked list with `append`, `prepend`, iteration and `reverse()`.

```python
from __future__ import annotations
from typing import Iterator


class Node:
    def __init__(self, val: int, next: Node | None = None) -> None:
        self.val, self.next = val, next


class LinkedList:
    def __init__(self) -> None:
        self.head: Node | None = None

    def prepend(self, val: int) -> None:
        self.head = Node(val, ____)                # BLANK 1: link to the old head

    def append(self, val: int) -> None:
        if self.head is None:
            self.head = Node(val); return
        cur = self.head
        while cur.____ is not None:                # BLANK 2: walk to the last node
            cur = cur.next
        cur.next = Node(val)

    def __iter__(self) -> Iterator[int]:
        cur = self.head
        while cur:
            ____ cur.val                           # BLANK 3: produce the value
            cur = cur.next

    def reverse(self) -> None:
        prev = None
        cur = self.head
        while cur:
            cur.next, prev, cur = ____, cur, cur.next  # BLANK 4: flip the pointer
        self.head = prev
```

---

## 💡 Quick Concept (2 lines only)
A linked list is nodes holding a value and a `next` pointer; prepend is O(1), append is O(n) without a tail pointer, and reverse flips each pointer in one pass.
हिंदी: हर node में value और `next` pointer होता है; reverse में एक-एक pointer उलटते जाते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from __future__ import annotations                 # allow Node | None before Node is defined
from typing import Iterator


class Node:
    def __init__(self, val: int, next: Node | None = None) -> None:
        self.val, self.next = val, next            # payload and pointer


class LinkedList:
    def __init__(self) -> None:
        self.head: Node | None = None              # empty list

    def prepend(self, val: int) -> None:           # O(1)
        self.head = Node(val, self.head)           # BLANK 1: new node points at the old head

    def append(self, val: int) -> None:            # O(n)
        if self.head is None:                      # empty list
            self.head = Node(val)                  # new node becomes head
            return
        cur = self.head                            # start at head
        while cur.next is not None:                # BLANK 2: stop at the LAST node
            cur = cur.next                         # advance
        cur.next = Node(val)                       # attach at the end

    def __iter__(self) -> Iterator[int]:           # makes list(ll) / for-loops work
        cur = self.head
        while cur:                                 # until we fall off the end
            yield cur.val                          # BLANK 3: emit the value
            cur = cur.next                         # move on

    def reverse(self) -> None:                     # O(n) time, O(1) space
        prev = None                                # reversed part starts empty
        cur = self.head
        while cur:
            cur.next, prev, cur = prev, cur, cur.next  # BLANK 4: flip pointer, step forward
        self.head = prev                           # prev is the new head


# ============================================
# TEST CASES
# ============================================
ll = LinkedList()
ll.append(2); ll.append(3)                         # 2 -> 3
ll.prepend(1)                                      # 1 -> 2 -> 3
print(list(ll))                                    # Expected: [1, 2, 3]
ll.reverse()                                       # 3 -> 2 -> 1
print(list(ll))                                    # Expected: [3, 2, 1]
print(list(LinkedList()))                          # Expected: []
one = LinkedList(); one.append(7); one.reverse()   # single node
print(list(one))                                   # Expected: [7]
```

---

## 🔍 Why This Works (3 lines max)
`prepend` just re-points the head. `reverse` keeps `prev` (already reversed part) and `cur`; the tuple assignment evaluates the right side first, so `cur.next` is saved before being overwritten.
हिंदी: Tuple assignment पहले right side evaluate करता है, इसलिए `cur.next` खोए बिना pointer पलट जाता है।

---

## ⚡ Alternative Solution
```python
# Dataclass node + tail pointer for O(1) append
from dataclasses import dataclass
from typing import Optional


@dataclass
class N:
    val: int                                       # payload
    next: Optional["N"] = None                     # pointer


class FastList:
    def __init__(self) -> None:
        self.head = self.tail = None               # track both ends

    def append(self, val: int) -> None:            # now O(1)
        node = N(val)
        if self.tail is None:                      # empty
            self.head = self.tail = node
        else:
            self.tail.next = node                  # link after tail
            self.tail = node                       # move tail

    def to_list(self) -> list[int]:
        out, cur = [], self.head                   # collect values
        while cur:
            out.append(cur.val); cur = cur.next
        return out

f = FastList(); [f.append(i) for i in range(4)]
print(f.to_list())                                 # Expected: [0, 1, 2, 3]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: while cur is not None: ... cur.next = Node(val)  -> cur is None at the end, AttributeError
# ❌ Wrong: in reverse, `cur.next = prev; cur = cur.next` -> cur.next was overwritten, loop ends early
# ❌ Wrong: forgetting self.head = prev -> list looks truncated to one node
# ✅ Correct: stop at cur.next is None; save next before flipping (tuple assignment)
```

---

## 🎯 Interview Tip (1 line)
Say: "Prepend O(1), append O(n) (O(1) with a tail pointer), reverse is three-pointer iteration in O(1) space — always handle empty and single-node lists."

---

## 🔗 Related Questions
→ Q102 (implement linked list) | Q154 (stack class) | D032 (reverse linked list) | D034 (cycle detection)
