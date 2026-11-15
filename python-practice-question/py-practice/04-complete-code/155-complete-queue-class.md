---

# Q155. Complete Queue Class
# Category: Complete the Code
# Difficulty: ⭐ Easy

---

## ❓ Question
Fill in the blanks (`____`) to finish a FIFO `Queue` class backed by `collections.deque`.

```python
from collections import deque
from typing import Generic, TypeVar

T = TypeVar("T")

class Queue(Generic[T]):
    def __init__(self) -> None:
        self._items: deque[T] = ____()          # blank 1: create empty deque

    def enqueue(self, item: T) -> None:
        self._items.____(item)                  # blank 2: add at the back

    def dequeue(self) -> T:
        if not self._items:
            raise IndexError("dequeue from empty queue")
        return self._items.____()               # blank 3: remove from the FRONT in O(1)

    def peek(self) -> T:
        return self._items[____]                # blank 4: index of the front item

    def __len__(self) -> int:
        return ____(self._items)                # blank 5: number of items
```

---

## 💡 Quick Concept (2 lines only)
A queue is FIFO (first in, first out); `deque` gives O(1) at both ends, while `list.pop(0)` is O(n).
हिंदी: Queue में जो पहले आया वही पहले निकलता है — इसके लिए `deque` use करो, `list.pop(0)` slow है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from collections import deque            # Step 1: deque = O(1) append/popleft
from typing import Generic, TypeVar      # Step 2: typing helpers for a generic class

T = TypeVar("T")                         # Step 3: type variable for item type

class Queue(Generic[T]):                 # Step 4: generic FIFO queue
    def __init__(self) -> None:          # Step 5: constructor
        self._items: deque[T] = deque()  # Blank 1 -> deque  (empty storage)

    def enqueue(self, item: T) -> None:  # Step 6: push to the back
        self._items.append(item)         # Blank 2 -> append

    def dequeue(self) -> T:              # Step 7: pop from the front
        if not self._items:              # guard: empty queue
            raise IndexError("dequeue from empty queue")  # clear error message
        return self._items.popleft()     # Blank 3 -> popleft (O(1))

    def peek(self) -> T:                 # Step 8: look at the front without removing
        return self._items[0]            # Blank 4 -> 0 (front index)

    def __len__(self) -> int:            # Step 9: len(q) support
        return len(self._items)          # Blank 5 -> len

    def __bool__(self) -> bool:          # bonus: `if q:` is False when empty
        return bool(self._items)         # delegate to deque truthiness

# ============================================
# TEST CASES
# ============================================
q: Queue[int] = Queue()                  # create an empty int queue
q.enqueue(1)                             # queue: [1]
q.enqueue(2)                             # queue: [1, 2]
q.enqueue(3)                             # queue: [1, 2, 3]
print(q.dequeue())                       # Expected: 1
print(q.peek())                          # Expected: 2
print(len(q))                            # Expected: 2
q.dequeue()                              # remove 2
q.dequeue()                              # remove 3
print(bool(q))                           # Expected: False
try:                                     # dequeue from empty
    q.dequeue()                          # raises IndexError
except IndexError as e:                  # catch it
    print(e)                             # Expected: dequeue from empty queue
```

---

## 🔍 Why This Works (3 lines max)
`deque.append` adds at the right and `popleft` removes from the left, both O(1), so first-in is first-out. `list.pop(0)` shifts every element, making it O(n). `__len__` and `__bool__` make the queue behave like a built-in container.
हिंदी: `append` पीछे जोड़ता है और `popleft` आगे से निकालता है — दोनों O(1)।

---

## ⚡ Alternative Solution
```python
# Using queue.Queue (thread-safe, blocking) from the standard library
from queue import Queue as TQueue, Empty   # thread-safe FIFO queue

tq: TQueue[str] = TQueue()                 # create it
tq.put("a")                                # enqueue
tq.put("b")                                # enqueue
print(tq.get())                            # Expected: a
print(tq.qsize())                          # Expected: 1
tq.get()                                   # remove "b"
try:                                       # empty queue, non-blocking get
    tq.get_nowait()                        # raises queue.Empty immediately
except Empty:                              # catch it
    print("empty")                         # Expected: empty

# Use queue.Queue for threads, collections.deque for single-thread speed.
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: list.pop(0) is O(n) — slow for big queues
class SlowQueue:
    def __init__(self):
        self.items = []                    # plain list
    def dequeue(self):
        return self.items.pop(0)           # shifts ALL remaining items left

# ✅ Correct: deque.popleft() is O(1)
from collections import deque
fast = deque([1, 2, 3])                    # deque storage
print(fast.popleft())                      # Expected: 1
```

---

## 🎯 Interview Tip (1 line)
Say: "I use `deque` for O(1) popleft; `queue.Queue` when threads share it, and I never use `list.pop(0)` for a queue."

---

## 🔗 Related Questions
→ Q101 (implement queue) | Q154 (complete stack) | Q216 (asyncio.Queue) | D044 (queue using stacks)
