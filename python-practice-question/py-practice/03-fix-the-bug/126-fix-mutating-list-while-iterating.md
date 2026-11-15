---

# Q126. Fix mutating list while iterating
# Category: FIX THE BUG
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Remove all even numbers from the list. The code runs without error but some evens stay. Fix it.

```python
nums = [1, 2, 2, 3, 4, 4, 5, 6]
for n in nums:
    if n % 2 == 0:
        nums.remove(n)       # BUG
print(nums)                  # expected [1, 3, 5]
```

---

## 💡 Quick Concept (2 lines only)
A list iterator walks by index; removing an item shifts the rest left, so the next item is skipped. Iterate over a copy or build a new list.
हिंदी: List iterator index से चलता है; item हटाने पर अगला element छूट जाता है — copy पर loop करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
nums = [1, 2, 2, 3, 4, 4, 5, 6]            # input

# Symptom (buggy):
buggy = nums.copy()                         # work on a copy to keep nums intact
for n in buggy:                             # iterator index moves 0,1,2,...
    if n % 2 == 0:                          # even?
        buggy.remove(n)                     # shifts items left -> next one skipped
print(buggy)                                # Output: [1, 2, 3, 4, 5]   <- BUG: 2 and 4 survive

# Trace on [1, 2, 2, 3]: i=0 n=1 | i=1 n=2 -> remove -> list [1,2,3] | i=2 n=3 (the second 2 was skipped!)

# Fix: list comprehension builds a NEW list (clear and fast)
evens_removed = [n for n in nums if n % 2]  # keep odd numbers only

# ============================================
# TEST CASES
# ============================================
print(evens_removed)                        # Expected: [1, 3, 5]
inplace = nums.copy()                       # need to mutate the SAME list object?
inplace[:] = [n for n in inplace if n % 2 != 0]   # slice assignment keeps identity
print(inplace)                              # Expected: [1, 3, 5]
print(nums)                                 # Expected: [1, 2, 2, 3, 4, 4, 5, 6]  (original untouched)
```

---

## 🔍 Why This Works (3 lines max)
The comprehension never touches the list being read, so no index shifting happens. Slice assignment `lst[:] = ...` is the way to filter "in place" while keeping other references valid.
हिंदी: नई list बनाओ (comprehension) — पुरानी list को loop के दौरान बदलो मत।

---

## ⚡ Alternative Solution
```python
# 1) Iterate over a shallow copy
f2 = nums.copy()
for n in f2[:]:                              # copy of the list is iterated
    if n % 2 == 0: f2.remove(n)              # removes from the real list (O(n) each)
print(f2)                                    # Output: [1, 3, 5]

# 2) Iterate backwards by index and delete
f3 = nums.copy()
for i in range(len(f3) - 1, -1, -1):         # indexes shift only AFTER i
    if f3[i] % 2 == 0: del f3[i]
print(f3)                                    # Output: [1, 3, 5]

# 3) filter()
print(list(filter(lambda n: n % 2, nums)))   # Output: [1, 3, 5]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: ADDING while iterating can loop forever / grow unexpectedly (no error raised for lists!)
ys = [1, 2, 3]
for x in ys:
    ys.append(x)                 # iterator keeps finding new items
    if len(ys) > 8: break        # safety break so this demo ends
print(ys)                        # Output: [1, 2, 3, 1, 2, 3, 1, 2, 3]

# Dicts and sets DO raise instead of silently misbehaving:
d = {"a": 1}
try:
    for k in d: d[k + "x"] = 0
except RuntimeError as e: print("RuntimeError:", e)   # Output: RuntimeError: dictionary changed size during iteration
# ✅ Correct: iterate over list(d) / a copy, or build a new collection
```

---

## 🎯 Interview Tip (1 line)
Say: "Never mutate a collection while iterating it — build a new one with a comprehension, iterate a copy, or go in reverse; lists skip silently, dicts raise RuntimeError."

---

## 🔗 Related Questions
→ Q127 (dict changed size during iteration) | Q068 (remove falsy values) | Q241 (comprehensions) | Q025 (generator exhaustion)
