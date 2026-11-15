---

# 167. inspect Module
# हिंदी में: inspect Module (Objects की गहरी जाँच का toolbox)

---

## 🔵 Simple Definition (English)
`inspect` is the standard library toolbox for looking inside live objects: function signatures, source code, class members, call stacks and frames. It builds on the basic introspection builtins and gives structured, reliable answers.

## 🔵 सरल परिभाषा (Hindi)
`inspect` standard library का toolbox है जिससे ज़िंदा objects के अंदर झाँका जाता है: function signatures, source code, class members, call stacks और frames। यह बुनियादी introspection builtins पर बना है और व्यवस्थित, भरोसेमंद जवाब देता है।

---

## 🔴 Problem it Solves
`dir()` and `__dict__` are low level and incomplete. If you want the parameter names and defaults of a function you would have to parse `__code__` by hand, and decorators, classes, partials and builtins each store things differently. `inspect.signature` handles all of these cases. It also solves "who called me", "show me this function's source" and "is this an async function".

## 🔴 यह क्यों बना? (Hindi)
`dir()` और `__dict__` निचले स्तर के और अधूरे हैं। Function के parameter names और defaults चाहिए तो `__code__` हाथ से पढ़ना पड़ता, और decorators, classes, partials, builtins सब अलग तरह से चीज़ें रखते हैं। `inspect.signature` ये सब cases संभालता है। यह "मुझे किसने call किया", "इस function का source दिखाओ" और "क्या यह async function है" जैसे सवाल भी हल करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → inspect.signature(fn) reads __code__, __defaults__, __kwdefaults__, __annotations__
Step 2 → It returns a Signature holding Parameter objects (name, kind, default, annotation)
Step 3 → kinds: POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD, VAR_POSITIONAL (*args),
           KEYWORD_ONLY, VAR_KEYWORD (**kwargs)
Step 4 → sig.bind(*args, **kw) checks a call without making it
Step 5 → getmembers / isfunction / isclass / iscoroutinefunction classify objects
Step 6 → currentframe / stack walk the live call stack (frame.f_back, f_lineno)
Step 7 → getsource reads the original .py file (fails for exec'd or built-in code)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → inspect.signature(fn) __code__, __defaults__, __kwdefaults__, __annotations__ पढ़ता है
Step 2 → वह Signature लौटाता है जिसमें Parameter objects (name, kind, default, annotation) होते हैं
Step 3 → kinds: POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD, VAR_POSITIONAL (*args),
           KEYWORD_ONLY, VAR_KEYWORD (**kwargs)
Step 4 → sig.bind(*args, **kw) call किए बिना जाँचता है कि call सही है या नहीं
Step 5 → getmembers / isfunction / isclass / iscoroutinefunction objects को वर्गीकृत करते हैं
Step 6 → currentframe / stack live call stack पर चलते हैं (frame.f_back, f_lineno)
Step 7 → getsource मूल .py file पढ़ता है (exec किए या built-in code पर fail होता है)
```

---

## 🟡 Real World Example
A tiny dependency-injection container for a microservice reads each handler's parameter annotations and passes the right service objects (DB, cache). A Slack bot framework uses `inspect.signature` to check that user-registered command functions take the right arguments. A logging helper uses `inspect.stack()` to add the caller's function name and line number to a log line.

## 🟡 Real Example Hindi mein
Microservice का छोटा dependency-injection container हर handler के parameter annotations पढ़कर सही service objects (DB, cache) पास करता है। Slack bot framework `inspect.signature` से जाँचता है कि user के register किए command functions सही arguments लेते हैं। Logging helper `inspect.stack()` से log line में caller का function नाम और line number जोड़ता है।

---

## 💻 Code Example — Basic
```python
# Basic inspect examples
import inspect                                    # the inspect module


def pay(amount: int, currency: str = "INR", *, retries: int = 3) -> bool:   # sample function
    """Charge a customer."""                      # docstring
    return True


sig: inspect.Signature = inspect.signature(pay)   # parameter details
print(sig)                                        # (amount: int, currency: str = 'INR', *, retries: int = 3) -> bool
for name, p in sig.parameters.items():            # loop over parameters
    print(name, p.kind.name, p.default is inspect.Parameter.empty)   # kind and "is required"
print(inspect.getdoc(pay))                        # clean docstring
print(inspect.isfunction(pay), inspect.isclass(pay), inspect.iscoroutinefunction(pay))
print(inspect.getsource(pay).splitlines()[0])     # first line of its source code
print(inspect.getmodule(pay).__name__)            # module that defines it

# Output:
# (amount: int, currency: str = 'INR', *, retries: int = 3) -> bool
# amount POSITIONAL_OR_KEYWORD True
# currency POSITIONAL_OR_KEYWORD False
# retries KEYWORD_ONLY False
# Charge a customer.
# True False False
# def pay(amount: int, currency: str = "INR", *, retries: int = 3) -> bool:   # sample function
# __main__
```

## 💻 Code Example — Advanced
```python
# Production style: tiny dependency injector + argument binding + caller info
import inspect                                    # signature, stack
from typing import Any, Callable                  # typing


class Db: ...                                     # a service
class Cache: ...                                  # another service

SERVICES: dict[type, Any] = {Db: Db(), Cache: Cache()}   # container: type -> instance


def inject(fn: Callable[..., Any]) -> Any:
    """Call fn after filling parameters from annotations (what FastAPI Depends does)."""
    kwargs: dict[str, Any] = {}                   # arguments we will pass
    for name, p in inspect.signature(fn).parameters.items():   # read each parameter
        if p.annotation in SERVICES:              # annotation is a known service
            kwargs[name] = SERVICES[p.annotation] # inject the instance
        elif p.default is inspect.Parameter.empty:   # required but unknown
            raise TypeError(f"cannot inject '{name}'")   # clear error
    return fn(**kwargs)                           # call with injected values


def handler(db: Db, cache: Cache, page: int = 1) -> str:   # page keeps its default
    return f"{type(db).__name__}+{type(cache).__name__} page={page}"


print(inject(handler))                            # Db+Cache page=1


def bad(user_id: int) -> None: ...                # int is not a service
try:                                              # injection fails cleanly
    inject(bad)
except TypeError as e:
    print("Error:", e)

def create(name: str, age: int = 18) -> str:      # sample target
    return f"{name}:{age}"

bound = inspect.signature(create).bind("Asha")    # check arguments without calling
bound.apply_defaults()                            # fill in defaults
print(bound.arguments)                            # {'name': 'Asha', 'age': 18}
try:
    inspect.signature(create).bind()              # missing required argument
except TypeError as e:
    print("Error:", e)

async def job() -> None: ...                      # coroutine function
print(inspect.iscoroutinefunction(job), inspect.iscoroutinefunction(create))   # True False

def who_called() -> str:
    frame = inspect.currentframe().f_back         # frame of the caller
    return f"{frame.f_code.co_name} line {frame.f_lineno}"   # name and line number

def outer() -> str:
    return who_called()                           # called from here

print(outer().split(" line ")[0])                 # outer

# Output:
# Db+Cache page=1
# Error: cannot inject 'user_id'
# {'name': 'Asha', 'age': 18}
# Error: missing a required argument: 'name'
# True False
# outer
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Parameter names | `inspect.signature(f).parameters` | parse `f.toString()` (fragile) |
| Parameter count | `len(sig.parameters)` | `f.length` |
| Function source | `inspect.getsource(f)` | `f.toString()` |
| Async check | `inspect.iscoroutinefunction(f)` | `f.constructor.name === "AsyncFunction"` |
| Call stack | `inspect.stack()` | `new Error().stack` (text) |

```python
# Python way
import inspect
def pay(a: int, b: int = 2) -> int: return a + b
print(list(inspect.signature(pay).parameters))  # ['a', 'b']
```
```javascript
// JavaScript way
function pay(a, b = 2) { return a + b; }
console.log(pay.length);                        // 1 (only parameters before the first default!)
console.log(pay.toString());                    // you must parse this text to get the names
```

Key difference: Python gives structured parameter data (name, kind, default, annotation). JavaScript gives only a count that even stops at the first default, and frameworks such as Angular parse `toString()`.

---

## 🟠 FastAPI Connection
FastAPI uses `inspect.signature` on every route and dependency at startup to decide where each parameter comes from. It also uses `iscoroutinefunction` to choose between awaiting the handler (`async def`) and running it in a threadpool (`def`).

```python
# FastAPI: how it uses inspect.signature to build dependencies
import inspect                                    # signature
from fastapi import Depends, FastAPI              # app + DI
from fastapi.testclient import TestClient         # in-process client

app: FastAPI = FastAPI()                          # create app


def get_user() -> str:                            # a dependency
    return "asha"


@app.get("/me")                                   # route
def me(user: str = Depends(get_user), verbose: bool = False) -> dict[str, object]:
    return {"user": user, "verbose": verbose}


sig = inspect.signature(me)                       # FastAPI does exactly this at startup
for n, p in sig.parameters.items():               # inspect each parameter
    print(n, type(p.default).__name__, p.annotation.__name__)   # Depends / bool
print(inspect.iscoroutinefunction(me))            # False -> FastAPI runs it in a threadpool

client: TestClient = TestClient(app)              # test client
print(client.get("/me", params={"verbose": "true"}).json())   # {'user': 'asha', 'verbose': True}

# Output:
# user Depends str
# verbose bool bool
# False
# {'user': 'asha', 'verbose': True}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Decorators without `functools.wraps`
✅ Correct: use `wraps` so `signature` and `__name__` stay correct

```python
import inspect, functools
def deco(f):
    def w(*a, **k): return f(*a, **k)
    return w
def deco2(f):
    @functools.wraps(f)
    def w(*a, **k): return f(*a, **k)
    return w
@deco
def f(a: int, b: int = 2): ...
@deco2
def g(a: int, b: int = 2): ...
print(inspect.signature(f))                     # (*a, **k)
print(inspect.signature(g))                     # (a: int, b: int = 2)
```

❌ Mistake 2: Using `inspect.stack()` in hot paths
✅ Correct: it reads source lines for every frame and is slow; use `sys._getframe(1)` or `inspect.currentframe()` when you only need the caller

❌ Mistake 3: Calling `getsource` on code defined in the REPL / `exec`
✅ Correct: wrap in `try/except (OSError, TypeError)`

❌ Mistake 4: Keeping frame objects in variables
✅ Correct: `del frame` (frames hold references to all locals and can create cycles and leaks)

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import inspect, functools
def deco(f):
    def w(*a, **k): return f(*a, **k)
    return w
def deco2(f):
    @functools.wraps(f)
    def w(*a, **k): return f(*a, **k)
    return w
@deco
def f(a: int, b: int = 2): ...
@deco2
def g(a: int, b: int = 2): ...
print(inspect.signature(f)); print(inspect.signature(g))
print(f.__name__, g.__name__)
```
Answer (verified on 3.13):
```
(*a, **k)
(a: int, b: int = 2)
w g
```
`wraps` copies `__name__`, `__doc__`, `__wrapped__` etc. and `signature` follows `__wrapped__` to the original function. Without it you see the wrapper's `(*a, **k)`, and FastAPI would then think the endpoint takes arbitrary args and break parameter parsing.

---

## ⚫ Interview Questions + Answers

Q1: How does FastAPI know which parameters are query parameters?
A1: It calls `inspect.signature(endpoint)`, then for each parameter checks the annotation and default: names found in the path template are path params, `Depends(...)` defaults are dependencies, Pydantic models are body, and simple types are query params.

Q2: `inspect.signature` vs `f.__code__.co_varnames`?
A2: `co_varnames` includes local variables too and has no defaults, kinds or annotations. `signature` gives only parameters with full details and follows `__wrapped__`.

Q3: How do you check without calling that a call would be valid?
A3: `sig.bind(*args, **kwargs)` raises `TypeError` for missing or extra arguments. `bind_partial` allows missing ones.

Q4: What are Parameter kinds?
A4: `POSITIONAL_ONLY` (before `/`), `POSITIONAL_OR_KEYWORD`, `VAR_POSITIONAL` (`*args`), `KEYWORD_ONLY` (after `*`), `VAR_KEYWORD` (`**kwargs`).

Q5: What is a frame?
A5: An object for one function call on the stack: it has `f_locals`, `f_globals`, `f_code`, `f_lineno` and `f_back` (the caller). Debuggers, tracebacks and logging use it.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building frameworks, DI containers, decorators that adapt to signatures
- Validating callbacks before registering them
- Debug and logging tools needing caller info

❌ Avoid when:
- App logic where you already know the types
- Performance-critical loops (cache the results)
- Source retrieval in packaged apps without `.py` files

---

## 📊 Visual Diagram
```
 def pay(amount: int, currency: str = "INR", *, retries: int = 3) -> bool

 inspect.signature(pay)
   ├─ amount    POSITIONAL_OR_KEYWORD  no default   int
   ├─ currency  POSITIONAL_OR_KEYWORD  "INR"        str
   ├─ retries   KEYWORD_ONLY           3            int
   └─ return annotation: bool
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Signature | Description of parameters | parameters का विवरण |
| Parameter | One argument slot with kind and default | एक argument की जगह |
| Frame | One active function call on the stack | stack पर एक चालू function call |
| `bind` | Check arguments against signature | arguments को signature से मिलाना |
| `wraps` | Decorator that preserves metadata | metadata बचाने वाला decorator |
| Coroutine function | `async def` function | `async def` वाला function |

---

## ⚡ 3-Line Summary
English: `inspect` gives structured information about live objects: signatures, members, source and frames. FastAPI's dependency injection is built on `inspect.signature`. Always use `functools.wraps` so signatures survive decorators.
Hindi: `inspect` ज़िंदा objects की व्यवस्थित जानकारी देता है: signatures, members, source और frames। FastAPI का dependency injection `inspect.signature` पर बना है। Decorators के बाद भी signature बचाने के लिए हमेशा `functools.wraps` लगाएँ।

---

## ➡️ Next Topic
**168. getattr/setattr/hasattr/delattr** — reading and writing attributes by string name.
