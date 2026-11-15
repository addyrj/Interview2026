---

# 174. import as (alias)
# हिंदी में: import as (module या नाम को छोटा/दूसरा नाम देना)

---

## 🔵 Simple Definition (English)
`import X as Y` loads module `X` but binds it to the name `Y` in your file. `from X import A as B` does the same for one name. The original name (`X` or `A`) is NOT created in your file.

## 🔵 सरल परिभाषा (Hindi)
`import X as Y` module `X` को load करता है लेकिन आपकी file में उसे `Y` नाम से जोड़ता है। `from X import A as B` एक नाम के लिए यही करता है। असली नाम (`X` या `A`) आपकी file में नहीं बनता।

---

## 🔴 Problem it Solves
Long names (`matplotlib.pyplot`) are tiring to type. Two libraries may export the same name (`json.dumps` and `orjson.dumps`). An alias shortens the name, avoids a clash, and lets you swap implementations in one line.

## 🔴 यह क्यों बना? (Hindi)
`matplotlib.pyplot` जैसे लंबे नाम बार-बार लिखना थकाने वाला है। दो libraries एक ही नाम दे सकती हैं (`json.dumps` और `orjson.dumps`)। Alias नाम छोटा करता है, टकराव रोकता है और implementation एक ही line में बदलने देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python imports the module normally (same cache, same single run)
Step 2 → Instead of binding "X", it binds the alias "Y" to the module object
Step 3 → X and Y (if both imported) point to the SAME object: `X is Y`
Step 4 → Only the alias exists in your namespace; using "X" gives NameError
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → module सामान्य तरीके से import होता है (वही cache, एक ही बार run)
Step 2 → असली नाम की जगह alias "Y" उस module object से जुड़ता है
Step 3 → X और Y दोनों import करें तो एक ही object होंगे: X is Y
Step 4 → namespace में सिर्फ alias रहता है; "X" लिखने पर NameError
```

---

## 🟡 Real World Example
Data and AI code uses community conventions: `import numpy as np`, `import pandas as pd`, `import matplotlib.pyplot as plt`. A Swiggy service imports `from datetime import datetime as dt`. A library picks a fast JSON encoder: `import orjson as json` if installed, else standard `json`.

## 🟡 Real Example Hindi mein
Data और AI code में conventions हैं: `import numpy as np`, `import pandas as pd`। Swiggy जैसी service में `from datetime import datetime as dt` दिखता है। Library fast JSON चाहे तो `orjson` को `json` नाम से import कर लेती है, न मिले तो standard `json`।

---

## 💻 Code Example — Basic
```python
# Basic alias examples - every line commented
import math as m  # module alias
print(m.sqrt(25))  # use the short alias
# Output: 5.0

import os.path as osp  # alias for a submodule (dotted path)
print(osp.join("a", "b"))  # os.path.join via the alias
# Output: a/b

from math import sqrt as root, pi as PI  # alias individual names
print(root(9), round(PI, 2))  # use the new names
# Output: 3.0 3.14

import json, json as j  # import the same module twice with two names
print(json is j)  # both names point at ONE module object
# Output: True

try:  # the original name was not created for "import math as m"
    print(math.pi)  # type: ignore[name-defined]  # math is not defined here
except NameError as exc:  # NameError, not ImportError
    print(exc)  # show the message
# Output: name 'math' is not defined
```

## 💻 Code Example — Advanced
```python
# Production style: swap implementations with an alias + resolve clashes
from __future__ import annotations  # modern type-hint behaviour
from typing import Any, Callable  # type hints

try:  # fast optional dependency
    import orjson as _fastjson  # type: ignore[import-not-found]
    def dumps(obj: Any) -> str:  # wrap so the return type is str
        return _fastjson.dumps(obj).decode()  # orjson returns bytes
except ImportError:  # fallback: standard library
    from json import dumps as _std_dumps  # alias the stdlib function
    def dumps(obj: Any) -> str:  # same public signature
        return _std_dumps(obj, separators=(",", ":"))  # compact output

print(dumps({"id": 1, "tags": ["a", "b"]}))  # callers never know which one
# Output: {"id":1,"tags":["a","b"]}

# Name clash: two functions called "loads" -> alias both clearly
from json import loads as json_loads  # JSON text -> Python
from pickle import loads as pickle_loads  # bytes -> Python (unsafe on untrusted data)

parsers: dict[str, Callable[[Any], Any]] = {  # a dispatch table
    "json": json_loads,  # alias keeps meanings visible
    "pickle": pickle_loads,
}
print(parsers["json"]('{"x": 5}'))  # call through the table
# Output: {'x': 5}

# datetime clash: module vs class share the word "datetime"
import datetime as dtm  # the module
from datetime import datetime as DateTime  # the class
print(isinstance(DateTime(2024, 1, 2), dtm.date))  # class is a date subclass
# Output: True
print(dtm.timedelta(days=1))  # module-level helper
# Output: 1 day, 0:00:00
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import numpy as np                  # alias whole module
from os.path import join as pjoin   # alias one name
```

```javascript
// JavaScript
import * as np from "numpy-js";            // alias the namespace
import { join as pjoin } from "path";      // alias one export
const fs = require("fs");                  // CommonJS: any variable name works
```

Key difference: JS `import { a as b }` and Python `from m import a as b` are almost identical. Python additionally lets you alias a dotted module: `import os.path as osp`.

---

## 🟠 FastAPI Connection
FastAPI projects alias routers: each module exposes `router`, and `main.py` renames them so names do not collide. SQLAlchemy models and Pydantic schemas often share a name (`User`), so aliasing keeps them apart.

```python
# FastAPI aliasing (needs: pip install fastapi)
from fastapi import APIRouter, FastAPI  # core classes

users_router: APIRouter = APIRouter(prefix="/users")  # stand-in for: from app.users import router as users_router
orders_router: APIRouter = APIRouter(prefix="/orders")  # stand-in for: from app.orders import router as orders_router

app: FastAPI = FastAPI()  # create the app
app.include_router(users_router)  # attach /users
app.include_router(orders_router)  # attach /orders
# in a real project:
#   from app.models import User as UserModel     (SQLAlchemy)
#   from app.schemas import User as UserSchema   (Pydantic)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the original name after aliasing
```python
# Wrong:
import math as m
# print(math.pi)   -> NameError

# Correct:
print(m.pi)
```

❌ Mistake 2: Shadowing a built-in or other module with an alias
```python
# Wrong - hides the built-in sum() and breaks later code:
# from numpy import sum as sum   (or: from numpy import *)

# Correct - use a distinct name:
from numpy import sum as np_sum  # needs numpy; shown for the idea
```

❌ Mistake 3: Inventing unusual aliases
```python
# Wrong - confusing for teammates:
# import pandas as banana

# Correct - use the community convention:
# import pandas as pd
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import os.path as p
import os
print(p is os.path, p.__name__)
import xml.etree.ElementTree as ET
print(ET.__name__)
import os.path
print("os" in dir(), "p" in dir())
```

**Answer**:
```
True posixpath
xml.etree.ElementTree
True True
```
`os.path` is just the `posixpath` module on macOS/Linux (`ntpath` on Windows), so the alias has that real name. `import a.b.c as X` binds the innermost module `c` (here `ElementTree`) to `X`, not the top package `xml`. The final `import os.path` binds the name `os`.

---

## ⚫ Interview Questions + Answers

Q1: Does an alias import the module twice?
A1: No. The module is loaded once and cached in `sys.modules`. The alias is only another name for the same object.

Q2: What does `import a.b.c as X` bind?
A2: The submodule `a.b.c` itself. Without `as`, `import a.b.c` binds only the top name `a`.

Q3: Why is `import numpy as np` universal?
A3: A community convention: short, readable, and shown in every doc/tutorial, so everyone understands it.

Q4: Can I alias at the same time as importing many names?
A4: Yes: `from math import sqrt as root, pi as PI`. Each item may have its own alias.

Q5: How do aliases help with optional dependencies?
A5: `try: import orjson as json / except ImportError: import json` gives the same name to either module, so the rest of the code does not change.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- A community convention exists (`np`, `pd`, `plt`)
- Two imports would clash (`datetime` module vs class)
- You wrap an optional/alternative library behind one name

❌ Avoid when:
- The alias hides a built-in (`sum`, `list`, `id`)
- The alias is cryptic and not a standard convention
- The name is short already (`import os as o` adds nothing)

---

## 📊 Visual Diagram

```
 import numpy as np
        │
        ▼
 sys.modules["numpy"] ──► <module numpy>      (loaded once)
                              ▲
 your namespace:  np ─────────┘
                  numpy  ✖  (NOT created)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Alias | Another name for an object | दूसरा नाम |
| Convention | Agreed community style | सामुदायिक नियम |
| Name clash | Two things with one name | नामों का टकराव |
| Dotted import | `import a.b.c` | नेस्टेड module import |
| Fallback | Backup if the first fails | विकल्प |
| Shadowing | Hiding an existing name | नाम को ढक देना |

---

## ⚡ 3-Line Summary
English: `as` binds a module or name under a new name; the original name is not created. The module still loads once, and the alias points to the same object. Use conventions and avoid shadowing built-ins.
Hindi: `as` module या नाम को नए नाम से जोड़ता है; असली नाम नहीं बनता। Module एक ही बार load होता है और alias उसी object को दिखाता है। Conventions follow करें और built-ins को न ढकें।

---

## ➡️ Next Topic
**175. `__name__ == "__main__"`** — make a file work both as a script and as an importable module.
