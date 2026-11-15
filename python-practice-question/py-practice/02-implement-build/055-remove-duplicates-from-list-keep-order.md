---

# Q055. Remove Duplicates from List (Keep Order)
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement `dedupe(items: list) -> list` that removes duplicates but keeps the first occurrence order.

```python
dedupe([3, 1, 3, 2, 1, 4])   # [3, 1, 2, 4]
```

---

## 💡 Quick Concept (2 lines only)
Track seen items in a set (O(1) lookup) and append only unseen ones. `list(set(x))` is shorter but does NOT guarantee order.
हिंदी: `seen` set रखो, नया item आए तभी result में जोड़ो — order बना रहता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

def dedupe(items: list) -> list:
    seen = set()                              # Step 1: items already added
    result = []                               # Step 2: ordered output
    for item in items:                        # Step 3: walk in original order
        if item not in seen:                  # first time we see it?
            seen.add(item)                    # remember it
            result.append(item)               # keep it
    return result                             # Step 4: duplicates removed, order kept

# ============================================
# TEST CASES
# ============================================
print(dedupe([3, 1, 3, 2, 1, 4]))             # Expected: [3, 1, 2, 4]
print(dedupe([]))                             # Expected: []
print(dedupe(["a", "b", "a"]))                # Expected: ['a', 'b']
print(dedupe([1, True, 1.0, 2]))              # Expected: [1, 2]  (1 == True == 1.0 and same hash)
```

---

## 🔍 Why This Works (3 lines max)
Set membership is O(1), so the whole pass is O(n) instead of O(n^2) for `item not in result`. Items must be hashable. Values equal under `==` with equal hashes (1, True, 1.0) are treated as the same.
हिंदी: set lookup O(1) है, इसलिए पूरा काम O(n); items hashable होने चाहिए।

---

## ⚡ Alternative Solution
```python
def dedupe2(items: list) -> list:
    return list(dict.fromkeys(items))         # dicts keep insertion order (3.7+), keys are unique

print(dedupe2([3, 1, 3, 2, 1, 4]))            # Output: [3, 1, 2, 4]

# Unhashable items (lists): fall back to O(n^2) list membership
def dedupe_unhash(items: list) -> list:
    out: list = []                            # result
    for i in items:
        if i not in out:                      # uses ==, not hashing
            out.append(i)
    return out

print(dedupe_unhash([[1], [1], [2]]))         # Output: [[1], [2]]

# Dedupe by key (case-insensitive)
def dedupe_key(items: list, key) -> list:
    seen: set = set()                         # keys seen
    out: list = []                            # result
    for i in items:
        k = key(i)                            # compute comparison key
        if k not in seen:
            seen.add(k)
            out.append(i)
    return out

print(dedupe_key(["Apple", "apple", "Bob"], str.lower))  # Output: ['Apple', 'Bob']
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: set() loses order (and string order changes run to run due to hash randomization)
print(list(set([3, 1, 3, 2, 1, 4])))          # Output: [1, 2, 3, 4]  (small ints happen to look sorted)
print(list(set(["banana", "apple", "cherry", "apple"])))
# Output varies between runs, e.g. ['apple', 'banana', 'cherry'] -> NOT insertion order

# ❌ Also: dedupe([[1], [1]]) -> TypeError: unhashable type: 'list'

# ✅ Correct: dict.fromkeys(items) or the seen-set loop
```

---

## 🎯 Interview Tip (1 line)
Say: "`dict.fromkeys` keeps order in O(n); mention hashability and the O(n^2) fallback for unhashable items."

---

## 🔗 Related Questions
→ Q067 (find duplicates) | Q069 (get unique values) | Q175 (mutability and hashability) | Q062 (intersection of lists)
