---

# Q067. Find Duplicates in a List
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐ Easy

---

## ❓ Question
Return the values that appear more than once, each listed only once.

```python
find_duplicates([1, 2, 3, 2, 1, 4, 2])  # [2, 1]
```

---

## 💡 Quick Concept (2 lines only)
Keep a `seen` set. If an item is already in `seen`, it is a duplicate - record it once. O(n) time, O(n) space.
हिंदी: `seen` set रखो — item पहले से `seen` में हो तो वो duplicate है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

from typing import Hashable, Iterable  # items must be hashable

def find_duplicates(items: Iterable[Hashable]) -> list:
    seen: set = set()                         # Step 1: values met so far
    dups: list = []                           # Step 2: duplicates found (each once)
    for it in items:                          # Step 3: scan in order
        if it in seen and it not in dups:     # Step 4: seen before AND not yet reported
            dups.append(it)                   # Step 5: report it once
        seen.add(it)                          # Step 6: remember this value
    return dups                               # Step 7: return the duplicates

# ============================================
# TEST CASES
# ============================================

print(find_duplicates([1, 2, 3, 2, 1, 4, 2]))   # Expected: [2, 1]  (order of 2nd occurrence)
print(find_duplicates([1, 2]))                  # Expected: []
print(find_duplicates([]))                      # Expected: []
```

---

## 🔍 Why This Works (3 lines max)
The first time a value is seen it only goes into `seen`; any later time it is a duplicate. `it not in dups` avoids reporting a value three times (it scans a list, so use the dict trick below for big inputs).
हिंदी: पहली बार `seen` में जाता है, दोबारा दिखे तो duplicate — `dups` में सिर्फ एक बार जोड़ते हैं।

---

## ⚡ Alternative Solution
```python
from collections import Counter                       # tally helper

data = [1, 2, 3, 2, 1, 4, 2]                          # sample data
print([k for k, v in Counter(data).items() if v > 1]) # Expected: [1, 2]  (first-appearance order)

def find_dups_fast(items):                            # O(n): dict as ordered set
    seen, dups = set(), {}                            # dups: dict keeps insertion order, O(1) insert
    for it in items:                                  # scan
        if it in seen:                                # already seen -> duplicate
            dups[it] = None                           # idempotent insert
        else:
            seen.add(it)                              # first sighting
    return list(dups)                                 # keys in order

print(find_dups_fast(data))                           # Expected: [2, 1]
print(len(data) != len(set(data)))                    # Expected: True  (just "are there any duplicates?")
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: appending on every repeat - the value 2 appears 3 times
def bad_d(a):
    seen = set(); d = []
    for x in a:
        if x in seen:
            d.append(x)      # no "already reported" check
        seen.add(x)
    return d
print(bad_d([1, 2, 3, 2, 1, 4, 2]))   # [2, 1, 2] <- 2 reported twice (verified)

# ❌ Wrong: [x for x in a if a.count(x) > 1] -> O(n^2) and still has repeats
# ✅ Correct: report once via a dict/set, or Counter
```

---

## 🎯 Interview Tip (1 line)
Say: "Set for O(n); Counter if you need frequencies; clarify output order and whether to report each duplicate once."

---

## 🔗 Related Questions
→ Q055 (remove duplicates keep order) | Q066 (count occurrences) | Q069 (unique values) | Q062 (intersection)
