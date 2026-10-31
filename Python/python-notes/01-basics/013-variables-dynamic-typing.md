---

# 013. Variables + Dynamic Typing
# हिंदी में: Variables और Dynamic Typing

---

## 🔵 Simple Definition (English)
In Python, a variable is a NAME that points to an object in memory. You do not declare its type; the type belongs to the object, not the name. This is called dynamic typing: the same name can point to an int now and a string later.

## 🔵 सरल परिभाषा (Hindi)
Python में variable एक NAME है जो memory में किसी object की ओर इशारा करता है। आप type declare नहीं करते; type object का होता है, name का नहीं। इसे dynamic typing कहते हैं: एक ही name पहले int और बाद में string की ओर point कर सकता है।

---

## 🔴 Problem it Solves
Statically typed languages (Java, C++) force you to write the type first (`int age = 25;`), which means more code and less flexibility. For quick scripting, data work and prototyping, that ceremony slows you down. Python lets you write `age = 25` and moves on. The cost: type mistakes show up at runtime, which is why type hints and tools like mypy exist.

## 🔴 यह क्यों बना? (Hindi)
Statically typed languages (Java, C++) में पहले type लिखना पड़ता है (`int age = 25;`), यानी ज़्यादा code और कम flexibility। Scripting, data work और prototyping में यह रफ़्तार घटाता है। Python में बस `age = 25` लिखें और आगे बढ़ें। कीमत: type की गलतियाँ runtime पर दिखती हैं, इसीलिए type hints और mypy जैसे tools हैं।

---

## 🟢 How it Works — Step by Step

```
Statement:  age = 25

Step 1 → Python creates an int object holding 25 in memory
Step 2 → It creates (or reuses) the name "age" in the current namespace
Step 3 → The name is bound to the object (name -> object reference)
Step 4 → age = "hello" simply re-binds the name to a NEW str object
Step 5 → The old int object is freed when no name points to it (ref count = 0)

    names (stack/namespace)        objects (heap)
    ┌─────────┐                    ┌──────────┐
    │  age    │ ─────────────────► │ int: 25  │
    └─────────┘                    └──────────┘
    b = age   → second name, SAME object (no copy!)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Statement:  age = 25

Step 1 → Python memory में 25 वाला int object बनाती है
Step 2 → Current namespace में name "age" बनता है (या मिलता है)
Step 3 → Name उस object से bind हो जाता है
Step 4 → age = "hello" से name नए str object पर दोबारा bind होता है
Step 5 → पुराना int object तब हटता है जब कोई name उसे point न करे

b = age → दूसरा name, वही object (copy नहीं बनती!)
```

---

## 🟡 Real World Example
In an Instagram-style API, one function reads a request value: `user_id = request.query["id"]` is a string like `"42"`. After validation, `user_id = int(user_id)` rebinds the same name to an int. In a data pipeline, a variable `data` can start as a list of dicts, then become a pandas DataFrame. This flexibility is great, but in production code teams add type hints (`user_id: int`) so editors and mypy catch mistakes early.

## 🟡 Real Example Hindi mein
Instagram जैसी API में एक function request की value पढ़ता है: `user_id = request.query["id"]` यानी `"42"` जैसी string। Validation के बाद `user_id = int(user_id)` उसी name को int पर दोबारा bind करता है। Data pipeline में `data` पहले dicts की list हो सकता है और फिर pandas DataFrame। यह flexibility अच्छी है, पर production code में teams type hints (`user_id: int`) लगाती हैं ताकि editor और mypy गलतियाँ जल्दी पकड़ें।

---

## 💻 Code Example — Basic
```python
# Basic: variables, dynamic typing and naming
name = "Priya"  # str: no type keyword needed
age = 25  # int
salary = 75000.50  # float
is_active = True  # bool (capital T)
nothing = None  # None means "no value"

print(type(age))  # Output: <class 'int'>

age = "twenty five"  # same name, now points to a str (allowed!)
print(type(age))  # Output: <class 'str'>

# Multiple assignment
x, y, z = 1, 2, 3  # unpack three values into three names
a = b = 0  # both names point to the SAME object 0
print(x, y, z, a, b)  # Output: 1 2 3 0 0

# Swap without a temp variable
x, y = y, x  # right side is evaluated first, then assigned
print(x, y)  # Output: 2 1

# Extended unpacking
first, *middle, last = [10, 20, 30, 40]  # star collects the rest
print(first, middle, last)  # Output: 10 [20, 30] 40

# Optional type hints (documentation only, not enforced)
city: str = "Pune"  # we TELL readers/tools it is a str
city = 123  # Python will NOT stop this at runtime
print(city)  # Output: 123
```

## 💻 Code Example — Advanced
```python
# Advanced: names vs objects, mutability, constants, scope
from __future__ import annotations  # modern hints on all 3.x

import sys  # to show reference counts
from typing import Final  # Final = "do not rebind" (checked by mypy only)

MAX_RETRIES: Final[int] = 3  # constant by convention: UPPER_CASE

# 1. Two names, one object (aliasing)
list_a: list[int] = [1, 2, 3]  # one list object
list_b: list[int] = list_a  # list_b is another NAME for the same list
list_b.append(4)  # mutate through list_b
print(list_a)  # Output: [1, 2, 3, 4]  <- list_a changed too!
print(list_a is list_b)  # Output: True  (same object)

# 2. Make a real copy when you need independence
list_c: list[int] = list_a.copy()  # new list object with the same items
list_c.append(5)  # changes only list_c
print(list_a, list_c)  # Output: [1, 2, 3, 4] [1, 2, 3, 4, 5]

# 3. Immutable objects: rebinding creates a new object
n: int = 10  # int object 10
before: int = id(n)  # memory identity of that object
n += 1  # ints are immutable: this makes a NEW int and rebinds n
print(id(n) == before)  # Output: False

# 4. Scope: assignment inside a function creates a LOCAL name
counter: int = 0  # module-level (global) name


def broken() -> None:
    counter = 99  # creates a new LOCAL variable; global is untouched
    print("inside:", counter)  # Output: inside: 99


def fixed() -> None:
    global counter  # say we mean the module-level name
    counter += 1  # now the global is updated


broken()  # runs the function with a local name
fixed()  # updates the global
print(counter)  # Output: 1

# 5. Naming rules and checks
print("user_name".isidentifier(), "2fast".isidentifier())  # Output: True False
print(sys.getrefcount(MAX_RETRIES) > 0)  # Output: True (every object has a ref count)
```

---

## 🟠 JavaScript vs Python Comparison
Both are dynamically typed. Key differences: JS needs `let`/`const`/`var`; Python has no keyword for creating a variable and no real `const` (only conventions and `Final` for type checkers). Python variables are scoped to the function (no block scope for `if`/`for`), and there is no hoisting or `undefined`: using an unassigned name raises `NameError`.

```python
# Python
count = 1  # just assign, no keyword
if True:
    inner = "visible"  # defined inside an if block
print(inner)  # Output: visible (no block scope in Python!)
PI = 3.14159  # constant by convention only
```
```javascript
// JavaScript
let count = 1; // keyword required
if (true) {
  let inner = "hidden"; // block scoped
}
// console.log(inner); // ReferenceError: inner is not defined
const PI = 3.14159; // real constant, cannot be reassigned
```

---

## 🟠 FastAPI Connection
In FastAPI the type hints on variables and parameters are not decoration: FastAPI and Pydantic READ them at runtime to validate and convert incoming data. So `user_id: int` in a path function turns the URL text `"42"` into the int `42`, and returns an error response (422) for `"abc"`. Dynamic typing plus enforced hints at the API boundary gives flexibility inside and safety at the edges.

```python
from fastapi import FastAPI  # the web framework

app: FastAPI = FastAPI()  # app object, hinted for readability


@app.get("/users/{user_id}")  # GET /users/42
def get_user(user_id: int, verbose: bool = False) -> dict[str, int | bool]:
    # user_id arrives as text "42" in the URL; FastAPI converts it using the hint
    return {"user_id": user_id, "verbose": verbose}  # "/users/42?verbose=true"
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Thinking `b = a` copies a list or dict
```python
# Wrong:
a = [1, 2]
b = a  # same object, not a copy
b.append(3)
print(a)  # [1, 2, 3]  <- surprise!

# Right:
c = a.copy()  # real copy (use copy.deepcopy for nested data)
```
✅ Correct: assignment binds names; use `.copy()` or `copy.deepcopy()`.

❌ Mistake 2: Using a keyword or builtin name as a variable
```python
# Wrong:
list = [1, 2, 3]  # shadows the builtin list()
# later: list("abc") -> TypeError: 'list' object is not callable
# Right:
items = [1, 2, 3]  # choose a descriptive name
```
✅ Correct: avoid names like `list`, `dict`, `str`, `id`, `type`, `input`, `sum`.

❌ Mistake 3: Reading a variable before assigning it
```python
# Wrong:
# print(total)   # NameError: name 'total' is not defined
# Right:
total = 0  # assign first
print(total)  # 0
```
✅ Correct: Python has no hoisting; define a name before using it.

---

## 🧠 Tricky Interview Question

```python
# What will this output?
a = 256
b = 256
print(a is b)

x = 1000
y = 1000
print(x is y)

def f():
    n = 5
    def g():
        print(n)
    n = 10
    return g

f()()
```
Answer: The first prints `True`: CPython caches small ints (-5 to 256), so both names point to the same object. The second is implementation-dependent: 1000 is outside the small-int cache, so in the interactive REPL it prints `False` (two separate objects), but when run as a script file CPython's compiler reuses one constant object and it prints `True`. Never rely on `is` for numbers. `f()()` prints `10`, not `5`: the closure remembers the variable `n`, not its value at the time `g` was defined, and `n` was changed to `10` before `g` ran. Lesson: use `==` for values, `is` only for `None`.

---

## ⚫ Interview Questions + Answers

Q1: Is Python statically or dynamically typed? Strongly or weakly?
A1: Dynamically typed (types checked at runtime, names have no fixed type) and strongly typed (it will not silently convert incompatible types: `"5" + 5` raises TypeError). JavaScript is dynamic and weak (`"5" + 5` gives `"55"`).

Q2: What happens in memory with `a = 5; b = a; a = 6`?
A2: `a` and `b` first point to the same int object 5. Then `a = 6` rebinds the name `a` to a different int object 6. `b` still points to 5. Rebinding never changes other names. Mutating a mutable object (list.append) is different: all names pointing to that object see the change.

Q3: What are the naming rules and conventions?
A3: Names may contain letters, digits and underscores, cannot start with a digit, are case sensitive, and cannot be keywords (`if`, `class`, `None`). PEP 8: `snake_case` for variables and functions, `PascalCase` for classes, `UPPER_CASE` for constants, `_name` for "internal", `__name` for name mangling.

Q4: Does Python have constants?
A4: Not enforced. By convention you write `MAX_SIZE = 100` in upper case. `typing.Final` lets mypy warn if you reassign it. For truly immutable data use tuples, frozensets, `frozen=True` dataclasses or `enum.Enum`.

Q5: Are type hints enforced at runtime?
A5: No. Python ignores them when running. They help editors, mypy/pyright and libraries such as Pydantic and FastAPI, which read them (via `__annotations__`) and enforce them deliberately. `x: int = "hi"` runs fine.

---

## 🔷 When to Use + When Not to Use
✅ Use dynamic typing when:
- Prototyping, scripts, data exploration
- Writing flexible helpers (duck typing)
- You add type hints on public functions for clarity

❌ Avoid relying on it when:
- Large codebases without hints or tests (bugs hide until runtime)
- Passing data across API boundaries without validation (use Pydantic)
- Reusing one variable name for unrelated types in the same function (confusing)

---

## 📊 Visual Diagram
```
  a = [1, 2]        b = a             b.append(3)          c = a.copy()
  ┌───┐             ┌───┐             ┌───┐                ┌───┐
  │ a │──┐          │ a │──┐          │ a │──┐             │ a │──► [1,2,3]
  └───┘  ▼          └───┘  ▼          └───┘  ▼             └───┘
      [1, 2]        ┌───┐ [1, 2]      ┌───┐ [1, 2, 3]      ┌───┐
                    │ b │──┘          │ b │──┘             │ c │──► [1,2,3] (new)
                    └───┘             └───┘                └───┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Variable | Name bound to an object | Object से bind हुआ name |
| Dynamic typing | Type checked at runtime | Type runtime पर check होता है |
| Binding | Connecting a name to an object | Name को object से जोड़ना |
| Mutable | Can change in place | जगह पर बदल सकता है |
| Alias | Second name for same object | उसी object का दूसरा name |
| Scope | Where a name is visible | Name कहाँ दिखता है |

---

## ⚡ 3-Line Summary
English: A Python variable is a name bound to an object, and types live on objects, not names. Assignment never copies; it only binds, so mutable objects shared by two names change together. Type hints document intent and are enforced only by tools like mypy and Pydantic.
Hindi: Python variable एक name है जो object से bind होता है, और type object का होता है। Assignment copy नहीं करता, सिर्फ bind करता है, इसलिए दो names वाला mutable object साथ बदलता है। Type hints सिर्फ intent बताते हैं; mypy और Pydantic उन्हें enforce करते हैं।

---

## ➡️ Next Topic
**014. Python Data Types Overview** — the built-in types (int, str, list, dict ...) and which are mutable.
