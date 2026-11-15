---

# Q071. Deep clone a dict
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `deep_clone(obj)` that returns a fully independent copy of a nested dict (dicts, lists, sets, tuples inside). Changing the clone must never change the original. Bonus: it must not crash on a self-referencing dict.

```python
src = {"a": 1, "b": [1, 2, {"c": 3}]}
clone = deep_clone(src)
clone["b"][2]["c"] = 99
print(src["b"][2]["c"])  # must still be 3
```

---

## 💡 Quick Concept (2 lines only)
A shallow copy (`dict.copy()`) copies only the top level — nested objects are still shared. A deep clone recurses and keeps a `memo` (id -> copy) so cycles don't loop forever.
हिंदी: Shallow copy में अंदर के objects shared रहते हैं; deep clone हर level पर नई copy बनाता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import copy                                            # used later to compare with the stdlib
import json                                            # used to show the JSON-roundtrip trap
from typing import Any                                 # type hint for "any value"

def deep_clone(obj: Any, _memo: dict[int, Any] | None = None) -> Any:
    memo = {} if _memo is None else _memo              # Step 1: memo maps id(original) -> clone (cycle guard)
    if id(obj) in memo:                                # Step 2: already cloned this object? reuse it
        return memo[id(obj)]                           # return the same clone (keeps the cycle intact)
    if isinstance(obj, dict):                          # Step 3: dict -> build a new dict
        new: Any = {}                                  # create empty dict first
        memo[id(obj)] = new                            # register BEFORE recursing so cycles resolve
        for k, v in obj.items():                       # walk every key/value
            new[deep_clone(k, memo)] = deep_clone(v, memo)  # clone both key and value
        return new                                     # return the finished clone
    if isinstance(obj, list):                          # Step 4: list -> new list
        new = []                                       # empty list
        memo[id(obj)] = new                            # register for cycle safety
        new.extend(deep_clone(i, memo) for i in obj)   # clone each element
        return new                                     # return clone
    if isinstance(obj, set):                           # Step 5: set -> new set of cloned items
        return {deep_clone(i, memo) for i in obj}      # items must be hashable so they are usually immutable
    if isinstance(obj, tuple):                         # Step 6: tuple may hide mutable items
        return tuple(deep_clone(i, memo) for i in obj) # rebuild tuple from cloned items
    return obj                                         # Step 7: int/str/None... are immutable, share them

# ============================================
# TEST CASES
# ============================================
src = {"a": 1, "b": [1, 2, {"c": 3}], "d": {"e": (1, [2])}}  # nested sample
c = deep_clone(src)                                    # clone it
print(c == src, c is src, c["b"] is src["b"], c["b"][2] is src["b"][2])  # Expected: True False False False
c["b"][2]["c"] = 99                                    # mutate deep inside the clone
print(src["b"][2]["c"])                                # Expected: 3  (original untouched)

cyc: dict = {"name": "loop"}                           # self-referencing dict
cyc["self"] = cyc                                      # cyc -> cyc
cc = deep_clone(cyc)                                   # must not recurse forever
print(cc["self"] is cc, cc is cyc)                     # Expected: True False

print(copy.deepcopy(src) == src)                       # Expected: True  (stdlib gives the same result)
print(json.loads(json.dumps(src)))                     # Expected: {'a': 1, 'b': [1, 2, {'c': 3}], 'd': {'e': [1, [2]]}}  <- tuple became list!
```

---

## 🔍 Why This Works (3 lines max)
Every container type is rebuilt recursively, so no inner object is shared; immutable leaves (int, str, None) are safe to share. Registering the new container in `memo` before recursing is what makes cycles terminate.
हिंदी: हर container नया बनता है और memo cycles को रोकता है; immutable values share करना safe है।

---

## ⚡ Alternative Solution
```python
# Pythonic: just use the standard library (handles classes, cycles, __deepcopy__)
import copy                                            # stdlib module

src = {"a": [1, 2, {"c": 3}]}                          # sample data
clone = copy.deepcopy(src)                             # one-liner deep clone
clone["a"][2]["c"] = 99                                # mutate the clone
print(src["a"][2]["c"])                                # Expected: 3
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: shallow copy — inner list is still shared
src = {"b": [1, 2]}                                    # original
sh = src.copy()                                        # same as dict(src) or {**src}: top level only
sh["b"].append(4)                                      # mutates the SHARED inner list
print(src["b"])                                        # Output: [1, 2, 4]  <- original changed!

# ❌ Also wrong: json.loads(json.dumps(x)) turns tuples into lists and fails on sets/datetime
# ✅ Correct: copy.deepcopy(src) or the recursive deep_clone above
```

---

## 🎯 Interview Tip (1 line)
Say: "dict.copy() is shallow; for a real clone I use copy.deepcopy, and if asked to hand-roll it I add a memo dict to survive circular references."

---

## 🔗 Related Questions
→ Q006 (shallow vs deepcopy) | Q176 (copy semantics) | Q293 (shallow vs deep copy) | Q072 (deep merge)
