---

# 440. Docker + Python Setup
# हिंदी में: Docker + Python Setup

---

## 🔵 Simple Definition (English)
Docker packages your app, Python version, system libraries and dependencies into an image. A container is a running copy of that image. The same image runs identically on your laptop, CI and production, so "it works on my machine" stops being a problem.

## 🔵 सरल परिभाषा (Hindi)
Docker आपके app, Python version, system libraries और dependencies को एक image में पैक कर देता है। Container उस image की चलती हुई copy है। वही image laptop, CI और production पर एक जैसी चलती है, इसलिए "मेरी machine पर तो चल रहा था" की समस्या खत्म हो जाती है।

---

## 🔴 Problem it Solves
Without Docker, each server needs the correct Python version, OS packages (`libpq`, `gcc`), the right pip versions and matching environment variables. Servers drift apart, a new teammate loses a day setting up, and a deploy breaks because production has Python 3.10 while you tested on 3.13. A Docker image freezes all of that into one artifact you build once and run anywhere.

## 🔴 यह क्यों बना? (Hindi)
Docker के बिना हर server को सही Python version, OS packages (`libpq`, `gcc`), सही pip versions और मिलते-जुलते environment variables चाहिए। Servers अलग-अलग हो जाते हैं, नए teammate का एक दिन setup में जाता है, और deploy इसलिए टूटता है कि production में Python 3.10 है जबकि आपने 3.13 पर test किया। Docker image यह सब एक artifact में जमा देती है जिसे एक बार बनाओ और कहीं भी चलाओ।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Dockerfile: recipe (base image, copy files, install deps, start command)
Step 2 → docker build -t orders-api:1.0 .   executes each line as a cached LAYER
Step 3 → Copy requirements.txt FIRST and pip install; copy code AFTER -> code edits reuse the cache
Step 4 → .dockerignore keeps .git, .venv, __pycache__, .env out of the image
Step 5 → docker run -p 8000:8000 --env-file .env orders-api:1.0   starts a container
Step 6 → Container runs ONE main process (uvicorn); logs go to stdout
Step 7 → HEALTHCHECK probes /health; orchestrator restarts unhealthy containers
Step 8 → docker push to a registry (Docker Hub, ECR, GHCR); servers pull and run it
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Dockerfile: recipe (base image, files copy, deps install, start command)
Step 2 → docker build -t orders-api:1.0 .  हर line को cached LAYER की तरह चलाता है
Step 3 → पहले requirements.txt copy करके pip install; code बाद में -> code बदलने पर cache reuse होता है
Step 4 → .dockerignore .git, .venv, __pycache__, .env को image से बाहर रखता है
Step 5 → docker run -p 8000:8000 --env-file .env orders-api:1.0 container चालू करता है
Step 6 → Container में एक main process (uvicorn); logs stdout पर
Step 7 → HEALTHCHECK /health जाँचता है; orchestrator unhealthy container restart करता है
Step 8 → docker push से registry (Docker Hub, ECR, GHCR) में; servers pull करके चलाते हैं
```

---

## 🟡 Real World Example
A fintech team builds one image `payments-api:<git-sha>` in GitHub Actions. The same image is run by a developer with `docker run`, by the staging server and by production on ECS. When a bug appears, they roll back by starting the previous tag. The image includes Python 3.13, `libpq` for PostgreSQL and exactly the pinned packages from `requirements.txt`.

## 🟡 Real Example Hindi mein
एक fintech team GitHub Actions में एक ही image `payments-api:<git-sha>` बनाती है। वही image developer `docker run` से, staging server और production ECS पर चलाते हैं। Bug आए तो पिछला tag चालू करके rollback हो जाता है। Image में Python 3.13, PostgreSQL के लिए `libpq` और `requirements.txt` के pinned packages ही होते हैं।

---

## 💻 Code Example — Basic
Dockerfile (**not run**: no Docker daemon in this environment, so the image was never built; the Python app below was run):

```dockerfile
# Dockerfile  (Docker comments must be on their own line, never after an instruction)

# small official base image, pinned minor version
FROM python:3.13-slim

# no .pyc files; logs appear immediately
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# all next commands run here
WORKDIR /app

# copy ONLY the deps file first (cache trick)
COPY requirements.txt .
# this layer is reused until requirements change
RUN pip install --no-cache-dir -r requirements.txt

# now copy the code (changes often, cheap layer)
COPY . .

# never run as root inside the container
RUN useradd --create-home app
USER app

# documentation only; -p does the real publishing
EXPOSE 8000
# exec form (JSON list): SIGTERM reaches uvicorn directly
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```text
# .dockerignore
.git
.venv
__pycache__/
*.pyc
.env
tests/
```

The app that runs inside it, with container-friendly logging and lifespan hooks:

```python
# Basic: a container-friendly FastAPI app (config from env, logs to stdout, /health)
import logging                                    # standard logging
import os                                         # env vars
import sys                                        # stdout stream
from contextlib import asynccontextmanager       # lifespan helper
from collections.abc import AsyncIterator         # lifespan return type

from fastapi import FastAPI                       # framework
from fastapi.testclient import TestClient         # local test

logging.basicConfig(stream=sys.stdout, level=logging.INFO,   # containers: log to stdout, not files
                    format="%(levelname)s %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)   # hide test-client request logs
log = logging.getLogger("app")                    # module logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    log.info("starting in %s mode", os.getenv("APP_ENV", "dev"))   # startup hook
    yield                                         # app serves requests here
    log.info("shutting down (docker stop sends SIGTERM)")          # graceful shutdown hook


app: FastAPI = FastAPI(lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}                       # used by HEALTHCHECK


with TestClient(app) as client:                   # `with` runs startup + shutdown
    print(client.get("/health").json())           # {'status': 'ok'}

# Output (real run, Python 3.13):
# INFO starting in dev mode
# {'status': 'ok'}
# INFO shutting down (docker stop sends SIGTERM)
```

## 💻 Code Example — Advanced
`healthcheck.py` uses only the standard library, so the image does not need `curl` or `requests`. It is wired in with `HEALTHCHECK CMD python healthcheck.py`. The demo starts a fake server, checks it, then shuts it down:

```python
# Advanced: healthcheck.py - what Docker's HEALTHCHECK runs inside the container
import sys                                        # exit codes
import threading                                  # run a fake server in the background
import urllib.request                             # stdlib only: no extra pip package in the image
from http.server import BaseHTTPRequestHandler, HTTPServer   # demo server


def check(url: str, timeout: float = 2.0) -> int:
    """Return 0 if healthy, 1 otherwise (Docker uses exit code 0/1)."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:   # GET the endpoint
            return 0 if resp.status == 200 else 1   # only 200 is healthy
    except Exception:                             # refused, timeout, 5xx raises HTTPError
        return 1                                  # unhealthy


class Ok(BaseHTTPRequestHandler):                 # fake FastAPI /health
    def do_GET(self) -> None:
        self.send_response(200 if self.path == "/health" else 500)
        self.end_headers()
        self.wfile.write(b"{}")
    def log_message(self, *args: object) -> None:  # silence request logs
        pass


server = HTTPServer(("127.0.0.1", 0), Ok)         # port 0 = pick any free port
port = server.server_address[1]
threading.Thread(target=server.serve_forever, daemon=True).start()   # serve in background
print("healthy  ->", check(f"http://127.0.0.1:{port}/health"))   # 0
print("500      ->", check(f"http://127.0.0.1:{port}/boom"))     # 1
server.shutdown()                                 # stop our demo server
print("no server ->", check(f"http://127.0.0.1:{port}/health"))  # 1

if __name__ == "__main__":                        # in the container: python healthcheck.py
    pass                                          # sys.exit(check("http://127.0.0.1:8000/health"))

# Output (real run, Python 3.13):
# healthy  -> 0
# 500      -> 1
# no server -> 1
```

Dockerfile lines that use it (**not run**):

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import sys,urllib.request as u; sys.exit(0 if u.urlopen('http://127.0.0.1:8000/health', timeout=2).status==200 else 1)"
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python image | Node.js image |
|---------|-------------|---------------|
| Base image | `python:3.13-slim` | `node:22-alpine` |
| Deps file (copy first) | `requirements.txt` | `package.json` + lockfile |
| Install | `pip install --no-cache-dir -r ...` | `npm ci --omit=dev` |
| Start | `uvicorn main:app` | `node server.js` |
| Env flag | `PYTHONUNBUFFERED=1` | `NODE_ENV=production` |

```python
# Python way — Dockerfile essentials (shown as comments)
# FROM python:3.13-slim
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . .
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```
```javascript
// JavaScript way — same pattern, different files (Dockerfile as comments)
// FROM node:22-alpine
// COPY package*.json ./
// RUN npm ci --omit=dev
// COPY . .
// CMD ["node", "server.js"]
```

Key difference: alpine images use musl libc and many Python wheels (numpy, pandas, psycopg) are built for glibc, so they compile slowly or fail. Prefer `-slim` (Debian) for Python; alpine is common for Node.

---

## 🟠 FastAPI Connection
FastAPI in a container must listen on `0.0.0.0`, not `127.0.0.1` (otherwise `-p 8000:8000` cannot reach it). Configuration comes from env vars (`--env-file`), logs go to stdout, and the lifespan shutdown hook runs when `docker stop` sends SIGTERM, which only works if `CMD` is in exec form (JSON list), so uvicorn is PID 1 and receives the signal. The official FastAPI docs show a one-process-per-container approach; scale by running more containers.

```python
# FastAPI example — config object read once from environment variables set by docker run -e
import os
from fastapi import FastAPI

app = FastAPI(title=os.getenv("APP_NAME", "orders-api"))

@app.get("/config")
def config() -> dict[str, str]:
    return {"env": os.getenv("APP_ENV", "dev")}   # docker run -e APP_ENV=production
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `COPY . .` before `pip install`, so every code change reinstalls all packages
✅ Correct: copy `requirements.txt`, install, then copy the code

```dockerfile
# Wrong
COPY . .
RUN pip install -r requirements.txt
# Right
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
```

❌ Mistake 2: Shell-form `CMD`, or host `127.0.0.1`
✅ Correct: exec-form `CMD` with `--host 0.0.0.0`

```dockerfile
# Wrong: shell form runs under /bin/sh so SIGTERM may never reach uvicorn,
# and 127.0.0.1 is unreachable from outside the container
CMD uvicorn main:app --host 127.0.0.1
# Right
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

❌ Mistake 3: Baking secrets or `.env` into the image
✅ Correct: pass secrets at run time; list `.env` in `.dockerignore`

```bash
# Wrong: COPY .env /app/.env   (anyone who pulls the image can read it with docker history / run)
# Right
docker run --env-file .env -p 8000:8000 orders-api:1.0
```

---

## 🧠 Tricky Interview Question

```dockerfile
# Dockerfile
FROM python:3.13-slim
WORKDIR /app
RUN echo "v1" > version.txt
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "-c", "print(open('/app/version.txt').read())"]
```
```python
# Question: you change only a comment in main.py and rebuild. Which steps are rebuilt, and what happens
# if you instead edit requirements.txt? Then: docker run is started with `-v $(pwd)/data:/app`
# - what does the container print?
```
Answer: Changing `main.py` invalidates the cache at `COPY . .`, so that layer and everything after it (`pip install`, `CMD` metadata) rebuild; the earlier layers are cached. Here pip reinstalls everything on every code change, which is the mistake from above. Changing `requirements.txt` also rebuilds from `COPY . .` on. With `-v $(pwd)/data:/app`, the bind mount **hides** the image's `/app` directory, so `version.txt` from the image is invisible and Python raises `FileNotFoundError` (unless `data/version.txt` exists on the host). A mount replaces the path inside the container, it does not merge with it.

---

## ⚫ Interview Questions + Answers

Q1: Image vs container?
A1: An image is a read-only template made of layers (like a class). A container is a running instance of it with a thin writable layer (like an object). Many containers can run from one image.

Q2: Why order Dockerfile lines carefully?
A2: Each instruction is a cached layer. Once a layer changes, all later layers rebuild. Put rarely-changing steps (OS packages, `requirements.txt` install) first and frequently-changing steps (code copy) last.

Q3: `CMD` vs `ENTRYPOINT`?
A3: `ENTRYPOINT` is the fixed executable; `CMD` gives default arguments that `docker run` can override. A common pattern is `ENTRYPOINT ["uvicorn"]` with `CMD ["main:app", ...]`, or just `CMD` alone for apps. Use the exec (JSON) form for both.

Q4: How do you keep Python images small?
A4: Use `-slim`, `--no-cache-dir`, a `.dockerignore`, multi-stage builds (next topic), and no build tools in the final stage. A typical FastAPI image lands around 150-250 MB.

Q5: How does data persist?
A5: Containers are disposable; the writable layer is deleted with the container. Use volumes (`-v pgdata:/var/lib/postgresql/data`) or external services (RDS, S3) for state.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want identical environments from laptop to production
- You deploy to ECS, Kubernetes, Cloud Run, Render, Railway or Fly.io
- CI needs reproducible builds and tests
- Multiple services need isolated dependencies

❌ Avoid when:
- A single script on one server where venv + systemd is simpler
- Very tight RAM on tiny machines (Docker daemon overhead)
- Heavy GPU work without the NVIDIA container toolkit set up

---

## 📊 Visual Diagram
```
 Dockerfile ──build──> IMAGE (layers, read-only)
                         [ python:3.13-slim ]
                         [ pip install deps ]   <- cached until requirements change
                         [ COPY code        ]
                              |
                          docker run
                              v
                       CONTAINER = image + writable layer
                       uvicorn main:app  (PID 1) --> port 8000 --(-p)--> host
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Image | Read-only package of app + environment | app + environment का read-only पैकेज |
| Container | Running instance of an image | image का चलता हुआ instance |
| Layer | Cached step of the build | build का cached चरण |
| Registry | Store of images (Docker Hub, ECR) | images का भंडार |
| Volume | Persistent storage outside the container | container के बाहर स्थायी storage |
| `.dockerignore` | Files excluded from the build | build से बाहर रखी फाइलें |

---

## ⚡ 3-Line Summary
English: Docker bundles the app and its environment into an image that runs the same everywhere. Order the Dockerfile for cache, run as non-root with exec-form CMD, and bind to 0.0.0.0. Keep secrets and state outside the image.
Hindi: Docker app और उसके environment को एक image में बाँधता है जो हर जगह एक जैसी चलती है। Dockerfile को cache के हिसाब से क्रम में रखो, non-root user और exec-form CMD से चलाओ और 0.0.0.0 पर bind करो। Secrets और state image के बाहर रखो।

---

## ➡️ Next Topic
**441. Multi-Stage Docker Build** — shrink the image and remove build tools from production.
