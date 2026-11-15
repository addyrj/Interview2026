---

# Q243. Advanced f-strings
# Category: Pythonic + Modern Python Features
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show advanced f-string features: format specs (width, precision, thousands, percent), alignment, `!r`, the `=` debug specifier, nested fields, datetime formatting and (3.12+) reusing quotes inside the expression.

---

## 💡 Quick Concept (2 lines only)
`f"{value:spec}"` — the part after `:` is the format spec; `!r` calls `repr()`; `{x=}` prints `x=value` for debugging. Since Python 3.12 f-strings can reuse the same quote type inside.
हिंदी: `{value:spec}` में spec से format तय होता है — `{x=}` debugging के लिए name और value दोनों दिखाता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from datetime import datetime                        # for date formatting

pi = 3.14159265                                      # float sample
n = 1234567                                          # int sample
name = "Ana"                                         # string sample

print(f"{pi:.2f}")                                   # Expected: 3.14        (2 decimals)
print(f"{n:,}")                                      # Expected: 1,234,567   (thousands sep)
print(f"{0.256:.1%}")                                # Expected: 25.6%       (percent)
print(f"{n:_}")                                      # Expected: 1_234_567   (underscore sep)
print(f"[{name:>6}]")                                # Expected: [   Ana]    (right-align, width 6)
print(f"[{name:<6}]")                                # Expected: [Ana   ]    (left-align)
print(f"[{name:^7}]")                                # Expected: [  Ana  ]   (center)
print(f"[{name:*^9}]")                               # Expected: [***Ana***] (fill char)
print(f"{255:#x} {255:08b} {255:o}")                 # Expected: 0xff 11111111 377
print(f"{name!r}")                                   # Expected: 'Ana'       (repr)
x = 42                                               # variable for debug demo
print(f"{x=} {x * 2=}")                              # Expected: x=42 x * 2=84

width, prec = 10, 3                                  # nested field values
print(f"[{pi:{width}.{prec}f}]")                     # Expected: [     3.142] (spec itself uses fields)

dt = datetime(2026, 11, 12, 9, 5)                    # fixed date for stable output
print(f"{dt:%Y-%m-%d %H:%M}")                        # Expected: 2026-11-12 09:05

# ============================================
# TEST CASES
# ============================================
d = {"k": "v"}                                       # dict sample
print(f"{d["k"]}")                                   # Expected: v  (3.12+: same quotes allowed)
print(f"{'yes' if x > 40 else 'no'}")                # Expected: yes (any expression works)
print(f"{{literal}} {x}")                            # Expected: {literal} 42 (double braces escape)
```

---

## 🔍 Why This Works (3 lines max)
The spec mini-language is `[[fill]align][sign][#][0][width][,|_][.precision][type]`. f-strings are evaluated at runtime and call `format(value, spec)`. Python 3.12 (PEP 701) lets you reuse quotes, nest f-strings and span lines inside `{}`.
हिंदी: spec = fill, align, width, `,`, `.precision`, type — Python 3.12 से अंदर वही quotes भी चल जाते हैं।

---

## ⚡ Alternative Solution
```python
# Same result with str.format and % (older styles) — f-string is shortest
pi = 3.14159265                                      # float sample
print("{:.2f}".format(pi))                           # Expected: 3.14
print("%.2f" % pi)                                   # Expected: 3.14
print(format(pi, ".2f"))                             # Expected: 3.14
print(f"{pi:.2f}")                                   # Expected: 3.14

# Table alignment — common real-world use
for item, price in [("pen", 2.5), ("notebook", 40)]: # sample rows
    print(f"{item:<10}|{price:>8.2f}")               # Expected: pen       |    2.50  then  notebook  |   40.00
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: f-string with logging -> formats even if the log level is disabled
# logging.debug(f"user={user}")        # string built always (wasted work)

# ❌ Wrong: forgetting the f prefix
name = "Ana"                                         # sample
print("Hello {name}")                                # Expected: Hello {name}  (plain string!)

# ✅ Correct
print(f"Hello {name}")                               # Expected: Hello Ana
# logging.debug("user=%s", user)       # lazy formatting for logs
```

---

## 🎯 Interview Tip (1 line)
Say: "I use `{x=}` for quick debugging, `{n:,}` / `{p:.1%}` for reports, and keep `%s` lazy formatting for `logging`."

---

## 🔗 Related Questions
→ Q035 (__repr__ vs __str__) | Q257 (string method tricks) | Q241 (comprehensions) | Q244 (walrus operator)
