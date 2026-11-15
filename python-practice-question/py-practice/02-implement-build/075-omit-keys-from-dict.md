---

# Q075. Omit keys from dict
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `omit(d, keys)` that returns a NEW dict without the given keys. Missing keys must be ignored and the original dict must stay unchanged.

```python
omit({"id": 1, "name": "A", "password": "x"}, ["password"])  # {'id': 1, 'name': 'A'}
```

---

## 💡 Quick Concept (2 lines only)
A dict comprehension filtered by `k not in drop` builds a new dict in one pass; converting `keys` to a `set` makes each lookup O(1). Typical use: hiding `password`/`token` before returning a response.
हिंदी: Comprehension से unwanted keys हटाकर नया dict बनाओ, original को मत छुओ।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
def omit(d: dict, keys: list[str]) -> dict:
    drop = set(keys)                                   # Step 1: set -> O(1) membership checks
    return {k: v for k, v in d.items() if k not in drop}  # Step 2: keep only keys not in drop

def omit_nested(d: dict, keys: list[str]) -> dict:     # bonus: removes the keys at every depth
    drop = set(keys)                                   # keys to remove
    return {
        k: (omit_nested(v, keys) if isinstance(v, dict) else v)  # recurse into child dicts
        for k, v in d.items() if k not in drop         # skip dropped keys at this level
    }

# ============================================
# TEST CASES
# ============================================
u = {"id": 1, "name": "A", "password": "x", "token": "t"}  # sample user
print(omit(u, ["password", "token"]))                  # Expected: {'id': 1, 'name': 'A'}
print(u)                                               # Expected: {'id': 1, 'name': 'A', 'password': 'x', 'token': 't'}  (unchanged)
print(omit(u, ["nope"]))                               # Expected: {'id': 1, 'name': 'A', 'password': 'x', 'token': 't'}  (missing key ignored)
print(omit_nested({"a": 1, "p": 2, "n": {"p": 3, "b": 4}}, ["p"]))  # Expected: {'a': 1, 'n': {'b': 4}}
```

---

## 🔍 Why This Works (3 lines max)
The comprehension never touches the source dict, it only reads it, so no mutation occurs. Keys that don't exist are simply never matched, so no `KeyError`.
हिंदी: Comprehension सिर्फ पढ़ता है, इसलिए original safe रहता है और missing key पर error नहीं आता।

---

## ⚡ Alternative Solution
```python
# Copy then pop with a default (also never raises)
u = {"id": 1, "name": "A", "password": "x", "token": "t"}  # sample
copyd = dict(u)                                        # shallow copy first
for k in ["password", "token"]:                        # keys to remove
    copyd.pop(k, None)                                 # pop(k, default) ignores missing keys
print(copyd)                                           # Expected: {'id': 1, 'name': 'A'}
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: deleting from the original dict (mutates the caller's data)
u = {"id": 1, "name": "A", "password": "x", "token": "t"}  # sample
bad = u                                                # same object, not a copy!
del bad["password"]                                    # removes it from u as well
print(u)                                               # Output: {'id': 1, 'name': 'A', 'token': 't'}  <- password gone from original
# ✅ Correct: build a new dict with a comprehension, or copy before pop()
```

---

## 🎯 Interview Tip (1 line)
Say: "I return a new dict, use a set for O(1) lookups, and pop(k, None) / comprehension so missing keys never raise."

---

## 🔗 Related Questions
→ Q076 (pick keys) | Q071 (deep clone) | Q068 (remove falsy) | Q233 (response models)
