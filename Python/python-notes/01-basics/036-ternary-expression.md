---

# 036. Ternary Expression
# हिंदी में: Ternary Expression — एक line का if/else

---

## 🔵 Simple Definition (English)
A ternary (conditional) expression picks one of two values in a single line: `value_if_true if condition else value_if_false`. It is an expression, so it produces a value and can be used inside assignments, returns and f-strings.

## 🔵 सरल परिभाषा (Hindi)
Ternary expression एक line में दो values में से एक चुनता है: `value_if_true if condition else value_if_false`। यह expression है, यानी value देता है — assignment, return और f-string में use हो सकता है।

---

## 🔴 Problem it Solves
Choosing between two values with a normal `if/else` takes four lines and a temporary variable. Ternary does it in one readable line, perfect for small decisions like labels, defaults and status text.

## 🔴 यह क्यों बना? (Hindi)
दो values में से एक चुनने के लिए सामान्य `if/else` में चार lines लगती हैं। Ternary एक ही line में यह काम कर देता है — छोटे फैसलों (label, default, status) के लिए बढ़िया।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python evaluates the CONDITION in the middle first
Step 2 → If truthy  → evaluates and returns the LEFT value
Step 3 → If falsy   → evaluates and returns the RIGHT value
Step 4 → Only ONE of the two branches is ever evaluated (lazy)
Step 5 → The result can be assigned, returned or nested
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → बीच वाली condition पहले evaluate होती है
Step 2 → True हो तो बाएँ वाली value मिलती है
Step 3 → False हो तो दाएँ वाली (else) value मिलती है
Step 4 → दोनों में से सिर्फ एक branch चलती है
```

---

## 🟡 Real World Example
Swiggy: `fee = 0 if order_total >= 199 else 30` — free delivery above a threshold. Chatbot UI: `role = "assistant" if is_bot else "user"`. FastAPI: `status = "ok" if db_alive else "degraded"` in a health check.

## 🟡 Real Example Hindi mein
Swiggy में `fee = 0 if order_total >= 199 else 30` — 199 से ऊपर free delivery। Health check में `"ok" if db_alive else "degraded"`।

---

## 💻 Code Example — Basic
```python
# Ternary expression basics
age: int = 20                                        # a number
status: str = "adult" if age >= 18 else "minor"      # pick one of two strings
print(status)                                        # adult

order_total: int = 150                               # cart value
fee: int = 0 if order_total >= 199 else 30           # delivery fee rule
print(fee)                                           # 30

n: int = 7                                           # another number
print("even" if n % 2 == 0 else "odd")               # odd  (used directly inside print)

name: str = ""                                       # empty name
display: str = name if name else "Guest"             # fallback when empty
print(display)                                       # Guest

items: list[int] = [1, 2, 3]                         # a list
print(f"{len(items)} item{'s' if len(items) != 1 else ''}")   # 3 items

def sign(x: int) -> str:                             # nested ternary
    return "positive" if x > 0 else "negative" if x < 0 else "zero"   # chain

print(sign(5), sign(-2), sign(0))                    # positive negative zero
```
Output:
```
adult
30
odd
Guest
3 items
positive negative zero
```

## 💻 Code Example — Advanced
```python
# Lazy evaluation, tuple trick trap, and when to avoid ternary
from typing import Optional                          # type hint


def expensive(tag: str) -> int:                      # function with a visible side effect
    print(f"computing {tag}")                        # shows when it runs
    return 42                                        # dummy result


flag: bool = True                                    # condition
result: int = expensive("A") if flag else expensive("B")   # only A runs
print(result)                                        # 42

# `and/or` trick is NOT the same as ternary:
value: int = 0                                       # falsy value
wrong = flag and value or 99                         # old trick: 0 is falsy -> gives 99
right = value if flag else 99                        # ternary: gives 0
print(wrong, right)                                  # 99 0

# Tuple indexing evaluates BOTH sides (not lazy):
calls: list[str] = []                                # track calls


def left() -> str:                                   # left option
    calls.append("left")                             # record call
    return "L"                                       # value


def right_() -> str:                                 # right option
    calls.append("right")                            # record call
    return "R"                                       # value


pick: str = (right_(), left())[flag]                 # old tuple trick: calls both
print(pick, calls)                                   # L ['right', 'left']

# Practical: Optional handling
def username(user: Optional[dict[str, str]]) -> str:         # may receive None
    return user["name"] if user is not None else "anonymous"  # safe access


print(username({"name": "Riya"}), username(None))    # Riya anonymous

# Ternary inside comprehension:
scores: list[int] = [35, 80, 49, 91]                 # marks
grades: list[str] = ["pass" if s >= 40 else "fail" for s in scores]   # per item
print(grades)                                        # ['fail', 'pass', 'pass', 'pass']

# Conditional function call:
mode: str = "upper"                                  # choose a function
fn = str.upper if mode == "upper" else str.lower     # pick a function object
print(fn("Hello"))                                   # HELLO
```
Output:
```
computing A
42
99 0
L ['right', 'left']
Riya anonymous
['fail', 'pass', 'pass', 'pass']
HELLO
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: value_if_true if condition else value_if_false
age = 20                                   # number
label = "adult" if age >= 18 else "minor"  # condition in the MIDDLE
print(label)                               # adult
```
```javascript
// JavaScript: condition ? value_if_true : value_if_false
const age = 20;                            // number
const label = age >= 18 ? "adult" : "minor";   // condition FIRST
console.log(label);                        // adult
```
Key difference: the order. JS puts the condition first (`c ? a : b`); Python puts the true-value first and the condition in the middle (`a if c else b`). Python has no `?:` operator.

---

## 🟠 FastAPI Connection
Ternaries are common for response fields, defaults and health checks.

```python
from fastapi import FastAPI                          # import FastAPI
from typing import Optional                          # type hint

app: FastAPI = FastAPI()                             # create app


@app.get("/greet")                                   # GET /greet
async def greet(name: Optional[str] = None) -> dict[str, str]:    # optional query param
    who: str = name if name else "stranger"          # fallback name
    return {"message": f"Hello {who}"}               # JSON response


@app.get("/health")                                  # GET /health
async def health(db_alive: bool = True) -> dict[str, str]:        # simulate DB state
    return {"status": "ok" if db_alive else "degraded"}           # ternary in response
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the `and/or` trick
```python
# Wrong — fails when the "true" value is falsy:
value = 0
result = True and value or 99     # 99 (surprise!)

# Correct:
result = value if True else 99    # 0
```

❌ Mistake 2: Deeply nested ternaries
```python
# Wrong — unreadable:
# grade = "A" if s > 90 else "B" if s > 80 else "C" if s > 70 else "D"

# Correct — use if/elif or a function:
def grade(s: int) -> str:
    if s > 90:
        return "A"
    if s > 80:
        return "B"
    return "C"
```

---

## 🧠 Tricky Interview Question

```python
x = 5
print("big" if x > 3 else "small" + "!")
print(("big" if x > 3 else "small") + "!")
```
Answer: First prints `big` (the `+ "!"` belongs only to the else branch). Second prints `big!`. Ternary has very low precedence, so use brackets when combining with other operators.

---

## ⚫ Interview Questions + Answers

Q1: Syntax of Python's ternary?
A1: `a if condition else b`. Condition is evaluated first, then only the chosen branch.

Q2: Is it lazy?
A2: Yes. Only the selected branch is evaluated, so `x if safe else 1/0` never divides when `safe` is True.

Q3: Why not use `condition and a or b`?
A3: It fails when `a` is falsy (0, "", [], None) — it returns `b`. The real ternary has no such bug.

Q4: Can ternaries be nested?
A4: Yes, right-associative: `a if c1 else b if c2 else c`. Keep to one level; beyond that use if/elif.

Q5: Can you use ternary on the left side of assignment?
A5: No directly (`x if c else y = 5` is invalid). Use `(a if c else b).attr = 5` for attribute targets or plain if/else.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Simple two-way value choice
- Inside f-strings, returns, comprehensions
- Defaulting None to a value

❌ Avoid when:
- Branches need multiple statements
- Nesting more than one level
- Branches have side effects that hide intent

---

## 📊 Visual Diagram
```
   "adult" if age >= 18 else "minor"
      │         │              │
      │         ▼              │
      │    condition? ─ True ──┘ (no)
      │         │ False
      ▼         ▼
   left      right
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Ternary | 3-part conditional expression | तीन हिस्सों वाला conditional |
| Expression | Code that gives a value | Value देने वाला code |
| Lazy evaluation | Run only what is needed | ज़रूरत भर का ही चलाना |
| Truthy / Falsy | Treated as True / False | True / False जैसा माना जाना |
| Fallback | Default value | Default value |
| Nested | One inside another | एक के अंदर दूसरा |

---

## ⚡ 3-Line Summary
English: Ternary is `a if cond else b`, an expression that returns one of two values. It is lazy and low-precedence, so use brackets when mixing. Keep it simple; nested ternaries hurt readability.
Hindi: Ternary = `a if cond else b`, जो दो में से एक value देता है। यह lazy है और precedence कम है, इसलिए brackets लगाएँ। Nested ternary से बचें।

---

## ➡️ Next Topic
**037. match/case (Python 3.10+)** — structural pattern matching, Python's powerful switch statement.
