---

# Q062. Find Intersection of Lists
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐ Easy

---

## ❓ Question
Return the items present in BOTH lists, without duplicates, keeping the order of the first list.

```python
intersection([1, 2, 2, 3, 4], [2, 4, 4, 5])  # [2, 4]
```

---

## 💡 Quick Concept (2 lines only)
Put the second list in a `set` for O(1) membership checks, then scan the first list. A `seen` set removes duplicates while preserving order.
हिंदी: दूसरी list को set बना लो ताकि जाँच तेज़ हो, फिर पहली list में से common items निकालो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

def intersection(a: list, b: list) -> list:
    in_b = set(b)                              # Step 1: O(1) lookup structure for b
    seen: set = set()                          # Step 2: remember what we already output
    out = []                                   # Step 3: ordered result
    for x in a:                                # Step 4: scan a in order
        if x in in_b and x not in seen:        # Step 5: common AND not yet added
            seen.add(x)                        # Step 6: mark as added
            out.append(x)                      # Step 7: keep it
    return out                                 # Step 8: return result

# ============================================
# TEST CASES
# ============================================

print(intersection([1, 2, 2, 3, 4], [2, 4, 4, 5]))  # Expected: [2, 4]
print(intersection([1], [2]))                       # Expected: []
print(intersection([], [1]))                        # Expected: []
```

---

## 🔍 Why This Works (3 lines max)
`x in set` is O(1), so the whole thing is O(n + m) instead of O(n * m). The `seen` set stops duplicates from `a` being repeated. Items must be hashable.
हिंदी: Set lookup O(1) है इसलिए कुल समय O(n+m) रहता है।

---

## ⚡ Alternative Solution
```python
from collections import Counter                       # multiset arithmetic

print(set([1, 2, 2, 3, 4]) & set([2, 4, 4, 5]))       # Expected: {2, 4} (shortest, but order NOT guaranteed)
print(list(dict.fromkeys(x for x in [3, 1, 3, 2] if x in {1, 3})))  # Expected: [3, 1] (ordered, deduped)
print(Counter([1, 2, 2, 2]) & Counter([2, 2, 3]))     # Expected: Counter({2: 2}) (keeps min counts - multiset intersection)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: `x in b` on a LIST is O(m) -> overall O(n*m), and duplicates survive
def bad_int(a, b):
    return [x for x in a if x in b]
print(bad_int([1, 2, 2, 3], [2, 3]))   # [2, 2, 3] <- duplicates kept (verified)

# ❌ Wrong: set([[1]]) -> TypeError: unhashable type: 'list' (verified)
# ✅ Correct: use a set for lookups; for unhashable items fall back to O(n*m) `in` on a list
```

---

## 🎯 Interview Tip (1 line)
Say: "Convert one side to a set for O(n+m); clarify whether duplicates and order matter."

---

## 🔗 Related Questions
→ Q063 (difference) | Q069 (unique values) | Q067 (find duplicates) | Q055 (remove duplicates keep order)
