---

# 073. String Slicing
# हिंदी में: String Slicing (String का टुकड़ा काटना)

---

## 🔵 Simple Definition (English)
String slicing means taking a part of a string using the syntax `text[start:stop:step]`. `start` is included, `stop` is excluded, and `step` says how many characters to jump. Slicing never changes the original string — it always returns a new string.

## 🔵 सरल परिभाषा (Hindi)
String slicing का मतलब है string का एक हिस्सा निकालना, syntax: `text[start:stop:step]`। `start` शामिल होता है, `stop` शामिल नहीं होता, और `step` बताता है कितने characters छोड़कर आगे बढ़ना है। Original string कभी नहीं बदलती — हमेशा नई string मिलती है।

---

## 🔴 Problem it Solves
Without slicing you would need loops and index math to cut a string: first 5 characters, last 4 digits of a card, a reversed string, every second letter. That is long and error-prone. JavaScript has `substring`, `slice`, `substr` (three different methods with different rules!). Python gives ONE consistent syntax that works on strings, lists, tuples, bytes — everything that is a sequence.

## 🔴 यह क्यों बना? (Hindi)
Slicing के बिना string काटने के लिए loop और index का हिसाब लगाना पड़ता: पहले 5 characters, card के आखिरी 4 digits, reverse string, हर दूसरा letter। यह लंबा और गलती-prone है। JavaScript में `substring`, `slice`, `substr` तीन अलग methods हैं। Python में एक ही syntax है जो string, list, tuple, bytes सब पर चलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python reads text[start:stop:step]
Step 2 → Missing values get defaults: start=0, stop=len, step=1
Step 3 → Negative index is converted: -1 → len-1, -2 → len-2 ...
Step 4 → Out-of-range values are CLIPPED (no IndexError in slices)
Step 5 → Python collects characters from start up to (not including) stop
Step 6 → A NEW string is created and returned

 H  e  l  l  o  ,     F  a  s  t  A  P  I  !
 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14     ← positive index
-15 ...                                    -2 -1  ← negative index
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Python text[start:stop:step] पढ़ता है
Step 2 → जो value नहीं दी, उसका default: start=0, stop=len, step=1
Step 3 → Negative index बदलता है: -1 → आखिरी character
Step 4 → Range से बाहर की values काट दी जाती हैं (slice में IndexError नहीं आता)
Step 5 → start से stop से पहले तक characters जमा होते हैं
Step 6 → नई string बनकर return होती है
```

---

## 🟡 Real World Example
Razorpay / Paytm style apps never show a full card number — they show `************1234`. An API that receives `Authorization: Bearer <token>` cuts the token with `header[7:]`. Pagination in a small in-memory API uses `items[start:start+size]`. A palindrome checker (very common interview question) uses `s[::-1]`.

## 🟡 Real Example Hindi mein
Razorpay / Paytm जैसे apps पूरा card number कभी नहीं दिखाते — `************1234` दिखाते हैं। जो API `Authorization: Bearer <token>` लेती है वो `header[7:]` से token निकालती है। छोटे in-memory API में pagination `items[start:start+size]` से होती है। Palindrome checker (बहुत common interview question) `s[::-1]` इस्तेमाल करता है।

---

## 💻 Code Example — Basic
```python
# Basic string slicing examples
text: str = "Hello, FastAPI!"        # a 15 character string

print(text[0])                       # first character -> H
print(text[-1])                      # last character -> !
print(text[0:5])                     # index 0 to 4 -> Hello
print(text[7:])                      # from index 7 to end -> FastAPI!
print(text[:5])                      # from start to index 4 -> Hello
print(text[::2])                     # every 2nd character -> Hlo atP!
print(text[::-1])                    # whole string reversed -> !IPAtsaF ,olleH
print(text[100:200] == "")           # out of range slice is empty, no error -> True
print(text[-8:-1])                   # negative start and stop -> FastAPI
s: slice = slice(0, 5)               # slice object, reusable
print(text[s])                       # same as text[0:5] -> Hello
print(s.indices(len(text)))          # resolved (start, stop, step) -> (0, 5, 1)
nums: list[int] = [10, 20, 30, 40, 50]   # slicing works on lists too
print(nums[1:4], nums[::-1])         # [20, 30, 40] [50, 40, 30, 20, 10]

# Output:
# H
# !
# Hello
# FastAPI!
# Hello
# Hlo atP!
# !IPAtsaF ,olleH
# True
# FastAPI
# Hello
# (0, 5, 1)
# [20, 30, 40] [50, 40, 30, 20, 10]
```

## 💻 Code Example — Advanced
```python
# Production style helpers built on slicing
from typing import Optional              # Optional type hint


def mask_card(card: str) -> str:
    """Show only the last 4 digits of a card number."""
    digits: str = card.replace(" ", "").replace("-", "")   # remove separators
    if len(digits) < 12:                                    # basic validation
        raise ValueError("card too short")                  # fail loudly
    return "*" * (len(digits) - 4) + digits[-4:]            # mask + last 4


def is_palindrome(s: str) -> bool:
    """Check palindrome ignoring case, spaces and punctuation."""
    cleaned: str = "".join(ch.lower() for ch in s if ch.isalnum())  # keep letters/digits
    return cleaned == cleaned[::-1]                                  # compare with reverse


def paginate(items: list[int], page: int, size: int = 3) -> list[int]:
    """Return one page of items (page starts from 1)."""
    if page < 1 or size < 1:                                # validate input
        raise ValueError("page and size must be >= 1")      # reject bad input
    start: int = (page - 1) * size                          # first index of page
    return items[start:start + size]                        # slice never raises


def split_token(header: str) -> Optional[str]:
    """Extract token from 'Bearer <token>' header."""
    prefix: str = "Bearer "                                 # expected prefix
    return header[len(prefix):] if header.startswith(prefix) else None  # cut prefix


print(mask_card("4111 1111 1111 1234"))                     # ************1234
print(is_palindrome("A man, a plan, a canal: Panama"))      # True
print(paginate(list(range(1, 11)), 2))                      # [4, 5, 6]
print(paginate(list(range(1, 11)), 4))                      # [10]
print(paginate(list(range(1, 11)), 9))                      # []
print(split_token("Bearer abc.def.ghi"))                    # abc.def.ghi
print(split_token("Basic xyz"))                             # None
try:                                                        # error handling demo
    mask_card("123")                                        # too short
except ValueError as e:                                     # catch the error
    print("Error:", e)                                      # Error: card too short
t: str = "abc"                                              # immutable string
t2: str = t[:]                                              # full slice of a str
print(t2 is t)                                              # True (CPython reuses it)

# Output:
# ************1234
# True
# [4, 5, 6]
# [10]
# []
# abc.def.ghi
# None
# Error: card too short
# True
```

---

## 🟠 JavaScript vs Python Comparison

| Task | Python | JavaScript |
|------|--------|-----------|
| First 5 chars | `s[:5]` | `s.slice(0, 5)` |
| Last 4 chars | `s[-4:]` | `s.slice(-4)` |
| Reverse | `s[::-1]` | `s.split("").reverse().join("")` |
| Every 2nd char | `s[::2]` | manual loop |
| Out of range | empty string | empty string |

```python
# Python way — one syntax for everything
s: str = "FastAPI"                  # sample string
print(s[:4])                        # Fast
print(s[-3:])                       # API
print(s[::-1])                      # IPAtsaF
```
```javascript
// JavaScript way — different methods, no step support
const s = "FastAPI";                // sample string
console.log(s.slice(0, 4));         // Fast
console.log(s.slice(-3));           // API
console.log([...s].reverse().join(""));   // IPAtsaF
```

Key difference: JS `slice` has no `step`. Python slicing works on lists and tuples too, JS needs `Array.slice` separately. JS `substring(5, 2)` silently swaps arguments; Python `s[5:2]` just gives an empty string.

---

## 🟠 FastAPI Connection
In FastAPI you slice strings and lists constantly: parsing the `Authorization` header, building pagination (`skip` and `limit` query params), masking sensitive data in logs, and trimming long text before returning it.

```python
# FastAPI example — pagination with slicing
from fastapi import FastAPI, Query      # FastAPI + Query validation

app: FastAPI = FastAPI()                # create the app
USERS: list[str] = [f"user{i}" for i in range(1, 51)]   # fake in-memory data


@app.get("/users")                      # GET /users?skip=0&limit=5
def list_users(skip: int = Query(0, ge=0), limit: int = Query(10, le=100)) -> list[str]:
    return USERS[skip:skip + limit]     # slice = pagination, no IndexError ever
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting that `stop` is excluded
✅ Correct: use `stop = last index + 1`

```python
# Wrong — expecting 'Hello' (5 chars) but missing the last one
text = "Hello, World"
print(text[0:4])        # Hell  <- 'o' is at index 4, excluded!
# Right
print(text[0:5])        # Hello
```

❌ Mistake 2: Trying to change a string through a slice
✅ Correct: build a new string

```python
# Wrong — strings are immutable
name = "hello"
# name[0] = "H"         # TypeError: 'str' object does not support item assignment
# Right
name = "H" + name[1:]   # Hello (new string)
```

❌ Mistake 3: Using a positive step with start > stop
✅ Correct: use a negative step to go backwards

```python
# Wrong — returns empty string, no error
print("abcdef"[4:1])      # '' (empty)
# Right
print("abcdef"[4:1:-1])   # edc
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
s = "abcdef"
print(s[::-2])
print(s[-1:-4:-1])
print(s[10])
```
Answer: `s[::-2]` starts from the end and jumps 2 backwards: `fdb`. `s[-1:-4:-1]` goes from index -1 down to (not including) -4: `fed`. `s[10]` is a single-index access, NOT a slice, so it raises `IndexError: string index out of range`. Slices never raise IndexError, plain indexing does. (The first two lines print before the error.)

---

## ⚫ Interview Questions + Answers

Q1: What does `s[::-1]` do and how does it work?
A1: It returns the reversed string. `start` and `stop` are omitted, `step=-1` means walk from the last character to the first. When step is negative the defaults flip: start becomes the last index, stop becomes "before the first". Time complexity O(n), it creates a new string.

Q2: Does slicing copy the data? Does it change the original?
A2: Slicing a str, tuple, or list creates a NEW object (a shallow copy for lists). The original is never changed. For `bytes`, use `memoryview` if you want a zero-copy slice. Because strings are immutable, you can never modify a string via slice assignment.

Q3: Why does `s[100]` raise an error but `s[100:200]` does not?
A3: Single indexing needs one exact valid position, so invalid means IndexError. A slice is a range request; Python clips the range to valid bounds, so an out-of-range slice just gives an empty result. This is by design to make slicing code safe.

Q4: What is the difference between `s[:]` and `s`?
A4: For strings (immutable) CPython may return the same object, so `s[:] is s` is usually True. For lists, `l[:]` creates a shallow copy, so `l[:] is l` is False. That is why `l[:]` is a common idiom to copy a list.

Q5: What is a `slice` object?
A5: `slice(start, stop, step)` is a built-in object. `s[1:4]` is internally `s.__getitem__(slice(1, 4, None))`. You can store it in a variable and reuse it, e.g. for fixed-width file parsing: `NAME = slice(0, 10)`. `slice.indices(length)` gives the resolved bounds.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Taking a prefix, suffix, or middle part of a string
- Reversing a string or list quickly
- Pagination with `skip` and `limit`
- Parsing fixed-width data or headers like `Bearer <token>`

❌ Avoid when:
- Splitting by a separator — use `split()` or `partition()` (more readable)
- Removing known prefix/suffix — use `removeprefix()` / `removesuffix()` (clear intent)
- Parsing complex formats — use `re` or a proper parser
- Doing many repeated cuts in a huge string — each slice copies data (O(k) each)

---

## 📊 Visual Diagram
```
text = "PYTHON"

index:     0    1    2    3    4    5
         +----+----+----+----+----+----+
         | P  | Y  | T  | H  | O  | N  |
         +----+----+----+----+----+----+
negative: -6   -5   -4   -3   -2   -1

text[1:4]   -> "YTH"    (1,2,3 — 4 excluded)
text[:3]    -> "PYT"
text[3:]    -> "HON"
text[::2]   -> "PTO"
text[::-1]  -> "NOHTYP"

 start (included) ---> stop (excluded)   step = jump size
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Slice | Part of a sequence | Sequence का एक हिस्सा |
| Index | Position number of an item | Item की position का number |
| Negative index | Counts from the end (-1 = last) | आखिर से गिनना |
| Step / Stride | Jump size between items | कितने छोड़कर आगे बढ़ना |
| Immutable | Cannot be changed after creation | बनने के बाद बदल नहीं सकते |
| slice() | Built-in slice object | Slice का object |

---

## ⚡ 3-Line Summary
English: Slicing uses `text[start:stop:step]` — start included, stop excluded. Out-of-range slices are safe and return empty strings, but single index access raises IndexError. Slicing always creates a new string and works the same on lists and tuples.
Hindi: Slicing का syntax `text[start:stop:step]` है — start शामिल, stop शामिल नहीं। Range से बाहर का slice safe है (खाली string), लेकिन single index पर IndexError आता है। Slicing हमेशा नई string बनाती है और list/tuple पर भी वैसे ही चलती है।

---

## ➡️ Next Topic
**074. Multiline Strings** — triple quotes, raw strings, `textwrap.dedent`, and how to write SQL / prompts / emails cleanly in code.
