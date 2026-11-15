---

# Q063. Find Difference of Lists
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐ Easy

---

## ❓ Question
Return the items of list `a` that are NOT in list `b` (order preserved).

```python
difference([1, 2, 2, 3, 4], [2, 5])  # [1, 3, 4]
```

---

## 💡 Quick Concept (2 lines only)
Build `set(b)` once, then keep each `x` from `a` where `x not in that set`. O(n + m).
हिंदी: `b` को set बनाओ और `a` के वो items रखो जो उसमें नहीं हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

def difference(a: list, b: list) -> list:
    remove = set(b)                     # Step 1: fast membership structure
    out = []                            # Step 2: result list
    for x in a:                         # Step 3: scan a (keeps order and duplicates of a)
        if x not in remove:             # Step 4: not present in b?
            out.append(x)               # Step 5: keep it
    return out                          # Step 6: return result

# ============================================
# TEST CASES
# ============================================

print(difference([1, 2, 2, 3, 4], [2, 5]))   # Expected: [1, 3, 4]
print(difference([1], [1]))                  # Expected: []
print(difference([], [1]))                   # Expected: []
```

---

## 🔍 Why This Works (3 lines max)
Membership in a set is O(1), so one pass over `a` suffices. Order of `a` is kept because we iterate the list, not the set. This is `a - b`, not symmetric difference.
हिंदी: `a` के order में चलते हैं इसलिए order बचा रहता है; यह सिर्फ `a - b` है।

---

## ⚡ Alternative Solution
```python
from collections import Counter                          # multiset subtraction

print(set([1, 2, 3, 4]) - set([2, 5]))                   # Expected: {1, 3, 4} (order not guaranteed)
print([x for x in [1, 2, 3, 4] if x not in {2, 5}])      # Expected: [1, 3, 4] (comprehension, ordered)
print(sorted(set([1, 2, 3]) ^ set([3, 4])))              # Expected: [1, 2, 4] (symmetric difference ^)
c = Counter([1, 2, 2, 3]) - Counter([2])                 # subtract counts: removes only ONE 2
print(list(c.elements()))                                # Expected: [1, 2, 3]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using set subtraction when duplicates / order matter
print(set([1, 2, 2, 3]) - {9})   # {1, 2, 3} <- duplicates collapsed, order not guaranteed (verified)

# ❌ Wrong: `x not in list_b` inside the loop -> O(n*m)
# ✅ Correct: precompute set(b); use Counter if you need multiset semantics
```

---

## 🎯 Interview Tip (1 line)
Clarify: "Do duplicates and order matter? Is it `a - b` or symmetric difference?" then use set or Counter accordingly.

---

## 🔗 Related Questions
→ Q062 (intersection) | Q067 (find duplicates) | Q069 (unique values) | Q013 (set operations output)
