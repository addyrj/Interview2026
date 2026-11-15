---

# Q004. Small Integer Caching (-5 to 256) Output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```python
a = int("256")
b = int("256")
print(a is b)

c = int("257")
d = int("257")
print(c is d, c == d)

print(int("-5") is int("-5"))
print(int("-6") is int("-6"))
```

---

## 💡 Quick Concept (2 lines only)
CPython pre-creates and reuses the int objects from -5 to 256, so equal small ints are the SAME object; larger ints are normally new objects each time.
हिंदी: CPython -5 से 256 तक के int पहले से बनाकर रखता है, इसलिए वे एक ही object होते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
# Step 1: int("256") is computed at runtime; 256 is inside the cached range
a = int("256")                          # returns the cached 256 object
b = int("256")                          # returns the SAME cached object
print(a is b)                           # Expected: True

# Step 2: 257 is outside the cache, so each call builds a new int
c = int("257")                          # new int object
d = int("257")                          # another new int object
print(c is d, c == d)                   # Expected: False True  (different objects, equal values)

# Step 3: the lower boundary is -5
print(int("-5") is int("-5"))           # Expected: True   (-5 is cached)
print(int("-6") is int("-6"))           # Expected: False  (-6 is not cached)
```

---

## 🔍 Why This Works (3 lines max)
CPython keeps a static array of small-int objects for -5..256 and returns them instead of allocating. Using `int("...")` forces runtime creation; with literals in one file the compiler may merge equal constants, making `257 is 257` True in a script but False in some REPL lines — an implementation detail.
हिंदी: यह सिर्फ CPython की optimisation है — इस पर कभी भरोसा मत करो, `==` use करो।

---

## ⚡ Alternative Solution
```python
# Same idea shown with id(); results are CPython-specific
x = int("100")                          # small int -> cached
print(id(x) == id(int("100")))          # Expected: True

y = int("1000")                         # big int -> fresh object
print(id(y) == id(int("1000")))         # Expected: False  (compares ids of two live objects)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using `is` to compare numbers because it "worked" for small values
# if count is 100: ...     # works by accident, breaks for 1000 (and gives SyntaxWarning)

# ✅ Correct: use == for value comparison
# if count == 100: ...
```

---

## 🎯 Interview Tip (1 line)
Say: "Small-int caching (-5..256) is a CPython implementation detail; `is` tests identity, so I always use `==` for numbers."

---

## 🔗 Related Questions
→ Q003 (is vs ==) | Q007 (string interning) | Q174 (is, == and interning) | Q128 (fix is vs == bug)
