---

# Q120. Implement an iterator class (Fibonacci)
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write a `Fibonacci(limit=None)` iterator class that yields Fibonacci numbers (0, 1, 1, 2, ...) using `__iter__` and `__next__`. With a limit it stops after that many items; without one it is infinite.

```python
list(Fibonacci(10))   # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

---

## 💡 Quick Concept (2 lines only)
An iterator has `__iter__` (returns itself) and `__next__` (returns next value or raises `StopIteration`). State lives on the instance.
हिंदी: Iterator में `__iter__` खुद को लौटाता है और `__next__` अगला value देता है या `StopIteration` उठाता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
class Fibonacci:
    def __init__(self, limit: int | None = None) -> None:
        self.limit = limit                               # Step 1: max count (None = infinite)
        self.a, self.b, self.count = 0, 1, 0             # state: F(n), F(n+1), items produced

    def __iter__(self) -> "Fibonacci":
        return self                                      # Step 2: iterator returns itself

    def __next__(self) -> int:
        if self.limit is not None and self.count >= self.limit:  # Step 3: finished?
            raise StopIteration                          # signal the end
        value = self.a                                   # current value
        self.a, self.b = self.b, self.a + self.b         # advance state
        self.count += 1                                  # track count
        return value                                     # give it out

# ============================================
# TEST CASES
# ============================================
import itertools                                         # for islice on the infinite version
print(list(Fibonacci(10)))                               # Expected: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
print(list(Fibonacci(0)))                                # Expected: []
print(list(itertools.islice(Fibonacci(), 8)))            # Expected: [0, 1, 1, 2, 3, 5, 8, 13]
fib = Fibonacci(3)
print(next(fib), next(fib), next(fib))                   # Expected: 0 1 1
try:
    next(fib)                                            # exhausted
except StopIteration:
    print("StopIteration")                               # Expected: StopIteration
print(list(fib))                                         # Expected: []  (an iterator is single-use)
print(sum(Fibonacci(10)))                                # Expected: 88
```

---

## 🔍 Why This Works (3 lines max)
`for`/`list()` call `iter(obj)` once, then `next()` until `StopIteration`. Because `__iter__` returns `self`, the object is a one-shot iterator — once exhausted it stays empty.
हिंदी: `for` loop बार-बार `__next__` बुलाता है जब तक `StopIteration` न आए।

---

## ⚡ Alternative Solution
```python
# Most Pythonic: a generator function (Python writes __iter__/__next__ for you)
from typing import Iterator                              # type hint
import itertools

def fib_gen(limit: int | None = None) -> Iterator[int]:
    a, b, n = 0, 1, 0                                    # state
    while limit is None or n < limit:                    # stop at limit
        yield a                                          # produce value
        a, b, n = b, a + b, n + 1                        # advance
print(list(fib_gen(10)))                                 # Output: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
print(list(itertools.islice(fib_gen(), 8)))              # Output: [0, 1, 1, 2, 3, 5, 8, 13]

# Re-usable ITERABLE (fresh iterator on every loop):
class FibIterable:
    def __init__(self, limit: int) -> None:
        self.limit = limit
    def __iter__(self) -> Iterator[int]:
        return fib_gen(self.limit)                       # new iterator each time
fi = FibIterable(5)
print(list(fi), list(fi))                                # Output: [0, 1, 1, 2, 3] [0, 1, 1, 2, 3]
f = Fibonacci(5)
print(list(f), list(f))                                  # Output: [0, 1, 1, 2, 3] []   (iterator is used up)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: __iter__ returns self but there is no __next__
class BadFib:
    def __init__(self, n): self.n = n
    def __iter__(self): return self
try:
    list(BadFib(3))
except TypeError as e:
    print("TypeError:", e)       # Output: TypeError: iter() returned non-iterator of type 'BadFib'

# ✅ Correct: implement __next__ too (or make __iter__ a generator)
```

---

## 🎯 Interview Tip (1 line)
Say: "Iterator = `__iter__` + `__next__` and is single-use; an iterable returns a fresh iterator from `__iter__`; generators are the concise way."

---

## 🔗 Related Questions
→ Q147 (complete iterator class) | Q171 (iterators vs iterables) | Q165 (generators) | Q297 (generators vs iterators)
