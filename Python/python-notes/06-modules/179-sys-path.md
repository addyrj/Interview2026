---

# 179. sys.path
# हिंदी में: sys.path (modules खोजने का रास्ता)

---

## 🔵 Simple Definition (English)
`sys.path` is a normal Python list of folder (or zip) paths. When you write `import x`, Python looks for `x` in these places in order and uses the first match. Changing the list changes where Python searches.

## 🔵 सरल परिभाषा (Hindi)
`sys.path` folders (या zip) के रास्तों की एक सामान्य Python list है। `import x` लिखने पर Python इन जगहों में क्रम से `x` खोजता है और पहला match इस्तेमाल करता है। List बदलने से खोज की जगह बदल जाती है।

---

## 🔴 Problem it Solves
Python needs a defined rule to find modules: your script's folder, installed packages (`site-packages`), the standard library. `sys.path` makes that rule visible and adjustable, so you can debug "ModuleNotFoundError", load plugins from a custom folder or understand why the wrong module got imported.

## 🔴 यह क्यों बना? (Hindi)
Python को modules खोजने का तय नियम चाहिए: आपकी script का folder, installed packages (`site-packages`), standard library। `sys.path` यह नियम दिखाता और बदलने देता है, ताकि "ModuleNotFoundError" debug हो, custom folder से plugins load हों या समझ आए कि गलत module क्यों import हुआ।

---

## 🟢 How it Works — Step by Step

```
Step 1 → `import x` : check sys.modules cache first
Step 2 → Not cached → walk sys.path from index 0 to the end
Step 3 → In each entry look for x/ (package) or x.py (module)
Step 4 → First match wins, later entries are never looked at
Step 5 → None found → ModuleNotFoundError: No module named 'x'
Order of sys.path: [script folder or cwd] + PYTHONPATH + stdlib + site-packages
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `import x` : पहले sys.modules cache देखता है
Step 2 → cache में न हो तो sys.path में index 0 से अंत तक चलता है
Step 3 → हर entry में x/ (package) या x.py (module) खोजता है
Step 4 → पहला match जीतता है, बाकी entries देखी ही नहीं जातीं
Step 5 → कुछ न मिले → ModuleNotFoundError
क्रम: [script folder / cwd] + PYTHONPATH + stdlib + site-packages
```

---

## 🟡 Real World Example
A Zomato CI job runs tests from a monorepo and fails with `No module named 'common'`; adding the repo root to `PYTHONPATH` (or installing the project with `pip install -e .`) fixes it. A plugin system adds `/opt/plugins` to `sys.path` at start-up and imports whatever it finds there.

## 🟡 Real Example Hindi mein
Zomato का CI job monorepo में tests चलाता है और `No module named 'common'` आता है; repo root को `PYTHONPATH` में डालने (या `pip install -e .`) से हल होता है। Plugin system शुरू में `/opt/plugins` को `sys.path` में जोड़कर वहाँ मिले modules import करता है।

---

## 💻 Code Example — Basic
```python
# Basic sys.path examples - every line commented
import sys  # the module that owns path
from pathlib import Path  # for building a temp module

print(type(sys.path).__name__)  # it is an ordinary list
# Output: list
print(len(sys.path) > 2)  # script dir + stdlib + more
# Output: True

import tempfile  # temp folder

with tempfile.TemporaryDirectory() as tmp:  # folder gone afterwards
    Path(tmp, "plugin_demo.py").write_text("VALUE = 42\n")  # a module only there
    try:  # not importable yet
        import plugin_demo  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:  # expected
        print(exc)  # message names the module
    # Output: No module named 'plugin_demo'

    sys.path.insert(0, tmp)  # highest priority = index 0
    import plugin_demo  # now it is found  # type: ignore[import-not-found]
    print(plugin_demo.VALUE)  # use it
    # Output: 42
    sys.path.remove(tmp)  # restore the original list
    sys.modules.pop("plugin_demo", None)  # forget it
```

## 💻 Code Example — Advanced
```python
# Production helpers: temporary path context manager, shadowing demo, and where a module came from.
import contextlib  # context manager helper
import importlib  # import_module
import sys  # sys.path / sys.modules
import tempfile  # sandbox
from pathlib import Path  # files
from typing import Iterator  # type hint


@contextlib.contextmanager
def extra_path(folder: str) -> Iterator[None]:
    """Add a folder to sys.path for a block, always restoring it."""
    sys.path.insert(0, folder)  # add with top priority
    try:
        yield  # run the caller's block
    finally:
        with contextlib.suppress(ValueError):  # ignore if already removed
            sys.path.remove(folder)  # restore


with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
    Path(first, "calc.py").write_text("WHO = 'first'\n")  # same module name in 2 folders
    Path(second, "calc.py").write_text("WHO = 'second'\n")  # duplicate
    sys.path[:0] = [first, second]  # first is searched before second
    try:
        calc = importlib.import_module("calc")  # first match wins
        print(calc.WHO)  # shadowing in action
        # Output: first
        print(Path(calc.__file__).parent == Path(first))  # confirm the origin
        # Output: True
    finally:
        sys.path.remove(first)  # cleanup
        sys.path.remove(second)  # cleanup
        sys.modules.pop("calc", None)  # forget cached module

    with extra_path(second):  # scoped addition
        calc = importlib.import_module("calc")  # now only "second" is visible
        print(calc.WHO)  # second wins here
        # Output: second
    print(second in sys.path)  # context manager restored sys.path
    # Output: False
    sys.modules.pop("calc", None)  # cleanup cache

print(sys.path[0] == "" or Path(sys.path[0]).exists())  # entry 0 is script dir (or '' in REPL/-c)
# Output: True
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import sys
sys.path.insert(0, "/opt/plugins")     # add search folder
import my_plugin                        # searched via sys.path
# env var: PYTHONPATH=/opt/plugins python app.py
```

```javascript
// JavaScript (Node)
// module.paths / NODE_PATH env var; node_modules lookup walks UP the folders
const p = require("/opt/plugins/my_plugin");   // usually an explicit path
// NODE_PATH=/opt/plugins node app.js
```

Key difference: Node walks up parent `node_modules` folders; Python searches a flat ordered list.

---

## 🟠 FastAPI Connection
`uvicorn app.main:app` must be able to import `app`. If it says `Could not import module "app.main"`, your project root is not on `sys.path`. Run uvicorn from the root, pass `--app-dir`, or install the project (`pip install -e .`). Never hack `sys.path` inside route files.

```python
# Diagnostic endpoint for a dev server (needs: pip install fastapi)
import sys  # sys.path
from typing import Dict, List  # type hints
from fastapi import FastAPI  # framework

app: FastAPI = FastAPI()  # create app


@app.get("/debug/path")  # GET /debug/path  (protect or remove in production!)
def debug_path() -> Dict[str, List[str]]:
    return {"sys_path": sys.path[:3]}  # first entries only
# CLI alternatives:   uvicorn main:app --app-dir src      |   PYTHONPATH=src uvicorn main:app
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Editing `sys.path` in every file
```python
# Wrong:
# import sys; sys.path.append("../")      # fragile, depends on cwd

# Correct: make the project installable and import normally
#   pip install -e .        (with pyproject.toml)
```

❌ Mistake 2: Naming your file like a stdlib/third-party module
```python
# Wrong: a local random.py / json.py / email.py  -> shadows the real one
# Correct: pick unique names; delete stale __pycache__
```

❌ Mistake 3: `append` when you needed priority
```python
# Wrong - an older installed copy wins because it is earlier in the list:
# sys.path.append("/my/fork")
# Correct:
# sys.path.insert(0, "/my/fork")
```

---

## 🧠 Tricky Interview Question

**Q**: You have a file `random.py` next to `main.py` containing `print("mine")`. `main.py` is:

```python
import random
print(random.randint(1, 6))
```
What happens?

**Answer**:
```
mine
AttributeError: module 'random' has no attribute 'randint'
```
(Python 3.13 adds a hint to the error: "consider renaming '.../random.py' since it has the same name as the standard library module named 'random' ...".)
`sys.path[0]` is the script's folder, searched before the standard library, so your own `random.py` shadows the stdlib one.

---

## ⚫ Interview Questions + Answers

Q1: What is in `sys.path[0]`?
A1: The directory of the script being run. For `python -m pkg.mod` it is the current directory, and for `python -c` it is an empty string `''` (meaning the current directory).

Q2: How do I add paths without code?
A2: Set the `PYTHONPATH` environment variable (colon-separated on Linux/macOS), or drop a `.pth` file in `site-packages`.

Q3: Is `sys.path` checked before `sys.modules`?
A3: No. `sys.modules` (cache) is consulted first; `sys.path` is only searched on a cache miss.

Q4: How do I stop Python adding the script folder?
A4: Run with `python -P` (3.11+) or `PYTHONSAFEPATH=1`, which avoids accidental shadowing from the cwd/script folder. Note that `python -I` (isolated mode) also ignores `PYTHONPATH` and the user site.

Q5: What is `pip install -e .` doing to sys.path?
A5: It registers your project folder (via a `.pth` file or an import hook) in `site-packages`, so it is importable from anywhere while still editable.

---

## 🔷 When to Use + When Not to Use

✅ Use `sys.path` edits when:
- Loading plugins from a user-provided folder
- Writing a quick one-off script or notebook helper
- Debugging import problems (print it)

❌ Avoid when:
- A proper package install (`pip install -e .`) can solve it
- It would run in library code (global side effect)
- You rely on the current working directory

---

## 📊 Visual Diagram

```
 import calc
    │
    ▼  sys.modules has "calc"? ── yes ──► use cached module
    │ no
    ▼
 sys.path = [ /my/script/dir,      ← index 0 (checked first)
              /usr/lib/python313.zip,
              /usr/lib/python3.13,
              .../site-packages ]  ← pip packages
    │
    └─ first folder containing calc.py or calc/ wins
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `sys.path` | Module search list | module खोज सूची |
| PYTHONPATH | Env var adding search paths | extra रास्तों वाला env var |
| site-packages | Folder for pip-installed libs | pip packages का folder |
| Shadowing | Local file hides a library | local file का library को ढकना |
| `.pth` file | File that adds paths | रास्ते जोड़ने वाली file |
| Editable install | `pip install -e .` | बदलाव तुरंत दिखने वाला install |

---

## ⚡ 3-Line Summary
English: `sys.path` is the ordered list of places Python searches for modules; the first match wins. Insert at 0 for priority, and prefer `pip install -e .` or `PYTHONPATH` over hacks. Local files can shadow libraries.
Hindi: `sys.path` modules खोजने की क्रमबद्ध list है; पहला match जीतता है। Priority के लिए index 0 पर डालें, और hacks की जगह `pip install -e .` या `PYTHONPATH` चुनें। Local files libraries को ढक सकती हैं।

---

## ➡️ Next Topic
**180. importlib** — import modules by string name at runtime (plugins, reload).
