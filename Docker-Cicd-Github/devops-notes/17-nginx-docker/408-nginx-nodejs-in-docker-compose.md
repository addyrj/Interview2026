# 408. Nginx + Node.js in Docker Compose
# हिंदी में: Docker Compose में Nginx + Node.js

---

## 🔵 Simple Definition (English)
This is the standard production layout for a Node.js (Express) API: a **Node.js container** that listens only on the private network and an **Nginx container** in front that handles public traffic, TLS, compression, rate limiting and static files. Docker Compose defines and starts both together.

## 🔵 सरल परिभाषा (Hindi)
यह Node.js (Express) API का standard production layout है: एक **Node.js container** जो सिर्फ private network पर सुनता है और उसके आगे **Nginx container** जो public traffic, TLS, compression, rate limiting और static files संभालता है। Docker Compose दोनों को साथ define और start करता है।

---

## 🔴 Problem it Solves
- Running `node server.js` directly on port 80 needs root and exposes Node to slow-client attacks.
- Node should not serve gzip/static/TLS; it wastes the single event loop.
- Without Compose, you start containers by hand with long `docker run` flags and wrong start order.

## 🔴 यह क्यों बना? (Hindi)
- `node server.js` को सीधे port 80 पर चलाना root माँगता है और Node को slow-client attacks के लिए खुला छोड़ता है।
- Node को gzip/static/TLS नहीं करना चाहिए; इससे single event loop बर्बाद होता है।
- Compose के बिना लंबे `docker run` flags और गलत start order के साथ हाथ से containers चलाने पड़ते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build the Node image (multi-stage, non-root user)
Step 2 → Compose creates a private network; services get DNS names
Step 3 → api: HEALTHCHECK /health; nginx waits until healthy
Step 4 → Browser -> nginx:80/443 -> proxy_pass http://api:3000
Step 5 → Express uses trust proxy to read real IP / https
Step 6 → Graceful shutdown: docker stop sends SIGTERM -> Node closes
         the server -> in-flight requests finish
Step 7 → CI/CD: docker compose pull && up -d, then nginx reload
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Node image build करो (multi-stage, non-root user)
Step 2 → Compose private network बनाता है; services को DNS नाम मिलते हैं
Step 3 → api: HEALTHCHECK /health; nginx healthy होने तक इंतज़ार करता है
Step 4 → Browser -> nginx:80/443 -> proxy_pass http://api:3000
Step 5 → Express असली IP / https पढ़ने के लिए trust proxy इस्तेमाल करता है
Step 6 → Graceful shutdown: docker stop SIGTERM भेजता है -> Node server
         बंद करता है -> चल रही requests पूरी होती हैं
Step 7 → CI/CD: docker compose pull && up -d, फिर nginx reload
```

---

## 🟡 Real World Example
A Razorpay-style payment webhook receiver is a small Express app. Nginx limits requests to 10/s per IP, caps body size to 1 MB, and only forwards `/webhooks/` to Node. Attackers hitting `/wp-admin` or sending 500 MB bodies never touch Node.

## 🟡 Real Example Hindi mein
Razorpay जैसा payment webhook receiver एक छोटा Express app है। Nginx हर IP को 10 requests/sec तक सीमित करता है, body 1 MB तक रखता है, और सिर्फ `/webhooks/` Node तक भेजता है। `/wp-admin` या 500 MB body भेजने वाले attackers Node तक पहुँचते ही नहीं।

---

## 💻 Code / Config Example — Basic

```javascript
// api/server.js -- minimal Express app (CommonJS)
const express = require('express');                 // web framework
const app = express();                              // create app
app.set('trust proxy', 1);                          // trust ONE proxy hop (our nginx)
app.get('/health', (req, res) => res.json({ ok: true }));        // health endpoint
app.get('/api/ip', (req, res) => res.json({ ip: req.ip, secure: req.secure }));  // shows real IP
const server = app.listen(3000, '0.0.0.0', () => console.log('api on 3000')); // bind all ifaces in container
process.on('SIGTERM', () => server.close(() => process.exit(0)));  // graceful stop
```

```dockerfile
# api/Dockerfile -- simple single-stage image
FROM node:20-alpine
# base image with Node 20 (example tag; update to current LTS)
WORKDIR /app
# working directory inside image
COPY package*.json ./
# copy manifests first for layer caching
RUN npm ci --omit=dev
# install production dependencies exactly from lockfile
COPY . .
# copy source code
USER node
# drop root privileges (node user exists in official image)
EXPOSE 3000
# document port (does not publish)
CMD ["node", "server.js"]
# start app; exec form so SIGTERM reaches node
```

```yaml
# docker-compose.yml -- basic
services:
  nginx:
    image: nginx:1.27-alpine
    ports: ["80:80"]                                  # public
    volumes: ["./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro"]
    depends_on: [api]
  api:
    build: ./api                                      # builds Dockerfile above
    expose: ["3000"]                                  # private only
```

## 💻 Code / Config Example — Advanced

```dockerfile
# api/Dockerfile -- multi-stage, production
FROM node:20-alpine AS deps
# stage 1: install dependencies
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
# only production deps end up in final image
FROM node:20-alpine AS runner
# stage 2: small runtime image
ENV NODE_ENV=production
# enables Express/Node production optimisations
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
# take deps from stage 1
COPY . .
# copy source (use .dockerignore to exclude node_modules, .env, .git)
USER node
# non-root
EXPOSE 3000
HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
# healthcheck using node itself (alpine has no curl by default); fetch needs Node 18+
CMD ["node", "server.js"]
```

```nginx
# nginx/default.conf -- rate limit, gzip, headers, proxy to Node
limit_req_zone $binary_remote_addr zone=api_rl:10m rate=10r/s;   # 10 req/s per IP, 10MB state

server {
    listen 80;
    server_name app.example.com;
    server_tokens off;                                 # hide version
    client_max_body_size 1m;                           # small bodies only
    gzip on;                                           # compress responses
    gzip_types application/json text/css application/javascript;  # which types

    location /api/ {
        limit_req zone=api_rl burst=20 nodelay;        # allow bursts, reject flood with 503
        proxy_pass http://api:3000;                    # to Node container
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
    }
    location = /health { proxy_pass http://api:3000/health; access_log off; }  # for uptime monitors
}
```

```yaml
# docker-compose.yml -- production-ish
services:
  nginx:
    image: nginx:1.27-alpine
    restart: unless-stopped
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      api: { condition: service_healthy }              # wait for health
    networks: [edge, backend]
  api:
    build: { context: ./api, target: runner }          # choose final stage
    restart: unless-stopped
    env_file: ./api/.env.production                    # secrets from file on server, not in Git
    environment:
      NODE_ENV: production
    read_only: true                                    # immutable FS
    tmpfs: ["/tmp"]                                    # writable temp
    cap_drop: [ALL]                                    # no extra capabilities
    security_opt: ["no-new-privileges:true"]
    mem_limit: 512m                                    # memory cap
    init: true                                         # tini as PID1 reaps zombies
    networks: [backend]
  db:
    image: postgres:16-alpine                          # example DB; or Mongo
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_pass     # secret not env text
    secrets: [db_pass]
    volumes: [pgdata:/var/lib/postgresql/data]         # persistent data
    networks: [backend]
secrets:
  db_pass: { file: ./secrets/db_pass.txt }             # keep out of Git
volumes:
  pgdata: {}
networks:
  edge: {}
  backend: {}
```

Verified: YAML parse and `node --check` on server.js, Dockerfile instruction sanity. Not built or run (no Docker daemon). The `db` service is optional; `.env.production` and `secrets/` must be created on the server.

---

## 🟠 My Stack Integration
- On Hostinger VPS: clone repo into `/opt/app`, create `.env.production`, run `docker compose up -d --build`.
- GitHub Actions: build image, push to GHCR/ECR, VPS runs `docker compose pull && docker compose up -d`.
- Add `nginx -t` to CI (405). Use the topic 404/407 TLS config for HTTPS.
- For clustering across CPU cores run more replicas (403) instead of PM2 in the container.

```bash
# Smoke test after deploy (works from your laptop or CI)
curl -fsS https://app.example.com/health          # should print {"ok":true}
curl -s https://app.example.com/api/ip            # secure:true proves trust proxy works
```

Security: non-root user, read-only FS, capabilities dropped, no published Node port, secrets via files, rate-limit and body limit at the edge, `npm audit`/image scan in CI.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Express listens on `127.0.0.1` only, so Nginx gets connection refused.
✅ Correct: Bind `0.0.0.0` inside the container.

❌ Mistake 2: `CMD npm start` (shell form), so SIGTERM goes to the shell and Node is killed after 10s.
✅ Correct: `CMD ["node","server.js"]` with `init: true`.

❌ Mistake 3: Forgetting `trust proxy`, so every request appears from the Nginx IP and rate limits per-user fail.
✅ Correct: `app.set('trust proxy', 1)`.

❌ Mistake 4: Copying `.env` into the image.
✅ Correct: `.dockerignore` it and inject at runtime.

---

## 🧠 Tricky Interview Question
Nginx rate limit is set to 10 r/s per IP, yet all users get 503 together during a small spike. What happened?

Answer: `$binary_remote_addr` is the IP that connected to Nginx. If Nginx itself sits behind another proxy/CDN (Cloudflare, ALB), every request shows the proxy's IP, so all users share one bucket. Fix with the `realip` module: `set_real_ip_from <proxy range>; real_ip_header X-Forwarded-For;` (only trusted ranges), or key the limit on a verified header.

---

## ⚫ Interview Questions + Answers

Q1: `expose` vs `ports`?
A1: `expose` documents the port for other containers on the network only; `ports` publishes it on the host.

Q2: Why is `depends_on` not enough?
A2: It only orders startup; use `condition: service_healthy` with a healthcheck for readiness.

Q3: Why exec-form CMD?
A3: The process becomes PID 1 and receives SIGTERM directly, enabling graceful shutdown.

Q4: Should Nginx serve static files or Node?
A4: Nginx; it is far more efficient. Node handles dynamic API logic only.

Q5: How to do zero-downtime updates here?
A5: Run 2+ replicas with health checks and update one at a time, or use blue/green (412).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Single VPS or small team running an Express/Nest API.
- You need TLS, rate-limits and static files at the edge.

❌ Avoid when:
- Serverless or managed container platforms already supply an ingress layer.

---

## 📊 Visual Diagram
```
 Client --HTTPS--> [nginx :443]  rate-limit, gzip, TLS, headers
                       |  proxy_pass (private "backend" net)
                       v
                  [api: Node/Express :3000]  non-root, read-only
                       |
                       v
                  [db: Postgres/Mongo]  volume pgdata
 only nginx publishes ports; api & db are unreachable from internet
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| trust proxy | Express trusts forwarded headers | proxy headers पर भरोसा |
| Rate limiting | Cap requests per time | requests की सीमा |
| Healthcheck | Readiness probe | सेहत जाँच |
| Graceful shutdown | Finish work before exit | सही तरह से बंद होना |
| PID 1 | First process in container | container की पहली process |
| `expose` | Port visible inside network only | सिर्फ network में |

---

## ⚡ 3-Line Summary
English: Nginx fronts a private Node.js container in Compose and handles TLS, limits and static files.
Use healthchecks, trust proxy, exec-form CMD and a non-root read-only API container.
Only Nginx publishes ports.
Hindi: Compose में Nginx private Node.js container के आगे TLS, limits और static files संभालता है।
Healthcheck, trust proxy, exec-form CMD और non-root read-only API container इस्तेमाल करो।
सिर्फ Nginx ports publish करता है।

---

## ➡️ Next Topic
409. Nginx + FastAPI in Docker Compose - the same pattern for your Python service.
