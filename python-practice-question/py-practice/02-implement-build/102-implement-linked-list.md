---

# Q102. Implement Linked List
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement a singly `LinkedList` with `append`, `prepend`, `delete(value)`, `reverse()`, iteration, `len()` and a readable `repr`.

```python
ll = LinkedList()
ll.append(1); ll.append(2); ll.prepend(0)
print(ll)   # 0 -> 1 -> 2 -> None
```

---

## 💡 Quick Concept (2 lines only)
A linked list is a chain of nodes, each holding a value and a `next` pointer; you only keep the `head`. Insert at head is O(1), search/append-without-tail is O(n).
हिंदी: Linked list में हर node अगले node को point करता है — सिर्फ head याद रखना होता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from __future__ import annotations  # allow Node | None forward references
from typing import Iterator  # for __iter__ type hint

class Node:  # one list node
    def __init__(self, value: int, next: Node | None = None) -> None:
        self.value = value  # Step 1: data stored in the node
        self.next = next  # pointer to the next node (or None)

class LinkedList:  # singly linked list
    def __init__(self) -> None:
        self.head: Node | None = None  # first node
        self.size = 0  # number of nodes

    def append(self, value: int) -> None:  # add at tail, O(n)
        node = Node(value)  # new node
        if self.head is None:  # empty list
            self.head = node  # node becomes head
        else:
            cur = self.head  # start at head
            while cur.next:  # walk to the last node
                cur = cur.next  # advance
            cur.next = node  # attach at the end
        self.size += 1  # update count

    def prepend(self, value: int) -> None:  # add at head, O(1)
        self.head = Node(value, self.head)  # new node points to old head
        self.size += 1  # update count

    def delete(self, value: int) -> bool:  # remove first match
        dummy = Node(0, self.head)  # Step 2: dummy node removes head special case
        prev, cur = dummy, self.head  # track previous + current
        while cur:  # scan the list
            if cur.value == value:  # found it
                prev.next = cur.next  # unlink the node
                self.head = dummy.next  # refresh head (it may have changed)
                self.size -= 1  # update count
                return True  # deleted
            prev, cur = cur, cur.next  # advance both pointers
        return False  # value not present

    def reverse(self) -> None:  # reverse in place, O(n)
        prev: Node | None = None  # reversed part starts empty
        cur = self.head  # start at head
        while cur:  # visit each node
            cur.next, prev, cur = prev, cur, cur.next  # flip pointer, move forward
        self.head = prev  # old tail is the new head

    def __iter__(self) -> Iterator[int]:  # iterate over values
        cur = self.head  # start at head
        while cur:  # until the end
            yield cur.value  # produce value
            cur = cur.next  # advance

    def __len__(self) -> int:  # len(ll)
        return self.size  # stored count

    def __repr__(self) -> str:  # readable output
        return " -> ".join(map(str, self)) + " -> None"  # 0 -> 1 -> None

# ============================================
# TEST CASES
# ============================================
ll = LinkedList()  # empty list
ll.append(1); ll.append(2); ll.append(3); ll.prepend(0)  # build list
print(ll)  # Expected: 0 -> 1 -> 2 -> 3 -> None
print(ll.delete(2), ll.delete(99))  # Expected: True False
print(ll)  # Expected: 0 -> 1 -> 3 -> None
ll.reverse()  # reverse in place
print(ll)  # Expected: 3 -> 1 -> 0 -> None
print(len(ll), list(ll))  # Expected: 3 [3, 1, 0]
ll.delete(3)  # delete the head node
print(ll)  # Expected: 1 -> 0 -> None
```

---

## 🔍 Why This Works (3 lines max)
Every operation just rewires `next` pointers. The dummy node in `delete` makes removing the head the same as removing any other node; the tuple assignment in `reverse` flips one pointer per step.
हिंदी: सब कुछ `next` pointers बदलने का खेल है — dummy node से head delete भी आसान हो जाता है।

---

## ⚡ Alternative Solution
```python
# Keep a tail pointer so append becomes O(1)
class FastList:
    def __init__(self) -> None:
        self.head: Node | None = None  # first node
        self.tail: Node | None = None  # last node

    def append(self, v: int) -> None:
        n = Node(v)  # new node
        if self.tail is None:  # empty list
            self.head = self.tail = n  # both point to n
        else:
            self.tail.next = n  # link after tail
            self.tail = n  # move tail

f = FastList()  # new list
for i in (1, 2, 3): f.append(i)  # append 1,2,3 in O(1) each
cur, out = f.head, []  # walk and collect
while cur: out.append(cur.value); cur = cur.next  # traverse
print(out)  # Expected: [1, 2, 3]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: moving self.head while traversing -> the list's start is lost forever
# while self.head.next:
#     self.head = self.head.next   # ❌ head now points to the tail
# (not run: it silently destroys the list)

# ✅ Correct: traverse with a separate pointer
# cur = self.head
# while cur.next:
#     cur = cur.next
```

---

## 🎯 Interview Tip (1 line)
Say: "Singly list: O(1) prepend, O(n) search; I use a dummy node to avoid head edge cases and a tail pointer for O(1) append."

---

## 🔗 Related Questions
→ Q100 (stack) | Q101 (queue) | Q099 (LRU cache) | Q153 (complete linked list)
