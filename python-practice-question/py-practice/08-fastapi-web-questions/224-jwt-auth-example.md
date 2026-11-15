---

# Q224. JWT auth example
# Category: FASTAPI + WEB QUESTIONS
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement JWT authentication in FastAPI: `/login` returns a signed token, `/me` requires `Authorization: Bearer <token>`, and expired or tampered tokens give 401. Use PyJWT (`pip install pyjwt`).

```python
curl -H 'Authorization: Bearer <token>' /me
```

---

## 💡 Quick Concept (2 lines only)
A JWT is `header.payload.signature`: the server signs claims (`sub`, `exp`) with a secret; on each request it verifies the signature and expiry - no session store needed.
हिंदी: JWT = header.payload.signature; server secret से sign करता है और हर request पर verify करता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

import hmac                                       # constant-time compare
from datetime import datetime, timedelta, timezone  # token expiry
from typing import Annotated                      # Annotated
import jwt                                        # PyJWT
from fastapi import Depends, FastAPI, HTTPException  # web
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer  # Bearer header parser
from fastapi.testclient import TestClient         # test client
from pydantic import BaseModel                    # login schema

SECRET = "change-me-use-env-var-at-least-32-bytes!"  # signing key (load from env in real apps)
ALGO = "HS256"                                    # HMAC-SHA256
USERS = {"aditya": "pass123"}                     # demo only; real apps store password HASHES

app = FastAPI()                                   # create app
bearer = HTTPBearer()                             # reads "Authorization: Bearer <token>"


class Login(BaseModel):
    username: str                                 # login name
    password: str                                 # login password


def make_token(sub: str, minutes: int = 15) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=minutes)  # expiry time
    return jwt.encode({"sub": sub, "exp": exp}, SECRET, algorithm=ALGO)  # sign payload


def current_user(cred: Annotated[HTTPAuthorizationCredentials, Depends(bearer)]) -> str:
    try:
        payload = jwt.decode(cred.credentials, SECRET, algorithms=[ALGO])  # verify sig + exp
    except jwt.ExpiredSignatureError:             # past `exp`
        raise HTTPException(401, "token expired") # client should re-login
    except jwt.InvalidTokenError:                 # tampered / malformed
        raise HTTPException(401, "invalid token") # reject
    return payload["sub"]                         # username from the token


@app.post("/login")
def login(body: Login) -> dict:
    expected = USERS.get(body.username, "")       # stored password (or empty)
    if not expected or not hmac.compare_digest(expected, body.password):  # timing-safe check
        raise HTTPException(401, "bad credentials")  # same message for both failures
    return {"access_token": make_token(body.username), "token_type": "bearer"}


@app.get("/me")
def me(user: Annotated[str, Depends(current_user)]) -> dict:
    return {"user": user}                         # only reached with a valid token


# ---------- TEST CASES ----------
c = TestClient(app)                               # test client
print(c.post("/login", json={"username": "aditya", "password": "x"}).status_code)  # 401
tok = c.post("/login", json={"username": "aditya", "password": "pass123"}).json()["access_token"]
print(c.get("/me", headers={"Authorization": f"Bearer {tok}"}).json())  # authorised
print(c.get("/me").status_code)                   # no header -> 401 (3.13 / current FastAPI)
old = make_token("aditya", minutes=-1)            # already expired
print(c.get("/me", headers={"Authorization": f"Bearer {old}"}).json())  # expired
print(c.get("/me", headers={"Authorization": f"Bearer {tok}x"}).json()) # tampered

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# 401
# {'user': 'aditya'}
# 401
# {'detail': 'token expired'}
# {'detail': 'invalid token'}
```

---

## 🔍 Why This Works (3 lines max)
`HTTPBearer` extracts the token; `jwt.decode(..., algorithms=[ALGO])` checks signature and `exp`. `compare_digest` avoids timing attacks. The payload is only base64-encoded, NOT encrypted (see alternative), so never put secrets in it. A missing header gives 401 on current FastAPI (older versions returned 403).
हिंदी: Payload encrypt नहीं होता, सिर्फ signed होता है; secret env var में रखो और algorithms हमेशा specify करो।

---

## ⚡ Alternative Solution
```python
import jwt                                        # PyJWT

SECRET = "change-me-use-env-var-at-least-32-bytes!"  # signing key

token = jwt.encode({"sub": "aditya", "role": "admin"}, SECRET, algorithm="HS256")  # create
header, payload, signature = token.split(".")     # 3 base64url parts
print(len(token.split(".")))                      # 3

print(jwt.decode(token, SECRET, algorithms=["HS256"]))  # verified payload
print(jwt.decode(token, options={"verify_signature": False}))  # readable WITHOUT key -> not encrypted!

try:
    jwt.decode(token, "wrong-key-wrong-key-wrong-key-123456", algorithms=["HS256"])  # wrong key
except jwt.InvalidSignatureError as e:
    print("InvalidSignatureError:", e)            # signature mismatch

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# 3
# {'sub': 'aditya', 'role': 'admin'}
# {'sub': 'aditya', 'role': 'admin'}
# InvalidSignatureError: Signature verification failed
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: not pinning algorithms / skipping verification
jwt.decode(token, SECRET)                                   # PyJWT requires algorithms=[...]
jwt.decode(token, options={"verify_signature": False})      # trusts forged tokens!

# ❌ Wrong: secrets or plain passwords in the payload, no `exp`, hard-coded SECRET in git
# ✅ Correct: algorithms=["HS256"], short exp, secret from env, password hashes (argon2/bcrypt)
```

---

## 🎯 Interview Tip (1 line)
Say: "JWT is stateless but signed, not encrypted: short expiry + refresh tokens, pinned algorithm, secret from env, hashed passwords."

---

## 🔗 Related Questions
→ Q222 (dependency injection) | Q238 (OAuth2 password flow) | Q225 (middleware) | Q236 (TestClient)
