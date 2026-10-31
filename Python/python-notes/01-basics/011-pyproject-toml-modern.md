---

# 011. pyproject.toml (modern)
# हिंदी में: pyproject.toml (आधुनिक project config)

---

## 🔵 Simple Definition (English)
`pyproject.toml` is the modern, standard configuration file of a Python project. In one TOML file you describe the project name, version, Python requirement, dependencies, build system and tool settings (pytest, ruff, black, mypy). It is defined by PEP 518, PEP 621 and later standards.

## 🔵 सरल परिभाषा (Hindi)
`pyproject.toml` Python project की आधुनिक, standard configuration file है। एक ही TOML file में project का नाम, version, Python requirement, dependencies, build system और tools (pytest, ruff, black, mypy) की settings लिखी जाती हैं। यह PEP 518, PEP 621 और बाद के standards से तय है।

---

## 🔴 Problem it Solves
Old projects scattered settings across many files: `setup.py` (executable code!), `setup.cfg`, `requirements.txt`, `pytest.ini`, `tox.ini`, `.flake8`, `mypy.ini`. Running `setup.py` just to read metadata was unsafe and slow, and nobody could declare "what do I need to build this package?" cleanly. pyproject.toml gives one static, declarative, tool-independent file.

## 🔴 यह क्यों बना? (Hindi)
पुराने projects में settings कई files में बिखरी थीं: `setup.py` (जो असल code था!), `setup.cfg`, `requirements.txt`, `pytest.ini`, `tox.ini`, `.flake8`, `mypy.ini`। सिर्फ metadata पढ़ने के लिए `setup.py` चलाना असुरक्षित और धीमा था। पैकेज build करने के लिए क्या चाहिए, यह भी साफ़ नहीं लिख सकते थे। pyproject.toml एक static, declarative, tool-independent file देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create pyproject.toml in the project root
Step 2 → [build-system]  : which tool builds the package (setuptools, hatchling, poetry-core)
Step 3 → [project]       : name, version, requires-python, dependencies (PEP 621)
Step 4 → [project.optional-dependencies] : extras like dev = ["pytest", "ruff"]
Step 5 → [tool.xxx]      : settings for tools, e.g. [tool.pytest.ini_options]
Step 6 → pip install .   (or pip install -e . for editable) reads this file,
         installs the build tools, builds the project and installs dependencies
Step 7 → Modern managers (uv, poetry, hatch) also read it and create lock files
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Project root में pyproject.toml बनाएँ
Step 2 → [build-system]  : कौन-सा tool package build करेगा
Step 3 → [project]       : name, version, requires-python, dependencies
Step 4 → [project.optional-dependencies] : extras जैसे dev = ["pytest", "ruff"]
Step 5 → [tool.xxx]      : tools की settings, जैसे [tool.pytest.ini_options]
Step 6 → pip install . (या editable के लिए pip install -e .) यह file पढ़ता है,
         build tools install करता है, project build करके dependencies लगाता है
Step 7 → uv, poetry, hatch भी इसे पढ़कर lock file बनाते हैं
```

---

## 🟡 Real World Example
A team at a SaaS company ships an internal library `payments-core` used by five services. Its `pyproject.toml` declares `requires-python = ">=3.10"`, runtime dependencies, a `dev` extra (pytest, ruff, mypy) and tool config such as `line-length = 100` for ruff. A single file replaces six config files, and `pip install -e ".[dev]"` sets up a complete developer environment in one command.

## 🟡 Real Example Hindi mein
एक SaaS company की team internal library `payments-core` बनाती है जो पाँच services में use होती है। उसकी `pyproject.toml` में `requires-python = ">=3.10"`, runtime dependencies, `dev` extra (pytest, ruff, mypy) और ruff के लिए `line-length = 100` जैसी settings हैं। एक file छह config files की जगह लेती है, और `pip install -e ".[dev]"` से पूरा developer environment एक command में बन जाता है।

---

## 💻 Code Example — Basic
```python
# Basic: read a pyproject.toml using the standard library (tomllib, Python 3.11+)
import tomllib  # built-in TOML parser (read-only)

toml_text: str = """
[project]
name = "orders-api"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.100",
    "sqlalchemy>=2.0",
]

[tool.ruff]
line-length = 100
"""  # a minimal project file as a string

data: dict = tomllib.loads(toml_text)  # parse TOML text into a normal dict

project: dict = data["project"]  # the [project] table
print(project["name"])  # Output: orders-api
print(project["version"])  # Output: 0.1.0
print(project["dependencies"])  # Output: ['fastapi>=0.100', 'sqlalchemy>=2.0']
print(data["tool"]["ruff"]["line-length"])  # Output: 100
```

## 💻 Code Example — Advanced
```python
# Advanced: validate a pyproject.toml like a CI check would
from __future__ import annotations  # modern hints on all 3.x

import re  # to read the dependency names
import sys  # to compare with the running Python
import tomllib  # TOML parser (3.11+)
from dataclasses import dataclass, field  # structured result


@dataclass
class ProjectInfo:
    name: str  # project name
    version: str  # project version
    requires_python: str  # e.g. ">=3.10"
    dependencies: list[str] = field(default_factory=list)  # raw requirement strings

    def dependency_names(self) -> list[str]:
        """Return only package names, without version rules."""
        names: list[str] = []  # collected names
        for dep in self.dependencies:  # each requirement string
            m = re.match(r"[A-Za-z0-9_.\-]+", dep)  # leading name part
            if m:  # only if a name was found
                names.append(m.group(0).lower())  # lower-case for comparison
        return names  # list of names


def load_project(text: str) -> ProjectInfo:
    """Parse and validate the [project] table."""
    data = tomllib.loads(text)  # may raise tomllib.TOMLDecodeError
    project = data.get("project")  # None if table is missing
    if project is None:  # fail with a clear message
        raise ValueError("Missing [project] table")
    for key in ("name", "version"):  # required fields
        if key not in project:  # check each one
            raise ValueError(f"Missing project.{key}")
    return ProjectInfo(
        name=project["name"],  # copy name
        version=project["version"],  # copy version
        requires_python=project.get("requires-python", ""),  # optional field
        dependencies=project.get("dependencies", []),  # optional list
    )


def python_ok(requires: str) -> bool:
    """Support the common '>=X.Y' form only (use `packaging` for full rules)."""
    m = re.fullmatch(r">=(\d+)\.(\d+)", requires)  # parse ">=3.10"
    if not m:  # unknown format
        return True  # be permissive in this demo
    return sys.version_info[:2] >= (int(m[1]), int(m[2]))  # tuple compare


text = '[project]\nname = "demo"\nversion = "1.0"\nrequires-python = ">=3.10"\ndependencies = ["FastAPI>=0.100", "uvicorn"]\n'
info = load_project(text)  # parse the sample
print(info.name, info.version)  # Output: demo 1.0
print(info.dependency_names())  # Output: ['fastapi', 'uvicorn']
print(python_ok(info.requires_python))  # Output: True (on Python 3.10 or newer)

try:
    load_project('[tool.ruff]\nline-length = 100\n')  # no [project] table
except ValueError as exc:  # our validation error
    print(f"Invalid: {exc}")  # Output: Invalid: Missing [project] table
```

---

## 🟠 JavaScript vs Python Comparison
`pyproject.toml` is Python's `package.json`: name, version, dependencies, scripts-like tool config in one file. Differences: TOML syntax instead of JSON (comments allowed!), and in Python the lock file (uv.lock, poetry.lock) is separate and tool-specific, while `package-lock.json` is standard for npm.

```python
# Python: pyproject.toml (TOML syntax, comments allowed)
# [project]
# name = "orders-api"
# version = "0.1.0"
# dependencies = ["fastapi>=0.100"]
#
# [tool.pytest.ini_options]
# testpaths = ["tests"]
import tomllib  # read it from Python

with open("pyproject.toml", "rb") as fh:  # tomllib needs binary mode
    cfg = tomllib.load(fh)  # dict like json.load
```
```javascript
// JavaScript: package.json (JSON, no comments)
// {
//   "name": "orders-api",
//   "version": "0.1.0",
//   "dependencies": { "express": "^4.19.0" },
//   "jest": { "testMatch": ["**/tests/**"] }
// }
const cfg = require("./package.json"); // read it from Node
```

---

## 🟠 FastAPI Connection
FastAPI itself is published with a `pyproject.toml`, and most FastAPI apps use one to declare dependencies and configure tools. With `uv` or `poetry` you run `uv add fastapi` and the dependency lands in the `[project]` table automatically. `requires-python` tells everyone which Python the API supports.

```python
# pyproject.toml of a FastAPI service (kept in a string for demonstration):
PYPROJECT: str = """\
[project]
name = "orders-api"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "fastapi[standard]>=0.115",
    "sqlalchemy>=2.0",
]

[project.optional-dependencies]
dev = ["pytest", "httpx", "ruff"]

[tool.pytest.ini_options]
testpaths = ["tests"]
"""
# Install for development:  python -m pip install -e ".[dev]"
import tomllib  # read it back

print(tomllib.loads(PYPROJECT)["project"]["optional-dependencies"]["dev"])  # Output: ['pytest', 'httpx', 'ruff']
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Wrong TOML syntax (it is not JSON or Python)
```python
# Wrong:
#   name = 'orders-api'            # fine, but
#   dependencies = fastapi, uvicorn  # TOML error: lists need [ ] and quotes
#   enabled = True                   # TOML booleans are lower-case: true
# Right:
#   dependencies = ["fastapi", "uvicorn"]
#   enabled = true
```
✅ Correct: strings in quotes, lists in brackets, booleans lower-case.

❌ Mistake 2: Missing `[build-system]` or confusing it with dependencies
```python
# Wrong: putting setuptools under [project].dependencies (it is a BUILD need)
# Right:
#   [build-system]
#   requires = ["setuptools>=68"]
#   build-backend = "setuptools.build_meta"
```
✅ Correct: build tools go to `[build-system]`, runtime libraries to `[project].dependencies`.

❌ Mistake 3: Expecting `pyproject.toml` to pin exact versions like a lock file
```python
# Wrong: dependencies = ["fastapi>=0.100"] and assuming builds are identical
# Right: also keep a lock file (uv.lock / poetry.lock) or a pinned requirements.txt
```
✅ Correct: pyproject.toml states what is ALLOWED, the lock file states what is INSTALLED.

---

## 🧠 Tricky Interview Question

```python
import tomllib

print(tomllib.loads('a = 1\nb = "2"\nc = [1, 2]\nd = true'))
```
Answer: `{'a': 1, 'b': '2', 'c': [1, 2], 'd': True}`. TOML has real types: integers, strings, arrays and booleans, and `tomllib` converts them to Python `int`, `str`, `list` and `bool`. Follow-up trap: `tomllib` can only READ TOML (no `dump`); to write TOML you need a third-party library such as `tomli-w`. Also `tomllib.load()` needs a file opened in binary mode (`"rb"`), otherwise it raises a TypeError.

---

## ⚫ Interview Questions + Answers

Q1: What is pyproject.toml and why was it introduced?
A1: A standard, static configuration file for Python projects. PEP 518 introduced `[build-system]` so tools know what is needed to build a package without running arbitrary `setup.py` code. PEP 621 added the `[project]` table for metadata and dependencies. It also holds `[tool.*]` settings for linters, formatters and test runners.

Q2: requirements.txt vs pyproject.toml?
A2: requirements.txt is just an installation list (often fully pinned, good for deploying an app). pyproject.toml describes the project: metadata, abstract dependency ranges, extras, build system and tool config. Libraries must use pyproject.toml; apps often use both, or use a lock file from uv/poetry.

Q3: What goes into `[build-system]`?
A3: `requires` (packages needed to build, such as `setuptools` or `hatchling`) and `build-backend` (the Python object that performs the build). pip reads this to create an isolated build environment automatically.

Q4: What are optional dependencies (extras)?
A4: Groups of extra packages under `[project.optional-dependencies]`, installed with `pip install "mypkg[dev]"`. Typical groups: `dev`, `test`, `docs`. This keeps production installs small while developers get tooling.

Q5: What replaced `setup.py`?
A5: Declarative config in pyproject.toml plus a build backend (setuptools, hatchling, flit, poetry-core, maturin). You build with `python -m build` and install with `pip install .`. `setup.py` is still supported for legacy cases but is no longer recommended for new projects.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Starting any new project (apps and libraries)
- Configuring pytest, ruff, black, mypy in one place
- Using uv, poetry or hatch for dependency management

❌ Avoid when:
- A single tiny script with no dependencies (not needed)
- You only need a quick pinned install list for a Docker image (requirements.txt is fine)
- Never put secrets or passwords in it

---

## 📊 Visual Diagram
```
 pyproject.toml
 ┌───────────────────────────────────────────────┐
 │ [build-system]   → how to BUILD   (setuptools)│
 │ [project]        → WHAT it is     (name, deps)│
 │ [project.optional-dependencies] → extras      │
 │ [tool.ruff] [tool.pytest...] [tool.mypy]      │ → tool settings
 └───────────────┬───────────────────────────────┘
                 │ read by
      ┌──────────┼───────────┬────────────┐
      ▼          ▼           ▼            ▼
     pip         uv        poetry      ruff/pytest
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TOML | Simple config file format | सरल config file format |
| PEP 621 | Standard for `[project]` metadata | `[project]` metadata का standard |
| Build backend | Tool that builds the package | Package build करने वाला tool |
| Extras | Optional dependency groups | वैकल्पिक dependency groups |
| Lock file | Exact resolved versions | Exact resolved versions की file |
| `requires-python` | Supported Python versions | Supported Python versions |

---

## ⚡ 3-Line Summary
English: pyproject.toml is the single modern config file for a Python project: metadata, dependencies, build system and tool settings. It replaces setup.py, setup.cfg and many tool-specific files. Pair it with a lock file for reproducible installs.
Hindi: pyproject.toml Python project की एक आधुनिक config file है: metadata, dependencies, build system और tool settings सब एक जगह। यह setup.py, setup.cfg और कई tool files की जगह लेती है। Reproducible installs के लिए इसके साथ lock file रखें।

---

## ➡️ Next Topic
**012. Python Interactive Shell (REPL)** — experiment with code line by line, the fastest way to learn and debug.
