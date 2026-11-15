---

# Q025. Generator exhaustion output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```python
g = (i for i in range(3))
print(list(g), list(g), sum(g))         # (a)

def gen():
    yield 1
    yield 2

gg = gen()
print(next(gg), next(gg))               # (b)
try:
    next(gg)                            # (c)
except StopIteration:
    print("StopIteration")
print(list(gg))                         # (d)

lst = [1, 2, 3]
it = iter(lst)
print(list(it), list(it), list(iter(lst)))   # (e)
```

---

## 💡 Quick Concept (2 lines only)
A generator is a one-shot iterator: once consumed it stays empty and never restarts. Lists are re-iterable because each `iter()` call creates a fresh iterator.
हिंदी: Generator सिर्फ एक बार चलता है; दोबारा loop करने पर खाली मिलता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
g = (i for i in range(3))                    # Step 1: generator expression
print(list(g), list(g), sum(g))              # (a) [0, 1, 2] [] 0 (second use is already exhausted)

def gen():                                   # Step 2: generator function
    yield 1                                  # First value
    yield 2                                  # Second value

gg = gen()                                   # Create generator object
print(next(gg), next(gg))                    # (b) 1 2
try:
    next(gg)                                 # (c) nothing left -> StopIteration
except StopIteration:
    print("StopIteration")                   # Printed
print(list(gg))                              # (d) [] (stays exhausted)

lst = [1, 2, 3]                              # Step 3: list is an iterable, not an iterator
it = iter(lst)                               # One iterator object
print(list(it), list(it), list(iter(lst)))   # (e) [1, 2, 3] [] [1, 2, 3]

# ============================================
# TEST CASES
# ============================================
# Expected output (real run, Python 3.13):
# [0, 1, 2] [] 0
# 1 2
# StopIteration
# []
# [1, 2, 3] [] [1, 2, 3]
```

---

## 🔍 Why This Works (3 lines max)
A generator is its own iterator (`iter(g) is g`) and keeps a single position. When it finishes it raises StopIteration forever; `list()`, `sum()` and `for` handle that quietly. `map`/`filter`/`zip` objects behave the same way.
हिंदी: दूसरी बार चाहिए तो generator दोबारा बनाइए या `list()` में store कर लीजिए।

---

## ⚡ Alternative Solution
```python
from itertools import tee                    # Split one iterator into several

def gen():                                   # Generator function
    yield 1                                  # Value 1
    yield 2                                  # Value 2

a, b = tee(gen())                            # Two independent iterators (buffers values)
print(list(a), list(b))                      # [1, 2] [1, 2]

m = map(str, [1, 2])                         # map objects are one-shot too
print(list(m), list(m))                      # ['1', '2'] []

print(iter(gen()).__class__.__name__)        # generator

# Re-iterable wrapper: a class with __iter__ that returns a NEW generator each time
class Repeatable:
    def __iter__(self):                      # Called on every for-loop
        yield 1                              # Fresh generator each time
        yield 2                              # Second value
r = Repeatable()                             # Instance
print(list(r), list(r))                      # [1, 2] [1, 2]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: iterating the same generator twice
squares = (n * n for n in range(3))           # Generator
total = sum(squares)                          # 5
count = len(list(squares))                    # 0  <- already consumed!
print(total, count)                           # 5 0

# ✅ Correct: materialise once, or build a new generator
squares = [n * n for n in range(3)]           # List can be reused
print(sum(squares), len(squares))             # 5 3
```

---

## 🎯 Interview Tip (1 line)
Say: "Generators are single-pass iterators — exhausted means empty forever; use a list, `itertools.tee`, or an iterable class if you need multiple passes."

---

## 🔗 Related Questions
→ Q026 (generator expression laziness) | Q027 (yield and send) | Q120 (iterator class)
