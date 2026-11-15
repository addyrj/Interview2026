---

# Q079. Count key occurrences in nested dicts
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `count_keys(obj)` that returns a `Counter` of how many times each key appears anywhere inside nested dicts (also looking through lists of dicts).

```python
doc = {"id": 1, "user": {"id": 2, "tags": [{"id": 3}]}}
count_keys(doc)["id"]  # 3
```

---

## 💡 Quick Concept (2 lines only)
Recurse through dicts and lists; for every dict key do `counter[k] += 1`, then recurse into the value. `collections.Counter` returns 0 for keys it never saw.
हिंदी: हर dict की key गिनो और values में recursion करो; Counter missing key पर 0 देता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from collections import Counter                        # counting helper
from typing import Any                                 # type hint

def count_keys(obj: Any, counter: Counter | None = None) -> Counter:
    counter = Counter() if counter is None else counter  # Step 1: create the shared counter once
    if isinstance(obj, dict):                          # Step 2: dict -> count its keys
        for k, v in obj.items():                       # each key/value pair
            counter[k] += 1                            # count this key
            count_keys(v, counter)                     # then look inside the value
    elif isinstance(obj, (list, tuple)):               # Step 3: list/tuple -> look at each element
        for item in obj:                               # iterate items
            count_keys(item, counter)                  # recurse (may be a dict)
    return counter                                     # Step 4: scalars add nothing

# ============================================
# TEST CASES
# ============================================
doc = {"id": 1, "user": {"id": 2, "tags": [{"id": 3, "name": "x"}, {"name": "y"}]}, "name": "root"}  # sample
r = count_keys(doc)                                    # count everything
print(r)                                               # Expected: Counter({'id': 3, 'name': 3, 'user': 1, 'tags': 1})
print(r["id"], r["name"], r["zzz"])                    # Expected: 3 3 0  (missing key -> 0, no KeyError)
```

---

## 🔍 Why This Works (3 lines max)
One `Counter` is passed through every recursive call, so all levels add to the same tally. Lists are traversed too, otherwise dicts inside lists would be missed.
हिंदी: एक ही Counter सब calls में जाता है, और lists के अंदर के dicts भी गिने जाते हैं।

---

## ⚡ Alternative Solution
```python
# Count ONE specific key with a generator-based recursion
def count_one(obj: object, key: str) -> int:
    if isinstance(obj, dict):                          # dict: count matches here + inside every value
        return sum((k == key) + count_one(v, key) for k, v in obj.items())  # bool adds as 0/1
    if isinstance(obj, (list, tuple)):                 # list: sum over elements
        return sum(count_one(i, key) for i in obj)
    return 0                                           # scalar: nothing to count

doc = {"id": 1, "user": {"id": 2, "tags": [{"id": 3}]}}  # sample
print(count_one(doc, "id"))                            # Expected: 3
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: stops recursing as soon as a key matches, and ignores lists
def bad_count(obj: object, key: str) -> int:
    n = 0                                              # running total
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                n += 1                                 # ❌ does not look inside v
            else:
                n += bad_count(v, key)                 # only recurses when NOT matched
    return n                                           # lists never handled

print(bad_count({"id": {"id": 1}}, "id"))              # Output: 1  <- expected 2
print(bad_count({"x": [{"id": 1}]}, "id"))             # Output: 0  <- expected 1 (list skipped)
# ✅ Correct: always recurse into the value AND handle lists, like count_keys above
```

---

## 🎯 Interview Tip (1 line)
Say: "Recursion must visit dict values and list items; I use Counter because it gives 0 for absent keys and handles the tally for me."

---

## 🔗 Related Questions
→ Q066 (count occurrences) | Q252 (collections) | Q073 (flatten dict) | Q199 (deep diff)
