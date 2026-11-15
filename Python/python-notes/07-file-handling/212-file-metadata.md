---

# 212. File Metadata
# हिंदी में: File Metadata (फ़ाइल की जानकारी: size, समय, permissions)

---

## 🔵 Simple Definition (English)
File metadata is data ABOUT a file, not its content: size, type, permissions, owner, and created/modified/accessed times. In Python you read it with `os.stat()` or `pathlib.Path.stat()`, which make one system call and return an `os.stat_result` object.

## 🔵 सरल परिभाषा (Hindi)
File metadata फ़ाइल के content के बारे में नहीं, फ़ाइल के "बारे में" जानकारी है: size, type, permissions, owner और बनने/बदलने/खोलने का समय। Python में इसे `os.stat()` या `pathlib.Path.stat()` से पढ़ते हैं, जो एक system call करके `os.stat_result` object देता है।

---

## 🔴 Problem it Solves
To know how big a file is, when it changed, or whether you may read it, you used to open and read the whole file or shell out to `ls`. That is slow and not portable. `stat` asks the operating system directly, without reading any content, so checking a 5 GB video costs the same as checking a 5 byte note.

## 🔴 यह क्यों बना? (Hindi)
फ़ाइल कितनी बड़ी है, कब बदली या पढ़ने की permission है या नहीं, यह जानने के लिए पहले पूरी फ़ाइल खोलकर पढ़नी पड़ती या `ls` shell command चलानी पड़ती, जो धीमा और non-portable है। `stat` सीधे operating system से पूछता है, content पढ़े बिना, इसलिए 5 GB की video और 5 byte का note जाँचने में लगभग बराबर समय लगता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build a Path (pathlib) or use a string path
Step 2 → Call path.stat() / os.stat(path) -> ONE system call
Step 3 → Get os.stat_result: st_size, st_mtime, st_mode, st_uid ...
Step 4 → Decode: stat.S_ISREG(st_mode), mode & 0o777, datetime.fromtimestamp(st_mtime)
Step 5 → lstat() does the same but does NOT follow symlinks
Step 6 → Missing file -> FileNotFoundError, no permission -> PermissionError
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Path (pathlib) बनाओ या string path लो
Step 2 → path.stat() / os.stat(path) -> सिर्फ़ एक system call
Step 3 → os.stat_result मिलता है: st_size, st_mtime, st_mode, st_uid ...
Step 4 → Decode करो: stat.S_ISREG(st_mode), mode & 0o777, datetime.fromtimestamp(st_mtime)
Step 5 → lstat() वही करता है पर symlink को follow नहीं करता
Step 6 → फ़ाइल न हो तो FileNotFoundError, permission न हो तो PermissionError
```

---

## 🟡 Real World Example
Swiggy's invoice service must delete exports older than 7 days from disk, so a cleanup job checks `st_mtime` of each file. A backup tool compares size and mtime to decide which files changed (like rsync). A FastAPI download endpoint returns `Content-Length` and `Last-Modified` headers from `stat()`. An upload service refuses files above 10 MB by checking `st_size` first.

## 🟡 Real Example Hindi mein
Swiggy की invoice service को 7 दिन से पुराने exports delete करने होते हैं, इसलिए cleanup job हर फ़ाइल का `st_mtime` देखती है। Backup tool size और mtime की तुलना करके तय करता है कि कौन सी फ़ाइलें बदलीं (rsync की तरह)। FastAPI download endpoint `stat()` से `Content-Length` और `Last-Modified` headers भेजता है। Upload service 10 MB से बड़ी फ़ाइल `st_size` देखकर पहले ही reject कर देती है।

---

## 💻 Code Example — Basic
```python
# Basic: file metadata with os.stat and pathlib
import os  # os module for stat
import time  # to format timestamps
from pathlib import Path  # modern path API
import tempfile  # a safe temp folder for the demo

with tempfile.TemporaryDirectory() as tmp:  # temp folder, auto-deleted
    p: Path = Path(tmp) / "report.txt"  # build a path
    p.write_text("hello world", encoding="utf-8")  # create 11-byte file
    st: os.stat_result = p.stat()  # one system call returns all metadata
    print(st.st_size)  # size in bytes
    print(p.exists(), p.is_file(), p.is_dir())  # type checks
    print(p.suffix, p.stem, p.name)  # name parts
    print(time.strftime("%Y", time.localtime(st.st_mtime)) >= "2024")  # mtime is a float of seconds since epoch
    print(oct(st.st_mode & 0o777))  # permission bits
    print(os.access(p, os.R_OK), os.access(p, os.X_OK))  # can I read / execute?
    os.chmod(p, 0o400)  # make read-only
    print(oct(p.stat().st_mode & 0o777))  # new mode
    print(type(st.st_mtime).__name__, type(st.st_mtime_ns).__name__)  # float vs int ns
```

**Real output** (Python 3.13.3):
```
11
True True False
.txt report report.txt
True
0o644
True False
0o400
float int
```

Note: `st_mtime` is a float (seconds since 1970); `st_mtime_ns` is an exact integer.

## 💻 Code Example — Advanced
```python
# Advanced: dataclass FileInfo, directory scan, hash, error handling
from __future__ import annotations
import hashlib, stat, tempfile  # hashing and mode helpers
from dataclasses import dataclass  # simple data holder
from datetime import datetime, timezone  # aware datetimes
from pathlib import Path  # path API
from typing import Iterator


@dataclass(frozen=True)
class FileInfo:
    name: str  # file name
    size: int  # bytes
    modified: datetime  # UTC aware datetime
    is_symlink: bool  # is it a link?
    sha256: str | None  # content hash (None for big files)


def human_size(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):  # walk up the units
        if n < 1024:  # fits this unit
            return f"{n:.1f} {unit}"
        n /= 1024  # go to next unit
    return f"{n:.1f} TB"


def file_info(path: Path, hash_limit: int = 1_000_000) -> FileInfo:
    st = path.lstat()  # lstat does not follow symlinks
    digest: str | None = None  # default no hash
    if stat.S_ISREG(st.st_mode) and st.st_size <= hash_limit:  # regular small file
        digest = hashlib.sha256(path.read_bytes()).hexdigest()  # hash content
    return FileInfo(path.name, st.st_size, datetime.fromtimestamp(st.st_mtime, tz=timezone.utc),
                    path.is_symlink(), digest)


def scan(folder: Path) -> Iterator[FileInfo]:
    for entry in sorted(folder.iterdir()):  # list directory
        try:
            yield file_info(entry)  # build info
        except (PermissionError, FileNotFoundError) as exc:  # file vanished or locked
            print("skip", entry.name, type(exc).__name__)


with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "a.txt").write_text("abc")
    (root / "b.bin").write_bytes(b"\x00" * 2048)
    (root / "link").symlink_to(root / "a.txt")
    for info in scan(root):
        print(info.name, human_size(info.size), info.is_symlink, (info.sha256 or "-")[:12], info.modified.tzinfo)
    try:
        (root / "missing").stat()  # does not exist
    except FileNotFoundError as e:
        print("FileNotFoundError:", e.errno)
    print(Path(tmp, "a.txt").stat().st_mtime_ns == Path(tmp, "a.txt").stat().st_mtime_ns)
```

**Real output** (Python 3.13.3):
```
a.txt 3.0 B False ba7816bf8f01 UTC
b.bin 2.0 KB False e5a00aa9991a UTC
link 66.0 B True - UTC
FileNotFoundError: 2
True
```

The symlink size (66.0 B above) equals the length of the target path, so it differs on your machine. Hash values for the same content are always the same.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
from pathlib import Path
st = Path("report.txt").stat()   # size, times, mode in one call
print(st.st_size)                # bytes
print(Path("report.txt").exists())
```

```javascript
// JavaScript (Node.js)
const fs = require("fs");
const st = fs.statSync("report.txt");   // fs.promises.stat for async
console.log(st.size);                   // bytes
console.log(fs.existsSync("report.txt"));
```

Both wrap the same OS `stat` call. Node's `mtimeMs` is a number in milliseconds; Python's `st_mtime` is seconds as a float. Python's `pathlib` also gives `.suffix`, `.stem`, `.is_dir()` directly on the path object, where Node needs the separate `path` module.

---

## 🟠 FastAPI Connection
FastAPI file endpoints (download, preview, listing) use metadata for `Content-Length`, `Last-Modified` and size limits. Always resolve the path and check it stays inside your upload folder, otherwise `../` in the URL can leak other files (path traversal).

```python
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile, os
app = FastAPI()
UPLOADS = Path(tempfile.mkdtemp())
(UPLOADS / "invoice.pdf").write_bytes(b"%PDF-1.4 fake")
@app.get("/files/{name}/meta")
def meta(name: str) -> dict[str, object]:
    p = (UPLOADS / name).resolve()
    if UPLOADS.resolve() not in p.parents or not p.is_file():
        raise HTTPException(404, "not found")
    st = p.stat()
    return {"name": p.name, "size": st.st_size, "mtime": int(st.st_mtime)}
c = TestClient(app)
r = c.get("/files/invoice.pdf/meta"); print(r.status_code, r.json()["size"], r.json()["name"])
print(c.get("/files/nope.pdf/meta").status_code)
print(c.get("/files/..%2Fetc/meta").status_code)
```

**Real output** (Python 3.13.3):
```
200 13 invoice.pdf
404
404
```


---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Checking `exists()` then using the file (race condition)
```python
# Wrong - file may vanish between the two lines (TOCTOU)
if path.exists():
    size = path.stat().st_size

# Right - just try it (EAFP)
try:
    size = path.stat().st_size
except FileNotFoundError:
    size = 0
```

❌ Mistake 2: Treating `st_mtime` as a datetime or as milliseconds
```python
# Wrong - it is a float of SECONDS, not a datetime
age = time.time() - path.stat().st_mtime_ns   # nanoseconds mixed with seconds!

# Right
from datetime import datetime, timezone
modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
```

❌ Mistake 3: Using `st_ctime` as "creation time"
```python
# Wrong on Linux/macOS: st_ctime is the last METADATA CHANGE time
created = path.stat().st_ctime

# Right: on macOS/BSD and Windows (3.12+) use st_birthtime where available
created = getattr(path.stat(), "st_birthtime", None)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from pathlib import Path
import tempfile, os
d = Path(tempfile.mkdtemp()); f = d / "a.txt"; f.write_text("hi")
os.utime(f, (0, 0))
print(f.stat().st_mtime)
f.write_text("hello")
print(f.stat().st_size, f.stat().st_mtime > 0)
l = d / "l"; l.symlink_to(f); f.unlink()
print(l.exists(), l.is_symlink(), l.lstat().st_size > 0)
```

**Answer** (real run on Python 3.13.3):
```
0.0
5 True
False True True
```
`os.utime` sets mtime to epoch 0 so `0.0` is printed; writing again updates mtime and size (5). After the target is deleted, a symlink is *dangling*: `exists()` follows the link and returns False, while `is_symlink()` and `lstat()` still work. (`st_ctime` meaning and `st_birthtime` depend on the OS.)

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `stat()` and `lstat()`?
A1: `stat()` follows symlinks and describes the target; `lstat()` describes the link itself. Use `lstat()` when scanning directories so you do not accidentally follow links outside the folder.

Q2: How do you get permissions as `rwx` style numbers?
A2: `oct(st.st_mode & 0o777)` gives `0o644`; `stat.filemode(st.st_mode)` gives `-rw-r--r--`. Change them with `os.chmod` / `Path.chmod`.

Q3: `os.path.getsize` vs `Path.stat().st_size`?
A3: Same result; `getsize` is a shortcut that calls `stat` for you. If you also need mtime or mode, call `stat()` once and reuse the object (one syscall instead of three).

Q4: How do you list a big directory with metadata fast?
A4: `os.scandir()` (used inside `Path.iterdir`/`os.walk`) returns `DirEntry` objects whose `is_dir()` and often `stat()` are cached from the directory read, which avoids an extra syscall per file.

Q5: How do you detect that a file changed?
A5: Compare `st_mtime_ns` and `st_size` (cheap) or a content hash like SHA-256 (exact but reads the file). Build tools use mtime+size first and hash only when those differ.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You need size, age or permissions without reading content
- Cleanup, backup or sync jobs decide by mtime and size
- You validate uploads or downloads before streaming them

❌ Avoid when:
- You need to be sure the file will still be there (just open it and handle the error)
- You need a content-based identity (use a hash, mtime can be faked or reset)
- You compare timestamps across machines with different clocks

---

## 📊 Visual Diagram

```
path.stat()
   |
   v   ONE system call to the OS (no file content read)
+---------------------------+
| st_size   -> 11           |
| st_mode   -> 0o100644     |  file type + permission bits
| st_mtime  -> 1.7e9 (float)|  last modified (seconds since 1970)
| st_uid/gid-> owner        |
+---------------------------+
   |-- stat.S_ISREG(mode)  -> regular file?
   |-- mode & 0o777        -> rw-r--r--
   +-- datetime.fromtimestamp(mtime)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Metadata | Data about a file | फ़ाइल के बारे में जानकारी |
| inode | OS record holding metadata | OS का फ़ाइल record |
| mtime | Last content modification time | आखिरी बदलाव का समय |
| st_mode | File type + permission bits | type और permission bits |
| Symlink | Shortcut pointing to another path | दूसरे path का shortcut |
| TOCTOU | Check-then-use race | जाँचने और इस्तेमाल के बीच की race |

---

## ⚡ 3-Line Summary
English: `Path.stat()` reads size, times and permissions in one system call without opening the file. Use `lstat()` for symlinks, `st_mtime_ns` for exact times, and handle `FileNotFoundError` instead of checking `exists()` first.
Hindi: `Path.stat()` एक system call में size, समय और permissions देता है, फ़ाइल खोले बिना। Symlink के लिए `lstat()`, सटीक समय के लिए `st_mtime_ns` लें, और `exists()` की जगह `FileNotFoundError` handle करें।

---

## ➡️ Next Topic
**213. Temporary Files** — create scratch files and folders that clean themselves up, and write files atomically.
