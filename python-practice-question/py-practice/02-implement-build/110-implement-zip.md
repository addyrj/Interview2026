---

# Q110. Implement zip()
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `my_zip(*iterables)` that lazily yields tuples pairing items by position and stops at the shortest input. It must work with any iterable (including generators), not only lists.

```python
list(my_zip([1, 2, 3], "ab"))   # [(1, 'a'), (2, 'b')]
```

---

## 💡 Quick Concept (2 lines only)
Turn every input into an iterator, then repeatedly pull one item from each and yield the tuple; stop as soon as any iterator runs out.
हिंदी: हर input से एक-एक item लेकर tuple बनाओ, और जो सबसे छोटा खत्म हो, वहीं रुक जाओ।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Any, Iterable, Iterator  # type hints

def my_zip(*iterables: Iterable[Any]) -> Iterator[tuple]:  # lazy zip
    iterators = [iter(it) for it in iterables]  # Step 1: make each input an iterator
    if not iterators:  # zip() with no arguments yields nothing
        return  # end generator immediately
    while True:  # Step 2: loop until the shortest input ends
        row = []  # items for the current tuple
        for it in iterators:  # take one item from each iterator
            try:
                row.append(next(it))  # pull the next item
            except StopIteration:  # this input is exhausted
                return  # stop the whole zip
        yield tuple(row)  # Step 3: emit one tuple

# ============================================
# TEST CASES
# ============================================
print(list(my_zip([1, 2, 3], "ab")))  # Expected: [(1, 'a'), (2, 'b')]
print(list(my_zip([1, 2], "ab", (True, False))))  # Expected: [(1, 'a', True), (2, 'b', False)]
print(list(my_zip()))  # Expected: []
print(list(my_zip([1, 2, 3])))  # Expected: [(1,), (2,), (3,)]
print(list(my_zip([], [1])))  # Expected: []
print(dict(my_zip("abc", range(3))))  # Expected: {'a': 0, 'b': 1, 'c': 2}
print(list(zip([1, 2, 3], "ab")))  # Expected: [(1, 'a'), (2, 'b')]  (built-in, same)
try:  # Python 3.10+: strict=True raises on unequal lengths
    list(zip([1, 2, 3], "ab", strict=True))  # built-in only (our version has no strict)
except ValueError as e:
    print(e)  # Expected: zip() argument 2 is shorter than argument 1
```

---

## 🔍 Why This Works (3 lines max)
Using `iter()` first makes it work for generators and files too (no indexing or `len`). The first exhausted iterator ends the loop, giving "shortest wins" behaviour.
हिंदी: iter() से generators पर भी चलता है, और पहला खत्म हुआ iterator पूरा zip रोक देता है।

---

## ⚡ Alternative Solution
```python
# Use next(it, sentinel) to avoid try/except
_END = object()  # unique end marker

def alt_zip(*its):
    its = [iter(i) for i in its]  # iterators
    while its:  # no inputs -> nothing
        row = tuple(next(i, _END) for i in its)  # next item or marker
        if _END in row: return  # any input exhausted -> stop
        yield row  # emit tuple

print(list(alt_zip([1, 2, 3], [4, 5])))  # Expected: [(1, 4), (2, 5)]

# Unzip trick with the built-in
print(list(zip(*[(1, "a"), (2, "b")])))  # Expected: [(1, 2), ('a', 'b')]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: indexing + len() only works for sequences, not iterators/generators
def bad(a, b):
    return [(a[i], b[i]) for i in range(min(len(a), len(b)))]
try:
    print(bad(iter([1, 2]), iter([3, 4])))
except TypeError as e:
    print(e)  # Output: object of type 'list_iterator' has no len()

# ✅ Correct: call iter() and use next(); lists still work: bad([1, 2], [3, 4]) -> [(1, 3), (2, 4)]
```

---

## 🎯 Interview Tip (1 line)
Say: "zip is lazy and stops at the shortest; use itertools.zip_longest to pad, or strict=True (3.10+) to catch length bugs."

---

## 🔗 Related Questions
→ Q061 (zip two lists manually) | Q111 (enumerate) | Q107 (map) | Q256 (zip/dict tricks)
