---

# 069. String — Complete Guide
# हिंदी में: String (स्ट्रिंग) — पूरी गाइड

---

## 🔵 Simple Definition (English)
A `str` is an immutable sequence of Unicode characters. You create it with single, double, or triple quotes. Once created, you cannot change a character in place — every "change" produces a new string.

## 🔵 सरल परिभाषा (Hindi)
`str` Unicode characters की immutable sequence है। इसे single, double या triple quotes से बनाते हैं। बनने के बाद किसी character को in-place नहीं बदल सकते — हर "change" एक नई string बनाता है।

---

## 🔴 Problem it Solves
Programs must handle names, emails, JSON text, SQL, logs, Hindi/Tamil/emoji text. Old languages (C) used raw byte arrays with null terminators — buffer overflows and encoding bugs everywhere. Python 3's `str` stores real Unicode text, so `"नमस्ते"` has length 6 and works the same on every OS. Immutability makes strings safe as dict keys and safe to share between threads.

## 🔴 यह क्यों बना? (Hindi)
Names, emails, JSON, logs, Hindi/emoji text — सब handle करना होता है। C में strings raw bytes थीं, encoding bugs और buffer overflow आम थे। Python 3 की `str` असली Unicode text रखती है, इसलिए `"नमस्ते"` की length 6 है और हर OS पर same चलती है। Immutable होने से string dict key बन सकती है और threads में safe है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Literal "hello" in source is decoded (UTF-8 by default)
Step 2 → Python creates a str object: array of Unicode code points
Step 3 → Object is immutable: s[0] = "H" raises TypeError
Step 4 → Operations (upper, +, slice) build a NEW str object
Step 5 → Short identifier-like strings may be "interned" (shared)
Step 6 → hash(s) is computed once and cached -> fast dict lookups
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Source का literal UTF-8 से decode होता है
Step 2 → str object बनता है: Unicode code points की array
Step 3 → Immutable: s[0] = "H" पर TypeError
Step 4 → upper, +, slice हमेशा NEW str बनाते हैं
Step 5 → छोटी strings interned (shared) हो सकती हैं
Step 6 → hash एक बार बनकर cache होता है -> dict lookup तेज़
```

---

## 🟡 Real World Example
Zomato search: user types "Paneer Tikka " (with trailing space, mixed case). Backend does `query.strip().lower()` before searching. Razorpay: order IDs like `"order_Kx92"` are strings used as dict keys. AI app: a prompt is a long string; token count is based on its text. FastAPI: every query/path parameter arrives as a string first, then is converted.

## 🟡 Real Example Hindi mein
Zomato search में user "Paneer Tikka " (पीछे space, mixed case) लिखता है — backend `query.strip().lower()` करके search करता है। Razorpay के order IDs strings हैं जो dict keys बनती हैं। AI app में prompt एक लंबी string है। FastAPI में हर query/path parameter पहले string के रूप में ही आता है।

---

## 💻 Code Example — Basic
```python
# Basic string operations
name: str = "Priya"                   # double quotes
city: str = 'Pune'                    # single quotes (same thing)
hindi: str = "नमस्ते"                  # Unicode text works directly

print(len(name))                      # 5   number of characters
print(len(hindi))                     # 6   code points, not bytes
print(name[0], name[-1])              # P a   first and last char
print(name + " from " + city)         # Priya from Pune   concatenation
print("ab" * 3)                       # ababab   repetition
print("ri" in name)                   # True   substring check
print(name.upper(), name.lower())     # PRIYA priya

# Strings are immutable
try:
    name[0] = "p"                     # try changing a character
except TypeError as e:
    print("Error:", e)                # Error: 'str' object does not support item assignment

new_name: str = "p" + name[1:]        # build a new string instead
print(new_name)                       # priya
print(name)                           # Priya   original unchanged

# Iteration and comparison
for ch in "abc":                      # loop over characters
    print(ch, ord(ch))                # a 97 / b 98 / c 99
print("apple" < "banana")             # True   lexicographic order
print(chr(65))                        # A   code point -> char
```

## 💻 Code Example — Advanced
```python
# Production-style string handling: normalize, validate, encode
from __future__ import annotations         # modern type hints
import re                                  # regex for validation
import sys                                 # for interning demo
import unicodedata                         # Unicode normalization

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.]+$")   # simple email pattern


def normalize_username(raw: str) -> str:
    """Clean user input into a safe, comparable username."""
    if not isinstance(raw, str):                       # type guard
        raise TypeError("username must be str")        # fail loudly
    text = unicodedata.normalize("NFC", raw)           # canonical Unicode form
    text = text.strip().casefold()                     # trim + aggressive lowercase
    if not 3 <= len(text) <= 20:                       # length rule
        raise ValueError("username must be 3-20 chars")
    return text                                        # safe value


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email.strip()))         # True/False


if __name__ == "__main__":
    print(normalize_username("  Priya_S  "))           # priya_s
    print(is_valid_email("a.b@site.co.in"))            # True
    print(is_valid_email("bad@"))                      # False

    # casefold vs lower: German sharp s
    print("Straße".lower())                            # straße
    print("Straße".casefold())                         # strasse

    # Two forms of "é": 1 char vs 2 chars
    a = "é"                                       # single code point
    b = "é"                                      # e + combining accent
    print(a == b, len(a), len(b))                      # False 1 2
    print(unicodedata.normalize("NFC", b) == a)        # True

    # Strings vs bytes
    data: bytes = "नमस्ते".encode("utf-8")              # str -> bytes
    print(len("नमस्ते"), len(data))                     # 6 18
    print(data.decode("utf-8"))                        # नमस्ते

    # Building big strings: join is O(n), += in loop is slower
    parts: list[str] = [str(i) for i in range(5)]      # ['0','1','2','3','4']
    print(",".join(parts))                             # 0,1,2,3,4

    # Interning: equal literals can be the same object
    x = sys.intern("hello world")                      # force interning
    y = sys.intern("hello world")                      # same value
    print(x is y)                                      # True
```

---

## 🟠 JavaScript vs Python Comparison
JS strings are also immutable, but they are UTF-16: `"😀".length` is 2 in JS, but `len("😀")` is 1 in Python. JS has no separate char type; neither does Python. Python has no `charAt`; use indexing `s[i]`. Negative indexes (`s[-1]`) work in Python only.

```python
# Python way
s = "Hello 😀"
print(len(s))        # 7   (emoji counts as 1)
print(s[-1])         # 😀  negative index
print(s[::-1])       # 😀 olleH   reverse
print("ell" in s)    # True
```
```javascript
// JavaScript way
const s = "Hello 😀";
console.log(s.length);          // 8  (emoji = 2 UTF-16 units)
console.log(s.at(-1));          // half of surrogate pair, broken char
console.log([...s].reverse().join(""));  // need spread to reverse safely
console.log(s.includes("ell")); // true
```

---

## 🟠 FastAPI Connection
FastAPI uses `str` for path and query params, and validates length/pattern via `Query` and Pydantic `Field`. Always `strip()` and normalize user strings before saving them.

```python
from fastapi import FastAPI, Query                 # FastAPI imports
from pydantic import BaseModel, Field              # validation models

app = FastAPI()                                    # app instance

class UserIn(BaseModel):
    username: str = Field(min_length=3, max_length=20, pattern=r"^[a-z0-9_]+$")  # str rules
    email: str                                     # plain string

@app.get("/search")
def search(q: str = Query(min_length=2, max_length=50)) -> dict[str, str]:
    return {"query": q.strip().casefold()}         # normalize before use

@app.post("/users")
def create(user: UserIn) -> dict[str, str]:
    return {"username": user.username}             # already validated
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting strings are immutable
```python
# Wrong
s = "hello"
s.upper()            # result thrown away
print(s)             # hello

# Right
s = s.upper()        # assign the new string
print(s)             # HELLO
```

❌ Mistake 2: Using `+=` in a big loop
```python
# Wrong (can be slow for huge loops)
out = ""
for w in words:
    out += w + ","

# Right
out = ",".join(words)
```

❌ Mistake 3: Mixing str and int with `+`
```python
# Wrong
age = 25
print("Age: " + age)         # TypeError

# Right
print("Age: " + str(age))    # or f"Age: {age}"
```

---

## 🧠 Tricky Interview Question

```python
a = "hello"
b = "hello"
c = "hel" + "lo"
d = "".join(["hel", "lo"])
print(a is b, a is c, a is d, a == d)
```
Answer: Typically `True True False True`. Identical literals are interned/shared (`a is b`). `"hel" + "lo"` is folded at compile time into `"hello"`, so also the same object. `join` builds the string at runtime, so it is a different object (`is` False) but equal in value. Lesson: use `==` for strings, never `is`. (The `is` results are a CPython implementation detail.)

---

## ⚫ Interview Questions + Answers

Q1: Are Python strings mutable?
A1: No. `s[0] = "x"` raises `TypeError`. Methods like `replace`, `upper` return new strings. This allows hashing, interning, and thread safety.

Q2: What is the difference between `str` and `bytes`?
A2: `str` is text (Unicode code points); `bytes` is raw 8-bit data. Convert with `encode()` (str -> bytes) and `decode()` (bytes -> str). Always specify encoding, usually UTF-8.

Q3: Why is `"".join(list)` faster than `+=` in a loop?
A3: `join` computes the total size once and copies each piece once: O(n). Repeated `+=` can copy the growing string every iteration: O(n^2) in the worst case (CPython sometimes optimizes it, but do not rely on that).

Q4: What is the difference between `lower()` and `casefold()`?
A4: `casefold()` is more aggressive and meant for caseless comparison across languages (`"ß"` -> `"ss"`). Use it to compare user input; `lower()` for display.

Q5: How do you reverse a string?
A5: `s[::-1]` (slice with step -1). For grapheme-correct reversal of combined characters you need a library, because combining marks are separate code points.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Handling text, identifiers, JSON keys, URLs, prompts
- You need hashable, immutable values

❌ Avoid when:
- You build huge text piece by piece (use list + `join`, or `io.StringIO`)
- You handle binary data (use `bytes`)
- You modify characters in place often (use list of chars or `bytearray`)

---

## 📊 Visual Diagram
```
 s = "Hello"
 index :   0    1    2    3    4
         +----+----+----+----+----+
         | H  | e  | l  | l  | o  |
         +----+----+----+----+----+
 neg   :  -5   -4   -3   -2   -1

 s.upper() ──► NEW object "HELLO"      s still "Hello"
 s[0]="h"  ──► TypeError (immutable)
 encode("utf-8")  str ───────► bytes
 decode("utf-8")  str ◄─────── bytes
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Immutable | Cannot change in place | In-place बदल नहीं सकते |
| Unicode | Standard for all world characters | सभी भाषाओं के characters का standard |
| Code point | Number assigned to a character | Character का number |
| Encoding | Rule to turn text into bytes | Text को bytes में बदलने का नियम |
| Interning | Sharing identical strings | समान strings का साझा object |
| Casefold | Aggressive lowercase for comparison | Comparison के लिए lowercase |

---

## ⚡ 3-Line Summary
English: `str` is an immutable Unicode text sequence. Every operation returns a new string; use `join` to build big strings and `==` to compare. Convert to `bytes` with `encode` when sending over networks or files.
Hindi: `str` immutable Unicode text sequence है। हर operation नई string देता है; बड़ी string के लिए `join` और compare के लिए `==` use करें। Network/file के लिए `encode` से `bytes` बनाएँ।

---

## ➡️ Next Topic
**070. String Methods** — split, join, strip, replace, find, format, encode: the everyday toolbox for strings.
