---

# Q254. Generator Tricks
# Category: PYTHONIC + MODERN PYTHON FEATURES
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show 4 useful generator tricks: (1) `yield from` delegation, (2) a lazy infinite generator with `itertools.islice`, (3) `send()` to make a running-average coroutine, (4) getting a generator's return value.

```python
def flatten(nested):
    ...                      # yield from?
# list(flatten([1, [2, [3, 4]], 5])) -> [1, 2, 3, 4, 5]
```

---

## 💡 Quick Concept (2 lines only)
A generator produces values lazily, one `yield` at a time, and keeps its local state between calls. `yield from` delegates to a sub-iterator and also captures its `return` value.
हिंदी: Generator values एक-एक करके देता है (lazy) — `yield from` किसी दूसरे iterable को सीधे delegate कर देता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from collections.abc import Generator, Iterator  # type hints
from itertools import islice                     # take first N from an infinite stream

# --- 1. yield from: recursive flatten ---
def flatten(nested: list) -> Iterator[int]:
    for item in nested:                          # walk each element
        if isinstance(item, list):               # nested list?
            yield from flatten(item)             # delegate to the recursive generator
        else:
            yield item                           # plain value

# --- 2. lazy infinite generator ---
def naturals(start: int = 1) -> Iterator[int]:
    n = start                                    # current value
    while True:                                  # infinite loop is safe: it is lazy
        yield n                                  # hand out one value, pause here
        n += 1                                   # resume here on next()

# --- 3. send(): running average coroutine ---
def averager() -> Generator[float, float, None]:
    total, count = 0.0, 0                        # state lives inside the generator
    avg = 0.0                                    # value handed back to the caller
    while True:
        value = yield avg                        # yield current avg, receive next value
        total += value                           # update running total
        count += 1                               # update count
        avg = total / count                      # recompute average

# --- 4. return value via yield from ---
def inner() -> Generator[int, None, str]:
    yield 1                                      # one value
    yield 2                                      # another value
    return "done"                                # becomes StopIteration.value

def outer() -> Generator[int, None, None]:
    result = yield from inner()                  # result captures inner's return
    print("inner returned:", result)             # prove we got it

# ============================================
# TEST CASES
# ============================================
print(list(flatten([1, [2, [3, 4]], 5])))        # recursive flatten
print(list(islice(naturals(), 5)))               # first 5 of infinite stream
a = averager()                                   # create the coroutine
next(a)                                          # prime it: run to first yield
print(a.send(10), a.send(20), a.send(30))        # running averages
print(list(outer()))                             # drains outer, prints return value

# Output:
# [1, 2, 3, 4, 5]
# [1, 2, 3, 4, 5]
# 10.0 15.0 20.0
# inner returned: done
# [1, 2]
```

---

## 🔍 Why This Works (3 lines max)
`yield` suspends the function and preserves its frame, so state (`n`, `total`) survives between calls. `send(x)` resumes the generator and makes the paused `yield` expression evaluate to `x`. `yield from` forwards values and `send()` calls to the sub-generator and evaluates to its `return` value.
हिंदी: `send(x)` से paused `yield` expression की value `x` बन जाती है — इसलिए generator state संभाल कर रखता है।

---

## ⚡ Alternative Solution
```python
# Generator expression + pipeline (constant memory)
from itertools import islice                     # slicing a lazy stream

squares = (n * n for n in range(1, 10**12))      # would be huge as a list; lazy here
evens = (s for s in squares if s % 2 == 0)       # chain another lazy stage
print(list(islice(evens, 3)))                    # only 3 items are ever computed

# Output:
# [4, 16, 36]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting to prime the coroutine before send()
def averager():
    total, count, avg = 0.0, 0, 0.0
    while True:
        value = yield avg
        total += value
        count += 1
        avg = total / count

a = averager()
try:
    a.send(10)                                   # ❌ not primed
except TypeError as e:
    print(e)                                     # can't send non-None value to a just-started generator

# ✅ Correct: call next(a) (or a.send(None)) first, then send values
a = averager()
next(a)
print(a.send(10))

# Output:
# can't send non-None value to a just-started generator
# 10.0
```

---

## 🎯 Interview Tip (1 line)
Say: "Generators are lazy and O(1) memory; `yield from` delegates, and a generator can only be consumed once."

---

## 🔗 Related Questions
→ Q025 (generator exhaustion) | Q026 (generator expression laziness) | Q027 (yield and send) | Q165 (explain generators) | Q297 (generators vs iterators)
