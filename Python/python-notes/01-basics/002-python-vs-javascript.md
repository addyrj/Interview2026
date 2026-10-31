---

# 002. Python vs JavaScript
# हिंदी में: Python बनाम JavaScript

---

## 🔵 Simple Definition (English)
Python and JavaScript are both high-level, dynamically typed, garbage-collected languages. JavaScript was born in the browser and runs everywhere through Node.js. Python was born as a general-purpose scripting language and now dominates data, AI and backend work. Knowing one makes the other easy to learn.

## 🔵 सरल परिभाषा (Hindi)
Python और JavaScript दोनों high-level, dynamically typed, garbage-collected languages हैं। JavaScript browser के लिए बनी थी और Node.js से server पर भी चलती है। Python general-purpose scripting language है जो आज data, AI और backend में सबसे आगे है। एक language आती हो तो दूसरी जल्दी सीख सकते हैं।

---

## 🔴 Problem it Solves
You already know JavaScript. In interviews and real jobs (FastAPI, AI, data) you need Python. If you do not map the two languages, you will write "JavaScript with Python syntax" and fall into traps: mutable defaults, indentation, `==` vs `is`, integer division, no `null`/`undefined` split, and different async models. This note builds that mental map once.

## 🔴 यह क्यों बना? (Hindi)
आपको JavaScript आती है, पर AI, data और FastAPI jobs में Python चाहिए। दोनों का mapping न हो तो आप "Python syntax में JavaScript" लिखेंगे और traps में फँसेंगे: mutable default, indentation, `==` बनाम `is`, integer division, `null`/`undefined` का फर्क, और अलग async model। यह note वही mapping एक बार साफ़ कर देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → JS:     source → V8 engine (JIT compiles to machine code) → run
Step 2 → Python: source → bytecode (.pyc) → CPython VM interprets → run
Step 3 → JS concurrency:     single thread + event loop (Promises, async/await)
Step 4 → Python concurrency: threads (GIL), multiprocessing, asyncio event loop
Step 5 → JS packages: npm + package.json + node_modules
Step 6 → Python packages: pip + requirements.txt/pyproject.toml + venv
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → JS: V8 engine source को JIT से machine code में बदलकर चलाता है
Step 2 → Python: source -> bytecode -> CPython VM उसे interpret करता है
Step 3 → JS: एक thread + event loop (Promise, async/await)
Step 4 → Python: threads (GIL के साथ), multiprocessing, और asyncio event loop
Step 5 → JS packages: npm + package.json
Step 6 → Python packages: pip + requirements.txt/pyproject.toml + venv
```

---

## 🟡 Real World Example
A startup builds a food-delivery product like Swiggy. The web frontend and a realtime chat gateway are in JavaScript/TypeScript (Node.js is great for many open sockets). The recommendation engine, ETA prediction and the public REST API are in Python (FastAPI + pandas + scikit-learn). One team, two languages, each used where it is strongest.

## 🟡 Real Example Hindi mein
Swiggy जैसा product सोचिए। Frontend और realtime chat gateway JavaScript/TypeScript (Node.js) में हैं क्योंकि बहुत सारे open sockets सँभालना आसान है। Recommendation engine, ETA prediction और public REST API Python (FastAPI + pandas + scikit-learn) में हैं। एक team, दो languages, हर एक वहाँ जहाँ वह सबसे अच्छी है।

---

## 💻 Code Example — Basic
```python
# Python vs JavaScript: the most common differences, runnable with python3

from typing import Optional  # import Optional for "value or None" type hints

# 1. No null/undefined split: Python has only None
nothing: Optional[str] = None  # None is Python's single "no value"
print(nothing is None)  # identity check with 'is' -> True

# 2. Truthiness: empty containers are falsy (JS: [] and {} are truthy!)
print(bool([]))  # empty list is falsy -> False
print(bool({}))  # empty dict is falsy -> False
print(bool("0"))  # non-empty string is truthy -> True

# 3. Division: / is always float, // is floor division (JS has only /)
print(7 / 2)  # true division -> 3.5
print(7 // 2)  # floor division -> 3
print(-7 // 2)  # floors toward minus infinity -> -4

# 4. Equality: == compares values, 'is' compares identity (JS has === for types)
a: list[int] = [1, 2]  # first list object
b: list[int] = [1, 2]  # second list object with same content
print(a == b)  # same value -> True
print(a is b)  # different objects -> False

# 5. Strings and f-strings (JS template literals)
name: str = "Priya"  # a string variable
print(f"Hello {name.upper()}!")  # expression inside {} -> Hello PRIYA!

# 6. Strict typing underneath: no implicit string+number coercion
try:
    print("5" + 5)  # JS gives "55", Python raises TypeError
except TypeError as exc:  # catch the error
    print("TypeError:", exc)  # show the message

# 7. Dict is like a JS object, but keys can be any hashable value
user: dict[str, int] = {"id": 1, "age": 25}  # create dict
print(user.get("email", "missing"))  # safe lookup with default -> missing
```

## 💻 Code Example — Advanced
```python
# Production-style mapping of JS patterns to Python: array methods, destructuring,
# spread, optional chaining, and a closure counter

from dataclasses import dataclass  # dataclass ~ JS class with auto constructor
from typing import Callable, Optional  # type hints for functions and optionals


@dataclass
class User:  # like a JS class User { constructor(id, name, address) }
    id: int  # required field
    name: str  # required field
    address: Optional[dict[str, str]] = None  # optional nested dict


def city_of(user: User) -> str:  # JS: user?.address?.city ?? "unknown"
    if user.address is None:  # no optional chaining operator, so check manually
        return "unknown"  # fallback value like ??
    return user.address.get("city", "unknown")  # dict.get gives a default


def make_counter() -> Callable[[], int]:  # closure factory (same idea as JS)
    count: int = 0  # captured variable

    def inc() -> int:  # inner function
        nonlocal count  # JS closures can assign freely; Python needs nonlocal
        count += 1  # update captured variable
        return count  # return new value

    return inc  # return the closure


def main() -> None:  # entry function
    nums: list[int] = [1, 2, 3, 4, 5]  # like const nums = [...]

    squares = [n * n for n in nums]  # JS: nums.map(n => n*n)
    evens = [n for n in nums if n % 2 == 0]  # JS: nums.filter(n => n%2===0)
    total = sum(nums)  # JS: nums.reduce((a,b) => a+b, 0)
    print(squares, evens, total)  # [1, 4, 9, 16, 25] [2, 4] 15

    first, *rest = nums  # JS: const [first, ...rest] = nums
    print(first, rest)  # 1 [2, 3, 4, 5]

    base = {"a": 1}  # JS: const base = {a: 1}
    merged = {**base, "b": 2}  # JS: {...base, b: 2}
    print(merged)  # {'a': 1, 'b': 2}

    print(city_of(User(1, "Asha")))  # unknown
    print(city_of(User(2, "Ravi", {"city": "Pune"})))  # Pune

    counter = make_counter()  # create closure
    counter()  # first call -> 1
    print(counter())  # second call -> 2


if __name__ == "__main__":  # run only when executed directly
    main()  # start program
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python way
import asyncio  # asyncio is Python's event loop library


async def fetch(n: int) -> int:  # coroutine function
    await asyncio.sleep(0.1)  # non-blocking wait, like await setTimeout promise
    return n * 2  # result


async def main() -> None:  # top-level coroutine
    results = await asyncio.gather(fetch(1), fetch(2))  # like Promise.all
    print(results)  # [2, 4]


asyncio.run(main())  # JS runs the loop for you; Python needs asyncio.run
```
```javascript
// JavaScript way
const fetchIt = (n) =>
  new Promise((resolve) => setTimeout(() => resolve(n * 2), 100)); // promise

async function main() {
  const results = await Promise.all([fetchIt(1), fetchIt(2)]); // parallel wait
  console.log(results); // [2, 4]
}
main(); // event loop is built in
```

Key differences: indentation is syntax; `None` instead of `null/undefined`; `and/or/not` instead of `&&/||/!`; `elif` instead of `else if`; `True/False` capitalised; no `++`; integers never overflow (arbitrary size); a Python coroutine does nothing until awaited or scheduled, while a JS promise starts immediately.

---

## 🟠 FastAPI Connection
FastAPI was designed to feel familiar to people coming from Express/NestJS: decorators on route functions, `async def` handlers, and automatic validation from type hints (like TypeScript types, but enforced at runtime by Pydantic).

```python
# FastAPI example (needs: pip install fastapi uvicorn)
from fastapi import FastAPI  # web framework, like Express

app = FastAPI()  # app = express()


@app.get("/users/{user_id}")  # app.get("/users/:id", ...) in Express
async def get_user(user_id: int) -> dict[str, int]:  # int is validated for you
    return {"id": user_id}  # dict becomes JSON automatically
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting `[]` or `{}` to be truthy like in JavaScript
```python
items: list[int] = []  # empty list
# Wrong (JS habit: "if (items)" is true for arrays)
if items:  # in Python an empty list is falsy
    print("has items")  # never runs
# Right: be explicit when you mean "not None"
if items is not None:  # checks only for None
    print("list exists")  # runs
```
✅ Correct: use `if items:` for "non-empty" and `is not None` for "exists".

❌ Mistake 2: Using `+` between string and number
```python
age: int = 25  # a number
# Wrong: "Age: " + age  -> TypeError (JS would coerce to "Age: 25")
# Right:
print("Age: " + str(age))  # explicit conversion
print(f"Age: {age}")  # best: f-string
```
✅ Correct: Python never coerces silently. Use `str()` or f-strings.

---

## 🧠 Tricky Interview Question

```python
# What will this output?
def add_item(item: int, bucket: list[int] = []) -> list[int]:
    bucket.append(item)  # mutates the default list
    return bucket  # returns it


print(add_item(1))
print(add_item(2))
```
Answer: `[1]` then `[1, 2]`. Default values are evaluated once, when the function is defined, so the same list is shared by all calls. In JavaScript, `function f(item, bucket = [])` creates a fresh array on every call, so JS developers get this wrong. Fix: use `bucket: Optional[list[int]] = None` and create the list inside.

---

## ⚫ Interview Questions + Answers

Q1: What are the main syntax differences between Python and JavaScript?
A1: Python uses indentation instead of braces, no semicolons, `def` instead of `function`, `None` instead of `null/undefined`, `True/False` capitalised, `and/or/not` instead of `&&/||/!`, `elif`, and f-strings instead of template literals. Python has no `let/const`; assignment creates the variable.

Q2: How do their concurrency models differ?
A2: JavaScript is single-threaded with a built-in event loop. Python has real OS threads but the GIL lets only one run Python bytecode at a time, so threads help for I/O but not CPU work. For CPU work use `multiprocessing`; for I/O concurrency use `asyncio`. A Python coroutine must be awaited or scheduled, a JS promise starts at once.

Q3: Both are dynamically typed. Is there a difference in strictness?
A3: Yes. JavaScript is weakly typed (`"5" * 2 === 10`, `[] + {}`). Python is strongly typed: `"5" * 2` is `"55"` (repetition) and `"5" + 5` raises TypeError. Python does not coerce unrelated types implicitly.

Q4: What is the equivalent of `===` and `==` in Python?
A4: Python `==` compares values and does not coerce types, so it is closest to `===` for primitives (`1 == 1.0` is True because numbers compare by value). `is` compares identity and is used for `None`: `if x is None`. JS `==` with coercion has no Python equivalent.

Q5: Which should you choose for a new backend?
A5: Choose Python (FastAPI) when the product touches data, ML, or AI libraries, or needs fast prototyping. Choose Node/TypeScript when you share code with a JS frontend or need many concurrent sockets. For raw CPU speed neither is ideal; consider Go or Rust.

---

## 🔷 When to Use + When Not to Use

✅ Use Python when:
- Data science, ML, AI, LLM apps, automation scripts
- REST APIs with strong validation (FastAPI)
- You value readability and a large standard library

✅ Use JavaScript when:
- Browser UI or full-stack TypeScript
- Realtime apps with many open connections

❌ Avoid Python when:
- Browser frontend code or mobile UI
- Hard real-time or very CPU-bound services without native extensions

---

## 📊 Visual Diagram
```
            JavaScript                      Python
         ┌───────────────┐             ┌───────────────┐
 source  │  app.js       │             │  app.py       │
         └──────┬────────┘             └──────┬────────┘
                │ V8 JIT                      │ compile
                ▼                             ▼
         machine code                   bytecode (.pyc)
                │                             │ CPython VM
                ▼                             ▼
        single thread +                threads(GIL) / processes
        event loop (libuv)             / asyncio event loop
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Truthy/Falsy | Value treated as true/false in a condition | Condition में true/false माना जाने वाला value |
| None | Python's "no value" | Python का "कोई value नहीं" |
| Floor division | `//` rounds down | `//` नीचे की तरफ round करता है |
| Event loop | Runs tasks cooperatively | Tasks को बारी-बारी चलाता है |
| GIL | One thread runs bytecode at a time | एक समय में एक thread bytecode चलाता है |
| Strong typing | No silent type coercion | Types अपने आप convert नहीं होते |

---

## ⚡ 3-Line Summary
English: Python and JavaScript are both dynamic, but Python is strongly typed, indentation-based and has one `None`. Concurrency differs: JS has a built-in event loop, Python uses threads with a GIL, processes, or `asyncio`. Use Python for data, AI and FastAPI; JavaScript for browsers and shared full-stack code.
Hindi: दोनों dynamic हैं, पर Python strongly typed है, indentation पर चलती है और उसमें सिर्फ `None` है। JS में event loop built-in है, Python में threads (GIL), processes या `asyncio`। Data, AI, FastAPI के लिए Python; browser और full-stack के लिए JavaScript।

---

## ➡️ Next Topic
**003. Python vs Java vs C++** — compiled vs interpreted, static vs dynamic typing, memory management, and speed trade-offs.
