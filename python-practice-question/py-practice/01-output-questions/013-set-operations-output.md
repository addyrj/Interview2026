---

# Q013. Set Operations Output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐ Easy

---

## ❓ Question
What will the following code print?

```python
a = {1, 2, 3, 4}
b = {3, 4, 5}

print(a | b, a & b, a - b, a ^ b)
print(a <= b, {1, 2} < a)
print(type({}), type({1}), type(set()))
```

---

## 💡 Quick Concept (2 lines only)
Sets support math operations: `|` union, `&` intersection, `-` difference, `^` symmetric difference, `<=`/`<` subset checks. `{}` is an empty DICT, not a set.
हिंदी: Set में union, intersection, difference आसान हैं; खाली set के लिए `set()` लिखो, `{}` dict है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
# Step 1: two sets with some overlap
a = {1, 2, 3, 4}                        # first set
b = {3, 4, 5}                           # second set

# Step 2: the four set operators (small ints print in sorted-looking order in CPython)
print(a | b, a & b, a - b, a ^ b)       # Expected: {1, 2, 3, 4, 5} {3, 4} {1, 2} {1, 2, 5}
# | everything in either; & only in both; - in a but not b; ^ in exactly one of them

# Step 3: subset checks
print(a <= b, {1, 2} < a)               # Expected: False True  (a is not within b; {1,2} is a proper subset of a)

# Step 4: the empty-literal trap
print(type({}), type({1}), type(set())) # Expected: <class 'dict'> <class 'set'> <class 'set'>
```

---

## 🔍 Why This Works (3 lines max)
Sets are hash tables of unique, hashable elements, so these operations run in roughly O(len) time. Set display order is arbitrary (here it looks sorted only because small ints hash to themselves); never depend on it. `{}` was dict syntax before sets existed.
हिंदी: Set का order भरोसेमंद नहीं है; सिर्फ membership और operations पर ध्यान दो।

---

## ⚡ Alternative Solution
```python
# Method forms accept any iterable, operators need sets on both sides
a = {1, 2, 3, 4}                        # first set
print(a.union([9]), a.issubset(range(10)))  # Expected: {1, 2, 3, 4, 9} True

# Elements must be hashable; use frozenset for sets-of-sets / dict keys
try:
    {[1]}                               # list is unhashable
except TypeError as e:                  # raises
    print(e)                            # Expected: unhashable type: 'list'
print({frozenset([1, 2]): "ok"})        # Expected: {frozenset({1, 2}): 'ok'}
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: empty set literal
# empty = {}                 # this is a dict!
# ❌ Wrong: relying on set order, or putting lists/dicts inside a set

# ✅ Correct
# empty = set()
# s = {(1, 2), frozenset({3})}   # hashable elements only
```

---

## 🎯 Interview Tip (1 line)
Say: "Sets give O(1) average membership and handy algebra (`| & - ^`); elements must be hashable and order is not guaranteed."

---

## 🔗 Related Questions
→ Q062 (intersection of lists) | Q063 (difference of lists) | Q069 (get unique values) | Q175 (mutability and hashability)
