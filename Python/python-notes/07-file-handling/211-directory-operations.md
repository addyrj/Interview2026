---

# 211. Directory Operations
# हिंदी में: Directory Operations (folders बनाना, देखना, कॉपी और delete करना)

---

## 🔵 Simple Definition (English)
Directory operations are the tasks you do on folders: create (`mkdir`), list (`iterdir`, `listdir`), search (`glob`, `rglob`), walk through all sub-folders (`os.walk`, `Path.walk`), copy/move (`shutil.copytree`, `shutil.move`) and delete (`rmdir`, `shutil.rmtree`). They use `pathlib`, `os` and `shutil`.

## 🔵 सरल परिभाषा (Hindi)
Directory operations वे काम हैं जो folders पर किए जाते हैं: बनाना (`mkdir`), list करना (`iterdir`, `listdir`), खोजना (`glob`, `rglob`), सभी sub-folders में घूमना (`os.walk`, `Path.walk`), copy/move (`shutil.copytree`, `shutil.move`) और delete (`rmdir`, `shutil.rmtree`)। इनके लिए `pathlib`, `os` और `shutil` इस्तेमाल होते हैं।

---

## 🔴 Problem it Solves
Real systems manage many files: daily export folders, upload directories, log rotation, build output. Doing this with shell commands (`rm -rf`, `cp -r`) is not portable and risky. Python's standard library gives safe, cross-platform functions with clear errors (`FileExistsError`, `OSError`), so jobs like "delete logs older than 7 days" can be written and tested like any other code.

## 🔴 यह क्यों बना? (Hindi)
असली systems में बहुत सारी files होती हैं: daily export folders, upload directories, log rotation, build output। यह सब shell commands (`rm -rf`, `cp -r`) से करना portable नहीं है और जोखिम भरा है। Python की standard library सुरक्षित, cross-platform functions और साफ errors (`FileExistsError`, `OSError`) देती है, इसलिए "7 दिन पुराने logs delete करो" जैसे jobs को सामान्य code की तरह लिखा और test किया जा सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create:   Path.mkdir(parents=True, exist_ok=True)   (like mkdir -p)
Step 2 → List one level:   Path.iterdir()  /  os.listdir()  /  os.scandir() (fast, has is_dir)
Step 3 → Search:   Path.glob("*.txt") one level, Path.rglob("*.py") all levels
Step 4 → Walk tree: os.walk(top) or Path.walk() (3.12+) -> (folder, subfolders, files)
Step 5 → Copy/move: shutil.copytree(src, dst), shutil.copy2(file, dst), shutil.move(src, dst)
Step 6 → Delete:   Path.rmdir() (EMPTY folder only)  |  shutil.rmtree() (folder + everything)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → बनाना: Path.mkdir(parents=True, exist_ok=True) (mkdir -p जैसा)
Step 2 → एक level की list: Path.iterdir() / os.listdir() / os.scandir()
Step 3 → खोज: Path.glob("*.txt") एक level, Path.rglob("*.py") सभी levels
Step 4 → पूरा tree घूमना: os.walk(top) या Path.walk() (3.12+)
Step 5 → copy/move: shutil.copytree, shutil.copy2, shutil.move
Step 6 → delete: Path.rmdir() (सिर्फ खाली folder) | shutil.rmtree() (folder + सब कुछ)
```

---

## 🟡 Real World Example
A Swiggy data job creates `exports/2026/01/31/` each night with `mkdir(parents=True, exist_ok=True)` and deletes exports older than 30 days. A Razorpay backup script copies the invoices folder with `copytree` and zips it with `make_archive`. An AI app scans a `docs/` folder with `rglob("*.pdf")` to find every document to embed.

## 🟡 Real Example Hindi mein
Swiggy का data job हर रात `mkdir(parents=True, exist_ok=True)` से `exports/2026/01/31/` बनाता है और 30 दिन पुराने exports delete करता है। Razorpay की backup script invoices folder को `copytree` से copy करके `make_archive` से zip करती है। AI app `docs/` folder में `rglob("*.pdf")` से हर document ढूँढकर embed करती है।

---

## 💻 Code Example — Basic
```python
# Directory operations - every line commented
import os  # low level directory functions
import shutil  # high level copy / move / delete
import tempfile  # temp folder
from pathlib import Path  # paths

d: Path = Path(tempfile.mkdtemp())  # temporary base folder
(d / "a" / "b").mkdir(parents=True)  # create nested folders at once

try:  # creating an existing folder
    (d / "a").mkdir()  # already exists
except FileExistsError:  # error
    print("FileExistsError")  # message
# Output: FileExistsError
(d / "a").mkdir(exist_ok=True)  # no error with exist_ok=True

try:  # missing parent
    (d / "x" / "y").mkdir()  # parent x does not exist
except FileNotFoundError:  # error
    print("FileNotFoundError")  # message
# Output: FileNotFoundError

for name in ("1.txt", "2.py", "a/3.txt", "a/b/4.py"):  # create four files
    (d / name).write_text(name)  # content = its own name

print(sorted(p.name for p in d.iterdir()))  # one level: files and folders
# Output: ['1.txt', '2.py', 'a']
print(sorted(os.listdir(d)))  # same with os (returns names, not Paths)
# Output: ['1.txt', '2.py', 'a']
print(sorted(p.name for p in d.glob("*.txt")))  # one level pattern search
# Output: ['1.txt']
print(sorted(p.name for p in d.rglob("*.py")))  # all levels
# Output: ['2.py', '4.py']
print(sorted(str(p.relative_to(d)) for p in d.rglob("*")))  # everything below d
# Output: ['1.txt', '2.py', 'a', 'a/3.txt', 'a/b', 'a/b/4.py']

for root, dirs, files in os.walk(d):  # walk the whole tree
    dirs.sort()  # sorting dirs in place controls visiting order
    print(Path(root).relative_to(d), sorted(files))  # folder and its files
# Output: . ['1.txt', '2.py']
# Output: a ['3.txt']
# Output: a/b ['4.py']

try:  # rmdir only works on empty folders
    (d / "a").rmdir()  # not empty
except OSError as exc:  # OSError
    print("OSError:", exc.strerror)  # reason
# Output: OSError: Directory not empty
(d / "e").mkdir()  # make an empty one
(d / "e").rmdir()  # delete it
print((d / "e").exists())  # gone
# Output: False
```

## 💻 Code Example — Advanced
```python
# Production style: copy/move, safe cleanup job with dry-run, temp dir, backup zip
import os  # utime, chdir
import shutil  # file tree operations
import tempfile  # temp folder
import time  # timestamps
from pathlib import Path  # paths
from typing import List  # type hints

d: Path = Path(tempfile.mkdtemp())  # base folder
(d / "a" / "b").mkdir(parents=True)  # structure
for name in ("1.txt", "2.py", "a/3.txt", "a/b/4.py"):  # sample files
    (d / name).write_text(name)  # write

# Copy a whole tree
shutil.copytree(d / "a", d / "a_copy")  # copy folder recursively
print(sorted(str(p.relative_to(d / "a_copy")) for p in (d / "a_copy").rglob("*")))
# Output: ['3.txt', 'b', 'b/4.py']
try:  # target must not exist by default
    shutil.copytree(d / "a", d / "a_copy")  # exists now
except FileExistsError:  # error
    print("FileExistsError")  # message
# Output: FileExistsError
shutil.copytree(d / "a", d / "a_copy", dirs_exist_ok=True)  # merge allowed (3.8+)

# Copy / move single files
shutil.copy2(d / "1.txt", d / "1_copy.txt")  # copy and keep timestamps
shutil.move(d / "1_copy.txt", d / "a" / "moved.txt")  # move to another folder
print((d / "a" / "moved.txt").read_text())  # content survived
# Output: 1.txt

# Delete a whole tree (dangerous: no recycle bin)
shutil.rmtree(d / "a_copy")  # delete folder + contents
print((d / "a_copy").exists())  # gone
# Output: False
try:  # missing folder raises
    shutil.rmtree(d / "nothere")  # does not exist
except FileNotFoundError:  # error
    print("FileNotFoundError from rmtree")  # message
# Output: FileNotFoundError from rmtree
shutil.rmtree(d / "nothere", ignore_errors=True)  # silent version


# A cleanup job: delete old files, with a dry-run safety switch
def cleanup_old(folder: Path, days: int, dry_run: bool = True) -> List[str]:
    """Return names of .txt files older than N days; delete them if dry_run=False."""
    cutoff: float = time.time() - days * 86400  # seconds since epoch
    removed: List[str] = []  # report
    for f in folder.rglob("*.txt"):  # all txt files below folder
        if f.is_file() and f.stat().st_mtime < cutoff:  # old enough
            removed.append(f.name)  # record it
            if not dry_run:  # only delete when asked
                f.unlink()  # delete file
    return removed  # what was (or would be) deleted


old_time: float = time.time() - 10 * 86400  # 10 days ago
os.utime(d / "1.txt", (old_time, old_time))  # fake an old modification time
print(cleanup_old(d, 7))  # dry run: nothing deleted
# Output: ['1.txt']
print((d / "1.txt").exists())  # still there
# Output: True
print(cleanup_old(d, 7, dry_run=False))  # real run
# Output: ['1.txt']
print((d / "1.txt").exists())  # deleted
# Output: False

# Backup as zip
zip_path: str = shutil.make_archive(str(d / "bk"), "zip", d / "a")  # bk.zip of folder a
print(zip_path.endswith("bk.zip"))  # created
# Output: True

# Temporary directory deleted automatically
with tempfile.TemporaryDirectory() as td:  # created here
    print(Path(td).is_dir())  # exists inside
    # Output: True
print(Path(td).exists())  # removed after the block
# Output: False

# Pitfall: rmtree refuses a symlink (it would never follow it)
os.symlink(d / "a", d / "link")  # symlink to folder a
try:  # try rmtree on the link
    shutil.rmtree(d / "link")  # refused
except OSError:  # "Cannot call rmtree on a symbolic link"
    print("OSError: use unlink() for symlinks")  # message
# Output: OSError: use unlink() for symlinks
(d / "link").unlink()  # correct way to remove the link
print((d / "a").exists())  # the real folder is untouched
# Output: True
```
Verified on Python 3.13.3 (macOS). The `errno` for "Directory not empty" is 66 on macOS and 39 on Linux, so compare `exc.errno == errno.ENOTEMPTY` instead of a number. `Path.walk()` is new in Python 3.12.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python way
from pathlib import Path
import shutil
Path("out/2026/01").mkdir(parents=True, exist_ok=True)
for p in Path("docs").rglob("*.pdf"):
    print(p)
shutil.rmtree("tmp_build", ignore_errors=True)
```
```javascript
// JavaScript way (Node.js 20+)
import { mkdirSync, readdirSync, rmSync } from "node:fs";
mkdirSync("out/2026/01", { recursive: true });              // mkdir -p
for (const f of readdirSync("docs", { recursive: true })) { // Node 20+: recursive listing
  if (f.endsWith(".pdf")) console.log(f);
}
rmSync("tmp_build", { recursive: true, force: true });      // rm -rf
// Copy tree: fs.cpSync(src, dst, { recursive: true })
```

Key differences: Python splits the work between `pathlib` (paths, glob), `os` (walk, listdir) and `shutil` (copy, move, rmtree). Node keeps it inside `fs` with options like `recursive` and `force`. Python raises specific exceptions (`FileExistsError`); Node uses error codes (`EEXIST`).

---

## 🟠 FastAPI Connection
Typical uses: create the upload folder at startup (lifespan), per-user folders, scheduled cleanup of temp files, listing available reports. Run blocking folder work in a normal `def` endpoint (thread pool), not in `async def`.

```python
# FastAPI: create the folder at startup, list reports (pip install fastapi)
import tempfile  # temp folder
from contextlib import asynccontextmanager  # lifespan helper
from pathlib import Path  # paths
from typing import AsyncIterator, List  # type hints
from fastapi import FastAPI  # framework

REPORTS: Path = Path(tempfile.mkdtemp()) / "reports"  # reports folder (not created yet)


@asynccontextmanager  # startup / shutdown handler
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    REPORTS.mkdir(parents=True, exist_ok=True)  # safe to run on every start
    (REPORTS / "jan.csv").write_text("a,b\n1,2\n")  # sample data
    yield  # app runs here


app: FastAPI = FastAPI(lifespan=lifespan)  # app with lifespan


@app.get("/reports")  # GET /reports
def list_reports() -> List[str]:
    return sorted(p.name for p in REPORTS.glob("*.csv"))  # def -> runs in thread pool
# Tested with TestClient (inside "with TestClient(app)" so lifespan runs): GET /reports -> ["jan.csv"]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `rmdir` on a non-empty folder / `rmtree` with a wrong variable
✅ Correct:

```python
# Wrong - OSError: Directory not empty
Path("build").rmdir()
# Right (but double-check the path first!)
shutil.rmtree("build")
# Safer: print the target or use a dry-run before deleting anything
```

❌ Mistake 2: `mkdir` without `parents` / `exist_ok`
✅ Correct:

```python
# Wrong - FileNotFoundError if parent missing, FileExistsError on rerun
Path("out/2026/01").mkdir()
# Right
Path("out/2026/01").mkdir(parents=True, exist_ok=True)
```

❌ Mistake 3: Changing the list while walking, or trusting unsorted order
✅ Correct:

```python
# Wrong - order of iterdir()/listdir()/glob() is arbitrary (OS dependent)
for p in folder.iterdir(): ...
# Right - sort when order matters (tests, reports)
for p in sorted(folder.iterdir()): ...
# To skip folders inside os.walk, edit `dirs` IN PLACE: dirs[:] = [d for d in dirs if d != ".git"]
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from pathlib import Path
import tempfile, shutil
d = Path(tempfile.mkdtemp())
(d / "a").mkdir()
(d / "a" / "f.txt").write_text("x")
try:
    (d / "a").rmdir()
except OSError as e:
    print("1", type(e).__name__)
try:
    (d / "a").mkdir()
except OSError as e:
    print("2", type(e).__name__)
shutil.rmtree(d / "a")
print("3", (d / "a").exists())
(d / "a").mkdir(exist_ok=True)
print("4", list((d / "a").iterdir()))
```

**Answer**:
```
1 OSError
2 FileExistsError
3 False
4 []
```
`rmdir` on a non-empty folder raises plain `OSError` (no special subclass). `mkdir` on an existing folder raises `FileExistsError`, which is a subclass of `OSError`, so the same `except OSError` catches both. After `rmtree` everything is gone, and the recreated folder is empty. (Verified on Python 3.13.)

---

## ⚫ Interview Questions + Answers

Q1: `os.listdir` vs `Path.iterdir` vs `os.scandir`?
A1: `listdir` returns name strings. `iterdir` returns `Path` objects lazily. `scandir` returns `DirEntry` objects that already know `is_dir()` without another system call, so it is the fastest for big folders (and `os.walk` uses it).

Q2: `glob` vs `rglob`?
A2: `glob("*.py")` searches one level; `rglob("*.py")` is the same as `glob("**/*.py")` and searches all sub-folders.

Q3: How do you delete a non-empty folder?
A3: `shutil.rmtree(path)`. `Path.rmdir()` and `os.rmdir()` work only on empty folders. `rmtree` cannot be undone.

Q4: How do you copy a folder?
A4: `shutil.copytree(src, dst)`; use `dirs_exist_ok=True` (3.8+) to merge into an existing target, and `ignore=shutil.ignore_patterns("*.pyc")` to skip files.

Q5: How do you avoid a race condition between `exists()` and `mkdir()`?
A5: Do not check first. Call `mkdir(exist_ok=True)` or catch the exception (EAFP style), because another process may change things between your check and your action.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Creating output/upload folders, rotating logs, cleaning temp files
- Finding files by pattern (`rglob("*.pdf")`)
- Backups and deployment scripts (copytree, make_archive)

❌ Avoid when:
- Watching a folder for changes live (use `watchdog`)
- Deleting with `rmtree` on a path built from user input (validate it first)
- Millions of files and you need speed: prefer `os.scandir` or `os.walk`

---

## 📊 Visual Diagram

```
d/
├── 1.txt
├── 2.py
└── a/
    ├── 3.txt
    └── b/
        └── 4.py

d.iterdir()      -> 1.txt, 2.py, a                 (one level)
d.glob("*.txt")  -> 1.txt                          (one level, pattern)
d.rglob("*.py")  -> 2.py, a/b/4.py                 (all levels)
os.walk(d)       -> (d,[a],[1.txt,2.py]) (d/a,[b],[3.txt]) (d/a/b,[],[4.py])
shutil.rmtree(d/"a") -> deletes a, 3.txt, b, 4.py
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| mkdir | Create a folder | folder बनाना |
| iterdir | List items in one folder | एक folder की items |
| glob / rglob | Pattern search (one / all levels) | pattern से खोज |
| os.walk | Visit every folder in a tree | पूरे tree में घूमना |
| shutil | High-level file operations | high-level file काम |
| rmtree | Delete folder with contents | folder और सब कुछ delete |

---

## ⚡ 3-Line Summary
English: Use `Path.mkdir(parents=True, exist_ok=True)` to create, `iterdir/glob/rglob/walk` to look, `shutil.copytree/move` to copy and `shutil.rmtree` to delete. `rmdir` only removes empty folders. Add a dry-run before any delete job.
Hindi: बनाने के लिए `Path.mkdir(parents=True, exist_ok=True)`, देखने के लिए `iterdir/glob/rglob/walk`, copy के लिए `shutil.copytree/move` और delete के लिए `shutil.rmtree` इस्तेमाल करें। `rmdir` सिर्फ खाली folder हटाता है। किसी भी delete job से पहले dry-run रखें।

---

## ➡️ Next Topic
**212. File Metadata** — size, timestamps and permissions with `stat()` and `os`.
