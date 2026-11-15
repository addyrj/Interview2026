---

# Q076. Pick keys from dict
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `pick(d, keys)` that returns a new dict containing only the requested keys that exist in `d`. Missing keys are skipped (no error), and the output follows the order of `keys`.

```python
pick({"id": 1, "name": "A", "email": "a@x.com"}, ["id", "name"])  # {'id': 1, 'name': 'A'}
```

---

## 💡 Quick Concept (2 lines only)
Iterate over the WANTED keys (not the dict) and keep those present: `{k: d[k] for k in keys if k in d}`. It is the opposite of omit and is used to whitelist fields.
हिंदी: चाहिए वाली keys पर loop करो और सिर्फ मौजूद keys रखो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
def pick(d: dict, keys: list[str]) -> dict:
    return {k: d[k] for k in keys if k in d}           # Step 1: loop over wanted keys, Step 2: skip the missing ones

# ============================================
# TEST CASES
# ============================================
u = {"id": 1, "name": "A", "email": "a@x.com", "age": None}  # sample
print(pick(u, ["id", "name"]))                         # Expected: {'id': 1, 'name': 'A'}
print(pick(u, ["name", "ghost", "age"]))               # Expected: {'name': 'A', 'age': None}  (None kept, 'ghost' skipped)
print(pick(u, ["name", "id"]))                         # Expected: {'name': 'A', 'id': 1}  (follows the order of keys)
print(pick({}, ["a"]))                                 # Expected: {}
```

---

## 🔍 Why This Works (3 lines max)
Looping over `keys` makes the cost O(len(keys)) instead of O(len(d)), and `k in d` guards against `KeyError`. Values like `None` or `0` are kept because we test key presence, not truthiness.
हिंदी: `k in d` से missing key skip होती है, और None/0 जैसी values भी रखी जाती हैं।

---

## ⚡ Alternative Solution
```python
# operator.itemgetter returns a tuple of values (raises KeyError if missing)
from operator import itemgetter                        # fast C-level getter

u = {"id": 1, "name": "A", "email": "a@x.com"}         # sample
print(itemgetter("id", "name")(u))                     # Expected: (1, 'A')
# Set-intersection version (order NOT guaranteed, set order varies):
print({k: u[k] for k in u.keys() & {"id", "email"}} == {"id": 1, "email": "a@x.com"})  # Expected: True
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: indexing without checking — missing key raises KeyError
u = {"id": 1, "name": "A"}                             # sample
try:
    {k: u[k] for k in ["id", "ghost"]}                 # 'ghost' is not in u
except KeyError as e:
    print("KeyError", e)                               # Output: KeyError 'ghost'
# ✅ Correct: add `if k in u` to the comprehension (or decide explicitly to raise)
```

---

## 🎯 Interview Tip (1 line)
Say: "I iterate over the wanted keys and test `in`, so it's O(k) and None/0 values survive" — and ask whether missing keys should be skipped or raise.

---

## 🔗 Related Questions
→ Q075 (omit keys) | Q074 (dotted path) | Q223 (Pydantic validation) | Q233 (response models)
