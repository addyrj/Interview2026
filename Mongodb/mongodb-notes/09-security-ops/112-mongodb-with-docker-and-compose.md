# 112. MongoDB with Docker and Docker Compose
# हिंदी में: Docker और Docker Compose के साथ MongoDB

---

## 🔵 Simple Definition (English)
**Docker** packages MongoDB (the official `mongo` image) into a container so every developer and server runs the identical version with one command. **Docker Compose** describes multi-container setups (app + MongoDB + mongo-express) in one `docker-compose.yml`. Key ideas: **port mapping** (`27017:27017`), **volumes** for persistent data (`/data/db`), **environment variables** to create the root user (`MONGO_INITDB_ROOT_USERNAME/PASSWORD`), **init scripts** (`/docker-entrypoint-initdb.d`), **healthchecks**, and the Compose **network** where the app reaches the DB by service name (`mongodb://mongo:27017`).

## 🔵 सरल परिभाषा (Hindi)
**Docker** MongoDB (official `mongo` image) को container में पैक करता है ताकि हर developer और server एक command से एक जैसा version चलाए। **Docker Compose** कई containers (app + MongoDB + mongo-express) को एक `docker-compose.yml` में बताता है। मुख्य बातें: **port mapping** (`27017:27017`), persistent data के लिए **volumes** (`/data/db`), root user बनाने के लिए **environment variables** (`MONGO_INITDB_ROOT_USERNAME/PASSWORD`), **init scripts** (`/docker-entrypoint-initdb.d`), **healthchecks**, और Compose **network** जिसमें app DB को service name (`mongodb://mongo:27017`) से पहुँचता है।

---

## 🔴 Problem it Solves
"Works on my machine": different MongoDB versions, manual installs, leftover data and port conflicts waste time. Docker gives disposable, reproducible databases: start a fresh one for tests, pin version 8.0 in dev and prod, spin up a 3-node replica set for transaction testing in seconds, and throw it away. Compose also makes the whole stack (API + DB + cache) start with `docker compose up`.

## 🔴 यह क्यों बना? (Hindi)
"मेरी machine पर चलता है": अलग MongoDB versions, manual install, बचा हुआ data और port conflicts समय खाते हैं। Docker disposable, reproducible databases देता है: tests के लिए नया DB, dev और prod में version 8.0 pin, transactions test के लिए सेकंडों में 3-node replica set, और फिर फेंक दो। Compose पूरा stack (API + DB + cache) `docker compose up` से चालू करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `docker run -d --name mongo -p 27017:27017 -v mongo-data:/data/db mongo:8.0` pulls the image and starts `mongod`.
Step 2 → The **volume** `mongo-data` stores `/data/db`; deleting the container keeps the data. Without a volume the data dies with the container.
Step 3 → On the **first start with an empty data dir**, the entrypoint reads `MONGO_INITDB_ROOT_USERNAME/PASSWORD` (creates the root user and starts with `--auth`) and runs `*.js/*.sh` files in `/docker-entrypoint-initdb.d` (seed users, collections, indexes). These do nothing on later starts.
Step 4 → In Compose, services share a **network**; the app uses hostname `mongo` (service name), NOT `localhost` (inside the app container `localhost` is the app itself).
Step 5 → `depends_on` with `condition: service_healthy` + a `healthcheck` (`mongosh --eval "db.adminCommand('ping')"`) makes the app wait until MongoDB is ready.
Step 6 → For a **replica set** (needed for transactions/change streams) start with `--replSet rs0` and run `rs.initiate()` once (via healthcheck or init script).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `docker run -d --name mongo -p 27017:27017 -v mongo-data:/data/db mongo:8.0` image pull करके `mongod` चालू करता है।
Step 2 → **Volume** `mongo-data` में `/data/db` रहता है; container हटाने पर भी data बचता है। Volume के बिना data container के साथ खत्म।
Step 3 → **खाली data dir के साथ पहली बार start** पर entrypoint `MONGO_INITDB_ROOT_USERNAME/PASSWORD` पढ़कर root user बनाता है (`--auth` के साथ चालू) और `/docker-entrypoint-initdb.d` की `*.js/*.sh` files चलाता है (users, collections, indexes seed)। बाद के starts पर ये नहीं चलतीं।
Step 4 → Compose में services एक **network** share करती हैं; app hostname `mongo` (service name) इस्तेमाल करे, `localhost` नहीं (app container में `localhost` खुद app है)।
Step 5 → `healthcheck` + `depends_on: condition: service_healthy` से app तब तक रुकता है जब तक MongoDB तैयार न हो।
Step 6 → **Replica set** (transactions/change streams) के लिए `--replSet rs0` और एक बार `rs.initiate()`।

---

## 🟡 Real World Example
A **Razorpay**-style team has `payments-api` (Node) and MongoDB. New hires run `docker compose up` and in 30 seconds get the API on `:3000`, a seeded MongoDB with test merchants (via an init script), and **mongo-express** on `:8081` to browse data. CI uses the same compose file with `docker compose down -v` after tests to guarantee a clean slate. For transaction-heavy features a second compose profile starts a single-node replica set.

## 🟡 Real Example Hindi mein
**Razorpay** जैसी team में `payments-api` (Node) और MongoDB है। नए सदस्य `docker compose up` चलाते हैं और 30 सेकंड में API `:3000` पर, init script से seed MongoDB (test merchants) और डेटा देखने के लिए `:8081` पर **mongo-express** मिलता है। CI उसी compose file से tests के बाद `docker compose down -v` करके साफ slate पक्का करता है। Transaction वाले features के लिए दूसरा compose profile single-node replica set चलाता है।

---

## 💻 Code Example — Basic

```bash
# Docker CLI (syntax-checked; the Docker daemon was not running in the verification
# environment, so image pulls were not executed. The same mongod flags were verified natively on 8.0.4.)

# -p host:container port mapping; -v named volume keeps data after container removal;
# MONGO_INITDB_* create the root user on first start (auth enabled); pin the version, avoid :latest
docker run -d --name mongo \
  -p 27017:27017 \
  -v mongo-data:/data/db \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=secret \
  mongo:8.0

# Connect from the host
mongosh "mongodb://admin:secret@localhost:27017/?authSource=admin"

# Inside the container
docker exec -it mongo mongosh -u admin -p secret --authenticationDatabase admin

docker logs -f mongo          # follow logs
docker stop mongo && docker rm mongo   # remove container; volume 'mongo-data' remains
docker volume rm mongo-data            # this DELETES the data
```

## 💻 Code Example — Advanced

```yaml
# docker-compose.yml — API + MongoDB (single-node replica set) + mongo-express
services:
  mongo:
    image: mongo:8.0
    container_name: mongo
    command: ["--replSet", "rs0", "--bind_ip_all"]   # replica set needed for transactions/change streams
    ports: ["27017:27017"]
    environment:
      MONGO_INITDB_DATABASE: shop                    # DB used by init scripts
    volumes:
      - mongo-data:/data/db                          # persistence
      - ./init:/docker-entrypoint-initdb.d:ro        # *.js seed scripts (first start only)
    healthcheck:                                     # also initiates the replica set once
      test: >
        mongosh --quiet --eval "try { rs.status().ok } catch (e) { rs.initiate({_id:'rs0',members:[{_id:0,host:'mongo:27017'}]}).ok }"
      interval: 5s
      timeout: 10s
      retries: 10
      start_period: 10s
    restart: unless-stopped

  api:
    build: .                                         # Dockerfile of the Node app
    ports: ["3000:3000"]
    environment:
      # service name 'mongo' replaces localhost; replicaSet name must match
      MONGO_URI: mongodb://mongo:27017/shop?replicaSet=rs0
    depends_on:
      mongo: { condition: service_healthy }          # start API only after Mongo is healthy

  mongo-express:                                     # optional web UI (dev only!)
    image: mongo-express
    ports: ["8081:8081"]
    environment:
      ME_CONFIG_MONGODB_URL: mongodb://mongo:27017/?replicaSet=rs0
    depends_on: [mongo]

volumes:
  mongo-data:
```

```javascript
// init/01-seed.js — runs once on first start (mongosh syntax)
db = db.getSiblingDB('shop');                        // MONGO_INITDB_DATABASE
db.createCollection('orders');                       // create collection
db.orders.createIndex({ userId: 1, createdAt: -1 }); // index for common query
db.orders.insertMany([{ item: 'Biryani', amt: 250 }, { item: 'Naan', amt: 40 }]); // seed data
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// app.js — reads the URI injected by compose; retries until Mongo is reachable
const express = require('express');
const mongoose = require('mongoose');

const uri = process.env.MONGO_URI || 'mongodb://localhost:27017/shop'; // localhost only for non-docker dev
const app = express();

mongoose.connect(uri, { serverSelectionTimeoutMS: 10000 })   // wait up to 10 s for a primary
  .then(() => app.listen(3000, () => console.log('API up, Mongo connected')))
  .catch((e) => { console.error('Mongo connect failed', e.message); process.exit(1); }); // let Docker restart us

app.get('/health', (req, res) => res.json({ db: mongoose.connection.readyState === 1 }));
```

```dockerfile
# Dockerfile for the Node API
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev          # reproducible install
COPY . .
USER node                      # don't run as root
CMD ["node", "app.js"]
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting the volume
```bash
# Wrong: data lives in the container layer; `docker rm` deletes everything
docker run -d mongo:8.0
# Right
docker run -d -v mongo-data:/data/db mongo:8.0
```
❌ Mistake 2: Using `localhost` in the app container.
```text
Wrong: MONGO_URI=mongodb://localhost:27017/shop   (points to the API container itself)
Right: MONGO_URI=mongodb://mongo:27017/shop        (Compose service name)
```
❌ Mistake 3: Expecting `MONGO_INITDB_*` or init scripts to run on an existing volume. They run only when `/data/db` is empty — change credentials by `docker compose down -v` (dev) or via `createUser`.

❌ Mistake 4: Publishing `27017` to `0.0.0.0` on a server without auth. Docker bypasses ufw rules via iptables. ✅ Bind `127.0.0.1:27017:27017` or don't publish the port; keep auth on.

❌ Mistake 5: `mongo:latest` in production — an unplanned major upgrade can break the data files (feature compatibility version). Pin tags.

---

## 🧠 Tricky Interview Question
**Q:** Your Compose `api` service connects to `mongodb://mongo:27017/shop?replicaSet=rs0` but you get `ReplicaSetNoPrimary` / hostname `localhost:27017` errors from outside Docker (your laptop), while it works inside the network. Why?

**Answer:** A replica set advertises the **member hostnames stored in its config** (`host: 'mongo:27017'`). Inside the Compose network `mongo` resolves, so it works. From the host machine, the driver discovers the set via the seed but then tries to connect to `mongo:27017`, which doesn't resolve on the laptop, so it never finds a primary. Fixes: add `127.0.0.1 mongo` to `/etc/hosts`, use `directConnection=true` for a single node, or configure the member host as `localhost:27017` for dev only.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a bind mount and a named volume for `/data/db`?
A1: Named volumes are managed by Docker (portable, correct permissions, faster on macOS/Windows). Bind mounts map a host folder (convenient for init scripts/config) but can have permission and performance issues for the data directory.

Q2: How do you create application users automatically?
A2: Put a `.js` script in `/docker-entrypoint-initdb.d` that runs `db.createUser({...})`; it executes once, on a fresh data dir, as the root user.

Q3: How to run a replica set in Docker?
A3: `--replSet rs0`, then `rs.initiate()` with a member host reachable by clients (service name), optionally a keyFile when auth is enabled. Needed for transactions and change streams.

Q4: Why is `depends_on` alone not enough?
A4: It only waits for the container to start, not for `mongod` to accept connections. Use `healthcheck` + `condition: service_healthy` and driver retry/`serverSelectionTimeoutMS`.

Q5: Should production databases run in Docker?
A5: Possible (with volumes, resource limits, pinned versions, backups, monitoring), but many teams prefer managed Atlas or Kubernetes operators; Docker is ideal for dev and CI.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Local dev, CI pipelines, demos, reproducible test databases, learning replica sets

✅ Production in containers when:
- You have orchestration (Kubernetes + operator), persistent storage and backups

❌ Avoid:
- Unpinned images, no volumes, public ports without auth, `mongo-express` exposed publicly

---

## 📊 Visual Diagram
```
docker compose up
──────────────────────────────────────────────────
 Host :3000 ─▶ ┌──────── compose network ─────────┐
 Host :8081 ─▶ │ api ──mongodb://mongo:27017──▶ mongo (rs0) │
 Host :27017─▶ │ mongo-express ───────────────▶     │       │
               └───────────────────────────────┬───┘
                                               ▼
                                   volume mongo-data → /data/db
 init scripts (/docker-entrypoint-initdb.d) run once on empty volume
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Image | Packaged MongoDB template | Packaged template |
| Container | Running instance of an image | Image का चलता instance |
| Volume | Persistent storage | स्थायी storage |
| Compose | Multi-container definition | कई containers की file |
| Healthcheck | Readiness probe | तैयार है या नहीं जाँच |
| Init script | Seed on first start | पहली बार का seed |
| Service name | DNS name inside network | Network में DNS नाम |

---

## ⚡ 3-Line Summary
English:
1. Run MongoDB with `docker run`/Compose using a pinned `mongo` image, a volume at `/data/db`, and `MONGO_INITDB_*` for the root user.
2. Inside Compose, connect via the service name, not `localhost`; use healthchecks and init scripts.
3. Replica sets need `--replSet` + `rs.initiate()`; never expose an unauthenticated port.

Hindi:
1. Pinned `mongo` image, `/data/db` पर volume और root user के लिए `MONGO_INITDB_*` के साथ `docker run`/Compose से MongoDB चलाओ।
2. Compose के अंदर service name से connect करो, `localhost` से नहीं; healthchecks और init scripts इस्तेमाल करो।
3. Replica sets के लिए `--replSet` + `rs.initiate()`; बिना authentication वाला port कभी expose मत करो।

---

## ➡️ Next Topic
**113. MongoDB in CI/CD (testing with mongodb-memory-server)** — Fast isolated database tests.
