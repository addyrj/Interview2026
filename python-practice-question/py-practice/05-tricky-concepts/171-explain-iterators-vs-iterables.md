---

# Q171. Explain Iterators vs Iterables
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is the difference between an iterable and an iterator? Why can you loop over a list many times but a generator only once?

---

## 💡 Quick Concept (2 lines only)
An iterable has `__iter__` (returns a fresh iterator); an iterator has `__next__` and `__iter__` returning itself, and gets exhausted.
हिंदी: Iterable से `iter()` नया iterator देता है; iterator खुद `next()` से चलता है और एक बार खत्म हो जाता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from collections.abc import Iterable, Iterator   # Step 1: ABCs for isinstance checks

nums = [1, 2, 3]                             # list = iterable (not iterator)
print(isinstance(nums, Iterable), isinstance(nums, Iterator))  # Expected: True False
it = iter(nums)                              # Step 2: ask the iterable for an iterator
print(isinstance(it, Iterator), iter(it) is it)  # Expected: True True (iterator returns itself)
print(next(it), next(it), next(it))          # Expected: 1 2 3
try:
    next(it)                                 # Step 3: exhausted
except StopIteration:
    print("StopIteration")                   # Expected: StopIteration
print(list(it))                              # Expected: [] (iterator stays exhausted)
print(list(nums), list(nums))                # Expected: [1, 2, 3] [1, 2, 3] (new iterator every time)

# ============================================
# TEST CASES — custom classes
# ============================================
class Countdown:                             # ITERABLE: __iter__ builds a new iterator each time
    def __init__(self, start: int) -> None:
        self.start = start                   # remember start
    def __iter__(self) -> Iterator[int]:
        n = self.start                       # fresh state per iteration
        while n > 0:
            yield n                          # generator = iterator
            n -= 1                           # count down

class CountdownIter:                         # ITERATOR: holds its own state
    def __init__(self, start: int) -> None:
        self.n = start                       # state lives in the object
    def __iter__(self):
        return self                          # iterator returns itself
    def __next__(self) -> int:
        if self.n <= 0:
            raise StopIteration              # signal the end
        self.n -= 1                          # advance
        return self.n + 1                    # return previous value

c = Countdown(3)                             # iterable
print(list(c), list(c))                      # Expected: [3, 2, 1] [3, 2, 1] (reusable)
ci = CountdownIter(3)                        # iterator
print(list(ci), list(ci))                    # Expected: [3, 2, 1] [] (one-shot)
```

---

## 🔍 Why This Works (3 lines max)
`for x in obj` calls `iter(obj)` once, then `next()` repeatedly until `StopIteration`. A container returns a new iterator every time, so it is reusable; an iterator carries position state, so it is single-use.
हिंदी: `for` पहले `iter()` बुलाता है फिर `next()`; container हर बार नया iterator बनाता है, iterator खुद state रखता है।

---

## ⚡ Alternative Solution
```python
# Old sequence protocol: __getitem__ with IndexError also works with iter()
class Legacy:                                # no __iter__ at all
    def __getitem__(self, i: int) -> int:
        if i >= 3:
            raise IndexError                 # ends iteration
        return i * 10                        # item at index i
print(list(Legacy()))                        # Expected: [0, 10, 20]

# Two-argument iter(callable, sentinel): call until sentinel appears
print(list(iter(iter([5, 6]).__next__, 6)))  # Expected: [5]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: reusing a generator expression (it is an iterator)
g = (x * x for x in range(3))                # generator expression
print(list(g))                               # Output: [0, 1, 4]
print(list(g))                               # Output: []  (exhausted — silent bug)

# ✅ Correct: build a list, or recreate the generator when needed
squares = [x * x for x in range(3)]          # reusable list
print(squares, squares)                      # Output: [0, 1, 4] [0, 1, 4]
```

---

## 🎯 Interview Tip (1 line)
Say: "Iterable = has `__iter__`; iterator = has `__next__` and `__iter__` returning self; generators are iterators, so they're single-pass."

---

## 🔗 Related Questions
→ Q025 (generator exhaustion) | Q120 (iterator class) | Q147 (complete iterator class) | Q165 (generators) | Q297 (generators vs iterators)
