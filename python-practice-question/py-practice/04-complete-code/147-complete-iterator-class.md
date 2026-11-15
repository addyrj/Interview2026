---

# Q147. Complete Iterator Class
# Category: Complete The Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Complete `Countdown` so `for n in Countdown(3)` prints 3, 2, 1 and the object can be iterated again.

```python
class Countdown:
    def __init__(self, start: int) -> None:
        self.start = start

    def __iter__(self) -> "____":                  # BLANK 1: iterator protocol: return what?
        self.current = self.start                  # reset so it is re-iterable
        return ____                                # BLANK 2

    def __next__(self) -> int:
        if self.current <= 0:
            raise ____                             # BLANK 3: signal "no more items"
        value = self.current
        self.current -= 1
        return value
```

---

## 💡 Quick Concept (2 lines only)
An iterator has `__iter__` (returns itself) and `__next__` (returns the next value or raises `StopIteration`); `for` loops call them for you.
हिंदी: Iterator में `__iter__` खुद को लौटाता है और `__next__` अगली value देता है, खत्म होने पर `StopIteration`।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
class Countdown:
    def __init__(self, start: int) -> None:        # Step 1: store the starting number
        self.start = start                         # immutable config
        self.current = start                       # mutable iteration state

    def __iter__(self) -> "Countdown":             # BLANK 1: returns an iterator (itself)
        self.current = self.start                  # reset: allows a second loop
        return self                                # BLANK 2: self has __next__

    def __next__(self) -> int:                     # Step 2: produce the next value
        if self.current <= 0:                      # exhausted?
            raise StopIteration                    # BLANK 3: tells `for` to stop
        value = self.current                       # remember current value
        self.current -= 1                          # advance state
        return value                               # hand it out


# ============================================
# TEST CASES
# ============================================
print(list(Countdown(3)))                          # Expected: [3, 2, 1]
c = Countdown(2)                                   # one object
print(list(c), list(c))                            # Expected: [2, 1] [2, 1]  (re-iterable thanks to reset)
print(list(Countdown(0)))                          # Expected: []

it = iter(Countdown(1))                            # manual protocol use
print(next(it))                                    # Expected: 1
try:
    next(it)                                       # exhausted
except StopIteration:
    print("done")                                  # Expected: done
```

---

## 🔍 Why This Works (3 lines max)
`for` calls `iter(obj)` once, then `next()` repeatedly until `StopIteration`. Resetting `current` in `__iter__` makes the object restartable, but two simultaneous loops would share state.
हिंदी: `for` पहले `iter()` फिर बार-बार `next()` बुलाता है; `StopIteration` पर रुक जाता है।

---

## ⚡ Alternative Solution
```python
# Better design: iterable (re-startable) separate from the iterator, via a generator __iter__
from typing import Iterator


class Countdown:
    def __init__(self, start: int) -> None:
        self.start = start                         # only configuration, no iteration state

    def __iter__(self) -> Iterator[int]:           # generator method -> new iterator per loop
        n = self.start                             # local state, not shared
        while n > 0:
            yield n                                # produce value
            n -= 1                                 # advance

c = Countdown(3)
print(list(c), list(c))                            # Expected: [3, 2, 1] [3, 2, 1]
print([(a, b) for a in Countdown(2) for b in Countdown(2)])  # Expected: [(2, 2), (2, 1), (1, 2), (1, 1)]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: raising StopIteration inside a generator (PEP 479) -> RuntimeError
# ❌ Wrong: __iter__ returns self without reset -> second loop yields nothing
# ❌ Wrong: __next__ never raises StopIteration -> infinite loop
# ✅ Correct: raise StopIteration in __next__ (class), or just `return` in a generator
```

---

## 🎯 Interview Tip (1 line)
Say: "Iterable = has `__iter__`; iterator = has `__next__` too; a generator method in `__iter__` gives a fresh iterator per loop."

---

## 🔗 Related Questions
→ Q120 (Fibonacci iterator) | Q145 (complete generator) | Q165 (explain generators) | Q171 (iterators vs iterables)
