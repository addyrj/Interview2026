---

# 315. OAuth2 in FastAPI
# हिंदी में: FastAPI में OAuth2 (Password Flow और Bearer Token)

---

## 🔵 Simple Definition (English)
OAuth2 is a standard for sending credentials once and then using an access token for later requests. In FastAPI the common setup is the "password flow": the client posts `username` and `password` as form data to `/token`, receives a bearer token, and sends `Authorization: Bearer <token>` afterwards. `OAuth2PasswordBearer` and `OAuth2PasswordRequestForm` do the plumbing.

## 🔵 सरल परिभाषा (Hindi)
OAuth2 एक standard है जिसमें credentials एक बार भेजकर बाद की requests में access token इस्तेमाल होता है। FastAPI में आम तरीका "password flow" है: client `/token` पर `username` और `password` form data में भेजता है, bearer token पाता है, और आगे `Authorization: Bearer <token>` भेजता है। `OAuth2PasswordBearer` और `OAuth2PasswordRequestForm` यह काम संभालते हैं।

---

## 🔴 Problem it Solves
Sending the password with every request is dangerous and slow. Every team also invented its own login format, so tools could not work with them. OAuth2 gives a known pattern: authenticate once, get a short-lived token, and send only the token. Swagger UI understands it too and shows an Authorize button.

## 🔴 यह क्यों बना? (Hindi)
हर request के साथ password भेजना खतरनाक और धीमा है। हर team अपना अलग login format बना लेती थी इसलिए tools उनके साथ नहीं चल पाते थे। OAuth2 एक जाना-पहचाना तरीका देता है: एक बार login, छोटी उम्र का token, और फिर सिर्फ़ token। Swagger UI भी इसे समझता है और Authorize button दिखाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client: POST /token  (form: username, password)
Step 2 → Server checks the password; if right, creates an access token
Step 3 → Server replies {"access_token": "...", "token_type": "bearer"}
Step 4 → Client stores the token and sends: Authorization: Bearer <token>
Step 5 → OAuth2PasswordBearer dependency extracts the token string
Step 6 → get_current_user verifies it and loads the user; bad token → 401
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Client: POST /token  (form: username, password)
Step 2 → Server password जाँचता है; सही हो तो access token बनाता है
Step 3 → Server जवाब देता है {"access_token": "...", "token_type": "bearer"}
Step 4 → Client token रखता है और भेजता है: Authorization: Bearer <token>
Step 5 → OAuth2PasswordBearer dependency token string निकालती है
Step 6 → get_current_user उसे verify करके user लाता है; गलत token पर 401
```

---

## 🟡 Real World Example
A Swiggy partner dashboard: the restaurant owner logs in with email and password at `/token`, receives a token valid for 30 minutes, and every later call (`/orders`, `/menu`) carries it. Big providers (Google, GitHub "Login with ...") use other OAuth2 flows (authorization code), where your app never sees the user's password.

## 🟡 Real Example Hindi mein
Swiggy partner dashboard में restaurant owner `/token` पर email और password से login करता है, 30 मिनट वाला token पाता है, और बाद की हर call (`/orders`, `/menu`) में वही token जाता है। Google, GitHub जैसे "Login with ..." बड़े providers दूसरे OAuth2 flows (authorization code) इस्तेमाल करते हैं जहाँ आपके app को user का password कभी दिखता ही नहीं।

---

## 💻 Code Example — Basic
```python
# Basic OAuth2 password flow with fake tokens - run directly (pip install fastapi httpx python-multipart)
from typing import Annotated  # type tools
from fastapi import Depends, FastAPI, HTTPException, status  # core
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  # OAuth2 helpers
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # create app
oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="token")  # tells Swagger where to log in

FAKE_USERS: dict[str, dict] = {"asha": {"username": "asha", "password": "pw1", "full_name": "Asha Rao"}}  # demo DB (plain text ONLY for demo)


@app.post("/token")  # login endpoint (must accept FORM data per spec)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:  # reads username and password
    user: dict | None = FAKE_USERS.get(form.username)  # find the user
    if user is None or user["password"] != form.password:  # wrong credentials
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")  # 401
    return {"access_token": f"token-{user['username']}", "token_type": "bearer"}  # fake token


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:  # extracts "Bearer xyz" -> "xyz"
    username: str = token.removeprefix("token-")  # fake decode
    user: dict | None = FAKE_USERS.get(username)  # load user
    if user is None:  # invalid token
        raise HTTPException(  # 401 with the standard header
            status_code=status.HTTP_401_UNAUTHORIZED,  # unauthenticated
            detail="Invalid token",  # message
            headers={"WWW-Authenticate": "Bearer"},  # tells client the scheme
        )
    return user  # valid


@app.get("/users/me")  # protected endpoint
def me(user: Annotated[dict, Depends(get_current_user)]) -> dict:  # injected user
    return {"username": user["username"], "full_name": user["full_name"]}  # no password


c: TestClient = TestClient(app)  # demo client
print(c.post("/token", data={"username": "asha", "password": "bad"}).status_code)  # wrong password
# Output: 401
tok: dict = c.post("/token", data={"username": "asha", "password": "pw1"}).json()  # correct login
print(tok)  # token response
# Output: {'access_token': 'token-asha', 'token_type': 'bearer'}
print(c.get("/users/me", headers={"Authorization": f"Bearer {tok['access_token']}"}).json())  # use the token
# Output: {'username': 'asha', 'full_name': 'Asha Rao'}
print(c.get("/users/me").status_code, c.get("/users/me").json())  # no token at all
# Output: 401 {'detail': 'Not authenticated'}
```

## 💻 Code Example — Advanced
```python
# Production style: scopes, OpenAPI security scheme, 401 vs 403, secure password check (stdlib only)
import hashlib  # password hashing from the standard library
import hmac  # constant-time comparison
import os  # random salt
from typing import Annotated  # metadata
from fastapi import Depends, FastAPI, HTTPException, Security, status  # core
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes  # scopes support
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # app
oauth2: OAuth2PasswordBearer = OAuth2PasswordBearer(  # scheme with scopes
    tokenUrl="token",  # login URL
    scopes={"orders:read": "Read orders", "orders:write": "Create orders"},  # shown in Swagger
)


def hash_password(password: str, salt: bytes | None = None) -> str:  # never store plain passwords
    salt = salt or os.urandom(16)  # random salt per user
    digest: bytes = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)  # slow, memory-hard hash
    return salt.hex() + "$" + digest.hex()  # store salt + hash


def verify_password(password: str, stored: str) -> bool:  # check a login attempt
    salt_hex, _ = stored.split("$")  # split salt
    candidate: str = hash_password(password, bytes.fromhex(salt_hex))  # hash again with same salt
    return hmac.compare_digest(candidate, stored)  # timing-safe equal


DB: dict[str, dict] = {  # users with granted scopes
    "asha": {"hash": hash_password("pw1"), "scopes": ["orders:read"]},  # read-only
    "ravi": {"hash": hash_password("pw2"), "scopes": ["orders:read", "orders:write"]},  # read+write
}


@app.post("/token")  # login with scopes
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:  # form carries requested scopes
    user: dict | None = DB.get(form.username)  # find user
    if user is None or not verify_password(form.password, user["hash"]):  # check
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect username or password")  # same message for both cases
    granted: list[str] = [s for s in form.scopes if s in user["scopes"]]  # give only what is allowed
    return {"access_token": f"{form.username}|{' '.join(granted)}", "token_type": "bearer"}  # fake token


def current_user(security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2)]) -> str:  # checks scopes
    name, _, scope_str = token.partition("|")  # fake decode
    have: set[str] = set(scope_str.split())  # scopes inside the token
    for needed in security_scopes.scopes:  # scopes the endpoint requires
        if needed not in have:  # missing
            raise HTTPException(  # authenticated but not permitted
                status_code=status.HTTP_403_FORBIDDEN,  # 403
                detail=f"Missing scope: {needed}",  # explain
                headers={"WWW-Authenticate": f'Bearer scope="{security_scopes.scope_str}"'},  # standard
            )
    return name  # user name


@app.get("/orders")  # needs read
def list_orders(user: Annotated[str, Security(current_user, scopes=["orders:read"])]) -> dict:  # Security = Depends + scopes
    return {"orders": [], "by": user}  # response


@app.post("/orders")  # needs write
def create_order(user: Annotated[str, Security(current_user, scopes=["orders:write"])]) -> dict:  # write scope
    return {"created_by": user}  # response


c: TestClient = TestClient(app)  # demo client
asha: str = c.post("/token", data={"username": "asha", "password": "pw1", "scope": "orders:read orders:write"}).json()["access_token"]  # asks for 2, gets 1
print(asha)  # only read was granted
# Output: asha|orders:read
print(c.get("/orders", headers={"Authorization": f"Bearer {asha}"}).json())  # allowed
# Output: {'orders': [], 'by': 'asha'}
r = c.post("/orders", headers={"Authorization": f"Bearer {asha}"})  # not allowed
print(r.status_code, r.json())  # 403 with reason
# Output: 403 {'detail': 'Missing scope: orders:write'}
print(c.post("/token", data={"username": "asha", "password": "nope"}).status_code)  # wrong password
# Output: 401
sec = app.openapi()["components"]["securitySchemes"]["OAuth2PasswordBearer"]["flows"]["password"]  # what Swagger reads
print(sec["tokenUrl"], sorted(sec["scopes"]))  # login URL and scopes
# Output: token ['orders:read', 'orders:write']
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (FastAPI): token extraction is a dependency
oauth2 = OAuth2PasswordBearer(tokenUrl="token")
def me(token: str = Depends(oauth2)): ...
```
```javascript
// JavaScript (Express + passport-jwt)
passport.use(new JwtStrategy({ jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(), secretOrKey: SECRET },
  (payload, done) => done(null, payload)));
app.get("/me", passport.authenticate("jwt", { session: false }), (req, res) => res.json(req.user));

// Browser client
const body = new URLSearchParams({ username, password });   // form-encoded, not JSON
const { access_token } = await (await fetch("/token", { method: "POST", body })).json();
await fetch("/users/me", { headers: { Authorization: `Bearer ${access_token}` } });
```

Key difference: login must be sent as form data (`URLSearchParams`), not JSON, to match the OAuth2 spec. FastAPI also registers the scheme in OpenAPI, so Swagger gets an Authorize button without extra code, while Express needs passport plus manual docs.

---

## 🟠 FastAPI Connection
`OAuth2PasswordBearer(tokenUrl="token")` is only an extractor and an OpenAPI marker: it returns the token string or raises 401 `Not authenticated` if the header is missing. It does NOT verify the token. Verification is your code in `get_current_user` (next topic: JWT). `OAuth2PasswordRequestForm` needs `python-multipart`.

```python
# FastAPI: what OAuth2PasswordBearer really does
from fastapi import Depends, FastAPI  # core
from fastapi.security import OAuth2PasswordBearer  # extractor
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # app
oauth2: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="token")  # extractor


@app.get("/raw")  # echo the extracted token
def raw(token: str = Depends(oauth2)) -> dict:  # no verification here
    return {"token": token}  # whatever the client sent


c: TestClient = TestClient(app)  # client
print(c.get("/raw", headers={"Authorization": "Bearer anything"}).json())  # accepted blindly
# Output: {'token': 'anything'}
print(c.get("/raw", headers={"Authorization": "Basic abc"}).status_code)  # wrong scheme
# Output: 401
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Thinking `OAuth2PasswordBearer` validates the token
```python
# Wrong - any string is accepted, the route is NOT protected
def me(token: str = Depends(oauth2)): return {"ok": True}

# Correct - verify signature/expiry and load the user
def me(user = Depends(get_current_user)): ...
```

❌ Mistake 2: Sending login as JSON
```python
# Wrong - the OAuth2 spec uses form fields, FastAPI returns 422
# client: fetch("/token", { body: JSON.stringify({username, password}) })

# Correct - application/x-www-form-urlencoded (data=... in requests/httpx)
```

❌ Mistake 3: Storing plain or fast-hashed passwords
```python
# Wrong
user["password"] == form.password          # plain text
hashlib.md5(pw.encode()).hexdigest()       # fast hash

# Correct - slow salted hash (bcrypt, argon2, scrypt) and hmac.compare_digest
```

---

## 🧠 Tricky Interview Question

**Q**: What status codes come out?

```python
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.testclient import TestClient

app = FastAPI()
oauth2 = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/p")
def p(t: str = Depends(oauth2)):
    return {"t": t}

c = TestClient(app)
print(c.get("/p").status_code)
print(c.get("/p", headers={"Authorization": "Bearer"}).status_code)
print(c.get("/p", headers={"Authorization": "bearer xyz"}).status_code)
print(c.get("/p", headers={"Authorization": "Bearer xyz"}).status_code)
```

**Answer**:
```
401
200
200
200
```
No header gives 401 "Not authenticated". A header that is just `Bearer` gives 200 in the tested version (FastAPI 0.162): the extractor returns an empty string as the token. So your own verification must reject empty tokens. The scheme name is case-insensitive (`bearer` works), and any non-empty token passes this dependency because verification is not its job. A wrong scheme like `Basic abc` gives 401. (Edge-case behaviour may differ between FastAPI versions.)

---

## ⚫ Interview Questions + Answers

Q1: What is the OAuth2 password flow and when should you avoid it?
A1: The client sends the user's username and password directly to your API to get a token. It is fine for your own first-party app, but not for third-party apps (they should use authorization code flow so they never see passwords). The OAuth 2.1 draft removes it.

Q2: What does `tokenUrl` do?
A2: It is only metadata for OpenAPI/Swagger so the Authorize dialog knows where to POST the login. FastAPI does not create that endpoint for you.

Q3: Why must login be a form, not JSON?
A3: The OAuth2 spec defines `application/x-www-form-urlencoded` with fields `username`, `password`, optional `scope`. `OAuth2PasswordRequestForm` follows it, so generic OAuth2 clients work.

Q4: 401 vs 403 in OAuth2?
A4: 401 means missing or invalid token (include `WWW-Authenticate: Bearer`). 403 means the token is valid but lacks permission (scope or role).

Q5: What are scopes?
A5: Permission strings stored in the token (`orders:read`). Endpoints declare required scopes with `Security(dep, scopes=[...])`, and `SecurityScopes` lets the dependency check them.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- First-party web/mobile app that logs in with username and password
- You want Swagger's Authorize button
- Fine-grained permissions with scopes

❌ Avoid when:
- Third-party access (use authorization code + PKCE with an identity provider like Auth0/Keycloak)
- Simple service-to-service calls (an API key or mTLS is simpler)
- You would implement token crypto yourself (use a library)

---

## 📊 Visual Diagram

```
 Client                         FastAPI
   │ POST /token (form) ─────────► OAuth2PasswordRequestForm
   │                               verify password
   │ ◄── {access_token, bearer} ── create token
   │
   │ GET /orders
   │ Authorization: Bearer T ────► oauth2_scheme (extract "T")
   │                               get_current_user (verify T)
   │                               Security(scopes) (check permission)
   │ ◄── 200 / 401 / 403 ───────── endpoint
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OAuth2 | Standard for token-based access | token आधारित access का standard |
| Access token | Short-lived proof of login | login का छोटी उम्र का प्रमाण |
| Bearer | Whoever holds the token is trusted | जिसके पास token वही मान्य |
| Scope | Permission label in token | token में permission का label |
| Password flow | Send password to get token | password देकर token पाना |
| tokenUrl | Login URL for Swagger | Swagger के लिए login URL |
| Salt | Random data added before hashing | hash से पहले जोड़ा random data |

---

## ⚡ 3-Line Summary
English: OAuth2 password flow: log in once at `/token` with form data, then send `Authorization: Bearer <token>`. `OAuth2PasswordBearer` only extracts the token; you must verify it. Use scopes for permissions and slow salted hashes for passwords.
Hindi: OAuth2 password flow में `/token` पर form data से एक बार login करें, फिर `Authorization: Bearer <token>` भेजें। `OAuth2PasswordBearer` सिर्फ़ token निकालता है, verify आपको करना है। Permissions के लिए scopes और passwords के लिए धीमा salted hash इस्तेमाल करें।

---

## ➡️ Next Topic
**316. JWT Auth in FastAPI** — replace the fake token with a real signed, expiring JWT.
