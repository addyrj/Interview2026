---

# 008. Virtual Environment
# हिंदी में: Virtual Environment (अलग Python माहौल)

---

## 🔵 Simple Definition (English)
A virtual environment (venv) is an isolated folder that holds its own Python interpreter link and its own installed packages. Each project gets its own venv, so packages of one project never interfere with another project or with the system Python.

## 🔵 सरल परिभाषा (Hindi)
Virtual environment (venv) एक अलग folder है जिसमें अपना Python interpreter link और अपने installed packages होते हैं। हर project का अपना venv होता है, इसलिए एक project के packages दूसरे project या system Python से नहीं टकराते।

---

## 🔴 Problem it Solves
Without venvs, all packages go into one global place. Project A needs `pydantic 1.x`, Project B needs `pydantic 2.x`. Only one can be installed, so one project breaks. Also, installing globally can damage tools the operating system itself uses. A venv gives every project its own private set of packages, so versions can differ safely.

## 🔴 यह क्यों बना? (Hindi)
venv के बिना सारे packages एक global जगह जाते हैं। Project A को `pydantic 1.x` चाहिए, Project B को `pydantic 2.x`। दोनों में से सिर्फ एक install हो सकता है, तो एक project टूट जाता है। Global install से operating system के अपने tools भी खराब हो सकते हैं। venv हर project को अपने private packages देता है, इसलिए versions अलग-अलग रह सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → python3 -m venv .venv
         Creates the folder .venv/ with:
           bin/python  (Scripts\python.exe on Windows)  -> link to base Python
           lib/python3.13/site-packages/                -> EMPTY package folder
           pyvenv.cfg                                   -> settings file
Step 2 → source .venv/bin/activate     (Windows: .venv\Scripts\activate)
         Activation puts .venv/bin at the FRONT of PATH and changes the prompt
Step 3 → `python` and `pip` now resolve to the venv copies
Step 4 → pip install fastapi  -> goes into .venv/lib/.../site-packages ONLY
Step 5 → deactivate  -> PATH restored, back to system Python
Step 6 → Never commit .venv/ to git (add it to .gitignore)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → python3 -m venv .venv  → .venv/ folder बनता है
         (bin/python, खाली site-packages, और pyvenv.cfg)
Step 2 → source .venv/bin/activate (Windows: .venv\Scripts\activate)
         PATH में .venv/bin सबसे आगे लग जाता है, prompt बदल जाता है
Step 3 → अब `python` और `pip` venv वाले चलते हैं
Step 4 → pip install fastapi → सिर्फ .venv के अंदर install होता है
Step 5 → deactivate → वापस system Python
Step 6 → .venv/ को कभी git में commit न करें (.gitignore में डालें)
```

---

## 🟡 Real World Example
A Zomato-style company has 30 microservices. The orders service uses FastAPI 0.110 and Python 3.11. The recommendations service uses an older scikit-learn on Python 3.9. Each developer keeps one venv per service, so working on both on the same laptop causes no conflicts. In CI/CD, the pipeline creates a fresh venv, installs from `requirements.txt` and runs tests, which proves the project builds from scratch.

## 🟡 Real Example Hindi mein
Zomato जैसी company में 30 microservices हैं। Orders service FastAPI 0.110 और Python 3.11 पर है। Recommendations service पुराने scikit-learn और Python 3.9 पर है। हर developer हर service के लिए अलग venv रखता है, इसलिए एक ही laptop पर दोनों पर काम करने में conflict नहीं होता। CI/CD pipeline नया venv बनाती है, `requirements.txt` से install करती है और tests चलाती है, जिससे साबित होता है कि project शून्य से build हो जाता है।

---

## 💻 Code Example — Basic
```python
# Basic: create a venv from Python code and inspect it
import tempfile  # to make a throwaway folder
import venv  # the standard library venv module
from pathlib import Path  # friendly path handling

with tempfile.TemporaryDirectory() as tmp:  # folder deleted automatically at the end
    env_dir: Path = Path(tmp) / ".venv"  # where the venv will live
    venv.create(env_dir, with_pip=False)  # same as: python3 -m venv (no pip, faster)

    cfg: Path = env_dir / "pyvenv.cfg"  # settings file every venv has
    print(cfg.exists())  # Output: True

    has_bin: bool = (env_dir / "bin").exists() or (env_dir / "Scripts").exists()  # Mac/Linux or Windows
    print(has_bin)  # Output: True

    first_line: str = cfg.read_text().splitlines()[0]  # first line of the cfg file
    print(first_line.split("=")[0].strip())  # Output: home  (path to the base Python)
```

## 💻 Code Example — Advanced
```python
# Advanced: detect a venv and build one with a reusable helper
from __future__ import annotations  # modern type hints everywhere

import subprocess  # run the venv's own python
import sys  # sys.prefix / sys.base_prefix tell us if we are in a venv
import tempfile  # temporary folder for the demo
import venv  # create the environment
from pathlib import Path  # path handling


def in_virtualenv() -> bool:
    """True when the running interpreter belongs to a venv."""
    return sys.prefix != sys.base_prefix  # inside a venv these two differ


def create_env(target: Path, *, with_pip: bool = False) -> Path:
    """Create a venv and return the path of its python executable."""
    builder = venv.EnvBuilder(clear=True, with_pip=with_pip)  # clear=True resets old content
    builder.create(target)  # build the environment on disk
    sub = "Scripts" if sys.platform == "win32" else "bin"  # folder name differs per OS
    exe = "python.exe" if sys.platform == "win32" else "python"  # executable name per OS
    return target / sub / exe  # full path to the venv python


print(f"Inside venv? {in_virtualenv()}")  # Output: Inside venv? False (when run with system Python)

with tempfile.TemporaryDirectory() as tmp:  # temp area for the demo
    python_path: Path = create_env(Path(tmp) / "demo")  # build the venv
    out = subprocess.run(  # ask the NEW python about itself
        [str(python_path), "-c", "import sys; print(sys.prefix != sys.base_prefix)"],
        capture_output=True,  # capture printed text
        text=True,  # return str, not bytes
        check=True,  # raise if the command fails
    )
    print(f"Child python inside venv? {out.stdout.strip()}")  # Output: Child python inside venv? True
```

---

## 🟠 JavaScript vs Python Comparison
In Node.js, `npm install` creates a local `node_modules` folder per project automatically. Python does NOT do this by default; you must create and activate a venv yourself. Think of `.venv` as Python's `node_modules` plus its own interpreter.

```python
# Python (terminal commands as comments)
# python3 -m venv .venv                 # create (once per project)
# source .venv/bin/activate             # activate (every new terminal)
# python3 -m pip install fastapi        # installs into .venv only
# deactivate                            # leave the venv
```
```javascript
// JavaScript (terminal commands as comments)
// npm init -y                  // create package.json (once)
// npm install express          // installs into ./node_modules automatically
// no activation step needed
// node app.js                  // always uses local node_modules
```

---

## 🟠 FastAPI Connection
Every FastAPI project should live in its own venv, so that `fastapi`, `uvicorn`, `pydantic` and `sqlalchemy` versions are isolated and reproducible. In Docker you often skip the venv because the container itself is the isolation, but locally and in CI the venv is essential.

```python
# Typical FastAPI project setup (shell commands as comments):
#   python3 -m venv .venv
#   source .venv/bin/activate
#   python3 -m pip install "fastapi[standard]" sqlalchemy
#   python3 -m pip freeze > requirements.txt
import sys  # to prove which environment FastAPI will run in

from fastapi import FastAPI  # installed in the venv, not globally

app: FastAPI = FastAPI()  # create the app


@app.get("/env")  # GET /env
def env_info() -> dict[str, str]:  # return type documented
    return {"prefix": sys.prefix}  # shows the venv folder path in the response
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting to activate the venv
```python
# Wrong: venv created, but you run `pip install` without activating
#   -> package goes to the global Python, import fails inside the venv
# Right:
#   source .venv/bin/activate
#   python3 -m pip install requests
# Check: `which python` should point inside .venv
```
✅ Correct: activate first, then install; confirm with `which python`.

❌ Mistake 2: Committing `.venv` to git or moving/copying the folder
```python
# Wrong: git add .venv   (huge, and paths are machine-specific)
# Wrong: cp -r old/.venv new/.venv   (absolute paths inside break)
# Right: add `.venv/` to .gitignore and recreate:
#   python3 -m venv .venv
#   python3 -m pip install -r requirements.txt
```
✅ Correct: venvs are disposable; rebuild them from `requirements.txt`.

❌ Mistake 3: Creating the venv with the wrong Python version
```python
# Wrong: `python -m venv .venv` used an old Python 3.8
# Right: choose explicitly
#   python3.12 -m venv .venv
```
✅ Correct: the venv inherits the Python used to create it; pick the version deliberately.

---

## 🧠 Tricky Interview Question

```python
# Inside an activated venv, what does this print?
import sys
print(sys.prefix == sys.base_prefix)
print(sys.prefix.endswith(".venv"))
```
Answer: `False` and `True` (assuming the venv folder is named `.venv`). Inside a venv, `sys.prefix` points to the venv folder while `sys.base_prefix` still points to the Python installation the venv was made from. Outside a venv they are equal. This is exactly how libraries and scripts detect "am I inside a virtual environment?". Also note: a venv does not copy the interpreter fully; on Mac/Linux it usually creates a symlink to the base Python.

---

## ⚫ Interview Questions + Answers

Q1: What is a virtual environment and why use it?
A1: An isolated Python environment with its own site-packages. It prevents version conflicts between projects, keeps the system Python clean, and makes projects reproducible because you can freeze exact versions. Without it, installing a package for one project may break another.

Q2: What does `activate` actually do?
A2: It prepends the venv's `bin` (or `Scripts`) folder to PATH, sets `VIRTUAL_ENV`, and changes the shell prompt. That's all. You can skip activation by calling `.venv/bin/python` directly, which is what production scripts and systemd services often do.

Q3: venv vs virtualenv vs conda vs poetry vs uv?
A3: `venv` is built into Python (standard). `virtualenv` is an older third-party tool with more features and speed. `conda` manages environments AND non-Python packages (CUDA, C libraries). `poetry` and `uv` manage dependencies plus the venv together using `pyproject.toml` and lock files; `uv` is extremely fast.

Q4: Should you use a venv inside Docker?
A4: Not required, since the container already isolates the app. Many teams still use a venv in multi-stage builds: build the venv in a builder stage, then copy it to a slim final image. This keeps the final image small and reproducible.

Q5: How do you recreate a teammate's environment?
A5: Clone the repo, create a new venv, then run `python -m pip install -r requirements.txt` (or `uv sync` / `poetry install`). Never share the `.venv` folder itself; share the dependency file.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every Python project, always, from day one
- CI pipelines and local development
- Testing code against different library versions

❌ Avoid when:
- Inside a tiny Docker image where the container already isolates (optional, not harmful)
- You need non-Python system libraries managed too (consider conda)
- Never commit or copy the venv between machines

---

## 📊 Visual Diagram
```
   System Python (global)           project-a/                project-b/
   ┌────────────────────┐        ┌───────────────────┐    ┌───────────────────┐
   │ python 3.13        │        │ .venv/            │    │ .venv/            │
   │ site-packages:     │        │  pydantic 1.10    │    │  pydantic 2.9     │
   │  (keep it clean!)  │        │  fastapi 0.80     │    │  fastapi 0.115    │
   └────────────────────┘        └───────────────────┘    └───────────────────┘
            ▲                              ▲                        ▲
            └──── base_prefix ─────────────┴──── prefix (different per venv)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| venv | Built-in virtual environment tool | Built-in virtual environment tool |
| Activate | Switch shell to use the venv | Shell को venv पर switch करना |
| site-packages | Where packages are installed | जहाँ packages install होते हैं |
| `sys.prefix` | Path of the current environment | मौजूदा environment का path |
| `sys.base_prefix` | Path of the base Python | Base Python का path |
| `.gitignore` | File listing what git must skip | Git को क्या छोड़ना है उसकी list |

---

## ⚡ 3-Line Summary
English: A venv gives each project its own isolated packages. Create it with `python3 -m venv .venv`, activate it, then use `python -m pip install`. Never commit the venv; share `requirements.txt` instead.
Hindi: venv हर project को अलग isolated packages देता है। `python3 -m venv .venv` से बनाएँ, activate करें, फिर `python -m pip install` चलाएँ। venv को commit न करें, `requirements.txt` share करें।

---

## ➡️ Next Topic
**009. pip vs pip3 vs conda** — which installer command to use and when conda is the better choice.
