---

# Q012. Dict Keys 1, 1.0, True Collision Output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What will the following code print?

```python
d = {}
d[1] = "int"
d[1.0] = "float"
d[True] = "bool"
print(d, len(d))

d2 = {0: "a", False: "b", 0.0: "c"}
print(d2)
```

---

## 💡 Quick Concept (2 lines only)
Dict keys are matched by hash AND equality. `1 == 1.0 == True` and they share a hash, so they are the SAME key: first key object is kept, last value wins.
हिंदी: `1`, `1.0` और `True` की hash और equality एक जैसी है, इसलिए dict में तीनों एक ही key हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
# Step 1: show the hash/equality facts that cause the collision
print(hash(1) == hash(1.0) == hash(True))   # Expected: True  (equal hashes)
print(1 == 1.0 == True)                     # Expected: True  (equal values)

# Step 2: inserting "different" keys that are really the same key
d = {}                                  # empty dict
d[1] = "int"                            # creates key 1 (the int object)
d[1.0] = "float"                        # equal key exists -> only the VALUE is replaced
d[True] = "bool"                        # same again; the stored key object stays 1
print(d, len(d))                        # Expected: {1: 'bool'} 1

# Step 3: same rule in a dict literal (0 == False == 0.0)
d2 = {0: "a", False: "b", 0.0: "c"}     # first key object 0 kept, last value kept
print(d2)                               # Expected: {0: 'c'}
```

---

## 🔍 Why This Works (3 lines max)
Lookup compares hashes first, then `==`. `True` is a subclass of `int`, and `hash(1.0) == hash(1)`, so all three hit the same slot. On a collision of equal keys, Python keeps the ORIGINAL key object but overwrites the value.
हिंदी: पहली key का object रहता है, value आखिरी वाली हो जाती है।

---

## ⚡ Alternative Solution
```python
# Order of insertion decides which key object survives
d = {True: "x", 1: "y"}                 # True inserted first
print(d)                                # Expected: {True: 'y'}  (key stays True, value is 'y')

# Keep them apart by making the keys distinct, e.g. include the type
d = {(type(k), k): v for k, v in [(1, "int"), (1.0, "float"), (True, "bool")]}
print(len(d))                           # Expected: 3
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using booleans / numeric flags as keys alongside ints
# counts = {1: "one", True: "yes"}    # silently merges into one entry

# ✅ Correct: use distinct key types (strings/enums) or tuples including the type
# counts = {"one": 1, "yes": True}
```

---

## 🎯 Interview Tip (1 line)
Say: "Keys are identified by hash plus equality; `1`, `1.0` and `True` are equal with equal hashes, so they collide into one entry."

---

## 🔗 Related Questions
→ Q014 (bool is int) | Q034 (__eq__ without __hash__) | Q175 (mutability and hashability) | Q011 (dict ordering)
