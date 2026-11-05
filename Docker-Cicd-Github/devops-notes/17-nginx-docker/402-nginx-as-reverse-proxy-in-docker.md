# 402. Nginx as Reverse Proxy in Docker
# हिंदी में: Docker में Nginx को Reverse Proxy बनाना

---

## 🔵 Simple Definition (English)
A **reverse proxy** sits in front of your backend containers, accepts client requests on one public address and forwards them to the right internal service (Node.js, FastAPI, React). In Docker, Nginx reaches the backends by their **Compose service name** over a private network, so the backends never expose ports to the internet.

## 🔵 सरल परिभाषा (Hindi)
**Reverse proxy** आपके backend containers के आगे बैठता है, एक public address पर client requests लेता है और उन्हें सही internal service (Node.js, FastAPI, React) तक forward करता है। Docker में Nginx backends को **Compose service name** से private network पर पहुँचता है, इसलिए backends internet पर कोई port expose नहीं करते।

---

## 🔴 Problem it Solves
- Without a proxy, each service needs its own public port (`:3000`, `:8000`), so users see ugly URLs and you open many firewall holes.
- No single place for TLS, gzip, rate-limiting, security headers or logging.
- Clients can hit your app servers directly, bypassing protections.
- Node.js/uvicorn are not designed to serve slow clients or static files efficiently.

## 🔴 यह क्यों बना? (Hindi)
- Proxy के बिना हर service को अपना public port (`:3000`, `:8000`) चाहिए; URLs भद्दे और firewall में कई छेद।
- TLS, gzip, rate-limit, security headers, logging के लिए एक जगह नहीं।
- Clients सीधे app servers तक पहुँचकर protections bypass कर सकते हैं।
- Node.js/uvicorn slow clients और static files के लिए नहीं बने।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Browser calls https://app.example.com/api/users
Step 2 → Request reaches VPS port 443 -> nginx container
Step 3 → Nginx matches server_name + location /api/
Step 4 → Docker's embedded DNS (127.0.0.11) resolves "api" to the
         container IP on the shared network
Step 5 → proxy_pass http://api:3000 forwards the request, adding
         X-Forwarded-For / X-Forwarded-Proto / Host headers
Step 6 → Backend replies -> Nginx streams response back to the browser
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Browser https://app.example.com/api/users call करता है
Step 2 → Request VPS के port 443 पर nginx container तक आती है
Step 3 → Nginx server_name + location /api/ match करता है
Step 4 → Docker का embedded DNS (127.0.0.11) "api" को shared network पर
         container IP में resolve करता है
Step 5 → proxy_pass http://api:3000 request forward करता है और
         X-Forwarded-For / X-Forwarded-Proto / Host headers जोड़ता है
Step 6 → Backend जवाब देता है -> Nginx response browser को stream करता है
```

---

## 🟡 Real World Example
A food-delivery startup runs `https://app.foodly.in` (React), `https://app.foodly.in/api` (Node.js) and `/ml` (FastAPI recommendations) on a single Hostinger VPS. Only Nginx publishes 80/443. When the Node.js container is redeployed it gets a new IP, but Nginx still reaches it by the name `api`, so no config change is needed.

## 🟡 Real Example Hindi mein
एक food-delivery startup एक ही Hostinger VPS पर `https://app.foodly.in` (React), `/api` (Node.js) और `/ml` (FastAPI recommendations) चलाती है। सिर्फ Nginx 80/443 publish करता है। Node.js container redeploy होने पर नया IP पाता है, पर Nginx उसे नाम `api` से ही पहुँचता है, इसलिए config बदलनी नहीं पड़ती।

---

## 💻 Code / Config Example — Basic

```nginx
# nginx/conf.d/default.conf  -- minimal reverse proxy to one Node.js container
server {
    listen 80;                               # accept HTTP
    server_name app.example.com;             # example domain, replace with yours

    location / {                             # every path
        proxy_pass http://api:3000;          # "api" = compose service name, 3000 = its port
        proxy_set_header Host $host;         # pass original Host header to backend
        proxy_set_header X-Real-IP $remote_addr;   # real client IP
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;  # IP chain
        proxy_set_header X-Forwarded-Proto $scheme; # http or https
    }
}
```

```yaml
# docker-compose.yml  -- matching minimal stack
services:
  nginx:
    image: nginx:1.27-alpine                 # proxy
    ports: ["80:80"]                         # only public port
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro  # mount config read-only
    depends_on: [api]                        # start order (not readiness)
  api:
    build: ./api                             # Node.js image built from ./api/Dockerfile
    expose: ["3000"]                         # documents port; NOT published to host
```

## 💻 Code / Config Example — Advanced

```nginx
# nginx/conf.d/default.conf -- multi-service, websocket-ready, hardened
upstream node_api {                           # named backend group
    server api:3000;                          # Node.js container
    keepalive 32;                             # reuse upstream connections
}
upstream fastapi_ml {
    server ml:8000;                           # FastAPI container (uvicorn)
    keepalive 16;
}

map $http_upgrade $connection_upgrade {       # needed for WebSocket upgrade
    default upgrade;                          # client asked for upgrade
    ''      close;                            # normal request
}

server {
    listen 80;
    server_name app.example.com;
    server_tokens off;                        # hide nginx version
    client_max_body_size 10m;                 # cap upload size

    add_header X-Content-Type-Options nosniff always;   # stop MIME sniffing
    add_header X-Frame-Options DENY always;             # clickjacking guard
    add_header Referrer-Policy strict-origin-when-cross-origin always;

    location /api/ {                          # Node.js API
        proxy_pass http://node_api;           # no trailing slash: URI passed unchanged
        proxy_http_version 1.1;               # required for keepalive/websocket
        proxy_set_header Connection $connection_upgrade;  # websocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 5s;             # fail fast if backend is down
        proxy_read_timeout 60s;               # max wait for response
    }

    location /ml/ {                           # FastAPI service
        proxy_pass http://fastapi_ml/;        # trailing slash strips the /ml/ prefix
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;              # model calls can be slow
    }

    location / {                              # React static build
        root /usr/share/nginx/html;
        try_files $uri /index.html;           # SPA fallback
    }
}
```

```yaml
# docker-compose.yml -- private backend network
services:
  nginx:
    image: nginx:1.27-alpine
    restart: unless-stopped
    ports: ["80:80"]
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./web/dist:/usr/share/nginx/html:ro   # React build output
    networks: [edge, backend]                 # sees both networks
    depends_on:
      api: { condition: service_healthy }     # wait until API reports healthy
  api:
    build: ./api
    restart: unless-stopped
    networks: [backend]                       # NOT on the edge network
    healthcheck:
      test: ["CMD", "node", "-e", "fetch('http://127.0.0.1:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]
      interval: 15s
      timeout: 3s
      retries: 3
  ml:
    build: ./fastapi
    restart: unless-stopped
    networks: [backend]
networks:
  edge: {}                                    # public-facing network
  backend:
    internal: true                            # no outbound internet from this network
```

Note: `internal: true` blocks outbound internet for backends; remove it if your API must call external services (e.g. payment APIs) or put those services on a second network. Not run locally (no Docker daemon here); YAML syntax was checked.

---

## 🟠 My Stack Integration
- Node.js on 3000 -> `/api/`, FastAPI on 8000 -> `/ml/`, React build served from Nginx itself.
- Express behind a proxy must set `app.set('trust proxy', 1)` to see the real client IP and `https` scheme.
- FastAPI with uvicorn: run `uvicorn app:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*'` only when traffic arrives solely via Nginx on a private network.

```yaml
# FastAPI service command in your compose file
  ml:
    build: ./fastapi
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]  # honour X-Forwarded-*
    networks: [backend]
```

Security: backends never publish ports; trust forwarded headers only from Nginx; set `client_max_body_size`; add rate limits (`limit_req_zone`) on login routes.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `proxy_pass http://localhost:3000;` - inside the nginx container, localhost is Nginx itself.
✅ Correct: Use the service name: `proxy_pass http://api:3000;`.

❌ Mistake 2: Publishing `3000:3000` on the API "just for testing" and forgetting it.
✅ Correct: Use `expose` or no ports at all; test via Nginx or `docker exec`.

❌ Mistake 3: Wrong trailing slash: `location /ml/ { proxy_pass http://fastapi_ml; }` sends `/ml/x` upstream, not `/x`.
✅ Correct: Decide intentionally: with `proxy_pass http://fastapi_ml/;` the prefix is stripped.

❌ Mistake 4: Not forwarding `Host` and `X-Forwarded-Proto`, so redirects and cookies break.
✅ Correct: Always set those headers.

---

## 🧠 Tricky Interview Question
Nginx starts, then 502 Bad Gateway appears right after `docker compose up`, but works after 20 seconds. Why, and how do you fix it?

Answer: `depends_on` only orders container start, not readiness. Nginx resolves `api` at startup (if the container is not in DNS yet Nginx may even fail with "host not found in upstream") and the Node process is still booting, so the first requests get connection refused (502). Fix: add a healthcheck and `depends_on: condition: service_healthy`, use `restart: unless-stopped`, and where needed use `resolver 127.0.0.11 valid=10s;` with a variable in `proxy_pass` so DNS is re-resolved at request time.

---

## ⚫ Interview Questions + Answers

Q1: Forward proxy vs reverse proxy?
A1: A forward proxy sits in front of clients (hides clients, e.g. corporate proxy). A reverse proxy sits in front of servers (hides and protects servers, adds TLS/caching/balancing).

Q2: Why use the service name and not an IP?
A2: Container IPs change on every recreate. Compose gives each service a DNS name on the network via Docker's embedded DNS.

Q3: What does `proxy_set_header Host $host` do?
A3: Preserves the client's original Host header; otherwise Nginx sends `Host: api:3000` and the backend generates wrong URLs/virtual-host matches.

Q4: How do you proxy WebSockets?
A4: Use HTTP/1.1 and forward `Upgrade` and `Connection` headers (the `map` shown above), and increase `proxy_read_timeout`.

Q5: 502 vs 504?
A5: 502 means Nginx could not get a valid response (backend down/refused/crashed). 504 means the backend did not answer within the timeout.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multiple services share one domain and one public IP.
- You want TLS, compression and headers in one place.
- You must hide internal topology.

❌ Avoid when:
- A managed load balancer (AWS ALB) already does routing and you have a single service; an extra hop adds little.
- Ultra-low-latency raw TCP traffic (use `stream` module or L4 LB instead).

---

## 📊 Visual Diagram
```
 Browser
   | https://app.example.com
   v
+------------- VPS ---------------------------------+
| [edge network]                                    |
|   nginx :80/:443  (only published ports)          |
|     | location /api/ -> proxy_pass http://api:3000|
|     | location /ml/  -> proxy_pass http://ml:8000 |
|     | location /     -> static React (try_files)  |
| [backend network - internal]                      |
|   api (Node.js 3000)        ml (FastAPI 8000)     |
+---------------------------------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Reverse proxy | Server that forwards client requests to backends | बैकएंड के आगे का proxy |
| `proxy_pass` | Directive naming the upstream | upstream बताने वाला directive |
| Upstream | Group of backend servers | बैकएंड servers का समूह |
| X-Forwarded-For | Header with original client IP chain | असली client IP |
| 502 Bad Gateway | Backend unreachable/invalid | backend नहीं मिला |
| Embedded DNS | Docker resolver at 127.0.0.11 | Docker का DNS |

---

## ⚡ 3-Line Summary
English: Nginx receives public traffic and forwards it to private containers by service name.
It adds headers, timeouts and WebSocket support, and hides the backends.
Mind trailing slashes, readiness and trusted forwarded headers.
Hindi: Nginx public traffic लेकर उसे service name से private containers तक forward करता है।
यह headers, timeouts और WebSocket support जोड़ता है और backends को छुपाता है।
Trailing slash, readiness और trusted forwarded headers का ध्यान रखें।

---

## ➡️ Next Topic
403. Nginx Load Balancer in Docker - one proxied container is a single point of failure; next we spread traffic across several replicas.
