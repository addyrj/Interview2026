---

# 185. sys Module
# हिंदी में: sys Module (Python interpreter की जानकारी और control)

---

## 🔵 Simple Definition (English)
The `sys` module gives access to the running Python interpreter: command-line arguments (`sys.argv`), module search path (`sys.path`), loaded modules (`sys.modules`), standard input/output/error streams, version and platform info, the recursion limit, and `sys.exit()` to end the program with a status code.

## 🔵 सरल परिभाषा (Hindi)
`sys` module चल रहे Python interpreter तक पहुँच देता है: command-line arguments (`sys.argv`), module खोज path (`sys.path`), loaded modules (`sys.modules`), standard input/output/error streams, version और platform की जानकारी, recursion limit और program को status code के साथ खत्म करने वाला `sys.exit()`।

---

## 🔴 Problem it Solves
Scripts need to read arguments, report errors on the right stream, exit with a code that shells and CI understand, adapt to OS or Python version, and inspect or tune the interpreter. `sys` is the one place for these interpreter-level facts.

## 🔴 यह क्यों बना? (Hindi)
Scripts को arguments पढ़ने, errors सही stream पर भेजने, shell और CI की समझ वाले code से exit करने, OS या Python version के हिसाब से बदलने और interpreter को देखने/ट्यून करने की ज़रूरत होती है। ये सब interpreter-level बातें `sys` में एक जगह हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python starts and builds the sys module before your code runs
Step 2 → sys.argv = ["script.py", "arg1", ...]  (argv[0] is the script)
Step 3 → sys.stdin / stdout / stderr are file-like objects (print uses stdout)
Step 4 → sys.exit(code) raises SystemExit → 0 = success, non-zero = failure
Step 5 → sys.version_info, sys.platform let code branch by version / OS
Step 6 → sys.modules (cache), sys.path (search list), sys.getrecursionlimit() = 1000
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आपके code से पहले Python sys module तैयार कर देता है
Step 2 → sys.argv = ["script.py", "arg1", ...]  (argv[0] script का नाम)
Step 3 → sys.stdin / stdout / stderr file जैसे objects हैं (print stdout पर लिखता है)
Step 4 → sys.exit(code) SystemExit उठाता है → 0 = सफल, non-zero = असफल
Step 5 → sys.version_info, sys.platform से version / OS के हिसाब से branch करें
Step 6 → sys.modules (cache), sys.path (खोज list), sys.getrecursionlimit() = 1000
```

---

## 🟡 Real World Example
A Zomato data-fix CLI reads the file name from `sys.argv`, writes errors to `sys.stderr`, and calls `sys.exit(1)` so the CI pipeline marks the step as failed. A library checks `sys.version_info >= (3, 11)` to import `tomllib`. A Dockerized FastAPI app logs to `sys.stdout` because container platforms collect stdout.

## 🟡 Real Example Hindi mein
Zomato का data-fix CLI file का नाम `sys.argv` से पढ़ता है, errors `sys.stderr` पर लिखता है और `sys.exit(1)` देता है ताकि CI pipeline वह step fail दिखाए। Library `sys.version_info >= (3, 11)` देखकर `tomllib` import करती है। Docker में चलने वाला FastAPI app `sys.stdout` पर log करता है क्योंकि container platforms stdout इकट्ठा करते हैं।

---

## 💻 Code Example — Basic
```python
# Basic sys examples - every line commented
import sys  # the module

print(sys.argv)  # list of command-line arguments; argv[0] is the script name
# Output: ['185_Basic.py']  (your script's path as typed; ['-c'] style differs)

print(sys.version_info[:2])  # (major, minor) tuple
# Output: (3, 13)   (depends on your Python)
print(sys.version_info >= (3, 10))  # tuples compare element by element
# Output: True

print(sys.platform)  # 'darwin' (mac), 'linux', 'win32'
# Output: darwin   (varies by OS)

sys.stdout.write("to stdout\n")  # what print() uses by default
# Output: to stdout
print("to stderr", file=sys.stderr)  # error stream, separate from normal output
# Output (on stderr): to stderr

print(type(sys.modules).__name__, "os" in sys.modules)  # cache of loaded modules
# Output: dict True

print(sys.getrecursionlimit())  # default max recursion depth
# Output: 1000

print(sys.maxsize)  # largest "native" index/size on this platform
# Output: 9223372036854775807   (64-bit build)

sys.exit(3)  # ends the program with exit code 3 (raises SystemExit)
# Output: (nothing printed; shell sees exit status 3)
```

## 💻 Code Example — Advanced
```python
# Production CLI with exit codes, stream swapping for tests, and recursion handling.
import io  # in-memory streams
import sys  # interpreter access
from contextlib import redirect_stdout  # safe stdout swap
from typing import List, Optional  # type hints


def count_lines(path: str) -> int:
    """Return number of lines in a text file."""
    with open(path, encoding="utf-8") as fh:  # open with explicit encoding
        return sum(1 for _ in fh)  # lazy count


def main(argv: Optional[List[str]] = None) -> int:
    """Return an exit code instead of calling sys.exit inside logic."""
    args: List[str] = sys.argv[1:] if argv is None else argv  # skip the script name
    if len(args) != 1:  # validate usage
        print("usage: lines.py FILE", file=sys.stderr)  # errors -> stderr
        return 2  # 2 = usage error (shell convention)
    try:
        print(count_lines(args[0]))  # normal output -> stdout
    except FileNotFoundError:  # expected failure
        print(f"error: no such file: {args[0]}", file=sys.stderr)
        return 1  # 1 = runtime failure
    return 0  # success


# Test main() without a shell by capturing stdout
buffer = io.StringIO()  # fake stdout
with redirect_stdout(buffer):  # temporarily replace sys.stdout
    code = main(["/definitely/missing.txt"])  # the error goes to the REAL stderr
print(code, repr(buffer.getvalue()))  # nothing on stdout, exit code 1
# Output: 1 ''
# (stderr shows: error: no such file: /definitely/missing.txt)

# sys.exit semantics: it raises SystemExit, which you can catch
try:
    sys.exit("fatal message")  # a string is printed to stderr, exit status 1
except SystemExit as exc:  # normally you should not catch this
    print("caught:", exc.code)  # the code / message
# Output: caught: fatal message


# Recursion limit: deep recursion raises RecursionError, not a crash
def depth(n: int) -> int:
    return depth(n + 1)  # infinite recursion


old: int = sys.getrecursionlimit()  # remember the old limit
sys.setrecursionlimit(200)  # lower it for a quick demo
try:
    depth(0)  # blow the stack safely
except RecursionError as exc:
    print("RecursionError:", str(exc).split(" ")[0:3])  # short message
# Output: RecursionError: ['maximum', 'recursion', 'depth']
finally:
    sys.setrecursionlimit(old)  # always restore

# Object sizes (bytes; vary by Python build)
print(sys.getsizeof([]), sys.getsizeof(1), sys.getsizeof(""))
# Output: 56 28 41
if __name__ == "__main__":  # real script usage
    sys.exit(main())  # exit with main's code (here: usage error 2 if no args)
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import sys
args = sys.argv[1:]                 # arguments after the script
print("oops", file=sys.stderr)      # stderr
sys.exit(1)                         # exit code
sys.stdout.write("no newline")      # raw write
```

```javascript
// JavaScript (Node)
const args = process.argv.slice(2);         // argv[0]=node, argv[1]=script
console.error("oops");                      // stderr
process.exit(1);                            // exit code
process.stdout.write("no newline");         // raw write
// process.platform ~ sys.platform ; process.version ~ sys.version
```

Key difference: Node's `process.argv` starts with the node binary AND the script (slice 2); Python's `sys.argv[0]` is the script (slice 1). Node's `process` is global; Python's `sys` must be imported.

---

## 🟠 FastAPI Connection
In deployments you read stdout/stderr logs from containers, so configure logging to `sys.stdout`. `sys.exit` is used in start-up checks (fail fast if config is missing). Version checks use `sys.version_info`.

```python
# FastAPI start-up checks and logging to stdout (needs: pip install fastapi)
import logging  # logging
import os  # environment variables
import sys  # stdout and exit
from fastapi import FastAPI  # framework

logging.basicConfig(stream=sys.stdout, level=logging.INFO)  # containers collect stdout
log = logging.getLogger("api")  # named logger

if sys.version_info < (3, 9):  # fail fast on unsupported Python
    sys.exit("Python 3.9+ required")  # message goes to stderr, exit code 1

app: FastAPI = FastAPI()  # application


@app.on_event("startup")  # older style; modern FastAPI prefers lifespan
def check_config() -> None:
    if not os.getenv("DATABASE_URL"):  # required setting missing
        log.error("DATABASE_URL missing")  # visible in container logs
        # in a real service: sys.exit(1) here so the orchestrator restarts/alerts
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `argv[0]` is the script name
```python
# Wrong:
# name = sys.argv[0]      # this is the script path, not the first argument

# Correct:
# name = sys.argv[1] if len(sys.argv) > 1 else "world"
# (for real CLIs use argparse or Typer)
```

❌ Mistake 2: Printing errors to stdout
```python
# Wrong: print("error!")                         # mixes with real output when piped
# Correct: print("error!", file=sys.stderr)      # shells can separate the streams
```

❌ Mistake 3: Raising the recursion limit instead of fixing the algorithm
```python
# Wrong: sys.setrecursionlimit(10**6)            # can crash the interpreter (C stack overflow)
# Correct: convert to a loop or use an explicit stack
```

---

## 🧠 Tricky Interview Question

**Q**: What is the exit code of this script, and what prints?

```python
import sys
try:
    sys.exit(2)
except Exception:
    print("caught by Exception")
finally:
    print("cleanup")
```

**Answer**:
```
cleanup
```
and the process exit code is `2`. `SystemExit` inherits from `BaseException`, not `Exception`, so `except Exception` does NOT catch it. The `finally` block still runs (printing `cleanup`), then the interpreter exits with status 2. Also `KeyboardInterrupt` and `GeneratorExit` are `BaseException` subclasses.

---

## ⚫ Interview Questions + Answers

Q1: What does `sys.exit()` actually do?
A1: It raises `SystemExit`. If uncaught, the interpreter exits: `None` or `0` means success, an int is the exit status, and any other object is printed to stderr with status 1.

Q2: `sys.exit()` vs `os._exit()`?
A2: `sys.exit` unwinds the stack, runs `finally` blocks and `atexit` handlers. `os._exit` ends immediately with no cleanup (used in forked children).

Q3: What is `sys.modules`?
A3: A dict of all loaded modules by name. It is the import cache; deleting an entry forces a re-import, and tests use it to patch modules.

Q4: Why is the default recursion limit 1000?
A4: It protects the C stack from overflowing. Python-to-Python calls got cheaper in 3.11 and 3.12 changed how limits apply, but `RecursionError` is still the safety net. Prefer iteration over a huge limit.

Q5: How do you check Python version or OS safely?
A5: `sys.version_info >= (3, 10)` (tuple comparison, never string compare "3.9" vs "3.10") and `sys.platform.startswith("linux")`.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Reading simple argv, exit codes, stderr output
- Version/platform feature checks
- Debugging imports (`sys.path`, `sys.modules`)

❌ Avoid when:
- Parsing complex CLI options (use `argparse`/Typer/click)
- Logging seriously (use `logging`)
- Tuning the recursion limit as a fix

---

## 📊 Visual Diagram

```
 python app.py --debug file.txt
   │
   ▼
 sys.argv   = ["app.py", "--debug", "file.txt"]
 sys.stdin  ◄── keyboard / pipe          sys.path    = [folders searched]
 sys.stdout ──► normal output (print)    sys.modules = {name: module}
 sys.stderr ──► errors (separate)        sys.version_info = (3, 13, ...)
   │
   ▼  sys.exit(code) → SystemExit → shell sees $? = code
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `sys.argv` | Command-line arguments | command-line arguments |
| `sys.exit` | End program with a code | code के साथ program खत्म |
| stdout / stderr | Output / error streams | सामान्य / error output |
| Exit code | 0 success, non-zero failure | निकासी कोड |
| `sys.modules` | Cache of loaded modules | loaded modules का cache |
| Recursion limit | Max function call depth | recursion की अधिकतम गहराई |

---

## ⚡ 3-Line Summary
English: `sys` exposes interpreter facts: `argv`, `path`, `modules`, streams, version, platform and `exit`. Send errors to `stderr` and return proper exit codes. Use `argparse` for real CLIs and fix recursion with loops.
Hindi: `sys` interpreter की जानकारी देता है: `argv`, `path`, `modules`, streams, version, platform और `exit`। Errors `stderr` पर भेजें और सही exit code लौटाएँ। असली CLI के लिए `argparse` और recursion की जगह loops चुनें।

---

## ➡️ Next Topic
**186. pathlib Module** — the modern object-oriented way to work with file paths (an existing note covers `os` and `pathlib` together in 184).
