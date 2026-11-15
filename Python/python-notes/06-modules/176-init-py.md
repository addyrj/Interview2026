---

# 176. `__init__.py`
# हिंदी में: `__init__.py` (folder को package बनाने वाली file)

---

## 🔵 Simple Definition (English)
`__init__.py` is a special file inside a folder. It marks the folder as a regular package, and its code runs once, the first time the package (or anything inside it) is imported. It is also the place to decide the package's public API.

## 🔵 सरल परिभाषा (Hindi)
`__init__.py` folder के अंदर की एक खास file है। यह folder को regular package बनाती है और इसका code package (या उसके अंदर की कोई चीज़) पहली बार import होने पर एक बार चलता है। Package की public API यहीं तय की जाती है।

---

## 🔴 Problem it Solves
Without a package marker, a folder of `.py` files is just files. Users would have to know your internal layout (`from shop.payments.gateway import charge`). `__init__.py` lets you re-export `charge` at the package level (`from shop.payments import charge`) so you can reorganize inside without breaking users.

## 🔴 यह क्यों बना? (Hindi)
Marker के बिना folder बस `.py` files का ढेर है। Users को अंदर की बनावट जाननी पड़ती (`from shop.payments.gateway import charge`)। `__init__.py` से `charge` को package level पर दे सकते हैं (`from shop.payments import charge`), जिससे अंदर का ढाँचा बदलने पर users का code नहीं टूटता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → `import shop.payments` : Python finds folder shop/payments on sys.path
Step 2 → It first imports parent `shop` (runs shop/__init__.py), then payments
Step 3 → Runs shop/payments/__init__.py top to bottom, ONCE
Step 4 → Names defined/imported there become attributes of the package
Step 5 → Submodules (gateway.py) load only when imported (or imported by __init__)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `import shop.payments` : Python sys.path में folder shop/payments खोजता है
Step 2 → पहले parent `shop` (shop/__init__.py चलती है), फिर payments import होता है
Step 3 → shop/payments/__init__.py ऊपर से नीचे एक बार चलती है
Step 4 → वहाँ बने/import हुए नाम package के attributes बन जाते हैं
Step 5 → submodules (gateway.py) तभी load होते हैं जब import हों (या __init__ उन्हें import करे)
```

---

## 🟡 Real World Example
A Razorpay-style SDK has `payments/__init__.py` with `from .gateway import charge, refund` so customers write `from payments import charge`. A FastAPI app has `app/models/__init__.py` importing every model so SQLAlchemy sees all tables before `create_all()`. `__version__` is also set in the top `__init__.py`.

## 🟡 Real Example Hindi mein
Razorpay जैसे SDK की `payments/__init__.py` में `from .gateway import charge, refund` होता है ताकि customer `from payments import charge` लिख सके। FastAPI app की `app/models/__init__.py` सारे models import करती है ताकि `create_all()` से पहले SQLAlchemy को सारी tables दिखें। `__version__` भी top `__init__.py` में रखते हैं।

---

## 💻 Code Example — Basic
```python
# Builds a tiny package in a temp folder and imports it.
import sys  # to extend sys.path
import tempfile  # temp folder
from pathlib import Path  # file creation

with tempfile.TemporaryDirectory() as tmp:  # deleted after the block
    pkg = Path(tmp, "shop")  # package folder
    pkg.mkdir()  # create the folder
    (pkg / "__init__.py").write_text(  # package initializer
        'print("shop init runs")\n'  # side effect, to show WHEN it runs
        '__version__ = "1.0"\n'  # package-level constant
        "from .money import to_paise\n"  # re-export (relative import)
    )
    (pkg / "money.py").write_text(  # a submodule
        "def to_paise(r: float) -> int:\n"
        "    return round(r * 100)\n"
    )
    sys.path.insert(0, tmp)  # make the temp folder importable
    import shop  # triggers __init__.py
    # Output: shop init runs
    print(shop.__version__)  # constant defined in __init__
    # Output: 1.0
    print(shop.to_paise(10.5))  # works at package level, not shop.money.to_paise
    # Output: 1050
    import shop  # second import is a cache hit - nothing runs
    print(shop.__name__, shop.__file__.endswith("__init__.py"))  # package facts
    # Output: shop True
    sys.path.remove(tmp)  # cleanup
    for name in [m for m in sys.modules if m == "shop" or m.startswith("shop.")]:
        del sys.modules[name]  # forget the temp package
```

## 💻 Code Example — Advanced
```python
# Production __init__.py: explicit API, lazy heavy import, version via metadata.
# (Contents of shop/payments/__init__.py, shown in a runnable demo harness.)
import sys  # sys.path / sys.modules
import tempfile  # temp folder
from pathlib import Path  # files

INIT_SRC: str = '''
"""Payments package public API."""
from __future__ import annotations
from importlib import import_module
from typing import TYPE_CHECKING, Any

from .gateway import charge, refund          # cheap, always loaded

__all__ = ["charge", "refund", "export_report"]   # the public API

if TYPE_CHECKING:                             # only for type checkers, no runtime cost
    from .reports import export_report

def __getattr__(name: str) -> Any:            # PEP 562: lazy attribute on module
    if name == "export_report":               # heavy module (pandas) loaded on demand
        return getattr(import_module(".reports", __name__), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
'''  # end of __init__.py source

with tempfile.TemporaryDirectory() as tmp:  # sandbox
    root = Path(tmp, "payments")  # package folder
    root.mkdir()  # create
    (root / "__init__.py").write_text(INIT_SRC)  # the init above
    (root / "gateway.py").write_text(  # light module
        "def charge(r: float) -> int:\n    return round(r * 100)\n"
        "def refund(r: float) -> int:\n    return -round(r * 100)\n"
    )
    (root / "reports.py").write_text(  # pretend heavy module
        "print('reports (heavy) imported')\n"
        "def export_report() -> str:\n    return 'report.csv'\n"
    )
    sys.path.insert(0, tmp)  # importable
    import payments  # runs __init__, NOT reports.py
    print("payments.reports" in sys.modules)  # heavy module not loaded yet
    # Output: False
    print(payments.export_report())  # first access triggers lazy import
    # Output (two lines): reports (heavy) imported
    #                     report.csv
    print(payments.charge(2.5), payments.__all__)  # normal re-exports
    # Output: 250 ['charge', 'refund', 'export_report']
    sys.path.remove(tmp)  # cleanup
    for name in [m for m in sys.modules if m == "payments" or m.startswith("payments.")]:
        del sys.modules[name]  # forget the package
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: shop/__init__.py
from .money import to_paise          # re-export for users
__all__ = ["to_paise"]               # public API list
# users:  from shop import to_paise
```

```javascript
// JavaScript: shop/index.js (barrel file)
export { toPaise } from "./money.js";   // re-export
// users:  import { toPaise } from "./shop";   (folder resolves to index.js)
```

Key difference: `__init__.py` is the JS `index.js` barrel file. In Python, since 3.3 a folder without it still imports as a "namespace package", but it is a different thing (no init code, can span directories).

---

## 🟠 FastAPI Connection
Large FastAPI projects use `__init__.py` to collect routers and models. A common pattern: `app/api/__init__.py` builds one parent router from all feature routers.

```python
# app/api/__init__.py (needs: pip install fastapi)
from fastapi import APIRouter  # router class

# in a real project these come from sibling modules:
#   from .users import router as users_router
#   from .orders import router as orders_router
users_router: APIRouter = APIRouter(prefix="/users", tags=["users"])  # stand-in
orders_router: APIRouter = APIRouter(prefix="/orders", tags=["orders"])  # stand-in

api_router: APIRouter = APIRouter(prefix="/api/v1")  # one parent router
api_router.include_router(users_router)  # /api/v1/users
api_router.include_router(orders_router)  # /api/v1/orders
# main.py then does: app.include_router(api_router)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Heavy work in `__init__.py`
```python
# Wrong - every import of any submodule connects to the DB / loads a model:
# engine = create_engine(...); model = load_big_model()

# Correct - keep it light; create resources in functions or lazily.
```

❌ Mistake 2: Circular imports through `__init__`
```python
# Wrong - __init__ imports a.py, a.py does `from pkg import b`, b imports a ...
# Correct - import from the specific module (`from pkg.b import X`), keep __init__ small
```

❌ Mistake 3: Forgetting it in a tool-sensitive setup
```python
# Wrong - pytest/mypy/setuptools may skip an "implicit namespace" folder
# Correct - add an (even empty) __init__.py in every package folder you ship
```

---

## 🧠 Tricky Interview Question

**Q**: Package `p` has `__init__.py` with `print("init")`, and `p/a.py` with `print("a")`. What prints?

```python
import p.a
import p.a
from p import a
```

**Answer**:
```
init
a
```
Importing `p.a` first imports `p` (prints `init`), then `a` (prints `a`). The next two imports are cache hits in `sys.modules`, so nothing prints again. The `__init__.py` always runs before any submodule.

---

## ⚫ Interview Questions + Answers

Q1: Is `__init__.py` still required in Python 3?
A1: Not to import (namespace packages work without it since 3.3), but you should still add it for regular packages: tools, packaging and `__all__`/re-exports depend on it.

Q2: When does `__init__.py` run?
A2: Once, the first time the package or any of its submodules is imported. Later imports reuse `sys.modules`.

Q3: Does `import pkg` automatically import `pkg.sub`?
A3: No, unless `__init__.py` imports it. `pkg.sub` raises `AttributeError` until the submodule has been imported somewhere.

Q4: What is a lazy `__getattr__` in `__init__.py`?
A4: PEP 562 lets a module define `__getattr__(name)` to build attributes on demand, delaying heavy imports until first use.

Q5: Can `__init__.py` be empty?
A5: Yes, that is common and valid. It still marks the folder as a regular package.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Defining a clean public API (`from pkg import Thing`)
- Setting `__version__` and `__all__`
- Registering models/plugins on package import

❌ Avoid when:
- You are tempted to put business logic or I/O there
- It would cause circular imports
- A plain module (single `.py`) is enough

---

## 📊 Visual Diagram

```
 shop/
 ├── __init__.py   ← runs first, exports API
 ├── money.py
 └── payments/
     ├── __init__.py   ← runs on first import of shop.payments
     └── gateway.py

 import shop.payments.gateway
   1) shop/__init__.py  2) payments/__init__.py  3) gateway.py
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Package | Folder of modules | modules का folder |
| Re-export | Expose a name from another module | नाम आगे उपलब्ध कराना |
| Public API | Names meant for users | users के लिए नाम |
| Namespace package | Package without `__init__.py` | बिना init वाला package |
| Lazy import | Import only when used | ज़रूरत पर import |
| PEP 562 | Module-level `__getattr__` | module का `__getattr__` |

---

## ⚡ 3-Line Summary
English: `__init__.py` makes a folder a regular package and runs once on first import. Use it to re-export a clean API, set `__all__` and `__version__`. Keep it light to avoid slow imports and cycles.
Hindi: `__init__.py` folder को regular package बनाती है और पहली import पर एक बार चलती है। इससे साफ API, `__all__` और `__version__` दें। इसे हल्का रखें ताकि import धीमा या circular न हो।

---

## ➡️ Next Topic
**177. Packages Structure** — how to lay out a real project with packages, subpackages and entry points.
