---

# Q297. Generators vs iterators
# Category: INTERVIEW CLASSICS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is the difference between an iterable, an iterator and a generator? Implement the same countdown as a class-based iterator and as a generator, and show what happens when you iterate twice.

```python
# NOT RUN (question stub)
for n in Countdown(3):
    print(n)          # 3 2 1
```

---

## 💡 Quick Concept (2 lines only)
Iterable has `__iter__`; iterator has `__iter__` + `__next__` and is single-use. A generator is an iterator that Python builds for you from a function with `yield` (lazy, keeps its own state).
हिंदी: Iterator = `__next__` वाला one-time object; generator = `yield` वाला function जो अपने आप iterator बनता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

from collections.abc import Iterator, Iterable      # ABCs for hints


class Countdown:                                    # iterable AND iterator in one class
    def __init__(self, start: int) -> None:
        self.current = start                        # state lives on the object

    def __iter__(self) -> "Countdown":
        return self                                 # an iterator returns itself

    def __next__(self) -> int:
        if self.current <= 0:                       # nothing left
            raise StopIteration                     # signal the end
        value = self.current                        # value to hand out
        self.current -= 1                           # advance state
        return value                                # return current value


def countdown(start: int) -> Iterator[int]:         # same thing as a generator
    while start > 0:                                # loop until done
        yield start                                 # pause here, hand out value
        start -= 1                                  # resume here on next()


# ============================================
# TEST CASES
# ============================================

print(list(Countdown(3)))                           # class-based
print(list(countdown(3)))                           # generator-based

gen = countdown(2)                                  # create generator (nothing runs yet)
print(next(gen), next(gen))                         # manual stepping
try:
    next(gen)                                       # exhausted
except StopIteration:
    print("StopIteration")

print(list(gen))                                    # second pass over an exhausted generator

nums = [1, 2, 3]                                    # a LIST is iterable, not an iterator
print(iter(nums) is nums, iter(gen) is gen)         # list makes a NEW iterator, generator returns itself
print(sum(1 for _ in nums), sum(1 for _ in nums))   # lists can be looped repeatedly

# Expected output:
# [3, 2, 1]
# [3, 2, 1]
# 2 1
# StopIteration
# []
# False True
# 3 3
```

---

## 🔍 Why This Works (3 lines max)
`for` calls `iter(obj)` once, then `next()` until `StopIteration`. A generator function returns a generator object whose frame is suspended at each `yield`, so it is lazy and uses O(1) memory, but it is exhausted after one pass.
हिंदी: `for` पहले `iter()` फिर बार-बार `next()` चलाता है; generator lazy है और एक ही बार चलता है।

---

## ⚡ Alternative Solution
```python
import sys                                          # to compare memory

# Generator expression vs list comprehension: lazy vs eager
squares_list = [n * n for n in range(100_000)]      # builds everything now
squares_gen = (n * n for n in range(100_000))       # builds nothing yet
print(sys.getsizeof(squares_list) > sys.getsizeof(squares_gen))  # list is much bigger
print(sum(squares_gen))                             # consumed lazily, one value at a time

# yield from: delegate to another iterable
def chain(*its):
    for it in its:                                  # each iterable in turn
        yield from it                               # re-yield all its items

print(list(chain([1, 2], "ab", range(2))))

# Expected output:
# True
# 333328333350000
# [1, 2, 'a', 'b', 0, 1]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: reusing a generator / iterator expecting a fresh start
gen = (n for n in range(3))
print(list(gen))        # [0, 1, 2]
print(list(gen))        # [] <- already exhausted, no error!

# ✅ Correct: make a new generator, or use an iterable class whose __iter__ returns a NEW iterator
def make():
    return (n for n in range(3))

print(list(make()), list(make()))

# Expected output:
# [0, 1, 2]
# []
# [0, 1, 2] [0, 1, 2]
```

---

## 🎯 Interview Tip (1 line)
Say: "Every generator is an iterator, not every iterator is a generator; generators are lazy, single-use, and keep state in the suspended frame."

---

## 🔗 Related Questions
→ Q025 (generator exhaustion) | Q026 (generator expression laziness) | Q027 (yield and send) | Q120 (iterator class Fibonacci)
