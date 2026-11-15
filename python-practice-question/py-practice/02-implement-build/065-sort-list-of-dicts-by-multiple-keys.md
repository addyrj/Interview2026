---

# Q065. Sort List of Dicts by Multiple Keys
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Given employees as dicts, sort by `dept` ascending, then `age` ascending. Then show how to sort `dept` ascending but `sal` DESCENDING.

```python
users = [
    {"name": "Ann", "dept": "IT", "age": 30, "sal": 5},
    {"name": "Bob", "dept": "HR", "age": 25, "sal": 7},
    {"name": "Cy",  "dept": "IT", "age": 25, "sal": 9},
    {"name": "Di",  "dept": "IT", "age": 30, "sal": 8},
]
```

---

## 💡 Quick Concept (2 lines only)
Use a tuple as the sort key - Python compares tuples element by element. For mixed directions, negate numbers or sort in several stable passes (last key first).
हिंदी: Key में tuple दो — Python पहले element से compare करता है, बराबर हो तो अगले से।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

from operator import itemgetter  # itemgetter("a", "b") returns a tuple key

users = [
    {"name": "Ann", "dept": "IT", "age": 30, "sal": 5},   # sample data
    {"name": "Bob", "dept": "HR", "age": 25, "sal": 7},
    {"name": "Cy",  "dept": "IT", "age": 25, "sal": 9},
    {"name": "Di",  "dept": "IT", "age": 30, "sal": 8},
]

def sort_by_keys(rows: list[dict], *keys: str) -> list[dict]:
    return sorted(rows, key=itemgetter(*keys))   # Step 1: tuple key (dept, age, ...) - ascending for all

# ============================================
# TEST CASES
# ============================================

print([r["name"] for r in sort_by_keys(users, "dept", "age")])
# Expected: ['Bob', 'Cy', 'Ann', 'Di']   (HR first; in IT, age 25 before 30; Ann/Di tie keeps input order - stable)

# Mixed direction: dept ASC, sal DESC -> negate the number
print([r["name"] for r in sorted(users, key=lambda r: (r["dept"], -r["sal"]))])
# Expected: ['Bob', 'Cy', 'Di', 'Ann']
print(sort_by_keys([], "dept"))                  # Expected: []
```

---

## 🔍 Why This Works (3 lines max)
Tuples compare lexicographically, so the second key only matters when the first ties. `sorted` is stable, so fully equal keys keep their original order (Ann before Di).
हिंदी: Tuple lexicographic compare होता है और `sorted` stable है — बराबर वालों का order नहीं बदलता।

---

## ⚡ Alternative Solution
```python
from operator import itemgetter                      # key getter

def multi_sort(rows, spec):                          # spec: [(key, reverse), ...] - works for STRINGS too
    out = list(rows)                                 # copy so input is not mutated
    for k, rev in reversed(spec):                    # sort by the LEAST important key first
        out.sort(key=itemgetter(k), reverse=rev)     # stable sorts stack up correctly
    return out

print([r["name"] for r in multi_sort(users, [("dept", False), ("age", True), ("name", False)])])
# Expected: ['Bob', 'Ann', 'Di', 'Cy']   (dept asc, age desc, name asc)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: sorting passes in the WRONG order (most important key first)
print([r["name"] for r in sorted(sorted(users, key=itemgetter("dept")), key=itemgetter("age"))])
# ['Bob', 'Cy', 'Ann', 'Di'] - age wins, dept is only the tiebreaker (verified), not "dept then age"

# ❌ Wrong: reverse=True flips ALL keys, not just one
print([r["name"] for r in sorted(users, key=itemgetter("dept", "age"), reverse=True)])
# ['Ann', 'Di', 'Cy', 'Bob'] (verified)  <- dept AND age both descending
# ❌ Wrong: missing/None values -> TypeError: '<' not supported between instances of 'NoneType' and 'int'
# ✅ Correct: tuple key, or stable passes from last key to first; handle None with (v is None, v)
```

---

## 🎯 Interview Tip (1 line)
Say: "Tuple key via `itemgetter`, negate numbers for descending, and rely on sort stability for multi-pass."

---

## 🔗 Related Questions
→ Q113 (sorted with key) | Q258 (sorted key tricks) | Q064 (group by key) | Q010 (sorted vs list.sort)
