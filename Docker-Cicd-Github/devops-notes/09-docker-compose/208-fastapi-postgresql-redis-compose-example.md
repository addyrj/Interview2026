# 208. FastAPI + PostgreSQL + Redis Compose Example
# हिंदी में: FastAPI + PostgreSQL + Redis Compose का पूरा उदाहरण

---

## 🔵 Simple Definition (English)
A complete Compose stack for a Python backend: a FastAPI app served by Uvicorn, PostgreSQL as the database and Redis as cache, with healthchecks, a non-root multi-stage image, environment-driven settings and persistent volumes.

## 🔵 सरल परिभाषा (Hindi)
Python backend के लिए पूरा Compose stack: Uvicorn से चलती FastAPI app, database के रूप में PostgreSQL और cache के रूप में Redis, healthchecks, non-root multi-stage image, environment से चलने वाली settings और persistent volumes के साथ।

---

## 🔴 Problem it Solves
Python teams struggle with virtualenv differences, system libraries for database drivers (`libpq`), and wiring async code to Postgres and Redis. Running everything in Compose removes machine differences and gives the same layout in dev and prod.

## 🔴 यह क्यों बना? (Hindi)
Python teams virtualenv के फर्क, database drivers के system libraries (`libpq`) और async code को Postgres व Redis से जोड़ने में परेशान होती हैं। सब कुछ Compose में चलाने से machine का फर्क हटता है और dev व prod में एक जैसी बनावट मिलती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → `docker compose up -d --build` builds the FastAPI image (wheels built in a builder stage)
Step 2 → Postgres and Redis start and report healthy
Step 3 → Uvicorn starts the ASGI app on 0.0.0.0:8000 as a non-root user
Step 4 → On startup, the app creates an asyncpg pool and a Redis client
Step 5 → GET /items/{id}: check Redis, else query Postgres, then cache for 60 s
Step 6 → /health checks DB and Redis; Compose healthcheck calls it
Step 7 → Swagger docs are available at /docs (disable or protect in production)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `docker compose up -d --build` FastAPI image बनाता है (wheels builder stage में बनते हैं)
Step 2 → Postgres और Redis चालू होकर healthy बताते हैं
Step 3 → Uvicorn ASGI app को 0.0.0.0:8000 पर non-root user से चलाता है
Step 4 → Startup पर app asyncpg pool और Redis client बनाती है
Step 5 → GET /items/{id}: पहले Redis, नहीं मिला तो Postgres, फिर 60 सेकंड cache
Step 6 → /health DB और Redis जाँचता है; Compose healthcheck इसे बुलाता है
Step 7 → Swagger docs /docs पर मिलते हैं (production में बंद करें या सुरक्षित करें)
```

---

## 🟡 Real World Example
A Razorpay-style internal service exposes payment status lookups. FastAPI validates requests with Pydantic, Postgres stores transactions, Redis holds hot status lookups for a few seconds and also rate-limit counters. The service runs on an EC2 instance behind Nginx; the same compose file with different env vars is used on developer laptops.

## 🟡 Real Example Hindi mein
Razorpay जैसी internal service payment status lookup देती है। FastAPI Pydantic से requests validate करती है, Postgres transactions रखता है, Redis कुछ सेकंड के लिए hot status lookups और rate-limit counters रखता है। Service EC2 पर Nginx के पीछे चलती है; वही compose file अलग env vars के साथ developers के laptops पर चलती है।

---

## 💻 Code / Config Example — Basic
```yaml
# compose.yaml  (Basic)
services:
  api:
    build: ./api                                   # build ./api/Dockerfile
    ports: ["8000:8000"]                           # http://localhost:8000/docs
    environment:
      DATABASE_URL: postgresql://app:secret@postgres:5432/app   # sync-style URL; asyncpg accepts it
      REDIS_URL: redis://redis:6379/0              # Redis DB 0
    depends_on: [postgres, redis]                  # start order
  postgres:
    image: postgres:16-alpine                      # example tag
    environment: { POSTGRES_USER: app, POSTGRES_PASSWORD: secret, POSTGRES_DB: app }  # demo credentials
    volumes: ["pgdata:/var/lib/postgresql/data"]   # persistent
  redis:
    image: redis:7-alpine                          # cache
volumes:
  pgdata: {}
```

## 💻 Code / Config Example — Advanced
```
project/
  compose.yaml
  .env                  (DB_PASS, REDIS_PASS)
  api/Dockerfile
  api/requirements.txt  (fastapi, uvicorn[standard], asyncpg, redis)
  api/main.py
  db/init.sql
```
```dockerfile
# api/Dockerfile  (multi-stage, non-root)
FROM python:3.12-slim AS builder                 # builder stage (example tag)
WORKDIR /build                                   # build folder
COPY requirements.txt .                          # dependency list first, for caching
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt   # install into /install
FROM python:3.12-slim AS runtime                 # small runtime stage
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 # no .pyc files, unbuffered logs
RUN useradd --create-home --uid 10001 app        # non-root user
WORKDIR /code                                    # app folder
COPY --from=builder /install /usr/local          # bring installed packages
COPY main.py .                                   # application code
USER app                                         # drop root
EXPOSE 8000                                      # documentation of port
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]   # exec form: PID 1 is uvicorn
```
```python
# api/main.py  (FastAPI + asyncpg + redis.asyncio)
import json, os                                   # stdlib imports
from contextlib import asynccontextmanager        # lifespan helper
import asyncpg                                    # async Postgres driver
import redis.asyncio as aioredis                  # async Redis client
from fastapi import FastAPI, HTTPException        # framework

@asynccontextmanager
async def lifespan(app: FastAPI):                 # runs on startup and shutdown
    app.state.pg = await asyncpg.create_pool(os.environ["DATABASE_URL"], min_size=1, max_size=10)  # DB pool
    app.state.redis = aioredis.from_url(os.environ["REDIS_URL"], decode_responses=True)           # Redis client
    yield                                         # app serves requests here
    await app.state.pg.close()                    # graceful close
    await app.state.redis.aclose()                # close Redis (redis-py 5+)

app = FastAPI(lifespan=lifespan, docs_url=None if os.getenv("ENV") == "production" else "/docs")  # hide docs in prod

@app.get("/health")
async def health():                               # used by Compose healthcheck
    await app.state.pg.fetchval("SELECT 1")       # raises if DB is down -> 500
    await app.state.redis.ping()                  # raises if Redis is down
    return {"ok": True}

@app.get("/items/{item_id}")
async def get_item(item_id: int):                 # int validates input automatically
    key = f"item:{item_id}"                       # cache key
    cached = await app.state.redis.get(key)       # try cache
    if cached:
        return {"source": "cache", **json.loads(cached)}
    row = await app.state.pg.fetchrow("SELECT id, name FROM items WHERE id=$1", item_id)  # parameterized query
    if row is None:
        raise HTTPException(status_code=404, detail="not found")
    data = {"id": row["id"], "name": row["name"]} # plain dict
    await app.state.redis.set(key, json.dumps(data), ex=60)   # cache for 60 seconds
    return {"source": "db", **data}
```
```yaml
# compose.yaml  (Advanced)
name: fastapi-app
services:
  api:
    build: ./api
    restart: unless-stopped
    ports: ["127.0.0.1:8000:8000"]                  # Nginx on host proxies here
    environment:
      ENV: production                               # hides /docs
      DATABASE_URL: postgresql://app:${DB_PASS}@postgres:5432/app
      REDIS_URL: redis://:${REDIS_PASS}@redis:6379/0
    depends_on:
      postgres: { condition: service_healthy }
      redis: { condition: service_healthy }
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health', timeout=2).status==200 else 1)"]  # slim image has no curl
      interval: 15s
      timeout: 4s
      retries: 3
      start_period: 15s
    read_only: true
    tmpfs: ["/tmp"]
    cap_drop: ["ALL"]
    security_opt: ["no-new-privileges:true"]
    deploy: { resources: { limits: { cpus: "1.00", memory: 512M } } }
  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment: { POSTGRES_USER: app, POSTGRES_PASSWORD: "${DB_PASS}", POSTGRES_DB: app }
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
    environment: { REDIS_PASS: "${REDIS_PASS}" }
    command: ["redis-server", "--requirepass", "${REDIS_PASS}", "--maxmemory", "128mb", "--maxmemory-policy", "allkeys-lru"]
    healthcheck:
      test: ["CMD-SHELL", "redis-cli -a $$REDIS_PASS ping | grep PONG"]
      interval: 5s
      timeout: 3s
      retries: 10
volumes:
  pgdata: {}
```
Run: `docker compose up -d --build`; test: `curl localhost:8000/items/1`. (Python syntax checked locally; image not built or run on this machine. Package versions are unpinned examples, pin them in `requirements.txt`.)

---

## 🟠 My Stack Integration
- **Uvicorn workers:** for CPU parallelism use `gunicorn -k uvicorn.workers.UvicornWorker -w N`, or run several containers behind Nginx.
- **Nginx:** `proxy_pass http://127.0.0.1:8000;` plus `proxy_set_header X-Forwarded-Proto $scheme;`; start uvicorn with `--proxy-headers` when behind a proxy.
- **React:** calls the API through Nginx; CORS configured via `CORSMiddleware` only for needed origins.
- **Migrations:** run Alembic as a one-off: `docker compose run --rm api alembic upgrade head` (add alembic to requirements).
- **AWS:** RDS and ElastiCache by changing URLs; secrets from Secrets Manager.
- **Security:** Pydantic validation, parameterized SQL, docs hidden in prod, non-root, no published DB ports.

```yaml
# snippet: one-off migration service
  migrate:
    build: ./api                              # same image
    command: ["alembic", "upgrade", "head"]   # apply DB migrations
    profiles: ["tools"]                       # runs only with --profile tools
    environment:
      DATABASE_URL: postgresql://app:${DB_PASS}@postgres:5432/app
    depends_on:
      postgres: { condition: service_healthy }
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using blocking libraries (`psycopg2`, `requests`) inside `async def` routes, blocking the event loop.
✅ Correct: Use `asyncpg` / `redis.asyncio` / `httpx`, or define the route with plain `def` so FastAPI uses a thread pool.

❌ Mistake 2: `CMD uvicorn main:app` in shell form, so signals do not reach uvicorn.
✅ Correct: Exec form JSON array.

❌ Mistake 3: `--reload` in production.
✅ Correct: Use reload only in the dev override.

❌ Mistake 4: Leaving `/docs` public with sensitive endpoints.
✅ Correct: Disable or protect behind auth.

---

## 🧠 Tricky Interview Question
With `-w 4` workers and a pool `max_size=10`, how many DB connections can this container open, and why does it matter?

Answer: Each worker process runs its own lifespan, so up to 4 x 10 = 40 connections. Postgres defaults to `max_connections=100`; with several containers you can exhaust it. Size pools as `max_connections / (containers x workers)` minus headroom, or add PgBouncer.

---

## ⚫ Interview Questions + Answers

Q1: Why multi-stage for Python?
A1: Build tools and caches stay in the builder; runtime is smaller with a smaller attack surface.

Q2: `lifespan` vs `@app.on_event`?
A2: `lifespan` is the modern recommended way; `on_event` is deprecated.

Q3: Why not curl in the healthcheck?
A3: `python:slim` has no curl; use Python's stdlib instead of installing extra packages.

Q4: How do you handle async DB migrations?
A4: Alembic runs synchronously as a separate command/service before the app starts.

Q5: Why `PYTHONUNBUFFERED=1`?
A5: Logs are flushed immediately so `docker logs` shows them in real time.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- I/O-bound APIs, ML-serving endpoints, quick validated REST services.

❌ Avoid when:
- Heavy CPU work inside request handlers (use a worker queue such as Celery/RQ).
- You need strong guarantees from an ORM and sync stack and do not need async.

---

## 📊 Visual Diagram
```
 Client -> Nginx -> [FastAPI/Uvicorn :8000] --asyncpg pool--> Postgres
                           |
                           +--redis.asyncio--> Redis (cache, rate limits)
 healthchecks: api -> /health (db+redis) ; postgres -> pg_isready ; redis -> ping
 build: builder(wheels) -> runtime(non-root) ; volumes: pgdata
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ASGI | Async Python web interface | async Python web interface |
| Uvicorn | ASGI server | ASGI server |
| lifespan | Startup/shutdown hook | startup/shutdown hook |
| Pydantic | Data validation library | data validation library |
| connection pool | Reused DB connections | DB connections का पूल |
| Alembic | DB migration tool | DB migration tool |

---

## ⚡ 3-Line Summary
English: FastAPI talks to Postgres (asyncpg) and Redis by service name; healthchecks gate startup. Use non-root multi-stage images, lifespan hooks, and size pools per worker. Run migrations as a one-off job.
Hindi: FastAPI, Postgres (asyncpg) और Redis से service name से बात करती है; healthchecks startup तय करते हैं। Non-root multi-stage images, lifespan hooks और हर worker के हिसाब से pool size रखें। Migrations को one-off job की तरह चलाएँ।

---

## ➡️ Next Topic
**209. React + Node.js + DB**: add the frontend to complete a full stack.
