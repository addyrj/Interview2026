---

# 009. pip vs pip3 vs conda
# हिंदी में: pip बनाम pip3 बनाम conda

---

## 🔵 Simple Definition (English)
`pip` and `pip3` are both Python package installers; `pip3` is just the name that is guaranteed to belong to Python 3 (on systems that also had Python 2). `conda` is a different tool: a package AND environment manager that can install Python itself plus non-Python software (CUDA, C libraries), popular in data science.

## 🔵 सरल परिभाषा (Hindi)
`pip` और `pip3` दोनों Python के package installer हैं; `pip3` वह नाम है जो पक्का Python 3 का होता है (उन systems पर जहाँ Python 2 भी था)। `conda` अलग tool है: package और environment manager, जो Python खुद और non-Python software (CUDA, C libraries) भी install कर सकता है। Data science में लोकप्रिय है।

---

## 🔴 Problem it Solves
When Python 2 and 3 lived together, `pip` could mean either. `pip3` removed the confusion. Later, data scientists faced another problem: libraries like NumPy, TensorFlow and PyTorch need compiled C/CUDA code that pip could not always install cleanly. conda solved this by shipping pre-built binaries for all dependencies, and by creating complete environments including the Python version.

## 🔴 यह क्यों बना? (Hindi)
जब Python 2 और 3 साथ थे, `pip` का मतलब कोई भी हो सकता था। `pip3` ने confusion हटाया। बाद में data scientists को दूसरी दिक्कत आई: NumPy, TensorFlow, PyTorch जैसी libraries को compiled C/CUDA code चाहिए जो pip हमेशा ठीक से install नहीं कर पाता था। conda ने सभी dependencies के pre-built binaries देकर और Python version समेत पूरा environment बनाकर यह हल किया।

---

## 🟢 How it Works — Step by Step

```
pip   → installs Python packages from PyPI into the CURRENT Python
pip3  → same program, but tied to Python 3 (older systems with both 2 and 3)
python3 -m pip → same as pip, but 100% tied to the python3 you typed

conda → Step 1: reads environment.yml or your command
        Step 2: solves ALL dependencies (Python + C libs + packages) together
        Step 3: downloads binaries from Anaconda channels (defaults, conda-forge)
        Step 4: installs into ~/miniconda3/envs/<name>/  (own Python inside)
        Step 5: `conda activate <name>` switches environments

Decision:
  Web/API project (FastAPI)            → venv + pip (or uv)
  Data science / GPU / heavy C deps    → conda (or pip wheels if available)
```

## 🟢 कैसे काम करता है? (Hindi)
```
pip   → PyPI से Python packages मौजूदा Python में install करता है
pip3  → वही program, लेकिन Python 3 से जुड़ा हुआ
python3 -m pip → pip जैसा ही, पर 100% उसी python3 से जुड़ा जो आपने लिखा

conda → Step 1: command या environment.yml पढ़ता है
        Step 2: Python + C libs + packages सबको साथ solve करता है
        Step 3: Anaconda channels (defaults, conda-forge) से binaries लाता है
        Step 4: ~/miniconda3/envs/<name>/ में install (अपना Python साथ)
        Step 5: `conda activate <name>` से environment बदलता है

फैसला: FastAPI/web → venv + pip | Data science / GPU → conda
```

---

## 🟡 Real World Example
A machine learning team at a fintech company trains models with PyTorch and CUDA on GPU servers. They use conda environments (`environment.yml`) so the CUDA toolkit and Python version are identical on every machine. The same company's FastAPI inference service, however, is built with a slim Docker image using `python:3.12-slim` and plain `pip install -r requirements.txt`. Training uses conda, serving uses pip.

## 🟡 Real Example Hindi mein
एक fintech company की ML team GPU servers पर PyTorch और CUDA से models train करती है। वे conda environments (`environment.yml`) use करते हैं ताकि हर machine पर CUDA toolkit और Python version एक जैसा रहे। उसी company की FastAPI inference service slim Docker image `python:3.12-slim` और साधारण `pip install -r requirements.txt` से बनती है। Training में conda, serving में pip।

---

## 💻 Code Example — Basic
```python
# Basic: find which pip belongs to which Python, and build safe commands
import shutil  # shutil.which finds programs on PATH
import sys  # sys.executable is the current interpreter

# 1. The SAFE command is always tied to the interpreter that runs this code
safe_cmd: list[str] = [sys.executable, "-m", "pip", "--version"]  # python -m pip
print(safe_cmd[1:])  # Output: ['-m', 'pip', '--version']

# 2. Is each tool present on PATH? (results depend on your machine)
for tool in ("pip", "pip3", "conda"):  # check three tools
    path = shutil.which(tool)  # returns a path string or None
    print(tool, "found" if path else "missing")  # e.g. pip found / conda missing

# 3. Quick comparison table stored as data
comparison: dict[str, str] = {
    "pip": "Python packages from PyPI",  # what pip installs
    "pip3": "same as pip, bound to Python 3",  # alias meaning
    "conda": "Python + non-Python packages + environments",  # conda scope
}
for name, meaning in comparison.items():  # loop over key/value pairs
    print(f"{name:<6} -> {meaning}")  # pad name to width 6
# Output:
# pip    -> Python packages from PyPI
# pip3   -> same as pip, bound to Python 3
# conda  -> Python + non-Python packages + environments
```

## 💻 Code Example — Advanced
```python
# Advanced: detect which environment manager is active
from __future__ import annotations  # modern hints on all 3.x

import os  # read environment variables
import sys  # prefix paths
from dataclasses import dataclass  # tidy result type


@dataclass(frozen=True)  # immutable report
class EnvReport:
    manager: str  # "conda", "venv" or "system"
    name: str | None  # environment name if known
    prefix: str  # path where packages are installed


def detect_environment() -> EnvReport:
    """Figure out whether we run under conda, a venv, or the system Python."""
    conda_prefix: str | None = os.environ.get("CONDA_PREFIX")  # set by `conda activate`
    if conda_prefix:  # conda wins if its variable exists
        return EnvReport("conda", os.environ.get("CONDA_DEFAULT_ENV"), conda_prefix)
    if sys.prefix != sys.base_prefix:  # venv check from topic 008
        return EnvReport("venv", os.path.basename(sys.prefix), sys.prefix)
    return EnvReport("system", None, sys.prefix)  # plain global Python


def install_hint(report: EnvReport) -> str:
    """Return the right install command for the detected environment."""
    if report.manager == "conda":  # conda users prefer conda for binaries
        return "conda install numpy   (or pip for PyPI-only packages)"
    if report.manager == "venv":  # normal project workflow
        return "python -m pip install numpy"
    return "create a venv first: python -m venv .venv"  # avoid global installs


report: EnvReport = detect_environment()  # inspect current environment
print(report.manager in {"conda", "venv", "system"})  # Output: True
print(install_hint(EnvReport("venv", ".venv", "/x/.venv")))  # Output: python -m pip install numpy
print(install_hint(EnvReport("system", None, "/usr")))  # Output: create a venv first: python -m venv .venv
```

---

## 🟠 JavaScript vs Python Comparison
In JS you have `npm`, `yarn`, `pnpm` (different clients for the same npm registry). In Python, `pip` is like `npm`, and `conda` is closer to a "system-level" manager like `nvm` plus Homebrew combined, because it installs the runtime and native libraries as well. `pip3` is like calling `npm` when you have two Node versions and need to be specific.

```python
# Python
# python3 -m pip install numpy        # like npm install (PyPI registry)
# conda create -n ml python=3.11      # like nvm install + new isolated project
# conda install pytorch               # installs binaries incl. native libs
```
```javascript
// JavaScript
// npm install lodash                 // npm registry
// nvm install 20 && nvm use 20       // choose the Node runtime version
// pnpm add lodash                    // alternative client, same registry
```

---

## 🟠 FastAPI Connection
FastAPI projects normally use `venv + pip` (or `uv`/`poetry`) because FastAPI and its dependencies are pure Python or ship ready-made wheels. You can still use conda locally if your project also loads a heavy ML model (PyTorch), but the production Docker image typically uses pip, since the image is smaller and builds faster.

```python
# FastAPI app that serves an ML result; the environment is created however you like
# pip way:   python3 -m pip install "fastapi[standard]" scikit-learn
# conda way: conda install -c conda-forge fastapi scikit-learn
from fastapi import FastAPI  # same import regardless of installer

app: FastAPI = FastAPI(title="Prediction API")  # app object


@app.get("/predict")  # GET /predict?x=3
def predict(x: float) -> dict[str, float]:  # query param validated as float
    return {"result": x * 2.0}  # placeholder "model"
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mixing pip and conda carelessly in one environment
```python
# Wrong: conda install numpy  ->  pip install numpy  ->  conda update numpy
#        (two managers overwrite each other's files, env gets corrupted)
# Right: install as much as possible with conda first, THEN use pip for the
#        remaining PyPI-only packages, and avoid going back to conda afterwards.
```
✅ Correct: conda first, pip last; or use only one manager per environment.

❌ Mistake 2: Using `pip` and `python` from different installs
```python
# Wrong: pip install pandas ; python script.py -> ModuleNotFoundError
# Right: python3 -m pip install pandas ; python3 script.py
```
✅ Correct: `python3 -m pip` removes any doubt which Python receives the package.

❌ Mistake 3: Using conda for a simple API and shipping a huge image
```python
# Wrong: FROM continuumio/miniconda3 (hundreds of MB) just for FastAPI
# Right: FROM python:3.12-slim and pip install -r requirements.txt
```
✅ Correct: pick the lightest tool that solves the problem.

---

## 🧠 Tricky Interview Question

```python
# Two environments exist: system Python 3.9 and conda env "ml" (Python 3.11).
# You activate "ml" then run:  pip install requests
# Where does requests go, and why might `python3 -c "import requests"` still fail?
```
Answer: Inside an activated conda env, `pip` normally points to the env's own pip, so requests goes into `ml`. `import requests` fails only if `python3` on PATH resolves to a different interpreter (for example a hard-coded `/usr/bin/python3` in a script's shebang or an IDE configured with the system interpreter). Diagnose with `which python3`, `python3 -m pip --version` and `python3 -c "import sys; print(sys.executable)"`. The rule: whenever packages "disappear", compare `sys.executable` with the pip that installed them.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between pip and pip3?
A1: Functionally the same installer. `pip3` is guaranteed to belong to Python 3, which mattered when systems had both Python 2 and 3. Today on most systems both exist and point to Python 3, but the safest form is `python3 -m pip`.

Q2: pip vs conda: when do you choose conda?
A2: Choose conda when you need non-Python binaries (CUDA, MKL, GDAL), a specific Python version without installing it separately, or reproducible scientific environments. Choose pip with venv for web backends, APIs and small Docker images. conda uses its own channels (defaults, conda-forge), while pip uses PyPI.

Q3: What is the difference between conda, miniconda and anaconda?
A3: conda is the tool. Anaconda is a large distribution that bundles conda plus 250+ pre-installed data science packages (GBs in size). Miniconda is a minimal installer with just conda and Python; you add what you need. Miniforge is similar but defaults to the conda-forge channel.

Q4: Can pip and conda be used together?
A4: Yes, carefully. Install conda packages first, then pip packages that conda does not have. Do not run conda installs after pip in the same environment, because conda cannot track pip's changes and may break dependencies. Export with `conda env export` and keep a `pip:` section in `environment.yml`.

Q5: What are `uv` and `poetry` and how do they compare?
A5: Both are modern project managers that use `pyproject.toml` and lock files, and they create virtual environments for you. `uv` (written in Rust) is much faster than pip. `poetry` adds packaging and publishing. They are pip-style (PyPI) tools, not conda replacements for native libraries.

---

## 🔷 When to Use + When Not to Use
✅ Use pip (in a venv) when:
- Building APIs, web apps, scripts, Docker images
- All dependencies are on PyPI with wheels

✅ Use conda when:
- Data science, GPU, scientific stacks with native libraries
- You need a specific Python version quickly per environment

❌ Avoid when:
- conda for small microservice images (too heavy)
- Mixing pip and conda repeatedly in the same environment
- Bare `pip` when several Pythons are installed (use `python3 -m pip`)

---

## 📊 Visual Diagram
```
                 ┌───────────────────────────┐
                 │   What are you building?  │
                 └─────────────┬─────────────┘
              ┌────────────────┴────────────────┐
              ▼                                  ▼
     Web API / script / Docker          ML / GPU / heavy native libs
              │                                  │
              ▼                                  ▼
     venv + python3 -m pip  (or uv)       conda / mamba (conda-forge)
              │                                  │
        PyPI wheels                    Anaconda channels (binaries)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| pip | PyPI package installer | PyPI का package installer |
| pip3 | pip bound to Python 3 | Python 3 वाला pip |
| conda | Package + environment manager | Package और environment manager |
| Miniconda | Minimal conda installer | छोटा conda installer |
| conda-forge | Community conda channel | Community का conda channel |
| `environment.yml` | conda environment definition file | conda environment की definition file |

---

## ⚡ 3-Line Summary
English: pip and pip3 install Python packages from PyPI; use `python3 -m pip` to be safe. conda manages environments plus non-Python binaries and shines in data science and GPU work. For FastAPI and web services, use venv with pip (or uv).
Hindi: pip और pip3 PyPI से Python packages install करते हैं; सुरक्षित तरीका `python3 -m pip` है। conda environments और non-Python binaries संभालता है, data science और GPU में बढ़िया है। FastAPI और web services में venv के साथ pip (या uv) use करें।

---

## ➡️ Next Topic
**010. requirements.txt** — save and restore exact package versions so everyone gets the same environment.
