---

# 213. Temporary Files
# हिंदी में: Temporary Files (अस्थायी फ़ाइलें और folders)

---

## 🔵 Simple Definition (English)
The `tempfile` module creates temporary files and directories with unique, unguessable names in the system temp folder. They are deleted automatically when you close them or leave a `with` block. It is the safe replacement for hand-made names like `/tmp/data.txt`.

## 🔵 सरल परिभाषा (Hindi)
`tempfile` module system के temp folder में unique और अनुमान न लगाए जा सकने वाले नामों से अस्थायी files और directories बनाता है। `with` block खत्म होते ही या close करते ही ये अपने-आप delete हो जाती हैं। `/tmp/data.txt` जैसे हाथ से बनाए नामों का यह सुरक्षित विकल्प है।

---

## 🔴 Problem it Solves
Hand-made temp names collide when two requests run together (one overwrites the other), leave junk behind after crashes, and can be pre-created by an attacker as a symlink to a sensitive file (a classic security bug). `tempfile` creates the file atomically with permission 0600 and a random name, and cleans up for you.

## 🔴 यह क्यों बना? (Hindi)
हाथ से बनाए temp नाम तब टकराते हैं जब दो requests साथ चलें (एक दूसरी को overwrite कर देती है), crash के बाद कचरा छोड़ते हैं, और attacker उसी नाम से किसी ज़रूरी फ़ाइल का symlink पहले से बना सकता है (पुराना security bug)। `tempfile` फ़ाइल atomically, 0600 permission और random नाम से बनाता है और cleanup भी खुद करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → tempfile picks a random unique name in gettempdir()
Step 2 → Creates it atomically (O_EXCL) with mode 0600 (owner only)
Step 3 → Returns a file object (or path / fd for mkstemp)
Step 4 → You read and write like a normal file
Step 5 → Leaving 'with' closes it and DELETES it (if delete=True)
Step 6 → For crash-safe saves: write temp in same folder, then os.replace()
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → tempfile gettempdir() में random unique नाम चुनता है
Step 2 → उसे atomically (O_EXCL) और mode 0600 (सिर्फ़ owner) के साथ बनाता है
Step 3 → file object (या mkstemp में path / fd) लौटाता है
Step 4 → आप सामान्य फ़ाइल की तरह पढ़ते-लिखते हैं
Step 5 → 'with' से निकलते ही close होकर DELETE हो जाती है (delete=True हो तो)
Step 6 → crash-safe save के लिए: उसी folder में temp लिखो, फिर os.replace()
```

---

## 🟡 Real World Example
A Razorpay settlement job downloads a 2 GB CSV, processes it in a `TemporaryDirectory`, and the folder vanishes even if the job crashes. A FastAPI endpoint streams an uploaded PDF to a temp file before running OCR. A config writer saves `settings.json` via a temp file and `os.replace` so readers never see a half-written file.

## 🟡 Real Example Hindi mein
Razorpay की settlement job 2 GB की CSV download करके `TemporaryDirectory` में process करती है, और job crash हो तब भी folder गायब हो जाता है। FastAPI endpoint upload हुई PDF को OCR से पहले temp file में stream करता है। Config writer `settings.json` को temp file + `os.replace` से save करता है ताकि readers को कभी आधी लिखी फ़ाइल न दिखे।

---

## 💻 Code Example — Basic
```python
import tempfile, os  # tempfile module
from pathlib import Path

with tempfile.TemporaryFile("w+", encoding="utf-8") as tf:  # anonymous file, no name on disk
    tf.write("scratch data")  # write
    tf.seek(0)  # rewind to start
    print(tf.read())  # read back

with tempfile.NamedTemporaryFile("w+", suffix=".csv", prefix="rep_", delete=False) as nf:  # has a real name
    nf.write("a,b\n1,2\n")  # write rows
    path = Path(nf.name)  # remember the path
print(path.suffix, path.name.startswith("rep_"), path.exists())  # file survives (delete=False)
path.unlink()  # we must clean up ourselves
print(path.exists())

with tempfile.TemporaryDirectory(prefix="job_") as d:  # temp folder
    (Path(d) / "x.txt").write_text("x")  # put a file inside
    print(os.listdir(d))
print(Path(d).exists())  # folder removed on exit

fd, name = tempfile.mkstemp(suffix=".tmp")  # low-level: returns (fd, path)
os.write(fd, b"raw")  # write bytes via fd
os.close(fd)  # you must close the fd
print(os.path.getsize(name))
os.remove(name)
print(tempfile.gettempdir() == str(Path(tempfile.gettempdir())))
```

**Real output** (Python 3.13.3):
```
scratch data
.csv True True
False
['x.txt']
False
3
True
```

Notes: `TemporaryFile` has no visible name on Unix. `NamedTemporaryFile` has a name but, on Windows, cannot be reopened while open (3.12 added `delete_on_close=False` for that). `mkstemp` gives YOU the cleanup duty.

## 💻 Code Example — Advanced
```python
from __future__ import annotations
import csv, os, tempfile  # imports
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


def atomic_write(target: Path, data: str) -> None:
    """Write to a temp file in the SAME folder, then os.replace (atomic on same filesystem)."""
    fd, tmp_name = tempfile.mkstemp(dir=target.parent, prefix=target.name, suffix=".tmp")  # same dir
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:  # wrap fd in file object
            fh.write(data)  # write everything
            fh.flush()  # python buffer -> OS
            os.fsync(fh.fileno())  # OS -> disk
        os.replace(tmp_name, target)  # atomic swap
    except BaseException:  # any failure
        Path(tmp_name).unlink(missing_ok=True)  # remove half-written temp
        raise


@contextmanager
def workspace(prefix: str = "etl_") -> Iterator[Path]:
    with tempfile.TemporaryDirectory(prefix=prefix) as d:  # auto-clean even on error
        yield Path(d)


with workspace() as ws:
    cfg = ws / "config.json"
    atomic_write(cfg, '{"v": 1}')
    atomic_write(cfg, '{"v": 2}')  # replaces safely
    print(cfg.read_text(), sorted(p.name for p in ws.iterdir()))
    with tempfile.SpooledTemporaryFile(max_size=20, mode="w+") as sp:  # memory until 20 bytes
        sp.write("short")
        print(sp._rolled)  # private attr: still in memory
        sp.write("x" * 50)  # exceeds max_size
        print(sp._rolled)  # now on disk
    try:
        with workspace() as w2:
            (w2 / "big.dat").write_bytes(b"1")
            kept = w2
            raise RuntimeError("job failed")
    except RuntimeError as e:
        print(e, kept.exists())  # folder cleaned anyway
```

**Real output** (Python 3.13.3):
```
{"v": 2} ['config.json']
False
True
job failed False
```

`os.replace` is atomic only when source and target are on the same filesystem, which is why the temp file is created with `dir=target.parent`. `SpooledTemporaryFile._rolled` is a private attribute, used here only to show the switch from memory to disk.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import tempfile
with tempfile.TemporaryDirectory() as d:   # auto-removed on exit
    print(d)
with tempfile.NamedTemporaryFile("w", suffix=".txt") as f:
    f.write("hi")
```

```javascript
// JavaScript (Node.js)
const fs = require("fs"), os = require("os"), path = require("path");
const dir = fs.mkdtempSync(path.join(os.tmpdir(), "job-"));  // you must clean up
try { fs.writeFileSync(path.join(dir, "a.txt"), "hi"); }
finally { fs.rmSync(dir, { recursive: true, force: true }); }
// Node 20+: fs.promises.mkdtempDisposable (newer) / npm 'tmp' package
```

Node only gives `mkdtemp`; you write the `try/finally` cleanup yourself (or use the `tmp` package). Python's context managers make cleanup automatic, even when an exception is raised.

---

## 🟠 FastAPI Connection
Upload endpoints should never keep a whole file in RAM. Stream `UploadFile.file` into a temporary file with `shutil.copyfileobj`, process it, then delete it. (FastAPI's `UploadFile` is itself a `SpooledTemporaryFile` that moves to disk above 1 MB.)

```python
import tempfile, shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile
from fastapi.testclient import TestClient
app = FastAPI()
@app.post("/upload")
async def upload(file: UploadFile) -> dict[str, int]:
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename or "").suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)  # stream to disk, not RAM
        p = Path(tmp.name)
    try:
        return {"bytes": p.stat().st_size}
    finally:
        p.unlink(missing_ok=True)
c = TestClient(app)
print(c.post("/upload", files={"file": ("a.txt", b"hello" * 10)}).json())
```

**Real output** (Python 3.13.3):
```
{'bytes': 50}
```


---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Predictable names like /tmp/output.csv
```python
# Wrong - two requests overwrite each other, attacker can pre-create it
open("/tmp/output.csv", "w")

# Right
with tempfile.NamedTemporaryFile("w", suffix=".csv") as f:
    ...
```

❌ Mistake 2: Reading a temp file before flushing
```python
# Wrong - text is still in Python's buffer, other readers see ''
with tempfile.NamedTemporaryFile("w") as f:
    f.write("abc")
    print(Path(f.name).read_text())   # ''

# Right
    f.flush()                          # now visible on disk
```

❌ Mistake 3: Forgetting cleanup with mkstemp or delete=False
```python
# Wrong - leaks a file and an open descriptor
fd, name = tempfile.mkstemp()

# Right
fd, name = tempfile.mkstemp()
try:
    os.close(fd)        # close the descriptor
    ...                 # use name
finally:
    os.unlink(name)     # remove the file
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import tempfile
from pathlib import Path
with tempfile.NamedTemporaryFile("w") as f:
    f.write("abc")
    print(repr(Path(f.name).read_text()))
    f.flush()
    print(repr(Path(f.name).read_text()))
print(Path(f.name).exists())
```

**Answer** (real run on Python 3.13.3):
```
''
'abc'
False
```
Writes are buffered, so another reader sees an empty string until `flush()`. After the `with` block the file is deleted, so `exists()` is `False`. (On Windows the first `read_text()` would even fail with PermissionError because the file is still open.)

---

## ⚫ Interview Questions + Answers

Q1: Difference between `TemporaryFile` and `NamedTemporaryFile`?
A1: `TemporaryFile` may have no directory entry at all (Unix), so no other process can open it by name. `NamedTemporaryFile` has a real `.name` you can pass to other programs, which is why most real code uses it.

Q2: Why is `mkstemp` safer than `mktemp`?
A2: `mktemp` only returns a name (deprecated), so another process can create it before you do. `mkstemp` creates the file atomically with 0600 and returns an open descriptor, removing the race.

Q3: How do you write a file so readers never see a half-written one?
A3: Write to a temp file in the same directory, `flush()` + `os.fsync()`, then `os.replace(tmp, target)` which is atomic on one filesystem.

Q4: What is `SpooledTemporaryFile`?
A4: It lives in memory until `max_size` is exceeded, then rolls over to a real disk file. Good for many small uploads with a few huge ones.

Q5: Where do temp files go and can I change it?
A5: `tempfile.gettempdir()` checks `TMPDIR`, `TEMP`, `TMP`, then `/tmp`. Pass `dir=` per call or set `tempfile.tempdir`; in containers mount a volume if the files are large.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You need scratch space for uploads, downloads, conversions
- You want unique names and automatic cleanup
- You need atomic file replacement (write temp, then rename)

❌ Avoid when:
- The data must survive restarts (use a real path or database)
- /tmp is a small RAM disk (tmpfs) and the file is huge
- You need a stable name other processes expect

---

## 📊 Visual Diagram

```
with TemporaryDirectory() as d:
   |-- create /tmp/job_k3x9a (random, 0700)
   |-- your code writes d/x.txt ...
   +-- exit (even on exception)
          |
          v
   rmtree(d)  -> everything inside is gone

atomic save:  config.json.tmp --(os.replace)--> config.json
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| tempfile | Module for temporary files | अस्थायी files का module |
| mkstemp | Low-level: returns (fd, path) | निचले स्तर का function |
| Atomic | All-or-nothing operation | पूरा या बिल्कुल नहीं |
| fsync | Force data to disk | डेटा को disk पर पक्का करना |
| Spooled | In memory first, disk if big | पहले memory, बड़ा हो तो disk |
| Race condition | Timing-dependent bug | समय पर निर्भर bug |

---

## ⚡ 3-Line Summary
English: `tempfile` gives unique, private, self-cleaning files and folders. Prefer `with TemporaryDirectory()` and `NamedTemporaryFile`; for crash-safe saves write a temp file in the same folder and `os.replace` it.
Hindi: `tempfile` unique, private और खुद साफ़ होने वाली files/folders देता है। `with TemporaryDirectory()` और `NamedTemporaryFile` इस्तेमाल करें; crash-safe save के लिए उसी folder में temp लिखकर `os.replace` करें।

---

## ➡️ Next Topic
**214. File Compression (zipfile, gzip)** — bundle and shrink files, and extract archives without security holes.
