---

# Q002. Late Binding Closure in Loop Output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```python
funcs = []
for i in range(3):
    funcs.append(lambda: i)

print([f() for f in funcs])
i = 10
print([f() for f in funcs])
```

---

## 💡 Quick Concept (2 lines only)
A closure captures the VARIABLE, not its value; the variable is looked up when the function is CALLED. After the loop, `i` is whatever it last was.
हिंदी: Lambda value नहीं, variable `i` याद रखता है — call के समय जो value होगी वही मिलेगी।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
# Step 1: every lambda refers to the same module-level name `i`
funcs = []                              # holds the three lambdas
for i in range(3):                      # i takes 0, 1, 2 (and stays 2 after the loop)
    funcs.append(lambda: i)             # lambda does NOT copy i; it reads i when called

# Step 2: calls happen after the loop, when i == 2
print([f() for f in funcs])             # Expected: [2, 2, 2]

# Step 3: rebinding i changes what every lambda sees
i = 10                                  # change the shared variable
print([f() for f in funcs])             # Expected: [10, 10, 10]
```

---

## 🔍 Why This Works (3 lines max)
Python resolves `i` at call time through the enclosing scope (here the module globals), not at lambda-creation time. The loop leaves `i == 2`, so all three return 2; reassigning `i = 10` changes all of them at once.
हिंदी: Name की lookup call के समय होती है, बनाते समय नहीं — इसलिए सब एक जैसा देते हैं।

---

## ⚡ Alternative Solution
```python
# Fix 1: bind the current value as a default argument (defaults are evaluated at creation)
funcs = [lambda i=i: i for i in range(3)]   # i=i freezes each loop value into the lambda
print([f() for f in funcs])                 # Expected: [0, 1, 2]

# Fix 2: functools.partial stores the value explicitly
from functools import partial               # partial pre-fills arguments
funcs = [partial(lambda x: x, i) for i in range(3)]  # x is bound to the current i
print([f() for f in funcs])                 # Expected: [0, 1, 2]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: assuming a list comprehension fixes it
funcs = [lambda: i for i in range(3)]       # lambdas still share ONE i (the comprehension's)
print([f() for f in funcs])                 # Expected: [2, 2, 2]  (still wrong!)

# ✅ Correct: freeze the value with a default argument or partial
funcs = [lambda i=i: i for i in range(3)]   # each lambda gets its own copy of i
```

---

## 🎯 Interview Tip (1 line)
Say: "Closures capture variables, not values (late binding); I freeze the value with a default argument or `functools.partial`."

---

## 🔗 Related Questions
→ Q001 (mutable default) | Q122 (fix late binding bug) | Q161 (closures explained) | Q040 (global vs nonlocal)
