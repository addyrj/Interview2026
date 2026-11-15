---

# 194. re Module (Regular Expressions)
# हिंदी में: re Module (pattern से text खोजना और बदलना)

---

## 🔵 Simple Definition (English)
`re` lets you describe a text pattern (like "5 letters, 4 digits, 1 letter") and then search, match, extract, split or replace text that fits that pattern. A pattern is written in a mini language of symbols such as `\d`, `+`, `[a-z]`, `( )`.

## 🔵 सरल परिभाषा (Hindi)
`re` आपको text का pattern बताने देता है (जैसे "5 अक्षर, 4 अंक, 1 अक्षर") और फिर उस pattern से मिलते text को खोजना, match करना, निकालना, बाँटना या बदलना सिखाता है। Pattern एक छोटी भाषा में लिखा जाता है, जिसमें `\d`, `+`, `[a-z]`, `( )` जैसे symbols होते हैं।

---

## 🔴 Problem it Solves
Plain string methods (`in`, `split`, `replace`, `startswith`) only handle fixed text. Checking "is this a valid PAN, phone or email?" or "extract all order ids from 10,000 log lines" would need long loops and many `if` checks. One regex does it in one line, and it is the same idea in almost every language.

## 🔴 यह क्यों बना? (Hindi)
सामान्य string methods (`in`, `split`, `replace`, `startswith`) सिर्फ fixed text संभालते हैं। "यह valid PAN, phone या email है?" या "10,000 log lines से सारे order ids निकालो" के लिए लंबे loops और कई `if` लगते। एक regex यह एक line में कर देता है, और यही idea लगभग हर भाषा में है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a pattern as a raw string: r"\d{4}-\d{2}"
Step 2 → re.compile(pattern) builds a matcher (re caches recent patterns too)
Step 3 → Choose the function:
         match = from the start, fullmatch = whole string, search = anywhere,
         findall = all matches, finditer = all match objects, sub = replace, split
Step 4 → The engine tries each start position and backtracks on failure
Step 5 → A Match object gives group(), groups(), groupdict(), span()
Step 6 → No match → None (always check before .group())
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Pattern को raw string में लिखें: r"\d{4}-\d{2}"
Step 2 → re.compile(pattern) एक matcher बनाता है (re हाल के patterns cache भी करता है)
Step 3 → Function चुनें:
         match = शुरुआत से, fullmatch = पूरी string, search = कहीं भी,
         findall = सारे matches, finditer = सारे match objects, sub = बदलना, split
Step 4 → Engine हर शुरुआती position आज़माता है और fail होने पर backtrack करता है
Step 5 → Match object से group(), groups(), groupdict(), span() मिलते हैं
Step 6 → Match न मिले तो None (.group() से पहले हमेशा जाँचें)
```

---

## 🟡 Real World Example
A Razorpay KYC step validates PAN (`^[A-Z]{5}\d{4}[A-Z]$`), IFSC and phone numbers before calling the bank API. A log analysis script pulls IP, method, path and status from nginx lines. An AI app strips PII (emails, phone numbers) from text with `re.sub` before sending it to an LLM.

## 🟡 Real Example Hindi mein
Razorpay का KYC step bank API बुलाने से पहले PAN (`^[A-Z]{5}\d{4}[A-Z]$`), IFSC और phone numbers validate करता है। Log analysis script nginx lines से IP, method, path और status निकालती है। AI app LLM को text भेजने से पहले `re.sub` से PII (emails, phone numbers) हटा देती है।

---

## 💻 Code Example — Basic
```python
# Basic re examples - every line commented
import re  # regular expressions

text: str = "Order #123 by asha@example.com on 2025-11-10, total Rs. 1,499.50"  # sample text

print(re.search(r"\d+", text).group())  # first number anywhere -> '123'
print(re.match(r"Order", text) is not None)  # match checks ONLY the start -> True
print(re.match(r"by", text))  # not at the start -> None
print(re.fullmatch(r"\d{4}-\d{2}-\d{2}", "2025-11-10") is not None)  # whole string must fit
print(re.findall(r"\d+", text))  # all numbers as a list of strings
print(re.findall(r"(\d{4})-(\d{2})-(\d{2})", text))  # groups -> list of tuples

m = re.search(r"(?P<user>\w+)@(?P<domain>[\w.]+)", text)  # named groups
print(m.group("user"), m.group("domain"), m.span())  # asha example.com (start, end)
print(m.groupdict())  # {'user': 'asha', 'domain': 'example.com'}

print(re.sub(r"\d", "#", "OTP 4821"))  # replace every digit
print(re.sub(r"(\w+)@(\w+)", r"\2 at \1", "asha@site"))  # backreferences in replacement
print(re.split(r"[,;]\s*", "a, b;c,   d"))  # split on several separators

for mt in re.finditer(r"\d+", "a1 b22 c333"):  # iterate match objects
    print(mt.group(), mt.start())  # value and position

pat = re.compile(r"^[A-Z]{5}\d{4}[A-Z]$")  # compile once (PAN card shape)
print(bool(pat.match("ABCDE1234F")), bool(pat.match("abcde1234f")))  # True False
print(bool(re.match(r"hello", "HELLO", re.IGNORECASE)))  # flag: ignore case
print(re.escape("a.b*c"))  # make special characters literal
```

Output (verified by running; ids/timestamps/paths may vary):
```
123
True
None
True
['123', '2025', '11', '10', '1', '499', '50']
[('2025', '11', '10')]
asha example.com (14, 30)
{'user': 'asha', 'domain': 'example.com'}
OTP ####
site at asha
['a', 'b', 'c', 'd']
1 1
22 4
333 8
True False
True
a\.b\*c
```

## 💻 Code Example — Advanced
```python
# Production style: verbose patterns, lookarounds, greedy vs lazy, ReDoS, tokenizer, safe usage
import re  # regular expressions
import time  # to show catastrophic backtracking
from typing import Dict, Iterator, List, NamedTuple, Optional  # type hints

# 1. Verbose pattern: readable, commented regex for Indian mobile numbers
PHONE = re.compile(
    r"""
    ^(?:\+91[\s-]?|0)?     # optional +91 or 0 prefix
    ([6-9]\d{9})$          # 10 digits starting with 6-9
    """,
    re.VERBOSE,
)


def normalise_phone(raw: str) -> Optional[str]:
    """Return a 10 digit number or None."""
    m = PHONE.match(raw.strip())  # try to match
    return m.group(1) if m else None  # captured digits


print([normalise_phone(x) for x in ["+919876543210", "09876543210", "98765 43210", "12345"]])
print(normalise_phone("+91 9876543210"), normalise_phone("+91-9876543210"))

# 2. Greedy vs lazy
html: str = "<b>bold</b> and <i>italic</i>"  # sample
print(re.findall(r"<.+>", html))  # greedy: one huge match
print(re.findall(r"<.+?>", html))  # lazy: smallest matches
print(re.findall(r"<(\w+)>", html))  # capture only tag names

# 3. Lookarounds: match without consuming
prices: str = "Rs.100 $200 Rs.300"  # sample
print(re.findall(r"(?<=Rs\.)\d+", prices))  # numbers preceded by Rs.
print(re.findall(r"(?<!\d)\d{2}(?!\d)", "5 10 abc 123"))  # exactly 2 digits, not part of a longer number
print(re.sub(r"(?<=\d)(?=(\d{3})+$)", ",", "1234567"))  # thousands separators 1,234,567

# 4. Tokenizer with named groups and lastgroup
class Token(NamedTuple):
    kind: str  # token type
    value: str  # text

TOKEN_RE = re.compile(r"(?P<NUM>\d+(?:\.\d+)?)|(?P<OP>[+\-*/])|(?P<WS>\s+)|(?P<BAD>.)")


def tokenize(expr: str) -> Iterator[Token]:
    for m in TOKEN_RE.finditer(expr):  # scan left to right
        kind = m.lastgroup or "BAD"  # which group matched
        if kind == "WS":  # skip spaces
            continue
        if kind == "BAD":  # unexpected character
            raise SyntaxError(f"bad char {m.group()!r} at {m.start()}")
        yield Token(kind, m.group())  # emit token


print(list(tokenize("3.5 + 12*4")))
try:  # invalid input
    list(tokenize("3 $ 4"))
except SyntaxError as exc:
    print("SyntaxError:", exc)

# 5. Parse log lines into dicts
LOG = re.compile(r"^(?P<ip>\d{1,3}(?:\.\d{1,3}){3}) .* \"(?P<method>[A-Z]+) (?P<path>\S+) HTTP/[\d.]+\" (?P<status>\d{3})$")
line: str = '10.0.0.7 - - [10/Nov/2025] "GET /api/users?id=5 HTTP/1.1" 404'
rec: Dict[str, str] = LOG.match(line).groupdict()  # type: ignore[union-attr]
print(rec)

# 6. sub with a function
print(re.sub(r"\d+", lambda m: str(int(m.group()) * 2), "2 apples, 10 pears"))

# 7. ReDoS: nested quantifiers explode on a non-matching input
bad = re.compile(r"^(a+)+$")  # catastrophic pattern
t0 = time.perf_counter()  # start timer
bad.match("a" * 22 + "!")  # fails only after trying ~2^22 ways
slow = time.perf_counter() - t0  # duration
good = re.compile(r"^a+$")  # equivalent safe pattern
t1 = time.perf_counter()  # start timer
good.match("a" * 22 + "!")  # fails instantly
fast = time.perf_counter() - t1  # duration
print("bad is slower by >100x:", slow > fast * 100)  # True (shape of the problem, not exact numbers)
```

Output (verified by running; ids/timestamps/paths may vary):
```
['9876543210', '9876543210', None, None]
9876543210 9876543210
['<b>bold</b> and <i>italic</i>']
['<b>', '</b>', '<i>', '</i>']
['b', 'i']
['100', '300']
['10']
1,234,567
[Token(kind='NUM', value='3.5'), Token(kind='OP', value='+'), Token(kind='NUM', value='12'), Token(kind='OP', value='*'), Token(kind='NUM', value='4')]
SyntaxError: bad char '$' at 2
{'ip': '10.0.0.7', 'method': 'GET', 'path': '/api/users?id=5', 'status': '404'}
4 apples, 20 pears
bad is slower by >100x: True
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import re
m = re.search(r"(?P<y>\d{4})-(?P<m>\d{2})", "on 2025-11-10")
print(m.group("y"), m["m"])                     # 2025 11
print(re.findall(r"\d+", "a1 b22"))             # ['1', '22']
print(re.sub(r"\s+", " ", "a   b"))             # 'a b'
```

```javascript
// JavaScript
const m = /(?<y>\d{4})-(?<m>\d{2})/.exec("on 2025-11-10");
console.log(m.groups.y, m.groups.m);                    // 2025 11
console.log("a1 b22".match(/\d+/g));                    // ['1', '22']
console.log("a   b".replace(/\s+/g, " "));              // 'a b'
```

Key differences: Python patterns are plain strings (use `r"..."` raw strings), JavaScript has `/.../flags` literals. Named groups are `(?P<name>...)` in Python (Python 3 `re` does not accept `(?<name>...)` for groups) and `(?<name>...)` in JS. JS needs the `g` flag for all matches; Python has `findall` / `finditer`. Python has `match` (start only) and `fullmatch`; JS does not.

---

## 🟠 FastAPI Connection
FastAPI can validate path/query parameters with `pattern=` (Pydantic v2; it was `regex=` in old versions) and Pydantic validators can call `re.fullmatch`. Compile patterns once at module level. Do not use regex to "sanitise" SQL or HTML; use parameterised queries and templating escapes.

```python
# FastAPI: validate with regex in Path/Query and in Pydantic (pip install fastapi httpx)
import re  # regular expressions
from typing import Dict  # type hints
from fastapi import FastAPI, Path, Query  # parameter validation
from pydantic import BaseModel, field_validator  # model validation

app: FastAPI = FastAPI()  # create app


@app.get("/pan/{pan}")  # GET /pan/ABCDE1234F
def pan(pan: str = Path(pattern=r"^[A-Z]{5}\d{4}[A-Z]$")) -> Dict[str, str]:
    return {"pan": pan}  # only valid shapes arrive here


@app.get("/search")  # GET /search?q=abc
def search(q: str = Query(min_length=2, max_length=20, pattern=r"^[\w\s-]+$")) -> Dict[str, str]:
    return {"q": q}  # safe characters only


class Signup(BaseModel):
    username: str  # raw input

    @field_validator("username")  # custom check
    @classmethod
    def check(cls, v: str) -> str:
        if not re.fullmatch(r"[a-z][a-z0-9_]{2,15}", v):  # fullmatch = whole string
            raise ValueError("3-16 chars, start with a letter, a-z 0-9 _ only")  # message
        return v  # accepted


@app.post("/signup")  # POST /signup
def signup(s: Signup) -> Signup:
    return s  # echo
```

Output (verified by running; ids/timestamps/paths may vary):
```
200 422
200 422
200 422
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting raw strings
```python
# Wrong - "\b" is a backspace character in a normal string
# re.findall("\bword\b", text)

# Correct
# re.findall(r"\bword\b", text)
```

❌ Mistake 2: `match` when you meant `search` (and unchecked `None`)
```python
# Wrong - match only checks the start; None.group() raises AttributeError
# re.match(r"\d+", "id 42").group()

# Correct
m = re.search(r"\d+", "id 42")
print(m.group() if m else "no match")     # 42
```

❌ Mistake 3: Validating with `$` and nested quantifiers
```python
# Wrong - $ also matches before a trailing newline; (a+)+ can hang (ReDoS)
# re.match(r"^\d+$", "123\n")          # matches!
# re.match(r"^(a+)+$", "aaaa...!")     # catastrophic backtracking

# Correct
# re.fullmatch(r"\d+", user_input)     # whole string, strict
# use simple, non-nested patterns; limit input length
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import re
print(re.match(r"a", "ba"), re.search(r"a", "ba").span())
print(re.findall(r"a*", "baac"))
print(re.findall(r"(a)(b)?", "ab a"))
print(bool(re.match(r"^\d+$", "123\n")), bool(re.fullmatch(r"\d+", "123\n")))
print(re.split(r"(,)", "a,b"), re.split(r",", "a,b,", maxsplit=1))
print(bool(re.match(r"\d", "٣")), bool(re.match(r"\d", "٣", re.ASCII)))
```

**Answer**:
```
None (1, 2)
['', 'aa', '', '']
[('a', 'b'), ('a', '')]
True False
['a', ',', 'b'] ['a', 'b,']
True False
```
`match` checks only position 0, so it fails on `"ba"`. `a*` can match empty text, so `findall` returns empty matches at `b`, between `aa` and `c`, and at the end. An unmatched optional group gives an empty string `''` in `findall`. `$` accepts a trailing newline but `fullmatch` does not. A group in `split` is kept in the result. `\d` matches any Unicode digit (such as the Arabic-Indic `٣`, or Devanagari digits) unless you use `re.ASCII`. (Verified by running.)

---

## ⚫ Interview Questions + Answers

Q1: `match` vs `search` vs `fullmatch`?
A1: `match` anchors at the start, `search` finds the first match anywhere, `fullmatch` requires the whole string to match. For validation prefer `fullmatch`.

Q2: Greedy vs lazy quantifiers?
A2: `*`, `+`, `?` are greedy: they take as much as possible. Adding `?` (`*?`, `+?`) makes them lazy: as little as possible. `<.+>` on `<b>x</b>` matches everything; `<.+?>` matches `<b>`.

Q3: What is catastrophic backtracking (ReDoS)?
A3: Patterns with nested or overlapping quantifiers like `(a+)+$` try an exponential number of ways on a failing input, freezing the CPU. Avoid nested quantifiers, bound the input length, and for untrusted patterns use a linear-time engine (like `re2`).

Q4: Why compile a pattern?
A4: `re.compile` parses the pattern once. `re` also keeps an internal cache, so the speed gain is small, but a compiled, named pattern is clearer and reusable.

Q5: How do I get named groups and use them in replacement?
A5: `(?P<name>...)`, read with `m.group("name")` or `m.groupdict()`, and use `\g<name>` in `re.sub` replacement strings.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Validating simple formats (PAN, pincode, phone)
- Extracting fields from logs or semi-structured text
- Cleaning text (whitespace, PII masking)

❌ Avoid when:
- Parsing HTML/XML/JSON (use a real parser)
- Plain substring checks (`in`, `startswith`, `str.replace` are faster and clearer)
- Validating complex standards like full email RFC (use a library) or user-supplied patterns (ReDoS risk)

---

## 📊 Visual Diagram

```
pattern  r"(?P<user>\w+)@(?P<domain>[\w.]+)"
text     "Order by asha@example.com on ..."
                    └─┬─┘ └───┬─────┘
                    user    domain      m.groupdict()

 match      ▶|abc.....        only at the start
 search     ...|abc...        first hit anywhere
 fullmatch  ▶|abc|◀           the whole string
 findall    ..abc..abc..      every hit, as a list
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pattern | The regex description | खोजने का नमूना |
| Group | Part in `( )` that you can capture | `( )` में पकड़ा गया हिस्सा |
| Greedy | Takes as much as possible | ज़्यादा से ज़्यादा लेना |
| Lazy | Takes as little as possible | कम से कम लेना |
| Lookahead / Lookbehind | Check around without consuming | आसपास देखना, खाए बिना |
| Backtracking | Engine tries other paths after failing | fail होने पर दूसरा रास्ता आज़माना |
| ReDoS | Regex denial-of-service attack | regex से सेवा ठप करना |

---

## ⚡ 3-Line Summary
English: Write patterns as raw strings, use `fullmatch` to validate and `search` / `findall` to extract. Use named groups for clarity and avoid nested quantifiers (ReDoS). Do not parse HTML or JSON with regex.
Hindi: Patterns raw strings में लिखें, validate के लिए `fullmatch` और निकालने के लिए `search` / `findall` लें। Clarity के लिए named groups रखें और nested quantifiers (ReDoS) से बचें। HTML या JSON को regex से parse न करें।

---

## ➡️ Next Topic
**195. math Module** — numbers: square roots, rounding, logs, trigonometry and exact integer math.
