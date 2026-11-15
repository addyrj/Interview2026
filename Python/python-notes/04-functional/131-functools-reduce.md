---

# 131. functools.reduce
# हिंदी में: functools.reduce (पूरी sequence को एक value में समेटना)

---

## 🔵 Simple Definition (English)
`reduce(function, iterable, initial)` applies a two-argument function cumulatively: it combines the first two items, then combines that result with the third, and so on until one value is left. It "folds" a sequence into a single result.

## 🔵 सरल परिभाषा (Hindi)
`reduce(function, iterable, initial)` दो-argument वाले function को क्रम से लगाता है: पहले दो items जोड़ता है, फिर उस result को तीसरे से, और ऐसे ही जब तक एक value बचे। यह sequence को एक result में "fold" करता है।

---

## 🔴 Problem it Solves
Sometimes you need to collapse a list into one thing with a custom rule: multiply all, merge many dicts, compose functions, intersect many sets. Built-ins `sum`, `max`, `min`, `any`, `all` cover common cases. `reduce` is the general tool for the rest. In Python 3 it moved from built-ins to `functools` because Guido found loops and built-ins usually more readable.

## 🔴 यह क्यों बना? (Hindi)
कभी-कभी list को custom rule से एक चीज़ में समेटना होता है: सबका गुणा, कई dicts merge, functions compose, कई sets का intersection। `sum`, `max`, `min`, `any`, `all` आम cases संभालते हैं। बाकी के लिए `reduce` सामान्य औज़ार है। Python 3 में यह built-ins से `functools` में चला गया क्योंकि Guido को loops और built-ins ज्यादा पढ़ने लायक लगे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → reduce(f, [a, b, c, d], init)
Step 2 → acc = init  (if no init, acc = first item and start from the second)
Step 3 → acc = f(acc, a)
Step 4 → acc = f(acc, b)
Step 5 → acc = f(acc, c) ... until the items end
Step 6 → return acc;  empty input with no init -> TypeError

reduce(lambda x, y: x + y, [1, 2, 3, 4])  =  ((1+2)+3)+4  =  10
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → reduce(f, [a, b, c, d], init)
Step 2 → acc = init  (init न हो तो acc = पहला item और दूसरे से शुरू)
Step 3 → acc = f(acc, a)
Step 4 → acc = f(acc, b)
Step 5 → acc = f(acc, c) ... items खत्म होने तक
Step 6 → acc लौटाओ;  खाली input और init नहीं हो तो TypeError
```

---

## 🟡 Real World Example
A pricing engine multiplies a chain of discount factors: `reduce(mul, factors, 1)`. A search service intersects the ID sets of each keyword: `reduce(set.intersection, id_sets)`. A config loader merges defaults, env file and CLI overrides: `reduce(merge, [defaults, env, cli], {})`. A middleware builder composes functions into one pipeline.

## 🟡 Real Example Hindi mein
Pricing engine discount factors की श्रृंखला का गुणा करता है: `reduce(mul, factors, 1)`। Search service हर keyword के ID sets का intersection लेती है: `reduce(set.intersection, id_sets)`। Config loader defaults, env file और CLI overrides को merge करता है: `reduce(merge, [defaults, env, cli], {})`। Middleware builder functions को एक pipeline में compose करता है।

---

## 💻 Code Example — Basic
```python
# Basic reduce
from functools import reduce                       # moved from builtins in Python 3
from operator import add, mul                      # function versions of + and *

nums: list[int] = [1, 2, 3, 4]                     # sample data

print(reduce(lambda a, b: a + b, nums))            # ((1+2)+3)+4
print(reduce(add, nums), sum(nums))                # same, but sum() is better here
print(reduce(mul, nums, 1))                        # product, with initial value 1
print(reduce(lambda a, b: a - b, nums))            # left fold: ((1-2)-3)-4
print(reduce(lambda a, b: b + a, "abc"))           # reverse a string: "cba"
print(reduce(max, [3, 9, 2]))                      # max via reduce (use max() normally)
print(reduce(lambda acc, x: acc + [x * 2], nums, []))      # build a list as the accumulator
print(reduce(add, [], 0))                          # empty input returns initial

try:                                               # empty input without initial fails
    reduce(add, [])                                # nothing to start from
except TypeError as e:                             # catch it
    print("Error:", e)                             # explains why

# Output:
# 10
# 10 10
# 24
# -8
# cba
# 9
# [2, 4, 6, 8]
# 0
# Error: reduce() of empty iterable with no initial value
```

## 💻 Code Example — Advanced
```python
# Production style: merge configs, intersect sets, compose functions, group counts
from collections.abc import Callable, Iterable     # typing helpers
from functools import reduce                       # the fold tool
from typing import Any, TypeVar                    # generic helpers

T = TypeVar("T")                                   # generic item type


def deep_merge(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Merge b into a copy of a; nested dicts merge recursively."""
    out = dict(a)                                  # never mutate the inputs
    for k, v in b.items():                         # walk the override layer
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)         # merge nested dicts
        else:
            out[k] = v                             # simple override
    return out


defaults = {"db": {"host": "localhost", "port": 5432}, "debug": False}   # lowest priority
env_file = {"db": {"host": "prod-db"}}                                    # overrides host
cli = {"debug": True}                                                     # highest priority
config = reduce(deep_merge, [defaults, env_file, cli], {})   # fold layers left to right
print(config)                                      # merged configuration


def common_ids(id_sets: list[set[int]]) -> set[int]:
    """Documents containing ALL keywords."""
    return reduce(set.intersection, id_sets) if id_sets else set()    # guard the empty case


print(common_ids([{1, 2, 3}, {2, 3, 4}, {3, 2, 9}]))    # {2, 3}


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """compose(f, g, h)(x) == h(g(f(x))): a tiny pipeline builder."""
    return lambda x: reduce(lambda acc, fn: fn(acc), funcs, x)   # feed result forward


clean = compose(str.strip, str.lower, lambda s: s.replace(" ", "-"))   # three steps in one
print(clean("  Hello World  "))                    # hello-world


def count_words(words: Iterable[str]) -> dict[str, int]:
    """Counting with reduce works, but see Counter below."""
    def step(acc: dict[str, int], w: str) -> dict[str, int]:
        acc[w] = acc.get(w, 0) + 1                 # increment this word
        return acc                                 # return the accumulator
    return reduce(step, words, {})


print(count_words(["a", "b", "a"]))                # {'a': 2, 'b': 1}
from collections import Counter                    # the better tool for this job
print(dict(Counter(["a", "b", "a"])))              # same answer, clearer

# Output:
# {'db': {'host': 'prod-db', 'port': 5432}, 'debug': True}
# {2, 3}
# hello-world
# {'a': 2, 'b': 1}
# {'a': 2, 'b': 1}
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Location | `functools.reduce(f, it, init)` | `array.reduce(f, init)` method |
| Argument order | function first | callback first, init second |
| Initial value | optional third arg | optional second arg |
| Empty without init | `TypeError` | `TypeError` |
| Style | discouraged for simple sums | very common |
| Right fold | none (reverse manually) | `reduceRight` |

```python
# Python way
from functools import reduce
print(reduce(lambda acc, x: acc + x, [1, 2, 3], 0))   # 6  (but sum() is preferred)
```
```javascript
// JavaScript way
console.log([1, 2, 3].reduce((acc, x) => acc + x, 0));  // 6 (idiomatic JS)
```

Key difference: In JS, `reduce` is the everyday tool for sums, grouping and objects. In Python you reach for `sum`, `Counter`, `groupby`, a comprehension or a loop first and use `reduce` only for genuine folds.

---

## 🟠 FastAPI Connection
`reduce` appears in FastAPI services when combining many optional filters into one SQLAlchemy condition, or merging layered settings. A common pattern: build a `WHERE` clause by folding filter conditions with `and_`.

```python
# FastAPI example — combine optional filters with reduce
from functools import reduce                       # fold tool
from operator import and_                          # bitwise & works for SQL expressions too
from fastapi import FastAPI                        # app
from fastapi.testclient import TestClient          # in-process test client

app: FastAPI = FastAPI()                           # create app
USERS = [{"name": "asha", "city": "Pune", "age": 30}, {"name": "ravi", "city": "Delhi", "age": 25}]


@app.get("/users")                                 # GET /users?city=Pune&min_age=26
def search(city: str | None = None, min_age: int | None = None) -> list[str]:
    checks = []                                    # list of predicate functions
    if city:
        checks.append(lambda u: u["city"] == city) # city filter
    if min_age is not None:
        checks.append(lambda u: u["age"] >= min_age)   # age filter
    keep = lambda u: reduce(and_, (c(u) for c in checks), True)   # AND all filters together
    return [u["name"] for u in USERS if keep(u)]   # no filters -> everyone


c = TestClient(app)
print(c.get("/users", params={"city": "Pune", "min_age": 26}).json(), c.get("/users").json())
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `reduce` for things that have a built-in
✅ Correct: `sum`, `max`, `min`, `any`, `all`, `"".join`, `math.prod`

```python
from functools import reduce
from operator import add
import math
nums = [1, 2, 3, 4]
# Wrong
print(reduce(add, nums))        # 10
# Right
print(sum(nums), math.prod(nums))   # 10 24
```

❌ Mistake 2: Forgetting the initial value on possibly empty data
✅ Correct: always pass an initial value when the list can be empty

```python
from functools import reduce
from operator import add
items = []
# Wrong
# reduce(add, items)            # TypeError
# Right
print(reduce(add, items, 0))    # 0
```

❌ Mistake 3: Mutating a shared initial accumulator
✅ Correct: create a fresh accumulator or return new objects

```python
from functools import reduce
def step(acc, x):
    acc.append(x); return acc
# Wrong: the shared default list keeps growing across calls
INIT = []
reduce(step, [1], INIT); reduce(step, [2], INIT)
print(INIT)                     # [1, 2]
# Right
print(reduce(step, [2], []))    # [2]
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from functools import reduce
print(reduce(lambda a, b: a - b, [10, 2, 3]))
print(reduce(lambda a, b: a / b, [8, 2, 2]))
print(reduce(lambda a, b: a + b, [[1], [2], [3]]))
print(reduce(lambda a, b: a + b, ["a", "b"], 5))
```
Answer: `5` (`(10-2)-3`). `2.0` (`(8/2)/2`, true division returns a float). `[1, 2, 3]` (list `+` concatenates). The last line raises `TypeError: unsupported operand type(s) for +: 'int' and 'str'` because the initial value `5` is combined with `"a"` first.

---

## ⚫ Interview Questions + Answers

Q1: Why was `reduce` moved out of built-ins in Python 3?
A1: Guido preferred explicit loops and built-ins like `sum`; he found complex `reduce` calls hard to read. It still lives in `functools` for the cases where a real fold is clearest.

Q2: Does `reduce` fold from the left or the right?
A2: From the left: `f(f(f(a, b), c), d)`. Python has no `reduceRight`; reverse the sequence if you need a right fold (careful with non-commutative operations).

Q3: What happens with one item and no initial value?
A3: It returns that single item without calling the function. With an initial value and an empty iterable, it returns the initial value.

Q4: Is `reduce` faster than a loop?
A4: Not really. With a lambda it calls a Python function per item, so it's often slower than a loop or a built-in like `sum`. `reduce(operator.add, ...)` is faster than a lambda but `sum()` still wins.

Q5: How do you implement `compose` or `pipeline` with it?
A5: `reduce(lambda acc, fn: fn(acc), funcs, value)` feeds the value through each function in order. This is one of the strongest legitimate uses.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Folding with a custom binary operation (merge, intersect, compose)
- Combining many predicates or filters
- The operation is associative and clear when read aloud

❌ Avoid when:
- A built-in exists: `sum`, `max`, `min`, `any`, `all`, `math.prod`, `"".join`
- The logic needs several lines (use a for loop)
- Counting or grouping (`Counter`, `defaultdict`, `groupby`)

---

## 📊 Visual Diagram
```
reduce(f, [1, 2, 3, 4], 0)

 acc = 0
 acc = f(0, 1) = 1
 acc = f(1, 2) = 3
 acc = f(3, 3) = 6
 acc = f(6, 4) = 10  --> result

        f
       / \
      f   4
     / \
    f   3
   / \
  f   2
 / \
0   1
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fold | Combine many into one | कई को एक में मिलाना |
| Accumulator | Running result | चलता हुआ result |
| Initial value | Starting accumulator | शुरुआती accumulator |
| Associative | Grouping doesn't change result | Grouping से result नहीं बदलता |
| Compose | Chain functions | Functions को जोड़ना |
| Binary function | Function of two arguments | दो arguments वाला function |

---

## ⚡ 3-Line Summary
English: `reduce(f, items, init)` folds a sequence from the left into one value using a two-argument function. Always supply an initial value for possibly empty data. Prefer built-ins (`sum`, `max`, `join`) when they fit.
Hindi: `reduce(f, items, init)` दो-argument function से sequence को बाएं से एक value में fold करता है। खाली हो सकने वाले data के लिए initial value दें। जहाँ built-ins (`sum`, `max`, `join`) फिट हों वहाँ उन्हें चुनें।

---

## ➡️ Next Topic
**132. Immutability in Python** — which types can't change, frozen dataclasses and why it matters.
