---

# Q009. += vs + on Lists Output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```python
a = [1, 2]
b = a
a += [3]
print(a, b, a is b)

a = [1, 2]
b = a
a = a + [3]
print(a, b, a is b)

c = [1, 2]
c += "xy"
print(c)
```

---

## 💡 Quick Concept (2 lines only)
`a += x` calls `__iadd__` which extends the list IN PLACE (and accepts any iterable); `a = a + x` builds a NEW list (and needs a list on the right).
हिंदी: `+=` वही list बदलता है, `+` नई list बनाता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
# Step 1: += mutates in place, so alias b sees the change
a = [1, 2]                              # original list
b = b_alias = a                         # b (and b_alias) point to the same list
a += [3]                                # list.__iadd__ -> same as a.extend([3])
print(a, b, a is b)                     # Expected: [1, 2, 3] [1, 2, 3] True

# Step 2: + creates a new list and rebinds a; b keeps the old one
a = [1, 2]                              # reset
b = a                                   # alias again
a = a + [3]                             # list.__add__ builds a brand-new list
print(a, b, a is b)                     # Expected: [1, 2, 3] [1, 2] False

# Step 3: += accepts any iterable, + does not
c = [1, 2]                              # fresh list
c += "xy"                               # extend with each character of the string
print(c)                                # Expected: [1, 2, 'x', 'y']
try:
    c = [1, 2] + "xy"                   # + requires both sides to be lists
except TypeError as e:                  # raises
    print(e)                            # Expected: can only concatenate list (not "str") to list
```

---

## 🔍 Why This Works (3 lines max)
For mutable types `+=` maps to `__iadd__`, which mutates and returns `self`, so aliases see the change. `+` maps to `__add__`, which returns a new object, leaving aliases untouched. Immutable types (int, str, tuple) have no `__iadd__`, so `+=` falls back to `+`.
हिंदी: Alias वाली list में `+=` का असर सब जगह दिखता है, `+` का नहीं।

---

## ⚡ Alternative Solution
```python
# Be explicit about intent instead of relying on += semantics
a = [1, 2]                              # original
b = a                                   # alias
a.extend([3])                           # explicit in-place growth
print(b)                                # Expected: [1, 2, 3]

a = [*a, 4]                             # explicit new list via unpacking
print(a, b)                             # Expected: [1, 2, 3, 4] [1, 2, 3]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: mutating a list argument with += and surprising the caller
# def add_tax(prices): prices += [0]      # caller's list is modified too

# ✅ Correct: return a new list if you must not touch the caller's data
# def add_tax(prices): return prices + [0]
```

---

## 🎯 Interview Tip (1 line)
Say: "`+=` is in-place (`__iadd__`) for lists and affects aliases; `+` creates a new object — the difference matters for function arguments."

---

## 🔗 Related Questions
→ Q008 (tuple with mutable element and +=) | Q001 (mutable default) | Q292 (mutable vs immutable) | Q304 (pass by object reference)
