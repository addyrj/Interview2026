---

# 500. Output Questions + Tricky Code
# हिंदी में: Output Questions और Tricky Code (interview में output बताओ)

Full runnable solution: [main.py](main.py) (18 classic traps; each case asserts its real output).

---

## 🔵 Simple Definition (English)
Output questions show a short snippet and ask "what prints?". They test whether you know Python's real rules: scoping, mutability, identity, evaluation order.

## 🔵 सरल परिभाषा (Hindi)
Output questions में छोटा code दिखाकर पूछा जाता है "क्या print होगा?"। ये जाँचते हैं कि आप Python के असली नियम जानते हैं: scoping, mutability, identity, evaluation order।

---

## 🔴 Problem it Solves
Many bugs come from a handful of Python surprises (shared mutable defaults, late-binding closures, aliasing). Interviewers use them to separate memorised syntax from real understanding.

## 🔴 यह क्यों बना? (Hindi)
कई bugs Python के कुछ गिने-चुने आश्चर्यों से आते हैं (साझा mutable defaults, late-binding closures, aliasing)। Interviewer इनसे रटे हुए syntax और असली समझ में फ़र्क करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Read the code slowly; note every name binding and mutation
Step 2 → Ask: is the object mutable? Is it shared (alias) or copied?
Step 3 → Ask: when is each expression evaluated (def time vs call time)?
Step 4 → Trace scopes: local, enclosing, global, builtin (LEGB)
Step 5 → Write the output, then run it to verify
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → code धीरे पढ़ो; हर name binding और mutation नोट करो
Step 2 → पूछो: object mutable है? साझा (alias) है या copy?
Step 3 → पूछो: हर expression कब evaluate होता है (def time या call time)?
Step 4 → scopes trace करो: local, enclosing, global, builtin (LEGB)
Step 5 → output लिखो, फिर चलाकर जाँचो
```

---

## 🟡 Real World Example
A FastAPI handler with `def add(item, bucket=[])` leaks one user's items into the next request, a production bug caused by trap #1. A loop registering callbacks with `lambda: i` all use the last `i`. Knowing the traps prevents these incidents.

## 🟡 Real Example Hindi mein
FastAPI handler में `def add(item, bucket=[])` एक user के items अगली request में पहुँचा देता है; यह trap #1 से हुआ production bug है। Callbacks के loop में `lambda: i` सब आखिरी `i` इस्तेमाल करते हैं। इन traps को जानना ऐसे incidents रोकता है।

---

## 💻 Code Example — Basic
```python
# Mutable default argument trap
def f(x, acc=[]):  # the list is created ONCE at def time
    acc.append(x)  # mutates the shared list
    return acc  # returns that same list

f(1)  # acc = [1]
f(2)  # acc = [1, 2]
print(f(3))  # same list again
# Output:
# [1, 2, 3]
```

## 💻 Code Example — Advanced
```python
# Excerpts from main.py (all verified)
fs = [lambda: i for i in range(3)]         # late binding
print([f() for f in fs])                    # [2, 2, 2]
fs = [lambda i=i: i for i in range(3)]      # bind now via default arg
print([f() for f in fs])                    # [0, 1, 2]

g = [[0] * 2] * 2                           # two references to ONE inner list
g[0][0] = 9
print(g)                                    # [[9, 0], [9, 0]]

t = ([1], 2)
try:
    t[0] += [3]                             # list is extended, THEN tuple assignment fails
except TypeError:
    pass
print(t)                                    # ([1, 3], 2)
```
Real output of `python main.py` (Python 3.13.3):
```
q1 [1, 2, 3]
q2 [2, 2, 2]
q3 [0, 1, 2]
q4 (True, False)
q5 [[9, 0], [9, 0]]
q6 ([1, 3], 2)
q7 finally
q8 {1: 'c'}
q9 ([0, 1, 2], [])
q10 (True, False, False, True)
q11 ([1], 0, 0)
q12 []
q13 UnboundLocalError
q14 (['A', 'B', 'a', 'b'], ['A', 'a', 'b', 'B'])
q15 (0, 2, 2, False)
q16 NameError
q17 dictionary changed size during iteration
q18 ([[1, 9], [2]], [[1], [2]])
all ok
```
Notes: q4 `a is b` is False for runtime ints above 256 in CPython (implementation detail, never rely on it); q8 keeps key `1` but the last value, since `1 == True == 1.0` and hashes equal; q11 `a.k += 1` creates an instance attribute, leaving `A.k` at 0; q15 uses banker's rounding; q16 the `as e` name is deleted after the except block.

---

## 🟠 JavaScript vs Python Comparison
JS `var` closures in loops are the same late-binding trap; `let` fixes it per iteration. Python has no per-iteration scope, so bind via default argument or `functools.partial`.

```python
fs = [lambda i=i: i for i in range(3)]  # bind current i
```
```javascript
const fs = [0, 1, 2].map(i => () => i);  // let/const bind per iteration
```

---

## 🟠 FastAPI Connection
Mutable defaults in handlers or Pydantic-less classes leak state across requests. Never use `bucket: list = []`; use `None` or `Field(default_factory=list)`. Module-level lists are shared by all requests (and all async tasks) too.

```python
from fastapi import FastAPI  # framework

app = FastAPI()  # app

@app.post("/add")
def add(item: str, bucket: list[str] | None = None) -> list[str]:  # None sentinel
    bucket = [] if bucket is None else bucket  # fresh list per call
    bucket.append(item)  # safe to mutate
    return bucket  # no leakage between requests
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `is` to compare values.
✅ Correct: `==` for values; `is` only for `None`/singletons.

```python
# Wrong
if x is 1000: ...
# Right
if x == 1000: ...
```

❌ Mistake 2: `[[0]*n]*m` for grids.
✅ Correct: `[[0]*n for _ in range(m)]`.

❌ Mistake 3: Modifying a dict/list while iterating it.
✅ Correct: iterate over `list(d)` or build a new collection.

❌ Mistake 4: `return` inside `finally`, which silently swallows exceptions and overrides returns.
✅ Correct: keep `finally` for cleanup only.

---

## 🧠 Tricky Interview Question
```python
a = [1, 2, 3]
b = a
b += [4]
c = a
c = c + [5]
print(a, b, c)
```
Answer: `[1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 4, 5]`. `+=` on a list is in-place (`__iadd__`), so `a` and `b` change together; `c + [5]` builds a new list and rebinds `c`.

---

## ⚫ Interview Questions + Answers

Q1: Why does `[lambda: i for i in range(3)]` give all 2s?
A1: Closures capture the variable, not its value; the lookup happens at call time after the loop ended.

Q2: `is` vs `==`?
A2: `==` compares values; `is` compares object identity. Small-int/string interning makes `is` appear to work by accident.

Q3: Why does a mutable default persist?
A3: Defaults are evaluated once when `def` runs and stored on the function object.

Q4: Shallow vs deep copy?
A4: Shallow copies the outer container only (inner objects shared); `copy.deepcopy` recursively copies (q18).

Q5: What gets printed for `try: return 1 finally: return 2`?
A5: `2`; `finally` runs last and its return wins.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Preparing for interviews and code reviews
- Debugging "impossible" shared-state bugs

❌ Avoid when:
- Writing production code that depends on such quirks (identity of ints, evaluation oddities); prefer explicit code

---

## 📊 Visual Diagram
```
g = [[0]*2]*2            g = [[0]*2 for _ in range(2)]
 g ─► [ ● , ● ]           g ─► [ ●────► [0,0]
        └─┬─┘                    ●────► [0,0] ]
          ▼  (one list)          (two separate lists)
        [0,0]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Mutable | Can change in place | बदला जा सकने वाला |
| Alias | Two names, one object | एक object के दो नाम |
| Late binding | Name looked up at call time | call पर name खोजना |
| Identity | Same object (`is`) | वही object |
| LEGB | Local, Enclosing, Global, Builtin | scope का क्रम |
| Interning | Reusing equal small objects | छोटे objects दोबारा इस्तेमाल |

---

## ⚡ 3-Line Summary
English: Most output traps come from mutability, aliasing and when names are evaluated.
English: Trace bindings and scopes instead of guessing.
English: Verify by running; never rely on CPython implementation details.
Hindi: ज़्यादातर output traps mutability, aliasing और name के evaluate होने के समय से आते हैं।
Hindi: अंदाज़े की जगह bindings और scopes trace करो।
Hindi: चलाकर जाँचो; CPython के implementation details पर भरोसा मत करो।

---

## ➡️ Next Topic
This closes the interview-problems section. Next: revisit weak topics, rebuild earlier problems from memory, and time yourself.

---
