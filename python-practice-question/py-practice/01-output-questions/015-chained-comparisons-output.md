---

# Q015. Chained comparisons output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```python
x = 5
print(1 < x < 10)       # (a)
print(3 > 2 > 5)        # (b)
print(1 < 3 > 2)        # (c)
print((1 < 2) < 3)      # (d)

def f(n):
    print("f", n)       # side effect so we can see evaluation
    return n

print(f(0) < f(5) < f(3))  # (e) how many times is f called?
```

---

## 💡 Quick Concept (2 lines only)
`a < b < c` means `a < b and b < c`, but each middle operand is evaluated only once and evaluation stops at the first False.
हिंदी: Chained comparison = दो comparisons का `and`, बीच वाला value सिर्फ एक बार evaluate होता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
x = 5                          # Step 1: plain variable
print(1 < x < 10)              # Step 2: (1 < 5) and (5 < 10) -> True
print(3 > 2 > 5)               # Step 3: (3 > 2) and (2 > 5) -> True and False -> False
print(1 < 3 > 2)               # Step 4: (1 < 3) and (3 > 2) -> True (no need for ordering!)
print((1 < 2) < 3)             # Step 5: brackets break the chain: True < 3 -> 1 < 3 -> True

def f(n: int) -> int:          # Helper that logs each call
    print("f", n)              # Show when it is evaluated
    return n                   # Return the same value

print(f(0) < f(5) < f(3))      # Step 6: f(0), f(5) evaluated; 0<5 True; then f(3); 5<3 False

# ============================================
# TEST CASES
# ============================================
# Expected output (real run, Python 3.13):
# True
# False
# True
# True
# f 0
# f 5
# f 3
# False
```

---

## 🔍 Why This Works (3 lines max)
Python rewrites `a op1 b op2 c` as `a op1 b and b op2 c` with `b` evaluated once; it short-circuits when the first comparison is False. Brackets create a normal boolean-vs-int comparison (`True` is `1`).
हिंदी: Chain बीच में टूट जाए तो आगे के operands evaluate नहीं होते; brackets लगाते ही chain खत्म।

---

## ⚡ Alternative Solution
```python
# Chains work with ANY comparison operators, even mixed ones
print(1 == 1 in [1])                 # (1 == 1) and (1 in [1]) -> True
print((1 == 1) in [1])               # brackets: True in [1] -> True (since True == 1)
print(1 < 2 >= 2)                    # (1 < 2) and (2 >= 2) -> True
print(5 > 3 > 1)                     # Descending chain -> True

# Explicit equivalent (only differs in how many times the middle is evaluated)
a, b, c = 1, 5, 10                   # Sample values
print(a < b and b < c)               # Same result as a < b < c -> True
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: assuming a chain is evaluated left to right like (a < b) < c
# print(1 < f(5) < 3)  # thinking: True < 3 -> True
# ✅ Correct: (1 < 5) and (5 < 3) -> False (and f(5) is called only ONCE)
def f(n):
    print("f", n)         # Log the call
    return n              # Return n
print(1 < f(5) < 3)       # Prints "f 5" once, then False
```

---

## 🎯 Interview Tip (1 line)
Say: "Chained comparisons are `and` under the hood, the middle operand is evaluated once, and they short-circuit — so `1 == 1 in [1]` is not `(1 == 1) in [1]`."

---

## 🔗 Related Questions
→ Q014 (bool is int) | Q016 (short-circuit and/or) | Q012 (dict key collision)
