# 350. Deploy FastAPI
# हिंदी में: FastAPI को Deploy करना

---

## 🔵 Simple Definition (English)
Deploying FastAPI means running the ASGI app with a production server (Uvicorn, often managed by Gunicorn), packaged in a Docker image, behind Nginx. A CD workflow tests the code, builds and pushes the image, then updates the container on the VPS or AWS and checks a health endpoint.

## 🔵 सरल परिभाषा (Hindi)
FastAPI deploy करने का मतलब है ASGI app को production server (Uvicorn, अक्सर Gunicorn के साथ) पर चलाना, Docker image में package करके, Nginx के पीछे। CD workflow code test करता है, image build और push करता है, फिर VPS या AWS पर container update करता है और health endpoint जाँचता है।

---

## 🔴 Problem it Solves
`uvicorn main:app --reload` is a dev command: single process, auto-reload, no supervision. Manual production deploys break on "works on my machine" Python version and dependency drift, and a crash leaves no process running. Teams also forget database migrations, health checks and graceful shutdown.

## 🔴 यह क्यों बना? (Hindi)
`uvicorn main:app --reload` development command है: एक process, auto-reload, कोई supervision नहीं। Manual production deploy में "मेरी machine पर चलता है" वाली Python version और dependency की गड़बड़ होती है, और crash होने पर कोई process बचता ही नहीं। Teams database migrations, health checks और graceful shutdown भी भूल जाती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Push to main starts the workflow
Step 2 → Install pinned deps (requirements.txt), run ruff and pytest
Step 3 → Build image: python slim base, non-root user, Gunicorn+Uvicorn workers
Step 4 → Push image tagged with commit SHA
Step 5 → SSH to the server, pull the image
Step 6 → Run alembic upgrade head in a one-off container
Step 7 → docker compose up -d api (new container replaces old)
Step 8 → Poll /health; if it fails, roll back to the previous tag
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → main पर push से workflow शुरू
Step 2 → pinned deps (requirements.txt) install, ruff और pytest चलाओ
Step 3 → Image build: python slim base, non-root user, Gunicorn+Uvicorn workers
Step 4 → Commit SHA tag के साथ image push
Step 5 → Server पर SSH, image pull
Step 6 → One-off container में alembic upgrade head चलाओ
Step 7 → docker compose up -d api (नया container पुराने की जगह)
Step 8 → /health poll करो; fail हो तो पिछले tag पर rollback
```

---

## 🟡 Real World Example
A fintech-style backend (FastAPI + PostgreSQL) serves a mobile app. The team runs 4 Gunicorn workers on a 2 vCPU AWS EC2 instance. Earlier, someone ran `git pull` and forgot `pip install`, so the new import crashed at startup. With CD, the exact same image that passed tests is what runs in production, migrations run before the switch, and the health check catches a bad release within seconds.

## 🟡 Real Example Hindi mein
Fintech जैसा backend (FastAPI + PostgreSQL) एक mobile app को serve करता है। Team 2 vCPU वाले AWS EC2 पर 4 Gunicorn workers चलाती है। पहले किसी ने `git pull` किया और `pip install` भूल गया, तो नया import startup पर crash हुआ। CD के बाद production में वही image चलती है जो tests में pass हुई, migrations switch से पहले चलते हैं, और health check खराब release को सेकंडों में पकड़ लेता है।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Dockerfile (basic)
FROM python:3.12-slim
# do not write .pyc files; flush logs immediately
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# working directory
WORKDIR /app
# install deps first (cache friendly)
COPY requirements.txt .
# no pip cache keeps the image smaller
RUN pip install --no-cache-dir -r requirements.txt
# copy the application code
COPY . .
# document the port
EXPOSE 8000
# simple production-like command (single process)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```python
# app/main.py - minimal app with a health endpoint
from fastapi import FastAPI

app = FastAPI()  # create the ASGI application


@app.get("/health")  # used by Docker, Nginx and CD to check liveness
def health():
    return {"status": "ok"}
```

## 💻 Code / Config Example — Advanced

```dockerfile
# Dockerfile (advanced) - multi-stage, non-root, Gunicorn with Uvicorn workers
# ---- builder: build wheels so the runtime stage needs no compilers ----
FROM python:3.12-slim AS builder
WORKDIR /w
# build tools only exist in this stage
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
# compile dependencies into wheel files
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ---- runtime ----
FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
# unprivileged user
RUN useradd --create-home --uid 10001 app
# install from local wheels only (fast, reproducible)
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels
# app code, owned by the unprivileged user
COPY --chown=app:app . .
USER app
EXPOSE 8000
# health probe using python (no curl needed)
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"
# Gunicorn manages workers; UvicornWorker runs the ASGI app
# keep-alive and graceful-timeout let in-flight requests finish on deploy
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", "--bind", "0.0.0.0:8000", \
     "--graceful-timeout", "30", "--timeout", "60", "--access-logfile", "-"]
```

```yaml
# .github/workflows/deploy-fastapi.yml
name: Deploy FastAPI             # workflow name
on:
  push:
    branches: [main]             # run on main only
permissions:
  contents: read                 # read code
  packages: write                # push image to GHCR
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4            # get the code
      - uses: actions/setup-python@v5        # install Python
        with:
          python-version: "3.12"
          cache: pip                         # cache pip downloads
      - run: pip install -r requirements.txt -r requirements-dev.txt   # deps
      - run: ruff check .                    # lint (assumes ruff in dev deps)
      - run: pytest -q                       # unit tests
  build-deploy:
    needs: test                              # only after tests pass
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3         # login to GHCR
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: tag                              # lower-case image name + short SHA
        run: echo "image=ghcr.io/${GITHUB_REPOSITORY,,}/api:${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"
      - uses: docker/build-push-action@v5    # build and push
        with:
          context: .
          push: true
          tags: ${{ steps.tag.outputs.image }}
      - uses: appleboy/ssh-action@v1.0.3     # deploy over SSH (example version)
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            set -e
            cd /srv/myapp
            echo "${{ secrets.GHCR_PULL_TOKEN }}" | docker login ghcr.io -u "${{ github.actor }}" --password-stdin
            PREV=$(grep '^API_IMAGE=' .env | cut -d= -f2-)   # remember the old tag
            sed -i "s|^API_IMAGE=.*|API_IMAGE=${{ steps.tag.outputs.image }}|" .env
            docker compose pull api
            docker compose run --rm api alembic upgrade head   # DB migrations
            docker compose up -d api
            for i in $(seq 1 15); do
              curl -fsS http://127.0.0.1:8000/health && exit 0   # healthy: done
              sleep 3
            done
            echo "Unhealthy, rolling back to $PREV"
            sed -i "s|^API_IMAGE=.*|API_IMAGE=${PREV}|" .env
            docker compose up -d api
            exit 1
```

---

## 🟠 My Stack Integration
FastAPI is the API behind Nginx; React or Next.js calls it at `/api/`. PostgreSQL runs as a container or on RDS. Env vars (DB URL, JWT secret) live in `/srv/myapp/.env` on the server, never in the repo.

```yaml
# /srv/myapp/docker-compose.yml (VPS)
services:
  api:
    image: ${API_IMAGE}                  # from .env, updated by CD
    restart: unless-stopped              # survive crashes and reboots
    env_file: .env                       # DATABASE_URL, SECRET_KEY, ...
    ports:
      - "127.0.0.1:8000:8000"            # reachable only by local Nginx
    depends_on:
      db:
        condition: service_healthy       # wait for Postgres readiness
  db:
    image: postgres:16-alpine            # example tag
    volumes:
      - pgdata:/var/lib/postgresql/data  # persistent data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 10
volumes:
  pgdata:
```

```nginx
# Nginx location for the API
location /api/ {
  proxy_pass http://127.0.0.1:8000/;      # trailing slash strips /api prefix
  proxy_set_header Host $host;            # preserve host
  proxy_set_header X-Forwarded-For $remote_addr;
  proxy_set_header X-Forwarded-Proto $scheme;
  proxy_read_timeout 60s;                 # match gunicorn --timeout
}
```

Security: run `uvicorn`/Gunicorn with `--proxy-headers` or `--forwarded-allow-ips` appropriately behind Nginx, restrict CORS origins, keep secrets in `.env` with `chmod 600`, and do not expose `/docs` publicly if the API is private.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `--reload` in production.
✅ Correct: Use Gunicorn with `UvicornWorker` or plain Uvicorn without reload.

❌ Mistake 2: Running migrations from every worker at startup.
✅ Correct: Run `alembic upgrade head` once as a separate step before starting the new container.

❌ Mistake 3: Binding to `127.0.0.1` inside the container.
✅ Correct: Bind to `0.0.0.0` in the container and restrict exposure with the published port (`127.0.0.1:8000:8000`).

❌ Mistake 4: Unpinned dependencies.
✅ Correct: Pin versions (or use a lock file) so CI and production install the same packages.

❌ Mistake 5: No health check, so a crashing release looks "deployed".
✅ Correct: Fail the pipeline unless `/health` returns 200.

---

## 🧠 Tricky Interview Question
You scale Gunicorn to 8 workers and the app starts opening too many Postgres connections and failing. Why, and what do you do?

Answer: Each worker process has its own SQLAlchemy pool. With `pool_size=10`, 8 workers can open 80 connections, exceeding Postgres `max_connections` (default 100) when combined with other services. Reduce the per-worker pool, use PgBouncer, and size workers to the CPU count rather than "more is better".

---

## ⚫ Interview Questions + Answers

Q1: Uvicorn vs Gunicorn - why both?
A1: Uvicorn is the ASGI server; Gunicorn is a process manager that supervises multiple Uvicorn workers and restarts crashed ones. Uvicorn alone also supports `--workers`, so either is acceptable.

Q2: How many workers should I run?
A2: A common start is `2 x CPU cores + 1` for sync apps; for async FastAPI start near the core count and measure, as memory and DB connections are the real limit.

Q3: How do you do zero-downtime deploys?
A3: Run two replicas or blue-green behind Nginx, use a graceful shutdown timeout, and ensure migrations are backward compatible (see 351 and 355).

Q4: Where does Alembic run?
A4: As a separate step or one-off container before switching traffic, using the new image so the migrations match the new code.

Q5: How do you keep `/docs` safe?
A5: Disable it in production (`docs_url=None`), or protect it with auth or an Nginx IP allowlist.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have a Python API that needs predictable, repeatable releases.
- You can containerize and have a VPS, EC2 or ECS to run it.

❌ Avoid when:
- It is a tiny function with sporadic traffic: AWS Lambda may be cheaper.
- You cannot run migrations safely yet: fix the data-change process first.

---

## 📊 Visual Diagram
```
 push main --> [pytest/ruff] --> [docker build] --> GHCR api:abc1234
                                                        |
                                                  SSH + docker pull
                                                        v
 Client --> Nginx :443 --> /api/ --> [ gunicorn + 4 uvicorn workers ] --> PostgreSQL
                                          ^ alembic upgrade head (before switch)
                                          ^ /health poll, rollback on failure
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ASGI | Async Python server interface | Async Python server का interface |
| Gunicorn | Process manager for workers | workers संभालने वाला process manager |
| UvicornWorker | Gunicorn worker class running ASGI | ASGI चलाने वाला Gunicorn worker |
| Alembic | SQLAlchemy migration tool | database migration tool |
| Health check | Endpoint proving liveness | liveness जाँचने वाला endpoint |

---

## ⚡ 3-Line Summary
English: Package FastAPI in a non-root image run by Gunicorn/Uvicorn and deploy it by SHA tag.
Run migrations once before switching and verify with a health check, rolling back on failure.
Keep secrets in server env files and expose the app only through Nginx.
Hindi: FastAPI को non-root image में package करो जिसे Gunicorn/Uvicorn चलाए, और SHA tag से deploy करो।
Switch से पहले migration एक बार चलाओ और health check से जाँचो, fail हो तो rollback।
Secrets server की env file में रखो और app को सिर्फ Nginx से expose करो।

---

## ➡️ Next Topic
**351. Blue-Green Deployment** — running two identical environments to switch traffic with zero downtime and instant rollback.
