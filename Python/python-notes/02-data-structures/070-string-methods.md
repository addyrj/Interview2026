---

# 070. String Methods (split, join, strip, replace, find, format, encode)
# हिंदी में: String Methods — रोज़ के काम के tools

---

## 🔵 Simple Definition (English)
String methods are built-in functions attached to every `str` object (like `s.split()` or `s.strip()`). Because strings are immutable, each method returns a NEW value and leaves the original unchanged.

## 🔵 सरल परिभाषा (Hindi)
String methods हर `str` object के साथ आने वाले built-in functions हैं (जैसे `s.split()`, `s.strip()`)। String immutable है, इसलिए हर method नई value return करता है और original नहीं बदलता।

---

## 🔴 Problem it Solves
User input is messy: extra spaces, wrong case, CSV lines, URLs, mixed encodings. Without methods, you would write manual loops over characters. Methods are implemented in C, so they are shorter, safer, and much faster than hand-written loops.

## 🔴 यह क्यों बना? (Hindi)
User input गंदा होता है: extra spaces, गलत case, CSV lines, URLs, encodings। Methods के बिना हमें characters पर manual loops लिखने पड़ते। Methods C में बने हैं — छोटे, safe और तेज़।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You call method on a string: "  a,b  ".strip()
Step 2 → CPython scans the underlying character array (in C)
Step 3 → A NEW str (or list / int / bool / bytes) is built
Step 4 → It is returned; the original string is untouched
Step 5 → Chain calls left-to-right: s.strip().lower().split(",")

Groups:
  Split/Join : split, rsplit, splitlines, partition, join
  Clean      : strip, lstrip, rstrip, removeprefix, removesuffix
  Search     : find, rfind, index, count, startswith, endswith, in
  Change     : replace, upper, lower, title, capitalize, swapcase
  Check      : isdigit, isalpha, isalnum, isspace, isupper
  Convert    : format, encode, zfill, center, ljust, rjust
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → String पर method call: "  a,b  ".strip()
Step 2 → CPython C में character array scan करता है
Step 3 → NEW str (या list / int / bool / bytes) बनता है
Step 4 → वह return होता है; original वैसा ही रहता है
Step 5 → Chaining बाएँ से दाएँ: s.strip().lower().split(",")
```

---

## 🟡 Real World Example
Swiggy: an address line `" 12, MG Road , Pune "` is cleaned with `strip` and `split(",")` into parts. Razorpay webhook: `signature.encode()` converts text to bytes for HMAC. A log parser: `line.partition(" - ")` splits timestamp and message. An AI app: `prompt.replace("{name}", user)` fills a template.

## 🟡 Real Example Hindi mein
Swiggy में address `" 12, MG Road , Pune "` को `strip` और `split(",")` से साफ़ parts में बाँटते हैं। Razorpay webhook में signature के लिए `.encode()` से text को bytes बनाते हैं। Log parser में `partition(" - ")` से timestamp और message अलग करते हैं।

---

## 💻 Code Example — Basic
```python
# Most-used string methods
raw: str = "  Hello, World  "            # messy input

print(raw.strip())                       # 'Hello, World'   remove edge spaces
print(raw.lstrip(), "|")                 # 'Hello, World  ' |  left only
print(raw.rstrip(), "|")                 # '  Hello, World' |  right only

text: str = raw.strip()                  # cleaned text
print(text.lower())                      # hello, world
print(text.upper())                      # HELLO, WORLD
print(text.replace("World", "Python"))   # Hello, Python
print(text.split(", "))                  # ['Hello', 'World']
print("-".join(["a", "b", "c"]))         # a-b-c

# Searching
print(text.find("World"))                # 7    index of first match
print(text.find("xyz"))                  # -1   not found (no error)
try:
    text.index("xyz")                    # index() raises instead
except ValueError as e:
    print("Error:", e)                   # Error: substring not found
print(text.count("l"))                   # 3
print(text.startswith("Hello"))          # True
print(text.endswith(("!", "d")))         # True  (tuple of options)

# Checks
print("123".isdigit(), "abc".isalpha())  # True True
print("ab12".isalnum(), " ".isspace())   # True True

# Padding and formatting
print("7".zfill(3))                      # 007
print("hi".center(6, "*"))               # **hi**
print("{} is {}".format("Sky", "blue"))  # Sky is blue

# encode / decode
b: bytes = "Hi".encode("utf-8")          # str -> bytes
print(b, b.decode("utf-8"))              # b'Hi' Hi
```

## 💻 Code Example — Advanced
```python
# Production-style text parsing with methods
from __future__ import annotations         # modern hints
from dataclasses import dataclass          # simple record


@dataclass
class LogEntry:
    level: str                             # INFO / ERROR
    user: str                              # user name
    message: str                           # rest of line


def parse_log(line: str) -> LogEntry:
    """Parse: '2024-01-05 | ERROR | priya | Payment failed: code=51'"""
    parts = [p.strip() for p in line.split("|", maxsplit=3)]   # split + clean
    if len(parts) != 4:                                        # validate shape
        raise ValueError(f"Bad log line: {line!r}")            # !r shows quotes
    _, level, user, message = parts                            # unpack
    return LogEntry(level.upper(), user.lower(), message)      # build record


def parse_query(qs: str) -> dict[str, str]:
    """'a=1&b=two&c=' -> {'a': '1', 'b': 'two', 'c': ''}"""
    result: dict[str, str] = {}                                # output dict
    for pair in qs.split("&"):                                 # each pair
        if not pair:                                           # skip empty
            continue
        key, _, value = pair.partition("=")                    # safe split
        result[key] = value                                    # store
    return result


def slugify(title: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else " " for ch in title)   # symbols->space
    return "-".join(cleaned.lower().split())                          # collapse spaces


if __name__ == "__main__":
    entry = parse_log("2024-01-05 | ERROR | Priya | Payment failed: code=51")
    print(entry)                               # LogEntry(level='ERROR', user='priya', message='Payment failed: code=51')
    print(parse_query("a=1&b=two&c="))         # {'a': '1', 'b': 'two', 'c': ''}
    print(slugify("  Hello, World! 2024  "))   # hello-world-2024

    # splitlines handles all newline types
    print("a\nb\r\nc".splitlines())            # ['a', 'b', 'c']

    # rsplit: split from the right
    print("a.b.c".rsplit(".", 1))              # ['a.b', 'c']

    # removeprefix / removesuffix (3.9+)
    print("test_user.py".removesuffix(".py"))  # test_user
    print("Bearer abc123".removeprefix("Bearer "))  # abc123

    # translate: fast multi-character replace
    table = str.maketrans({"a": "4", "e": "3"})      # mapping table
    print("leet speak".translate(table))             # l33t sp34k

    # strip() removes a SET of chars, not a substring
    print("xxhixx".strip("x"))                       # hi
    print("abcba".strip("ab"))                       # c
```

---

## 🟠 JavaScript vs Python Comparison

| Task | Python | JavaScript |
|------|--------|-----------|
| trim | `s.strip()` | `s.trim()` |
| split | `s.split(",")` | `s.split(",")` |
| join | `",".join(lst)` | `arr.join(",")` |
| contains | `"a" in s` | `s.includes("a")` |
| find index | `s.find("a")` | `s.indexOf("a")` |
| replace all | `s.replace("a","b")` | `s.replaceAll("a","b")` |
| starts with | `s.startswith("a")` | `s.startsWith("a")` |

Big difference: in Python `join` is a method of the SEPARATOR string, not the list. Python `replace` replaces ALL matches by default; JS `replace` replaces only the first (with a string pattern).

```python
# Python way
print(",".join(["a", "b"]))     # a,b   (separator.join(list))
print("a-a".replace("a", "x"))  # x-x   (all replaced)
```
```javascript
// JavaScript way
console.log(["a", "b"].join(","));   // a,b   (list.join(separator))
console.log("a-a".replace("a","x")); // x-a   (only first!)
```

---

## 🟠 FastAPI Connection
Clean incoming strings in a Pydantic validator, and parse headers such as `Authorization: Bearer <token>` with `split` / `removeprefix`.

```python
from fastapi import FastAPI, Header, HTTPException   # FastAPI imports
from pydantic import BaseModel, field_validator      # validation

app = FastAPI()                                      # app

class Signup(BaseModel):
    email: str                                       # raw email

    @field_validator("email")
    @classmethod
    def clean_email(cls, v: str) -> str:
        return v.strip().lower()                     # normalize before saving

@app.get("/me")
def me(authorization: str = Header()) -> dict[str, str]:
    if not authorization.startswith("Bearer "):      # check scheme
        raise HTTPException(401, "Bad auth header")  # reject
    token = authorization.removeprefix("Bearer ")    # get token only
    return {"token_len": str(len(token))}            # demo response
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Ignoring the return value
```python
# Wrong
name = "  priya "
name.strip()              # does nothing to name
# Right
name = name.strip()
```

❌ Mistake 2: Thinking `strip("abc")` removes the substring
```python
# Wrong assumption
"cabbage".strip("abc")    # 'ge' -> strips every char of the SET from both edges
# For exact prefix/suffix use:
"file.txt".removesuffix(".txt")   # 'file'
```

❌ Mistake 3: `split()` vs `split(" ")`
```python
# Wrong
"a  b".split(" ")         # ['a', '', 'b']  empty item
# Right
"a  b".split()            # ['a', 'b']  splits on any whitespace run
```

---

## 🧠 Tricky Interview Question

```python
s = "banana"
print(s.replace("a", "o", 2))
print(s.find("na"), s.rfind("na"), s.count("ana"))
print("a,b,,c".split(","))
print("  x ".split(" "))
```
Answer:
```
bonona
2 4 1
['a', 'b', '', 'c']
['', '', 'x', '']
```
`replace(old, new, 2)` replaces only the first 2. `find` gives the first index (2), `rfind` the last (4). `count("ana")` counts NON-overlapping matches: "banana" has "ana" at 1 and 3 (overlap), so only 1. `split(",")` keeps empty strings; `split(" ")` on `"  x "` yields empties at the edges.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `find()` and `index()`?
A1: Both return the first match position. If not found, `find` returns -1, `index` raises `ValueError`. Use `find` when absence is normal, `index` when absence is a bug.

Q2: Difference between `split()` and `partition()`?
A2: `split` returns a list of all parts. `partition(sep)` splits only at the first separator and always returns a 3-tuple `(before, sep, after)`; if not found it returns `(s, "", "")`. `partition` is safer for `key=value` parsing.

Q3: How do you check whether a string is a number?
A3: `isdigit()` only handles non-negative digit characters (`"-5".isdigit()` is False, `"²".isdigit()` is True). The robust way is try/except: `float(s)` or `int(s)`.

Q4: What does `strip()` do with arguments?
A4: It removes any characters in the given set from both ends, not a substring. `"xxhixx".strip("x")` -> `hi`. Use `removeprefix` / `removesuffix` for exact text.

Q5: Why must you `encode()` before hashing or sending over sockets?
A5: Hash functions (hashlib, hmac) and sockets work with `bytes`, not `str`. `hashlib.sha256("hi".encode()).hexdigest()` is the correct pattern.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Cleaning and splitting simple text (`strip`, `split`, `partition`)
- Exact prefix/suffix/substring checks
- Converting between text and bytes

❌ Avoid when:
- The pattern is complex (use `re` regex)
- Parsing structured formats (use `json`, `csv`, `urllib.parse`) instead of manual `split`
- Building huge text in loops with `+=` (use `join`)

---

## 📊 Visual Diagram
```
 "  a,b,c  "
     │ strip()
     ▼
 "a,b,c"
     │ split(",")
     ▼
 ["a", "b", "c"]
     │ "-".join(...)
     ▼
 "a-b-c"
     │ .encode("utf-8")
     ▼
 b"a-b-c"

 partition("=") on "k=v=x"  ──► ("k", "=", "v=x")
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| split | Break string into list | String को list में तोड़ना |
| join | Combine list into string | List को string में जोड़ना |
| strip | Remove edge chars | किनारों के characters हटाना |
| partition | Split at first separator into 3 parts | पहले separator पर 3 हिस्सों में बाँटना |
| encode | str to bytes | str से bytes बनाना |
| chaining | Calling methods one after another | Methods को एक के बाद एक call करना |

---

## ⚡ 3-Line Summary
English: String methods never change the original; they return new values. Know split/join/strip/replace/find/partition/startswith/encode by heart. Prefer `partition` and `removeprefix` for safe parsing.
Hindi: String methods original नहीं बदलते, नई value देते हैं। split/join/strip/replace/find/partition/startswith/encode याद रखें। Safe parsing के लिए `partition` और `removeprefix` बेहतर हैं।

---

## ➡️ Next Topic
**071. f-strings — Complete Guide** — the modern, fastest way to embed values and expressions into strings.
