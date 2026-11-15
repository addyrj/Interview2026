---

# Q011. Dict Ordering and update Output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```python
d = {"b": 1, "a": 2}
d["c"] = 3
d["b"] = 10
print(d)

del d["a"]
d["a"] = 0
print(d)

print({"x": 1, "y": 2} == {"y": 2, "x": 1})
print(list({"x": 1, "y": 2}) == list({"y": 2, "x": 1}))
```

---

## 💡 Quick Concept (2 lines only)
Since Python 3.7 dicts keep INSERTION order. Updating an existing key keeps its position; deleting and re-adding moves it to the end. `==` ignores order.
हिंदी: Dict insertion order याद रखता है; पुरानी key update करने पर जगह नहीं बदलती, delete करके जोड़ने पर आखिर में जाती है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
# Step 1: new keys append; updating an existing key keeps its slot
d = {"b": 1, "a": 2}                    # order: b, a
d["c"] = 3                              # new key goes to the end
d["b"] = 10                             # existing key: value changes, position stays first
print(d)                                # Expected: {'b': 10, 'a': 2, 'c': 3}

# Step 2: delete + re-insert moves the key to the end
del d["a"]                              # remove 'a'
d["a"] = 0                              # insert again -> treated as a new key
print(d)                                # Expected: {'b': 10, 'c': 3, 'a': 0}

# Step 3: dict equality ignores order, list of keys does not
print({"x": 1, "y": 2} == {"y": 2, "x": 1})                      # Expected: True
print(list({"x": 1, "y": 2}) == list({"y": 2, "x": 1}))          # Expected: False
```

---

## 🔍 Why This Works (3 lines max)
Dicts store entries in an array in insertion order; a key's slot is created when it is first inserted. Overwriting changes only the value, while delete-then-insert creates a new slot at the end. Dict `==` compares key/value pairs, not order (use `OrderedDict` for order-sensitive equality).
हिंदी: `==` order नहीं देखता, लेकिन `list(d)` में order दिखता है।

---

## ⚡ Alternative Solution
```python
# update(), | and popitem() with ordering
d = {"a": 1}                            # start
d.update({"b": 2, "a": 5})              # 'a' updated in place, 'b' appended
print(d)                                # Expected: {'a': 5, 'b': 2}

print({"a": 1} | {"b": 2, "a": 9})      # Expected: {'a': 9, 'b': 2}  (3.9+ merge, right side wins)
print(d.popitem(), d)                   # Expected: ('b', 2) {'a': 5}   (popitem removes the LAST inserted)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: relying on dict order in Python < 3.7 or on sets (sets are NOT ordered)
# ❌ Wrong: thinking d["b"] = 10 moves 'b' to the end

# ✅ Correct: use collections.OrderedDict.move_to_end("b") when you need to reorder explicitly
```

---

## 🎯 Interview Tip (1 line)
Say: "Dicts preserve insertion order (guaranteed since 3.7); overwriting keeps position, re-inserting moves to the end, and `==` ignores order."

---

## 🔗 Related Questions
→ Q012 (dict keys 1, 1.0, True) | Q013 (set operations) | Q252 (collections) | Q099 (implement LRU cache)
