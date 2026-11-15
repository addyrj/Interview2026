---

# 178. Relative vs Absolute Imports
# हिंदी में: Relative बनाम Absolute Imports

---

## 🔵 Simple Definition (English)
An absolute import gives the full path from the top package (`from shop.utils.money import to_paise`). A relative import gives the path from the current file's package using dots (`from ..utils.money import to_paise`): one dot is "this package", two dots is "the parent package". Relative imports work only inside a package.

## 🔵 सरल परिभाषा (Hindi)
Absolute import top package से पूरा रास्ता देता है (`from shop.utils.money import to_paise`)। Relative import मौजूदा file के package से dots के ज़रिए रास्ता देता है (`from ..utils.money import to_paise`): एक dot = "यही package", दो dots = "parent package"। Relative import सिर्फ package के अंदर चलता है।

---

## 🔴 Problem it Solves
Inside a big package, repeating the full name is long, and renaming the top package means editing every file. Relative imports survive a rename. Absolute imports are clearer to read and work even when a file is moved or run in other contexts. You need to know both.

## 🔴 यह क्यों बना? (Hindi)
बड़े package में पूरा नाम बार-बार लिखना लंबा है, और top package का नाम बदलने पर हर file बदलनी पड़ती है। Relative imports rename से बच जाते हैं। Absolute imports पढ़ने में साफ हैं और file हिलाने पर भी चलते हैं। दोनों आने चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python reads the file's __package__ (e.g. "shop.payments")
Step 2 → `.`  = shop.payments   `..` = shop   `...` = parent of shop
Step 3 → `from ..utils.money import X` → resolves to  shop.utils.money
Step 4 → Absolute import skips this; it starts from a top name found on sys.path
Step 5 → If __package__ is empty (file run as a script) → relative import fails
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Python file का __package__ पढ़ता है (जैसे "shop.payments")
Step 2 → `.` = shop.payments   `..` = shop   `...` = shop का parent
Step 3 → `from ..utils.money import X` → shop.utils.money बन जाता है
Step 4 → Absolute import इसे छोड़कर sys.path में मिले top नाम से शुरू करता है
Step 5 → file को script की तरह चलाएँ तो __package__ खाली, relative import fail
```

---

## 🟡 Real World Example
In a Razorpay-style SDK, `payments/gateway.py` does `from .errors import PaymentError` (sibling) and `from ..utils.money import to_paise` (cousin). A FastAPI service uses absolute imports (`from app.core.config import settings`) because the top name `app` is stable and linters/IDEs resolve it everywhere.

## 🟡 Real Example Hindi mein
Razorpay जैसे SDK की `payments/gateway.py` में `from .errors import PaymentError` (भाई-बहन module) और `from ..utils.money import to_paise` (चचेरा module) होता है। FastAPI service में absolute imports (`from app.core.config import settings`) चलते हैं क्योंकि `app` नाम स्थिर है और IDE हर जगह समझता है।

---

## 💻 Code Example — Basic
```python
# Build package: shop/payments/gateway.py uses a relative import to shop/utils/money.py
import sys  # sys.path
import tempfile  # sandbox
from pathlib import Path  # file creation

FILES: dict[str, str] = {  # path -> content
    "shop/__init__.py": "",
    "shop/utils/__init__.py": "",
    "shop/utils/money.py": "def to_paise(r: float) -> int:\n    return round(r * 100)\n",
    "shop/payments/__init__.py": "",
    "shop/payments/gateway.py": (
        "from ..utils.money import to_paise\n"      # relative: up one level, then utils
        "from shop.utils import money\n"            # absolute: from the top package
        "def charge(r: float) -> int:\n"
        "    return to_paise(r)\n"
        "def refund(r: float) -> int:\n"
        "    return money.to_paise(r)\n"
    ),
}

with tempfile.TemporaryDirectory() as tmp:  # sandbox
    for rel, text in FILES.items():  # create the files
        p = Path(tmp, rel)  # target
        p.parent.mkdir(parents=True, exist_ok=True)  # folders
        p.write_text(text)  # content
    sys.path.insert(0, tmp)  # project root
    from shop.payments.gateway import charge, refund  # normal import works
    print(charge(10.5), refund(1))  # both import styles resolved
    # Output: 1050 100
    import shop.payments.gateway as gw  # module object
    print(gw.__package__, gw.__name__)  # __package__ is what relatives use
    # Output: shop.payments shop.payments.gateway
    sys.path.remove(tmp)  # cleanup
    for n in [m for m in sys.modules if m == "shop" or m.startswith("shop.")]:
        del sys.modules[n]  # forget temp modules
```

## 💻 Code Example — Advanced
```python
# Resolve relative names by hand, then show the classic script failure.
import importlib.util  # resolve_name lives here
import subprocess  # run a child python
import sys  # interpreter path
import tempfile  # sandbox
from pathlib import Path  # files

# 1) What does `from ..utils.money import X` mean inside shop.payments.gateway?
print(importlib.util.resolve_name("..utils.money", "shop.payments"))  # dots -> full name
# Output: shop.utils.money
print(importlib.util.resolve_name(".errors", "shop.payments"))  # one dot = sibling
# Output: shop.payments.errors

# 2) Too many dots is an error
try:  # going above the top package
    importlib.util.resolve_name("....x", "shop.payments")  # only 2 levels exist
except ImportError as exc:  # ImportError, with a clear message
    print(exc)  # show it
# Output: attempted relative import beyond top-level package

# 3) Running the same file as a SCRIPT vs as a MODULE
with tempfile.TemporaryDirectory() as tmp:  # sandbox
    for rel, text in {
        "shop/__init__.py": "",
        "shop/utils/__init__.py": "",
        "shop/utils/money.py": "def to_paise(r):\n    return round(r * 100)\n",
        "shop/payments/__init__.py": "",
        "shop/payments/gateway.py": (
            "from ..utils.money import to_paise\n"
            "if __name__ == '__main__':\n"
            "    print('paise', to_paise(2))\n"
        ),
    }.items():
        p = Path(tmp, rel)  # target
        p.parent.mkdir(parents=True, exist_ok=True)  # folders
        p.write_text(text)  # content

    as_script = subprocess.run(  # python path/to/file.py
        [sys.executable, "shop/payments/gateway.py"], cwd=tmp, capture_output=True, text=True
    )
    print(as_script.stderr.strip().splitlines()[-1])  # last line of the traceback
    # Output: ImportError: attempted relative import with no known parent package

    as_module = subprocess.run(  # python -m package.module
        [sys.executable, "-m", "shop.payments.gateway"], cwd=tmp, capture_output=True, text=True
    )
    print(as_module.stdout.strip())  # works: package context is known
    # Output: paise 200
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
from .errors import PaymentError          # sibling (same package)
from ..utils.money import to_paise        # parent's child
from shop.utils.money import to_paise     # absolute
```

```javascript
// JavaScript (ES modules)
import { PaymentError } from "./errors.js";        // sibling
import { toPaise } from "../utils/money.js";       // parent's child
import { toPaise } from "@shop/utils/money";       // "absolute" via alias / package name
```

Key difference: JS paths are file paths (`./`, `../`). Python dots mean package levels, and relative imports need a known `__package__`.

---

## 🟠 FastAPI Connection
FastAPI's docs use relative imports inside `app/` (`from ..dependencies import get_token`), but many teams prefer absolute `from app.dependencies import ...` for IDE support. Pick one style and be consistent.

```python
# app/routers/items.py - relative imports (shown as comments; the file also runs standalone)
from fastapi import APIRouter  # third-party: always absolute
# from ..dependencies import get_token_header   # relative: parent package
# from app.dependencies import get_token_header # absolute: same thing

router: APIRouter = APIRouter(prefix="/items", tags=["items"])  # router


@router.get("/")  # GET /items/
async def read_items() -> list[dict[str, str]]:
    return [{"name": "Portal Gun"}]  # JSON list
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Relative import in a file you run directly
```python
# Wrong: python shop/payments/gateway.py
#   ImportError: attempted relative import with no known parent package

# Correct: python -m shop.payments.gateway     (from the project root)
```

❌ Mistake 2: Implicit relative import (Python 2 style)
```python
# Wrong - `import money` expecting the sibling file
# Correct - `from . import money`  or  `from shop.utils import money`
```

❌ Mistake 3: Mixing styles randomly in one codebase
```python
# Wrong: half the files use `from ..x`, the other half `from app.x`
# Correct: agree on one style (many teams: absolute everywhere, relative only for siblings)
```

---

## 🧠 Tricky Interview Question

**Q**: File `shop/utils/money.py` has `from . import helpers`, and `shop/utils/helpers.py` exists. Another file does `from shop.utils.money import *`. What name is in `money`'s namespace, and is `helpers` also visible as `shop.utils.helpers`?

**Answer**:
```
money.helpers is the module  shop.utils.helpers   (same object)
```
`from . import helpers` imports the submodule `shop.utils.helpers` and binds the name `helpers` in `money`. Importing a submodule also sets it as an attribute on its parent package, so `shop.utils.helpers` works after that. Because `money` has no `__all__`, `import *` copies every public name, including the module `helpers`.

---

## ⚫ Interview Questions + Answers

Q1: What do one, two and three leading dots mean?
A1: `.` the current package, `..` its parent, `...` the grandparent.

Q2: Why does "attempted relative import with no known parent package" appear?
A2: The file ran as a script, so `__package__` is empty. Run it with `python -m package.module` or import it from another module.

Q3: Which style does PEP 8 recommend?
A3: Absolute imports are recommended; explicit relative imports are acceptable in complex package layouts where absolute paths would be too verbose.

Q4: Can a relative import go outside the top package?
A4: No: `ImportError: attempted relative import beyond top-level package`.

Q5: Do relative imports work in `__init__.py`?
A5: Yes, and they are common there: `from .gateway import charge`.

---

## 🔷 When to Use + When Not to Use

✅ Use relative when:
- Importing a sibling inside a self-contained library package
- The package may be renamed or vendored

✅ Use absolute when:
- App code (FastAPI services), tests, scripts
- You want IDE jump-to-definition and grep-ability

❌ Avoid when:
- Deep chains like `from ....a import b` (use absolute)
- The file is also run directly as a script

---

## 📊 Visual Diagram

```
 shop/
 ├── utils/money.py
 └── payments/gateway.py      (__package__ = "shop.payments")

   .          →  shop.payments
   ..         →  shop
   ..utils    →  shop.utils
   ..utils.money → shop.utils.money

 absolute: shop.utils.money  (start at the top, found on sys.path)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Absolute import | Full path from top package | पूरा रास्ता |
| Relative import | Path using dots | dots वाला रास्ता |
| `__package__` | Package name of a module | module का package नाम |
| Sibling | Module in same package | उसी package का module |
| Top-level package | Outermost package | सबसे बाहरी package |
| Script mode | Running a file directly | file सीधे चलाना |

---

## ⚡ 3-Line Summary
English: Absolute imports start at the top package; relative imports use dots from the current package. Relative imports fail in scripts because `__package__` is empty. Prefer absolute for apps, relative for tight library internals.
Hindi: Absolute import top package से शुरू होता है; relative import मौजूदा package से dots के साथ। Script में `__package__` खाली होने से relative import fail होता है। Apps में absolute, library के अंदर relative अच्छा रहता है।

---

## ➡️ Next Topic
**179. sys.path** — the list Python searches to find modules, and how to control it.
