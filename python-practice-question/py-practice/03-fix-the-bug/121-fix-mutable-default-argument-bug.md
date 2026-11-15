---

# Q121. Fix mutable default argument bug
# Category: FIX THE BUG
# Difficulty: ⭐ Easy

---

## ❓ Question
This function should return a fresh list each call, but data leaks between calls. Find and fix the bug.

```python
def add_item(item, bucket=[]):   # BUG
    bucket.append(item)
    return bucket

print(add_item("a"))   # ['a']
print(add_item("b"))   # expected ['b'], but prints ['a', 'b']
```

---

## 💡 Quick Concept (2 lines only)
Default values are evaluated ONCE, when `def` runs, and stored on the function — a mutable default is shared by every call.
हिंदी: Default value `def` चलने पर सिर्फ एक बार बनता है, इसलिए mutable default सब calls में share होता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
# Symptom (buggy version):
def add_item(item, bucket=[]):          # the [] is created once and stored in __defaults__
    bucket.append(item)                 # mutates the shared list
    return bucket                       # returns the shared list

print(add_item("a"))                    # Output: ['a']
print(add_item("b"))                    # Output: ['a', 'b']   <- BUG: leaked state
print(add_item.__defaults__)            # Output: (['a', 'b'],)  <- the default itself changed

# Fix: use None as sentinel and create the list inside the function
def add_fixed(item, bucket=None):       # Step 1: immutable default
    if bucket is None:                  # Step 2: no list passed in?
        bucket = []                     # Step 3: create a NEW list per call
    bucket.append(item)                 # add item
    return bucket                       # return it

# ============================================
# TEST CASES
# ============================================
print(add_fixed("a"))                   # Expected: ['a']
print(add_fixed("b"))                   # Expected: ['b']
print(add_fixed("c", ["x"]))            # Expected: ['x', 'c']
print(add_fixed.__defaults__)           # Expected: (None,)
```

---

## 🔍 Why This Works (3 lines max)
`None` is immutable, so the default never changes; a new list is built inside the body on every call. `__defaults__` proves the old default object was mutated in place.
हिंदी: `None` default रखो और list function के अंदर बनाओ — हर call पर नई list मिलती है।

---

## ⚡ Alternative Solution
```python
# Dataclasses refuse mutable defaults and force default_factory
from dataclasses import dataclass, field                # stdlib

@dataclass
class Cart:
    items: list[str] = field(default_factory=list)      # new list per instance

c1, c2 = Cart(), Cart()                                 # two carts
c1.items.append("x")                                    # change only c1
print(c1, c2)                                           # Output: Cart(items=['x']) Cart(items=[])
try:
    @dataclass
    class Bad:
        items: list = []                                # mutable default
except ValueError as e:
    print("ValueError:", e)                             # Output: ValueError: mutable default <class 'list'> for field items is not allowed: use default_factory
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: "fixing" with `bucket = bucket or []` breaks when caller passes an EMPTY list they want mutated
def g(bucket=None):
    bucket = bucket or []                # empty list is falsy -> replaced by a new list
    return bucket
shared = []
print(g(shared) is shared)               # Output: False  (caller's list ignored)

# ✅ Correct: compare with `is None`
def h(bucket=None):
    if bucket is None: bucket = []
    return bucket
print(h(shared) is shared)               # Output: True

# Same trap with time: def stamp(t=datetime.now()) is evaluated once at definition time.
```

---

## 🎯 Interview Tip (1 line)
Say: "Defaults are evaluated once at definition; use `None` plus `if x is None`, or `default_factory` in dataclasses."

---

## 🔗 Related Questions
→ Q001 (mutable default output) | Q138 (shared class variable bug) | Q148 (complete dataclass) | Q292 (mutable vs immutable)
