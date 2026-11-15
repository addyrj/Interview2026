---

# 119. reduce() Function
# हिंदी में: reduce() Function (पूरी list को एक value में समेटना)

---

## 🔵 Simple Definition (English)
`functools.reduce(func, iterable, initial)` combines all items of an iterable into ONE value by applying a two-argument function from left to right: `reduce(f, [a, b, c])` is `f(f(a, b), c)`. It is also called a "fold". Unlike `map` and `filter`, it is not a built-in: you import it from `functools`.

## 🔵 सरल परिभाषा (Hindi)
`functools.reduce(func, iterable, initial)` iterable के सारे items को दो-argument वाले function से बाएं से दाएं जोड़कर एक value बनाता है: `reduce(f, [a, b, c])` यानी `f(f(a, b), c)`। इसे "fold" भी कहते हैं। `map` और `filter` के उलट यह built-in नहीं है: इसे `functools` से import करना पड़ता है।

---

## 🔴 Problem it Solves
Many tasks mean "walk through items and keep a running result": sum, product, maximum, merge many dicts into one, compose many functions, build a nested value from a path. The manual way is an accumulator variable plus a loop. `reduce` expresses the pattern in one line and works with any combining function. In modern Python, though, `sum`, `max`, `min`, `math.prod`, `any`, `all` and `"".join` cover the common cases faster and more clearly, so `reduce` is for what is left (merging, composing, custom folds).

## 🔴 यह क्यों बना? (Hindi)
कई काम का मतलब होता है "items पर चलो और running result रखो": sum, product, maximum, कई dicts को एक में merge करना, कई functions को जोड़ना, path से nested value निकालना। हाथ से करने पर accumulator variable और loop चाहिए। `reduce` यह pattern एक line में कहता है और किसी भी combining function के साथ चलता है। आधुनिक Python में हालांकि `sum`, `max`, `min`, `math.prod`, `any`, `all` और `"".join` आम cases ज्यादा तेज और साफ संभालते हैं, इसलिए `reduce` बचे हुए कामों (merge, compose, custom fold) के लिए है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → reduce(f, [1, 2, 3, 4], 0)   (0 is the optional initial value)
Step 2 → acc = 0  (the initial value; without it, acc = first item)
Step 3 → acc = f(acc, 1)  -> f(0, 1)
Step 4 → acc = f(acc, 2)  -> f(1, 2)
Step 5 → acc = f(acc, 3), then f(acc, 4)
Step 6 → return the final acc. Empty iterable + no initial -> TypeError

With f = add:   ((((0+1)+2)+3)+4) = 10
reduce is EAGER (computes at once) and returns a single value, not an iterator
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → reduce(f, [1, 2, 3, 4], 0)   (0 optional initial value है)
Step 2 → acc = 0  (initial value; इसके बिना acc = पहला item)
Step 3 → acc = f(acc, 1)  -> f(0, 1)
Step 4 → acc = f(acc, 2)  -> f(1, 2)
Step 5 → acc = f(acc, 3), फिर f(acc, 4)
Step 6 → अंतिम acc लौटाओ। खाली iterable + initial नहीं -> TypeError

f = add के साथ:   ((((0+1)+2)+3)+4) = 10
reduce EAGER है (तुरंत compute करता है) और एक value लौटाता है, iterator नहीं
```

---

## 🟡 Real World Example
An order service totals the cart: `reduce(lambda total, item: total + item.price * item.qty, cart, 0)`. A config loader merges layered settings (defaults, then file, then environment) into one dict with `reduce(merge, layers)`. A middleware stack is built by folding handlers: each middleware wraps the previous one. A report finds a deeply nested field from a path like `"user.address.city"`.

## 🟡 Real Example Hindi mein
Order service cart का total `reduce(lambda total, item: total + item.price * item.qty, cart, 0)` से निकालती है। Config loader परतदार settings (defaults, फिर file, फिर environment) को `reduce(merge, layers)` से एक dict में merge करता है। Middleware stack handlers को fold करके बनता है: हर middleware पिछले को wrap करता है। Report `"user.address.city"` जैसे path से गहरे nested field तक पहुंचता है।

---

## 💻 Code Example — Basic
```python
# Basic reduce() examples
from functools import reduce                      # reduce lives in functools
from operator import add, mul                     # function versions of + and *

nums: list[int] = [1, 2, 3, 4]                    # sample numbers

print(reduce(lambda a, b: a + b, nums))           # ((1+2)+3)+4 = 10
print(reduce(add, nums))                          # operator.add is faster than a lambda
print(reduce(mul, nums))                          # 1*2*3*4 = 24
print(reduce(lambda a, b: a if a > b else b, nums))   # maximum (but max() is simpler)

print(reduce(add, nums, 100))                     # initial value 100 -> 110
print(reduce(add, [], 0))                         # empty list + initial -> returns initial
try:                                              # empty list and NO initial value
    reduce(add, [])                               # nothing to start from
except TypeError as e:                            # catch it
    print("TypeError:", e)

words: list[str] = ["py", "thon", "!"]            # strings
print(reduce(add, words))                         # string concatenation (use "".join instead)

# Trace the steps with a printing function
def trace(acc: int, x: int) -> int:               # shows each step
    print(f"acc={acc}, x={x}")
    return acc + x

print(reduce(trace, [1, 2, 3]))                   # watch the accumulator grow

print(sum(nums), max(nums))                       # built-ins beat reduce for these jobs

# Output:
# 10
# 10
# 24
# 4
# 110
# 0
# TypeError: reduce() of empty iterable with no initial value
# python!
# acc=1, x=2
# acc=3, x=3
# 6
# 10 4
```

## 💻 Code Example — Advanced
```python
# Production style: merge config layers, compose functions, nested lookup, group-by fold
from functools import reduce                      # fold
from typing import Any, Callable, Iterable, TypeVar

T = TypeVar("T")


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Merge two dicts recursively; `override` wins. Returns a NEW dict."""
    result: dict[str, Any] = dict(base)           # copy so inputs are not mutated
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)   # merge nested dicts
        else:
            result[key] = value                   # replace/insert
    return result


defaults: dict[str, Any] = {"db": {"host": "localhost", "port": 5432}, "debug": False}
file_cfg: dict[str, Any] = {"db": {"host": "db.internal"}}
env_cfg: dict[str, Any] = {"debug": True, "db": {"port": 6543}}

config = reduce(deep_merge, [defaults, file_cfg, env_cfg])   # layers applied left to right
print(config)                                     # later layers win
print(defaults["db"]["host"])                     # unchanged: no mutation


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """compose(f, g, h)(x) == h(g(f(x)))  (left to right)."""
    return reduce(lambda f, g: lambda x: g(f(x)), funcs, lambda x: x)   # identity as initial


clean = compose(str.strip, str.lower, lambda s: s.replace(" ", "-"))
print(clean("  Hello Big World "))                # hello-big-world


def get_path(data: dict[str, Any], path: str, default: Any = None) -> Any:
    """get_path(d, 'user.address.city') with a safe default."""
    try:
        return reduce(lambda node, key: node[key], path.split("."), data)
    except (KeyError, TypeError):                 # missing key or not a dict
        return default


user = {"user": {"address": {"city": "Pune"}}}
print(get_path(user, "user.address.city"))        # Pune
print(get_path(user, "user.phone.number", "n/a")) # n/a


def group_by(items: Iterable[T], key: Callable[[T], str]) -> dict[str, list[T]]:
    """Fold items into a dict of lists."""
    def step(acc: dict[str, list[T]], item: T) -> dict[str, list[T]]:
        acc.setdefault(key(item), []).append(item)   # mutate the accumulator
        return acc                                   # and return it for the next step
    return reduce(step, items, {})


print(group_by(["apple", "avocado", "banana", "blueberry", "cherry"], lambda s: s[0]))

# Output:
# {'db': {'host': 'db.internal', 'port': 6543}, 'debug': True}
# localhost
# hello-big-world
# Pune
# n/a
# {'a': ['apple', 'avocado'], 'b': ['banana', 'blueberry'], 'c': ['cherry']}
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Fold | `reduce(f, items, init)` (import from `functools`) | `items.reduce(f, init)` |
| Callback signature | `f(acc, item)` | `f(acc, item, index, array)` |
| Initial value | 3rd argument | 2nd argument |
| Empty without initial | `TypeError` | `TypeError` |
| Usage style | rare, use `sum`/`max`/`join` first | very common |

```python
# Python way
from functools import reduce
nums: list[int] = [1, 2, 3, 4]
print(reduce(lambda acc, x: acc + x, nums, 0))   # 10
print(sum(nums))                                  # 10 - preferred
```
```javascript
// JavaScript way
const nums = [1, 2, 3, 4];
console.log(nums.reduce((acc, x) => acc + x, 0));   // 10 - idiomatic in JS
// JS has no sum(); reduce is the standard tool, and is also used to build objects:
const counts = ["a", "b", "a"].reduce((m, k) => ({ ...m, [k]: (m[k] || 0) + 1 }), {});
console.log(counts);                                // { a: 2, b: 1 }
```

Key difference: in JavaScript `reduce` is everyday code because there are no `sum`, `max` for arrays or `Counter`. In Python the standard library has better tools (`sum`, `max`, `math.prod`, `Counter`, `"".join`), so `reduce` is used less and was even moved out of the built-ins in Python 3. Argument order also differs: Python's initial value is the LAST argument.

---

## 🟠 FastAPI Connection
`reduce` appears in FastAPI code mostly for merging layered settings, combining many optional filters into one rule, and folding permission checks. A classic: combine several SQLAlchemy conditions with `reduce(operator.and_, conditions)` (or the simpler `and_(*conditions)`).

```python
# FastAPI example - fold optional query filters into one rule, total the matches
from functools import reduce                      # fold
from operator import add                          # +
from typing import Callable                       # type hint
from fastapi import FastAPI                       # app
from fastapi.testclient import TestClient         # tests

app: FastAPI = FastAPI()                          # create app
ITEMS: list[dict] = [
    {"name": "pen", "price": 10, "color": "blue"},
    {"name": "book", "price": 250, "color": "red"},
    {"name": "bag", "price": 900, "color": "red"},
]
Rule = Callable[[dict], bool]                     # a filter rule


def both(r1: Rule, r2: Rule) -> Rule:             # combine two rules with AND
    return lambda item: r1(item) and r2(item)


@app.get("/items")                                # GET /items?color=red&max_price=500
def items(color: str | None = None, max_price: int | None = None) -> dict:
    rules: list[Rule] = [lambda i: True]          # start with "accept all"
    if color:
        rules.append(lambda i: i["color"] == color)
    if max_price is not None:
        rules.append(lambda i: i["price"] <= max_price)
    rule: Rule = reduce(both, rules)              # fold all rules into one
    found = [i for i in ITEMS if rule(i)]
    return {"items": [i["name"] for i in found],
            "total": reduce(add, (i["price"] for i in found), 0)}   # sum with an initial value


client: TestClient = TestClient(app)              # client
print(client.get("/items", params={"color": "red", "max_price": 500}).json())
print(client.get("/items").json())

# Output:
# {'items': ['book'], 'total': 250}
# {'items': ['pen', 'book', 'bag'], 'total': 1160}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting the initial value for possibly-empty input
✅ Correct: always pass an initial value when the iterable can be empty

```python
from functools import reduce
from operator import add
# Wrong
try:
    reduce(add, [])
except TypeError:
    print("crash on empty")        # crash on empty
# Right
print(reduce(add, [], 0))          # 0
```

❌ Mistake 2: Using `reduce` where a built-in is clearer and faster
✅ Correct: use `sum`, `max`, `min`, `math.prod`, `"".join`, `any`, `all`

```python
from functools import reduce
import math
nums = [1, 2, 3, 4]
# Wrong - verbose, slow for strings (quadratic)
print(reduce(lambda a, b: a * b, nums))   # 24
print(reduce(lambda a, b: a + b, ["a", "b", "c"]))   # abc
# Right
print(math.prod(nums))                    # 24
print("".join(["a", "b", "c"]))           # abc
```

❌ Mistake 3: Mixing up the argument order of the function (acc comes FIRST)
✅ Correct: `f(accumulator, item)`; matters for non-commutative operations

```python
from functools import reduce
# Wrong assumption: f(item, acc)
print(reduce(lambda x, y: x - y, [10, 2, 3]))      # ((10-2)-3) = 5
print(reduce(lambda acc, x: x - acc, [10, 2, 3]))  # item - acc: (2-10)=-8, (3-(-8)) = 11
# Right: write names so the order is obvious
print(reduce(lambda acc, x: acc - x, [10, 2, 3]))  # 5
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from functools import reduce

print(reduce(lambda a, b: a + b, [[1], [2], [3]]))
print(reduce(lambda a, b: a + [b], [1, 2, 3], []))
print(reduce(lambda a, b: a - b, [10, 2, 3], 100))
print(reduce(lambda a, b: b, [1, 2, 3]))
print(reduce(lambda a, b: a, ["x"], "init"))
```
Answer: `[1, 2, 3]`, `[1, 2, 3]`, `85`, `3`, `init`. The first adds lists (concatenation), the second builds a list by appending each item to the initial `[]`. The third computes `((100-10)-2)-3 = 85`. The fourth returns the last item because the function always returns `b`. The fifth returns the initial value: the function returns the accumulator and ignores the item. Also remember that a mutable initial value (like `[]`) is created once per call, which is fine here, but reusing the same list object across calls would share state.

---

## ⚫ Interview Questions + Answers

Q1: Why is `reduce` in `functools` and not a built-in?
A1: In Python 3, Guido van Rossum moved it out of the built-ins because most uses are clearer with an explicit loop or with `sum`, `max`, `min`, `any`, `all`. It is still available via `from functools import reduce`.

Q2: What does the initial value do?
A2: It is the starting accumulator and also the result for an empty iterable. Without it, the first item is the start and an empty iterable raises `TypeError`. It also decides the result type (e.g. `[]`, `{}`, `0`).

Q3: How do `reduce` and `itertools.accumulate` differ?
A3: `reduce` returns only the final value; `accumulate` is lazy and yields every intermediate value (running totals): `list(accumulate([1,2,3]))` is `[1, 3, 6]`.

Q4: Is `reduce` ever better than a loop?
A4: For short, well-known folds like merging dicts, composing functions or `operator.and_` over conditions, it is concise. Anything with branches or side effects is clearer as a `for` loop. Avoid `reduce(lambda a, b: a + b, strings)` because repeated concatenation is O(n^2); use `"".join`.

Q5: Does `reduce` work on a parallel/associative basis?
A5: No, it is strictly left to right and sequential. If your operation is associative (sum, max), you can split data into chunks, reduce each in parallel (multiprocessing), then reduce the partial results: the idea behind MapReduce.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Folding with a custom combining function (merge dicts, compose functions)
- Combining many predicates/conditions with `operator.and_` / `or_`
- Navigating nested data with a path
- You want a one-value result from a sequence and no built-in fits

❌ Avoid when:
- `sum`, `max`, `min`, `math.prod`, `"".join`, `any`, `all` do the job
- The lambda is complicated or has side effects (use a loop)
- You want all intermediate values (use `itertools.accumulate`)
- The iterable may be huge and the accumulator grows, e.g. list concatenation with `+` (quadratic)

---

## 📊 Visual Diagram
```
reduce(f, [1, 2, 3, 4], 0)

 acc=0 --f(0,1)--> 1 --f(1,2)--> 3 --f(3,3)--> 6 --f(6,4)--> 10
         item 1         item 2        item 3        item 4

 with f = add :  ((((0 + 1) + 2) + 3) + 4) = 10      -> ONE value

 map     : [a, b, c] -> [f(a), f(b), f(c)]      (many in, many out)
 filter  : [a, b, c] -> [a, c]                  (many in, fewer out)
 reduce  : [a, b, c] -> f(f(a, b), c)           (many in, ONE out)
 accumulate: [a, b, c] -> [a, f(a,b), f(f(a,b),c)] (all running values)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `reduce` / fold | Combine items into one value | items को एक value में समेटना |
| Accumulator | Running result passed along | आगे बढ़ता हुआ running result |
| Initial value | Starting accumulator | शुरुआती accumulator |
| Associative | Grouping does not change result | grouping से result नहीं बदलता |
| `accumulate` | Yields all running results | सारे running results देता है |
| `operator` module | Function versions of operators | operators के function रूप |

---

## ⚡ 3-Line Summary
English: `functools.reduce(f, items, init)` folds an iterable into one value by repeatedly calling `f(acc, item)`. Always pass an initial value for possibly-empty input, and prefer `sum`, `max`, `math.prod` or `"".join` when they fit. Use `reduce` for custom folds such as merging dicts or composing functions.
Hindi: `functools.reduce(f, items, init)` बार-बार `f(acc, item)` call करके iterable को एक value में fold करता है। संभवतः खाली input के लिए हमेशा initial value दें, और जहां `sum`, `max`, `math.prod` या `"".join` चलें वहां उन्हें चुनें। Dicts merge करने या functions compose करने जैसे custom folds के लिए `reduce` use करें।

---

## ➡️ Next Topic
**120. zip() + enumerate()** - walk through several iterables side by side and get index plus value in one loop.
