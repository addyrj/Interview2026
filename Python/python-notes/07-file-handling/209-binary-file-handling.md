---

# 209. Binary File Handling
# हिंदी में: Binary File Handling (bytes पढ़ना-लिखना)

---

## 🔵 Simple Definition (English)
Binary file handling means opening a file in `"rb"`, `"wb"` or `"ab"` mode and working with `bytes` instead of text. No decoding or newline translation happens. It is used for images, PDFs, audio, ZIP files, model weights, and any custom data format.

## 🔵 सरल परिभाषा (Hindi)
Binary file handling का मतलब file को `"rb"`, `"wb"` या `"ab"` mode में खोलकर text की जगह `bytes` के साथ काम करना है। इसमें कोई decoding या newline बदलाव नहीं होता। यह images, PDF, audio, ZIP, model weights और custom data formats के लिए है।

---

## 🔴 Problem it Solves
Not every file is text. If you open a PNG in text mode, Python tries to decode the bytes as UTF-8 and fails with `UnicodeDecodeError`, or on Windows silently changes `\r\n`. Binary mode gives you the exact bytes on disk, so copying, uploading, hashing and parsing file formats stay correct.

## 🔴 यह क्यों बना? (Hindi)
हर file text नहीं होती। PNG को text mode में खोलने पर Python bytes को UTF-8 की तरह decode करने की कोशिश करता है और `UnicodeDecodeError` आता है, या Windows पर `\r\n` चुपचाप बदल जाता है। Binary mode disk के असली bytes देता है, इसलिए copy, upload, hash और file-format parsing सही रहते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → open(path, "rb") or open(path, "wb")  (no encoding argument allowed)
Step 2 → f.read(n) returns bytes (b'...'); iterating bytes gives integers 0..255
Step 3 → f.write(b"...") needs bytes or bytearray; str -> TypeError
Step 4 → f.seek(offset, whence) / f.tell() jump anywhere (random access works)
Step 5 → struct.pack / struct.unpack convert numbers <-> bytes for custom formats
Step 6 → Process big files in chunks (e.g. 1 MB) so memory stays small
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → open(path, "rb") या open(path, "wb") (encoding argument नहीं चलता)
Step 2 → f.read(n) bytes लौटाता है; bytes पर loop करने पर 0..255 के integers मिलते हैं
Step 3 → f.write(b"...") में bytes या bytearray चाहिए; str देने पर TypeError
Step 4 → f.seek(offset) / f.tell() से कहीं भी कूद सकते हैं
Step 5 → struct.pack / struct.unpack numbers और bytes के बीच बदलते हैं
Step 6 → बड़ी files को chunks (जैसे 1 MB) में process करें ताकि memory कम रहे
```

---

## 🟡 Real World Example
A Swiggy app uploads restaurant photos: the backend reads the first bytes to check the real file type (PNG starts with `\x89PNG`) before saving. Razorpay computes the SHA-256 of a settlement file to detect tampering. An AI team saves embeddings as raw float32 bytes (`numpy.tofile`) and memory-maps them. A file-transfer service copies 10 GB videos in 1 MB chunks.

## 🟡 Real Example Hindi mein
Swiggy app में restaurant photos upload होती हैं: backend save करने से पहले पहले bytes देखकर असली file type जाँचता है (PNG `\x89PNG` से शुरू होता है)। Razorpay tampering पकड़ने के लिए settlement file का SHA-256 निकालता है। AI team embeddings को raw float32 bytes में save करके memory-map करती है। File-transfer service 10 GB के videos को 1 MB chunks में copy करती है।

---

## 💻 Code Example — Basic
```python
# Binary files - every line commented
import tempfile  # temp folder
from pathlib import Path  # paths

d: Path = Path(tempfile.mkdtemp())  # temporary directory
p: Path = d / "b.bin"  # binary file path

with open(p, "wb") as f:  # write bytes
    print(f.write(bytes([0, 1, 2, 255])))  # write() returns the byte count
# Output: 4

with open(p, "rb") as f:  # read bytes
    data: bytes = f.read()  # whole file as bytes
print(data, type(data).__name__)  # raw bytes, shown with \x escapes
# Output: b'\x00\x01\x02\xff' bytes
print(data[0], data[3], list(data), len(data))  # indexing gives integers
# Output: 0 255 [0, 1, 2, 255] 4

print(data.hex(), bytes.fromhex("000102ff"))  # hex text <-> bytes
# Output: 000102ff b'\x00\x01\x02\xff'

buf = bytearray(data)  # bytes is immutable, bytearray is mutable
buf[0] = 99  # change the first byte
print(buf)  # 99 is the letter 'c'
# Output: bytearray(b'c\x01\x02\xff')

try:  # bytes cannot be changed
    data[0] = 1  # not allowed
except TypeError as exc:  # TypeError
    print("TypeError:", exc)  # message
# Output: TypeError: 'bytes' object does not support item assignment

# text <-> bytes needs an encoding
print("हि".encode("utf-8"), len("हि"), len("हि".encode()))  # 2 characters, 6 bytes
# Output: b'\xe0\xa4\xb9\xe0\xa4\xbf' 2 6
try:  # wrong decoding
    b"\xff\xfe".decode("utf-8")  # not valid UTF-8
except UnicodeDecodeError as exc:  # error
    print("UnicodeDecodeError:", exc.reason)  # reason
# Output: UnicodeDecodeError: invalid start byte

# open in text mode a file that is not text -> same failure; "rb" never decodes
(d / "n.txt").write_bytes(b"a\r\nb\n")  # Windows-style newline in a file
print(repr(open(d / "n.txt").read()), open(d / "n.txt", "rb").read())  # text vs binary view
# Output: 'a\nb\n' b'a\r\nb\n'
```

## 💻 Code Example — Advanced
```python
# Production style: magic numbers, struct records, seek, chunked copy, hashing
import base64  # bytes <-> text for JSON/email
import hashlib  # hashes
import os  # SEEK_END
import struct  # fixed-size binary records
import tempfile  # temp folder
from pathlib import Path  # paths
from typing import Tuple  # type hints

d: Path = Path(tempfile.mkdtemp())  # temp folder

# 1) Check a real file type by its first bytes (magic number)
PNG_MAGIC: bytes = b"\x89PNG\r\n\x1a\n"  # first 8 bytes of every PNG
(d / "x.png").write_bytes(PNG_MAGIC + b"rest")  # fake png for the test
with open(d / "x.png", "rb") as f:  # open
    print(f.read(8) == PNG_MAGIC)  # trust bytes, not the file extension
# Output: True

# 2) struct: pack numbers into fixed-size records
rec: bytes = struct.pack("<IHf", 7, 3, 2.5)  # little-endian: uint32, uint16, float32
print(rec, len(rec), struct.unpack("<IHf", rec))  # round trip
# Output: b'\x07\x00\x00\x00\x03\x00\x00\x00 @' 10 (7, 3, 2.5)

RECORD: str = "<If"  # uint32 id + float32 value
SIZE: int = struct.calcsize(RECORD)  # 8 bytes per record
table: Path = d / "b.bin"  # data file
with open(table, "wb") as f:  # write 3 records
    for i in range(3):  # ids 0, 1, 2
        f.write(struct.pack(RECORD, i, i * 1.5))  # id and value

with open(table, "rb") as f:  # read records one by one
    while chunk := f.read(SIZE):  # empty bytes ends the loop
        print(struct.unpack(RECORD, chunk))  # tuple (id, value)
# Output: (0, 0.0)
# Output: (1, 1.5)
# Output: (2, 3.0)

# 3) Random access: jump straight to record number 2 (no scanning)
with open(table, "rb") as f:  # open
    f.seek(SIZE * 2)  # skip 2 records
    print(struct.unpack(RECORD, f.read(SIZE)), f.tell())  # record 2, position 24
    # Output: (2, 3.0) 24
    f.seek(-SIZE, os.SEEK_END)  # from the end
    print(f.tell())  # 24 - 8 = 16
    # Output: 16


# 4) Chunked copy: constant memory for any file size
def copy_file(src: Path, dst: Path, chunk: int = 1 << 20) -> int:
    """Copy using 1 MB chunks; returns bytes copied."""
    total: int = 0  # counter
    with open(src, "rb") as s, open(dst, "wb") as t:  # two files in one with
        while buf := s.read(chunk):  # read a chunk
            t.write(buf)  # write it
            total += len(buf)  # count
    return total  # result


print(copy_file(table, d / "copy.bin", 5), (d / "copy.bin").read_bytes() == table.read_bytes())
# Output: 24 True   (5-byte chunks only to prove the loop; use 1 MB in real code)


# 5) Hash a big file without loading it
def sha256_of(path: Path) -> str:
    h = hashlib.sha256()  # hash object
    with open(path, "rb") as f:  # binary
        for block in iter(lambda: f.read(8192), b""):  # until empty bytes
            h.update(block)  # feed the hash
    return h.hexdigest()  # hex string


print(sha256_of(table) == hashlib.sha256(table.read_bytes()).hexdigest())  # same as one-shot
# Output: True

# 6) bytes <-> text safe for JSON
print(base64.b64encode(b"\x00\xffhi"), base64.b64decode("AP9oaQ=="))  # base64 round trip
# Output: b'AP9oaQ==' b'\x00\xffhi'
```
Verified on Python 3.13.3. Hash/struct values above are deterministic; file locations vary.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python way
with open("photo.png", "rb") as f:
    data = f.read()                       # bytes
print(data[:4], len(data))
with open("copy.png", "wb") as f:
    f.write(data)
```
```javascript
// JavaScript way (Node.js)
import { readFileSync, writeFileSync } from "node:fs";
const data = readFileSync("photo.png");           // Buffer (no encoding => binary)
console.log(data.subarray(0, 4), data.length);
writeFileSync("copy.png", data);
// Browser: await file.arrayBuffer() -> new Uint8Array(buffer)
```

Key differences: Python decides binary vs text by the mode (`"rb"`); Node decides by whether you pass an encoding. Python's `bytes` is immutable (`bytearray` is the mutable one), JS uses `Buffer`/`Uint8Array`. Indexing a Python `bytes` gives an int, like a `Uint8Array`.

---

## 🟠 FastAPI Connection
File uploads (`UploadFile`), image responses (`Response(content=bytes, media_type="image/png")`) and downloads (`FileResponse`) are all binary. Validate uploads by magic bytes and size, not by the filename the user sends.

```python
# FastAPI: accept only real PNG uploads (pip install fastapi python-multipart)
import hashlib  # file fingerprint
from typing import Dict  # type hints
from fastapi import FastAPI, HTTPException, UploadFile  # framework

app: FastAPI = FastAPI()  # app
PNG_MAGIC: bytes = b"\x89PNG\r\n\x1a\n"  # PNG signature
MAX_BYTES: int = 1_000_000  # 1 MB limit


@app.post("/avatar")  # POST /avatar
def avatar(file: UploadFile) -> Dict[str, object]:
    head: bytes = file.file.read(8)  # first 8 bytes only
    if head != PNG_MAGIC:  # not a png
        raise HTTPException(status_code=415, detail="PNG only")  # Unsupported Media Type
    rest: bytes = file.file.read(MAX_BYTES + 1)  # read up to limit + 1
    if len(rest) > MAX_BYTES:  # too big
        raise HTTPException(status_code=413, detail="file too large")  # Payload Too Large
    digest: str = hashlib.sha256(head + rest).hexdigest()  # fingerprint
    return {"bytes": len(head) + len(rest), "sha256": digest[:12]}  # summary
# Tested with TestClient: valid PNG -> 200 with byte count, GIF bytes -> 415, over 1 MB -> 413.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Reading a binary file in text mode
✅ Correct:

```python
# Wrong - UnicodeDecodeError or corrupted data
open("photo.png").read()
# Right
open("photo.png", "rb").read()
```

❌ Mistake 2: Writing `str` to a binary file
✅ Correct:

```python
# Wrong - TypeError: a bytes-like object is required, not 'str'
open("a.bin", "wb").write("hello")
# Right
open("a.bin", "wb").write("hello".encode("utf-8"))
```

❌ Mistake 3: Loading a huge file at once
✅ Correct:

```python
# Wrong - 8 GB video eats all RAM
data = open("movie.mp4", "rb").read()
# Right - chunks
with open("movie.mp4", "rb") as f:
    while chunk := f.read(1 << 20):
        process(chunk)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
data = b"abc"
print(data[0])
print(data[0:1])
print(list(data))
print(bytes([97]) == b"a", "a" == b"a")
print(len("हि"), len("हि".encode("utf-8")))
```

**Answer**:
```
97
b'a'
[97, 98, 99]
True False
2 6
```
Indexing `bytes` gives an integer, slicing gives `bytes`. A `str` is never equal to `bytes` (and `python -b` even warns). The two-letter Hindi string has 2 characters but 6 UTF-8 bytes, so text length and byte length differ.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `bytes` and `bytearray`?
A1: `bytes` is immutable, hashable; `bytearray` is mutable. Both hold numbers 0 to 255.

Q2: Why no `encoding` argument in binary mode?
A2: Binary mode never converts to text, so encoding makes no sense. Passing it raises `ValueError: binary mode doesn't take an encoding argument`.

Q3: What is `struct` used for?
A3: Converting between Python numbers and fixed-layout bytes (network protocols, file headers). Use `<` for little-endian, `>` for big-endian and `calcsize` for the record size.

Q4: How do you read a file in chunks?
A4: `while chunk := f.read(size):` (walrus operator, Python 3.8+) or `iter(lambda: f.read(size), b"")`.

Q5: How do you detect the real type of an upload?
A5: Check magic bytes (PNG `\x89PNG`, PDF `%PDF`, ZIP `PK`) or use a library such as `python-magic`/`filetype`. File extensions and the client `Content-Type` can be faked.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Images, audio, video, PDFs, archives, model files
- Copying, hashing, uploading or downloading any file
- Custom or network binary formats with `struct`

❌ Avoid when:
- The file is plain text (use text mode with `encoding`)
- You can use a higher-level library: `Pillow` for images, `zipfile`, `numpy.load`
- Unpickling data from untrusted sources (`pickle` is binary but unsafe)

---

## 📊 Visual Diagram

```
Disk:  89 50 4E 47 0D 0A 1A 0A ...      (raw bytes)
          |
   open("rb")   ->  b'\x89PNG\r\n\x1a\n...'   (bytes, no decoding)
   open("r")    ->  tries UTF-8 -> 0x89 invalid start byte -> UnicodeDecodeError

seek(n) jumps to byte n:  |0|1|2|3|4|5|6|7|8| ...
                                 ^ f.seek(4)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| bytes | Immutable sequence of 0-255 | 0-255 की immutable sequence |
| bytearray | Mutable version of bytes | bytes का बदलने योग्य रूप |
| Magic number | First bytes that identify a format | format पहचानने वाले शुरुआती bytes |
| struct | Pack/unpack binary records | binary records बनाना/खोलना |
| Endianness | Byte order of numbers | numbers में bytes का क्रम |
| Chunk | Small piece read at a time | एक बार में पढ़ा जाने वाला टुकड़ा |

---

## ⚡ 3-Line Summary
English: Use `"rb"`/`"wb"` for non-text files; you get exact `bytes` with no decoding. Process big files in chunks, use `seek` for random access and `struct` for fixed records. Validate uploads by magic bytes, not extension.
Hindi: Non-text files के लिए `"rb"`/`"wb"` इस्तेमाल करें; बिना decoding के सही `bytes` मिलते हैं। बड़ी files chunks में process करें, random access के लिए `seek` और fixed records के लिए `struct` लें। Uploads की जाँच extension नहीं, magic bytes से करें।

---

## ➡️ Next Topic
**210. File Path Handling (pathlib)** — the modern object-oriented way to work with paths.
