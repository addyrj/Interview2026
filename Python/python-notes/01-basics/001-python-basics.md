---

# 001. What is Python + How it Works
# हिंदी में: Python क्या है + कैसे काम करता है

---

## 🔵 Simple Definition (English)
Python is a high-level, interpreted, dynamically typed programming language. "High-level" means you write human-readable code, not machine instructions. "Interpreted" means Python executes code line by line without compiling to binary first. "Dynamically typed" means you don't declare variable types — Python figures them out at runtime.

## 🔵 सरल परिभाषा (Hindi)
Python एक high-level, interpreted, dynamically typed programming language है। "Interpreted" = binary compile किए बिना line-by-line execute। "Dynamically typed" = variable types declare नहीं करते, Python runtime पर figure out करती है।

---

## 🔴 Problem it Solves
C/C++: fast but manual memory management, complex syntax. Java: verbose, compile step required. JavaScript: browser-first, not ideal for data/AI work. Python: readable as English, batteries included (huge stdlib), dominates data science, ML, and backend. Same language for scripting, web APIs, ML, and automation.

## 🔴 यह क्यों बना? (Hindi)
C/C++ complex, Java verbose। Python: English जैसा readable, huge stdlib, data science + ML + backend — एक language से सब।

---

## 🟢 How Python Works — Step by Step

```
Step 1 → You write: hello.py  (human-readable source code)
Step 2 → Python compiler → bytecode (.pyc files in __pycache__)
Step 3 → CPython VM (Virtual Machine) executes bytecode
Step 4 → CPython calls OS/C functions for actual operations
Step 5 → Results returned to your Python code

Source (.py) → Bytecode (.pyc) → CPython VM → OS/Hardware
```

## 🟢 कैसे काम करता है? (Hindi)
```
.py file → bytecode (.pyc) → CPython VM → OS/Hardware
Same source runs on Windows, Mac, Linux — VM handles differences
```

---

## 🟡 Real World Example
Instagram (Django/Python), Dropbox (Python), Netflix (Python for automation), Spotify (Python microservices), Google (Python as first-class language). FastAPI — Python-first web framework used by Uber, Netflix, Microsoft.

---

## 💻 Code Example — Basic
```python
# Python vs JavaScript — side by side comparison

# VARIABLES — no type declaration needed:
name = "Priya"            # str
age = 25                  # int (Python figures it out)
salary = 75000.50         # float
is_senior = False         # bool
nothing = None            # None (like JS null)

# PRINT:
print(f"Name: {name}, Age: {age}")   # f-string (like JS template literals)

# TYPES — Python knows at runtime:
print(type(name))         # <class 'str'>
print(type(age))          # <class 'int'>
print(isinstance(age, int))  # True

# DYNAMIC TYPING — same variable, different type:
x = 10
print(type(x))   # <class 'int'>
x = "hello"
print(type(x))   # <class 'str'>  — no error! (JS does this too)

# TYPE HINTS — optional, for readability + IDE support:
def greet(name: str, age: int) -> str:      # hints don't enforce at runtime!
    return f"Hello {name}, you are {age}"

result: str = greet("Priya", 25)
print(result)
```

## 💻 Code Example — Advanced
```python
# Python execution model + CPython specifics

# 1. See bytecode (what CPython actually runs):
import dis

def add(a, b):
    return a + b

dis.dis(add)
# Output:
#   LOAD_FAST  0 (a)
#   LOAD_FAST  1 (b)
#   BINARY_OP  +
#   RETURN_VALUE

# 2. Python vs PyPy — same code, different speeds:
# CPython: reference implementation, standard, ~1x
# PyPy: JIT-compiled Python, 5-10x faster for CPU-bound code
# Run the same file: python hello.py vs pypy hello.py

# 3. Virtual environments (every project needs one):
# python -m venv venv          ← create venv
# source venv/bin/activate      ← activate (Mac/Linux)
# venv\Scripts\activate         ← activate (Windows)
# pip install fastapi            ← installs ONLY in this venv
# pip freeze > requirements.txt  ← save dependencies

# 4. Modern: pyproject.toml (replaces requirements.txt)
# [project]
# name = "my-app"
# version = "0.1.0"
# dependencies = ["fastapi>=0.100", "sqlalchemy>=2.0"]

# 5. The __name__ == "__main__" guard:
def main():
    print("App starting...")

if __name__ == "__main__":
    main()
# When imported: __name__ = "module_name" → main() NOT called
# When run directly: __name__ = "__main__" → main() IS called
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
name = "Priya"          # no 'let/const/var'
age = 25                # no semicolons
if age >= 18:           # colon, no braces
    print("adult")      # INDENTATION is the block!
    
# list (like JS array):
fruits = ["apple", "mango", "banana"]
for fruit in fruits:    # no 'for (let i=0...)'
    print(fruit)

# function:
def greet(name, age=18):    # default parameter
    return f"Hi {name}"
```

```javascript
// JavaScript
let name = "Priya";     // need let/const/var
let age = 25;           // semicolons
if (age >= 18) {        // braces required
    console.log("adult");
}

// array:
let fruits = ["apple", "mango", "banana"];
for (let fruit of fruits) {
    console.log(fruit);
}

// function:
function greet(name, age=18) {
    return `Hi ${name}`;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mixing tabs and spaces (causes IndentationError)
```python
# Wrong — mixing tabs and spaces:
def func():
    x = 1       # 4 spaces
	y = 2       # 1 tab ← IndentationError!

# Correct — always use 4 spaces (PEP8 standard):
def func():
    x = 1
    y = 2
```

❌ Mistake 2: Thinking type hints enforce types
```python
# Wrong assumption:
def add(a: int, b: int) -> int:
    return a + b

result = add("hello", "world")   # NO error! returns "helloworld"
# Type hints are documentation only — Python doesn't enforce them
# Use mypy or Pydantic for actual enforcement
```

---

## 🧠 Tricky Interview Question

**Q**: "Python is called interpreted but it compiles to bytecode. Is Python compiled or interpreted?"

**Answer**: Both. Python source code IS compiled — to bytecode (.pyc files). But that bytecode isn't machine code — it runs on the CPython virtual machine, which interprets it. So Python is "compiled to bytecode, then interpreted." This is why Python is slower than C (C compiles all the way to machine code) but faster than truly interpreted languages. PyPy goes further — it JIT-compiles the bytecode to native machine code at runtime.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between CPython and PyPy?
A1: CPython: the standard, reference implementation written in C. Interprets bytecode. Most libraries (NumPy, Django) are built for CPython. PyPy: alternative implementation with JIT (Just-In-Time) compilation — compiles hot code paths to machine code at runtime. 5-10x faster for CPU-bound tasks. Not all libraries work with PyPy (those with C extensions may not). For FastAPI/web: CPython is standard; for number-crunching scripts: PyPy is worth trying.

Q2: What is PEP 8?
A2: Python Enhancement Proposal 8 — the style guide for Python code. Key rules: 4 spaces for indentation (not tabs), max line length 79 characters (99 in modern projects), snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants, two blank lines between top-level functions/classes. Use `black` (formatter) or `ruff` to auto-apply PEP 8. Interviewers notice sloppy formatting.

Q3: What is a virtual environment and why is it needed?
A3: A venv is an isolated Python environment with its own installed packages. Without it: all packages install globally — Project A needs Django 3.2, Project B needs Django 4.2 → conflict. With venv: each project has its own isolated packages. `python -m venv venv`, `source venv/bin/activate`, `pip install`. Modern alternative: `poetry` or `uv` (much faster than pip).

Q4: What is the difference between `==` and `is` in Python?
A4: `==` checks value equality: `[1,2] == [1,2]` is `True`. `is` checks object identity (same memory address): `[1,2] is [1,2]` is `False` (two different list objects). Exception: small integers (-5 to 256) and interned strings are cached — `a = 256; b = 256; a is b` is `True` because Python reuses the same int object. Rule: only use `is` for `None`, `True`, `False`: `if x is None:`.

Q5: What is duck typing?
A5: "If it walks like a duck and quacks like a duck, it is a duck." Python doesn't check types — it checks if an object supports the required operation. `len(obj)` works on lists, strings, dicts, custom classes with `__len__` — Python doesn't check "is this a list?", just calls `obj.__len__()`. This enables more flexible, reusable code. Downside: type errors appear at runtime, not compile time (solved with type hints + mypy).

---

## 🔷 When to Use Python

✅ Use Python when:
- Backend APIs (FastAPI, Django, Flask)
- Data science / ML / AI (numpy, pandas, scikit-learn, PyTorch)
- Scripting and automation
- Prototyping (fastest to write and run)

❌ Avoid Python when:
- Mobile apps (use Swift/Kotlin)
- Performance-critical real-time systems (use Go, Rust, C++)
- Frontend (use JavaScript/TypeScript)

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Interpreter | Executes code line by line | Code line-by-line execute करता है |
| Bytecode | Compiled intermediate code | Intermediate compiled code |
| CPython | Default Python implementation | Default Python implementation |
| Virtual environment | Isolated package space | Isolated package space |
| Dynamic typing | Types determined at runtime | Runtime पर types decide होती हैं |
| PEP 8 | Python style guide | Python का style guide |

---

## ⚡ 3-Line Summary
English: Python is interpreted (line-by-line), dynamically typed (no type declarations), and compiles to bytecode that runs on the CPython VM. It dominates data science, AI, and backend development because of readable syntax and rich libraries. Always use virtual environments and type hints for clean, maintainable code.
Hindi: Python interpreted (line-by-line), dynamically typed है — bytecode में compile होकर CPython VM पर run होती है। Data science, AI, backend में dominant। Virtual environment + type hints = clean code।

---

## ➡️ Next Topic
**002. Python vs JavaScript** — syntax differences, async models, use cases, when to choose which.
