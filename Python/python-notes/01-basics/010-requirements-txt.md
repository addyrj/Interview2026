---

# 010. requirements.txt
# हिंदी में: requirements.txt (dependencies की list)

---

## 🔵 Simple Definition (English)
`requirements.txt` is a plain text file that lists the packages (and usually their versions) a Python project needs, one per line. You create it with `pip freeze` and restore the same environment anywhere with `pip install -r requirements.txt`.

## 🔵 सरल परिभाषा (Hindi)
`requirements.txt` एक साधारण text file है जिसमें project के लिए ज़रूरी packages (और आम तौर पर उनके versions) एक-एक line में लिखे होते हैं। इसे `pip freeze` से बनाते हैं और कहीं भी वही environment `pip install -r requirements.txt` से वापस बना लेते हैं।

---

## 🔴 Problem it Solves
"It works on my machine." Without a dependency list, a teammate or server does not know which libraries and which versions to install. A new FastAPI release may change behavior and break the app silently. requirements.txt records exact versions so every laptop, CI job and production server installs the same thing.

## 🔴 यह क्यों बना? (Hindi)
"मेरी machine पर तो चल रहा है।" Dependency list के बिना teammate या server को पता नहीं होता कि कौन-सी library और कौन-सा version चाहिए। FastAPI का नया release behavior बदलकर app चुपचाप तोड़ सकता है। requirements.txt exact versions दर्ज करता है ताकि हर laptop, CI job और production server पर वही चीज़ install हो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Activate your venv and install what you need:
         python -m pip install fastapi uvicorn
Step 2 → Save exact versions:
         python -m pip freeze > requirements.txt
Step 3 → File looks like:
         fastapi==0.115.0
         uvicorn==0.30.6
         pydantic>=2.5,<3.0      # you can also write ranges by hand
Step 4 → Commit requirements.txt to git (NOT the .venv folder)
Step 5 → Anyone else: create venv, then
         python -m pip install -r requirements.txt
Step 6 → pip reads each line, resolves dependencies and installs
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → venv activate करें और packages install करें
Step 2 → python -m pip freeze > requirements.txt  (exact versions save)
Step 3 → File में fastapi==0.115.0, uvicorn==0.30.6 जैसी lines होती हैं
         (हाथ से ranges जैसे pydantic>=2.5,<3.0 भी लिख सकते हैं)
Step 4 → requirements.txt को git में commit करें (.venv को नहीं)
Step 5 → दूसरा व्यक्ति: venv बनाए, फिर
         python -m pip install -r requirements.txt
Step 6 → pip हर line पढ़कर dependencies resolve करके install करता है
```

---

## 🟡 Real World Example
A Swiggy-style delivery-tracking service has `requirements.txt` with 35 lines. The Dockerfile copies this file first and runs `pip install -r requirements.txt`; Docker caches that layer, so rebuilds are fast unless dependencies change. Teams often keep two files: `requirements.txt` (production) and `requirements-dev.txt` (pytest, black, mypy) that starts with `-r requirements.txt`.

## 🟡 Real Example Hindi mein
Swiggy जैसी delivery-tracking service की `requirements.txt` में 35 lines हैं। Dockerfile पहले यही file copy करके `pip install -r requirements.txt` चलाती है; Docker उस layer को cache करता है, इसलिए dependencies बदले बिना rebuild तेज़ रहता है। Teams अक्सर दो files रखती हैं: `requirements.txt` (production) और `requirements-dev.txt` (pytest, black, mypy), जो `-r requirements.txt` से शुरू होती है।

---

## 💻 Code Example — Basic
```python
# Basic: read a requirements.txt and list the packages
import tempfile  # temporary folder for the demo
from pathlib import Path  # path handling

content: str = """\
# web framework
fastapi==0.115.0
uvicorn==0.30.6

pydantic>=2.5,<3.0
"""  # a typical requirements file (comments and blank lines are allowed)

with tempfile.TemporaryDirectory() as tmp:  # auto-deleted folder
    path: Path = Path(tmp) / "requirements.txt"  # file location
    path.write_text(content)  # save the sample file

    lines: list[str] = path.read_text().splitlines()  # read all lines
    packages: list[str] = [  # keep only real requirement lines
        line.strip()  # remove spaces around the line
        for line in lines  # go through each line
        if line.strip() and not line.strip().startswith("#")  # skip blank + comments
    ]
    print(len(packages))  # Output: 3
    for pkg in packages:  # show each requirement
        print(pkg)  # Output: fastapi==0.115.0 / uvicorn==0.30.6 / pydantic>=2.5,<3.0
```

## 💻 Code Example — Advanced
```python
# Advanced: parse requirements and flag unpinned packages (a real CI check)
from __future__ import annotations  # modern hints on all 3.x

import re  # regular expressions
from dataclasses import dataclass  # small data holder

# name, optional extras like [standard], optional specifier like ==1.0 or >=2,<3
LINE_RE = re.compile(r"^(?P<name>[A-Za-z0-9_.\-]+)(?:\[[^\]]*\])?\s*(?P<spec>.*)$")


@dataclass(frozen=True)  # immutable record of one requirement
class Requirement:
    name: str  # package name
    spec: str  # version specifier text (can be empty)

    @property
    def pinned(self) -> bool:
        """True only for exact pins like ==1.2.3."""
        return self.spec.startswith("==")  # only == gives reproducible installs


def parse(text: str) -> list[Requirement]:
    """Turn requirements text into Requirement objects."""
    result: list[Requirement] = []  # collected items
    for raw in text.splitlines():  # one line at a time
        line = raw.split("#", 1)[0].strip()  # drop inline comments
        if not line or line.startswith("-"):  # skip blanks and options like -r
            continue  # nothing to parse
        match = LINE_RE.match(line)  # try to understand the line
        if match is None:  # unknown syntax
            raise ValueError(f"Cannot parse: {raw!r}")  # fail loudly
        result.append(Requirement(match["name"].lower(), match["spec"].strip()))
    return result  # list of parsed requirements


sample = "fastapi[standard]==0.115.0\nrequests\npydantic>=2.5,<3.0  # range\n-r base.txt\n"
reqs = parse(sample)  # parse the text
for r in reqs:  # report each one
    print(f"{r.name:<9} pinned={r.pinned}")  # show the pin status
# Output:
# fastapi   pinned=True
# requests  pinned=False
# pydantic  pinned=False
loose = [r.name for r in reqs if not r.pinned]  # packages that are not exact
print(loose)  # Output: ['requests', 'pydantic']
```

---

## 🟠 JavaScript vs Python Comparison
`requirements.txt` plays the role of `package.json` + `package-lock.json`, but it is much simpler: just a list of lines. `pip freeze` is like reading `package-lock.json` (exact versions of everything, including sub-dependencies). There is no automatic lockfile in plain pip, so you create it yourself.

```python
# Python: requirements.txt
# fastapi==0.115.0
# uvicorn==0.30.6
# commands:
#   python -m pip install -r requirements.txt   # restore
#   python -m pip freeze > requirements.txt     # save
```
```javascript
// JavaScript: package.json
// { "dependencies": { "express": "^4.19.0" } }
// commands:
//   npm install          // restore from package.json + lockfile
//   npm install express  // adds to package.json automatically
```
Key difference: `npm install x` updates `package.json` automatically; `pip install x` does NOT update requirements.txt. You must refreeze or edit by hand.

---

## 🟠 FastAPI Connection
A FastAPI service lists `fastapi`, `uvicorn` (the ASGI server), `pydantic`, a DB driver and so on. The Dockerfile uses this file for reproducible builds. Pinning matters: FastAPI and Pydantic have had breaking changes between major versions, so `pydantic==2.9.2` prevents surprise breakage.

```python
# requirements.txt for a small FastAPI service (shown as a Python string):
REQUIREMENTS: str = """\
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.9.2
sqlalchemy==2.0.35
"""  # pinned for repeatable builds

# Dockerfile lines that use it (as comments):
#   COPY requirements.txt .
#   RUN pip install --no-cache-dir -r requirements.txt
#   COPY . .
print(REQUIREMENTS.count("==") == 4)  # Output: True (all four are pinned)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Running `pip freeze` outside a venv
```python
# Wrong: pip freeze (global Python) -> 200 unrelated packages in the file
# Right: activate the project venv first, then freeze
#   source .venv/bin/activate
#   python -m pip freeze > requirements.txt
```
✅ Correct: freeze only inside the project's venv.

❌ Mistake 2: Leaving packages unpinned
```python
# Wrong: requirements.txt contains just "fastapi" and "pydantic"
#   -> next month a new major version installs and the app breaks
# Right: pin exact versions for apps
#   fastapi==0.115.0
#   pydantic==2.9.2
```
✅ Correct: pin versions for applications; use ranges for libraries.

❌ Mistake 3: Saving the file in the wrong encoding on Windows
```python
# Wrong: PowerShell `pip freeze > requirements.txt` can write UTF-16,
#        then pip fails with "Invalid requirement" characters.
# Right: python -m pip freeze | Out-File -Encoding utf8 requirements.txt
#        (or use bash / WSL / uv pip compile)
```
✅ Correct: make sure the file is UTF-8.

---

## 🧠 Tricky Interview Question

```python
# You ran: pip install requests
# then:    pip freeze
# Output shows 5 lines, but you installed only ONE package. Why?
```
Answer: `pip freeze` lists every installed package, including transitive dependencies. `requests` depends on `urllib3`, `idna`, `certifi` and `charset-normalizer`, so you get five lines. This is both a strength (fully reproducible) and a weakness (you cannot tell which ones you chose yourself). That is why many teams keep a short hand-written `requirements.in` (top-level packages) and generate the full pinned `requirements.txt` with `pip-compile` or `uv pip compile`.

---

## ⚫ Interview Questions + Answers

Q1: What is requirements.txt and how do you create it?
A1: A text file listing project dependencies, one per line, usually with pinned versions. Create it with `python -m pip freeze > requirements.txt` inside the project's virtual environment. Restore it with `python -m pip install -r requirements.txt`.

Q2: What do `==`, `>=`, `~=` and `!=` mean in version specifiers?
A2: `==1.4.2` is an exact version. `>=1.4` means 1.4 or higher. `~=1.4.2` is a compatible release: `>=1.4.2, ==1.4.*`. `!=1.4.3` excludes a bad version. You can combine them with commas: `pydantic>=2.5,<3.0`.

Q3: What is the difference between `requirements.txt` and `pyproject.toml`?
A3: requirements.txt is a plain list of packages for installation (an app's lock-style list). pyproject.toml is the modern project config file: it holds metadata, dependencies, tool settings (black, ruff, pytest) and build info. Libraries should declare dependencies in pyproject.toml; many apps keep both.

Q4: How do you manage dev vs production dependencies?
A4: Use separate files: `requirements.txt` (runtime only) and `requirements-dev.txt` with `-r requirements.txt` on its first line plus pytest, mypy, ruff. Production images install only the first file, keeping them smaller and more secure.

Q5: How do you make installs reproducible and secure?
A5: Pin exact versions, ideally with hashes (`pip-compile --generate-hashes`, then `pip install --require-hashes -r requirements.txt`). Regularly scan with `pip-audit` for known vulnerabilities and update deliberately using a bot like Dependabot or Renovate.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Deploying apps and Docker images that need repeatable installs
- Sharing a project with a team or CI pipeline
- Quick scripts and small services

❌ Avoid when:
- Publishing a library to PyPI (use pyproject.toml)
- You need automatic lockfiles and dependency groups (use uv or poetry)
- Never include secrets or private tokens inside the file

---

## 📊 Visual Diagram
```
   Developer laptop                         Server / CI / Docker
   ┌───────────────────┐                    ┌─────────────────────┐
   │ .venv             │                    │ fresh venv          │
   │  fastapi 0.115.0  │                    │  (empty)            │
   │  uvicorn 0.30.6   │                    └──────────▲──────────┘
   └─────────┬─────────┘                               │
             │ pip freeze                    pip install -r
             ▼                                         │
   ┌───────────────────┐   git push / copy   ┌─────────┴─────────┐
   │ requirements.txt  │ ──────────────────► │ requirements.txt  │
   └───────────────────┘                     └───────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `pip freeze` | Lists installed packages with versions | Installed packages और versions की list |
| Pinning | Fixing an exact version (`==`) | Exact version तय करना |
| Specifier | Version rule like `>=2.0,<3.0` | Version का नियम |
| Transitive dependency | Dependency of a dependency | Dependency की dependency |
| Lock file | File with exact resolved versions | Exact resolved versions वाली file |
| `-r` | Include another requirements file | दूसरी requirements file शामिल करना |

---

## ⚡ 3-Line Summary
English: requirements.txt lists the packages a project needs so any machine can recreate the same environment. Create it with `pip freeze` inside the venv and install with `pip install -r`. Pin exact versions for applications to avoid surprise breakage.
Hindi: requirements.txt में project के packages की list होती है ताकि कोई भी machine वही environment बना सके। venv के अंदर `pip freeze` से बनाएँ और `pip install -r` से install करें। Applications में exact versions pin करें ताकि अचानक कुछ न टूटे।

---

## ➡️ Next Topic
**011. pyproject.toml (modern)** — the modern single config file for dependencies, metadata and tool settings.
