---

# Q001. Mutable Default Argument Output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```python
def add_item(item, bucket=[]):
    bucket.append(item)
    return bucket

print(add_item(1))
print(add_item(2))
print(add_item(3, []))
print(add_item(4))
```

---

## 💡 Quick Concept (2 lines only)
Default values are evaluated ONCE, when `def` runs — not on every call. A mutable default (list/dict/set) is therefore shared by all calls that don't pass their own.
हिंदी: Default argument सिर्फ एक बार बनता है, इसलिए list हर call में वही रहती है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
# Step 1: `def` executes -> the default [] is created once and stored on the function object
def add_item(item, bucket=[]):          # bucket's default list lives in add_item.__defaults__
    bucket.append(item)                 # mutates the SAME shared list when bucket is not passed
    return bucket                       # returns the shared list itself (not a copy)

# ============================================
# TEST CASES
# ============================================
print(add_item(1))                      # Expected: [1]         (shared list: [1])
print(add_item(2))                      # Expected: [1, 2]      (same shared list, now [1, 2])
print(add_item(3, []))                  # Expected: [3]         (caller passed a fresh list, shared one untouched)
print(add_item(4))                      # Expected: [1, 2, 4]   (shared list again, 3 never went in)
print(add_item.__defaults__)            # Expected: ([1, 2, 4],) (proof: default object was mutated)
```

---

## 🔍 Why This Works (3 lines max)
The default `[]` is created at function-definition time and kept in `__defaults__`. Every call without `bucket` reuses that exact object, so `append` keeps growing it. Passing your own list bypasses the default, which is why `3` never lands in the shared one.
हिंदी: def चलते ही default बन जाता है; बाद की हर call वही object use करती है।

---

## ⚡ Alternative Solution
```python
# Standard fix: use None as a sentinel and build a new list inside the function
def add_safe(item, bucket=None):        # None is immutable, so sharing it is harmless
    if bucket is None:                  # no list supplied by the caller
        bucket = []                     # create a NEW list on every call
    bucket.append(item)                 # mutate the local list only
    return bucket                       # return it

print(add_safe(1), add_safe(2))         # Expected: [1] [2]  (no leakage between calls)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: thinking each call gets a fresh [] -> expecting [1] then [2]
# def add_item(item, bucket=[]): ...     # actual output: [1] then [1, 2]

# ✅ Correct: default to None and create the list inside the body
# def add_item(item, bucket=None):
#     bucket = [] if bucket is None else bucket
```

---

## 🎯 Interview Tip (1 line)
Say: "Defaults are evaluated once at definition time, so I use `None` as a sentinel for mutable defaults" — and mention `dataclasses.field(default_factory=list)` for classes.

---

## 🔗 Related Questions
→ Q002 (late binding closure) | Q121 (fix mutable default bug) | Q138 (shared class variable bug) | Q029 (class attribute mutation)
