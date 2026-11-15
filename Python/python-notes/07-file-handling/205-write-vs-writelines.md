---

# 205. write() vs writelines()
# हिंदी में: write() बनाम writelines()

---

## 🔵 Simple Definition (English)
`write(s)` writes ONE string and returns how many characters it wrote. `writelines(iterable)` writes MANY strings one after another from a list or generator. Neither adds a newline for you. Both accept only `str` in text mode (`bytes` in binary mode).

## 🔵 सरल परिभाषा (Hindi)
`write(s)` एक string लिखता है और बताता है कि कितने characters लिखे। `writelines(iterable)` list या generator की कई strings एक के बाद एक लिखता है। दोनों में से कोई भी अपने आप newline नहीं जोड़ता। Text mode में सिर्फ `str` चलता है (binary में `bytes`)।

---

## 🔴 Problem it Solves
Programs must save results: reports, logs, exports. Writing one big string requires joining everything in memory first. `write()` lets you write piece by piece, and `writelines()` writes a whole collection in one call, so you can stream results without building a giant string.

## 🔴 यह क्यों बना? (Hindi)
Programs को results save करने होते हैं: reports, logs, exports। एक बड़ी string लिखने के लिए पहले सब कुछ memory में जोड़ना पड़ता है। `write()` टुकड़ों में लिखने देता है और `writelines()` पूरा collection एक call में लिखता है, इसलिए बिना विशाल string बनाए results stream कर सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → open(path, "w") gives a writable file object (file is erased)
Step 2 → f.write("text") puts text in the buffer, returns len(text)
Step 3 → f.writelines(items) loops over items and calls write() for each
Step 4 → NO "\n" is added by either method - you add it yourself
Step 5 → Data reaches disk on flush() / close() / leaving the with block
Step 6 → Non-str item -> TypeError (convert with str() or f-strings)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → open(path, "w") writable file object देता है (file खाली हो जाती है)
Step 2 → f.write("text") text को buffer में रखता है और len(text) लौटाता है
Step 3 → f.writelines(items) items पर loop चलाकर हर एक के लिए write() करता है
Step 4 → दोनों में "\n" अपने आप नहीं जुड़ता - आपको जोड़ना है
Step 5 → Data disk पर flush() / close() / with block से निकलने पर पहुँचता है
Step 6 → str के अलावा कुछ और दिया तो TypeError (str() या f-string इस्तेमाल करें)
```

---

## 🟡 Real World Example
A Razorpay settlement job writes one line per transaction using `write(f"{txn_id},{amount}\n")` while looping over the database cursor. A Swiggy analytics script collects error messages in a list, then dumps them with `writelines(line + "\n" for line in errors)`. An AI app writes JSON Lines (`.jsonl`) training data, one JSON object per line.

## 🟡 Real Example Hindi mein
Razorpay का settlement job database cursor पर loop चलाते हुए हर transaction के लिए `write(f"{txn_id},{amount}\n")` लिखता है। Swiggy की analytics script errors की list बनाकर `writelines(line + "\n" for line in errors)` से file में डालती है। AI app training data JSON Lines (`.jsonl`) में लिखती है, हर line पर एक JSON object।

---

## 💻 Code Example — Basic
```python
# write() vs writelines() - every line commented
import tempfile  # temp folder
from pathlib import Path  # paths

d: Path = Path(tempfile.mkdtemp())  # temporary directory
p: Path = d / "w.txt"  # file to write

with open(p, "w", encoding="utf-8") as f:  # open for writing
    n: int = f.write("hello\n")  # write returns the number of characters
    print(n)  # includes the \n
# Output: 6
    print(f.write("नमस्ते"))  # characters, NOT bytes
# Output: 6
print(p.stat().st_size)  # bytes on disk: 6 + 18 (3 bytes per Hindi letter)
# Output: 24

with open(p, "w") as f:  # reopen (erases old content)
    f.writelines(["a", "b", "c"])  # NO newline added between items
print(repr(p.read_text()))  # all glued together
# Output: 'abc'

with open(p, "w") as f:  # reopen
    f.writelines(x + "\n" for x in ["a", "b"])  # add the newline yourself (generator is fine)
print(repr(p.read_text()))  # two lines
# Output: 'a\nb\n'

with open(p, "w") as f:  # print() can also write to a file
    print("hi", "there", sep="-", file=f)  # print adds the newline for you
    print("x", file=f)  # another line
print(repr(p.read_text()))  # content
# Output: 'hi-there\nx\n'

try:  # write needs str
    with open(p, "w") as f:  # open
        f.write(42)  # int is not allowed
except TypeError as exc:  # TypeError
    print("TypeError:", exc)  # message
# Output: TypeError: write() argument must be str, not int

with open(p, "w") as f:  # convert first
    f.write(str(42) + "\n")  # int -> str
    f.write(f"{3.5}\n")  # f-string conversion
print(repr(p.read_text()))  # content
# Output: '42\n3.5\n'
```

## 💻 Code Example — Advanced
```python
# Production style: streaming writer, JSON Lines, buffer flush, redirect
import json  # for JSON Lines
import tempfile  # temp folder
from contextlib import redirect_stdout  # send print() to a file
from pathlib import Path  # paths
from typing import Any, Dict, Iterable, List  # type hints


def write_lines(path: Path, lines: Iterable[str]) -> int:
    """Write each item as one line; returns the line count."""
    count: int = 0  # how many lines written
    with open(path, "w", encoding="utf-8", newline="\n") as fh:  # \n on every OS
        for line in lines:  # works with a generator, so memory stays small
            fh.write(line.rstrip("\n") + "\n")  # exactly one newline per line
            count += 1  # count it
    return count  # report


def append_jsonl(path: Path, records: Iterable[Dict[str, Any]]) -> None:
    """Append records as JSON Lines (one JSON object per line)."""
    with open(path, "a", encoding="utf-8") as fh:  # append keeps old rows
        for rec in records:  # each record
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")  # one object per line


d: Path = Path(tempfile.mkdtemp())  # temp folder
p: Path = d / "out.txt"  # output file

total: int = write_lines(p, (f"row {i}" for i in range(3)))  # generator input
print(total, repr(p.read_text()))  # count and content
# Output: 3 'row 0\nrow 1\nrow 2\n'

append_jsonl(p, [{"id": 1}, {"id": 2}])  # add two JSON lines
tail: List[str] = p.read_text().splitlines()[-2:]  # last two lines
print(tail)  # JSON text lines
# Output: ['{"id": 1}', '{"id": 2}']

# Buffering: data may not be on disk until flush()
f = open(p, "w")  # open without with, on purpose
f.write("data")  # goes to the buffer
print(p.stat().st_size)  # disk still shows 0 bytes
# Output: 0
f.flush()  # push buffer to the OS
print(p.stat().st_size)  # now 4 bytes
# Output: 4
f.close()  # close properly

# redirect_stdout: every print() inside goes to the file
with open(p, "w") as f2, redirect_stdout(f2):  # two context managers
    print("captured")  # not shown on screen
print(repr(p.read_text()))  # it is in the file
# Output: 'captured\n'

# writelines with a plain str iterates characters (it is an iterable of 1-char strings)
with open(p, "w") as f3:  # open
    f3.writelines("abc")  # same as write("abc")
print(repr(p.read_text()))  # content
# Output: 'abc'
```
Verified on Python 3.13.3 (the size values in the buffer demo are for a short write; the buffer is flushed automatically once it grows past about 8 KB).

---

## 🟠 JavaScript vs Python Comparison

```python
# Python way
with open("out.txt", "w", encoding="utf-8") as f:
    f.write("line 1\n")
    f.writelines(f"row {i}\n" for i in range(3))
with open("out.txt", "a", encoding="utf-8") as f:
    f.write("appended\n")
```
```javascript
// JavaScript way (Node.js)
import { writeFileSync, appendFileSync, createWriteStream } from "node:fs";
writeFileSync("out.txt", "line 1\n");                              // like write (replaces file)
appendFileSync("out.txt", ["row 0", "row 1"].join("\n") + "\n");   // join instead of writelines
const ws = createWriteStream("big.txt");                           // streaming, like repeated write()
ws.write("a\n"); ws.end();
```

Key differences: Node's `writeFileSync` replaces the whole file in one call; Python lets you keep the file open and call `write()` many times. JS has no `writelines`, you `join`. Python's `write` returns the number of characters, JS returns nothing.

---

## 🟠 FastAPI Connection
Background tasks often write reports, audit logs or exported CSV/JSONL files after returning the response. Use `BackgroundTasks` so the client does not wait. The file writing function is plain Python using `write()`.

```python
# FastAPI: write an audit line in a background task (pip install fastapi)
import tempfile  # temp folder
from pathlib import Path  # paths
from fastapi import BackgroundTasks, FastAPI  # framework

app: FastAPI = FastAPI()  # app
AUDIT: Path = Path(tempfile.mkdtemp()) / "audit.log"  # audit file


def write_audit(user: str, action: str) -> None:
    with open(AUDIT, "a", encoding="utf-8") as fh:  # append mode keeps history
        fh.write(f"{user},{action}\n")  # one line per event


@app.post("/pay")  # POST /pay
def pay(user: str, tasks: BackgroundTasks) -> dict[str, str]:
    tasks.add_task(write_audit, user, "payment")  # runs after response is sent
    return {"status": "ok"}  # client gets this immediately
# Not run as a server in this note; write_audit is plain file code (same as the examples above, which were run).
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting `writelines()` to add newlines
✅ Correct:

```python
rows = ["a", "b", "c"]
# Wrong - file contains 'abc'
f.writelines(rows)
# Right
f.writelines(r + "\n" for r in rows)
```

❌ Mistake 2: Writing numbers or lists without converting
✅ Correct:

```python
# Wrong - TypeError: write() argument must be str, not int
f.write(42)
# Right
f.write(str(42))
f.write(f"{amount:.2f}\n")
```

❌ Mistake 3: Not closing, so data is lost on a crash
✅ Correct:

```python
# Wrong - buffer may never reach disk
f = open("out.txt", "w"); f.write("important")
# Right - with closes and flushes
with open("out.txt", "w", encoding="utf-8") as f:
    f.write("important")
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
with open("t.txt", "w", encoding="utf-8") as f:
    print(f.write("नमस्ते"))
    f.writelines(["a", "b"])
    f.writelines("cd")
    f.write("e", "f")
```

**Answer**:
```
6
TypeError: TextIOWrapper.write() takes exactly one argument (2 given)
```
`write()` returns the number of characters (6), not bytes (18). `writelines` adds no newline, so the file has `नमस्तेabcd` before the error. `write("e", "f")` raises `TypeError` because `write` takes exactly one argument; the exact message differs by version (shown for Python 3.13). The `with` block still closes the file, so earlier text is saved.

---

## ⚫ Interview Questions + Answers

Q1: Does `writelines()` add newlines?
A1: No. Add `"\n"` yourself. The name is misleading; it writes an iterable of strings.

Q2: What does `write()` return?
A2: The number of characters written (text mode) or bytes (binary mode).

Q3: Is `writelines` faster than a loop of `write`?
A3: Slightly, because the loop runs in C, but the difference is small. Readability matters more.

Q4: How do you write a dict or number to a file?
A4: Convert it: `str(x)`, an f-string, or `json.dumps(obj)` for structured data.

Q5: Why is my file empty even though I called `write()`?
A5: The data is still in the buffer. Call `flush()`/`close()` or use `with`. Also check you did not open with `"w"` again, which erases the file.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- `write()`: one chunk or one line at a time (streaming)
- `writelines()`: you already have an iterable of ready-made lines
- `print(..., file=f)`: you want automatic newlines and separators

❌ Avoid when:
- Writing structured data by hand: use `csv` / `json` modules
- Concurrent writers to the same file without a lock (lines may interleave)
- Large exports built into one giant string first

---

## 📊 Visual Diagram

```
write("a\n")  ------->  [ buffer: a\n ]
write("b\n")  ------->  [ buffer: a\nb\n ]
writelines(["c\n","d\n"]) -> [ buffer: a\nb\nc\nd\n ]
                              |
              flush() / close() / end of with
                              v
                         [ disk: a b c d ]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| write | Write one string | एक string लिखना |
| writelines | Write an iterable of strings | strings का iterable लिखना |
| Buffer | Temporary memory before disk | disk से पहले की अस्थायी memory |
| flush | Push buffer out now | buffer अभी बाहर भेजना |
| JSON Lines | One JSON object per line | हर line पर एक JSON object |
| Newline | Line break character \n | नई line का character |

---

## ⚡ 3-Line Summary
English: `write()` writes one string and returns its length; `writelines()` writes many strings but adds no newlines. Convert non-strings with `str()`/f-strings. Use `with` so the buffer is flushed and the file closed.
Hindi: `write()` एक string लिखता है और उसकी length लौटाता है; `writelines()` कई strings लिखता है पर newline नहीं जोड़ता। Non-strings को `str()`/f-string से बदलें। Buffer flush और file close के लिए `with` इस्तेमाल करें।

---

## ➡️ Next Topic
**206. with Statement for Files** — why context managers guarantee the file is closed.
