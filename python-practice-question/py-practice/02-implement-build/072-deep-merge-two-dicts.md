---

# Q072. Deep merge two dicts
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `deep_merge(a, b)` that merges `b` into `a` recursively. When both values are dicts, merge them; otherwise the value from `b` wins. Do NOT mutate the inputs.

```python
a = {"n": {"x": 1, "y": 2}}
b = {"n": {"y": 20, "z": 30}}
print(deep_merge(a, b))  # {'n': {'x': 1, 'y': 20, 'z': 30}}
```

---

## 💡 Quick Concept (2 lines only)
`a | b` and `{**a, **b}` merge only the top level — a nested dict in `b` REPLACES the one in `a`. A deep merge recurses whenever both sides are dicts (typical for config overrides).
हिंदी: `|` सिर्फ top level merge करता है; deep merge अंदर के dicts को भी जोड़ता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from functools import reduce                           # used for merging many dicts

def deep_merge(a: dict, b: dict) -> dict:
    out = dict(a)                                      # Step 1: shallow copy of a so inputs stay untouched
    for k, v in b.items():                             # Step 2: go through every key of b
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):  # Step 3: both sides dicts?
            out[k] = deep_merge(out[k], v)             # recurse and store merged child
        else:                                          # Step 4: otherwise b's value wins
            out[k] = v                                 # overwrite / add the key
    return out                                         # Step 5: return the merged dict

def merge_all(*dicts: dict) -> dict:
    return reduce(deep_merge, dicts, {})               # fold many dicts left-to-right (later wins)

# ============================================
# TEST CASES
# ============================================
d1 = {"a": 1, "n": {"x": 1, "y": 2}, "l": [1]}         # base config
d2 = {"b": 2, "n": {"y": 20, "z": 30}, "l": [2]}       # overrides
print(deep_merge(d1, d2))                              # Expected: {'a': 1, 'n': {'x': 1, 'y': 20, 'z': 30}, 'l': [2], 'b': 2}
print(d1)                                              # Expected: {'a': 1, 'n': {'x': 1, 'y': 2}, 'l': [1]}  (unchanged)
print(d1 | d2)                                         # Expected: {'a': 1, 'n': {'y': 20, 'z': 30}, 'l': [2], 'b': 2}  <- 'x' lost!
print(deep_merge({"a": {"b": 1}}, {"a": 5}))           # Expected: {'a': 5}
print(deep_merge({"a": 5}, {"a": {"b": 1}}))           # Expected: {'a': {'b': 1}}
print(merge_all({"a": {"x": 1}}, {"a": {"y": 2}}, {"a": {"x": 9}}))  # Expected: {'a': {'x': 9, 'y': 2}}
```

---

## 🔍 Why This Works (3 lines max)
Only when both values are dicts do we recurse; any other combination is a plain override, so lists and scalars from `b` replace those in `a`. Copying `a` first (and building new dicts on recursion) keeps inputs unmodified.
हिंदी: दोनों तरफ dict हो तभी recursion, वरना b की value जीतती है।

---

## ⚡ Alternative Solution
```python
# Pythonic: dict comprehension over the union of keys
def deep_merge2(a: dict, b: dict) -> dict:
    return {                                           # build the result in one expression
        k: (deep_merge2(a[k], b[k])                    # both present and both dicts -> recurse
            if k in a and k in b and isinstance(a[k], dict) and isinstance(b[k], dict)
            else b[k] if k in b else a[k])             # else prefer b, fall back to a
        for k in a.keys() | b.keys()                   # every key from either side (set order varies)
    }

print(deep_merge2({"n": {"x": 1}}, {"n": {"y": 2}}))   # Expected: {'n': {'x': 1, 'y': 2}}
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: mutates the first argument in place (surprising side effect)
def bad(a: dict, b: dict) -> dict:
    for k, v in b.items():                             # loop over b
        if isinstance(v, dict) and k in a:             # nested dict present in a
            bad(a[k], v)                               # recurse INTO a's dict, changing it
        else:
            a[k] = v                                   # writes into the caller's dict
    return a

x = {"n": {"x": 1}}                                    # caller's dict
bad(x, {"n": {"y": 2}})                                # result is thrown away...
print(x)                                               # Output: {'n': {'x': 1, 'y': 2}}  <- x was changed!
# ✅ Correct: copy first (dict(a)) and return a new dict, as in the solution
```

---

## 🎯 Interview Tip (1 line)
Clarify the rules out loud: "dict+dict recurses, everything else (including lists) is overridden — and I won't mutate the inputs."

---

## 🔗 Related Questions
→ Q071 (deep clone) | Q073 (flatten dict) | Q192 (config loader) | Q199 (deep diff)
