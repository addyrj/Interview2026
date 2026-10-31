---

# 075. bytes + bytearray
# हिंदी में: bytes और bytearray (Binary Data)

---

## 🔵 Simple Definition (English)
`bytes` is an immutable sequence of numbers from 0 to 255 (raw binary data). `bytearray` is the same but mutable — you can change it in place. A `str` is text; `bytes` is what actually travels over the network and gets saved in files.

## 🔵 सरल परिभाषा (Hindi)
`bytes` 0 से 255 तक की numbers की immutable sequence है (raw binary data)। `bytearray` वही है लेकिन mutable — उसे जगह पर ही बदल सकते हैं। `str` text है; `bytes` वो है जो असल में network पर जाता है और file में save होता है।

---

## 🔴 Problem it Solves
Computers store everything as bytes — images, PDFs, network packets, encrypted data, hashes. Text (`str`) cannot represent arbitrary binary data safely. Python 2 mixed text and bytes in one type, which caused endless Unicode bugs. Python 3 separates them: `str` for text, `bytes` for binary, and you convert explicitly with `encode()` / `decode()`.

## 🔴 यह क्यों बना? (Hindi)
Computer सब कुछ bytes में रखता है — images, PDF, network packets, encrypted data, hashes। `str` हर binary data को safely नहीं रख सकती। Python 2 में text और bytes एक ही type थे, जिससे Unicode के बहुत bugs आते थे। Python 3 में दोनों अलग हैं: text के लिए `str`, binary के लिए `bytes`, और बदलने के लिए `encode()` / `decode()`।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You have text: "नमस्ते" (6 Unicode characters)
Step 2 → .encode("utf-8") converts text -> bytes (18 bytes, Hindi takes 3 each)
Step 3 → bytes travel over network / get stored in a file
Step 4 → Receiver calls .decode("utf-8") to get the text back
Step 5 → Use bytes when data is read-only (hash, token, file chunk)
Step 6 → Use bytearray when you must modify or fill a buffer in place

str  --encode-->  bytes  --decode-->  str
                  bytes  --bytearray()--> bytearray (mutable copy)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आपके पास text है: "नमस्ते" (6 Unicode characters)
Step 2 → .encode("utf-8") text को bytes बनाता है (18 bytes, हर हिंदी अक्षर 3 bytes)
Step 3 → bytes network पर जाते हैं / file में save होते हैं
Step 4 → पाने वाला .decode("utf-8") से वापस text बनाता है
Step 5 → Read-only data (hash, token, file chunk) के लिए bytes
Step 6 → जगह पर बदलना हो या buffer भरना हो तो bytearray
```

---

## 🟡 Real World Example
Razorpay sends a webhook; your server must compute an HMAC-SHA256 signature over the raw request body (bytes) and compare it. Uploading a profile photo in FastAPI gives you `bytes`. Downloading a large file in chunks uses `bytes`; a socket receive buffer uses `bytearray`. Base64 encoding of images for an AI vision API works on bytes.

## 🟡 Real Example Hindi mein
Razorpay webhook भेजता है; आपके server को request body (bytes) पर HMAC-SHA256 signature निकालकर compare करना होता है। FastAPI में profile photo upload करने पर `bytes` मिलते हैं। बड़ी file chunks में download करते समय `bytes`, और socket का receive buffer `bytearray` होता है। AI vision API के लिए image का Base64 भी bytes पर चलता है।

---

## 💻 Code Example — Basic
```python
# Basic bytes and bytearray examples
b: bytes = b"Hello"                       # b prefix makes a bytes literal
print(b, b[0], type(b[0]))                # indexing gives an int (72), not a char
print(b[0:2])                             # slicing bytes gives bytes

s: str = "नमस्ते"                          # Hindi text, 6 characters
enc: bytes = s.encode("utf-8")            # text -> bytes
print(len(s), len(enc))                   # 6 characters but 18 bytes
print(enc.decode("utf-8") == s)           # bytes -> text round trip -> True

ba: bytearray = bytearray(b"Hello")       # mutable copy of the bytes
ba[0] = ord("J")                          # change first byte using its int value
ba.append(33)                             # add byte 33 which is "!"
print(ba, bytes(ba))                      # bytearray and frozen bytes version

try:                                      # bytes are immutable
    b[0] = 74  # type: ignore             # item assignment is not allowed
except TypeError as e:                    # catch the error
    print("TypeError:", e)                # shows the reason

print(bytes([72, 105]), bytes(3), list(b"Hi"))   # from ints, zero filled, to list
print(b"abc".hex(), bytes.fromhex("616263"))     # hex string conversion
print(str(b"hi"))                         # str() of bytes gives repr text, no decode!
print(b"hi" == "hi")                      # bytes never equal str -> False

# Output:
# b'Hello' 72 <class 'int'>
# b'He'
# 6 18
# True
# bytearray(b'Jello!') b'Jello!'
# TypeError: 'bytes' object does not support item assignment
# b'Hi' b'\x00\x00\x00' [72, 105]
# 616263 b'abc'
# b'hi'
# False
```

## 💻 Code Example — Advanced
```python
# Production style: hashing, webhook signature, chunked read, buffers
import hashlib                            # hash functions
import hmac                               # keyed hash for signatures
import base64                             # base64 text encoding
import tempfile                           # temporary folder for the demo
from pathlib import Path                  # file paths


def sha256_hex(data: bytes) -> str:
    """Return SHA-256 hash of bytes as hex text."""
    return hashlib.sha256(data).hexdigest()           # hashing needs bytes


def sign(secret: bytes, message: bytes) -> str:
    """Create HMAC signature (like a webhook signature)."""
    return hmac.new(secret, message, hashlib.sha256).hexdigest()   # keyed hash


def verify(secret: bytes, message: bytes, signature: str) -> bool:
    """Compare signatures in constant time (prevents timing attacks)."""
    return hmac.compare_digest(sign(secret, message), signature)   # safe compare


def read_chunks(path: Path, size: int = 4) -> list[bytes]:
    """Read a binary file in small chunks."""
    chunks: list[bytes] = []                          # collected chunks
    with path.open("rb") as f:                        # "rb" = read binary
        while chunk := f.read(size):                  # empty bytes ends the loop
            chunks.append(chunk)                      # store the chunk
    return chunks                                     # list of bytes


def fill_buffer(buf: bytearray, data: bytes) -> int:
    """Copy as much data as fits into a pre-allocated buffer."""
    n: int = min(len(buf), len(data))                 # how much fits
    buf[:n] = data[:n]                                # slice assignment, in place
    return n                                          # bytes copied


print(sha256_hex(b"hello")[:16])                      # 2cf24dba5fb0a30e
sig: str = sign(b"key", b'{"amount": 100}')           # sign a JSON body
print(sig[:16])                                       # d92ef9e2388551ba
print(verify(b"key", b'{"amount": 100}', sig))        # True
print(verify(b"key", b'{"amount": 999}', sig))        # False (body changed)
enc: bytes = base64.b64encode(b"user:pass")           # bytes -> base64 bytes
print(enc, base64.b64decode(enc))                     # and back again
with tempfile.TemporaryDirectory() as d:              # auto cleaned folder
    p: Path = Path(d) / "x.bin"                       # file path
    p.write_bytes(b"0123456789")                      # write 10 bytes
    print(read_chunks(p))                             # read in chunks of 4
buf: bytearray = bytearray(6)                         # 6 zero bytes buffer
print(fill_buffer(buf, b"abcdefgh"), buf)             # only 6 fit
mv: memoryview = memoryview(buf)                      # zero-copy view of buffer
mv[0:2] = b"ZZ"                                       # write through the view
print(buf)                                            # buffer changed in place

# Output:
# 2cf24dba5fb0a30e
# d92ef9e2388551ba
# True
# False
# b'dXNlcjpwYXNz' b'user:pass'
# [b'0123', b'4567', b'89']
# 6 bytearray(b'abcdef')
# bytearray(b'ZZcdef')
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Immutable binary | `bytes` | `Uint8Array` (mutable!) / `Buffer` in Node |
| Mutable binary | `bytearray` | `Uint8Array` |
| Text to bytes | `s.encode("utf-8")` | `new TextEncoder().encode(s)` |
| Bytes to text | `b.decode("utf-8")` | `new TextDecoder().decode(b)` |
| Indexing | gives int | gives number |

```python
# Python way
data: bytes = "Hi".encode("utf-8")      # text -> bytes
print(list(data))                       # [72, 105]
print(data.decode("utf-8"))             # Hi
```
```javascript
// JavaScript way
const data = new TextEncoder().encode("Hi");     // text -> Uint8Array
console.log(Array.from(data));                   // [72, 105]
console.log(new TextDecoder().decode(data));     // Hi
```

Key difference: JS has no immutable bytes type — `Uint8Array` is always mutable. In Python, `bytes` is immutable and hashable (can be a dict key), `bytearray` is mutable and not hashable. Python never converts between `str` and `bytes` automatically.

---

## 🟠 FastAPI Connection
FastAPI uses bytes for file uploads (`UploadFile.read()` returns bytes), for raw request bodies (`await request.body()`), and for binary responses (`Response(content=bytes, media_type="image/png")`). Webhook signature verification needs the exact raw bytes.

```python
# FastAPI example — verify a webhook signature on raw bytes
import hashlib                                    # hash algorithm
import hmac                                       # HMAC signature
from fastapi import FastAPI, Header, HTTPException, Request   # FastAPI parts

app: FastAPI = FastAPI()                          # create app
SECRET: bytes = b"my-webhook-secret"              # shared secret as bytes


@app.post("/webhook")                             # POST /webhook
async def webhook(request: Request, x_signature: str = Header(...)) -> dict[str, str]:
    body: bytes = await request.body()            # raw bytes, NOT parsed JSON
    expected: str = hmac.new(SECRET, body, hashlib.sha256).hexdigest()   # our signature
    if not hmac.compare_digest(expected, x_signature):   # constant time compare
        raise HTTPException(status_code=401, detail="Bad signature")     # reject
    return {"status": "ok"}                       # accepted
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mixing `str` and `bytes`
✅ Correct: encode or decode explicitly

```python
# Wrong
# "abc" + b"def"           # TypeError: can only concatenate str (not "bytes") to str
# Right
print("abc".encode() + b"def")   # b'abcdef'
```

❌ Mistake 2: Using `str(b)` to decode
✅ Correct: use `.decode()`

```python
# Wrong — gives the text "b'hi'" (with the b and quotes), not "hi"
print(str(b"hi"))          # b'hi'
# Right
print(b"hi".decode())      # hi
```

❌ Mistake 3: Building big data with `bytes +=` in a loop
✅ Correct: use `bytearray` (or `b"".join(parts)`)

```python
# Wrong — bytes are immutable, every += copies everything (slow, O(n^2))
data = b""
for _ in range(3):
    data += b"x"
# Right
buf = bytearray()
for _ in range(3):
    buf.extend(b"x")       # amortized O(1)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
b = b"abc"
print(b[0], b[0:1])
print(len("é"), len("é".encode("utf-8")))
print(bytes(3) == b"\x00\x00\x00", bytes([3]))
```
Answer: `97 b'a'` — indexing bytes gives an INT, slicing gives bytes (differs from str, where both give str). Second line: `1 2` — one character takes two bytes in UTF-8. Third: `True b'\x03'` — `bytes(3)` means "3 zero bytes", but `bytes([3])` means "one byte with value 3". Same-looking call, very different meaning.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `bytes` and `bytearray`?
A1: `bytes` is immutable and hashable, safe to use as a dict key or to share. `bytearray` is mutable (append, slice assignment, in-place edit) and not hashable. Use `bytes` for fixed data, `bytearray` for buffers you build up or modify.

Q2: What is the difference between `str` and `bytes`?
A2: `str` is a sequence of Unicode characters (text). `bytes` is a sequence of integers 0-255 (binary). They are never implicitly converted. Convert with `str.encode(encoding)` and `bytes.decode(encoding)`. Always specify `utf-8` explicitly.

Q3: What happens if you decode with the wrong encoding?
A3: You get `UnicodeDecodeError` or garbled text (mojibake). Handle it with `errors="replace"` / `errors="ignore"` only when losing data is acceptable. For binary files (images, PDFs) never decode at all.

Q4: Why does `hmac.compare_digest` exist? Why not `==`?
A4: `==` stops at the first different byte, so response time leaks how many bytes matched — an attacker can guess a signature byte by byte (timing attack). `compare_digest` always takes the same time.

Q5: What is `memoryview`?
A5: A zero-copy window over a bytes-like object. Slicing `bytes` copies data; slicing a `memoryview` does not. Useful for large buffers, socket I/O and parsing binary protocols. Writing is possible only if the source is mutable (like `bytearray`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Hashing, signing, encryption, base64
- Reading/writing binary files (images, PDFs, audio) with `"rb"` / `"wb"`
- Network sockets, file uploads, raw HTTP bodies
- `bytearray` for buffers that grow or change

❌ Avoid when:
- Working with human text — use `str`
- Repeated `bytes +=` concatenation — use `bytearray` or `join`
- You need fast numeric arrays — use `array` or NumPy

---

## 📊 Visual Diagram
```
"Hi नमस्ते"   (str, Unicode text)
      |
      | .encode("utf-8")
      v
b'Hi \xe0\xa4\xa8...'   (bytes, immutable)   ----> hash / network / file
      |                         |
      | bytearray(b)            | .decode("utf-8")
      v                         v
bytearray (mutable)          back to str
  ba[0] = 74
  ba.append(33)

index 0  1  2  3 ...
value 72 105 32 224 ...   (each is an int 0..255)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| bytes | Immutable binary sequence | न बदलने वाला binary data |
| bytearray | Mutable binary sequence | बदलने वाला binary data |
| Encoding | Text to bytes (UTF-8) | Text को bytes में बदलना |
| Decoding | Bytes to text | Bytes को text में बदलना |
| memoryview | Zero-copy view of a buffer | बिना copy किए buffer का view |
| HMAC | Keyed hash for signatures | Secret key वाला hash signature |

---

## ⚡ 3-Line Summary
English: `bytes` is immutable binary data and `bytearray` is its mutable twin; `str` is text and they never convert automatically. Use `encode()` and `decode()` with UTF-8 to move between them. Use bytes for hashing, files, uploads and webhooks.
Hindi: `bytes` immutable binary data है और `bytearray` उसका mutable रूप; `str` text है और ये अपने आप convert नहीं होते। इनके बीच जाने के लिए UTF-8 के साथ `encode()` और `decode()` इस्तेमाल करें। Hashing, files, uploads और webhooks में bytes काम आते हैं।

---

## ➡️ Next Topic
**076. Array Module** — a compact, typed array for numbers that uses far less memory than a list of ints.
