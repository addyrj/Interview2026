---

# Q160. Complete a Class with __getitem__ and __len__
# Category: Complete the Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks (`____`) so `Playlist` supports `len()`, indexing, slicing, `in`, and `for` loops, using only `__len__` and `__getitem__`.

```python
class Playlist:
    def __init__(self, *songs: str) -> None:
        self._songs = list(songs)

    def ____(self) -> int:                      # blank 1: len(p)
        return len(self._songs)

    def ____(self, index):                      # blank 2: p[i] and p[a:b]
        if isinstance(index, ____):             # blank 3: slice object?
            return Playlist(*self._songs[index])
        return self._songs[index]
```

---

## 💡 Quick Concept (2 lines only)
`__len__` powers `len()`, and `__getitem__` powers `obj[i]`, slicing, and even `for`/`in` through the old sequence protocol.
हिंदी: `__len__` और `__getitem__` लिखते ही class में len, index, slice और for-loop सब चलने लगते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
class Playlist:                                   # Step 1: custom sequence-like class
    def __init__(self, *songs: str) -> None:      # Step 2: take any number of songs
        self._songs = list(songs)                 # store them privately

    def __len__(self) -> int:                     # Blank 1 -> __len__
        return len(self._songs)                   # delegate to the list

    def __getitem__(self, index):                 # Blank 2 -> __getitem__
        if isinstance(index, slice):              # Blank 3 -> slice (p[1:3] passes a slice)
            return Playlist(*self._songs[index])  # return a new Playlist, not a plain list
        return self._songs[index]                 # int index (negative works, IndexError ends loops)

    def __repr__(self) -> str:                    # nice printing
        return f"Playlist({', '.join(map(repr, self._songs))})"   # readable form

# ============================================
# TEST CASES
# ============================================
p = Playlist("a", "b", "c", "d")                  # build a playlist
print(len(p))                                     # Expected: 4
print(p[0], p[-1])                                # Expected: a d
print(p[1:3])                                     # Expected: Playlist('b', 'c')
print("c" in p)                                   # Expected: True   (falls back to __getitem__ loop)
print([s.upper() for s in p])                     # Expected: ['A', 'B', 'C', 'D']
print(list(reversed(p)))                          # Expected: ['d', 'c', 'b', 'a']  (uses __len__ + __getitem__)
try:                                              # out of range index
    p[10]                                         # list raises IndexError
except IndexError as e:                           # catch it
    print(e)                                      # Expected: list index out of range
```

---

## 🔍 Why This Works (3 lines max)
`len()` calls `__len__`; `p[x]` calls `__getitem__(x)`, passing a `slice` object for `p[a:b]`. With no `__iter__`, Python iterates by calling `__getitem__(0), (1), ...` until `IndexError`, and `reversed()` uses `__len__` too.
हिंदी: `__iter__` न हो तो Python 0,1,2... index से `__getitem__` बुलाकर IndexError तक loop चलाता है।

---

## ⚡ Alternative Solution
```python
# Inherit from collections.abc.Sequence: only __len__ + __getitem__ needed, rest is free
from collections.abc import Sequence              # abstract base class

class Playlist2(Sequence):                        # gets __contains__, __iter__, index, count, __reversed__
    def __init__(self, *songs: str) -> None:      # store songs
        self._songs = list(songs)                 # private list
    def __len__(self) -> int:                     # required abstract method
        return len(self._songs)                   # size
    def __getitem__(self, i):                     # required abstract method
        return self._songs[i]                     # list handles int and slice

q = Playlist2("x", "y", "x")                      # build
print(q.index("y"), q.count("x"))                 # Expected: 1 2
print(list(q[:2]))                                # Expected: ['x', 'y']  (plain list slice here)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: only __getitem__, no __len__
class Bad:
    def __init__(self, *items): self.items = list(items)
    def __getitem__(self, i): return self.items[i]   # iteration works, len() does not

try:
    len(Bad(1, 2))                                   # no __len__
except TypeError as e:
    print(e)                                         # Actual: object of type 'Bad' has no len()

# ✅ Correct: add __len__ (and decide what slicing returns, like Playlist above)
```

---

## 🎯 Interview Tip (1 line)
Say: "Implement `__len__` and `__getitem__` (or inherit `collections.abc.Sequence`) and you get iteration, `in`, and `reversed` for free."

---

## 🔗 Related Questions
→ Q118 (immutable dict) | Q120 (iterator class) | Q147 (complete iterator class) | Q171 (iterators vs iterables) | Q306 (dunder methods)
