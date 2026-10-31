---

# 077. heapq Module
# हिंदी में: heapq Module (Priority Queue / Min-Heap)

---

## 🔵 Simple Definition (English)
`heapq` turns a normal Python list into a min-heap: a structure where the smallest item is always at index 0. You can push new items and pop the smallest one in O(log n) time. It is the standard way to build a priority queue in Python.

## 🔵 सरल परिभाषा (Hindi)
`heapq` एक सामान्य Python list को min-heap बना देता है: ऐसी structure जिसमें सबसे छोटा item हमेशा index 0 पर रहता है। नया item push करना और सबसे छोटा pop करना O(log n) में होता है। Python में priority queue बनाने का यही standard तरीका है।

---

## 🔴 Problem it Solves
Imagine you need the most urgent task from a list again and again. Calling `min(list)` each time costs O(n). Keeping the list sorted and inserting costs O(n) too. A heap gives you the smallest item instantly (O(1)) and keeps itself organized with only O(log n) work per push/pop. This is essential for schedulers, shortest-path (Dijkstra), top-K problems, and merging sorted streams.

## 🔴 यह क्यों बना? (Hindi)
मान लो आपको list में से सबसे urgent task बार-बार चाहिए। हर बार `min(list)` O(n) लेता है। List को sorted रखकर insert करना भी O(n) है। Heap सबसे छोटा item तुरंत (O(1)) देता है और हर push/pop पर सिर्फ O(log n) काम करके खुद को ठीक रखता है। Schedulers, shortest path (Dijkstra), top-K problems और sorted streams merge करने में यह जरूरी है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → A heap is a binary tree stored inside a plain list
Step 2 → Rule: parent <= both children. So the root (index 0) is the smallest
Step 3 → For index i: children are at 2*i+1 and 2*i+2, parent at (i-1)//2
Step 4 → heappush: add at the end, then "sift up" while smaller than parent
Step 5 → heappop: take index 0, move last item to root, "sift down"
Step 6 → The list is NOT fully sorted — only the heap rule holds

heappush(h, 1) on [3, 5, 8]:   [3,5,8,1] -> swap with parent -> [1,3,8,5]
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Heap एक binary tree है जो सामान्य list के अंदर रखी जाती है
Step 2 → Rule: parent <= दोनों children। इसलिए root (index 0) सबसे छोटा होता है
Step 3 → Index i के लिए: children 2*i+1 और 2*i+2 पर, parent (i-1)//2 पर
Step 4 → heappush: आखिर में जोड़ो, फिर parent से छोटा हो तो ऊपर "sift up"
Step 5 → heappop: index 0 निकालो, आखिरी item को root पर रखो, "sift down"
Step 6 → List पूरी sorted नहीं होती — सिर्फ heap rule सही रहता है
```

---

## 🟡 Real World Example
A payment backend processes jobs by priority: fraud-check and payment first, then email and SMS. Uber-style dispatch picks the nearest driver using a heap. A leaderboard keeps only the top 10 scores out of a million-event stream using `heapq.nlargest`. Dijkstra's algorithm in a delivery-route planner (Swiggy/Zomato) uses a heap to pick the next closest node.

## 🟡 Real Example Hindi mein
Payment backend jobs को priority से process करता है: पहले fraud-check और payment, फिर email और SMS। Uber जैसा dispatch सबसे नजदीकी driver heap से चुनता है। Leaderboard दस लाख events में से सिर्फ top 10 scores `heapq.nlargest` से रखता है। Delivery-route planner (Swiggy/Zomato) में Dijkstra algorithm अगला सबसे पास का node heap से चुनता है।

---

## 💻 Code Example — Basic
```python
# Basic heapq examples
import heapq                                  # heap functions live here

h: list[int] = []                             # a heap is just a list
for n in [5, 1, 8, 3]:                        # push items one by one
    heapq.heappush(h, n)                      # keeps the heap rule
print(h)                                      # not sorted! only h[0] is guaranteed smallest
print(heapq.heappop(h), h)                    # removes and returns smallest
print(h[0])                                   # peek at the smallest without removing

data: list[int] = [9, 4, 7, 1, 8]             # an ordinary list
heapq.heapify(data)                           # turn it into a heap in O(n), in place
print(data)                                   # heap order, smallest first
print(heapq.nlargest(2, data), heapq.nsmallest(2, data))   # top 2 and bottom 2
print(heapq.heappushpop(data, 0), heapq.heapreplace(data, 100))   # two combined operations

mx: list[int] = []                            # max-heap trick: store negatives
for n in [3, 9, 5]:                           # push negative of each number
    heapq.heappush(mx, -n)                    # smallest negative = largest number
print(-heapq.heappop(mx))                     # flip the sign back -> 9

# Output:
# [1, 3, 8, 5]
# 1 [3, 5, 8]
# 3
# [1, 4, 7, 9, 8]
# [9, 8] [1, 4]
# 0 1
# 9
```

## 💻 Code Example — Advanced
```python
# Production style: priority queue with FIFO tie-break, top-K, merge, streaming
import heapq                                  # heap functions
import itertools                              # counter for tie-breaking
from dataclasses import dataclass, field      # simple data class


@dataclass(order=True)                        # order=True compares fields in order
class Job:
    priority: int                             # lower number = more urgent
    seq: int                                  # insertion order, breaks ties
    name: str = field(compare=False)          # name is ignored in comparison


class PriorityQueue:
    """Priority queue: lowest priority number first, FIFO for equal priority."""

    def __init__(self) -> None:
        self._heap: list[Job] = []            # the heap storage
        self._counter = itertools.count()     # 0, 1, 2, ... for ordering

    def push(self, name: str, priority: int) -> None:
        job: Job = Job(priority, next(self._counter), name)   # build the job
        heapq.heappush(self._heap, job)       # insert in O(log n)

    def pop(self) -> str:
        if not self._heap:                    # nothing to pop
            raise IndexError("queue is empty")   # fail with a clear message
        return heapq.heappop(self._heap).name # smallest job's name

    def __len__(self) -> int:
        return len(self._heap)                # number of waiting jobs


pq: PriorityQueue = PriorityQueue()           # create queue
pq.push("email", 2)                           # low urgency
pq.push("payment", 1)                         # high urgency
pq.push("sms", 2)                             # low urgency, after email
pq.push("fraud-check", 1)                     # high urgency, after payment
while len(pq):                                # drain the queue
    print(pq.pop())                           # payment, fraud-check, email, sms
try:                                          # empty queue error handling
    pq.pop()                                  # nothing left
except IndexError as e:                       # catch it
    print("Error:", e)                        # Error: queue is empty


def top_k(scores: dict[str, int], k: int) -> list[tuple[str, int]]:
    """Return k users with highest scores."""
    return heapq.nlargest(k, scores.items(), key=lambda kv: kv[1])   # key picks the score


print(top_k({"a": 10, "b": 50, "c": 30, "d": 40}, 2))     # [('b', 50), ('d', 40)]


def merge_sorted(*lists: list[int]) -> list[int]:
    """Merge already-sorted lists lazily."""
    return list(heapq.merge(*lists))          # O(n log k), no full re-sort


print(merge_sorted([1, 4, 9], [2, 3, 10], [0, 5]))        # [0, 1, 2, 3, 4, 5, 9, 10]


def k_largest_stream(stream: list[int], k: int) -> list[int]:
    """Keep the k largest numbers using a min-heap of size k."""
    heap: list[int] = []                      # holds the current k best
    for x in stream:                          # one pass over data
        if len(heap) < k:                     # still filling up
            heapq.heappush(heap, x)           # just add
        elif x > heap[0]:                     # better than the worst of the best
            heapq.heapreplace(heap, x)        # pop smallest, push x
    return sorted(heap, reverse=True)         # final order, largest first


print(k_largest_stream([5, 1, 9, 3, 7, 8], 3))            # [9, 8, 7]

# Output:
# payment
# fraud-check
# email
# sms
# Error: queue is empty
# [('b', 50), ('d', 40)]
# [0, 1, 2, 3, 4, 5, 9, 10]
# [9, 8, 7]
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Built-in heap / priority queue | `heapq` (stdlib) | none — write your own or use a library |
| Heap type | min-heap only | n/a |
| Max-heap | push negatives | custom comparator |
| Top-K | `heapq.nlargest` | sort the whole array |
| Peek smallest | `h[0]` | n/a |

```python
# Python way — 4 lines
import heapq                               # stdlib, nothing to install
h: list[int] = []                          # plain list
heapq.heappush(h, 3)                       # push
heapq.heappush(h, 1)                       # push
print(heapq.heappop(h))                    # 1
```
```javascript
// JavaScript way — no built-in heap
const arr = [];                            // plain array
arr.push(3); arr.push(1);                  // push
arr.sort((a, b) => a - b);                 // O(n log n) every time!
console.log(arr.shift());                  // 1
// Real projects use npm packages like "heap-js" or "@datastructures-js/priority-queue"
```

Key difference: JavaScript has no heap in the standard library, so interview solutions must implement one by hand. In Python, `heapq` is ready to use, but it is a min-heap only and works on a plain list.

---

## 🟠 FastAPI Connection
FastAPI itself is async, but background work is often prioritized: premium users' jobs first, retries with timestamps (scheduled retry = heap ordered by next-run time), and rate limiters that expire oldest entries first. `asyncio.PriorityQueue` is built on `heapq`.

```python
# FastAPI example — priority job queue endpoint
import heapq                                          # heap functions
import itertools                                      # tie-break counter
from fastapi import FastAPI                           # FastAPI app

app: FastAPI = FastAPI()                              # create app
queue: list[tuple[int, int, str]] = []                # (priority, seq, task)
counter = itertools.count()                           # unique increasing number


@app.post("/jobs")                                    # POST /jobs?name=email&priority=2
def add_job(name: str, priority: int = 5) -> dict[str, int]:
    heapq.heappush(queue, (priority, next(counter), name))   # tuple compares left to right
    return {"waiting": len(queue)}                    # how many jobs wait


@app.post("/jobs/next")                               # POST /jobs/next
def next_job() -> dict[str, str]:
    if not queue:                                     # nothing to do
        return {"job": "none"}                        # empty reply
    return {"job": heapq.heappop(queue)[2]}           # most urgent job name
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting the heap list to be sorted
✅ Correct: use `heappop` to get sorted order, or `sorted()`

```python
import heapq
h = [5, 1, 8, 3]
heapq.heapify(h)
# Wrong
print(h)                                  # [1, 3, 8, 5]  <- not sorted
# Right
print([heapq.heappop(h) for _ in range(len(h))])   # [1, 3, 5, 8]
```

❌ Mistake 2: Using `h.append()` / `h.pop()` / `h.sort()` directly on a heap
✅ Correct: always use `heappush` / `heappop`

```python
import heapq
h = []
# Wrong — breaks the heap rule silently
h.append(5); h.append(1)         # [5, 1]  -> h[0] is 5, NOT the smallest!
# Right
h = []
heapq.heappush(h, 5); heapq.heappush(h, 1)   # h[0] is 1
```

❌ Mistake 3: Pushing tuples whose second item cannot be compared
✅ Correct: add a unique counter as the tie-breaker

```python
import heapq
h = []
heapq.heappush(h, (1, {"a": 1}))
# Wrong — same priority makes Python compare dicts
# heapq.heappush(h, (1, {"b": 2}))   # TypeError: '<' not supported between 'dict' and 'dict'
# Right
heapq.heappush(h, (1, 1, {"b": 2}))  # (priority, seq, payload) — seq decides
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import heapq
h = [3, 1, 2]
heapq.heappush(h, 0)
print(h)
print(heapq.nlargest(2, [1, 5, 3]))
print(heapq.heappop([5, 1, 3]))
```
Answer: The first line is `[0, 3, 2, 1]`. The list `[3, 1, 2]` was never heapified, so `heappush` just adds 0 at the end and sifts it up: the parent of index 3 is index 1 (value 1), so 0 swaps with 1; then the parent at index 0 (value 3) swaps with 0. The rest was never fixed, so the result is NOT a valid heap (3 sits above its child 1). Second line: `[5, 3]`. Third line: `5` — `heappop` assumes the list is already a heap, it returns the first item (5), not the smallest. Always call `heapify` first on existing data.

---

## ⚫ Interview Questions + Answers

Q1: What is the time complexity of heap operations?
A1: `heappush` O(log n), `heappop` O(log n), peek `h[0]` O(1), `heapify` O(n), `nlargest(k)` O(n log k). Building by pushing n items one by one is O(n log n), so prefer `heapify` for existing data.

Q2: How do you make a max-heap with `heapq`?
A2: `heapq` is min-heap only. Store negated values (`-x`) and negate again on pop. For objects, store tuples like `(-score, item)`, or give the class a reversed `__lt__`.

Q3: How do you find the K largest elements in a huge stream?
A3: Keep a MIN-heap of size K. For each number, if it is larger than `heap[0]`, replace the root. Memory is O(K) and time is O(n log K). The root is always the K-th largest so far. This is the classic "Top K frequent / largest" interview answer.

Q4: What is the difference between `heapq.nlargest(k, data)` and `sorted(data)[-k:]`?
A4: `nlargest` is O(n log k) and uses O(k) memory, better when k is small. Sorting is O(n log n). If k is close to n, `sorted` is simpler and about as fast. For k = 1 use `max()`.

Q5: How is `heapq` different from `queue.PriorityQueue`?
A5: `heapq` is a set of functions on a list: no locking, very fast, single-threaded. `queue.PriorityQueue` wraps heapq with thread-safe locks (use with threads). `asyncio.PriorityQueue` is for coroutines. All three are min-first.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You repeatedly need the smallest (or largest) item
- Task schedulers and priority queues
- Top-K problems, running median, merging K sorted lists
- Dijkstra / A* shortest path

❌ Avoid when:
- You need fully sorted data — use `sorted()`
- You need to search for arbitrary items or delete from the middle quickly (heap is bad at it)
- Multiple threads share the queue — use `queue.PriorityQueue`
- You only need the min once — just use `min()`

---

## 📊 Visual Diagram
```
heap list:  [1, 3, 8, 5]

Tree view:         1            index 0 (smallest, always)
                 /   \
                3     8         index 1, 2
               /
              5                 index 3

Rule: parent <= children      children of i -> 2i+1, 2i+2

heappush(0):  add at end    ->  [1,3,8,5,0]
              sift up       ->  swap with parent 3 -> swap with 1
              result        ->  [0,1,8,5,3]

heappop():    take 0, move last (3) to root, sift down
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Heap | Tree where parent <= children | Parent सबसे छोटा वाला tree |
| Priority queue | Queue where most urgent leaves first | Priority से निकलने वाली queue |
| heapify | Convert list to heap in O(n) | List को heap बनाना |
| Sift up / down | Move item to keep heap rule | Item को ऊपर / नीचे खिसकाना |
| Top-K | K largest or smallest items | सबसे बड़े / छोटे K items |
| Tie-breaker | Extra field to order equal priorities | बराबर priority में order तय करने वाला field |

---

## ⚡ 3-Line Summary
English: `heapq` makes a plain list into a min-heap where `h[0]` is always the smallest. Push and pop cost O(log n), and `nlargest` / `nsmallest` solve top-K problems. It is min-heap only, so use negatives for a max-heap and add a counter for tie-breaking.
Hindi: `heapq` सामान्य list को min-heap बनाता है जिसमें `h[0]` हमेशा सबसे छोटा होता है। Push और pop O(log n) में होते हैं, और `nlargest` / `nsmallest` से top-K हल होता है। यह सिर्फ min-heap है, max-heap के लिए negative values और tie-break के लिए counter लगाएं।

---

## ➡️ Next Topic
**078. bisect Module** — binary search and sorted insertion on a list: find positions in O(log n) and keep a list sorted as you add.
