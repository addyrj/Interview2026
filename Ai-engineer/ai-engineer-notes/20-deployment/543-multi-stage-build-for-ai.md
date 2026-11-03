
---

# 543. Multi-Stage Build for AI
# हिंदी में: AI के लिए Multi-Stage Build

---

## 🔵 Simple Definition (English)
A multi-stage Docker build uses several `FROM` steps in one Dockerfile. Early stages have compilers and build tools to install dependencies; the final stage copies only what is needed to run. The result is a smaller, faster and safer image for your FastAPI / LangChain service.

## 🔵 सरल परिभाषा (Hindi)
Multi-stage Docker build में एक Dockerfile में कई `FROM` steps होते हैं। शुरुआती stages में compilers और build tools होते हैं जो dependencies install करते हैं; आखिरी stage में सिर्फ वही copy होता है जो चलाने के लिए चाहिए। नतीजा: FastAPI / LangChain service के लिए छोटी, तेज़ और सुरक्षित image।

---

## 🔴 Problem it Solves
- A single-stage image keeps build tools, caches and headers: often 1-2 GB for a Python AI app.
- Big images pull slowly, so deploys, autoscaling and cold starts are slow.
- More packages in the image means more vulnerabilities and a larger attack surface.
- Secrets or source files used only at build time may stay in image layers.

## 🔴 यह क्यों बना? (Hindi)
- Single-stage image में build tools, caches और headers रह जाते हैं: Python AI app के लिए अक्सर 1-2 GB।
- बड़ी images धीरे pull होती हैं, इसलिए deploy, autoscaling और cold start धीमे हो जाते हैं।
- Image में ज़्यादा packages यानी ज़्यादा vulnerabilities और बड़ा attack surface।
- जो secrets या source files सिर्फ build में चाहिए थे, वे image layers में रह सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Stage "builder": FROM python:3.12-slim, install build tools, create a virtualenv
Step 2 → In builder: copy requirements first, pip install into /opt/venv (layer cached)
Step 3 → Stage "runtime": a fresh FROM python:3.12-slim (no compilers)
Step 4 → COPY --from=builder /opt/venv /opt/venv (only the installed packages)
Step 5 → Copy app source code (changes most often, so last)
Step 6 → Create non-root user, set PATH, EXPOSE port, HEALTHCHECK
Step 7 → CMD uvicorn app.main:app (exec form so signals reach the process)
Step 8 → Build, check size with `docker images`, scan with a vulnerability scanner
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Stage "builder": FROM python:3.12-slim, build tools install, virtualenv बनाओ
Step 2 → Builder में: पहले requirements copy करो, pip install को /opt/venv में करो (layer cache)
Step 3 → Stage "runtime": नया FROM python:3.12-slim (compilers नहीं)
Step 4 → COPY --from=builder /opt/venv /opt/venv (सिर्फ installed packages)
Step 5 → App source code copy करो (सबसे ज़्यादा बदलता है, इसलिए आखिर में)
Step 6 → Non-root user बनाओ, PATH set करो, port EXPOSE, HEALTHCHECK
Step 7 → CMD uvicorn app.main:app (exec form ताकि signals process तक पहुँचें)
Step 8 → Build करो, `docker images` से size देखो, vulnerability scanner चलाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: The API uses FastAPI, LangChain, a Qdrant client and `numpy`. A single-stage image with `build-essential` is about 1.4 GB (illustrative). With a multi-stage build the final image has only the venv and code, which is often several hundred MB smaller. When Kubernetes scales from 2 to 10 pods during month-end customs rush, smaller images pull faster, so new pods are ready sooner.

**Zomato-style AI**: A recommendation API is rebuilt 10 times a day. Ordering the Dockerfile so dependencies are cached means rebuilds take seconds when only code changes.

## 🟡 Real Example Hindi mein
**Tariff Classification System**: API में FastAPI, LangChain, Qdrant client और `numpy` हैं। `build-essential` वाली single-stage image लगभग 1.4 GB (illustrative) होती है। Multi-stage build में final image में सिर्फ venv और code होता है, जो अक्सर कई सौ MB छोटी होती है। Month-end customs rush में Kubernetes जब 2 से 10 pods करता है, छोटी images जल्दी pull होती हैं, इसलिए नए pods जल्दी तैयार होते हैं।

**Zomato-style AI**: Recommendation API दिन में 10 बार rebuild होती है। Dockerfile का order ऐसा रखो कि dependencies cached रहें, तो सिर्फ code बदलने पर rebuild सेकंडों में होता है।

---

## 💻 Code Example — Basic
```python
# Basic: a Python helper that checks a Dockerfile follows multi-stage best practices.
# (The Dockerfile itself is shown in the Advanced block below.)
from pathlib import Path                               # file access

def lint_dockerfile(text: str) -> list[str]:
    """Return a list of simple warnings."""
    lines = [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("#")]
    warnings: list[str] = []                           # collected warnings
    from_count = sum(1 for l in lines if l.upper().startswith("FROM "))
    if from_count < 2:                                 # only one stage
        warnings.append("single stage: consider multi-stage")
    if not any(l.upper().startswith("USER ") for l in lines):
        warnings.append("no USER: container runs as root")
    if any(":latest" in l for l in lines if l.upper().startswith("FROM ")):
        warnings.append("avoid :latest tags, pin versions")
    if not any("--no-cache-dir" in l for l in lines):
        warnings.append("use pip --no-cache-dir to keep layers small")
    return warnings

if __name__ == "__main__":
    bad = "FROM python:latest\nCOPY . .\nRUN pip install -r requirements.txt\n"
    print(lint_dockerfile(bad))                        # shows four warnings
```

## 💻 Code Example — Advanced
Production Dockerfile (illustrative; adjust paths and versions to your repo):

```dockerfile
# syntax=docker/dockerfile:1
# ---------- Stage 1: builder ----------
FROM python:3.12-slim AS builder
# Keep Python from writing .pyc files and buffering output
ENV PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
# Build tools only exist in this stage (needed only if a package must compile)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
# Create a virtualenv we can copy as a whole
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /build
# Copy ONLY requirements first so this layer is cached until deps change
COPY requirements.txt .
RUN pip install -r requirements.txt

# ---------- Stage 2: runtime ----------
FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/opt/venv/bin:$PATH"
# Non-root user for safety
RUN useradd --create-home --uid 10001 appuser
WORKDIR /app
# Copy the prepared venv from the builder (no compilers come along)
COPY --from=builder /opt/venv /opt/venv
# Copy application code last (changes most often)
COPY --chown=appuser:appuser app ./app
USER appuser
EXPOSE 8000
# Health check uses python so we need no curl in the image
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"
# Exec form: SIGTERM reaches uvicorn for graceful shutdown
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Companion `.dockerignore` (keeps junk and secrets out of the build context):
```
.git
.env
__pycache__/
*.pyc
.venv/
tests/
data/
*.ipynb
```

Python-side check that the build works (offline-friendly helper):
```python
# Compare image sizes from `docker images --format json` output (illustrative)
import json                                            # parse docker output
import subprocess                                      # run docker CLI

def image_size_mb(tag: str) -> float:
    """Return image size in MB, raising a clear error if docker/tag is missing."""
    try:
        out = subprocess.run(
            ["docker", "image", "inspect", tag, "--format", "{{.Size}}"],
            capture_output=True, text=True, check=True, timeout=20,
        ).stdout.strip()                               # bytes as a string
    except FileNotFoundError as exc:                   # docker not installed
        raise RuntimeError("docker CLI not found") from exc
    except subprocess.CalledProcessError as exc:       # tag missing
        raise RuntimeError(f"cannot inspect {tag}: {exc.stderr.strip()}") from exc
    return int(out) / 1_000_000                        # bytes to MB

# print(image_size_mb("tariff-api:single"), image_size_mb("tariff-api:multi"))
```

---

## 🟠 FastAPI Integration
The image needs a `/health` endpoint (used by `HEALTHCHECK`, Kubernetes probes and load balancers) and a graceful shutdown.

```python
# app/main.py: FastAPI with health and readiness endpoints
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from typing import AsyncIterator

ready = {"ok": False}                                  # flipped after startup work

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup: load config, open DB/vector clients (kept light so the pod starts fast)
    ready["ok"] = True
    yield
    # Shutdown: close clients cleanly when SIGTERM arrives
    ready["ok"] = False

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "alive"}                         # process is up

@app.get("/ready")
async def readiness(response: Response) -> dict[str, str]:
    if not ready["ok"]:
        response.status_code = 503                     # not ready for traffic yet
        return {"status": "starting"}
    return {"status": "ready"}
```
Run several workers with `uvicorn --workers N` or one process per container with the orchestrator scaling replicas (more common in Kubernetes).

---

## 🔗 LangChain / LangGraph Connection
- LangChain pulls in many packages; pin versions in `requirements.txt` (or use `uv`/`pip-tools` lock files) so builds are reproducible.
- Install only the integrations you use (for example `langchain-openai` or `langchain-anthropic`, not every provider) to keep the venv small.
- Do not bake model weights into the image unless you must; large local models belong on a mounted volume or are downloaded at startup. API-based LLM apps need no weights at all.
- LangGraph checkpoints and vector data live outside the container (Postgres, Qdrant), so the image stays stateless.

```python
# Quick check that heavy optional packages are NOT in the runtime image (illustrative)
import importlib.util

def present(pkg: str) -> bool:
    return importlib.util.find_spec(pkg) is not None   # True if installed

for pkg in ("fastapi", "langchain_core", "torch"):
    print(pkg, present(pkg))                           # torch should be False for API-only apps
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Copying all code before installing dependencies
```dockerfile
# Wrong: any code change invalidates the pip install layer
COPY . .
RUN pip install -r requirements.txt
# Right: copy requirements first
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app ./app
```

❌ Mistake 2: Putting secrets in the image
```dockerfile
# Wrong: key stays in a layer forever
ENV OPENAI_API_KEY=sk-...
# Right: inject at runtime (env var from the orchestrator or secret manager)
# docker run -e OPENAI_API_KEY ...   (or use BuildKit secrets for build-time needs)
```

❌ Mistake 3: Running as root and using `latest`
✅ Correct: Create a non-root `USER` and pin base image versions (and ideally digests).

---

## 🧠 Tricky Interview Question

**Q**: "You switched to a multi-stage build and the image shrank, but the app crashes at startup with `ModuleNotFoundError` for a package that exists in the builder stage. What happened?"

**Answer**: The final stage only has what you copied. Typical causes: (1) packages were installed into the system site-packages in the builder, but you copied only `/opt/venv`; (2) the venv's Python path points to an interpreter location that differs in the runtime stage (use the same base image version in both stages); (3) a package needs a system shared library (for example a `libpq` or `libgomp`) installed in the builder but not in the runtime stage, so you must install the runtime library in the final stage; (4) `PATH` not set to the venv in the final stage. Fix by installing into one venv, using the same Python base in both stages, adding only the needed runtime libs, and testing with `docker run --rm image python -c "import yourpkg"` in CI.

---

## ⚫ Interview Questions + Answers

Q1: What is a Docker layer?
A1: Each Dockerfile instruction creates a cached layer. If an instruction and its inputs are unchanged, Docker reuses the cached layer, which makes builds fast.

Q2: Why copy `requirements.txt` before the code?
A2: Dependencies change rarely and code changes often. Putting the slow `pip install` layer before the code layer means it stays cached across code edits.

Q3: Slim vs alpine base images for Python AI apps?
A3: `-slim` (Debian) usually works best because most wheels (numpy etc.) are built for glibc. Alpine uses musl, which often forces slow source builds or breaks packages, so images may not even be smaller.

Q4: What goes in `.dockerignore` and why?
A4: `.git`, `.env`, caches, virtualenvs, data and notebooks. It makes the build context small and prevents secrets from entering the image.

Q5 (Hard): Your AI service needs a local embedding model (about 400 MB). Where should the weights live?
A5: Not in the code layer. Options: bake into a dedicated, separately cached layer (simple, but large image and slower pulls), download at startup into a mounted volume or cache (smaller image, slower first start, needs network), or serve the model from a separate inference service so the API image stays small. For autoscaling, prefer a shared volume or a model registry download with a warm cache, plus a readiness probe that waits until the model is loaded. Pin the model version for reproducibility.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production container for Python services
- Packages need compilers to install (build stage only)
- You care about pull time, autoscaling speed and security

❌ Avoid when:
- A quick local experiment (single stage is fine)
- Everything installs from wheels and the image is already small: gains are smaller (still use non-root and caching)

---

## 📊 Visual Diagram
```
Single stage                         Multi-stage
+--------------------------+         +------------------+   +-------------------+
| python base              |         | builder          |   | runtime           |
| + build-essential        |         | + build tools    |   | python slim       |
| + pip cache              |         | + pip install    |   | + /opt/venv  <----+--- COPY --from=builder
| + packages               |         | -> /opt/venv     |   | + app code        |
| + code                   |         +------------------+   | non-root user     |
+--------------------------+              (discarded)       +-------------------+
   big, more CVEs                                              small, fewer CVEs
```

---

## 💰 Cost Impact
- Docker image size has no token cost, but it changes infrastructure cost: smaller images mean faster autoscaling (fewer idle warm pods needed), lower registry storage and transfer charges, and shorter CI builds.
- Example (illustrative): 10 pods start at month-end; pulling 1.4 GB vs 0.6 GB per node saves about a minute per node, so you can scale on demand rather than over-provision.
- Optimise: cache dependency layers, use BuildKit cache mounts for pip, avoid baking models into images, and scan images so you do not pay for incident response.
- Runtime token costs are unaffected, but a faster-starting service lets you scale to zero or low replicas safely, cutting compute spend.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Multi-stage build | Many FROM steps, keep only the last | कई FROM, सिर्फ आखिरी रखो |
| Layer | Cached step of an image | Image का cached step |
| Builder stage | Stage with build tools | Build tools वाला stage |
| Runtime stage | Final small stage | अंतिम छोटा stage |
| `.dockerignore` | Files excluded from build context | Build से बाहर रखी फ़ाइलें |
| Non-root user | Container user without admin rights | बिना admin अधिकार का user |
| Healthcheck | Probe to test the app is alive | App जीवित है या नहीं की जाँच |

---

## ⚡ 3-Line Summary
English: Multi-stage builds compile and install in one stage, then copy only the venv and code into a small runtime stage. Order layers so dependencies are cached, run as non-root, and never put secrets in the image. The result is faster deploys and fewer vulnerabilities.
Hindi: Multi-stage build एक stage में install करता है, फिर सिर्फ venv और code को छोटे runtime stage में copy करता है। Layers का order ऐसा रखो कि dependencies cached रहें, non-root चलाओ और image में secrets कभी मत रखो। नतीजा: तेज़ deploy और कम vulnerabilities।

---

## ➡️ Next Topic
**544. Docker Compose for AI Stack** — running the API, vector DB, cache and database together locally with one command.
