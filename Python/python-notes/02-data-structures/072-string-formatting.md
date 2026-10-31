---

# 072. String Formatting
# हिंदी में: String Formatting (Strings में values डालना)

---

## 🔵 Simple Definition (English)
String formatting means putting values into a text template in a controlled way: padding, alignment, number precision, commas, percentages, dates. Python has three styles: f-strings (modern, best), `str.format()` (flexible) and `%` formatting (old). All use the same "format spec mini-language", like `:>10`, `:.2f`, `:,`.

## 🔵 सरल परिभाषा (Hindi)
String formatting का मतलब text template में values को control के साथ डालना: padding, alignment, number की precision, commas, percentage, dates। Python में तीन तरीके हैं: f-strings (modern, सबसे अच्छा), `str.format()` (flexible) और `%` formatting (पुराना)। सब एक ही "format spec mini-language" use करते हैं, जैसे `:>10`, `:.2f`, `:,`।

---

## 🔴 Problem it Solves
Joining strings with `+` needs manual `str()` conversion and is messy: `"Total: " + str(price) + " INR"`. Floats print as `3.3000000000000003`. Reports need aligned columns and thousand separators. Formatting gives clean, readable, correctly rounded output in one template.

## 🔴 यह क्यों बना? (Hindi)
`+` से strings जोड़ने में हाथ से `str()` करना पड़ता है और code गंदा होता है। Floats `3.3000000000000003` जैसे print होते हैं। Reports में aligned columns और हज़ार के separators चाहिए। Formatting साफ़, readable और सही rounded output एक template में देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → f"Hello {name}"           → Python evaluates {name} at runtime and inserts str(name)
Step 2 → f"{x:.2f}"                → after ':' comes the format spec -> 2 decimal places
Step 3 → f"{x:>10}"                → align right in width 10 (< left, ^ center, > right)
Step 4 → f"{n:,}"  f"{p:.1%}"      → thousands separator / percentage
Step 5 → "{} {}".format(a, b)      → same engine, values passed to .format() later (reusable template)
Step 6 → "%s is %d" % (name, age)  → old C-style, still seen in logging and legacy code
```

## 🟢 कैसे काम करता है? (Hindi)
```
f"Hello {name}" → {name} runtime पर evaluate होकर str बनता है
':' के बाद format spec: .2f = 2 decimal, >10 = width 10 में right align
,  = हज़ार separator;  .1% = percentage
.format() = template पहले, values बाद में
% = पुराना C-style
```

---

## 🟡 Real World Example
Razorpay invoice: `f"{item:<20}{qty:>5}{price:>12,.2f}"` prints aligned columns with comma-separated amounts. A FastAPI service logs `f"{method} {path} took {ms:.1f} ms"`. Notice that for logging you should use lazy `%` style: `logger.info("user %s logged in", user_id)` so the string is built only if the log level is enabled.

## 🟡 Real Example Hindi mein
Razorpay invoice में `f"{item:<20}{qty:>5}{price:>12,.2f}"` aligned columns और comma वाले amounts print करता है। FastAPI service log करती है `f"{method} {path} took {ms:.1f} ms"`। ध्यान दें: logging में lazy `%` style बेहतर है: `logger.info("user %s logged in", user_id)` ताकि string तभी बने जब log level enabled हो।

---

## 💻 Code Example — Basic
```python
# Basic: the three formatting styles and common specs
name: str = "Priya"                          # sample string
age: int = 25                                # sample int
price: float = 1234567.891                   # sample float

print(f"Name: {name}, Age: {age}")           # Output: Name: Priya, Age: 25
print("Name: {}, Age: {}".format(name, age)) # Output: Name: Priya, Age: 25
print("Name: %s, Age: %d" % (name, age))     # Output: Name: Priya, Age: 25

print(f"{price:.2f}")                        # Output: 1234567.89   (2 decimals)
print(f"{price:,.2f}")                       # Output: 1,234,567.89 (thousand separator)
print(f"{0.256:.1%}")                        # Output: 25.6%        (percentage)
print(f"{42:05d}")                           # Output: 00042        (zero padding)
print(f"{255:b} {255:x} {255:#X}")           # Output: 11111111 ff 0XFF  (binary, hex)
print(f"{1500000:.2e}")                      # Output: 1.50e+06     (scientific)

print(f"[{name:<10}]")                       # Output: [Priya     ]  (left)
print(f"[{name:>10}]")                       # Output: [     Priya]  (right)
print(f"[{name:^10}]")                       # Output: [  Priya   ]  (center)
print(f"[{name:*^11}]")                      # Output: [***Priya***] (fill with *)

print(f"{name=}")                            # Output: name='Priya'  (debug form, 3.8+)
print(f"{age + 5} {name.upper()}")           # Output: 30 PRIYA      (any expression)
print(f"{{literal braces}}")                 # Output: {literal braces}

print("{0} {1} {0}".format("a", "b"))        # Output: a b a   (positional reuse)
print("{city}".format(city="Pune"))          # Output: Pune    (named)
```

## 💻 Code Example — Advanced
```python
# Advanced: dynamic specs, tables, dates, repr/str and safe logging
from __future__ import annotations           # modern hints
from datetime import datetime                # for date formatting
from decimal import Decimal                  # exact money values
import logging                               # for lazy formatting demo

# 1. Dynamic width and precision inside the spec
width: int = 12                              # column width
prec: int = 3                                # decimals
value: float = 3.14159265                    # number to print
print(f"[{value:{width}.{prec}f}]")          # Output: [       3.142]

# 2. Aligned table (invoice style)
rows: list[tuple[str, int, float]] = [
    ("Keyboard", 2, 1500.5),
    ("Monitor", 1, 12999.0),
    ("USB Cable", 10, 99.99),
]
header: str = f"{'Item':<12}{'Qty':>5}{'Price':>12}"       # header line
print(header)                                # Output: Item          Qty       Price
print("-" * len(header))                     # Output: ---------------------------
total: float = 0.0                           # running total
for item, qty, unit in rows:                 # print each row
    line_total: float = qty * unit           # compute line total
    total += line_total                      # add to total
    print(f"{item:<12}{qty:>5}{line_total:>12,.2f}")
print(f"{'TOTAL':<17}{total:>12,.2f}")       # Output: TOTAL               16,999.90

# 3. Dates
moment = datetime(2025, 3, 7, 14, 5, 9)      # fixed date for stable output
print(f"{moment:%d-%b-%Y %H:%M}")            # Output: 07-Mar-2025 14:05
print(f"{moment:%Y-%m-%dT%H:%M:%S}")         # Output: 2025-03-07T14:05:09

# 4. Money: floats vs Decimal
print(f"{0.1 + 0.2}")                        # Output: 0.30000000000000004
print(f"{0.1 + 0.2:.2f}")                    # Output: 0.30 (display only; value is still inexact)
print(f"{Decimal('0.1') + Decimal('0.2')}")  # Output: 0.3  (exact, use for money)

# 5. !r, !s, !a conversions (repr vs str)
text: str = "hi\n"                           # string with newline
print(f"{text!s}|{text!r}")                  # Output: "hi", a newline, then |'hi\n'

# 6. Custom __format__ for your own class
class Money:
    """Tiny money class with its own format spec support."""
    def __init__(self, amount: float, currency: str = "INR") -> None:
        self.amount: float = amount          # numeric amount
        self.currency: str = currency        # currency code

    def __format__(self, spec: str) -> str:
        spec = spec or ",.2f"                # default spec
        return f"{self.currency} {format(self.amount, spec)}"   # reuse float formatting

print(f"{Money(1234.5)}")                    # Output: INR 1,234.50
print(f"{Money(1234.5):.0f}")                # Output: INR 1234 (1234.5 rounds half-to-even to 1234)

# 7. Errors: wrong spec for the type
try:                                         # str with a number-only spec
    print(f"{'abc':.2f}")                    # invalid for strings
except ValueError as err:                    # catch it
    print("Error:", err)                     # Output: Error: Unknown format code 'f' for object of type 'str'

# 8. Logging: use lazy % style so formatting happens only when needed
logging.basicConfig(level=logging.WARNING)   # INFO is disabled
log = logging.getLogger("demo")              # logger
log.info("user %s logged in", "priya")       # not formatted at all (level too low)
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
name, price = "Priya", 1234.5
print(f"Hi {name}, total {price:,.2f}")      # f-string with format spec
print(f"{name:>10}|{7:03d}")                 # pad and align
```

```javascript
// JavaScript
const name = "Priya", price = 1234.5;
console.log(`Hi ${name}, total ${price.toLocaleString("en-IN", {minimumFractionDigits: 2})}`);
console.log(name.padStart(10) + "|" + String(7).padStart(3, "0"));  // manual padding
console.log(price.toFixed(2));               // returns a string: "1234.50"
```

Key difference: JS template literals only insert values; formatting needs `toFixed`, `padStart`, `toLocaleString`. Python puts formatting inside the placeholder (`{x:,.2f}`). FastAPI link: f-strings build messages and log lines; for JSON money values return numbers (or Decimal) and let the client format, do not return pre-formatted strings from an API.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using quotes of the same type inside f-string (older Python)
```python
d = {"name": "Priya"}
# f"{d["name"]}"        # SyntaxError before Python 3.12
print(f"{d['name']}")   # Correct everywhere: use different quotes
```

❌ Mistake 2: Formatting user input as a template (security)
```python
# Wrong: user_text.format(secret=SECRET)   # attacker passes "{secret}" or "{obj.__class__}" and leaks data
# Correct: print(f"Hello {user_text}")      # user_text is only a VALUE, never the template
```

❌ Mistake 3: Using round-looking float output for money
```python
# f"{2.675:.2f}" gives 2.67 (binary float is 2.67499999...)
# Correct: use Decimal and quantize for money
```

---

## 🧠 Tricky Interview Question

**Q**: "What does `f'{0.1 + 0.2 == 0.3}'` print, and what do `f'{2.5:.0f}'` and `f'{3.5:.0f}'` print?"

**Answer**: The first prints `False`, because `0.1 + 0.2` is `0.30000000000000004` in binary floating point. The next two print `2` and `4`: format rounding uses round-half-to-even ("banker's rounding") on the exact binary value, so `2.5` goes to `2` and `3.5` goes to `4`. That surprises people expecting `3`. For money use `Decimal` with an explicit rounding mode such as `ROUND_HALF_UP`.

---

## ⚫ Interview Questions + Answers

Q1: Which formatting method is best and why?
A1: f-strings (3.6+). They are the most readable, evaluate expressions inline, and are the fastest because they compile to simple string-building bytecode. Use `.format()` when the template is stored separately (config, i18n) and filled later. Use `%` mostly in `logging` calls (lazy formatting) and when reading legacy code.

Q2: How do you format a float to 2 decimals with thousand separators?
A2: `f"{x:,.2f}"`. In `,.2f`: `,` adds separators, `.2` sets two decimal places, `f` means fixed-point. For Indian grouping (12,34,567) the standard format spec does not support it; use `locale` or the `babel` library.

Q3: What is the format spec mini-language order?
A3: `[[fill]align][sign][#][0][width][grouping][.precision][type]`. Example `*^+12,.2f`: fill `*`, align center, sign always, width 12, comma grouping, 2 decimals, fixed type. Dates use their own spec (`%Y-%m-%d`) through `datetime.__format__`.

Q4: What is `!r` and `{x=}` in an f-string?
A4: `!r` applies `repr()` instead of `str()`, great for debugging because it shows quotes and escape sequences. `{x=}` (3.8+) prints both the expression text and its repr, like `x=5`, which is a quick debugging aid. `!s` and `!a` are the `str` and `ascii` conversions.

Q5: Why use `logger.info("x=%s", x)` instead of an f-string in logging?
A5: With `%s` arguments, logging builds the message only if the record passes the level filter, so disabled log levels cost almost nothing. An f-string is built always, even if INFO is disabled. It also lets log systems group messages by template. In production hot paths this matters.

---

## 🔷 When to Use Which Style

✅ Use f-strings for:
- Almost all new code, messages, reports

✅ Use `.format()` for:
- Templates stored in variables or files, reused with different values

✅ Use `%` style for:
- `logging` calls and legacy code

❌ Avoid:
- `+` concatenation with many parts
- Formatting untrusted strings as templates
- Floats for money

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| f-string | Inline `f"..{expr}.."` formatting | String के अंदर expression वाला format |
| Format spec | Rules after `:` in a placeholder | `:` के बाद के नियम |
| Precision | Digits after decimal point | दशमलव के बाद के अंक |
| Alignment | `<` left, `^` center, `>` right | Text को किस तरफ रखना |
| Placeholder | `{}` slot for a value | Value की जगह `{}` |
| Lazy formatting | Build string only when needed | ज़रूरत पड़ने पर ही string बनाना |

---

## ⚡ 3-Line Summary
English: Use f-strings for formatting: `{x:.2f}`, `{x:,}`, `{x:>10}`, `{x:%Y-%m-%d}`. Use `.format()` for stored templates and `%` args for logging. Never format untrusted text as a template, and use `Decimal` (not float) for money.
Hindi: Formatting के लिए f-strings: `{x:.2f}`, `{x:,}`, `{x:>10}`, `{x:%Y-%m-%d}`। Stored templates के लिए `.format()` और logging में `%` args। Untrusted text को template की तरह format न करें, और पैसों के लिए float नहीं `Decimal` use करें।

---

## ➡️ Next Topic
**073. String Slicing and Indexing** — positive and negative indexes, slice steps, reversing and common slicing tricks.
