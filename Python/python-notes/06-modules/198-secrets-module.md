---

# 198. secrets Module
# हिंदी में: secrets Module (सुरक्षित random tokens और passwords)

---

## 🔵 Simple Definition (English)
`secrets` is a standard-library module (since Python 3.6) that generates cryptographically strong random values: tokens, passwords, API keys and reset links. It uses the operating system's secure random source, so the values cannot be guessed.

## 🔵 सरल परिभाषा (Hindi)
`secrets` Python का standard-library module है (Python 3.6 से) जो cryptographically मज़बूत random values बनाता है: tokens, passwords, API keys और reset links। यह OS के secure random source का इस्तेमाल करता है, इसलिए values का अंदाज़ा नहीं लगाया जा सकता।

---

## 🔴 Problem it Solves
Developers used the `random` module for OTPs and tokens. `random` uses the Mersenne Twister, which is predictable: if an attacker sees enough outputs, they can calculate the next ones. A guessable password-reset token means account takeover. `secrets` fixes this with unpredictable values and a safe comparison function.

## 🔴 यह क्यों बना? (Hindi)
Developers OTP और tokens के लिए `random` module इस्तेमाल करते थे। `random` Mersenne Twister पर चलता है जो predictable है: attacker को कुछ outputs दिख जाएँ तो अगली values निकाल सकता है। अनुमान लगाने लायक reset token का मतलब account hack। `secrets` unpredictable values और safe comparison function देकर यह problem हल करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You call secrets.token_urlsafe(32)
Step 2 → Python asks the OS for random bytes (os.urandom -> /dev/urandom, getrandom)
Step 3 → The OS mixes hardware noise (timings, CPU, interrupts) into a CSPRNG
Step 4 → Bytes come back and are encoded (hex / base64-url / raw bytes)
Step 5 → You store a HASH of the token, never the token itself
Step 6 → Later compare with secrets.compare_digest() (constant time)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप secrets.token_urlsafe(32) call करते हैं
Step 2 → Python OS से random bytes माँगता है (os.urandom)
Step 3 → OS hardware noise से बने CSPRNG से bytes देता है
Step 4 → Bytes hex / base64-url / raw bytes में encode होकर मिलते हैं
Step 5 → Token की जगह उसका HASH database में रखें
Step 6 → तुलना के लिए secrets.compare_digest() (constant time) इस्तेमाल करें
```

---

## 🟡 Real World Example
Razorpay-style payment dashboards create API keys like `rzp_live_...` with `token_urlsafe`. Zomato/Swiggy login flows send a password-reset link containing a one-time token. An AI app (OpenAI-style) issues per-user API keys, stores only the SHA-256 hash, and checks incoming keys with `compare_digest`. OTPs of 6 digits are made with `secrets.randbelow(10**6)`.

## 🟡 Real Example Hindi mein
Razorpay जैसे payment dashboards `token_urlsafe` से `rzp_live_...` जैसी API keys बनाते हैं। Zomato/Swiggy के password-reset link में एक बार चलने वाला token होता है। AI app हर user को API key देती है, सिर्फ SHA-256 hash store करती है और आने वाली key को `compare_digest` से check करती है। 6 digit का OTP `secrets.randbelow(10**6)` से बनता है।

---

## 💻 Code Example — Basic
```python
# Basic secrets examples - every line commented
import secrets  # secure random generator (standard library)
import string  # ready-made character sets

token: str = secrets.token_hex(16)  # 16 random bytes -> 32 hex characters
print(len(token))  # hex doubles the byte count
# Output: 32  (the token itself is different every run)

url_token: str = secrets.token_urlsafe(16)  # 16 bytes -> base64 text safe for URLs
print(len(url_token))  # about 1.3 characters per byte
# Output: 22  (letters, digits, - and _ only)

raw: bytes = secrets.token_bytes(8)  # raw bytes, not text
print(type(raw).__name__, len(raw))  # check type and size
# Output: bytes 8

print(len(secrets.token_hex()))  # no argument -> default size (32 bytes since 3.9)
# Output: 64

otp: str = f"{secrets.randbelow(10**6):06d}"  # number 0..999999, padded to 6 digits
print(len(otp), otp.isdigit())  # always 6 digits, e.g. "048213"
# Output: 6 True

print(secrets.choice("abc") in "abc")  # pick one random item securely
# Output: True

print(secrets.randbits(8) < 256)  # random integer with 8 random bits
# Output: True

# Safe comparison - time does not leak how many characters matched
print(secrets.compare_digest("abc", "abc"), secrets.compare_digest("abc", "abd"))
# Output: True False

# alphabet for a password
alphabet: str = string.ascii_letters + string.digits  # a-zA-Z0-9
password: str = "".join(secrets.choice(alphabet) for _ in range(12))  # 12 secure picks
print(len(password))  # check the length only (value is random)
# Output: 12
```

## 💻 Code Example — Advanced
```python
# Production style: password policy, hashed API keys, safe verification
import hashlib  # to hash API keys before storing them
import secrets  # secure randomness
import string  # character sets
from dataclasses import dataclass  # simple record type
from typing import Dict, Optional  # type hints

SYMBOLS: str = "!@#$%"  # allowed special characters


def generate_password(length: int = 12) -> str:
    """Create a password that always contains lower, upper, digit and symbol."""
    if length < 8:  # weak passwords are rejected early
        raise ValueError("length must be at least 8")  # clear message
    alphabet: str = string.ascii_letters + string.digits + SYMBOLS  # allowed chars
    while True:  # retry until the policy is satisfied
        pw: str = "".join(secrets.choice(alphabet) for _ in range(length))  # candidate
        if (
            any(c.islower() for c in pw)  # needs a lowercase letter
            and any(c.isupper() for c in pw)  # needs an uppercase letter
            and any(c.isdigit() for c in pw)  # needs a digit
            and any(c in SYMBOLS for c in pw)  # needs a symbol
        ):
            return pw  # policy satisfied


@dataclass(frozen=True)  # immutable record
class ApiKey:
    plain: str  # shown to the user ONE time only
    hashed: str  # this is what we store in the database


def create_api_key(prefix: str = "sk") -> ApiKey:
    """Return a new key. Only the hash must be saved."""
    plain: str = f"{prefix}_{secrets.token_urlsafe(32)}"  # 256 bits of randomness
    hashed: str = hashlib.sha256(plain.encode()).hexdigest()  # one-way hash
    return ApiKey(plain=plain, hashed=hashed)  # give both back


def verify_api_key(candidate: str, stored_hash: str) -> bool:
    """Compare in constant time to stop timing attacks."""
    candidate_hash: str = hashlib.sha256(candidate.encode()).hexdigest()  # hash input
    return secrets.compare_digest(candidate_hash, stored_hash)  # safe compare


db: Dict[str, str] = {}  # pretend database: user -> key hash
key: ApiKey = create_api_key()  # make a key
db["aditya"] = key.hashed  # store the hash only
print(key.plain.startswith("sk_"), len(key.hashed))  # shape check
# Output: True 64
print(verify_api_key(key.plain, db["aditya"]))  # correct key
# Output: True
print(verify_api_key("sk_wrong", db["aditya"]))  # wrong key
# Output: False

# compare_digest edge cases
try:  # str arguments must be ASCII only
    secrets.compare_digest("é", "é")  # non-ASCII str
except TypeError as exc:  # raises TypeError
    print("TypeError:", exc)  # see the message
# Output: TypeError: comparing strings with non-ASCII characters is not supported
print(secrets.compare_digest("é".encode(), "é".encode()))  # bytes work for any text
# Output: True

# randbelow validates input
try:  # upper bound must be positive
    secrets.randbelow(0)  # invalid
except ValueError as exc:  # ValueError
    print("ValueError:", exc)  # message
# Output: ValueError: Upper bound must be positive.

policy_pw: Optional[str] = generate_password(14)  # policy-checked password
print(len(policy_pw))  # length is guaranteed
# Output: 14
```
All random values (tokens, passwords, keys) differ on every run; only lengths and booleans above are stable. Verified on Python 3.13.3.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python way
import secrets
token = secrets.token_hex(16)        # 32 hex chars
otp = secrets.randbelow(10**6)       # secure integer 0..999999
```
```javascript
// JavaScript way (Node.js)
const crypto = require("crypto");
const token = crypto.randomBytes(16).toString("hex");   // 32 hex chars
const otp = crypto.randomInt(0, 1_000_000);             // secure integer
// Browser: crypto.getRandomValues(new Uint8Array(16))
// WRONG for secrets: Math.random()  (like Python's random module)
```

Key differences: `Math.random()` in JS and `random` in Python are both NOT secure. Node's `crypto` and Python's `secrets` are the secure options. `secrets.compare_digest` equals Node's `crypto.timingSafeEqual`.

---

## 🟠 FastAPI Connection
FastAPI itself ships no token generator, so API-key creation, session ids and reset tokens use `secrets`. Always store only the hash and verify with `compare_digest`. The code below was run with `fastapi.testclient`.

```python
# FastAPI: issue and verify an API key (pip install fastapi httpx)
import hashlib  # hashing
import secrets  # secure tokens
from typing import Dict  # type hints
from fastapi import FastAPI, Header, HTTPException  # framework pieces

app: FastAPI = FastAPI()  # create app
DB: Dict[str, str] = {}  # user -> key hash (pretend DB)


@app.post("/keys")  # create a key
def create(user: str) -> Dict[str, str]:
    key: str = "sk_" + secrets.token_urlsafe(24)  # new random key
    DB[user] = hashlib.sha256(key.encode()).hexdigest()  # store hash only
    return {"api_key": key}  # shown once


@app.get("/me")  # protected route
def me(user: str, x_api_key: str = Header()) -> Dict[str, str]:
    stored: str = DB.get(user, "")  # saved hash (empty if unknown)
    given: str = hashlib.sha256(x_api_key.encode()).hexdigest()  # hash header value
    if not secrets.compare_digest(stored, given):  # constant-time compare
        raise HTTPException(status_code=401, detail="bad key")  # reject
    return {"user": user}  # success
# Test result: valid key -> {'user': 'aditya'}, wrong key -> 401
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `random` for security values
✅ Correct:

```python
import random, secrets
# Wrong - predictable generator:
token = "".join(random.choice("0123456789abcdef") for _ in range(32))
# Right - cryptographically secure:
token = secrets.token_hex(16)
```

❌ Mistake 2: Comparing tokens with `==`
✅ Correct:

```python
import secrets
# Wrong - returns early at the first different character (timing leak):
ok = user_token == saved_token
# Right - constant time:
ok = secrets.compare_digest(user_token, saved_token)
```

❌ Mistake 3: Tokens too short, or storing them in plain text
✅ Correct:

```python
import secrets, hashlib
# Wrong - only 4 bytes (32 bits) is brute-forceable, and stored raw
t = secrets.token_hex(2)
# Right - 32 bytes (256 bits) and keep only the hash
t = secrets.token_urlsafe(32)
saved = hashlib.sha256(t.encode()).hexdigest()
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import random, secrets

random.seed(1); a = random.random()
random.seed(1); b = random.random()
print(a == b)

rng = secrets.SystemRandom()
rng.seed(1)                      # does this make it repeatable?
print(rng.random() == secrets.SystemRandom().random())
print(len(secrets.token_hex(16)), len(secrets.token_urlsafe(16)))
print(secrets.compare_digest("é", "é"))
```

**Answer**:
```
True
False
32 22
TypeError: comparing strings with non-ASCII characters is not supported
```
`random` is deterministic after `seed`, so `a == b`. `SystemRandom.seed()` is silently ignored because values come from the OS, so two draws are (almost surely) different. Hex doubles the byte count (32), base64 gives about 4/3 (22). The last line raises `TypeError`; use `.encode()` bytes for non-ASCII. (Third value verified: 32 and 22 on Python 3.13.)

---

## ⚫ Interview Questions + Answers

Q1: Why not use `random` for tokens?
A1: `random` is a Mersenne Twister. Its state can be recovered from about 624 outputs, so future values are predictable. `secrets` uses the OS CSPRNG.

Q2: What is `compare_digest` for?
A2: It compares two strings/bytes in time that does not depend on where they differ. A normal `==` stops at the first mismatch, letting an attacker guess a token one character at a time by measuring time.

Q3: How many bytes should a token have?
A3: `secrets` doc says about 32 bytes (256 bits) is a good default today. Since Python 3.9 the default for `token_*` is 32 bytes.

Q4: `token_hex` vs `token_urlsafe` vs `token_bytes`?
A4: `token_bytes` returns raw bytes, `token_hex` returns hex text (2 chars per byte), `token_urlsafe` returns base64-url text (safe in URLs and headers, no `+` or `/`).

Q5: Is `secrets` enough to store passwords?
A5: No. `secrets` generates values. To store user passwords you must hash them with a slow algorithm (bcrypt, argon2, `hashlib.scrypt`/`pbkdf2_hmac`).

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Creating API keys, session ids, CSRF tokens, reset links
- Generating OTPs or temporary passwords
- Picking random values an attacker must not guess

❌ Avoid when:
- You need repeatable randomness (tests, simulations): use `random.seed`
- You need speed for millions of non-secret values: `random` is faster
- You need to hash passwords: use bcrypt/argon2

---

## 📊 Visual Diagram

```
random module                    secrets module
-------------                    --------------
seed (time) -> Mersenne Twister  OS entropy (hardware noise)
   -> predictable stream            -> kernel CSPRNG (/dev/urandom)
   -> NOT for security              -> secrets.token_*()
                                       -> store HASH in DB
                                       -> verify with compare_digest
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CSPRNG | Cryptographically secure random generator | सुरक्षित random generator |
| Entropy | Real unpredictability from hardware/OS | असली अनिश्चितता |
| Token | Random string used as a secret | secret के रूप में random string |
| Timing attack | Guessing secrets by measuring response time | समय नापकर secret का अंदाज़ा |
| Hash | One-way fingerprint of data | data का one-way fingerprint |
| OTP | One-time password | एक बार चलने वाला password |

---

## ⚡ 3-Line Summary
English: `secrets` gives unpredictable random values from the OS, unlike `random`. Use `token_urlsafe`, `token_hex`, `randbelow`, `choice` for tokens and passwords, and `compare_digest` for safe comparison. Store only hashes of keys.
Hindi: `secrets` OS से unpredictable random values देता है, `random` की तरह नहीं। Tokens और passwords के लिए `token_urlsafe`, `token_hex`, `randbelow`, `choice` और तुलना के लिए `compare_digest` इस्तेमाल करें। Keys का सिर्फ hash रखें।

---

## ➡️ Next Topic
**199. logging Module** is already covered; continue with **200. argparse Module** — build command-line tools with arguments and flags.
