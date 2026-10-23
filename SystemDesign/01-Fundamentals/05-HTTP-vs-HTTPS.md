# 05. HTTP vs HTTPS
# हिंदी में: HTTP — ब्राउज़र और सर्वर के बीच बातचीत की भाषा; HTTPS — वही भाषा, पर ताले (एन्क्रिप्शन) के साथ

---

## 🔵 Simple Definition (English)
**HTTP** (HyperText Transfer Protocol) is the application-layer protocol used by browsers, mobile apps and APIs to send **requests** and receive **responses**.
**HTTPS** = HTTP + **TLS encryption**. Same requests and responses, but no one in the middle can read or change them.

## 🔵 सरल परिभाषा (Hindi)
HTTP वो नियम है जिससे क्लाइंट (ब्राउज़र/ऐप) सर्वर से कुछ माँगता है (request) और सर्वर जवाब देता है (response)।
HTTPS में यही बातचीत एन्क्रिप्ट हो जाती है — बीच में बैठा कोई भी पढ़ या बदल नहीं सकता।

---

## 🔴 Problem it Solves
**HTTP** gave a simple, universal, text-based format for clients and servers to exchange documents and data: any browser can talk to any server.

**Why HTTPS was needed:** plain HTTP is sent as readable text. On public Wi-Fi (airport, café), anyone on the network can:
- **Read** passwords, tokens, card numbers (sniffing),
- **Modify** responses — inject ads or malware (ISPs in some countries injected ads into HTTP pages),
- **Impersonate** the server (man-in-the-middle).

HTTPS gives three guarantees: **Confidentiality** (encrypted), **Integrity** (not modified), **Authentication** (you're really talking to swiggy.com, verified by a certificate).

## 🔴 यह क्यों बना? (Hindi)
HTTP ने सबको एक सामान्य भाषा दी, पर उसमें सब कुछ खुला टेक्स्ट होता है — Wi-Fi पर बैठा हैकर पासवर्ड और टोकन पढ़ सकता है, जवाब बदल सकता है।
HTTPS तीन चीज़ें देता है: डेटा छिपा रहे (encryption), डेटा बदले नहीं (integrity), और सर्वर असली है (certificate)।

---

## 🟢 How it Works — Step by Step

### Anatomy of an HTTP request and response

```
REQUEST ───────────────────────────────────────────────────────────
POST /api/v1/orders HTTP/1.1                 ← Method  Path  Version
Host: api.swiggy.com                         ← Headers
Authorization: Bearer eyJhbGciOi...
Content-Type: application/json
Idempotency-Key: 7f3a-...
                                             ← blank line
{"restaurantId": 42, "items": [101, 205]}    ← Body

RESPONSE ──────────────────────────────────────────────────────────
HTTP/1.1 201 Created                         ← Version  Status code
Content-Type: application/json
Cache-Control: no-store
Set-Cookie: session=abc; HttpOnly; Secure

{"orderId": 98765, "status": "PLACED"}
```

### HTTP Methods

```
┌────────┬────────────────────────────┬──────────┬────────────┐
│ Method │ Use                        │ Safe?    │ Idempotent?│
├────────┼────────────────────────────┼──────────┼────────────┤
│ GET    │ Read a resource            │ Yes      │ Yes        │
│ POST   │ Create / trigger action    │ No       │ NO         │
│ PUT    │ Replace whole resource     │ No       │ Yes        │
│ PATCH  │ Update part of a resource  │ No       │ Not always │
│ DELETE │ Delete a resource          │ No       │ Yes        │
│ HEAD   │ Like GET, headers only     │ Yes      │ Yes        │
│ OPTIONS│ What's allowed? (CORS)     │ Yes      │ Yes        │
└────────┴────────────────────────────┴──────────┴────────────┘
Safe = doesn't change data.  Idempotent = calling N times = same result as once.
(Retry a POST blindly → duplicate order! See Topic 64 Idempotency.)
```

### Status codes (memorize these)

```
1xx Info        101 Switching Protocols (WebSocket upgrade)
2xx Success     200 OK · 201 Created · 202 Accepted (async job) · 204 No Content
3xx Redirect    301 Moved Permanently · 302 Found · 304 Not Modified (cache hit)
                307/308 Redirect keeping the method
4xx Client err  400 Bad Request · 401 Unauthorized (not logged in)
                403 Forbidden (logged in, no permission) · 404 Not Found
                409 Conflict · 422 Unprocessable (validation) · 429 Too Many Requests
5xx Server err  500 Internal Error · 502 Bad Gateway (Nginx can't reach Node)
                503 Service Unavailable (overloaded/maintenance) · 504 Gateway Timeout
```

### Important headers

```
Content-Type / Accept         → format of body (application/json)
Authorization                 → Bearer token / Basic auth
Cache-Control, ETag,          → caching (Topic F07)
  If-None-Match
Cookie / Set-Cookie           → sessions (HttpOnly, Secure, SameSite)
Origin, Access-Control-*      → CORS (Topic F15)
X-Forwarded-For               → real client IP behind proxy
User-Agent                    → client type (browser / RN app version)
Content-Encoding: gzip/br     → compression
Strict-Transport-Security     → force HTTPS (HSTS)
```

### HTTP is stateless
Each request is independent; the server doesn't remember the previous one. State is carried by **cookies, tokens or session IDs** in every request. (This makes horizontal scaling easy — Topic 23.)

### HTTP versions

```
HTTP/1.0 (1996)  New TCP connection for EVERY request. Very slow.

HTTP/1.1 (1997)  Keep-alive (reuse connection). But one request at a time per connection
                 → browsers open ~6 parallel connections per domain.
                 Text headers, repeated every request.

HTTP/2  (2015)   ONE TCP connection, MANY parallel streams (multiplexing).
                 Binary framing, HPACK header compression.
                 Still TCP → head-of-line blocking at packet level.

HTTP/3  (2022)   HTTP/2 ideas over QUIC (UDP). No TCP HOL blocking,
                 faster handshake, survives network switch (great for mobile).

  HTTP/1.1                         HTTP/2                       
  conn1: [req A]──[resp A]         conn1: [A][B][C][A][C][B]... (interleaved streams)
  conn2: [req B]──[resp B]
  conn3: [req C]──[resp C]
```

### HTTP vs HTTPS

```
HTTP:   Client ──── "password=1234" (plain text) ────► Server
                         ▲
                     Hacker reads it ✗

HTTPS:  Client ── TCP handshake ── TLS handshake ── "x8#kL@9..." (encrypted) ──► Server
                                                         ▲
                                                Hacker sees garbage ✓
Port:   HTTP = 80     HTTPS = 443
```
(How TLS sets up the keys → next topic.)

## 🟢 कैसे काम करता है? (Hindi)
1. क्लाइंट request भेजता है: Method (GET/POST), Path, Headers, और Body।
2. सर्वर response भेजता है: Status code (200, 404, 500), Headers, Body।
3. HTTP stateless है — सर्वर पिछला request याद नहीं रखता, इसलिए हर request में token/cookie भेजना पड़ता है।
4. HTTP/2 में एक ही कनेक्शन पर कई request साथ-साथ चलते हैं; HTTP/3 UDP (QUIC) पर चलता है।
5. HTTPS में पहले TLS से ताला लगता है, फिर वही HTTP बातचीत एन्क्रिप्ट होकर जाती है।

---

## 🟡 Real World Example

**Google Chrome "Not Secure" label + SEO**
- Since 2018 Chrome marks every HTTP page as "Not Secure", and Google ranks HTTPS sites higher. Today ~95% of Chrome traffic is HTTPS. HTTPS is no longer optional.

**Firesheep (2010)**
- A Firefox extension let anyone on café Wi-Fi click a button and log into other people's Facebook/Twitter accounts by stealing session cookies sent over HTTP. This pushed Facebook, Twitter and Gmail to HTTPS-everywhere.

**Swiggy app**
- Every API call (`api.swiggy.com`) is HTTPS with HTTP/2. Static images come from a CDN over HTTP/2 or HTTP/3. Status codes drive app behaviour: `401` → refresh token and retry, `429` → back off, `503` → show "high demand, please wait" screen.

## 🟡 Real Example Hindi में
2010 में Firesheep नाम के टूल से कैफ़े के Wi-Fi पर बैठकर दूसरों का Facebook अकाउंट खोला जा सकता था, क्योंकि कुकी HTTP पर खुली जाती थी — इसके बाद सब कंपनियाँ HTTPS पर आ गईं।
आज Chrome हर HTTP साइट को "Not Secure" दिखाता है।

---

## 🟠 My Stack Example

### Express — correct status codes
```js
app.post('/api/v1/orders', auth, async (req, res) => {
  const parsed = OrderSchema.safeParse(req.body);
  if (!parsed.success) return res.status(422).json({ error: parsed.error.flatten() });

  if (!req.user.canOrder) return res.status(403).json({ error: 'Forbidden' });

  const order = await createOrder(parsed.data);
  return res.status(201).location(`/api/v1/orders/${order.id}`).json(order);
});
```

### FastAPI — same thing
```python
from fastapi import FastAPI, HTTPException, status

@app.post("/api/v1/orders", status_code=status.HTTP_201_CREATED)
async def create_order(body: OrderIn, user = Depends(current_user)):
    if not user.can_order:
        raise HTTPException(status_code=403, detail="Forbidden")
    return await orders.create(body)    # Pydantic validation errors auto → 422
```

### Nginx — force HTTPS, HTTP/2, HSTS, free certs
```nginx
server {
  listen 80;
  server_name api.myapp.com;
  return 301 https://$host$request_uri;          # redirect all HTTP → HTTPS
}

server {
  listen 443 ssl;
  http2 on;
  server_name api.myapp.com;

  ssl_certificate     /etc/letsencrypt/live/api.myapp.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/api.myapp.com/privkey.pem;

  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

  gzip on;
  gzip_types application/json;

  location / { proxy_pass http://api:3000; }
}
```
```bash
sudo certbot --nginx -d api.myapp.com      # Let's Encrypt: free cert + auto-renew
```
On AWS: use **ACM** (free certs) on the ALB/CloudFront — no cert files on servers.

### Cookies set correctly
```js
res.cookie('refreshToken', token, {
  httpOnly: true,     // JS can't read it → XSS can't steal it
  secure: true,       // only sent over HTTPS
  sameSite: 'strict', // not sent on cross-site requests → CSRF protection
  maxAge: 7 * 24 * 3600 * 1000,
});
```

### React Native — HTTPS is enforced by the OS
- iOS **App Transport Security** blocks plain HTTP by default.
- Android 9+ blocks cleartext HTTP by default (`android:usesCleartextTraffic`).
- For local dev with `http://10.0.2.2:3000` you need a debug-only exception — never ship it in release builds.

```js
// Central API client: handle status codes in one place
api.interceptors.response.use(undefined, async (err) => {
  if (err.response?.status === 401) return refreshAndRetry(err.config);
  if (err.response?.status === 429) await sleep(retryAfter(err.response));
  throw err;
});
```

### Check what version a site uses
```bash
curl -I --http2 https://api.myapp.com          # look for "HTTP/2 200"
curl -I --http3 https://www.google.com         # if curl built with HTTP/3
```

---

## ⚫ Interview Questions + Answers

**Q1: What's the difference between HTTP and HTTPS?**
A1: HTTPS is HTTP sent over a TLS-encrypted connection (port 443 instead of 80). It gives confidentiality (encryption), integrity (tampering is detected), and authentication (the server's identity is verified by a certificate from a trusted CA). The HTTP messages themselves are identical. Cost: an extra TLS handshake, which is tiny with TLS 1.3 and session resumption.

**Q2: Difference between 401 and 403? 502, 503 and 504?**
A2: 401 = not authenticated (missing/invalid/expired token, so log in or refresh). 403 = authenticated but not allowed. 502 = the proxy got an invalid response or couldn't connect to the upstream (Node crashed or wrong port). 503 = the service is temporarily unavailable (overloaded, maintenance, no healthy targets). 504 = the proxy timed out waiting for the upstream (slow query, slow downstream API).

**Q3: What does idempotent mean? Which HTTP methods are idempotent?**
A3: An operation is idempotent if doing it once or many times leaves the server in the same state. GET, HEAD, PUT, DELETE and OPTIONS are idempotent; POST is not, and PATCH may not be. This matters for retries: clients and proxies can safely retry idempotent requests. For POST (create order, payment) we use an **Idempotency-Key** header so the server can detect duplicates.

**Q4: What did HTTP/2 improve over HTTP/1.1, and what did HTTP/3 improve over HTTP/2?**
A4: HTTP/2 added multiplexing (many concurrent requests over one TCP connection), binary framing and header compression (HPACK), which removed the need for multiple connections and hacks like domain sharding and sprite sheets. HTTP/2 is still on TCP, so one lost packet stalls all streams. HTTP/3 runs over QUIC (UDP) with independent streams, a faster combined handshake, and connection migration, which is a big win on lossy mobile networks.

**Q5: HTTP is stateless — so how do websites keep you logged in?**
A5: The client sends identifying data with every request: a session cookie, whose ID maps to session data stored on the server or in Redis, or a token (JWT) in the `Authorization` header that carries signed user info. Because each request is self-contained, any server behind the load balancer can handle it, which enables horizontal scaling.

---

## 🔷 Trade-offs
✅ Advantages (HTTP/HTTPS):
- Universal, simple, human-readable, huge tooling ecosystem (curl, Postman, browsers).
- Stateless → easy to scale and cache (CDNs, browser cache).
- HTTPS: secure by default, needed for HTTP/2 in browsers, better SEO, required by mobile OSes.

❌ Disadvantages:
- Request-response only — server can't push without polling/SSE/WebSocket.
- Text headers repeated on every request (fixed by HTTP/2 compression).
- HTTPS adds handshake latency + certificate management (mostly automated now).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Request / Response | Client asks, server answers | माँगना / जवाब देना |
| Method (GET, POST…) | Action type on a resource | किस तरह का काम |
| Status Code | Result of a request (200, 404…) | नतीजे का नंबर |
| Header | Metadata about request/response | अतिरिक्त जानकारी |
| Stateless | Server doesn't remember past requests | सर्वर पिछला याद नहीं रखता |
| Idempotent | Same result no matter how many times | कितनी बार भी करो, नतीजा एक |
| Multiplexing | Many requests on one connection | एक कनेक्शन पर कई request |
| HSTS | Browser must always use HTTPS | हमेशा HTTPS ही इस्तेमाल करो |
| Certificate | Proof of server identity | सर्वर की पहचान का प्रमाणपत्र |

---

## ⚡ 3-Line Summary
**English:**
1. HTTP = request (method, path, headers, body) → response (status, headers, body); it's stateless.
2. HTTPS = HTTP over TLS → encrypted, tamper-proof, server verified. Always use it.
3. HTTP/2 multiplexes over one TCP connection; HTTP/3 uses QUIC (UDP) for better mobile performance.

**Hindi:**
1. HTTP = request और response की भाषा; सर्वर पिछला request याद नहीं रखता।
2. HTTPS = HTTP + TLS ताला — हमेशा इस्तेमाल करो।
3. HTTP/2 एक कनेक्शन पर कई request; HTTP/3 UDP पर, मोबाइल के लिए बेहतर।

---

## ➡️ Next Topic Suggestion
**06. TLS/SSL — How Encryption Works** — You know HTTPS = HTTP + TLS. Next: what actually happens in the TLS handshake, symmetric vs asymmetric keys, certificates, and where to terminate TLS in your architecture.
