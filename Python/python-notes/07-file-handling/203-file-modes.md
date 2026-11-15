---

# 203. File Modes (r, w, a, rb, wb)
# हिंदी में: File Modes (file खोलने के तरीके)

---

## 🔵 Simple Definition (English)
A file mode is the short string given to `open()` that says what you may do with the file: read (`r`), write and erase (`w`), add at the end (`a`), create only if new (`x`), plus `b` for binary and `+` for read and write together. Wrong mode choice can erase your data.

## 🔵 सरल परिभाषा (Hindi)
File mode वह छोटी string है जो `open()` को दी जाती है और बताती है कि file के साथ क्या कर सकते हैं: पढ़ना (`r`), लिखना और मिटाना (`w`), अंत में जोड़ना (`a`), सिर्फ नई file बनाना (`x`), साथ में `b` binary के लिए और `+` पढ़ने-लिखने दोनों के लिए। गलत mode चुनने से data मिट सकता है।

---

## 🔴 Problem it Solves
Without modes, any code could read, overwrite or delete any file by accident. Modes state the intent, so the OS and Python can protect you: a file opened with `r` cannot be written, `x` refuses to overwrite, `a` never touches old content. Binary mode keeps images and PDFs from being damaged by text conversion.

## 🔴 यह क्यों बना? (Hindi)
Modes के बिना कोई भी code गलती से किसी भी file को पढ़, overwrite या delete कर सकता था। Mode आपका इरादा बताता है, इसलिए Python और OS आपकी रक्षा करते हैं: `r` से खुली file में लिख नहीं सकते, `x` overwrite करने से मना करता है, `a` पुराने content को नहीं छूता। Binary mode images और PDF को text conversion से खराब होने से बचाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick the main letter:  r (read) | w (write) | a (append) | x (exclusive create)
Step 2 → Pick the type:         t (text, default) or b (binary)
Step 3 → Optional +             adds the missing ability (read AND write)
Step 4 → open() applies it:     w/w+ TRUNCATE (erase) immediately on open
                                a/a+ always write at the END, seek is ignored for writes
                                r/r+ file must exist  | x fails if file exists
Step 5 → Text mode uses str, binary mode uses bytes (mixing -> TypeError)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → मुख्य अक्षर चुनें: r (पढ़ना) | w (लिखना) | a (जोड़ना) | x (नई बनाना)
Step 2 → type चुनें: t (text, default) या b (binary)
Step 3 → + लगाने पर दोनों काम (पढ़ना और लिखना)
Step 4 → w/w+ खुलते ही file खाली कर देता है; a/a+ हमेशा अंत में लिखता है
Step 5 → text में str, binary में bytes; मिलाने पर TypeError
```

---

## 🟡 Real World Example
Swiggy writes the day's order report with `"w"` (fresh file each day), but the live application log uses `"a"` so old lines stay. Razorpay's invoice generator opens PDFs with `"rb"` to attach to emails. A lock-file or payout-once guard uses `"x"` so two workers cannot create the same file. An AI app saves model weights with `"wb"`.

## 🟡 Real Example Hindi mein
Swiggy दिन की order report `"w"` से लिखता है (रोज़ नई file), पर live application log `"a"` से, ताकि पुरानी lines बनी रहें। Razorpay का invoice generator PDF को email में लगाने के लिए `"rb"` से पढ़ता है। Lock-file या payout-once guard `"x"` इस्तेमाल करता है ताकि दो workers एक ही file न बना सकें। AI app model weights `"wb"` से save करती है।

---

## 💻 Code Example — Basic
```python
# File modes - every line commented
import io  # for the UnsupportedOperation error type
import tempfile  # temporary folder
from pathlib import Path  # paths

d: Path = Path(tempfile.mkdtemp())  # empty temp folder
p: Path = d / "m.txt"  # test file

with open(p, "w", encoding="utf-8") as f:  # "w" creates the file or ERASES it
    f.write("one\ntwo\n")  # write two lines

with open(p, "a", encoding="utf-8") as f:  # "a" adds at the end
    f.write("three\n")  # old lines are kept
print(repr(p.read_text(encoding="utf-8")))  # read it back
# Output: 'one\ntwo\nthree\n'

with open(p, "w", encoding="utf-8") as f:  # opening with "w" ...
    pass  # ... and writing nothing still erases the file
print(repr(p.read_text(encoding="utf-8")), p.stat().st_size)  # now empty
# Output: '' 0

try:  # "x" = exclusive creation
    open(p, "x")  # file already exists
except FileExistsError:  # protects existing files
    print("FileExistsError")  # message
# Output: FileExistsError

try:  # "r" cannot write
    with open(p, "r") as f:  # read-only
        f.write("x")  # not allowed
except io.UnsupportedOperation as exc:  # error type
    print("UnsupportedOperation:", exc)  # message
# Output: UnsupportedOperation: not writable

with open(p, "wb") as f:  # "wb" = write bytes
    print(f.write(b"\x00\x01\xff"))  # returns number of bytes written
# Output: 3

with open(p, "rb") as f:  # "rb" = read bytes
    print(f.read())  # raw bytes
# Output: b'\x00\x01\xff'
```

## 💻 Code Example — Advanced
```python
# Production style: atomic write, r+/w+/a+ behaviour, mode mistakes
import os  # fsync and replace
import tempfile  # temp folder
from pathlib import Path  # paths


def atomic_write(path: Path, data: str) -> None:
    """Replace a file safely: a crash never leaves a half-written file."""
    tmp: Path = path.with_suffix(path.suffix + ".tmp")  # temp file beside target
    with open(tmp, "w", encoding="utf-8") as fh:  # write to the temp file
        fh.write(data)  # new content
        fh.flush()  # Python buffer -> OS
        os.fsync(fh.fileno())  # OS cache -> disk
    os.replace(tmp, path)  # atomic rename (same filesystem)


d: Path = Path(tempfile.mkdtemp())  # temp folder
p: Path = d / "m.txt"  # test file

p.write_text("abcdef")  # start with known content
with open(p, "r+", encoding="utf-8") as f:  # "r+" read AND write, no erase
    print(f.read(2))  # read 2 characters
    f.write("ZZ")  # where does this go? (see tricky question)
    f.seek(0)  # go to start
    print(f.read())  # whole content
# Output: ab
# Output: abcdefZZ

with open(p, "w+", encoding="utf-8") as f:  # "w+" erases, then read/write
    f.write("hello")  # write
    f.seek(0)  # rewind before reading
    print(f.read())  # read back
# Output: hello

with open(p, "a+", encoding="utf-8") as f:  # "a+" append and read
    print(repr(f.read()))  # position is at the end -> nothing to read
    f.seek(0)  # move to start for reading
    print(repr(f.read()))  # now we can read
    f.write("!")  # writes ALWAYS go to the end
# Output: ''
# Output: 'hello'
print(p.read_text())  # file content
# Output: hello!

# seek() does not change where append mode writes
p.write_text("abc")  # reset
with open(p, "a") as f:  # append mode
    f.seek(0)  # try to jump to the start
    f.write("X")  # still goes to the end
print(p.read_text())  # result
# Output: abcX

# Invalid combinations raise ValueError
try:  # two main modes
    open(p, "rw")  # not valid
except ValueError as exc:
    print("ValueError:", exc)  # message
# Output: ValueError: must have exactly one of create/read/write/append mode
try:  # text and binary together
    open(p, "rt+b")  # not valid
except ValueError as exc:
    print("ValueError:", exc)  # message
# Output: ValueError: can't have text and binary mode at once

atomic_write(p, "safe")  # safe replace
print(p.read_text(), sorted(x.name for x in d.iterdir()))  # no .tmp left behind
# Output: safe ['m.txt']
```
Verified on Python 3.13.3 (macOS).

---

## 🟠 JavaScript vs Python Comparison

```python
# Python way: mode string
open("a.txt", "w")     # write (erase)
open("a.txt", "a")     # append
open("a.txt", "x")     # create only
open("a.png", "rb")    # read bytes
```
```javascript
// JavaScript way: flags in Node.js fs
import fs from "node:fs";
fs.writeFileSync("a.txt", "data");                       // flag "w" (default)
fs.appendFileSync("a.txt", "more");                      // flag "a"
fs.writeFileSync("a.txt", "data", { flag: "wx" });       // "wx" = Python "x"
const buf = fs.readFileSync("a.png");                    // Buffer = bytes
```

Key differences: Node has the same letters but calls them `flag` (`"wx"` for exclusive create); Python uses `"x"` and has a separate `b` letter. Node returns text only if you pass an encoding, otherwise a `Buffer`; Python decides by `b` in the mode.

---

## 🟠 FastAPI Connection
Uploads arrive as bytes, so saving them uses `"wb"`. Use `"xb"` to refuse overwriting an existing file (for example two users uploading `photo.png`). Serving a file back with `FileResponse` internally reads it in binary mode.

```python
# FastAPI: refuse to overwrite an existing upload (pip install fastapi python-multipart)
import tempfile  # temp folder
from pathlib import Path  # paths
from fastapi import FastAPI, HTTPException, UploadFile  # framework

app: FastAPI = FastAPI()  # app
DIR: Path = Path(tempfile.mkdtemp())  # upload folder


@app.post("/files")  # POST /files
def save(file: UploadFile) -> dict[str, str]:
    name: str = Path(file.filename or "file").name  # strip any folders
    try:  # exclusive binary create
        with open(DIR / name, "xb") as out:  # fails if name exists
            out.write(file.file.read())  # write bytes
    except FileExistsError:  # duplicate upload
        raise HTTPException(status_code=409, detail="file exists")  # 409 Conflict
    return {"saved": name}  # JSON response
# Tested with TestClient: first upload -> 200, same name again -> 409.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Opening with `"w"` to "add" data
✅ Correct:

```python
# Wrong - erases the file at open time, even before write()
with open("log.txt", "w") as f:
    f.write("new entry\n")
# Right - append
with open("log.txt", "a", encoding="utf-8") as f:
    f.write("new entry\n")
```

❌ Mistake 2: Mixing str and bytes
✅ Correct:

```python
# Wrong
# open("a.bin", "wb").write("text")   -> TypeError: a bytes-like object is required, not 'str'
# open("a.txt", "w").write(b"x")      -> TypeError: write() argument must be str, not bytes
# Right
open("a.bin", "wb").write("text".encode("utf-8"))
open("a.txt", "w", encoding="utf-8").write("text")
```

❌ Mistake 3: Opening images/PDF in text mode
✅ Correct:

```python
# Wrong - decoding errors or silent corruption
open("photo.png").read()
# Right
open("photo.png", "rb").read()
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from pathlib import Path
p = Path("t.txt"); p.write_text("abcdef")
with open(p, "r+") as f:
    print(f.read(2))
    f.write("ZZ")
    f.seek(0)
    print(f.read())
with open(p, "a") as f:
    f.seek(0)
    f.write("X")
print(p.read_text())
```

**Answer**:
```
ab
abcdefZZ
abcdefZZX
```
In text mode `read(2)` actually pulls the whole small file into an internal buffer, so the OS position is already at the end and `ZZ` is appended, not written after `ab`. If you need to write at a position, call `f.seek(f.tell())` or `f.seek(2)` between read and write. In `"a"` mode every write goes to the end regardless of `seek`, so `X` is appended.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `w`, `a` and `x`?
A1: `w` creates or erases, `a` creates or appends, `x` creates but raises `FileExistsError` if the file is there.

Q2: What does `+` do?
A2: It adds the missing ability. `r+` reads and writes without erasing, `w+` erases then reads/writes, `a+` appends and reads.

Q3: When is data erased: at `open()` or at `write()`?
A3: At `open()`. `open(p, "w")` truncates immediately.

Q4: Text mode vs binary mode?
A4: Text mode decodes bytes to `str` with an encoding and translates newlines. Binary mode gives raw `bytes` with no changes, required for images, PDFs, zip, pickle.

Q5: How do you update a file safely?
A5: Write to a temp file, `flush()` and `os.fsync()`, then `os.replace(tmp, target)`. The rename is atomic, so readers see either old or new content.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- `r` for reading config/data, `w` for fresh exports, `a` for logs
- `x` for lock files and "create once" safety
- `rb`/`wb` for anything that is not plain text

❌ Avoid when:
- Using `w` on important files without a backup or atomic write
- Using `r+`/`w+` when simple read and write steps are clearer
- Text mode for binary files

---

## 📊 Visual Diagram

```
mode   file must exist?  erases on open?  write position   read?  write?
----   ----------------  ---------------  --------------   -----  ------
r      yes               no               -                yes    no
r+     yes               no               current          yes    yes
w      no (created)      YES              start            no     yes
w+     no (created)      YES              start            yes    yes
a      no (created)      no               always END       no     yes
a+     no (created)      no               always END       yes    yes
x      must NOT exist    -                start            no     yes
add b for bytes:  rb  wb  ab  xb
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Truncate | Cut the file to length 0 | file खाली करना |
| Append | Write after existing content | मौजूदा content के बाद लिखना |
| Binary mode | Raw bytes, no decoding | बिना decode के raw bytes |
| Atomic | All-or-nothing operation | या पूरा या कुछ नहीं |
| fsync | Force data onto disk | data को disk पर पक्का करना |
| Exclusive create | Fail if file already exists | file पहले से हो तो fail |

---

## ⚡ 3-Line Summary
English: `r` reads, `w` erases then writes, `a` adds at the end, `x` creates only new files; `b` means bytes and `+` allows read plus write. `w` truncates the moment you open. Use atomic write (temp file + `os.replace`) for important files.
Hindi: `r` पढ़ता है, `w` मिटाकर लिखता है, `a` अंत में जोड़ता है, `x` सिर्फ नई file बनाता है; `b` मतलब bytes और `+` पढ़ना-लिखना दोनों। `w` खोलते ही file खाली कर देता है। ज़रूरी files के लिए atomic write (temp file + `os.replace`) इस्तेमाल करें।

---

## ➡️ Next Topic
**204. read() vs readline() vs readlines()** — three ways to read, and which one is safe for huge files.
