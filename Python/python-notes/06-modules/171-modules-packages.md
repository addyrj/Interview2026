---

# 171. Modules + Packages — Complete Guide
# हिंदी में: Modules + Packages — पूरी Guide

---

## 🔵 Simple Definition (English)
A module is a `.py` file containing Python code (functions, classes, variables). A package is a directory containing multiple modules and a `__init__.py` file. Modules let you organize code into reusable, importable units. Python has three types: standard library (built-in), third-party (installed via pip), and your own modules.

## 🔵 सरल परिभाषा (Hindi)
Module एक `.py` file है जिसमें Python code होता है। Package एक directory है multiple modules + `__init__.py` के साथ। Modules से code को reusable, importable units में organize करते हैं।

---

## 💻 Code Example — Basic
```python
# ─── Import styles ────────────────────────────────────────────────

# 1. Import module (access via module.name):
import math
print(math.sqrt(16))     # 4.0
print(math.pi)           # 3.14159...

# 2. Import specific names (no prefix needed):
from math import sqrt, pi, floor
print(sqrt(16))          # 4.0 (no 'math.' prefix)

# 3. Import with alias (rename):
import numpy as np              # convention: np
import pandas as pd             # convention: pd
import matplotlib.pyplot as plt # convention: plt

# 4. Import all (AVOID — pollutes namespace):
from math import *    # ← bad practice! import sqrt, pi, floor, etc. all!
# Now you can use sqrt() directly but you don't know where it came from

# ─── __name__ == "__main__" ───────────────────────────────────────
# mymodule.py

def useful_function():
    return "I'm useful!"

def _private_function():    # underscore = convention for "internal use only"
    return "Don't use me directly"

# This block runs ONLY when the file is executed directly
# NOT when it's imported as a module:
if __name__ == "__main__":
    print("Running mymodule directly")
    print(useful_function())

# When imported: __name__ = "mymodule" → block doesn't run
# When executed: __name__ = "__main__" → block runs

# ─── __all__ — control what 'from module import *' exposes ────────
# In mymodule.py:
__all__ = ["useful_function", "MyClass"]  # only these are exported with *
# _private_function excluded even if user does 'from mymodule import *'

# ─── Checking what's in a module ─────────────────────────────────
import os
print(dir(os))              # list all names in module
print(help(os.path.join))   # show docstring
print(os.__file__)          # where is this module located?
```

## 💻 Code Example — Advanced
```python
# Package structure for a FastAPI app:

# myapp/
# ├── __init__.py          ← makes myapp a package
# ├── main.py              ← FastAPI app entry point
# ├── config.py            ← settings
# ├── models/
# │   ├── __init__.py
# │   ├── user.py
# │   └── product.py
# ├── routers/
# │   ├── __init__.py
# │   ├── users.py
# │   └── products.py
# └── services/
#     ├── __init__.py
#     └── email.py

# ─── myapp/__init__.py ────────────────────────────────────────────
# Can be empty, or expose the package's public API:
from myapp.config import settings
from myapp.main import app
__all__ = ["app", "settings"]

# ─── Absolute vs Relative imports ────────────────────────────────
# In myapp/routers/users.py:

# Absolute import (always works, preferred):
from myapp.models.user import User
from myapp.services.email import send_welcome_email

# Relative import (only inside a package):
from ..models.user import User            # go up one level, then models/user
from ..services.email import send_email   # go up one level, then services/email
from .products import get_product         # same package, products module
# Note: relative imports fail when file is run directly (no package context)

# ─── sys.path — where Python looks for modules ───────────────────
import sys
print(sys.path)
# ['', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', ...]
# '' means current directory is checked first

# Add custom path (for testing or unusual layouts):
sys.path.insert(0, "/path/to/my/custom/modules")
import my_custom_module   # now Python finds it

# ─── Lazy imports (for performance) ──────────────────────────────
# Import heavy libraries only when needed:
def process_csv(filepath: str):
    import pandas as pd     # only imported when this function is called
    df = pd.read_csv(filepath)
    return df

# ─── importlib — dynamic imports ─────────────────────────────────
import importlib

# Dynamically import a module by name:
module_name = "json"
json = importlib.import_module(module_name)
print(json.dumps({"key": "value"}))

# Reload a module (useful in interactive sessions):
importlib.reload(json)

# ─── Circular import fix ──────────────────────────────────────────
# PROBLEM: a.py imports from b.py, b.py imports from a.py → circular!

# BAD structure:
# a.py: from b import func_b
# b.py: from a import func_a   ← circular!

# FIX 1: Import inside function (lazy):
# b.py:
def func_b():
    from a import func_a    # import at call time, not module load time
    return func_a()

# FIX 2: Create a third module c.py with shared code:
# a.py and b.py both import from c.py — no circle
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python module:
# math_utils.py
def add(a, b): return a + b
def multiply(a, b): return a * b
__all__ = ["add", "multiply"]

# Import:
from math_utils import add, multiply
import math_utils
math_utils.add(1, 2)
```

```javascript
// JavaScript ES module:
// mathUtils.js
export function add(a, b) { return a + b; }
export function multiply(a, b) { return a * b; }
export default { add, multiply };

// Import:
import { add, multiply } from './mathUtils.js';
import mathUtils from './mathUtils.js';
mathUtils.add(1, 2);
```

Key differences:
- Python `import module` = load entire module. `from module import x` = load specific names.
- JS has default exports. Python has no default export — just names.
- Python `__all__` controls `import *`. JS export declarations control what's public.
- Python `__init__.py` makes a directory a package. JS has `index.js` convention.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `from module import *` in production code
```python
# Wrong — you don't know what names are imported:
from os.path import *
exists(".")   # works but where does exists() come from?

# Correct — explicit imports:
from os.path import exists, join, dirname
exists(".")   # clear where it comes from
```

❌ Mistake 2: Missing `__init__.py` (Python 3 allows "namespace packages" without it, but it causes confusion)
```
# If you want a proper package (not namespace package):
mypackage/
    __init__.py     ← required for relative imports to work
    module.py
```

---

## 🧠 Tricky Interview Question

**Q**: `module_a.py` has `x = 10`. You import it in two files: `b.py` and `c.py`. If `b.py` does `module_a.x = 99`, does `c.py` see `x = 99`?

**Answer**: **Yes!** Python caches imported modules in `sys.modules` — the same module object is shared. `b.py` modifying `module_a.x` changes the shared object. `c.py` importing `module_a` gets the cached version and sees `x = 99`. This is why mutable module-level state is dangerous in multi-module apps.

---

## ⚫ Interview Questions + Answers

Q1: What is `sys.modules`?
A1: A dict mapping module names to loaded module objects — Python's import cache. When you `import json`, Python checks `sys.modules` first — if found, returns the cached module (no re-execution). This is why importing the same module multiple times is cheap. `del sys.modules["json"]` forces a fresh import next time (rarely needed — used in testing).

Q2: What is the difference between `__init__.py` and a namespace package?
A2: With `__init__.py`: traditional package — relative imports work, `__init__.py` code runs on package import. Without `__init__.py` (Python 3.3+ namespace package): allows splitting a package across multiple directories. For application code: always use `__init__.py`. Namespace packages are for distribution/plugin systems.

Q3: What is `__all__` and what does it control?
A3: `__all__ = ["func1", "ClassA"]` is a list of names to export when someone does `from module import *`. Without `__all__`: `import *` exports all names that don't start with `_`. With `__all__`: only listed names are exported (even if others don't start with `_`). Best practice: define `__all__` in any module with a public API to make the interface explicit.

Q4: How do relative imports work?
A4: Relative imports use dot notation. `from . import module` imports from the same package. `from .. import module` goes up one level. `from ..sibling import x` goes up one, then into sibling package. Only valid inside packages (files with a parent package). Cannot use relative imports in files run directly as scripts (`python myscript.py`) — only in files imported as part of a package.

Q5: What is `__package__` and `__spec__`?
A5: `__package__` is the package name of the current module — used to resolve relative imports. If a file is run as a script: `__package__` is `None` or `""` — relative imports fail. `__spec__` contains module spec information including the module's origin (path), submodule search locations (for packages), and loader. Used by import machinery — rarely needed in application code, but useful in frameworks and tools.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Module | Single .py file | Single .py file |
| Package | Directory with __init__.py | Directory with __init__.py |
| __init__.py | Makes directory a package | Directory को package बनाता है |
| __all__ | Controls what `import *` exports | `import *` क्या export करे |
| __name__ | Module's name at runtime | Runtime पर module का नाम |
| sys.modules | Import cache | Import cache |
| Circular import | A imports B, B imports A | A imports B, B imports A |

---

## ⚡ 3-Line Summary
English: A module is a `.py` file; a package is a directory with `__init__.py`. Always use explicit imports (`from module import x`) — avoid `import *`. The `if __name__ == "__main__":` guard prevents setup code from running on import.
Hindi: Module = `.py` file; Package = directory + `__init__.py`। Always explicit imports। `if __name__ == "__main__":` import पर setup code रोकता है।

---

## ➡️ Next Topic
**184. os Module** — file system operations. **186. pathlib Module** — modern path handling. **199. logging Module** — production logging setup.
