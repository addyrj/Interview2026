---

# 541. Dockerizing AI Apps
# हिंदी में: AI Apps को Docker में पैक करना

---

## 🔵 Simple Definition (English)
Docker packages your app, its Python version, libraries and system dependencies into an image. A container started from that image behaves the same on your laptop, in CI and in production. For AI apps this solves "works on my machine" problems with heavy libraries like torch, tiktoken or faiss.

## 🔵 सरल परिभाषा (Hindi)
Docker आपके app, उसके Python version, libraries और system dependencies को एक image में पैक करता है। उस image से चला container laptop, CI और production में एक जैसा चलता है। AI apps में torch, tiktoken या faiss जैसी भारी libraries के "मेरी machine पर चलता है" वाले झंझट खत्म होते हैं।

---

## 🔴 Problem it Solves
AI apps depend on exact library versions, native packages and sometimes model files. Without containers, each server is configured by hand, versions drift, and deploys break. Docker gives reproducible builds, easy rollback (previous image tag), and the same artifact from dev to prod.

## 🔴 यह क्यों बना? (Hindi)
AI apps सटीक library versions, native packages और कभी-कभी model files पर निर्भर होते हैं। Containers के बिना हर server हाथ से configure होता है, versions अलग हो जाते हैं और deploy टूटते हैं। Docker reproducible builds, आसान rollback (पुराना image tag) और dev से prod तक एक ही artifact देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a Dockerfile: base image, copy requirements, install, copy code, set CMD
Step 2 → docker build -t tariff-api:1.0 .  (each instruction becomes a cached layer)
Step 3 → Image is stored locally or pushed to a registry (ECR, Docker Hub)
Step 4 → docker run -p 8000:8000 --env-file .env tariff-api:1.0 starts a container
Step 5 → Container runs one process (uvicorn) isolated from the host
Step 6 → Health check (/health) tells the orchestrator if it is alive
Step 7 → New release = build new tag, deploy it, roll back by redeploying the old tag
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Dockerfile लिखो: base image, requirements copy, install, code copy, CMD
Step 2 → docker build -t tariff-api:1.0 . (हर instruction एक cached layer बनता है)
Step 3 → Image local या registry (ECR, Docker Hub) में रखो
Step 4 → docker run -p 8000:8000 --env-file .env tariff-api:1.0 से container शुरू
Step 5 → Container एक process (uvicorn) चलाता है, host से isolated
Step 6 → Health check (/health) बताता है कि app ज़िंदा है या नहीं
Step 7 → नई release = नया tag build करो, deploy करो, rollback = पुराना tag दोबारा deploy
```

---

## 🟡 Real World Example
**Tariff Classification System**: The FastAPI service, the schedule loader and the embedding client are packed into `tariff-api:2.3`. The same image runs in staging for testing and in production, so a classification bug seen in staging reproduces exactly.
**Zomato-style**: During dinner peak, the platform starts 20 more containers of the chat service from the same image within seconds.

## 🟡 Real Example Hindi mein
**Tariff System**: FastAPI service, schedule loader और embedding client सब `tariff-api:2.3` में पैक हैं। वही image staging में test और production में चलती है, इसलिए staging में दिखा classification bug बिल्कुल वैसा ही दोहराया जा सकता है।
**Zomato-style**: Dinner peak में platform उसी image से chat service के 20 और containers कुछ seconds में चालू कर देता है।

---

## 💻 Code Example — Basic
```dockerfile
# Dockerfile: simplest working image for a FastAPI app
FROM python:3.12-slim                 # small official Python base image
WORKDIR /app                          # all next commands run in /app
COPY requirements.txt .               # copy dependency list first (better layer caching)
RUN pip install --no-cache-dir -r requirements.txt   # install libs without keeping pip cache
COPY . .                              # copy the application code
EXPOSE 8000                           # document the port
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]   # start server on all interfaces
```

```python
# main.py: the app the Dockerfile runs (pure FastAPI, no API key needed)
from fastapi import FastAPI                            # web framework

app = FastAPI()                                        # app instance


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}                            # used by health checks
```

## 💻 Code Example — Advanced
```python
# Production style: build and run the image from Python (docker SDK) with health wait and cleanup
# pip install docker  (illustrative; CLI commands are the normal way)
import asyncio                                         # async version of waiting
import time                                            # sync waiting
import urllib.request                                  # simple HTTP check
from typing import Optional                            # optional type


def wait_healthy(url: str, timeout_s: float = 30.0) -> bool:
    """Poll /health until it answers 200 or timeout."""
    deadline = time.monotonic() + timeout_s            # when to give up
    while time.monotonic() < deadline:                 # keep trying
        try:
            with urllib.request.urlopen(url, timeout=2) as r:   # call endpoint
                if r.status == 200:                    # healthy
                    return True
        except OSError:                                # not ready yet (connection refused etc.)
            pass
        time.sleep(1)                                  # wait before retry
    return False                                       # never became healthy


async def wait_healthy_async(url: str, timeout_s: float = 30.0) -> bool:
    """Async version: run the blocking check in a thread so the event loop stays free."""
    return await asyncio.to_thread(wait_healthy, url, timeout_s)   # offload to thread


def run_container(image: str, port: int = 8000) -> Optional[str]:
    """Start a container and return its id, or None on failure."""
    try:
        import docker                                  # imported lazily: optional dependency
        client = docker.from_env()                     # connect to the Docker daemon
        c = client.containers.run(image, detach=True, ports={"8000/tcp": port})   # start in background
        return c.id                                    # container id
    except Exception as exc:                           # daemon down, image missing, port busy...
        print(f"failed to start: {exc}")               # report
        return None
```

---

## 🟠 FastAPI Integration
Containers need `/health` (liveness) and `/ready` (readiness: dependencies loaded). Read config from environment, handle SIGTERM gracefully (uvicorn does), and log to stdout.

```python
import os                                              # env vars
from fastapi import FastAPI, Response                  # FastAPI

app = FastAPI()                                        # app
READY = {"model": False}                               # readiness flags


@app.on_event("startup")                               # older style; lifespan is the modern option
async def load() -> None:
    READY["model"] = True                              # pretend: load schedule/index here


@app.get("/health")
async def health() -> dict:
    return {"status": "alive"}                         # process is up


@app.get("/ready")
async def ready(resp: Response) -> dict:
    if not READY["model"]:                             # not finished loading
        resp.status_code = 503                         # tell orchestrator to wait
    return {"ready": READY["model"], "env": os.getenv("APP_ENV", "dev")}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain apps are normal Python processes, so they containerize the same way. Points to watch: pin `langchain`, `langchain-openai`, `langgraph` versions in requirements (APIs change quickly), pass API keys by env/secrets, and persist LangGraph checkpoints in an external DB (Postgres/Redis), not in the container filesystem, because containers are disposable.

```python
# Config reading inside a containerised LangChain service
import os                                              # env access
from langchain_openai import ChatOpenAI                # model wrapper

llm = ChatOpenAI(model=os.getenv("LLM_MODEL", "gpt-4o-mini"))   # model name from env (illustrative default)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Copying code before installing requirements
✅ Correct: copy `requirements.txt`, install, then copy code, so dependency layer stays cached.

```dockerfile
# Wrong:
# COPY . .
# RUN pip install -r requirements.txt     # every code edit reinstalls everything

# Right:
# COPY requirements.txt .
# RUN pip install -r requirements.txt
# COPY . .
```

❌ Mistake 2: Baking API keys into the image
✅ Correct: pass them at runtime (`--env-file`, secret manager). Images get shared and pushed to registries.

❌ Mistake 3: Binding to 127.0.0.1
✅ Correct: `--host 0.0.0.0`, otherwise the port mapping cannot reach the app.

---

## 🧠 Tricky Interview Question
**Q**: "Your container works locally but the deployed one is killed after startup without errors in the app logs. What do you check?"

**Answer**: Likely OOM kill: loading a big model/index exceeds the memory limit (check `docker inspect` for OOMKilled, or exit code 137). Other causes: failing health check so orchestrator restarts it, slow startup beyond the timeout, wrong CPU architecture (built on ARM Mac, deployed on x86; use `--platform` or buildx). Fix by raising memory, lazy loading, adjusting probe timeouts, and building for the target platform.

---

## ⚫ Interview Questions + Answers

Q1: Image vs container?
A1: An image is a read-only template. A container is a running instance of it.

Q2: Why a `.dockerignore`?
A2: Exclude `.git`, `.env`, venvs, data and caches. Faster builds, smaller images, no secrets copied.

Q3: Why use a slim base image?
A3: Smaller download and attack surface. Alpine can break some wheels (musl), so `-slim` Debian images are the common choice for Python.

Q4: Why run as non-root?
A4: Limits damage if the app is compromised. Add `RUN useradd` and `USER app`.

Q5: (Hard) How do you handle large model files?
A5: Do not bake multi-GB weights into every image layer unless needed. Download at startup into a mounted volume or cache, or use a separate model-serving service. Trade-offs: baked image is self-contained and starts predictable but is slow to pull; runtime download starts slow but keeps images small. For API-based LLMs (OpenAI, Anthropic) there are no weights, so images stay small.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Deploying to cloud, Kubernetes, ECS, or sharing a consistent dev environment

❌ Avoid when:
- A quick one-off script on your own machine
- Serverless platforms where a zip deploy is simpler (although many now accept container images)

---

## 📊 Visual Diagram
```
 Dockerfile ──build──▶ Image (layers) ──push──▶ Registry
                                                  │ pull
                                                  ▼
 requirements layer (cached)           Container (uvicorn :8000)
 code layer                               ▲        │ /health
                                    env / secrets   ▼
                                                 Orchestrator
```

---

## 💰 Cost Impact
Docker itself does not change LLM token cost, but it changes infrastructure cost: image size (pull time, registry storage), idle containers, and right-sizing CPU/memory. API-based AI apps usually need small containers; self-hosted models need GPUs, which dominate cost.
Optimize: slim images, multi-stage builds, autoscale on load, scale to zero for rarely used services, and set memory limits to avoid overpaying. Token usage is unchanged, so keep prompt/caching optimisations in the app.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Image | Read-only app template | App का read-only template |
| Container | Running instance of an image | Image का चलता हुआ रूप |
| Dockerfile | Build instructions | Image बनाने के निर्देश |
| Layer | Cached build step | Build का cached चरण |
| Registry | Image storage service | Images रखने की service |
| Health check | Endpoint proving app is alive | App ज़िंदा होने की जाँच |

---

## ⚡ 3-Line Summary
English: Docker packages the app and its dependencies for identical runs everywhere. Copy requirements first, keep secrets out of images, and add health checks. Containers are disposable, so keep state outside.
Hindi: Docker app और dependencies को पैक करता है ताकि हर जगह एक जैसा चले। पहले requirements copy करो, secrets image में मत रखो और health checks जोड़ो। Containers अस्थायी हैं, इसलिए state बाहर रखो।

---

## ➡️ Next Topic
**542. Docker for FastAPI + LangChain**: a complete, production-style Dockerfile for the tariff API.
