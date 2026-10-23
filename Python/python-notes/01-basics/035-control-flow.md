---

# 035. Control Flow — if/elif/else, Loops, break/continue/pass
# हिंदी में: Control Flow — Complete Guide

---

## 🔵 Simple Definition (English)
Control flow determines the order code executes. Python has: `if/elif/else` for branching, `for` loop for iterating over sequences, `while` loop for condition-based repetition, and `break/continue/pass` to control loop execution. Python uses indentation (not braces) to define blocks.

## 🔵 सरल परिभाषा (Hindi)
Control flow code के execute होने का order decide करता है। Python में: `if/elif/else` branching, `for` sequence iterate करने के लिए, `while` condition-based loop, `break/continue/pass` loop control। Python braces की जगह indentation use करती है।

---

## 💻 Code Example — Basic
```python
# ─── if/elif/else ────────────────────────────────────────────────
age = 22

if age < 13:
    print("child")
elif age < 18:
    print("teenager")
elif age < 60:
    print("adult")
else:
    print("senior")

# TERNARY (one-liner if/else):
status = "adult" if age >= 18 else "minor"
print(status)   # "adult"

# MATCH/CASE (Python 3.10+ — like switch):
command = "quit"
match command:
    case "start":
        print("Starting...")
    case "stop" | "quit":       # multiple values with |
        print("Stopping...")
    case _:                      # default (like else)
        print(f"Unknown: {command}")

# ─── for loop ────────────────────────────────────────────────────
fruits = ["apple", "mango", "banana"]

# Basic iteration:
for fruit in fruits:
    print(fruit)

# With index: enumerate (NEVER use range(len(fruits))!)
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")       # 0: apple, 1: mango, 2: banana

# Iterate dict:
person = {"name": "Priya", "age": 25}
for key, value in person.items():
    print(f"{key}: {value}")

# range():
for i in range(5):              # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):           # 1, 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2):      # 0, 2, 4, 6, 8 (step=2)
    print(i)

# ─── while loop ──────────────────────────────────────────────────
count = 0
while count < 5:
    print(count)
    count += 1

# while with break — read until sentinel:
while True:
    user_input = input("Enter (q to quit): ")
    if user_input == "q":
        break
    print(f"You entered: {user_input}")

# ─── break / continue / pass ─────────────────────────────────────
for i in range(10):
    if i == 3:
        continue        # skip 3, keep going
    if i == 7:
        break           # stop at 7
    print(i)            # prints: 0 1 2 4 5 6

# pass — do nothing (placeholder):
def not_implemented_yet():
    pass                # valid empty function body

class EmptyClass:
    pass                # valid empty class
```

## 💻 Code Example — Advanced
```python
# Production patterns using control flow

# ─── for/else and while/else ─────────────────────────────────────
# else clause runs only if loop completed WITHOUT break:

def find_admin(users: list[dict]) -> str | None:
    for user in users:
        if user.get("role") == "admin":
            return user["name"]   # found — function exits
    else:
        return None               # loop completed without finding admin

# More common pattern (same result, clearer):
admin = next((u["name"] for u in users if u.get("role") == "admin"), None)

# ─── Nested loops with labels (Python has no labels — use functions):
def find_pair(matrix: list[list[int]], target: int) -> tuple[int, int] | None:
    """Find first cell with target value."""
    for i, row in enumerate(matrix):
        for j, val in enumerate(row):
            if val == target:
                return (i, j)   # exits both loops immediately!
    return None

matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print(find_pair(matrix, 5))   # (1, 1)

# ─── Comprehensions — preferred over loops for simple transforms:
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# List comprehension vs loop:
evens_loop = []
for n in numbers:
    if n % 2 == 0:
        evens_loop.append(n)

evens_comp = [n for n in numbers if n % 2 == 0]  # cleaner!
print(evens_comp)    # [2, 4, 6, 8, 10]

# Nested comprehension (matrix flatten):
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [n for row in matrix for n in row]   # [1,2,3,4,5,6,7,8,9]

# Dict comprehension:
squared = {n: n**2 for n in range(1, 6)}
print(squared)   # {1:1, 2:4, 3:9, 4:16, 5:25}

# zip() — iterate two sequences together:
names  = ["Priya", "Raj", "Amit"]
scores = [95, 87, 92]
for name, score in zip(names, scores):
    print(f"{name}: {score}")

# zip stops at shortest — use itertools.zip_longest for full iteration
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: no braces, colon + indentation
if x > 0:
    print("positive")
elif x < 0:
    print("negative")
else:
    print("zero")

# Python for loop:
for i in range(5):
    print(i)

# Python ternary:
result = "yes" if condition else "no"
```

```javascript
// JavaScript: braces required
if (x > 0) {
    console.log("positive");
} else if (x < 0) {
    console.log("negative");
} else {
    console.log("zero");
}

// JS for loop:
for (let i = 0; i < 5; i++) {
    console.log(i);
}

// JS ternary:
let result = condition ? "yes" : "no";
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `range(len(list))` instead of `enumerate`
```python
# Wrong — C-style, not Pythonic:
for i in range(len(fruits)):
    print(fruits[i])

# Correct — Pythonic:
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")
```

❌ Mistake 2: Modifying a list while iterating it
```python
# Wrong — may skip elements or crash:
for item in my_list:
    if condition(item):
        my_list.remove(item)    # modifying while iterating!

# Correct — iterate a copy:
for item in my_list[:]:        # my_list[:] is a copy
    if condition(item):
        my_list.remove(item)

# Or better — filter to new list:
my_list = [item for item in my_list if not condition(item)]
```

---

## 🧠 Tricky Interview Question

```python
for i in range(3):
    print(i)
else:
    print("done")
```
What prints if we add `break` when `i == 1`?
```python
for i in range(3):
    if i == 1:
        break
    print(i)
else:
    print("done")
```
Answer: prints `0` only. The `else` block does NOT run when loop exits via `break`. `else` only runs when the loop completes normally (exhausts the iterable or condition becomes False for while).

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `break`, `continue`, and `pass`?
A1: `break` exits the loop entirely. `continue` skips the rest of the current iteration and goes to the next. `pass` does absolutely nothing — it's a syntactic placeholder for empty blocks that must be syntactically valid (empty function, empty class, empty if branch). Example: `if debug: pass` — valid syntax with no effect.

Q2: What does `enumerate()` do and why prefer it over `range(len())`?
A2: `enumerate(iterable)` yields `(index, value)` pairs. `enumerate(fruits, start=1)` starts counting from 1. Prefer it because: (1) reads like English — "for index, item in items", (2) works with any iterable (not just things with `.len()`), (3) no chance of off-by-one errors, (4) more Pythonic (PEP 20: "Beautiful is better than ugly").

Q3: What is a list comprehension and when should you use it?
A3: `[expression for item in iterable if condition]` — creates a new list in one line. Use it for simple transformations and filtering that would otherwise be a for loop with `.append()`. Don't use it for: (1) complex logic that needs multiple lines, (2) side effects (printing, modifying external state), (3) deeply nested (more than 2 levels = use a regular loop for readability).

Q4: What does `zip()` return and how do you handle lists of different lengths?
A4: `zip()` returns an iterator of tuples, stopping at the shortest iterable. `zip([1,2,3], [4,5])` yields `(1,4), (2,5)` — 3 is dropped. For full iteration: `itertools.zip_longest([1,2,3], [4,5], fillvalue=0)` yields `(1,4), (2,5), (3,0)`.

Q5: What is the walrus operator `:=` and when is it useful?
A5: Assignment expression (Python 3.8+) — assigns and returns a value in one step. Useful in `while` loops: `while chunk := f.read(8192): process(chunk)` instead of `chunk = f.read(8192); while chunk: process(chunk); chunk = f.read(8192)`. In comprehensions: `[y for x in data if (y := process(x)) > 0]` — avoids calling `process(x)` twice.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Control flow | Order of code execution | Code execution का order |
| Ternary | One-line if/else | One-line if/else |
| enumerate | Index + value iteration | Index + value एक साथ |
| break | Exit loop immediately | Loop से तुरंत बाहर |
| continue | Skip current iteration | Current iteration skip करो |
| pass | Do nothing (placeholder) | कुछ मत करो (placeholder) |
| Comprehension | One-line loop to create list/dict/set | One-line loop |

---

## ⚡ 3-Line Summary
English: Python control flow uses colon + indentation (no braces). Use `enumerate` instead of `range(len())`, and comprehensions for simple loop-and-collect patterns. `break` skips the `else` block on a loop; `continue` skips the iteration; `pass` is a syntactic no-op.
Hindi: Python में braces नहीं — colon + indentation। `enumerate` use करो `range(len())` की जगह। `break` से loop `else` नहीं चलता; `pass` = nothing।

---

## ➡️ Next Topic
**036. Ternary Expression** → **037. match/case** → **038. for Loop Deep Dive** — iterables, iterators, `iter()`, `next()`.
