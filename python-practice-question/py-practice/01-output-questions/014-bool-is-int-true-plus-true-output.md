---

# Q014. bool is int (True + True) Output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐ Easy

---

## ❓ Question
What will the following code print?

```python
print(True + True, True * 10, sum([True, False, True]))
print(isinstance(True, int), [10, 20][True])
print(type(True + 1), type(True & False), type(True & 1))
```

---

## 💡 Quick Concept (2 lines only)
`bool` is a subclass of `int`: `True == 1` and `False == 0`, so arithmetic works. Bitwise ops between two bools stay `bool`; mixing with an int gives `int`.
हिंदी: Python में `True` असल में 1 है और `False` 0, इसलिए इनसे जोड़-घटाव हो जाता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
# Step 1: arithmetic treats True as 1
print(True + True, True * 10, sum([True, False, True]))   # Expected: 2 10 2
# sum() of booleans counts the Trues -> handy for counting matches

# Step 2: bool is a real subclass of int
print(isinstance(True, int), [10, 20][True])              # Expected: True 20
# True works as list index 1 because it IS the int 1

# Step 3: result types
print(type(True + 1), type(True & False), type(True & 1)) # Expected: <class 'int'> <class 'bool'> <class 'int'>
# + promotes to int; & between two bools returns bool; bool & int returns int
```

---

## 🔍 Why This Works (3 lines max)
`class bool(int)` — its MRO is `(bool, int, object)`, so it inherits all int arithmetic. `bool` only overrides `&`, `|`, `^` (and repr) to keep results as bool when both operands are bool. This is also why `1`, `1.0` and `True` collide as dict keys.
हिंदी: `bool`, `int` की subclass है — इसलिए int के सारे operations काम करते हैं।

---

## ⚡ Alternative Solution
```python
# Practical uses and the MRO proof
print(issubclass(bool, int), bool.__mro__)   # Expected: True (<class 'bool'>, <class 'int'>, <class 'object'>)

nums = [3, 8, 1, 9]                     # sample data
print(sum(n > 2 for n in nums))         # Expected: 3  (count of items greater than 2)
print(int(True), -True, True / 2)       # Expected: 1 -1 0.5
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: treating True/1 as different in sums, indexes, or dict keys
# {1: "a", True: "b"}      # one key only
# isinstance(x, int) accepts True: a function validating "int" input also accepts bools

# ✅ Correct: exclude bools explicitly when needed
# isinstance(x, int) and not isinstance(x, bool)
```

---

## 🎯 Interview Tip (1 line)
Say: "`bool` subclasses `int`, so `True + True == 2` and `isinstance(True, int)` is True — I exclude bools explicitly when validating ints."

---

## 🔗 Related Questions
→ Q012 (dict keys 1, 1.0, True) | Q017 (truthy/falsy values) | Q016 (short-circuit and/or) | Q019 (float precision)
