---

# 202. open() Function
# हिंदी में: open() Function (file खोलना)

---

## 🔵 Simple Definition (English)
`open(path, mode, encoding=...)` is the built-in function that opens a file and returns a file object. You use that object to read or write. Text mode returns `str`; binary mode returns `bytes`. You must close the file (best done with `with`).

## 🔵 सरल परिभाषा (Hindi)
`open(path, mode, encoding=...)` built-in function है जो file खोलकर एक file object देता है। उसी object से पढ़ते या लिखते हैं। Text mode में `str` मिलता है, binary mode में `bytes`। File बंद करना ज़रूरी है (`with` सबसे अच्छा तरीका है)।

---

## 🔴 Problem it Solves
Programs need data that survives after they stop: logs, uploads, config, exports. Talking to disk directly is OS-specific (file descriptors, buffers, newline styles, character encodings). `open()` hides all of that behind one simple object with the same API on Windows, Linux and macOS.

## 🔴 यह क्यों बना? (Hindi)
Programs को ऐसा data चाहिए जो बंद होने के बाद भी रहे: logs, uploads, config, exports। Disk से सीधे बात करना OS पर निर्भर है (file descriptors, buffers, newline styles, encodings)। `open()` यह सब एक आसान object के पीछे छिपाता है, और API Windows, Linux, macOS पर एक जैसी रहती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → open("a.txt", "w", encoding="utf-8") asks the OS for a file handle
Step 2 → Mode decides rights: read / write / append / binary / create
Step 3 → Python wraps the handle: FileIO -> BufferedReader/Writer -> TextIOWrapper
Step 4 → read()/write() work on a memory buffer (fast), flushed to disk later
Step 5 → close() flushes the buffer and returns the handle to the OS
Step 6 → Any use after close -> ValueError: I/O operation on closed file
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → open() OS से file handle माँगता है
Step 2 → Mode तय करता है: read / write / append / binary / create
Step 3 → Python handle को परतों में लपेटता है: FileIO -> Buffered -> TextIOWrapper
Step 4 → read()/write() पहले memory buffer में चलते हैं, बाद में disk पर जाते हैं
Step 5 → close() buffer flush करके handle OS को लौटा देता है
Step 6 → close के बाद इस्तेमाल करने पर ValueError आता है
```

---

## 🟡 Real World Example
A Swiggy order service appends each order to a daily `orders-2026-01-31.log`. Razorpay's settlement job opens a CSV in `"w"` mode every night. A RAG pipeline opens thousands of PDF files with `"rb"` to extract text and embed it. A FastAPI upload endpoint saves the user's image with `open(path, "wb")`.

## 🟡 Real Example Hindi mein
Swiggy की order service हर order को रोज़ की `orders-2026-01-31.log` file में append करती है। Razorpay का settlement job हर रात CSV को `"w"` mode में खोलता है। RAG pipeline हज़ारों PDF को `"rb"` से खोलकर text निकालती है। FastAPI upload endpoint user की image `open(path, "wb")` से save करता है।

---

## 💻 Code Example — Basic
```python
# Basic open() - every line commented
import tempfile  # to get a safe temporary folder
from pathlib import Path  # path handling

folder: Path = Path(tempfile.mkdtemp())  # new empty temp directory
path: Path = folder / "a.txt"  # file path inside it

f = open(path, "w", encoding="utf-8")  # open for writing (creates the file)
print(type(f).__name__, f.mode, f.closed, f.encoding)  # inspect the object
# Output: TextIOWrapper w False utf-8

f.write("नमस्ते\nline2\n")  # write text (Hindi is fine with utf-8)
f.close()  # flush and release the file
print(f.closed)  # now it is closed
# Output: True

try:  # using a closed file is an error
    f.write("x")  # not allowed
except ValueError as exc:  # ValueError
    print("ValueError:", exc)  # show message
# Output: ValueError: I/O operation on closed file.

print(path.stat().st_size)  # size in BYTES, not characters
# Output: 25   (Hindi letters take 3 bytes each in utf-8)

with open(path, encoding="utf-8") as g:  # default mode is "r"
    print(repr(g.read()))  # read the whole file
# Output: 'नमस्ते\nline2\n'

try:  # opening a missing file
    open(folder / "nope.txt")  # does not exist
except FileNotFoundError as exc:  # specific error
    print("FileNotFoundError errno:", exc.errno)  # errno 2
# Output: FileNotFoundError errno: 2

b = open(path, "rb")  # binary mode
print(type(b).__name__, b.read(3))  # first 3 raw bytes
# Output: BufferedReader b'\xe0\xa4\xa8'
b.close()  # always close
```

## 💻 Code Example — Advanced
```python
# Production style: explicit encoding, error handling, parameters
import os  # low level file descriptors
import tempfile  # temp folder
from pathlib import Path  # paths
from typing import Optional  # type hints


def read_text_safe(path: Path, default: Optional[str] = None) -> Optional[str]:
    """Return file text, or default when the file is missing or unreadable."""
    try:  # all risky work inside try
        with open(path, "r", encoding="utf-8") as fh:  # always give encoding
            return fh.read()  # whole content
    except FileNotFoundError:  # no such file
        return default  # use fallback
    except IsADirectoryError:  # path is a folder
        return default  # use fallback
    except PermissionError:  # not allowed to read
        raise  # let the caller decide
    except UnicodeDecodeError as exc:  # file is not valid utf-8
        raise ValueError(f"{path} is not utf-8: {exc.reason}") from exc  # clear error


folder: Path = Path(tempfile.mkdtemp())  # temp dir
target: Path = folder / "data.txt"  # file path
print(read_text_safe(target, "missing"))  # file does not exist yet
# Output: missing

# newline="" or "\n" stops Windows from changing \n to \r\n
with open(target, "w", encoding="utf-8", newline="\n") as out:  # write
    out.write("a\nb")  # two lines
print(target.read_bytes())  # raw bytes: exactly \n, no \r
# Output: b'a\nb'

# buffering=0 is only allowed in binary mode and gives an unbuffered FileIO
raw = open(target, "rb", buffering=0)  # no Python buffer
print(type(raw).__name__)  # FileIO
# Output: FileIO
raw.close()  # close

# encoding is NOT allowed in binary mode
try:  # wrong combination
    open(target, "rb", encoding="utf-8")  # invalid
except ValueError as exc:  # ValueError
    print("ValueError:", exc)  # message
# Output: ValueError: binary mode doesn't take an encoding argument

# open() also accepts an integer file descriptor
fd: int = os.open(target, os.O_RDONLY)  # low level open
with open(fd, closefd=True) as fh2:  # wrap the descriptor
    print(fh2.read()[:1])  # first character
# Output: a

# opening a folder fails
try:  # directory, not a file
    open(folder)  # invalid
except IsADirectoryError:  # POSIX error (Windows raises PermissionError)
    print("IsADirectoryError")  # confirm
# Output: IsADirectoryError
```
Verified on Python 3.13.3 (macOS). Default encoding without `encoding=` depends on the OS (locale); Python 3.15 is planned to make UTF-8 the default (PEP 686). Always pass `encoding="utf-8"`.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python way
with open("notes.txt", "r", encoding="utf-8") as f:   # auto close
    text = f.read()
with open("out.txt", "w", encoding="utf-8") as f:
    f.write(text.upper())
```
```javascript
// JavaScript way (Node.js)
import { readFileSync, writeFileSync } from "node:fs";
const text = readFileSync("notes.txt", "utf-8");        // whole file at once
writeFileSync("out.txt", text.toUpperCase(), "utf-8");
// Async: await fs.promises.readFile("notes.txt", "utf-8")
// Streams: fs.createReadStream(path)  ~  iterating a Python file object
```

Key differences: Python uses one function `open()` and a mode string (`r/w/a/b`); Node has separate functions (`readFile`, `writeFile`, `appendFile`). A Python file object is already an iterator (line by line), and `with` closes it, like `try/finally`.

---

## 🟠 FastAPI Connection
FastAPI's `UploadFile` wraps a spooled temporary file. To save an upload permanently you `open(path, "wb")` and write chunks. A plain `open()` blocks the event loop, so for big files use `def` endpoints (run in a thread pool) or `aiofiles`.

```python
# FastAPI: save an upload to disk (pip install fastapi python-multipart)
import tempfile  # safe upload folder
from pathlib import Path  # paths
from typing import Dict  # type hints
from fastapi import FastAPI, UploadFile  # framework

app: FastAPI = FastAPI()  # app
UPLOAD_DIR: Path = Path(tempfile.mkdtemp())  # where files go


@app.post("/upload")  # POST /upload
def upload(file: UploadFile) -> Dict[str, int]:  # sync def -> thread pool
    target: Path = UPLOAD_DIR / Path(file.filename or "x").name  # .name blocks ../ tricks
    size: int = 0  # bytes written
    with open(target, "wb") as out:  # binary write
        while chunk := file.file.read(1024 * 1024):  # 1 MB at a time
            out.write(chunk)  # write chunk
            size += len(chunk)  # count bytes
    return {"bytes": size}  # JSON response
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Not closing the file
✅ Correct:

```python
# Wrong - if write() fails, close() never runs
f = open("a.txt", "w"); f.write("x"); f.close()
# Right - with always closes
with open("a.txt", "w", encoding="utf-8") as f:
    f.write("x")
```

❌ Mistake 2: Forgetting `encoding`
✅ Correct:

```python
# Wrong - uses the OS default; Hindi text may break on Windows (cp1252)
open("a.txt", "w").write("नमस्ते")
# Right
open("a.txt", "w", encoding="utf-8").write("नमस्ते")
```

❌ Mistake 3: Using `"w"` when you meant `"a"` (data loss)
✅ Correct:

```python
# Wrong - erases the whole log file every time
open("app.log", "w").write("new line\n")
# Right - add to the end
open("app.log", "a", encoding="utf-8").write("new line\n")
# Or use "x" to fail if the file already exists
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
f = open("t.txt", "w", encoding="utf-8")
f.write("hello")
print(open("t.txt", encoding="utf-8").read() == "")
f.close()
print(open("t.txt", encoding="utf-8").read())
```

**Answer**:
```
True
hello
```
`write()` goes into a buffer first, not directly to disk. Until `flush()` or `close()`, another reader sees an empty file. After `close()` the data is on disk. This is why unclosed files can lose data. (Typical result with a small write; buffer size is about 8 KB so larger writes may appear earlier.)

---

## ⚫ Interview Questions + Answers

Q1: What does `open()` return?
A1: A file object: `TextIOWrapper` in text mode, `BufferedReader`/`BufferedWriter` in binary mode, `FileIO` when `buffering=0`.

Q2: Which errors can `open()` raise?
A2: `FileNotFoundError`, `PermissionError`, `IsADirectoryError`, `FileExistsError` (mode `"x"`), all subclasses of `OSError`; plus `ValueError` for bad argument combinations.

Q3: Why pass `encoding="utf-8"`?
A3: Without it Python uses the locale encoding, so the same code behaves differently on Windows and Linux. `python -X warn_default_encoding` (3.10+) warns you.

Q4: What is `newline` for?
A4: It controls translation of `\n`. In read mode the default converts `\r\n` to `\n`. For CSV files use `newline=""`.

Q5: Is there a limit on open files?
A5: Yes, the OS limits file descriptors per process (`ulimit -n`). A server that forgets to close files eventually fails with `OSError: Too many open files`.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Reading or writing text/binary files directly
- Appending to logs, exporting reports
- You need fine control over mode, encoding and buffering

❌ Avoid when:
- A one-liner is enough: `Path.read_text()` / `write_text()`
- Structured data: use `csv`, `json` modules
- Blocking the async event loop with very large files (use threads or `aiofiles`)

---

## 📊 Visual Diagram

```
Your code      open()                  Python layers              OS
---------   -----------   ------------------------------------   ------
f.write() -> TextIOWrapper -> BufferedWriter (8 KB buffer) -> FileIO -> disk
             (str<->bytes)       (memory)                     (fd=5)
f.close() or flush() pushes the buffer down to disk
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| File object | Handle returned by open() | open() से मिला handle |
| Mode | r, w, a, x, b, + options | file खोलने का तरीका |
| Encoding | How text maps to bytes (utf-8) | text से bytes बनाने का तरीका |
| Buffer | Memory area before disk write | disk से पहले की memory |
| File descriptor | Number the OS gives the file | OS द्वारा दिया गया file number |
| Flush | Push buffer data to disk | buffer का data disk पर भेजना |

---

## ⚡ 3-Line Summary
English: `open()` returns a file object; text mode gives `str`, binary mode gives `bytes`. Always pass `encoding="utf-8"` and use `with` so the file is closed. Writes are buffered until flush or close.
Hindi: `open()` file object देता है; text mode में `str`, binary में `bytes`। हमेशा `encoding="utf-8"` दें और `with` इस्तेमाल करें ताकि file बंद हो। Writes flush या close तक buffer में रहती हैं।

---

## ➡️ Next Topic
**203. File Modes (r, w, a, rb, wb)** — what each mode does and when data gets erased.
