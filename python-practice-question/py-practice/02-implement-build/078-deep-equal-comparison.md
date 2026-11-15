---

# Q078. Deep equal comparison
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `deep_equal(a, b)` that compares nested dicts/lists/tuples/sets by value. Unlike `==`, it should be strict about types (`1` vs `1.0`, `[1, 2]` vs `(1, 2)`, `True` vs `1`) and treat `NaN` as equal to `NaN`.

```python
deep_equal({"a": [1, {"b": 2}]}, {"a": [1, {"b": 2}]})  # True
deep_equal(1, 1.0)                                       # False (strict)
```

---

## 💡 Quick Concept (2 lines only)
Python's `==` already compares nested containers by value, but it is loose: `1 == 1.0 == True` and `nan != nan`. A custom deep equal checks `type(a) is type(b)` first, then recurses by container kind.
हिंदी: `==` खुद deep compare करता है पर type के मामले में ढीला है; strict compare के लिए type भी check करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Any                                 # type hint

def deep_equal(a: Any, b: Any) -> bool:
    if a is b:                                         # Step 1: same object -> equal (fast path)
        return True                                    # also makes the same NaN object equal to itself
    if type(a) is not type(b):                         # Step 2: strict type check (int != float != bool)
        return False                                   # 1 vs 1.0, list vs tuple all fail here
    if isinstance(a, dict):                            # Step 3: dicts -> same keys, equal values
        return a.keys() == b.keys() and all(deep_equal(a[k], b[k]) for k in a)  # key order is ignored
    if isinstance(a, (list, tuple)):                   # Step 4: sequences -> same length, pairwise equal
        return len(a) == len(b) and all(deep_equal(x, y) for x, y in zip(a, b))  # order matters
    if isinstance(a, set):                             # Step 5: sets -> plain set equality (items hashable)
        return a == b
    if isinstance(a, float) and a != a and b != b:     # Step 6: both NaN -> treat as equal
        return True
    return a == b                                      # Step 7: leaves compared with ==

# ============================================
# TEST CASES
# ============================================
print(deep_equal({"a": [1, {"b": 2}]}, {"a": [1, {"b": 2}]}))  # Expected: True
print(deep_equal({"a": [1, 2]}, {"a": [1, 3]}))        # Expected: False
print(deep_equal({"a": 1, "b": 2}, {"b": 2, "a": 1}))  # Expected: True  (dict key order ignored)
print(deep_equal(1, 1.0), 1 == 1.0)                    # Expected: False True
print(deep_equal([1, 2], (1, 2)), [1, 2] == (1, 2))    # Expected: False False
print(deep_equal(True, 1), True == 1)                  # Expected: False True
print(deep_equal({"a": 1}, {"a": 1, "b": 2}))          # Expected: False
print(deep_equal(float("nan"), float("nan")), float("nan") == float("nan"))  # Expected: True False
```

---

## 🔍 Why This Works (3 lines max)
The type check rejects look-alike values before any comparison, then each container kind is compared the right way (dict by keys, list by position, set by membership). NaN is special-cased because `nan != nan` by IEEE 754.
हिंदी: पहले type मिलाओ, फिर container के हिसाब से compare करो; NaN के लिए अलग case।

---

## ⚡ Alternative Solution
```python
# In most real code, plain == is already a deep value comparison
a = {"a": [1, {"b": 2}], "t": (1, 2)}                  # nested sample
b = {"t": (1, 2), "a": [1, {"b": 2}]}                  # same data, different key order
print(a == b)                                          # Expected: True
x = float("nan")                                       # one NaN object
print({"v": x} == {"v": x})                            # Expected: True   (identity shortcut inside containers!)
print({"v": float("nan")} == {"v": float("nan")})      # Expected: False  (two different NaN objects)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: comparing with `is` (identity) instead of ==
a = {"k": [1, 2]}                                      # sample
b = {"k": [1, 2]}                                      # equal by value, different objects
print(a is b)                                          # Output: False  <- identity says "different"
print(a == b)                                          # Output: True
# ❌ Also wrong: assuming == is type-strict
print([1, 2] == [1.0, 2.0])                            # Output: True  (use deep_equal if types matter)
# ✅ Correct: == for value equality, deep_equal when you need strict types
```

---

## 🎯 Interview Tip (1 line)
Say: "== already recurses in Python, so I'd only hand-write it to add rules like strict types, NaN, or ignoring certain keys."

---

## 🔗 Related Questions
→ Q003 (is vs ==) | Q018 (NaN comparison) | Q034 (__eq__ without __hash__) | Q199 (deep diff)
