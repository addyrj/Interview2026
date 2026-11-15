---

# 316. JWT Auth in FastAPI
# हिंदी में: FastAPI में JWT Authentication (signed token से login)

---

## 🔵 Simple Definition (English)
A JWT (JSON Web Token) is a signed string with three parts, `header.payload.signature`. The payload holds claims like the user id (`sub`) and expiry (`exp`). The server signs it with a secret key, so later it can verify the token without looking up a session in a database.

## 🔵 सरल परिभाषा (Hindi)
JWT (JSON Web Token) तीन हिस्सों वाली signed string है: `header.payload.signature`। Payload में user id (`sub`) और expiry (`exp`) जैसे claims होते हैं। Server इसे secret key से sign करता है, इसलिए बाद में database में session ढूँढे बिना token verify हो जाता है।

---

## 🔴 Problem it Solves
Server-side sessions need shared storage (Redis/DB) and lookups on every request, which is hard with many servers or microservices. JWTs are self-contained: any service that has the key can verify the signature, check `exp` and trust the claims, so authentication scales horizontally without a session store.

## 🔴 यह क्यों बना? (Hindi)
Server-side sessions को साझा storage (Redis/DB) और हर request पर lookup चाहिए, जो कई servers या microservices में मुश्किल है। JWT खुद में पूरा होता है: key वाली कोई भी service signature verify करके `exp` देख सकती है और claims पर भरोसा कर सकती है, इसलिए बिना session store के authentication scale होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Login: server verifies username + password
Step 2 → Server builds payload {"sub": "asha", "exp": now+15min}
Step 3 → jwt.encode(payload, SECRET, algorithm="HS256") -> token string
Step 4 → Client sends Authorization: Bearer <token> on each request
Step 5 → jwt.decode(token, SECRET, algorithms=["HS256"]) checks signature AND exp
Step 6 → Invalid/expired → 401; valid → load user from "sub"
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Login: server username + password जाँचता है
Step 2 → Server payload बनाता है {"sub": "asha", "exp": अभी+15 मिनट}
Step 3 → jwt.encode(payload, SECRET, algorithm="HS256") से token string बनती है
Step 4 → Client हर request में Authorization: Bearer <token> भेजता है
Step 5 → jwt.decode(token, SECRET, algorithms=["HS256"]) signature और exp दोनों जाँचता है
Step 6 → गलत/expired हो तो 401; सही हो तो "sub" से user लाओ
```

---

## 🟡 Real World Example
A Razorpay-like merchant app issues a 15-minute access token and a 7-day refresh token. The mobile app attaches the access token to each call. When it expires, the app uses the refresh token to get a new pair, so users stay logged in without sending the password again. Microservices (orders, payments) all verify the same token.

## 🟡 Real Example Hindi mein
Razorpay जैसा merchant app 15 मिनट का access token और 7 दिन का refresh token देता है। Mobile app हर call में access token लगाता है। Expire होने पर app refresh token से नई जोड़ी लेता है, इसलिए user को दोबारा password नहीं देना पड़ता। Microservices (orders, payments) सब वही token verify करती हैं।

---

## 💻 Code Example — Basic
```python
# Basic JWT with PyJWT - run directly (pip install pyjwt)
import time  # for exp as unix seconds
import jwt  # PyJWT library

SECRET: str = "change-me-use-a-long-random-string-32chars+"  # in production: from environment variable
ALGO: str = "HS256"  # HMAC-SHA256 signing

payload: dict = {"sub": "asha", "role": "admin", "exp": int(time.time()) + 60}  # claims: subject, custom, expiry (60 s)
token: str = jwt.encode(payload, SECRET, algorithm=ALGO)  # create the signed token
print(token.count("."))  # three parts means two dots
# Output: 2

decoded: dict = jwt.decode(token, SECRET, algorithms=[ALGO])  # verify signature + expiry, return claims
print(decoded["sub"], decoded["role"])  # claims are readable
# Output: asha admin

try:  # a tampered token must fail
    bad: str = token[:-2] + ("AA" if not token.endswith("AA") else "BB")  # change the signature end
    jwt.decode(bad, SECRET, algorithms=[ALGO])  # verify
except jwt.InvalidTokenError as exc:  # base class for all JWT problems
    print(type(exc).__name__)  # which error
# Output: InvalidSignatureError

try:  # an expired token must fail
    old: str = jwt.encode({"sub": "asha", "exp": int(time.time()) - 10}, SECRET, algorithm=ALGO)  # already expired
    jwt.decode(old, SECRET, algorithms=[ALGO])  # verify
except jwt.ExpiredSignatureError:  # specific error
    print("expired")  # message
# Output: expired

print(jwt.decode(token, options={"verify_signature": False})["sub"])  # reading WITHOUT verifying (never trust this)
# Output: asha
```

## 💻 Code Example — Advanced
```python
# Production style: login, access + refresh tokens, current_user dependency, role check (pip install fastapi httpx python-multipart pyjwt)
import hashlib  # password hashing
import hmac  # constant-time compare
import os  # salt
import time  # timestamps
from typing import Annotated  # metadata
import jwt  # PyJWT
from fastapi import Depends, FastAPI, HTTPException, status  # core
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  # OAuth2 helpers
from fastapi.testclient import TestClient  # demo client

SECRET: str = os.environ.get("JWT_SECRET", "dev-only-secret-change-me-please-32+")  # NEVER hardcode in production
ALGO: str = "HS256"  # signing algorithm
ACCESS_TTL: int = 15 * 60  # 15 minutes
REFRESH_TTL: int = 7 * 24 * 3600  # 7 days

app: FastAPI = FastAPI()  # app
oauth2: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="token")  # token extractor


def hash_pw(pw: str, salt: bytes | None = None) -> str:  # salted slow hash (stdlib)
    salt = salt or os.urandom(16)  # random salt
    return salt.hex() + "$" + hashlib.scrypt(pw.encode(), salt=salt, n=2**14, r=8, p=1).hex()  # salt$hash


def check_pw(pw: str, stored: str) -> bool:  # verify password
    return hmac.compare_digest(hash_pw(pw, bytes.fromhex(stored.split("$")[0])), stored)  # timing-safe


USERS: dict[str, dict] = {  # fake DB
    "asha": {"hash": hash_pw("pw1"), "role": "admin"},  # admin
    "ravi": {"hash": hash_pw("pw2"), "role": "viewer"},  # viewer
}


def make_token(sub: str, kind: str, ttl: int) -> str:  # build any token
    now: int = int(time.time())  # current time
    claims: dict = {"sub": sub, "type": kind, "iat": now, "exp": now + ttl}  # standard claims + token type
    return jwt.encode(claims, SECRET, algorithm=ALGO)  # sign


def decode(token: str, expected_type: str) -> dict:  # verify and check type
    try:  # catch all JWT errors
        claims: dict = jwt.decode(token, SECRET, algorithms=[ALGO], options={"require": ["exp", "sub"]})  # fix the algorithm list!
    except jwt.ExpiredSignatureError:  # old token
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token expired", headers={"WWW-Authenticate": "Bearer"})  # 401
    except jwt.InvalidTokenError:  # any other problem
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token", headers={"WWW-Authenticate": "Bearer"})  # 401
    if claims.get("type") != expected_type:  # refresh token used as access token, or reverse
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong token type")  # 401
    return claims  # trusted claims


@app.post("/token")  # login
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:  # form fields
    user: dict | None = USERS.get(form.username)  # find
    if user is None or not check_pw(form.password, user["hash"]):  # check
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect username or password")  # same message for both
    return {  # token pair
        "access_token": make_token(form.username, "access", ACCESS_TTL),  # short
        "refresh_token": make_token(form.username, "refresh", REFRESH_TTL),  # long
        "token_type": "bearer",  # scheme
    }


@app.post("/refresh")  # exchange refresh for a new access token
def refresh(refresh_token: str) -> dict:  # token in query for the demo (use a body or cookie in real life)
    claims: dict = decode(refresh_token, "refresh")  # must be a refresh token
    return {"access_token": make_token(claims["sub"], "access", ACCESS_TTL), "token_type": "bearer"}  # new access


def current_user(token: Annotated[str, Depends(oauth2)]) -> dict:  # dependency used by routes
    claims: dict = decode(token, "access")  # verify
    user: dict | None = USERS.get(claims["sub"])  # load user (also detect deleted users)
    if user is None:  # user removed after token was issued
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")  # 401
    return {"username": claims["sub"], "role": user["role"]}  # user info


def admin_only(user: Annotated[dict, Depends(current_user)]) -> dict:  # role check
    if user["role"] != "admin":  # not admin
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admins only")  # 403
    return user  # ok


@app.get("/me")  # any logged-in user
def me(user: Annotated[dict, Depends(current_user)]) -> dict:  # injected
    return user  # response


@app.get("/admin")  # admins only
def admin(user: Annotated[dict, Depends(admin_only)]) -> dict:  # injected
    return {"welcome": user["username"]}  # response


c: TestClient = TestClient(app)  # demo client
pair: dict = c.post("/token", data={"username": "asha", "password": "pw1"}).json()  # login
auth: dict = {"Authorization": f"Bearer {pair['access_token']}"}  # header
print(c.get("/me", headers=auth).json())  # works
# Output: {'username': 'asha', 'role': 'admin'}
print(c.get("/admin", headers=auth).json())  # admin route
# Output: {'welcome': 'asha'}
ravi: dict = c.post("/token", data={"username": "ravi", "password": "pw2"}).json()  # viewer login
print(c.get("/admin", headers={"Authorization": f"Bearer {ravi['access_token']}"}).status_code)  # forbidden
# Output: 403
print(c.get("/me", headers={"Authorization": f"Bearer {pair['refresh_token']}"}).json())  # refresh token rejected as access
# Output: {'detail': 'Wrong token type'}
new: dict = c.post("/refresh", params={"refresh_token": pair["refresh_token"]}).json()  # get a new access token
print(c.get("/me", headers={"Authorization": f"Bearer {new['access_token']}"}).status_code)  # works
# Output: 200
expired: str = jwt.encode({"sub": "asha", "type": "access", "exp": int(time.time()) - 5}, SECRET, algorithm=ALGO)  # old token
print(c.get("/me", headers={"Authorization": f"Bearer {expired}"}).json())  # explains why
# Output: {'detail': 'Token expired'}
none_token: str = jwt.encode({"sub": "asha", "type": "access", "exp": int(time.time()) + 60}, key=None, algorithm="none")  # "alg: none" attack
print(c.get("/me", headers={"Authorization": f"Bearer {none_token}"}).json())  # rejected because algorithms=[HS256]
# Output: {'detail': 'Invalid token'}
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (PyJWT)
token = jwt.encode({"sub": "asha", "exp": exp}, SECRET, algorithm="HS256")
claims = jwt.decode(token, SECRET, algorithms=["HS256"])
```
```javascript
// JavaScript (jsonwebtoken)
const jwt = require("jsonwebtoken");
const token = jwt.sign({ sub: "asha" }, SECRET, { algorithm: "HS256", expiresIn: "15m" });
const claims = jwt.verify(token, SECRET, { algorithms: ["HS256"] });
// Browser: where to keep it? In memory or an HttpOnly cookie; localStorage is readable by any XSS script
```

Key difference: the token format is identical, so a token made in Node can be verified in Python and the reverse. PyJWT takes `exp` as a unix timestamp (or a `datetime`), while `jsonwebtoken` has the handy `expiresIn: "15m"` string. In both, always pass the allowed `algorithms`.

---

## 🟠 FastAPI Connection
The recommended structure: `/token` login route, `OAuth2PasswordBearer` to extract, `current_user` dependency to decode and load, then `admin_only` or scope dependencies on top. Keep the signing secret in settings (`pydantic-settings`) and load it from an environment variable.

```python
# FastAPI: settings-driven secret and a timing-safe 401 helper
import os  # env access
import time  # clock
import jwt  # PyJWT
from fastapi import Depends, FastAPI, HTTPException  # core
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer  # simple bearer extractor
from fastapi.testclient import TestClient  # demo client

SECRET: str = os.environ.get("JWT_SECRET", "x" * 40)  # from environment, with demo fallback
app: FastAPI = FastAPI()  # app
bearer: HTTPBearer = HTTPBearer()  # extractor without OAuth2 form flow (good for pure API clients)


def current_sub(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> str:  # verify token
    try:  # decode
        return jwt.decode(creds.credentials, SECRET, algorithms=["HS256"])["sub"]  # return subject
    except jwt.InvalidTokenError:  # any failure
        raise HTTPException(status_code=401, detail="Invalid token")  # 401


@app.get("/whoami")  # protected
def whoami(sub: str = Depends(current_sub)) -> dict:  # injected
    return {"sub": sub}  # response


c: TestClient = TestClient(app)  # client
t: str = jwt.encode({"sub": "asha", "exp": int(time.time()) + 60}, SECRET, algorithm="HS256")  # make token
print(c.get("/whoami", headers={"Authorization": f"Bearer {t}"}).json())  # valid
# Output: {'sub': 'asha'}
print(c.get("/whoami", headers={"Authorization": "Bearer garbage"}).status_code)  # invalid
# Output: 401
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Not restricting `algorithms` on decode
```python
# Wrong - older libraries accepted alg "none" or key-confusion tricks
jwt.decode(token, SECRET)               # PyJWT 2.x raises, but never rely on defaults

# Correct
jwt.decode(token, SECRET, algorithms=["HS256"])
```

❌ Mistake 2: Putting secrets in the payload
```python
# Wrong - the payload is only base64 encoded, ANYONE can read it
{"sub": "asha", "password": "pw1", "card": "4111..."}

# Correct - only non-sensitive claims: sub, role, exp, iat
```

❌ Mistake 3: Long-lived access tokens with no way to revoke
```python
# Wrong - exp = 1 year; a stolen token works for a year
# Correct - 5-15 minute access token + refresh token (stored server-side or rotated) so you can revoke
```

---

## 🧠 Tricky Interview Question

**Q**: What does this print?

```python
import time
import jwt

t = jwt.encode({"sub": "a", "exp": int(time.time()) + 60}, "k" * 32, algorithm="HS256")
h, p, s = t.split(".")
print(jwt.decode(t, "k" * 32, algorithms=["HS256"])["sub"])
print(jwt.decode(t, options={"verify_signature": False})["sub"])
try:
    jwt.decode(t, "other" * 8, algorithms=["HS256"])
except jwt.InvalidTokenError as e:
    print(type(e).__name__)
print(len(t.split(".")), h[:2])
```

**Answer**:
```
a
a
InvalidSignatureError
3 ey
```
Verification needs the correct key, but anyone can read the payload without a key, because a JWT is signed, not encrypted. The header and payload are base64url JSON, and JSON starting with `{"` encodes to `ey`, so JWTs usually begin with `ey`.

---

## ⚫ Interview Questions + Answers

Q1: Is a JWT encrypted?
A1: No. A normal JWT (JWS) is only signed: anyone can read the payload, but nobody can change it without breaking the signature. Never store secrets in it. Encrypted tokens (JWE) are a different format.

Q2: HS256 vs RS256?
A2: HS256 uses one shared secret for signing and verifying (simple, single service). RS256 uses a private key to sign and a public key to verify (other services can verify without being able to create tokens). Use RS256 or ES256 across many services or when using an identity provider.

Q3: How do you log a user out or revoke a JWT?
A3: JWTs are stateless, so you cannot "delete" one. Use short expiry plus refresh tokens that you can revoke, or keep a blocklist (by `jti`) in Redis until the token expires, or rotate the signing key to kill all tokens.

Q4: Where should the client store it?
A4: In memory, or an `HttpOnly; Secure; SameSite` cookie. `localStorage` is readable by any injected script (XSS). With cookies, add CSRF protection.

Q5: What is the `alg: none` attack?
A5: A forged token with header `alg: none` and no signature. A naive library trusting the header accepts it. Always pass an explicit `algorithms=[...]` list to `decode`, as the example shows.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Stateless APIs, mobile apps, microservices
- You want to verify identity without a database lookup per request
- Short-lived access tokens with refresh flow

❌ Avoid when:
- You need instant revoke or "log out everywhere" with no extra infrastructure (use server-side sessions)
- A browser-only app is simpler with HttpOnly session cookies
- You are tempted to store sensitive data inside the token

---

## 📊 Visual Diagram

```
 Token:  eyJhbGciOi...  .  eyJzdWIiOiJhc2hhIn0  .  SflKxwRJSMeKKF2QT4f
          └─ header ──┘     └─── payload ─────┘     └── signature ──┘
          {"alg":"HS256"}   {"sub":"asha","exp":..} HMAC(header.payload, SECRET)

 verify:  recompute HMAC with SECRET  == signature ?   and   now < exp ?
              yes ─► trust claims          no ─► 401
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| JWT | Signed JSON token | signed JSON token |
| Claim | A field in the payload | payload का एक field |
| sub | Subject (user id) | user की पहचान |
| exp | Expiry time | समाप्ति का समय |
| Signature | Proof the token was not changed | token न बदले जाने का प्रमाण |
| Refresh token | Long-lived token to get new access tokens | नया access token लेने वाला लंबा token |
| HS256 / RS256 | Symmetric / asymmetric signing | एक key / जोड़ी key से signing |

---

## ⚡ 3-Line Summary
English: A JWT is a signed token with claims and an expiry that the server verifies without a session store. Always set `exp`, fix the `algorithms` list, keep secrets out of the payload, and use short access plus refresh tokens. A JWT is signed, not encrypted.
Hindi: JWT claims और expiry वाला signed token है जिसे server बिना session store के verify करता है। हमेशा `exp` लगाएँ, `algorithms` list तय रखें, payload में secret न रखें और छोटा access तथा refresh token इस्तेमाल करें। JWT signed होता है, encrypted नहीं।

---

## ➡️ Next Topic
**317. API Key Auth in FastAPI** — simple header-based keys for server-to-server access.
