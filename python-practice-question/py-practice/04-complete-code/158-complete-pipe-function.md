---

# Q158. Complete Pipe Function
# Category: Complete the Code
# Difficulty: ⭐ Easy

---

## ❓ Question
Fill in the blanks (`____`) so `pipe(f, g, h)(x)` computes `h(g(f(x)))` (left to right).

```python
from functools import ____                      # blank 1: the fold helper
from typing import Callable, Any

def pipe(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    def piped(value: Any) -> Any:
        return reduce(lambda acc, fn: ____(acc), funcs, ____)   # blanks 2, 3
    return piped

add1 = lambda x: x + 1
double = lambda x: x * 2
print(pipe(add1, double)(5))     # should print 12
```

---

## 💡 Quick Concept (2 lines only)
`pipe` passes a value through functions left to right; `compose` does the same right to left.
हिंदी: `pipe` में function बाएँ से दाएँ चलते हैं, हर एक का output अगले का input बनता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from functools import reduce                 # Blank 1 -> reduce
from typing import Callable, Any             # Step 1: type hints

def pipe(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:   # Step 2: take any functions
    def piped(value: Any) -> Any:            # Step 3: returned function takes the start value
        return reduce(lambda acc, fn: fn(acc), funcs, value)      # Blanks 2,3 -> fn(acc), value
    return piped                             # Step 4: return the pipeline

# ============================================
# TEST CASES
# ============================================
add1 = lambda x: x + 1                       # +1
double = lambda x: x * 2                     # *2
square = lambda x: x ** 2                    # squared
print(pipe(add1, double)(5))                 # Expected: 12   ((5+1)*2)
print(pipe(double, add1)(5))                 # Expected: 11   ((5*2)+1) — order matters
print(pipe(add1, double, square)(1))         # Expected: 16   (((1+1)*2)**2)
print(pipe()(7))                             # Expected: 7    (no functions = identity)
print(pipe(str.strip, str.upper, len)("  hi "))   # Expected: 2
```

---

## 🔍 Why This Works (3 lines max)
`reduce` folds the list of functions: start with `value`, then apply each function to the running result (`acc`). With no functions, `reduce` returns the initial value, so `pipe()` is the identity function.
हिंदी: `reduce` initial value से शुरू करके हर function को पिछले result पर apply करता है।

---

## ⚡ Alternative Solution
```python
# Plain loop version + compose (right to left)
from functools import reduce                 # for compose

def pipe_loop(*funcs):                       # loop-based pipe
    def piped(value):                        # takes the start value
        for fn in funcs:                     # go left to right
            value = fn(value)                # feed output into the next function
        return value                         # final result
    return piped                             # return pipeline

def compose(*funcs):                         # compose = pipe reversed
    return pipe_loop(*reversed(funcs))       # run the last function first

print(pipe_loop(lambda x: x + 1, lambda x: x * 2)(5))      # Expected: 12
print(compose(lambda x: x + 1, lambda x: x * 2)(5))        # Expected: 11  (double first, then +1)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting the initial value -> reduce starts with the first FUNCTION
from functools import reduce
funcs = [lambda x: x + 1, lambda x: x * 2]
# reduce(lambda acc, fn: fn(acc), funcs)   # acc = first lambda, then calls double(lambda) -> TypeError (not run)

# ✅ Correct: pass the value as the 3rd argument of reduce
print(reduce(lambda acc, fn: fn(acc), funcs, 5))    # Expected: 12
```

---

## 🎯 Interview Tip (1 line)
Say: "pipe is `reduce` over functions with the input as the initial value; compose is the same with the order reversed."

---

## 🔗 Related Questions
→ Q085 (compose) | Q086 (implement pipe) | Q109 (implement reduce) | Q144 (complete curry) | Q251 (functools)
