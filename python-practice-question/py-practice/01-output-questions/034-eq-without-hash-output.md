---

# Q034. __eq__ without __hash__ output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What happens when you define `__eq__` but not `__hash__` and then use the object in a set?

```python
class P:
    def __init__(self, x):
        self.x = x
    def __eq__(self, other):
        return isinstance(other, P) and self.x == other.x

print(P(1) == P(1))
s = {P(1)}
```

---

## 💡 Quick Concept (2 lines only)
Defining `__eq__` in a class sets `__hash__` to `None`, making instances unhashable. Equal objects must have equal hashes, so you must define both.
हिंदी: सिर्फ़ `__eq__` लिखने पर Python `__hash__` को `None` कर देता है, इसलिए object set/dict key नहीं बन सकता।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
class P:
    def __init__(self, x: int) -> None:
        self.x = x                                   # store value
    def __eq__(self, other: object) -> bool:
        return isinstance(other, P) and self.x == other.x  # value equality

class Q:
    def __init__(self, x: int) -> None:
        self.x = x
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Q) and self.x == other.x
    def __hash__(self) -> int:
        return hash(self.x)                          # equal objects -> equal hash

# ============================================
# TEST CASES
# ============================================
print(P(1) == P(1))          # Expected: True
print(P.__hash__)            # Expected: None
try:
    hash(P(1))               # unhashable
except TypeError as e:
    print("TypeError:", e)   # Expected: TypeError: unhashable type: 'P'
try:
    s = {P(1)}               # sets need hash()
except TypeError as e:
    print("TypeError:", e)   # Expected: TypeError: unhashable type: 'P'
print(len({Q(1), Q(1), Q(2)}))  # Expected: 2
print(Q(1) in {Q(1)})           # Expected: True
```

---

## 🔍 Why This Works (3 lines max)
Python's data model: if a class overrides `__eq__` without `__hash__`, its `__hash__` is implicitly set to `None`. Sets/dicts hash first and then compare, so `Q` needs both to deduplicate correctly.
हिंदी: Hash पहले, equality बाद में — इसलिए दोनों methods consistent होने चाहिए।

---

## ⚡ Alternative Solution
```python
# dataclass(frozen=True) generates __eq__ and __hash__ for you
from dataclasses import dataclass

@dataclass(frozen=True)       # frozen + eq=True -> __hash__ generated
class R:
    x: int                    # field used in eq and hash

print(len({R(1), R(1)}))      # Expected: 1
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: hash on a mutable field, then mutating it after inserting into a set
#    (object is "lost" in the set because its hash changed)
# ✅ Correct: hash only immutable fields, or make the class frozen
```

---

## 🎯 Interview Tip (1 line)
Say: "If `a == b` then `hash(a) == hash(b)` must hold; defining `__eq__` alone disables hashing, and mutable hashed fields are a bug."

---

## 🔗 Related Questions
→ Q134 (fix __eq__ without __hash__) | Q175 (mutability and hashability) | Q246 (dataclasses)
