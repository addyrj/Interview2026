---

# Q228. File upload example
# Category: FASTAPI + WEB QUESTIONS
# Difficulty: ⭐⭐

---

## ❓ Question
Create an `/upload` endpoint that accepts a file, rejects wrong content types (415) and files over 1 KB (413), and returns name/size/type. Then show multi-file upload that saves to disk in chunks.

---

## 💡 Quick Concept (2 lines only)
Use `UploadFile` (spooled to disk, async `read()`) instead of `bytes` so big files don't live fully in RAM. Needs `python-multipart` installed.
हिंदी: बड़ी file के लिए `UploadFile` use करो और type/size हमेशा validate करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from fastapi import FastAPI, UploadFile, File, HTTPException  # upload types
from fastapi.testclient import TestClient  # client

app = FastAPI()  # app
MAX_BYTES = 1024  # 1 KB limit for demo
ALLOWED = {"text/plain", "image/png"}  # allowed content types

@app.post("/upload")  # endpoint
async def upload(file: UploadFile = File(...)) -> dict[str, object]:  # UploadFile streams from disk/memory
    if file.content_type not in ALLOWED:  # Step 1: validate type
        raise HTTPException(415, "unsupported type")  # 415 Unsupported Media Type
    data = await file.read()  # Step 2: read bytes (async)
    if len(data) > MAX_BYTES:  # Step 3: validate size
        raise HTTPException(413, "too large")  # 413 Payload Too Large
    return {"name": file.filename, "size": len(data), "type": file.content_type}  # metadata

# ============================================
# TEST CASES
# ============================================
client = TestClient(app)  # client
ok = client.post("/upload", files={"file": ("a.txt", b"hello", "text/plain")})  # valid file
print(ok.status_code, ok.json())  # Expected: 200 {'name': 'a.txt', 'size': 5, 'type': 'text/plain'}
bad = client.post("/upload", files={"file": ("a.exe", b"MZ", "application/octet-stream")})  # bad type
print(bad.status_code)  # Expected: 415
big = client.post("/upload", files={"file": ("b.txt", b"x" * 2000, "text/plain")})  # too big
print(big.status_code)  # Expected: 413
print(client.post("/upload").status_code)  # Expected: 422 (file missing)
```

---

## 🔍 Why This Works (3 lines max)
`UploadFile` wraps a spooled temp file; `await file.read()` or chunked reads avoid loading everything at once. Never trust `content_type` or `filename` from the client alone — use `pathlib.Path(name).name` to stop `../` path tricks.
हिंदी: Client का filename/content-type भरोसेमंद नहीं है — `Path(name).name` से path traversal रोको।

---

## ⚡ Alternative Solution
```python
# (same file as above — reuses its imports/names)
# ---- Alternative: multiple files + save to disk in chunks ----
import tempfile, pathlib  # temp dir for saving

app2 = FastAPI()  # app
tmp = pathlib.Path(tempfile.mkdtemp())  # temp folder

@app2.post("/multi")  # endpoint
async def multi(files: list[UploadFile]) -> dict[str, list[int]]:  # many files
    sizes: list[int] = []  # collect sizes
    for f in files:  # loop files
        total = 0  # counter
        with open(tmp / pathlib.Path(f.filename or "x").name, "wb") as out:  # .name blocks ../ path tricks
            while chunk := await f.read(4):  # read 4 bytes at a time (tiny for demo)
                out.write(chunk)  # write chunk
                total += len(chunk)  # count
        sizes.append(total)  # store
    return {"sizes": sizes}  # result

r = TestClient(app2).post("/multi", files=[("files", ("a.txt", b"abcdefghij", "text/plain")), ("files", ("b.txt", b"xy", "text/plain"))])  # two files
print(r.json())  # Expected: {'sizes': [10, 2]}
print(sorted(p.name for p in tmp.iterdir()))  # Expected: ['a.txt', 'b.txt']
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using bytes -> the whole file is loaded in memory, no filename/content-type
@app.post("/upload")
async def upload(file: bytes = File(...)): ...

# ❌ Wrong: saving with the raw client filename -> "../../etc/x" escapes the folder
open(f"uploads/{file.filename}", "wb")

# ✅ Correct: UploadFile + sanitise name + read in chunks
open(dir / Path(file.filename).name, "wb")
```

---

## 🎯 Interview Tip (1 line)
Say: "UploadFile streams from a spooled file; I validate type and size, sanitise the filename, and stream to disk or S3 in chunks."

---

## 🔗 Related Questions
→ Q223 (Pydantic validation) | Q220 (async generators) | Q234 (streaming response) | Q233 (status codes)
