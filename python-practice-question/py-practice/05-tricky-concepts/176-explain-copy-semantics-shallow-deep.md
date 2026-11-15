---

# Q176. Explain Copy Semantics (Shallow / Deep)
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Explain assignment vs shallow copy vs deep copy. What does the code print after mutating a nested list?

---

## 💡 Quick Concept (2 lines only)
Assignment copies nothing (same object); a shallow copy duplicates the outer container but shares inner objects; a deep copy duplicates everything recursively.
हिंदी: Assignment सिर्फ नाम जोड़ता है, shallow copy ऊपर की परत copy करता है, deep copy अंदर तक सब copy करता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import copy                                  # Step 1: copy module

orig = [[1, 2], [3, 4]]                      # nested list
alias = orig                                 # Step 2: same object, new name
shallow = orig.copy()                        # outer list copied, inner lists shared
deep = copy.deepcopy(orig)                   # everything copied
orig[0].append(99)                           # mutate an INNER list

# ============================================
# TEST CASES
# ============================================
print(alias)                                 # Expected: [[1, 2, 99], [3, 4]]
print(shallow)                               # Expected: [[1, 2, 99], [3, 4]]  (shares inner list)
print(deep)                                  # Expected: [[1, 2], [3, 4]]      (independent)
orig.append([5])                             # mutate the OUTER list
print(len(shallow), len(alias), len(deep))   # Expected: 2 3 2
print(shallow[0] is orig[0], deep[0] is orig[0])  # Expected: True False
```

---

## 🔍 Why This Works (3 lines max)
`list.copy()`, `[:]`, `dict.copy()`, `copy.copy()` are all shallow: new outer object, same inner references. `deepcopy` walks the structure (with a memo dict, so cycles are fine) and builds new objects; classes can customize it via `__deepcopy__`.
हिंदी: Shallow में inner objects वही रहते हैं; `deepcopy` memo से cycles भी संभाल लेता है।

---

## ⚡ Alternative Solution
```python
import copy                                  # module

d = {"a": [1], "b": {"c": 1}}                # nested dict
sh = d.copy()                                # shallow
sh["a"].append(2)                            # mutates shared list
sh["b"]["c"] = 5                             # mutates shared dict
print(d)                                     # Expected: {'a': [1, 2], 'b': {'c': 5}}

# Immutables are never really copied
t = (1, 2)                                   # tuple of immutables
print(copy.copy(t) is t, copy.deepcopy(t) is t)    # Expected: True True
t2 = (1, [2])                                # tuple containing a list
print(copy.copy(t2) is t2, copy.deepcopy(t2) is t2)  # Expected: True False

# Cycles are handled
a: list = [1]                                # self-referencing list
a.append(a)
b = copy.deepcopy(a)                         # no infinite recursion
print(b, b[1] is b)                          # Expected: [1, [...]] True

# Custom hook
class Box:
    def __init__(self) -> None:
        self.items = [1]                     # state
    def __deepcopy__(self, memo):            # called by deepcopy
        print("custom deepcopy")             # Expected: custom deepcopy
        n = Box()                            # build new
        n.items = list(self.items)           # copy state
        return n
bx = copy.deepcopy(Box())                    # triggers hook
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: [[0]*2]*2 repeats the SAME inner list
grid = [[0] * 2] * 2
grid[0][0] = 1
print(grid)                                  # Output: [[1, 0], [1, 0]]

# ✅ Correct: build each row separately
grid = [[0] * 2 for _ in range(2)]
grid[0][0] = 1
print(grid)                                  # Output: [[1, 0], [0, 0]]
```

---

## 🎯 Interview Tip (1 line)
Say: "Python passes/assigns references; shallow copy shares nested objects, so use `copy.deepcopy` (or rebuild) when nested data must be independent."

---

## 🔗 Related Questions
→ Q005 (list multiplication aliasing) | Q006 (shallow vs deepcopy) | Q071 (deep clone a dict) | Q293 (shallow vs deep copy) | Q304 (pass by object reference)
