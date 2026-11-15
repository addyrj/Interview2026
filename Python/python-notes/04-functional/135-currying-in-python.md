---

# 135. Currying in Python
# हिंदी में: Currying (कई arguments वाले function को एक-एक argument की chain में बदलना)

---

## 🔵 Simple Definition (English)
Currying turns a function `f(a, b, c)` into a chain `f(a)(b)(c)`, where each call takes one argument and returns the next function. Python does not do this automatically. You build it with closures, `functools.partial` or a small decorator.

## 🔵 सरल परिभाषा (Hindi)
Currying में `f(a, b, c)` जैसे function को `f(a)(b)(c)` की chain में बदलते हैं, जहाँ हर call एक argument लेकर अगला function लौटाती है। Python यह अपने आप नहीं करता। इसे closure, `functools.partial` या छोटे decorator से बनाते हैं।

---

## 🔴 Problem it Solves
You often call the same function with the first few arguments fixed (same tax rate, same base URL, same log level). Repeating them everywhere is noisy. Currying (and partial application) lets you fix some arguments once and get a smaller, reusable function.

## 🔴 यह क्यों बना? (Hindi)
अक्सर एक ही function को पहले कुछ arguments वही रखकर बार-बार call करना पड़ता है (वही tax rate, वही base URL, वही log level)। हर जगह दोहराना गंदा लगता है। Currying (और partial application) से कुछ arguments एक बार fix करके छोटा, दोबारा इस्तेमाल होने वाला function मिल जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write add(a, b, c) normally
Step 2 → Curried form: add(a) returns a function waiting for b
Step 3 → That function, given b, returns a function waiting for c
Step 4 → When all arguments are collected, the real function runs
Step 5 → Each step is a closure that remembers the earlier arguments
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → add(a, b, c) सामान्य रूप में लिखो
Step 2 → Curried रूप में add(a) एक function लौटाता है जो b का इंतज़ार करता है
Step 3 → वह b मिलने पर ऐसा function लौटाता है जो c का इंतज़ार करता है
Step 4 → सारे arguments मिलने पर असली function चलता है
Step 5 → हर step एक closure है जो पिछले arguments याद रखता है
```

---

## 🟡 Real World Example
Zomato computes the final bill as `bill(tax)(discount)(price)`. The tax rate for a city is fixed once (`gst = bill(0.05)`), the coupon is fixed per order, and the price changes per item. A logging helper `log(level)(service)(message)` lets each microservice fix its level and name once. An AI app fixes the model name and temperature once with `partial` and then only passes prompts.

## 🟡 Real Example Hindi mein
Zomato final bill को `bill(tax)(discount)(price)` से निकाल सकता है। शहर का tax rate एक बार fix होता है (`gst = bill(0.05)`), coupon हर order का fix, और price हर item का बदलता है। Logging helper `log(level)(service)(message)` में हर microservice अपना level और नाम एक बार fix कर लेती है। AI app में model name और temperature `partial` से एक बार fix करके सिर्फ prompt भेजते हैं।

---

## 💻 Code Example — Basic
```python
# Basic currying - every line commented
from functools import partial  # standard tool for fixing arguments
from typing import Callable  # type hints


def add3(a: int, b: int, c: int) -> int:  # normal 3-argument function
    return a + b + c  # plain sum


def add3_curried(a: int) -> Callable[[int], Callable[[int], int]]:  # manual curry
    def with_b(b: int) -> Callable[[int], int]:  # waits for b
        def with_c(c: int) -> int:  # waits for c
            return a + b + c  # a and b come from closures
        return with_c  # return last step
    return with_b  # return middle step


print(add3(1, 2, 3))  # normal call
# Output: 6
print(add3_curried(1)(2)(3))  # chain of single-argument calls
# Output: 6

add_to_ten = add3_curried(10)  # fix a=10, get a function back
print(add_to_ten(5)(5))  # supply remaining arguments later
# Output: 20


# Same idea with lambdas (like JS arrow functions)
mul: Callable[[int], Callable[[int], int]] = lambda x: lambda y: x * y  # curried mul
print(mul(4)(5))  # call it
# Output: 20

# functools.partial: fix arguments without writing nested functions
double = partial(add3, 1, 1)  # a=1, b=1 fixed; still needs c
print(double(8))  # only c is passed
# Output: 10

power = partial(pow, exp=2)  # fix the keyword exp=2 (builtin pow supports it)
print(power(9))  # 9 squared
# Output: 81

print(double.func.__name__, double.args)  # partial remembers what it holds
# Output: add3 (1, 1)
```

## 💻 Code Example — Advanced
```python
# Production style: generic curry decorator, partial config, billing example
import inspect  # to count the parameters of a function
from functools import partial, wraps  # partial + metadata helper
from typing import Any, Callable, Dict, List  # type hints


def curry(func: Callable[..., Any]) -> Callable[..., Any]:  # auto-curry decorator
    arity: int = len(inspect.signature(func).parameters)  # how many args needed

    @wraps(func)  # keep name and docstring
    def curried(*args: Any) -> Any:  # collects args over many calls
        if len(args) >= arity:  # enough arguments collected
            return func(*args[:arity])  # run the real function
        return lambda *more: curried(*args, *more)  # wait for more arguments
    return curried  # return the curried version


@curry  # apply the decorator
def bill(tax: float, discount: float, price: float) -> float:  # 3 inputs
    return round(price * (1 - discount) * (1 + tax), 2)  # final amount


print(bill(0.05, 0.10, 200))  # all at once
# Output: 189.0
print(bill(0.05)(0.10)(200))  # one at a time
# Output: 189.0
print(bill(0.05, 0.10)(200))  # mixed styles also work
# Output: 189.0

mumbai_bill = bill(0.05)  # fix the city tax once
welcome_offer = mumbai_bill(0.20)  # fix the coupon too
prices: List[float] = [100, 250, 80]  # item prices
print([welcome_offer(p) for p in prices])  # reuse for many items
# Output: [84.0, 210.0, 67.2]


# partial for configuration: fix model settings, vary only the prompt
def call_llm(model: str, temperature: float, prompt: str) -> Dict[str, Any]:  # fake LLM
    return {"model": model, "temp": temperature, "prompt": prompt}  # echo settings


creative = partial(call_llm, "gpt-mini", 0.9)  # high randomness preset
strict = partial(call_llm, "gpt-mini", 0.0)  # deterministic preset
print(creative("write a poem"))  # uses preset
# Output: {'model': 'gpt-mini', 'temp': 0.9, 'prompt': 'write a poem'}
print(strict(prompt="extract date"))  # keyword for the last argument
# Output: {'model': 'gpt-mini', 'temp': 0.0, 'prompt': 'extract date'}


# Logging factory: three levels of currying
def log(level: str) -> Callable[[str], Callable[[str], str]]:  # first argument
    def for_service(service: str) -> Callable[[str], str]:  # second argument
        def message(text: str) -> str:  # last argument
            return f"[{level}] {service}: {text}"  # formatted line
        return message  # final function
    return for_service  # middle function


error_in_payments = log("ERROR")("payments")  # fixed level and service
print(error_in_payments("card declined"))  # only message left
# Output: [ERROR] payments: card declined
```

---

## 🟠 JavaScript vs Python Comparison
In JavaScript, currying is natural: arrow functions chain easily (`a => b => c => ...`) and libraries like lodash provide `_.curry`. In Python nested lambdas work too, but `functools.partial` is the idiomatic tool, because Python functions accept keyword arguments and defaults.

```python
# Python way
from functools import partial
def volume(l, w, h): return l * w * h
print(volume(2, 3, 4))                       # 24
print(partial(volume, 2, 3)(4))              # 24 (partial application)
print((lambda l: lambda w: lambda h: l*w*h)(2)(3)(4))   # 24 (true currying)
```
```javascript
// JavaScript way
const volume = (l) => (w) => (h) => l * w * h;   // curried by shape
console.log(volume(2)(3)(4));                    // 24
const base = volume(2)(3);                       // reuse partially
console.log(base(4));                            // 24
// const f = _.curry((a, b, c) => a + b + c);    // lodash auto-curry
```

Key differences: true currying (one argument per call) is the JS default style, while Python prefers `partial` (fix any number of arguments, in one step). Python's standard library has no `curry`; write one or use `toolz.curry`.

---

## 🟠 FastAPI Connection
Dependencies in FastAPI are called with no arguments by the framework, so configuration must be fixed beforehand. A curried factory (or `partial`) produces a dependency already configured, for example a rate limiter with a fixed limit, or a pagination checker with a fixed maximum.

```python
# FastAPI: curried dependency factory (pip install fastapi httpx)
from typing import Callable, Dict  # type hints
from fastapi import Depends, FastAPI, Query  # core imports
from fastapi.testclient import TestClient  # in-process testing

app: FastAPI = FastAPI()  # create app


def limit_of(max_allowed: int) -> Callable[..., int]:  # first call fixes the max
    def dependency(limit: int = Query(10, ge=1)) -> int:  # FastAPI calls this
        return min(limit, max_allowed)  # clamp to the allowed maximum
    return dependency  # configured dependency


@app.get("/orders")  # GET /orders?limit=...
def orders(limit: int = Depends(limit_of(50))) -> Dict[str, int]:  # use factory
    return {"limit": limit}  # response


client = TestClient(app)  # test client
print(client.get("/orders?limit=500").json())  # asks for too many
# Output: {'limit': 50}
print(client.get("/orders").json())  # default
# Output: {'limit': 10}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Confusing currying with `partial`
```python
# Wrong assumption - partial does not return a one-argument chain
from functools import partial
f = partial(lambda a, b, c: a + b + c, 1)
# f(2)(3) -> TypeError, because f(2) already needs c

# Right - partial fixes arguments in one step; call with the rest together
print(f(2, 3))   # 6
```

❌ Mistake 2: Curry decorator on functions with defaults or *args
```python
# Wrong - len(signature.parameters) counts defaults and *args too
# @curry
# def f(a, b=1): ...      # curry thinks it needs 2 arguments

# Right - curry only fixed-arity functions, or pass the arity explicitly
```

❌ Mistake 3: Late binding when building curried lambdas in a loop
```python
# Wrong - every adder uses the last n
adders = [lambda x: x + n for n in range(3)]
print([a(10) for a in adders])    # [12, 12, 12]

# Right - fix n using partial or a default argument
from functools import partial
adders = [partial(lambda n, x: x + n, n) for n in range(3)]
print([a(10) for a in adders])    # [10, 11, 12]
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from functools import partial

def f(a, b, c=0):
    return (a, b, c)

g = partial(f, 1)
h = partial(g, c=5)
print(g(2), h(2))
print(g.func is f, h.func is f)
try:
    partial(f, a=1)(2)
except TypeError as e:
    print("TypeError:", e)
```

**Answer**:
```
(1, 2, 0) (1, 2, 5)
True True
TypeError: f() got multiple values for argument 'a'
```
Nesting `partial` flattens: `h` holds `f` directly (not `g`) with the merged arguments. The last call fails because `a=1` is fixed as a keyword, and then the positional `2` also fills `a`. Positional arguments fill from the left, so fixing a keyword for an early parameter breaks positional calls.

---

## ⚫ Interview Questions + Answers

Q1: What is currying?
A1: Converting a function of n arguments into n nested functions of one argument each, so `f(a, b, c)` becomes `f(a)(b)(c)`.

Q2: How is currying different from partial application?
A2: Currying always yields single-argument steps. Partial application fixes some arguments and returns a function taking the rest, in any grouping. `functools.partial` is partial application.

Q3: Does Python have built-in currying?
A3: No. Use closures, `functools.partial`, or third-party `toolz.curry`. You can also write a small decorator using `inspect.signature`.

Q4: Why is currying useful?
A4: It creates specialised functions from general ones (fixed tax rate, fixed model), improves reuse, and fits pipelines like `map(tax_for_mumbai, prices)`.

Q5: What is a drawback of currying in Python?
A5: It is unusual in Python code, so teammates find it harder to read, stack traces are deeper, and keyword arguments do not fit the one-argument chain well. Often `partial` or a small class is clearer.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You reuse a function with the same first arguments many times
- You need a function with a fixed config for `map`, callbacks or `Depends`
- You build configurable validators, loggers or pricing rules

❌ Avoid when:
- A default argument or keyword argument solves the problem
- The team is not familiar with the style (readability first)
- The function has many optional or keyword-only parameters

---

## 📊 Visual Diagram

```
 normal : bill(0.05, 0.10, 200) ───────────────────────────► 189.0

 curried: bill(0.05) ──► fn_b ──(0.10)──► fn_c ──(200)──► 189.0
              │                │
        saves tax=0.05   saves tax + discount
        (closure)        (closure)

 partial: partial(bill, 0.05, 0.10) ──(200)──► 189.0   (one step)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Currying | f(a,b,c) → f(a)(b)(c) | एक-एक argument की chain |
| Partial application | Fix some arguments now, rest later | कुछ arguments पहले fix करना |
| Arity | Number of arguments a function takes | arguments की संख्या |
| Closure | Inner function remembering outer values | बाहरी values याद रखने वाला function |
| `functools.partial` | Standard tool to pre-fill arguments | arguments पहले से भरने वाला tool |
| Specialisation | Making a general function specific | सामान्य function को खास बनाना |

---

## ⚡ 3-Line Summary
English: Currying converts a multi-argument function into a chain of one-argument functions built from closures. Python has no automatic curry, so use nested functions, `partial` or a decorator. It helps create reusable, pre-configured functions.
Hindi: Currying कई arguments वाले function को एक-एक argument वाले functions की chain बनाता है, जो closures से बनती है। Python में automatic curry नहीं है, इसलिए nested functions, `partial` या decorator इस्तेमाल करें। यह पहले से configured, दोबारा इस्तेमाल होने वाले functions बनाने में मदद करता है।

---

## ➡️ Next Topic
**136. Iterators — Complete Guide** — move from functions to lazy sequences and learn how `for` loops really work.
