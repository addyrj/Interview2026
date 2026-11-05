---

# 209. React + Node.js + DB Compose Example
# हिंदी में: React + Node.js + DB Compose उदाहरण

---

## 🔵 Simple Definition (English)
A **React + Node.js + DB Compose example** is one `docker-compose.yml` that starts three services together: a React frontend (served by Nginx), a Node.js/Express API, and a database (PostgreSQL here). One command (`docker compose up`) gives you the whole app on any machine.

## 🔵 सरल परिभाषा (Hindi)
**React + Node.js + DB Compose example** एक ही `docker-compose.yml` है जो तीन services साथ में चलाती है: React frontend (Nginx से serve), Node.js/Express API, और database (यहाँ PostgreSQL)। एक command (`docker compose up`) से पूरा app किसी भी machine पर चल जाता है।

---

## 🔴 Problem it Solves
Without Compose, a new developer must install Node, Postgres, run the API, run `npm start` for React, set env variables by hand, and hope versions match. "Works on my machine" bugs appear. Starting containers by hand with five `docker run` commands is error-prone: wrong network, wrong order (API starts before DB is ready), forgotten volume (data lost).

## 🔴 यह क्यों बना? (Hindi)
Compose के बिना नए developer को Node, Postgres install करना, API चलाना, React के लिए `npm start`, env variables हाथ से set करना पड़ता है, और versions match होने की उम्मीद करनी पड़ती है। "मेरी machine पर चल रहा है" वाले bugs आते हैं। पाँच `docker run` commands हाथ से चलाना गलतियों से भरा है: गलत network, गलत order (DB ready होने से पहले API start), volume भूल गए तो data गया।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write Dockerfile for api (Node) and web (React build -> Nginx)
Step 2 → Write docker-compose.yml with 3 services: db, api, web
Step 3 → Compose creates one private network; services reach each other by NAME (db, api)
Step 4 → depends_on + healthcheck makes api wait until Postgres is healthy
Step 5 → Named volume keeps DB data after container is removed
Step 6 → Only web publishes port 80/8080 to host; db is never exposed
Step 7 → docker compose up -d --build starts everything
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → api (Node) और web (React build -> Nginx) के लिए Dockerfile लिखो
Step 2 → 3 services वाली docker-compose.yml लिखो: db, api, web
Step 3 → Compose एक private network बनाता है; services एक-दूसरे को NAME से पाती हैं (db, api)
Step 4 → depends_on + healthcheck से api तब तक रुकता है जब तक Postgres healthy न हो
Step 5 → Named volume से container हटने पर भी DB data बचा रहता है
Step 6 → सिर्फ web host port publish करता है; db कभी expose नहीं होता
Step 7 → docker compose up -d --build से सब कुछ start
```

---

## 🟡 Real World Example
A small startup builds an internal **order-tracking dashboard** (like a mini Swiggy ops panel). React shows the orders table, Express exposes `/api/orders`, Postgres stores orders. On the team's single AWS EC2 / VPS box they run exactly this compose file. Nginx inside the `web` container serves the React build and proxies `/api/` to the `api` service, so the browser talks to only one origin (no CORS headaches).

## 🟡 Real Example Hindi mein
एक छोटा startup **order-tracking dashboard** बनाता है (Swiggy के mini ops panel जैसा)। React orders table दिखाता है, Express `/api/orders` देता है, Postgres orders रखता है। Team के एक AWS EC2 / VPS पर यही compose file चलती है। `web` container के अंदर Nginx React build serve करता है और `/api/` को `api` service पर proxy करता है, इसलिए browser सिर्फ एक origin से बात करता है (CORS की दिक्कत नहीं)।

---

## 💻 Code / Config Example — Basic

Folder layout:
```
project/
  docker-compose.yml
  api/    Dockerfile, package.json, server.js
  web/    Dockerfile, nginx.conf, (React source)
```

```yaml
# docker-compose.yml  (BASIC)
services:                          # top-level list of containers
  db:                              # service name = hostname "db" on the network
    image: postgres:16-alpine      # official Postgres image (example tag, update it)
    environment:                   # env vars read by the image on first start
      POSTGRES_USER: app           # DB user to create
      POSTGRES_PASSWORD: secret    # BASIC demo only; never hardcode in real use
      POSTGRES_DB: appdb           # DB to create
    volumes:                       # persist data
      - pgdata:/var/lib/postgresql/data   # named volume -> Postgres data dir

  api:                             # Node.js Express backend
    build: ./api                   # build image from api/Dockerfile
    environment:                   # config for the app
      DATABASE_URL: postgres://app:secret@db:5432/appdb  # host is "db", not localhost
      PORT: "3000"                 # port the API listens on
    depends_on:                    # start order
      - db                         # start db before api (does not wait for ready)

  web:                             # React build served by Nginx
    build: ./web                   # build image from web/Dockerfile
    ports:                         # publish to host
      - "8080:80"                  # host 8080 -> container 80
    depends_on:                    # start order
      - api                        # start api before web

volumes:                           # declare named volumes
  pgdata:                          # Docker manages this volume
```

```dockerfile
# api/Dockerfile (BASIC)
FROM node:20-alpine
# small Node base image (example tag)
WORKDIR /app
# all following commands run in /app
COPY package*.json ./
# copy manifests first so npm install layer is cached
RUN npm install --omit=dev
# install only production dependencies
COPY . .
# copy the app source
CMD ["node", "server.js"]
# start the API
```

```dockerfile
# web/Dockerfile (BASIC)
FROM node:20-alpine AS build
# stage 1: build React
WORKDIR /src
# working dir for the build
COPY package*.json ./
# copy manifests for caching
RUN npm ci
# clean install exact versions
COPY . .
# copy React source
RUN npm run build
# creates /src/build (CRA) or /src/dist (Vite)
FROM nginx:1.27-alpine
# stage 2: tiny runtime image
COPY --from=build /src/build /usr/share/nginx/html
# copy static files (change build -> dist for Vite)
COPY nginx.conf /etc/nginx/conf.d/default.conf
# our proxy + SPA config
```

```nginx
# web/nginx.conf
server {
    listen 80;                                   # listen on container port 80
    root /usr/share/nginx/html;                  # React build lives here
    location / {
        try_files $uri /index.html;              # SPA fallback for React Router
    }
    location /api/ {
        proxy_pass http://api:3000;              # "api" resolves via Compose DNS
        proxy_set_header Host $host;             # pass original host
        proxy_set_header X-Real-IP $remote_addr; # pass client IP
    }
}
```

---

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.yml  (ADVANCED, production-minded)
name: orders-app                       # project name (prefix for networks/volumes)

services:
  db:
    image: postgres:16-alpine          # pinned major version (example, update)
    restart: unless-stopped            # restart after crash/reboot, not after manual stop
    environment:
      POSTGRES_USER: app               # DB user
      POSTGRES_DB: appdb               # DB name
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password   # read password from a file (secret)
    secrets:
      - db_password                    # mount the secret into the container
    volumes:
      - pgdata:/var/lib/postgresql/data   # persistent data
    networks:
      - backend                        # db lives ONLY on the private backend network
    healthcheck:                       # tells Compose when DB is truly ready
      test: ["CMD-SHELL", "pg_isready -U app -d appdb"]   # exits 0 when accepting connections
      interval: 10s                    # check every 10 seconds
      timeout: 5s                      # each check must finish in 5s
      retries: 5                       # 5 failures -> unhealthy
      start_period: 10s                # grace time during boot
    deploy:
      resources:
        limits:
          memory: 512m                 # cap RAM so DB cannot starve the host

  api:
    build:
      context: ./api                   # build context folder
      dockerfile: Dockerfile           # Dockerfile name
    restart: unless-stopped            # auto restart
    environment:
      NODE_ENV: production             # enables Express/Node production optimisations
      PORT: "3000"                     # listen port
      DB_HOST: db                      # service name as hostname
      DB_USER: app                     # DB user
      DB_NAME: appdb                   # DB name
      DB_PASSWORD_FILE: /run/secrets/db_password   # app reads the password from this file
    secrets:
      - db_password                    # same secret shared with API
    depends_on:
      db:
        condition: service_healthy     # wait until db healthcheck passes
    networks:
      - backend                        # talks to db
      - frontend                       # talks to web
    healthcheck:
      test: ["CMD", "node", "-e", "fetch('http://localhost:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]   # Node 20 has fetch built in
      interval: 15s                    # poll every 15s
      timeout: 5s                      # fail if slower than 5s
      retries: 3                       # 3 strikes -> unhealthy
    read_only: true                    # root filesystem read-only (hardening)
    tmpfs:
      - /tmp                           # allow writes only in RAM /tmp
    cap_drop:
      - ALL                            # drop all Linux capabilities
    security_opt:
      - no-new-privileges:true         # block privilege escalation
    deploy:
      resources:
        limits:
          cpus: "0.50"                 # max half a CPU
          memory: 256m                 # max 256 MB RAM

  web:
    build: ./web                       # React + Nginx image
    restart: unless-stopped            # auto restart
    ports:
      - "127.0.0.1:8080:80"            # bind to localhost only; host Nginx / ALB does TLS
    depends_on:
      api:
        condition: service_healthy     # start after API is healthy
    networks:
      - frontend                       # web only sees api, never db

networks:
  frontend:                            # public-facing side
  backend:                             # private side
    internal: true                     # no outbound internet, no host access

secrets:
  db_password:
    file: ./secrets/db_password.txt    # local file, keep OUT of git (.gitignore)

volumes:
  pgdata:                              # persistent Postgres data
```

```javascript
// api/server.js  (minimal Express API matching the compose file)
const express = require('express');                 // web framework
const fs = require('fs');                           // to read secret file
const { Pool } = require('pg');                     // Postgres client (npm i express pg)

const pw = process.env.DB_PASSWORD_FILE             // prefer secret file
  ? fs.readFileSync(process.env.DB_PASSWORD_FILE, 'utf8').trim()
  : process.env.DB_PASSWORD;                        // fallback to env var
const pool = new Pool({                             // connection pool
  host: process.env.DB_HOST, user: process.env.DB_USER,
  database: process.env.DB_NAME, password: pw, port: 5432,
});
const app = express();                              // create app
app.get('/health', (_req, res) => res.json({ ok: true }));   // used by healthcheck
app.get('/api/orders', async (_req, res) => {       // example route
  const { rows } = await pool.query('SELECT now() AS ts');   // trivial query
  res.json(rows);                                   // send JSON
});
app.listen(process.env.PORT || 3000);               // start server
```

Note: configs were syntax-checked (YAML/JS parse), but the stack was not built or run locally because no Docker daemon was available. Image tags are examples; update them.

---

## 🟠 My Stack Integration
Your stack is Node.js/FastAPI + React + Nginx on a VPS/AWS. This example maps directly: the `api` service can be swapped for FastAPI (`uvicorn main:app --host 0.0.0.0`). On the VPS, a **host-level Nginx** terminates HTTPS (Let's Encrypt) and proxies to `127.0.0.1:8080`, while the container Nginx only serves static files and proxies `/api/`. On AWS, replace the `db` service with **RDS** and keep only `api` + `web`, injecting `DATABASE_URL` from SSM Parameter Store.

```yaml
# docker-compose.override.yml  -> local dev only (auto-merged by Compose)
services:
  api:
    build: ./api                        # same build
    command: npx nodemon server.js      # hot reload in dev
    volumes:
      - ./api:/app                      # bind mount source code
    ports:
      - "3000:3000"                     # expose API directly for debugging
    read_only: false                    # dev needs writes (overrides hardening)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `localhost` as the DB host inside the API container.
✅ Correct: Use the service name `db`. `localhost` inside a container means that container itself.

❌ Mistake 2: Assuming `depends_on: [db]` waits until Postgres is ready.
✅ Correct: Add a `healthcheck` on `db` and use `condition: service_healthy`.

❌ Mistake 3: Publishing `5432:5432` on a VPS public IP.
✅ Correct: Do not publish the DB port at all. Only `api` reaches it on the private network. Docker bypasses UFW rules, so a published port is really open.

❌ Mistake 4: Running `docker compose down -v` casually.
✅ Correct: `-v` deletes named volumes (your data). Use plain `down` unless you truly want a wipe.

❌ Mistake 5: Committing passwords in compose or `.env` to git.
✅ Correct: Use secrets files or CI secrets; add `secrets/` and `.env` to `.gitignore`.

---

## 🧠 Tricky Interview Question
**Q:** Your React app inside the browser calls `http://api:3000/orders` and fails with "ERR_NAME_NOT_RESOLVED", but the Node API can reach `db:5432` fine. Why?

**Answer:** The React code runs in the **user's browser**, not inside Docker. Only containers on the Compose network can resolve `api` and `db`. The browser must call a public URL. Fix: call a relative path like `/api/orders` and let the Nginx in the `web` container proxy to `http://api:3000`. (If React does Server-Side Rendering in a container, then server-side calls may use `api`, but browser calls cannot.)

---

## ⚫ Interview Questions + Answers

**Q1: How do services find each other in Compose?**
A1: Compose creates a default (or custom) network with built-in DNS. Each service name resolves to the container IP(s). So `db` and `api` work as hostnames.

**Q2: Why use a multi-stage Dockerfile for React?**
A2: The build stage needs Node and hundreds of MB of `node_modules`; the runtime only needs static files. Multi-stage copies just the build output into small Nginx, giving a ~50 MB image and a smaller attack surface.

**Q3: How do you persist DB data and how can you lose it?**
A3: Use a named volume (`pgdata`). You lose it with `docker compose down -v`, `docker volume rm`, or `docker system prune --volumes`. Also back it up with `pg_dump`; a volume is not a backup.

**Q4: What does `internal: true` on a network do?**
A4: It blocks external connectivity: containers on it can talk to each other, but cannot reach the internet or be reached from the host. Good for the DB network.

**Q5: How would you move this to production on AWS?**
A5: Push images to ECR, run `api` and `web` on ECS/EC2 or a VPS with Compose, use RDS for Postgres, put an ALB with ACM certificate in front, and keep secrets in Secrets Manager/SSM.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Local development of a multi-service app
- Single-server (one VPS / EC2) deployments, demos, internal tools
- CI integration tests that need a real DB

❌ Avoid when:
- You need multi-node high availability or auto-scaling (use Kubernetes/ECS)
- The DB holds critical data and you have no backup/replication plan (prefer managed RDS)

---

## 📊 Visual Diagram
```
 Browser
    |  HTTPS (host Nginx / ALB)
    v
+-----------------------------------------------+
| Docker host                                   |
|  frontend network          backend network    |
|  +---------+   /api/   +---------+  +-------+ |
|  |  web    |---------->|  api    |->|  db   | |
|  | (Nginx  |  :3000    | (Node)  |  |(Postg)| |
|  |  +React)|           +---------+  +---+---+ |
|  +----+----+                            |     |
|   127.0.0.1:8080                   [pgdata vol]|
+-----------------------------------------------+
   Only web is reachable from outside. db is private.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Service | One container definition in Compose | Compose में एक container की definition |
| Healthcheck | Command that tells if container is ready | Container तैयार है या नहीं जाँचने वाली command |
| Named volume | Docker-managed persistent storage | Docker द्वारा managed स्थायी storage |
| Internal network | Network without outside access | बिना बाहरी access वाला network |
| Reverse proxy | Server forwarding requests to backend | Requests को backend तक भेजने वाला server |

---

## ⚡ 3-Line Summary
English: One compose file runs React (Nginx), Node API and Postgres together.
Services talk by name on a private network; use healthchecks, volumes and secrets.
Expose only the web port; keep the DB private and never hardcode passwords.

Hindi: एक compose file React (Nginx), Node API और Postgres साथ चलाती है।
Services private network पर नाम से बात करती हैं; healthcheck, volume और secrets इस्तेमाल करो।
सिर्फ web port expose करो; DB को private रखो और password hardcode मत करो।

---

## ➡️ Next Topic
**210. Full Stack Compose Example**: now we combine everything (FastAPI, Redis, Nginx, workers) into one complete multi-service production-style stack.

---
