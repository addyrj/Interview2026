---

# Q179. Explain Comprehension Scoping
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Do comprehension variables leak into the surrounding scope? What happens in a class body, and what do the lambda-in-comprehension examples print?

---

## 💡 Quick Concept (2 lines only)
In Python 3, list/set/dict comprehensions and generator expressions have their own scope, so the loop variable does not leak (unlike a `for` loop). Class-body names are not visible inside them.
हिंदी: Comprehension का अपना scope होता है — loop variable बाहर नहीं आता; और class के variables comprehension के अंदर नहीं दिखते।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
x = "global"                                 # Step 1: outer x
res = [x for x in range(3)]                  # comprehension x is local to it
print(res, x)                                # Expected: [0, 1, 2] global

for i in range(3):                           # Step 2: a plain for loop DOES leak
    pass
print(i)                                     # Expected: 2

class K:                                     # Step 3: class-body scope rule
    base = 10                                # class variable
    try:
        vals = [base + n for n in range(2)]  # `base` is not visible inside the comprehension
    except NameError as e:
        print("NameError:", e)               # Expected: NameError: name 'base' is not defined
    vals2 = [n for n in range(base - 8)]     # outermost iterable IS evaluated in class scope
print(K.vals2)                               # Expected: [0, 1]

# ============================================
# TEST CASES
# ============================================
print("walrus:", end=" ")                    # walrus binds in the ENCLOSING scope
print([y := 7 for _ in range(1)], y)         # Expected: walrus: [7] 7
data = [1, 2, 3]
total = [t for t in data]                    # t stays inside
try:
    print(t)                                 # not defined here
except NameError as e:
    print("NameError:", e)                   # Expected: NameError: name 't' is not defined
```

---

## 🔍 Why This Works (3 lines max)
Comprehensions are compiled as their own function-like scope (inlined since 3.12 by PEP 709, with the same visible behaviour). Only the first `for` iterable is evaluated in the outer scope; the rest runs inside, so class variables are invisible there.
हिंदी: सिर्फ पहला iterable बाहर के scope में evaluate होता है, बाकी अंदर — इसलिए class variable नहीं मिलता।

---

## ⚡ Alternative Solution
```python
# Late binding inside comprehensions: lambdas see the variable's final value
funcs = [lambda: n for n in range(3)]        # all share one n
print([f() for f in funcs])                  # Expected: [2, 2, 2]

# Fix: bind via default argument
funcs = [lambda n=n: n for n in range(3)]    # n captured at definition time
print([f() for f in funcs])                  # Expected: [0, 1, 2]

# Generator expressions are lazy but scoped the same way
g = (z for z in range(2))                    # z does not leak
print(list(g))                               # Expected: [0, 1]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using a comprehension variable after the comprehension
data = [1, 2, 3]
total = [t for t in data]
print(t)                                     # NameError: name 't' is not defined

# ✅ Correct: use a loop if you need the last value, or compute it explicitly
last = data[-1]                              # explicit and clear
```

---

## 🎯 Interview Tip (1 line)
Say: "Comprehensions have their own scope (no leaking in Py3); class variables aren't visible inside them, and lambdas in them still late-bind."

---

## 🔗 Related Questions
→ Q024 (comprehension variable scope) | Q002 (late binding closure) | Q041 (LEGB scope) | Q244 (walrus operator)
