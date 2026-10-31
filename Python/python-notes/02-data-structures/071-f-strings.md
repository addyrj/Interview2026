---

# 071. f-strings — Complete Guide
# हिंदी में: f-strings — पूरी गाइड

---

## 🔵 Simple Definition (English)
An f-string is a string literal prefixed with `f` that evaluates expressions inside `{}` at runtime: `f"Hi {name}"`. It supports format specs like `{price:.2f}` and debugging with `{x=}`. It is the fastest and most readable formatting method (Python 3.6+).

## 🔵 सरल परिभाषा (Hindi)
f-string वह string है जिसके आगे `f` लगता है और `{}` के अंदर के expressions runtime पर evaluate होते हैं: `f"Hi {name}"`। इसमें `{price:.2f}` जैसे format specs और `{x=}` debugging भी चलती है। यह सबसे तेज़ और readable तरीका है (Python 3.6+)।

---

## 🔴 Problem it Solves
Before f-strings: `"Hi " + name + ", age " + str(age)` (ugly, needs `str()`), `"Hi %s" % name` (cryptic), `"Hi {}".format(name)` (verbose, values far from placeholders). f-strings keep the value right inside the text, so bugs like wrong argument order disappear.

## 🔴 यह क्यों बना? (Hindi)
पहले `+` से जोड़ना पड़ता था (`str()` चाहिए), `%s` cryptic था, `.format()` लंबा था और values placeholder से दूर रहती थीं। f-string में value सीधे text के अंदर होती है — argument order की गलतियाँ ख़त्म।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python parser sees f"..." prefix
Step 2 → Text is split into literal parts and {expression} parts
Step 3 → Each expression is compiled as normal Python code
Step 4 → At runtime: expression evaluated -> format(value, spec) called
Step 5 → Pieces are joined with BUILD_STRING (one fast operation)

Syntax inside braces:
  {expr}            plain value
  {expr!r}          repr()   (also !s, !a)
  {expr:spec}       format spec  e.g. :.2f  :>10  :,  :08.3f  :%
  {expr=}           prints "expr=value" (debug)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Parser को f"..." prefix दिखता है
Step 2 → Text literal parts और {expression} parts में बँटता है
Step 3 → हर expression normal Python code की तरह compile होता है
Step 4 → Runtime पर expression evaluate -> format(value, spec)
Step 5 → सब pieces एक साथ जुड़ जाते हैं (तेज़)
```

---

## 🟡 Real World Example
Razorpay receipt: `f"Paid ₹{amount:,.2f} to {merchant}"`. Logging: `logger.info(f"order={order_id} status={status}")`. AI prompt building: `f"Summarize this text:\n{doc}"`. Debugging: `print(f"{user_id=}")` shows `user_id=42`.

## 🟡 Real Example Hindi mein
Razorpay receipt: `f"Paid ₹{amount:,.2f} to {merchant}"`। AI prompt बनाना: `f"Summarize this text:\n{doc}"`। Debugging में `print(f"{user_id=}")` से `user_id=42` दिखता है।

---

## 💻 Code Example — Basic
```python
# f-string basics
name: str = "Priya"                              # a string
age: int = 25                                    # an int
price: float = 1234567.891                       # a float

print(f"Hi {name}, age {age}")                   # Hi Priya, age 25
print(f"Next year: {age + 1}")                   # Next year: 26  (expression)
print(f"Upper: {name.upper()}")                  # Upper: PRIYA   (method call)
print(f"{price:.2f}")                            # 1234567.89     2 decimals
print(f"{price:,.2f}")                           # 1,234,567.89   thousands separator
print(f"{age:05d}")                              # 00025          zero padded
print(f"{name:>10}|")                            #      Priya|    right align width 10
print(f"{name:<10}|")                            # Priya     |    left align
print(f"{name:^11}|")                            #    Priya   |   center
print(f"{name:*^11}")                            # ***Priya***    fill char
print(f"{0.256:.1%}")                            # 25.6%          percent
print(f"{255:b} {255:x} {255:#X}")               # 11111111 ff 0XFF
print(f"{name!r}")                               # 'Priya'        repr
print(f"{age=}")                                 # age=25         debug mode
print(f"{{literal braces}}")                     # {literal braces}

# multi-line f-string
msg: str = (
    f"Name: {name}\n"                            # line 1
    f"Age: {age}"                                # line 2
)
print(msg)                                       # Name: Priya / Age: 25
```

## 💻 Code Example — Advanced
```python
# Production-style f-string usage
from __future__ import annotations           # modern hints
from datetime import datetime                # dates in f-strings
from decimal import Decimal                  # exact money type
import logging                               # logging demo

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")  # simple log
logger = logging.getLogger("app")            # named logger


def receipt(merchant: str, amount: Decimal, paid_at: datetime) -> str:
    """Build an aligned receipt using nested format specs."""
    width: int = 12                                         # dynamic width
    lines = [
        f"{'Merchant':<{width}}: {merchant}",                # nested {width}
        f"{'Amount':<{width}}: ₹{amount:>10,.2f}",           # money format
        f"{'Date':<{width}}: {paid_at:%d %b %Y, %H:%M}",     # datetime spec
    ]
    return "\n".join(lines)                                 # join lines


def table(rows: list[tuple[str, float]]) -> str:
    out: list[str] = []                                     # collect lines
    for item, cost in rows:                                 # each row
        out.append(f"{item:<10}{cost:>8.2f}")               # aligned columns
    return "\n".join(out)                                   # final text


class User:
    def __init__(self, name: str) -> None:
        self.name = name                                    # store name

    def __format__(self, spec: str) -> str:                 # custom format hook
        return self.name.upper() if spec == "u" else self.name


if __name__ == "__main__":
    when = datetime(2024, 3, 9, 14, 5)                      # fixed date
    print(receipt("Swiggy", Decimal("1499.5"), when))
    # Merchant    : Swiggy
    # Amount      : ₹  1,499.50
    # Date        : 09 Mar 2024, 14:05
    print(table([("Dosa", 80), ("Coffee", 45.5)]))
    # Dosa         80.00
    # Coffee       45.50
    u = User("Priya")                                       # custom object
    print(f"{u} / {u:u}")                                   # Priya / PRIYA

    # Quote rules: reuse of same quotes allowed from Python 3.12
    d = {"k": 1}                                            # dict
    print(f"{d['k']}")                                      # 1  (different quotes: all versions)
    print(f"{d["k"]}")                                      # 1  (same quotes: 3.12+ only)

    # Logging: lazy %-style is preferred, f-string builds string even if level is off
    user_id = 42
    logger.info("user=%s logged in", user_id)               # lazy formatting
    logger.info(f"user={user_id} logged in")                # eager (always built)

    # Debug specifier with format
    x = 3.14159
    print(f"{x=:.2f}")                                      # x=3.14
    print(f"{x * 2 = }")                                    # x * 2 = 6.28318
```

---

## 🟠 JavaScript vs Python Comparison
JS template literals use backticks and `${}`. Python uses `f"..."` and `{}`. Python has built-in format specs (`:.2f`, `:,`); JS needs `toFixed()`, `toLocaleString()`.

```python
# Python way
name, price = "Tea", 12.5
print(f"{name}: ₹{price:.2f}")      # Tea: ₹12.50
print(f"{1_000_000:,}")             # 1,000,000
print(f"{price=}")                  # price=12.5
```
```javascript
// JavaScript way
const name = "Tea", price = 12.5;
console.log(`${name}: ₹${price.toFixed(2)}`);   // Tea: ₹12.50
console.log((1000000).toLocaleString());        // 1,000,000
// no equivalent of {price=}
```

---

## 🟠 FastAPI Connection
Use f-strings for error messages, dynamic response text, file names and prompts. NEVER use them to build SQL — that causes SQL injection; use parameters.

```python
from fastapi import FastAPI, HTTPException           # imports

app = FastAPI()                                      # app
ITEMS: dict[int, str] = {1: "Dosa"}                  # fake DB

@app.get("/items/{item_id}")
def get_item(item_id: int) -> dict[str, str]:
    if item_id not in ITEMS:                         # missing?
        raise HTTPException(404, f"Item {item_id} not found")   # f-string message
    return {"message": f"You ordered {ITEMS[item_id]}"}          # f-string response

# DANGEROUS:  db.execute(f"SELECT * FROM users WHERE id = {item_id}")
# SAFE:       db.execute("SELECT * FROM users WHERE id = :id", {"id": item_id})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting the `f` prefix
```python
# Wrong
name = "Priya"
print("Hi {name}")        # prints: Hi {name}
# Right
print(f"Hi {name}")       # Hi Priya
```

❌ Mistake 2: Using f-strings for SQL
```python
# Wrong
query = f"SELECT * FROM users WHERE name = '{name}'"   # SQL injection!
# Right
query = "SELECT * FROM users WHERE name = %s"          # parameterized
```

❌ Mistake 3: Backslash / same quotes inside braces on old Python
```python
# Wrong (before 3.12)
f"{'\n'.join(items)}"       # SyntaxError on 3.11 and older
# Right
sep = "\n"
f"{sep.join(items)}"
```

---

## 🧠 Tricky Interview Question

```python
x = 10
s = f"{x}"
x = 20
print(s)

funcs = [lambda: f"{i}" for i in range(3)]
print([f() for f in funcs])

width = 6
print(f"{'ab':>{width}}|")
```
Answer: `10` — an f-string is evaluated immediately, producing a plain string; later changes to `x` do not affect it. The lambdas give `['2', '2', '2']` because they look up `i` lazily at call time (late binding), and after the loop `i == 2`. Third prints `    ab|` (width from nested `{width}`).

---

## ⚫ Interview Questions + Answers

Q1: Why are f-strings faster than `.format()` and `%`?
A1: The expression parts are compiled into bytecode and joined with a single BUILD_STRING; there is no runtime parsing of a format string or method call overhead.

Q2: Are f-strings evaluated lazily?
A2: No. They are evaluated immediately where they appear. For templates evaluated later, use `str.format` or `string.Template`.

Q3: How do you print a literal `{`?
A3: Double it: `f"{{"` prints `{`.

Q4: What does `f"{x=}"` do?
A4: Prints the expression text, `=`, and the repr of the value: `x=25`. Great for quick debugging (3.8+).

Q5: Should you use f-strings in logging calls?
A5: Prefer `logger.info("user=%s", uid)`. The f-string is built even if the log level is disabled; lazy `%s` formatting skips the work. For structured logging, pass `extra=`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building messages, labels, prompts, file names
- You need number/date formatting inline

❌ Avoid when:
- Building SQL or shell commands (injection risk)
- Template is stored in a DB/config and filled later (use `.format` / `Template`)
- Hot logging calls with disabled levels

---

## 📊 Visual Diagram
```
 f"Total: {price * qty:>10,.2f} INR"
      │         │       │  │ │ └─ f = float, 2 decimals
      │         │       │  │ └─── , = thousands separator
      │         │       │  └───── 10 = width
      │         │       └──────── > = right align
      │         └──────────────── expression (evaluated now)
      └────────────────────────── literal text

 Result: "Total:   12,500.00 INR"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| f-string | String with embedded expressions | Expressions वाली string |
| Format spec | Rules after `:` like `.2f` | `:` के बाद formatting rules |
| Conversion flag | `!r`, `!s`, `!a` | repr/str/ascii में बदलना |
| Interpolation | Inserting values into text | Text में value डालना |
| SQL injection | Attack via unsafe query strings | Unsafe query से attack |
| Debug specifier | `{x=}` | `x=value` print करना |

---

## ⚡ 3-Line Summary
English: f-strings evaluate expressions inside `{}` immediately and support format specs. They are the fastest, cleanest formatting option. Never use them for SQL, and use lazy formatting for logging.
Hindi: f-string `{}` के expressions तुरंत evaluate करती है और format specs support करती है। सबसे तेज़ और साफ़ तरीका है। SQL में कभी use न करें, logging में lazy formatting बेहतर।

---

## ➡️ Next Topic
**072. String Formatting** — `%` and `.format()` styles, `Template`, and when each is still needed.
