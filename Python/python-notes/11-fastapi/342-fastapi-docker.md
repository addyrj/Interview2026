---

# 342. FastAPI + Docker
# हिंदी में: FastAPI + Docker (Container में API चलाना)

---

## 🔵 Simple Definition (English)
Docker packages your FastAPI app, its Python version and all dependencies into an image that runs the same way on any machine. You describe the image in a `Dockerfile`, and run several containers together (API, worker, database, Redis) with `docker compose`.

## 🔵 सरल परिभाषा (Hindi)
Docker आपके FastAPI app, उसके Python version और सभी dependencies को एक image में पैक करता है जो किसी भी machine पर एक जैसे चलती है। आप image का वर्णन `Dockerfile` में करते हैं, और कई containers (API, worker, database, Redis) को `docker compose` से साथ चलाते हैं।

---

## 🔴 Problem it Solves
"It works on my machine" bugs: different Python versions, missing system libraries, different package versions between dev and production. Manual server setup is slow and not repeatable. A container image is built once, tested, and deployed unchanged everywhere. It also isolates services and makes scaling (more containers) and rollbacks (older image tag) easy.

## 🔴 यह क्यों बना? (Hindi)
"मेरी machine पर तो चल रहा है" वाले bugs: अलग Python versions, गायब system libraries, dev और production के बीच अलग package versions। Server हाथ से setup करना धीमा और दोहराने योग्य नहीं है। Container image एक बार बनती है, test होती है और हर जगह बिना बदले deploy होती है। यह services को अलग रखता है और scaling (ज्यादा containers) और rollback (पुराना image tag) आसान बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write Dockerfile: FROM python:3.13-slim (base image)
Step 2 → COPY requirements.txt first and RUN pip install (this layer is cached)
Step 3 → COPY the app code afterwards (code changes do not redo pip install)
Step 4 → Create a non-root user and switch to it (USER app)
Step 5 → CMD runs uvicorn on 0.0.0.0 (not 127.0.0.1) so the port is reachable
Step 6 → docker build -t myapi:1.0 .   creates the image
Step 7 → docker run -p 8000:8000 myapi:1.0   starts a container
Step 8 → docker compose up   starts API + worker + db + redis together
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Dockerfile लिखें: FROM python:3.13-slim (base image)
Step 2 → पहले requirements.txt COPY करें और RUN pip install (यह layer cache होती है)
Step 3 → उसके बाद app code COPY करें (code बदलने पर pip install दोबारा नहीं चलता)
Step 4 → non-root user बनाएं और उसी पर switch करें (USER app)
Step 5 → CMD uvicorn को 0.0.0.0 पर चलाता है (127.0.0.1 नहीं) ताकि port पहुँच योग्य हो
Step 6 → docker build -t myapi:1.0 .   image बनाता है
Step 7 → docker run -p 8000:8000 myapi:1.0   container शुरू करता है
Step 8 → docker compose up   API + worker + db + redis एक साथ शुरू करता है
```

---

## 🟡 Real World Example
A startup ships its FastAPI backend: the CI pipeline builds the image on every merge, pushes it to a registry (Docker Hub / AWS ECR), and the server pulls and restarts it. Locally, `docker compose up` starts PostgreSQL, Redis, the API and a Celery worker with one command, so a new developer is productive in minutes instead of a day.

## 🟡 Real Example Hindi mein
एक startup अपना FastAPI backend ship करता है: CI pipeline हर merge पर image बनाती है, उसे registry (Docker Hub / AWS ECR) में push करती है, और server उसे pull करके restart करता है। Local में `docker compose up` एक command से PostgreSQL, Redis, API और Celery worker शुरू कर देता है, इसलिए नया developer एक दिन की बजाय मिनटों में काम शुरू कर लेता है।

---

## 💻 Code Example — Basic
```dockerfile
# Dockerfile — basic version (comments sit on their own lines: Docker does not allow trailing comments after an instruction; NOT built, no Docker daemon here)
# small official Python image
FROM python:3.13-slim
# all next commands run in /app
WORKDIR /app
# copy only the dependency list first (layer cache!)
COPY requirements.txt .
# install packages, no pip cache in the image
RUN pip install --no-cache-dir -r requirements.txt
# now copy the application code
COPY . .
# documentation: app listens on 8000
EXPOSE 8000
# exec form: signals reach uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
```python
# app/main.py — the app inside the container (verified: /health responds with TestClient)
from fastapi import FastAPI                   # FastAPI class

app: FastAPI = FastAPI()                      # create the app


@app.get("/health")                           # used by Docker/Kubernetes health checks
def health() -> dict[str, str]:               # simple, no database call
    return {"status": "ok"}                   # healthy

# Output of TestClient(app).get("/health").json():
# {'status': 'ok'}
```
```text
# requirements.txt (pin versions in real projects)
fastapi
uvicorn[standard]
```
Commands (not run here): `docker build -t myapi:1.0 .` then `docker run --rm -p 8000:8000 myapi:1.0`, then open `http://localhost:8000/health`.

## 💻 Code Example — Advanced
```dockerfile
# Dockerfile — production: multi-stage, non-root, healthcheck (NOT built here; review the syntax)
# stage 1: build wheels
FROM python:3.13-slim AS builder
# work folder for the build stage
WORKDIR /build
# dependency list
COPY requirements.txt .
# build wheels once
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# stage 2: small final image
FROM python:3.13-slim AS runtime
# no .pyc files; logs appear immediately
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
# app folder
WORKDIR /app
# take only the built wheels from stage 1
COPY --from=builder /wheels /wheels
# dependency list again
COPY requirements.txt .
# install offline from wheels, then delete them
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels
# create a non-root user
RUN useradd --create-home --uid 10001 app
# app code owned by that user
COPY --chown=app:app . .
# never run as root in production
USER app
# port documentation
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```
```yaml
# docker-compose.yml — API + Celery worker + PostgreSQL + Redis (YAML parsed OK with PyYAML; NOT run: no Docker Compose here)
services:
  api:
    build: .                                  # build from the Dockerfile above
    ports: ["8000:8000"]                      # host:container
    environment:
      DATABASE_URL: postgresql+asyncpg://app:secret@db:5432/app   # "db" is the service name = hostname
      REDIS_URL: redis://redis:6379/0         # "redis" resolves inside the compose network
    depends_on:
      db:
        condition: service_healthy            # wait until postgres is really ready
      redis:
        condition: service_started            # redis starts fast
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 3s
      retries: 3
  worker:
    build: .                                  # same image as the API
    command: celery -A app.worker.celery_app worker --loglevel=INFO   # different command
    depends_on: [redis]                       # needs the broker
  db:
    image: postgres:17-alpine                 # official database image
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret               # use secrets / .env file in real life
      POSTGRES_DB: app
    volumes: [pgdata:/var/lib/postgresql/data]   # data survives container restarts
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      retries: 5
  redis:
    image: redis:7-alpine                     # broker + cache
volumes:
  pgdata:                                     # named volume
```
Verified: the YAML parses and `depends_on.db.condition` is `service_healthy` (checked with `yaml.safe_load`). The Dockerfiles and the compose stack were NOT built or started: this environment has no Docker daemon. The `docker compose` plugin is also not available here.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (FastAPI) | JavaScript (Node/Express) |
|---------|------------------|---------------------------|
| Base image | `python:3.13-slim` | `node:22-alpine` |
| Install step | `pip install -r requirements.txt` | `npm ci --omit=dev` |
| Start command | `uvicorn app.main:app --host 0.0.0.0` | `node server.js` |
| Cache trick | copy requirements first | copy package*.json first |
| Env flags | `PYTHONUNBUFFERED=1` | `NODE_ENV=production` |

```dockerfile
# Python way
FROM python:3.13-slim
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
```dockerfile
# JavaScript way
FROM node:22-alpine
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
CMD ["node", "server.js"]
```

Key difference: the pattern is identical (dependency file first, code second, start command last). Python adds the ASGI server (uvicorn) as the entry point, and you must bind to `0.0.0.0` so the port is reachable from outside the container.

---

## 🟠 FastAPI Connection
Inside the container, FastAPI is started by uvicorn. For more CPU use, run several uvicorn workers (`--workers N`) per container or, in Kubernetes, run several containers with one worker each (preferred). Configuration comes from environment variables (Pydantic `BaseSettings`/`pydantic-settings`), never baked into the image. Run Alembic migrations as a separate step (`docker compose run --rm api alembic upgrade head`) or an init job, then start the API. Put the `/health` route to use for Docker, load balancer and Kubernetes probes. Behind a proxy use `--proxy-headers`.

```python
# FastAPI example — settings from environment variables (works the same in Docker)
import os                                                       # read env vars
from fastapi import FastAPI                                     # framework

app: FastAPI = FastAPI()                                        # create app
DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///local.db")   # set by docker compose


@app.get("/info")                                               # which database am I using?
def info() -> dict[str, str]:                                   # never expose secrets in real apps!
    return {"db": DATABASE_URL.split("://")[0]}                 # only the scheme
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `--host 127.0.0.1` (default) inside the container
✅ Correct: `--host 0.0.0.0`, otherwise the port mapping cannot reach the app

```dockerfile
# Wrong — only reachable from inside the container
CMD ["uvicorn", "app.main:app"]
# Right
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

❌ Mistake 2: `COPY . .` before installing dependencies
✅ Correct: copy `requirements.txt` first so Docker caches the install layer

```dockerfile
# Wrong — every code change reinstalls all packages (slow builds)
COPY . .
RUN pip install -r requirements.txt
# Right
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

❌ Mistake 3: Running as root, shipping secrets/`.env` in the image, no `.dockerignore`
✅ Correct: `USER app`, pass secrets at runtime, and add `.dockerignore` (`.git`, `.venv`, `__pycache__`, `.env`)

```dockerfile
# Wrong
ENV DATABASE_PASSWORD=supersecret
# Right — provided at runtime: docker run -e DATABASE_PASSWORD=... or compose env_file / secrets
```

---

## 🧠 Tricky Interview Question

```dockerfile
# Why does "docker stop" take 10 seconds and the app never shuts down gracefully?
CMD uvicorn app.main:app --host 0.0.0.0
```
Answer: This is the shell form of `CMD`. Docker runs it as `/bin/sh -c "uvicorn ..."`, so the shell is PID 1 and does not forward `SIGTERM` to uvicorn. After the timeout (10 s default) Docker sends `SIGKILL`, which kills the app abruptly (in-flight requests are lost, lifespan shutdown code never runs). Use the exec form `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]` so uvicorn is PID 1 and handles `SIGTERM` for a graceful shutdown (or add `--init`/tini).

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between an image and a container?
A1: An image is a read-only template (layers). A container is a running instance of an image with a thin writable layer. Many containers can run from one image.

Q2: Why multi-stage builds?
A2: They keep build tools (compilers, headers) out of the final image, making it smaller and with fewer vulnerabilities. Copy only the artifacts (wheels, venv) into the runtime stage.

Q3: How do containers talk to each other in compose?
A3: Compose creates a network, and each service name is a DNS hostname: the API connects to `db:5432` and `redis:6379`. `localhost` inside a container means that container itself, a classic bug.

Q4: How many uvicorn/gunicorn workers per container?
A4: One worker per container if an orchestrator (Kubernetes, ECS) handles scaling; otherwise about the number of CPU cores (`--workers N` or `gunicorn -k uvicorn.workers.UvicornWorker`). Each worker is a separate process with its own memory and DB pool.

Q5: How do you handle database data and secrets?
A5: Data lives in volumes (`pgdata`), not in the container's writable layer. Secrets come from environment variables, `env_file`, Docker/Kubernetes secrets, or a secret manager; never in the image or Git.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Deploying to any cloud, VPS, Kubernetes or ECS
- You want identical dev/CI/prod environments
- You run several services (API, worker, DB, Redis) together

❌ Avoid when:
- A tiny one-off script on one machine
- Heavy GPU/driver setups you cannot containerise easily (need NVIDIA toolkit)
- You use Docker as a database host for production data with no volumes or backups

---

## 📊 Visual Diagram
```
 Dockerfile ──docker build──► Image (layers: python, pip install, app code)
                                   │ docker run / compose up
        ┌──────────────────────────┼───────────────────────────┐
        ▼                          ▼                           ▼
   api container            worker container           db / redis containers
   uvicorn :8000            celery worker              postgres :5432 (volume)
        │                          │                           ▲
        └──────── compose network: hostnames "db", "redis" ────┘
   host:8000 ◄── ports mapping
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Image | Read-only app template | केवल-पढ़ने योग्य app template |
| Container | Running instance of an image | Image का चलता हुआ instance |
| Layer cache | Reuse of unchanged build steps | अपरिवर्तित build steps का पुनः उपयोग |
| Multi-stage build | Build in one stage, ship another | एक stage में build, दूसरे से ship |
| Volume | Persistent storage outside container | Container के बाहर स्थायी storage |
| Health check | Probe that tells if app is alive | App जीवित है या नहीं बताने वाला probe |

---

## ⚡ 3-Line Summary
English: Docker packages FastAPI and its dependencies into an image; use a slim base, copy requirements first, run as non-root, and start uvicorn with `--host 0.0.0.0` in exec form. Docker Compose runs the API, worker, database and Redis together using service names as hostnames. Configuration and secrets come from environment variables, not the image.
Hindi: Docker FastAPI और उसकी dependencies को image में पैक करता है; slim base उपयोग करें, requirements पहले copy करें, non-root चलाएं, और uvicorn को exec form में `--host 0.0.0.0` के साथ शुरू करें। Docker Compose service names को hostnames बनाकर API, worker, database और Redis साथ चलाता है। Configuration और secrets environment variables से आते हैं, image से नहीं।

---

## ➡️ Next Topic
**343. Next topic in the FastAPI section** — continue with deployment topics such as Gunicorn with Uvicorn workers, reverse proxies and production tuning.
