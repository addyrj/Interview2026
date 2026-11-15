---

# 181. `__all__` Variable
# हिंदी में: `__all__` Variable (public API की सूची)

---

## 🔵 Simple Definition (English)
`__all__` is a list of strings in a module that names its public API. It controls exactly which names `from module import *` brings in. Without it, `import *` copies every name that does not start with an underscore (including names the module itself imported).

## 🔵 सरल परिभाषा (Hindi)
`__all__` module में strings की list है जो उसकी public API के नाम बताती है। यह तय करती है कि `from module import *` कौन से नाम लाएगा। इसके बिना `import *` हर वह नाम ले आता है जो underscore से शुरू नहीं होता (module ने खुद जो import किए वे भी)।

---

## 🔴 Problem it Solves
Star imports leak helper names, imported modules and constants into the user's namespace, and may overwrite their variables. `__all__` declares "these names are the contract", which also documents the API for readers and tools (linters, IDEs, docs).

## 🔴 यह क्यों बना? (Hindi)
Star import helper नाम, import किए हुए modules और constants user के namespace में डाल देता है और उनके variables को overwrite भी कर सकता है। `__all__` कहता है "यही नाम contract हैं", जो readers और tools (linter, IDE, docs) के लिए API का दस्तावेज़ भी है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Module defines:  __all__ = ["charge", "refund"]
Step 2 → `from module import *` reads module.__all__
Step 3 → ONLY those names are bound in the importer's namespace
Step 4 → No __all__ → every name not starting with "_" is exported
Step 5 → __all__ does NOT block explicit access: `from module import _secret` still works
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Module में लिखा है:  __all__ = ["charge", "refund"]
Step 2 → `from module import *` module.__all__ पढ़ता है
Step 3 → सिर्फ वही नाम importer के namespace में आते हैं
Step 4 → __all__ न हो → "_" से न शुरू होने वाले सारे नाम export होते हैं
Step 5 → __all__ सीधे access नहीं रोकता: `from module import _secret` फिर भी चलेगा
```

---

## 🟡 Real World Example
A Razorpay-style SDK exposes `charge`, `refund`, `PaymentError` in `payments/__init__.py` via `__all__`; internal helpers like `_sign()` stay hidden. NumPy, Pandas and `os` define `__all__` so `from os import *` does not drag in `sys`. Sphinx and IDEs use `__all__` to decide what to document and auto-import.

## 🟡 Real Example Hindi mein
Razorpay जैसा SDK `payments/__init__.py` में `__all__` से `charge`, `refund`, `PaymentError` खोलता है; `_sign()` जैसे internal helpers छिपे रहते हैं। NumPy, Pandas और `os` में `__all__` है ताकि `from os import *` से `sys` न आ जाए। Sphinx और IDE `__all__` से तय करते हैं कि क्या document/auto-import करना है।

---

## 💻 Code Example — Basic
```python
# Create a module with __all__ and test import * from it.
import sys  # sys.path
import tempfile  # sandbox
from pathlib import Path  # files

SRC: str = '''
import math                      # an imported module (not part of the API)
__all__ = ["charge", "PI_RS"]    # public API only
PI_RS = 3.14
def charge(x): return x * 2      # public
def refund(x): return -x         # public-looking, but NOT listed in __all__
def _sign(x): return "sig"      # private by convention
'''  # module source

with tempfile.TemporaryDirectory() as tmp:  # sandbox
    Path(tmp, "billing.py").write_text(SRC)  # write the module
    sys.path.insert(0, tmp)  # importable
    ns: dict = {}  # a clean namespace to receive the star import
    exec("from billing import *", ns)  # star import into ns
    print(sorted(k for k in ns if not k.startswith("__")))  # what arrived?
    # Output: ['PI_RS', 'charge']
    exec("from billing import refund, _sign", ns)  # explicit import still works
    print(ns["refund"](5), ns["_sign"](1))  # both usable
    # Output: -5 sig
    sys.path.remove(tmp)  # cleanup
    sys.modules.pop("billing", None)  # forget it
```

## 💻 Code Example — Advanced
```python
# Production: build __all__ with a decorator, and test that the API is stable.
import sys  # sys.modules
import types  # ModuleType
from typing import Any, Callable, List, TypeVar  # type hints

F = TypeVar("F", bound=Callable[..., Any])  # any function type


def export(fn: F) -> F:
    """Decorator: add the function's name to its module's __all__."""
    module = sys.modules[fn.__module__]  # module where fn is defined
    names: List[str] = module.__dict__.setdefault("__all__", [])  # create list lazily
    if fn.__name__ not in names:  # avoid duplicates
        names.append(fn.__name__)  # register
    return fn  # return the function unchanged


# Demo with an in-memory module so the example is self-contained
demo = types.ModuleType("demo_api")  # create a fake module
sys.modules["demo_api"] = demo  # register it
exec(  # define functions inside it
    "def charge(x): return x\n"
    "def helper(x): return x\n",
    demo.__dict__,
)
demo.charge.__module__ = "demo_api"  # make __module__ point to our module
export(demo.charge)  # mark only charge as public
print(demo.__all__)  # the generated list
# Output: ['charge']

ns: dict = {}  # target namespace
exec("from demo_api import *", ns)  # star import respects the list
print("charge" in ns, "helper" in ns)  # helper stays private
# Output: True False


def check_all(module: types.ModuleType) -> List[str]:
    """Return names listed in __all__ that do not exist (a classic bug)."""
    declared: List[str] = list(getattr(module, "__all__", []))  # read the list
    return [n for n in declared if not hasattr(module, n)]  # missing ones


demo.__all__.append("ghost")  # a typo / removed function
print(check_all(demo))  # catches it in a unit test
# Output: ['ghost']
try:  # and star import fails loudly
    exec("from demo_api import *", {})  # AttributeError for missing name
except AttributeError as exc:  # show the message
    print(exc)
# Output: module 'demo_api' has no attribute 'ghost'
del sys.modules["demo_api"]  # cleanup
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: explicit public list
__all__ = ["charge", "refund"]
def charge(): ...
def refund(): ...
def _internal(): ...        # not exported by import *
```

```javascript
// JavaScript: exports are explicit by default
export function charge() {}
export function refund() {}
function internal() {}      // not exported - JS is "private unless exported"
```

Key difference: JS makes everything private unless you `export`. Python makes everything public (except `_name` by convention) unless you restrict star imports with `__all__`.

---

## 🟠 FastAPI Connection
In FastAPI projects, `__all__` in `schemas/__init__.py` or `models/__init__.py` documents which Pydantic/ORM classes are public and keeps `from app.schemas import *` (used in tests/notebooks) tidy. Linters also flag unused re-exports unless they are listed in `__all__`.

```python
# app/schemas/__init__.py (needs: pip install pydantic)
from pydantic import BaseModel  # base class


class OrderIn(BaseModel):  # request body
    item: str  # item name
    qty: int = 1  # default quantity


class OrderOut(BaseModel):  # response body
    id: int  # order id
    item: str  # item name


__all__: list[str] = ["OrderIn", "OrderOut"]  # public schemas; BaseModel is not re-exported
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: A name in `__all__` that does not exist
```python
# Wrong:
# __all__ = ["charge", "refnd"]      # typo -> AttributeError on `import *`

# Correct: keep names in sync; add a unit test using check_all()
```

❌ Mistake 2: Thinking `__all__` makes things private
```python
# Wrong assumption: from billing import refund  -> blocked
# Reality: it still works; __all__ only affects `import *` and docs/tools.
```

❌ Mistake 3: Putting non-strings in `__all__`
```python
# Wrong: __all__ = [charge, refund]     # functions, not strings -> TypeError
# Correct: __all__ = ["charge", "refund"]
```

---

## 🧠 Tricky Interview Question

**Q**: Module `m.py` has `__all__ = ["a"]`, plus `a = 1`, `b = 2`, `_c = 3`. What does this print?

```python
from m import *
print("a" in dir(), "b" in dir(), "_c" in dir())
from m import b, _c
print(b, _c)
import m
print(m.b)
```

**Answer**:
```
True False False
2 3
2
```
`import *` follows `__all__`, so only `a`. Explicit imports of `b` and `_c` and attribute access `m.b` always work: `__all__` is not enforcement.

---

## ⚫ Interview Questions + Answers

Q1: What does `__all__` change?
A1: Only the behaviour of `from module import *` (and what many tools consider public). It never blocks direct access.

Q2: What if `__all__` is missing?
A2: `import *` takes all names not starting with `_`, including names the module itself imported.

Q3: Does `__all__` work on packages?
A3: Yes. In `pkg/__init__.py`, `__all__` can also list submodule names, and `from pkg import *` will import those submodules.

Q4: Does the underscore prefix hide a name?
A4: It is only a convention: `_name` is skipped by `import *` when there is no `__all__`, but `from m import _name` still works.

Q5: Should application code (not libraries) use `__all__`?
A5: Optional. It is most valuable for libraries and `__init__.py` re-exports, and for making linters accept re-exports.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Writing a library or SDK with a clear public API
- Re-exporting names in `__init__.py`
- Supporting `import *` in notebooks or REPL helpers

❌ Avoid when:
- In small scripts that nobody imports
- As a security tool (it is not one)
- If you let it drift out of sync with the code

---

## 📊 Visual Diagram

```
 billing.py                        from billing import *
 ┌─────────────────────────┐       ┌─────────────────────┐
 │ __all__ = [charge,PI_RS]│──────►│ charge, PI_RS only  │
 │ charge, refund, _sign   │   ✖   │ (refund, _sign, math│
 │ import math             │       │  are NOT copied)    │
 └─────────────────────────┘       └─────────────────────┘
 Explicit: from billing import refund   → still allowed
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `__all__` | List of public names | public नामों की list |
| Star import | `from m import *` | सब नाम import |
| Public API | Names users may rely on | users के लिए नाम |
| Re-export | Expose imported name | import किया नाम आगे देना |
| Convention | Agreed habit, not enforced | तय आदत, लागू नहीं |
| Namespace pollution | Too many stray names | namespace में फालतू नाम |

---

## ⚡ 3-Line Summary
English: `__all__` lists the public names of a module and controls `from m import *`. It documents the API but does not enforce privacy. Keep it in sync, and prefer explicit imports in real code.
Hindi: `__all__` module के public नाम बताती है और `from m import *` को नियंत्रित करती है। यह API document करती है, privacy लागू नहीं करती। इसे code के साथ sync रखें और असली code में explicit imports चुनें।

---

## ➡️ Next Topic
**182. Circular Imports — How to Fix** — what happens when two modules import each other, and the fixes.
