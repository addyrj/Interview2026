---

# 189. tempfile Module
# हिंदी में: tempfile Module (अस्थायी files और folders)

---

## 🔵 Simple Definition (English)
`tempfile` creates temporary files and folders with unique, unpredictable names in a safe location, and (with context managers) deletes them automatically. Use it for scratch data that you do not need after the job is done.

## 🔵 सरल परिभाषा (Hindi)
`tempfile` सुरक्षित जगह पर unique और अनुमान न लगने वाले नामों के साथ अस्थायी files और folders बनाता है, और context manager के साथ उन्हें अपने आप delete कर देता है। जिस scratch data की काम खत्म होने के बाद ज़रूरत नहीं, उसके लिए इसे इस्तेमाल करें।

---

## 🔴 Problem it Solves
Hand made temp names like `/tmp/output.txt` collide when two requests run together, can be guessed by an attacker (symlink attack), and are often forgotten and never deleted, filling the disk. `tempfile` creates the file atomically with permission `0600`, picks a random name and cleans up.

## 🔴 यह क्यों बना? (Hindi)
हाथ से बनाए नाम जैसे `/tmp/output.txt` दो requests साथ चलने पर टकराते हैं, attacker अनुमान लगा सकता है (symlink attack), और अक्सर delete करना भूल जाते हैं जिससे disk भर जाती है। `tempfile` file को atomically `0600` permission के साथ बनाता है, random नाम चुनता है और सफाई करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Picks a base folder: TMPDIR env, then the OS default (gettempdir())
Step 2 → Generates a random name (prefix + random + suffix)
Step 3 → Creates it with O_EXCL (fails instead of reusing an existing name)
Step 4 → File mode 0600 / folder mode 0700 → only the owner can access
Step 5 → TemporaryFile / TemporaryDirectory delete on exit of "with"
Step 6 → mkstemp / mkdtemp do NOT delete: you must clean up yourself
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Base folder चुनता है: पहले TMPDIR env, फिर OS default (gettempdir())
Step 2 → Random नाम बनाता है (prefix + random + suffix)
Step 3 → O_EXCL के साथ बनाता है (पुराना नाम दोबारा नहीं लेता, fail हो जाता है)
Step 4 → File mode 0600 / folder mode 0700 → सिर्फ owner access कर सकता है
Step 5 → TemporaryFile / TemporaryDirectory "with" खत्म होते ही delete हो जाते हैं
Step 6 → mkstemp / mkdtemp delete नहीं करते: सफाई आपको खुद करनी है
```

---

## 🟡 Real World Example
A Razorpay invoice service renders a PDF into a temp folder, uploads it to S3, and lets the folder vanish. A pytest suite uses `TemporaryDirectory` so tests never touch real data. An AI app unzips a user-uploaded dataset into a temp folder, runs embedding, and cleans up even if the job crashes.

## 🟡 Real Example Hindi mein
Razorpay की invoice service PDF को temp folder में बनाती है, S3 पर upload करती है और folder अपने आप गायब हो जाता है। pytest suite `TemporaryDirectory` इस्तेमाल करती है ताकि tests असली data को न छुएँ। AI app user का upload किया dataset temp folder में unzip करती है, embedding चलाती है और job crash होने पर भी सफाई हो जाती है।

---

## 💻 Code Example — Basic
```python
# Basic tempfile examples - every line commented
import os  # os-level file handles
import tempfile  # temporary files and folders
from pathlib import Path  # path objects

with tempfile.TemporaryFile(mode="w+") as tf:  # anonymous temp file, deleted on exit
    tf.write("scratch data")  # write text
    tf.seek(0)  # go back to start
    print(tf.read())  # read it back

with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", prefix="rep_") as nf:  # has a name
    nf.write("hello")  # write
    nf.flush()  # push data to disk so others can read it
    print(Path(nf.name).name.startswith("rep_"), nf.name.endswith(".txt"))  # name pattern
    print(Path(nf.name).read_text())  # another reader sees the data
    saved: str = nf.name  # remember the name
print(os.path.exists(saved))  # deleted after the with block -> False

with tempfile.TemporaryDirectory(prefix="job_") as d:  # temp folder
    p: Path = Path(d)  # wrap it
    (p / "x.txt").write_text("1")  # create a file inside
    print(p.name.startswith("job_"), (p / "x.txt").exists())  # True True
print(p.exists())  # whole folder removed -> False

print(tempfile.gettempdir() != "")  # system temp folder (differs per OS)

fd, path = tempfile.mkstemp(suffix=".bin")  # low level: returns (open fd, path)
os.write(fd, b"\x01\x02")  # write bytes through the descriptor
os.close(fd)  # YOU must close the descriptor
print(Path(path).stat().st_size)  # 2 bytes
os.remove(path)  # YOU must delete it too
```

Output (verified by running; ids/timestamps/paths may vary):
```
scratch data
True True
hello
False
True True
False
True
2
```

## 💻 Code Example — Advanced
```python
# Production style: safe workspace, atomic replace, spooled files, keep-on-error (3.12+)
import os  # fsync and replace
import tempfile  # temp helpers
from pathlib import Path  # paths
from typing import Iterator, List  # type hints
from contextlib import contextmanager  # build a custom context manager


def atomic_write_text(target: Path, text: str) -> None:
    """Write via a temp file in the SAME folder, then replace atomically."""
    fd, tmp_name = tempfile.mkstemp(dir=target.parent, prefix=target.name + ".", suffix=".tmp")
    try:  # make sure the temp file never lingers
        with os.fdopen(fd, "w", encoding="utf-8") as f:  # wrap the descriptor
            f.write(text)  # write all content
            f.flush()  # flush Python buffer
            os.fsync(f.fileno())  # flush OS buffer to disk
        os.replace(tmp_name, target)  # atomic swap
    except BaseException:  # any failure
        Path(tmp_name).unlink(missing_ok=True)  # clean up the temp file
        raise  # re-raise the real error


@contextmanager
def workspace(keep_on_error: bool = True) -> Iterator[Path]:
    """Temp folder that is kept for debugging if the job fails (3.12+: delete=False)."""
    tmp = tempfile.TemporaryDirectory(prefix="etl_", delete=False)  # delete param is 3.12+
    path: Path = Path(tmp.name)  # folder path
    try:  # run the job
        yield path  # give the folder to the caller
    except BaseException:  # job failed
        if not keep_on_error:  # caller wants cleanup
            tmp.cleanup()  # remove now
        else:  # keep it for debugging
            print("kept for debugging:", path.name.startswith("etl_"))  # info line
        raise  # propagate
    else:  # success path
        tmp.cleanup()  # always remove after success


with tempfile.TemporaryDirectory() as root:  # sandbox for the demo
    target: Path = Path(root) / "config.json"  # final file
    atomic_write_text(target, '{"v": 1}')  # first write
    atomic_write_text(target, '{"v": 2}')  # second write
    print(target.read_text(), [p.name for p in Path(root).iterdir()])  # no stray .tmp

with workspace() as w:  # successful job
    (w / "out.csv").write_text("a,b")  # work in the folder
    ok_path: Path = w  # remember it
print("after success exists:", ok_path.exists())  # False

try:  # failing job
    with workspace() as w2:  # create workspace
        bad_path: Path = w2  # remember
        raise RuntimeError("boom")  # job fails
except RuntimeError as exc:  # caught outside
    print("error:", exc, "| folder kept:", bad_path.exists())  # True
    import shutil  # clean our demo leftover
    shutil.rmtree(bad_path)  # remove it

with tempfile.SpooledTemporaryFile(max_size=10, mode="w+") as sp:  # RAM until 10 bytes
    sp.write("tiny")  # still in memory
    print("rolled to disk:", getattr(sp, "_rolled", None))  # False (private attr, demo only)
    sp.write("-now-bigger-than-ten")  # exceeds max_size
    print("rolled to disk:", getattr(sp, "_rolled", None))  # True

with tempfile.NamedTemporaryFile("w+", delete_on_close=False) as nf:  # 3.12+ option
    nf.write("data")  # write
    nf.close()  # closes the handle, file STILL exists (Windows friendly)
    print(Path(nf.name).read_text())  # reopen by name and read
print(Path(nf.name).exists())  # removed when the with block ends
```

Output (verified by running; ids/timestamps/paths may vary):
```
{"v": 2} ['config.json']
after success exists: False
kept for debugging: True
error: boom | folder kept: True
rolled to disk: False
rolled to disk: True
data
False
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import tempfile
with tempfile.TemporaryDirectory() as d:     # auto delete on exit
    print(d)
with tempfile.NamedTemporaryFile("w+") as f: # auto delete on exit
    f.write("x")
```

```javascript
// JavaScript (Node.js)
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
const dir = await fs.mkdtemp(path.join(os.tmpdir(), "job-"));   // creates folder
try {
  /* work in dir */
} finally {
  await fs.rm(dir, { recursive: true, force: true });           // you must clean up
}
```

Key differences: Node's `mkdtemp` only creates the folder; you write the try/finally cleanup yourself. Python's context managers make cleanup automatic.

---

## 🟠 FastAPI Connection
Use `tempfile` inside endpoints and background tasks that process an upload: save to a temp folder, work, return, and let the `with` block delete everything. Never use the client's file name for the path. FastAPI's own `UploadFile` already uses a `SpooledTemporaryFile` under the hood (small uploads stay in RAM, big ones spill to disk).

```python
# FastAPI: process an upload in a temp folder that is always cleaned (pip install fastapi httpx python-multipart)
import tempfile  # temp folder
from pathlib import Path  # paths
from typing import Dict  # type hints
from fastapi import FastAPI, UploadFile  # app + upload

app: FastAPI = FastAPI()  # create app


@app.post("/count-lines")  # POST /count-lines
def count_lines(file: UploadFile) -> Dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="upload_") as tmp:  # private workspace
        dest: Path = Path(tmp) / "input.txt"  # fixed safe name, ignore user's name
        dest.write_bytes(file.file.read())  # save upload
        lines: int = len(dest.read_text().splitlines())  # do the work
    return {"lines": lines, "cleaned": not dest.exists()}  # folder is gone here
```

Output (verified by running; ids/timestamps/paths may vary):
```
{'lines': 3, 'cleaned': True}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `mktemp()` (insecure, deprecated)
```python
# Wrong - returns a name only; another process can grab it before you create it
# name = tempfile.mktemp()

# Correct
# with tempfile.NamedTemporaryFile() as f: ...   # or mkstemp()
```

❌ Mistake 2: Reading a `NamedTemporaryFile` before flushing
```python
# Wrong - data may still sit in Python's buffer, so a second reader sees an empty file
# f.write("abc"); Path(f.name).read_text()  -> ""

# Correct
# f.write("abc"); f.flush(); Path(f.name).read_text()  -> "abc"
```

❌ Mistake 3: Forgetting to close/delete `mkstemp` results
```python
# Wrong - leaks a file descriptor AND a file
# fd, path = tempfile.mkstemp()

# Correct
# fd, path = tempfile.mkstemp()
# try: os.write(fd, b"x")
# finally: os.close(fd); os.remove(path)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import tempfile, os
from pathlib import Path

with tempfile.NamedTemporaryFile("w") as f:
    f.write("abc")
    print(Path(f.name).read_text() == "")
    f.flush()
    print(Path(f.name).read_text())
d = tempfile.mkdtemp()
print(os.path.isdir(d))
with tempfile.TemporaryDirectory() as t:
    pass
print(os.path.exists(t))
```

**Answer**:
```
True
abc
True
False
```
Before `flush()` the text is still in Python's buffer, so the file on disk is empty (for such a small write). `mkdtemp()` never deletes, so the folder stays until you remove it. `TemporaryDirectory` removes its folder when the `with` block ends. (Verified by running.)

---

## ⚫ Interview Questions + Answers

Q1: `TemporaryFile` vs `NamedTemporaryFile`?
A1: `TemporaryFile` may have no visible name on Unix (so nobody else can open it). `NamedTemporaryFile` has a real name in `.name`, so other code or processes can open it by path.

Q2: Why can't I reopen a `NamedTemporaryFile` on Windows?
A2: While it is open, Windows blocks a second open. Python 3.12 added `delete_on_close=False`: you can close it, reopen by name, and it is deleted when the `with` block ends.

Q3: When do I use `mkstemp` instead?
A3: When you need full control, for example the atomic-write pattern: create a temp file in the target folder, write, `fsync`, then `os.replace`. You must close and delete it yourself.

Q4: What is `SpooledTemporaryFile`?
A4: A file kept in memory until it exceeds `max_size`, then moved to a real temp file. Great for variable-size uploads.

Q5: Why create the temp file in the same folder as the final file?
A5: `os.replace` is atomic only inside one filesystem. `/tmp` is often a different mount (or RAM disk), so a cross-device rename fails or becomes copy+delete.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Intermediate files for a single job or request
- Tests that must not touch real data
- Atomic file replacement (`mkstemp` in the target folder)

❌ Avoid when:
- The data must survive restart (use a real folder or object storage)
- Several processes must find the same file by name (use a known path)
- You expect `/tmp` to be large (containers often have a small RAM `/tmp`)

---

## 📊 Visual Diagram

```
with TemporaryDirectory() as d:        /tmp/tmpab12cd/   (mode 0700)
    ├─ input.txt                         created inside
    ├─ output.csv                        created inside
    └─ ...
 (block ends) ───────────────────────►   folder + contents deleted

 mkstemp() ──► (fd, "/tmp/tmpxyz.bin")   YOU close(fd) and remove(path)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TemporaryFile | Unnamed auto-deleted file | बिना नाम की अपने-आप हटने वाली file |
| NamedTemporaryFile | Temp file with a visible name | नाम वाली अस्थायी file |
| TemporaryDirectory | Auto-deleted temp folder | अपने-आप हटने वाला folder |
| mkstemp | Low-level, you clean up | low-level, सफाई खुद |
| Spooled | RAM first, disk if large | पहले RAM, बड़ा हो तो disk |
| Race condition | Two actors collide on one name | एक नाम पर दो का टकराव |

---

## ⚡ 3-Line Summary
English: `tempfile` makes secure, uniquely named temporary files and folders. Prefer `TemporaryDirectory` / `NamedTemporaryFile` with `with`, avoid `mktemp()`, and use `mkstemp` in the target folder for atomic writes.
Hindi: `tempfile` सुरक्षित और unique नाम वाली अस्थायी files व folders बनाता है। `with` के साथ `TemporaryDirectory` / `NamedTemporaryFile` लें, `mktemp()` से बचें, और atomic write के लिए target folder में `mkstemp` इस्तेमाल करें।

---

## ➡️ Next Topic
**190. json Module** — turn Python data into text (and back) for APIs and config files.
