---

# 134. Higher Order Functions
# हिंदी में: Higher Order Functions (ऐसे functions जो दूसरे functions लेते या लौटाते हैं)

---

## 🔵 Simple Definition (English)
A higher order function (HOF) is a function that takes another function as an argument, returns a function, or both. This works because in Python functions are normal objects, just like numbers or strings. `map`, `filter`, `sorted(key=...)` and decorators are all HOFs.

## 🔵 सरल परिभाषा (Hindi)
Higher order function (HOF) वह function है जो किसी दूसरे function को argument में लेता है, function को return करता है, या दोनों करता है। यह इसलिए संभव है क्योंकि Python में function एक सामान्य object है, बिल्कुल number या string की तरह। `map`, `filter`, `sorted(key=...)` और decorators सब HOF हैं।

---

## 🔴 Problem it Solves
Without HOFs you copy the same loop again and again, changing only one small rule inside it (filter by price, filter by city, sort by rating). HOFs let you write the loop once and pass the changing rule as a function. This removes duplication and makes code easy to test.

## 🔴 यह क्यों बना? (Hindi)
HOF के बिना एक ही loop बार-बार copy करना पड़ता है और सिर्फ अंदर का छोटा rule बदलता है (price से filter, city से filter, rating से sort)। HOF में loop एक बार लिखते हैं और बदलने वाला rule function के रूप में pass करते हैं। इससे duplicate code कम होता है और testing आसान होती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → A function is an object, so a name can point to it: f = len
Step 2 → You pass that object as an argument: apply(f, data)
Step 3 → Inside, the HOF calls it: f(data)
Step 4 → Or the HOF builds an inner function and returns it (closure)
Step 5 → The caller stores the returned function and calls it later
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → function एक object है, इसलिए कोई भी नाम उसे point कर सकता है: f = len
Step 2 → उस object को argument की तरह pass करते हैं: apply(f, data)
Step 3 → HOF के अंदर उसे call करते हैं: f(data)
Step 4 → या HOF अंदर एक function बनाकर return करता है (closure)
Step 5 → caller returned function को रखता है और बाद में call करता है
```

---

## 🟡 Real World Example
Swiggy's backend filters restaurants by many rules: veg only, rating above 4, delivery under 30 minutes. One function `apply_filters(restaurants, rule)` takes the rule as a function. Razorpay retries failed API calls with a `retry(times)` HOF that wraps any payment function. A FastAPI service sorts orders with `sorted(orders, key=lambda o: o.total)`.

## 🟡 Real Example Hindi mein
Swiggy backend restaurants को कई rules से filter करता है: सिर्फ veg, rating 4 से ऊपर, delivery 30 मिनट से कम। एक ही `apply_filters(restaurants, rule)` function rule को function की तरह लेता है। Razorpay का `retry(times)` HOF किसी भी payment function को wrap करके fail होने पर दोबारा try करता है। FastAPI service में orders `sorted(orders, key=lambda o: o.total)` से sort होते हैं।

---

## 💻 Code Example — Basic
```python
# Basic higher order functions - every line commented
from typing import Callable, List  # type hints for function arguments


def apply_twice(func: Callable[[int], int], value: int) -> int:  # takes a function
    return func(func(value))  # call the given function two times


def add_five(n: int) -> int:  # a normal small function
    return n + 5  # add five


print(apply_twice(add_five, 10))  # pass the function itself, no ()
# Output: 20

print(apply_twice(lambda n: n * 3, 2))  # lambda is an inline function
# Output: 18


def make_multiplier(factor: int) -> Callable[[int], int]:  # returns a function
    def multiply(n: int) -> int:  # inner function remembers factor
        return n * factor  # use the remembered value
    return multiply  # return the function, do not call it


double = make_multiplier(2)  # double is now a function
triple = make_multiplier(3)  # triple is another function
print(double(7), triple(7))  # call both
# Output: 14 21

nums: List[int] = [1, 2, 3, 4, 5, 6]  # sample data
print(list(map(lambda n: n * n, nums)))  # map applies a function to each item
# Output: [1, 4, 9, 16, 25, 36]
print(list(filter(lambda n: n % 2 == 0, nums)))  # filter keeps items where True
# Output: [2, 4, 6]

words: List[str] = ["pear", "fig", "banana", "kiwi"]  # sample words
print(sorted(words, key=len))  # sorted is a HOF, key is the function
# Output: ['fig', 'pear', 'kiwi', 'banana']
print(max(words, key=len))  # max is also a HOF
# Output: banana

print(callable(add_five), callable(5))  # check if something can be called
# Output: True False
```

## 💻 Code Example — Advanced
```python
# Production style: filter pipeline, retry HOF, timing HOF (all typed)
import time  # for timing and sleeping
from functools import reduce, wraps  # reduce folds a list, wraps keeps metadata
from typing import Any, Callable, Dict, Iterable, List, TypeVar  # generic types

T = TypeVar("T")  # generic item type
Predicate = Callable[[Dict[str, Any]], bool]  # alias: dict in, bool out

restaurants: List[Dict[str, Any]] = [  # fake Swiggy data
    {"name": "Meghana", "rating": 4.5, "veg": False, "eta": 25},
    {"name": "Saravana", "rating": 4.2, "veg": True, "eta": 35},
    {"name": "Truffles", "rating": 4.7, "veg": False, "eta": 20},
    {"name": "Udupi", "rating": 3.9, "veg": True, "eta": 15},
]


def rating_above(limit: float) -> Predicate:  # HOF that RETURNS a rule
    return lambda r: r["rating"] >= limit  # rule remembers limit


def faster_than(minutes: int) -> Predicate:  # another rule factory
    return lambda r: r["eta"] <= minutes  # compare eta


def all_of(*rules: Predicate) -> Predicate:  # HOF that takes and returns rules
    return lambda r: all(rule(r) for rule in rules)  # every rule must pass


def apply_filters(items: Iterable[Dict[str, Any]], rule: Predicate) -> List[str]:
    return [i["name"] for i in items if rule(i)]  # keep names that pass


print(apply_filters(restaurants, rating_above(4.3)))  # single rule
# Output: ['Meghana', 'Truffles']
print(apply_filters(restaurants, all_of(rating_above(4.0), faster_than(30))))
# Output: ['Meghana', 'Truffles']


def retry(times: int) -> Callable[[Callable[..., T]], Callable[..., T]]:  # decorator factory
    def decorator(func: Callable[..., T]) -> Callable[..., T]:  # takes the function
        @wraps(func)  # keep name and docstring of func
        def wrapper(*args: Any, **kwargs: Any) -> T:  # new behaviour
            last_error: Exception | None = None  # remember last failure
            for attempt in range(1, times + 1):  # try up to `times`
                try:  # attempt the call
                    return func(*args, **kwargs)  # success returns immediately
                except ConnectionError as exc:  # only retry network errors
                    last_error = exc  # store it
                    print(f"attempt {attempt} failed")  # log
            raise RuntimeError("all retries failed") from last_error  # give up
        return wrapper  # return the wrapped function
    return decorator  # return the decorator


calls: Dict[str, int] = {"n": 0}  # counter to fake a flaky service


@retry(times=3)  # HOF used as decorator
def charge_card(amount: int) -> str:  # flaky payment function
    calls["n"] += 1  # count calls
    if calls["n"] < 3:  # fail the first two times
        raise ConnectionError("gateway down")  # simulate network error
    return f"charged {amount}"  # third call works


print(charge_card(500))  # retry happens inside
# Output:
# attempt 1 failed
# attempt 2 failed
# charged 500
print(charge_card.__name__)  # wraps preserved the name
# Output: charge_card


def timed(func: Callable[..., T]) -> Callable[..., T]:  # simple timing HOF
    @wraps(func)  # keep metadata
    def wrapper(*args: Any, **kwargs: Any) -> T:  # wrapper
        start: float = time.perf_counter()  # start clock
        result: T = func(*args, **kwargs)  # run the real function
        print(f"{func.__name__} took {time.perf_counter() - start < 1}")  # fast check
        return result  # pass result through
    return wrapper  # return wrapper


@timed  # decorate
def total(xs: List[int]) -> int:  # function to time
    return reduce(lambda a, b: a + b, xs, 0)  # fold list into a sum


print(total([1, 2, 3, 4]))  # run
# Output:
# total took True
# 10
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript developers already know HOFs (`map`, `filter`, `reduce`, callbacks). The idea is identical. Python uses `map()`/`filter()` as separate functions and prefers list comprehensions.

```python
# Python way
nums = [1, 2, 3, 4]
print(list(map(lambda n: n * 2, nums)))        # [2, 4, 6, 8]
print([n * 2 for n in nums])                   # comprehension (preferred)
print(sorted(["bb", "a"], key=len))            # ['a', 'bb']
def make_adder(x):                             # returns a function
    return lambda y: x + y
print(make_adder(3)(4))                        # 7
```
```javascript
// JavaScript way
const nums = [1, 2, 3, 4];
console.log(nums.map(n => n * 2));             // [2, 4, 6, 8]
console.log(["bb", "a"].sort((a, b) => a.length - b.length));  // comparator, not key
const makeAdder = x => y => x + y;             // returns a function
console.log(makeAdder(3)(4));                  // 7
```

Key differences: in JS `map` is a method on arrays; in Python it is a global function returning a lazy iterator. Python `sorted` takes a `key` function, JS `sort` takes a two-argument comparator. Python lambdas can hold only one expression.

---

## 🟠 FastAPI Connection
FastAPI itself is full of HOFs. `Depends(get_db)` receives a function. Route decorators like `@app.get("/x")` are HOFs that register your function. You can build dependency factories that return a function configured with a parameter.

```python
# FastAPI: dependency factory (a HOF that returns a dependency)
from typing import Callable, Dict  # type hints
from fastapi import Depends, FastAPI, Header, HTTPException  # core imports
from fastapi.testclient import TestClient  # to test without a server

app: FastAPI = FastAPI()  # create app


def require_role(role: str) -> Callable[..., str]:  # HOF: returns a dependency
    def checker(x_role: str = Header(default="guest")) -> str:  # reads header
        if x_role != role:  # compare with required role
            raise HTTPException(status_code=403, detail="forbidden")  # block
        return x_role  # allow
    return checker  # return the dependency function


@app.get("/admin")  # route
def admin(role: str = Depends(require_role("admin"))) -> Dict[str, str]:  # inject
    return {"role": role}  # response


client = TestClient(app)  # test client
print(client.get("/admin", headers={"x-role": "admin"}).json())  # allowed
# Output: {'role': 'admin'}
print(client.get("/admin").status_code)  # default guest
# Output: 403
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling the function instead of passing it
```python
# Wrong - add_five(3) runs now and passes the result 8
# sorted(words, key=len(words))   # TypeError

# Right - pass the function object without ()
print(sorted(["bb", "a"], key=len))   # ['a', 'bb']
```

❌ Mistake 2: Late binding in lambdas created in a loop
```python
# Wrong - all lambdas see the final value of i
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])           # [2, 2, 2]

# Right - bind the current value with a default argument
funcs = [lambda i=i: i for i in range(3)]
print([f() for f in funcs])           # [0, 1, 2]
```

❌ Mistake 3: Forgetting `functools.wraps` in a wrapper
```python
# Wrong - the wrapper hides the real name (breaks logs, FastAPI docs)
# def deco(f):
#     def wrapper(*a, **k): return f(*a, **k)
#     return wrapper

# Right - use @wraps(f) on the wrapper
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
def make():
    return [lambda x: x * i for i in range(3)]

print([f(10) for f in make()])
print(list(filter(None, [0, 1, "", "a", None, [], [0]])))
print(sorted([3, -5, 1], key=abs))
```

**Answer**:
```
[20, 20, 20]
[1, 'a', [0]]
[1, 3, -5]
```
The lambdas look up `i` when called, not when created, so all see `i = 2` (late binding). `filter(None, ...)` keeps only truthy items. `sorted(key=abs)` sorts by absolute value but returns the original numbers.

---

## ⚫ Interview Questions + Answers

Q1: What makes a function "higher order"?
A1: It either accepts a function as a parameter or returns a function (or both). Python allows this because functions are first-class objects.

Q2: Are decorators higher order functions?
A2: Yes. A decorator takes a function and returns a new function. `@retry(3)` is a HOF returning a HOF.

Q3: `map`/`filter` or list comprehension?
A3: Comprehensions are usually clearer and faster for simple cases. Use `map` when you already have a named function, like `map(str.strip, lines)`.

Q4: What does `reduce` do and where is it?
A4: It folds a sequence into one value using a two-argument function. It lives in `functools`, not builtins, since Python 3.

Q5: What is the difference between `sorted(key=f)` and a JS comparator?
A5: `key` computes one value per item once, then compares values. A comparator compares two items each time. Python's way is simpler and faster; use `functools.cmp_to_key` if you truly need a comparator.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- The loop is the same but one rule changes (filter, sort, transform)
- You need to wrap behaviour: retry, logging, timing, caching
- You want configurable factories (role checker, validators)

❌ Avoid when:
- A simple comprehension or loop is clearer
- The lambda becomes long or nested (write a named `def`)
- Deeply stacked HOFs make debugging hard

---

## 📊 Visual Diagram

```
 HOF type 1: takes a function            HOF type 2: returns a function
 ───────────────────────────             ───────────────────────────────
 apply(rule, data)                       make_multiplier(3)
        │                                       │
   ┌────▼─────┐                           ┌─────▼──────┐
   │ rule(x)  │ called inside             │ multiply() │ closure keeps factor=3
   └──────────┘                           └─────┬──────┘
                                                │ returned
                                          triple = ...  ;  triple(5) → 15
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| First-class function | Function treated like any value | function भी एक सामान्य value |
| Callback | Function passed to be called later | बाद में call होने वाला function |
| Predicate | Function that returns True/False | True/False देने वाला function |
| Closure | Inner function remembering outer variables | बाहरी variables याद रखने वाला inner function |
| Decorator | HOF that wraps another function | function को wrap करने वाला HOF |
| Lambda | Small anonymous function | छोटा बिना नाम का function |

---

## ⚡ 3-Line Summary
English: A higher order function takes a function or returns one. It lets you keep the loop fixed and change only the rule. `map`, `filter`, `sorted(key=)`, decorators and `Depends` are all HOFs.
Hindi: Higher order function किसी function को लेता है या return करता है। इससे loop वही रहता है और सिर्फ rule बदलता है। `map`, `filter`, `sorted(key=)`, decorators और `Depends` सब HOF हैं।

---

## ➡️ Next Topic
**135. Currying in Python** — turn a many-argument function into a chain of one-argument functions, built on the same closure idea.
