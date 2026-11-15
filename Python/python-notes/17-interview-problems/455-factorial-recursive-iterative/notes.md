---

# 455. Factorial (recursive + iterative)
# हिंदी में: Factorial (recursive और iterative तरीके)

Runnable solution with asserts: `main.py` in this folder (`python3 main.py` prints a RecursionError demo line and `All factorial tests passed`, verified on Python 3.13.3).

---

## 🔵 Simple Definition (English)
`n!` (n factorial) is the product of all positive integers up to n: `5! = 5 x 4 x 3 x 2 x 1 = 120`. By definition `0! = 1`. Factorial is not defined for negative numbers.

## 🔵 सरल परिभाषा (Hindi)
`n!` (n factorial) n तक की सभी धनात्मक संख्याओं का गुणनफल है: `5! = 5 x 4 x 3 x 2 x 1 = 120`। परिभाषा से `0! = 1`। Negative संख्याओं के लिए factorial परिभाषित नहीं है।

---

## 🔴 Problem it Solves
Factorial counts arrangements (permutations): in how many ways can 5 tasks be ordered? In interviews it is the simplest example for comparing recursion (clear, uses the call stack) with iteration (safe, constant stack), and it shows Python's unlimited integer size.

## 🔴 यह क्यों बना? (Hindi)
Factorial arrangements (permutations) गिनता है: 5 कामों को कितने क्रमों में रखा जा सकता है? Interview में यह recursion (साफ़, call stack इस्तेमाल करता है) और iteration (सुरक्षित, constant stack) की तुलना का सबसे सरल उदाहरण है, और Python के असीमित integer भी दिखाता है।

---

## 🟢 How it Works — Step by Step

```
Recursive: fact(n) = n * fact(n - 1), base case fact(0) = fact(1) = 1
  fact(4) -> 4 * fact(3) -> 4 * 3 * fact(2) -> 4 * 3 * 2 * fact(1) -> 24
  (stack grows n frames deep, then unwinds)
Iterative: result = 1; for i in 2..n: result *= i   (no stack growth)
Functional: reduce(mul, range(2, n + 1), 1)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Recursive: fact(n) = n * fact(n - 1), base case fact(0) = fact(1) = 1
  fact(4) -> 4 * fact(3) -> 4 * 3 * fact(2) -> 4 * 3 * 2 * fact(1) -> 24
  (stack n frames गहरा जाता है, फिर वापस लौटता है)
Iterative: result = 1; for i in 2..n: result *= i   (stack नहीं बढ़ता)
Functional: reduce(mul, range(2, n + 1), 1)
```

---

## 🟡 Real World Example
A Zomato-style "combo planner" counts how many orders of 6 dishes are possible (`6! = 720`). A test-scheduling tool uses `n!` to estimate how many orderings of n tests exist, and decides to sample randomly instead of trying all of them when n gets large.

## 🟡 Real Example Hindi mein
Zomato जैसा "combo planner" गिनता है कि 6 dishes के कितने क्रम संभव हैं (`6! = 720`)। एक test-scheduling tool `n!` से अंदाज़ा लगाता है कि n tests के कितने क्रम होंगे, और n बड़ा होने पर सारे क्रम आज़माने की बजाय random sampling चुनता है।

---

## 💻 Code Example — Basic
```python
# Basic: recursive and iterative factorial
def fact_rec(n: int) -> int:  # recursive version
    if n < 0:  # undefined for negatives
        raise ValueError("factorial is not defined for negative numbers")
    if n <= 1:  # base case: 0! = 1! = 1
        return 1
    return n * fact_rec(n - 1)  # n * (n-1)!


def fact_iter(n: int) -> int:  # iterative version
    if n < 0:  # same validation
        raise ValueError("factorial is not defined for negative numbers")
    result: int = 1  # multiplicative identity
    for i in range(2, n + 1):  # 2..n (multiplying by 1 changes nothing)
        result *= i  # accumulate
    return result


print(fact_rec(5), fact_iter(5))  # both give 120
# Output: 120 120
print(fact_rec(0), fact_iter(0))  # 0! = 1
# Output: 1 1
```

## 💻 Code Example — Advanced
```python
# From main.py: stdlib check, reduce version, big numbers and the recursion limit
import math  # reference implementation
import sys  # recursion limit
from functools import reduce  # fold
from operator import mul  # multiplication as a function


def fact_reduce(n: int) -> int:
    return reduce(mul, range(2, n + 1), 1)  # initial value 1 handles n = 0 and 1


def fact_rec(n: int) -> int:
    return 1 if n <= 1 else n * fact_rec(n - 1)  # recursive version


assert all(fact_reduce(n) == math.factorial(n) for n in range(30))  # matches the stdlib
print(len(str(fact_reduce(100))))  # 100! has 158 digits and Python stores it exactly
# Output: 158
limit: int = sys.getrecursionlimit()  # usually 1000
print(limit)
# Output: 1000
try:  # recursion deeper than the limit
    fact_rec(limit + 500)
except RecursionError:
    print("RecursionError")  # the stack ran out
# Output: RecursionError
print(len(str(fact_reduce(limit + 500))))  # iterative / reduce still works
# Output: 4115
```

All outputs were produced by running on CPython 3.13.3; the default recursion limit is 1000 (CPython 3.12+ no longer ties it to the C stack, but the limit still applies).

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import math
math.factorial(25)   # 15511210043330985984000000  (exact)
```
```javascript
// JavaScript
const fact = (n) => (n <= 1n ? 1n : n * fact(n - 1n));   // BigInt needed beyond 20!
fact(25n);   // 15511210043330985984000000n
// Number: 21! = 51090942171709440000 loses precision (> 2^53)
```

Key differences: Python ints are unlimited; JS needs `BigInt` after about 18! to stay exact. Both languages limit recursion depth (Python about 1000 frames; Node about 10,000 with default stack). Python has `math.factorial`, which is C-implemented and the best choice in production.

---

## 🟠 FastAPI Connection
Never let a user pick an arbitrary `n`: `10000!` has 35,660 digits and would burn CPU and memory. Validate the range and use a sync endpoint so the heavy work runs in the thread pool.

```python
# FastAPI: factorial with input protection (pip install fastapi)
import math  # C-speed factorial

from fastapi import FastAPI, Query  # framework

app: FastAPI = FastAPI()  # create app


@app.get("/factorial")  # GET /factorial?n=10
def factorial(n: int = Query(..., ge=0, le=2000)) -> dict[str, str]:  # bounded input
    return {"n": str(n), "value": str(math.factorial(n))}  # str avoids JSON precision loss in JS clients
```

Not run as a server here; `math.factorial` itself is exercised in `main.py`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Missing base case
✅ Correct: always stop recursion at `n <= 1`.

```python
# Wrong -> RecursionError for every input
def fact(n): return n * fact(n - 1)
# Right
def fact(n): return 1 if n <= 1 else n * fact(n - 1)
```

❌ Mistake 2: Returning 0 for `0!` or not validating negatives
✅ Correct: `0! = 1`; raise `ValueError` for negatives (that is what `math.factorial` does).

❌ Mistake 3: Using recursion for large n in production
✅ Correct: use a loop or `math.factorial`; recursion hits the limit near 1000.

---

## 🧠 Tricky Interview Question

**Q**: What happens here?

```python
import math
print(math.factorial(0))
print(math.factorial(5))
try:
    math.factorial(3.0)
except Exception as e:
    print(type(e).__name__, e)
try:
    math.factorial(-1)
except ValueError as e:
    print(e)
```

**Answer**:
```
1
120
TypeError 'float' object cannot be interpreted as an integer
factorial() not defined for negative values
```
`0!` is 1 by definition. Since Python 3.10 floats (even `3.0`) are rejected with `TypeError`; negative integers raise `ValueError`. (Exact message wording can differ between Python versions.)

---

## ⚫ Interview Questions + Answers

Q1: Why is `0! = 1`?
A1: It is the empty product and it keeps formulas such as `C(n, 0) = n! / (0! n!) = 1` consistent: there is exactly one way to arrange zero items.

Q2: Recursive vs iterative: which is better in Python?
A2: Iterative. Python does not optimise tail calls and has a recursion limit of 1000 by default, so deep recursion fails and costs extra memory per frame.

Q3: Time and space complexity?
A3: O(n) multiplications. Space is O(n) stack for recursion and O(1) extra for iteration (the result itself grows with about n log n bits).

Q4: Can you raise the recursion limit?
A4: `sys.setrecursionlimit(10_000)` works but risks crashing the interpreter on a real stack overflow. Prefer iteration.

Q5: How would you compute `n!` modulo a number for huge n?
A5: Multiply in a loop and take `% mod` at each step, so numbers stay small: `result = result * i % mod`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Counting permutations or computing combinations
- Demonstrating recursion with a clear base case
- You need exact big-number results (Python handles them)

❌ Avoid when:
- n is huge and untrusted (denial-of-service risk)
- You write your own when `math.factorial` exists
- You rely on deep recursion in production

---

## 📊 Visual Diagram

```
 fact(4)
   └─ 4 * fact(3)
          └─ 3 * fact(2)
                 └─ 2 * fact(1)
                        └─ 1          <- base case
 unwind:   2*1=2  ->  3*2=6  ->  4*6=24

 stack depth = n          iterative loop: result = 1 -> 2 -> 6 -> 24
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Factorial | Product 1 x 2 x ... x n | 1 से n तक का गुणनफल |
| Base case | Condition that ends recursion | recursion रोकने की शर्त |
| Call stack | Memory of active function calls | चालू function calls की memory |
| RecursionError | Stack depth limit exceeded | recursion की गहराई सीमा पार |
| Permutation | Ordered arrangement | क्रमबद्ध व्यवस्था |
| Arbitrary precision | Unlimited integer size | असीमित integer आकार |

---

## ⚡ 3-Line Summary
English: Factorial multiplies 1 to n, with `0! = 1` and an error for negatives. Recursion is clear but limited by the recursion limit; iteration or `math.factorial` is production-safe. Python integers never overflow, but validate untrusted `n`.
Hindi: Factorial 1 से n तक गुणा करता है, `0! = 1` और negative पर error। Recursion साफ़ है पर recursion limit से बँधी है; iteration या `math.factorial` production के लिए सुरक्षित है। Python integers overflow नहीं होते, पर untrusted `n` को validate करें।

---

## ➡️ Next Topic
**456. Find Duplicates in List** — use sets and `Counter` to spot repeated values in O(n).
