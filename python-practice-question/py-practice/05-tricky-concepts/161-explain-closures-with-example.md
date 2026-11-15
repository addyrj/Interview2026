---

# Q161. Explain Closures with Example
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is a closure in Python? Show a counter built with a closure, how to modify the captured variable, and how to inspect what is captured.

---

## 💡 Quick Concept (2 lines only)
A closure is an inner function that remembers variables of its enclosing function even after the outer function has returned.
हिंदी: Closure वह inner function है जो outer function ख़त्म होने के बाद भी उसके variables याद रखता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
def make_counter(start: int = 0):             # Step 1: outer function (enclosing scope)
    count = start                             # Step 2: free variable that will be captured

    def increment(step: int = 1) -> int:      # Step 3: inner function = the closure
        nonlocal count                        # Step 4: rebind the OUTER variable (not a new local)
        count += step                         # Step 5: update captured state
        return count                          # Step 6: return the new value

    return increment                          # Step 7: return the function; make_counter is done

# ============================================
# TEST CASES
# ============================================
c1 = make_counter()                           # independent closure #1
c2 = make_counter(100)                        # independent closure #2 with its own state
print(c1(), c1(), c1(5))                      # Expected: 1 2 7
print(c2())                                   # Expected: 101   (c1 and c2 do not share state)
print(c1.__code__.co_freevars)                # Expected: ('count',)   (names captured from outside)
print(c1.__closure__[0].cell_contents)        # Expected: 7   (the live value inside the cell)
print(c2.__closure__[0].cell_contents)        # Expected: 101
```

---

## 🔍 Why This Works (3 lines max)
Python stores captured variables in "cells" attached to the inner function (`__closure__`), so they outlive the outer call. Each call to `make_counter` creates new cells, so closures are independent. Without `nonlocal`, `count += step` would try to create a local and raise `UnboundLocalError`.
हिंदी: Captured variable "cell" में रहता है, और `nonlocal` के बिना `count += step` UnboundLocalError देता है।

---

## ⚡ Alternative Solution
```python
# Same idea with a class (explicit state) and with a mutable default (hacky)
class Counter:                                # class-based equivalent
    def __init__(self, start: int = 0) -> None:   # store state on the instance
        self.count = start                    # explicit state
    def __call__(self, step: int = 1) -> int: # make the object callable
        self.count += step                    # update state
        return self.count                     # return it

c = Counter()                                 # create
print(c(), c(), c(5))                         # Expected: 1 2 7

# Closure that captures a list (mutation needs no nonlocal)
def make_logger():                            # outer
    history: list[str] = []                   # captured mutable list
    def log(msg: str) -> list[str]:           # inner
        history.append(msg)                   # mutate in place: no rebinding, so no nonlocal
        return history                        # return the shared list
    return log                                # return closure

log = make_logger()                           # create
log("a")                                      # add first message
print(log("b"))                               # Expected: ['a', 'b']
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: late binding — all lambdas see the FINAL value of i
funcs = [lambda: i for i in range(3)]         # each lambda captures the variable i, not its value
print([f() for f in funcs])                   # Actual: [2, 2, 2]

# ✅ Correct: bind the value at definition time with a default argument
funcs = [lambda i=i: i for i in range(3)]     # default is evaluated immediately
print([f() for f in funcs])                   # Expected: [0, 1, 2]
```

---

## 🎯 Interview Tip (1 line)
Say: "A closure captures variables, not values (late binding); use `nonlocal` to rebind and a default argument or `functools.partial` to freeze a value."

---

## 🔗 Related Questions
→ Q002 (late binding output) | Q040 (global vs nonlocal) | Q122 (fix late binding) | Q166 (decorators with arguments) | Q041 (LEGB)
