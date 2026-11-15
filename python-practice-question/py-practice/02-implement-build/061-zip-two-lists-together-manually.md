---

# Q061. Zip Two Lists Together Manually
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement `my_zip(a, b)` without using `zip()`. It should pair items by index and stop at the shorter list.

```python
my_zip([1, 2, 3], ["a", "b", "c"])  # [(1, 'a'), (2, 'b'), (3, 'c')]
```

---

## 💡 Quick Concept (2 lines only)
Loop `i` from 0 to `min(len(a), len(b))` and build `(a[i], b[i])` tuples. Real `zip` truncates to the shortest input.
हिंदी: सबसे छोटी list की length तक चलो और हर index के जोड़े बनाओ।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

from typing import Sequence  # type hint for indexable inputs

def my_zip(a: Sequence, b: Sequence) -> list[tuple]:
    out = []                                    # Step 1: result list of pairs
    for i in range(min(len(a), len(b))):        # Step 2: stop at the shorter sequence
        out.append((a[i], b[i]))                # Step 3: pair items at the same index
    return out                                  # Step 4: return the pairs

# ============================================
# TEST CASES
# ============================================

print(my_zip([1, 2, 3], ["a", "b", "c"]))   # Expected: [(1, 'a'), (2, 'b'), (3, 'c')]
print(my_zip([1, 2, 3], ["a"]))             # Expected: [(1, 'a')]
print(my_zip([], [1]))                      # Expected: []
```

---

## 🔍 Why This Works (3 lines max)
`min(len(a), len(b))` guarantees both indexes are valid. Each tuple groups the i-th items, matching `list(zip(a, b))`. This version needs indexable inputs, not generators.
हिंदी: `min` से length लेने पर कोई index बाहर नहीं जाता, इसलिए error नहीं आता।

---

## ⚡ Alternative Solution
```python
from itertools import zip_longest                         # pads the shorter input

def my_zip_gen(*its):                                     # any number of ANY iterables, lazy
    iters = [iter(i) for i in its]                        # turn each input into an iterator
    while True:                                           # keep producing rows
        row = []                                          # current row
        for i in iters:                                   # take one item from each
            try:
                row.append(next(i))                       # next item of this iterator
            except StopIteration:                         # any iterator exhausted -> stop
                return                                    # ends the generator
        yield tuple(row)                                  # emit the row

print(list(my_zip_gen([1, 2, 3], "abc", range(10, 13)))) # Expected: [(1, 'a', 10), (2, 'b', 11), (3, 'c', 12)]
print(list(zip_longest([1, 2, 3], "ab", fillvalue=None)))# Expected: [(1, 'a'), (2, 'b'), (3, None)]
try:
    list(zip([1, 2, 3], "ab", strict=True))              # Python 3.10+: strict length check
except ValueError as e:
    print(e)                                             # Expected: zip() argument 2 is shorter than argument 1
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: looping over len(a) only
def bad_zip(a, b):
    return [(a[i], b[i]) for i in range(len(a))]
# bad_zip([1, 2, 3], ["a"])  -> IndexError: list index out of range (verified)

# ❌ Subtle zip gotcha: the longer iterator loses one item when it is the FIRST argument
g = iter([1, 2, 3])
print(list(zip(g, "ab")), list(g))   # [(1, 'a'), (2, 'b')] [] <- 3 was consumed and dropped (verified)
# ✅ Put the shorter / unwanted-to-lose iterator first, or use zip_longest / strict=True
```

---

## 🎯 Interview Tip (1 line)
Mention truncation to the shortest input, `zip_longest` for padding, and `strict=True` (3.10+) for safety.

---

## 🔗 Related Questions
→ Q110 (implement zip) | Q111 (enumerate) | Q047 (zip unequal lengths output) | Q256 (zip/dict tricks)
