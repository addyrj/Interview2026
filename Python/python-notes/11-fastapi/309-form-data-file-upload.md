---

# 309. Form Data + File Upload
# हिंदी में: Form Data और File Upload (JSON के अलावा request)

---

## 🔵 Simple Definition (English)
Form data is how browsers send HTML form fields (`application/x-www-form-urlencoded`), and multipart form data (`multipart/form-data`) is used when files are included. FastAPI reads them with `Form(...)`, `File(...)` and `UploadFile`. It needs the `python-multipart` package.

## 🔵 सरल परिभाषा (Hindi)
Form data वह तरीका है जिससे browser HTML form के fields भेजता है (`application/x-www-form-urlencoded`), और file के साथ `multipart/form-data` इस्तेमाल होता है। FastAPI इन्हें `Form(...)`, `File(...)` और `UploadFile` से पढ़ता है। इसके लिए `python-multipart` package चाहिए।

---

## 🔴 Problem it Solves
JSON cannot carry a binary file (a photo, a PDF) without ugly base64 encoding that makes it 33% bigger. Plain HTML forms and the OAuth2 login flow also do not send JSON. Multipart lets one request carry text fields and several files together, and `UploadFile` streams big files to disk instead of loading everything in RAM.

## 🔴 यह क्यों बना? (Hindi)
JSON में binary file (photo, PDF) बिना base64 के नहीं जा सकती, और base64 से size 33% बढ़ जाता है। सादे HTML forms और OAuth2 login भी JSON नहीं भेजते। Multipart एक ही request में text fields और कई files भेजने देता है, और `UploadFile` बड़ी file को पूरी RAM में लाने की बजाय disk पर stream करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client sends Content-Type: multipart/form-data; boundary=XYZ
Step 2 → Body is split into parts by the boundary (one part per field/file)
Step 3 → python-multipart parses the parts
Step 4 → Form(...) params get text values; File params get UploadFile objects
Step 5 → Large files are spooled to a temp file (not all in memory)
Step 6 → Your function reads / saves the file; wrong type or size → you raise an error
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Client भेजता है Content-Type: multipart/form-data; boundary=XYZ
Step 2 → Body boundary से हिस्सों में बँटी होती है (हर field/file एक हिस्सा)
Step 3 → python-multipart इन हिस्सों को parse करता है
Step 4 → Form(...) को text मिलता है; File वाले parameter को UploadFile object मिलता है
Step 5 → बड़ी files temp file में रहती हैं (पूरी memory में नहीं)
Step 6 → आपका function file पढ़ता/सेव करता है; गलत type या size पर error आप raise करते हैं
```

---

## 🟡 Real World Example
Swiggy partner app: a restaurant uploads a menu photo plus the fields `name` and `price` in a single `multipart/form-data` request. An AI app (RAG) accepts a PDF upload, reads it, and sends the text to be embedded. The login form `POST /token` uses `username` and `password` as form fields (OAuth2 spec), not JSON.

## 🟡 Real Example Hindi mein
Swiggy partner app में restaurant एक ही `multipart/form-data` request में menu की photo और `name`, `price` fields भेजता है। AI app (RAG) PDF upload लेता है, पढ़ता है और text को embedding के लिए भेजता है। Login form `POST /token` में `username` और `password` form fields होते हैं (OAuth2 नियम), JSON नहीं।

---

## 💻 Code Example — Basic
```python
# Basic Form + File - run directly (pip install fastapi httpx python-multipart)
from typing import Annotated  # modern way to attach metadata to types
from fastapi import FastAPI, File, Form, UploadFile  # form helpers
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # create app


@app.post("/login")  # classic HTML form login
def login(username: Annotated[str, Form()], password: Annotated[str, Form()]) -> dict:  # fields from form body
    return {"user": username, "pw_len": len(password)}  # never echo the password itself


@app.post("/size")  # small file as raw bytes
def size(file: Annotated[bytes, File()]) -> dict:  # whole file is read into memory
    return {"bytes": len(file)}  # size of the file


@app.post("/upload")  # normal way: UploadFile + extra form field
async def upload(file: UploadFile, note: Annotated[str, Form()] = "") -> dict:  # file and text together
    content: bytes = await file.read()  # read the data (async)
    return {  # response with metadata
        "filename": file.filename,  # name sent by client
        "content_type": file.content_type,  # MIME type sent by client
        "size": len(content),  # actual size in bytes
        "note": note,  # the text field
    }


c: TestClient = TestClient(app)  # demo client
print(c.post("/login", data={"username": "asha", "password": "s3cret"}).json())  # form-urlencoded
# Output: {'user': 'asha', 'pw_len': 6}
print(c.post("/size", files={"file": ("a.txt", b"hello")}).json())  # multipart with bytes
# Output: {'bytes': 5}
r = c.post("/upload", files={"file": ("menu.txt", b"biryani 250", "text/plain")}, data={"note": "v1"})  # file + field
print(r.json())  # metadata
# Output: {'filename': 'menu.txt', 'content_type': 'text/plain', 'size': 11, 'note': 'v1'}
print(c.post("/login", json={"username": "a", "password": "b"}).status_code)  # JSON sent to a form endpoint
# Output: 422
```

## 💻 Code Example — Advanced
```python
# Production style: validate type + size while streaming, multiple files, safe filenames
import re  # to clean filenames
import tempfile  # safe temp folder for the demo
import uuid  # unique names
from pathlib import Path  # path handling
from typing import Annotated  # metadata
from fastapi import FastAPI, HTTPException, UploadFile, status  # core
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # app
UPLOAD_DIR: Path = Path(tempfile.mkdtemp())  # in real life: a mounted volume or S3
ALLOWED: set[str] = {"image/png", "image/jpeg"}  # whitelist of types
MAX_BYTES: int = 20  # tiny limit for the demo (use 5 * 1024 * 1024 in production)
CHUNK: int = 8  # read size (use 1 MB in production)


def safe_name(name: str | None) -> str:  # never trust client filenames
    base: str = re.sub(r"[^A-Za-z0-9._-]", "_", Path(name or "file").name)  # strip folders and odd chars
    return f"{uuid.uuid4().hex[:8]}_{base}"  # prefix to avoid collisions/overwrites


async def save_limited(file: UploadFile) -> dict:  # stream to disk with a size cap
    if file.content_type not in ALLOWED:  # check declared type (client controlled, not proof)
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"{file.content_type} not allowed")  # 415
    target: Path = UPLOAD_DIR / safe_name(file.filename)  # final path
    total: int = 0  # bytes so far
    with target.open("wb") as out:  # open destination
        while chunk := await file.read(CHUNK):  # read piece by piece
            total += len(chunk)  # count
            if total > MAX_BYTES:  # too big
                out.close()  # close before deleting
                target.unlink(missing_ok=True)  # remove the partial file
                raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "File too large")  # 413
            out.write(chunk)  # save the piece
    return {"saved_as": target.name, "size": total}  # result


@app.post("/avatars")  # many files at once
async def avatars(files: list[UploadFile]) -> list[dict]:  # list means repeated "files" parts
    return [await save_limited(f) for f in files]  # process each


c: TestClient = TestClient(app)  # demo client
ok = c.post("/avatars", files=[("files", ("a.png", b"12345", "image/png")), ("files", ("../../x.jpg", b"abc", "image/jpeg"))])  # 2 files
print(ok.status_code, [(d["saved_as"][9:], d["size"]) for d in ok.json()])  # names cleaned (random prefix removed)
# Output: 200 [('a.png', 5), ('x.jpg', 3)]
print(c.post("/avatars", files=[("files", ("a.gif", b"1", "image/gif"))]).status_code)  # wrong type
# Output: 415
print(c.post("/avatars", files=[("files", ("big.png", b"x" * 100, "image/png"))]).status_code)  # too big
# Output: 413
print(len(list(UPLOAD_DIR.iterdir())))  # big file was removed, only 2 good ones remain
# Output: 2
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (FastAPI) - receiving
@app.post("/upload")
async def upload(file: UploadFile, title: str = Form()):
    data = await file.read()
```
```javascript
// JavaScript - sending from the browser
const fd = new FormData();            // builds multipart body
fd.append("file", fileInput.files[0]); // the file
fd.append("title", "My menu");        // a text field
await fetch("/upload", { method: "POST", body: fd }); // do NOT set Content-Type manually

// JavaScript (Express + multer) - receiving
app.post("/upload", upload.single("file"), (req, res) => {
  res.json({ name: req.file.originalname, title: req.body.title });
});
```

Key difference: Express needs `multer` (or busboy) and a config for storage. FastAPI parses multipart itself (via `python-multipart`) and gives a typed `UploadFile`. In JS never set the `Content-Type` header yourself for `FormData`, or the boundary is lost.

---

## 🟠 FastAPI Connection
`OAuth2PasswordRequestForm` (used in JWT login) is a form dependency. Swagger UI shows a "choose file" button for `UploadFile`. Because form fields and a JSON body are different encodings, one endpoint cannot accept both `Form` and a JSON body model.

```python
# FastAPI: OAuth2 login form and why Form + JSON body cannot mix
from fastapi import Depends, FastAPI  # app and dependency
from fastapi.security import OAuth2PasswordRequestForm  # form with username/password
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # app


@app.post("/token")  # OAuth2 password flow login
def token(form: OAuth2PasswordRequestForm = Depends()) -> dict:  # reads username & password form fields
    return {"access_token": f"tok-{form.username}", "token_type": "bearer"}  # fake token


c: TestClient = TestClient(app)  # client
print(c.post("/token", data={"username": "asha", "password": "x"}).json())  # form
# Output: {'access_token': 'tok-asha', 'token_type': 'bearer'}
print(c.post("/token", json={"username": "asha", "password": "x"}).status_code)  # JSON is rejected
# Output: 422
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `python-multipart`
```python
# Wrong - Form/File params without the package -> RuntimeError at startup:
# 'Form data requires "python-multipart" to be installed.'

# Correct
# pip install python-multipart
```

❌ Mistake 2: Reading a huge file fully into memory
```python
# Wrong - bytes type loads the entire file; 2 GB upload = 2 GB RAM
async def up(file: bytes = File()): ...

# Correct - UploadFile + chunked read/write
async def up(file: UploadFile):
    while chunk := await file.read(1024 * 1024): ...
```

❌ Mistake 3: Trusting `filename` and `content_type`
```python
# Wrong - "../../etc/passwd" or a fake image/png
open(f"uploads/{file.filename}", "wb")

# Correct - sanitize the name, generate your own, check magic bytes (e.g. PIL / filetype) for real validation
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from fastapi import FastAPI, Form
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str

@app.post("/a")
def a(name: str = Form()):
    return {"name": name}

@app.post("/b")
def b(item: Item):
    return item

c = TestClient(app)
print(c.post("/a", data={"name": "x"}).status_code)
print(c.post("/a", json={"name": "x"}).status_code)
print(c.post("/b", data={"name": "x"}).status_code)
```

**Answer**:
```
200
422
422
```
Each endpoint accepts only its own encoding. `/a` expects form fields, so JSON fails (422). `/b` expects a JSON body, so form data fails (422). That is why you cannot mix `Form` and a JSON `Body` in one route.

---

## ⚫ Interview Questions + Answers

Q1: `bytes` vs `UploadFile` for file parameters?
A1: `bytes` reads the whole file into memory (fine for tiny files). `UploadFile` uses a spooled temp file (memory first, then disk), exposes `filename`, `content_type`, and async `read/write/seek/close`, and is the right choice for most uploads.

Q2: Why does FastAPI need `python-multipart`?
A2: FastAPI/Starlette do not bundle a multipart parser. Without the package, any `Form`/`File` usage raises an error at startup.

Q3: How do you limit upload size?
A3: Check `Content-Length` early (a proxy like nginx `client_max_body_size` is best), and count bytes while streaming chunks in your code; raise 413 when over the limit. Newer Starlette also lets you set multipart limits.

Q4: Can I send JSON and a file in one request?
A4: Not as a JSON body. Send the JSON as a string field in the form and parse it with `Json`/`json.loads` or a validator, or upload the file separately.

Q5: How do you accept many files?
A5: Declare `files: list[UploadFile]` and send multiple parts with the same field name.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Users upload images, PDFs, CSVs or audio
- Handling HTML forms or the OAuth2 password login
- Mixing text fields with a file in one request

❌ Avoid when:
- Very large files (use presigned S3/GCS upload URLs so the file skips your server)
- Normal structured data (use JSON bodies)
- You need JSON + file in one typed model (use two endpoints)

---

## 📊 Visual Diagram

```
POST /upload   Content-Type: multipart/form-data; boundary=XYZ

--XYZ
Content-Disposition: form-data; name="note"
v1
--XYZ
Content-Disposition: form-data; name="file"; filename="menu.txt"
Content-Type: text/plain
biryani 250
--XYZ--
        │ python-multipart parses
        ▼
 note: Form(str)      file: UploadFile(filename, content_type, read())
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| multipart/form-data | Encoding that can carry files | files ले जा सकने वाली encoding |
| Form() | Read a form field | form field पढ़ना |
| UploadFile | Streamed uploaded file object | stream होने वाली upload file |
| MIME type | File type label | file के प्रकार का label |
| Boundary | Separator between parts | हिस्सों को अलग करने वाली रेखा |
| 413 | Payload too large | data बहुत बड़ा |
| 415 | Unsupported media type | file type समर्थित नहीं |

---

## ⚡ 3-Line Summary
English: Use `Form()` for HTML form fields and `UploadFile` for files; both need `python-multipart`. Stream big files in chunks and validate type, size and filename. A route cannot mix form fields with a JSON body.
Hindi: HTML form fields के लिए `Form()` और files के लिए `UploadFile` इस्तेमाल करें; दोनों को `python-multipart` चाहिए। बड़ी files chunk में पढ़ें और type, size, filename जाँचें। एक route में form fields और JSON body साथ नहीं चल सकते।

---

## ➡️ Next Topic
**310. Headers + Cookies** — reading and setting HTTP headers and cookies (tokens, session, correlation ids).
