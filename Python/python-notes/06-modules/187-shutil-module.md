---

# 187. shutil Module
# हिंदी में: shutil Module (files और folders की copy, move, delete, archive)

---

## 🔵 Simple Definition (English)
`shutil` ("shell utilities") does high level file jobs: copy a file, copy a whole folder, move, delete a folder tree, create or extract zip/tar archives, check disk space and find programs on `PATH`. `pathlib` can create and read files, but `shutil` does the bulk operations.

## 🔵 सरल परिभाषा (Hindi)
`shutil` ("shell utilities") बड़े file कामों के लिए है: file copy करना, पूरा folder copy करना, move, folder tree delete, zip/tar archive बनाना या खोलना, disk space देखना और `PATH` में program खोजना। `pathlib` file बना और पढ़ सकता है, लेकिन bulk काम `shutil` करता है।

---

## 🔴 Problem it Solves
Without `shutil` you would write loops with `os.walk`, open files, copy bytes, fix permissions and handle cross-disk moves yourself. Deleting a non-empty folder with `os.rmdir` fails. `shutil` gives tested one-line functions for all of this, and works on every OS.

## 🔴 यह क्यों बना? (Hindi)
`shutil` के बिना आपको `os.walk` के loops, bytes copy, permissions और अलग-अलग disk के बीच move खुद लिखने पड़ते। `os.rmdir` से खाली न होने वाला folder delete नहीं होता। `shutil` इन सबके लिए tested one-line functions देता है, जो हर OS पर चलते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → copy(src, dst): copies content + permission bits (not timestamps)
Step 2 → copy2(src, dst): also keeps timestamps and metadata
Step 3 → copytree(src, dst): walks the tree and copies every file
Step 4 → move(src, dst): tries os.rename; if on another disk, copy then delete
Step 5 → rmtree(path): deletes files first, then the empty folders
Step 6 → make_archive / unpack_archive: zip or tar a folder and back
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → copy(src, dst): content और permission bits copy होते हैं (timestamps नहीं)
Step 2 → copy2(src, dst): timestamps और metadata भी रखता है
Step 3 → copytree(src, dst): पूरा tree घूमकर हर file copy करता है
Step 4 → move(src, dst): पहले os.rename; दूसरी disk पर हो तो copy फिर delete
Step 5 → rmtree(path): पहले files, फिर खाली folders delete करता है
Step 6 → make_archive / unpack_archive: folder का zip/tar बनाना और वापस खोलना
```

---

## 🟡 Real World Example
A Swiggy-style nightly job archives `logs/2025-11-10/` into a zip with `make_archive`, uploads it to S3, then removes the folder with `rmtree`. A FastAPI upload endpoint streams big videos to disk with `copyfileobj`. A deployment script copies the project to `release/` with `copytree(..., ignore=ignore_patterns("__pycache__", "*.tmp"))`.

## 🟡 Real Example Hindi mein
Swiggy जैसी nightly job `logs/2025-11-10/` को `make_archive` से zip करती है, S3 पर upload करती है और फिर `rmtree` से folder हटा देती है। FastAPI upload endpoint बड़े videos को `copyfileobj` से disk पर stream करता है। Deployment script `copytree(..., ignore=ignore_patterns("__pycache__", "*.tmp"))` से project को `release/` में copy करती है।

---

## 💻 Code Example — Basic
```python
# Basic shutil examples - every line commented
import shutil  # high level file operations
import tempfile  # throw-away folder
from pathlib import Path  # path objects

with tempfile.TemporaryDirectory() as tmp:  # auto cleanup
    base: Path = Path(tmp)  # root of the demo
    src: Path = base / "src"  # source folder
    (src / "sub").mkdir(parents=True)  # create nested folders
    (src / "a.txt").write_text("alpha")  # file 1
    (src / "sub" / "b.txt").write_text("beta")  # file 2

    shutil.copy(src / "a.txt", base / "a_copy.txt")  # copy content + permissions
    print((base / "a_copy.txt").read_text())  # same content

    shutil.copytree(src, base / "backup")  # copy a whole folder tree
    print(sorted(p.relative_to(base).as_posix() for p in (base / "backup").rglob("*")))

    shutil.copytree(src, base / "backup", dirs_exist_ok=True)  # allow existing target (3.8+)

    shutil.move(str(base / "a_copy.txt"), str(base / "moved.txt"))  # move / rename
    print((base / "a_copy.txt").exists(), (base / "moved.txt").exists())

    shutil.rmtree(base / "backup")  # delete a folder and everything inside
    print((base / "backup").exists())  # gone

    total, used, free = shutil.disk_usage(base)  # disk numbers in bytes
    print(total > used >= 0 and free > 0)  # sanity check only (values differ per machine)

    print(shutil.which("python3") is not None)  # find an executable on PATH
    print(shutil.which("no-such-tool-xyz"))  # missing tool -> None
```

Output (verified by running; ids/timestamps/paths may vary):
```
alpha
['backup/a.txt', 'backup/sub', 'backup/sub/b.txt']
False True
False
True
True
None
```

## 💻 Code Example — Advanced
```python
# Production style: archive, restore, safe delete, streaming copy, ignore patterns
import shutil  # file helpers
import tempfile  # sandbox
from pathlib import Path  # paths
from typing import Any, Callable, List  # type hints


def make_backup(src: Path, out_dir: Path, name: str) -> Path:
    """Zip a folder and return the archive path."""
    archive: str = shutil.make_archive(str(out_dir / name), "zip", root_dir=src)  # adds .zip
    return Path(archive)  # wrap in Path


def safe_rmtree(path: Path) -> List[str]:
    """Delete a tree, collect errors instead of crashing (3.12+ uses onexc)."""
    errors: List[str] = []  # collect failures

    def on_error(func: Callable[..., Any], p: str, exc: BaseException) -> None:
        errors.append(f"{func.__name__}:{Path(p).name}:{type(exc).__name__}")  # note it

    shutil.rmtree(path, onexc=on_error)  # onexc replaced onerror in 3.12
    return errors  # empty list means clean delete


def copy_stream(src: Path, dst: Path, chunk: int = 1024 * 64) -> int:
    """Copy big files in chunks so memory stays small."""
    with src.open("rb") as fin, dst.open("wb") as fout:  # open both files
        shutil.copyfileobj(fin, fout, length=chunk)  # chunked copy
    return dst.stat().st_size  # bytes written


with tempfile.TemporaryDirectory() as tmp:  # sandbox
    base: Path = Path(tmp)  # root
    app: Path = base / "app"  # project folder
    (app / "__pycache__").mkdir(parents=True)  # junk folder
    (app / "main.py").write_text("print('hi')")  # real file
    (app / "notes.tmp").write_text("junk")  # junk file
    (app / "__pycache__" / "main.cpython-313.pyc").write_bytes(b"\x00")  # junk bytes

    ignore = shutil.ignore_patterns("*.tmp", "__pycache__")  # skip rules
    shutil.copytree(app, base / "release", ignore=ignore)  # copy without junk
    print(sorted(p.name for p in (base / "release").rglob("*")))  # only main.py

    zip_path: Path = make_backup(base / "release", base, "release_v1")  # create zip
    print(zip_path.name, zip_path.stat().st_size > 0)  # name + non empty

    shutil.unpack_archive(zip_path, base / "restored")  # extract (format by extension)
    print(sorted(p.name for p in (base / "restored").iterdir()))  # restored files

    big: Path = base / "big.bin"  # a 1 MB file
    big.write_bytes(b"x" * 1_000_000)  # create it
    print(copy_stream(big, base / "big_copy.bin"), "bytes copied")  # chunk copy

    print(safe_rmtree(base / "app"), (base / "app").exists())  # [] False
    try:  # deleting a missing tree
        shutil.rmtree(base / "app")  # missing path
    except FileNotFoundError as exc:  # expected
        print("FileNotFoundError:", type(exc).__name__)  # show type
    shutil.rmtree(base / "app", ignore_errors=True)  # silently ignore instead
```

Output (verified by running; ids/timestamps/paths may vary):
```
['main.py']
release_v1.zip True
['main.py']
1000000 bytes copied
[] False
FileNotFoundError: FileNotFoundError
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import shutil
shutil.copy("a.txt", "b.txt")                       # copy file
shutil.copytree("src", "dst", dirs_exist_ok=True)   # copy folder
shutil.move("b.txt", "archive/b.txt")               # move
shutil.rmtree("dst")                                # rm -rf
```

```javascript
// JavaScript (Node.js 16.7+ has fs.cp)
import fs from "node:fs/promises";
await fs.copyFile("a.txt", "b.txt");                    // copy file
await fs.cp("src", "dst", { recursive: true });         // copy folder
await fs.rename("b.txt", "archive/b.txt");              // move (same disk only)
await fs.rm("dst", { recursive: true, force: true });   // rm -rf
```

Key differences: Node `rename` fails across disks (EXDEV) while `shutil.move` falls back to copy+delete automatically. Python has built in archive support (`make_archive`), Node needs a package like `archiver`.

---

## 🟠 FastAPI Connection
FastAPI's `UploadFile` exposes a file-like object in `.file`. The standard pattern is `shutil.copyfileobj(file.file, out)`, which copies in chunks so a 2 GB video does not fill RAM. Always keep only `Path(name).name` so a hostile file name cannot escape the folder.

```python
# FastAPI: save an uploaded file with shutil.copyfileobj (pip install fastapi httpx python-multipart)
import tempfile  # demo folder
from pathlib import Path  # paths
import shutil  # streaming copy
from typing import Dict  # type hints
from fastapi import FastAPI, UploadFile  # app + upload type

UPLOAD_DIR: Path = Path(tempfile.mkdtemp())  # real app: a configured folder
app: FastAPI = FastAPI()  # create app


@app.post("/upload")  # POST /upload
def upload(file: UploadFile) -> Dict[str, int]:
    name: str = Path(file.filename or "unnamed").name  # strip folders from the name
    dest: Path = UPLOAD_DIR / name  # final location
    with dest.open("wb") as out:  # open destination in binary
        shutil.copyfileobj(file.file, out)  # stream, never load whole file in RAM
    return {"bytes": dest.stat().st_size}  # report size
```

Output (verified by running; ids/timestamps/paths may vary):
```
200 {'bytes': 11} ['evil.txt']
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `os.rmdir` / `os.remove` for folders with content
```python
# Wrong - OSError: Directory not empty
# os.rmdir("build")

# Correct
# shutil.rmtree("build", ignore_errors=True)
```

❌ Mistake 2: `copytree` into an existing folder (before 3.8 habits)
```python
# Wrong - FileExistsError on the second run
# shutil.copytree("src", "dst")

# Correct - allow merging into the existing folder (3.8+)
# shutil.copytree("src", "dst", dirs_exist_ok=True)
```

❌ Mistake 3: Using the old `onerror` argument on new Python
```python
# Wrong - onerror is deprecated since 3.12
# shutil.rmtree(p, onerror=handler)       # handler(func, path, exc_info)

# Correct - 3.12+ gets the exception object itself
# shutil.rmtree(p, onexc=handler)         # handler(func, path, exc)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output (`a.txt` and an empty folder `d/` exist in `base`)?

```python
import shutil
from pathlib import Path

print(Path(shutil.copy(base / "a.txt", base / "d")).relative_to(base))
shutil.copytree(base / "d", base / "d2")
try:
    shutil.copytree(base / "d", base / "d2")
except FileExistsError:
    print("FileExistsError")
(base / "e").mkdir()
print(Path(shutil.move(base / "a.txt", base / "e")).relative_to(base))
print(shutil.rmtree(base / "e"), (base / "e").exists())
```

**Answer**:
```
d/a.txt
FileExistsError
e/a.txt
None False
```
When the destination is an existing directory, `copy` and `move` put the file INSIDE it, keeping its name (not overwrite the directory). A second `copytree` to an existing target fails unless `dirs_exist_ok=True`. `rmtree` returns `None`. (Verified by running.)

---

## ⚫ Interview Questions + Answers

Q1: Difference between `copy`, `copy2` and `copyfile`?
A1: `copyfile` copies only content and needs a full file destination. `copy` adds permission bits and accepts a directory destination. `copy2` also preserves timestamps and as much metadata as possible.

Q2: How does `shutil.move` work across disks?
A2: It first tries `os.rename`. If that fails (different filesystems), it copies the data with `copy2` and then deletes the source.

Q3: How do you delete a read-only file during `rmtree` on Windows?
A3: Pass an error handler (`onexc` on 3.12+, `onerror` before) that does `os.chmod(path, stat.S_IWRITE)` and retries the failed function.

Q4: How do you avoid loading a huge file into memory while copying?
A4: Use `shutil.copyfileobj(fin, fout, length=chunk_size)`. `copy`/`copyfile` already use fast OS level copying internally.

Q5: Is `shutil.rmtree` safe against symlink attacks?
A5: On modern platforms it uses fd-based functions and does not follow symlinks to delete outside the tree, but never call it on a path built from raw user input; validate it first.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Copying, moving or deleting whole directory trees
- Creating or extracting zip/tar backups
- Streaming an upload to disk (`copyfileobj`)

❌ Avoid when:
- You only need to create or read one small file (use `pathlib`)
- You need a transactional/atomic multi-file update (use a temp folder + rename)
- You delete user supplied paths without validation

---

## 📊 Visual Diagram

```
copy()      a.txt ──► b.txt          (content + permissions)
copy2()     a.txt ──► b.txt          (+ timestamps)
copytree()  src/ ──► dst/            (recursive)
move()      A ─rename─► B            same disk
            A ─copy2─► B ─delete A   different disk
rmtree()    build/  ✖  (files first, then folders)
make_archive("rel","zip",src) ─► rel.zip ─unpack_archive─► folder
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| copytree | Copy a directory recursively | folder को पूरा copy करना |
| rmtree | Delete a directory recursively | folder को पूरा delete करना |
| archive | One file holding many files (zip/tar) | कई files वाली एक file |
| copyfileobj | Chunked copy between file objects | chunks में copy |
| ignore_patterns | Skip names matching patterns | pattern वाले नाम छोड़ना |
| onexc | Error callback for rmtree (3.12+) | rmtree error handler |

---

## ⚡ 3-Line Summary
English: `shutil` handles bulk file work: `copy`, `copytree`, `move`, `rmtree`, archives and disk usage. Use `copyfileobj` to stream big files and `ignore_patterns` to skip junk. On 3.12+ use `onexc`, not `onerror`.
Hindi: `shutil` bulk file काम करता है: `copy`, `copytree`, `move`, `rmtree`, archives और disk usage। बड़ी files stream करने के लिए `copyfileobj` और junk छोड़ने के लिए `ignore_patterns` लें। 3.12+ में `onerror` नहीं, `onexc` इस्तेमाल करें।

---

## ➡️ Next Topic
**188. glob Module** — find many files by pattern like `*.csv` before you copy or process them.
