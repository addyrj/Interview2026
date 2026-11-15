---

# Q068. Remove Falsy Values
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `remove_falsy(items)` that drops every falsy value (`0`, `0.0`, `False`, `""`, `None`, `[]`, `{}`) and keeps the rest.

---

## 💡 Quick Concept (2 lines only)
Falsy values evaluate to `False` in a boolean context, so `[x for x in items if x]` is enough. `filter(None, items)` does the same.
हिंदी: `if x` जिन्हें False मानता है (0, "", None, [], {}) उन्हें हटा दो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

from typing import Iterable  # type hint

def remove_falsy(items: Iterable) -> list:
    return [x for x in items if x]      # Step 1: keep only truthy values (bool(x) is True)

# ============================================
# TEST CASES
# ============================================

print(remove_falsy([0, 1, False, 2, "", 3, None, "a", [], {}, 0.0, float("nan")]))
# Expected: [1, 2, 3, 'a', nan]   <- NaN is TRUTHY, so it stays!
print(remove_falsy(["", None, 0]))   # Expected: []
print(remove_falsy([" ", [0]]))      # Expected: [' ', [0]]  (non-empty containers/strings are truthy)
```

---

## 🔍 Why This Works (3 lines max)
`if x` calls `bool(x)`, which is False for zero numbers, empty containers/strings and `None`. NaN, `" "` and `[0]` are truthy. Falsy values are a language rule, not "empty-looking" values.
हिंदी: `if x` अंदर से `bool(x)` चलाता है; NaN और `" "` truthy होते हैं।

---

## ⚡ Alternative Solution
```python
print(list(filter(None, [0, 1, "", 2, None])))          # Expected: [1, 2] (None as predicate = truthiness test)

def remove_none(items):                                 # remove ONLY None, keep 0/""/False
    return [x for x in items if x is not None]          # identity check, not truthiness

print(remove_none([0, None, "", False, 1]))             # Expected: [0, '', False, 1]
print(bool(float("nan")), bool(" "), bool([0]), bool(0j))  # Expected: True True True False
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using `if x` when 0 / False are VALID data (e.g. scores, flags)
scores = [0, 10, None, 7]
print([s for s in scores if s])              # [10, 7] <- real score 0 was lost!

# ✅ Correct: filter only what you mean
print([s for s in scores if s is not None])  # [0, 10, 7]
# Also: `if arr` on a NumPy array raises ValueError (ambiguous truth value) - use arr.size / any() / all()
```

---

## 🎯 Interview Tip (1 line)
Always ask: "Remove falsy, or only None?" - `0` and `False` are often legitimate values.

---

## 🔗 Related Questions
→ Q017 (truthy/falsy output) | Q016 (short-circuit values) | Q069 (unique values) | Q049 (any/all with empty)
