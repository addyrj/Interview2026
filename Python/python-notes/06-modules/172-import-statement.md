---

# 172. import Statement
# हिंदी में: import Statement (दूसरे module का code इस्तेमाल करना)

---

## 🔵 Simple Definition (English)
`import` loads a module (a `.py` file or package), runs it once, caches it in `sys.modules`, and binds a name to it in your current scope. Later imports of the same module reuse the cached object and do not run the file again.

## 🔵 सरल परिभाषा (Hindi)
`import` किसी module (`.py` file या package) को load करता है, उसे एक बार चलाता है, `sys.modules` में cache करता है और आपके scope में उसका नाम बाँध देता है। उसी module की अगली imports cached object reuse करती हैं और file दोबारा नहीं चलती।

---

## 🔴 Problem it Solves
A real project has hundreds of files. Without imports you would copy code between files or keep one giant file. `import` provides code reuse, namespaces (`math.sqrt` vs your own `sqrt`), lazy loading, and a single shared instance of each module (so settings or a DB engine can live at module level safely). The cache avoids running initialisation code twice.

## 🔴 यह क्यों बना? (Hindi)
असली project में सैकड़ों files होती हैं। Imports के बिना code files के बीच कॉपी करना पड़ता या एक विशाल file रखनी पड़ती। `import` code reuse, namespaces (`math.sqrt` बनाम आपका अपना `sqrt`), lazy loading और हर module का एक साझा instance देता है (इसलिए settings या DB engine module level पर सुरक्षित रह सकते हैं)। Cache के कारण initialisation code दो बार नहीं चलता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → import shop.pricing  -> first checks sys.modules["shop.pricing"]
Step 2 → If cached: bind the name and stop (module code does NOT run again)
Step 3 → Otherwise, import the parent package "shop" first (runs shop/__init__.py)
Step 4 → Finders search sys.path (script folder, PYTHONPATH, site-packages ...)
Step 5 → The loader reads the file (or the .pyc cache), creates a module object
Step 6 → Put it in sys.modules BEFORE running the code (this is why circular imports half-work)
Step 7 → Execute the module body top to bottom; names it defines become module attributes
Step 8 → Bind the name in your scope:
           import a.b      -> binds "a"
           import a.b as x -> binds "x" to a.b
           from a import b -> binds "b"
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → import shop.pricing  -> पहले sys.modules["shop.pricing"] देखता है
Step 2 → Cache में हो तो नाम bind करके रुक जाता है (module code दोबारा नहीं चलता)
Step 3 → वरना पहले parent package "shop" import होता है (shop/__init__.py चलती है)
Step 4 → Finders sys.path में खोजते हैं (script folder, PYTHONPATH, site-packages ...)
Step 5 → Loader file (या .pyc cache) पढ़कर module object बनाता है
Step 6 → Code चलाने से पहले उसे sys.modules में रखा जाता है (इसीलिए circular imports आधे चलते हैं)
Step 7 → Module body ऊपर से नीचे चलती है; उसके बनाए नाम module के attributes बनते हैं
Step 8 → आपके scope में नाम bind होता है:
           import a.b      -> "a" bind होता है
           import a.b as x -> "x", a.b से bind होता है
           from a import b -> "b" bind होता है
```

---

## 🟡 Real World Example
A FastAPI project has `main.py`, `routers/users.py`, `db/session.py` and `config.py`. `main.py` imports routers, routers import `get_db` from `db.session`, and everybody imports one `settings` object from `config`. Because modules are cached, `settings` is built once and shared everywhere. Heavy libraries (such as ML frameworks) are sometimes imported inside a function so the API starts faster.

## 🟡 Real Example Hindi mein
FastAPI project में `main.py`, `routers/users.py`, `db/session.py` और `config.py` हैं। `main.py` routers import करता है, routers `db.session` से `get_db` लेते हैं और सब `config` से एक `settings` object import करते हैं। Modules cache होते हैं, इसलिए `settings` एक बार बनता है और हर जगह साझा रहता है। भारी libraries (जैसे ML frameworks) कभी function के अंदर import होती हैं ताकि API जल्दी start हो।

---

## 💻 Code Example — Basic
```python
# Basic import statement forms
import math                                       # import whole module
import os.path as osp                             # import submodule with alias
from collections import Counter, deque            # import specific names
import sys                                        # sys.modules is the import cache

print(math.sqrt(16))                              # 4.0, access through the module name
print(osp.basename("/a/b/c.txt"))                 # c.txt
print(Counter("aab"))                             # Counter({'a': 2, 'b': 1})
print("math" in sys.modules, math is sys.modules["math"])   # True True: cached after first import
import math as m2                                 # second import does NOT re-run the module
print(m2 is math)                                 # True
print(math.__name__, math.__spec__.name)          # math math
try:
    import not_a_real_module                      # missing module
except ModuleNotFoundError as e:
    print("ModuleNotFoundError:", e)
try:
    from math import nothing                      # name missing in module
except ImportError as e:
    print("ImportError:", str(e)[:36])

# Output:
# 4.0
# c.txt
# Counter({'a': 2, 'b': 1})
# True True
# True
# math math
# ModuleNotFoundError: No module named 'not_a_real_module'
# ImportError: cannot import name 'nothing' from 'm
```

## 💻 Code Example — Advanced
```python
# Production style: how import really works - build a package on disk and import it
import importlib                                  # dynamic imports
import importlib.util                             # find_spec lives here
import sys                                        # path and module cache
import tempfile                                   # temp folder
from pathlib import Path                          # paths

with tempfile.TemporaryDirectory() as tmp:        # throw-away project
    root: Path = Path(tmp)
    pkg: Path = root / "shop"                     # a package = folder with __init__.py
    pkg.mkdir()
    (pkg / "__init__.py").write_text("print('shop package loaded')\nfrom .pricing import tax\n__all__ = ['tax']\n")
    (pkg / "pricing.py").write_text("print('pricing loaded')\nRATE = 0.18\ndef tax(x: float) -> float:\n    return round(x * RATE, 2)\n")
    sys.path.insert(0, tmp)                       # make the folder importable

    import shop                                   # runs __init__.py once (prints 2 lines)
    print(shop.tax(100))                          # 18.0
    import shop                                   # cached -> prints nothing
    from shop import pricing                      # submodule already in sys.modules
    print(pricing.RATE, "shop.pricing" in sys.modules)   # 0.18 True

    (pkg / "pricing.py").write_text("print('pricing v2')\nRATE = 0.28\ndef tax(x):\n    return x * RATE\n")
    print(shop.pricing.RATE)                      # still 0.18: file edits are ignored until reload
    importlib.reload(shop.pricing)                # re-execute the module
    print(shop.pricing.RATE)                      # 0.28

    mod = importlib.import_module("shop.pricing") # import by string name (plugins)
    print(mod is shop.pricing)                    # True
    print(shop.__path__ == [str(pkg)], shop.__file__.endswith("__init__.py"))   # package attributes
    del sys.modules["shop.pricing"]               # forget it -> next import runs it again
    importlib.import_module("shop.pricing")       # prints 'pricing v2'
    sys.path.remove(tmp)                          # clean up

spec = importlib.util.find_spec("json")           # locate a module WITHOUT importing it
print(spec.name, spec.origin.endswith("__init__.py"))   # json True


def lazy_import(name: str):
    """Import only when first needed (faster startup)."""
    return importlib.import_module(name)          # cached by sys.modules after first call


print(lazy_import("decimal").Decimal("1.10") + 1) # 2.10

# Output:
# shop package loaded
# pricing loaded
# 18.0
# 0.18 True
# 0.18
# pricing v2
# 0.28
# True
# True True
# pricing v2
# json True
# 2.10
```

Circular import: how it breaks and how to fix it.
```python
# Circular import demo and the fix
import sys, tempfile                              # helpers
from pathlib import Path                          # paths

with tempfile.TemporaryDirectory() as tmp:        # temp project
    t: Path = Path(tmp)
    (t / "a.py").write_text("from b import B_VAL\nA_VAL = 1\n")   # a needs b
    (t / "b.py").write_text("from a import A_VAL\nB_VAL = 2\n")   # b needs a -> cycle
    sys.path.insert(0, tmp)
    try:
        import a                                  # a -> b -> a (a not finished yet)
    except ImportError as e:
        print("ImportError:", str(e).split(" (")[0])   # cannot import name 'A_VAL' from partially initialized module 'a'
    for m in ("a", "b"):
        sys.modules.pop(m, None)                  # clean the cache
    (t / "b.py").write_text("def get() -> int:\n    from a import A_VAL   # import inside the function\n    return A_VAL\nB_VAL = 2\n")
    import a                                      # works now
    import b
    print(b.get())                                # 1
    sys.path.remove(tmp)

# Output:
# ImportError: cannot import name 'A_VAL' from partially initialized module 'a'
# 1
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript (ES modules) |
|---------|--------|--------------------------|
| Import whole module | `import math` | `import * as math from "math"` |
| Import names | `from math import pi` | `import { pi } from "math"` |
| Alias | `import numpy as np` | `import * as np from "numpy"` |
| Run once and cache | yes (`sys.modules`) | yes (module map) |
| Dynamic import | `importlib.import_module(name)` | `await import(name)` |
| Location | runtime statement, anywhere | hoisted, top level only (static) |
| Search path | `sys.path` | node_modules / URL resolution |

```python
# Python way
import math                                     # a normal statement, runs at this line
from math import pi                             # bind a name
print(math.sqrt(9), pi > 3)                     # 3.0 True
```
```javascript
// JavaScript way (ES modules)
import { sqrt, PI } from "./mymath.js";         // hoisted: resolved before the file runs
console.log(sqrt(9), PI > 3);                   // 3 true
```

Key difference: A Python `import` is an ordinary runtime statement; you can put it inside a function or `if`. ES module imports are static and hoisted. Python also gives you a module object whose attributes can be mutated by anyone (a known gotcha).

---

## 🟠 FastAPI Connection
Large FastAPI apps split routes into `APIRouter` modules and import them into `main.py`. Import order matters: the cached module is shared, so a settings module or DB engine is created once. Lazy imports inside endpoints or startup hooks keep cold start fast for heavy ML libraries.

```python
# FastAPI: routers imported into main (typical project layout), plus lazy heavy import
import importlib                                  # dynamic import
from fastapi import APIRouter, FastAPI            # app + router
from fastapi.testclient import TestClient         # in-process client

router: APIRouter = APIRouter(prefix="/ml")       # would live in routers/ml.py


@router.get("/ready")                             # GET /ml/ready
def ready() -> dict[str, bool]:
    json_mod = importlib.import_module("json")    # heavy libs (torch) are often imported lazily here
    return {"loaded": json_mod is not None}


app: FastAPI = FastAPI()                          # would be main.py: `from routers.ml import router`
app.include_router(router)                        # register the imported router

client: TestClient = TestClient(app)              # test client
print(client.get("/ml/ready").json())             # {'loaded': True}

# Output:
# {'loaded': True}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Circular imports (a imports b, b imports a)
✅ Correct: move the shared code to a third module, or import inside the function that needs it (see circular demo above)

❌ Mistake 2: `from module import *`
✅ Correct: import the names you need; star imports pollute the namespace and hide where names come from

```python
# Wrong
from math import *
# Right
from math import sqrt, pi
```

❌ Mistake 3: Naming your file like a standard module (`random.py`, `json.py`, `email.py`)
✅ Correct: choose unique names; your file shadows the stdlib module and breaks imports

❌ Mistake 4: Editing a module and expecting a running program to see the change
✅ Correct: restart (or `importlib.reload` in development; uvicorn `--reload` restarts the process)

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import sys, math
from math import pi
math.pi = 3
print(pi, math.pi)
import os.path
print(os.sep == "/")
try: print(path)
except NameError as e: print("NameError", e)
import json
del json
import json
print('json' in sys.modules)
```
Answer (verified on 3.13 on macOS): `3.141592653589793 3`, `True`, `NameError name 'path' is not defined`, `True`. `from math import pi` copied the value into our namespace, so later changing `math.pi` does not affect `pi`. `import os.path` binds only the top name `os`, so `path` is undefined. `del json` removes only our name; the module stays in `sys.modules`, so the second import is instant and does not re-run the file.

---

## ⚫ Interview Questions + Answers

Q1: What happens when you import a module twice?
A1: The second time Python finds it in `sys.modules` and just binds the name; the module code does not run again.

Q2: `import x` vs `from x import y`?
A2: `import x` binds the module, and you write `x.y`. `from x import y` binds `y` directly in your namespace (a copy of the reference at that moment). Both load the whole module the first time.

Q3: How does Python find modules?
A3: Through `sys.meta_path` finders: built-in modules, frozen modules, then `sys.path` entries (script directory, `PYTHONPATH`, standard library, `site-packages`). Printing `sys.path` shows the order.

Q4: How do circular imports fail and how do you fix them?
A4: Module `a` is in `sys.modules` but only partly executed when `b` asks for a name that `a` has not defined yet, giving `ImportError: cannot import name ... (partially initialized module)`. Fixes: restructure (shared third module), import inside functions, or `import a` and use `a.name` later.

Q5: What is `__import__` and `importlib.import_module`?
A5: `import` statements call `__import__` internally. `importlib.import_module("pkg.mod")` is the clean way to import by string name (plugins, config-driven code). `importlib.reload(mod)` re-executes a module.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Splitting code into modules and packages
- Using stdlib and third-party libraries
- Lazy-loading heavy dependencies inside functions
- Dynamic plugin loading (`importlib.import_module`)

❌ Avoid when:
- Importing for side effects at import time (hard to test)
- `import *` in application code
- Importing inside hot loops (cached, but still a lookup cost)

---

## 📊 Visual Diagram
```
 import shop.pricing
        │
        ▼
 in sys.modules? ──yes──► bind name, DONE
        │ no
        ▼
 import parent "shop" (runs shop/__init__.py)
        ▼
 search sys.path for shop/pricing.py (or .pyc)
        ▼
 create module object -> sys.modules["shop.pricing"] = module
        ▼
 run module body -> attributes (RATE, tax)
        ▼
 bind name "shop" in your scope
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Module | A `.py` file as an object | एक `.py` file object के रूप में |
| Package | Folder of modules with `__init__.py` | modules का folder |
| `sys.modules` | Cache of loaded modules | loaded modules का cache |
| `sys.path` | List of folders searched | खोजे जाने वाले folders की list |
| Circular import | Two modules needing each other | दो modules का एक-दूसरे पर निर्भर होना |
| `importlib` | API for dynamic import and reload | dynamic import और reload का API |

---

## ⚡ 3-Line Summary
English: `import` finds a module through `sys.path`, runs it once, caches it in `sys.modules`, and binds a name. Later imports reuse the cache. Avoid circular imports and `import *`.
Hindi: `import` `sys.path` से module ढूँढता है, एक बार चलाता है, `sys.modules` में cache करता है और नाम bind करता है। आगे की imports cache reuse करती हैं। Circular imports और `import *` से बचें।

---

## ➡️ Next Topic
**173. from X import Y** — importing specific names and how it differs from importing the module.
