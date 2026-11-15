---

# Q293. Shallow vs Deep Copy
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is the difference between assignment, shallow copy and deep copy? Show it with a nested list.

---

## 💡 Quick Concept (2 lines only)
Assignment copies nothing (same object). Shallow copy duplicates the outer container but shares inner objects. Deep copy duplicates everything recursively.
हिंदी: Shallow copy में अंदर के objects shared रहते हैं, deep copy में सब कुछ नया बनता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import copy  # stdlib copy module

original = [[1, 2], [3, 4]]  # Step 1: nested list

alias = original  # Step 2: same object
shallow = copy.copy(original)  # Step 3: new outer list, same inner lists
deep = copy.deepcopy(original)  # Step 4: fully independent copy

original[0].append(99)  # Step 5: mutate an INNER list

# ============================================
# TEST CASES
# ============================================
print(alias)  # Expected: [[1, 2, 99], [3, 4]]
print(shallow)  # Expected: [[1, 2, 99], [3, 4]]  (inner list shared)
print(deep)  # Expected: [[1, 2], [3, 4]]  (unaffected)
print(shallow is original, shallow[0] is original[0])  # Expected: False True
print(deep[0] is original[0])  # Expected: False

original.append([5])  # mutate the OUTER list
print(len(original), len(shallow), len(deep))  # Expected: 3 2 2
```

---

## 🔍 Why This Works (3 lines max)
`copy.copy` creates a new outer list but copies only references to the inner lists. `deepcopy` walks the structure and clones each object (and handles cycles with a memo dict). `list[:]`, `.copy()` and `list()` are all shallow.
हिंदी: `[:]`, `.copy()`, `list()` सब shallow हैं — nested data के लिए `deepcopy` चाहिए।

---

## ⚡ Alternative Solution
```python
import copy  # stdlib


class Node:  # object with a self reference
    def __init__(self) -> None:
        self.me = self  # cycle


n = Node()  # create
n2 = copy.deepcopy(n)  # deepcopy handles cycles
print(n2.me is n2, n2 is n)  # Expected: True False

data = {"a": [1, 2]}  # dict with a list
print(data.copy()["a"] is data["a"])  # Expected: True (dict.copy is shallow)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: believing [:] gives an independent copy of a 2D grid
grid = [[0, 0], [0, 0]]  # 2D list
bad = grid[:]  # shallow
bad[0][0] = 1  # changes grid too
print(grid)  # [[1, 0], [0, 0]]

# ✅ Correct: deepcopy, or copy each row
good = [row[:] for row in [[0, 0], [0, 0]]]  # independent rows
print(good)  # Expected: [[0, 0], [0, 0]]
```

---

## 🎯 Interview Tip (1 line)
Say: "Shallow copies share nested objects; for nested mutable data I use copy.deepcopy - and note it is slower."

---

## 🔗 Related Questions
→ Q006 (shallow vs deepcopy output) | Q005 (list multiplication aliasing) | Q071 (deep clone a dict) | Q176 (copy semantics)
