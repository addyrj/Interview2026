---

# 007. Installing Python + pip
# हिंदी में: Python और pip को Install करना

---

## 🔵 Simple Definition (English)
Installing Python means putting the Python interpreter on your computer so it can run `.py` files. `pip` is Python's package installer: it downloads libraries (like FastAPI or requests) from PyPI (the Python Package Index) and installs them for you. pip comes bundled with Python 3.4+.

## 🔵 सरल परिभाषा (Hindi)
Python install करने का मतलब है अपने computer पर Python interpreter रखना ताकि वो `.py` files चला सके। `pip` Python का package installer है: ये PyPI (Python Package Index) से libraries (जैसे FastAPI, requests) download करके install करता है। pip, Python 3.4+ के साथ आता है।

---

## 🔴 Problem it Solves
Without pip you would download every library by hand, copy it into your project, and also hunt for the libraries it depends on. Versions would clash and updating would be painful. pip does: find package → resolve dependencies → download → install → record the version. One command replaces hours of manual work.

## 🔴 यह क्यों बना? (Hindi)
pip के बिना हर library हाथ से download करनी पड़ती, project में copy करनी पड़ती और उसकी dependencies भी खुद ढूँढनी पड़तीं। versions टकराते और update करना मुश्किल होता। pip यह सब करता है: package ढूँढो → dependencies resolve करो → download → install → version record। एक command घंटों का काम बचाती है।

---

## 🟢 How it Works — Step by Step

```
INSTALLING PYTHON
Step 1 → Download from python.org (or use a package manager)
         Mac:     brew install python
         Windows: installer from python.org (tick "Add Python to PATH")
         Linux:   sudo apt install python3 python3-pip python3-venv
Step 2 → Open a NEW terminal (so PATH refreshes)
Step 3 → Verify:  python3 --version   and   python3 -m pip --version

INSTALLING A PACKAGE WITH pip
Step 1 → pip contacts PyPI (pypi.org) and finds "requests"
Step 2 → It reads the package's dependency list (urllib3, certifi ...)
Step 3 → Downloads wheel files (.whl, pre-built) or source (.tar.gz)
Step 4 → Installs into site-packages of the CURRENT Python
Step 5 → Records metadata so `pip list` / `pip uninstall` work
```

## 🟢 कैसे काम करता है? (Hindi)
```
PYTHON INSTALL
Step 1 → python.org से download करें (या package manager से)
         Mac: brew install python | Linux: sudo apt install python3 python3-pip
         Windows: installer चलाएँ और "Add Python to PATH" tick करें
Step 2 → नया terminal खोलें (ताकि PATH refresh हो)
Step 3 → जाँचें: python3 --version और python3 -m pip --version

pip से PACKAGE INSTALL
Step 1 → pip, PyPI पर package ढूँढता है
Step 2 → उसकी dependencies की list पढ़ता है
Step 3 → wheel (.whl) file download करता है
Step 4 → मौजूदा Python के site-packages में install करता है
Step 5 → metadata save करता है ताकि pip list / uninstall चले
```

---

## 🟡 Real World Example
A new developer joins a Razorpay-style payments team. Day one: install Python 3.12, run `python3 -m pip install -r requirements.txt`, and the whole FastAPI service with 40 libraries is ready in two minutes. On a fresh Ubuntu EC2 server the same steps run in a deploy script. Common pip commands used daily: `pip install`, `pip uninstall`, `pip list`, `pip show`, `pip freeze`.

## 🟡 Real Example Hindi mein
Razorpay जैसी payments team में नया developer आता है। पहले दिन: Python 3.12 install, `python3 -m pip install -r requirements.txt` चलाया और 40 libraries वाली पूरी FastAPI service दो मिनट में तैयार। Ubuntu EC2 server पर यही steps deploy script में चलते हैं। रोज़ के pip commands: `pip install`, `pip uninstall`, `pip list`, `pip show`, `pip freeze`।

---

## 💻 Code Example — Basic
```python
# Basic: check that Python and pip are installed correctly
import importlib.util  # to check if a module can be found
import importlib.metadata  # to read installed package metadata
import sys  # info about the interpreter

# 1. Which interpreter file is running this code?
print(isinstance(sys.executable, str))  # Output: True
# (the real path differs per machine, e.g. /usr/local/bin/python3)

# 2. Is pip available for THIS interpreter?
pip_spec = importlib.util.find_spec("pip")  # returns None if pip is missing
print(pip_spec is not None)  # Output: True

# 3. Read the version of an installed package
pip_version: str = importlib.metadata.version("pip")  # e.g. "25.0.1" (varies)
print(pip_version.count(".") >= 1)  # Output: True (version looks like 25.0.1)

# 4. The recommended pip commands (shown as plain strings)
commands: list[str] = [
    "python3 -m pip install requests",  # install a package
    "python3 -m pip install requests==2.32.3",  # install an exact version
    "python3 -m pip install --upgrade requests",  # upgrade to the newest
    "python3 -m pip uninstall requests",  # remove a package
    "python3 -m pip list",  # list everything installed
    "python3 -m pip show requests",  # details of one package
]
for cmd in commands:  # loop through each command
    print(cmd)  # print it so you can copy it
```

## 💻 Code Example — Advanced
```python
# Advanced: safely run pip from Python and handle failures
from __future__ import annotations  # modern hints on all 3.x versions

import subprocess  # run external commands
import sys  # to get the current interpreter path
from dataclasses import dataclass  # small result container


@dataclass(frozen=True)  # immutable result object
class PipResult:
    ok: bool  # did the command succeed?
    output: str  # captured stdout text


def run_pip(*args: str, timeout: int = 60) -> PipResult:
    """Run `python -m pip <args>` using the SAME interpreter as this script."""
    cmd: list[str] = [sys.executable, "-m", "pip", *args]  # never call bare `pip`
    try:
        done = subprocess.run(  # execute the command
            cmd,  # command as a list (no shell, so no injection risk)
            capture_output=True,  # capture stdout and stderr
            text=True,  # decode bytes into str
            timeout=timeout,  # do not hang forever
            check=False,  # we inspect returncode ourselves
        )
    except subprocess.TimeoutExpired:  # command took too long
        return PipResult(False, "timeout")  # report failure
    return PipResult(done.returncode == 0, done.stdout.strip())  # success flag + text


result = run_pip("--version")  # ask pip for its version
print(result.ok)  # Output: True
print(result.output.startswith("pip "))  # Output: True  (e.g. "pip 25.0.1 from ...")

bad = run_pip("install", "--dry-run", "this-package-does-not-exist-xyz-123")  # fake name
print(bad.ok)  # Output: False  (needs network; fails offline too)
```

---

## 🟠 JavaScript vs Python Comparison
pip is like npm. `package.json` is like `requirements.txt` / `pyproject.toml`. PyPI is like the npm registry. The big difference: npm installs into a local `node_modules` folder by default, while pip installs into the global site-packages unless you use a virtual environment.

```python
# Python (terminal commands shown as comments)
# python3 -m pip install fastapi      # install a package
# python3 -m pip uninstall fastapi    # remove it
# python3 -m pip freeze > requirements.txt   # save versions
# python3 -m pip install -r requirements.txt # restore versions
import fastapi  # import after installing
```
```javascript
// JavaScript (terminal commands shown as comments)
// npm install express          // install a package (local by default)
// npm uninstall express        // remove it
// package.json + package-lock.json  // saved automatically
// npm install                  // restore from package.json
const express = require("express"); // require after installing
```

---

## 🟠 FastAPI Connection
FastAPI is not part of Python. You install it with pip: `pip install "fastapi[standard]"` (this also gives you the `uvicorn` server). Every FastAPI project starts with this step, and your Dockerfile repeats it with `pip install --no-cache-dir -r requirements.txt` to keep the image small.

```python
# After: python3 -m pip install "fastapi[standard]"
from fastapi import FastAPI  # works only if pip installed it in THIS interpreter

app: FastAPI = FastAPI()  # create the app


@app.get("/")  # root route
def home() -> dict[str, str]:  # simple handler with a return type
    return {"message": "installed correctly"}  # JSON response

# Run with: fastapi dev main.py   (or: uvicorn main:app --reload)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: pip installs into a different Python than the one you run
```python
# Wrong: `pip` may belong to Python 3.9 while `python` is 3.13
#   pip install requests
#   python app.py   -> ModuleNotFoundError: No module named 'requests'

# Right: tie pip to the exact interpreter
#   python3 -m pip install requests
#   python3 app.py
```
✅ Correct: always use `python3 -m pip`.

❌ Mistake 2: Forgetting "Add Python to PATH" on Windows
```python
# Symptom: 'python' is not recognized as an internal or external command
# Right: re-run the installer, tick "Add python.exe to PATH",
#        or use the launcher:  py -3 --version
```
✅ Correct: tick PATH during install or use the `py` launcher.

❌ Mistake 3: Using `sudo pip install` on Linux/Mac
```python
# Wrong: sudo pip install requests   (can break system tools)
# Right: use a virtual environment, then plain pip install
#   python3 -m venv .venv && source .venv/bin/activate
#   python3 -m pip install requests
```
✅ Correct: never use sudo with pip; use a venv.

---

## 🧠 Tricky Interview Question

```python
# Why does this fail even though "pip install numpy" printed success?
import numpy  # ModuleNotFoundError: No module named 'numpy'
```
Answer: pip and python are two different programs on your PATH. `pip` installed numpy into the site-packages of one Python (say 3.9), but `python` runs another (say 3.13), whose site-packages does not have numpy. Fix: run `python -m pip install numpy` so pip uses the same interpreter, or check with `python -m pip --version` which prints the path pip belongs to. Inside an activated venv both point to the same place, which is why venvs avoid this problem.

---

## ⚫ Interview Questions + Answers

Q1: What is pip and where does it download from?
A1: pip is the standard package installer for Python. By default it downloads from PyPI (pypi.org). You can point it at a private index with `--index-url` (companies use this for internal packages, e.g. Artifactory or AWS CodeArtifact).

Q2: What is a wheel (.whl) file?
A2: A wheel is a pre-built package format. Installing a wheel is fast because it only unpacks files and needs no compiler. Source distributions (.tar.gz) must be built first, which can need a C compiler. Packages like NumPy ship wheels for each OS and Python version.

Q3: Why `python -m pip` instead of `pip`?
A3: `python -m pip` guarantees pip runs with the same interpreter you will use to run your code. Plain `pip` is whichever pip comes first on PATH and may belong to a different Python. Pip's own docs recommend the `-m` form.

Q4: How do you upgrade pip itself and check outdated packages?
A4: `python -m pip install --upgrade pip` upgrades pip. `python -m pip list --outdated` shows packages with newer versions. In production, upgrade deliberately and test, instead of blindly upgrading everything.

Q5: What does `pip install "fastapi>=0.100,<1.0"` mean?
A5: It uses a version specifier. pip installs the newest FastAPI that is at least 0.100 and below 1.0. Common operators are `==` (exact), `>=`, `<=`, `~=` (compatible release), and `!=`. Quotes stop the shell from treating `>` as redirection.

---

## 🔷 When to Use + When Not to Use
✅ Use pip when:
- Installing libraries from PyPI inside a virtual environment
- Reproducing an environment from `requirements.txt`
- Building Docker images for Python services

❌ Avoid when:
- Installing into the system Python with `sudo` (use a venv instead)
- You need non-Python dependencies (CUDA, GDAL); conda may suit better
- You need fast, locked resolution for big teams; consider `uv` or `poetry`

---

## 📊 Visual Diagram
```
  You: python3 -m pip install requests
            │
            ▼
   ┌──────────────────┐    1. search      ┌───────────────┐
   │       pip        │ ───────────────►  │  PyPI (cloud) │
   │ (tied to Python) │ ◄───────────────  │ pypi.org      │
   └──────────────────┘    2. wheel files └───────────────┘
            │ 3. resolve dependencies (urllib3, certifi...)
            ▼
   ┌──────────────────────────────────────┐
   │ .../site-packages/requests, urllib3  │  4. installed
   └──────────────────────────────────────┘
            │
            ▼
      import requests   ← now works
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| pip | Python package installer | Python का package installer |
| PyPI | Public package repository | Packages का public भंडार |
| Wheel (.whl) | Pre-built package file | Pre-built package file |
| site-packages | Folder of installed libraries | Installed libraries का folder |
| PATH | List of folders searched for programs | Programs ढूँढने वाले folders की list |
| Dependency | Library another library needs | वह library जिस पर दूसरी निर्भर है |

---

## ⚡ 3-Line Summary
English: Install Python from python.org or a package manager, then verify with `python3 --version`. pip downloads libraries from PyPI into site-packages. Always run `python3 -m pip` inside a virtual environment.
Hindi: Python को python.org या package manager से install करें और `python3 --version` से जाँचें। pip, PyPI से libraries download करके site-packages में रखता है। हमेशा virtual environment में `python3 -m pip` चलाएँ।

---

## ➡️ Next Topic
**008. Virtual Environment** — isolate each project's packages so versions never clash.
