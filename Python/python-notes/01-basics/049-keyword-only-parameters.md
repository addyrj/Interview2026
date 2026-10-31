---

# 049. Keyword Only Parameters
# हिंदी में: सिर्फ Keyword से पास होने वाले Parameters

---

## 🔵 Simple Definition (English)
A keyword-only parameter is a function parameter that can be passed ONLY by name (`f(x=1)`), never by position (`f(1)`). You create them by putting a bare `*` in the parameter list: every parameter after the `*` is keyword-only. This makes function calls self-documenting and safe.

## 🔵 सरल परिभाषा (Hindi)
Keyword-only parameter वह parameter है जिसे सिर्फ नाम से पास किया जा सकता है (`f(x=1)`), position से नहीं (`f(1)`)। Parameter list में सिर्फ `*` लगाने से उसके बाद के सभी parameters keyword-only बन जाते हैं। इससे function call पढ़ने में साफ़ और सुरक्षित रहती है।

---

## 🔴 Problem it Solves
Imagine `create_user("Priya", True, False, 3)`. What do `True`, `False` and `3` mean? Nobody knows without opening the function. Also, if someone later reorders the parameters, old calls silently break with wrong data. Boolean flags and config options are the worst offenders. Keyword-only parameters force the caller to write `create_user("Priya", is_admin=True, send_email=False, retries=3)`, so the call explains itself and argument order stops mattering.

## 🔴 यह क्यों बना? (Hindi)
`create_user("Priya", True, False, 3)` में `True`, `False`, `3` का मतलब क्या है? function खोले बिना पता नहीं चलता। अगर बाद में parameters का order बदल जाए तो पुरानी calls चुपचाप गलत data दे देती हैं। Keyword-only से caller को नाम लिखना ही पड़ता है, इसलिए code खुद समझाता है और order का फर्क नहीं पड़ता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → def f(a, b, *, c, d=10):   ← bare * marks the boundary
Step 2 → a, b are normal: positional OR keyword
Step 3 → c, d are keyword-only: MUST be written as c=..., d=...
Step 4 → f(1, 2, c=3)   works  (d uses default 10)
Step 5 → f(1, 2, 3)     TypeError: takes 2 positional arguments but 3 were given
Step 6 → def g(*args, c): same idea — anything after *args is keyword-only too
Step 7 → def h(a, /, b, *, c): "/" = positional-only, "*" = keyword-only (Python 3.8+)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → def f(a, b, *, c, d=10):  ← अकेला * सीमा-रेखा है
Step 2 → a, b normal हैं: position या keyword दोनों चलेंगे
Step 3 → c, d keyword-only हैं: c=..., d=... लिखना ज़रूरी
Step 4 → f(1, 2, c=3) चलेगा (d का default 10)
Step 5 → f(1, 2, 3) → TypeError
Step 6 → *args के बाद वाले parameters भी अपने आप keyword-only होते हैं
Step 7 → "/" = positional-only, "*" = keyword-only
```

---

## 🟡 Real World Example
Razorpay-style payment helper: `create_order(amount, *, currency="INR", capture=True, notes=None)`. The amount is obvious by position, but `capture=True` must be named, otherwise nobody can read `create_order(500, "INR", True, None)`. Python's own stdlib does this too: `sorted(items, *, key=None, reverse=False)` and `print(..., sep=" ", end="\n")`. You cannot write `sorted(items, len)`; you must write `sorted(items, key=len)`.

## 🟡 Real Example Hindi mein
Razorpay जैसा payment helper: `create_order(amount, *, currency="INR", capture=True)`। Amount position से समझ आ जाता है, लेकिन `capture=True` नाम के साथ लिखना ज़रूरी है वरना `create_order(500, "INR", True)` कोई पढ़ नहीं पाएगा। Python का `sorted(items, key=len)` भी ऐसे ही काम करता है; `sorted(items, len)` error देगा।

---

## 💻 Code Example — Basic
```python
# Basic keyword-only parameters

def create_user(name: str, *, is_admin: bool = False, retries: int = 3) -> str:  # bare * starts keyword-only zone
    return f"{name} admin={is_admin} retries={retries}"  # build a readable string

print(create_user("Priya"))                      # Output: Priya admin=False retries=3
print(create_user("Priya", is_admin=True))       # Output: Priya admin=True retries=3
print(create_user("Priya", retries=5, is_admin=True))  # order of keywords does not matter -> Priya admin=True retries=5

try:  # passing keyword-only by position must fail
    create_user("Priya", True)  # type: ignore[misc]  # 2nd positional is not allowed
except TypeError as err:  # catch the error
    print(err)  # Output: create_user() takes 1 positional argument but 2 were given

# keyword-only WITHOUT a default = required keyword
def connect(host: str, *, port: int) -> str:  # port has no default, so caller must pass port=...
    return f"{host}:{port}"  # return host:port

print(connect("localhost", port=8000))  # Output: localhost:8000

try:  # forgetting the required keyword
    connect("localhost")  # type: ignore[call-arg]  # port is missing
except TypeError as err:  # catch it
    print(err)  # Output: connect() missing 1 required keyword-only argument: 'port'
```

## 💻 Code Example — Advanced
```python
# Production style: *args + keyword-only, positional-only "/", and **kwargs forwarding
import logging  # standard logging module
from typing import Any  # for flexible kwargs typing

logging.basicConfig(level=logging.INFO, format="%(message)s")  # print only the message
logger: logging.Logger = logging.getLogger("svc")  # module-level logger

# 1. After *args every parameter is keyword-only
def total(*numbers: float, round_to: int = 2) -> float:  # round_to can ONLY be passed by name
    return round(sum(numbers), round_to)  # sum all numbers and round

print(total(1.234, 2.345, round_to=1))  # Output: 3.6
print(total(1, 2, 3))                   # Output: 6

# 2. Positional-only (/) + normal + keyword-only (*) in one signature
def fetch(url: str, /, method: str = "GET", *, timeout: float = 5.0, verify: bool = True) -> dict[str, Any]:
    # url is positional-only, method is flexible, timeout/verify are keyword-only
    return {"url": url, "method": method, "timeout": timeout, "verify": verify}  # echo config

print(fetch("https://api.test", "POST", timeout=2.5))
# Output: {'url': 'https://api.test', 'method': 'POST', 'timeout': 2.5, 'verify': True}

# 3. Forwarding options safely with **kwargs
def call_api(endpoint: str, **options: Any) -> dict[str, Any]:  # accept any named options
    logger.info("calling %s with %s", endpoint, options)  # log what we send
    return fetch(endpoint, **options)  # unpack options into keyword-only params

print(call_api("https://api.test", timeout=1.0))
# Output (log line first): calling https://api.test with {'timeout': 1.0}
# Output: {'url': 'https://api.test', 'method': 'GET', 'timeout': 1.0, 'verify': True}

# 4. Inspect the signature at runtime
import inspect  # signature introspection
sig: inspect.Signature = inspect.signature(fetch)  # read the signature object
for pname, p in sig.parameters.items():  # loop over parameters
    print(pname, p.kind.name)  # print name and kind
# Output:
# url POSITIONAL_ONLY
# method POSITIONAL_OR_KEYWORD
# timeout KEYWORD_ONLY
# verify KEYWORD_ONLY
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript has no keyword arguments. The common trick is to pass ONE object and destructure it, which gives named parameters. Python has the feature built into the language.

```python
# Python: built-in keyword-only
def create_order(amount: int, *, currency: str = "INR", capture: bool = True) -> str:
    return f"{amount} {currency} capture={capture}"

print(create_order(500, capture=False))  # Output: 500 INR capture=False
```
```javascript
// JavaScript: destructured options object (simulated keyword-only)
function createOrder(amount, { currency = "INR", capture = true } = {}) {
    return `${amount} ${currency} capture=${capture}`;
}
console.log(createOrder(500, { capture: false }));  // 500 INR capture=false
// JS cannot raise an error if the caller passes a wrong key; Python raises TypeError.
```

---

## 🟠 FastAPI Connection
FastAPI itself uses keyword-only style everywhere: `FastAPI(title="x", version="1")`, `Query(default=None, max_length=50)`, `Depends(...)`. Writing your own helpers and services with `*` gives the same clean call style. Also, FastAPI path functions often put `*` first so that parameters with defaults can come before parameters without defaults.

```python
from fastapi import FastAPI, Query  # FastAPI app + Query helper

app: FastAPI = FastAPI(title="Shop")  # title is passed by keyword

@app.get("/items")  # GET /items
async def list_items(*, q: str | None = Query(default=None, max_length=50), limit: int = 10) -> dict[str, object]:
    # the leading * lets a default parameter sit before a required one without SyntaxError
    return {"q": q, "limit": limit}  # echo query params
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Passing a keyword-only parameter by position
```python
def send(msg: str, *, urgent: bool = False) -> None: ...

# Wrong:
# send("hi", True)          # TypeError: send() takes 1 positional argument but 2 were given

# Right:
send("hi", urgent=True)     # name it
```

❌ Mistake 2: Putting `*` as the LAST parameter or using two bare `*`
```python
# Wrong:
# def f(a, *): ...           # SyntaxError: named arguments must follow bare *
# def f(*, *, a): ...        # SyntaxError: * argument may appear only once

# Right:
def f(a, *, b): ...          # at least one named parameter after *
```

❌ Mistake 3: Thinking required keyword-only parameters need a default
```python
# Wrong belief: "everything after * must have a default"
# Right: no default means "required keyword"
def g(*, token: str) -> str:  # caller must write g(token="abc")
    return token
```

---

## 🧠 Tricky Interview Question

```python
def f(a, b=2, *args, c, d=4):
    return a, b, args, c, d

print(f(1, 2, 3, 4, c=5))
print(f(1, c=5))
# print(f(1, 2, 3))   # what happens here?
```
Answer: First prints `(1, 2, (3, 4), 5, 4)`: extra positional values go into `args`, and `c` must be named. Second prints `(1, 2, (), 5, 4)`: b and d use defaults, args is an empty tuple. The commented call raises `TypeError: f() missing 1 required keyword-only argument: 'c'`, because `3` is swallowed by `*args`, so `c` was never supplied. Key point: parameters after `*args` can never be filled by position.

---

## ⚫ Interview Questions + Answers

Q1: What is a keyword-only parameter and how do you declare it?
A1: A parameter that must be passed by name. Put a bare `*` in the signature (`def f(a, *, b)`) or place the parameter after `*args` (`def f(*args, b)`). Everything after the `*` is keyword-only.

Q2: What is the difference between `*` and `/` in a signature?
A2: `/` ends the positional-only zone (parameters before it cannot be passed by keyword). `*` starts the keyword-only zone (parameters after it cannot be passed by position). Parameters between `/` and `*` can be passed either way. Example: `def f(a, /, b, *, c)`.

Q3: Why would you use keyword-only parameters in an API design?
A3: Readability (call sites explain themselves), safety (reordering parameters in the future does not break callers), and extensibility (you can add new options without worrying about positional order). They are ideal for boolean flags and optional configuration.

Q4: Can a keyword-only parameter be required?
A4: Yes. If you give no default value, it is a required keyword-only parameter, and omitting it raises `TypeError: missing 1 required keyword-only argument`.

Q5: How do you list which parameters of a function are keyword-only at runtime?
A5: Use `inspect.signature(func).parameters` and check `param.kind == inspect.Parameter.KEYWORD_ONLY`. Frameworks like FastAPI and Pydantic use this kind of introspection to read your function signatures.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The function has boolean flags or many optional settings
- You want call sites to be self-documenting
- You want freedom to reorder or extend parameters later
- Building a public library or service layer API

❌ Avoid when:
- The function has 1 or 2 obvious parameters (`add(a, b)`)
- Parameters are naturally ordered (`point(x, y)`, `pow(base, exp)`)
- You need to call the function through `map()` style positional unpacking

---

## 📊 Visual Diagram
```
def fetch(url, /, method="GET", *, timeout=5.0, verify=True)
          ─────  ─────────────  ─────────────────────────
            │          │                   │
   positional-only   normal          keyword-only
   fetch("u")       fetch("u","POST")  timeout=2.5  (name REQUIRED)
   (no url=...)     or method="POST"   fetch("u","POST",2.5) -> TypeError
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Keyword-only | Must be passed by name | सिर्फ नाम से पास होता है |
| Bare `*` | Marker that starts keyword-only zone | keyword-only शुरू करने वाला निशान |
| Positional-only `/` | Parameters before `/` cannot use names | `/` से पहले सिर्फ position |
| `*args` | Collects extra positional args as tuple | extra positional values का tuple |
| `inspect.signature` | Reads function parameter details | function के parameters की जानकारी |

---

## ⚡ 3-Line Summary
English: A bare `*` in a function signature makes every parameter after it keyword-only. Callers must write `name=value`, which makes code readable and safe against reordering. Combine with `/` for positional-only and use it for flags and options.
Hindi: Signature में अकेला `*` लगाने से उसके बाद के सारे parameters keyword-only हो जाते हैं। Caller को `name=value` लिखना पड़ता है, इसलिए code साफ़ और order बदलने से सुरक्षित रहता है। Flags और options के लिए इसका उपयोग करें।

---

## ➡️ Next Topic
**050. Lambda Functions** — small anonymous functions, which you will often pass as `key=` (a keyword-only parameter of `sorted`) in sorting and filtering.
