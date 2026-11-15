---

# Q073. Flatten a nested dict
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `flatten_dict(d, sep=".")` that turns nested dicts into a single-level dict with joined keys. Leave lists and empty dicts as leaf values.

```python
flatten_dict({"a": 1, "b": {"c": 2, "d": {"e": 3}}})
# {'a': 1, 'b.c': 2, 'b.d.e': 3}
```

---

## 💡 Quick Concept (2 lines only)
Recurse into every non-empty dict, carrying the key path so far (`parent`); when the value is not a dict, store it under the joined path. Used for env-var names, CSV columns, log fields.
हिंदी: Nested keys को "a.b.c" जैसे एक level की key में जोड़ दो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
def flatten_dict(d: dict, parent: str = "", sep: str = ".") -> dict:
    out: dict = {}                                     # Step 1: result dict
    for k, v in d.items():                             # Step 2: walk each key/value
        key = f"{parent}{sep}{k}" if parent else str(k)  # Step 3: build full dotted path
        if isinstance(v, dict) and v:                  # Step 4: non-empty dict -> go deeper
            out.update(flatten_dict(v, key, sep))      # merge the flattened child into result
        else:                                          # Step 5: leaf (scalar, list, empty dict)
            out[key] = v                               # store under the full path
    return out                                         # Step 6: return flat dict

def unflatten(flat: dict, sep: str = ".") -> dict:     # bonus: the reverse operation
    out: dict = {}                                     # result
    for k, v in flat.items():                          # each dotted key
        cur = out                                      # start at the root
        *parts, last = k.split(sep)                    # split path; last part holds the value
        for p in parts:                                # create intermediate dicts
            cur = cur.setdefault(p, {})                # reuse existing or make a new one
        cur[last] = v                                  # set the leaf value
    return out                                         # return nested dict

# ============================================
# TEST CASES
# ============================================
nested = {"a": 1, "b": {"c": 2, "d": {"e": 3}}, "f": {}, "g": [1, {"h": 2}]}  # sample
print(flatten_dict(nested))                            # Expected: {'a': 1, 'b.c': 2, 'b.d.e': 3, 'f': {}, 'g': [1, {'h': 2}]}
print(flatten_dict(nested, sep="/"))                   # Expected: {'a': 1, 'b/c': 2, 'b/d/e': 3, 'f': {}, 'g': [1, {'h': 2}]}
print(unflatten({"a.b": 1, "a.c": 2, "d": 3}))         # Expected: {'a': {'b': 1, 'c': 2}, 'd': 3}
```

---

## 🔍 Why This Works (3 lines max)
The path prefix is passed down each recursive call, so a leaf knows its full address. Empty dicts and lists are kept as leaves so no data silently disappears.
हिंदी: Recursion के साथ path आगे बढ़ता है, leaf पर पहुँचकर full key बन जाती है।

---

## ⚡ Alternative Solution
```python
# Iterative with an explicit stack (no recursion-limit risk on very deep dicts)
def flatten_iter(d: dict, sep: str = ".") -> dict:
    out: dict = {}                                     # result
    stack = [("", d)]                                  # (path-so-far, dict-to-visit)
    while stack:                                       # until nothing left
        prefix, cur = stack.pop()                      # take one dict
        for k, v in cur.items():                       # visit its items
            key = f"{prefix}{sep}{k}" if prefix else str(k)  # full path
            if isinstance(v, dict) and v:              # nested dict -> push for later
                stack.append((key, v))
            else:                                      # leaf -> store
                out[key] = v
    return out

print(flatten_iter({"a": 1, "b": {"c": 2, "d": {"e": 3}}, "f": {}}))  # Expected: {'a': 1, 'f': {}, 'b.c': 2, 'b.d.e': 3}  (key ORDER differs)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: passes only the last key as parent, losing the upper path
def flat_bad(d: dict, parent: str = "") -> dict:
    out: dict = {}                                     # result
    for k, v in d.items():                             # loop
        if isinstance(v, dict):
            out.update(flat_bad(v, k))                 # ❌ should pass the FULL path, not just k
        else:
            out[f"{parent}.{k}" if parent else k] = v  # builds a wrong key
    return out

print(flat_bad({"b": {"c": 2, "d": {"e": 3}}}))        # Output: {'b.c': 2, 'd.e': 3}  <- 'b.d.e' expected!
# ✅ Correct: build `key = f"{parent}{sep}{k}"` first, then recurse with `key`
```

---

## 🎯 Interview Tip (1 line)
Mention edge cases up front: empty dict (keep or drop?), keys containing the separator, and lists (index paths like `g.0.h` or leave as-is).

---

## 🔗 Related Questions
→ Q058 (flatten list) | Q059 (deep flatten list) | Q074 (dotted path) | Q196 (CSV to JSON)
