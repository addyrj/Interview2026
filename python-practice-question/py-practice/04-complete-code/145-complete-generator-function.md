---

# Q145. Complete Generator Function
# Category: Complete The Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Complete `batched(iterable, n)` as a generator that yields lists of at most `n` items, lazily (works on infinite iterables).

```python
from typing import Iterable, Iterator


def batched(iterable: Iterable, n: int) -> Iterator[list]:
    batch: list = []                               # current batch
    for item in iterable:
        batch.append(item)                         # add item
        if len(batch) == n:                        # batch full?
            ____ batch                             # BLANK 1: hand it to the caller
            batch = ____                           # BLANK 2: start a new batch
    if ____:                                       # BLANK 3: leftover items?
        yield batch
```

---

## 💡 Quick Concept (2 lines only)
A generator uses `yield` to produce values one at a time and pauses between them, so it needs almost no memory and can handle infinite streams.
हिंदी: Generator `yield` से एक-एक value देता है और बीच में रुक जाता है — memory बहुत कम लगती है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from itertools import count, islice                # used in the infinite-stream test
from typing import Iterable, Iterator


def batched(iterable: Iterable, n: int) -> Iterator[list]:  # generator function
    batch: list = []                               # Step 1: current batch
    for item in iterable:                          # Step 2: pull items lazily
        batch.append(item)                         # add to the batch
        if len(batch) == n:                        # full?
            yield batch                            # BLANK 1: emit and pause here
            batch = []                             # BLANK 2: fresh list (do not reuse the emitted one)
    if batch:                                      # BLANK 3: Step 3: emit the partial last batch
        yield batch


# ============================================
# TEST CASES
# ============================================
print(list(batched([1, 2, 3, 4, 5], 2)))           # Expected: [[1, 2], [3, 4], [5]]
print(list(batched("abcdef", 3)))                  # Expected: [['a', 'b', 'c'], ['d', 'e', 'f']]
print(list(batched([], 3)))                        # Expected: []

gen = batched(count(1), 3)                         # infinite source: 1, 2, 3, ...
print(list(islice(gen, 2)))                        # Expected: [[1, 2, 3], [4, 5, 6]]
print(next(batched(range(10), 4)))                 # Expected: [0, 1, 2, 3]
```

---

## 🔍 Why This Works (3 lines max)
Each `yield` suspends the function and keeps its local state (`batch`). Resetting `batch = []` after yielding matters because the caller still holds the old list. The final `if batch` flushes the remainder.
हिंदी: `yield` function को pause करता है और local state सुरक्षित रखता है; आख़िर में बचा हुआ batch भी भेजना ज़रूरी है।

---

## ⚡ Alternative Solution
```python
# Python 3.12+: itertools.batched (yields tuples) or a slice-based version for sequences
from itertools import batched as ibatched, islice
from typing import Iterable, Iterator

print(list(ibatched([1, 2, 3, 4, 5], 2)))          # Expected: [(1, 2), (3, 4), (5,)]

def batched2(iterable: Iterable, n: int) -> Iterator[list]:
    it = iter(iterable)                            # one shared iterator
    while chunk := list(islice(it, n)):            # take n items; stop when empty
        yield chunk                                # emit chunk

print(list(batched2(range(5), 2)))                 # Expected: [[0, 1], [2, 3], [4]]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: batch.clear() instead of batch = []  -> yielded lists are the SAME object
#    list(batched(range(4), 2)) would give [[], []] after clear() is called on the shared list
# ❌ Wrong: forgetting the final partial batch -> last items silently lost
# ❌ Wrong: return [..] list instead of yield -> not lazy, infinite input hangs
# ✅ Correct: create a new list after each yield and flush the remainder
```

---

## 🎯 Interview Tip (1 line)
Say: "Generators are lazy and memory-O(1) per item; I'd use `itertools.batched` in 3.12+, but I can write it by hand."

---

## 🔗 Related Questions
→ Q060 (chunk list) | Q120 (iterator class) | Q147 (complete iterator) | Q165 (explain generators) | Q279 (generators vs lists)
