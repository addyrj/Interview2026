---

# 437. Gunicorn + Uvicorn — Production Deployment
# हिंदी में: Gunicorn + Uvicorn — Production Deployment

---

## 🔵 Simple Definition (English)
**Uvicorn** is an ASGI (Asynchronous Server Gateway Interface) server — it runs FastAPI apps. **Gunicorn** is a battle-tested WSGI process manager that can manage multiple Uvicorn worker processes. In production: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app` — Gunicorn manages 4 Uvicorn workers. Workers = parallel request handlers. Rule: `(2 × CPU cores) + 1` workers.

## 🔵 सरल परिभाषा (Hindi)
**Uvicorn** = ASGI server — FastAPI apps run करता है। **Gunicorn** = process manager जो multiple Uvicorn workers manage करता है। Production में: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`। Workers = parallel request handlers। Formula: `(2 × CPU cores) + 1`।

---

## 💻 Code Example — Basic
```python
# ─── main.py — FastAPI app ────────────────────────────────────────
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — run before first request:
    print("Starting up...")
    # Connect to DB, load models, warm cache:
    await database.connect()
    await redis_client.ping()
    yield
    # Shutdown — run after last request:
    print("Shutting down...")
    await database.disconnect()
    await redis_client.close()

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok"}
```

```bash
# ─── Development — Uvicorn directly ──────────────────────────────
uvicorn main:app --reload --port 8000
# --reload: auto-restart on file change (dev only!)
# --port: bind to port 8000
# --host 0.0.0.0: accept connections from any IP (needed in Docker)

# ─── Production — Gunicorn + Uvicorn ─────────────────────────────
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --keepalive 5 \
  --access-logfile - \
  --error-logfile -

# Workers: (2 × CPU) + 1 = 9 workers for 4-core machine
# --timeout 120: kill worker if request takes > 120s
# --keepalive 5: HTTP keep-alive timeout
# - (dash) = log to stdout/stderr (good for Docker)

# ─── Environment variables for config ───────────────────────────
WEB_CONCURRENCY=4      # Gunicorn reads this automatically
WORKERS_PER_CORE=2     # alternative calculation
PORT=8000              # many platforms set this
```

## 💻 Code Example — Advanced
```python
# ─── gunicorn.conf.py — config file ──────────────────────────────
import multiprocessing
import os

# Worker count:
workers = int(os.environ.get("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"

# Binding:
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Timeouts:
timeout = 120
keepalive = 5
graceful_timeout = 30   # time to finish in-flight requests on shutdown

# Logging:
accesslog = "-"    # stdout
errorlog = "-"     # stderr
loglevel = "info"

# Security:
limit_request_line = 4096       # max URL length
limit_request_field_size = 8190 # max header field size

# Run as:
# gunicorn main:app -c gunicorn.conf.py
```

```dockerfile
# ─── Dockerfile — production FastAPI ─────────────────────────────
FROM python:3.11-slim

# Install dependencies first (cached unless requirements.txt changes):
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code:
COPY . .

# Non-root user (security):
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Expose port:
EXPOSE 8000

# Health check:
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command:
CMD ["gunicorn", "main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120"]
```

```yaml
# ─── docker-compose.yml — local development ──────────────────────
version: "3.9"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/mydb
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - WEB_CONCURRENCY=2
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - .:/app   # mount code for hot reload in dev
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 5s
      timeout: 5s
      retries: 5
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: FastAPI + Uvicorn
# ASGI → async by default
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
# Workers: (2×CPU)+1 rule

# Uvicorn single process (dev):
# uvicorn main:app --reload

# All config via gunicorn.conf.py or CLI flags
```

```javascript
// Node.js: Express + PM2 (similar concept)
// app.listen(3000);
// pm2 start app.js --instances 4
// Or cluster module for multi-process

// Next.js: next start
// npm run start (built-in cluster via Next.js)
```

Key differences:
- Python ASGI (Uvicorn) vs Node.js single-process event loop.
- Python needs multiple workers for CPU parallelism (GIL!). Node.js is single-threaded but cluster handles it.
- PM2 for Node.js = Gunicorn for Python (process manager).
- Both use reverse proxy (Nginx) in front for SSL termination, static files, load balancing.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `--reload` in production
```bash
# Wrong — auto-reload scans files, uses more CPU, security risk:
uvicorn main:app --reload  # DEVELOPMENT ONLY

# Correct for production:
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

❌ Mistake 2: Too many workers on small containers
```bash
# Wrong — 8 workers on 512MB container → OOM killed:
gunicorn main:app --workers 8 ...

# Correct — 1-2 workers per 256MB memory:
# 512MB container → 2 workers
WEB_CONCURRENCY=2
```

---

## 🧠 Tricky Interview Question

**Q**: If you have 4 CPU cores, how many Gunicorn workers should you run? What's the formula and why?

**Answer**: **`(2 × num_cores) + 1 = 9 workers`** for 4 cores. The formula comes from Gunicorn's docs. The `2×` accounts for workers waiting on I/O (DB queries, HTTP calls) — while one worker waits for a DB response, others can process other requests. The `+1` is a buffer. For **I/O-heavy apps** (FastAPI + async): you might use fewer workers but more async tasks per worker. For **CPU-bound apps**: match workers to cores (GIL means extra workers don't help for CPU work). In containers: limit by memory too — each worker ~50-100MB for a FastAPI app.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between WSGI and ASGI?
A1: **WSGI** (Web Server Gateway Interface): synchronous Python web standard. One request handled at a time per worker. Django, Flask. **ASGI** (Asynchronous Server Gateway Interface): async Python web standard. One worker handles multiple concurrent requests via async/await. FastAPI, Django 3.1+ Channels, Starlette. WSGI workers: block during DB I/O. ASGI workers: await I/O, handle other requests meanwhile. For async FastAPI: must use ASGI server (Uvicorn, Hypercorn, Daphne) — not WSGI (Gunicorn alone).

Q2: Why use Gunicorn + Uvicorn together instead of just Uvicorn?
A2: Uvicorn alone is single-process — can't use multiple CPU cores. Gunicorn spawns multiple Uvicorn worker processes, enabling parallel CPU usage. Gunicorn also handles: graceful restarts (zero-downtime deploys), worker crash recovery (auto-respawn), max request limits (force-restart workers to prevent memory leaks), signal handling (SIGTERM/HUP). Alternative: `uvicorn --workers 4` (Uvicorn 0.12+) — similar but fewer management features. In Kubernetes: often use single Uvicorn process per pod + horizontal pod autoscaling instead.

Q3: How do you do a zero-downtime deploy of a FastAPI app?
A3: Gunicorn supports graceful restarts: `kill -HUP $(cat gunicorn.pid)` — spawns new workers, old workers finish in-flight requests, then exit. In Docker/Kubernetes: rolling deploy — new pods start before old pods terminate. `SIGTERM` → Gunicorn sends each worker a graceful shutdown signal → workers finish current requests → exit. `graceful_timeout=30` gives workers 30 seconds. Key: `lifespan` handler in FastAPI for startup/shutdown logic. Kubernetes: `terminationGracePeriodSeconds: 60` > Gunicorn's graceful_timeout.

Q4: What is the `HEALTHCHECK` in Dockerfile and why is it important?
A4: `HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1` tells Docker/Kubernetes whether the container is healthy. Docker: only starts traffic after health check passes. Kubernetes: readinessProbe stops sending traffic to unhealthy pods; livenessProbe restarts hung pods. Your `/health` endpoint should check: can process requests (app is up), can reach DB (connection pool ok), can reach Redis. Return 200 for healthy, 503 for unhealthy. Without it: Kubernetes sends traffic to pods still starting up → 502 errors during deploys.

Q5: What are environment variables best practices for production Python apps?
A5: (1) Never hardcode secrets — use env vars: `os.environ["API_KEY"]`. (2) Use Pydantic Settings: `class Settings(BaseSettings): api_key: str = Field(...)` — auto-reads from env, validates types, raises on missing. (3) `.env` file for development: `python-dotenv` loads it. Never commit `.env` to git — add to `.gitignore`. (4) In Docker: pass via `--env-file .env` or `environment:` in compose. (5) In Kubernetes: use Secrets (not ConfigMaps) for sensitive values — mounted as env vars or files. (6) Distinguish between config (DB URL, feature flags) and secrets (API keys, passwords).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Uvicorn | ASGI server for FastAPI | FastAPI का ASGI server |
| Gunicorn | Multi-process manager | Multi-process manager |
| Workers | Parallel request handlers | Parallel request handlers |
| ASGI | Async Python web standard | Async Python web standard |
| lifespan | FastAPI startup/shutdown | FastAPI startup/shutdown |
| HEALTHCHECK | Container health probe | Container health probe |
| WEB_CONCURRENCY | Number of workers env var | Workers की संख्या |

---

## ⚡ 3-Line Summary
English: Use `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app` in production — never bare `uvicorn --reload`. Workers formula: `(2 × CPU cores) + 1`, but cap by memory (50-100MB/worker). Use FastAPI's `lifespan` for startup/shutdown, expose `/health` endpoint for Kubernetes probes.
Hindi: Production में `gunicorn -w 4 -k uvicorn.workers.UvicornWorker`। Workers = `(2×CPU)+1`, memory से limit करो। FastAPI `lifespan` से startup/shutdown। `/health` endpoint Kubernetes probes के लिए।

---

## ➡️ Next Topic
**440. Docker Python** — multi-stage builds, .dockerignore, layers optimization. **442. Docker Compose** — multi-service dev environment. **447. CI/CD GitHub Actions** — test + build + deploy pipeline.
