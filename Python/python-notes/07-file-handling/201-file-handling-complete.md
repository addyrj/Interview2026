---

# 201. File Handling — Complete Guide
# हिंदी में: File Handling — पूरी Guide

---

## 🔵 Simple Definition (English)
File handling in Python means reading from and writing to files on disk. Python uses the built-in `open()` function with context managers (`with` statement) to safely work with files — context managers auto-close files even if an exception occurs. Key modes: `r` (read), `w` (write/overwrite), `a` (append), `b` (binary).

## 🔵 सरल परिभाषा (Hindi)
File handling = disk पर files पढ़ना और लिखना। Python `open()` function और `with` statement (context manager) use करता है। Context manager automatically file close करता है — even if exception आए। Key modes: `r` (read), `w` (write), `a` (append), `b` (binary)।

---

## 💻 Code Example — Basic
```python
# ─── Reading files ────────────────────────────────────────────────
# Always use 'with' — auto-closes file (even on exception):
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()        # read entire file as string

with open("data.txt", "r") as f:
    lines = f.readlines()     # read all lines as list (includes \n)
    # ['line1\n', 'line2\n', 'line3\n']

with open("data.txt", "r") as f:
    for line in f:            # memory-efficient: one line at a time
        print(line.strip())   # strip removes trailing \n

# readline() — read one line at a time:
with open("data.txt", "r") as f:
    first_line = f.readline()
    second_line = f.readline()

# ─── Writing files ────────────────────────────────────────────────
# 'w' — creates file if not exists, OVERWRITES if exists:
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Hello, World!\n")    # write string (no auto-newline)
    f.write("Second line\n")

# 'a' — append: adds to end of file, creates if not exists:
with open("log.txt", "a", encoding="utf-8") as f:
    f.write("New log entry\n")

# writelines() — write list of strings (no auto-newline!):
lines = ["line 1\n", "line 2\n", "line 3\n"]
with open("data.txt", "w") as f:
    f.writelines(lines)

# ─── File modes summary ───────────────────────────────────────────
# "r"   — read (default). Error if file doesn't exist.
# "w"   — write. Creates file. TRUNCATES (overwrites) if exists.
# "a"   — append. Creates file. Adds to end if exists.
# "x"   — exclusive create. Error if file already EXISTS.
# "r+"  — read and write. File must exist.
# "w+"  — read and write. Creates/truncates file.
# "rb"  — read binary (images, PDFs, etc.)
# "wb"  — write binary
# "ab"  — append binary

# ─── Checking file state ──────────────────────────────────────────
import os

print(os.path.exists("data.txt"))     # True if file/dir exists
print(os.path.isfile("data.txt"))     # True only if file (not dir)
print(os.path.isdir("data.txt"))      # True only if directory
print(os.path.getsize("data.txt"))    # file size in bytes
print(os.path.abspath("data.txt"))    # absolute path
```

## 💻 Code Example — Advanced
```python
import os
import json
import csv
from pathlib import Path

# ─── pathlib — modern path handling (preferred over os.path) ──────
path = Path("data") / "reports" / "2024.txt"  # OS-independent path
print(path)           # data/reports/2024.txt
print(path.name)      # '2024.txt'
print(path.stem)      # '2024' (name without extension)
print(path.suffix)    # '.txt'
print(path.parent)    # data/reports
print(path.exists())  # True/False

# Create directories:
path.parent.mkdir(parents=True, exist_ok=True)

# Read/write with pathlib:
path.write_text("Hello, pathlib!", encoding="utf-8")
content = path.read_text(encoding="utf-8")

# Find files by pattern:
for py_file in Path(".").glob("**/*.py"):
    print(py_file)

# ─── JSON file handling ───────────────────────────────────────────
data = {"name": "Priya", "age": 25, "skills": ["Python", "FastAPI"]}

# Write JSON to file:
with open("user.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Read JSON from file:
with open("user.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)
print(loaded["name"])   # "Priya"

# ─── CSV file handling ────────────────────────────────────────────
# Write CSV:
users = [
    {"name": "Priya", "age": 25, "city": "Mumbai"},
    {"name": "Raj", "age": 30, "city": "Delhi"},
]
with open("users.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "age", "city"])
    writer.writeheader()
    writer.writerows(users)

# Read CSV:
with open("users.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"], row["age"])   # rows as dicts

# ─── Binary files (images, PDFs) ─────────────────────────────────
# Copy a binary file:
def copy_file(src: str, dst: str) -> None:
    with open(src, "rb") as source:
        with open(dst, "wb") as dest:
            while chunk := source.read(8192):    # walrus: read 8KB chunks
                dest.write(chunk)

# Or use shutil:
import shutil
shutil.copy("source.jpg", "destination.jpg")
shutil.copy2("src.pdf", "dst.pdf")       # copy2 preserves metadata
shutil.move("old.txt", "new_location/")  # move (rename + move)

# ─── Temp files (don't pollute working dir) ───────────────────────
import tempfile

with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
    f.write("temp data")
    temp_path = f.name
print(f"Temp file: {temp_path}")
os.unlink(temp_path)    # manual cleanup when delete=False

# ─── Safe file write (atomic write pattern) ───────────────────────
# Prevents data loss if program crashes mid-write:
import tempfile

def safe_write(filepath: str, content: str) -> None:
    dir_path = os.path.dirname(os.path.abspath(filepath))
    with tempfile.NamedTemporaryFile(
        mode="w", dir=dir_path, delete=False, suffix=".tmp"
    ) as f:
        f.write(content)
        temp_path = f.name
    os.replace(temp_path, filepath)   # atomic on POSIX!
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python file handling:
# Sync (blocking) — fine for scripts, not FastAPI endpoints!
with open("data.json", "r") as f:
    data = json.load(f)

# Async file I/O with aiofiles:
import aiofiles

async def read_file_async(path: str) -> str:
    async with aiofiles.open(path, "r") as f:
        return await f.read()
```

```javascript
// JavaScript — async by default (Node.js fs):
import { readFile, writeFile } from 'fs/promises';

// Async/await:
const data = await readFile('data.json', 'utf8');
const parsed = JSON.parse(data);

// Streams for large files:
import { createReadStream } from 'fs';
const stream = createReadStream('large.txt');
```

Key differences:
- Python default `open()` is synchronous. Use `aiofiles` for async in FastAPI.
- JS `fs` is callback/Promise based by default.
- Python `with` statement = JS `finally { file.close() }` — both guarantee cleanup.
- `pathlib.Path` in Python is cleaner than Node's `path.join()`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `with` — file left open
```python
# Wrong — file might not close on exception:
f = open("data.txt", "r")
data = f.read()
f.close()  # skipped if read() raises exception

# Correct:
with open("data.txt", "r") as f:
    data = f.read()
# file auto-closed here, even on exception
```

❌ Mistake 2: Missing `encoding="utf-8"` for text files
```python
# Wrong — platform-dependent encoding (Windows may use cp1252):
with open("data.txt", "r") as f:
    data = f.read()

# Correct — explicit UTF-8:
with open("data.txt", "r", encoding="utf-8") as f:
    data = f.read()
```

---

## 🧠 Tricky Interview Question

**Q**: What is the difference between `f.read()`, `f.readlines()`, and iterating `for line in f:`?

**Answer**: `f.read()` reads the **entire file** into a single string — uses lots of memory for large files. `f.readlines()` reads **all lines** into a list — also loads entire file. `for line in f:` uses a **file iterator** — reads one line at a time, O(1) memory regardless of file size. For large files (logs, datasets), always use `for line in f:` or read in chunks with `f.read(8192)`.

---

## ⚫ Interview Questions + Answers

Q1: What happens if you open a file with `"w"` mode and the file already exists?
A1: The existing file is **truncated (emptied) immediately**, then written. Data is lost even if you don't write anything. To avoid accidental overwrites: use `"x"` mode (raises FileExistsError if file exists), check with `os.path.exists()` before opening, or use `"a"` to append. The atomic write pattern (write to temp file, then `os.replace`) is safest for critical data.

Q2: How do you handle large files (GB+) without loading into memory?
A2: Three approaches: (1) Iterate line by line: `for line in f:` — O(1) memory. (2) Read in chunks: `while chunk := f.read(8192): process(chunk)`. (3) `mmap` for random access: `with mmap.mmap(f.fileno(), 0) as m:` — memory-maps the file (OS handles paging). For CSV/JSON processing of large files: use pandas `read_csv(chunksize=10000)` or `ijson` for streaming JSON parsing.

Q3: What is the difference between `os.path` and `pathlib`?
A3: `os.path` uses string functions: `os.path.join("a","b","c")`. `pathlib` uses OOP: `Path("a") / "b" / "c"`. Both work cross-platform. `pathlib` is more readable and modern (Python 3.4+). `Path.glob("**/*.py")` is cleaner than `os.walk()`. `path.read_text()` replaces `open().read()`. Most new code should use `pathlib`. `os.path` is still valid for compatibility.

Q4: How do you read a JSON file in Python?
A4: `import json; data = json.load(open("file.json"))` — but always use `with`: `with open("file.json", encoding="utf-8") as f: data = json.load(f)`. For async FastAPI: `import aiofiles; async with aiofiles.open("file.json") as f: content = await f.read(); data = json.loads(content)`. For large JSON: use `ijson` library for streaming parsing.

Q5: What is `newline=""` in CSV writing and why is it needed?
A5: On Windows, Python's text mode translates `\n` → `\r\n`. The CSV module also adds `\r\n`. Without `newline=""`, you get double `\r\r\n` — blank rows between CSV lines! `newline=""` disables Python's automatic translation, letting `csv` module control line endings. Always use `newline=""` when opening files for `csv.writer` or `csv.DictWriter`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| open() | Built-in to open files | Files खोलने का built-in |
| mode | r/w/a/b — how to open | कैसे खोलें |
| context manager | `with` — auto-close | `with` — auto-close |
| encoding | Text encoding (utf-8) | Text encoding |
| pathlib | Modern OOP file paths | Modern OOP file paths |
| truncate | Clear file on `w` open | `w` mode पर file clear |
| aiofiles | Async file I/O | Async file I/O |

---

## ⚡ 3-Line Summary
English: Always use `with open(...)` — context manager guarantees file close even on exceptions. Specify `encoding="utf-8"` for text files to avoid platform encoding bugs. Use `pathlib.Path` for path manipulation and `for line in f:` for memory-efficient large file reading.
Hindi: हमेशा `with open(...)` use करो — exception पर भी file close होगी। Text files के लिए `encoding="utf-8"` specify करो। Large files के लिए `for line in f:` use करो — memory efficient है।

---

## ➡️ Next Topic
**208. JSON Handling** — json.load, json.dump, custom serializers. **210. pathlib Deep Dive** — complete Path API. **215. Pickle** — Python object serialization.
