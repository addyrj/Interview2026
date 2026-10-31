---

# 045. *args + **kwargs
# हिंदी में: *args + **kwargs (अनगिनत arguments)

---

## 🔵 Simple Definition (English)
`*args` collects any extra positional arguments into a tuple. `**kwargs` collects any extra keyword arguments into a dict. They let a function accept a flexible number of inputs. The names `args` and `kwargs` are only convention; the stars do the work.

## 🔵 सरल परिभाषा (Hindi)
`*args` extra positional arguments को एक tuple में जमा करता है। `**kwargs` extra keyword arguments को एक dict में जमा करता है। इनसे function को कितने भी inputs मिल सकते हैं। `args` और `kwargs` सिर्फ convention हैं; असली काम stars का है।

---

## 🔴 Problem it Solves
A function like `add(a, b)` fails when you want to add 5 numbers. Wrappers and decorators must forward whatever arguments the wrapped function takes, without knowing them. `*args/**kwargs` solves both: variadic functions (`print`, `max`) and "pass-through" code (decorators, middleware, subclass `__init__`).

## 🔴 यह क्यों बना? (Hindi)
`add(a, b)` तब fail होता है जब 5 numbers जोड़ने हों। Wrappers और decorators को बिना जाने सारे arguments आगे forward करने होते हैं। `*args/**kwargs` दोनों हल करता है: variable arguments वाले functions (`print`, `max`) और pass-through code (decorators, middleware, subclass का `__init__`)।

---

## 🟢 How it Works — Step by Step

```
DEFINING (packing):
Step 1 → def f(a, *args, **kwargs)
Step 2 → Named params take their values first
Step 3 → Leftover positional values → tuple  args
Step 4 → Leftover keyword values    → dict   kwargs

CALLING (unpacking):
Step 5 → f(*my_list)   spreads a list/tuple as positional args
Step 6 → f(**my_dict)  spreads a dict as keyword args
```

## 🟢 कैसे काम करता है? (Hindi)
```
Define करते समय (packing):
  बाकी बचे positional values → tuple (args)
  बाकी बचे keyword values   → dict (kwargs)

Call करते समय (unpacking):
  f(*list)  → list को अलग positional args बना देता है
  f(**dict) → dict को keyword args बना देता है
```

---

## 🟡 Real World Example
A FastAPI logging decorator wraps any endpoint: it must accept whatever parameters each endpoint has, so it uses `*args, **kwargs` and forwards them. Razorpay SDK style: `client.create(amount=500, currency="INR", **extra_options)`. In AI apps, `llm.chat(messages, **model_params)` passes temperature, max_tokens and so on without listing them.

## 🟡 Real Example Hindi mein
FastAPI के logging decorator को हर endpoint के अलग parameters लेने होते हैं, इसलिए वह `*args, **kwargs` लेकर आगे forward करता है। Razorpay SDK style: `client.create(amount=500, currency="INR", **extra_options)`. AI apps में `llm.chat(messages, **model_params)` से temperature, max_tokens बिना list किए पास होते हैं।

---

## 💻 Code Example — Basic
```python
# Basic *args and **kwargs - every line commented
from typing import Any, Dict, Tuple  # type hints


def total(*args: int) -> int:  # *args packs positional values into a tuple
    print(args, type(args))  # show what we received
    return sum(args)  # add them all


print(total(1, 2, 3))  # three arguments
# Output:
# (1, 2, 3) <class 'tuple'>
# 6
print(total())  # zero arguments also fine
# Output:
# () <class 'tuple'>
# 0


def show(**kwargs: Any) -> None:  # **kwargs packs keyword values into a dict
    print(kwargs, type(kwargs))  # show the dict
    for key, value in kwargs.items():  # loop over key/value pairs
        print(f"{key} = {value}")  # print each one


show(name="Asha", age=25)  # keyword arguments only
# Output:
# {'name': 'Asha', 'age': 25} <class 'dict'>
# name = Asha
# age = 25


def mixed(a: int, b: int, *args: int, **kwargs: Any) -> Tuple[int, Tuple[int, ...], Dict[str, Any]]:
    return a + b, args, kwargs  # return all three parts


print(mixed(1, 2, 3, 4, x=10))  # a=1, b=2, args=(3,4), kwargs={'x':10}
# Output: (3, (3, 4), {'x': 10})

# Unpacking when CALLING a function
nums = [1, 2, 3]  # a list
print(total(*nums))  # * spreads the list as separate arguments
# Output:
# (1, 2, 3) <class 'tuple'>
# 6
config = {"name": "Ravi", "age": 30}  # a dict
show(**config)  # ** spreads the dict as keyword arguments
# Output:
# {'name': 'Ravi', 'age': 30} <class 'dict'>
# name = Ravi
# age = 30

# Merge lists and dicts with the same operators
print([*nums, 4, 5])  # Output: [1, 2, 3, 4, 5]
print({**config, "city": "Pune"})  # Output: {'name': 'Ravi', 'age': 30, 'city': 'Pune'}
```

## 💻 Code Example — Advanced
```python
# Production style: decorator forwarding, subclass init, keyword-only after *args
import functools  # wraps keeps the original function's name
import time  # to measure duration
from typing import Any, Callable, TypeVar  # type hints

F = TypeVar("F", bound=Callable[..., Any])  # any callable type


def timed(func: F) -> F:  # decorator that works for ANY signature
    @functools.wraps(func)  # copy __name__ and __doc__
    def wrapper(*args: Any, **kwargs: Any) -> Any:  # accept everything
        start: float = time.perf_counter()  # start the clock
        result = func(*args, **kwargs)  # forward all arguments unchanged
        elapsed_ms: float = (time.perf_counter() - start) * 1000  # milliseconds
        print(f"{func.__name__} took {'fast' if elapsed_ms < 1000 else 'slow'}")  # stable output
        return result  # give back the original result
    return wrapper  # type: ignore[return-value]


@timed  # apply the decorator
def create_order(user: str, *items: str, express: bool = False, **meta: Any) -> str:
    return f"{user}: {items}, express={express}, meta={meta}"  # build summary


print(create_order("asha", "pizza", "coke", express=True, coupon="NEW50"))
# Output:
# create_order took fast
# asha: ('pizza', 'coke'), express=True, meta={'coupon': 'NEW50'}


class Base:  # parent class
    def __init__(self, name: str, **kwargs: Any) -> None:
        self.name: str = name  # store the name
        self.extra: dict[str, Any] = kwargs  # keep unknown options


class Child(Base):  # subclass adds one field
    def __init__(self, *args: Any, level: int = 1, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)  # forward the rest to the parent
        self.level: int = level  # own field


c = Child("bot", level=3, theme="dark")  # mixes parent and child arguments
print(c.name, c.level, c.extra)  # Output: bot 3 {'theme': 'dark'}


def call_llm(prompt: str, **params: Any) -> dict[str, Any]:  # pass-through settings
    defaults: dict[str, Any] = {"temperature": 0.7, "max_tokens": 100}  # defaults
    return {"prompt": prompt, **defaults, **params}  # later dict wins on conflict


print(call_llm("hi", temperature=0.0))  # override one setting
# Output: {'prompt': 'hi', 'temperature': 0.0, 'max_tokens': 100}


def strict_fn(*args: int, scale: int = 1) -> list[int]:  # keyword-only after *args
    return [a * scale for a in args]  # scale must be passed by name


print(strict_fn(1, 2, 3, scale=10))  # Output: [10, 20, 30]
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
def total(*args):                  # rest -> tuple
    return sum(args)

def show(**kwargs):                # no JS equivalent for keyword args
    print(kwargs)

total(*[1, 2, 3])                  # spread a list
show(**{"a": 1})                   # spread a dict
```

```javascript
// JavaScript
function total(...args) {          // rest parameters -> real Array
  return args.reduce((a, b) => a + b, 0);
}
function show(options = {}) {      // JS emulates kwargs with an object
  console.log(options);
}
total(...[1, 2, 3]);               // spread an array
show({ ...{ a: 1 }, b: 2 });       // spread an object
```

Key differences: Python `*args` ~ JS `...args` (but a tuple, not an array). JS has no true keyword arguments; it passes one options object. Python `**kwargs` is first-class, with real keyword syntax at the call site.

---

## 🟠 FastAPI Connection
Every FastAPI decorator, dependency wrapper and middleware relies on `*args, **kwargs`. Custom decorators on endpoints must forward them, and `functools.wraps` must be used or FastAPI cannot read the endpoint's signature.

```python
# FastAPI: logging decorator on an endpoint (needs: pip install fastapi)
import functools  # wraps keeps the signature visible to FastAPI
from typing import Any, Awaitable, Callable  # type hints
from fastapi import FastAPI  # the framework

app: FastAPI = FastAPI()  # create app


def log_calls(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    @functools.wraps(func)  # IMPORTANT: preserves parameters for FastAPI
    async def wrapper(*args: Any, **kwargs: Any) -> Any:  # forward everything
        print("calling", func.__name__, kwargs)  # log the call
        return await func(*args, **kwargs)  # run the real endpoint
    return wrapper  # return decorated function


@app.get("/users/{user_id}")  # route
@log_calls  # our decorator sits under the route decorator
async def get_user(user_id: int) -> dict[str, int]:  # real endpoint
    return {"id": user_id}  # response
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Wrong parameter order
```python
# Wrong - SyntaxError (kwargs must be last, *args before it):
# def f(**kwargs, *args): ...

# Correct order: normal, *args, keyword-only, **kwargs
def f(a, b=2, *args, key=None, **kwargs):
    return a, b, args, key, kwargs
```

❌ Mistake 2: Forgetting to unpack when forwarding
```python
def inner(a, b):
    return a + b

def outer(*args):
    # Wrong - passes ONE tuple argument -> TypeError (missing b):
    # return inner(args)

    # Correct - spread the tuple:
    return inner(*args)

print(outer(1, 2))   # 3
```

❌ Mistake 3: Mutating the shared kwargs dict / losing type safety
```python
def f(**kwargs):
    kwargs["x"] = 1      # fine: kwargs is a NEW dict for each call
    return kwargs

opts = {"a": 0}
print(f(**opts), opts)   # {'a': 0, 'x': 1} {'a': 0}  - original untouched

# But overusing **kwargs hides the real API; prefer explicit parameters
# and document/validate (Pydantic) the options you accept.
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
def f(*args, **kwargs):
    return args, kwargs

print(f(1, 2, a=3))
print(f(*"ab", **{"x": 1}))
print(f([1, 2]), f(*[1, 2]))

d1 = {"a": 1, "b": 2}
d2 = {"b": 3}
try:
    f(**d1, **d2)
except TypeError as e:
    print("TypeError:", e)
```

**Answer**:
```
((1, 2), {'a': 3})
(('a', 'b'), {'x': 1})
(([1, 2],), {}) ((1, 2), {})
TypeError: __main__.f() got multiple values for keyword argument 'b'
```
`f([1, 2])` passes ONE list argument (so `args` has one element); `f(*[1, 2])` spreads it into two. Duplicate keys when unpacking two dicts in a call raise `TypeError`, whereas merging with `{**d1, **d2}` just lets the later one win.

---

## ⚫ Interview Questions + Answers

Q1: What are `*args` and `**kwargs`?
A1: `*args` gathers extra positional arguments into a tuple; `**kwargs` gathers extra keyword arguments into a dict. The star syntax matters, the names are convention.

Q2: What is the order of parameters in a function definition?
A2: Positional/normal parameters, then defaults, then `*args`, then keyword-only parameters, then `**kwargs`. (Positional-only `/` comes before the normal ones.)

Q3: What does `*` mean in a function call versus a definition?
A3: In a definition it packs (collects) values. In a call it unpacks (spreads) an iterable into separate positional arguments. `**` does the same for dicts and keyword arguments.

Q4: Why use `functools.wraps` in decorators?
A4: Without it the wrapper replaces the function's `__name__`, docstring and signature. Frameworks like FastAPI read the signature to build dependencies and docs, so it would break.

Q5: When should you avoid `**kwargs`?
A5: In public APIs. It hides valid parameter names, kills IDE autocomplete and type checking, and silently swallows typos. Prefer explicit parameters; use `**kwargs` for forwarding and extension points.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Writing decorators, wrappers and middleware
- Forwarding options to another function or library
- Functions that accept any number of similar values (`max`, `print`)

❌ Avoid when:
- A fixed, known set of parameters exists (list them explicitly)
- You want IDE help and type checking
- A single list or dict parameter would be clearer

---

## 📊 Visual Diagram

```
 call:  f(1, 2, 3, x=10, y=20)
              │          │
   def f(a, *args, **kwargs)
          │    │       │
          1  (2, 3)  {'x': 10, 'y': 20}
          a   args      kwargs
          (tuple)       (dict)

 forward:  g(*args, **kwargs)   ← spreads them again
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| *args | Extra positional args as tuple | extra positional values का tuple |
| **kwargs | Extra keyword args as dict | extra keyword values का dict |
| Packing | Collecting values into one object | values को एक में जमा करना |
| Unpacking | Spreading values into arguments | values को arguments में फैलाना |
| Variadic | Accepts a variable count | कितने भी arguments लेने वाला |
| Decorator | Function that wraps a function | function को wrap करने वाला function |

---

## ⚡ 3-Line Summary
English: `*args` packs extra positional arguments into a tuple and `**kwargs` packs extra keyword arguments into a dict. In calls, `*` and `**` unpack iterables and dicts. They are essential for decorators and forwarding, but explicit parameters are better for public APIs.
Hindi: `*args` extra positional arguments का tuple और `**kwargs` extra keyword arguments का dict बनाता है। Call में `*` और `**` unpack करते हैं। Decorators और forwarding के लिए ज़रूरी हैं, पर public API में explicit parameters बेहतर हैं।

---

## ➡️ Next Topic
**046. Default Parameters** — give parameters fallback values, and avoid the famous mutable default trap.
