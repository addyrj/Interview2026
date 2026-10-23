# 11. Reverse Proxy (Nginx)
# हिंदी में: Reverse Proxy — सर्वरों के आगे खड़ा एक "गेटकीपर", जो यूज़र की request लेकर सही backend सर्वर तक पहुँचाता है

---

## 🔵 Simple Definition (English)
A **reverse proxy** is a server that sits **in front of your backend servers**. Clients talk only to the proxy; the proxy forwards requests to the right backend and returns the response. Clients never see or reach the real servers directly.
**Nginx** is the most popular reverse proxy (others: HAProxy, Caddy, Traefik, Envoy, AWS ALB).

## 🔵 सरल परिभाषा (Hindi)
Reverse proxy आपके असली सर्वरों के आगे खड़ा रहता है। यूज़र सिर्फ़ proxy से बात करता है, proxy अंदर सही सर्वर से जवाब लाकर देता है।
जैसे होटल का रिसेप्शन — मेहमान रिसेप्शन से बात करता है, अंदर किचन/रूम सर्विस तक सीधे नहीं जाता।

---

## 🔴 Problem it Solves
Exposing Node.js/FastAPI directly to the internet causes problems:
- **Security:** app servers, ports and internal IPs are exposed; no shield against slow-loris attacks or huge request bodies.
- **TLS everywhere:** every app must manage certificates.
- **Scaling:** one public IP → how do you split traffic across 5 app instances?
- **Performance:** Node is not great at serving static files, gzip and thousands of slow clients. Nginx is event-driven C code built exactly for that.
- **Routing:** `/api` → Node, `/ml` → FastAPI, `/` → Next.js, all on one domain.

A reverse proxy centralizes all of this in one place.

## 🔴 यह क्यों बना? (Hindi)
Node/FastAPI को सीधे इंटरनेट पर खोलना असुरक्षित है, हर ऐप में SSL लगाना मुश्किल है, और कई सर्वरों में ट्रैफ़िक बाँटना संभव नहीं।
Reverse proxy एक जगह पर SSL, load balancing, caching, compression, security और routing — सब संभाल लेता है।

---

## 🟢 How it Works — Step by Step

### Forward vs Reverse proxy (classic interview question)

```
FORWARD PROXY (protects/represents CLIENTS)      REVERSE PROXY (protects/represents SERVERS)

 Client A ┐                                                      ┌─► Server 1
 Client B ┼─► [Forward Proxy] ─► Internet ─► Server     Client ─► [Reverse Proxy] ─┼─► Server 2
 Client C ┘                                                      └─► Server 3
 Server sees the PROXY's IP, not client's          Client sees the PROXY, not servers
 e.g. corporate proxy, VPN, Squid                  e.g. Nginx, Cloudflare, AWS ALB
```

### Request flow through Nginx

```
Client ──HTTPS──► Nginx :443
                   │ 1. TLS decrypt
                   │ 2. Match server_name + location
                   │ 3. Apply: rate limit, body size limit, headers, cache lookup
                   │ 4. Choose upstream (round robin / least_conn / ip_hash)
                   ├──HTTP──► node-1:3000
                   ├──HTTP──► node-2:3000
                   └──HTTP──► fastapi:8000  (for /ml/*)
                   │ 5. Get response, gzip, add security headers, maybe cache it
Client ◄──────────┘
```

### What a reverse proxy can do

```
┌─────────────────────────┬──────────────────────────────────────────────┐
│ Feature                 │ Why                                          │
├─────────────────────────┼──────────────────────────────────────────────┤
│ TLS termination         │ One place for certs; apps speak plain HTTP   │
│ Load balancing          │ Spread traffic over N instances              │
│ Path / host routing     │ /api → Node, /ml → FastAPI, admin.x → Admin  │
│ Static file serving     │ Fast, sendfile, cache headers                │
│ Compression             │ gzip/brotli → smaller payloads               │
│ Response caching        │ Cache GET responses (micro-caching)          │
│ Rate limiting           │ Per-IP limits (limit_req)                    │
│ Security                │ Hide backends, max body size, block bad bots,│
│                         │ security headers, IP allow/deny              │
│ Buffering slow clients  │ Node isn't held by a slow 2G client          │
│ Health checks / failover│ Skip dead upstreams                          │
│ WebSocket proxying      │ Upgrade header support                       │
│ Zero-downtime deploys   │ Switch upstreams (blue/green), reload config │
└─────────────────────────┴──────────────────────────────────────────────┘
```

### Why Nginx is fast (event-driven architecture)

```
Apache (old prefork):  1 process/thread per connection → 10k connections = 10k threads ❌ memory

Nginx:  1 master + few workers (1 per CPU core)
        each worker = event loop (epoll) handling THOUSANDS of connections
        → 10k idle keep-alive connections ≈ a few MB of memory ✅
(Same idea as Node.js event loop — that's why "C10k problem" was solved by Nginx)
```

### Reverse proxy vs Load balancer vs API gateway

```
Reverse proxy  → general front door (Nginx). CAN load balance.
Load balancer  → focused on spreading traffic + health checks (AWS ALB/NLB, HAProxy).
API gateway    → reverse proxy + API features: auth, API keys, quotas, request transform,
                 per-route policies, developer portal (Kong, AWS API Gateway) — Topic 93.
In practice they overlap; Nginx can do a bit of all three.
```

## 🟢 कैसे काम करता है? (Hindi)
1. यूज़र की request Nginx पर (port 443) आती है; Nginx SSL खोलता (decrypt) है।
2. URL देखकर तय करता है कि किस backend पर भेजना है (`/api` → Node, `/ml` → FastAPI)।
3. रास्ते में rate limit, body size limit, cache जैसे नियम लगाता है।
4. कई सर्वर हों तो उनमें ट्रैफ़िक बाँटता है और मरे हुए सर्वर को छोड़ देता है।
5. जवाब को gzip करके, security headers लगाकर यूज़र को वापस भेजता है।

---

## 🟡 Real World Example

**Cloudflare** — a giant global reverse proxy. ~20% of websites sit behind it. Your DNS points to Cloudflare; it terminates TLS at 300+ edge locations, blocks DDoS attacks, caches content, and forwards only clean traffic to your origin server, whose IP stays hidden.

**Netflix / Lyft — Envoy, Zuul**
- Netflix built **Zuul** as its edge reverse proxy/gateway (routing, auth, canary testing). Lyft built **Envoy**, now the standard proxy inside service meshes (Istio).

**Indian startups on a single VPS**
- A very common production setup: one ₹2,000/month VPS with Docker, where Nginx routes `example.com` → Next.js, `api.example.com` → Node, `admin.example.com` → React admin, all with Let's Encrypt certs. One Nginx, many apps.

## 🟡 Real Example Hindi में
Cloudflare दुनिया का सबसे बड़ा reverse proxy है — लाखों वेबसाइट्स के आगे खड़ा होकर DDoS रोकता है, SSL संभालता है, cache करता है और असली सर्वर का IP छिपाता है।
भारत के कई स्टार्टअप एक ही VPS पर Nginx लगाकर वेबसाइट, API और admin panel — तीनों अलग-अलग डोमेन पर चलाते हैं।

---

## 🟠 My Stack Example

### docker-compose.yml
```yaml
services:
  nginx:
    image: nginx:1.27-alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on: [web, api, ml]
  web:  { build: ./web }        # Next.js :3000
  api:  { build: ./api, deploy: { replicas: 3 } }   # Node :4000
  ml:   { build: ./ml }         # FastAPI :8000
```

### Production-ready Nginx config
```nginx
# /etc/nginx/conf.d/app.conf

# ---------- upstreams ----------
upstream api_upstream {
  least_conn;                              # send to the least busy instance
  server api:4000 max_fails=3 fail_timeout=10s;   # Docker DNS resolves all replicas
  keepalive 64;
}
upstream web_upstream { server web:3000; keepalive 32; }
upstream ml_upstream  { server ml:8000;  keepalive 16; }

# ---------- rate limit zones ----------
limit_req_zone $binary_remote_addr zone=api_rl:10m rate=20r/s;
limit_req_zone $binary_remote_addr zone=login_rl:10m rate=5r/m;

# ---------- micro cache for public GETs ----------
proxy_cache_path /var/cache/nginx keys_zone=micro:10m max_size=500m inactive=10m;

# ---------- HTTP → HTTPS ----------
server {
  listen 80;
  server_name myapp.com api.myapp.com;
  return 301 https://$host$request_uri;
}

# ---------- API ----------
server {
  listen 443 ssl;
  http2 on;
  server_name api.myapp.com;
  ssl_certificate     /etc/letsencrypt/live/api.myapp.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/api.myapp.com/privkey.pem;

  client_max_body_size 10m;                # reject giant uploads early
  gzip on; gzip_types application/json;

  add_header X-Content-Type-Options nosniff always;
  add_header Strict-Transport-Security "max-age=31536000" always;

  # common proxy headers
  proxy_http_version 1.1;
  proxy_set_header Connection "";
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;
  proxy_set_header X-Request-ID $request_id;
  proxy_connect_timeout 5s;
  proxy_read_timeout 30s;

  location /auth/login {
    limit_req zone=login_rl burst=5 nodelay;   # brute-force protection
    proxy_pass http://api_upstream;
  }

  location /public/menu {                      # cache public menu for 30s
    proxy_cache micro;
    proxy_cache_valid 200 30s;
    proxy_cache_use_stale error timeout updating;   # serve stale if Node is down!
    add_header X-Cache $upstream_cache_status;
    proxy_pass http://api_upstream;
  }

  location /ml/ {
    proxy_pass http://ml_upstream/;            # strips /ml prefix → FastAPI sees /predict
    proxy_read_timeout 120s;                   # ML can be slow
  }

  location /socket.io/ {
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 3600s;
    proxy_pass http://api_upstream;
  }

  location / {
    limit_req zone=api_rl burst=40 nodelay;
    proxy_pass http://api_upstream;
  }
}

# ---------- Next.js web ----------
server {
  listen 443 ssl;
  http2 on;
  server_name myapp.com;
  ssl_certificate     /etc/letsencrypt/live/myapp.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/myapp.com/privkey.pem;

  location /_next/static/ {                    # hashed files → cache forever
    proxy_pass http://web_upstream;
    add_header Cache-Control "public, max-age=31536000, immutable";
  }
  location / { proxy_pass http://web_upstream; }
}
```

### Useful commands
```bash
nginx -t                      # test config BEFORE reload (never skip!)
nginx -s reload               # zero-downtime reload (old workers finish requests)
docker compose exec nginx nginx -t && docker compose exec nginx nginx -s reload
tail -f /var/log/nginx/error.log   # "connect() failed (111: Connection refused)" → app down → 502
```

### App side: trust the proxy
```js
app.set('trust proxy', 1);          // Express: req.ip / req.protocol from X-Forwarded-*
```
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips="*"
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between a forward proxy and a reverse proxy?**
A1: A forward proxy sits in front of clients and makes requests on their behalf. Servers see the proxy's IP. Uses: corporate filtering, VPNs, anonymity, caching for an office. A reverse proxy sits in front of servers and receives requests on their behalf. Clients see only the proxy. Uses: TLS termination, load balancing, caching, security and routing (Nginx, Cloudflare, ALB).

**Q2: Why put Nginx in front of a Node.js app instead of exposing Node directly?**
A2: Nginx handles TLS, gzip and static files much more efficiently. It buffers slow clients so Node's event loop isn't tied up, and enforces limits (body size, rate limits, timeouts). It load-balances across multiple Node processes/containers, supports zero-downtime reloads, and hides internal ports and IPs. It can also serve stale cached responses when Node is down. Node then focuses on business logic.

**Q3: How does Nginx handle so many concurrent connections?**
A3: An event-driven, non-blocking architecture: a master process and a small number of worker processes (usually one per CPU core). Each worker runs an event loop using epoll/kqueue to multiplex thousands of connections without a thread per connection. Memory per idle connection is tiny, which is how Nginx solved the C10k problem.

**Q4: Is a reverse proxy a single point of failure? How do you make it highly available?**
A4: Yes, if you run just one. Solutions: run two or more Nginx instances behind a cloud load balancer (ALB/NLB) or DNS failover; use keepalived with a floating virtual IP (active-passive) on bare metal; or use managed edges (Cloudflare, CloudFront, ALB), which are redundant by design. Also keep config in Git and test it with `nginx -t` in CI.

**Q5: A user sees intermittent 502 errors behind Nginx/ALB. What could cause it?**
A5: The upstream app crashed or is restarting (check the container/PM2 logs), there's a wrong upstream host or port, the app is out of memory, or the connection pool is exhausted. A classic cause is keep-alive timeout mismatch: the app closes an idle keep-alive connection exactly when the proxy reuses it. Fix it by setting the Node `keepAliveTimeout` higher than the proxy/ALB idle timeout. Deploys without graceful shutdown (killing in-flight requests) also cause 502s, and so do health checks that mark all instances unhealthy.

---

## 🔷 Trade-offs
✅ Advantages:
- Security (hide backends, limits, WAF), TLS in one place.
- Performance (compression, caching, static, connection handling).
- Flexibility (routing, load balancing, blue/green, canary).

❌ Disadvantages:
- Extra hop (≈ sub-ms on same host, small but non-zero).
- Another component to configure, monitor, and make highly available.
- Misconfiguration risks (wrong headers → wrong client IP; timeouts → 504s; caching private data!).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Reverse Proxy | Front door for servers | सर्वरों का गेटकीपर |
| Forward Proxy | Front door for clients | क्लाइंट्स का प्रतिनिधि |
| Upstream | Backend servers behind proxy | proxy के पीछे वाले सर्वर |
| TLS Termination | Decrypt HTTPS at proxy | proxy पर SSL खोलना |
| Micro-caching | Caching responses for seconds | कुछ सेकंड का cache |
| Event loop | One thread handling many connections | एक thread, हज़ारों कनेक्शन |
| X-Forwarded-For | Header with original client IP | असली यूज़र का IP |
| Graceful reload | Apply config without dropping requests | बिना रुकावट config बदलना |

---

## ⚡ 3-Line Summary
**English:**
1. A reverse proxy is the front door to your servers; clients never touch backends directly.
2. Nginx does TLS, routing, load balancing, caching, compression, rate limiting and security headers efficiently.
3. Make it highly available, pass X-Forwarded-* headers, set timeouts, and always `nginx -t` before reload.

**Hindi:**
1. Reverse proxy आपके सर्वरों का मुख्य दरवाज़ा है; यूज़र सीधे backend तक नहीं जाता।
2. Nginx SSL, routing, load balancing, cache, gzip, rate limit — सब तेज़ी से करता है।
3. इसे HA बनाओ, सही headers भेजो, timeout लगाओ, और reload से पहले `nginx -t` चलाओ।

---

## ➡️ Next Topic Suggestion
**12. Forward Proxy** — You've seen the server-side proxy. Next: the client-side one — corporate proxies, VPNs, egress proxies for your servers' outbound calls, and why they matter for security and IP whitelisting.
