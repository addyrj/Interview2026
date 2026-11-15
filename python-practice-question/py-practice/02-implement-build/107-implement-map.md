---

# Q107. Implement map()
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement your own `my_map(fn, iterable)` that behaves like built-in `map`: it must be **lazy** (return an iterator, not a list). Bonus: support multiple iterables.

```python
list(my_map(lambda x: x * 2, [1, 2, 3]))   # [2, 4, 6]
```

---

## 💡 Quick Concept (2 lines only)
`map` applies a function to each item and yields results one at a time — it never builds the full list. A generator function is the natural way to write it.
हिंदी: map हर item पर function लगाता है और results एक-एक करके देता है — list नहीं बनाता (lazy)।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Callable, Iterable, Iterator, TypeVar  # type hints

T = TypeVar("T")  # input item type
R = TypeVar("R")  # output item type

def my_map(fn: Callable[[T], R], iterable: Iterable[T]) -> Iterator[R]:  # lazy map
    for item in iterable:  # Step 1: walk the input one item at a time
        yield fn(item)  # Step 2: apply fn and yield (generator => lazy)

# ============================================
# TEST CASES
# ============================================
print(list(my_map(lambda x: x * 2, [1, 2, 3])))  # Expected: [2, 4, 6]
print(list(my_map(str.upper, "abc")))  # Expected: ['A', 'B', 'C']
m = my_map(abs, [-1, -2])  # create the iterator (nothing computed yet)
print(type(m).__name__)  # Expected: generator
print(next(m), next(m))  # Expected: 1 2
try:  # asking for a third item
    next(m)  # nothing left
except StopIteration:  # generator is exhausted
    print("exhausted")  # Expected: exhausted
print(list(my_map(lambda x: x, [])))  # Expected: []

# Multiple iterables (stops at the shortest, like the built-in)
def my_map_multi(fn, *iterables):  # n-ary version
    for args in zip(*iterables):  # zip stops at the shortest input
        yield fn(*args)  # call fn with one item from each

print(list(my_map_multi(lambda a, b: a + b, [1, 2, 3], [10, 20])))  # Expected: [11, 22]
print(list(map(lambda a, b: a + b, [1, 2, 3], [10, 20])))  # Expected: [11, 22]  (built-in, same)
```

---

## 🔍 Why This Works (3 lines max)
A generator runs only when asked for the next value, so work is deferred and memory stays O(1). It also works on infinite iterables.
हिंदी: generator तभी चलता है जब next माँगा जाए, इसलिए memory कम लगती है और infinite input भी चलता है।

---

## ⚡ Alternative Solution
```python
# Generator expression: one line, same laziness
def alt(fn, it):
    return (fn(x) for x in it)  # parentheses = lazy generator expression

print(list(alt(len, ["a", "bb"])))  # Expected: [1, 2]

# Works on infinite iterators, because it is lazy
import itertools  # for islice
def gen_nat():  # 0, 1, 2, ... forever
    n = 0
    while True:
        yield n; n += 1
print(list(itertools.islice(my_map(lambda x: x * x, gen_nat()), 4)))  # Expected: [0, 1, 4, 9]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: list comprehension -> eager; computes everything immediately, hangs on infinite input
def bad(fn, it):
    return [fn(x) for x in it]  # ❌ returns a list, not an iterator
# next(bad(...)) -> TypeError: 'list' object is not an iterator

# ✅ Correct: yield (generator function) or a generator expression
```

---

## 🎯 Interview Tip (1 line)
Say: "map is lazy in Python 3 — I'd write it as a generator, and in practice prefer a list/generator comprehension for readability."

---

## 🔗 Related Questions
→ Q108 (filter) | Q109 (reduce) | Q110 (zip) | Q303 (comprehension vs map/filter)
