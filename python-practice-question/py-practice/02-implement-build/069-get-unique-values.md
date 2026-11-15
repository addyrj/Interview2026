---

# Q069. Get Unique Values
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐ Easy

---

## ❓ Question
Return the unique values of a list. Show the order-preserving version, and handle unhashable items (like lists).

```python
unique([3, 1, 3, 2, 1])  # [3, 1, 2]
```

---

## 💡 Quick Concept (2 lines only)
`set()` removes duplicates but loses order and needs hashable items. For first-seen order use a `seen` set or `dict.fromkeys()`.
हिंदी: `set` duplicates हटाता है पर order नहीं बचाता — order चाहिए तो `dict.fromkeys` या `seen` set.

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

from typing import Hashable, Iterable  # items must be hashable

def unique(items: Iterable[Hashable]) -> list:
    seen: set = set()               # Step 1: values already output
    out: list = []                  # Step 2: ordered unique values
    for it in items:                # Step 3: scan in order
        if it not in seen:          # Step 4: first time we see it?
            seen.add(it)            # Step 5: remember it
            out.append(it)          # Step 6: keep it
    return out                      # Step 7: return the result

# ============================================
# TEST CASES
# ============================================

print(unique([3, 1, 3, 2, 1]))          # Expected: [3, 1, 2]
print(unique([]))                       # Expected: []
print(unique("hello"))                  # Expected: ['h', 'e', 'l', 'o']
print(unique([1, 1.0, True, 0, False])) # Expected: [1, 0]  (1 == 1.0 == True, 0 == False)
```

---

## 🔍 Why This Works (3 lines max)
`seen` gives O(1) "have I seen this" checks and the list preserves first-seen order. Equality/hash rules decide what counts as "the same" value.
हिंदी: `seen` से जाँच O(1) होती है और list से order बचा रहता है।

---

## ⚡ Alternative Solution
```python
print(list(dict.fromkeys([3, 1, 3, 2, 1])))   # Expected: [3, 1, 2] (shortest ordered version, dict keeps insertion order)
print(set([3, 1, 3, 2, 1]))                   # Expected: {1, 2, 3} (no order guarantee)

def unique_unhashable(items):                 # works for lists/dicts too, but O(n^2)
    out = []                                  # result
    for it in items:                          # scan
        if it not in out:                     # linear equality check (no hashing needed)
            out.append(it)                    # keep first occurrence
    return out

print(unique_unhashable([[1], [2], [1], {"a": 1}, {"a": 1}]))  # Expected: [[1], [2], {'a': 1}]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: assuming list(set(x)) keeps order
print(list(set([3, 1, 3, 2, 1])))   # [1, 2, 3] here, but set order is an implementation detail;
                                    # for str items it even changes between runs (hash randomisation)
# ❌ Wrong: set of unhashable items
# set([[1], [2]])  -> TypeError: unhashable type: 'list' (verified)
# ✅ Correct: dict.fromkeys(items) for order; convert to tuples or use the O(n^2) version for unhashables
```

---

## 🎯 Interview Tip (1 line)
Say: "`dict.fromkeys` is the idiomatic ordered dedupe (dicts preserve insertion order since 3.7); sets need hashable items."

---

## 🔗 Related Questions
→ Q055 (remove duplicates keep order) | Q067 (find duplicates) | Q062 (intersection) | Q175 (mutability and hashability)
