---

# Q308. if __name__ == '__main__'
# Category: INTERVIEW CLASSICS
# Difficulty: ⭐ Easy

---

## ❓ Question
What does `if __name__ == "__main__":` do, and why does it matter when a file is both run as a script and imported as a module? Show the value of `__name__` in both cases.

```python
# NOT RUN (question stub) -- file: tools.py
def add(a, b):
    return a + b

print("tools loaded")     # runs on import too!
print(add(1, 2))
```

---

## 💡 Quick Concept (2 lines only)
When a file is executed directly (`python tools.py`) Python sets its `__name__` to `"__main__"`; when it is imported, `__name__` is the module name (`"tools"`). The guard lets one file be reusable code AND a runnable script.
हिंदी: सीधे चलाओ तो `__name__ == "__main__"`; import करो तो module का नाम — guard से import पर side effects नहीं चलते।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION  (we create tools.py in a temp dir, then run it both ways)
# ============================================
import pathlib                                           # write files
import subprocess                                        # run python as a child process
import sys                                               # path to the current interpreter
import tempfile                                          # throw-away directory

SOURCE = '''
def add(a, b):
    return a + b                                         # reusable logic

print("__name__ is", __name__)                           # shows how we were loaded

if __name__ == "__main__":                               # only when run directly
    print("running as script:", add(1, 2))               # script behaviour
'''

with tempfile.TemporaryDirectory() as d:                 # temp dir cleaned up automatically
    pathlib.Path(d, "tools.py").write_text(SOURCE)       # create the module file

    run = subprocess.run([sys.executable, "tools.py"],   # python tools.py
                         cwd=d, capture_output=True, text=True)
    print(run.stdout, end="")                            # direct run output

    imp = subprocess.run([sys.executable, "-c", "import tools; print(tools.add(5, 5))"],
                         cwd=d, capture_output=True, text=True)  # import tools
    print(imp.stdout, end="")                            # import output

# Expected output:
# __name__ is __main__
# running as script: 3
# __name__ is tools
# 10
```

---

## 🔍 Why This Works (3 lines max)
The interpreter runs the top-level code of every module it loads; only the entry-point module gets `__name__ = "__main__"`. On import, the `if` block is skipped, so `import tools` defines `add` without printing "running as script".
हिंदी: Import पर पूरा module एक बार चलता है, पर `if __name__ == "__main__"` वाला हिस्सा skip हो जाता है।

---

## ⚡ Alternative Solution
```python
# Typical real-world layout: a main() function + guard + exit code
import sys                                               # argv / exit


def main(argv: list[str] | None = None) -> int:          # testable entry point
    args = sys.argv[1:] if argv is None else argv        # allow tests to pass args
    print("args:", args)                                 # do the work
    return 0                                             # exit status


if __name__ == "__main__":                               # skipped on import
    sys.exit(main())                                     # propagate status to the shell
else:
    print("imported, not run")                           # shows the other branch


# Notes:
#  - `python -m package.module` also sets __name__ == "__main__" for that module
#  - a package can provide __main__.py so `python -m package` works
#  - in a notebook / REPL, __name__ is also "__main__"

# Expected output when this block is run as a script:
# args: []
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: top-level side effects with no guard -> importing the module triggers them
#   (e.g. starts a server, connects to a DB, runs tests, prints noise)
# connect_to_database()
# app.run()

# ❌ Wrong: typo / using = instead of ==
# if __name__ = "__main__":      # SyntaxError

# ✅ Correct: put executable code in main() and guard the call
def main() -> None:
    print("started")                                     # real work lives here

if __name__ == "__main__":                               # runs only as a script
    main()

# Expected output:
# started
```

---

## 🎯 Interview Tip (1 line)
Say: "The guard makes a file importable without side effects; the entry module's `__name__` is `'__main__'`, and I keep logic in `main()` so tests can call it."

---

## 🔗 Related Questions
→ Q041 (LEGB scope output) | Q300 (__init__ vs __new__) | Q306 (dunder methods) | Q310 (Python vs JavaScript)
