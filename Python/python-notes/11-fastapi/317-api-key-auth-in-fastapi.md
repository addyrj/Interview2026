---

# 317. API Key Auth in FastAPI
# हिंदी में: FastAPI में API Key Authentication (header वाली चाबी)

---

## 🔵 Simple Definition (English)
An API key is a long secret string that identifies a client application (not a person). The client sends it in a header such as `X-API-Key`, and the server checks it. FastAPI provides `APIKeyHeader`, `APIKeyQuery` and `APIKeyCookie` to read the key and show it in Swagger.

## 🔵 सरल परिभाषा (Hindi)
API key एक लंबी secret string है जो किसी client application (व्यक्ति नहीं) की पहचान करती है। Client इसे `X-API-Key` जैसे header में भेजता है और server उसे जाँचता है। FastAPI में `APIKeyHeader`, `APIKeyQuery` और `APIKeyCookie` हैं जो key पढ़ते हैं और Swagger में दिखाते हैं।

---

## 🔴 Problem it Solves
Server-to-server calls and public developer APIs do not have a human typing a password. Username/password plus JWT login is too heavy for a cron job or a partner integration. An API key is the simplest identity: easy to issue, rotate, rate-limit and revoke per client, and easy to send in one header.

## 🔴 यह क्यों बना? (Hindi)
Server-to-server calls और public developer APIs में कोई इंसान password नहीं डालता। Cron job या partner integration के लिए username/password और JWT login भारी है। API key सबसे सरल पहचान है: जारी करना, बदलना, rate limit लगाना और रद्द करना हर client के लिए आसान, और एक ही header में भेजी जा सकती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You generate a random key: secrets.token_urlsafe(32)
Step 2 → You store only its HASH in the DB (like a password), show the key once
Step 3 → Client sends header  X-API-Key: <key>
Step 4 → APIKeyHeader dependency extracts it (missing → 401/403)
Step 5 → You hash the received key and look it up (timing-safe compare)
Step 6 → Found and active → request allowed, client id known for rate limits and logs
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप random key बनाते हैं: secrets.token_urlsafe(32)
Step 2 → DB में सिर्फ़ उसका HASH रखते हैं (password की तरह), key एक बार दिखाते हैं
Step 3 → Client header भेजता है  X-API-Key: <key>
Step 4 → APIKeyHeader dependency उसे निकालती है (न हो तो 401/403)
Step 5 → आप मिली key का hash निकालकर lookup करते हैं (timing-safe compare)
Step 6 → मिली और active हो तो request allowed, client की पहचान rate limit और logs में काम आती है
```

---

## 🟡 Real World Example
An AI app sells its API: each customer gets a key like `sk-live-...`. Usage is counted per key for billing and rate limits. Razorpay, Stripe and OpenAI all use key-based auth for server calls. A webhook receiver validates a shared secret header from the provider.

## 🟡 Real Example Hindi mein
कोई AI app अपनी API बेचता है: हर customer को `sk-live-...` जैसी key मिलती है। Billing और rate limit के लिए usage हर key पर गिना जाता है। Razorpay, Stripe और OpenAI सब server calls के लिए key आधारित auth इस्तेमाल करते हैं। Webhook receiver provider का भेजा shared secret header जाँचता है।

---

## 💻 Code Example — Basic
```python
# Basic API key auth - run directly (pip install fastapi httpx)
from fastapi import Depends, FastAPI, HTTPException, Security, status  # core
from fastapi.security import APIKeyHeader  # reads the key from a header
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # create app
api_key_header: APIKeyHeader = APIKeyHeader(name="X-API-Key", auto_error=False)  # auto_error=False: we craft the error

VALID_KEYS: set[str] = {"key-abc-123", "key-def-456"}  # demo only; real keys live hashed in a DB


def require_api_key(key: str | None = Security(api_key_header)) -> str:  # dependency that returns the key
    if key not in VALID_KEYS:  # missing or wrong (None is also "not in")
        raise HTTPException(  # reject
            status_code=status.HTTP_401_UNAUTHORIZED,  # unauthenticated
            detail="Invalid or missing API key",  # message
        )
    return key  # accepted


@app.get("/data")  # protected endpoint
def data(key: str = Depends(require_api_key)) -> dict:  # key injected
    return {"data": [1, 2, 3], "client": key[-3:]}  # show only last 3 chars (never echo full keys)


@app.get("/public")  # open endpoint
def public() -> dict:  # no auth
    return {"hello": "world"}  # response


c: TestClient = TestClient(app)  # demo client
print(c.get("/public").json())  # no key needed
# Output: {'hello': 'world'}
print(c.get("/data").status_code)  # no key
# Output: 401
print(c.get("/data", headers={"X-API-Key": "wrong"}).status_code)  # wrong key
# Output: 401
print(c.get("/data", headers={"x-api-key": "key-abc-123"}).json())  # header names are case-insensitive
# Output: {'data': [1, 2, 3], 'client': '123'}
```

## 💻 Code Example — Advanced
```python
# Production style: hashed keys, timing-safe check, per-key scopes, simple rate limit, rotation
import hashlib  # hash keys before storing
import hmac  # constant-time compare
import secrets  # generate keys
import time  # rate-limit window
from dataclasses import dataclass, field  # record type
from typing import Annotated  # metadata
from fastapi import Depends, FastAPI, HTTPException, Request, Security, status  # core
from fastapi.security import APIKeyHeader  # extractor
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # app
header: APIKeyHeader = APIKeyHeader(name="X-API-Key", auto_error=False)  # custom errors


def sha256(key: str) -> str:  # fast hash is fine for HIGH-ENTROPY random keys (not for passwords)
    return hashlib.sha256(key.encode()).hexdigest()  # hex digest


@dataclass
class Client:  # what we store per key
    name: str  # customer name
    scopes: set[str]  # allowed actions
    active: bool = True  # revoked keys are inactive
    hits: list[float] = field(default_factory=list)  # request timestamps for rate limit


def new_key(name: str, scopes: set[str]) -> str:  # issue a key
    raw: str = "sk_" + secrets.token_urlsafe(24)  # unguessable random key
    STORE[sha256(raw)] = Client(name, scopes)  # store ONLY the hash
    return raw  # show to the customer once


STORE: dict[str, Client] = {}  # hash -> client (a DB table in real life)
READER: str = new_key("reader-co", {"read"})  # key that can read
WRITER: str = new_key("writer-co", {"read", "write"})  # key that can read and write


def authenticate(key: str | None = Security(header)) -> Client:  # find the client
    if not key:  # header missing
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing API key", headers={"WWW-Authenticate": "ApiKey"})  # 401
    digest: str = sha256(key)  # hash the presented key
    found: Client | None = None  # result
    for stored, client in STORE.items():  # constant-time compare against each stored hash (small tables only; use DB index otherwise)
        if hmac.compare_digest(stored, digest):  # timing-safe
            found = client  # match
    if found is None or not found.active:  # unknown or revoked
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid API key")  # 401
    return found  # ok


def rate_limit(client: Annotated[Client, Depends(authenticate)]) -> Client:  # 3 requests per 60 seconds per key
    now: float = time.monotonic()  # monotonic clock is safe against clock changes
    client.hits[:] = [t for t in client.hits if now - t < 60]  # drop old hits
    if len(client.hits) >= 3:  # limit reached
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Rate limit exceeded", headers={"Retry-After": "60"})  # 429
    client.hits.append(now)  # record
    return client  # ok


def need(scope: str):  # factory for scope check
    def check(client: Annotated[Client, Depends(rate_limit)]) -> Client:  # chain: authenticate -> rate_limit -> scope
        if scope not in client.scopes:  # not allowed
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Scope '{scope}' required")  # 403
        return client  # ok
    return check  # return dependency


@app.get("/items")  # needs read
def items(c: Annotated[Client, Depends(need("read"))]) -> dict:  # injected
    return {"client": c.name}  # response


@app.post("/items")  # needs write
def add(c: Annotated[Client, Depends(need("write"))]) -> dict:  # injected
    return {"added_by": c.name}  # response


tc: TestClient = TestClient(app)  # demo client
print(len(READER) > 20, READER.startswith("sk_"))  # random key format
# Output: True True
print(any(READER in k for k in STORE))  # raw keys are NOT stored, only hashes
# Output: False
print(tc.get("/items", headers={"X-API-Key": READER}).json())  # read ok
# Output: {'client': 'reader-co'}
print(tc.post("/items", headers={"X-API-Key": READER}).status_code)  # reader cannot write
# Output: 403
print(tc.post("/items", headers={"X-API-Key": WRITER}).json())  # writer can
# Output: {'added_by': 'writer-co'}
print(tc.get("/items").status_code, tc.get("/items", headers={"X-API-Key": "sk_fake"}).status_code)  # missing / wrong
# Output: 401 401
r = tc.get("/items", headers={"X-API-Key": READER})  # 3rd request of the minute for READER (1 + 403 + this = 3)
r2 = tc.get("/items", headers={"X-API-Key": READER})  # 4th request -> limited
print(r.status_code, r2.status_code, r2.headers["retry-after"])  # limit hit
# Output: 200 429 60
STORE[sha256(WRITER)].active = False  # revoke the writer key
print(tc.post("/items", headers={"X-API-Key": WRITER}).status_code)  # no longer works
# Output: 401
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (FastAPI)
api_key = APIKeyHeader(name="X-API-Key")
@app.get("/data")
def data(key: str = Security(api_key)): ...
```
```javascript
// JavaScript (Express middleware)
const apiKey = (req, res, next) => {
  const key = req.header("x-api-key");
  if (!VALID.has(key)) return res.status(401).json({ detail: "Invalid API key" });
  next();
};
app.get("/data", apiKey, (req, res) => res.json({ data: [1, 2, 3] }));

// Client
fetch("/data", { headers: { "X-API-Key": process.env.API_KEY } });
```

Key difference: the logic is the same. FastAPI registers the key scheme in OpenAPI so Swagger shows an Authorize button for it, and you can combine it with scopes and rate limit as chained dependencies. Never ship an API key inside browser JavaScript, anyone can read it. Keys belong on servers.

---

## 🟠 FastAPI Connection
`APIKeyHeader`, `APIKeyQuery` and `APIKeyCookie` are dependencies (security schemes). Apply to one route (`Depends`/`Security`), a router (`dependencies=[...]`) or the whole app. With `auto_error=True` (default) a missing key produces an automatic error (401 in recent FastAPI versions, 403 in older ones), so set `auto_error=False` to control the message yourself.

```python
# FastAPI: protect a whole router with one key check
from fastapi import APIRouter, Depends, FastAPI, HTTPException  # core
from fastapi.security import APIKeyHeader  # extractor
from fastapi.testclient import TestClient  # demo client

header: APIKeyHeader = APIKeyHeader(name="X-API-Key", auto_error=False)  # extractor


def check(key: str | None = Depends(header)) -> None:  # guard (no return value needed)
    if key != "secret":  # compare (use hmac.compare_digest in real code)
        raise HTTPException(status_code=401, detail="Bad key")  # reject


admin: APIRouter = APIRouter(prefix="/admin", dependencies=[Depends(check)])  # every route needs a key


@admin.get("/stats")  # route in the router
def stats() -> dict:  # no parameter needed
    return {"users": 10}  # response


app: FastAPI = FastAPI()  # app
app.include_router(admin)  # attach
c: TestClient = TestClient(app)  # client
print(c.get("/admin/stats").status_code, c.get("/admin/stats", headers={"X-API-Key": "secret"}).json())  # blocked then allowed
# Output: 401 {'users': 10}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Comparing keys with `==` or storing them in plain text
```python
# Wrong - timing attack and a leaked DB exposes every key
if key == stored_key: ...

# Correct - store a hash, compare with hmac.compare_digest
hmac.compare_digest(sha256(key), stored_hash)
```

❌ Mistake 2: Sending keys in the URL query
```python
# Wrong - URLs end up in logs, browser history and referrer headers
# GET /data?api_key=secret

# Correct - header X-API-Key (or Authorization)
```

❌ Mistake 3: One shared key for everyone, with no way to revoke
```python
# Wrong - one leaked key breaks everyone; cannot tell who did what
# Correct - one key per client with scopes, last-used time, expiry and a revoke flag
```

---

## 🧠 Tricky Interview Question

**Q**: What does this print?

```python
from fastapi import Depends, FastAPI
from fastapi.security import APIKeyHeader
from fastapi.testclient import TestClient

app = FastAPI()
h = APIKeyHeader(name="X-Key", auto_error=False)

@app.get("/a")
def a(k: str | None = Depends(h)):
    return {"k": k}

c = TestClient(app)
print(c.get("/a").json())
print(c.get("/a", headers={"x-key": "v"}).json())
print(c.get("/a", headers={"X-Key": ""}).json())
```

**Answer**:
```
{'k': None}
{'k': 'v'}
{'k': None}
```
With `auto_error=False` the extractor never fails: no header gives `None`, so YOUR code must handle `None`. Header names are case-insensitive. An empty header value also becomes `None` in the tested version (FastAPI 0.162, behaviour can differ between versions), so still write `if not key` rather than only `is None`.

---

## ⚫ Interview Questions + Answers

Q1: API key vs JWT?
A1: An API key identifies an application, is long-lived and is looked up on every request (easy to revoke). A JWT identifies a user session, is short-lived and is verified by signature without a lookup. Use keys for server-to-server and public developer APIs, JWTs for user login.

Q2: How should keys be stored?
A2: Generate with `secrets.token_urlsafe`, show once, store only a hash (SHA-256 is enough for high-entropy random keys; passwords need bcrypt/argon2/scrypt). Keep a short prefix visible (`sk_live_ab12`) to help users identify keys.

Q3: Where should the key be sent?
A3: In a header (`X-API-Key` or `Authorization: Bearer`) over HTTPS. Not in query strings, because URLs are logged.

Q4: What does `auto_error` do?
A4: `True` (default) makes the extractor raise automatically when the key is missing. `False` returns `None` so you can customize the error or allow several auth methods (key or JWT).

Q5: How do you rotate keys without downtime?
A5: Allow two active keys per client during an overlap period, then deactivate the old one. Track `last_used_at` to see whether clients switched.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Server-to-server APIs, cron jobs, webhooks, partner integrations
- Public developer APIs with per-customer usage limits and billing
- Internal tools where a simple secret is enough

❌ Avoid when:
- Browser or mobile client code (the key would be visible), use user login + JWT
- You need to know which human acted (keys identify apps)
- You need fine, per-user permissions (combine with scopes or use OAuth2)

---

## 📊 Visual Diagram

```
 Client app                     FastAPI
   │ GET /items                    │
   │ X-API-Key: sk_abc... ───────► APIKeyHeader (extract)
   │                               sha256(key) ──► lookup in DB (hash)
   │                               active? scope ok? under rate limit?
   │ ◄── 200 / 401 / 403 / 429 ─── endpoint

 DB stores:  sha256(key) | client | scopes | active | created | last_used
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| API key | Secret identifying an app | app की पहचान वाली secret |
| APIKeyHeader | FastAPI extractor for a header key | header से key पढ़ने वाला |
| auto_error | Auto-raise when key missing | key न होने पर अपने-आप error |
| Rate limit | Max requests per time | समय में अधिकतम requests |
| 429 | Too many requests | बहुत ज़्यादा requests |
| Rotation | Replace old key with new | पुरानी key की जगह नई |
| Timing attack | Guess secret from compare time | compare के समय से secret का अंदाज़ा |

---

## ⚡ 3-Line Summary
English: An API key is a secret header value that identifies a client app. Store only its hash, compare in constant time, send it in a header over HTTPS, and give each client its own revocable key. Add scopes and rate limits as chained dependencies.
Hindi: API key एक secret header value है जो client app की पहचान कराती है। सिर्फ़ उसका hash रखें, constant time में compare करें, HTTPS पर header में भेजें और हर client को अपनी रद्द की जा सकने वाली key दें। Scopes और rate limit को chained dependencies की तरह जोड़ें।

---

## ➡️ Next Topic
**318. Middleware in FastAPI** — run code around every request: logging, timing, request ids, CORS.
