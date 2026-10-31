---

# 006. Python Versions (2 vs 3)
# हिंदी में: Python Versions (2 बनाम 3)

---

## 🔵 Simple Definition (English)
Python 2 is the old, retired version of the language (end of life: 1 January 2020). Python 3 is the current version and the only one you should use. Python 3 fixed many design mistakes of Python 2, but the two are NOT fully compatible, so old Python 2 code often breaks on Python 3.

## 🔵 सरल परिभाषा (Hindi)
Python 2 भाषा का पुराना और बंद हो चुका version है (support 1 जनवरी 2020 को खत्म)। Python 3 आज का version है और सिर्फ यही use करना चाहिए। Python 3 ने Python 2 की कई design गलतियाँ ठीक कीं, लेकिन दोनों पूरी तरह compatible नहीं हैं, इसलिए पुराना Python 2 code अक्सर Python 3 पर टूट जाता है।

---

## 🔴 Problem it Solves
Python 2 had deep problems: `print` was a statement, strings were bytes by default (Unicode was painful), `7 / 2` gave `3` (silent integer division), and `range()` built a full list in memory. Fixing these needed breaking changes. So Python 3 (released 2008) was created as a clean break. Result: text handling is Unicode-first, division is predictable, and modern features (type hints, async/await, f-strings) became possible.

## 🔴 यह क्यों बना? (Hindi)
Python 2 में दिक्कतें थीं: `print` statement था, strings default में bytes थीं (Unicode मुश्किल), `7 / 2` का जवाब `3` आता था (चुपचाप integer division), और `range()` पूरी list memory में बनाता था। इन्हें ठीक करने के लिए पुराने code को तोड़ना ज़रूरी था। इसलिए 2008 में Python 3 एक clean break के तौर पर आया। नतीजा: Unicode-first text, predictable division, और type hints, async/await, f-strings जैसे modern features।

---

## 🟢 How it Works — Step by Step

```
Step 1 → 2008: Python 3.0 released (not backward compatible with 2.x)
Step 2 → 2008-2020: Both lived together; libraries supported "2 and 3" using the `six` library
Step 3 → 2010-2019: Python 2.7 kept alive as the "last" 2.x release
Step 4 → 1 Jan 2020: Python 2 reached End Of Life (no security fixes at all)
Step 5 → Today: Python 3.x gets a new minor version every year (3.12, 3.13, 3.14 ...)
Step 6 → Each minor version is supported for about 5 years, then it is retired too

Version number meaning:  3 . 13 . 3
                         │   │   └── micro (bug fixes only)
                         │   └────── minor (new features, yearly)
                         └────────── major (3 is the only one alive)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → 2008: Python 3.0 आया (2.x के साथ backward compatible नहीं)
Step 2 → 2008-2020: दोनों साथ चले; libraries `six` से दोनों support करती थीं
Step 3 → Python 2.7 आखिरी 2.x release रहा
Step 4 → 1 जनवरी 2020: Python 2 End Of Life (कोई security fix नहीं)
Step 5 → आज: हर साल नया minor version (3.12, 3.13, 3.14 ...)
Step 6 → हर minor version करीब 5 साल support होता है, फिर वो भी retire

Version number: 3 . 13 . 3  →  major . minor . micro
```

---

## 🟡 Real World Example
Dropbox and Instagram ran huge Python 2 codebases and spent years migrating to Python 3 (Instagram moved in 2017 and reported performance gains). Today every modern tool, such as FastAPI, Django 4+, NumPy, PyTorch and the OpenAI SDK, supports only Python 3. If a Swiggy-style backend team hires you, the production service will be on Python 3.10 to 3.13, and a Dockerfile will start with `FROM python:3.12-slim`.

## 🟡 Real Example Hindi mein
Dropbox और Instagram के पास बहुत बड़े Python 2 codebase थे और उन्होंने सालों लगाकर Python 3 में migrate किया (Instagram ने 2017 में किया और performance बेहतर बताई)। आज FastAPI, Django 4+, NumPy, PyTorch, OpenAI SDK सब सिर्फ Python 3 support करते हैं। किसी Swiggy जैसी backend team में production service Python 3.10 से 3.13 पर होगी और Dockerfile `FROM python:3.12-slim` से शुरू होगी।

---

## 💻 Code Example — Basic
```python
# Basic: what changed between Python 2 and Python 3
import sys  # sys module gives information about the running interpreter

# 1. Which Python am I running? (version_info is a named tuple)
major: int = sys.version_info.major  # major version number, always 3 today
minor: int = sys.version_info.minor  # minor version number, e.g. 13
print(f"Running Python {major}.{minor}")  # Output: Running Python 3.13 (on 3.13)

# 2. print is a FUNCTION in Python 3 (it was a statement in Python 2)
print("hello")  # Python 2 allowed: print "hello" (no brackets) -> SyntaxError in 3

# 3. Division: / is always true division, // is floor division
print(7 / 2)  # Output: 3.5   (Python 2 gave 3 here!)
print(7 // 2)  # Output: 3    (explicit floor division, same in both)

# 4. Strings are Unicode by default; bytes are a separate type
text: str = "नमस्ते"  # a normal str holds Unicode characters directly
data: bytes = text.encode("utf-8")  # convert str -> bytes explicitly
print(len(text), len(data))  # Output: 6 18  (6 characters, 18 bytes)

# 5. range() is lazy in Python 3 (does not build a full list)
r = range(1_000_000)  # no million-item list is created in memory
print(type(r).__name__)  # Output: range
print(r[999_999])  # Output: 999999  (computed on demand)

# 6. dict keeps insertion order (guaranteed since Python 3.7)
d: dict[str, int] = {"b": 1, "a": 2, "c": 3}  # keys inserted in this order
print(list(d))  # Output: ['b', 'a', 'c']
```

## 💻 Code Example — Advanced
```python
# Advanced: production guard that fails fast on unsupported Python versions
from __future__ import annotations  # lets us use modern type hints on older 3.x

import sys  # to read the interpreter version
from typing import Final  # Final marks a constant for type checkers

MIN_VERSION: Final[tuple[int, int]] = (3, 9)  # lowest version our service supports


class UnsupportedPythonError(RuntimeError):
    """Raised when the interpreter is too old for this application."""


def check_python(minimum: tuple[int, int] = MIN_VERSION) -> str:
    """Return a status message or raise if Python is too old."""
    current: tuple[int, int] = sys.version_info[:2]  # slice to (major, minor)
    if current < minimum:  # tuples compare element by element
        needed = ".".join(map(str, minimum))  # (3, 9) -> "3.9"
        raise UnsupportedPythonError(f"Python {needed}+ required, got {current}")
    return f"OK: running Python {current[0]}.{current[1]}"  # success message


def describe(value: int | str) -> str:
    """Use structural pattern matching (needs Python 3.10+)."""
    match value:  # match/case does not exist in Python 2 or old 3.x
        case int():  # matches any int
            return "number"
        case str():  # matches any str
            return "text"


print(check_python())  # Output: OK: running Python 3.13 (on 3.13)
print(describe(5), describe("hi"))  # Output: number text

try:
    check_python((99, 0))  # pretend we need Python 99
except UnsupportedPythonError as exc:  # catch our own error type
    print(f"Blocked: {exc}")  # Output: Blocked: Python 99.0+ required, got (3, 13)
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript also had a "version problem" (ES5 vs ES6+), but browsers and Node kept old syntax working, so old code still runs. Python 3 chose a clean break instead. In JS you check `node --version`; in Python you check `python --version`.

```python
# Python: Python 3 style, modern and explicit
print(7 / 2)            # 3.5 (true division always)
print(7 // 2)           # 3   (floor division, separate operator)
name = "Aman"
print(f"Hi {name}")      # f-string (3.6+)
```
```javascript
// JavaScript: ES6+ style
console.log(7 / 2);          // 3.5 (JS has only one number type)
console.log(Math.floor(7/2)); // 3  (no // operator in JS)
const name = "Aman";
console.log(`Hi ${name}`);    // template literal
```
Key difference: JS never broke old code (`var` still works). Python broke old code once (2 to 3) and now removes features slowly through deprecation warnings.

---

## 🟠 FastAPI Connection
FastAPI is built on type hints, `async`/`await` and `typing` features that exist only in Python 3. New FastAPI releases keep raising the minimum Python version, so the Python version of your project decides which FastAPI and Pydantic versions you can install. Always pin the version in your Dockerfile and in `pyproject.toml` (`requires-python`).

```python
# FastAPI: a health endpoint that reports the Python version in use
import sys  # to read the interpreter version

from fastapi import FastAPI  # the web framework (pip install fastapi)

app: FastAPI = FastAPI()  # create the application object


@app.get("/health")  # GET /health
async def health() -> dict[str, str]:  # async def + type hints = Python 3 only
    return {"python": f"{sys.version_info.major}.{sys.version_info.minor}"}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using Python 2 `print` syntax or `raw_input`
```python
# Wrong (Python 2 only):
# print "hello"            -> SyntaxError in Python 3
# name = raw_input("Name") -> NameError in Python 3

# Right (Python 3):
print("hello")             # print is a function
name: str = input("Name: ")  # input() replaced raw_input()
```
✅ Correct: use `print()` and `input()`.

❌ Mistake 2: Expecting integer division from `/`
```python
# Wrong assumption (Python 2 habit):
average = 7 / 2        # you expect 3, but Python 3 gives 3.5
# Right: use // when you really want an integer result
average_int: int = 7 // 2   # 3
```
✅ Correct: `/` is always float, `//` is floor division.

❌ Mistake 3: Typing `python` and assuming it is Python 3
```python
# On some old Linux/Mac systems `python` may still point to Python 2.
# Right: be explicit and check
#   python3 --version
#   python3 -m venv .venv
```
✅ Correct: use `python3` or a virtual environment, and verify the version.

---

## 🧠 Tricky Interview Question

```python
# What will this output?
print(type(3 / 1))
print(3 // 2.0)
print("5" + str(5))
print(0.1 + 0.2 == 0.3)
```
Answer:
```
<class 'float'>
1.0
55
False
```
`3 / 1` is true division so the result is `float` (3.0) even though both sides are int. `3 // 2.0` is floor division with a float, so the result is `1.0` (still a float). `"5" + str(5)` joins two strings into `"55"`. `0.1 + 0.2` is `0.30000000000000004` due to binary floating point, so the comparison is `False`.

---

## ⚫ Interview Questions + Answers

Q1: What is the main difference between Python 2 and Python 3?
A1: Python 3 is not backward compatible. Key changes: `print` is a function, `/` is true division, strings are Unicode by default (bytes is a separate type), `range` is lazy, `input()` replaced `raw_input()`, and new features like f-strings, type hints, `async/await` exist only in 3. Python 2 reached end of life on 1 January 2020.

Q2: Why did Python 3 break backward compatibility?
A2: The old design had flaws that could not be fixed without changing behavior, mainly text vs bytes confusion and integer division. The core team accepted a one-time break so the language could be cleaner for the next decades. The migration took over 10 years, and tools like `2to3`, `six` and `futurize` helped.

Q3: Which Python version should I use for a new project today?
A3: Use a currently supported Python 3 version, usually the latest stable or one version behind (for example 3.12 or 3.13), because all libraries support it. Avoid versions near end of life. Check the support table on python.org and pin the version in the Dockerfile.

Q4: What does `3.13.3` mean?
A4: Major 3, minor 13, micro 3. A minor version adds features and can deprecate or remove old ones. A micro version only has bug and security fixes. Code that works on 3.13.1 will work on 3.13.3, but code written for 3.13 may not run on 3.9 (for example `match` needs 3.10+).

Q5: How do you write code that works on multiple Python 3 versions?
A5: Set `requires-python` in `pyproject.toml`, test on several versions with `tox` or a CI matrix, use `from __future__ import annotations` for newer type hint syntax, and check `sys.version_info` only when a feature truly differs. Avoid features newer than your minimum version.

---

## 🔷 When to Use + When Not to Use
✅ Use Python 3 (latest supported) when:
- Starting any new project, API, script or ML work
- You need async, type hints, f-strings, dataclasses, `match`
- You want security patches and library support

❌ Avoid when:
- Never use Python 2 for anything new
- Avoid an end-of-life Python 3 (like 3.7 or 3.8) in production
- Avoid the very newest release on day one if a key library does not support it yet

---

## 📊 Visual Diagram
```
 2000      2008          2020                    2026
  │         │             │                       │
  ▼         ▼             ▼                       ▼
 Py 2.0 ── Py 3.0 ──── Py 2 EOL ─────────────── Py 3.13 / 3.14
            │             ✗ no fixes               ✓ active
            └── clean break (not backward compatible)

 print "x"   ──►  print("x")
 7 / 2 = 3   ──►  7 / 2 = 3.5,  7 // 2 = 3
 str = bytes ──►  str (Unicode) + bytes (separate)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| EOL (End of Life) | Version gets no more fixes | Version को कोई fix नहीं मिलता |
| Backward compatible | Old code still runs | पुराना code चलता रहे |
| Minor version | Yearly release with new features | साल में एक बार नए features वाला release |
| `sys.version_info` | Tuple with version numbers | Version numbers वाला tuple |
| Unicode | Standard for all world scripts | सभी भाषाओं के characters का standard |
| 2to3 | Tool to convert Py2 code to Py3 | Py2 code को Py3 में बदलने वाला tool |

---

## ⚡ 3-Line Summary
English: Python 2 is dead (end of life in 2020); Python 3 is the only choice. Python 3 changed print, division, strings and added modern features like f-strings, type hints and async. Always pin a supported Python 3 version for your project and Docker image.
Hindi: Python 2 खत्म हो चुका है (2020 में EOL), सिर्फ Python 3 use करें। Python 3 में print, division, strings बदले और f-strings, type hints, async जैसे नए features आए। अपने project और Docker image में supported Python 3 version pin करें।

---

## ➡️ Next Topic
**007. Installing Python + pip** — how to install Python on Mac/Windows/Linux, check it works, and use pip to install packages.
