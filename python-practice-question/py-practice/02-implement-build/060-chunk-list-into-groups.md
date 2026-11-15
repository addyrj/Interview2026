---

# Q060. Chunk List into Groups
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `chunk(items, size)` that splits a sequence into groups of `size`. The last group may be shorter.

```python
chunk([1, 2, 3, 4, 5, 6, 7], 3)  # [[1, 2, 3], [4, 5, 6], [7]]
```

---

## 💡 Quick Concept (2 lines only)
Step through the indices with `range(0, len, size)` and slice `items[i:i+size]`. Slicing never raises an error past the end, so the last chunk is simply shorter.
हिंदी: `range` में `size` की step लेकर slice काटो — आखिरी chunk अपने-आप छोटा बनता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

from typing import Sequence  # type hint for lists, strings, tuples

def chunk(items: Sequence, size: int) -> list[list]:
    if size <= 0:                                           # Step 1: validate size
        raise ValueError("size must be > 0")                # size 0 would loop forever / error
    return [list(items[i:i + size])                         # Step 3: slice one chunk -> list
            for i in range(0, len(items), size)]            # Step 2: start index of each chunk

# ============================================
# TEST CASES
# ============================================

print(chunk([1, 2, 3, 4, 5, 6, 7], 3))   # Expected: [[1, 2, 3], [4, 5, 6], [7]]
print(chunk([], 3))                      # Expected: []
print(chunk("abcde", 2))                 # Expected: [['a', 'b'], ['c', 'd'], ['e']]
try:
    chunk([1], 0)                        # invalid size
except ValueError as e:
    print(e)                             # Expected: size must be > 0
```

---

## 🔍 Why This Works (3 lines max)
`range(0, n, size)` yields 0, size, 2*size... and each slice takes up to `size` items. Out-of-range slice ends are silently clipped, which handles the remainder chunk.
हिंदी: Slice की end index list से बड़ी हो तो भी error नहीं आता, बस जितना बचा है उतना मिलता है।

---

## ⚡ Alternative Solution
```python
from itertools import batched, islice       # batched is new in Python 3.12+

print(list(batched([1, 2, 3, 4, 5, 6, 7], 3)))   # Expected: [(1, 2, 3), (4, 5, 6), (7,)] (tuples!)

def chunk_iter(it, size):                   # works for ANY iterable, even generators
    it = iter(it)                           # make sure we have an iterator
    while batch := list(islice(it, size)):  # take next `size` items; empty list ends loop
        yield batch                         # hand out one chunk lazily

print(list(chunk_iter(range(5), 2)))        # Expected: [[0, 1], [2, 3], [4]]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting to validate size - range() step 0 raises a confusing error
# list(range(0, 5, 0))  -> ValueError: range() arg 3 must not be zero (verified)

# ❌ Wrong: slicing a generator - generators are not subscriptable
# ✅ Correct: validate size first; use islice-based chunk_iter for non-sequences
```

---

## 🎯 Interview Tip (1 line)
Say: "Slicing for sequences, `islice` for streams, and `itertools.batched` in 3.12+ (returns tuples)."

---

## 🔗 Related Questions
→ Q058 (flatten) | Q070 (list rotation) | Q182 (pagination helper) | Q217 (batch API calls)
