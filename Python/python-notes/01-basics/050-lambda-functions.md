---

# 050. Lambda Functions
# हिंदी में: Lambda Functions (छोटे बिना नाम वाले functions)

---

## 🔵 Simple Definition (English)
A lambda is a small anonymous function written in one line: `lambda x: x * 2`. It can take any number of arguments but contains only ONE expression, whose value is returned automatically. It is mainly used where a short throw-away function is needed, for example as `key=` in `sorted()`.

## 🔵 सरल परिभाषा (Hindi)
Lambda एक छोटा anonymous (बिना नाम का) function है जो एक line में लिखा जाता है: `lambda x: x * 2`। इसमें कितने भी arguments हो सकते हैं लेकिन body में सिर्फ एक expression होता है जिसकी value अपने आप return होती है। इसका मुख्य उपयोग `sorted()` के `key=` जैसी जगहों पर होता है।

---

## 🔴 Problem it Solves
Many functions (`sorted`, `max`, `filter`, `map`, callbacks) need a tiny function as an argument. Writing a full `def` with a name for a one-time use makes code long and clutters the namespace. Lambda lets you define the function exactly where you use it, inline, with no name.

## 🔴 यह क्यों बना? (Hindi)
`sorted`, `max`, `filter`, `map`, callbacks को argument के रूप में छोटा function चाहिए होता है। एक बार के उपयोग के लिए नाम वाला पूरा `def` लिखना code को लंबा और गंदा करता है। Lambda से function वहीं inline बन जाता है जहाँ ज़रूरत हो, बिना नाम के।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Syntax: lambda <params>: <single expression>
Step 2 → Python creates a function object (type: function, __name__ = "<lambda>")
Step 3 → When called, the expression is evaluated
Step 4 → The result is returned automatically (no 'return' keyword)
Step 5 → Names inside the body are looked up LATE (when called), not when defined
Step 6 → Statements (assignment, if-block, for, try, print as statement) are NOT allowed
         but ternary "a if cond else b" IS an expression and is allowed
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Syntax: lambda <params>: <एक expression>
Step 2 → Python एक function object बनाता है (नाम "<lambda>")
Step 3 → call होने पर expression evaluate होता है
Step 4 → result अपने आप return होता है (return लिखना नहीं पड़ता)
Step 5 → body के variable names call के समय देखे जाते हैं (late binding)
Step 6 → statements (assignment, for, try) allowed नहीं; ternary allowed है
```

---

## 🟡 Real World Example
Zomato-style restaurant list: sort restaurants by rating (highest first) then by delivery time: `sorted(restaurants, key=lambda r: (-r["rating"], r["eta"]))`. In a FastAPI service, you might filter active users with `filter(lambda u: u.is_active, users)` or use `default_factory=lambda: {"status": "new"}` in a dataclass.

## 🟡 Real Example Hindi mein
Zomato जैसी restaurant list को rating (ज़्यादा पहले) और फिर delivery time से sort करना: `sorted(restaurants, key=lambda r: (-r["rating"], r["eta"]))`। FastAPI service में active users filter करना या dataclass में `default_factory=lambda: {...}` देना भी lambda के सामान्य उपयोग हैं।

---

## 💻 Code Example — Basic
```python
# Basic lambda usage

square = lambda x: x * x  # one parameter, returns x squared (fine for a demo)
add = lambda a, b: a + b  # two parameters
greet = lambda name="guest": f"Hello {name}"  # default argument works too

print(square(5))        # Output: 25
print(add(2, 3))        # Output: 5
print(greet())          # Output: Hello guest
print(greet("Priya"))   # Output: Hello Priya

# Ternary inside a lambda (an expression, so it is allowed)
sign = lambda n: "positive" if n > 0 else "non-positive"  # conditional expression
print(sign(3), sign(-1))  # Output: positive non-positive

# Typical use: sorting with key=
words: list[str] = ["banana", "kiwi", "apple", "fig"]  # sample data
print(sorted(words, key=lambda w: len(w)))  # sort by length (stable)
# Output: ['fig', 'kiwi', 'apple', 'banana']

# filter and map with lambda
nums: list[int] = [1, 2, 3, 4, 5, 6]  # sample numbers
evens: list[int] = list(filter(lambda n: n % 2 == 0, nums))  # keep even numbers
doubled: list[int] = list(map(lambda n: n * 2, nums))  # double every number
print(evens)    # Output: [2, 4, 6]
print(doubled)  # Output: [2, 4, 6, 8, 10, 12]
```

## 💻 Code Example — Advanced
```python
# Production style lambda usage: sorting records, dispatch table, factories, late binding
from collections.abc import Callable  # type for callables
from dataclasses import dataclass, field  # dataclass with default_factory
from functools import reduce  # fold a list into one value

Restaurant = dict[str, object]  # alias for readability

restaurants: list[Restaurant] = [  # sample data
    {"name": "Biryani House", "rating": 4.5, "eta": 30},
    {"name": "Pizza Spot", "rating": 4.5, "eta": 20},
    {"name": "Dosa Corner", "rating": 4.1, "eta": 15},
]

# 1. Multi-key sort: rating DESC, then eta ASC (negate rating to flip order)
ranked: list[Restaurant] = sorted(restaurants, key=lambda r: (-float(r["rating"]), int(r["eta"])))  # type: ignore[arg-type]
print([r["name"] for r in ranked])  # Output: ['Pizza Spot', 'Biryani House', 'Dosa Corner']

# 2. max/min with key
fastest: Restaurant = min(restaurants, key=lambda r: int(r["eta"]))  # type: ignore[arg-type]
print(fastest["name"])  # Output: Dosa Corner

# 3. Dispatch table: replace long if/elif chain with a dict of lambdas
ops: dict[str, Callable[[float, float], float]] = {  # operator name -> function
    "add": lambda a, b: a + b,
    "sub": lambda a, b: a - b,
    "mul": lambda a, b: a * b,
}
print(ops["mul"](6, 7))  # Output: 42

# 4. Function factory returning a lambda (closure)
def multiplier(n: int) -> Callable[[int], int]:  # returns a function
    return lambda x: x * n  # n is remembered from the outer scope

triple: Callable[[int], int] = multiplier(3)  # build a "multiply by 3" function
print(triple(10))  # Output: 30

# 5. reduce with lambda: product of a list
print(reduce(lambda acc, x: acc * x, [1, 2, 3, 4], 1))  # Output: 24

# 6. dataclass default_factory needs a zero-arg callable -> lambda is perfect
@dataclass
class Job:  # simple job record
    name: str  # job name
    meta: dict[str, str] = field(default_factory=lambda: {"status": "new"})  # fresh dict per instance

print(Job("email").meta)  # Output: {'status': 'new'}

# 7. LATE BINDING trap: all lambdas see the final i
bad: list[Callable[[], int]] = [lambda: i for i in range(3)]  # i is looked up at call time
print([f() for f in bad])  # Output: [2, 2, 2]
good: list[Callable[[], int]] = [lambda i=i: i for i in range(3)]  # default arg captures current i
print([f() for f in good])  # Output: [0, 1, 2]
```

---

## 🟠 JavaScript vs Python Comparison
JS arrow functions are close cousins of lambda, but arrow functions can have multi-statement bodies with `{}`. Python lambda is strictly ONE expression.

```python
# Python
double = lambda x: x * 2                         # single expression only
print(list(map(lambda x: x * 2, [1, 2, 3])))     # [2, 4, 6]
print(sorted(["bb", "a", "ccc"], key=lambda s: len(s)))  # ['a', 'bb', 'ccc']

# Multi-statement logic? Use a normal def:
def process(x: int) -> int:
    y = x * 2
    return y + 1
```
```javascript
// JavaScript
const double = x => x * 2;                       // arrow function
console.log([1, 2, 3].map(x => x * 2));          // [2, 4, 6]
console.log(["bb", "a", "ccc"].sort((a, b) => a.length - b.length));

// Arrow functions CAN have multiple statements:
const process = x => {
    const y = x * 2;
    return y + 1;
};
```

---

## 🟠 FastAPI Connection
Lambdas appear in FastAPI projects as sort keys for response data, `default_factory` in Pydantic models (fresh list/dict per object), and small inline dependency overrides in tests.

```python
from datetime import datetime  # for timestamps
from fastapi import FastAPI  # web framework
from pydantic import BaseModel, Field  # validation models

app: FastAPI = FastAPI()  # create app

class Order(BaseModel):  # response/request model
    id: int  # order id
    items: list[str] = Field(default_factory=lambda: [])  # new list for every order
    created: datetime = Field(default_factory=lambda: datetime.now())  # evaluated at creation time

@app.get("/orders", response_model=list[Order])  # GET /orders
async def list_orders() -> list[Order]:
    orders: list[Order] = [Order(id=2), Order(id=1)]  # sample data
    return sorted(orders, key=lambda o: o.id)  # sort by id using lambda key

# In tests: replace a dependency with a lambda
# app.dependency_overrides[get_db] = lambda: fake_db
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assigning a lambda to a name (PEP 8 E731)
```python
# Wrong (style): the whole point of lambda is to be anonymous
square = lambda x: x * x

# Right: use def if it needs a name (better tracebacks, docstring, type hints)
def square_fn(x: int) -> int:
    return x * x
```

❌ Mistake 2: Using statements inside a lambda
```python
# Wrong:
# f = lambda x: print(x); return x      # SyntaxError
# f = lambda x: y = x + 1               # SyntaxError (assignment is a statement)

# Right: walrus operator for assignment, or just use def
f = lambda x: (y := x + 1) * 2          # works (Python 3.8+) but hard to read; prefer def
```

❌ Mistake 3: Late binding in loops (see Advanced example)
```python
# Wrong:
funcs = [lambda: i for i in range(3)]   # all return 2

# Right: capture value with a default argument
funcs = [lambda i=i: i for i in range(3)]
```

---

## 🧠 Tricky Interview Question

```python
funcs = []
for i in range(3):
    funcs.append(lambda x: x + i)

print([f(10) for f in funcs])
```
Answer: `[12, 12, 12]`. The lambda does not copy `i`; it looks up the variable `i` in the enclosing scope when it is CALLED. By then the loop has finished and `i == 2`. Fix with a default argument (`lambda x, i=i: x + i` gives `[10, 11, 12]`) or `functools.partial`.

---

## ⚫ Interview Questions + Answers

Q1: What is a lambda function and how is it different from `def`?
A1: A lambda is an anonymous function limited to a single expression, whose value is implicitly returned. `def` can contain many statements, has a name, a docstring, annotations and better tracebacks. Both create ordinary function objects.

Q2: Can a lambda have multiple statements or a return statement?
A2: No. The body must be a single expression. You cannot use `return`, assignment, loops or `try`. You can use a conditional expression (`a if c else b`), comprehensions, and the walrus operator. For anything longer, use `def`.

Q3: Explain late binding in lambdas.
A3: Free variables in a lambda are resolved when the lambda is called, not when it is created. In a loop, all lambdas share the same variable and see its final value. Capture the current value with a default argument (`lambda i=i: i`) or use `functools.partial`.

Q4: When should you prefer a list comprehension over `map`/`filter` with lambda?
A4: Almost always. `[x * 2 for x in nums if x > 0]` is more readable and usually faster than `map(lambda x: x * 2, filter(lambda x: x > 0, nums))`. Use `map`/`filter` with a lambda only when you already have a named function or the lambda is trivial. `operator.itemgetter` and `operator.attrgetter` are faster alternatives for sort keys.

Q5: Can lambda have type hints?
A5: Not directly: the lambda syntax has no annotation slots. Annotate the variable that holds it (`f: Callable[[int], int] = lambda x: x`) or just write a `def` with full type hints.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Short `key=` functions for `sorted`, `min`, `max`
- Simple `default_factory`, callbacks, dispatch tables
- One-off tiny logic passed as an argument

❌ Avoid when:
- Logic is longer than one simple expression
- The function is reused in many places (give it a name with `def`)
- You need docstrings, type hints, or clear tracebacks

---

## 📊 Visual Diagram
```
 def square(x):          lambda x: x * x
     return x * x        ───────┬───────
        │                       │
        ▼                       ▼
 named function object    anonymous function object
 (can have many lines)    (ONE expression, returns it automatically)

 sorted(data, key=lambda r: r["age"])
                   └──── called once per item to produce the sort key
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Lambda | Anonymous one-expression function | बिना नाम का एक-expression function |
| Anonymous function | Function without a name | बिना नाम वाला function |
| Expression | Code that produces a value | ऐसा code जो value देता है |
| Late binding | Variable looked up at call time | call के समय variable की value देखना |
| `key=` | Function giving the sort/compare value | sort के लिए value देने वाला function |
| Callable | Anything that can be called | जिसे call किया जा सके |

---

## ⚡ 3-Line Summary
English: A lambda is a one-expression anonymous function: `lambda args: expression`. It is perfect for short `key=`, `default_factory` and callback uses, but not for long or reusable logic. Beware of late binding inside loops.
Hindi: Lambda एक-expression वाला बिना नाम का function है: `lambda args: expression`। छोटे `key=`, `default_factory` और callbacks के लिए बढ़िया है, लंबे या बार-बार उपयोग वाले logic के लिए नहीं। Loop में late binding से सावधान रहें।

---

## ➡️ Next Topic
**051. List (complete)** — the most used data structure in Python; then 052 List Methods (append, extend, insert, remove, pop, sort, reverse).
