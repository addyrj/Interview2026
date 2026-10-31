---

# 047. Keyword Arguments
# हिंदी में: Keyword Arguments (नाम से argument देना)

---

## 🔵 Simple Definition (English)
A keyword argument is passed by parameter name at the call site: `connect(host="db", port=5432)`. Order no longer matters, and the call explains itself. Positional arguments must come first, then keyword arguments.

## 🔵 सरल परिभाषा (Hindi)
Keyword argument call करते समय parameter के नाम से दिया जाता है: `connect(host="db", port=5432)`. इसमें order मायने नहीं रखता और call खुद समझा देती है। Positional arguments पहले आते हैं, फिर keyword arguments।

---

## 🔴 Problem it Solves
Calls like `create_user("Asha", 25, True, False, None, "IN")` are unreadable: what is `True`? What is `False`? Swapping two positions causes silent bugs. Keyword arguments make every value labelled, allow skipping optional parameters, and let you add new parameters later without breaking old callers.

## 🔴 यह क्यों बना? (Hindi)
`create_user("Asha", 25, True, False, None, "IN")` जैसी call पढ़ी नहीं जाती: `True` क्या है? दो positions बदलने से चुपचाप bug आता है। Keyword arguments हर value को नाम देते हैं, optional parameters skip करने देते हैं, और बाद में नया parameter जोड़ने पर पुराने callers नहीं टूटते।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python fills positional arguments left to right
Step 2 → Then it matches each name=value to the parameter with that name
Step 3 → Unfilled parameters use their defaults
Step 4 → Errors:
           - unknown name              → TypeError (unexpected keyword)
           - same parameter twice      → TypeError (multiple values)
           - required parameter missing→ TypeError (missing argument)
Step 5 → Extra names go to **kwargs if the function has it
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले positional arguments बाएँ से दाएँ भरते हैं
Step 2 → फिर हर name=value उसी नाम के parameter से match होता है
Step 3 → बाकी parameters में default आता है
Step 4 → गलत नाम / दो बार value / required missing → TypeError
Step 5 → extra नाम **kwargs में जाते हैं (अगर function में हो)
```

---

## 🟡 Real World Example
Razorpay: `client.order.create(amount=50000, currency="INR", receipt="rcpt_1")`. Anyone reading it knows exactly what is sent. Calling OpenAI: `client.chat.completions.create(model="gpt-4o", messages=msgs, temperature=0)`; these libraries are keyword-heavy by design. Logging: `logging.basicConfig(level=..., format=...)`.

## 🟡 Real Example Hindi mein
Razorpay: `client.order.create(amount=50000, currency="INR", receipt="rcpt_1")`. पढ़ने वाले को साफ़ पता चलता है क्या भेजा जा रहा है। OpenAI call: `client.chat.completions.create(model="gpt-4o", messages=msgs, temperature=0)`; ये libraries जान-बूझकर keyword-heavy हैं।

---

## 💻 Code Example — Basic
```python
# Basic keyword arguments - every line commented
from typing import Optional  # type hint helper


def create_user(name: str, age: int, city: str = "Pune", active: bool = True) -> str:
    return f"{name}, {age}, {city}, active={active}"  # describe the user


print(create_user("Asha", 25))  # positional only
# Output: Asha, 25, Pune, active=True

print(create_user(name="Ravi", age=30))  # all keyword
# Output: Ravi, 30, Pune, active=True

print(create_user(age=22, name="Meera"))  # order does not matter
# Output: Meera, 22, Pune, active=True

print(create_user("Kabir", 28, active=False))  # mix: positional first, then keyword
# Output: Kabir, 28, Pune, active=False

print(create_user("Zoya", 31, city="Delhi"))  # skip 'active', set 'city'
# Output: Zoya, 31, Delhi, active=True


def connect(host: str, port: int = 5432, *, timeout: Optional[float] = None) -> str:
    return f"{host}:{port} timeout={timeout}"  # timeout is keyword-only


print(connect("db", timeout=2.5))  # timeout MUST be named
# Output: db:5432 timeout=2.5

# Built-ins use keyword arguments too
print("a", "b", sep="-", end="!\n")  # sep and end are keyword-only
# Output: a-b!
print(sorted([3, 1, 2], reverse=True))  # reverse is keyword-only
# Output: [3, 2, 1]
print(sorted(["bb", "a", "ccc"], key=len))  # key is keyword-only
# Output: ['a', 'bb', 'ccc']
```

## 💻 Code Example — Advanced
```python
# Production style: kwargs unpacking, error handling, config merging, inspect
import inspect  # to look at function signatures
from typing import Any, Dict  # type hints


def send_email(to: str, subject: str, body: str = "", *, cc: str = "", retries: int = 3) -> str:
    return f"to={to} subject={subject!r} cc={cc!r} retries={retries}"  # summary


# 1. Unpack a dict into keyword arguments
payload: Dict[str, Any] = {"to": "a@x.com", "subject": "Hi", "retries": 1}  # from JSON
print(send_email(**payload))  # keys must match parameter names
# Output: to=a@x.com subject='Hi' cc='' retries=1

# 2. Typical errors are TypeErrors - know them
for bad_call in (
    lambda: send_email("a@x.com", subject="Hi", to="b@x.com"),  # same parameter twice
    lambda: send_email("a@x.com", "Hi", colour="red"),  # unknown name
    lambda: send_email("a@x.com"),  # missing required 'subject'
    lambda: send_email("a@x.com", "Hi", "body", "cc@x.com"),  # cc is keyword-only
):
    try:  # run the bad call
        bad_call()  # triggers TypeError
    except TypeError as exc:  # catch and show
        print("TypeError:", exc)  # message explains the problem
# Output:
# TypeError: send_email() got multiple values for argument 'to'
# TypeError: send_email() got an unexpected keyword argument 'colour'
# TypeError: send_email() missing 1 required positional argument: 'subject'
# TypeError: send_email() takes from 2 to 3 positional arguments but 4 were given

# 3. Config pattern: defaults dict overridden by caller options
DEFAULTS: Dict[str, Any] = {"timeout": 5, "retries": 3, "verify": True}  # base config


def make_client(**overrides: Any) -> Dict[str, Any]:
    unknown = set(overrides) - set(DEFAULTS)  # names we do not recognise
    if unknown:  # catch typos early
        raise TypeError(f"unknown options: {sorted(unknown)}")  # clear error
    return {**DEFAULTS, **overrides}  # caller wins over defaults


print(make_client(retries=5))  # override one
# Output: {'timeout': 5, 'retries': 5, 'verify': True}
try:  # typo 'timout'
    make_client(timout=1)  # misspelled
except TypeError as exc:  # caught
    print(exc)  # Output: unknown options: ['timout']

# 4. Inspect which parameters are keyword-only
sig = inspect.signature(send_email)  # read the signature
kw_only = [n for n, p in sig.parameters.items() if p.kind is inspect.Parameter.KEYWORD_ONLY]
print(kw_only)  # Output: ['cc', 'retries']
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: real keyword arguments
def create_user(name, age, city="Pune"):
    ...
create_user(age=25, name="Asha")            # any order
create_user("Asha", 25, city="Delhi")       # mix positional + keyword
```

```javascript
// JavaScript: no keyword arguments; pass ONE options object
function createUser({ name, age, city = "Pune" }) {   // destructuring + defaults
  return `${name} ${age} ${city}`;
}
createUser({ age: 25, name: "Asha" });                // object acts like kwargs
createUser({ name: "Asha", age: 25, city: "Delhi" });
// a typo in a key silently gives undefined
```

Key differences: JS fakes keyword arguments with an options object; typos produce `undefined` silently. Python checks names itself and raises `TypeError` for unknown or duplicate names. Python can also mix positional and keyword in one call.

---

## 🟠 FastAPI Connection
FastAPI itself is built on keyword arguments: query/path/body parameters are matched by NAME from the request to your function parameters. Responses are built with keyword-heavy helpers too (`JSONResponse(content=..., status_code=...)`, `Query(default, ge=1)`).

```python
# FastAPI: parameter NAMES are the API (needs: pip install fastapi)
from typing import Optional  # type hints
from fastapi import FastAPI, Query  # app and query validator
from fastapi.responses import JSONResponse  # custom response

app: FastAPI = FastAPI()  # create app


@app.get("/items/{item_id}")  # item_id comes from the path by name
def read_item(
    item_id: int,  # matched to {item_id}
    q: Optional[str] = None,  # matched to ?q=...
    limit: int = Query(10, ge=1, le=100),  # keyword args configure validation
) -> JSONResponse:
    body = {"item_id": item_id, "q": q, "limit": limit}  # build payload
    return JSONResponse(content=body, status_code=200)  # keywords keep it clear
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Positional argument after a keyword argument
```python
def f(a, b):
    return a, b

# Wrong - SyntaxError: positional argument follows keyword argument
# f(a=1, 2)

# Correct:
f(1, b=2)
f(a=1, b=2)
```

❌ Mistake 2: Giving the same parameter twice
```python
def f(a, b):
    return a, b

# Wrong - TypeError: f() got multiple values for argument 'a'
# f(1, a=2)

# Correct:
f(1, b=2)
```

❌ Mistake 3: Typos swallowed by **kwargs
```python
def connect(host, **options):
    return options

print(connect("db", timout=5))    # {'timout': 5}  - typo silently accepted!

# Correct: list real parameters explicitly, or validate the keys
def connect2(host, *, timeout=5):
    return timeout
# connect2("db", timout=5)  -> TypeError (unexpected keyword)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
def f(a, b=2, *args, c=3, **kw):
    return a, b, args, c, kw

print(f(1))
print(f(1, 2, 3, 4, c=5, d=6))
print(f(b=9, a=8))
print(f(1, 2, 3, b=4))
```

**Answer**: The last line fails. The outputs are:
```
(1, 2, (), 3, {})
(1, 2, (3, 4), 5, {'d': 6})
(8, 9, (), 3, {})
TypeError: f() got multiple values for argument 'b'
```
In the last call, `1, 2, 3` fill `a`, `b` and then `args=(3,)`; `b=4` assigns `b` again, so Python raises TypeError. Anything after `*args` (like `c`) can only be given by keyword.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between an argument and a parameter?
A1: A parameter is the name in the function definition (`def f(x)`). An argument is the value you pass in the call (`f(5)`). Keyword arguments are arguments passed as `name=value`.

Q2: Why prefer keyword arguments for booleans and optional values?
A2: `send(msg, True, False)` is unreadable; `send(msg, urgent=True, retry=False)` documents itself and survives reordering of parameters. Many style guides make such parameters keyword-only.

Q3: What happens if you pass a keyword the function does not define?
A3: `TypeError: got an unexpected keyword argument`, unless the function accepts `**kwargs`, in which case it is collected in the dict.

Q4: How do you force callers to use keywords?
A4: Put a bare `*` in the parameter list: `def f(a, *, b, c=1)`. Everything after the star is keyword-only (next topics 048/049 cover this).

Q5: How does FastAPI use keyword arguments?
A5: It inspects your function signature and matches request path, query, header and body data to parameters by NAME and type annotation, using defaults to decide what is optional.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- A function has many parameters or optional flags
- Passing booleans, numbers or None whose meaning is not obvious
- Wrapping libraries and APIs (OpenAI, Razorpay, SQLAlchemy)

❌ Avoid when:
- The function has one obvious argument (`len(x)`, `abs(x)`)
- Names might change (positional-only protects internal names)
- You accept `**kwargs` just to avoid defining parameters

---

## 📊 Visual Diagram

```
 def create_user(name, age, city="Pune", active=True)

 create_user("Asha", 25, active=False)
              │       │       │
              ▼       ▼       ▼
            name=…  age=…   active=False      city → default "Pune"

 positional (by place) ──► first      keyword (by name) ──► after
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Keyword argument | Passed as name=value | name=value के रूप में दिया गया |
| Positional argument | Passed by position | position से दिया गया |
| Parameter | Name in the definition | definition में लिखा नाम |
| Argument | Value in the call | call में दी गई value |
| Keyword-only | Must be named | नाम से देना ज़रूरी |
| TypeError | Error for wrong call shape | गलत call पर आने वाला error |

---

## ⚡ 3-Line Summary
English: Keyword arguments pass values by name (`f(x=1)`), making calls readable and order-independent. Positional arguments come first; duplicates and unknown names raise `TypeError`. Use a bare `*` to force keyword-only parameters in your own APIs.
Hindi: Keyword arguments नाम से value देते हैं (`f(x=1)`), जिससे call readable और order-free बनती है। Positional पहले आते हैं; duplicate या अनजान नाम पर `TypeError`। अपनी API में bare `*` से keyword-only parameters बनाएँ।

---

## ➡️ Next Topic
**048. Positional Only Parameters** — use `/` to lock parameters so they cannot be passed by name.
