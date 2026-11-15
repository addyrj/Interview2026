---

# Q101. Implement Queue
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement a `Queue` class (FIFO) with `enqueue`, `dequeue`, `peek`, `is_empty` and `len()`, where both `enqueue` and `dequeue` are O(1).

```python
q = Queue()
q.enqueue("a"); q.enqueue("b")
q.dequeue()   # "a"  (first in, first out)
```

---

## 💡 Quick Concept (2 lines only)
A queue is First-In-First-Out: add at the back, remove from the front. Use `collections.deque` — `list.pop(0)` is O(n).
हिंदी: Queue में जो पहले आया वही पहले निकलता है — इसके लिए list नहीं, deque इस्तेमाल करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from collections import deque  # O(1) operations at both ends
from typing import Generic, TypeVar  # typed generic container

T = TypeVar("T")  # element type

class Queue(Generic[T]):  # FIFO queue
    def __init__(self) -> None:  # constructor
        self._items: deque[T] = deque()  # Step 1: deque as backing store

    def enqueue(self, item: T) -> None:  # add to the back
        self._items.append(item)  # Step 2: O(1)

    def dequeue(self) -> T:  # remove from the front
        if not self._items:  # Step 3: empty check
            raise IndexError("dequeue from empty queue")  # clear error
        return self._items.popleft()  # O(1) (list.pop(0) would be O(n))

    def peek(self) -> T:  # front item without removing
        if not self._items:  # empty check
            raise IndexError("peek from empty queue")  # clear error
        return self._items[0]  # index 0 is the front

    def is_empty(self) -> bool:  # emptiness test
        return not self._items  # True when empty

    def __len__(self) -> int:  # len(queue)
        return len(self._items)  # number of items

    def __repr__(self) -> str:  # debug output
        return f"Queue({list(self._items)})"  # front -> back

# ============================================
# TEST CASES
# ============================================
q: Queue[str] = Queue()  # new empty queue
q.enqueue("a"); q.enqueue("b"); q.enqueue("c")  # add three
print(q)  # Expected: Queue(['a', 'b', 'c'])
print(q.dequeue())  # Expected: a
print(q.peek())  # Expected: b
print(len(q))  # Expected: 2
print(q.is_empty())  # Expected: False
q.dequeue(); q.dequeue()  # drain it
try:  # dequeue from empty
    q.dequeue()  # should raise
except IndexError as e:  # catch
    print(e)  # Expected: dequeue from empty queue
```

---

## 🔍 Why This Works (3 lines max)
`deque` is a doubly linked block list: `append` and `popleft` are O(1). A list shifts every element on `pop(0)`, making each dequeue O(n).
हिंदी: deque दोनों सिरों पर O(1) है, list का pop(0) सारे elements खिसकाता है।

---

## ⚡ Alternative Solution
```python
# Classic interview twist: queue using TWO stacks (amortized O(1))
class TwoStackQueue:
    def __init__(self) -> None:
        self.inbox: list[int] = []  # receives new items
        self.outbox: list[int] = []  # serves items in FIFO order

    def enqueue(self, x: int) -> None:
        self.inbox.append(x)  # push on inbox

    def dequeue(self) -> int:
        if not self.outbox:  # outbox empty: refill
            while self.inbox:  # move everything over
                self.outbox.append(self.inbox.pop())  # reverses the order
        return self.outbox.pop()  # oldest item is now on top

t = TwoStackQueue()  # new queue
t.enqueue(1); t.enqueue(2); t.enqueue(3)  # add 1,2,3
print(t.dequeue(), t.dequeue())  # Expected: 1 2

# Measured: popleft() on a 100k deque beats pop(0) on a 100k list (timings vary by machine)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: list.pop(0) -> O(n) per dequeue, slow for big queues
items = [1, 2, 3]
items.pop(0)  # shifts every remaining element left

# ✅ Correct: deque.popleft() -> O(1)
from collections import deque
d = deque([1, 2, 3])
print(d.popleft())  # Expected: 1
# (For thread/async producer-consumer use queue.Queue / asyncio.Queue instead)
```

---

## 🎯 Interview Tip (1 line)
Say: "Queue = FIFO; I'd use deque for O(1) both ends — and mention queue.Queue / asyncio.Queue for concurrency."

---

## 🔗 Related Questions
→ Q100 (stack) | Q102 (linked list) | Q155 (complete queue class) | Q184 (request queue) | Q216 (producer-consumer)
