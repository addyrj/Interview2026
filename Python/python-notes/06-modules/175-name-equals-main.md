---

# 175. `__name__ == "__main__"`
# हिंदी में: `__name__ == "__main__"` (file सीधे चली या import हुई?)

---

## 🔵 Simple Definition (English)
Every Python file has a built-in variable `__name__`. If you run the file directly (`python file.py`), `__name__` is `"__main__"`. If another file imports it, `__name__` is the module's own name (like `"utils"`). The `if __name__ == "__main__":` check lets code run only in the first case.

## 🔵 सरल परिभाषा (Hindi)
हर Python file में `__name__` नाम का built-in variable होता है। File को सीधे चलाएँ (`python file.py`) तो `__name__` = `"__main__"` होता है। कोई दूसरी file उसे import करे तो `__name__` module का अपना नाम (जैसे `"utils"`) होता है। `if __name__ == "__main__":` से code सिर्फ पहली स्थिति में चलता है।

---

## 🔴 Problem it Solves
A file with useful functions often also has demo or startup code. Without the guard, importing it would run that code as a side effect (start a server, print, hit a database). The guard separates "library part" from "script part".

## 🔴 यह क्यों बना? (Hindi)
काम की functions वाली file में अक्सर demo या startup code भी होता है। Guard के बिना import करते ही वह code चल जाता (server शुरू, print, database call)। Guard "library वाला हिस्सा" और "script वाला हिस्सा" अलग करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → `python app.py`   : Python runs app.py as the top-level script
Step 2 → It sets app.__name__ = "__main__" before running the code
Step 3 → `import app` from elsewhere: __name__ = "app" instead
Step 4 → `if __name__ == "__main__":` is True only in Step 1
Step 5 → `python -m pkg.app` also gives "__main__" (and keeps package imports working)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `python app.py` से app.py सबसे ऊपर की script के रूप में चलती है
Step 2 → code चलने से पहले __name__ = "__main__" सेट होता है
Step 3 → कहीं और से `import app` करें तो __name__ = "app" होता है
Step 4 → `if __name__ == "__main__":` सिर्फ Step 1 में True होता है
Step 5 → `python -m pkg.app` भी "__main__" देता है (और package imports सही चलते हैं)
```

---

## 🟡 Real World Example
A Zomato data team has `clean.py` with `clean_orders()`. Other jobs import it. Running `python clean.py` triggers a quick self-test under the guard. A FastAPI `main.py` starts `uvicorn.run(...)` under the guard so `import main` in tests does not start a server.

## 🟡 Real Example Hindi mein
Zomato की data team की `clean.py` में `clean_orders()` है जिसे दूसरे jobs import करते हैं। `python clean.py` चलाने पर guard के अंदर self-test चलता है। FastAPI की `main.py` में `uvicorn.run(...)` guard में होता है ताकि tests में `import main` से server शुरू न हो।

---

## 💻 Code Example — Basic
```python
# Basic __name__ example - save as greet.py and run: python greet.py
def greet(name: str) -> str:  # reusable function (the "library" part)
    return f"Hello, {name}!"  # build the greeting


print("module name is:", __name__)  # runs on import AND on direct run
# Output (direct run):  module name is: __main__
# Output (when imported): module name is: greet

if __name__ == "__main__":  # True only when run directly
    print(greet("Asha"))  # script part: runs only for `python greet.py`
    # Output: Hello, Asha!
```

## 💻 Code Example — Advanced
```python
# Production CLI pattern: main() returns an exit code, guard calls sys.exit
import argparse  # command line parsing
import sys  # for exit codes and stderr
from typing import Optional, Sequence  # type hints


def total(prices: Sequence[float], tax: float = 0.18) -> float:
    """Pure function: easy to import and unit-test."""
    if tax < 0:  # validate input
        raise ValueError("tax cannot be negative")  # clear error
    return round(sum(prices) * (1 + tax), 2)  # sum then add tax


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Entry point. Takes argv so tests can call main(['1','2'])."""
    parser = argparse.ArgumentParser(description="Bill total")  # build parser
    parser.add_argument("prices", nargs="+", type=float)  # one or more numbers
    parser.add_argument("--tax", type=float, default=0.18)  # optional tax
    args = parser.parse_args(argv)  # parse (None -> sys.argv[1:])
    try:  # business call
        print(total(args.prices, args.tax))  # print the result
    except ValueError as exc:  # report bad input politely
        print(f"error: {exc}", file=sys.stderr)  # error goes to stderr
        return 2  # non-zero = failure for shells / CI
    return 0  # success


if __name__ == "__main__":  # only when run as a script
    sys.exit(main())  # exit code goes back to the shell

# Test it in-process without a shell:
#   print(main(["100", "50"]))
# Output: 177.0   then   0
#   print(main(["100", "--tax=-1"]))
# Output on stderr: error: tax cannot be negative   then   2
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
def main() -> None:
    print("running as script")

if __name__ == "__main__":      # script only, not on import
    main()
```

```javascript
// JavaScript (Node, CommonJS)
function main() { console.log("running as script"); }
if (require.main === module) { main(); }   // same idea

// Node ES modules (no require.main):
// if (import.meta.url === `file://${process.argv[1]}`) main();
// The browser has no equivalent: code runs on load.
```

Key difference: Python sets one built-in variable; Node compares `require.main` with `module`.

---

## 🟠 FastAPI Connection
Put `uvicorn.run` under the guard so that tests, `uvicorn main:app`, and Gunicorn can all import `app` without side effects. Pass the app as an import string when you want `reload=True`.

```python
# main.py (needs: pip install fastapi uvicorn)
from fastapi import FastAPI  # web framework

app: FastAPI = FastAPI()  # created at import time, side-effect free


@app.get("/health")  # simple route
def health() -> dict[str, str]:
    return {"status": "ok"}  # JSON response


if __name__ == "__main__":  # only for `python main.py`
    import uvicorn  # imported lazily, only for local dev
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)  # start server
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Heavy code at top level without a guard
```python
# Wrong - importing this file starts the server/downloads data:
# uvicorn.run(app)

# Correct:
# if __name__ == "__main__":
#     uvicorn.run(app)
```

❌ Mistake 2: Running a package file as a script and breaking relative imports
```python
# Wrong: python shop/payments/gateway.py
#   ImportError: attempted relative import with no known parent package

# Correct: run as a module from the project root
#   python -m shop.payments.gateway
```

❌ Mistake 3: Putting all logic inside the guard
```python
# Wrong - cannot be imported or tested:
# if __name__ == "__main__":
#     ...100 lines of logic...

# Correct - define main() and call it:
# def main() -> int: ...
# if __name__ == "__main__":
#     raise SystemExit(main())
```

---

## 🧠 Tricky Interview Question

**Q**: `a.py` contains the two lines below. What does `python a.py` print, and what does `import a` (from another file) print?

```python
print("a loaded, name =", __name__)
if __name__ == "__main__":
    import a
    print("done")
```

**Answer**:
```
a loaded, name = __main__
a loaded, name = a
done
```
Running `python a.py` executes the file as `__main__`. Inside, `import a` is a NEW import (the main script is stored as `__main__`, not `a`), so the file runs a second time with `__name__ == "a"`. That is why the same file can be loaded twice, under two names. During `import a` from outside, only `a loaded, name = a` prints.

---

## ⚫ Interview Questions + Answers

Q1: What is `__name__` when a module is imported?
A1: The module's dotted path, e.g. `"utils"` or `"shop.utils.money"`.

Q2: Why use `sys.exit(main())` instead of just `main()`?
A2: The return value becomes the process exit code (0 = success). CI and shell scripts use it to detect failure.

Q3: Is the guard required in every file?
A3: No. Only in files that should work both as import and script, or have executable side effects like starting a server.

Q4: How does `python -m pkg.mod` differ from `python pkg/mod.py`?
A4: `-m` runs the module with the package context (`__package__` set, sys.path starts at the current directory), so relative imports work. Running the file path sets `sys.path[0]` to the file's folder and loses the package.

Q5: With multiprocessing on macOS/Windows, why is the guard essential?
A5: Child processes re-import the main module ("spawn"). Without the guard they would re-run the startup code and fork endlessly or crash.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- A file has reusable functions plus a script entry point
- You start a dev server or CLI from a file
- You use `multiprocessing` (spawn start method)

❌ Avoid when:
- The file is only a library, with no script behaviour
- You are hiding big untestable logic inside the guard
- You can use a proper entry point (`console_scripts`, `__main__.py`)

---

## 📊 Visual Diagram

```
 python greet.py                      import greet
       │                                   │
       ▼                                   ▼
 __name__ = "__main__"             __name__ = "greet"
       │                                   │
 guard True  → script part runs     guard False → only definitions load
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `__name__` | Module's name variable | module का नाम |
| `__main__` | Name of the top-level script | मुख्य script का नाम |
| Entry point | Where a program starts | शुरुआत का बिंदु |
| Side effect | Action happening on import | import पर होने वाला असर |
| Exit code | Number returned to the shell | shell को लौटाई संख्या |
| `-m` flag | Run a module by dotted name | module को नाम से चलाना |

---

## ⚡ 3-Line Summary
English: `__name__` is `"__main__"` when a file is run directly and the module name when imported. The guard keeps script-only code (servers, CLIs) from running on import. Put logic in `main()` and call it under the guard.
Hindi: File सीधे चलाने पर `__name__` = `"__main__"` और import पर module का नाम होता है। Guard से script वाला code (server, CLI) import पर नहीं चलता। Logic `main()` में रखें और guard में बुलाएँ।

---

## ➡️ Next Topic
**176. `__init__.py`** — the file that turns a folder into a package and controls what it exports.
