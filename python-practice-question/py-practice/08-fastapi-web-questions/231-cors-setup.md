---

# Q231. CORS setup
# Category: FASTAPI + WEB QUESTIONS
# Difficulty: ⭐⭐

---

## ❓ Question
Configure CORS in FastAPI for a frontend at `https://app.example.com` allowing credentials. Show what headers a normal request and a preflight (OPTIONS) get, what happens for a disallowed origin, and a regex setup for subdomains.

---

## 💡 Quick Concept (2 lines only)
CORS is a BROWSER rule: the server must send `Access-Control-Allow-Origin` or the browser hides the response. `CORSMiddleware` answers preflight `OPTIONS` requests and adds the headers.
हिंदी: CORS browser का नियम है — server header भेजता है, header न हो तो browser response block कर देता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from fastapi import FastAPI  # app
from fastapi.middleware.cors import CORSMiddleware  # CORS middleware
from fastapi.testclient import TestClient  # client

app = FastAPI()  # app
app.add_middleware(  # Step 1: register CORS
    CORSMiddleware,  # the middleware class
    allow_origins=["https://app.example.com"],  # Step 2: whitelist exact origins (not "*" with cookies)
    allow_credentials=True,  # allow cookies/auth headers
    allow_methods=["GET", "POST"],  # allowed methods
    allow_headers=["Authorization", "Content-Type"],  # allowed request headers
    max_age=600,  # browser may cache preflight 10 min
)

@app.get("/hello")  # a route
async def hello() -> dict[str, str]:  # handler
    return {"hi": "there"}  # body

# ============================================
# TEST CASES
# ============================================
client = TestClient(app)  # client

# Simple request from an allowed origin
r = client.get("/hello", headers={"Origin": "https://app.example.com"})  # browser adds Origin
print(r.headers.get("access-control-allow-origin"))  # Expected: https://app.example.com
print(r.headers.get("access-control-allow-credentials"))  # Expected: true

# Request from a different origin: server still answers, but NO CORS header -> browser blocks it
r = client.get("/hello", headers={"Origin": "https://evil.com"})  # other origin
print(r.status_code, r.headers.get("access-control-allow-origin"))  # Expected: 200 None

# Preflight (OPTIONS) request
pre = client.options("/hello", headers={  # browser sends this before POST with JSON
    "Origin": "https://app.example.com",  # who is asking
    "Access-Control-Request-Method": "POST",  # method it wants
    "Access-Control-Request-Headers": "Authorization",  # header it wants
})
print(pre.status_code, pre.headers["access-control-allow-methods"])  # Expected: 200 GET, POST
print(pre.headers["access-control-max-age"])  # Expected: 600

# Disallowed method in preflight
bad = client.options("/hello", headers={"Origin": "https://app.example.com", "Access-Control-Request-Method": "DELETE"})  # DELETE not allowed
print(bad.status_code)  # Expected: 400
```

---

## 🔍 Why This Works (3 lines max)
For an allowed origin the middleware echoes it back in `Access-Control-Allow-Origin`. A different origin still gets a 200 but no CORS header, so the browser (not the server) blocks it. Preflight is answered by the middleware itself without reaching your route.
हिंदी: Server अनुमति नहीं मिलने पर भी 200 देता है — block browser करता है, इसलिए curl पर CORS error नहीं दिखता।

---

## ⚡ Alternative Solution
```python
# (same file as above — reuses its imports/names)
# ---- Alternative: regex for subdomains (dev/staging) ----
app2 = FastAPI()  # app
app2.add_middleware(CORSMiddleware, allow_origin_regex=r"https://.*\.example\.com", allow_methods=["*"])  # any subdomain

@app2.get("/")  # route
async def root() -> str:  # handler
    return "ok"  # body

c2 = TestClient(app2)  # client
print(c2.get("/", headers={"Origin": "https://staging.example.com"}).headers.get("access-control-allow-origin"))  # Expected: https://staging.example.com
print(c2.get("/", headers={"Origin": "https://example.org"}).headers.get("access-control-allow-origin"))  # Expected: None
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: wildcard origin together with credentials (browsers reject it)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True)

# ❌ Wrong: adding CORSMiddleware but forgetting the preflight methods/headers -> POST with JSON fails

# ✅ Correct: list exact origins when using credentials, set allow_methods / allow_headers explicitly
```

---

## 🎯 Interview Tip (1 line)
Say: "CORS is enforced by the browser; I whitelist exact origins, never '*' with credentials, and it is NOT a security replacement for auth."

---

## 🔗 Related Questions
→ Q225 (middleware) | Q224 (JWT auth) | Q238 (OAuth2) | Q239 (versioning)
