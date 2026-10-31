---

# 048. Positional Only Parameters
# हिंदी में: Positional Only Parameters (सिर्फ position से दिए जाने वाले)

---

## 🔵 Simple Definition (English)
Positional-only parameters are parameters that can be passed only by position, never by name. You mark them by putting a `/` in the parameter list: `def f(a, b, /, c)`. Everything before the `/` is positional-only. This syntax exists since Python 3.8 (PEP 570).

## 🔵 सरल परिभाषा (Hindi)
Positional-only parameters वे हैं जिन्हें सिर्फ position से दिया जा सकता है, नाम से कभी नहीं। इन्हें parameter list में `/` लगाकर बनाते हैं: `def f(a, b, /, c)`. `/` से पहले का सब कुछ positional-only है। यह syntax Python 3.8 (PEP 570) से है।

---

## 🔴 Problem it Solves
Once a parameter name is public, callers can use it as a keyword (`f(a=1)`), so renaming it later breaks their code. For functions like `len(obj)` or `pow(x, y)` the name carries no meaning at all. Also, with `**kwargs` a parameter name can clash with a key. Positional-only makes the name private, free to change, and avoids those clashes.

## 🔴 यह क्यों बना? (Hindi)
Parameter का नाम public हो जाए तो callers उसे keyword की तरह (`f(a=1)`) इस्तेमाल कर सकते हैं, फिर नाम बदलने पर उनका code टूटता है। `len(obj)` या `pow(x, y)` जैसे functions में नाम का कोई मतलब ही नहीं। साथ ही `**kwargs` में parameter का नाम किसी key से टकरा सकता है। Positional-only नाम को private बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write the signature: def f(a, b, /, c, *, d)
Step 2 → Parts:
           a, b  → before '/'      → positional-only
           c     → between / and * → positional OR keyword
           d     → after '*'       → keyword-only
Step 3 → f(1, 2, 3, d=4)   OK
Step 4 → f(a=1, b=2, c=3, d=4) → TypeError (a, b used as keywords)
Step 5 → The names a, b are free to appear as keys in **kwargs
```

## 🟢 कैसे काम करता है? (Hindi)
```
def f(a, b, /, c, *, d)
  a, b → '/' से पहले  → सिर्फ positional
  c    → बीच में      → positional या keyword दोनों
  d    → '*' के बाद   → सिर्फ keyword
f(a=1, ...) करने पर TypeError आता है
```

---

## 🟡 Real World Example
Built-ins use this a lot: `len(obj, /)`, `isinstance(obj, class_or_tuple, /)`, `divmod(x, y, /)`. A library author writes `def get(self, key, /, default=None)` so they can later rename `key` without breaking anyone. A web framework forwards user-supplied options in `**kwargs`; positional-only lets an option literally named `self` or `key` pass through.

## 🟡 Real Example Hindi mein
Built-ins में यह बहुत होता है: `len(obj, /)`, `isinstance(obj, class_or_tuple, /)`, `divmod(x, y, /)`. Library author `def get(self, key, /, default=None)` लिखता है ताकि बाद में `key` का नाम बदलने पर किसी का code न टूटे। Framework user के दिए options `**kwargs` में forward करता है; positional-only होने से `self` या `key` नाम का option भी पास हो जाता है।

---

## 💻 Code Example — Basic
```python
# Basic positional-only parameters - every line commented
def add(a: int, b: int, /) -> int:  # a and b can only be passed by position
    return a + b  # add them


print(add(2, 3))  # positional call works
# Output: 5

try:  # try the keyword form
    add(a=2, b=3)  # type: ignore[call-arg]  # not allowed
except TypeError as exc:  # Python rejects it
    print("TypeError:", exc)  # show the message
# Output: TypeError: add() got some positional-only arguments passed as keyword arguments: 'a, b'


def greet(name: str, /, greeting: str = "Hello") -> str:  # name is positional-only
    return f"{greeting}, {name}!"  # build text


print(greet("Asha"))  # name positional
# Output: Hello, Asha!
print(greet("Asha", greeting="Hi"))  # greeting can be a keyword
# Output: Hi, Asha!
print(greet("Asha", "Namaste"))  # greeting can also be positional
# Output: Namaste, Asha!


def f(a: int, b: int, /, c: int, *, d: int) -> tuple[int, int, int, int]:  # all three kinds
    return a, b, c, d  # return everything


print(f(1, 2, 3, d=4))  # a, b by position; c either; d by keyword
# Output: (1, 2, 3, 4)
print(f(1, 2, c=3, d=4))  # c as keyword is fine
# Output: (1, 2, 3, 4)

# Built-ins are positional-only too
try:  # keyword with len
    len(obj=[1, 2])  # type: ignore[call-arg]
except TypeError as exc:  # rejected
    print("TypeError:", exc)  # show message
# Output: TypeError: len() takes no keyword arguments
```

## 💻 Code Example — Advanced
```python
# Production style: free renaming, kwargs name clash, inspect, copy-like APIs
import inspect  # read signatures
from typing import Any, Dict, Optional  # type hints


# 1. The name clash that positional-only solves
def format_message_old(template: str, **values: Any) -> str:
    return template.format(**values)  # values may not use the name 'template'


def format_message(template: str, /, **values: Any) -> str:
    return template.format(**values)  # 'template' can now be a placeholder name too


print(format_message("{template} is {x}", template="design", x="ready"))
# Output: design is ready
try:  # same call on the old version
    format_message_old("{template} is {x}", template="design", x="ready")
except TypeError as exc:  # clash!
    print("TypeError:", exc)
# Output: TypeError: format_message_old() got multiple values for argument 'template'


# 2. A class with a stable public API: parameter names are private
class Cache:
    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}  # internal storage

    def get(self, key: str, default: Optional[Any] = None, /) -> Any:
        return self._data.get(key, default)  # callers cannot depend on names 'key'/'default'

    def set(self, key: str, value: Any, /) -> None:
        self._data[key] = value  # store value


cache = Cache()  # new cache
cache.set("user:1", "Asha")  # positional only
print(cache.get("user:1"), cache.get("user:2", "n/a"))  # Output: Asha n/a


# 3. Inspect parameter kinds
def sample(a: int, b: int, /, c: int, *args: int, d: int, **kw: int) -> None:
    pass  # body not needed


for name, p in inspect.signature(sample).parameters.items():  # each parameter
    print(f"{name:5} {p.kind.name}")  # show its kind
# Output:
# a     POSITIONAL_ONLY
# b     POSITIONAL_ONLY
# c     POSITIONAL_OR_KEYWORD
# args  VAR_POSITIONAL
# d     KEYWORD_ONLY
# kw    VAR_KEYWORD


# 4. Wrapper that forwards everything (the safe way)
def call_with_timing(func: Any, /, *args: Any, **kwargs: Any) -> Any:
    # 'func' is positional-only so the wrapped function can have a parameter called func
    return func(*args, **kwargs)  # forward unchanged


def process(func: str, value: int) -> str:  # has its own 'func' parameter
    return f"{func}:{value}"  # simple result


print(call_with_timing(process, func="resize", value=3))  # no name clash
# Output: resize:3
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: choose per parameter how it may be passed
def f(a, b, /, c, *, d):
    return a, b, c, d
f(1, 2, 3, d=4)             # a,b positional-only; c either; d keyword-only
```

```javascript
// JavaScript: arguments are positional only; NO keyword calls at all
function f(a, b, c, { d } = {}) {   // 'd' emulated by an options object
  return [a, b, c, d];
}
f(1, 2, 3, { d: 4 });
// Parameter names are never part of the public call syntax,
// so renaming 'a' is always safe - Python needs '/' to get this guarantee.
```

Key differences: in JS every parameter is effectively positional-only, so names are private by default. In Python, all parameter names are public (callers can use them as keywords) unless you add `/`. Python gives finer control with three zones: positional-only, either, and keyword-only.

---

## 🟠 FastAPI Connection
FastAPI maps request data to parameters by NAME, so endpoint parameters should stay normal (positional-or-keyword). Positional-only (`/`) is useful in your internal helpers, service layer and shared libraries, where you want freedom to rename arguments later without breaking callers.

```python
# FastAPI: endpoint uses names; internal helper uses positional-only (pip install fastapi)
from fastapi import FastAPI  # the framework

app: FastAPI = FastAPI()  # create app


def slugify(text: str, /, sep: str = "-") -> str:  # 'text' name is private
    return sep.join(text.lower().split())  # "Hello World" -> "hello-world"


@app.get("/slug")  # GET /slug?title=Hello World
def make_slug(title: str, sep: str = "-") -> dict[str, str]:  # names matter here
    return {"slug": slugify(title, sep=sep)}  # call helper: positional + keyword
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Passing a positional-only parameter by name
```python
def area(width, height, /):
    return width * height

# Wrong - TypeError:
# area(width=2, height=3)

# Correct:
print(area(2, 3))   # 6
```

❌ Mistake 2: Putting `/` in the wrong place
```python
# Wrong - SyntaxError: '/' must come before '*', and after at least one parameter
# def f(/, a): ...
# def f(*, a, /): ...

# Correct:
def f(a, /, b, *, c):
    return a, b, c
```

❌ Mistake 3: Using positional-only on FastAPI endpoints
```python
# Wrong idea: FastAPI matches request data by NAME. Hiding names with '/'
# on an endpoint's parameters breaks that mapping:
# @app.get("/items")
# def read(q: str, /): ...   # not meant for query parameters

# Correct: use normal parameters in endpoints; use '/' in helper functions.
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
def f(a, /, **kw):
    return a, kw

print(f(1, a=2))

def g(a, b=2, /, c=3):
    return a, b, c

print(g(1, c=9))
print(g(1, 5))
```

**Answer**:
```
(1, {'a': 2})
(1, 2, 9)
(1, 5, 3)
```
`a` is positional-only, so the keyword `a=2` is not a clash: it goes into `kw`. In `g`, positional-only parameters can have defaults, so `g(1, c=9)` gives `(1, 2, 9)` and `g(1, 5)` gives `(1, 5, 3)`.

---

## ⚫ Interview Questions + Answers

Q1: What does `/` mean in a function signature?
A1: Parameters before `/` are positional-only. They cannot be passed by keyword. Added in Python 3.8 (PEP 570). It is the mirror of `*`, which marks keyword-only parameters.

Q2: Why would a library author use positional-only parameters?
A2: To keep parameter names out of the public API. They can rename or reorder internals later without breaking users, and avoid name collisions with `**kwargs` keys.

Q3: Name built-ins that are positional-only.
A3: `len(obj, /)`, `abs(x, /)`, `divmod(x, y, /)`, `isinstance(obj, cls, /)`. Their docs show a `/` in the signature (`help(len)`).

Q4: Can positional-only parameters have defaults?
A4: Yes: `def f(a, b=2, /)`. Parameters after a defaulted one also need defaults, as usual.

Q5: What is the full order of parameter kinds?
A5: Positional-only, `/`, positional-or-keyword, `*args` (or bare `*`), keyword-only, `**kwargs`.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- The name carries no meaning (`len(x)`, `add(a, b)`)
- You want freedom to rename parameters in a library
- A `**kwargs` key could clash with a parameter name

❌ Avoid when:
- Names help readability at call sites (use keywords instead)
- It is a FastAPI endpoint or Pydantic-driven function that depends on names
- Targeting Python older than 3.8

---

## 📊 Visual Diagram

```
 def f( a, b,  /,  c,  *,  d, **kw )
        └──┬──┘     │      │   └ extra keywords
   positional-only  │   keyword-only
                    └ positional OR keyword

 call:  f( 1, 2,    3,     d=4 )
          ▲  ▲      ▲      ▲
         by place  either  by name only
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `/` marker | Ends positional-only zone | positional-only हिस्से का अंत |
| `*` marker | Starts keyword-only zone | keyword-only हिस्से की शुरुआत |
| PEP 570 | Proposal that added `/` | `/` जोड़ने वाला proposal |
| Public API | Names callers may rely on | जिन नामों पर callers निर्भर हों |
| Name clash | Same name used twice | एक ही नाम का टकराव |
| inspect | Module to read signatures | signatures पढ़ने वाला module |

---

## ⚡ 3-Line Summary
English: Parameters before `/` can only be passed by position, which keeps their names private and free to change. Use it for meaningless names and to avoid clashes with `**kwargs`. Order of kinds: positional-only, `/`, normal, `*`, keyword-only, `**kwargs`.
Hindi: `/` से पहले के parameters सिर्फ position से दिए जाते हैं, इसलिए उनके नाम private रहते हैं और बदले जा सकते हैं। बेमतलब नामों और `**kwargs` के टकराव से बचने के लिए इस्तेमाल करें। क्रम: positional-only, `/`, normal, `*`, keyword-only, `**kwargs`।

---

## ➡️ Next Topic
**049. Keyword Only Parameters** — use a bare `*` to force callers to name important arguments.
