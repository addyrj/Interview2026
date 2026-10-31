---

# 016. str — String Complete Guide
# हिंदी में: str — String की पूरी guide

---

## 🔵 Simple Definition (English)
A `str` is an immutable sequence of Unicode characters used for text. You create it with single, double or triple quotes. Because it is immutable, every "change" (upper, replace, slice) returns a NEW string and leaves the original untouched.

## 🔵 सरल परिभाषा (Hindi)
`str` Unicode characters का immutable sequence है जो text के लिए use होता है। इसे single, double या triple quotes से बनाते हैं। Immutable होने के कारण हर "बदलाव" (upper, replace, slice) एक NEW string लौटाता है और original जस की तस रहती है।

---

## 🔴 Problem it Solves
Text is everywhere: names, emails, JSON, URLs, logs, prompts for AI models. Older languages used ASCII bytes and struggled with Hindi, Chinese or emoji. Python 3 strings are Unicode by default, so `"नमस्ते 🙏"` just works. Rich built-in methods (`split`, `join`, `strip`, `replace`, f-strings) remove the need for manual character loops.

## 🔴 यह क्यों बना? (Hindi)
Text हर जगह है: नाम, emails, JSON, URLs, logs, AI models के prompts। पुरानी languages ASCII bytes use करती थीं और हिंदी, चीनी या emoji में दिक्कत होती थी। Python 3 की strings default में Unicode हैं, इसलिए `"नमस्ते 🙏"` सीधे चलता है। `split`, `join`, `strip`, `replace`, f-strings जैसे methods से character loops लिखने की ज़रूरत नहीं पड़ती।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Literal "Python" creates a str object (sequence of Unicode code points)
Step 2 → Each character has an index:   P  y  t  h  o  n
                                        0  1  2  3  4  5
                                       -6 -5 -4 -3 -2 -1   (negative from the end)
Step 3 → Slicing s[start:stop:step] builds a NEW string (stop is excluded)
Step 4 → Methods (s.upper(), s.replace(...)) return NEW strings; s never changes
Step 5 → Formatting: f"Hi {name}" evaluates expressions inside {} at runtime
Step 6 → Saving/sending text: s.encode("utf-8") -> bytes ; b.decode("utf-8") -> str
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → "Python" literal एक str object बनाता है (Unicode code points का sequence)
Step 2 → हर character का index होता है: P=0, y=1, t=2, h=3, o=4, n=5
         पीछे से negative index: n=-1, o=-2 ...
Step 3 → Slicing s[start:stop:step] नई string बनाती है (stop शामिल नहीं)
Step 4 → Methods (s.upper(), s.replace(...)) नई strings लौटाते हैं; s नहीं बदलती
Step 5 → Formatting: f"Hi {name}" में {} के अंदर expressions runtime पर चलते हैं
Step 6 → Save/send करने के लिए: s.encode("utf-8") → bytes ; b.decode("utf-8") → str
```

---

## 🟡 Real World Example
In an AI chat app built with FastAPI, a user message arrives as a string. You `strip()` extra spaces, `lower()` it for a command check, use an f-string to build the prompt (`f"Answer in Hindi: {question}"`), count characters for token limits, and `json.dumps` the result. In a Swiggy-style service, you normalize phone numbers (`replace(" ", "")`), validate pincodes (`isdigit()`), and build log lines with f-strings.

## 🟡 Real Example Hindi mein
FastAPI से बने AI chat app में user message एक string के रूप में आता है। आप extra spaces `strip()` करते हैं, command check के लिए `lower()` करते हैं, prompt बनाने के लिए f-string (`f"Answer in Hindi: {question}"`) लगाते हैं, token limit के लिए characters गिनते हैं और result को `json.dumps` करते हैं। Swiggy जैसी service में phone numbers normalize (`replace(" ", "")`), pincode validate (`isdigit()`) और log lines f-strings से बनती हैं।

---

## 💻 Code Example — Basic
```python
# Basic: creating, indexing, slicing and common methods
name: str = "  Python Rocks  "  # string with leading/trailing spaces
clean: str = name.strip()  # remove spaces at both ends -> new string
print(clean)  # Output: Python Rocks
print(name)  # Output:   Python Rocks   (original unchanged: immutable)

# Indexing and slicing (stop index is excluded)
word: str = "Python"  # sample word
print(word[0], word[-1])  # Output: P n
print(word[0:2], word[2:], word[:3])  # Output: Py thon Pyt
print(word[::-1])  # Output: nohtyP   (step -1 reverses)
print(word[::2])  # Output: Pto       (every 2nd character)

# Common methods
print(clean.upper(), clean.lower())  # Output: PYTHON ROCKS python rocks
print(clean.replace("Rocks", "Wins"))  # Output: Python Wins
print(clean.split())  # Output: ['Python', 'Rocks']
print("-".join(["a", "b", "c"]))  # Output: a-b-c
print(clean.startswith("Py"), clean.endswith("s"))  # Output: True True
print(clean.find("Rocks"), clean.find("Java"))  # Output: 7 -1  (-1 means not found)
print(clean.count("o"))  # Output: 2

# Formatting with f-strings
price: float = 1234.5678  # a float to format
print(f"Name={word!r} price={price:.2f} big={1234567:,}")  # Output: Name='Python' price=1234.57 big=1,234,567
print(f"{word:>10}|{word:<10}|{word:^10}|")  # Output:     Python|Python    |  Python  |

# Checks
print("123".isdigit(), "abc".isalpha(), "ab12".isalnum(), "   ".isspace())  # Output: True True True True

# Multi-line and raw strings
text: str = """line one
line two"""  # triple quotes keep line breaks
print(text.splitlines())  # Output: ['line one', 'line two']
print(r"C:\new\table")  # Output: C:\new\table  (raw string: backslashes stay)
```

## 💻 Code Example — Advanced
```python
# Advanced: Unicode, bytes, efficient building, validation and templates
from __future__ import annotations  # modern hints on all 3.x

import re  # regular expressions
import unicodedata  # Unicode normalization
from string import Template  # safe user-facing templates

# 1. Unicode: characters vs bytes
hindi: str = "नमस्ते"  # 6 code points
raw: bytes = hindi.encode("utf-8")  # text -> bytes
print(len(hindi), len(raw))  # Output: 6 18
print(raw.decode("utf-8") == hindi)  # Output: True  (round trip)
print("héllo" == unicodedata.normalize("NFC", "he\u0301llo"))  # Output: True  (same text, two encodings)

# 2. Strings are immutable: building in a loop with += is slow; use join
parts: list[str] = [str(i) for i in range(5)]  # pieces to combine
slow: str = ""  # accumulator
for p in parts:  # each += creates a new string
    slow += p
fast: str = "".join(parts)  # one allocation, preferred
print(slow == fast, fast)  # Output: True 01234

# 3. Validate and normalize a phone number
PHONE_RE = re.compile(r"^(?:\+91)?[6-9]\d{9}$")  # Indian mobile pattern


def normalize_phone(raw_value: str) -> str:
    """Remove spaces and dashes, then validate an Indian mobile number."""
    cleaned = re.sub(r"[\s\-]", "", raw_value)  # drop separators
    if not PHONE_RE.match(cleaned):  # invalid format
        raise ValueError(f"Invalid phone: {raw_value!r}")
    return cleaned[-10:]  # keep the last 10 digits


print(normalize_phone("+91 98765-43210"))  # Output: 9876543210
try:
    normalize_phone("12345")  # too short and wrong start
except ValueError as exc:
    print(exc)  # Output: Invalid phone: '12345'


# 4. Slugify a title for URLs
def slugify(title: str) -> str:
    """'  Hello, World! 2024 ' -> 'hello-world-2024'."""
    lowered = title.strip().lower()  # trim and lower-case
    return re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")  # non-alphanumerics -> '-'


print(slugify("  Hello, World! 2024 "))  # Output: hello-world-2024

# 5. Template for text that users can edit (safer than eval/format on user input)
tpl = Template("Hi $name, your order $order_id is confirmed")  # $placeholders
print(tpl.substitute(name="Asha", order_id=42))  # Output: Hi Asha, your order 42 is confirmed

# 6. Immutability proof
s: str = "abc"  # a string
try:
    s[0] = "z"  # type: ignore[index]  # item assignment is not allowed
except TypeError as exc:
    print(exc)  # Output: 'str' object does not support item assignment
```

---

## 🟠 JavaScript vs Python Comparison
Both have immutable strings and template literals. Python indexes by Unicode code point (JS uses UTF-16 code units, so emoji count as 2). Python has slicing `s[1:4]` and negative indexes; JS uses `slice`, `substring`, `at(-1)`. Python has no separate char type: a character is just a string of length 1.

```python
# Python
s = "Hello, World"
print(s[0:5], s[-5:])  # Hello World
print(s.upper(), s.split(", "))  # HELLO, WORLD ['Hello', 'World']
print(" | ".join(["a", "b"]))  # a | b
print(f"{s} has {len(s)} chars")  # Hello, World has 12 chars
print("😀"[0], len("😀"))  # 😀 1  (one code point)
```
```javascript
// JavaScript
const s = "Hello, World";
console.log(s.slice(0, 5), s.slice(-5)); // Hello World
console.log(s.toUpperCase(), s.split(", ")); // HELLO, WORLD [ 'Hello', 'World' ]
console.log(["a", "b"].join(" | ")); // a | b (join belongs to the array!)
console.log(`${s} has ${s.length} chars`); // Hello, World has 12 chars
console.log("😀".length); // 2 (UTF-16 surrogate pair)
```
Key difference: in Python `join` is a string method (`sep.join(list)`), in JS it is an array method.

---

## 🟠 FastAPI Connection
Strings are the most common FastAPI types: path parameters, query parameters, headers and JSON fields. Pydantic offers `Field(min_length=..., max_length=..., pattern=...)` and `Annotated[str, ...]` for constraints. Use `strip` and `lower` in validators to normalize emails. Be careful: query parameter text is always a string first, and FastAPI converts it using your type hint.

```python
from typing import Annotated  # attach metadata to types

from fastapi import FastAPI, Query  # web framework and query helper
from pydantic import BaseModel, Field, field_validator  # validation tools

app: FastAPI = FastAPI()  # app object


class SignUp(BaseModel):
    username: str = Field(min_length=3, max_length=20, pattern=r"^[a-z0-9_]+$")
    email: str  # raw text, normalized below

    @field_validator("email")  # runs after basic type checks
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()  # " Asha@Example.COM " -> "asha@example.com"


@app.post("/signup")  # POST /signup
def signup(data: SignUp) -> SignUp:
    return data  # returns the cleaned model


@app.get("/search")  # GET /search?q=pizza
def search(q: Annotated[str, Query(min_length=2, max_length=50)]) -> dict[str, str]:
    return {"query": q.strip().lower()}  # normalize search text
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trying to modify a string in place
```python
# Wrong:
s = "hello"
# s[0] = "H"      # TypeError: 'str' object does not support item assignment
# Right:
s = "H" + s[1:]  # build a new string -> "Hello"
```
✅ Correct: strings are immutable; create a new one.

❌ Mistake 2: Ignoring that methods return new strings
```python
# Wrong:
name = "  asha  "
name.strip()  # result thrown away!
print(repr(name))  # '  asha  '  (unchanged)
# Right:
name = name.strip()  # assign the result back
print(repr(name))  # 'asha'
```
✅ Correct: always assign the returned value.

❌ Mistake 3: Concatenating str and int, or building big strings with `+=`
```python
# Wrong:
age = 25
# print("Age: " + age)   # TypeError: can only concatenate str (not "int") to str
# Right:
print("Age: " + str(age))  # explicit conversion
print(f"Age: {age}")  # best: f-string
# Also avoid: result += piece inside huge loops. Use "".join(pieces).
```
✅ Correct: use f-strings and `join`.

---

## 🧠 Tricky Interview Question

```python
# What will this output?
a = "hello"
b = "hel" + "lo"
c = "".join(["hel", "lo"])
print(a == b, a == c)
print(a is b, a is c)
print("abc" * 0 == "", "abc"[5:10], "abc"[::-1])
try:
    print("abc"[5])
except IndexError as e:
    print(e)
```
Answer:
```
True True
True False
True  cba
string index out of range
```
`==` compares values, so all are equal. `a is b` is `True` because the compiler folds `"hel" + "lo"` into the constant `"hello"` and CPython shares identical constants; `c` is built at runtime so it is a different object (`is` is `False`). Never use `is` to compare strings. Slicing is forgiving: `"abc"[5:10]` returns an empty string `''` (printed as nothing, hence the double space), but indexing `"abc"[5]` raises `IndexError`. Exact `is` results are a CPython implementation detail.

---

## ⚫ Interview Questions + Answers

Q1: Why are strings immutable in Python, and what are the consequences?
A1: Immutability makes strings hashable (usable as dict keys), thread-safe and safe to share or cache (CPython interns many short strings). The consequence is that every modification creates a new object, so repeated `+=` in a loop is O(n²). Collect pieces in a list and use `"".join(pieces)`.

Q2: What is the difference between `str` and `bytes`?
A2: `str` is text (Unicode code points); `bytes` is raw binary data (0-255 values). Convert with `s.encode("utf-8")` and `b.decode("utf-8")`. Files opened in `"rb"` mode, network sockets and hashes (`hashlib`) work with bytes, so you must encode text first. Always specify the encoding explicitly.

Q3: Compare `%` formatting, `str.format()` and f-strings.
A3: `"%s is %d" % (name, age)` is old C-style. `"{} is {}".format(name, age)` is more flexible. f-strings (`f"{name} is {age}"`, Python 3.6+) are the fastest and most readable, and allow expressions and format specs: `f"{price:.2f}"`, `f"{n:,}"`. Avoid f-strings in logging calls (`logger.info("x %s", x)` defers formatting) and for untrusted templates.

Q4: How do `split`, `join`, `strip` and `replace` work?
A4: `s.split(sep)` returns a list of pieces (no argument splits on any whitespace and drops empties). `sep.join(iterable)` glues strings together. `s.strip()` removes whitespace (or given characters) from both ends; `lstrip`/`rstrip` do one side. `s.replace(old, new, count)` returns a copy with replacements. All return new values.

Q5: What is string interning and when does `is` work on strings?
A5: CPython reuses (interns) some strings, such as identifiers and short compile-time constants, to save memory and speed up comparisons. So `is` may be `True` for equal strings, but this is an implementation detail and not guaranteed. Always use `==` for string comparison; use `sys.intern()` only for deliberate optimization.

---

## 🔷 When to Use + When Not to Use
✅ Use `str` when:
- Handling any human-readable text: names, emails, prompts, logs, JSON keys
- Building messages with f-strings and joining with `"".join(...)`
- Validating input with `isdigit`, `startswith`, regex

❌ Avoid when:
- Storing numbers you will calculate with (convert to `int`/`Decimal`)
- Building huge text by repeated `+=` (use `join` or `io.StringIO`)
- Handling binary data (use `bytes`)
- Putting user input into `eval`, SQL or shell strings (use parameters)

---

## 📊 Visual Diagram
```
   s = "Python"

   index :   0   1   2   3   4   5
           ┌───┬───┬───┬───┬───┬───┐
           │ P │ y │ t │ h │ o │ n │
           └───┴───┴───┴───┴───┴───┘
   negative: -6  -5  -4  -3  -2  -1

   s[1:4]  -> "yth"      (start included, stop excluded)
   s[::-1] -> "nohtyP"   (reverse)
   s.upper() creates a NEW object; s still points to "Python"

   text (str) ── encode("utf-8") ──► bytes ── decode("utf-8") ──► text (str)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Immutable | Cannot be changed in place | जगह पर बदला नहीं जा सकता |
| Slicing | Taking part of a sequence | Sequence का हिस्सा निकालना |
| f-string | Inline formatted string `f"{x}"` | Inline formatting वाली string |
| Unicode | Standard covering all scripts | सभी लिपियों का standard |
| Encoding | Converting text to bytes | Text को bytes में बदलना |
| Interning | Reusing identical string objects | समान string objects को दोबारा use करना |

---

## ⚡ 3-Line Summary
English: A `str` is an immutable Unicode text sequence; all methods return new strings, so assign the result back. Use slicing, f-strings, `split`/`join` and encode/decode for bytes. Build large text with `"".join(...)` and compare with `==`, never `is`.
Hindi: `str` immutable Unicode text sequence है; सारे methods नई strings लौटाते हैं, इसलिए result वापस assign करें। Slicing, f-strings, `split`/`join` और bytes के लिए encode/decode use करें। बड़ा text `"".join(...)` से बनाएँ और compare `==` से करें, `is` से कभी नहीं।

---

## ➡️ Next Topic
**017. bool (Boolean)** — True/False, truthy and falsy values, and how conditions really work.
