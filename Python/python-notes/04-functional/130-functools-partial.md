---

# 130. functools.partial
# हिंदी में: functools.partial (कुछ arguments पहले से भर देना)

---

## 🔵 Simple Definition (English)
`partial(func, *args, **kwargs)` creates a new callable that behaves like `func` with some arguments already filled in. When you call it, you supply only the remaining arguments. It is "function with presets".

## 🔵 सरल परिभाषा (Hindi)
`partial(func, *args, **kwargs)` एक नया callable बनाता है जो `func` जैसा ही है पर कुछ arguments पहले से भरे हुए हैं। इसे बुलाते समय सिर्फ बाकी arguments देने होते हैं। यह "presets वाला function" है।

---

## 🔴 Problem it Solves
Callbacks, thread targets, `map`, `sorted(key=...)` and framework hooks accept a function with a FIXED call shape (for example one argument). But your function needs extra settings. A `lambda x: f(x, 2)` works but is anonymous, harder to debug and late-binds variables. `partial` is explicit, picklable, and has a readable repr.

## 🔴 यह क्यों बना? (Hindi)
Callbacks, thread targets, `map`, `sorted(key=...)` और framework hooks ऐसा function माँगते हैं जिसकी call shape तय हो (जैसे एक argument)। पर आपके function को अतिरिक्त settings चाहिए। `lambda x: f(x, 2)` चलता है पर anonymous है, debug करना कठिन है और variables late-bind होते हैं। `partial` साफ है, picklable है और उसका repr पढ़ने लायक है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → p = partial(f, a, k=1) stores f, args (a,) and keywords {k: 1}
Step 2 → p(b, j=2) combines: f(a, b, k=1, j=2)
Step 3 → Stored positional args go FIRST; new positional args come after
Step 4 → New keyword args override stored keywords with the same name
Step 5 → p.func, p.args, p.keywords expose what was stored
Step 6 → partial objects can be pickled and nested; use partialmethod in classes

partial(int, base=2)("101")  ->  int("101", base=2)  ->  5
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → p = partial(f, a, k=1) f, args (a,) और keywords {k: 1} सहेजता है
Step 2 → p(b, j=2) मिलाकर बनाता है: f(a, b, k=1, j=2)
Step 3 → सहेजे positional args पहले आते हैं; नए positional बाद में
Step 4 → नए keyword args उसी नाम के सहेजे keywords को override करते हैं
Step 5 → p.func, p.args, p.keywords दिखाते हैं कि क्या सहेजा है
Step 6 → partial pickle हो सकता है और nest हो सकता है; class में partialmethod use करें
```

---

## 🟡 Real World Example
A Swiggy notification module has `send(channel, sender, to, text)`. Services create `send_sms = partial(send, "sms", "SWIGGY")`. A Razorpay client builds `post_json = partial(requests.post, headers=AUTH, timeout=5)` once. A thread pool runs `partial(process, retries=3)` for each file. A Tkinter/GUI button callback binds the row id with `partial(on_click, row_id)`.

## 🟡 Real Example Hindi mein
Swiggy के notification module में `send(channel, sender, to, text)` है। Services `send_sms = partial(send, "sms", "SWIGGY")` बनाती हैं। Razorpay client `post_json = partial(requests.post, headers=AUTH, timeout=5)` एक बार बनाता है। Thread pool हर file के लिए `partial(process, retries=3)` चलाता है। GUI button callback में row id `partial(on_click, row_id)` से बाँधी जाती है।

---

## 💻 Code Example — Basic
```python
# Basic partial
from functools import partial                      # the tool


def power(base: int, exp: int) -> int:
    return base ** exp                             # simple math function


square = partial(power, exp=2)                     # fix exp as a keyword
cube = partial(power, exp=3)                       # another preset
two_to = partial(power, 2)                         # fix base as positional
print(square(5), cube(2), two_to(10))              # 25 8 1024

binary = partial(int, base=2)                      # int("101", base=2)
print(binary("101"), list(map(binary, ["1", "10", "11"])))   # works with map

print(square.func.__name__, square.args, square.keywords)    # inspect what is stored
print(partial(power, exp=2)(3, exp=4))             # new keyword overrides the stored one

sort_desc = partial(sorted, reverse=True)          # sorted with reverse preset
print(sort_desc([3, 1, 2]))                        # [3, 2, 1]

lam = [lambda x: power(x, i) for i in range(3)]    # lambda late-binding trap
par = [partial(power, exp=i) for i in range(3)]    # partial freezes i NOW
print([f(2) for f in lam], [f(2) for f in par])    # [4, 4, 4] vs [1, 2, 4]

# Output:
# 25 8 1024
# 5 [1, 2, 3]
# power () {'exp': 2}
# 81
# [3, 2, 1]
# [4, 4, 4] [1, 2, 4]
```

## 💻 Code Example — Advanced
```python
# Production style: pre-configured API client + thread pool + pickling + partialmethod
import pickle                                      # prove partial is picklable
from concurrent.futures import ThreadPoolExecutor  # run jobs in threads
from functools import partial, partialmethod       # presets for functions and methods
from typing import Callable                        # type for callables


def send(channel: str, sender: str, to: str, text: str, retries: int = 1) -> str:
    """Pretend notification sender."""
    return f"{channel}/{sender} -> {to}: {text} (retries={retries})"


send_sms: Callable[..., str] = partial(send, "sms", "SWIGGY", retries=3)    # team-wide preset
send_otp = partial(send_sms, text="Your OTP is 4821")      # partial of a partial
print(send_sms("98100", "Order out for delivery"))         # only `to` and `text` left
print(send_otp("98765"))                                   # only `to` left

with ThreadPoolExecutor(max_workers=2) as pool:            # executor needs one-arg callables
    results = list(pool.map(send_otp, ["111", "222", "333"]))   # same preset, many users
print(len(results), results[2])                            # 3 results, order preserved

restored = pickle.loads(pickle.dumps(partial(send, "email", "APP")))     # round-trip
print(restored("a@b.com", "Hi"))                           # still works after pickling


class Logger:
    def log(self, level: str, msg: str) -> str:
        return f"[{level}] {msg}"                          # instance method

    info = partialmethod(log, "INFO")                      # method with preset arg
    error = partialmethod(log, "ERROR")                    # another one


lg = Logger()                                              # create object
print(lg.info("started"), lg.error("boom"))                # bound correctly with self


def retry_call(fn: Callable[[], str], times: int = 2) -> str:
    """Accepts ZERO-argument callables: perfect target for partial."""
    last: Exception | None = None                          # remember the last error
    for _ in range(times):                                 # try several times
        try:
            return fn()                                    # call without args
        except ValueError as e:
            last = e                                       # store failure
    raise RuntimeError(f"gave up: {last}")                 # report the final error


print(retry_call(partial(send, "sms", "APP", "1", "ok")))  # bind ALL args, call later

# Output:
# sms/SWIGGY -> 98100: Order out for delivery (retries=3)
# sms/SWIGGY -> 98765: Your OTP is 4821 (retries=3)
# 3 sms/SWIGGY -> 333: Your OTP is 4821 (retries=3)
# email/APP -> a@b.com: Hi (retries=1)
# [INFO] started [ERROR] boom
# sms/APP -> 1: ok (retries=1)
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Pre-fill args | `partial(f, a, k=1)` | `f.bind(null, a)` (positional only) |
| Keyword presets | yes | no keyword args (use object params) |
| Currying | not built in | libraries (lodash `curry`) |
| Pickle/serialize | works | functions not serializable |
| Inspect | `.func .args .keywords` | none |

```python
# Python way
from functools import partial
greet = partial("{}, {}!".format, "Hello")         # fix the first argument
print(greet("Asha"))                               # Hello, Asha!
```
```javascript
// JavaScript way
const greet = (hello, name) => `${hello}, ${name}!`;
const hi = greet.bind(null, "Hello");              // bind pre-fills from the left
console.log(hi("Asha"));                           // Hello, Asha!
```

Key difference: `bind` also fixes `this` (hence `null`) and only supports positional arguments; Python's `partial` also presets keyword arguments, and you can inspect it.

---

## 🟠 FastAPI Connection
FastAPI's `Depends(...)` needs a callable without extra required arguments. When a dependency needs configuration (a role name, a limit), you can build it with `partial` or a factory. `partial` is also what you pass to `BackgroundTasks.add_task` and to `run_in_threadpool` when a function needs extra fixed args.

```python
# FastAPI example — configurable dependency with partial
from functools import partial                      # presets
from fastapi import Depends, FastAPI, HTTPException   # app, DI, errors
from fastapi.testclient import TestClient          # in-process test client

app: FastAPI = FastAPI()                           # create app


def check_role(required: str, role: str = "guest") -> str:
    if role != required:                           # role passed as ?role=...
        raise HTTPException(status_code=403, detail=f"{required} only")
    return role                                    # allowed


admin_only = partial(check_role, "admin")          # preset the required role


@app.get("/admin")                                 # GET /admin?role=admin
def admin_page(role: str = Depends(admin_only)) -> dict[str, str]:
    return {"role": role}                          # reached only when allowed


c = TestClient(app)                                # test it
print(c.get("/admin", params={"role": "admin"}).status_code, c.get("/admin").status_code)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting new positional args to fill the "middle"
✅ Correct: partial fixes arguments from the LEFT; use keywords for others

```python
from functools import partial
def f(a, b, c): return (a, b, c)
# Wrong: trying to fix b only with positional  -> partial(f, 2) fixes `a`
print(partial(f, 2)(3, 4))        # (2, 3, 4)
# Right: keyword preset
print(partial(f, b=2)(1, c=3))    # (1, 2, 3)
```

❌ Mistake 2: Mutable default values as presets
✅ Correct: build the mutable object inside the function

```python
from functools import partial
def add(x, bag): bag.append(x); return bag
# Wrong — the SAME list is shared by every call
p = partial(add, bag=[])
p(1); print(p(2))      # [1, 2]  <- state leaked
```

❌ Mistake 3: Using `partial` where a clear `def` is better
✅ Correct: if the preset needs logic or a docstring, write a small function

```python
# Wrong: heavy logic hidden in nested partials
# Right: def send_sms(to, text): return send("sms", "APP", to, text)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from functools import partial
def f(a, b, c=0):
    return a, b, c

p = partial(f, 1, c=5)
print(p(2))
print(p(2, c=9))
q = partial(p, 7)
print(q())
print(partial(f, 1, 2)(3))
```
Answer: `(1, 2, 5)`; then `(1, 2, 9)` because a new keyword overrides the stored one; then `(1, 7, 5)`: `partial(p, 7)` flattens into `f(1, 7, c=5)` (nested partials are merged); and finally `(1, 2, 3)`: the third positional argument fills `c`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `partial` and a lambda?
A1: Both freeze arguments. `partial` evaluates presets immediately (no late binding), has inspectable `.func/.args/.keywords`, is picklable and has a clear repr. A lambda is more flexible (can compute things) but late-binds variables and is anonymous.

Q2: What is currying and is `partial` currying?
A2: Currying turns `f(a, b, c)` into `f(a)(b)(c)`. `partial` is partial application: fix some arguments now, the rest later in one call. They are related but not identical.

Q3: What is `partialmethod`?
A3: A `partial` for methods in a class body. Normal `partial` objects are not descriptors, so they don't receive `self`. `partialmethod` binds correctly.

Q4: Does `partial` keep the original function's name?
A4: No: the partial object has no `__name__` or `__doc__` by default (use `p.func.__name__`). Use `functools.update_wrapper(p, f)` if tools need them.

Q5: Where is `partial` common in async code?
A5: `loop.run_in_executor(None, partial(blocking_fn, arg, flag=True))` because `run_in_executor` accepts only positional args. `asyncio.to_thread` accepts args directly.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Callbacks, executors and `map` require fewer arguments
- You reuse the same configuration (headers, timeouts, channel)
- You need picklable callables (multiprocessing)

❌ Avoid when:
- A named `def` with a docstring is clearer
- You need to compute presets at call time (use a lambda or closure)
- Presets are mutable objects

---

## 📊 Visual Diagram
```
def send(channel, sender, to, text)

send_sms = partial(send, "sms", "SWIGGY")
              │       │      └──── fixed (left to right)
              │       └─ fixed
              └─ original function

send_sms("98100", "Hi")  ==>  send("sms", "SWIGGY", "98100", "Hi")
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Partial application | Fix some args now | कुछ args अभी तय करना |
| Currying | One-arg-at-a-time functions | एक-एक argument लेने वाले functions |
| Preset | Pre-filled value | पहले से भरी value |
| Callback | Function passed to be called later | बाद में बुलाने के लिए दिया function |
| Late binding | Variable read at call time | Call के समय variable पढ़ना |
| partialmethod | partial for class methods | Class methods के लिए partial |

---

## ⚡ 3-Line Summary
English: `partial(f, *a, **k)` returns a callable with those arguments pre-filled; later arguments are appended and keywords can override. It avoids lambda's late-binding problem, is picklable and inspectable. Use `partialmethod` inside classes.
Hindi: `partial(f, *a, **k)` ऐसा callable देता है जिसमें ये arguments पहले से भरे हैं; बाद के arguments जुड़ते हैं और keywords override हो सकते हैं। यह lambda की late-binding समस्या से बचाता है, picklable और inspectable है। Class के अंदर `partialmethod` use करें।

---

## ➡️ Next Topic
**131. functools.reduce** — fold a sequence into a single value and know when NOT to.
