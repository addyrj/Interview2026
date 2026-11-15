---

# Q024. List comprehension variable scope output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What will the following code print?

```python
x = "outer"
r = [x for x in range(3)]                     # (a)
print(x, r)

for i in range(3):                            # (b)
    pass
print(i)

fs = [lambda: n for n in range(3)]            # (c)
print([f() for f in fs])

class C:
    xs = [1, 2, 3]
    ys = [x * 2 for x in xs]                  # (d)
    try:
        zs = [x * k for x in xs for k in xs]  # (e)
    except NameError as e:
        print("NameError:", e)
print(C.ys)
```

---

## 💡 Quick Concept (2 lines only)
Comprehensions have their own scope (Python 3), so the loop variable does not leak; a `for` loop does leak. Inside a class body, comprehensions cannot see class variables (except the first iterable).
हिंदी: Comprehension का variable बाहर leak नहीं होता, `for` loop का होता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
x = "outer"                                   # Step 1: outer variable
r = [x for x in range(3)]                     # Step 2: inner x lives only inside the comprehension
print(x, r)                                   # (a) outer [0, 1, 2]

for i in range(3):                            # Step 3: plain for loop shares the enclosing scope
    pass                                      # Do nothing
print(i)                                      # (b) 2 (i leaked)

fs = [lambda: n for n in range(3)]            # Step 4: lambdas capture the variable n, not its value
print([f() for f in fs])                      # (c) [2, 2, 2] (late binding)

class C:                                      # Step 5: class body scope
    xs = [1, 2, 3]                            # Class variable
    ys = [x * 2 for x in xs]                  # (d) OK: first iterable `xs` is evaluated in class scope
    try:
        zs = [x * k for x in xs for k in xs] # (e) inner `xs` is looked up inside comprehension scope
    except NameError as e:                    # NameError: name 'xs' is not defined
        print("NameError:", e)                # Printed during class creation
print(C.ys)                                   # [2, 4, 6]

# ============================================
# TEST CASES
# ============================================
# Expected output (real run, Python 3.13):
# outer [0, 1, 2]
# 2
# [2, 2, 2]
# NameError: name 'xs' is not defined
# [2, 4, 6]
```

---

## 🔍 Why This Works (3 lines max)
Since Python 3 a comprehension is its own function-like scope (3.12+ inlines it, but scoping rules are unchanged), so its variable stays private. Class scope is skipped by nested scopes, so only the outermost iterable is resolved in the class body.
हिंदी: Class body के variables nested scope को नहीं दिखते — यह भी एक famous gotcha है।

---

## ⚡ Alternative Solution
```python
fs = [lambda n=n: n for n in range(3)]        # Default arg freezes the value at creation
print([f() for f in fs])                      # [0, 1, 2]

print([(w := j) for j in range(3)], w)        # [0, 1, 2] 2 (walrus DOES bind in the enclosing scope)

class C:                                      # Fix for class scope: pass the data as an argument
    xs = [1, 2, 3]                            # Class variable
    zs = (lambda xs: [x * k for x in xs for k in xs])(xs)   # Lambda argument is a local
print(C.zs)                                   # [1, 2, 3, 2, 4, 6, 3, 6, 9]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: relying on the for-loop variable after the loop (and on comprehension leaking)
# for item in []: pass
# print(item)            # NameError: item never assigned (loop body never ran)

# ✅ Correct: initialise explicitly if you need it afterwards
item = None              # Safe default
for item in [1, 2]:      # Loop var leaks, last value stays
    pass
print(item)              # 2
```

---

## 🎯 Interview Tip (1 line)
Say: "Comprehensions have their own scope, for-loops do not, closures capture variables not values, and class scope is invisible to nested scopes."

---

## 🔗 Related Questions
→ Q002 (late binding closure) | Q041 (LEGB scope) | Q040 (global vs nonlocal)
