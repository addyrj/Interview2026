---

# Q111. Implement enumerate()
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement `my_enumerate(iterable, start=0)` that lazily yields `(index, item)` pairs. It must work on generators too, not only on lists.

```python
list(my_enumerate("abc"))            # [(0, 'a'), (1, 'b'), (2, 'c')]
list(my_enumerate(["x", "y"], 1))    # [(1, 'x'), (2, 'y')]
```

---

## 💡 Quick Concept (2 lines only)
Walk the iterable with a `for` loop, keep a counter, and `yield (counter, item)`. No `range(len(...))` needed.
हिंदी: iterable पर loop चलाओ, एक counter रखो, और (index, item) yield करते जाओ।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Iterable, Iterator, TypeVar  # type hints

T = TypeVar("T")  # item type

def my_enumerate(iterable: Iterable[T], start: int = 0) -> Iterator[tuple[int, T]]:  # lazy enumerate
    index = start  # Step 1: counter begins at `start`
    for item in iterable:  # Step 2: walk items one by one
        yield index, item  # Step 3: yield the (index, item) pair
        index += 1  # advance the counter

# ============================================
# TEST CASES
# ============================================
print(list(my_enumerate("abc")))  # Expected: [(0, 'a'), (1, 'b'), (2, 'c')]
print(list(my_enumerate(["x", "y"], start=1)))  # Expected: [(1, 'x'), (2, 'y')]
print(list(my_enumerate([])))  # Expected: []
print(dict(my_enumerate("ab", 10)))  # Expected: {10: 'a', 11: 'b'}
print(list(enumerate("abc")))  # Expected: [(0, 'a'), (1, 'b'), (2, 'c')]  (built-in, same)
for i, ch in my_enumerate("hi"):  # typical usage with unpacking
    print(i, ch)  # Expected: 0 h  then  1 i

def gen():  # generator has no len() or indexing
    yield "p"; yield "q"
print(list(my_enumerate(gen())))  # Expected: [(0, 'p'), (1, 'q')]
```

---

## 🔍 Why This Works (3 lines max)
A generator keeps its local `index` between yields, so no list is ever built. Because it only uses `for`, it works with any iterable, including generators and files.
हिंदी: generator अपना index याद रखता है, इसलिए list बनाने की ज़रूरत नहीं और हर iterable चलता है।

---

## ⚡ Alternative Solution
```python
# zip + itertools.count (same idea, one line)
import itertools  # count(start) is an infinite counter
def alt(it, start=0):
    return zip(itertools.count(start), it)  # pairs counter with items, stops with `it`

print(list(alt("abc", 5)))  # Expected: [(5, 'a'), (6, 'b'), (7, 'c')]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: range(len(it)) + indexing only works for sequences
def bad(it):
    out = []
    for i in range(len(it)):  # ❌ fails for iterators / generators
        out.append((i, it[i]))
    return out
print(bad("ab"))  # Output: [(0, 'a'), (1, 'b')]  (fine for str)
try:
    bad(iter("ab"))
except TypeError as e:
    print(e)  # Output: object of type 'str_ascii_iterator' has no len()  (exact type name may vary by version)

# ✅ Correct: loop with `for item in iterable` and a counter (or the built-in enumerate)
```

---

## 🎯 Interview Tip (1 line)
Say: "enumerate is lazy and replaces range(len(x)); the `start` argument avoids manual `i + 1` arithmetic."

---

## 🔗 Related Questions
→ Q110 (zip) | Q107 (map) | Q048 (enumerate and reversed output) | Q112 (range)
