---

# Q165. Explain Generators
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is a generator? Show lazy evaluation, memory savings, `yield from`, and what happens when a generator is exhausted.

---

## 💡 Quick Concept (2 lines only)
A generator function uses `yield` to produce values one at a time, pausing and resuming with its local state intact, so nothing is computed or stored until asked.
हिंदी: Generator `yield` से एक-एक value देता है और बीच में रुककर state याद रखता है — पूरी list memory में नहीं बनती।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import sys                                        # Step 1: to compare object sizes
from collections.abc import Iterator              # Step 2: type hint

def countdown(n: int) -> Iterator[int]:           # Step 3: generator function (contains yield)
    print("start")                                # runs only on the FIRST next()
    while n > 0:                                  # loop while there is work
        yield n                                   # pause here, hand n to the caller
        n -= 1                                    # resumes here on the next next()
    print("done")                                 # runs when the loop ends, before StopIteration

def chain(*iterables) -> Iterator:                # Step 4: delegate to sub-iterators
    for it in iterables:                          # each source
        yield from it                             # yield every item from it (3.3+)

# ============================================
# TEST CASES
# ============================================
g = countdown(3)                                  # nothing runs yet (lazy)
print(type(g).__name__)                           # Expected: generator
print(next(g))                                    # Expected: start  then  3
print(next(g))                                    # Expected: 2
print(list(g))                                    # Expected: done  then  [1]  (consumes the rest)
print(list(g))                                    # Expected: []   (exhausted: generators are one-shot)
try:                                              # next() on an exhausted generator
    next(g)                                       # raises StopIteration
except StopIteration:                             # caught
    print("StopIteration")                        # Expected: StopIteration

print(list(chain([1, 2], "ab", range(2))))        # Expected: [1, 2, 'a', 'b', 0, 1]

big_list = [i * i for i in range(1_000_000)]      # materialises 1M ints in memory
big_gen = (i * i for i in range(1_000_000))       # generator expression: constant memory
print(sys.getsizeof(big_list) > 100 * sys.getsizeof(big_gen))   # Expected: True (list ~8 MB, generator ~200 bytes)
print(sum(big_gen))                               # Expected: 333332833333500000
```

---

## 🔍 Why This Works (3 lines max)
Calling a generator function returns a generator object without running the body; each `next()` runs until the next `yield`. When the body ends, `StopIteration` is raised, and the generator cannot be restarted. Because values are produced on demand, memory stays constant.
हिंदी: Generator function call करने पर body नहीं चलती; हर `next()` अगले `yield` तक चलाता है, और ख़त्म होने पर StopIteration आता है।

---

## ⚡ Alternative Solution
```python
# Real use: stream a "huge" source lazily, and send() values into a generator
from itertools import islice                      # take the first N items lazily

def fib():                                        # infinite generator
    a, b = 0, 1                                   # first two numbers
    while True:                                   # never ends, but costs nothing until used
        yield a                                   # hand out a
        a, b = b, a + b                           # advance

print(list(islice(fib(), 10)))                    # Expected: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

def running_avg():                                # coroutine-style generator
    total, n = 0.0, 0                             # state
    avg = None                                    # first yield returns None
    while True:                                   # loop forever
        x = yield avg                             # receive a value sent by the caller
        total += x                                # update sum
        n += 1                                    # update count
        avg = total / n                           # new average

r = running_avg()                                 # create
next(r)                                           # prime: run to the first yield
print(r.send(10), r.send(20), r.send(60))         # Expected: 10.0 15.0 30.0
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: iterating a generator twice, expecting it to restart
squares = (x * x for x in range(3))
print(list(squares))      # [0, 1, 4]
print(list(squares))      # Actual: []   (already exhausted)

# ✅ Correct: re-create it (call the function again) or store results in a list/tuple if you need them twice
squares = (x * x for x in range(3))
print(list(squares))      # Expected: [0, 1, 4]
```

---

## 🎯 Interview Tip (1 line)
Say: "Generators are lazy, single-use iterators with O(1) memory; use them for streams and pipelines, and `yield from` to delegate."

---

## 🔗 Related Questions
→ Q025 (generator exhaustion) | Q026 (generator expression laziness) | Q027 (yield and send) | Q145 (complete generator) | Q220 (async generators)
