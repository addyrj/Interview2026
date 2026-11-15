---

# 438. Nginx + FastAPI Setup
# हिंदी में: Nginx + FastAPI Setup (Reverse Proxy)

---

## 🔵 Simple Definition (English)
Nginx is a fast web server that sits in front of your FastAPI app as a reverse proxy. Browsers talk to Nginx on ports 80/443; Nginx handles HTTPS, compression, static files and limits, then forwards the request to uvicorn on `127.0.0.1:8000`.

## 🔵 सरल परिभाषा (Hindi)
Nginx एक तेज़ web server है जो FastAPI app के आगे reverse proxy की तरह बैठता है। Browser, Nginx से port 80/443 पर बात करते हैं; Nginx HTTPS, compression, static files और limits संभालकर request को `127.0.0.1:8000` पर चल रहे uvicorn को भेज देता है।

---

## 🔴 Problem it Solves
Uvicorn is great at running Python but is not built to face the open internet: it does not manage TLS certificates, buffer slow clients, serve static files efficiently, apply connection limits or host several domains on one port 443. Without a proxy, a slow client can hold a worker, and every certificate renewal means restarting the app.

## 🔴 यह क्यों बना? (Hindi)
Uvicorn Python चलाने में बढ़िया है पर सीधे इंटरनेट के सामने रहने के लिए नहीं बना: यह TLS certificates नहीं संभालता, slow clients को buffer नहीं करता, static files कुशलता से serve नहीं करता, connection limits नहीं लगाता और एक port 443 पर कई domains नहीं चला सकता। Proxy के बिना एक slow client worker को रोक सकता है और हर certificate renewal पर app restart करना पड़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → DNS: api.example.com -> VPS public IP
Step 2 → Nginx listens on :80 (redirect to https) and :443 (TLS from Let's Encrypt)
Step 3 → location / { proxy_pass http://127.0.0.1:8000; } forwards the request
Step 4 → Nginx adds headers: Host, X-Real-IP, X-Forwarded-For, X-Forwarded-Proto
Step 5 → uvicorn --proxy-headers trusts those headers (only from 127.0.0.1)
Step 6 → FastAPI sees the REAL client IP and https scheme
Step 7 → Nginx buffers the response, gzips it and returns it to the client
Step 8 → nginx -t (test config) then systemctl reload nginx (no downtime)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → DNS: api.example.com -> VPS का public IP
Step 2 → Nginx :80 (https पर redirect) और :443 (Let's Encrypt का TLS) पर सुनता है
Step 3 → location / { proxy_pass http://127.0.0.1:8000; } request आगे भेजता है
Step 4 → Nginx headers जोड़ता है: Host, X-Real-IP, X-Forwarded-For, X-Forwarded-Proto
Step 5 → uvicorn --proxy-headers इन headers पर भरोसा करता है (सिर्फ 127.0.0.1 से)
Step 6 → FastAPI को असली client IP और https scheme दिखता है
Step 7 → Nginx response buffer करता है, gzip करता है और client को लौटाता है
Step 8 → nginx -t (config test) फिर systemctl reload nginx (बिना downtime)
```

---

## 🟡 Real World Example
A food-delivery backend has `api.example.com` (FastAPI), `admin.example.com` (another app) and a static `/media/` folder of restaurant photos. One Nginx on the VPS terminates HTTPS for all, serves `/media/` directly from disk (never touching Python), proxies `/` to FastAPI and rate-limits `/login` to stop password guessing.

## 🟡 Real Example Hindi mein
एक food-delivery backend में `api.example.com` (FastAPI), `admin.example.com` (दूसरा app) और restaurant photos का static `/media/` folder है। VPS पर एक Nginx सबके लिए HTTPS संभालता है, `/media/` सीधे disk से देता है (Python तक नहीं जाता), `/` को FastAPI पर proxy करता है और password guessing रोकने के लिए `/login` को rate-limit करता है।

---

## 💻 Code Example — Basic
Nginx side (shown here, **not run**: no Nginx in this environment; run `sudo nginx -t` on your server to validate):

```nginx
# /etc/nginx/sites-available/orders-api
upstream fastapi_app {
    server 127.0.0.1:8000;                  # uvicorn/gunicorn address
    keepalive 16;                           # reuse connections to the app
}

server {
    listen 80;
    server_name api.example.com;
    return 301 https://$host$request_uri;  # force HTTPS
}

server {
    listen 443 ssl http2;
    server_name api.example.com;
    ssl_certificate     /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    client_max_body_size 10m;               # max upload size (default is only 1m)

    location /media/ {                      # static files straight from disk
        alias /srv/app/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://fastapi_app;
        proxy_http_version 1.1;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
```

The Python side: what FastAPI sees with and without the proxy-header middleware (this is what `uvicorn --proxy-headers --forwarded-allow-ips=127.0.0.1` does):

```python
# Basic: what Nginx forwards and how FastAPI should read it
from fastapi import FastAPI, Request              # app + request object
from fastapi.testclient import TestClient         # local client
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware   # same code as --proxy-headers

app: FastAPI = FastAPI()                          # plain app


@app.get("/whoami")
def whoami(request: Request) -> dict[str, str | None]:
    return {
        "client_ip": request.client.host if request.client else None,   # peer address
        "scheme": request.url.scheme,             # http or https as the browser used
        "host": request.headers.get("host"),      # domain name
    }


client = TestClient(app)                          # NO proxy middleware yet
hdrs = {"X-Forwarded-For": "49.36.10.5", "X-Forwarded-Proto": "https"}   # what Nginx adds
print(client.get("/whoami", headers=hdrs).json()) # ip is the proxy's, scheme is http (wrong)

# trusted_hosts="*" only for the demo; in production use the proxy's IP, e.g. "127.0.0.1"
proxied = ProxyHeadersMiddleware(app, trusted_hosts="*")   # honour X-Forwarded-* headers
client2 = TestClient(proxied)                     # same app, now behind the middleware
print(client2.get("/whoami", headers=hdrs).json())   # real visitor ip + https

# Output (real run, Python 3.13):
# {'client_ip': 'testclient', 'scheme': 'http', 'host': 'testserver'}
# {'client_ip': '49.36.10.5', 'scheme': 'https', 'host': 'testserver'}
```

## 💻 Code Example — Advanced
```python
# Advanced: behind Nginx with a /api prefix, trusted hosts and per-real-IP rate limit
import time                                       # monotonic clock
from collections import defaultdict, deque        # sliding window storage

from fastapi import Depends, FastAPI, HTTPException, Request   # framework
from fastapi.middleware.trustedhost import TrustedHostMiddleware   # Host header check
from fastapi.testclient import TestClient         # local client
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware   # X-Forwarded-*

# Nginx: location /api/ { proxy_pass http://127.0.0.1:8000/; }  (strips /api)
# Start the server with `uvicorn main:app --root-path /api` so /docs links include /api
# (the FastAPI(root_path=...) argument is deprecated in recent FastAPI versions)
app: FastAPI = FastAPI()
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["api.example.com", "testserver"])

hits: dict[str, deque[float]] = defaultdict(deque)   # ip -> recent request times
LIMIT, WINDOW = 3, 60.0                           # 3 requests per minute per IP


def rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"   # real ip after proxy middleware
    now = time.monotonic()                        # not affected by clock changes
    q = hits[ip]                                  # this visitor's timestamps
    while q and now - q[0] > WINDOW:              # drop old entries
        q.popleft()
    if len(q) >= LIMIT:                           # too many
        raise HTTPException(status_code=429, detail="slow down")
    q.append(now)                                 # record this hit


@app.get("/ping", dependencies=[Depends(rate_limit)])
def ping() -> dict[str, str]:
    return {"pong": "ok"}


wrapped = ProxyHeadersMiddleware(app, trusted_hosts="127.0.0.1,testclient")   # outermost layer
c = TestClient(wrapped)
# two different visitors behind the same proxy - limited separately
for ip in ["1.1.1.1"] * 4 + ["2.2.2.2"]:
    r = c.get("/ping", headers={"X-Forwarded-For": ip})
    print(ip, r.status_code)
print(c.get("/openapi.json").status_code)         # docs endpoint still works

# Output (real run, Python 3.13):
# 1.1.1.1 200
# 1.1.1.1 200
# 1.1.1.1 200
# 1.1.1.1 429
# 2.2.2.2 200
# 200
```

Notes: `--root-path /api` (a uvicorn/`fastapi run` flag) tells docs links about the prefix Nginx stripped. The `FastAPI(root_path=...)` constructor argument still exists in some versions but is deprecated in newer FastAPI (this run used FastAPI 0.162), so prefer the server flag. The first visitor is blocked on the 4th request; the second visitor is counted separately because the limiter uses the real IP.

---

## 🟠 JavaScript vs Python Comparison

| Concept | FastAPI | Express |
|---------|---------|---------|
| Trust proxy | `--proxy-headers`, `ProxyHeadersMiddleware` | `app.set("trust proxy", 1)` |
| Real IP | `request.client.host` | `req.ip` |
| Scheme | `request.url.scheme` | `req.protocol` |
| Prefix | `--root-path /api` | `app.use("/api", router)` |
| Static files | Nginx serves them | `express.static` (better via Nginx) |

```python
# Python way — real client IP (works after proxy-headers middleware)
from fastapi import Request
def ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"
```
```javascript
// JavaScript way — Express must be told to trust the proxy
app.set("trust proxy", 1);                       // trust the first hop (Nginx)
app.get("/ip", (req, res) => res.json({ ip: req.ip }));
```

Key difference: both ecosystems have the same trap. If you trust `X-Forwarded-For` from everyone, any client can fake their IP. Trust it only from the proxy's address.

---

## 🟠 FastAPI Connection
FastAPI does not know a proxy exists unless you tell it. Start uvicorn with `--proxy-headers --forwarded-allow-ips=127.0.0.1` (gunicorn: `--forwarded-allow-ips`). Then redirects (`RedirectResponse`), `request.url_for()` and OAuth callback URLs use `https://api.example.com` instead of `http://127.0.0.1:8000`. Also add `TrustedHostMiddleware` so requests with a forged `Host` header are rejected.

```python
# FastAPI example — url_for generates the public https URL only with proxy headers
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

app = FastAPI()

@app.get("/items/{i}", name="item")
def item(i: int) -> dict[str, int]:
    return {"i": i}

@app.get("/link")
def link(request: Request) -> dict[str, str]:
    return {"url": str(request.url_for("item", i=7))}   # absolute URL

c = TestClient(ProxyHeadersMiddleware(app, trusted_hosts="*"))
h = {"X-Forwarded-Proto": "https", "X-Forwarded-Host": "api.example.com", "host": "api.example.com"}
print(c.get("/link", headers=h).json())    # {'url': 'https://api.example.com/items/7'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `proxy_set_header` lines, so FastAPI sees only `127.0.0.1`
✅ Correct: pass Host, X-Real-IP, X-Forwarded-For and X-Forwarded-Proto, and enable `--proxy-headers`

```nginx
# Wrong
location / { proxy_pass http://127.0.0.1:8000; }
# Right
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

❌ Mistake 2: `trusted_hosts="*"` / `--forwarded-allow-ips="*"` in production on a public port
✅ Correct: trust only the proxy IP, and bind uvicorn to `127.0.0.1`

```python
# Wrong: anyone can send X-Forwarded-For: 1.2.3.4 and fake their address
ProxyHeadersMiddleware(app, trusted_hosts="*")
# Right
ProxyHeadersMiddleware(app, trusted_hosts="127.0.0.1")
```

❌ Mistake 3: Trailing-slash mistakes in `proxy_pass` and default 1 MB upload limit
✅ Correct: know that `proxy_pass http://x/;` strips the matched prefix and `http://x;` keeps it; raise `client_max_body_size`

```nginx
# location /api/ { proxy_pass http://127.0.0.1:8000;  }   -> app receives /api/ping (prefix kept)
# location /api/ { proxy_pass http://127.0.0.1:8000/; }   -> app receives /ping     (prefix stripped)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output? (Nginx adds X-Forwarded-For: client, and the app is behind TWO proxies)
xff = "9.9.9.9, 10.0.0.5, 10.0.0.6"      # header value received by the app
parts = [p.strip() for p in xff.split(",")]
print(parts[0])
print(parts[-1])
```
Answer: It prints `9.9.9.9` and then `10.0.0.6`. Each proxy appends the address it received the request from, so the header is a chain. The **leftmost** entry is whatever the first client claimed, which an attacker can fake by sending their own `X-Forwarded-For`. The **rightmost** entry is the address of the last proxy's peer and cannot be spoofed by the client. Safe logic: walk from the right, skip addresses of your own trusted proxies, and take the first untrusted one. That is why uvicorn only reads the header when the direct peer is in `--forwarded-allow-ips`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a forward proxy and a reverse proxy?
A1: A forward proxy sits in front of clients and hides them from servers (corporate proxy, VPN). A reverse proxy sits in front of servers and hides them from clients (Nginx before FastAPI). It gives TLS, load balancing, caching and one public entry point.

Q2: Why must WebSockets or streaming need extra Nginx config?
A2: WebSockets need an HTTP/1.1 Upgrade handshake, so add `proxy_set_header Upgrade $http_upgrade;` and `proxy_set_header Connection "upgrade";`. For streaming/SSE responses add `proxy_buffering off;` so chunks reach the client immediately.

Q3: How do you do load balancing in Nginx?
A3: Put several servers in an `upstream` block (`server 10.0.0.1:8000; server 10.0.0.2:8000;`). Default is round-robin; `least_conn` and `ip_hash` are alternatives. Add `max_fails` and `fail_timeout` for passive health checks.

Q4: How do you get free HTTPS?
A4: Install certbot (`certbot --nginx -d api.example.com`). It obtains a Let's Encrypt certificate, edits the Nginx config and sets a systemd timer for automatic renewal every 60 days or so.

Q5: How do you debug a 502 Bad Gateway?
A5: 502 means Nginx could not get a valid answer from upstream: the app is down, listens on a different port, or crashed. Check `systemctl status orders-api`, `curl 127.0.0.1:8000/health` on the server, and `/var/log/nginx/error.log`. A 504 means the app answered too slowly (raise `proxy_read_timeout` or fix the slow code).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You run on a VPS or bare metal and need HTTPS and domains
- You want static files, gzip, rate limits and multiple apps on one server
- You need load balancing across several app instances

❌ Avoid when:
- A managed platform (Render, Railway, Cloud Run, an AWS ALB) already terminates TLS for you
- Pure serverless (Lambda behind API Gateway)
- A tiny internal tool on a trusted network

---

## 📊 Visual Diagram
```
 Client --HTTPS--> [ Nginx :443 ]
                    | TLS off, gzip, limits, static /media
                    | adds X-Forwarded-For / -Proto / Host
                    v  http://127.0.0.1:8000
              [ uvicorn --proxy-headers ]
                    v
               FastAPI route: request.client.host = real visitor IP
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Reverse proxy | Server that forwards requests to your app | app को requests आगे भेजने वाला server |
| upstream | Backend servers Nginx sends to | Nginx जिन backends को भेजता है |
| TLS termination | Decrypt HTTPS at the proxy | proxy पर HTTPS खोलना |
| X-Forwarded-For | Header with the client IP chain | client IP की श्रृंखला वाला header |
| 502 / 504 | Bad gateway / gateway timeout | खराब gateway / gateway timeout |
| certbot | Let's Encrypt client | मुफ्त HTTPS certificate tool |

---

## ⚡ 3-Line Summary
English: Nginx faces the internet and handles TLS, static files and limits, then proxies to uvicorn on localhost. Forward the right headers and tell uvicorn to trust them only from the proxy. Test with `nginx -t` and reload without downtime.
Hindi: Nginx इंटरनेट के सामने रहकर TLS, static files और limits संभालता है, फिर localhost के uvicorn को proxy करता है। सही headers भेजो और uvicorn को बताओ कि सिर्फ proxy पर भरोसा करे। `nginx -t` से test करो और बिना downtime reload करो।

---

## ➡️ Next Topic
**439. Supervisor Setup** — an alternative process manager that keeps uvicorn/gunicorn and background workers alive.
