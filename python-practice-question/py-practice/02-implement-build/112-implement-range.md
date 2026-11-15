---

# Q112. Implement range()
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement a `MyRange(*args)` class that behaves like `range`: supports `(stop)`, `(start, stop)`, `(start, stop, step)` including negative steps, `len()`, indexing, `in`, and can be iterated many times. `step == 0` must raise `ValueError`.

```python
list(MyRange(0, 10, 3))   # [0, 3, 6, 9]
list(MyRange(5, 0, -2))   # [5, 3, 1]
```

---

## 💡 Quick Concept (2 lines only)
`range` is a lazy, re-iterable sequence that stores only `start/stop/step` and computes values on demand. So it needs `__iter__`, `__len__`, `__getitem__`, `__contains__` — not a generator function.
हिंदी: range सिर्फ start/stop/step याद रखता है और values ज़रूरत पर निकालता है — इसलिए class चाहिए, सिर्फ generator नहीं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Iterator  # type hint

class MyRange:  # lazy sequence like range
    def __init__(self, *args: int) -> None:  # parse 1, 2 or 3 arguments
        if len(args) == 1:  # range(stop)
            self.start, self.stop, self.step = 0, args[0], 1  # defaults
        elif len(args) == 2:  # range(start, stop)
            self.start, self.stop, self.step = args[0], args[1], 1  # step defaults to 1
        elif len(args) == 3:  # range(start, stop, step)
            self.start, self.stop, self.step = args  # unpack all three
        else:  # anything else is invalid
            raise TypeError(f"range expected 1 to 3 arguments, got {len(args)}")  # same idea as stdlib
        if self.step == 0:  # step 0 would loop forever
            raise ValueError("range() arg 3 must not be zero")  # same message as stdlib

    def __iter__(self) -> Iterator[int]:  # fresh generator each time -> re-iterable
        cur = self.start  # start value
        while (cur < self.stop) if self.step > 0 else (cur > self.stop):  # direction depends on step sign
            yield cur  # produce value
            cur += self.step  # move by step

    def __len__(self) -> int:  # number of items, O(1)
        if self.step > 0:  # counting up
            return max(0, (self.stop - self.start + self.step - 1) // self.step)  # ceil division
        return max(0, (self.start - self.stop - self.step - 1) // -self.step)  # counting down

    def __getitem__(self, i: int) -> int:  # r[i] in O(1)
        n = len(self)  # size
        if i < 0:  # support negative index
            i += n  # wrap around
        if not 0 <= i < n:  # bounds check
            raise IndexError("range object index out of range")  # same as stdlib
        return self.start + i * self.step  # computed, not stored

    def __contains__(self, x: int) -> bool:  # `x in r` in O(1)
        if self.step > 0:  # ascending: start <= x < stop
            ok = self.start <= x < self.stop
        else:  # descending: stop < x <= start
            ok = self.stop < x <= self.start
        return ok and (x - self.start) % self.step == 0  # must land exactly on a step

# ============================================
# TEST CASES
# ============================================
print(list(MyRange(5)))  # Expected: [0, 1, 2, 3, 4]
print(list(MyRange(2, 6)))  # Expected: [2, 3, 4, 5]
print(list(MyRange(0, 10, 3)))  # Expected: [0, 3, 6, 9]
print(list(MyRange(5, 0, -2)))  # Expected: [5, 3, 1]
print(list(MyRange(3, 3)))  # Expected: []
print(len(MyRange(0, 10, 3)), len(MyRange(5, 0, -2)), len(MyRange(5, 1)))  # Expected: 4 3 0
print(MyRange(10)[3], MyRange(10)[-1])  # Expected: 3 9
print(7 in MyRange(1, 10, 3), 8 in MyRange(1, 10, 3))  # Expected: True False
try:  # zero step
    MyRange(1, 5, 0)  # should raise
except ValueError as e:
    print(e)  # Expected: range() arg 3 must not be zero
print(list(range(0, 10, 3)), len(range(5, 0, -2)))  # Expected: [0, 3, 6, 9] 3  (built-in, same)
r = MyRange(3)  # one object
print(list(r), list(r))  # Expected: [0, 1, 2] [0, 1, 2]  (re-iterable)
```

---

## 🔍 Why This Works (3 lines max)
Only three integers are stored, so memory is O(1) and `len`, indexing and `in` are computed with arithmetic. `__iter__` creates a new generator per call, so the object can be looped over repeatedly (unlike a generator).
हिंदी: सिर्फ 3 numbers store होते हैं, बाकी सब गणित से निकलता है, और हर loop को नया generator मिलता है।

---

## ⚡ Alternative Solution
```python
# Simple generator (enough for `for` loops, but one-shot: no len/index/in, not re-iterable)
def gen_range(start, stop, step=1):
    while (start < stop) if step > 0 else (start > stop):  # direction check
        yield start  # produce value
        start += step  # advance

print(list(gen_range(0, 5, 2)))  # Expected: [0, 2, 4]
print(list(gen_range(5, 0, -2)))  # Expected: [5, 3, 1]

# The real range handles huge sizes instantly because nothing is materialised
print(range(10**12)[5], range(10**12))  # Expected: 5 range(0, 1000000000000)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: builds a list (not lazy) and only handles positive steps
def bad(start, stop, step=1):
    out = []
    while start < stop:  # ❌ negative step never enters the loop
        out.append(start); start += step  # ❌ O(n) memory
    return out
print(bad(5, 0, -1))  # Output: []  (WRONG, should be [5, 4, 3, 2, 1])

# ✅ Correct: choose the comparison by the step sign (see MyRange.__iter__)
```

---

## 🎯 Interview Tip (1 line)
Say: "range is a lazy immutable sequence — O(1) memory, O(1) len/index/in, re-iterable; I handle negative steps and reject step 0."

---

## 🔗 Related Questions
→ Q107 (map) | Q110 (zip) | Q111 (enumerate) | Q120 (iterator class) | Q171 (iterators vs iterables)
