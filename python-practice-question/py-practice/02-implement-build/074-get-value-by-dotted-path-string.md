---

# Q074. Get value by dotted path string
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `get_path(obj, "a.b.0.c", default=None)` that safely walks nested dicts and lists using a dotted string. If any step is missing, return `default` instead of raising.

```python
get_path({"user": {"tags": ["a", "b"]}}, "user.tags.1")  # 'b'
get_path({"user": {}}, "user.phone.home", "none")        # 'none'
```

---

## 💡 Quick Concept (2 lines only)
Split the path and walk one step at a time: dict -> key lookup, list -> integer index. Any failed step returns `default` — Python's version of JS optional chaining `a?.b?.c`.
हिंदी: Path को split करके एक-एक step चलो; कुछ missing हो तो default लौटाओ।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Any                                 # type hint

def get_path(obj: Any, path: str, default: Any = None, sep: str = ".") -> Any:
    cur = obj                                          # Step 1: start at the root object
    for part in path.split(sep):                       # Step 2: take each path segment
        if isinstance(cur, dict) and part in cur:      # Step 3a: dict and key exists
            cur = cur[part]                            # go one level deeper
        elif (isinstance(cur, (list, tuple))           # Step 3b: list/tuple and part is an int index
              and part.lstrip("-").isdigit()           # allow negative indexes like "-1"
              and -len(cur) <= int(part) < len(cur)):  # index must be in range
            cur = cur[int(part)]                       # go one level deeper
        else:                                          # Step 4: anything else = path broken
            return default                             # give back the fallback
    return cur                                         # Step 5: reached the end, return the value

# ============================================
# TEST CASES
# ============================================
data = {"user": {"name": "Asha", "tags": ["a", "b"], "address": {"city": "Pune", "zip": None}}}  # sample
print(get_path(data, "user.name"))                     # Expected: Asha
print(get_path(data, "user.tags.1"))                   # Expected: b
print(get_path(data, "user.address.city"))             # Expected: Pune
print(get_path(data, "user.address.zip", "n/a"))       # Expected: None  (key EXISTS, value is None, so no default)
print(get_path(data, "user.phone.home", "none"))       # Expected: none
print(get_path(data, "user.tags.5", "oob"))            # Expected: oob   (index out of range)
```

---

## 🔍 Why This Works (3 lines max)
Each loop iteration narrows `cur`; we check "does this step exist?" with `in` / range checks instead of try/except. A key that exists with value `None` is returned as `None`, not replaced by `default`.
हिंदी: हर step पर check होता है कि key/index मौजूद है; नहीं तो default वापस।

---

## ⚡ Alternative Solution
```python
# Pythonic: functools.reduce (raises KeyError on a missing step)
from functools import reduce                           # fold helper

data = {"user": {"address": {"city": "Pune"}}}         # sample
print(reduce(lambda c, k: c[k], "user.address.city".split("."), data))  # Expected: Pune
try:
    reduce(lambda c, k: c[k], "user.phone.home".split("."), data)  # 'phone' missing
except KeyError as e:                                  # reduce version does not give a default
    print("KeyError", e)                               # Expected: KeyError 'phone'
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: treats None as "missing" and breaks on valid falsy values
def get_path_none(obj: dict, path: str) -> object:
    cur = obj                                          # root
    for p in path.split("."):                          # each segment
        cur = cur.get(p)                               # .get returns None for missing keys
        if cur is None:                                # ❌ can't tell "missing" from "stored None"
            return "n/a"
    return cur

print(get_path_none({"user": {"address": {"zip": None}}}, "user.address.zip"))  # Output: n/a  <- real value was None
# ✅ Correct: check `part in cur` (or use a sentinel object()) so None stays a valid value
```

---

## 🎯 Interview Tip (1 line)
Say: "I use `in` checks or a sentinel instead of `.get()` so a stored None/0/'' isn't mistaken for missing" — it shows you know falsy traps.

---

## 🔗 Related Questions
→ Q073 (flatten dict) | Q076 (pick keys) | Q130 (too-broad except) | Q192 (config loader)
