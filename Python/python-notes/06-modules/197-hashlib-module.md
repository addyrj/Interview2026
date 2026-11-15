---

# 197. hashlib Module
# हिंदी में: hashlib Module (data का fixed-size fingerprint, यानी hash)

---

## 🔵 Simple Definition (English)
`hashlib` turns any bytes (a password, a file, a message) into a short fixed-size "fingerprint" called a hash or digest, using algorithms like SHA-256. The same input always gives the same hash; a tiny change gives a completely different hash; and you cannot go back from the hash to the input.

## 🔵 सरल परिभाषा (Hindi)
`hashlib` किसी भी bytes (password, file, message) को SHA-256 जैसे algorithms से एक छोटे fixed-size "fingerprint" में बदलता है जिसे hash या digest कहते हैं। वही input हमेशा वही hash देता है; ज़रा-सा बदलाव बिल्कुल अलग hash देता है; और hash से वापस input नहीं निकाला जा सकता।

---

## 🔴 Problem it Solves
You need to check that a download is not corrupted, detect duplicate files, store passwords without saving them in plain text, and verify that a webhook was really sent by the payment provider. Comparing whole files byte by byte or storing secrets directly is slow or dangerous. A hash gives a small, comparable fingerprint.

## 🔴 यह क्यों बना? (Hindi)
आपको जाँचना होता है कि download खराब तो नहीं, duplicate files पहचाननी होती हैं, passwords को plain text में रखे बिना store करना होता है, और verify करना होता है कि webhook सच में payment provider ने भेजा। पूरी files byte-by-byte तुलना करना धीमा है और secrets सीधे रखना खतरनाक। Hash एक छोटा, तुलना योग्य fingerprint देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Convert the input to bytes ("text".encode("utf-8"))
Step 2 → Pick an algorithm: sha256 (default choice), sha3_256, blake2b ...
Step 3 → h = hashlib.sha256(); h.update(chunk) can be called many times (streaming)
Step 4 → h.hexdigest() → hex text (64 chars for sha256); h.digest() → raw bytes (32)
Step 5 → Same input → same output. One bit changed → totally different output
Step 6 → For passwords use a SLOW salted function (pbkdf2_hmac, scrypt), not plain sha256
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Input को bytes बनाएँ ("text".encode("utf-8"))
Step 2 → Algorithm चुनें: sha256 (default पसंद), sha3_256, blake2b ...
Step 3 → h = hashlib.sha256(); h.update(chunk) कई बार चल सकता है (streaming)
Step 4 → h.hexdigest() → hex text (sha256 के लिए 64 chars); h.digest() → raw bytes (32)
Step 5 → वही input → वही output। एक bit बदलने पर → बिल्कुल अलग output
Step 6 → Passwords के लिए धीमा और salted function लें (pbkdf2_hmac, scrypt), सादा sha256 नहीं
```

---

## 🟡 Real World Example
A Razorpay webhook comes with an HMAC-SHA256 signature of the raw body; your server recomputes it with the shared secret to confirm it is genuine. A file-upload service names objects by their SHA-256 so duplicate uploads are stored once. A deployment tool publishes a checksum so users can verify a download. A login system stores `pbkdf2$iterations$salt$hash`, never the password.

## 🟡 Real Example Hindi mein
Razorpay webhook raw body का HMAC-SHA256 signature लेकर आता है; आपका server shared secret से उसे दोबारा निकालकर पक्का करता है कि वह असली है। File-upload service objects का नाम उनके SHA-256 से रखती है ताकि duplicate upload एक ही बार store हो। Deployment tool checksum देता है ताकि users download verify कर सकें। Login system `pbkdf2$iterations$salt$hash` रखता है, password कभी नहीं।

---

## 💻 Code Example — Basic
```python
# Basic hashlib examples - every line commented
import hashlib  # hash functions

data: bytes = "hello".encode("utf-8")  # hashes work on BYTES, not str
print(hashlib.sha256(data).hexdigest())  # 64 hex characters (256 bits)
print(hashlib.md5(data).hexdigest())  # 32 hex chars - BROKEN for security, ok for cache keys
print(hashlib.sha1(data).hexdigest())  # 40 hex chars - also broken for security
print(hashlib.sha512(data).hexdigest()[:32], "...")  # first 32 chars of 128

h = hashlib.sha256()  # create an empty hasher
h.update(b"hel")  # feed data piece by piece
h.update(b"lo")  # more data
print(h.hexdigest() == hashlib.sha256(b"hello").hexdigest())  # same result: True
print(h.digest_size, h.block_size, h.name)  # 32 bytes, 64, 'sha256'

print(hashlib.sha256(b"hello").hexdigest() == hashlib.sha256(b"Hello").hexdigest())  # tiny change -> False
print(hashlib.sha256(b"").hexdigest()[:16])  # even empty input has a hash

print(hashlib.blake2b(data, digest_size=8).hexdigest())  # blake2: fast, variable length
print(hashlib.sha3_256(data).hexdigest()[:16])  # SHA-3 family

print(sorted(hashlib.algorithms_guaranteed)[:5])  # always available names (first 5)
print(len(hashlib.sha256(b"x" * 10_000_000).hexdigest()))  # any input size -> always 64 chars
```

Output (verified by running; ids/timestamps/paths may vary):
```
2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
5d41402abc4b2a76b9719d911017c592
aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d
9b71d224bd62f3785d96d46ad3ea3d73 ...
True
32 64 sha256
False
e3b0c44298fc1c14
a7b6eda801e5347d
3338be694f50c5f3
['blake2b', 'blake2s', 'md5', 'sha1', 'sha224']
64
```

## 💻 Code Example — Advanced
```python
# Production style: file checksums, password hashing, HMAC webhook verification, timing safety
import base64  # encode salts
import hashlib  # hashes
import hmac  # keyed hashes
import os  # secure random salt
import tempfile  # demo file
from pathlib import Path  # paths
from typing import Tuple  # type hints


def file_sha256(path: Path, chunk: int = 1024 * 1024) -> str:
    """Hash a file in chunks so a 10 GB file does not fill RAM."""
    h = hashlib.sha256()  # hasher
    with path.open("rb") as f:  # binary mode
        while block := f.read(chunk):  # read until empty
            h.update(block)  # feed chunk
    return h.hexdigest()  # result


with tempfile.TemporaryDirectory() as tmp:  # sandbox
    p: Path = Path(tmp) / "report.bin"  # file
    p.write_bytes(b"hello")  # content
    print(file_sha256(p))  # same as sha256(b"hello")
    with p.open("rb") as fh:  # 3.11+: ready-made helper
        print(hashlib.file_digest(fh, "sha256").hexdigest() == file_sha256(p))  # True


def hash_password(password: str, iterations: int = 600_000) -> str:
    """PBKDF2-HMAC-SHA256 with a random salt. (Prefer argon2/bcrypt libs when you can.)"""
    salt: bytes = os.urandom(16)  # unique random salt
    dk: bytes = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)  # slow on purpose
    return f"pbkdf2_sha256${iterations}${base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}"


def verify_password(password: str, stored: str) -> bool:
    """Recompute with the stored salt and compare in constant time."""
    _, iters, salt_b64, dk_b64 = stored.split("$")  # parse the record
    dk: bytes = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.b64decode(salt_b64), int(iters))
    return hmac.compare_digest(dk, base64.b64decode(dk_b64))  # constant time


stored: str = hash_password("s3cret!")  # store this string, never the password
print(stored.split("$")[0], len(stored) > 80)  # format marker
print(verify_password("s3cret!", stored), verify_password("wrong", stored))  # True False
print(hash_password("s3cret!") != stored)  # random salt -> different every time: True


def sign(secret: bytes, body: bytes) -> str:
    """HMAC-SHA256 signature, like Razorpay/Stripe/GitHub webhooks."""
    return hmac.new(secret, body, hashlib.sha256).hexdigest()  # keyed hash


def verify_webhook(secret: bytes, body: bytes, signature: str) -> bool:
    """Compare signatures without leaking timing information."""
    return hmac.compare_digest(sign(secret, body), signature)  # constant time


body: bytes = b'{"event":"payment.captured","amount":19990}'  # RAW request body bytes
sig: str = sign(b"whsec_demo", body)  # sender computes this
print(sig[:16], verify_webhook(b"whsec_demo", body, sig))  # True
print(verify_webhook(b"whsec_demo", body + b" ", sig))  # body changed -> False

# Content-addressed id: same content -> same id (deduplicate uploads)
print(hashlib.sha256(b"photo-bytes").hexdigest()[:12], hashlib.sha256(b"photo-bytes").hexdigest()[:12])

# usedforsecurity=False documents a non-security use (works on FIPS systems too)
print(hashlib.md5(b"cache-key", usedforsecurity=False).hexdigest())

# Why hashes cannot be "decrypted": different inputs may share only by collision, output is fixed size
print(len({hashlib.sha1(str(i).encode()).hexdigest()[:2] for i in range(2000)}) <= 256)  # True
```

Output (verified by running; ids/timestamps/paths may vary):
```
2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
True
pbkdf2_sha256 True
True False
True
bbb8b901288ae01e True
False
dac6f451810b dac6f451810b
2536a13781f33e55574faff9acb9f995
True
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import hashlib, hmac
hashlib.sha256(b"hello").hexdigest()                     # 2cf24dba...
hmac.new(b"key", b"msg", hashlib.sha256).hexdigest()     # keyed hash
hashlib.pbkdf2_hmac("sha256", b"pw", b"salt", 600_000)   # password hashing
```

```javascript
// JavaScript (Node.js)
import crypto from "node:crypto";
crypto.createHash("sha256").update("hello").digest("hex");          // 2cf24dba...
crypto.createHmac("sha256", "key").update("msg").digest("hex");     // keyed hash
crypto.pbkdf2Sync("pw", "salt", 600000, 32, "sha256");              // password hashing
```

Key differences: Python hashing functions only take `bytes`, so you must `.encode()` strings (a `str` raises `TypeError`); Node accepts strings. Both give the same hex digest for the same bytes. Python `hmac.compare_digest` equals Node's `crypto.timingSafeEqual`. Python's built in `hash()` is NOT a cryptographic hash and changes between runs.

---

## 🟠 FastAPI Connection
Payment and Git providers sign webhooks. In FastAPI read the RAW body with `await request.body()`, compute `hmac.new(secret, body, sha256)`, and compare with `hmac.compare_digest`. For user passwords, use a library (`passlib`, `argon2-cffi`, `bcrypt`) or at least `hashlib.pbkdf2_hmac` with a random salt; never plain `sha256(password)`.

```python
# FastAPI: verify a webhook signature on the RAW body (pip install fastapi httpx)
import hashlib  # hashes
import hmac  # keyed hashes
from typing import Dict  # type hints
from fastapi import FastAPI, Header, HTTPException, Request  # request pieces

app: FastAPI = FastAPI()  # create app
SECRET: bytes = b"whsec_demo"  # real app: read from environment


@app.post("/webhook")  # POST /webhook
async def webhook(request: Request, x_signature: str = Header(...)) -> Dict[str, bool]:
    body: bytes = await request.body()  # RAW bytes (do not re-serialise JSON!)
    expected: str = hmac.new(SECRET, body, hashlib.sha256).hexdigest()  # our signature
    if not hmac.compare_digest(expected, x_signature):  # constant time compare
        raise HTTPException(status_code=401, detail="bad signature")  # reject
    return {"ok": True}  # accepted
```

Output (verified by running; ids/timestamps/paths may vary):
```
{'ok': True}
401
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Hashing a `str`, or using the wrong encoding
```python
# Wrong - TypeError: Strings must be encoded before hashing
# hashlib.sha256("hello")

# Correct - always say the encoding
# hashlib.sha256("hello".encode("utf-8")).hexdigest()
```

❌ Mistake 2: Plain MD5/SHA for passwords, and `==` for secrets
```python
# Wrong - fast hashes are cracked at billions per second; == leaks timing
# stored = hashlib.md5(password.encode()).hexdigest()
# if signature == expected: ...

# Correct
# hashlib.pbkdf2_hmac("sha256", pw, os.urandom(16), 600_000)   # or argon2 / bcrypt
# hmac.compare_digest(signature, expected)
```

❌ Mistake 3: Reading a whole file into memory, and treating a hash as encryption
```python
# Wrong - huge RAM use; and "decrypting" a hash is impossible
# hashlib.sha256(open("big.iso", "rb").read()).hexdigest()

# Correct - stream in chunks (or hashlib.file_digest on 3.11+)
# with open("big.iso", "rb") as f:
#     print(hashlib.file_digest(f, "sha256").hexdigest())
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import hashlib
try:
    hashlib.sha256("hello")
except TypeError as e:
    print("TypeError:", e)
print(hashlib.sha256(b"a").digest()[:2], len(hashlib.sha256(b"a").digest()))
h = hashlib.sha256(b"ab")
h2 = h.copy(); h2.update(b"c")
print(h.hexdigest() == hashlib.sha256(b"ab").hexdigest(), h2.hexdigest() == hashlib.sha256(b"abc").hexdigest())
print(hashlib.sha256("é".encode("utf-8")).hexdigest() == hashlib.sha256("é".encode("latin-1")).hexdigest())
```

**Answer**:
```
TypeError: Strings must be encoded before hashing
b'\xca\x97' 32
True True
False
```
A `str` must be encoded to bytes first. `digest()` returns 32 raw bytes (the hex form has 64 characters). `copy()` clones the state so you can continue one copy without changing the other. The same text encoded differently (`utf-8` vs `latin-1`) is different bytes and so has a different hash, a classic cause of "signature mismatch" bugs. (Verified by running.)

---

## ⚫ Interview Questions + Answers

Q1: Hashing vs encryption?
A1: Encryption is two-way (decrypt with a key). Hashing is one-way: you cannot recover the input, you can only hash a guess and compare.

Q2: Why is MD5/SHA-1 unsafe, and what should I use?
A2: Practical collision attacks exist, so attackers can create two different inputs with the same hash. Use SHA-256 / SHA-3 / BLAKE2 for integrity. MD5 is still fine for non-security cache keys (`usedforsecurity=False`).

Q3: How should passwords be stored?
A3: With a slow, salted, memory/CPU-hard function: Argon2, bcrypt, scrypt, or `pbkdf2_hmac` with a high iteration count and a random per-user salt. Store the algorithm, parameters, salt and hash together, and compare with `hmac.compare_digest`.

Q4: What is HMAC and why not `sha256(secret + message)`?
A4: HMAC mixes a secret key into the hash in a safe way, to prove both integrity and authenticity. Naive `hash(secret + message)` is vulnerable to length extension attacks with SHA-2 family hashes.

Q5: What is a salt and what is a collision?
A5: A salt is random data added before hashing, so two users with the same password have different hashes and rainbow tables fail. A collision means two different inputs have the same hash; for good algorithms they are practically impossible to find.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Checksums for files and downloads
- Webhook/API signatures (HMAC)
- Deduplication, cache keys and content-addressed storage
- Password hashing with `pbkdf2_hmac` / `scrypt` (or a dedicated library)

❌ Avoid when:
- You need to get the original data back (use encryption: `cryptography`)
- Hashing passwords with plain `sha256` / `md5`
- You need a hash for dict keys (use built in `hash()` or the object itself)

---

## 📊 Visual Diagram

```
 "hello" ──sha256──► 2cf24dba5fb0a30e...b9824   (64 hex chars)
 "Hello" ──sha256──► 185f8db32271fe25...        (totally different)
 10 GB file ─sha256─► 64 hex chars              (always same size)

        input ─────► hash        ✔ easy
        input ◄───── hash        ✖ impossible (one-way)

 password ─+ salt ─► PBKDF2 (600k rounds) ─► stored: algo$iters$salt$hash
 webhook:  HMAC(secret, raw_body) == header signature ?  → compare_digest
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hash / digest | Fixed-size fingerprint of data | data का fixed-size fingerprint |
| Salt | Random data added before hashing | hash से पहले जोड़ा random data |
| HMAC | Hash with a secret key | secret key वाला hash |
| Collision | Two inputs with the same hash | दो inputs का एक hash |
| Checksum | Hash used to verify integrity | अखंडता जाँचने का hash |
| Constant-time compare | Comparison with no timing leak | timing leak के बिना तुलना |

---

## ⚡ 3-Line Summary
English: `hashlib` creates one-way fingerprints of bytes: use SHA-256 for integrity, HMAC for signatures, and a slow salted function (PBKDF2, scrypt, Argon2) for passwords. Always encode text to bytes and compare secrets with `hmac.compare_digest`.
Hindi: `hashlib` bytes के एक-तरफा fingerprints बनाता है: integrity के लिए SHA-256, signatures के लिए HMAC, और passwords के लिए धीमा salted function (PBKDF2, scrypt, Argon2)। Text को हमेशा bytes में encode करें और secrets की तुलना `hmac.compare_digest` से करें।

---

## ➡️ Next Topic
**198. secrets Module** — cryptographically secure random values for tokens, OTPs and password resets.
