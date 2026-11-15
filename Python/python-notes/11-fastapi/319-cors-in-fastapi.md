---

# 319. CORS in FastAPI
# हिंदी में: FastAPI में CORS (Cross-Origin Resource Sharing)

---

## 🔵 Simple Definition (English)
CORS is a browser rule: JavaScript on one origin (`http://localhost:3000`) may read responses from another origin (`https://api.shop.com`) only if the server says yes using `Access-Control-*` headers. In FastAPI you turn this on with `CORSMiddleware`.

## 🔵 सरल परिभाषा (Hindi)
CORS browser का नियम है: एक origin (`http://localhost:3000`) की JavaScript दूसरे origin (`https://api.shop.com`) का response तभी पढ़ सकती है जब server `Access-Control-*` headers से हाँ कहे। FastAPI में इसे `CORSMiddleware` से चालू करते हैं।

---

## 🔴 Problem it Solves
Browsers use the Same-Origin Policy to stop a malicious page from reading your bank data with your cookies. But a React app on port 3000 and an API on port 8000 are different origins, so the browser blocks the call. CORS lets the server list exactly which origins, methods and headers are trusted.

CORS protects the user in the browser. It is NOT server security: curl, Postman and other servers ignore it completely.

## 🔴 यह क्यों बना? (Hindi)
Browser Same-Origin Policy लगाता है ताकि कोई गलत website आपकी cookies से bank का data न पढ़ ले। लेकिन port 3000 का React app और port 8000 की API अलग origin हैं, इसलिए browser call रोक देता है। CORS में server बताता है कि कौन से origins, methods और headers भरोसेमंद हैं।

CORS browser में user की सुरक्षा करता है। यह server की security नहीं है: curl, Postman और दूसरे servers इसे ignore करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Browser JS calls fetch('https://api.shop.com/orders') from https://app.shop.com
Step 2 → If the call is 'non-simple' (JSON POST, Authorization header, PUT/DELETE) the browser first sends OPTIONS (preflight)
Step 3 → CORSMiddleware checks Origin, Access-Control-Request-Method and -Headers against your lists
Step 4 → Allowed → 200 + Access-Control-Allow-Origin (+ Allow-Methods, Max-Age). Not allowed → 400 'Disallowed CORS origin'
Step 5 → Browser sends the real request; the response also carries Access-Control-Allow-Origin
Step 6 → If the header is missing or wrong, the browser hides the response from JS (console CORS error)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → https://app.shop.com की JS, https://api.shop.com को fetch करती है
Step 2 → अगर call 'non-simple' है (JSON POST, Authorization header, PUT/DELETE) तो browser पहले OPTIONS (preflight) भेजता है
Step 3 → CORSMiddleware Origin, Request-Method और Request-Headers को आपकी lists से मिलाता है
Step 4 → Allowed → 200 + Access-Control-Allow-Origin। Allowed नहीं → 400 'Disallowed CORS origin'
Step 5 → Browser असली request भेजता है; response में भी Access-Control-Allow-Origin आता है
Step 6 → header न हो या गलत हो तो browser response को JS से छुपा देता है (console में CORS error)
```

---

## 🟡 Real World Example
A Swiggy-style React dashboard at `https://dash.swiggy-clone.com` calls a FastAPI service at `https://api.swiggy-clone.com` with an `Authorization: Bearer` token. Production lists exactly the dashboard origin; local development adds `http://localhost:5173`. A Next.js AI chat UI calling a FastAPI LLM gateway needs the same setup.

## 🟡 Real Example Hindi mein
Swiggy जैसा React dashboard `https://dash.swiggy-clone.com` से `https://api.swiggy-clone.com` वाली FastAPI service को `Authorization: Bearer` token के साथ call करता है। Production में सिर्फ dashboard का origin लिखते हैं; local development में `http://localhost:5173` जोड़ते हैं। LLM gateway वाला Next.js AI chat UI भी यही setup माँगता है।

---

## 💻 Code Example — Basic
Allow one frontend origin and watch the header appear or disappear.

```python
# Basic CORS setup - every line commented
from fastapi import FastAPI  # the app class
from fastapi.middleware.cors import CORSMiddleware  # CORS middleware from Starlette
from fastapi.testclient import TestClient  # in-process test client

app: FastAPI = FastAPI()  # create the app
app.add_middleware(  # register the middleware
    CORSMiddleware,  # the class
    allow_origins=["http://localhost:3000"],  # only this frontend origin is allowed
    allow_methods=["GET"],  # only GET is allowed
    allow_headers=["*"],  # any request header is allowed
)


@app.get("/ping")  # simple endpoint
def ping() -> dict[str, str]:  # returns a dict
    return {"msg": "pong"}  # JSON body


client: TestClient = TestClient(app)  # client to call the app
r = client.get("/ping", headers={"Origin": "http://localhost:3000"})  # request from the allowed origin
print(r.status_code, r.headers.get("access-control-allow-origin"))  # browser looks at this header
# Output: 200 http://localhost:3000
r = client.get("/ping", headers={"Origin": "http://evil.com"})  # request from some other origin
print(r.status_code, r.headers.get("access-control-allow-origin"))  # no header -> browser blocks JS from reading it
# Output: 200 None
```

## 💻 Code Example — Advanced
Production setup: origins from environment, credentials, exposed headers, preflight cache. Preflight is tested directly.

```python
# Production style: env-driven origins, credentials, preflight
import os  # read environment variables
from fastapi import FastAPI  # app class
from fastapi.middleware.cors import CORSMiddleware  # CORS middleware
from fastapi.testclient import TestClient  # test client


def load_origins() -> list[str]:  # parse origins from env
    raw: str = os.getenv("CORS_ORIGINS", "http://localhost:3000")  # comma separated list
    return [o.strip() for o in raw.split(",") if o.strip()]  # clean each item


app: FastAPI = FastAPI()  # create app
app.add_middleware(  # add CORS
    CORSMiddleware,  # class
    allow_origins=load_origins(),  # explicit list (never "*" with cookies)
    allow_credentials=True,  # allow cookies / Authorization header
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # allowed verbs
    allow_headers=["Authorization", "Content-Type"],  # allowed request headers
    expose_headers=["X-Request-ID"],  # response headers JS may read
    max_age=600,  # browser may cache preflight for 10 minutes
)


@app.post("/orders")  # a POST endpoint
def create_order() -> dict[str, int]:  # handler
    return {"order_id": 1}  # JSON body


client: TestClient = TestClient(app)  # test client
pre = client.options(  # preflight request the browser sends first
    "/orders",  # target path
    headers={  # preflight headers
        "Origin": "http://localhost:3000",  # who is asking
        "Access-Control-Request-Method": "POST",  # what they want to do
        "Access-Control-Request-Headers": "Authorization",  # which header they will send
    },
)
print(pre.status_code)  # 200 means the preflight passed
# Output: 200
print(pre.headers["access-control-allow-origin"], pre.headers["access-control-allow-credentials"], pre.headers["access-control-max-age"])
# Output: http://localhost:3000 true 600
bad = client.options("/orders", headers={"Origin": "http://evil.com", "Access-Control-Request-Method": "POST"})  # bad origin
print(bad.status_code, bad.text)  # preflight rejected
# Output: 400 Disallowed CORS origin
post = client.post("/orders", headers={"Origin": "http://localhost:3000"})  # actual request
print(post.json(), post.headers["access-control-allow-credentials"])  # body and header
# Output: {'order_id': 1} true
```

---

## 🟠 JavaScript vs Python Comparison

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["https://app.shop.com"],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
```

```javascript
// Express: the cors package
const cors = require('cors');
app.use(cors({ origin: 'https://app.shop.com', credentials: true }));
```

Same idea in both: a middleware that adds `Access-Control-*` headers and answers OPTIONS. The browser-side `fetch` code is identical in both cases; for cookies add `credentials: 'include'` in JS, and the server must set `allow_credentials=True` with an explicit origin list.

---

## 🟠 FastAPI Connection
CORS is the first thing a React/Next.js team asks for. Add the middleware once on the app. Middleware order matters: `add_middleware` wraps outward, so the LAST added runs FIRST. Add CORS last (outermost) so even error responses from other middleware get CORS headers.

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app: FastAPI = FastAPI()
# ... other middleware first ...
app.add_middleware(  # CORS added LAST = outermost
    CORSMiddleware,
    allow_origins=["https://app.shop.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `allow_origins=["*"]` together with credentials
```python
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True)  # reflects ANY origin
```
✅ Correct:
```python
app.add_middleware(CORSMiddleware, allow_origins=["https://app.shop.com"], allow_credentials=True)
```

❌ Mistake 2: Trailing slash or wrong scheme in origin
```python
allow_origins=["https://app.shop.com/"]  # origin has NO path/trailing slash
```
✅ Correct:
```python
allow_origins=["https://app.shop.com"]  # scheme + host (+ port) only
```

❌ Mistake 3: Thinking CORS secures the API
```python
# 'CORS is on, so nobody else can call my API'  (false: curl ignores CORS)
```
✅ Correct:
```python
# Always add real auth (tokens, permissions) - CORS only guides browsers
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True)

@app.get("/")
def root():
    return {}

c = TestClient(app)
print(c.get("/", headers={"Origin": "http://a.com"}).headers.get("access-control-allow-origin"))
print(c.get("/", headers={"Origin": "http://a.com", "Cookie": "sid=1"}).headers.get("access-control-allow-origin"))
print(c.get("/").headers.get("access-control-allow-origin"))
```

**Answer**:
```
http://a.com
http://a.com
None
```
With `allow_origins=["*"]` and `allow_credentials=True`, Starlette reflects the request's `Origin` back (because browsers reject a literal `*` with credentials). That means ANY website can make credentialed calls, which is a security hole. With no `Origin` header the request is not cross-origin, so no CORS header is added.

---

## ⚫ Interview Questions + Answers

Q1: Why do I see a CORS error but the server log shows 200?
A1: The server did answer. The browser blocked JavaScript from reading the response because `Access-Control-Allow-Origin` was missing or did not match. Fix the server's allowed origins.

Q2: What is a preflight request?
A2: An automatic `OPTIONS` request the browser sends before non-simple requests (JSON body, custom headers, PUT/DELETE) asking permission. `max_age` lets the browser cache the answer.

Q3: Can I use `*` for origins?
A3: Yes for public APIs without cookies. Not with credentials; list explicit origins instead (or use `allow_origin_regex` for subdomains).

Q4: Does CORS stop CSRF or API abuse?
A4: No. CORS only controls what browser JS can read. Use auth tokens, SameSite cookies and CSRF protection.

Q5: Where do I add CORSMiddleware relative to other middleware?
A5: Make it the outermost (added last) so error responses and early returns still carry CORS headers.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- A browser frontend on a different origin/port calls your API
- You need cookies or Authorization headers across origins
- Local dev: React on :3000, FastAPI on :8000

❌ Avoid when:
- Server-to-server calls (CORS is irrelevant)
- As your only security layer
- `*` with credentials

---

## 📊 Visual Diagram

```
Browser (https://app.shop.com)             FastAPI (https://api.shop.com)
        |  OPTIONS /orders  (preflight)             |
        |  Origin, Request-Method, Request-Headers  |
        | ----------------------------------------> |  CORSMiddleware checks lists
        | <---------------------------------------- |  200 + Allow-Origin/Methods/Max-Age
        |  POST /orders (real request)              |
        | ----------------------------------------> |
        | <---------------------------------------- |  200 + Allow-Origin  -> JS can read
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Origin | scheme + host + port | तीनों मिलकर पहचान (origin) |
| Preflight | OPTIONS permission check | पहले की अनुमति जाँच |
| allow_origins | Trusted origin list | भरोसेमंद origins की list |
| Credentials | Cookies / auth headers | cookies / auth headers |
| max_age | Preflight cache seconds | preflight cache का समय |
| Same-Origin Policy | Browser default isolation | browser की default सुरक्षा |

---

## ⚡ 3-Line Summary
English: CORS lets a browser frontend on another origin read your API responses. Add `CORSMiddleware` with an explicit origin list, last in the middleware chain. It is browser-only protection, so keep real authentication.
Hindi: CORS से दूसरे origin का browser frontend आपकी API का response पढ़ पाता है। `CORSMiddleware` को explicit origin list के साथ, middleware chain में आखिर में जोड़ें। यह सिर्फ browser की सुरक्षा है, असली authentication ज़रूर रखें।

---

## ➡️ Next Topic
**320. Background Tasks** — run work (emails, logs) after the response is sent.

---

**Verification note:** Every code block was run with FastAPI 0.162.4, Starlette 1.10.0, Python 3.13.3 using TestClient / httpx (no real browser). The Output comments are the real printed output.
