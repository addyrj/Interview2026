---

# Q238. OAuth2 password flow
# Category: FASTAPI + WEB QUESTIONS
# Difficulty: ⭐⭐⭐

---

## ❓ Question
Implement the OAuth2 password flow in FastAPI: `POST /token` takes form data (`username`, `password`) and returns a signed JWT `access_token`; `GET /me` is protected using `OAuth2PasswordBearer`. Handle wrong password, missing/invalid/expired tokens.

---

## 💡 Quick Concept (2 lines only)
`OAuth2PasswordBearer` extracts `Authorization: Bearer <token>` and makes Swagger show a Login button. `/token` verifies credentials (form-encoded!) and returns a JWT; a dependency decodes it for protected routes.
हिंदी: `/token` पर form से login होता है और JWT मिलता है; protected route में `Bearer` token decode होकर user मिलता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import hashlib  # password hashing (stdlib)
import hmac  # constant-time compare
from datetime import datetime, timedelta, timezone  # token expiry
from typing import Annotated  # Depends typing
import jwt  # PyJWT: pip install pyjwt
from fastapi import FastAPI, Depends, HTTPException, status  # web
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  # OAuth2 helpers
from fastapi.testclient import TestClient  # client

SECRET = "change-me-use-env-var-and-32+bytes-long"  # signing key (never hardcode in prod)
ALGO = "HS256"  # signing algorithm

def hash_pw(pw: str) -> str:  # slow salted hash (use argon2/bcrypt in prod)
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), b"static-salt-demo", 10_000).hex()  # demo only

FAKE_USERS = {"ann": {"username": "ann", "hash": hash_pw("secret")}}  # fake db

app = FastAPI()  # app
oauth2 = OAuth2PasswordBearer(tokenUrl="token")  # Step 1: tells Swagger where to log in; extracts Bearer token

@app.post("/token")  # Step 2: login endpoint
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict[str, str]:  # form-encoded body
    user = FAKE_USERS.get(form.username)  # find user
    ok = user is not None and hmac.compare_digest(user["hash"], hash_pw(form.password))  # verify password
    if not ok:  # wrong creds
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "bad credentials", headers={"WWW-Authenticate": "Bearer"})  # 401
    exp = datetime.now(timezone.utc) + timedelta(minutes=30)  # expiry time
    token = jwt.encode({"sub": form.username, "exp": exp}, SECRET, algorithm=ALGO)  # Step 3: sign JWT
    return {"access_token": token, "token_type": "bearer"}  # OAuth2 response shape

async def current_user(token: Annotated[str, Depends(oauth2)]) -> dict:  # Step 4: protect routes
    try:  # decode may fail
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])  # checks signature + exp
    except jwt.PyJWTError:  # bad/expired token
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token", headers={"WWW-Authenticate": "Bearer"})  # 401
    user = FAKE_USERS.get(payload.get("sub", ""))  # load user
    if user is None:  # deleted user
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "unknown user")  # 401
    return user  # inject

@app.get("/me")  # protected route
async def me(user: Annotated[dict, Depends(current_user)]) -> dict[str, str]:  # needs token
    return {"username": user["username"]}  # body

# ============================================
# TEST CASES
# ============================================
client = TestClient(app)  # client
print(client.get("/me").status_code)  # Expected: 401 (no token; Bearer header missing)
print(client.post("/token", data={"username": "ann", "password": "wrong"}).status_code)  # Expected: 401
r = client.post("/token", data={"username": "ann", "password": "secret"})  # correct login (form data, NOT json)
print(r.status_code, r.json()["token_type"])  # Expected: 200 bearer
tok = r.json()["access_token"]  # grab token
print(client.get("/me", headers={"Authorization": f"Bearer {tok}"}).json())  # Expected: {'username': 'ann'}
print(client.get("/me", headers={"Authorization": "Bearer garbage"}).json())  # Expected: {'detail': 'invalid token'}
print(client.post("/token", json={"username": "ann", "password": "secret"}).status_code)  # Expected: 422 (JSON not accepted)
```

---

## 🔍 Why This Works (3 lines max)
The login form must be `application/x-www-form-urlencoded` (spec requirement) — JSON gives 422. `jwt.decode` checks signature AND `exp`, so expired or tampered tokens raise `PyJWTError` -> 401 with `WWW-Authenticate: Bearer`. Compare hashes with `hmac.compare_digest`.
हिंदी: Login form-encoded होना चाहिए (JSON नहीं); `jwt.decode` signature और expiry दोनों जाँचता है।

---

## ⚡ Alternative Solution
```python
# (same file as above — reuses its imports/names)
# ---- Alternative: scopes-free, expired token check ----
old = jwt.encode({"sub": "ann", "exp": datetime.now(timezone.utc) - timedelta(seconds=5)}, SECRET, algorithm=ALGO)  # already expired
print(client.get("/me", headers={"Authorization": f"Bearer {old}"}).status_code)  # Expected: 401
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: storing/comparing plain-text passwords, or comparing with ==
if user["password"] == form.password: ...
# ✅ Correct: slow salted hash (argon2/bcrypt) + hmac.compare_digest

# ❌ Wrong: jwt.decode(token, SECRET)  # no algorithms=[...] -> algorithm confusion risk
# ✅ Correct: jwt.decode(token, SECRET, algorithms=["HS256"])

# ❌ Wrong: hardcoded SECRET in code, tokens with no "exp"  ->  use env var + short expiry
```

---

## 🎯 Interview Tip (1 line)
Say: "Password flow = form login -> signed short-lived JWT -> Bearer dependency; hash passwords properly, pin the algorithm, and prefer authorization-code+PKCE for third-party apps."

---

## 🔗 Related Questions
→ Q224 (JWT auth) | Q222 (dependencies) | Q231 (CORS) | Q232 (error handlers)
