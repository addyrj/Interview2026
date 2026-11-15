---

# Q199. Build deep diff utility
# Category: REAL WORLD PROBLEMS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build `deep_diff(old, new)` that compares two nested structures (dicts and lists) and returns a list of changes: `added`, `removed`, `changed`, each with a dotted/indexed path.

```python
deep_diff({"a": {"b": 1}}, {"a": {"b": 2}, "c": 3})
# [{'op': 'changed', 'path': 'a.b', 'old': 1, 'new': 2}, {'op': 'added', 'path': 'c', 'new': 3}]
```

---

## 💡 Quick Concept (2 lines only)
Recurse through dicts (by key) and lists (by index), carrying a `path` string; at the leaves record a change if values differ.
हिंदी: दोनों structure में recursion से चलो, path साथ रखो, और leaf पर अलग values मिलें तो change लिख दो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Any                               # loose value type

def deep_diff(old: Any, new: Any, path: str = "") -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []               # list of change records
    if isinstance(old, dict) and isinstance(new, dict):  # both dicts -> compare keys
        for key in old.keys() | new.keys():          # union of all keys
            p = f"{path}.{key}" if path else str(key)  # dotted path to this key
            if key not in new:                       # key only in old
                changes.append({"op": "removed", "path": p, "old": old[key]})
            elif key not in old:                     # key only in new
                changes.append({"op": "added", "path": p, "new": new[key]})
            else:                                    # key in both -> recurse
                changes.extend(deep_diff(old[key], new[key], p))
    elif isinstance(old, list) and isinstance(new, list):  # both lists -> compare by index
        for i in range(max(len(old), len(new))):     # cover the longer list
            p = f"{path}[{i}]"                       # index path
            if i >= len(new):                        # list got shorter
                changes.append({"op": "removed", "path": p, "old": old[i]})
            elif i >= len(old):                      # list got longer
                changes.append({"op": "added", "path": p, "new": new[i]})
            else:                                    # same index -> recurse
                changes.extend(deep_diff(old[i], new[i], p))
    elif old != new or type(old) is not type(new):   # leaf values differ (1 vs True too)
        changes.append({"op": "changed", "path": path, "old": old, "new": new})
    return changes                                   # all collected changes

# ============================================
# TEST CASES
# ============================================
a = {"name": "Ann", "age": 30, "tags": ["x", "y"], "addr": {"city": "Pune", "zip": "1"}}
b = {"name": "Ann", "age": 31, "tags": ["x"], "addr": {"city": "Delhi"}, "vip": True}
for c in sorted(deep_diff(a, b), key=lambda c: c["path"]):  # sort: set order of keys varies
    print(c)
print(deep_diff({"a": 1}, {"a": 1}))                 # Expected: []
print(deep_diff({"a": 1}, {"a": True}))              # type change is detected

# --- Real output (Python 3.13) ---
# {'op': 'changed', 'path': 'addr.city', 'old': 'Pune', 'new': 'Delhi'}
# {'op': 'removed', 'path': 'addr.zip', 'old': '1'}
# {'op': 'changed', 'path': 'age', 'old': 30, 'new': 31}
# {'op': 'removed', 'path': 'tags[1]', 'old': 'y'}
# {'op': 'added', 'path': 'vip', 'new': True}
# []
# [{'op': 'changed', 'path': 'a', 'old': 1, 'new': True}]
```

---

## 🔍 Why This Works (3 lines max)
Dict keys are compared via the union of both key sets: only in `old` = removed, only in `new` = added, in both = recurse. Using `type(old) is not type(new)` catches `1` vs `True`, which `==` treats as equal. Key order comes from a set, so the test sorts output.
हिंदी: Keys का union लेते हैं; सिर्फ old में = removed, सिर्फ new में = added, दोनों में = recurse।

---

## ⚡ Alternative Solution
```python
# ============================================
# ALTERNATIVE: flatten both dicts, then compare flat maps
# ============================================
from typing import Any                               # loose value type

def flatten(d: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}                         # flat result
    for k, v in d.items():                           # each key
        p = f"{prefix}.{k}" if prefix else k         # dotted path
        if isinstance(v, dict):                      # nested dict -> go deeper
            out.update(flatten(v, p))                # merge deeper keys
        else:                                        # leaf value
            out[p] = v                               # store it
    return out                                       # flat dict

def diff_flat(old: dict, new: dict) -> dict[str, tuple]:
    fo, fn = flatten(old), flatten(new)              # flatten both
    return {k: (fo.get(k, "<missing>"), fn.get(k, "<missing>"))  # (old, new) per key
            for k in sorted(fo.keys() | fn.keys())   # sorted -> deterministic output
            if fo.get(k, "<missing>") != fn.get(k, "<missing>")}  # keep only differences

print(diff_flat({"a": {"b": 1, "c": 2}}, {"a": {"b": 1, "c": 3}, "d": 4}))
# Expected: {'a.c': (2, 3), 'd': ('<missing>', 4)}

# --- Real output (Python 3.13) ---
# {'a.c': (2, 3), 'd': ('<missing>', 4)}
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: only == at the top level — tells you SOMETHING changed, not WHAT
print({"a": {"b": 1}} == {"a": {"b": 2}})   # False  (no path, no old/new values)
print(1 == True)                              # True   (so a pure == diff misses int -> bool)

# ✅ Correct: recurse and compare types too (see solution)
```

---

## 🎯 Interview Tip (1 line)
Say: "Lists are diffed by index here; for reordering-heavy data I'd diff by an id key or use LCS — tell the interviewer that trade-off."

---

## 🔗 Related Questions
→ Q078 (deep equal) | Q071 (deep clone) | Q072 (deep merge) | Q073 (flatten dict) | Q188 (state manager)
