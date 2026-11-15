---

# 349. FastAPI Security Checklist
# हिंदी में: FastAPI Security Checklist (live जाने से पहले की सुरक्षा सूची)

---

## 🔵 Simple Definition (English)
A security checklist is a list of protections to confirm before your API goes live: strong password hashing, authentication on every private route, strict input validation, CORS limited to your frontend, HTTPS and security headers, rate limiting, secrets outside the code, and hidden docs and error details in production. FastAPI gives tools for most of these, but you must switch them on.

## 🔵 सरल परिभाषा (Hindi)
Security checklist उन सुरक्षाओं की सूची है जो API live जाने से पहले पक्की करनी होती हैं: मज़बूत password hashing, हर private route पर authentication, सख़्त input validation, सिर्फ़ आपके frontend के लिए CORS, HTTPS और security headers, rate limiting, code के बाहर secrets और production में docs व error details छिपाना। FastAPI ज़्यादातर के लिए tools देता है, पर इन्हें चालू आपको करना पड़ता है।

---

## 🔴 Problem it Solves
APIs are attacked within hours of going public: password leaks, brute-force logins, SQL injection, mass assignment (client sets `is_admin`), cross-origin abuse and bot floods. Most breaches come from missing basics, not clever hacks. A checklist makes the basics routine.

## 🔴 यह क्यों बना? (Hindi)
API public होने के कुछ घंटों में ही उस पर हमले शुरू हो जाते हैं: password leak, brute-force login, SQL injection, mass assignment (client खुद `is_admin` सेट कर दे), cross-origin दुरुपयोग और bot floods। ज़्यादातर breaches चालाक hacks से नहीं, बुनियादी चीज़ें छूटने से होते हैं। Checklist उन बुनियादी चीज़ों को आदत बना देती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Passwords: hash with scrypt/argon2/bcrypt + salt, never store plain text
Step 2 → Auth: Depends(...) on every private route; compare secrets in constant time
Step 3 → Validation: Pydantic Field limits, extra="forbid", regex for formats
Step 4 → SQL: only bound parameters or ORM; never f-string SQL
Step 5 → CORS: allow only your frontend origins; TrustedHost for allowed hostnames
Step 6 → Headers + HTTPS: HSTS, nosniff; TLS terminated at nginx/load balancer
Step 7 → Rate limit login and expensive endpoints (per IP/user; Redis in production)
Step 8 → Production hygiene: docs off or protected, no stack traces, secrets in env, logs without PII, dependency updates
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Passwords: scrypt/argon2/bcrypt + salt से hash करें, plain text कभी नहीं
Step 2 → Auth: हर private route पर Depends(...); secrets constant time में compare करें
Step 3 → Validation: Pydantic Field limits, extra="forbid", formats के लिए regex
Step 4 → SQL: सिर्फ़ bound parameters या ORM; f-string SQL कभी नहीं
Step 5 → CORS: सिर्फ़ अपने frontend origins; allowed hostnames के लिए TrustedHost
Step 6 → Headers + HTTPS: HSTS, nosniff; TLS nginx/load balancer पर खत्म करें
Step 7 → Login और भारी endpoints पर rate limit (per IP/user; production में Redis)
Step 8 → Production hygiene: docs बंद/सुरक्षित, stack trace नहीं, secrets env में, logs में PII नहीं, dependencies update
```

---

## 🟡 Real World Example
A UPI payments API: `POST /transfer` needs a valid bearer token, the amount is limited to `gt=0, le=100000`, the IFSC code must match a regex, unknown fields are rejected so nobody can inject `"admin": true`, login attempts are limited to 5 per minute per IP, `/docs` is disabled in production, and the API only accepts calls from `app.example.com` and `api.example.com` hosts.

## 🟡 Real Example Hindi mein
UPI payments API: `POST /transfer` के लिए वैध bearer token चाहिए, amount `gt=0, le=100000` तक सीमित है, IFSC code regex से मिलना चाहिए, अनजान fields reject होते हैं ताकि कोई `"admin": true` न डाल सके, login प्रयास प्रति IP प्रति मिनट 5 तक सीमित हैं, production में `/docs` बंद है और API सिर्फ़ `app.example.com` और `api.example.com` hosts से calls लेती है।

---

## 💻 Code Example — Basic
```python
# Basic: hash a password safely using only the standard library
import hashlib  # scrypt hash function
import hmac  # constant-time compare
import os  # secure random salt


def hash_password(pw: str) -> str:
    salt: bytes = os.urandom(16)  # random salt per user
    dk: bytes = hashlib.scrypt(pw.encode(), salt=salt, n=2**14, r=8, p=1)  # slow, memory-hard hash
    return salt.hex() + ":" + dk.hex()  # store salt together with the hash


def verify_password(pw: str, stored: str) -> bool:
    salt_hex, dk_hex = stored.split(":")  # separate salt and hash
    dk: bytes = hashlib.scrypt(pw.encode(), salt=bytes.fromhex(salt_hex), n=2**14, r=8, p=1)  # re-hash
    return hmac.compare_digest(dk.hex(), dk_hex)  # constant-time comparison


stored: str = hash_password("secret123")  # create hash
print(verify_password("secret123", stored), verify_password("wrong", stored))  # check both
# Output: True False
print(hash_password("a") == hash_password("a"))  # same password, different salt
# Output: False
```

## 💻 Code Example — Advanced
```python
# Production style: API key auth, CORS, TrustedHost, headers, strict validation, rate limit
# pip install fastapi httpx   (every line below was run; outputs shown are real)
import secrets  # constant-time compare
import time  # monotonic clock for rate limit
from typing import Annotated, Dict, List, Optional  # types

from fastapi import Depends, FastAPI, HTTPException, Request, status  # core
from fastapi.middleware.cors import CORSMiddleware  # CORS
from fastapi.middleware.trustedhost import TrustedHostMiddleware  # Host header check
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer  # Bearer auth
from fastapi.testclient import TestClient  # demo runner
from pydantic import BaseModel, ConfigDict, Field  # strict schemas

# docs_url/redoc_url/openapi_url=None hides the interactive docs in production
app: FastAPI = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["testserver", "api.example.com"])  # block bad Host
app.add_middleware(  # only your frontend may call from a browser
    CORSMiddleware,
    allow_origins=["https://app.example.com"],  # NOT "*" when using credentials
    allow_methods=["GET", "POST"],  # only needed verbs
    allow_headers=["Authorization"],  # only needed headers
)


@app.middleware("http")  # add security headers to every response
async def security_headers(request: Request, call_next):
    response = await call_next(request)  # run the route
    response.headers["X-Content-Type-Options"] = "nosniff"  # stop MIME sniffing
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"  # force HTTPS
    return response  # send back


bearer: HTTPBearer = HTTPBearer(auto_error=False)  # we raise our own 401
API_KEY: str = "s3cr3t-key"  # in real life: os.environ / secrets manager


def require_key(creds: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer)]) -> None:
    if creds is None or not secrets.compare_digest(creds.credentials, API_KEY):  # constant-time
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,  # 401 = not authenticated
            "Invalid credentials",  # vague message on purpose
            headers={"WWW-Authenticate": "Bearer"},  # tells client how to authenticate
        )


class Transfer(BaseModel):  # strict request model
    model_config = ConfigDict(extra="forbid")  # unknown fields -> 422 (blocks mass assignment)
    amount: float = Field(gt=0, le=100000)  # sane limits
    to: str = Field(pattern=r"^[A-Z]{4}0[A-Z0-9]{6}$")  # IFSC-like format


@app.post("/transfer", dependencies=[Depends(require_key)])  # auth on the route
def transfer(t: Transfer) -> Dict[str, str]:
    return {"status": "ok"}  # business logic here


calls: Dict[str, List[float]] = {}  # per-IP timestamps (use Redis in production)


def rate_limit(request: Request) -> None:
    ip: str = request.client.host if request.client else "?"  # caller IP
    now: float = time.monotonic()  # current time
    window: List[float] = [t for t in calls.get(ip, []) if now - t < 60]  # last 60 s
    if len(window) >= 3:  # limit 3 per minute (demo)
        raise HTTPException(429, "Too many requests")  # 429 = slow down
    window.append(now)  # record this call
    calls[ip] = window  # save


@app.get("/login-ish", dependencies=[Depends(rate_limit)])  # limited route
def login_ish() -> Dict[str, str]:
    return {"ok": "1"}  # pretend login


c: TestClient = TestClient(app)  # demo client
body = {"amount": 5, "to": "HDFC0123456"}  # valid payload
print(c.post("/transfer", json=body).status_code)  # no token
# Output: 401
r = c.post("/transfer", json=body, headers={"Authorization": "Bearer s3cr3t-key"})  # good token
print(r.status_code, r.headers["x-content-type-options"])  # 200 and header
# Output: 200 nosniff
print(c.post("/transfer", json={**body, "amount": -5}, headers={"Authorization": "Bearer s3cr3t-key"}).status_code)
# Output: 422
print(c.post("/transfer", json={**body, "admin": True}, headers={"Authorization": "Bearer s3cr3t-key"}).status_code)
# Output: 422
print(c.get("/docs").status_code)  # docs disabled
# Output: 404
print(c.get("/login-ish", headers={"host": "evil.com"}).status_code)  # wrong Host header
# Output: 400
print([c.get("/login-ish").status_code for _ in range(4)])  # 4th call is limited
# Output: [200, 200, 200, 429]
```
Also verified: a CORS preflight `OPTIONS` from `https://app.example.com` returned `200` with `access-control-allow-origin: https://app.example.com`, while one from `https://evil.com` returned `400` with no allow-origin header. For real login endpoints use a maintained library (`pwdlib` with Argon2, or `passlib`/`bcrypt`) and JWT via `PyJWT` or `authlib`; the stdlib scrypt shown here is valid but you must tune the cost parameters yourself.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (FastAPI): security via middleware + dependencies
app.add_middleware(CORSMiddleware, allow_origins=["https://app.example.com"])  # CORS
@app.post("/pay", dependencies=[Depends(require_key)])  # auth
def pay(t: Transfer) -> dict: ...  # validation by Pydantic
```
```javascript
// JavaScript (Express): the same checklist with packages
app.use(cors({ origin: "https://app.example.com" }));   // CORS
app.use(helmet());                                       // security headers
app.use(rateLimit({ windowMs: 60_000, max: 5 }));        // rate limit
app.post("/pay", requireKey, validate(transferSchema), handler);  // auth + zod validation
// password hashing: bcrypt / argon2 packages
```

Key differences: Express needs `helmet`, `express-rate-limit`, `zod` as separate packages; FastAPI has CORS, TrustedHost, HTTPBearer and Pydantic validation built in, but security headers and rate limiting are still your job (or nginx/`slowapi`).

---

## 🟠 FastAPI Connection
FastAPI's `Depends` is the natural place for auth, so security cannot be forgotten route by route: attach it to a whole router.

```python
# Protect an entire router once
from fastapi import APIRouter, Depends, FastAPI  # pieces

admin: APIRouter = APIRouter(prefix="/admin", dependencies=[Depends(require_key)])  # all routes locked


@admin.get("/stats")  # inherits the dependency
def stats() -> dict:
    return {"users": 100}  # only reachable with a valid key


app2: FastAPI = FastAPI()  # app
app2.include_router(admin)  # mount
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Storing or comparing passwords in plain text / fast hashes
```python
# Wrong:
db.save(password)                                 # plain text
hashlib.md5(pw.encode()).hexdigest()              # fast hash, crackable

# Right: scrypt / argon2 / bcrypt with a per-user salt, compare with hmac.compare_digest
```

❌ Mistake 2: `allow_origins=["*"]` with credentials, or `allow_methods=["*"]` everywhere
```python
# Wrong:
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True)

# Right: list exact frontend origins
app.add_middleware(CORSMiddleware, allow_origins=["https://app.example.com"])
```

❌ Mistake 3: Building SQL with f-strings
```python
# Wrong:
db.execute(text(f"SELECT * FROM users WHERE name = '{name}'"))

# Right: bound parameters
db.execute(text("SELECT * FROM users WHERE name = :n"), {"n": name})
```

❌ Mistake 4: Leaving `/docs`, debug mode and detailed errors on in production
```python
# Right: FastAPI(docs_url=None, redoc_url=None, openapi_url=None) or protect them; debug=False
```

❌ Mistake 5: Trusting the client for permissions
```python
# Wrong: body contains {"role": "admin"} and you save it
# Right: extra="forbid" and set role on the server only (and check ownership: object-level auth)
```

---

## 🧠 Tricky Interview Question

**Q**: You hash the same password twice with a random salt. Are the two stored values equal? Can both verify the password?

```python
print(hash_password("a") == hash_password("a"))
print(verify_password("a", hash_password("a")))
```

**Answer**:
```
False
True
```
Each hash includes its own random salt, so two users with the same password get different stored values (attackers cannot reuse a lookup table), yet `verify_password` re-hashes using the stored salt and matches. (Verified by running.)

---

## ⚫ Interview Questions + Answers

Q1: 401 vs 403?
A1: 401 means "not authenticated" (no or bad credentials). 403 means "authenticated but not allowed".

Q2: Why `secrets.compare_digest` / `hmac.compare_digest` instead of `==`?
A2: `==` can stop at the first different character, leaking timing information. The digest comparison takes the same time regardless.

Q3: What does CORS protect?
A3: Browsers block cross-origin JavaScript from reading responses unless the server allows the origin. It does NOT protect your API from curl or other servers; you still need authentication.

Q4: What is mass assignment and how does Pydantic help?
A4: Client sends extra fields (`is_admin`) and the server blindly saves them. Use separate input schemas, `extra="forbid"`, and never `Model(**request_json)` into a DB model with privileged fields.

Q5: Where should rate limiting live?
A5: Ideally at the edge (nginx, API gateway, Cloudflare). In the app, use Redis-backed limiting (e.g. `slowapi`/custom) because in-memory counters are per worker.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Every API that has users, money or personal data (always)
- Before each production release as a gate

❌ Avoid when:
- Never skip it. You may relax items for internal throwaway tools, but still keep auth and validation

---

## 📊 Visual Diagram

```
 Internet
    │  HTTPS (TLS at nginx / LB)
    ▼
 [nginx] rate limit, size limit, gzip
    ▼
 TrustedHost ─► CORS ─► security headers
    ▼
 Router ─ Depends(auth) ─► Pydantic validation (extra="forbid")
    ▼
 Service (authorization: does THIS user own THIS object?)
    ▼
 DB (bound parameters only) ─ secrets from env, hashed passwords
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hashing | One-way scramble of a password | password को एकतरफ़ा बदलना |
| Salt | Random value added before hashing | hash से पहले जोड़ा गया random मान |
| CORS | Browser cross-origin permission | browser की cross-origin अनुमति |
| Rate limit | Cap on requests per time | समय में requests की सीमा |
| Mass assignment | Client sets forbidden fields | client का मना किए fields भरना |
| HSTS | Header that forces HTTPS | HTTPS ज़बरदस्ती कराने वाला header |

---

## ⚡ 3-Line Summary
English: Hash passwords with salt, put auth on every private route, validate strictly, limit CORS and hosts, add headers and rate limits, and hide docs and secrets in production.
Hindi: Passwords को salt के साथ hash करें, हर private route पर auth लगाएँ, सख़्त validation करें, CORS व hosts सीमित करें, headers और rate limits जोड़ें और production में docs व secrets छिपाएँ।

---

## ➡️ Next Topic
**350. FastAPI Deployment** — running FastAPI in production with Uvicorn, Gunicorn, Docker and nginx.
