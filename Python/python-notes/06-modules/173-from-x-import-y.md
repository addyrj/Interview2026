---

# 173. from X import Y
# हिंदी में: from X import Y (module से सिर्फ ज़रूरी चीज़ import करना)

---

## 🔵 Simple Definition (English)
`from X import Y` loads module `X` and copies only the name `Y` from it into your current file. You can then use `Y` directly, without writing `X.` in front. The whole module is still executed once and cached in `sys.modules`.

## 🔵 सरल परिभाषा (Hindi)
`from X import Y` module `X` को load करता है और उसमें से सिर्फ `Y` नाम आपकी file में ले आता है। फिर आप `X.` लिखे बिना सीधे `Y` use कर सकते हैं। पूरा module एक बार चलता है और `sys.modules` में cache हो जाता है।

---

## 🔴 Problem it Solves
With plain `import math` you must write `math.sqrt(...)` every time. For names used very often (`Path`, `datetime`, `Depends`) this is noisy. `from X import Y` shortens the code and also documents exactly which names a file depends on.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ `import math` करने पर हर बार `math.sqrt(...)` लिखना पड़ता है। जो नाम बार-बार आते हैं (`Path`, `datetime`, `Depends`) उनके लिए यह लंबा लगता है। `from X import Y` code छोटा करता है और साफ बताता है कि file किन नामों पर निर्भर है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python looks in sys.modules for "X" (cache)
Step 2 → If missing: find X on sys.path, run its code ONCE, store in sys.modules
Step 3 → Look up attribute Y on the module object
Step 4 → Bind the name Y in YOUR namespace to the SAME object (a reference copy)
Step 5 → Missing Y → ImportError: cannot import name 'Y' from 'X'
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले sys.modules (cache) में "X" देखता है
Step 2 → न मिले तो sys.path में खोजकर X का code एक बार चलाता है और cache करता है
Step 3 → module object में attribute Y खोजता है
Step 4 → आपके namespace में Y नाम उसी object से जोड़ देता है (reference copy)
Step 5 → Y न मिले तो ImportError आता है
```

---

## 🟡 Real World Example
A Razorpay-style FastAPI service starts with `from fastapi import FastAPI, Depends, HTTPException` and `from datetime import datetime, timezone`. An AI app does `from typing import Annotated` and `from pydantic import BaseModel, Field`. Each file lists just the pieces it needs.

## 🟡 Real Example Hindi mein
Razorpay जैसी FastAPI service की शुरुआत `from fastapi import FastAPI, Depends, HTTPException` और `from datetime import datetime, timezone` से होती है। AI app में `from pydantic import BaseModel, Field` आम है। हर file सिर्फ अपनी ज़रूरत के हिस्से import करती है।

---

## 💻 Code Example — Basic
```python
# Basic from-import examples - every line commented
from math import sqrt, pi  # import two names from math
print(sqrt(16))  # use sqrt directly, no "math." prefix
# Output: 4.0
print(round(pi, 3))  # pi is also available directly
# Output: 3.142

from collections import Counter  # import one class
print(Counter("aab").most_common(1))  # count characters
# Output: [('a', 2)]

from math import (  # parentheses allow a multi-line import list
    floor,  # round down
    ceil,  # round up
)
print(floor(2.7), ceil(2.1))  # both used directly
# Output: 2 3

try:  # a name that does not exist in the module
    from math import nothing  # type: ignore[attr-defined]
except ImportError as exc:  # raised as ImportError, not AttributeError
    print(type(exc).__name__)  # show the exception type
# Output: ImportError
```

## 💻 Code Example — Advanced
```python
# Binding semantics: from-import COPIES THE REFERENCE, not a live link.
# Saves a helper module to a temp dir, then imports it two ways.
import sys  # to edit sys.path
import tempfile  # to create a temp folder
from pathlib import Path  # path handling
from typing import Callable  # type hint for the function

with tempfile.TemporaryDirectory() as tmp:  # folder deleted at the end
    Path(tmp, "cfg.py").write_text(  # write a tiny module
        "counter = 0\n"  # a module-level variable
        "def bump():\n"  # a function that rebinds it
        "    global counter\n"  # modify the module global
        "    counter += 1\n"
    )
    sys.path.insert(0, tmp)  # make the temp folder importable
    try:
        import cfg  # module import: live access via cfg.counter
        from cfg import counter, bump  # from-import: copies the value 0
        bump_fn: Callable[[], None] = bump  # hold the function with a type hint
        bump_fn()  # module global becomes 1
        print(counter)  # our copy still points to the old int 0
        # Output: 0
        print(cfg.counter)  # the module attribute is updated
        # Output: 1
    finally:
        sys.path.remove(tmp)  # clean up sys.path
        sys.modules.pop("cfg", None)  # forget the temp module


# Safe optional import with a fallback (common in libraries)
try:  # prefer the fast library if installed
    from orjson import dumps as fast_dumps  # type: ignore[import-not-found]
except ImportError:  # not installed -> use the standard one
    from json import dumps as fast_dumps  # same name, different source
print(fast_dumps({"ok": True}))  # works either way
# Output: {"ok": true}   (orjson would return bytes b'{"ok":true}')
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
from math import sqrt, pi            # named imports
from math import sqrt as root        # rename
import math                          # whole module (namespace)
# from math import *                 # star import (avoid)
```

```javascript
// JavaScript (ES modules)
import { sqrt, PI } from "./math.js";       // named imports
import { sqrt as root } from "./math.js";   // rename
import * as math from "./math.js";          // whole module (namespace)
// ES imports are LIVE bindings; Python from-import is a one-time copy of the reference.
```

Key difference: in JS `import { counter }` stays linked to the exporting module, so updates are visible. In Python the name is just a copy of the reference, so rebinding in the source module is not seen.

---

## 🟠 FastAPI Connection
Every FastAPI file is built from from-imports: `from fastapi import APIRouter, Depends`, `from sqlalchemy.orm import Session`, `from .schemas import OrderIn`. Importing the exact names keeps routers short.

```python
# FastAPI with from-imports (needs: pip install fastapi)
from fastapi import APIRouter, Depends, HTTPException  # the pieces we need
from typing import Dict  # type hints

router: APIRouter = APIRouter(prefix="/items")  # grouped routes
DB: Dict[int, str] = {1: "pen"}  # fake database


def get_db() -> Dict[int, str]:  # dependency provider
    return DB  # return the fake db


@router.get("/{item_id}")  # GET /items/1
def read_item(item_id: int, db: Dict[int, str] = Depends(get_db)) -> Dict[str, str]:
    if item_id not in db:  # not found
        raise HTTPException(status_code=404, detail="missing")  # 404 response
    return {"name": db[item_id]}  # JSON response
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting a from-imported variable to update
```python
# Wrong - 'counter' is a stale copy:
# from cfg import counter ; bump() ; print(counter)  -> still 0

# Correct - read it through the module:
# import cfg ; bump() ; print(cfg.counter)  -> 1
```

❌ Mistake 2: Star import hides where names come from
```python
# Wrong - which module gave us 'floor'? any name may be overwritten silently:
# from math import *
# from numpy import *   # numpy's own names now shadow math's

# Correct - name what you use:
from math import floor
```

❌ Mistake 3: Naming your file like a library
```python
# Wrong - a local file named random.py breaks "from random import choice"
# Correct - rename your file (e.g. my_random.py) and delete the __pycache__
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output? (module `m.py` contains `items = []` and `def add(x): items.append(x)`)

```python
from m import items, add
add(1)
print(items)
items = [99]
add(2)
print(items)
import m
print(m.items)
```

**Answer**:
```
[1]
[99]
[1, 2]
```
`items` is the same list object, so `add(1)` (which mutates, not rebinds) is visible. Then `items = [99]` rebinds only OUR name to a new list. `add(2)` still mutates the module's original list, so `m.items` is `[1, 2]`.

---

## ⚫ Interview Questions + Answers

Q1: Does `from X import Y` import only Y and skip running X?
A1: No. The whole module X runs once (top to bottom) and is cached in `sys.modules`. Only the name Y is bound in your namespace.

Q2: What error appears for a wrong name?
A2: `ImportError: cannot import name 'Y' from 'X'`. A missing module gives `ModuleNotFoundError` (a subclass of ImportError).

Q3: Is `from X import Y` faster than `import X`?
A3: Not at import time; both run the module once. At call time `Y(...)` skips one attribute lookup (`X.Y`), a negligible gain.

Q4: Why is `from X import *` discouraged?
A4: It pollutes the namespace, hides origins, breaks linters and can silently shadow names. Use it only with a curated `__all__` or in `__init__.py` re-exports.

Q5: How do you import a submodule vs a name?
A5: `from package import submodule` works for both: Python first checks for an attribute, then tries to import `package.submodule` as a module.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- A few specific names are used often (`Path`, `Depends`, `BaseModel`)
- You want the file's dependencies visible at the top
- You rename on import (`from json import dumps as to_json`)

❌ Avoid when:
- The imported value is a module-level variable that changes over time
- Two modules export the same name (use `import X` to avoid a clash)
- You are tempted to use `*`

---

## 📊 Visual Diagram

```
 cfg.py (module object in sys.modules)         your file
 ┌──────────────────────┐                  ┌──────────────────┐
 │ counter ──► int 0    │ ── from import ─►│ counter ─► int 0 │
 │ bump    ──► function │                  │ bump ──► function│
 └──────────────────────┘                  └──────────────────┘
 bump() rebinds cfg.counter → 1            your 'counter' still → 0
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Namespace | Table of names in a file/module | नामों की तालिका |
| Binding | Linking a name to an object | नाम को object से जोड़ना |
| sys.modules | Cache of loaded modules | load हुए modules का cache |
| Star import | `from X import *` | सब कुछ import करना |
| ImportError | Name/module could not be imported | import की गड़बड़ी |
| Shadowing | A new name hides an older one | नाम का दूसरे को ढक देना |

---

## ⚡ 3-Line Summary
English: `from X import Y` runs X once and binds name Y to the same object in your file. It is a reference copy, not a live link, so rebinding in X is not visible. Avoid `*` imports.
Hindi: `from X import Y` X को एक बार चलाकर Y को आपकी file में उसी object से जोड़ देता है। यह reference की copy है, live link नहीं, इसलिए X में rebinding दिखाई नहीं देती। `*` import से बचें।

---

## ➡️ Next Topic
**174. import as (alias)** — rename modules and names (`import numpy as np`) to shorten code and avoid clashes.
