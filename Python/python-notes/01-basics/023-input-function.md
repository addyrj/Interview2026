---

# 023. input() Function
# हिंदी में: input() Function — user से input लेना

---

## 🔵 Simple Definition (English)
`input(prompt)` pauses the program, shows an optional prompt, waits for the user to type a line and press Enter, and returns what they typed as a **string** (without the trailing newline). Even if the user types `25`, you get `"25"`, not the number 25.

## 🔵 सरल परिभाषा (Hindi)
`input(prompt)` program को रोकता है, prompt दिखाता है, user के type करके Enter दबाने का इंतज़ार करता है और जो लिखा गया उसे **string** के रूप में return करता है (आखिरी newline के बिना)। User `25` लिखे तब भी आपको `"25"` मिलता है, number 25 नहीं।

---

## 🔴 Problem it Solves
Programs with fixed values are useless. You need a way to get data at runtime: a name, an age, a choice from a menu. `input()` is the simplest way to make a command-line program interactive without any library, and it is the base for CLI tools, quick scripts and coding-test problems.

## 🔴 यह क्यों बना? (Hindi)
Fixed values वाले programs बेकार होते हैं। Runtime पर data चाहिए: नाम, उम्र, menu का choice। `input()` बिना किसी library के command-line program को interactive बनाने का सबसे आसान तरीका है। CLI tools, scripts और coding tests का आधार यही है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → input("Enter age: ") prints the prompt (no newline) to stdout
Step 2 → Program is BLOCKED, waiting on stdin
Step 3 → User types characters and presses Enter
Step 4 → Python reads the full line and removes the trailing "\n"
Step 5 → Returns it as str (always!)
Step 6 → You convert it: int(text), float(text) and validate it
Step 7 → If stdin is closed (Ctrl+D / piped input ends) → EOFError
         If user presses Ctrl+C → KeyboardInterrupt
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → prompt screen पर आता है
Step 2 → Program रुक जाता है, stdin का इंतज़ार करता है
Step 3 → User type करके Enter दबाता है
Step 4 → Line पढ़ी जाती है, आखिरी "\n" हट जाता है
Step 5 → हमेशा str return होती है
Step 6 → int()/float() से convert और validate करो
Step 7 → Ctrl+D पर EOFError, Ctrl+C पर KeyboardInterrupt
```

---

## 🟡 Real World Example
A bank CLI tool asks `Enter account number:` and `Enter amount:`; the amount must be converted to a number and validated before a transfer. In competitive programming and coding rounds, input comes from stdin: `n = int(input())`, then `arr = list(map(int, input().split()))`. A deployment script asks `Deploy to production? (y/n):` before doing something risky. In a FastAPI web service you almost never use `input()`; data comes from the HTTP request instead.

## 🟡 Real Example Hindi mein
Bank का CLI tool `Enter amount:` पूछता है और transfer से पहले उसे number में convert करके validate करता है। Coding rounds में `n = int(input())` और `arr = list(map(int, input().split()))` आम pattern है। Deployment script risky काम से पहले `Deploy to production? (y/n):` पूछती है। FastAPI web service में `input()` लगभग कभी नहीं होता, data HTTP request से आता है।

---

## 💻 Code Example — Basic
```python
# input() basics — run with: python3 file.py (then type values)
# To test without typing: printf 'Priya\n25\n1 2 3\n' | python3 file.py

# Read a name: always a string
name: str = input("Enter your name: ")          # waits for user, returns str
print(f"Hello, {name}!")                         # use the value

# Read an age: convert str -> int
age_text: str = input("Enter your age: ")        # "25" is still a string
age: int = int(age_text)                         # convert to int
print(f"Next year you will be {age + 1}")        # arithmetic works on int

# Proof that input returns a string
print(type(age_text))                            # Output: <class 'str'>
print(type(age))                                 # Output: <class 'int'>

# Read many numbers on one line: "1 2 3"
line: str = input("Enter numbers: ")             # e.g. "1 2 3"
parts: list[str] = line.split()                  # ['1', '2', '3']
numbers: list[int] = [int(p) for p in parts]     # [1, 2, 3]
print("Sum:", sum(numbers))                      # Output: Sum: 6

# strip() removes extra spaces around the text
raw: str = "  Priya  "                           # imagine the user typed spaces
print(repr(raw.strip()))                         # Output: 'Priya'
```

## 💻 Code Example — Advanced
```python
# Production style input: validation loop, defaults, EOF handling, testable design
from collections.abc import Callable          # type for the input function
from typing import TypeVar                    # generic return type

T = TypeVar("T")                              # T = whatever the parser returns


def ask(
    prompt: str,                              # text shown to the user
    parser: Callable[[str], T],               # function that converts the text
    *,
    default: T | None = None,                 # value to use if user presses Enter
    max_tries: int = 3,                       # do not loop forever
    reader: Callable[[str], str] = input,     # injectable, so tests can fake input
) -> T:
    """Keep asking until parser accepts the answer or tries run out."""
    for attempt in range(1, max_tries + 1):   # 1..max_tries
        try:
            text: str = reader(prompt).strip()      # read and clean the answer
        except EOFError:                             # stdin closed (piped input ended)
            if default is not None:                  # fall back to default if present
                return default
            raise ValueError("no input available") from None
        if text == "" and default is not None:       # empty answer -> default
            return default
        try:
            return parser(text)                      # try to convert
        except ValueError:                           # bad format
            print(f"  invalid input ({attempt}/{max_tries}), try again")
    raise ValueError(f"too many invalid attempts for: {prompt!r}")


def positive_int(text: str) -> int:
    """Parser: accept only positive integers."""
    value: int = int(text)                    # raises ValueError if not a number
    if value <= 0:                            # business rule
        raise ValueError("must be positive")
    return value


def yes_no(text: str) -> bool:
    """Parser: accept y/yes/n/no."""
    answer: str = text.lower()                # normalise case
    if answer in {"y", "yes"}:                # truthy answers
        return True
    if answer in {"n", "no"}:                 # falsy answers
        return False
    raise ValueError("answer y or n")         # anything else is invalid


def main() -> None:
    # Fake user answers so this file runs without typing anything
    answers = iter(["abc", "-5", "42", "", "maybe", "y"])   # simulated keystrokes

    def fake_input(prompt: str) -> str:       # replaces input() in this demo
        value: str = next(answers)            # next simulated answer
        print(f"{prompt}{value}")             # echo like a terminal would
        return value

    qty: int = ask("Quantity: ", positive_int, reader=fake_input)
    # Output: Quantity: abc / invalid input (1/3) ... Quantity: -5 / invalid ... Quantity: 42
    print("qty =", qty)                       # Output: qty = 42

    city: str = ask("City [Delhi]: ", str, default="Delhi", reader=fake_input)
    print("city =", city)                     # Output: city = Delhi

    confirm: bool = ask("Confirm (y/n): ", yes_no, reader=fake_input)
    # "maybe" is invalid, then "y" is accepted
    print("confirm =", confirm)               # Output: confirm = True


if __name__ == "__main__":
    main()                                    # run only when executed directly
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: built in, blocking, synchronous
name = input("Name: ")            # waits right here
age = int(input("Age: "))         # convert yourself
print(f"{name} is {age}")
```
```javascript
// JavaScript (Node.js): no built-in blocking input, you need readline
const readline = require("readline");
const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

rl.question("Name: ", (name) => {          // callback style (async)
  rl.question("Age: ", (age) => {
    console.log(`${name} is ${Number(age)}`); // Number() converts
    rl.close();
  });
});

// Browser: prompt("Name?") is the closest to Python's input()
```

Key differences: Python `input()` is **blocking and synchronous**, so code reads top to bottom. Node needs callbacks or `readline/promises`. Both return text, so you must convert numbers yourself (`int()` vs `Number()`). Python raises `ValueError` for `int("abc")`; JS `Number("abc")` silently gives `NaN`.

---

## 🟠 FastAPI Connection
A web server has no keyboard; calling `input()` inside an endpoint would block the whole process forever. Input comes from the request instead, and FastAPI does the "convert and validate" job that you do by hand with `int(input())`: you declare types and FastAPI parses and returns a 422 error for bad values. The `ask()` function above is the same idea (parse + validate + retry), just for a terminal.

```python
# FastAPI example (needs: pip install fastapi)
from fastapi import FastAPI, Query              # framework + query validation

app: FastAPI = FastAPI()                        # create app


@app.get("/pay")                                # GET /pay?amount=500
async def pay(amount: int = Query(gt=0)) -> dict[str, int]:
    # "amount" arrives as text in the URL, FastAPI converts to int and checks > 0
    return {"paid": amount}                     # JSON response
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting that input() returns a string
```python
# Wrong: "10" + "20" joins text
a = "10"                      # imagine a = input()
b = "20"                      # imagine b = input()
print(a + b)                  # Output: 1020  (not 30!)

# Right: convert first
print(int(a) + int(b))        # Output: 30
```

❌ Mistake 2: No validation, program crashes on bad input
```python
# Wrong: int("abc") raises ValueError and crashes the program
# age = int(input("Age: "))

# Right: catch the error
text: str = "abc"             # imagine this came from input()
try:
    age: int = int(text)      # may fail
except ValueError:
    age = 0                   # safe fallback
    print("Please enter a number")
```

❌ Mistake 3: Using eval(input()) to get numbers
```python
# Wrong: eval runs ANY code the user types, e.g. __import__("os").system("rm -rf ~")
# n = eval(input())

# Right: use int(), float() or ast.literal_eval for literals
import ast
data = ast.literal_eval("[1, 2, 3]")   # safe: only literals allowed
print(data)                            # Output: [1, 2, 3]
```

❌ Mistake 4: Not handling EOFError / empty lines in scripts
```python
# Wrong: crashes with EOFError when stdin is empty (cron, Docker, CI)
# name = input("Name: ")

# Right: handle EOF and provide a default
try:
    name: str = input("Name: ")
except EOFError:
    name = "guest"
print(name)
```

---

## 🧠 Tricky Interview Question

```python
# Assume the user types: 5 and then 3
a = input()
b = input()
print(a + b)
print(a * 2)
print(max(a, b))
print(a < "10")
```

**Answer:**
```
53
55
5
False
```
Both values are strings. `a + b` is concatenation `"53"`. `a * 2` repeats the text `"55"`. `max("5", "3")` compares characters alphabetically, so `"5"`. `"5" < "10"` is `False` because string comparison is character by character: `"5"` vs `"1"`, and `"5"` is bigger. With real ints, `5 < 10` would be `True`. This is the classic bug when input is not converted.

---

## ⚫ Interview Questions + Answers

Q1: What type does input() return?
A1: Always `str`, even for digits. Python never guesses the type. Use `int()`, `float()` or a parser to convert. In Python 2, `raw_input()` did this and `input()` evaluated the text; Python 3 removed that dangerous behaviour.

Q2: How do you read multiple integers from one line?
A2: `nums = list(map(int, input().split()))` or `[int(x) for x in input().split()]`. `split()` with no argument splits on any whitespace and ignores extra spaces. For very large inputs in competitive programming, `sys.stdin.readline` is faster than `input()`.

Q3: What exceptions can input() raise?
A3: `EOFError` when no more data is available (Ctrl+D, closed pipe) and `KeyboardInterrupt` on Ctrl+C. The conversion afterwards (`int(...)`) can raise `ValueError`. A robust script handles all three.

Q4: Why is eval(input()) dangerous?
A4: `eval` executes arbitrary Python code, so a user can run anything: delete files, read secrets. Never use `eval` or `exec` on untrusted data. Use `int()`, `float()`, `json.loads()` or `ast.literal_eval()` for safe parsing.

Q5: How do you make code that uses input() testable?
A5: Do not call `input()` deep inside logic. Pass the reader function as a parameter (dependency injection), as in the `ask(..., reader=input)` example, or use `unittest.mock.patch("builtins.input", side_effect=[...])` in tests. Separating "get text" from "process text" makes the logic easy to test.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Small CLI scripts and learning programs
- Coding interviews and competitive programming (stdin input)
- Simple confirmations (`y/n`) in admin scripts

❌ Avoid when:
- Web servers and APIs (use request parameters/body)
- Secrets like passwords (use `getpass.getpass()` so text is hidden)
- Large inputs in speed-sensitive code (use `sys.stdin`)
- Rich CLIs (use `argparse`, `click` or `typer`)

---

## 📊 Visual Diagram
```
 keyboard ──► terminal ──► stdin buffer
                              │
                 input("Age: ")  (program blocked here)
                              │
                 reads until "\n", drops "\n"
                              │
                        returns str "25"
                              │
              int("25") ──► 25   ✔
              int("abc") ──► ValueError ✘ → ask again
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| stdin | Standard input stream | Standard input का रास्ता |
| prompt | Message shown before waiting | User को दिखाया जाने वाला message |
| blocking | Program stops until input arrives | Input आने तक program रुका रहता है |
| EOFError | No more input to read | Input खत्म हो गया |
| validation | Checking input is acceptable | Input की जाँच |
| type casting | Converting between types | Type बदलना |
| getpass | Read hidden input (passwords) | छुपा हुआ input |

---

## ⚡ 3-Line Summary
English: `input()` blocks, reads one line from stdin, and always returns a string. Convert with `int()`/`float()` and validate with try/except. Never use `eval(input())`, and handle `EOFError` in scripts.
Hindi: `input()` program रोकता है, stdin से एक line पढ़ता है और हमेशा string देता है। `int()`/`float()` से convert करो और try/except से validate करो। `eval(input())` कभी नहीं, और scripts में `EOFError` handle करो।

---

## ➡️ Next Topic
**024. Comments + Docstrings** — how to document code with `#` comments and triple-quoted docstrings, and how tools read them.
