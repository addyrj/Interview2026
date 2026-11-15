---

# Q086. Implement Pipe
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `pipe(*fns)` that returns a function applying the given functions **left to right**.
`pipe(f, g, h)(x)` must equal `h(g(f(x)))`. With no functions it returns the input unchanged.

```python
pipe(add1, double)(5)   # double(add1(5)) -> 12
```

---

## 💡 Quick Concept (2 lines only)
Pipe is the readable cousin of compose: data flows through functions in the order you write them, like a Unix pipe `a | b | c`.
हिंदी: Pipe में functions बाएँ से दाएँ चलते हैं — जैसे लिखा है वैसे ही data बहता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Callable  # type hint for callables


def pipe(*fns: Callable) -> Callable:  # accept any number of functions
    def piped(x):  # Step 1: new function takes the initial value
        for fn in fns:  # Step 2: walk functions left -> right
            x = fn(x)  # Step 3: output of one is input of the next
        return x  # Step 4: no fns -> returns x (identity)
    return piped  # Step 5: return the pipeline


# ============================================
# TEST CASES
# ============================================
add1 = lambda x: x + 1  # helper
double = lambda x: x * 2  # helper

print(pipe(add1, double)(5))  # Expected: 12   (add1 -> 6, double -> 12)
print(pipe(double, add1)(5))  # Expected: 11   (double -> 10, add1 -> 11)
print(pipe()(7))  # Expected: 7
print(pipe(str.strip, str.split, len)("  a b c  "))  # Expected: 3
```

---

## 🔍 Why This Works (3 lines max)
Each function receives exactly the previous function's result, so the loop is a manual fold over the function list. The returned closure keeps `fns`, so the pipeline is reusable.
हिंदी: Loop हर function का result अगले function को देता है — closure में fns सुरक्षित रहते हैं।

---

## ⚡ Alternative Solution
```python
from functools import reduce  # fold helper
import asyncio  # for the async version


def pipe(*fns):  # reduce version
    return lambda x: reduce(lambda acc, fn: fn(acc), fns, x)  # fold left to right


print(pipe(add1, double)(5))  # Expected: 12


def apipe(*fns):  # async-aware pipe: awaits coroutine results
    async def run(x):  # coroutine that runs the chain
        for fn in fns:  # left to right
            x = fn(x)  # call the step
            if asyncio.iscoroutine(x):  # if the step was async
                x = await x  # wait for its result
        return x  # final value
    return run


async def adouble(x):  # simulated async I/O step
    await asyncio.sleep(0.01)  # pretend network call
    return x * 2  # result


print(asyncio.run(apipe(add1, adouble, add1)(5)))  # Expected: 13
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: passing a value instead of a function
try:
    pipe(5, add1)(1)  # ❌ 5 is not callable
except TypeError as e:
    print("TypeError:", e)  # TypeError: 'int' object is not callable

# ✅ Correct: pipe takes functions; the value goes into the returned function
print(pipe(add1, add1)(5))  # 7
```

---

## 🎯 Interview Tip (1 line)
Say: "pipe is left-to-right and more readable; I can derive compose from it with `pipe(*reversed(fns))`, and mention the async-aware variant."

---

## 🔗 Related Questions
→ Q085 (compose) | Q158 (complete pipe function) | Q084 (curry) | Q109 (reduce)
