---

# Q127. Fix Dict Changed Size During Iteration
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
This function should remove all inactive users from a dict. Instead it crashes with `RuntimeError: dictionary changed size during iteration`. Find and fix the bug.

```python
# BUGGY CODE:
def drop_inactive_buggy(users: dict[str, bool]) -> dict[str, bool]:
    for name, active in users.items():  # iterating over a live view of the dict
        if not active:                  # inactive user found
            del users[name]             # ❌ dict size changes while iterating
    return users

drop_inactive_buggy({"a": True, "b": False, "c": True})  # RuntimeError
```

---

## 💡 Quick Concept (2 lines only)
`dict.items()` is a live view, not a copy — adding or deleting keys during the loop invalidates the iterator, so Python raises `RuntimeError`. Iterate over a snapshot (`list(...)`) or build a new dict.
हिंदी: `.items()` live view है, copy नहीं — loop के दौरान keys add/delete करोगे तो RuntimeError आएगा।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

def drop_inactive_buggy(users: dict[str, bool]) -> dict[str, bool]:
    for name, active in users.items():  # live view over the dict
        if not active:                  # inactive user
            del users[name]             # size changes -> iterator breaks
    return users                        # never reached on failure

try:
    drop_inactive_buggy({"a": True, "b": False, "c": True})  # run the buggy version
except RuntimeError as e:               # catch the crash
    print("Error:", e)                  # Expected: Error: dictionary changed size during iteration

# Step 1: iterate over a SNAPSHOT of the items, mutate the real dict
def drop_inactive(users: dict[str, bool]) -> dict[str, bool]:
    for name, active in list(users.items()):  # list() copies items first
        if not active:                        # inactive user
            del users[name]                   # safe: we are looping over the copy
    return users                              # return the cleaned dict

# ============================================
# TEST CASES
# ============================================
print(drop_inactive({"a": True, "b": False, "c": True}))  # Expected: {'a': True, 'c': True}
print(drop_inactive({}))                                  # Expected: {}
print(drop_inactive({"x": False}))                        # Expected: {}
```

---

## 🔍 Why This Works (3 lines max)
`list(users.items())` makes a separate list, so deleting from `users` no longer affects the loop. CPython checks the dict size on every `next()` and raises `RuntimeError` if it changed. Changing only the VALUE of an existing key is allowed (size is the same).
हिंदी: copy पर loop चलाओ और original dict को modify करो — तब iterator नहीं टूटता।

---

## ⚡ Alternative Solution
```python
# Alternative 1: dict comprehension — build a NEW dict (most Pythonic)
def drop_inactive_comp(users: dict[str, bool]) -> dict[str, bool]:
    return {n: a for n, a in users.items() if a}  # keep only active users

print(drop_inactive_comp({"a": True, "b": False, "c": True}))  # Output: {'a': True, 'c': True}

# Alternative 2: collect keys first, then pop them
d = {"a": False, "b": True}                         # sample data
for k in [k for k, v in d.items() if not v]:        # list of keys to remove
    d.pop(k)                                        # safe: list is already built
print(d)                                            # Output: {'b': True}

# Adding keys has the same problem — loop over list(d) instead
d = {"a": 1, "b": 2}                                # sample data
for k in list(d):                                   # snapshot of keys
    d[k + "_copy"] = d[k]                           # adding is safe now
print(d)                                            # Output: {'a': 1, 'b': 2, 'a_copy': 1, 'b_copy': 2}
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: thinking only deletion is dangerous — adding keys breaks it too
d = {"a": 1}                       # sample dict
try:
    for k in d:                    # iterating over live keys
        d["new"] = 1               # adding a key changes size
except RuntimeError as e:
    print(e)                       # Output: dictionary changed size during iteration

# ✅ Correct: changing values of EXISTING keys is fine
d = {"a": 1, "b": 2}               # sample dict
for k in d:                        # iterating over live keys
    d[k] = d[k] * 10               # same size, no error
print(d)                           # Output: {'a': 10, 'b': 20}
```

---

## 🎯 Interview Tip (1 line)
Say: "Never change a dict's size while iterating it — loop over `list(d.items())` or build a new dict with a comprehension."

---

## 🔗 Related Questions
→ Q126 (mutating list while iterating) | Q011 (dict ordering and update) | Q175 (mutability and hashability) | Q241 (comprehensions)
