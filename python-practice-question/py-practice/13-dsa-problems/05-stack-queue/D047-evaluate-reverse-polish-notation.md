---

# D047. Evaluate Reverse Polish Notation
# Category: DSA — Stack & Queue
# Difficulty: ⭐⭐ Medium | LeetCode #150 | Asked: Amazon, LinkedIn, Google

---

## ❓ Problem
Evaluate an arithmetic expression in Reverse Polish Notation. Valid operators are `+ - * /`. Division truncates toward zero.

```
Input:  ["2", "1", "+", "3", "*"]   Output: 9    ((2 + 1) * 3)
Input:  ["4", "13", "5", "/", "+"]  Output: 6    (4 + (13 / 5))
```

---

## 💡 Quick Concept (2 lines only)
Push numbers on a stack; on an operator pop two operands (right first, then left), apply it, push the result. The last item is the answer.
हिंदी: संख्या stack में डालो, operator आए तो दो संख्या निकालो, गणना करके result वापस push करो।

---

## ✅ Solution

```python
import operator                                 # function versions of + - *


# ============================================
# APPROACH 1: Brute force — repeatedly find the first operator and collapse
# O(n^2) time, O(n) space
# ============================================
def eval_rpn_brute(tokens: list[str]) -> int:
    ops = {"+", "-", "*", "/"}                  # operator set
    toks = tokens[:]                            # copy, don't mutate input
    while len(toks) > 1:                        # until one value remains
        i = next(k for k, t in enumerate(toks) if t in ops)  # first operator position
        a, b = int(toks[i - 2]), int(toks[i - 1])  # its two operands
        if toks[i] == "+": r = a + b            # add
        elif toks[i] == "-": r = a - b          # subtract
        elif toks[i] == "*": r = a * b          # multiply
        else: r = int(a / b)                    # divide, truncate toward zero
        toks[i - 2:i + 1] = [str(r)]            # replace 3 tokens with the result
    return int(toks[0])                         # final value


# ============================================
# APPROACH 2: Stack — O(n) time, O(n) space ✅ PREFERRED
# ============================================
def eval_rpn(tokens: list[str]) -> int:
    stack: list[int] = []                       # operand stack
    ops = {                                     # operator -> function
        "+": operator.add,                      # a + b
        "-": operator.sub,                      # a - b
        "*": operator.mul,                      # a * b
        "/": lambda a, b: int(a / b),           # truncate toward zero (// would floor)
    }
    for tok in tokens:                          # left to right
        if tok in ops:                          # operator
            b = stack.pop()                     # right operand comes off first
            a = stack.pop()                     # then the left operand
            stack.append(ops[tok](a, b))        # push result
        else:
            stack.append(int(tok))              # number (handles "-11" too)
    return stack[0]                             # single value left


# ============================================
# TEST CASES
# ============================================
print(eval_rpn_brute(["2", "1", "+", "3", "*"]))                  # 9
print(eval_rpn(["2", "1", "+", "3", "*"]))                        # 9
print(eval_rpn(["4", "13", "5", "/", "+"]))                       # 6
print(eval_rpn(["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]))  # 22
print(eval_rpn(["7", "-2", "/"]))                                 # -3
print(eval_rpn(["5"]))                                            # 5
```

---

## 🔍 Why It Works
```
["4","13","5","/","+"]
push 4, 13, 5        stack [4, 13, 5]
"/" : b=5, a=13 -> int(13/5)=2   stack [4, 2]
"+" : b=2, a=4  -> 6             stack [6]
```
हिंदी: Operator हमेशा सबसे हाल की दो संख्याओं पर काम करता है, जो stack के top पर होती हैं।

---

## 📊 Complexity
```
Brute force: Time O(n^2) | Space O(n)
Stack:       Time O(n)   | Space O(n) ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Infix -> RPN using the shunting-yard algorithm (operator stack + precedence)
# VARIANT 2: Basic Calculator (LeetCode #224/#227) — stack with precedence handling
# VARIANT 3: Support unary minus or exponent "^" — add entries to the ops dict
print(7 // -2, int(7 / -2))                     # -4 -3   (floor vs truncate)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using // for division — floors toward -infinity, not toward zero
print(7 // -2)                                  # -4  (expected -3)

# ❌ Wrong: operand order a = pop(); b = pop() -> "3 2 -" would compute 2 - 3 = -1
# ✅ Correct: b = stack.pop() first, then a = stack.pop(); apply a OP b; use int(a / b)
```

---

## 🎯 Interview Tip
Say: "A stack evaluates RPN in one pass. I pop the right operand first, and use `int(a / b)` since Python's `//` floors rather than truncating toward zero." That detail is what interviewers watch for.

---

## 🔗 Related Problems
→ D042 (Valid Parentheses) | D049 (Decode String) | D043 (Min Stack)
