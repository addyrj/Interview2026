---

# 177. Packages Structure
# हिंदी में: Packages की बनावट (project का folder layout)

---

## 🔵 Simple Definition (English)
A package is a folder of modules, and a package can contain sub-packages, which makes a tree. A good structure groups code by feature or layer (routers, models, services) so imports are predictable and nothing is tangled.

## 🔵 सरल परिभाषा (Hindi)
Package modules का folder है, और package के अंदर sub-packages हो सकते हैं, यानी एक tree बनता है। अच्छी structure code को feature या layer (routers, models, services) के हिसाब से बाँटती है ताकि imports साफ रहें और कुछ उलझे नहीं।

---

## 🔴 Problem it Solves
One 3000-line `main.py` is impossible to test, review or share between teams. Splitting into packages gives clear ownership, smaller files, reusable parts and fewer merge conflicts.

## 🔴 यह क्यों बना? (Hindi)
3000 line की एक `main.py` को test, review या teams में बाँटना नामुमकिन है। Packages में बाँटने से ownership साफ होती है, files छोटी होती हैं, हिस्से दोबारा काम आते हैं और merge conflicts घटते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick ONE top-level package for your code (e.g. app/)
Step 2 → Split by responsibility: api/, models/, schemas/, services/, core/
Step 3 → Add __init__.py to each folder; re-export the public names
Step 4 → Use ABSOLUTE imports from the top package (from app.core import config)
Step 5 → Run from the project root: python -m app.main / uvicorn app.main:app
Step 6 → Keep dependencies one-directional: api -> services -> models (never back)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → code के लिए एक top-level package चुनें (जैसे app/)
Step 2 → ज़िम्मेदारी से बाँटें: api/, models/, schemas/, services/, core/
Step 3 → हर folder में __init__.py रखें; public नाम re-export करें
Step 4 → top package से ABSOLUTE imports करें (from app.core import config)
Step 5 → project root से चलाएँ: python -m app.main / uvicorn app.main:app
Step 6 → dependency एक दिशा में रखें: api -> services -> models (उल्टी कभी नहीं)
```

---

## 🟡 Real World Example
A Swiggy-like order service: `app/api` (HTTP routes), `app/services` (business rules), `app/models` (DB tables), `app/schemas` (request/response shapes), `app/core` (settings, security). The same `services` package is imported by both the API and a Celery worker.

## 🟡 Real Example Hindi mein
Swiggy जैसी order service: `app/api` (HTTP routes), `app/services` (business rules), `app/models` (DB tables), `app/schemas` (request/response shape), `app/core` (settings, security)। वही `services` package API और Celery worker दोनों import करते हैं।

---

## 💻 Code Example — Basic
```python
# Create the layout in a temp folder and verify it imports.
import sys  # sys.path
import tempfile  # temp folder
from pathlib import Path  # file creation

LAYOUT: dict[str, str] = {  # relative path -> file content
    "app/__init__.py": "",  # top package marker
    "app/core/__init__.py": "",  # sub-package
    "app/core/config.py": "APP_NAME = 'orders'\n",  # settings module
    "app/services/__init__.py": "",  # sub-package
    "app/services/pricing.py": (  # business logic uses core via ABSOLUTE import
        "from app.core.config import APP_NAME\n"
        "def label(total: float) -> str:\n"
        "    return f'{APP_NAME}: Rs {total:.2f}'\n"
    ),
}

with tempfile.TemporaryDirectory() as tmp:  # sandbox
    for rel, text in LAYOUT.items():  # create every file
        path = Path(tmp, rel)  # full path
        path.parent.mkdir(parents=True, exist_ok=True)  # ensure folders
        path.write_text(text)  # write content
    sys.path.insert(0, tmp)  # tmp plays the role of the "project root"
    from app.services.pricing import label  # normal absolute import
    print(label(99.5))  # uses config through the package tree
    # Output: orders: Rs 99.50
    import app.services  # a package object
    print(app.services.__path__[0].endswith("services"))  # packages have __path__
    # Output: True
    sys.path.remove(tmp)  # cleanup
    for name in [m for m in sys.modules if m == "app" or m.startswith("app.")]:
        del sys.modules[name]  # forget temp modules
```

## 💻 Code Example — Advanced
```python
# Inspect a package tree and detect modules that import "upwards" (layer violation).
import ast  # parse code without running it
import tempfile  # sandbox
from pathlib import Path  # file walking
from typing import Dict, List, Set  # type hints

LAYERS: Dict[str, int] = {"core": 0, "models": 1, "services": 2, "api": 3}  # higher may import lower


def imports_of(path: Path) -> Set[str]:
    """Return top-level 'app.<layer>' names a file imports."""
    tree = ast.parse(path.read_text())  # parse source to a syntax tree
    found: Set[str] = set()  # collect layers
    for node in ast.walk(tree):  # visit every node
        if isinstance(node, ast.ImportFrom) and node.module:  # from x import y
            parts = node.module.split(".")  # ['app', 'api', 'routes']
            if parts[0] == "app" and len(parts) > 1:  # only our code
                found.add(parts[1])  # keep the layer name
    return found  # layers used


def violations(root: Path) -> List[str]:
    """List 'lower layer imports higher layer' mistakes."""
    problems: List[str] = []  # result list
    for file in sorted((root / "app").rglob("*.py")):  # every module
        layer = file.relative_to(root / "app").parts[0]  # first folder = layer
        if layer not in LAYERS:  # skip app/__init__.py
            continue
        for used in imports_of(file):  # layers this file imports
            if used in LAYERS and LAYERS[used] > LAYERS[layer]:  # points upward
                problems.append(f"{file.name}: {layer} -> {used}")  # record it
    return problems  # may be empty


with tempfile.TemporaryDirectory() as tmp:  # sandbox
    base = Path(tmp)  # root
    for rel, text in {  # a deliberately bad layout
        "app/__init__.py": "",
        "app/api/routes.py": "from app.services.pricing import label\n",
        "app/services/pricing.py": "from app.api.routes import label\n",  # BAD: upward
    }.items():
        p = base / rel  # target file
        p.parent.mkdir(parents=True, exist_ok=True)  # folders
        p.write_text(text)  # content
    print(violations(base))  # run the check
    # Output: ['pricing.py: services -> api']
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python tree
# app/
#   __init__.py
#   services/__init__.py
#   services/pricing.py
from app.services.pricing import label     # dotted path = folder path
```

```javascript
// JavaScript tree
// src/
//   services/index.js
//   services/pricing.js
import { label } from "./services/pricing.js";   // file path with ./ and extension
// Node resolves node_modules; Python resolves sys.path
```

Key difference: Python imports use dots and the root is defined by `sys.path`; JS imports use file paths relative to the current file.

---

## 🟠 FastAPI Connection
The official "bigger applications" layout is a package. Each router file exposes `router`, and `main.py` includes them. Use absolute imports and run `uvicorn app.main:app` from the project root.

```python
# Typical layout (text) + main.py wiring
#   project/
#   ├── app/
#   │   ├── __init__.py
#   │   ├── main.py
#   │   ├── api/{__init__.py, users.py, orders.py}
#   │   ├── services/  models/  schemas/  core/
#   ├── tests/
#   └── pyproject.toml
from fastapi import APIRouter, FastAPI  # framework

router: APIRouter = APIRouter(prefix="/ping")  # stand-in for app.api.users.router


@router.get("")  # GET /ping
def ping() -> dict[str, str]:
    return {"pong": "ok"}  # JSON response


app: FastAPI = FastAPI()  # in main.py: app.include_router(users.router) etc.
app.include_router(router)  # wire the router in
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Everything in one folder with `import utils` style imports
```python
# Wrong - works only when run from inside that folder:
# import services      # fails from another cwd

# Correct - one top package + absolute imports from the root:
# from app.services import pricing
```

❌ Mistake 2: Layers importing each other in both directions
```python
# Wrong: models imports services, services imports models  -> circular import
# Correct: models know nothing about services; services use models
```

❌ Mistake 3: Giant `utils.py` / `helpers.py`
```python
# Wrong - 40 unrelated functions dumped in utils.py
# Correct - name modules by purpose: dates.py, money.py, security.py
```

---

## 🧠 Tricky Interview Question

**Q**: Layout: `app/main.py` contains `from services import pricing`, and `app/services/pricing.py` exists. You run `python app/main.py` from `app/`'s parent. What happens, and what if you run `python -m app.main`?

**Answer**:
```
python app/main.py   -> works only if `services` is found: sys.path[0] is app/ (the script's folder),
                        so `services` resolves. It breaks the moment you run from elsewhere
                        or import app.main from tests (ModuleNotFoundError: No module named 'services').
python -m app.main   -> sys.path[0] is the project root, `services` is NOT top-level
                        -> ModuleNotFoundError. The correct import is `from app.services import pricing`.
```
Script-path runs put the *script's folder* on `sys.path`; `-m` puts the *current directory*. Always import from the top package name (`app.`) so both work.

---

## ⚫ Interview Questions + Answers

Q1: Module vs package?
A1: A module is one `.py` file. A package is a folder of modules (usually with `__init__.py`) and can nest sub-packages.

Q2: Layered or feature-based structure?
A2: Small apps use layers (`api/models/services`). Large apps group by feature (`users/`, `orders/`, each with its own router/models/service) so a team owns a whole slice.

Q3: Where do tests go?
A3: In a top-level `tests/` folder mirroring the package tree, not inside the package, so they are not shipped.

Q4: What is `src/` layout?
A4: Put the package under `src/app/`. It forces you to install the package before importing it, which catches packaging bugs. Popular for libraries.

Q5: How do I stop circular imports structurally?
A5: Keep dependencies one-directional between layers, put shared types in a low-level module (`core`/`schemas`), and import inside functions only as a last resort.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- The project has more than a few modules
- Several people or entry points (API, worker, CLI) share code
- You plan to package or deploy it

❌ Avoid when:
- A 50-line script (one file is fine)
- Over-nesting (`app/a/b/c/d/e.py`) hides code
- Splitting before you understand the boundaries

---

## 📊 Visual Diagram

```
 project/
 ├── pyproject.toml
 ├── tests/
 └── app/                 ← top-level package
     ├── main.py          ← creates FastAPI(), includes routers
     ├── api/             ← HTTP layer (depends on services, schemas)
     ├── services/        ← business rules (depends on models, core)
     ├── models/          ← DB tables  (depends on core)
     ├── schemas/         ← Pydantic shapes
     └── core/            ← config, security (depends on nothing)

 allowed direction:  api ──► services ──► models ──► core
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Package | Folder of modules | modules का folder |
| Sub-package | Package inside a package | package के अंदर package |
| Layer | Group by responsibility | ज़िम्मेदारी की परत |
| Project root | Folder where you run commands | project की जड़ folder |
| `src` layout | Code under `src/` | `src/` वाली बनावट |
| Entry point | File/command that starts the app | शुरू करने वाली जगह |

---

## ⚡ 3-Line Summary
English: Organize code as one top-level package with sub-packages by layer or feature. Use absolute imports from the top package and run from the project root. Keep dependencies one-way.
Hindi: Code को एक top-level package में layer या feature के sub-packages के रूप में रखें। Top package से absolute imports करें और project root से चलाएँ। Dependencies एक ही दिशा में रखें।

---

## ➡️ Next Topic
**178. Relative vs Absolute Imports** — which import style to use inside the package tree and why.
