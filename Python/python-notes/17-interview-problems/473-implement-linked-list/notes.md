---

# 473. Implement Linked List
# हिंदी में: Linked List बनाना (Singly Linked List)

Runnable solution with tests: [main.py](./main.py) (run: `python main.py`, verified on Python 3.13).

---

## 🔵 Simple Definition (English)
A linked list is a chain of nodes. Each node stores a value and a pointer to the next node. You only keep the `head`; to reach any item you walk the chain.

## 🔵 सरल परिभाषा (Hindi)
Linked list nodes की एक चेन है। हर node में एक value और अगले node का pointer होता है। आप सिर्फ `head` रखते हैं; किसी भी item तक पहुँचने के लिए चेन पर चलना पड़ता है।

---

## 🔴 Problem it Solves
Arrays (Python lists) store items in one contiguous block. Inserting or deleting in the front or middle shifts everything: O(n). A linked list inserts at the head in O(1) and removes a known node in O(1) because only pointers change. Interviewers use it to test pointer thinking: reversing, cycle detection, dummy nodes, edge cases (empty list, single node, head deletion).

## 🔴 यह क्यों बना? (Hindi)
Arrays (Python lists) items को एक continuous block में रखते हैं। शुरू या बीच में insert/delete करने पर सब कुछ खिसकता है: O(n)। Linked list में head पर insert O(1) में होता है और पता हुए node को हटाना भी O(1) है, क्योंकि सिर्फ pointers बदलते हैं। Interviewer इससे pointer की समझ परखते हैं: reverse, cycle detection, dummy node, edge cases (खाली list, एक node, head delete)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Node = (value, next). The list holds only `head`
Step 2 → prepend(v): new node points to old head; head = new node        O(1)
Step 3 → append(v): walk to the last node (next is None), link new node  O(n)
Step 4 → find(v): walk from head comparing values                        O(n)
Step 5 → delete(v): keep `prev`; set prev.next = cur.next (a dummy node
          before head removes the special case for deleting the head)
Step 6 → reverse(): for each node flip next to point to prev             O(n), O(1) space
Step 7 → cycle check: slow moves 1, fast moves 2; if they meet, a loop exists
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Node = (value, next)। List सिर्फ `head` रखती है
Step 2 → prepend(v): नया node पुराने head की ओर point करता है; head = नया node   O(1)
Step 3 → append(v): आखिरी node (next None) तक चलो, नया node जोड़ो                O(n)
Step 4 → find(v): head से चलते हुए values compare करो                             O(n)
Step 5 → delete(v): `prev` रखो; prev.next = cur.next (head से पहले dummy node
          लगाने से head delete का special case खत्म हो जाता है)
Step 6 → reverse(): हर node का next पीछे वाले (prev) की ओर पलट दो                O(n), O(1) space
Step 7 → cycle check: slow 1 कदम, fast 2 कदम; अगर मिल गए तो loop है
```

---

## 🟡 Real World Example
A browser's "back" history, an undo stack in an editor, the free-list inside a memory allocator, and the chaining in hash maps are linked structures. In a Swiggy-style delivery app, a driver's route stops can be a list where inserting a new stop mid-route is just a pointer change. Python's own `collections.deque` is a linked list of fixed-size blocks.

## 🟡 Real Example Hindi mein
Browser की "back" history, editor का undo stack, memory allocator की free-list और hash map की chaining, सब linked structures हैं। Swiggy जैसे delivery app में driver के route के stops एक list हो सकते हैं, जहाँ बीच में नया stop जोड़ना सिर्फ pointer बदलना है। Python का `collections.deque` भी fixed-size blocks की linked list है।

---

## 💻 Code Example — Basic
```python
# Basic singly linked list, built by hand
class Node:
    def __init__(self, value: int) -> None:
        self.value: int = value                # data stored in the node
        self.next: "Node | None" = None        # pointer to next node

head: Node = Node(1)                           # first node
head.next = Node(2)                            # link second node
head.next.next = Node(3)                       # link third node

cur: "Node | None" = head                      # start at the head
values: list[int] = []                         # collect values here
while cur is not None:                         # walk until the end
    values.append(cur.value)                   # read current value
    cur = cur.next                             # move to next node
print(values)                                  # [1, 2, 3]

prev: "Node | None" = None                     # reverse: nothing behind head yet
cur = head                                     # start again at head
while cur is not None:                         # visit every node
    nxt = cur.next                             # remember the rest of the list
    cur.next = prev                            # flip the pointer backwards
    prev, cur = cur, nxt                       # step forward
out: list[int] = []                            # read the reversed list
cur = prev                                     # prev is the new head
while cur is not None:                         # walk again
    out.append(cur.value)                      # collect
    cur = cur.next                             # advance
print(out)                                     # [3, 2, 1]

# Output:
# [1, 2, 3]
# [3, 2, 1]
```

## 💻 Code Example — Advanced
```python
# Production style: generic, iterable, dummy-node delete (full class + tests in main.py)
from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, Iterator, Optional, TypeVar

T = TypeVar("T")                               # value type


@dataclass
class Node(Generic[T]):
    value: T                                   # payload
    next: Optional["Node[T]"] = None           # next pointer


class LinkedList(Generic[T]):
    def __init__(self) -> None:
        self.head: Optional[Node[T]] = None    # first node
        self._size = 0                         # cached length

    def prepend(self, value: T) -> None:
        self.head = Node(value, self.head)     # O(1) insert at head
        self._size += 1                        # keep size in sync

    def delete(self, value: T) -> bool:
        dummy: Node[T] = Node(None)  # type: ignore[arg-type]   # sentinel before head
        dummy.next = self.head                 # attach it
        prev, cur = dummy, self.head           # two pointers
        while cur is not None:                 # scan
            if cur.value == value:             # found it
                prev.next = cur.next           # unlink the node
                self.head = dummy.next         # head may have changed
                self._size -= 1                # update size
                return True                    # deleted
            prev, cur = cur, cur.next          # advance both
        return False                           # not present

    def has_cycle(self) -> bool:
        slow = fast = self.head                # both start at head
        while fast is not None and fast.next is not None:   # fast needs 2 nodes ahead
            slow = slow.next                   # tortoise: 1 step
            fast = fast.next.next              # hare: 2 steps
            if slow is fast:                   # met -> there is a loop
                return True
        return False                           # fast fell off the end

    def __iter__(self) -> Iterator[T]:
        cur = self.head                        # start at head
        while cur is not None:                 # until the end
            yield cur.value                    # lazily produce values
            cur = cur.next                     # advance

    def __len__(self) -> int:
        return self._size                      # O(1) length


ll: LinkedList[int] = LinkedList()             # create
for v in (3, 2, 1):                            # prepend 3, then 2, then 1
    ll.prepend(v)                              # list becomes 1 -> 2 -> 3
print(list(ll), len(ll))                       # iterate and size
print(ll.delete(1), list(ll))                  # delete the head
print(ll.has_cycle())                          # no loop

# Output:
# [1, 2, 3] 3
# True [2, 3]
# False
```

---

## 🟠 JavaScript vs Python Comparison
Same idea; Python uses `None`, JS uses `null`. Python objects with `__slots__` or dataclasses reduce node memory. Neither language has a built-in singly linked list.

```python
# Python way
class Node:
    def __init__(self, val, nxt=None):
        self.val, self.next = val, nxt
head = Node(1, Node(2, Node(3)))
```
```javascript
// JavaScript way
class ListNode {
  constructor(val, next = null) { this.val = val; this.next = next; }
}
const head = new ListNode(1, new ListNode(2, new ListNode(3)));
```

---

## 🟠 FastAPI Connection
You rarely write a linked list in a FastAPI service, but the idea appears everywhere: middleware is a chain where each layer calls the next (`await call_next(request)`), and dependency graphs are resolved by following links. A paginated "next cursor" API is a linked list over HTTP: each page tells you where the next one is.

```python
from fastapi import FastAPI

app = FastAPI()
ITEMS: list[int] = list(range(1, 26))

@app.get("/items")
def items(cursor: int = 0, limit: int = 10) -> dict:
    page = ITEMS[cursor:cursor + limit]                     # current page
    nxt = cursor + limit if cursor + limit < len(ITEMS) else None   # pointer to next page
    return {"items": page, "next_cursor": nxt}              # None marks the end, like node.next
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: losing the rest of the list while reversing (overwriting `cur.next` before saving it).
✅ Correct: save `nxt = cur.next` first.

```python
# Wrong
cur.next = prev
cur = cur.next       # now cur is prev -> infinite loop / lost nodes
# Right
nxt = cur.next
cur.next = prev
prev, cur = cur, nxt
```

❌ Mistake 2: forgetting to handle deleting the head or an empty list.
✅ Correct: use a dummy node before the head, test empty and single-node lists.

❌ Mistake 3: `while fast.next.next:` crashes with `AttributeError` on short lists.
✅ Correct: `while fast is not None and fast.next is not None:`.

---

## 🧠 Tricky Interview Question
```python
class Node:
    def __init__(self, v): self.v, self.next = v, None

a = Node(1); b = Node(2); a.next = b
b = Node(3)
print(a.next.v)
```
Answer: `2`. `b = Node(3)` rebinds the name `b`; it does not change the object that `a.next` still points to. Python variables are references (labels), not boxes. To change the list you must assign to `a.next`.

---

## ⚫ Interview Questions + Answers

Q1: Array vs linked list?
A1: Array: O(1) index access, O(n) insert in the middle, cache friendly. Linked list: O(1) insert/delete at a known node, O(n) access, extra memory per pointer. In Python, list is usually faster in practice due to cache locality.

Q2: How do you find the middle node?
A2: Slow/fast pointers: when fast reaches the end, slow is at the middle. One pass, O(1) space.

Q3: How does Floyd's cycle detection work?
A3: Fast moves 2 steps, slow 1. Inside a loop the gap changes by 1 each iteration, so they must meet. O(n) time, O(1) space (a set of visited ids is O(n) space).

Q4: Why add a tail pointer?
A4: It makes `append` O(1). The cost: you must update it on delete of the last node.

Q5: Singly vs doubly linked list?
A5: Doubly has `prev` too: O(1) delete of a given node and backward walk, at the cost of more memory. LRU caches use a doubly linked list (topic 474).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Frequent insert/delete at the ends or at known nodes
- You build queues, LRU caches, or undo history
- You need stable references to nodes while the list changes

❌ Avoid when:
- You need random access by index (use list)
- Memory and cache speed matter (pointers cost more; Python lists win)
- A `deque` already does the job

---

## 📊 Visual Diagram
```
 head
  |
  v
+---+---+    +---+---+    +---+------+
| 1 | *-+--->| 2 | *-+--->| 3 | None |
+---+---+    +---+---+    +---+------+

 reverse: three pointers
   prev     cur      nxt
   None     [1]  ->  [2] -> [3]
   step 1:  [1] -> None ;  prev=[1], cur=[2]
   step 2:  [2] -> [1]  ;  prev=[2], cur=[3]
   step 3:  [3] -> [2]  ;  prev=[3]  => new head
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Node | One element: value + next | एक कड़ी |
| head | First node | पहला node |
| pointer | Reference to another node | दूसरे node का संदर्भ |
| dummy/sentinel | Fake node to simplify edge cases | नकली सहायक node |
| Floyd's algorithm | Slow/fast pointers for cycles | चक्र खोजने की तरकीब |
| in-place | Uses O(1) extra memory | बिना अतिरिक्त memory के |

---

## ⚡ 3-Line Summary
English: A linked list is nodes chained by `next` pointers; you only hold `head`.
English: Insert at head is O(1), search is O(n); reverse and cycle detection use pointer tricks.
English: Use dummy nodes and test empty, one-node and head-deletion cases.

Hindi: Linked list `next` pointers से जुड़े nodes हैं; आप सिर्फ `head` रखते हैं।
Hindi: Head पर insert O(1), search O(n); reverse और cycle detection pointer की चालों से होते हैं।
Hindi: Dummy node इस्तेमाल करो और खाली, एक node और head-delete के cases test करो।

---

## ➡️ Next Topic
**474. Implement LRU Cache** — combine a hash map with a doubly linked list to get O(1) get and put with eviction.

---
