---

# 350. FastAPI Deployment
# हिंदी में: FastAPI Deployment (production में चलाना)

---

## 🔵 Simple Definition (English)
Deploying FastAPI means running it on a real server so users can reach it: an ASGI server (Uvicorn, optionally managed by Gunicorn) runs several worker processes, a Docker image packages the app, and a reverse proxy (nginx or a cloud load balancer) handles HTTPS and forwards traffic. Config comes from environment variables.

## 🔵 सरल परिभाषा (Hindi)
FastAPI deploy करने का मतलब उसे असली server पर चलाना है ताकि users पहुँच सकें: एक ASGI server (Uvicorn, चाहें तो Gunicorn की देखरेख में) कई worker processes चलाता है, Docker image app को package करती है और reverse proxy (nginx या cloud load balancer) HTTPS संभालकर traffic आगे भेजता है। Config environment variables से आती है।

---

## 🔴 Problem it Solves
`uvicorn main:app --reload` on your laptop is for development only: one process, auto-reload, no HTTPS, dies if the terminal closes. Production needs restarts on crash, multiple CPU cores, TLS, health checks, zero-downtime updates and the same environment everywhere (not "works on my machine").

## 🔴 यह क्यों बना? (Hindi)
Laptop पर `uvicorn main:app --reload` सिर्फ़ development के लिए है: एक process, auto-reload, HTTPS नहीं, terminal बंद होते ही खत्म। Production में crash पर restart, कई CPU cores, TLS, health checks, बिना रुकावट update और हर जगह वही environment चाहिए ("मेरे यहाँ तो चलता है" नहीं)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pin dependencies (requirements.txt / pyproject + lock file)
Step 2 → Write a Dockerfile: slim Python image, install deps, copy app, non-root user
Step 3 → Start command: uvicorn --workers N  OR  gunicorn -k uvicorn_worker.UvicornWorker -w N
Step 4 → Put nginx / cloud LB in front: TLS, gzip, request size limits, forward headers
Step 5 → Config via env vars (DATABASE_URL, SECRET_KEY); never bake secrets into the image
Step 6 → Run `alembic upgrade head` once per release (init container / pre-deploy job)
Step 7 → Health endpoint (/health) for the orchestrator; graceful shutdown via SIGTERM
Step 8 → Roll out: build image -> push to registry -> deploy -> check health -> roll back if bad
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Dependencies pin करें (requirements.txt / pyproject + lock file)
Step 2 → Dockerfile: slim Python image, deps install, app copy, non-root user
Step 3 → Start command: uvicorn --workers N  या  gunicorn -k uvicorn_worker.UvicornWorker -w N
Step 4 → आगे nginx / cloud LB: TLS, gzip, request size limit, headers आगे भेजना
Step 5 → Config env vars से (DATABASE_URL, SECRET_KEY); secrets image में कभी नहीं
Step 6 → हर release पर एक बार `alembic upgrade head` (init container / pre-deploy job)
Step 7 → Orchestrator के लिए /health endpoint; SIGTERM पर graceful shutdown
Step 8 → Rollout: image build -> registry में push -> deploy -> health जाँच -> खराब हो तो rollback
```

---

## 🟡 Real World Example
A Razorpay-like service ships as a Docker image to AWS ECS or Kubernetes. Each container runs Gunicorn with 2 Uvicorn workers; an Application Load Balancer terminates HTTPS and calls `/health` every 10 s. On each release a pre-deploy task runs Alembic, then the new tasks start and the old ones drain. Secrets come from AWS Secrets Manager as environment variables.

## 🟡 Real Example Hindi mein
Razorpay जैसी service Docker image के रूप में AWS ECS या Kubernetes पर जाती है। हर container में Gunicorn 2 Uvicorn workers के साथ चलता है; Application Load Balancer HTTPS खत्म करता है और हर 10 s पर `/health` बुलाता है। हर release पर पहले pre-deploy task Alembic चलाता है, फिर नए tasks शुरू होते हैं और पुराने खाली होते हैं। Secrets AWS Secrets Manager से environment variables बनकर आते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: the app + how to start it. Save as main.py
# Dev:  uvicorn main:app --reload                       (auto-reload, one process)
# Prod: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
# Verified: 2 workers started and GET /health returned {"status":"ok"} via curl
import os  # read environment variables
from typing import Dict  # type hints
from fastapi import FastAPI  # framework

app: FastAPI = FastAPI()  # the ASGI application object "app" inside main.py


@app.get("/health")  # used by load balancer / Kubernetes probes
def health() -> Dict[str, str]:
    return {"status": "ok"}  # tiny and fast, no DB call


@app.get("/info")  # shows which process answered
def info() -> Dict[str, str]:
    return {"env": os.environ.get("APP_ENV", "dev")}  # config from environment


if __name__ == "__main__":  # allows: python main.py
    import uvicorn  # ASGI server

    uvicorn.run("main:app", host="127.0.0.1", port=8000)  # simple local run
```

## 💻 Code Example — Advanced
```dockerfile
# Dockerfile (production style). NOT RUN here: no Docker daemon was available.
# The same command line was run without Docker and worked (see note below).
FROM python:3.13-slim AS base
# Do not write .pyc files; flush logs immediately
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# Install dependencies first so Docker caches this layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY app ./app

# Run as a non-root user (security)
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
# Docker will mark the container unhealthy if /health fails
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"

# exec-form CMD so SIGTERM reaches gunicorn (graceful shutdown)
CMD ["gunicorn", "app.main:app", "-k", "uvicorn_worker.UvicornWorker", "-w", "2", "-b", "0.0.0.0:8000", "--graceful-timeout", "30"]
```
```text
# requirements.txt
fastapi==0.162.4
gunicorn==27.0.0
uvicorn-worker
uvicorn
pydantic-settings
```
```yaml
# docker-compose.yml  (NOT RUN: no Docker daemon here; syntax follows Compose spec)
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql+psycopg://app:app@db:5432/shop
      APP_ENV: production
    depends_on:
      db:
        condition: service_healthy
    command: sh -c "alembic upgrade head && gunicorn app.main:app -k uvicorn_worker.UvicornWorker -w 2 -b 0.0.0.0:8000"
  db:
    image: postgres:16
    environment: { POSTGRES_USER: app, POSTGRES_PASSWORD: app, POSTGRES_DB: shop }
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d shop"]
      interval: 5s
      retries: 10
```
```nginx
# nginx.conf (NOT RUN): reverse proxy with TLS in front of the app
server {
    listen 443 ssl;
    server_name api.example.com;
    ssl_certificate     /etc/ssl/fullchain.pem;
    ssl_certificate_key /etc/ssl/privkey.pem;
    client_max_body_size 5m;                 # limit upload size
    location / {
        proxy_pass http://127.0.0.1:8000;    # the app
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
```python
# Run the app behind a proxy and trust its X-Forwarded-* headers
# uvicorn app.main:app --proxy-headers --forwarded-allow-ips="127.0.0.1"
```
What was verified: `gunicorn app.main:app -k uvicorn_worker.UvicornWorker -w 2 -b 127.0.0.1:34150` booted two workers (`Booting worker with pid ...`) and `curl /health` returned `{"status":"ok"}`; `uvicorn app.main:app --workers 2` also served it. This needs `pip install gunicorn uvicorn-worker` (the old `uvicorn.workers.UvicornWorker` is deprecated in favour of the separate `uvicorn-worker` package; version-dependent). The Dockerfile, Compose file and nginx config were not executed (no Docker daemon, no nginx), only written to match the documented syntax.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
# gunicorn app.main:app -k uvicorn_worker.UvicornWorker -w 4
# systemd or Docker restarts on crash
```
```javascript
// JavaScript (Node)
// pm2 start server.js -i 4        // cluster mode, 4 processes
// or: node server.js inside Docker, orchestrator restarts on crash
// Dockerfile: FROM node:22-slim ... CMD ["node", "server.js"]
```

Key differences: Node's `pm2 -i max` clusters processes much like Gunicorn workers. Python adds an ASGI server layer (Uvicorn) between the app and the OS; Node has HTTP built in. In both, containers + a reverse proxy are the common production approach.

---

## 🟠 FastAPI Connection
FastAPI's `lifespan` handles graceful startup and shutdown (open and close DB pools); `/health` and `/ready` endpoints serve orchestrator probes; settings come from env vars through `pydantic-settings`. Workers do not share memory, so state must live in a DB or Redis.

```python
# Readiness probe: only report ready when the DB works
from typing import Dict  # types
from fastapi import FastAPI, HTTPException  # app + errors

app: FastAPI = FastAPI()  # app


def db_ok() -> bool:  # replace with real "SELECT 1"
    return True  # pretend DB is reachable


@app.get("/ready")  # Kubernetes readinessProbe target
def ready() -> Dict[str, str]:
    if not db_ok():  # dependency not ready
        raise HTTPException(status_code=503, detail="db down")  # LB stops sending traffic
    return {"status": "ready"}  # OK
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Running with `--reload` in production
```bash
# Wrong:
uvicorn main:app --reload
# Right:
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

❌ Mistake 2: Keeping state in a global variable with several workers
```python
# Wrong: counter = 0  (each worker has its own copy: users see random values)
# Right: store shared state in Redis/PostgreSQL
```

❌ Mistake 3: Running as root and baking secrets into the image
```dockerfile
# Wrong:
ENV SECRET_KEY=abc123          # visible in image layers
# Right: USER appuser; pass secrets at runtime (env, Docker/K8s secrets)
```

❌ Mistake 4: Shell-form CMD so the app never receives SIGTERM
```dockerfile
# Wrong:  CMD gunicorn app.main:app      (a shell may swallow signals)
# Right:  CMD ["gunicorn", "app.main:app", ...]   (exec form)
```

❌ Mistake 5: Exposing the app directly without a proxy / TLS
```text
# Right: nginx/ALB terminates HTTPS; app trusts X-Forwarded-* only from the proxy
```

---

## 🧠 Tricky Interview Question

**Q**: Two workers run this app. You call `/hit` six times. What might you see?

```python
hits = 0

@app.get("/hit")
def hit():
    global hits
    hits += 1
    return {"hits": hits}
```

**Answer**:
```
{"hits":1}
{"hits":2}
{"hits":1}
{"hits":2}
{"hits":3}
{"hits":4}
```
This is a real output from `uvicorn --workers 2`: each worker process keeps its own `hits`, so the numbers jump around depending on which worker answers (the exact sequence varies). Shared counters, caches and sessions must live in Redis or a database. (Verified by running.)

---

## ⚫ Interview Questions + Answers

Q1: Uvicorn vs Gunicorn?
A1: Uvicorn is the ASGI server. Gunicorn is a process manager that can start many Uvicorn workers, restart crashed ones and handle signals. Modern Uvicorn can also run `--workers N` itself; in Kubernetes many teams run one Uvicorn process per container and scale with pods.

Q2: How many workers?
A2: Start near the number of CPU cores available to the container, then load-test. In Kubernetes prefer 1-2 workers per pod and more replicas.

Q3: Why a reverse proxy?
A3: TLS termination, buffering slow clients, static files, rate limits, compression and routing several services under one domain.

Q4: How do you deploy without downtime?
A4: Rolling update: start new instances, wait until `/ready` passes, shift traffic, drain old instances (graceful shutdown). Keep migrations backward compatible.

Q5: Where do secrets go?
A5: Environment variables injected at runtime from a secrets manager. Not in git, not in the Dockerfile, not in the image.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Docker + reverse proxy: almost every production API (portable, repeatable)
- Gunicorn + Uvicorn workers: a VM or a container that needs several processes

❌ Avoid when:
- `--reload`, `debug=True` and single dev server in production
- Serverless (Lambda) needs a different adapter (Mangum); do not copy VM commands there

---

## 📊 Visual Diagram

```
 Browser ──HTTPS──► nginx / Cloud LB  ──► Container A: gunicorn ─┬─ uvicorn worker 1
                       │                                           └─ uvicorn worker 2
                       └──────────────► Container B: gunicorn ─┬─ ...
                                                                  │
                      /health, /ready probes                      ▼
                                                      PostgreSQL / Redis (shared state)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ASGI server | Runs async Python web apps | async web apps चलाने वाला server |
| Worker | One app process | app की एक process |
| Reverse proxy | Server in front of the app | app के आगे लगा server |
| Health check | URL that reports app status | app की स्थिति बताने वाला URL |
| Graceful shutdown | Finish requests before exit | बंद होने से पहले चल रही requests पूरी करना |
| Container image | Packaged app + environment | app और environment का package |

---

## ⚡ 3-Line Summary
English: Package FastAPI in a Docker image, run it with Gunicorn+Uvicorn workers (or Uvicorn workers) behind nginx or a load balancer, and pass config as environment variables. Add health checks, migrate once per release, and keep state out of worker memory.
Hindi: FastAPI को Docker image में package करें, nginx या load balancer के पीछे Gunicorn+Uvicorn workers से चलाएँ और config environment variables से दें। Health checks लगाएँ, हर release पर एक बार migrate करें और state को worker memory से बाहर रखें।

---

## ➡️ Next Topic
**351. Database in Python Overview** — how Python talks to databases: drivers, DB-API, ORMs.
