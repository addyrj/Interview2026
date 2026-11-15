---

# 186. pathlib Module
# हिंदी में: pathlib Module (object-oriented file paths)

---

## 🔵 Simple Definition (English)
`pathlib` gives you a `Path` object for files and folders. Instead of gluing strings with `os.path.join`, you use `/` to join parts and call methods like `.read_text()`, `.exists()`, `.mkdir()` and `.glob()` on the path itself. It is the modern replacement for most of `os.path`.

## 🔵 सरल परिभाषा (Hindi)
`pathlib` files और folders के लिए `Path` object देता है। `os.path.join` से strings जोड़ने की जगह आप `/` से parts जोड़ते हैं और path पर ही `.read_text()`, `.exists()`, `.mkdir()`, `.glob()` जैसे methods चलाते हैं। यह `os.path` का modern विकल्प है।

---

## 🔴 Problem it Solves
Old code used plain strings: `"data" + "/" + name`. This breaks on Windows (`\`), forgets separators, and needs many functions from `os`, `os.path`, `glob` and `shutil` for simple jobs. Strings also have no type, so a path and a normal text look the same. `pathlib` gives one typed object with all common operations and the correct separator on every OS.

## 🔴 यह क्यों बना? (Hindi)
पुराना code plain strings इस्तेमाल करता था: `"data" + "/" + name`। यह Windows (`\`) पर टूटता है, separator भूल जाता है, और छोटे काम के लिए `os`, `os.path`, `glob`, `shutil` के कई functions चाहिए। String का कोई type नहीं होता, इसलिए path और सामान्य text एक जैसे दिखते हैं। `pathlib` एक typed object देता है जिसमें सारे common operations हैं और हर OS पर सही separator लगता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Path("a") creates PosixPath or WindowsPath depending on your OS
Step 2 → Path / "b" / "c.txt" builds a new Path (paths are immutable)
Step 3 → Pure methods (name, stem, suffix, parent, with_suffix) only do string work
Step 4 → Concrete methods (exists, read_text, mkdir, iterdir, glob) talk to the disk
Step 5 → resolve() makes it absolute and removes "..", symlinks
Step 6 → PurePath classes let you handle paths of another OS without disk access
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Path("a") आपके OS के हिसाब से PosixPath या WindowsPath बनाता है
Step 2 → Path / "b" / "c.txt" नया Path बनाता है (paths immutable हैं)
Step 3 → Pure methods (name, stem, suffix, parent, with_suffix) सिर्फ string का काम करते हैं
Step 4 → Concrete methods (exists, read_text, mkdir, iterdir, glob) disk से बात करते हैं
Step 5 → resolve() path को absolute बनाता है और ".." व symlink हटाता है
Step 6 → PurePath classes से दूसरे OS के path बिना disk छुए संभाल सकते हैं
```

---

## 🟡 Real World Example
A Razorpay-style reconciliation job reads `settlements/2025/11/*.csv`, writes a cleaned file next to each input with `with_suffix(".clean.csv")`, and moves processed files into `archive/`. A FastAPI upload service stores files under `uploads/<user_id>/` and must prevent `../../etc/passwd` tricks. An AI app keeps model files in `Path(__file__).parent / "models"` so it works from any working directory.

## 🟡 Real Example Hindi mein
Razorpay जैसी reconciliation job `settlements/2025/11/*.csv` पढ़ती है, हर input के पास `with_suffix(".clean.csv")` से साफ file लिखती है और processed files को `archive/` में भेजती है। FastAPI upload service files को `uploads/<user_id>/` में रखती है और `../../etc/passwd` जैसी चालों को रोकना पड़ता है। AI app model files को `Path(__file__).parent / "models"` में रखती है ताकि किसी भी working directory से चले।

---

## 💻 Code Example — Basic
```python
# Basic pathlib examples - every line commented
import tempfile  # to get a safe throw-away folder
from pathlib import Path  # the main class

p: Path = Path("reports") / "2025" / "sales.csv"  # "/" joins path parts
print(p)  # the joined path
print(p.name, p.stem, p.suffix)  # file name, name without extension, extension
print(p.parent, p.parts)  # parent folder and all parts as a tuple
print(p.with_suffix(".json"))  # same path, new extension (no disk change)
print(p.with_name("summary.txt"))  # same folder, new file name
print(p.is_absolute())  # relative path -> False

with tempfile.TemporaryDirectory() as tmp:  # auto-deleted folder
    base: Path = Path(tmp)  # wrap the temp folder name in Path
    folder: Path = base / "logs" / "app"  # nested folder path
    folder.mkdir(parents=True, exist_ok=True)  # create all levels, no error if exists
    f: Path = folder / "today.txt"  # file path
    f.write_text("hello\nworld\n", encoding="utf-8")  # create + write in one line
    print(f.read_text(encoding="utf-8").splitlines())  # read whole file back
    print(f.exists(), f.is_file(), f.is_dir())  # existence checks
    print(f.stat().st_size, "bytes")  # file size from stat()
    (folder / "b.log").touch()  # create an empty file
    (folder / "a.log").touch()  # another empty file
    print(sorted(x.name for x in folder.iterdir()))  # direct children only
    print(sorted(x.name for x in folder.glob("*.log")))  # pattern match
    print([x.relative_to(base).as_posix() for x in sorted(base.rglob("*"))])  # recursive
    f.rename(folder / "yesterday.txt")  # rename / move a file
    print(sorted(x.name for x in folder.iterdir()))  # see the change
    (folder / "a.log").unlink()  # delete a file
    (folder / "missing.txt").unlink(missing_ok=True)  # no error if absent (3.8+)
    print(sorted(x.name for x in folder.iterdir()))  # after delete
```

Output (verified by running; ids/timestamps/paths may vary):
```
reports/2025/sales.csv
sales.csv sales .csv
reports/2025 ('reports', '2025', 'sales.csv')
reports/2025/sales.json
reports/2025/summary.txt
False
['hello', 'world']
True True False
12 bytes
['a.log', 'b.log', 'today.txt']
['a.log', 'b.log']
['logs', 'logs/app', 'logs/app/a.log', 'logs/app/b.log', 'logs/app/today.txt']
['a.log', 'b.log', 'yesterday.txt']
['b.log', 'yesterday.txt']
```

## 💻 Code Example — Advanced
```python
# Production style: safe uploads, atomic write, path traversal defence, walk (3.12+)
import tempfile  # temp folder for the demo
from pathlib import Path, PurePosixPath, PureWindowsPath  # real and pure paths
from typing import Iterator, List  # type hints


class UnsafePathError(ValueError):
    """Raised when a user supplied path escapes the base folder."""


def safe_join(base: Path, user_path: str) -> Path:
    """Join user input to base and block '../' tricks (path traversal)."""
    root: Path = base.resolve()  # absolute, symlinks resolved
    target: Path = (root / user_path).resolve()  # resolve the final path
    if not target.is_relative_to(root):  # 3.9+: is target inside root?
        raise UnsafePathError(f"blocked: {user_path!r}")  # reject it
    return target  # safe to use


def atomic_write(path: Path, data: str) -> None:
    """Write to a temp file then replace, so readers never see half a file."""
    tmp: Path = path.with_suffix(path.suffix + ".tmp")  # sibling temp file
    tmp.write_text(data, encoding="utf-8")  # write fully first
    tmp.replace(path)  # atomic rename on the same filesystem


def python_files(root: Path) -> Iterator[Path]:
    """Yield all .py files below root, skipping hidden folders."""
    for p in sorted(root.rglob("*.py")):  # recursive search
        if not any(part.startswith(".") for part in p.relative_to(root).parts):
            yield p  # keep non hidden


with tempfile.TemporaryDirectory() as tmp:  # sandbox
    base: Path = Path(tmp) / "uploads"  # upload folder
    base.mkdir()  # create it
    ok: Path = safe_join(base, "invoice.pdf")  # normal name
    print("ok ->", ok.relative_to(base.resolve()))  # relative view
    for bad in ("../secret.txt", "/etc/passwd", "a/../../x"):  # attack samples
        try:  # try each attack
            safe_join(base, bad)  # should fail
        except UnsafePathError as exc:  # expected
            print("UnsafePathError:", exc)  # show message

    cfg: Path = base / "config.json"  # target file
    atomic_write(cfg, '{"v": 1}')  # first write
    atomic_write(cfg, '{"v": 2}')  # overwrite atomically
    print(cfg.read_text(), [p.name for p in base.iterdir()])  # no .tmp left behind

    (base / "pkg").mkdir()  # make a package folder
    (base / "pkg" / "a.py").write_text("x = 1")  # visible file
    (base / ".git").mkdir()  # hidden folder
    (base / ".git" / "hook.py").write_text("x = 2")  # should be skipped
    print([p.relative_to(base).as_posix() for p in python_files(base)])

    walked: List[str] = []  # collect walk results
    for dirpath, dirnames, filenames in base.walk():  # Path.walk() is new in 3.12
        walked.append(f"{dirpath.relative_to(base).as_posix()}:{sorted(filenames)}")
    print(sorted(walked))  # deterministic order

# Pure paths: manipulate paths of another OS without touching the disk
print(PureWindowsPath(r"C:\Users\Asha\data.csv").parts)  # Windows style
print(PurePosixPath("/var/log/app.log").parent)  # POSIX style
print(PureWindowsPath("C:/a/b") / "c.txt")  # joined with backslashes
```

Output (verified by running; ids/timestamps/paths may vary):
```
ok -> invoice.pdf
UnsafePathError: blocked: '../secret.txt'
UnsafePathError: blocked: '/etc/passwd'
UnsafePathError: blocked: 'a/../../x'
{"v": 2} ['config.json']
['pkg/a.py']
[".:['config.json']", ".git:['hook.py']", "pkg:['a.py']"]
('C:\\', 'Users', 'Asha', 'data.csv')
/var/log
C:\a\b\c.txt
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
from pathlib import Path
p = Path("data") / "users.json"        # join with "/"
text = p.read_text(encoding="utf-8")   # read file
p.parent.mkdir(parents=True, exist_ok=True)  # mkdir -p
print(p.suffix, p.stem)                # .json users
```

```javascript
// JavaScript (Node.js)
import path from "node:path";
import fs from "node:fs";
const p = path.join("data", "users.json");        // join
const text = fs.readFileSync(p, "utf-8");         // read file
fs.mkdirSync(path.dirname(p), { recursive: true });  // mkdir -p
console.log(path.extname(p), path.basename(p, ".json"));  // .json users
```

Key differences: Node splits the work between `path` (strings) and `fs` (disk). Python's `Path` is one object that does both. Node paths are plain strings; Python paths are real objects, and `/` is an operator on them. In Python `Path.read_text()` always needs an `encoding` if you want portable behaviour.

---

## 🟠 FastAPI Connection
FastAPI apps use `pathlib` for static folders, templates, upload directories and `FileResponse`. The key production rule: never trust a user supplied file name. Resolve the final path and check `is_relative_to(BASE_DIR)`.

```python
# FastAPI: serve files from a safe folder (pip install fastapi httpx)
import tempfile  # demo folder
from pathlib import Path  # path handling
from fastapi import FastAPI, HTTPException  # app and errors
from fastapi.responses import FileResponse  # stream a file

BASE_DIR: Path = Path(tempfile.mkdtemp()).resolve()  # real app: Path(__file__).parent / "static"
(BASE_DIR / "hello.txt").write_text("hi from disk")  # demo file
app: FastAPI = FastAPI()  # create app


@app.get("/files/{name:path}")  # :path allows slashes in the name
def get_file(name: str) -> FileResponse:
    target: Path = (BASE_DIR / name).resolve()  # normalise the path
    if not target.is_relative_to(BASE_DIR):  # block ../ traversal
        raise HTTPException(status_code=400, detail="bad path")  # 400
    if not target.is_file():  # missing file
        raise HTTPException(status_code=404, detail="not found")  # 404
    return FileResponse(target)  # efficient file streaming
```

Output (verified by running; ids/timestamps/paths may vary):
```
200 hi from disk
404
400
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mixing strings and Path with `+`
```python
# Wrong - TypeError: unsupported operand type(s) for +: 'PosixPath' and 'str'
# Path("data") + "/file.txt"

# Correct - use "/" or joinpath
from pathlib import Path
print(Path("data") / "file.txt")
```

❌ Mistake 2: Trusting user input in a path
```python
# Wrong - "/" with an absolute path REPLACES the left side
from pathlib import Path
print(Path("/srv/uploads") / "/etc/passwd")     # /etc/passwd  (!)

# Correct - resolve and check it is inside the base
base = Path("/srv/uploads").resolve()
target = (base / "x/../../etc/passwd").resolve()
print(target.is_relative_to(base))              # False -> reject
```

❌ Mistake 3: Forgetting encoding and `exist_ok`
```python
# Wrong - default encoding depends on OS; mkdir fails if folder exists
# Path("out").mkdir()          # FileExistsError on second run
# Path("a.txt").read_text()

# Correct
# Path("out").mkdir(parents=True, exist_ok=True)
# Path("a.txt").read_text(encoding="utf-8")
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from pathlib import Path

p = Path("archive.tar.gz")
print(p.suffix, p.suffixes, p.stem)
print(Path("/a") / "/b" / "c")
print(Path("a/b/../c").parts, Path("a//b/./c"))
print(Path("") == Path("."), Path(".hidden").suffix == "")
```

**Answer**:
```
.gz ['.tar', '.gz'] archive.tar
/b/c
('a', 'b', '..', 'c') a/b/c
True True
```
`suffix` is only the last extension; use `suffixes` for all. An absolute right operand throws away everything before it. `Path` normalises double slashes and `.` but does NOT collapse `..` (that needs `resolve()`, because symlinks can make `..` mean something different). A file that only starts with a dot, like `.hidden`, has no suffix.

---

## ⚫ Interview Questions + Answers

Q1: Why prefer `pathlib` over `os.path`?
A1: One typed object, readable `/` joins, built-in read/write/glob/mkdir, correct separators on every OS, and methods chain nicely. `os.path` still works and returns plain strings, which some old libraries need.

Q2: What is the difference between `Path` and `PurePath`?
A2: `PurePath` (and `PurePosixPath`, `PureWindowsPath`) only manipulates path text and never touches the disk. `Path` adds methods like `exists()` and `read_text()`. Use pure paths to handle another OS's paths.

Q3: `resolve()` vs `absolute()`?
A3: `absolute()` just prepends the current directory. `resolve()` also removes `..` and follows symlinks. For security checks always use `resolve()`.

Q4: How do you list files recursively?
A4: `Path.rglob("*.py")` or `glob("**/*.py")`. Since Python 3.12 there is also `Path.walk()`, which works like `os.walk`. Python 3.13 added `full_match()` and `Path.from_uri()` for newer pattern and URI needs.

Q5: How do you write a file safely?
A5: Write to a temp file in the same folder, then call `replace()`; the rename is atomic, so readers never see a half written file.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You build, inspect or walk file paths in new code
- You need cross-platform code (Windows + Linux)
- You read or write small and medium text files with `read_text` / `write_text`

❌ Avoid when:
- A library demands a `str`; then pass `str(path)` or `os.fspath(path)`
- You need to copy trees or move across disks (use `shutil`)
- You process huge files line by line (use `with path.open() as f`, not `read_text`)

---

## 📊 Visual Diagram

```
Path("/srv/app/data/report.final.csv")

 /srv/app/data / report.final.csv
 └─ parent ───┘   └─ name ───────┘
                   stem   = report.final
                   suffix = .csv
                   suffixes = ['.final', '.csv']

 PurePath  ──►  text only (no disk)
    └── Path ──► + exists(), read_text(), mkdir(), glob() ...
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Path | Object for a file or folder path | file/folder path का object |
| PurePath | Path logic without disk access | बिना disk वाला path |
| suffix | Last file extension | आखिरी extension |
| resolve() | Absolute path, no `..`, symlinks followed | पूरा सही path |
| glob / rglob | Pattern search (rglob is recursive) | pattern से files खोजना |
| Path traversal | Attack using `../` to escape a folder | `../` से folder से बाहर निकलने का attack |

---

## ⚡ 3-Line Summary
English: `pathlib.Path` replaces string based `os.path` code with one immutable object. Join with `/`, read and write with `read_text` / `write_text`, search with `glob`, and always `resolve()` plus `is_relative_to()` for user input.
Hindi: `pathlib.Path` string वाले `os.path` code की जगह एक immutable object देता है। `/` से जोड़ें, `read_text` / `write_text` से पढ़ें-लिखें, `glob` से खोजें, और user input के लिए हमेशा `resolve()` व `is_relative_to()` इस्तेमाल करें।

---

## ➡️ Next Topic
**187. shutil Module** — copy, move and delete whole folders, which `pathlib` alone does not do.
