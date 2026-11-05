# 95. Multi-Stage Build for Python
# हिंदी में: Python के लिए Multi-Stage Build

---

## 🔵 Simple Definition (English)
A Python multi-stage build compiles and installs dependencies (wheels) into a virtualenv in a builder stage that has gcc and headers, then copies just the virtualenv and app code into a clean `python:3.12-slim` runtime stage, running as a non-root user.

## 🔵 सरल परिभाषा (Hindi)
Python multi-stage build में builder stage (जिसमें gcc और headers होते हैं) dependencies को virtualenv में compile और install करता है, फिर सिर्फ virtualenv और app code को साफ `python:3.12-slim` runtime stage में copy किया जाता है, और app non-root user से चलती है।

---

## 🔴 Problem it Solves
Packages like `psycopg2`, `cryptography`, `uvloop` or `numpy` may need gcc, `libpq-dev`, `libffi-dev` to build. Leaving these in the final image adds 300-500 MB and gives an attacker a compiler. Also `pip` caches wheels in `~/.cache/pip`, doubling disk usage.

## 🔴 यह क्यों बना? (Hindi)
`psycopg2`, `cryptography`, `uvloop` या `numpy` जैसे packages को build के लिए gcc, `libpq-dev`, `libffi-dev` चाहिए होते हैं। इन्हें final image में छोड़ने से 300-500 MB बढ़ता है और attacker को compiler मिल जाता है। साथ ही `pip` wheels को `~/.cache/pip` में cache करता है जिससे disk दुगना भरता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → builder: python:3.12-slim + apt install gcc libpq-dev
Step 2 → python -m venv /opt/venv; pip install -r requirements.txt
Step 3 → runtime: fresh python:3.12-slim + only libpq5 (runtime lib)
Step 4 → COPY --from=builder /opt/venv /opt/venv
Step 5 → PATH=/opt/venv/bin:$PATH, copy app code, USER app
Step 6 → CMD uvicorn / gunicorn (exec form)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → builder: python:3.12-slim + apt install gcc libpq-dev
Step 2 → python -m venv /opt/venv; pip install -r requirements.txt
Step 3 → runtime: नई python:3.12-slim + सिर्फ libpq5 (runtime lib)
Step 4 → COPY --from=builder /opt/venv /opt/venv
Step 5 → PATH=/opt/venv/bin:$PATH, app code copy, USER app
Step 6 → CMD uvicorn / gunicorn (exec form)
```

---

## 🟡 Real World Example
A recommendation service (FastAPI + Postgres driver + pandas) at an e-commerce company was 1.6 GB because gcc and build-essential stayed in the image. After the multi-stage rewrite it was 380 MB; the security scanner's HIGH findings dropped from 41 to 6, because most were OS packages that only existed for compilation.

## 🟡 Real Example Hindi mein
एक e-commerce company की recommendation service (FastAPI + Postgres driver + pandas) 1.6 GB की थी क्योंकि gcc और build-essential image में रह गए थे। Multi-stage rewrite के बाद वह 380 MB हो गई; security scanner के HIGH findings 41 से 6 रह गए, क्योंकि ज़्यादातर OS packages सिर्फ compile के लिए थे।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Dockerfile - basic Python multi-stage (FastAPI)
# Builder stage (example tag, update as needed)
FROM python:3.12-slim AS builder
# Work dir
WORKDIR /build
# Create a virtualenv we can copy as a single folder
RUN python -m venv /opt/venv
# Put the venv first in PATH so pip installs into it
ENV PATH="/opt/venv/bin:$PATH"
# Copy only requirements for caching
COPY requirements.txt .
# Install deps without keeping pip cache
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.12-slim
# Work dir
WORKDIR /app
# Copy the ready virtualenv from builder
COPY --from=builder /opt/venv /opt/venv
# Use that venv
ENV PATH="/opt/venv/bin:$PATH"
# Do not write .pyc files and do not buffer logs
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# Copy the app code
COPY ./app ./app
# Start FastAPI with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 💻 Code / Config Example — Advanced

```dockerfile
# syntax=docker/dockerfile:1
# Production FastAPI image with compiled deps and non-root user
ARG PYTHON_VERSION=3.12
# ---- builder: has compilers ----
FROM python:${PYTHON_VERSION}-slim AS builder
# Avoid interactive prompts and keep Python quiet
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONDONTWRITEBYTECODE=1
# Install build-only system packages and clean apt lists in the same layer
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential libpq-dev \
 && rm -rf /var/lib/apt/lists/*
# Create venv
RUN python -m venv /opt/venv
# Activate venv through PATH
ENV PATH="/opt/venv/bin:$PATH"
# Work dir
WORKDIR /build
# Requirements first (cache layer)
COPY requirements.txt .
# Cache mount for pip downloads, kept outside the image
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# ---- runtime: no compilers ----
FROM python:${PYTHON_VERSION}-slim AS runtime
# Runtime flags
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PATH="/opt/venv/bin:$PATH"
# Only the shared library Postgres driver needs at runtime
RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq5 \
 && rm -rf /var/lib/apt/lists/*
# Create an unprivileged user and group (fixed uid helps volume permissions)
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home app
# Work dir
WORKDIR /app
# Venv from the builder
COPY --from=builder /opt/venv /opt/venv
# App code owned by the app user
COPY --chown=app:app ./app ./app
# Drop privileges
USER app
# Port
EXPOSE 8000
# Health check using Python (no curl in slim image)
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" || exit 1
# Gunicorn with uvicorn workers (gunicorn and uvicorn must be in requirements.txt)
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "-b", "0.0.0.0:8000"]
```

---

## 🟠 My Stack Integration
**FastAPI**: this Dockerfile; set workers by CPU count (`2*cores+1` is a starting point, test it). **Nginx**: reverse proxy to port 8000 with `X-Forwarded-*` headers; run uvicorn with `--proxy-headers`. **VPS/AWS**: pass `DATABASE_URL` through env or AWS Secrets Manager, not the image. **Node.js** services can sit in the same compose file.

```yaml
# docker-compose.yml - FastAPI + Postgres on a VPS
services:
  api:
    build:
      context: .                         # Dockerfile folder
      target: runtime                    # final stage
    restart: unless-stopped              # survive reboot
    environment:
      DATABASE_URL: postgresql://app:${DB_PASSWORD}@db:5432/app  # from .env
    depends_on:
      db:
        condition: service_healthy       # wait for DB readiness
    ports:
      - "127.0.0.1:8000:8000"            # only Nginx on host reaches it
  db:
    image: postgres:16-alpine            # example tag
    environment:
      POSTGRES_USER: app                 # DB user
      POSTGRES_PASSWORD: ${DB_PASSWORD}  # secret from .env file
      POSTGRES_DB: app                   # DB name
    volumes:
      - pgdata:/var/lib/postgresql/data  # persistent data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]  # readiness probe
      interval: 5s                       # check often
      retries: 10                        # then mark unhealthy
volumes:
  pgdata: {}                             # named volume
```

Security: pin versions in `requirements.txt` (use `pip-compile`/`uv` with hashes), run `pip-audit` in CI, non-root user, no compilers in runtime.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `python:3.12-alpine` for pandas/numpy.
✅ Correct: Use `-slim` (glibc, manylinux wheels), alpine builds from source and is slower and often larger.

❌ Mistake 2: Forgetting the runtime shared libs (`libpq5`) so the app fails with "libpq.so not found".
✅ Correct: Install the runtime library (not `-dev`) in the final stage.

❌ Mistake 3: Missing `PYTHONUNBUFFERED=1`, so logs appear late in `docker logs`.
✅ Correct: Set it, so logs stream instantly to CloudWatch/Loki.

---

## 🧠 Tricky Interview Question
You copy `/opt/venv` from builder to runtime. Everything works, but a different team uses `python:3.12-slim` in builder and `python:3.11-slim` in runtime and gets weird import errors. Why?

Answer: A venv contains a symlink to the builder's Python interpreter and compiled C extensions built for that ABI (e.g. `cpython-312`). Python minor versions differ, so the copied extensions and symlinks do not match. Builder and runtime must use the same Python minor version and the same OS family (use one `ARG PYTHON_VERSION` for both).

---

## ⚫ Interview Questions + Answers

Q1: Why use a venv in Docker if the container is isolated?
A1: A venv gives one self-contained folder (`/opt/venv`) that is easy to copy between stages. Alternative: `pip install --prefix=/install` and copy `/install`.

Q2: Slim vs alpine for Python?
A2: Slim (Debian glibc) supports prebuilt manylinux wheels; alpine (musl) often compiles from source. Slim is the safer default.

Q3: What does `--no-install-recommends` do?
A3: Skips optional recommended packages, keeping the layer smaller.

Q4: Why `PYTHONDONTWRITEBYTECODE`?
A4: Avoids `.pyc` files in the image and prevents writes, useful with read-only root filesystems.

Q5: Uvicorn or gunicorn?
A5: Uvicorn alone is fine behind an orchestrator running many replicas; gunicorn with `UvicornWorker` adds process management on a single VPS.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Dependencies need compilation (psycopg2, cryptography, lxml).
- You want a small, scanner-friendly production image.

❌ Avoid when:
- All deps are pure Python with wheels; one stage with `--no-cache-dir` is fine.
- Quick prototype where build time matters more.

---

## 📊 Visual Diagram
```
 +------------- builder -------------+      +----------- runtime -----------+
 | python:3.12-slim                   |      | python:3.12-slim               |
 | + gcc, libpq-dev      (heavy)      |      | + libpq5 only                  |
 | pip install -> /opt/venv           | ---> | /opt/venv (copied)             |
 +------------------------------------+ COPY | app/ code, USER app            |
        discarded after build                 +--------------------------------+
                                                     | :8000
                                                   Nginx
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| venv | Isolated Python environment folder | अलग Python environment folder |
| wheel | Prebuilt Python package | पहले से बना Python package |
| manylinux | Wheel format for glibc Linux | glibc Linux के लिए wheel format |
| libpq | Postgres client C library | Postgres client library |
| ABI | Binary compatibility of compiled code | compiled code की compatibility |

---

## ⚡ 3-Line Summary
English: Compile and install dependencies in a builder, copy the venv to a slim runtime.
Keep Python versions identical across stages and run as non-root.
Install only runtime libraries, never compilers, in the final image.
Hindi: Builder में dependencies compile/install करो, venv को slim runtime में copy करो।
दोनों stages में Python version एक जैसा रखो और non-root से चलाओ।
Final image में सिर्फ runtime libraries रखो, compilers कभी नहीं।

---

## ➡️ Next Topic
**96. Multi-Stage Build for React**: build static files with Node, serve with Nginx.
