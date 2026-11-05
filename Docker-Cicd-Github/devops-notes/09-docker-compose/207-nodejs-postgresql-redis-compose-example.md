# 207. Node.js + PostgreSQL + Redis Compose Example
# हिंदी में: Node.js + PostgreSQL + Redis Compose का पूरा उदाहरण

---

## 🔵 Simple Definition (English)
This is a complete, copy-paste Compose stack for the most common backend: a Node.js (Express) API that stores data in PostgreSQL and caches reads in Redis, with healthchecks, a non-root image and persistent volumes.

## 🔵 सरल परिभाषा (Hindi)
यह सबसे आम backend का पूरा, copy-paste योग्य Compose stack है: Node.js (Express) API जो डेटा PostgreSQL में रखती है और reads को Redis में cache करती है, healthchecks, non-root image और persistent volumes के साथ।

---

## 🔴 Problem it Solves
Beginners can run each piece alone but get stuck on wiring: wrong hostnames (`localhost` instead of service names), API starting before Postgres is ready, lost data, and missing cache invalidation. One working reference removes guesswork.

## 🔴 यह क्यों बना? (Hindi)
Beginners हर हिस्सा अलग-अलग चला लेते हैं पर जोड़ने में अटकते हैं: गलत hostnames (service name की जगह `localhost`), Postgres तैयार होने से पहले API का चालू होना, खोया हुआ data, और cache invalidation का अभाव। एक चलता हुआ reference अंदाज़े हटा देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Browser/Client calls GET /items/1 on the API (port 3000)
Step 2 → API asks Redis (host "redis", port 6379) for key item:1
Step 3 → Cache hit  -> return JSON immediately (about 1 ms)
Step 4 → Cache miss -> API queries Postgres (host "postgres", port 5432)
Step 5 → API stores the row in Redis with a 60 second TTL, returns it
Step 6 → On POST/PUT the API writes to Postgres and deletes the Redis key (invalidation)
Step 7 → Compose waits for Postgres/Redis healthchecks before starting the API
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Client API (port 3000) पर GET /items/1 बुलाता है
Step 2 → API Redis (host "redis", port 6379) से key item:1 माँगती है
Step 3 → Cache hit  -> JSON तुरंत लौटता है (लगभग 1 ms)
Step 4 → Cache miss -> API Postgres (host "postgres", port 5432) से query करती है
Step 5 → API row को 60 सेकंड TTL के साथ Redis में रखती है और लौटाती है
Step 6 → POST/PUT पर API Postgres में लिखती है और Redis key हटाती है (invalidation)
Step 7 → Compose API से पहले Postgres/Redis के healthchecks का इंतज़ार करता है
```

---

## 🟡 Real World Example
Swiggy-style restaurant menu API: menus are read thousands of times per minute but updated rarely. Redis serves hot menus; Postgres is the source of truth. After a restaurant edits a dish, the API deletes the Redis key so the next read fetches fresh data. This pattern (cache-aside) cuts database load by 80-90% in typical read-heavy systems.

## 🟡 Real Example Hindi mein
Swiggy जैसी restaurant menu API: menus हर मिनट हज़ारों बार पढ़े जाते हैं पर कम बदलते हैं। Redis गरम menus देता है; Postgres सच्चा स्रोत है। Restaurant dish बदले तो API Redis key हटा देती है ताकि अगला read ताज़ा data लाए। यह pattern (cache-aside) read-heavy systems में database load को आम तौर पर 80-90% तक घटाता है।

---

## 💻 Code / Config Example — Basic
```yaml
# compose.yaml  (Basic: three services)
services:
  api:
    build: ./api                                  # build ./api/Dockerfile
    ports: ["3000:3000"]                          # expose API
    environment:
      DATABASE_URL: postgres://app:secret@postgres:5432/app   # service name = host
      REDIS_URL: redis://redis:6379               # redis service
    depends_on: [postgres, redis]                 # start order only
  postgres:
    image: postgres:16-alpine                     # example tag
    environment:
      POSTGRES_USER: app                          # DB user
      POSTGRES_PASSWORD: secret                   # demo password
      POSTGRES_DB: app                            # DB name
    volumes: ["pgdata:/var/lib/postgresql/data"]  # persistent data
  redis:
    image: redis:7-alpine                         # cache
volumes:
  pgdata: {}                                      # named volume
```

## 💻 Code / Config Example — Advanced
```
project/
  compose.yaml
  .env                 (DB_PASS=change-me)
  api/Dockerfile
  api/package.json
  api/server.js
  db/init.sql
```
```dockerfile
# api/Dockerfile  (multi-stage, non-root)
FROM node:20-alpine AS deps                   # stage 1: install dependencies (example tag)
WORKDIR /app                                  # working directory
COPY package*.json ./                         # manifests only, for caching
RUN npm ci --omit=dev                         # production deps only (needs package-lock.json)
FROM node:20-alpine AS runtime                # stage 2: small runtime image
ENV NODE_ENV=production                       # production mode
WORKDIR /app                                  # working directory
COPY --from=deps /app/node_modules ./node_modules   # bring modules
COPY server.js ./                             # app code
USER node                                     # run as non-root
EXPOSE 3000                                   # documentation of the port
CMD ["node", "server.js"]                     # PID 1 is node
```
```javascript
// api/server.js  (npm i express pg redis) cache-aside example
const express = require('express');                         // web framework
const { Pool } = require('pg');                             // Postgres pool
const { createClient } = require('redis');                  // Redis client (v4+)
const app = express();                                      // create app
app.use(express.json());                                    // parse JSON bodies
const pool = new Pool({ connectionString: process.env.DATABASE_URL }); // reuse connections
const redis = createClient({ url: process.env.REDIS_URL }); // Redis connection
redis.on('error', (e) => console.error('redis', e.message)); // do not crash on cache errors
app.get('/health', async (req, res) => {                    // used by healthcheck
  try { await pool.query('SELECT 1'); res.json({ ok: true }); } // DB reachable?
  catch { res.status(503).json({ ok: false }); }            // unhealthy
});
app.get('/items/:id', async (req, res) => {                 // read with cache
  const key = `item:${req.params.id}`;                      // cache key
  const hit = await redis.get(key).catch(() => null);       // cache failure = treat as miss
  if (hit) return res.json({ source: 'cache', ...JSON.parse(hit) }); // return cached
  const r = await pool.query('SELECT id, name FROM items WHERE id=$1', [req.params.id]); // parameterized (no SQL injection)
  if (!r.rows[0]) return res.status(404).json({ error: 'not found' }); // missing
  await redis.set(key, JSON.stringify(r.rows[0]), { EX: 60 }).catch(() => {}); // cache 60s
  res.json({ source: 'db', ...r.rows[0] });                 // return DB row
});
app.post('/items', async (req, res) => {                    // write
  const r = await pool.query('INSERT INTO items(name) VALUES($1) RETURNING id, name', [req.body.name]); // insert
  await redis.del(`item:${r.rows[0].id}`).catch(() => {});  // invalidate
  res.status(201).json(r.rows[0]);                          // created
});
redis.connect().then(() => app.listen(3000, () => console.log('up'))); // start after Redis connects
process.on('SIGTERM', async () => { await pool.end(); await redis.quit(); process.exit(0); }); // graceful stop
```
```sql
-- db/init.sql  runs once on an empty data volume
CREATE TABLE IF NOT EXISTS items (id SERIAL PRIMARY KEY, name TEXT NOT NULL); -- sample table
INSERT INTO items(name) VALUES ('Paneer Tikka'), ('Masala Dosa');             -- sample rows
```
```yaml
# compose.yaml  (Advanced)
name: nodeapp
services:
  api:
    build: ./api                                           # Dockerfile above
    restart: unless-stopped
    ports: ["127.0.0.1:3000:3000"]                         # Nginx on host proxies here
    environment:
      DATABASE_URL: postgres://app:${DB_PASS}@postgres:5432/app   # DB_PASS from .env
      REDIS_URL: redis://:${REDIS_PASS}@redis:6379         # Redis password
    depends_on:
      postgres: { condition: service_healthy }             # wait DB
      redis: { condition: service_healthy }                # wait cache
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]  # alpine has busybox wget
      interval: 15s
      timeout: 3s
      retries: 3
      start_period: 15s
    read_only: true                                        # immutable FS
    tmpfs: ["/tmp"]
    cap_drop: ["ALL"]                                      # no extra privileges
    security_opt: ["no-new-privileges:true"]
    deploy: { resources: { limits: { cpus: "0.75", memory: 384M } } }
  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${DB_PASS}
      POSTGRES_DB: app
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 5s
      timeout: 3s
      retries: 10
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: ["redis-server", "--requirepass", "${REDIS_PASS}", "--maxmemory", "128mb", "--maxmemory-policy", "allkeys-lru"]  # auth + eviction
    volumes: ["redisdata:/data"]
    healthcheck:
      test: ["CMD-SHELL", "redis-cli -a $$REDIS_PASS ping | grep PONG"]  # $$ escapes for the container shell
      interval: 5s
      timeout: 3s
      retries: 10
    environment:
      REDIS_PASS: ${REDIS_PASS}                            # make it visible to the healthcheck
volumes:
  pgdata: {}
  redisdata: {}
```
Run: `docker compose up -d --build`, then `curl localhost:3000/items/1` twice: first `"source":"db"`, then `"source":"cache"`. (Written and linted for syntax; not built or run on this machine, so adjust versions as needed.)

---

## 🟠 My Stack Integration
- **Nginx:** host Nginx `proxy_pass http://127.0.0.1:3000;` with TLS.
- **React:** calls `/api/...` through Nginx, same origin, so no CORS pain.
- **AWS:** swap `postgres` for RDS and `redis` for ElastiCache by changing only the two URLs.
- **GitHub Actions:** build the api image and push; the server runs `pull && up -d`.
- **Security:** parameterized SQL, Redis password, non-root user, no DB/Redis ports published, secrets from `.env` (git-ignored).

```nginx
# /etc/nginx/conf.d/api.conf  (host Nginx; not tested with nginx -t here)
server {
  listen 80;                                   # HTTP (add TLS with certbot)
  server_name api.example.com;                 # your domain
  location / {
    proxy_pass http://127.0.0.1:3000;          # compose published port
    proxy_set_header Host $host;               # keep host header
    proxy_set_header X-Forwarded-For $remote_addr;   # client IP
  }
}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `DATABASE_URL=...@localhost:5432/...` inside the container.
✅ Correct: Host is `postgres` (the service name).

❌ Mistake 2: `depends_on: [postgres]` and assuming readiness.
✅ Correct: `condition: service_healthy`.

❌ Mistake 3: Caching without TTL or invalidation, serving stale data forever.
✅ Correct: `EX` TTL plus delete on write.

❌ Mistake 4: Redis without a password but published on a public port.
✅ Correct: No published port, `requirepass`, and a firewall.

---

## 🧠 Tricky Interview Question
After a write, users still see old data for up to a minute. Is Redis broken?

Answer: No, this is the cache-aside TTL. If the write path does not delete or update the key, readers get the cached copy until the 60 s TTL expires. Fix by invalidating on write (done above), by write-through updates, or by shorter TTLs for volatile data. Also watch race conditions: a read between DB write and cache delete may re-cache old data, so delete after commit.

---

## ⚫ Interview Questions + Answers

Q1: Why Redis if Postgres is fast?
A1: Redis answers from memory in sub-millisecond time, reducing load and latency on hot reads.

Q2: What does `maxmemory-policy allkeys-lru` do?
A2: When memory is full Redis evicts the least recently used keys, so the cache never crashes the box.

Q3: Why `$$` in the healthcheck?
A3: Compose treats `$VAR` as interpolation; `$$` passes a literal `$` to the container shell.

Q4: Why `pool.end()` on SIGTERM?
A4: Graceful shutdown closes DB connections so Postgres does not accumulate dead sessions.

Q5: How would you scale the API?
A5: Run more replicas behind Nginx; the app is stateless because state is in Postgres/Redis.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Read-heavy API with hot, rarely changing data.
- Single-server deployment with a path to managed services.

❌ Avoid when:
- Data must always be strongly consistent (e.g., account balances).
- Tiny apps where caching adds complexity without need.

---

## 📊 Visual Diagram
```
 Client -> Nginx(443) -> API:3000
                          |   \
                  GET hit |    \ miss
                          v     v
                       Redis   Postgres
                    (60s TTL)  (source of truth)
 write: API -> Postgres, then DEL redis key
 volumes: pgdata, redisdata   network: default Compose network
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| cache-aside | App checks cache, then DB | पहले cache फिर DB |
| TTL | Time before a key expires | key की उम्र |
| invalidation | Removing stale cache | पुराना cache हटाना |
| connection pool | Reused DB connections | DB connections का पुन: उपयोग |
| eviction | Removing keys when full | memory भरने पर keys हटाना |
| graceful shutdown | Clean stop on SIGTERM | सलीके से बंद होना |

---

## ⚡ 3-Line Summary
English: API talks to Postgres and Redis by service name; healthchecks control start order. Cache-aside with TTL and invalidation keeps reads fast and correct. Harden with non-root, passwords, internal ports.
Hindi: API, Postgres और Redis से service name से बात करती है; healthchecks start order तय करते हैं। TTL और invalidation वाला cache-aside reads को तेज़ और सही रखता है। Non-root, passwords और internal ports से सुरक्षित करें।

---

## ➡️ Next Topic
**208. FastAPI + PostgreSQL + Redis Compose Example**: the same architecture with Python.
