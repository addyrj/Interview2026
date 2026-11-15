---

# 214. File Compression (zipfile, gzip)
# हिंदी में: File Compression (zipfile और gzip से फ़ाइलें compress करना)

---

## 🔵 Simple Definition (English)
`zipfile` packs many files into one `.zip` archive (each file compressed separately, random access). `gzip` compresses ONE stream of bytes into a `.gz` file (usually combined with `tar` as `.tar.gz`). Both are in the standard library and use the DEFLATE algorithm via `zlib`.

## 🔵 सरल परिभाषा (Hindi)
`zipfile` कई files को एक `.zip` archive में पैक करता है (हर फ़ाइल अलग compress होती है, किसी भी फ़ाइल को सीधे पढ़ सकते हैं)। `gzip` bytes के एक stream को `.gz` में compress करता है (अक्सर `tar` के साथ `.tar.gz`)। दोनों standard library में हैं और `zlib` के DEFLATE algorithm पर चलते हैं।

---

## 🔴 Problem it Solves
Large logs, CSV exports and backups waste disk space and network bandwidth. Sending 500 separate files is slow and error-prone. Compression shrinks text 5x to 10x, and an archive bundles everything into one file. Untrusted archives are also dangerous (zip-slip, zip bombs), so you need to know how to extract them safely.

## 🔴 यह क्यों बना? (Hindi)
बड़े logs, CSV exports और backups disk और network bandwidth बर्बाद करते हैं। 500 अलग files भेजना धीमा और गलती-prone है। Compression text को 5x से 10x छोटा कर देता है और archive सबको एक file में बाँध देता है। Untrusted archives खतरनाक भी होते हैं (zip-slip, zip bomb), इसलिए उन्हें सुरक्षित तरीके से extract करना आना चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Open ZipFile(path, 'w', ZIP_DEFLATED) or gzip.open(path, 'wb')
Step 2 → Add data: zf.write(file, arcname) / zf.writestr(name, text) / write bytes to gz
Step 3 → DEFLATE finds repeated patterns and encodes them in fewer bits
Step 4 → Close (with-block) -> central directory (zip) or trailer CRC (gzip) is written
Step 5 → Read: zf.namelist(), zf.read(name), zf.extractall(dest) / gzip.open(path, 'rt')
Step 6 → Before extracting untrusted zips: check paths and total size
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → ZipFile(path, 'w', ZIP_DEFLATED) या gzip.open(path, 'wb') खोलो
Step 2 → data जोड़ो: zf.write(file, arcname) / zf.writestr(name, text) / gz में bytes लिखो
Step 3 → DEFLATE दोहराए पैटर्न ढूँढकर उन्हें कम bits में लिखता है
Step 4 → Close (with-block) पर central directory (zip) या CRC trailer (gzip) लिखा जाता है
Step 5 → पढ़ना: zf.namelist(), zf.read(name), zf.extractall(dest) / gzip.open(path, 'rt')
Step 6 → Untrusted zip extract करने से पहले paths और कुल size जाँचो
```

---

## 🟡 Real World Example
Zomato's nightly job gzips 20 GB of order logs before uploading to S3. A GST tool lets users download all invoices of a month as one ZIP. A FastAPI server turns on `GZipMiddleware` so large JSON responses are compressed. A data-science upload endpoint accepts a ZIP of images and must reject archives that try to write outside the target folder.

## 🟡 Real Example Hindi mein
Zomato की nightly job S3 पर upload से पहले 20 GB के order logs gzip करती है। GST tool में user पूरे महीने के invoices एक ZIP में download करता है। FastAPI server में `GZipMiddleware` चालू करने से बड़े JSON responses compress होकर जाते हैं। Data-science upload endpoint जो images की ZIP लेता है, उसे ऐसे archive reject करने होते हैं जो target folder के बाहर लिखने की कोशिश करें।

---

## 💻 Code Example — Basic
```python
import zipfile, gzip, shutil, tempfile  # compression modules
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    d = Path(tmp)
    (d / "a.txt").write_text("hello " * 1000)  # compressible text
    (d / "b.txt").write_text("world")
    zp = d / "out.zip"
    with zipfile.ZipFile(zp, "w", compression=zipfile.ZIP_DEFLATED) as zf:  # create zip
        zf.write(d / "a.txt", arcname="a.txt")  # add file
        zf.writestr("notes/readme.txt", "inline text")  # add from string
    with zipfile.ZipFile(zp) as zf:  # open for reading
        print(zf.namelist())
        info = zf.getinfo("a.txt")
        print(info.file_size, info.compress_size < info.file_size)
        print(zf.read("b.txt") if "b.txt" in zf.namelist() else "b.txt not in zip")
        zf.extractall(d / "unzipped")  # extract all
    print(sorted(p.name for p in (d / "unzipped").iterdir()))

    gz = d / "a.txt.gz"
    with open(d / "a.txt", "rb") as src, gzip.open(gz, "wb") as dst:  # stream compress
        shutil.copyfileobj(src, dst)
    print(gz.stat().st_size < (d / "a.txt").stat().st_size)
    with gzip.open(gz, "rt", encoding="utf-8") as fh:  # text mode read
        print(fh.read(11))
    print(gzip.decompress(gzip.compress(b"abc")))
```

**Real output** (Python 3.13.3):
```
['a.txt', 'notes/readme.txt']
6000 True
b.txt not in zip
['a.txt', 'notes']
True
hello hello
b'abc'
```

Notes: `info.file_size` is the original size, `info.compress_size` the stored size. `extractall` creates the `notes/` folder from the name `notes/readme.txt`.

## 💻 Code Example — Advanced
```python
from __future__ import annotations
import gzip, io, shutil, tempfile, zipfile
from pathlib import Path


def safe_extract(zip_path: Path, dest: Path, max_total: int = 10_000_000) -> list[str]:
    """Extract zip safely: block zip-slip and zip bombs."""
    dest = dest.resolve()  # absolute target
    names: list[str] = []
    with zipfile.ZipFile(zip_path) as zf:
        total = sum(i.file_size for i in zf.infolist())  # declared uncompressed size
        if total > max_total:  # zip bomb guard
            raise ValueError(f"archive too large: {total}")
        for info in zf.infolist():
            target = (dest / info.filename).resolve()  # where it would land
            if dest not in target.parents and target != dest:  # path traversal ("../")
                raise ValueError(f"unsafe path: {info.filename}")
            names.append(info.filename)
        zf.extractall(dest)  # all checked, now extract
    return names


def zip_folder(src: Path, out: Path) -> int:
    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for p in sorted(src.rglob("*")):  # walk recursively
            if p.is_file():
                zf.write(p, p.relative_to(src))  # keep relative path inside zip
                count += 1
    return count


with tempfile.TemporaryDirectory() as tmp:
    d = Path(tmp)
    (d / "src" / "sub").mkdir(parents=True)
    (d / "src" / "x.log").write_text("log line\n" * 500)
    (d / "src" / "sub" / "y.log").write_text("y")
    print(zip_folder(d / "src", d / "bundle.zip"))
    print(safe_extract(d / "bundle.zip", d / "out"))
    evil = d / "evil.zip"
    with zipfile.ZipFile(evil, "w") as zf:
        zf.writestr("../escape.txt", "pwned")
    try:
        safe_extract(evil, d / "out2")
    except ValueError as e:
        print("blocked:", e)
    # in-memory gzip for HTTP-like payloads
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as g:
        g.write(b'{"k": 1}' * 100)
    print(len(buf.getvalue()) < 800, gzip.decompress(buf.getvalue())[:8])
    shutil.make_archive(str(d / "snap"), "gztar", d / "src")  # tar.gz in one call
    print((d / "snap.tar.gz").exists())
```

**Real output** (Python 3.13.3):
```
2
['sub/y.log', 'x.log']
blocked: unsafe path: ../escape.txt
True b'{"k": 1}'
True
```

`zipfile` in 3.12+ already strips leading `/` and `..` in `extract`, but checking yourself is still the right habit, and the size check protects against zip bombs. Declared sizes in headers can lie, so for hostile input also cap bytes while reading.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import zipfile, gzip
with zipfile.ZipFile("out.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write("a.txt")
data = gzip.compress(b"hello")
```

```javascript
// JavaScript (Node.js)
const zlib = require("zlib");
const gz = zlib.gzipSync(Buffer.from("hello"));      // built in
// zip files need a package: npm i adm-zip   (or archiver, jszip)
const AdmZip = require("adm-zip");
const z = new AdmZip(); z.addLocalFile("a.txt"); z.writeZip("out.zip");
```

Node has gzip/deflate (`zlib`) built in but no ZIP support; you install `adm-zip` or `archiver`. Python ships both `zipfile` and `gzip`, plus `tarfile` and `shutil.make_archive`.

---

## 🟠 FastAPI Connection
Two common uses: `GZipMiddleware` compresses large responses automatically (clients send `Accept-Encoding: gzip`), and an export endpoint builds a ZIP in memory with `io.BytesIO` and returns it as a `StreamingResponse` with a `Content-Disposition` header.

```python
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import StreamingResponse
from fastapi.testclient import TestClient
import io, zipfile
app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=500)
@app.get("/big")
def big() -> dict[str, str]:
    return {"data": "x" * 5000}
@app.get("/export.zip")
def export() -> StreamingResponse:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("report.csv", "id,amt\n1,100\n")
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/zip", headers={"Content-Disposition": 'attachment; filename="export.zip"'})
c = TestClient(app)
r = c.get("/big", headers={"Accept-Encoding": "gzip"})
print(r.headers.get("content-encoding"), len(r.json()["data"]))
z = c.get("/export.zip")
print(z.headers["content-type"], zipfile.ZipFile(io.BytesIO(z.content)).namelist())
```

**Real output** (Python 3.13.3):
```
gzip 5000
application/zip ['report.csv']
```


---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Extracting untrusted zips blindly (zip-slip)
```python
# Wrong - a name like ../../etc/cron.d/x writes outside the folder
zipfile.ZipFile(upload).extractall("/srv/data")

# Right - validate every member path and total size first (see safe_extract above)
```

❌ Mistake 2: Forgetting ZIP_DEFLATED (default is no compression!)
```python
# Wrong - default compression=ZIP_STORED: file is just bundled, not smaller
zipfile.ZipFile("a.zip", "w")

# Right
zipfile.ZipFile("a.zip", "w", compression=zipfile.ZIP_DEFLATED)
```

❌ Mistake 3: Reading a huge .gz fully into memory
```python
# Wrong - 5 GB in RAM
data = gzip.open("big.gz").read()

# Right - iterate line by line (streaming)
with gzip.open("big.gz", "rt", encoding="utf-8") as fh:
    for line in fh:
        ...
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import zipfile, io, gzip, warnings
warnings.simplefilter("ignore")
b = io.BytesIO()
with zipfile.ZipFile(b, "w") as z:
    z.writestr("a.txt", "1"); z.writestr("a.txt", "2")
with zipfile.ZipFile(b) as z:
    print(z.namelist(), z.read("a.txt"))
print(gzip.decompress(gzip.compress(b"a") * 2))
```

**Answer** (real run on Python 3.13.3):
```
['a.txt', 'a.txt'] b'2'
b'aa'
```
ZIP allows duplicate names (Python only warns with a `UserWarning`), so `namelist()` has two entries and `read` returns the LAST one written. Concatenated gzip members are valid, so `decompress` joins them into `b'aa'`.

---

## ⚫ Interview Questions + Answers

Q1: ZIP vs GZIP vs TAR?
A1: ZIP = archive + compression per file with random access. GZIP = compression of a single stream only. TAR = archive only (no compression), so `.tar.gz` = tar then gzip. ZIP can extract one file quickly; tar.gz must be read sequentially.

Q2: What is a zip bomb and how do you defend?
A2: A tiny file that expands to terabytes (e.g. 42.zip). Check the sum of `file_size` before extracting, limit the number of members, and cap bytes read while streaming.

Q3: What is zip-slip?
A3: Member names containing `../` that escape the extraction folder. Resolve each target path and make sure it is inside the destination before writing.

Q4: How do you compress a file without loading it in memory?
A4: Use `shutil.copyfileobj(src, gzip_file)` which copies in chunks (about 64 KB at a time). Same for reading with `gzip.open(..., 'rt')` in a loop.

Q5: Which compression level should I pick?
A5: `compresslevel` goes 0-9 (zip/gzip). 6 is the default balance; 9 is slower with small gains; 1 is fast. For JSON logs use 6. For speed at scale consider zstd (third party, or `compression.zstd` in Python 3.14).

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Bundling many files for download or backup (zip)
- Compressing one big text/log stream (gzip)
- Reducing network size for API responses (GZipMiddleware)

❌ Avoid when:
- Data is already compressed (JPEG, MP4, PNG, existing zip): little gain, wasted CPU
- Archive comes from users and you skip safety checks
- You need random updates inside the archive often (use a database)

---

## 📊 Visual Diagram

```
ZIP (many files, random access)        GZIP (one stream)
+----------------------------+          +----------------------+
| a.txt  (deflated)          |          | header               |
| notes/readme.txt (deflated)|          | deflated bytes ....  |
| central directory (index)  | <- read  | CRC32 + size trailer |
+----------------------------+   first  +----------------------+
zf.read("a.txt") jumps directly        must read from the start

tar.gz = tar (bundle)  --->  gzip (compress)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Archive | One file holding many files | कई files वाली एक file |
| DEFLATE | Compression algorithm of zip/gzip | zip/gzip का compression algorithm |
| arcname | Name stored inside the zip | zip के अंदर का नाम |
| Zip-slip | Extraction escaping the folder via ../ | ../ से folder के बाहर लिखना |
| Zip bomb | Tiny file that expands hugely | छोटी file जो बहुत बड़ी खुलती है |
| Stream | Data processed in chunks | टुकड़ों में data process करना |

---

## ⚡ 3-Line Summary
English: Use `zipfile` for multi-file archives and `gzip` for single streams; set `ZIP_DEFLATED` explicitly. Stream large data and never extract untrusted archives without checking paths and total size.
Hindi: कई files के लिए `zipfile`, एक stream के लिए `gzip`; `ZIP_DEFLATED` ज़रूर दें। बड़े data को stream करें और untrusted archive को paths और कुल size जाँचे बिना extract न करें।

---

## ➡️ Next Topic
**215. Pickle Module** — serialise Python objects to bytes, and why unpickling untrusted data is dangerous.
