---

# 482. Build Auth System (FastAPI+JWT)
# हिंदी में: Auth System बनाना (FastAPI + JWT)

Runnable solution with tests: [main.py](./main.py) (run: `python main.py`, verified on Python 3.13 with fastapi, PyJWT, pwdlib[argon2], python-multipart, httpx via TestClient).

---

## 🔵 Simple Definition (English)
An auth system checks who you are (authentication) and what you may do (authorization). With JWT, the server issues a signed token after login; the client sends it on each request in the `Authorization: Bearer` header, and the server verifies the signature instead of looking up a session.

## 🔵 सरल परिभाषा (Hindi)
Auth system जाँचता है कि आप कौन हैं (authentication) और आप क्या कर सकते हैं (authorization)। JWT में login के बाद server एक signed token देता है; client हर request में उसे `Authorization: Bearer` header में भेजता है, और server session खोजने की जगह signature verify करता है।

---

## 🔴 Problem it Solves
HTTP is stateless: the server forgets you after every request. Sending the password every time is dangerous. Storing passwords in plain text is a disaster if the DB leaks. JWT lets the server prove "this request comes from user X until time T" without server-side session storage, and password hashing (Argon2/bcrypt) protects stored credentials.

## 🔴 यह क्यों बना? (Hindi)
HTTP stateless है: हर request के बाद server आपको भूल जाता है। हर बार password भेजना खतरनाक है। Passwords को plain text में रखना DB leak होने पर आपदा है। JWT से server बिना session storage के साबित कर सकता है कि "यह request user X की है, समय T तक", और password hashing (Argon2/bcrypt) संग्रहीत credentials को बचाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → POST /register: hash the password (Argon2) and store only the hash
Step 2 → POST /login (form: username, password): verify hash with pwd.verify
Step 3 → On success create JWT: {"sub": username, "iat": now, "exp": now+15min}
Step 4 → Sign it with SECRET_KEY (HS256) and return {"access_token", "token_type": "bearer"}
Step 5 → Client sends  Authorization: Bearer <token>  on later requests
Step 6 → OAuth2PasswordBearer dependency extracts the token
Step 7 → current_user decodes: signature + exp are checked; bad -> 401
Step 8 → require_admin depends on current_user and checks role -> 403 if not allowed
Step 9 → Use the SAME error for unknown user and wrong password (no user enumeration)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → POST /register: password hash (Argon2) करो और सिर्फ hash रखो
Step 2 → POST /login (form: username, password): pwd.verify से hash जाँचो
Step 3 → सफल होने पर JWT बनाओ: {"sub": username, "iat": now, "exp": now+15min}
Step 4 → SECRET_KEY (HS256) से sign करो और {"access_token", "token_type": "bearer"} लौटाओ
Step 5 → Client आगे की requests में  Authorization: Bearer <token>  भेजता है
Step 6 → OAuth2PasswordBearer dependency token निकालती है
Step 7 → current_user decode करता है: signature और exp जाँचे जाते हैं; गलत हो तो 401
Step 8 → require_admin, current_user पर निर्भर है और role देखता है -> अनुमति न हो तो 403
Step 9 → अज्ञात user और गलत password दोनों पर एक ही error दो (user enumeration रोकने के लिए)
```

---

## 🟡 Real World Example
A Razorpay-style merchant dashboard: merchants log in, receive a 15-minute access token, and every dashboard API call carries it. Admin-only endpoints (refund override, user list) check the role claim. Mobile apps keep a long-lived refresh token (in secure storage) to get new access tokens without asking for the password again.

## 🟡 Real Example Hindi mein
Razorpay जैसा merchant dashboard: merchants login करते हैं, 15 मिनट का access token पाते हैं, और dashboard की हर API call उसे साथ ले जाती है। Admin-only endpoints (refund override, user list) role claim जाँचते हैं। Mobile apps लंबे समय वाला refresh token (secure storage में) रखते हैं ताकि password दोबारा पूछे बिना नए access tokens मिलें।

---

## 💻 Code Example — Basic
```python
# Basic: hash a password, create and verify a JWT
import jwt                                     # PyJWT
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash                # modern hashing library

SECRET: str = "dev-only-change-me-32-bytes-minimum!!"   # load from env in production
pwd = PasswordHash.recommended()               # Argon2id with safe defaults

stored: str = pwd.hash("s3cretpass")           # store this, never the password
print(stored.startswith("$argon2id$"))         # a salted Argon2id hash
print(pwd.verify("s3cretpass", stored), pwd.verify("wrong", stored))   # check attempts

now = datetime.now(timezone.utc)               # current UTC time
token: str = jwt.encode({"sub": "bob", "exp": now + timedelta(minutes=15)}, SECRET, algorithm="HS256")
data = jwt.decode(token, SECRET, algorithms=["HS256"])   # verifies signature and expiry
print(data["sub"])                             # the user

try:
    jwt.decode(token, "other-secret-other-secret-other-1", algorithms=["HS256"])
except jwt.InvalidSignatureError:              # wrong key -> forged/modified token
    print("invalid signature")

# Output:
# True
# True False
# bob
# invalid signature
```

## 💻 Code Example — Advanced
```python
# Production style: register, login, protected route, role check
# (the complete file including expired/tampered token tests is main.py)
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from pydantic import BaseModel, Field

SECRET_KEY = os.getenv("JWT_SECRET", "dev-only-change-me-32-bytes-minimum!!")   # env var in prod
pwd = PasswordHash.recommended()
oauth2 = OAuth2PasswordBearer(tokenUrl="/login")   # reads the Bearer token
app = FastAPI()
USERS: dict[str, dict[str, str]] = {}          # use a database in production


class Register(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8)        # reject weak/short passwords


class UserOut(BaseModel):
    username: str                              # never include the hash here
    role: str


def create_token(sub: str, minutes: int = 15) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": sub, "iat": now, "exp": now + timedelta(minutes=minutes)},
                      SECRET_KEY, algorithm="HS256")


def current_user(token: Annotated[str, Depends(oauth2)]) -> UserOut:
    err = HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token",
                        headers={"WWW-Authenticate": "Bearer"})
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])   # pin the algorithm list
    except jwt.PyJWTError:
        raise err                              # bad signature / expired / malformed
    user = USERS.get(data.get("sub", ""))
    if user is None:
        raise err                              # token valid but user deleted
    return UserOut(username=data["sub"], role=user["role"])


def require_admin(user: Annotated[UserOut, Depends(current_user)]) -> UserOut:
    if user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admins only")   # authenticated but not allowed
    return user


@app.post("/register", response_model=UserOut, status_code=201)
def register(body: Register) -> UserOut:
    if body.username in USERS:
        raise HTTPException(409, "Username taken")
    role = "admin" if not USERS else "user"    # demo rule: first user becomes admin
    USERS[body.username] = {"hash": pwd.hash(body.password), "role": role}
    return UserOut(username=body.username, role=role)


@app.post("/login")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict[str, str]:
    user = USERS.get(form.username)
    if user is None or not pwd.verify(form.password, user["hash"]):   # same error for both cases
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect username or password")
    return {"access_token": create_token(form.username), "token_type": "bearer"}


@app.get("/admin/stats")
def stats(_: Annotated[UserOut, Depends(require_admin)]) -> dict[str, int]:
    return {"users": len(USERS)}


c = TestClient(app)
c.post("/register", json={"username": "root", "password": "supersecret"})   # becomes admin
c.post("/register", json={"username": "bob", "password": "password123"})    # normal user
print(c.get("/admin/stats").status_code)       # no token
tok = c.post("/login", data={"username": "bob", "password": "password123"}).json()["access_token"]
print(c.get("/admin/stats", headers={"Authorization": f"Bearer {tok}"}).status_code)   # wrong role
atok = c.post("/login", data={"username": "root", "password": "supersecret"}).json()["access_token"]
print(c.get("/admin/stats", headers={"Authorization": f"Bearer {atok}"}).json())

# Output:
# 401
# 403
# {'users': 2}
```

---

## 🟠 JavaScript vs Python Comparison
Same flow in Node: `bcrypt`/`argon2` to hash, `jsonwebtoken` to sign/verify, an Express middleware to check the header. In FastAPI the "middleware" is a dependency, and the OpenAPI docs get an Authorize button automatically.

```python
# Python way
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```
```javascript
// JavaScript way
const payload = jwt.verify(token, SECRET_KEY, { algorithms: ["HS256"] });
// Express: app.get("/me", authMiddleware, (req, res) => res.json(req.user));
```

---

## 🟠 FastAPI Connection
`OAuth2PasswordBearer` + `Depends` is the official FastAPI security pattern. Dependencies compose: `require_admin` depends on `current_user`, which depends on `oauth2`. Any route adds `Depends(current_user)` to become protected, and the `/docs` page gets a lock icon and login dialog. `OAuth2PasswordRequestForm` needs `python-multipart` installed because login uses form data.

```python
# Protect a whole router at once
from fastapi import APIRouter
admin = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: storing plain or fast-hashed (MD5/SHA256) passwords.
✅ Correct: slow, salted hashes: Argon2id or bcrypt.

```python
# Wrong
db["pw"] = hashlib.sha256(password.encode()).hexdigest()
# Right
db["pw"] = pwd.hash(password)      # Argon2id with per-password salt
```

❌ Mistake 2: `jwt.decode(token, key)` without `algorithms=[...]`, or hard-coding the secret in source.
✅ Correct: always pass an explicit algorithm list; load the secret from an environment variable/secret manager.

❌ Mistake 3: putting sensitive data in the JWT payload (it is only encoded, not encrypted) or giving tokens a huge/no expiry.
✅ Correct: store only `sub`/role; short-lived access tokens (5-15 min) + refresh tokens that can be revoked.

---

## 🧠 Tricky Interview Question
```python
import base64, json
payload = {"sub": "bob", "role": "user"}
part = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
print(json.loads(base64.urlsafe_b64decode(part + "==")))
```
Answer: `{'sub': 'bob', 'role': 'user'}`. Anyone can read a JWT payload by base64-decoding it; no key needed. The signature only prevents tampering, not reading. Changing `role` to `admin` would break the signature and be rejected, but secrets must never be put inside a JWT.

---

## ⚫ Interview Questions + Answers

Q1: Authentication vs authorization?
A1: Authentication = who are you (401 when failing). Authorization = what may you do (403 when failing).

Q2: JWT vs server sessions?
A2: JWT is stateless and scales across servers, but cannot be revoked easily before expiry (use short expiry, refresh tokens, or a denylist). Sessions are revocable but need shared storage (Redis).

Q3: What are the three parts of a JWT?
A3: Header (algorithm), payload (claims such as `sub`, `exp`), signature (HMAC/RSA over header.payload). Format: `xxxxx.yyyyy.zzzzz`.

Q4: Why a refresh token?
A4: Keeps access tokens short-lived. A stolen access token expires quickly; the refresh token is stored more safely, rotated, and revocable server-side.

Q5: How do you prevent user enumeration and brute force?
A5: Same error message for bad username and bad password, rate-limit login attempts, lockout/backoff, and constant-time comparison (done inside `verify`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- APIs consumed by SPAs, mobile apps and other services
- Several backend instances without shared session storage
- Short-lived access with role/scope claims

❌ Avoid when:
- You need instant logout/revocation everywhere (prefer server sessions)
- A classic server-rendered site fits (cookies + sessions are simpler)
- You can delegate to a provider (Auth0, Cognito, Keycloak, Google login)

---

## 📊 Visual Diagram
```
 Client                              FastAPI
   | POST /login (user, pass)           |
   |----------------------------------->| verify Argon2 hash
   |<---- {access_token: JWT} ----------| sign(exp = now + 15 min)
   |                                    |
   | GET /me  Authorization: Bearer JWT |
   |----------------------------------->| decode: signature OK? exp OK?
   |                                    |   no  -> 401
   |                                    |   yes -> load user -> role check
   |<---- 200 {"username": "bob"} ------|   wrong role -> 403
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Authentication | Proving identity | पहचान सिद्ध करना |
| Authorization | Checking permissions | अनुमति जाँचना |
| JWT | Signed token with claims | हस्ताक्षरित token |
| Claim (`sub`, `exp`) | Fields inside the token | token के अंदर के fields |
| Hashing | One-way password transform | एक-तरफ़ा password रूपांतरण |
| Bearer token | Token sent in Authorization header | header में भेजा जाने वाला token |

---

## ⚡ 3-Line Summary
English: Hash passwords with Argon2, issue a short-lived signed JWT at login, verify it on each request.
English: Use `OAuth2PasswordBearer` and chained `Depends` for 401 (not logged in) and 403 (not allowed).
English: Keep secrets in env vars, pin the algorithm, never put secrets inside the token.

Hindi: Passwords को Argon2 से hash करो, login पर छोटी उम्र का signed JWT दो, हर request पर verify करो।
Hindi: `OAuth2PasswordBearer` और chained `Depends` से 401 (login नहीं) और 403 (अनुमति नहीं) संभालो।
Hindi: Secrets env vars में रखो, algorithm तय करो, token के अंदर secret कभी मत रखो।

---

## ➡️ Next Topic
**483. Build File Upload API** — accept files safely: size limits, type checks, streaming to disk.

---
