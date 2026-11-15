---

# Q049. any/all with Empty Iterables Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will this code print?

```python
print(any([]), all([]))
print(any([0, "", None]), all([1, "a", True]))
print(any([[]]), all([[]]))
print(all(x > 5 for x in []))

def noisy():
    for i in [0, 1, 2]:
        print("check", i)
        yield i

print(any(noisy()))
print(all(noisy()))
```

---

## 💡 Quick Concept (2 lines only)
`any([])` is `False` (no item is truthy) and `all([])` is `True` (vacuous truth — no item is falsy). Both short-circuit and work lazily on generators.
हिंदी: खाली iterable पर `any` = False, `all` = True; दोनों जैसे ही जवाब मिले रुक जाते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

print(any([]), all([]))                       # Step 1: empty -> False True (vacuous truth)
print(any([0, "", None]), all([1, "a", True]))  # Step 2: all falsy -> any False; all truthy -> all True
print(any([[]]), all([[]]))                   # Step 3: the item is [] (falsy) -> False False
print(all(x > 5 for x in []))                 # Step 4: no elements to fail -> True

def noisy():
    for i in [0, 1, 2]:                       # yields 0, 1, 2
        print("check", i)                     # shows how far evaluation goes
        yield i                               # lazily produce next value

print(any(noisy()))                           # Step 5: stops at first truthy (1) -> never checks 2
print(all(noisy()))                           # Step 6: stops at first falsy (0) -> only checks 0

# ============================================
# TEST CASES (real output, Python 3.13)
# ============================================
# False True
# False True
# False False
# True
# check 0
# check 1
# True
# check 0
# False
```

---

## 🔍 Why This Works (3 lines max)
`any` returns True on the first truthy item, `all` returns False on the first falsy item; with no items there is nothing to trigger either, so the defaults are `False` and `True`. `[[]]` has one item, an empty list, which is falsy. Generators are consumed only as far as needed.
हिंदी: `any` पहला truthy मिलते ही रुकता है, `all` पहला falsy मिलते ही; खाली हो तो default False / True।

---

## ⚡ Alternative Solution
```python
print(any(()), all(""), any({}), all({}))     # Output: False True False True

vals: list[int] = []                          # imagine: no validation rules/inputs
print("empty valid" if all(v > 0 for v in vals) else "invalid")  # Output: empty valid
print(bool(vals) and all(v > 0 for v in vals))                   # Output: False
# second form requires at least one item to be valid
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: assuming all() on an empty list means "failed validation"
def is_valid(scores: list[int]) -> bool:
    return all(s >= 0 for s in scores)        # is_valid([]) -> True (maybe a bug!)

# ✅ Correct: handle the empty case explicitly when it matters
def is_valid_ok(scores: list[int]) -> bool:
    return bool(scores) and all(s >= 0 for s in scores)  # is_valid_ok([]) -> False
```

---

## 🎯 Interview Tip (1 line)
Say: "`all([])` is True by vacuous truth and `any([])` is False; both short-circuit, so guard the empty case explicitly."

---

## 🔗 Related Questions
→ Q016 (short-circuit and/or) | Q017 (truthy/falsy) | Q026 (generator expression laziness) | Q050 (for/while else)
