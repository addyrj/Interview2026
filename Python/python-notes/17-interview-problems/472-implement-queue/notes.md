---

# 472. Implement Queue
# हिंदी में: Queue बनाना (FIFO Data Structure)

Runnable solution with tests: [main.py](./main.py) (run: `python main.py`, verified on Python 3.13).

---

## 🔵 Simple Definition (English)
A queue is a line: the first item that enters is the first item that leaves (FIFO = First In, First Out). You `enqueue` at the back and `dequeue` from the front. Both must be O(1).

## 🔵 सरल परिभाषा (Hindi)
Queue एक कतार (line) है: जो item सबसे पहले अंदर आता है, वही सबसे पहले बाहर जाता है (FIFO)। `enqueue` पीछे से होता है और `dequeue` आगे से। दोनों operations O(1) में होने चाहिए।

---

## 🔴 Problem it Solves
Many systems must process work in arrival order: print jobs, payment webhooks, Celery tasks, BFS graph traversal. A plain Python `list` looks fine, but `list.pop(0)` shifts every element, so it is O(n). With a million items this becomes painfully slow. The interviewer wants to see that you know the right structure (`deque` or ring buffer) and the trade-offs.

## 🔴 यह क्यों बना? (Hindi)
कई systems में काम आने के क्रम में ही होना चाहिए: print jobs, payment webhooks, Celery tasks, BFS traversal। सामान्य `list` ठीक लगती है, लेकिन `list.pop(0)` हर element को खिसकाता है, इसलिए O(n) है। दस लाख items पर यह बहुत धीमा हो जाता है। Interviewer देखना चाहता है कि आप सही structure (`deque` या ring buffer) और उनके trade-offs जानते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick storage: collections.deque (O(1) at both ends)
Step 2 → enqueue(x): append(x) puts x at the right (back)
Step 3 → dequeue(): popleft() removes from the left (front)
Step 4 → peek(): look at index 0 without removing
Step 5 → Guard the empty case: raise IndexError instead of returning garbage
Step 6 → Variant A: ring buffer = fixed array + head index + modulo wrap-around
Step 7 → Variant B: two stacks (inbox/outbox) = amortized O(1) dequeue
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Storage चुनो: collections.deque (दोनों सिरों पर O(1))
Step 2 → enqueue(x): append(x) से x दाईं तरफ (पीछे) जुड़ता है
Step 3 → dequeue(): popleft() बाईं तरफ (आगे) से हटाता है
Step 4 → peek(): बिना हटाए index 0 देखो
Step 5 → Empty case संभालो: garbage return करने की जगह IndexError raise करो
Step 6 → Variant A: ring buffer = fixed array + head index + modulo से घुमाव
Step 7 → Variant B: दो stacks (inbox/outbox) = amortized O(1) dequeue
```

---

## 🟡 Real World Example
Zomato order dispatch: orders arrive and kitchens must handle them oldest-first. A webhook receiver from Razorpay pushes events into a queue and a worker drains it in order. A rate-limited API client keeps a bounded queue (ring buffer) of the last N requests. In production you would use Redis/RabbitMQ/SQS, but the in-process `Queue` class is the same idea.

## 🟡 Real Example Hindi mein
Zomato order dispatch: orders आते हैं और kitchen को सबसे पुराना order पहले संभालना होता है। Razorpay का webhook receiver events को queue में डालता है और worker उन्हें क्रम से खाली करता है। Rate-limited API client पिछले N requests की bounded queue (ring buffer) रखता है। Production में Redis/RabbitMQ/SQS इस्तेमाल होता है, पर in-process `Queue` class का विचार वही है।

---

## 💻 Code Example — Basic
```python
# Basic queue with deque
from collections import deque                 # double-ended queue

q: deque[str] = deque()                        # create an empty queue
q.append("order-1")                            # enqueue at the back
q.append("order-2")                            # enqueue another
q.append("order-3")                            # and another
print(q[0])                                    # peek at the front item
print(q.popleft())                             # dequeue -> oldest item
print(q.popleft())                             # dequeue -> next oldest
print(list(q), len(q))                         # what is left

slow: list[int] = [1, 2, 3]                    # a list used as a queue (works, but slow)
print(slow.pop(0))                             # O(n): every other item shifts left

# Output:
# order-1
# order-1
# order-2
# ['order-3'] 1
# 1
```

## 💻 Code Example — Advanced
```python
# Production style: generic, typed, bounded ring buffer (full code + tests in main.py)
from typing import Generic, Optional, TypeVar

T = TypeVar("T")                               # element type


class CircularQueue(Generic[T]):
    """Fixed-capacity FIFO queue. enqueue/dequeue are O(1), no resizing."""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:                      # validate input early
            raise ValueError("capacity must be positive")
        self._buf: list[Optional[T]] = [None] * capacity   # preallocated slots
        self._cap = capacity                   # maximum size
        self._head = 0                         # index of the oldest item
        self._size = 0                         # how many items stored

    def enqueue(self, item: T) -> bool:
        if self._size == self._cap:            # full -> signal back-pressure
            return False
        self._buf[(self._head + self._size) % self._cap] = item   # write at the tail
        self._size += 1                        # count it
        return True

    def dequeue(self) -> T:
        if self._size == 0:                    # empty -> error
            raise IndexError("dequeue from empty queue")
        item = self._buf[self._head]           # read oldest item
        self._buf[self._head] = None           # drop the reference (helps GC)
        self._head = (self._head + 1) % self._cap   # advance head with wrap-around
        self._size -= 1                        # one less
        return item  # type: ignore[return-value]


cq: CircularQueue[str] = CircularQueue(2)      # capacity 2
print(cq.enqueue("a"), cq.enqueue("b"), cq.enqueue("c"))   # third is rejected
print(cq.dequeue())                            # frees a slot
print(cq.enqueue("c"))                         # now it fits (wraps around)
print(cq.dequeue(), cq.dequeue())              # b then c, FIFO preserved

# Output:
# True True False
# a
# True
# b c
```

---

## 🟠 JavaScript vs Python Comparison
In JS, `array.shift()` is the "dequeue" and it is also O(n) in theory (engines optimize small arrays). Python gives you a real O(1) structure: `deque`.

```python
# Python way
from collections import deque
q: deque[int] = deque([1, 2, 3])
q.append(4)            # enqueue
front = q.popleft()    # dequeue, O(1)
```
```javascript
// JavaScript way
const q = [1, 2, 3];
q.push(4);             // enqueue
const front = q.shift();  // dequeue, can be O(n) for large arrays
// For heavy use people write a linked list or two-index queue by hand
```

---

## 🟠 FastAPI Connection
FastAPI's `BackgroundTasks` and `asyncio.Queue` are queues. A common pattern: the endpoint puts a job on an `asyncio.Queue` and returns 202 immediately; a worker task consumes it. `asyncio.Queue(maxsize=N)` gives you the same back-pressure idea as our ring buffer (`put` waits when full).

```python
import asyncio
from fastapi import FastAPI

jobs: asyncio.Queue[str] = asyncio.Queue(maxsize=100)   # bounded async queue
app = FastAPI()

@app.post("/jobs", status_code=202)
async def submit(name: str) -> dict[str, int]:
    jobs.put_nowait(name)                  # raises QueueFull if over capacity
    return {"queued": jobs.qsize()}        # tell the client how many are waiting
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: using `list.pop(0)` as dequeue (O(n)).
✅ Correct: use `collections.deque.popleft()` (O(1)).

```python
# Wrong
items = list(range(1_000_000)); items.pop(0)
# Right
from collections import deque
items = deque(range(1_000_000)); items.popleft()
```

❌ Mistake 2: not handling the empty queue (`IndexError: pop from an empty deque` leaks a confusing message, or code returns `None` silently).
✅ Correct: raise a clear error or provide `is_empty()` / a default.

❌ Mistake 3: using `queue.Queue` in async code. It blocks the event loop.
✅ Correct: use `asyncio.Queue` in coroutines, `queue.Queue` only between threads.

---

## 🧠 Tricky Interview Question
```python
from collections import deque
d = deque([1, 2, 3], maxlen=3)
d.append(4)
print(list(d))
d.appendleft(0)
print(list(d))
```
Answer: `[2, 3, 4]` then `[0, 2, 3]`. With `maxlen`, a full deque silently discards from the opposite end: appending on the right drops the leftmost item, `appendleft` drops the rightmost. That makes `deque(maxlen=N)` a perfect "last N items" buffer, but it is also a silent data-loss trap.

---

## ⚫ Interview Questions + Answers

Q1: Why is `list.pop(0)` slow?
A1: Removing index 0 shifts all remaining elements one place left: O(n). `deque` is a doubly-linked list of blocks, so both ends are O(1).

Q2: Implement a queue using two stacks.
A2: Push to `inbox`. On dequeue, if `outbox` is empty, pop everything from `inbox` into `outbox` (this reverses order). Pop from `outbox`. Each element moves at most once, so amortized O(1). See `QueueWithTwoStacks` in main.py.

Q3: What is a circular queue and why use it?
A3: A fixed array with `head` and `size`; the tail index is `(head + size) % capacity`. No allocation, constant memory, natural back-pressure. Used in network buffers and logging.

Q4: Difference between `queue.Queue`, `asyncio.Queue`, `multiprocessing.Queue`?
A4: `queue.Queue` is thread-safe and blocking; `asyncio.Queue` is for coroutines in a single event loop (not thread-safe); `multiprocessing.Queue` pickles items across processes.

Q5: How would you implement a priority queue?
A5: `heapq` with `(priority, counter, item)` tuples; the counter keeps FIFO order for equal priorities and avoids comparing items. (See topic 077.)

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Work must be processed in arrival order (BFS, task pipelines, buffering)
- Producer and consumer run at different speeds
- You need a "last N items" window (`deque(maxlen=N)`)

❌ Avoid when:
- You need random access by index in the middle (use list)
- Priority matters more than arrival (use `heapq`)
- Work must survive a crash or span machines (use Redis/RabbitMQ/SQS, not memory)

---

## 📊 Visual Diagram
```
 enqueue -->  [ back ]                         [ front ]  --> dequeue
                 |                                 |
                 v                                 v
              +-----+-----+-----+-----+-----+-----+
              |  F  |  E  |  D  |  C  |  B  |  A  |
              +-----+-----+-----+-----+-----+-----+
 (A entered first, so A leaves first)

 Ring buffer, capacity 4, head=2, size=3:
   index:   0     1     2     3
          [ d ] [ _ ] [ b ] [ c ]     tail slot = (2+3) % 4 = 1
                        ^head
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| FIFO | First in, first out | जो पहले आए वह पहले जाए |
| enqueue | Add to the back | पीछे जोड़ना |
| dequeue | Remove from the front | आगे से हटाना |
| deque | Double-ended queue, O(1) at both ends | दोनों सिरों वाली queue |
| ring buffer | Fixed array that wraps around | गोल घूमने वाला buffer |
| back-pressure | Telling producers to slow down when full | भरे होने पर producer को रोकना |

---

## ⚡ 3-Line Summary
English: A queue is FIFO; enqueue at the back, dequeue at the front, both O(1).
English: Use `collections.deque`, never `list.pop(0)`; use a ring buffer for a fixed size.
English: Handle the empty case explicitly, and use real brokers for durable work.

Hindi: Queue FIFO होती है; पीछे जोड़ो, आगे से हटाओ, दोनों O(1)।
Hindi: `collections.deque` इस्तेमाल करो, `list.pop(0)` कभी नहीं; fixed size के लिए ring buffer।
Hindi: Empty case साफ़ संभालो, और टिकाऊ काम के लिए असली brokers इस्तेमाल करो।

---

## ➡️ Next Topic
**473. Implement Linked List** — the pointer-based structure that explains how deque blocks and LRU caches work internally.

---
