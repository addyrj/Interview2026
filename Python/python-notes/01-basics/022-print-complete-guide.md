---

# 022. print() — Complete Guide
# हिंदी में: print() — पूरी गाइड

---

## 🔵 Simple Definition (English)
`print()` is Python's built-in function that sends text to the screen (standard output). It converts every value to a string, joins them with a separator, and adds a newline at the end. You can change the separator, the ending, and even the destination.

## 🔵 सरल परिभाषा (Hindi)
`print()` Python का built-in function है जो text को screen (standard output) पर भेजता है। यह हर value को string में बदलता है, `sep` से जोड़ता है और आखिर में `end` (default newline) जोड़ता है। Separator, ending और destination तीनों बदले जा सकते हैं।

---

## 🔴 Problem it Solves
Every program must talk to the outside world: show results, debug values, write logs. Without a simple output function you would need low-level OS calls. `print()` gives one friendly function: no type conversion by hand, no manual newline, works on any OS. It is also the first debugging tool every developer uses.

## 🔴 यह क्यों बना? (Hindi)
हर program को बाहर की दुनिया से बात करनी होती है: result दिखाना, debug करना, log लिखना। `print()` से हमें एक आसान function मिलता है: type conversion खुद नहीं करनी, newline खुद नहीं लगानी, हर OS पर चलता है। Debugging का पहला tool भी यही है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You call print(a, b, c, sep=" ", end="\n", file=sys.stdout, flush=False)
Step 2 → Each argument is converted with str(arg)  (calls __str__)
Step 3 → All strings are joined using `sep`
Step 4 → `end` is appended at the very last
Step 5 → Result is written to `file` (default: sys.stdout)
Step 6 → If flush=True, buffer is forced out immediately

print("a", "b", 1)  →  "a" + " " + "b" + " " + "1" + "\n"  →  screen
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → print(a, b, c) call होता है
Step 2 → हर argument पर str() लगता है
Step 3 → सब strings को sep (default space) से जोड़ा जाता है
Step 4 → आखिर में end (default "\n") जुड़ता है
Step 5 → Output file (default sys.stdout) में लिखा जाता है
Step 6 → flush=True हो तो buffer तुरंत खाली हो जाता है
```

---

## 🟡 Real World Example
Swiggy's backend worker processes an order and prints progress lines like `order=1042 status=ASSIGNED`. In a Docker container these lines go to stdout and the platform (Kubernetes, CloudWatch) collects them as logs. A progress bar in a data-import script uses `end="\r"` and `flush=True` to update the same line. In a FastAPI service, `print()` is fine for quick debugging, but production code uses the `logging` module (same idea, more control).

## 🟡 Real Example Hindi mein
Swiggy का backend worker order process करते समय `order=1042 status=ASSIGNED` जैसी lines print करता है। Docker container में ये lines stdout पर जाती हैं और Kubernetes/CloudWatch इन्हें logs की तरह collect करता है। Data-import script में progress bar के लिए `end="\r"` और `flush=True` से एक ही line बार-बार update होती है। FastAPI production में `logging` module use होता है।

---

## 💻 Code Example — Basic
```python
# print() basics — run directly with: python3 file.py

# Simple print: one value
print("Hello, Priya")                     # Output: Hello, Priya

# Many values: separated by a space by default
name: str = "Priya"                       # a string variable
age: int = 25                             # an int variable
print("Name:", name, "Age:", age)         # Output: Name: Priya Age: 25

# sep: change the separator between values
print("2025", "01", "15", sep="-")        # Output: 2025-01-15

# end: change what is printed at the end (default is newline)
print("Loading", end="...")               # no newline after this
print("done")                             # Output: Loading...done

# f-string: the most readable way to format output
salary: float = 75000.5                   # a float value
print(f"{name} earns {salary:,.2f}")      # Output: Priya earns 75,000.50

# Escape characters inside strings
print("Line1\nLine2")                     # \n makes a new line
print("Tab\there")                        # \t makes a tab space

# Printing with no arguments prints an empty line
print()                                   # Output: (blank line)

# Unpacking a list with * to print items separated by sep
items: list[str] = ["apple", "mango", "banana"]   # list of strings
print(*items, sep=", ")                   # Output: apple, mango, banana

# print returns None
result: None = print("check")             # prints "check"
print(result)                             # Output: None
```

## 💻 Code Example — Advanced
```python
# Advanced print(): file=, flush, stderr, custom __str__/__repr__, StringIO
import io                                  # for in-memory text buffer
import sys                                 # for stdout / stderr
from dataclasses import dataclass          # to build a small model


@dataclass
class Order:                               # a simple order model
    order_id: int                          # id of the order
    status: str                            # current status

    def __str__(self) -> str:              # used by print() and str()
        return f"Order #{self.order_id} [{self.status}]"

    # __repr__ is generated by @dataclass, used in lists and debugging


def log_info(message: str) -> None:        # normal logs go to stdout
    print(f"INFO  {message}", file=sys.stdout)


def log_error(message: str) -> None:       # errors go to stderr
    print(f"ERROR {message}", file=sys.stderr)


def render_table(rows: list[tuple[str, float]]) -> str:
    """Build a text table using print() into an in-memory buffer."""
    buffer: io.StringIO = io.StringIO()    # fake file that lives in memory
    print(f"{'Item':<10}{'Price':>10}", file=buffer)      # header, left/right aligned
    print("-" * 20, file=buffer)                           # separator line
    for item, price in rows:                               # loop over rows
        print(f"{item:<10}{price:>10.2f}", file=buffer)    # one formatted row
    return buffer.getvalue()               # get everything written so far


def main() -> None:
    order: Order = Order(1042, "ASSIGNED")  # create an order
    print(order)                            # Output: Order #1042 [ASSIGNED]
    print([order])                          # list uses __repr__
    # Output: [Order(order_id=1042, status='ASSIGNED')]

    log_info("worker started")              # Output: INFO  worker started
    log_error("this goes to stderr")        # shown on terminal, but NOT in stdout pipe

    table: str = render_table([("Pizza", 299.0), ("Coke", 60.5)])
    print(table, end="")                    # table already ends with newline
    # Output:
    # Item           Price
    # --------------------
    # Pizza         299.00
    # Coke           60.50

    # Progress style output: \r returns cursor to line start
    for pct in (25, 50, 100):               # three progress steps
        print(f"\rProgress: {pct}%", end="", flush=True)  # overwrite same line
    print()                                 # finally move to next line

    # Debug shortcut (Python 3.8+): = shows name and value
    total: int = 3 * 7                      # some value
    print(f"{total=}")                      # Output: total=21

    # repr vs str inside f-string
    text: str = "hi\n"                      # string with newline
    print(f"{text!r}")                      # Output: 'hi\n'


if __name__ == "__main__":
    main()                                  # run only when executed directly
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
name = "Priya"
print("Hello", name)                  # auto space between args, auto newline
print("a", "b", sep="-")              # a-b
print("no newline", end="")           # stays on same line
print(f"Total: {10 * 2}")             # f-string
print([1, 2, 3])                      # [1, 2, 3]
print({"a": 1})                       # {'a': 1}  (single quotes)
```
```javascript
// JavaScript
const name = "Priya";
console.log("Hello", name);           // auto space between args, auto newline
console.log(["a", "b"].join("-"));    // no sep option, use join
process.stdout.write("no newline");   // console.log always adds newline
console.log(`Total: ${10 * 2}`);      // template literal
console.log([1, 2, 3]);               // [ 1, 2, 3 ]
console.log({ a: 1 });                // { a: 1 }
```

Key differences: Python `print` has `sep`, `end`, `file`, `flush` built in. JS `console.log` has none of these, and has `console.error/warn` instead of `file=sys.stderr`. `print` is a normal function in Python 3 (it was a statement in Python 2), so parentheses are required.

---

## 🟠 FastAPI Connection
In FastAPI, `print()` shows up in the terminal where `uvicorn` runs. It is handy during development, but in production use `logging`, because logs need levels, timestamps and structured output. Remember: `print()` inside an endpoint is synchronous but very fast; heavy printing in a hot path can still slow down the service.

```python
# FastAPI example (needs: pip install fastapi)
import logging                                    # production logging module
from fastapi import FastAPI                       # the web framework

app: FastAPI = FastAPI()                          # create the app
logger: logging.Logger = logging.getLogger("api")  # named logger


@app.get("/orders/{order_id}")                    # GET /orders/10
async def get_order(order_id: int) -> dict[str, int]:
    print(f"DEBUG order_id={order_id}")           # quick debug (dev only)
    logger.info("fetching order %s", order_id)    # proper logging (production)
    return {"order_id": order_id}                 # FastAPI converts dict to JSON
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `+` to join a string and a number
```python
age: int = 25
# Wrong: TypeError: can only concatenate str (not "int") to str
# print("Age: " + age)

# Right: use commas or f-string
print("Age:", age)            # Output: Age: 25
print(f"Age: {age}")          # Output: Age: 25
```

❌ Mistake 2: Forgetting parentheses (Python 2 habit)
```python
# Wrong (SyntaxError in Python 3):
# print "hello"

# Right:
print("hello")
```

❌ Mistake 3: Expecting print() to give back the text
```python
# Wrong: x is None, not the text
x = print("hi")
print(x)                      # Output: None

# Right: build the string first, then print it
message: str = "hi"
print(message)
```

❌ Mistake 4: Output not appearing immediately (buffering)
```python
import time
# Wrong: with end="" and no flush the text may appear late when piped to a file/log
# print("working...", end="")
# time.sleep(2)

# Right: flush=True forces it out now
print("working...", end="", flush=True)
time.sleep(0.01)
print(" ok")
```

---

## 🧠 Tricky Interview Question

```python
print("a", "b", sep="")
print("c", end="")
print("d")
print(print("x"))
print(1, 2, 3, sep="\n", end="!\n")
```

**Answer:**
```
ab
cd
x
None
1
2
3!
```
Line 1: empty separator joins "a" and "b" as `ab`. Line 2 prints `c` with no newline, so Line 3 continues on the same line: `cd`. Line 4: the inner `print("x")` runs first, prints `x`, and returns `None`; the outer print then prints `None`. Line 5: `sep="\n"` puts each number on its own line and `end="!\n"` adds `!` after the last one.

---

## ⚫ Interview Questions + Answers

Q1: What does print() return?
A1: It always returns `None`. Its job is a side effect (writing to a stream), not producing a value. That is why `x = print("hi")` makes `x` equal to `None`.

Q2: What is the difference between `str()` and `repr()` in the context of print?
A2: `print(obj)` calls `str(obj)` which is for end users (readable). `repr(obj)` is for developers (unambiguous, ideally valid code). Containers like lists show items using `repr`, so `print(["a"])` shows `['a']` with quotes. Define `__str__` for friendly text and `__repr__` for debugging.

Q3: How do you print to stderr, and why?
A3: `print("msg", file=sys.stderr)`. stdout is for normal program output (which may be piped into another program), stderr is for errors and diagnostics. Keeping them separate lets `python app.py > out.txt` save only real output while errors still show on the terminal.

Q4: Why use `flush=True`?
A4: stdout is usually line-buffered on a terminal but fully buffered when redirected to a file or pipe (Docker logs, CI). Without flush, your text may appear late or be lost if the process crashes. `flush=True` forces the buffer out immediately. Useful for progress bars and containers. `python -u` or `PYTHONUNBUFFERED=1` does it globally.

Q5: print() vs logging, which one in production?
A5: `logging`. It has levels (DEBUG/INFO/ERROR), timestamps, handlers (file, JSON, cloud), and can be turned on or off by config without changing code. `print()` has no levels and is harder to filter. Use `print()` for scripts and quick debugging only.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Quick debugging while developing
- Small scripts, CLI tools, learning and practice
- Showing the final result of a command-line program
- Interview coding rounds

❌ Avoid when:
- Production services (use `logging`)
- You need log levels, timestamps or structured JSON logs
- Performance-critical loops (printing is slow)
- Writing real files (use `open()` / `pathlib`)

---

## 📊 Visual Diagram
```
print("a", "b", sep="-", end="!\n", file=sys.stdout)

   args ──► str() each ──► "a" , "b"
                              │
                         join with sep "-"
                              │
                           "a-b"
                              │
                        + end "!\n"
                              │
                         "a-b!\n"
                              │
            ┌─────────────────┴─────────────────┐
         file=sys.stdout                    file=sys.stderr
         (terminal / pipe)                  (error stream)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| stdout | Standard output stream | Normal output का रास्ता |
| stderr | Standard error stream | Error output का रास्ता |
| sep | Separator between arguments | Arguments के बीच का separator |
| end | Text added after the last argument | आखिर में जुड़ने वाला text |
| flush | Force buffer to be written now | Buffer तुरंत खाली करना |
| f-string | Formatted string literal `f"{x}"` | Formatted string |
| `__str__` | Readable text of an object | Object का readable text |
| `__repr__` | Developer text of an object | Object का developer text |

---

## ⚡ 3-Line Summary
English: `print()` converts values with `str()`, joins them with `sep`, adds `end`, and writes to `file` (stdout by default). It returns `None`. Use f-strings for formatting, `file=sys.stderr` for errors, and `logging` in production.
Hindi: `print()` values को `str()` से बदलता है, `sep` से जोड़ता है, `end` लगाता है और `file` (default stdout) में लिखता है। यह `None` return करता है। Formatting के लिए f-string, errors के लिए stderr, production में `logging`।

---

## ➡️ Next Topic
**023. input() Function** — how to read user input, why it always returns a string, and how to validate it safely.
