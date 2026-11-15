---

# 310. Headers + Cookies
# हिंदी में: Headers और Cookies (request के साथ जाने वाली जानकारी)

---

## 🔵 Simple Definition (English)
Headers are key-value metadata sent with every HTTP request and response (`Authorization`, `User-Agent`, `Content-Type`). Cookies are small values the server asks the browser to store and send back automatically with each request. FastAPI reads them with `Header()` and `Cookie()` and sets them on a `Response`.

## 🔵 सरल परिभाषा (Hindi)
Headers हर HTTP request और response के साथ जाने वाली key-value जानकारी हैं (`Authorization`, `User-Agent`, `Content-Type`)। Cookies छोटे values हैं जिन्हें server browser से store करवाता है और browser हर request में अपने आप वापस भेजता है। FastAPI इन्हें `Header()` और `Cookie()` से पढ़ता है और `Response` पर set करता है।

---

## 🔴 Problem it Solves
HTTP is stateless: the server forgets you after each request. Query strings and bodies are the wrong place for tokens, language preferences, tracing ids or session ids. Headers carry request-level metadata, and cookies give the browser automatic memory (login session) without JavaScript code.

## 🔴 यह क्यों बना? (Hindi)
HTTP stateless है: हर request के बाद server आपको भूल जाता है। Token, भाषा की पसंद, tracing id या session id को query string या body में रखना सही नहीं है। Headers request की metadata ले जाते हैं और cookies browser को अपने आप याद रखने की क्षमता देती हैं (login session), बिना JavaScript के।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client sends headers: Authorization: Bearer abc, X-Request-ID: 42
Step 2 → FastAPI maps a function parameter Header() to a header name
Step 3 → user_agent -> "user-agent" (underscore turned into hyphen automatically)
Step 4 → Server sets a cookie: Set-Cookie: session=xyz; HttpOnly; Secure
Step 5 → Browser stores it and sends Cookie: session=xyz on every later request
Step 6 → Cookie(...) parameter reads it back
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Client headers भेजता है: Authorization: Bearer abc, X-Request-ID: 42
Step 2 → FastAPI function के Header() parameter को header के नाम से जोड़ता है
Step 3 → user_agent अपने आप "user-agent" बन जाता है (underscore से hyphen)
Step 4 → Server cookie set करता है: Set-Cookie: session=xyz; HttpOnly; Secure
Step 5 → Browser इसे रखता है और आगे हर request में Cookie: session=xyz भेजता है
Step 6 → Cookie(...) parameter इसे वापस पढ़ लेता है
```

---

## 🟡 Real World Example
Razorpay-style API: every call carries `Authorization: Bearer <key>` and an `X-Request-ID` for tracing logs. A web dashboard stores the login session in an `HttpOnly` cookie so JavaScript (and XSS attacks) cannot read it. An AI app reads `Accept-Language` to answer in Hindi, and sets a `Retry-After` header when rate limiting.

## 🟡 Real Example Hindi mein
Razorpay जैसी API में हर call में `Authorization: Bearer <key>` और logs trace करने के लिए `X-Request-ID` जाता है। Web dashboard login session को `HttpOnly` cookie में रखता है ताकि JavaScript (और XSS attack) उसे पढ़ न सके। AI app `Accept-Language` पढ़कर हिंदी में जवाब देता है और rate limit पर `Retry-After` header भेजता है।

---

## 💻 Code Example — Basic
```python
# Basic headers and cookies - run directly (pip install fastapi httpx)
from typing import Annotated, Optional  # type tools
from fastapi import Cookie, FastAPI, Header, Response  # helpers
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # create app


@app.get("/whoami")  # read a header and a cookie
def whoami(
    user_agent: Annotated[Optional[str], Header()] = None,  # reads header "user-agent"
    x_request_id: Annotated[Optional[str], Header()] = None,  # reads header "x-request-id"
    session: Annotated[Optional[str], Cookie()] = None,  # reads cookie named "session"
) -> dict:  # response body
    return {"ua": user_agent, "rid": x_request_id, "session": session}  # echo what we got


@app.post("/login")  # set a cookie and a header
def login(response: Response) -> dict:  # injected Response to modify
    response.set_cookie(key="session", value="abc123", httponly=True, max_age=3600, samesite="lax")  # cookie
    response.headers["X-Server"] = "demo"  # custom response header
    return {"ok": True}  # body


c: TestClient = TestClient(app)  # demo client
r = c.get("/whoami", headers={"User-Agent": "demo-agent", "X-Request-ID": "42"}, cookies={"session": "s1"})  # send them
print(r.json())  # values read correctly
# Output: {'ua': 'demo-agent', 'rid': '42', 'session': 's1'}
r2 = c.post("/login")  # server sets cookie
print(r2.headers["x-server"])  # custom header
# Output: demo
print(r2.headers["set-cookie"])  # raw Set-Cookie header
# Output: session=abc123; HttpOnly; Max-Age=3600; Path=/; SameSite=lax
print(c.cookies.get("session"))  # the test client stored the cookie, like a browser
# Output: abc123
```

## 💻 Code Example — Advanced
```python
# Production style: required header, duplicate headers, alias, cookie delete, response headers via dependency
from typing import Annotated  # metadata
from fastapi import Cookie, Depends, FastAPI, Header, HTTPException, Response, status  # core
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # app


def require_api_version(x_api_version: Annotated[str, Header()]) -> int:  # required header (no default)
    if x_api_version not in {"1", "2"}:  # only allow known versions
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unsupported API version")  # 400
    return int(x_api_version)  # convert to int


@app.get("/data")  # versioned endpoint
def data(
    version: Annotated[int, Depends(require_api_version)],  # header via dependency
    tags: Annotated[list[str], Header(alias="X-Tag")] = [],  # repeated header -> list
    token: Annotated[str | None, Header(alias="Authorization")] = None,  # exact header name
    convert: Annotated[str | None, Header(convert_underscores=False)] = None,  # no underscore->hyphen
) -> dict:  # response body
    return {"version": version, "tags": tags, "has_token": token is not None, "convert": convert}  # echo


@app.post("/logout")  # remove the session cookie
def logout(response: Response, session: Annotated[str | None, Cookie()] = None) -> dict:  # read + delete
    response.delete_cookie("session")  # sends Set-Cookie with an expiry in the past
    return {"was_logged_in": session is not None}  # info


c: TestClient = TestClient(app)  # demo client
print(c.get("/data").status_code)  # missing required header -> validation error
# Output: 422
print(c.get("/data", headers={"X-API-Version": "9"}).status_code)  # bad value
# Output: 400
r = c.get("/data", headers=[("X-API-Version", "2"), ("X-Tag", "a"), ("X-Tag", "b"), ("Authorization", "Bearer t")])  # repeated header
print(r.json())  # list collected
# Output: {'version': 2, 'tags': ['a', 'b'], 'has_token': True, 'convert': None}
out = c.post("/logout", cookies={"session": "abc"})  # logout with a cookie
print(out.json(), "Max-Age=0" in out.headers["set-cookie"])  # cookie is expired
# Output: {'was_logged_in': True} True
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (FastAPI)
@app.get("/me")
def me(authorization: str = Header(), session: str | None = Cookie(None), response: Response = None):
    response.set_cookie("seen", "1", httponly=True)
    return {"auth": authorization}
```
```javascript
// JavaScript (Express + cookie-parser)
app.get("/me", (req, res) => {
  const auth = req.headers["authorization"];   // header names arrive in lower case
  const session = req.cookies.session;         // needs cookie-parser middleware
  res.cookie("seen", "1", { httpOnly: true }); // set cookie
  res.json({ auth });
});
// Browser fetch: fetch(url, { headers: { Authorization: "Bearer x" }, credentials: "include" })
```

Key difference: FastAPI turns `user_agent` into `user-agent` for you and validates types. Express exposes raw lower-case keys. In the browser, cross-site cookies need `credentials: "include"` on the client and `allow_credentials=True` in CORS on the server.

---

## 🟠 FastAPI Connection
Auth uses headers heavily: `HTTPBearer` and `OAuth2PasswordBearer` read `Authorization`, `APIKeyHeader` reads a custom key header, and session-based apps use `APIKeyCookie`. Middleware commonly adds an `X-Request-ID` and timing header to every response.

```python
# FastAPI: bearer token via the security helper (shows up as the Authorize button in Swagger)
from fastapi import Depends, FastAPI  # app
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer  # reads "Authorization: Bearer x"
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # app
bearer: HTTPBearer = HTTPBearer()  # parses the scheme + token


@app.get("/me")  # protected route
def me(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:  # injected credentials
    return {"scheme": creds.scheme, "token": creds.credentials}  # echo


c: TestClient = TestClient(app)  # client
print(c.get("/me", headers={"Authorization": "Bearer abc"}).json())  # with token
# Output: {'scheme': 'Bearer', 'token': 'abc'}
print(c.get("/me").status_code)  # no header (403 in older FastAPI, 401 in newer)
# Output: 401
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Writing the header name with hyphens in Python
```python
# Wrong - "user-agent" is not a valid Python name
# def f(user-agent: str = Header()): ...

# Correct - underscores, FastAPI converts to hyphens
def f(user_agent: str = Header()): ...
```

❌ Mistake 2: Storing session tokens in cookies without flags
```python
# Wrong - readable by JavaScript, sent over HTTP, sent cross-site
response.set_cookie("session", token)

# Correct
response.set_cookie("session", token, httponly=True, secure=True, samesite="lax", max_age=3600)
```

❌ Mistake 3: Using `Header()` for a repeated header with a plain `str`
```python
# Wrong - only gets one value
def f(x_tag: str = Header()): ...

# Correct - use a list type to collect all values
def f(x_tag: list[str] = Header()): ...
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from fastapi import FastAPI, Header
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/a")
def a(user_agent: str = Header(), my_key: str = Header(convert_underscores=False, default="none")):
    return {"ua": user_agent, "key": my_key}

c = TestClient(app)
print(c.get("/a", headers={"User-Agent": "u", "My-Key": "k1", "my_key": "k2"}).json())
```

**Answer**:
```
{'ua': 'u', 'key': 'k2'}
```
`user_agent` maps to `user-agent` (case-insensitive). With `convert_underscores=False`, `my_key` is looked up as the literal name `my_key`, so `My-Key: k1` is ignored and `k2` is used. (Underscore headers are blocked by some proxies such as nginx by default, which is why the conversion exists.)

---

## ⚫ Interview Questions + Answers

Q1: How does FastAPI map `x_token` to a header?
A1: It converts underscores to hyphens and matches case-insensitively, so `x_token` reads `X-Token`. Turn this off with `convert_underscores=False`, or use `alias=` for an exact name.

Q2: What do `HttpOnly`, `Secure` and `SameSite` do?
A2: `HttpOnly` hides the cookie from JavaScript (stops XSS theft). `Secure` sends it over HTTPS only. `SameSite` limits cross-site sending (defends against CSRF).

Q3: Header vs Cookie vs Query for auth?
A3: APIs for apps use the `Authorization` header (not logged in URLs like query strings). Browser web apps often use HttpOnly cookies (sent automatically, need CSRF protection). Never put secrets in the query string.

Q4: How do you set a response header?
A4: Add a `response: Response` parameter and use `response.headers[...] = ...`, or return a `JSONResponse(headers={...})`, or use middleware for all routes.

Q5: How do you read all headers at once?
A5: Add a `request: Request` parameter and use `request.headers` (case-insensitive mapping) and `request.cookies`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Tokens and API keys (`Authorization`, `X-API-Key`)
- Tracing ids, API version, language, idempotency keys
- Browser sessions with HttpOnly cookies

❌ Avoid when:
- Putting large data in headers (servers limit total header size, about 8 KB)
- Storing sensitive data readable by JavaScript in non-HttpOnly cookies
- Using cookies for a pure mobile/server API without a browser

---

## 📊 Visual Diagram

```
 Browser                                   FastAPI
   │  POST /login                             │
   │ ───────────────────────────────────────► │
   │  ◄── Set-Cookie: session=abc; HttpOnly ── │
   │                                           │
   │  GET /whoami                              │
   │  Cookie: session=abc                      │
   │  User-Agent: demo   X-Request-ID: 42      │
   │ ───────────────────────────────────────► │  Cookie()/Header() params
   │  ◄── 200 {"session":"abc", ...} ───────── │
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Header | Metadata key-value in HTTP | HTTP के साथ जाने वाली metadata |
| Cookie | Small value stored by browser | browser में रखा छोटा value |
| Set-Cookie | Response header that creates a cookie | cookie बनाने वाला response header |
| HttpOnly | Hidden from JavaScript | JavaScript से छिपी |
| SameSite | Limits cross-site sending | cross-site भेजने पर रोक |
| Bearer token | Token sent in Authorization header | Authorization header में भेजा token |
| Stateless | Server keeps no memory between requests | requests के बीच server कुछ याद नहीं रखता |

---

## ⚡ 3-Line Summary
English: Headers carry request metadata; cookies let the browser store and resend small values. Use `Header()` and `Cookie()` to read, and `Response.set_cookie` or `response.headers` to write. Always set HttpOnly, Secure and SameSite on session cookies.
Hindi: Headers request की metadata ले जाते हैं; cookies browser को छोटे values store और दोबारा भेजने देती हैं। पढ़ने के लिए `Header()` और `Cookie()`, लिखने के लिए `Response.set_cookie` या `response.headers` इस्तेमाल करें। Session cookies पर हमेशा HttpOnly, Secure और SameSite लगाएँ।

---

## ➡️ Next Topic
**312. Dependencies — Complete Guide** — reuse logic like auth, DB sessions and pagination with `Depends` (311 covers the intro).
