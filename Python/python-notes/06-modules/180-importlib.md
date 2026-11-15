---

# 180. importlib
# हिंदी में: importlib (string नाम से module import करना)

---

## 🔵 Simple Definition (English)
`importlib` is the standard library module that exposes Python's import machinery as functions. With `importlib.import_module("pkg.mod")` you import a module using a string name decided at runtime. It can also reload a module, find a module without importing it, and load a module from any file path.

## 🔵 सरल परिभाषा (Hindi)
`importlib` standard library का module है जो Python की import machinery को functions के रूप में देता है। `importlib.import_module("pkg.mod")` से runtime पर तय हुए string नाम से module import होता है। यह module reload कर सकता है, बिना import किए खोज सकता है और किसी भी file path से load कर सकता है।

---

## 🔴 Problem it Solves
The `import` statement needs the name written in the source code. Plugin systems, config-driven apps ("use backend `redis`") and test tools only know the name at runtime. `importlib` lets code choose what to import dynamically, without `exec` or `__import__` hacks.

## 🔴 यह क्यों बना? (Hindi)
`import` statement में नाम source code में लिखा होना चाहिए। Plugin systems, config-driven apps ("backend `redis` इस्तेमाल करो") और test tools को नाम runtime पर ही पता चलता है। `importlib` बिना `exec` या `__import__` hacks के dynamic import देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → importlib.import_module("a.b")  : same machinery as `import a.b`
Step 2 → Checks sys.modules; else finds a spec via sys.path finders
Step 3 → Loader executes the file once; module object stored in sys.modules
Step 4 → Returns the LEAF module (a.b), unlike __import__ which returns top "a"
Step 5 → importlib.reload(m) re-executes the source INTO the same module object
Step 6 → util.spec_from_file_location + module_from_spec + exec_module : load by path
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → importlib.import_module("a.b") : वही machinery जो `import a.b` की है
Step 2 → sys.modules देखता है; नहीं तो sys.path के finders से spec खोजता है
Step 3 → Loader file एक बार चलाता है; module sys.modules में रखा जाता है
Step 4 → सबसे अंदर वाला module (a.b) लौटाता है; __import__ top "a" देता है
Step 5 → importlib.reload(m) source को उसी module object में दोबारा चलाता है
Step 6 → util.spec_from_file_location + module_from_spec + exec_module : path से load
```

---

## 🟡 Real World Example
A Razorpay-style payments service reads `PAYMENT_BACKEND=payments.stripe_backend` from environment and loads it with `import_module`, so adding a new gateway needs no code change in the core. Django loads `INSTALLED_APPS` and FastAPI plugin loaders scan a `plugins/` folder the same way. An AI app picks `models.openai_llm` or `models.local_llm` from YAML.

## 🟡 Real Example Hindi mein
Razorpay जैसी payments service environment से `PAYMENT_BACKEND=payments.stripe_backend` पढ़कर `import_module` से load करती है, इसलिए नया gateway जोड़ने पर core code नहीं बदलता। Django `INSTALLED_APPS` ऐसे ही load करता है। AI app YAML से `models.openai_llm` या `models.local_llm` चुनती है।

---

## 💻 Code Example — Basic
```python
# Basic importlib examples - every line commented
import importlib  # the module itself
import importlib.util  # find_spec and file loading live here

name: str = "json"  # a name known only at runtime
mod = importlib.import_module(name)  # same as `import json`
print(mod.dumps({"a": 1}))  # use it like a normal module
# Output: {"a": 1}

sub = importlib.import_module("os.path")  # dotted names work, returns the leaf
print(sub.__name__)  # posixpath on macOS/Linux (ntpath on Windows)
# Output: posixpath

print(importlib.util.find_spec("json") is not None)  # does it exist? (no import done)
# Output: True
print(importlib.util.find_spec("no_such_module"))  # missing -> None
# Output: None

try:  # importing a missing module raises
    importlib.import_module("no_such_module")  # string name, not found
except ModuleNotFoundError as exc:  # specific ImportError subclass
    print(repr(exc))  # show it
    print(exc.name)  # the missing module name
# Output: ModuleNotFoundError("No module named 'no_such_module'")
# Output: no_such_module
```

## 💻 Code Example — Advanced
```python
# Production plugin loader: by dotted name, by file path, with reload and clear errors.
import importlib  # import_module / reload
import importlib.util  # file-based loading
import sys  # sys.modules / sys.path
import tempfile  # sandbox
from pathlib import Path  # files
from types import ModuleType  # return type
from typing import Callable, Dict  # type hints


def load_backend(dotted: str) -> Callable[[str], str]:
    """Load 'package.module:function' and return the function."""
    module_name, _, func_name = dotted.partition(":")  # split "mod:func"
    try:
        module = importlib.import_module(module_name)  # dynamic import
    except ModuleNotFoundError as exc:  # config typo -> clear message
        raise RuntimeError(f"backend module not found: {module_name}") from exc
    func = getattr(module, func_name, None)  # look up the function
    if not callable(func):  # validate the contract
        raise RuntimeError(f"{dotted} is not callable")
    return func  # ready to use


def load_from_path(path: Path, name: str) -> ModuleType:
    """Load a .py file by path without touching sys.path."""
    spec = importlib.util.spec_from_file_location(name, path)  # describe the file
    if spec is None or spec.loader is None:  # safety check
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)  # empty module object
    spec.loader.exec_module(module)  # run the file inside it
    return module  # NOT in sys.modules unless you add it


with tempfile.TemporaryDirectory() as tmp:  # sandbox
    Path(tmp, "pay_stripe.py").write_text("def pay(x):\n    return f'stripe:{x}'\n")
    Path(tmp, "pay_upi.py").write_text("def pay(x):\n    return f'upi:{x}'\n")
    sys.path.insert(0, tmp)  # make the folder importable
    try:
        registry: Dict[str, Callable[[str], str]] = {  # config-driven selection
            name: load_backend(f"{name}:pay") for name in ("pay_stripe", "pay_upi")
        }
        print(registry["pay_upi"]("100"))  # call the loaded function
        # Output: upi:100
        try:
            load_backend("pay_missing:pay")  # bad config
        except RuntimeError as exc:
            print(exc)
        # Output: backend module not found: pay_missing

        # reload: change the file, then reload the SAME module object
        mod = importlib.import_module("pay_upi")  # cached module
        Path(tmp, "pay_upi.py").write_text("def pay(x):\n    return f'upi-v2:{x}'\n")
        importlib.invalidate_caches()  # let finders see the changed file
        importlib.reload(mod)  # re-executes the source
        print(mod.pay("5"))  # new behaviour
        # Output: upi-v2:5

        loaded = load_from_path(Path(tmp, "pay_stripe.py"), "dyn_stripe")  # by path
        print(loaded.pay("7"), "dyn_stripe" in sys.modules)  # not registered globally
        # Output: stripe:7 False
    finally:
        sys.path.remove(tmp)  # cleanup
        for n in ("pay_stripe", "pay_upi"):
            sys.modules.pop(n, None)  # forget temp modules
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import importlib
mod = importlib.import_module("plugins.csv_export")   # name from config
mod.run()
```

```javascript
// JavaScript: dynamic import() returns a Promise
const name = "./plugins/csv_export.js";               // name from config
const mod = await import(name);                        // async
mod.run();
// CommonJS: const mod = require(name);   (sync)
```

Key difference: JS dynamic `import()` is asynchronous (a Promise); Python's `import_module` is synchronous and returns the module directly.

---

## 🟠 FastAPI Connection
Large FastAPI apps auto-register routers from a `routers/` package: list the modules with `pkgutil`, import each with `importlib`, and call `app.include_router`. Uvicorn itself uses `importlib` to turn `"app.main:app"` into the app object.

```python
# Auto-register routers (needs: pip install fastapi)
import importlib  # dynamic import
from fastapi import APIRouter, FastAPI  # framework

app: FastAPI = FastAPI()  # the application


def register(app: FastAPI, module_names: list[str]) -> None:
    for name in module_names:  # e.g. ["app.routers.users", "app.routers.orders"]
        module = importlib.import_module(name)  # import by string
        router: APIRouter = module.router  # convention: each module has `router`
        app.include_router(router)  # attach it
# Usage: register(app, ["app.routers.users", "app.routers.orders"])
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting `reload` to update `from x import y` names
```python
# Wrong - 'y' still points to the OLD function after reload:
# from pay_upi import pay ; importlib.reload(pay_upi) ; pay(...)  -> old code

# Correct: call through the module: mod = import_module("pay_upi"); mod.pay(...)
```

❌ Mistake 2: Importing user-supplied names without validation
```python
# Wrong - security risk, runs arbitrary code:
# importlib.import_module(request.query_params["mod"])

# Correct - allow-list:
ALLOWED: set[str] = {"plugins.csv_export", "plugins.json_export"}
```

❌ Mistake 3: Forgetting `invalidate_caches()` after creating files at runtime
```python
# Wrong: write new plugin file then import -> sometimes ModuleNotFoundError
# Correct: importlib.invalidate_caches() before importing it
```

---

## 🧠 Tricky Interview Question

**Q**: What is the difference in the results?

```python
import importlib
a = __import__("os.path")
b = importlib.import_module("os.path")
print(a.__name__, b.__name__)
```

**Answer**:
```
os posixpath
```
`__import__("os.path")` returns the TOP-level package `os` (like `import os.path` binds `os`). `importlib.import_module("os.path")` returns the leaf module itself. That is the main reason to prefer `import_module`.

---

## ⚫ Interview Questions + Answers

Q1: `import_module` vs `__import__`?
A1: `import_module` returns the module you named; `__import__` returns the top package unless `fromlist` is given. Docs recommend `import_module`.

Q2: What does `importlib.reload` do exactly?
A2: Re-executes the module's source into the same module object. Existing references to old functions/classes stay unchanged, and `from m import x` names are not refreshed. Use it for development, not production hot-swap.

Q3: How do I check a package is installed without importing it?
A3: `importlib.util.find_spec("name") is not None`. For installed distribution versions use `importlib.metadata.version("pkg")`.

Q4: How do I load a `.py` file that is not on `sys.path`?
A4: `spec_from_file_location`, `module_from_spec`, then `spec.loader.exec_module(module)`.

Q5: What is `importlib.resources` for?
A5: Reading data files shipped inside a package (`importlib.resources.files("pkg").joinpath("data.json").read_text()`), working even from zip installs.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Plugin systems and config-driven backends
- Optional dependencies (`find_spec` check)
- Dev tools that reload code, or loading a script by path

❌ Avoid when:
- A normal `import` works (it is clearer and analyzable)
- The name comes from untrusted users
- You think `reload` is production-safe

---

## 📊 Visual Diagram

```
 config: "payments.upi"  (a string)
          │
          ▼
 importlib.import_module("payments.upi")
          │  cache hit? ── yes ─► return sys.modules["payments.upi"]
          ▼ no
   find spec (sys.path finders) ─► loader.exec_module ─► sys.modules
          │
          ▼
   module object ──► getattr(module, "pay")(...)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `import_module` | Import by string name | string से import |
| Spec | Description of how to load | load करने का विवरण |
| Loader | Object that executes module code | module चलाने वाला |
| Reload | Re-run a loaded module | दोबारा चलाना |
| Plugin | Add-on loaded at runtime | runtime पर जुड़ने वाला हिस्सा |
| `find_spec` | Locate without importing | बिना import खोजना |

---

## ⚡ 3-Line Summary
English: `importlib.import_module("a.b")` imports by a runtime string and returns the leaf module. Use `find_spec` to check existence, `reload` for dev, and file-path loading for plugins. Never import unvalidated user input.
Hindi: `importlib.import_module("a.b")` runtime string से import करता है और अंदर वाला module लौटाता है। मौजूद है या नहीं जाँचने के लिए `find_spec`, dev में `reload`, plugins के लिए path loading। User के बिना जाँचे नाम कभी import न करें।

---

## ➡️ Next Topic
**181. `__all__` Variable** — control what `from module import *` exposes.
