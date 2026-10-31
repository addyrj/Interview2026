---

# 012. Python Interactive Shell (REPL)
# हिंदी में: Python Interactive Shell (REPL)

---

## 🔵 Simple Definition (English)
The REPL (Read-Eval-Print Loop) is Python's interactive shell. You type one statement, Python Reads it, Evaluates it, Prints the result and Loops back to wait for the next input. Start it by typing `python3` in a terminal. It is perfect for quick experiments.

## 🔵 सरल परिभाषा (Hindi)
REPL (Read-Eval-Print Loop) Python का interactive shell है। आप एक statement लिखते हैं, Python उसे Read करती है, Evaluate करती है, result Print करती है और फिर अगले input का इंतज़ार (Loop) करती है। Terminal में `python3` लिखकर शुरू करें। छोटे experiments के लिए बहुत बढ़िया।

---

## 🔴 Problem it Solves
In compiled languages you write a file, compile, run, and read the output, even just to test one line. That is slow for learning and debugging. The REPL gives instant feedback: try a function, inspect an object, test a regex, or check a library's behavior in seconds, without creating a file.

## 🔴 यह क्यों बना? (Hindi)
Compiled languages में सिर्फ एक line test करने के लिए भी file लिखो, compile करो, चलाओ, output देखो। सीखने और debugging के लिए यह धीमा है। REPL तुरंत feedback देता है: function आज़माओ, object inspect करो, regex test करो, library का behavior सेकंडों में देखो, बिना file बनाए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Type  python3  in the terminal; you see the prompt  >>>
Step 2 → READ   : Python reads what you typed (one statement)
Step 3 → EVAL   : It compiles and executes the statement
Step 4 → PRINT  : If it is an expression, the result is shown (via repr)
Step 5 → LOOP   : Prompt returns; variables stay alive in memory
Step 6 → Multi-line blocks (def, for, if) show the prompt  ...
         and end with a blank line
Step 7 → Exit with  exit()  or Ctrl+D (Mac/Linux) / Ctrl+Z then Enter (Windows)

Special tricks:
  _          → holds the last printed result
  help(x)    → manual page of x
  dir(x)     → list the attributes of x
  python3 -i script.py → run a script, then stay in the REPL
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Terminal में python3 लिखें; prompt >>> दिखता है
Step 2 → READ  : आपका लिखा statement पढ़ती है
Step 3 → EVAL  : उसे compile करके चलाती है
Step 4 → PRINT : अगर expression है तो result (repr से) दिखाती है
Step 5 → LOOP  : prompt लौट आता है; variables memory में बने रहते हैं
Step 6 → Multi-line blocks (def, for, if) में prompt ... दिखता है,
         खत्म करने के लिए blank line दें
Step 7 → बाहर निकलें: exit() या Ctrl+D (Mac/Linux) / Ctrl+Z फिर Enter (Windows)

Tricks: _ = पिछला result | help(x) | dir(x) | python3 -i script.py
```

---

## 🟡 Real World Example
A backend developer at a food-delivery company gets a bug report about a wrong GST amount. Instead of editing files, they open `python3`, import the pricing module, call `calculate_gst(499, 0.05)`, and see the answer in one second. Data scientists use the richer `ipython` or Jupyter for the same idea. FastAPI developers use the REPL to test Pydantic models before wiring them to endpoints.

## 🟡 Real Example Hindi mein
Food-delivery company का backend developer GST amount गलत होने की bug report पाता है। Files बदलने की जगह वह `python3` खोलता है, pricing module import करता है, `calculate_gst(499, 0.05)` चलाता है और एक सेकंड में जवाब देख लेता है। Data scientists यही काम `ipython` या Jupyter में करते हैं। FastAPI developers endpoints जोड़ने से पहले Pydantic models REPL में test करते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: simulate a REPL session from a script using the code module
import contextlib  # to capture what the REPL prints
import io  # in-memory text buffer
from code import InteractiveConsole  # the same engine behind python3's prompt

console: InteractiveConsole = InteractiveConsole()  # a fresh REPL session
buffer: io.StringIO = io.StringIO()  # where the output will be collected

with contextlib.redirect_stdout(buffer):  # capture printed output
    console.push("x = 5")  # like typing: >>> x = 5      (no output)
    console.push("x * 2")  # like typing: >>> x * 2      (prints 10)
    console.push("name = 'Asha'")  # assignment again, still no output
    console.push("name.upper()")  # expression -> REPL shows the repr: 'ASHA'
    console.push("def sq(n):")  # start a multi-line block (prompt would be ...)
    console.push("    return n * n")  # function body
    console.push("")  # blank line ends the block
    console.push("sq(7)")  # call the function we just defined

print(buffer.getvalue())  # show everything the REPL printed
# Output:
# 10
# 'ASHA'
# 49
```

## 💻 Code Example — Advanced
```python
# Advanced: explore objects the way you do in a REPL (dir, help, inspect, _)
from __future__ import annotations  # modern hints on all 3.x

import inspect  # signature and source introspection
import sys  # displayhook is what the REPL uses to print results


def public_methods(obj: object, prefix: str = "") -> list[str]:
    """Like typing dir(obj) but without dunder names, optionally filtered."""
    return [n for n in dir(obj) if not n.startswith("_") and n.startswith(prefix)]


print(public_methods("hello", "up"))  # Output: ['upper']
print(public_methods([], "ap"))  # Output: ['append']
print(public_methods({}, "ke"))  # Output: ['keys']

# inspect.signature shows how to call a function (like help() but compact)
sig = inspect.signature(sorted)  # signature of the builtin sorted()
print(sig)  # Output: (iterable, /, *, key=None, reverse=False)

# The first line of any docstring is what help() shows first
first_line: str = (str.upper.__doc__ or "").splitlines()[0]  # docstring of str.upper
print(first_line)  # Output: Return a copy of the string converted to uppercase.

# The REPL prints expression results by calling sys.displayhook:
captured: list[object] = []  # we collect results here instead of printing


def my_hook(value: object) -> None:
    """Replace the default hook to capture results (what IPython does)."""
    if value is not None:  # the REPL never shows None
        captured.append(value)  # store instead of print


old_hook = sys.displayhook  # remember the original
sys.displayhook = my_hook  # install ours
sys.displayhook(3 + 4)  # simulate the REPL evaluating "3 + 4"
sys.displayhook(None)  # None is ignored, exactly like the real REPL
sys.displayhook = old_hook  # always restore it
print(captured)  # Output: [7]
```

---

## 🟠 JavaScript vs Python Comparison
Python's REPL is like the browser DevTools console or running `node` with no arguments (the Node REPL). Both evaluate a line and show the result. Differences: Python uses `_` for the last result (Node also uses `_`), Python needs a blank line to finish a multi-line block, and `help()`/`dir()` have no direct equivalent (in Node you use `console.dir` or `.help`).

```python
# Python REPL session (>>> is the prompt, shown as comments)
# >>> 2 + 3
# 5
# >>> _ * 10        # _ is the last result
# 50
# >>> dir("abc")    # explore methods
# >>> help(str.split)
x: int = 5  # in a script, assignment prints nothing either
```
```javascript
// Node REPL session (> is the prompt)
// > 2 + 3
// 5
// > _ * 10          // _ is the last result in Node too
// 50
// > .help           // Node REPL commands start with a dot
let x = 5; // assignment in the REPL prints "undefined"
```

---

## 🟠 FastAPI Connection
Use the REPL to test the pieces of a FastAPI app before running the server: Pydantic models, helper functions, database queries. You can even call your endpoint functions or use `TestClient` right in the shell. For `async` code, run `python3 -m asyncio` to get a REPL that allows top-level `await`.

```python
# Try this in a REPL (python3), with fastapi and httpx installed:
# >>> from fastapi import FastAPI
# >>> from fastapi.testclient import TestClient
from fastapi import FastAPI  # the framework
from fastapi.testclient import TestClient  # needs httpx installed

app: FastAPI = FastAPI()  # tiny app


@app.get("/ping")  # GET /ping
def ping() -> dict[str, str]:  # return type
    return {"status": "ok"}  # JSON body


client: TestClient = TestClient(app)  # calls the app without starting a server
print(client.get("/ping").json())  # Output: {'status': 'ok'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Pasting indented multi-line code and forgetting the blank line
```python
# Wrong: in the classic REPL, after "def f():" and its body you must press
#        Enter on an empty line before calling f(), or you get a SyntaxError.
# Right: use the blank line, or use ipython / the Python 3.13 REPL
#        (3.13 has multi-line editing and paste mode with F3).
```
✅ Correct: end blocks with a blank line, or use IPython for paste-friendly input.

❌ Mistake 2: Trusting the REPL for final code
```python
# Wrong: writing the whole application inside the REPL (history lost on exit)
# Right: experiment in the REPL, then copy the working lines into a .py file
```
✅ Correct: REPL for exploring, files for real code.

❌ Mistake 3: Thinking `_` works inside scripts
```python
# In the REPL:   >>> 3 + 4   then   >>> _   -> 7
# In a script:   _ is just an ordinary name (often used for "ignored value")
for _ in range(3):  # here _ means "I don't need this variable"
    pass  # nothing to do in the loop body
```
✅ Correct: `_` as last-result is a REPL-only feature.

---

## 🧠 Tricky Interview Question

```python
# In the REPL:
# >>> a = 10
# >>> a
# >>> print(a)
# >>> None
# Which of these lines print something, and what appears?
```
Answer: `a = 10` prints nothing (an assignment is a statement, not an expression). `a` prints `10` because the REPL shows the repr of any expression result. `print(a)` prints `10`, but the call returns `None`, and the REPL does not display `None`. The last line `None` prints nothing for the same reason. Key rule: the REPL displays the `repr()` of the value of an expression unless it is `None`. That is why strings show quotes in the REPL (`'hi'`) but not with `print` (`hi`).

---

## ⚫ Interview Questions + Answers

Q1: What does REPL stand for and how do you use it?
A1: Read-Eval-Print Loop. Run `python3` and type statements at the `>>>` prompt. Each statement is read, evaluated, the result printed, and then it waits for more. It keeps state between lines, so variables and imports stay available.

Q2: How is `python3 -i script.py` useful?
A2: It runs the script, then leaves you in the REPL with all variables and functions of the script still defined. It is great for debugging: when a script crashes, `-i` drops you into the REPL after the error so you can inspect the variables. `python3 -m pdb` and `breakpoint()` are the deeper debugging tools.

Q3: What is the difference between the standard REPL, IPython and Jupyter?
A3: The standard REPL is built in and minimal (the 3.13 version added colors and multi-line editing). IPython adds tab completion, syntax highlighting, magic commands (`%timeit`) and better history. Jupyter notebooks use IPython kernels in the browser and mix code, output and notes; good for data science, not for production code.

Q4: Why do strings appear with quotes in the REPL but not with print?
A4: The REPL uses `repr()` (developer-oriented, unambiguous), while `print` uses `str()` (user-friendly). `repr('hi')` is `"'hi'"`, `str('hi')` is `hi`. Custom classes control this with `__repr__` and `__str__`.

Q5: How do you explore an unknown object in the REPL?
A5: `type(obj)` tells its class, `dir(obj)` lists attributes and methods, `help(obj)` shows documentation, `vars(obj)` shows instance data, and `inspect.getsource(fn)` prints a function's code. For a package, `help('module')` or `import module; dir(module)`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Learning Python or testing a snippet in seconds
- Exploring a new library's API (`dir`, `help`)
- Debugging with `python3 -i` or checking a regex/format string

❌ Avoid when:
- Writing code that must be saved, reviewed or deployed
- Long multi-line programs (use a file or notebook)
- Performance measurement (use `timeit` or a profiler instead)

---

## 📊 Visual Diagram
```
        ┌──────────────────────────────────────────┐
        │                                          │
        ▼                                          │
   ┌─────────┐   ┌──────────┐   ┌─────────┐   ┌────┴────┐
   │  READ   │──►│   EVAL   │──►│  PRINT  │──►│  LOOP   │
   │ >>> 2+3 │   │ compute  │   │   5     │   │ next >>>│
   └─────────┘   └──────────┘   └─────────┘   └─────────┘
        ▲
        └── state (variables, imports) lives in memory between loops
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| REPL | Read-Eval-Print Loop | Read-Eval-Print Loop (interactive shell) |
| Prompt `>>>` | Where you type | जहाँ आप type करते हैं |
| `_` | Last REPL result | पिछला REPL result |
| `repr()` | Developer-friendly text of an object | Object का developer-friendly text |
| IPython | Enhanced interactive shell | बेहतर interactive shell |
| `dir()` | Lists names of attributes | Attributes के नाम की list |

---

## ⚡ 3-Line Summary
English: The REPL reads, evaluates and prints one statement at a time and keeps state between lines. Use `dir`, `help` and `_` to explore quickly. Experiment in the REPL, but write real code in files.
Hindi: REPL एक-एक statement पढ़ता, चलाता और result दिखाता है, और lines के बीच state याद रखता है। जल्दी explore करने के लिए `dir`, `help` और `_` use करें। Experiment REPL में करें, असली code files में लिखें।

---

## ➡️ Next Topic
**013. Variables + Dynamic Typing** — how names point to objects and why you never declare types.
