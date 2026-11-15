---

# 483. Build File Upload API
# हिंदी में: File Upload API बनाना

Runnable solution with tests: [main.py](./main.py) (run: `python main.py`, verified on Python 3.13 with fastapi, python-multipart, httpx via TestClient; it uses a temp folder and deletes it).

---

## 🔵 Simple Definition (English)
A file upload API receives a file from a client (multipart/form-data), validates it (type, size, content), saves it somewhere safe under a server-chosen name, and returns an id that can be used to download or delete it later.

## 🔵 सरल परिभाषा (Hindi)
File upload API client से file (multipart/form-data) लेती है, उसे validate करती है (type, size, content), server के चुने नाम से सुरक्षित जगह सहेजती है, और एक id लौटाती है जिससे बाद में download या delete हो सके।

---

## 🔴 Problem it Solves
Uploads are one of the most attacked features. Dangers: huge files exhaust memory/disk, a `.exe` renamed to `.png`, filenames like `../../etc/passwd` (path traversal), overwriting other users' files, and half-written files after failures. A careful upload API streams the data, limits size, checks real content, ignores client file names and cleans up on errors.

## 🔴 यह क्यों बना? (Hindi)
Uploads सबसे ज़्यादा attack होने वाली features में से हैं। खतरे: बहुत बड़ी files से memory/disk खत्म, `.exe` का नाम बदलकर `.png` कर देना, `../../etc/passwd` जैसे filenames (path traversal), दूसरों की files overwrite होना, और failure के बाद अधूरी files बचना। सावधान upload API data को stream करती है, size सीमित करती है, असली content जाँचती है, client के file names अनदेखे करती है और error पर सफाई करती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client sends multipart/form-data with a `file` part
Step 2 → FastAPI gives an UploadFile (spooled temp file, not all in RAM)
Step 3 → Check declared content_type against an allow-list (415 if not)
Step 4 → Generate our own name: uuid4().hex + extension from the allow-list
Step 5 → Read in 64 KB chunks; count bytes; abort with 413 once over the limit
Step 6 → Compute sha256 while streaming (dedup / integrity)
Step 7 → Check magic bytes (PNG: \x89PNG, PDF: %PDF) match the declared type (400)
Step 8 → On any failure delete the partial file
Step 9 → Return id/size/hash; GET /files/{id} downloads, DELETE removes (validate id: no ../)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Client `file` part के साथ multipart/form-data भेजता है
Step 2 → FastAPI एक UploadFile देता है (spooled temp file, पूरा RAM में नहीं)
Step 3 → घोषित content_type को allow-list से मिलाओ (न हो तो 415)
Step 4 → अपना नाम बनाओ: uuid4().hex + allow-list से extension
Step 5 → 64 KB chunks में पढ़ो; bytes गिनो; limit पार होते ही 413 से रोक दो
Step 6 → Streaming के दौरान sha256 निकालो (dedup / integrity)
Step 7 → Magic bytes (PNG: \x89PNG, PDF: %PDF) घोषित type से मिलाओ (न मिले तो 400)
Step 8 → किसी भी failure पर अधूरी file हटा दो
Step 9 → id/size/hash लौटाओ; GET /files/{id} download, DELETE हटाता है (id validate करो: ../ नहीं)
```

---

## 🟡 Real World Example
KYC document upload for a fintech (Aadhaar/PAN scan as PDF or JPG, max 5 MB), profile pictures in a social app, invoice PDFs uploaded to a Razorpay-like dashboard, CSV import for bulk orders. In production the bytes usually go to S3/GCS (often via a presigned URL so the file never touches your API), with only metadata in the database.

## 🟡 Real Example Hindi mein
Fintech के लिए KYC document upload (Aadhaar/PAN scan PDF या JPG, अधिकतम 5 MB), social app की profile pictures, Razorpay जैसे dashboard पर invoice PDFs, bulk orders के लिए CSV import। Production में bytes आमतौर पर S3/GCS में जाते हैं (अक्सर presigned URL से, ताकि file आपकी API से गुज़रे ही नहीं), और database में सिर्फ metadata रहता है।

---

## 💻 Code Example — Basic
```python
# Basic upload endpoint (needs: pip install python-multipart)
from fastapi import FastAPI, File, UploadFile
from fastapi.testclient import TestClient

app = FastAPI()                                # the application

@app.post("/upload")
async def upload(file: UploadFile = File(...)) -> dict[str, str | int]:
    content: bytes = await file.read()         # read all bytes (fine for tiny files only)
    return {"filename": file.filename or "", "size": len(content), "type": file.content_type or ""}

c = TestClient(app)                            # in-process client
r = c.post("/upload", files={"file": ("hello.txt", b"hello world", "text/plain")})
print(r.status_code, r.json())                 # 200 and metadata
print(c.post("/upload").status_code)           # no file sent -> 422

# Output:
# 200 {'filename': 'hello.txt', 'size': 11, 'type': 'text/plain'}
# 422
```

## 💻 Code Example — Advanced
```python
# Production style: streaming, size limit, allow-list, magic bytes, safe names, cleanup
# (full file with download/delete and 10 assertions is main.py)
import hashlib
import tempfile
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.testclient import TestClient

UPLOAD_DIR = Path(tempfile.mkdtemp(prefix="uploads_"))   # use a volume or S3 in production
MAX_BYTES = 1024 * 1024                        # 1 MB
CHUNK = 64 * 1024                              # 64 KB per read
ALLOWED = {"image/png": ".png", "image/jpeg": ".jpg", "application/pdf": ".pdf"}
MAGIC = {b"\x89PNG": "image/png", b"\xff\xd8\xff": "image/jpeg", b"%PDF": "application/pdf"}

app = FastAPI()


def sniff(head: bytes) -> str | None:          # detect type from the real bytes
    for magic, mime in MAGIC.items():
        if head.startswith(magic):
            return mime
    return None


@app.post("/upload", status_code=201)
async def upload(file: Annotated[UploadFile, File()]) -> dict[str, str | int]:
    if file.content_type not in ALLOWED:       # allow-list, not deny-list
        raise HTTPException(415, f"Unsupported type {file.content_type}")
    file_id = uuid.uuid4().hex                 # server-chosen name: no traversal, no collisions
    dest = UPLOAD_DIR / f"{file_id}{ALLOWED[file.content_type]}"
    size, sha, first = 0, hashlib.sha256(), b""
    try:
        with dest.open("wb") as out:
            while chunk := await file.read(CHUNK):   # constant memory
                if not first:
                    first = chunk[:8]          # remember the header bytes
                size += len(chunk)
                if size > MAX_BYTES:
                    raise HTTPException(413, "File too large")
                sha.update(chunk)
                out.write(chunk)
        if sniff(first) != file.content_type:  # header lied about the type
            raise HTTPException(400, "Content does not match declared type")
    except HTTPException:
        dest.unlink(missing_ok=True)           # never leave partial files behind
        raise
    return {"id": file_id, "size": size, "sha256": sha.hexdigest()}


c = TestClient(app)
png = b"\x89PNG\r\n\x1a\n" + b"0" * 100
print(c.post("/upload", files={"file": ("../../evil.png", png, "image/png")}).status_code)   # ok
print(c.post("/upload", files={"file": ("a.txt", b"hi", "text/plain")}).status_code)         # wrong type
print(c.post("/upload", files={"file": ("a.png", b"not a png", "image/png")}).status_code)   # fake png
print(c.post("/upload", files={"file": ("b.png", b"\x89PNG" + b"0" * (MAX_BYTES + 10), "image/png")}).status_code)
print(len(list(UPLOAD_DIR.iterdir())))         # only the one valid file remains
import shutil; shutil.rmtree(UPLOAD_DIR)       # clean the demo folder

# Output:
# 201
# 415
# 400
# 413
# 1
```

---

## 🟠 JavaScript vs Python Comparison
Node uses `multer` or `busboy` for multipart parsing; FastAPI includes the parser (via `python-multipart`). Both can stream; the security checks are the same in either language.

```python
# Python way
@app.post("/upload")
async def upload(file: UploadFile): ...
```
```javascript
// JavaScript way (Express + multer)
const upload = multer({ dest: "uploads/", limits: { fileSize: 1024 * 1024 } });
app.post("/upload", upload.single("file"), (req, res) => res.json({ size: req.file.size }));
```

---

## 🟠 FastAPI Connection
`UploadFile` wraps a `SpooledTemporaryFile` (memory up to a threshold, then disk), has async `read/write/seek/close`, and exposes `filename`, `content_type`. Using `file: UploadFile` instead of `file: bytes` avoids loading the whole file into RAM. Note: FastAPI does not enforce a max size itself, so enforce it in code, at the reverse proxy (nginx `client_max_body_size`) and ideally with a `Content-Length` pre-check. Return a `FileResponse` to download.

```python
from fastapi.responses import FileResponse
@app.get("/files/{file_id}")
def download(file_id: str) -> FileResponse:
    return FileResponse(find_path(file_id))    # streams the file from disk
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: trusting `file.filename` when saving (path traversal, overwrites).
✅ Correct: generate your own name (uuid) and keep the original only as metadata via `Path(name).name`.

```python
# Wrong
open(f"uploads/{file.filename}", "wb")     # filename "../../app.py" overwrites code
# Right
open(UPLOAD_DIR / f"{uuid.uuid4().hex}.png", "wb")
```

❌ Mistake 2: `await file.read()` on the whole upload without a size limit (memory exhaustion, DoS).
✅ Correct: read in chunks and stop at a maximum.

❌ Mistake 3: trusting `content_type` or the extension alone.
✅ Correct: allow-list plus magic-byte check; for risky formats scan/transcode (e.g. re-encode images) and serve with `Content-Disposition: attachment`.

---

## 🧠 Tricky Interview Question
```python
from fastapi import FastAPI, UploadFile
from fastapi.testclient import TestClient

app = FastAPI()

@app.post("/size")
async def size(file: UploadFile) -> dict[str, int]:
    a = len(await file.read())
    b = len(await file.read())
    return {"first": a, "second": b}

r = TestClient(app).post("/size", files={"file": ("x.bin", b"12345", "application/octet-stream")})
print(r.json())
```
Answer: `{'first': 5, 'second': 0}`. Reading advances the file position; the second `read()` starts at the end and returns empty bytes. Call `await file.seek(0)` to read again (for example after validating the header).

---

## ⚫ Interview Questions + Answers

Q1: `bytes` vs `UploadFile` parameter?
A1: `bytes` loads the whole file into memory. `UploadFile` is a spooled temp file with async methods; large files go to disk, so it is the right choice.

Q2: How do you enforce a size limit?
A2: Count bytes while streaming chunks and return 413 when over the limit (as in main.py); also set the limit at nginx/ASGI server level, and pre-check `Content-Length` (which can be faked, so keep the streaming check).

Q3: How do you stop path traversal?
A3: Never use the client name for the storage path; generate ids, validate ids with a strict pattern (`isalnum`), and resolve paths inside a fixed directory.

Q4: Where should production files be stored?
A4: Object storage (S3/GCS) with metadata in the database; use presigned URLs so large uploads bypass your API servers; local disk does not survive scaling to multiple instances.

Q5: Why is `async def` with a blocking file write a problem?
A5: `out.write()` on a normal file blocks the event loop. For big files use `aiofiles` or run the writing in a threadpool (`run_in_threadpool`), or use a plain `def` route.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Users upload documents, images, CSVs of moderate size
- You need validation, scanning, or metadata handling in your own code

❌ Avoid when:
- Files are very large (video): use presigned URLs / resumable uploads (tus, S3 multipart)
- You can offload to a managed service
- Untrusted executable formats would be served back to other users

---

## 📊 Visual Diagram
```
 Client --multipart--> [nginx: client_max_body_size]
                           |
                           v
                  FastAPI UploadFile
                           |
     content_type in allow-list? --no--> 415
                           |yes
          read 64KB chunks, size > MAX? --yes--> 413 (delete partial)
                           |no
          magic bytes match type? --no--> 400 (delete partial)
                           |yes
              saved as  uploads/<uuid>.png
                           |
                  201 {id, size, sha256}
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| multipart/form-data | Request format for files | files भेजने का request format |
| UploadFile | FastAPI's streaming file object | streaming file object |
| Magic bytes | First bytes identifying a file type | file type बताने वाले शुरुआती bytes |
| Path traversal | `../` trick to escape a folder | `../` से folder से बाहर निकलना |
| Presigned URL | Temporary direct-to-S3 link | S3 पर सीधा अस्थायी link |
| 413 / 415 | Too large / unsupported type | बहुत बड़ा / असमर्थित type |

---

## ⚡ 3-Line Summary
English: Accept `UploadFile`, stream in chunks, enforce a size limit and an allow-list of types.
English: Verify real content with magic bytes, store under your own uuid names, delete partial files.
English: In production send big files to object storage and never trust client-provided names or headers.

Hindi: `UploadFile` लो, chunks में stream करो, size limit और allowed types की सूची लागू करो।
Hindi: असली content magic bytes से जाँचो, अपने uuid नामों से सहेजो, अधूरी files हटाओ।
Hindi: Production में बड़ी files object storage में भेजो और client के दिए नाम या headers पर भरोसा मत करो।

---

## ➡️ Next Topic
**484. Build WebSocket Chat** — real-time two-way communication after request/response APIs.

---
