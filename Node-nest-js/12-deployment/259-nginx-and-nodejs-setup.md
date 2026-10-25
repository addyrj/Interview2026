# 259. Nginx + Node.js Setup
# हिंदी में: Nginx को Node.js App के आगे Reverse Proxy की तरह लगाना

---

## 🔵 Simple Definition (English)
**Nginx** is a high-performance web server that sits IN FRONT of your Node.js app as a **reverse proxy** — it receives all internet traffic on port 80/443, handles SSL/TLS termination, serves static files directly, and forwards (proxies) dynamic requests to your Node app running on an internal port like 3000. You never expose Node directly to the internet in production.

## 🔵 सरल परिभाषा (Hindi)
**Nginx** एक high-performance web server है जो तुम्हारे Node.js app के **आगे reverse proxy** की तरह बैठता है — यह port 80/443 पर पूरा internet traffic receive करता है, SSL/TLS termination handle करता है, static files directly serve करता है, और dynamic requests को तुम्हारे Node app को forward (proxy) करता है जो किसी internal port जैसे 3000 पर चल रहा होता है। Production में Node को कभी directly internet पर expose नहीं करते।

---

## 🔴 Problem it Solves
```
EXPOSING NODE.JS DIRECTLY TO THE INTERNET (bad practice):
  - Node must run as root to bind to port 80/443 (privileged ports)
    → huge security risk if the app has any vulnerability.
  - Node is single-threaded for I/O event loop handling — it's NOT
    optimized for things like: serving large static files efficiently,
    handling thousands of raw TCP/TLS handshakes, buffering slow clients.
  - No easy way to run MULTIPLE Node instances behind one public IP
    for load balancing — you'd need to build that logic yourself.
  - SSL/TLS certificate management (renewal, cipher config) baked into
    app code = more code to maintain, more attack surface.
  - A single slow/malicious client holding a connection open can tie up
    a Node worker that could otherwise serve other users.

WITH NGINX AS REVERSE PROXY:
  - Nginx (written in C, event-driven, battle-tested) handles port 80/443,
    runs as its own hardened process — Node stays on an internal port,
    running as a non-root user, never directly reachable.
  - Nginx serves static assets (images, CSS, JS bundles) directly from
    disk — MUCH faster than routing them through Node, and frees up
    Node to focus purely on dynamic/API logic.
  - SSL/TLS termination happens at Nginx — Let's Encrypt/certbot handles
    free, auto-renewing certificates, Node never deals with TLS at all.
  - Nginx can load-balance across MULTIPLE Node instances (e.g., PM2
    cluster workers on different ports, or separate app servers) using
    simple `upstream` blocks — horizontal scaling without app code changes.
  - Nginx buffers slow client connections efficiently, protecting Node's
    event loop from being blocked by slow/flaky clients.
```

## 🔴 यह क्यों बना? (Hindi)
```
Node.js को directly internet पर expose करना (bad practice):
  - Node को port 80/443 (privileged ports) पर bind करने के लिए root
    चाहिए → app में कोई vulnerability हो तो बड़ा security risk।
  - Node I/O event loop handling के लिए single-threaded है — यह large
    static files efficiently serve करने, हज़ारों raw TCP/TLS handshakes
    handle करने, slow clients buffer करने के लिए optimized नहीं है।
  - एक public IP के पीछे MULTIPLE Node instances load balancing के लिए
    चलाने का कोई easy way नहीं — वह logic खुद बनानी पड़ेगी।
  - SSL/TLS certificate management (renewal, cipher config) app code में
    baked = ज्यादा code maintain करना, ज्यादा attack surface।
  - एक slow/malicious client connection खुला रखकर एक Node worker को busy
    रख सकता है जो बाकी users को serve कर सकता था।

NGINX को REVERSE PROXY की तरह लगाने के साथ:
  - Nginx (C में लिखा, event-driven, battle-tested) port 80/443 handle
    करता है, अपना hardened process चलाता है — Node internal port पर
    रहता है, non-root user के रूप में, कभी directly reachable नहीं।
  - Nginx static assets (images, CSS, JS bundles) directly disk से serve
    करता है — Node से route करने से MUCH faster, और Node को सिर्फ
    dynamic/API logic पर focus करने देता है।
  - SSL/TLS termination Nginx पर होता है — Let's Encrypt/certbot free,
    auto-renewing certificates handle करता है, Node कभी TLS deal नहीं
    करता।
  - Nginx MULTIPLE Node instances के across load-balance कर सकता है
    (जैसे PM2 cluster workers अलग ports पर, या separate app servers)
    simple `upstream` blocks से — horizontal scaling बिना app code बदले।
  - Nginx slow client connections को efficiently buffer करता है, Node के
    event loop को slow/flaky clients से block होने से बचाता है।
```

---

## 🟢 How it Works — Step by Step

Step 1 → Install Nginx on the VPS (`apt install nginx`); it starts listening on port 80 by default, with its own systemd service managing it.
Step 2 → Node.js app runs on an internal-only port (e.g., 3000), bound to `localhost` — never directly exposed to the public internet via the firewall.
Step 3 → Create an Nginx **server block** config file (in `/etc/nginx/sites-available/`) that defines: `server_name` (your domain), and a `location /` block with `proxy_pass http://localhost:3000` — this is the actual reverse-proxy rule.
Step 4 → Symlink the config into `/etc/nginx/sites-enabled/`, test config syntax (`nginx -t`), then reload Nginx (`systemctl reload nginx`) to apply without downtime.
Step 5 → Install `certbot` (Let's Encrypt client), run `certbot --nginx -d yourdomain.com` — it automatically obtains a free SSL certificate, edits the Nginx config to add HTTPS (port 443) with the right certificate paths, and sets up a cron job for auto-renewal (certs expire every 90 days).
Step 6 → For load balancing across multiple Node instances (e.g., cluster mode on different internal ports, or multiple app servers), define an `upstream` block listing all backend addresses, then `proxy_pass http://upstream_name` instead of a single port.
Step 7 → For static files, add a dedicated `location` block pointing directly to a folder on disk (e.g., `/var/www/myapp/public`) with `try_files`, bypassing Node entirely for those requests — much faster.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → VPS पर Nginx install करो (`apt install nginx`); यह default रूप से port 80 पर listen करना शुरू करता है, अपनी systemd service के साथ managed।
Step 2 → Node.js app internal-only port पर चलता है (जैसे 3000), `localhost` से bound — firewall के through कभी public internet को directly expose नहीं।
Step 3 → एक Nginx **server block** config file बनाओ (`/etc/nginx/sites-available/` में) जो define करे: `server_name` (तुम्हारा domain), और एक `location /` block `proxy_pass http://localhost:3000` के साथ — यही actual reverse-proxy rule है।
Step 4 → Config को `/etc/nginx/sites-enabled/` में symlink करो, syntax test करो (`nginx -t`), फिर Nginx reload करो (`systemctl reload nginx`) बिना downtime apply करने के लिए।
Step 5 → `certbot` (Let's Encrypt client) install करो, `certbot --nginx -d yourdomain.com` चलाओ — यह automatically free SSL certificate लेता है, Nginx config edit करता है HTTPS (port 443) add करने के लिए सही certificate paths के साथ, और auto-renewal के लिए cron job set करता है (certs हर 90 days expire होते हैं)।
Step 6 → Multiple Node instances के across load balancing के लिए (जैसे cluster mode अलग internal ports पर, या multiple app servers), एक `upstream` block define करो जो सभी backend addresses list करे, फिर single port के बजाय `proxy_pass http://upstream_name` करो।
Step 7 → Static files के लिए, एक dedicated `location` block add करो जो directly disk पर folder को point करे (जैसे `/var/www/myapp/public`) `try_files` के साथ, उन requests के लिए Node को पूरी तरह bypass करते हुए — बहुत faster।

---

## 🟡 Real World Example
**Amazon-style seller dashboard (a mid-size e-commerce backend team):** runs their Node.js API on 4 PM2 cluster workers (ports 3001-3004 internally) across 2 VPS instances. Nginx sits in front, configured with an `upstream` block listing all 4 internal addresses with `least_conn` load-balancing strategy (routes new connections to whichever worker has the fewest active connections — better than round-robin for mixed-duration requests). Static assets for the seller dashboard's React build (JS/CSS bundles, images) are served directly by Nginx from `/var/www/seller-dashboard/build`, cutting load on Node entirely for those. `certbot --nginx` auto-renews their `sellers.example.com` SSL cert every 90 days via a cron job, with zero manual intervention. When a worker crashes, Nginx's health-aware routing combined with PM2's auto-restart means users rarely notice.

## 🟡 Real Example Hindi mein
**Amazon-style seller dashboard (एक mid-size e-commerce backend team):** अपना Node.js API 4 PM2 cluster workers (internally ports 3001-3004) पर 2 VPS instances के across चलाती है। Nginx आगे बैठता है, एक `upstream` block configured के साथ जो सभी 4 internal addresses को `least_conn` load-balancing strategy के साथ list करता है (नई connections उस worker को route करता है जिसके पास सबसे कम active connections हैं — mixed-duration requests के लिए round-robin से बेहतर)। Seller dashboard के React build (JS/CSS bundles, images) के static assets Nginx directly `/var/www/seller-dashboard/build` से serve करता है, उन requests के लिए Node पर load पूरी तरह cut करते हुए। `certbot --nginx` उनका `sellers.example.com` SSL cert हर 90 days auto-renew करता है एक cron job से, zero manual intervention के साथ। जब कोई worker crash होता है, Nginx की health-aware routing PM2 के auto-restart के साथ मिलकर users को शायद ही कभी notice होने देती है।

---

## 💻 Code Example — Basic

```nginx
# /etc/nginx/sites-available/myapp.conf
# Basic reverse proxy config: Nginx on port 80 forwards to Node on port 3000

server {
    listen 80;                       # listen for plain HTTP on standard port 80
    server_name myapp.com www.myapp.com;  # which domain(s) this block handles

    # ─── FORWARD ALL REQUESTS TO THE NODE APP ──────────────────────────────
    location / {
        proxy_pass http://localhost:3000;          # send the request to Node running locally
        proxy_http_version 1.1;                     # use HTTP/1.1 for keep-alive support
        proxy_set_header Upgrade $http_upgrade;      # needed for WebSocket upgrade support
        proxy_set_header Connection 'upgrade';       # needed for WebSocket upgrade support
        proxy_set_header Host $host;                 # pass the original Host header to Node
        proxy_set_header X-Real-IP $remote_addr;     # pass the real client IP (Node sees Nginx's IP otherwise)
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; # chain of proxy IPs
        proxy_set_header X-Forwarded-Proto $scheme;  # tells Node if original request was http or https
        proxy_cache_bypass $http_upgrade;            # don't cache WebSocket upgrade requests
    }
}
```

```bash
# enable-and-test-nginx-config.sh
# Commands to activate the config above and verify it works.

#!/bin/bash

# ─── 1. SYMLINK CONFIG FROM sites-available TO sites-enabled ──────────────
sudo ln -s /etc/nginx/sites-available/myapp.conf /etc/nginx/sites-enabled/

# ─── 2. REMOVE DEFAULT NGINX WELCOME PAGE CONFIG (avoid conflicts) ────────
sudo rm -f /etc/nginx/sites-enabled/default

# ─── 3. TEST CONFIG SYNTAX BEFORE RELOADING (catches typos safely) ────────
sudo nginx -t   # should print "syntax is ok" and "test is successful"

# ─── 4. RELOAD NGINX TO APPLY CHANGES WITHOUT DROPPING CONNECTIONS ────────
sudo systemctl reload nginx

# ─── 5. VERIFY NODE APP IS RUNNING BEHIND IT ───────────────────────────────
curl -I http://localhost:3000   # confirm Node responds locally first
curl -I http://myapp.com        # confirm Nginx correctly proxies to it
```

## 💻 Code Example — Advanced

```nginx
# /etc/nginx/sites-available/myapp-advanced.conf
# Production config: SSL/TLS, load balancing across multiple Node instances,
# serving static files directly, and security headers.

# ─── UPSTREAM BLOCK: defines the pool of Node backend instances ───────────
upstream node_backend {
    least_conn;                       # route new requests to the least-busy worker
    server 127.0.0.1:3001;            # PM2 cluster worker 1
    server 127.0.0.1:3002;            # PM2 cluster worker 2
    server 127.0.0.1:3003;            # PM2 cluster worker 3
    server 127.0.0.1:3004;            # PM2 cluster worker 4
    keepalive 64;                     # keep connections open to backends for reuse (faster)
}

# ─── REDIRECT ALL HTTP TRAFFIC TO HTTPS ────────────────────────────────────
server {
    listen 80;
    server_name myapp.com www.myapp.com;
    return 301 https://$host$request_uri;   # permanent redirect to HTTPS version
}

# ─── MAIN HTTPS SERVER BLOCK ────────────────────────────────────────────────
server {
    listen 443 ssl;                                  # listen on standard HTTPS port
    server_name myapp.com www.myapp.com;

    # SSL certificate paths — these lines are auto-added by `certbot --nginx`
    ssl_certificate /etc/letsencrypt/live/myapp.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/myapp.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;                    # only allow modern, secure TLS versions
    ssl_ciphers HIGH:!aNULL:!MD5;                     # disable weak/insecure cipher suites

    # Security headers — good practice for production
    add_header X-Frame-Options "SAMEORIGIN" always;        # prevent clickjacking via iframes
    add_header X-Content-Type-Options "nosniff" always;    # prevent MIME-type sniffing attacks
    add_header Strict-Transport-Security "max-age=31536000" always; # force HTTPS for a year

    # ─── SERVE STATIC FILES DIRECTLY — Node never sees these requests ─────
    location /static/ {
        alias /var/www/myapp/public/;    # serve directly from disk
        expires 30d;                      # tell browsers to cache for 30 days
        add_header Cache-Control "public, immutable"; # safe to cache aggressively
    }

    # ─── PROXY DYNAMIC REQUESTS TO THE NODE UPSTREAM POOL ──────────────────
    location / {
        proxy_pass http://node_backend;              # load-balanced across all 4 workers
        proxy_http_version 1.1;
        proxy_set_header Connection "";                # clear Connection header for keepalive reuse
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts — protect against slow/hanging backend connections
        proxy_connect_timeout 5s;
        proxy_read_timeout 60s;

        # Basic rate limiting reference (zone defined in http{} block, applied here)
        limit_req zone=api_limit burst=20 nodelay;
    }
}
```

```javascript
// server.js — Node app aware it's behind a reverse proxy
const express = require('express');
const app = express();

// CRITICAL: tells Express to trust X-Forwarded-* headers from Nginx,
// so req.ip and req.secure reflect the REAL client, not Nginx itself
app.set('trust proxy', 1);

app.get('/orders/:id', (req, res) => {
  res.json({
    orderId: req.params.id,
    clientIp: req.ip,              // correctly shows the real visitor's IP, thanks to trust proxy
    isSecure: req.secure,          // true because X-Forwarded-Proto says https
  });
});

const PORT = process.env.PORT || 3001; // matches one of the upstream ports in Nginx config
app.listen(PORT, 'localhost', () => {   // bind to localhost only — never 0.0.0.0 in this setup
  console.log(`Worker on port ${PORT} ready, served behind Nginx`);
});
```

---

## 🟠 Express.js Integration

```javascript
// app.js — Express app correctly configured for the Nginx + PM2 cluster setup
const express = require('express');
const app = express();

// Must trust the proxy for correct IP/protocol detection behind Nginx
app.set('trust proxy', 1);

// Health check — Nginx or a monitoring tool can hit this to verify the worker is alive
app.get('/health', (req, res) => res.status(200).send('OK'));

// Enforce HTTPS at the app level too (defense in depth, even though Nginx already redirects)
app.use((req, res, next) => {
  if (!req.secure && process.env.NODE_ENV === 'production') {
    return res.redirect(`https://${req.headers.host}${req.url}`);
  }
  next();
});

app.get('/api/orders/:id', (req, res) => {
  res.json({ orderId: req.params.id, pid: process.pid }); // pid shows which PM2 worker served it
});

// Let Node focus purely on API routes — static files are handled by Nginx,
// so there's no express.static() call needed for the public assets at all.

const PORT = process.env.PORT || 3001;
app.listen(PORT, 'localhost', () => console.log(`API worker ${process.pid} on ${PORT}`));
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `app.set('trust proxy', 1)` behind Nginx
```javascript
// WRONG — req.ip always shows Nginx's own IP (127.0.0.1), not the real client,
// breaking rate-limiting, logging, and geo-based features
app.get('/orders', (req, res) => {
  console.log(req.ip); // always "127.0.0.1" — useless for abuse detection!
});

// CORRECT — trust the X-Forwarded-For header Nginx sets
app.set('trust proxy', 1);
app.get('/orders', (req, res) => {
  console.log(req.ip); // now shows the REAL client IP
});
```

❌ **Mistake 2:** Binding Node to `0.0.0.0` instead of `localhost` in a reverse-proxy setup
```javascript
// WRONG — Node listens on ALL network interfaces, meaning it's reachable
// directly from the internet too (bypassing Nginx entirely if the firewall
// doesn't block the port) — defeats the purpose of the proxy layer
app.listen(3000, '0.0.0.0');

// CORRECT — bind only to localhost so Node is reachable ONLY via Nginx on this machine
app.listen(3000, 'localhost');
// (Also ensure ufw doesn't allow external access to port 3000 as a second layer of defense)
```

❌ **Mistake 3:** Not setting WebSocket upgrade headers when the app uses Socket.IO/WebSockets
```nginx
# WRONG — missing upgrade headers break real-time features (chat, live tracking)
location / {
    proxy_pass http://localhost:3000;
    # missing Upgrade/Connection headers!
}

# CORRECT — explicitly forward the WebSocket upgrade handshake
location / {
    proxy_pass http://localhost:3000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
}
```

❌ **Mistake 4:** Letting certbot certificates expire due to a broken renewal cron
```bash
# WRONG — assuming certbot "just works" forever without ever verifying the
# renewal cron/systemd timer is actually active
certbot --nginx -d myapp.com   # run once, never checked again

# CORRECT — verify the auto-renewal mechanism and test it periodically
sudo systemctl status certbot.timer   # confirm it's active
sudo certbot renew --dry-run           # simulates a renewal without changing real certs
```

---

## 🧠 Tricky Interview Question

**Q: Users report that after you added Nginx in front of your Node app, all requests show the SAME client IP in your logs (Nginx's own IP), breaking your rate-limiter which was working fine before. What's the fix, and why did this happen?**

```javascript
// server.js — rate limiter using req.ip BEFORE adding Nginx
const rateLimit = require('express-rate-limit');
app.use(rateLimit({ windowMs: 60000, max: 100, keyGenerator: (req) => req.ip }));
// Before Nginx: req.ip was the real client IP (direct connection).
// After Nginx: req.ip is now 127.0.0.1 for EVERY request!
```

Answer: Before Nginx, Node received TCP connections directly from clients, so `req.ip` (derived from the raw socket) correctly showed each visitor's real IP. After adding Nginx as a reverse proxy, every connection Node sees now comes from Nginx itself (`127.0.0.1` or the proxy's internal IP) — the original client's IP is only available in the `X-Forwarded-For` HTTP header that Nginx adds. Express doesn't automatically trust/parse that header for security reasons (a malicious client could forge `X-Forwarded-For` otherwise) — you must explicitly opt in with `app.set('trust proxy', 1)`, which tells Express "there is exactly 1 trusted proxy in front of me (Nginx), parse `X-Forwarded-For` from it." Setting the wrong trust proxy count (or omitting it) is a very common production bug that silently breaks IP-based rate limiting, geo-blocking, and audit logging.

---

## ⚫ Interview Questions + Answers

**Q1: Why shouldn't Node.js be exposed directly to the internet in production?**
A1: Binding to privileged ports (80/443) typically requires root, a security risk for any app vulnerability. Node's single-threaded event loop isn't optimized for raw TLS handshake overhead, serving large static files efficiently, or absorbing many slow/malicious connections — a dedicated reverse proxy like Nginx (written in C, highly optimized, battle-tested against DoS-style attacks) handles all of that far better, letting Node focus purely on application logic. It also centralizes SSL/TLS management and makes horizontal scaling (multiple Node instances) trivial via load balancing.

**Q2: What does `proxy_pass` do in an Nginx config, and what headers should typically accompany it?**
A2: `proxy_pass` tells Nginx to forward the matched request to a specified backend address (e.g., `http://localhost:3000`) and relay the response back to the client — this is the core mechanism of a reverse proxy. It should typically be accompanied by: `proxy_set_header Host $host` (preserve the original domain for the app), `proxy_set_header X-Real-IP $remote_addr` and `X-Forwarded-For` (preserve the real client IP since the app now only sees Nginx's connection), and `X-Forwarded-Proto $scheme` (tells the app whether the original request was HTTP or HTTPS, important for redirect logic and `req.secure`).

**Q3: How does Nginx achieve SSL/TLS termination, and why is it beneficial to do this at Nginx rather than in Node?**
A3: SSL/TLS termination means the HTTPS connection (encryption/decryption, certificate handling) ends at Nginx — Nginx decrypts incoming HTTPS traffic and forwards PLAIN HTTP internally to Node on `localhost` (safe since it never leaves the machine). Benefits: Node's code stays simpler (no certificate/cipher config in app code), certificate renewal (via certbot/Let's Encrypt) is centralized and automated without touching the app, and Nginx's C-based TLS implementation is typically faster/more optimized than doing it in a Node process, freeing Node's event loop for actual business logic.

**Q4: How do you load-balance across multiple Node.js instances with Nginx, and what load-balancing strategies are available?**
A4: Define an `upstream` block listing multiple backend addresses (different ports for PM2 cluster workers, or different servers entirely), then use `proxy_pass http://upstream_name` in the server block instead of a single address. Strategies: **round-robin** (default — cycles through servers evenly), **least_conn** (routes to whichever backend currently has the fewest active connections — better when request durations vary a lot), and **ip_hash** (routes the same client IP consistently to the same backend — useful for maintaining in-memory session affinity, though stateless JWT-based apps usually don't need this).

**Q5: Why serve static files (images, CSS, JS bundles) via Nginx directly instead of through Node's `express.static()`?**
A5: Nginx is written in C and highly optimized for raw file I/O and serving static content efficiently, with built-in support for things like `sendfile` syscalls, byte-range requests, and gzip/brotli compression, often faster than Node's JS-based static file serving. More importantly, it offloads that work from Node's single-threaded event loop entirely — every static file request handled by Nginx is one less request competing for Node's limited concurrency for actual dynamic/API logic, improving overall throughput for the application that matters most: your business logic.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Deploying any production Node.js app on a VPS/bare server — Nginx as reverse proxy is close to a universal best practice.
- You need SSL/TLS termination, load balancing across multiple instances, or efficient static file serving.
- You want a single public-facing entry point that can route to multiple backend services (microservices, API + static frontend) based on path/domain.

❌ Avoid when:
- Using a fully managed PaaS (Vercel, Heroku, Render, AWS Elastic Beanstalk, Google Cloud Run) that already handles reverse proxying, TLS, and load balancing for you at the platform level — adding your own Nginx layer there is usually redundant.
- A purely local development environment — the overhead of configuring Nginx isn't worth it when you can just hit `localhost:3000` directly.

---

## 📊 Visual Diagram
```
NGINX + NODE.JS PRODUCTION ARCHITECTURE:
──────────────────────────────────────────────────────────────

                    [ Internet Users ]
                           │
                           │ HTTPS (443)
                           ▼
              ┌─────────────────────────┐
              │          Nginx            │
              │  - SSL/TLS termination     │
              │    (Let's Encrypt/certbot) │
              │  - Serves /static/ directly │
              │  - Security headers        │
              │  - Rate limiting           │
              └────────────┬────────────┘
                            │ plain HTTP (internal, localhost only)
              ┌─────────────┼─────────────┬─────────────┐
              ▼             ▼             ▼             ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ Node      │  │ Node      │  │ Node      │  │ Node      │
        │ worker 1  │  │ worker 2  │  │ worker 3  │  │ worker 4  │
        │ :3001     │  │ :3002     │  │ :3003     │  │ :3004     │
        │ (PM2      │  │ (PM2      │  │ (PM2      │  │ (PM2      │
        │  cluster) │  │  cluster) │  │  cluster) │  │  cluster) │
        └──────────┘  └──────────┘  └──────────┘  └──────────┘
              upstream node_backend { least_conn; ... }

  Static files (/var/www/myapp/public) ──► served by Nginx directly,
                                             NEVER touches Node.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Reverse Proxy | Server that forwards client requests to backend servers | Client requests को backend servers को forward करने वाला server |
| proxy_pass | Nginx directive forwarding requests to a backend | Backend को requests forward करने वाली Nginx directive |
| SSL/TLS Termination | Decrypting HTTPS at the proxy, plain HTTP internally | Proxy पर HTTPS decrypt करना, internally plain HTTP |
| Let's Encrypt / certbot | Free, auto-renewing SSL certificate provider/tool | Free, auto-renewing SSL certificate provider/tool |
| Upstream Block | Nginx config defining a pool of backend servers | Backend servers का pool define करने वाला config |
| Load Balancing | Distributing requests across multiple backend instances | Requests को multiple backend instances में distribute करना |
| trust proxy | Express setting to trust X-Forwarded-* headers | X-Forwarded-* headers trust करने की Express setting |
| Static Files | Unchanging assets (images, CSS, JS) served directly | बिना बदलने वाले assets जो directly serve होते हैं |

---

## ⚡ 3-Line Summary
**English:**
1. Nginx sits in front of Node as a reverse proxy, handling port 80/443, SSL/TLS termination, static files, and load balancing — Node itself stays on an internal port, never exposed directly.
2. `proxy_pass` forwards dynamic requests to Node; `upstream` blocks enable load balancing across multiple Node/PM2 cluster instances.
3. Always set `app.set('trust proxy', 1)` in Express behind Nginx, or `req.ip`/`req.secure` will show the wrong values and silently break rate limiting and security logic.

**Hindi:**
1. Nginx Node के आगे reverse proxy की तरह बैठता है, port 80/443, SSL/TLS termination, static files, और load balancing handle करता है — Node खुद internal port पर रहता है, कभी directly expose नहीं होता।
2. `proxy_pass` dynamic requests को Node को forward करता है; `upstream` blocks multiple Node/PM2 cluster instances के across load balancing enable करते हैं।
3. Nginx के पीछे Express में हमेशा `app.set('trust proxy', 1)` set करो, नहीं तो `req.ip`/`req.secure` गलत values दिखाएंगे और rate limiting/security logic silently टूट जाएगी।

---

## ➡️ Next Topic
**260. PM2 — Complete Guide** — PM2 की deep dive: cluster mode, zero-downtime reloads, log management, monitoring, ecosystem config files।
