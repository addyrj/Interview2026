---

# 210. File Path Handling (pathlib)
# हिंदी में: File Path Handling (pathlib से रास्ते संभालना)

---

## 🔵 Simple Definition (English)
`pathlib.Path` is an object that represents a file or folder path. You join parts with `/`, read parts like `.name`, `.suffix`, `.parent`, and call methods like `.exists()`, `.read_text()`, `.mkdir()`. It works the same on Windows, macOS and Linux and replaces most of `os.path`.

## 🔵 सरल परिभाषा (Hindi)
`pathlib.Path` एक object है जो file या folder का path दर्शाता है। आप `/` से हिस्से जोड़ते हैं, `.name`, `.suffix`, `.parent` जैसे हिस्से पढ़ते हैं और `.exists()`, `.read_text()`, `.mkdir()` जैसे methods चलाते हैं। यह Windows, macOS और Linux पर एक जैसा चलता है और `os.path` का ज़्यादातर काम करता है।

---

## 🔴 Problem it Solves
Paths as plain strings are fragile: `"data" + "/" + name` breaks on Windows (`\`), double slashes sneak in, and you need `os.path.join`, `os.path.splitext`, `os.path.dirname` functions with awkward nesting. Worse, joining user input blindly allows path traversal attacks (`../../etc/passwd`). `Path` gives readable, cross-platform code with safe helper methods.

## 🔴 यह क्यों बना? (Hindi)
Paths को string मानना नाज़ुक है: `"data" + "/" + name` Windows (`\`) पर टूटता है, double slashes घुस जाते हैं, और `os.path.join`, `os.path.splitext`, `os.path.dirname` जैसे उलझे functions चाहिए। इससे भी बुरा, user input को सीधे जोड़ने से path traversal attack (`../../etc/passwd`) हो सकता है। `Path` पढ़ने लायक, cross-platform code और सुरक्षित helper methods देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → p = Path("/srv/app") / "data" / "jan.csv"      join with the / operator
Step 2 → Pure parts (no disk access): p.name, p.stem, p.suffix, p.parent, p.parts
Step 3 → Change parts: p.with_suffix(".txt"), p.with_name("x.csv"), p.with_stem("feb")
Step 4 → Disk checks: p.exists(), p.is_file(), p.is_dir(), p.stat()
Step 5 → Disk actions: p.read_text(), p.write_text(), p.mkdir(), p.unlink(), p.rename()
Step 6 → p.resolve() makes it absolute and removes "..", used for security checks
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → p = Path("/srv/app") / "data" / "jan.csv"      / operator से जोड़ें
Step 2 → Disk छुए बिना हिस्से: p.name, p.stem, p.suffix, p.parent, p.parts
Step 3 → हिस्से बदलें: p.with_suffix(".txt"), p.with_name("x.csv")
Step 4 → Disk जाँच: p.exists(), p.is_file(), p.is_dir(), p.stat()
Step 5 → Disk काम: p.read_text(), p.write_text(), p.mkdir(), p.unlink(), p.rename()
Step 6 → p.resolve() absolute बनाता है और ".." हटाता है, security जाँच में काम आता है
```

---

## 🟡 Real World Example
A Swiggy ETL job builds `BASE_DIR / "exports" / f"{date}.csv"` regardless of whether it runs on a developer's Windows laptop or a Linux server. Razorpay's invoice service takes a user-supplied filename and checks the resolved path stays inside the invoices folder. A FastAPI app finds its templates with `Path(__file__).resolve().parent / "templates"`.

## 🟡 Real Example Hindi mein
Swiggy का ETL job `BASE_DIR / "exports" / f"{date}.csv"` बनाता है, चाहे वह developer के Windows laptop पर चले या Linux server पर। Razorpay की invoice service user से मिला filename लेती है और जाँचती है कि resolved path invoices folder के अंदर ही है। FastAPI app अपने templates `Path(__file__).resolve().parent / "templates"` से ढूँढती है।

---

## 💻 Code Example — Basic
```python
# pathlib basics - every line commented
import tempfile  # temp folder
from pathlib import Path, PureWindowsPath  # Path and a Windows-style pure path

f: Path = Path("/srv/app/data") / "reports" / "2026" / "jan.tar.gz"  # join with /
print(f)  # full path
# Output: /srv/app/data/reports/2026/jan.tar.gz
print(f.name, f.stem, f.suffix, f.suffixes)  # name, name without last suffix, last suffix, all
# Output: jan.tar.gz jan.tar .gz ['.tar', '.gz']
print(f.parent)  # folder containing the file
# Output: /srv/app/data/reports/2026
print(f.parents[1])  # two levels up
# Output: /srv/app/data/reports
print(f.with_suffix(".zip"))  # replace the last suffix
# Output: /srv/app/data/reports/2026/jan.tar.zip
print(f.with_name("x.txt"))  # replace the whole file name
# Output: /srv/app/data/reports/2026/x.txt
print(f.with_stem("feb"))  # replace stem, keep suffix (Python 3.9+)
# Output: /srv/app/data/reports/2026/feb.gz

print(Path("a/b/../c"), Path("a//b/./c"))  # normalises "//" and "./" but keeps ".."
# Output: a/b/../c a/b/c
print(Path("/a/b/c").relative_to("/a"))  # part below /a
# Output: b/c
print(Path("report.final.csv").suffix, Path(".bashrc").suffix)  # dotfile has no suffix
# Output: .csv   (the second value is an empty string)

d: Path = Path(tempfile.mkdtemp())  # real temp folder
t: Path = d / "sub" / "n.txt"  # nested file path
t.parent.mkdir(parents=True, exist_ok=True)  # create folders; no error if present
t.write_text("hello नमस्ते", encoding="utf-8")  # write text in one line
print(t.exists(), t.is_file(), t.is_dir(), t.read_text(encoding="utf-8"), t.stat().st_size)
# Output: True True False hello नमस्ते 24

print(PureWindowsPath("C:/Users/Aditya/file.txt").parts)  # Windows path analysed on any OS
# Output: ('C:\\', 'Users', 'Aditya', 'file.txt')
```

## 💻 Code Example — Advanced
```python
# Production style: safe join (path traversal), rename/replace, glob, project paths
import tempfile  # temp folder
from pathlib import Path  # paths
from typing import List  # type hints

BASE_DIR: Path = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()  # project root
# Output: BASE_DIR is the folder holding this script


def safe_join(root: Path, user_path: str) -> Path:
    """Join user input to root and make sure we cannot escape the root."""
    root_resolved: Path = root.resolve()  # real absolute root
    candidate: Path = (root_resolved / user_path).resolve()  # resolve removes ".." and symlinks
    if not candidate.is_relative_to(root_resolved):  # Python 3.9+
        raise PermissionError(f"escape attempt: {user_path}")  # block it
    return candidate  # safe path


root: Path = Path(tempfile.mkdtemp())  # pretend uploads folder
(root / "sub").mkdir()  # create sub folder
(root / "sub" / "n.txt").write_text("x")  # sample file
print(safe_join(root, "sub/n.txt").name)  # allowed
# Output: n.txt
for bad in ("../../etc/passwd", "/etc/passwd"):  # two attack strings
    try:  # try each
        safe_join(root, bad)  # should fail
    except PermissionError:  # blocked
        print("PermissionError", bad)  # report
# Output: PermissionError ../../etc/passwd
# Output: PermissionError /etc/passwd

# Gotcha: joining an absolute path REPLACES everything before it
print(Path("/a/b") / "/etc/passwd")  # right side is absolute
# Output: /etc/passwd

# relative_to raises ValueError when the path is not inside
try:  # unrelated path
    Path("/x/y").relative_to("/a")  # not below /a
except ValueError as exc:  # ValueError
    print("ValueError:", exc)  # message
# Output: ValueError: '/x/y' is not in the subpath of '/a'

# glob / rglob: search
(root / "sub" / "a.csv").write_text("1")  # another file
csvs: List[str] = sorted(p.name for p in root.rglob("*.csv"))  # recursive search
print(csvs)  # only csv files
# Output: ['a.csv']

# rename / replace / unlink / touch
src: Path = root / "sub" / "n.txt"  # existing file
src.rename(src.with_name("m.txt"))  # rename in place
print(sorted(x.name for x in src.parent.iterdir()))  # list the folder
# Output: ['a.csv', 'm.txt']
(root / "sub" / "m.txt").replace(root / "z.txt")  # move; overwrites target silently
print((root / "z.txt").exists())  # moved
# Output: True
(root / "z.txt").unlink()  # delete the file
(root / "z.txt").unlink(missing_ok=True)  # no error if already gone (3.8+)
(root / "touch.txt").touch()  # create empty file or update its time
print((root / "touch.txt").stat().st_size)  # 0 bytes
# Output: 0

# Paths work anywhere a string path is expected
with open(root / "touch.txt", "rb") as fh:  # open accepts Path
    print(len(fh.read()))  # empty file
# Output: 0
```
Verified on Python 3.13.3 (macOS). `Path.full_match()` (glob-style whole-path match) is new in 3.13; `with_stem` and `is_relative_to` need 3.9+.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python way
from pathlib import Path
p = Path("/srv/app") / "data" / "jan.csv"
print(p.name, p.suffix, p.parent)
print(p.with_suffix(".txt"))
text = p.read_text(encoding="utf-8") if p.exists() else ""
```
```javascript
// JavaScript way (Node.js)
import path from "node:path";
import { existsSync, readFileSync } from "node:fs";
const p = path.join("/srv/app", "data", "jan.csv");
console.log(path.basename(p), path.extname(p), path.dirname(p));
console.log(path.join(path.dirname(p), path.basename(p, ".csv") + ".txt"));
const text = existsSync(p) ? readFileSync(p, "utf-8") : "";
// ES modules: __dirname = path.dirname(fileURLToPath(import.meta.url))
```

Key differences: Node's `path` is a set of string functions; Python's `Path` is an object with methods and the `/` operator. `Path.read_text()` has no direct Node twin (you use `fs`). Python's `Path(__file__)` equals Node's `__filename`.

---

## 🟠 FastAPI Connection
FastAPI projects use `Path` for template folders, static files, upload directories and config files. Never trust a filename sent by a client: strip it with `Path(name).name` or check with `safe_join` before reading or writing.

```python
# FastAPI: safe file download endpoint (pip install fastapi)
import tempfile  # temp folder
from pathlib import Path  # paths
from fastapi import FastAPI, HTTPException  # framework
from fastapi.responses import FileResponse  # file download

app: FastAPI = FastAPI()  # app
ROOT: Path = Path(tempfile.mkdtemp()).resolve()  # public files folder
(ROOT / "hello.txt").write_text("hi")  # sample file


@app.get("/files/{name:path}")  # GET /files/anything/here.txt
def download(name: str) -> FileResponse:
    target: Path = (ROOT / name).resolve()  # resolve ".." tricks
    if not target.is_relative_to(ROOT) or not target.is_file():  # outside root or missing
        raise HTTPException(status_code=404, detail="not found")  # same error for both
    return FileResponse(target)  # streams file with right headers
# Tested with TestClient: hello.txt -> "hi"; missing file, "../" traversal and "//etc/passwd" -> all 404.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Building paths with string `+`
✅ Correct:

```python
# Wrong - double slash or wrong separator on Windows
p = "data/" + "/" + name
# Right
from pathlib import Path
p = Path("data") / name
```

❌ Mistake 2: Joining user input without checking
✅ Correct:

```python
# Wrong - name could be "../../etc/passwd" or "/etc/passwd"
data = (ROOT / name).read_text()
# Right
target = (ROOT / name).resolve()
if not target.is_relative_to(ROOT.resolve()):
    raise PermissionError("blocked")
```

❌ Mistake 3: Relying on the working directory
✅ Correct:

```python
# Wrong - breaks when started from another folder
open("config/settings.json")
# Right - anchor to this file
CONFIG = Path(__file__).resolve().parent / "config" / "settings.json"
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from pathlib import Path
print(Path("/a/b") / "/etc/passwd")
print(Path("a.tar.gz").with_suffix(""))
print(Path(".bashrc").suffix == "", Path(".bashrc").stem)
print(Path("a/b/../c"), Path("a/b/../c").resolve() == Path("a/c").resolve())
```

**Answer**:
```
/etc/passwd
a.tar
True .bashrc
a/b/../c True
```
Joining with an absolute path discards everything on the left. `with_suffix("")` removes only the last suffix. A dotfile like `.bashrc` has an empty suffix and its stem is the full name. `Path` does not collapse `..` by itself (because of symlinks); `resolve()` does. (Output verified on Python 3.13.)

---

## ⚫ Interview Questions + Answers

Q1: `pathlib` vs `os.path`?
A1: `pathlib` is object-oriented, readable and cross-platform; `os.path` is string functions. Both work, and since Python 3.6 `open()` and `os` functions accept `Path` objects (`os.fspath`).

Q2: `Path.resolve()` vs `Path.absolute()`?
A2: `resolve()` also removes `..` and follows symlinks; `absolute()` only prepends the current directory.

Q3: How do you list files recursively?
A3: `Path.rglob("*.py")` or `Path.walk()` (new in 3.12, like `os.walk`).

Q4: How do you prevent path traversal?
A4: `resolve()` the joined path and check `is_relative_to(root)` (3.9+). Also reject absolute inputs and handle symlinks.

Q5: What are PurePath classes?
A5: `PurePosixPath` and `PureWindowsPath` do path maths without touching the disk or caring about the current OS; useful for parsing paths from another system.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Any new Python code that handles files and folders
- Building cross-platform paths and project-relative paths
- Quick one-line file reads/writes

❌ Avoid when:
- A library demands strings: convert with `str(path)` or `os.fspath(path)`
- You need to hand paths to a URL (use `PurePosixPath` or `as_posix()`)
- Bulk-copying trees: use `shutil` (with `Path` arguments)

---

## 📊 Visual Diagram

```
Path("/srv/app/data/reports/2026/jan.tar.gz")
 anchor  parents...                 name = jan.tar.gz
   /     srv app data reports 2026   stem   = jan.tar
                                     suffix = .gz   suffixes = ['.tar', '.gz']

 .parent  -> /srv/app/data/reports/2026
 .parents[1] -> /srv/app/data/reports
 p / "x"  -> adds a child         p / "/etc"  -> REPLACES everything
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Path | Object for a file/folder path | path का object |
| Suffix | File extension like .csv | file extension |
| Stem | Name without the last suffix | आखिरी suffix के बिना नाम |
| Resolve | Make absolute, remove .. | absolute बनाना, .. हटाना |
| Path traversal | Escaping a folder using .. | .. से folder से बाहर निकलना |
| Glob | Pattern search like *.csv | *.csv जैसी pattern खोज |

---

## ⚡ 3-Line Summary
English: `Path` gives readable, cross-platform paths: join with `/`, read `.name/.suffix/.parent`, act with `.read_text()/.mkdir()/.unlink()`. Anchor to `__file__`, not the working directory. Always `resolve()` and check `is_relative_to()` for user-supplied paths.
Hindi: `Path` पढ़ने लायक, cross-platform paths देता है: `/` से जोड़ें, `.name/.suffix/.parent` पढ़ें, `.read_text()/.mkdir()/.unlink()` से काम करें। Working directory की जगह `__file__` से anchor करें। User के paths के लिए हमेशा `resolve()` और `is_relative_to()` जाँचें।

---

## ➡️ Next Topic
**211. Directory Operations** — create, list, walk, copy and delete folders with `pathlib`, `os` and `shutil`.
