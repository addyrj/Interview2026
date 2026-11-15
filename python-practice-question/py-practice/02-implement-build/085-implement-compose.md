---

# Q085. Implement Compose
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `compose(*fns)` that returns a new function applying the given functions **right to left**.
`compose(f, g, h)(x)` must equal `f(g(h(x)))`. With no functions it should return the input unchanged.

```python
add1 = lambda x: x + 1
double = lambda x: x * 2
compose(add1, double)(5)   # add1(double(5)) -> 11
```

---

## 💡 Quick Concept (2 lines only)
Compose chains functions into one: the output of the rightmost function becomes the input of the next one to its left. Math style `f ∘ g ∘ h`.
हिंदी: Compose कई functions को एक में जोड़ता है — दाएँ से बाएँ (right to left) चलता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Callable  # type hint for callables


def compose(*fns: Callable) -> Callable:  # accept any number of functions
    def composed(x):  # Step 1: the new function takes the initial value
        for fn in reversed(fns):  # Step 2: walk functions right -> left
            x = fn(x)  # Step 3: feed previous result into next function
        return x  # Step 4: with zero fns the loop is skipped -> identity
    return composed  # Step 5: return the combined function


# ============================================
# TEST CASES
# ============================================
add1 = lambda x: x + 1  # simple helper
double = lambda x: x * 2  # simple helper
square = lambda x: x ** 2  # simple helper

print(compose(add1, double)(5))  # Expected: 11   (double first: 10, then add1: 11)
print(compose(double, add1)(5))  # Expected: 12   (add1 first: 6, then double: 12)
print(compose()(7))  # Expected: 7    (identity)
print(compose(str, square, add1)(3))  # Expected: 16   (as str: add1 -> 4, square -> 16)
print(compose(str.upper, str.strip)("  hi  "))  # Expected: HI
```

---

## 🔍 Why This Works (3 lines max)
`reversed(fns)` gives right-to-left order, and each result is passed as the argument to the next call. The closure `composed` remembers `fns`, so we build the pipeline once and reuse it.
हिंदी: reversed से order उल्टा होता है, और हर function का output अगले का input बनता है।

---

## ⚡ Alternative Solution
```python
from functools import reduce  # fold a list into a single value


def compose(*fns):  # reduce-based, one-liner style
    return lambda x: reduce(lambda acc, fn: fn(acc), reversed(fns), x)  # fold from the right


print(compose(add1, double)(5))  # Expected: 11
print(compose()(7))  # Expected: 7

# Variant: rightmost function may take multiple args (like JS lodash flow)
def compose_multi(*fns):  # last function receives *args/**kwargs
    def composed(*args, **kwargs):  # accept anything
        *rest, last = fns  # split off the rightmost function
        result = last(*args, **kwargs)  # call it with the original arguments
        for fn in reversed(rest):  # remaining ones take one value each
            result = fn(result)  # pass the result along
        return result  # final value
    return composed


print(compose_multi(add1, lambda a, b: a * b)(3, 4))  # Expected: 13
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: iterating fns left-to-right — that is pipe(), not compose()
def bad(*fns):
    def composed(x):
        for fn in fns:  # ❌ wrong order
            x = fn(x)
        return x
    return composed

print(bad(add1, double)(5))  # 12  (expected 11 for compose)

# ✅ Correct: use reversed(fns)
```

---

## 🎯 Interview Tip (1 line)
Say: "compose is right-to-left, pipe is left-to-right — same machinery, only the iteration order differs, and zero functions must act as identity."

---

## 🔗 Related Questions
→ Q086 (pipe) | Q084 (curry) | Q158 (complete pipe function) | Q109 (reduce)
