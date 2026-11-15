---

# Q008. Tuple with Mutable Element and += Output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What will the following code print? Does the tuple change even though an error is raised?

```python
t = (1, [2, 3])
try:
    t[1] += [4]
except TypeError as e:
    print("TypeError:", e)
print(t)
```

---

## 💡 Quick Concept (2 lines only)
`t[1] += x` does two steps: `list.__iadd__` mutates the list in place (succeeds), then assigns the result back into the tuple slot (fails). Both happen.
हिंदी: List में बदलाव हो जाता है, फिर tuple में दोबारा assign करने पर error आता है — दोनों होते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
# Step 1: tuple is immutable, but the list inside it is a normal mutable list
t = (1, [2, 3])                         # tuple holding an int and a list

# Step 2: t[1] += [4] is roughly: tmp = t[1]; tmp = tmp.__iadd__([4]); t[1] = tmp
try:
    t[1] += [4]                         # __iadd__ extends the list in place, THEN t[1] = ... raises
except TypeError as e:                  # tuple has no item assignment
    print("TypeError:", e)              # Expected: TypeError: 'tuple' object does not support item assignment

# Step 3: the in-place extend already happened before the error
print(t)                                # Expected: (1, [2, 3, 4])
```

---

## 🔍 Why This Works (3 lines max)
Augmented assignment on a subscript loads the item, calls `__iadd__` (which mutates the list and returns it), then stores it back via `__setitem__`. The tuple rejects the store, but the list was already extended, so you get both an error and a changed value.
हिंदी: Error के बावजूद list बदल चुकी होती है — यही इस सवाल की trick है।

---

## ⚡ Alternative Solution
```python
# Avoid the error entirely: mutate the inner list without re-assigning to the tuple
t = (1, [2, 3])                         # fresh tuple
t[1].append(4)                          # in-place mutation, no store into the tuple -> no error
print(t)                                # Expected: (1, [2, 3, 4])

t[1].extend([5])                        # extend() is equivalent and also error-free
print(t)                                # Expected: (1, [2, 3, 4, 5])
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: believing "it raised, so nothing changed" (or "tuples can never change")
# t[1] += [4]  -> TypeError, yet t is now (1, [2, 3, 4])

# ✅ Correct: use t[1].extend([4]) (or .append) when you only want to mutate the inner list
```

---

## 🎯 Interview Tip (1 line)
Say: "Tuples are immutable containers of references; a mutable element can still change, and `+=` on a subscript mutates first and fails on the rebind."

---

## 🔗 Related Questions
→ Q009 (+= vs + on lists) | Q175 (mutability and hashability) | Q291 (list vs tuple) | Q292 (mutable vs immutable)
