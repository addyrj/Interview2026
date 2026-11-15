---

# Q058. Flatten a Nested List
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐ Easy

---

## ❓ Question
Flatten a list of lists **one level** deep: `[[1, 2], [3], [], [4, 5]]` -> `[1, 2, 3, 4, 5]`.
(Arbitrary depth is the next question, Q059.)

---

## 💡 Quick Concept (2 lines only)
Loop over each sub-list and append its items to one result list. The Pythonic way is a nested comprehension or `itertools.chain.from_iterable`.
हिंदी: हर sub-list के अंदर के items को एक नई list में डालो — सिर्फ एक level flatten होता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

def flatten(nested: list[list]) -> list:
    out = []                        # Step 1: result list
    for sub in nested:              # Step 2: visit each sub-list
        for x in sub:               # Step 3: visit each item inside it
            out.append(x)           # Step 4: add the item to the result
    return out                      # Step 5: return the flat list

# ============================================
# TEST CASES
# ============================================

print(flatten([[1, 2], [3], [], [4, 5]]))   # Expected: [1, 2, 3, 4, 5]
print(flatten([]))                          # Expected: []
print(flatten([[1, [2, 3]], [4]]))          # Expected: [1, [2, 3], 4]  (only ONE level removed)
```

---

## 🔍 Why This Works (3 lines max)
The outer loop picks each sub-list, the inner loop copies its elements in order. Empty sub-lists simply contribute nothing. Inner nesting stays untouched because we never look inside the items.
हिंदी: बाहर वाला loop sub-list देता है, अंदर वाला उसके items — खाली list कुछ नहीं जोड़ती।

---

## ⚡ Alternative Solution
```python
from itertools import chain                              # chain lazily joins iterables

data = [[1, 2], [3], [], [4, 5]]                         # sample data
print(list(chain.from_iterable(data)))                   # Expected: [1, 2, 3, 4, 5] (fast, idiomatic)
print([x for sub in data for x in sub])                  # Expected: [1, 2, 3, 4, 5] (outer loop FIRST, then inner)
print(sum([[1], [2]], []))                               # Expected: [1, 2] (works but O(n^2) - avoid!)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: passing strings - a string is also an iterable of characters
print(flatten(["ab", "cd"]))        # ['a', 'b', 'c', 'd'] <- surprising if you expected 2 items (verified)

# ❌ Wrong: sum(list_of_lists, []) copies the growing list each time -> O(n^2)
# ✅ Correct: itertools.chain.from_iterable(...) or a comprehension -> O(n)
```

---

## 🎯 Interview Tip (1 line)
Say: "`chain.from_iterable` is O(n) and lazy; `sum(lists, [])` looks clever but is quadratic."

---

## 🔗 Related Questions
→ Q059 (deep flatten) | Q060 (chunk list) | Q073 (flatten nested dict) | Q114 (itertools.chain)
