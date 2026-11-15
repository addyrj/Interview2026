---

# 441. Multi-Stage Docker Build
# हिंदी में: Multi-Stage Docker Build

---

## 🔵 Simple Definition (English)
A multi-stage build uses several `FROM` lines in one Dockerfile. Early stages (the "builder") have compilers and tools to build wheels or assets. The final stage starts from a clean slim image and copies only the results with `COPY --from=builder`. Build tools never reach production.

## 🔵 सरल परिभाषा (Hindi)
Multi-stage build में एक Dockerfile में कई `FROM` lines होती हैं। शुरुआती stages ("builder") में compilers और tools होते हैं जो wheels या assets बनाते हैं। आखिरी stage एक साफ slim image से शुरू होता है और `COPY --from=builder` से सिर्फ नतीजे कॉपी करता है। Build tools कभी production तक नहीं पहुँचते।

---

## 🔴 Problem it Solves
Some Python packages (`psycopg2`, `cryptography`, `lxml`, `numpy` on odd platforms) need `gcc` and development headers to install. If you install them in the same image that runs the app, your final image carries 300-600 MB of compilers, pip caches and header files. It is slower to pull, slower to scale, and has a bigger attack surface (more packages to patch, a compiler available to an attacker).

## 🔴 यह क्यों बना? (Hindi)
कुछ Python packages (`psycopg2`, `cryptography`, `lxml`, अजीब platforms पर `numpy`) को install होने के लिए `gcc` और development headers चाहिए। अगर उन्हें उसी image में install करो जो app चलाती है, तो final image में 300-600 MB compilers, pip caches और header files आ जाती हैं। Pull धीमा, scale धीमा, और attack surface बड़ा (patch करने को ज़्यादा packages, हमलावर के हाथ में compiler)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Stage "builder": FROM python:3.13-slim AS builder  (+ apt install gcc libpq-dev)
Step 2 → In builder: pip install --prefix=/install -r requirements.txt  (or build a venv / wheels)
Step 3 → Stage "runtime": a NEW FROM python:3.13-slim  (clean: no gcc, no pip cache)
Step 4 → COPY --from=builder /install /usr/local  -> only installed packages come over
Step 5 → Install only RUNTIME libs (libpq5, not libpq-dev), add non-root user
Step 6 → COPY the app code, set USER, HEALTHCHECK, CMD
Step 7 → Docker discards builder layers from the final image (they stay in build cache only)
Step 8 → docker build --target builder . lets you stop at a stage (e.g., a "test" stage in CI)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Stage "builder": FROM python:3.13-slim AS builder (+ apt install gcc libpq-dev)
Step 2 → builder में: pip install --prefix=/install -r requirements.txt (या venv / wheels)
Step 3 → Stage "runtime": नया FROM python:3.13-slim (साफ: gcc नहीं, pip cache नहीं)
Step 4 → COPY --from=builder /install /usr/local -> सिर्फ installed packages आते हैं
Step 5 → सिर्फ RUNTIME libs (libpq5, libpq-dev नहीं), non-root user जोड़ो
Step 6 → app code COPY करो, USER, HEALTHCHECK, CMD सेट करो
Step 7 → Docker builder layers को final image से हटा देता है (सिर्फ build cache में रहती हैं)
Step 8 → docker build --target builder . से किसी stage पर रुक सकते हो (जैसे CI का "test" stage)
```

---

## 🟡 Real World Example
A data-heavy FastAPI service uses PostgreSQL (`psycopg`) and `cryptography`. Single-stage image: about 900 MB. After moving compilers into a builder stage: about 200 MB, which pulls in seconds on a fresh ECS task or Kubernetes node during autoscaling. Security scanners (Trivy, Docker Scout) also report far fewer CVEs because gcc, make and header packages are gone. (Sizes are typical numbers, not measured here: no Docker daemon was available.)

## 🟡 Real Example Hindi mein
Data-भारी FastAPI service PostgreSQL (`psycopg`) और `cryptography` इस्तेमाल करती है। Single-stage image: लगभग 900 MB। Compilers को builder stage में ले जाने के बाद: लगभग 200 MB, जो autoscaling के समय नए ECS task या Kubernetes node पर सेकंडों में pull होती है। Security scanners (Trivy, Docker Scout) भी बहुत कम CVEs दिखाते हैं क्योंकि gcc, make और header packages हट चुके हैं। (Sizes सामान्य अनुमान हैं, यहाँ नापे नहीं गए: Docker daemon उपलब्ध नहीं था।)

---

## 💻 Code Example — Basic
A real multi-stage Dockerfile (**not run**: no Docker daemon here, so it was not built; comments are on their own lines because Docker does not allow trailing comments):

```dockerfile
# ---------- Stage 1: builder ----------
FROM python:3.13-slim AS builder

# compilers + headers needed ONLY to build wheels
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements.txt .

# install into /install so we can copy just that folder
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------- Stage 2: runtime ----------
FROM python:3.13-slim AS runtime

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

# runtime library only (no -dev package, no compiler)
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home app

# bring over only the installed packages
COPY --from=builder /install /usr/local

WORKDIR /app
COPY --chown=app:app . .
USER app
EXPOSE 8000
CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "-b", "0.0.0.0:8000"]
```

What *was* run: a tiny parser that lists the stages of a Dockerfile (used later by the linter):

```python
# Basic: parse a Dockerfile and list its build stages
import re                                         # regex for FROM lines

DOCKERFILE = """
FROM python:3.13-slim AS builder
RUN pip install --prefix=/install -r requirements.txt
FROM python:3.13-slim AS runtime
COPY --from=builder /install /usr/local
USER app
CMD ["gunicorn", "main:app"]
"""


def stages(text: str) -> list[tuple[str, str]]:
    found = re.findall(r"^FROM\s+(\S+)(?:\s+AS\s+(\S+))?", text, flags=re.M | re.I)   # (image, name)
    return [(img, name or "unnamed") for img, name in found]   # default name if no AS


for img, name in stages(DOCKERFILE):
    print(f"stage {name!r:12} base={img}")        # one line per stage
print("multi-stage:", len(stages(DOCKERFILE)) > 1)

# Output (real run, Python 3.13):
# stage 'builder'    base=python:3.13-slim
# stage 'runtime'    base=python:3.13-slim
# multi-stage: True
```

## 💻 Code Example — Advanced
A Dockerfile linter you can run in CI. It checks for multi-stage builds, pinned tags, a non-root user and cache flags. This is real executed code, applied to a good and a bad sample:

```python
# Advanced: Dockerfile linter - enforce multi-stage, non-root, no pip cache
import re                                         # line matching
from dataclasses import dataclass                 # finding object


@dataclass
class Finding:
    rule: str                                     # short rule id
    msg: str                                      # explanation


def lint(text: str) -> list[Finding]:
    out: list[Finding] = []                       # collected findings
    lines = [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("#")]
    froms = [l for l in lines if l.upper().startswith("FROM ")]
    if len(froms) < 2:                            # one stage means build tools ship to prod
        out.append(Finding("multi-stage", "use a builder stage + slim runtime stage"))
    if any(":latest" in l or ":" not in l.split()[1] for l in froms):
        out.append(Finding("pin-tag", "pin base image tags (no :latest / untagged)"))
    users = [l for l in lines if l.upper().startswith("USER ")]
    if not users or users[-1].split()[1] in ("root", "0"):
        out.append(Finding("non-root", "final stage must run as a non-root USER"))
    for l in lines:
        if l.upper().startswith("RUN ") and "pip install" in l and "--no-cache-dir" not in l:
            out.append(Finding("pip-cache", "add --no-cache-dir to pip install"))
        if re.search(r"apt-get install(?!.*--no-install-recommends)", l):
            out.append(Finding("apt", "use --no-install-recommends and clean /var/lib/apt/lists"))
    return out


GOOD = """
FROM python:3.13-slim AS builder
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
FROM python:3.13-slim
COPY --from=builder /install /usr/local
USER app
"""
BAD = """
FROM python:latest
RUN pip install -r requirements.txt
RUN apt-get install -y gcc
"""
print("GOOD:", [f.rule for f in lint(GOOD)])      # []
print("BAD :", [f.rule for f in lint(BAD)])

# Output (real run, Python 3.13):
# GOOD: []
# BAD : ['multi-stage', 'pin-tag', 'non-root', 'pip-cache', 'apt']
```

Advanced Dockerfile pattern (**not run**): a `test` stage for CI, built with `docker build --target test .`, while production uses `docker build --target runtime .`:

```dockerfile
FROM runtime AS test
USER root
RUN pip install --no-cache-dir pytest httpx
USER app
CMD ["pytest", "-q"]
```
Because `test` is defined after `runtime`, a plain `docker build .` would end on the test stage. Always build production with `--target runtime` (or define `test` earlier from `builder`).

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | Node.js |
|---------|--------|---------|
| Build stage does | compile wheels (`gcc`, headers) | `npm ci`, TypeScript/webpack build |
| What is copied | `/install` (site-packages) | `dist/` + prod `node_modules` |
| Final stage base | `python:3.13-slim` | `node:22-alpine` or distroless |
| Typical saving | 300-600 MB | 500 MB+ (dev dependencies, source) |

```python
# Python way — build in one stage, copy results (Dockerfile as comments)
# FROM python:3.13-slim AS builder
# RUN pip install --prefix=/install -r requirements.txt
# FROM python:3.13-slim
# COPY --from=builder /install /usr/local
```
```javascript
// JavaScript way — build TypeScript in one stage, copy dist (Dockerfile as comments)
// FROM node:22 AS build
// RUN npm ci && npm run build
// FROM node:22-alpine
// COPY --from=build /app/dist ./dist
```

Key difference: in Node the build stage often produces compiled output (`dist/`) while Python's builder produces installed packages. Python has no compile step for your own code, so the multi-stage win comes from dependencies that need compilation.

---

## 🟠 FastAPI Connection
FastAPI itself is pure Python, so the benefits come from its dependencies (`psycopg`, `asyncpg`, `cryptography`, `pydantic-core` ship wheels, but some packages still compile). Final-stage best practices for FastAPI: gunicorn with `UvicornWorker` or plain `uvicorn`, non-root user, `HEALTHCHECK` against `/health`, `PYTHONUNBUFFERED=1` for logs. Alternative: build a virtualenv in the builder and copy `/opt/venv`.

```python
# FastAPI example — virtualenv-in-builder variant, activated through PATH (Dockerfile as comments)
# builder:  RUN python -m venv /opt/venv && /opt/venv/bin/pip install -r requirements.txt
# runtime:  COPY --from=builder /opt/venv /opt/venv
#           ENV PATH="/opt/venv/bin:$PATH"
#           CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Copying the whole builder filesystem or installing build tools in the final stage
✅ Correct: copy only `/install` (or the venv) and the app code

```dockerfile
# Wrong
COPY --from=builder / /
# Right
COPY --from=builder /install /usr/local
```

❌ Mistake 2: Installing `libpq-dev` in the runtime stage, or forgetting the runtime library (`libpq5`)
✅ Correct: dev packages in builder, shared runtime library in final (otherwise `ImportError: libpq.so.5`)

```dockerfile
# Wrong (runtime stage): nothing installed -> ImportError: libpq.so.5: cannot open shared object file
# Right
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*
```

❌ Mistake 3: Putting `COPY . .` before dependency install in the builder
✅ Correct: copy `requirements.txt` first so the expensive layer stays cached

```dockerfile
# Wrong
COPY . .
RUN pip install -r requirements.txt
# Right
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
```

---

## 🧠 Tricky Interview Question

```dockerfile
FROM python:3.13-slim AS builder
RUN pip install --no-cache-dir --prefix=/install fastapi
FROM python:3.13-slim
CMD ["python", "-c", "import fastapi"]
```
Question: the image builds, but `docker run` prints `ModuleNotFoundError: No module named 'fastapi'`. Why?

Answer: The final stage is a brand-new image. Nothing from `builder` is present unless you copy it: there is no `COPY --from=builder /install /usr/local`. The packages were installed in a stage whose layers are not part of the final image. Add the COPY line. Also remember that `--prefix=/install` creates `/install/lib/python3.13/site-packages/...` and `/install/bin/...`, so copying to `/usr/local` merges them into the standard locations on Python's path, and the Python minor version must be the same in both stages.

---

## ⚫ Interview Questions + Answers

Q1: What does `COPY --from=builder` do?
A1: It copies files from an earlier stage (or even an external image like `--from=nginx:latest`) into the current stage. Only those files end up in the final image.

Q2: How much smaller will the image be?
A2: It depends on dependencies. When compilers and build caches are removed, 40-70% is common (for example 900 MB to 250 MB). A pure-Python app with only wheels gains little; use `-slim` and `--no-cache-dir` anyway.

Q3: How do stages and BuildKit caching interact?
A3: BuildKit builds independent stages in parallel and skips unused ones. You can add cache mounts: `RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt` to keep pip's download cache between builds without storing it in a layer.

Q4: Slim vs alpine vs distroless for Python?
A4: Slim (Debian) is the safe default because manylinux wheels work. Alpine (musl) often forces source builds and can be slower. Distroless (`gcr.io/distroless/python3`) is smallest and has no shell, which is secure but harder to debug.

Q5: How do you run tests in a stage?
A5: Add a `test` stage that includes dev dependencies and runs pytest, build it in CI with `--target test`, and build the default (runtime) stage for deployment so test tools never ship.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Dependencies need compilers or `-dev` packages
- You want a small, secure production image
- You need a separate test or docs build stage

❌ Avoid when:
- Everything installs from wheels and the image is already small (extra complexity is not needed)
- Quick local prototype
- You cannot keep Python versions identical in both stages

---

## 📊 Visual Diagram
```
 STAGE 1: builder (python:3.13-slim + gcc + libpq-dev)   ~700 MB, thrown away
   pip install --prefix=/install  ->  /install  (site-packages)
                                          |
                                COPY --from=builder
                                          v
 STAGE 2: runtime (python:3.13-slim + libpq5)             ~200 MB, shipped
   /usr/local  <- packages          /app <- your code      USER app
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Stage | One `FROM` block of a build | build का एक `FROM` हिस्सा |
| Builder | Stage that compiles/installs | compile/install करने वाला stage |
| `COPY --from` | Copy files from another stage | दूसरे stage से files कॉपी |
| `--target` | Stop the build at a named stage | नाम वाले stage पर build रोकना |
| Wheel | Pre-built Python package | पहले से बना Python package |
| Distroless | Image without OS shell/tools | बिना OS shell/tools की image |

---

## ⚡ 3-Line Summary
English: Build in one stage with compilers, ship from a second clean stage. Copy only installed packages and app code with `COPY --from`. The result is a smaller, faster and more secure image.
Hindi: एक stage में compilers के साथ build करो, दूसरे साफ stage से ship करो। `COPY --from` से सिर्फ installed packages और app code लाओ। नतीजा: छोटी, तेज़ और ज़्यादा सुरक्षित image।

---

## ➡️ Next Topic
**442. Docker Compose + FastAPI + DB** — run the API, PostgreSQL and more as one stack with a single command.
