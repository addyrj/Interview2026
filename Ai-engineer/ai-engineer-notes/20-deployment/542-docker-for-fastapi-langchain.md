---

# 542. Docker for FastAPI + LangChain
# हिंदी में: FastAPI + LangChain के लिए Docker

---

## 🔵 Simple Definition (English)
This topic shows how to containerize a FastAPI service that uses LangChain: pinned dependencies, non-root user, proper startup command, health check, environment-based config, and graceful shutdown. It is the practical recipe for the tariff API.

## 🔵 सरल परिभाषा (Hindi)
यह topic बताता है कि LangChain इस्तेमाल करने वाली FastAPI service को कैसे container करें: pinned dependencies, non-root user, सही startup command, health check, environment से config और graceful shutdown। यह tariff API की practical recipe है।

---

## 🔴 Problem it Solves
LangChain pulls many packages and changes fast; unpinned installs make builds differ day to day. LLM calls are slow, so shutdowns can cut requests midway. And a container started as root with secrets in the image is a security problem.

## 🔴 यह क्यों बना? (Hindi)
LangChain कई packages लाता है और तेज़ी से बदलता है; unpinned install से रोज़ अलग build बनते हैं। LLM calls धीमे हैं, इसलिए shutdown से requests बीच में कट सकती हैं। और root से चलता container जिसकी image में secrets हों, security की समस्या है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → requirements.txt pins versions (pip freeze or a lock tool like uv / pip-tools)
Step 2 → Dockerfile: slim base, env flags, install deps, copy code
Step 3 → Create non-root user and switch to it
Step 4 → HEALTHCHECK calls /health
Step 5 → CMD runs uvicorn (one process per container; scale with more containers)
Step 6 → Config and API keys come from environment at runtime
Step 7 → On stop, Docker sends SIGTERM; uvicorn finishes in-flight requests, then exits
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → requirements.txt में versions pin (pip freeze या uv / pip-tools)
Step 2 → Dockerfile: slim base, env flags, deps install, code copy
Step 3 → Non-root user बनाओ और उसी पर switch करो
Step 4 → HEALTHCHECK /health को call करता है
Step 5 → CMD uvicorn चलाता है (एक container में एक process; scale = ज़्यादा containers)
Step 6 → Config और API keys runtime पर environment से आते हैं
Step 7 → Stop पर Docker SIGTERM भेजता है; uvicorn चल रही requests पूरी करके बंद होता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: The `/classify` endpoint calls LangChain, which calls the LLM (5-15 s). During a deploy, old containers get SIGTERM; with a proper stop timeout they finish current classifications before exit, so officers do not see random 502 errors.
**Amazon-style**: Rolling deploys of a product Q&A service with zero dropped requests.

## 🟡 Real Example Hindi mein
**Tariff System**: `/classify` endpoint LangChain से LLM को call करता है (5-15 s)। Deploy के समय पुराने containers को SIGTERM मिलता है; सही stop timeout हो तो वे चल रही classifications पूरी करके बंद होते हैं, और officers को अचानक 502 errors नहीं दिखते।
**Amazon-style**: Product Q&A service के rolling deploy में एक भी request नहीं छूटती।

---

## 💻 Code Example — Basic
```dockerfile
# Dockerfile (basic but safe)
FROM python:3.12-slim                                  # small base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1       # no .pyc files, logs appear immediately
WORKDIR /app                                           # working directory
COPY requirements.txt .                                # deps first for caching
RUN pip install --no-cache-dir -r requirements.txt     # install pinned deps
COPY app/ ./app/                                       # copy only the app package
EXPOSE 8000                                            # port documentation
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]   # run server
```

```text
# requirements.txt (versions are illustrative: pin what you tested)
fastapi==0.115.0
uvicorn[standard]==0.30.6
langchain-openai==0.2.0
langchain-core==0.3.0
pydantic-settings==2.5.2
```

## 💻 Code Example — Advanced
```dockerfile
# Dockerfile (production style)
FROM python:3.12-slim AS base                          # base image
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1   # python + pip flags
WORKDIR /app                                           # workdir
RUN useradd --create-home --uid 1000 appuser           # non-root user
COPY requirements.txt .                                # deps list
RUN pip install -r requirements.txt                    # install deps
COPY --chown=appuser:appuser app/ ./app/               # copy code owned by non-root user
USER appuser                                           # drop privileges
EXPOSE 8000                                            # port
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status==200 else 1)"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-graceful-shutdown", "30"]
```

```python
# app/main.py: settings from env, lifespan startup/shutdown, async LLM endpoint with error handling
import asyncio                                         # timeouts
from contextlib import asynccontextmanager             # lifespan helper
from typing import AsyncIterator                       # type hint

from fastapi import FastAPI, HTTPException             # FastAPI
from pydantic import BaseModel, Field                  # request model
from pydantic_settings import BaseSettings             # env-based config


class Settings(BaseSettings):
    openai_api_key: str = ""                           # read from OPENAI_API_KEY
    llm_model: str = "gpt-4o-mini"                     # illustrative default
    llm_timeout_s: float = 30.0                        # per-request timeout


settings = Settings()                                  # load once
state: dict[str, object] = {}                          # shared objects


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create clients at startup and close at shutdown."""
    if settings.openai_api_key:                        # only if a key exists
        from langchain_openai import ChatOpenAI        # lazy import
        state["llm"] = ChatOpenAI(model=settings.llm_model)   # reuse one client
    yield                                              # app runs here
    state.clear()                                      # cleanup on shutdown


app = FastAPI(lifespan=lifespan)                       # attach lifespan


class Req(BaseModel):
    text: str = Field(min_length=3, max_length=4000)   # validate input size


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}                            # liveness


@app.post("/classify")
async def classify(req: Req) -> dict[str, str]:
    llm = state.get("llm")                             # may be missing offline
    if llm is None:                                    # no key configured
        return {"code": "8518.30", "note": "mock (no API key)"}   # offline fallback
    try:
        msg = await asyncio.wait_for(llm.ainvoke(f"HS code for: {req.text}"), settings.llm_timeout_s)   # async call
    except asyncio.TimeoutError:
        raise HTTPException(504, "LLM timeout")        # gateway timeout
    except Exception as exc:                           # provider error
        raise HTTPException(502, f"LLM error: {exc}")  # bad gateway
    return {"code": str(msg.content)}                  # model text
```

---

## 🟠 FastAPI Integration
Run `uvicorn` as the container's main process. For more CPU use, run more containers (or `--workers N` if memory allows; each worker loads its own copy of models and clients). Behind an ALB/nginx, add `--proxy-headers`.

```python
# Quick check of settings precedence: env var overrides default
import os                                              # env access
from pydantic_settings import BaseSettings             # settings class


class S(BaseSettings):
    llm_model: str = "gpt-4o-mini"                     # default value


os.environ["LLM_MODEL"] = "other-model"                # simulate docker run -e LLM_MODEL=other-model
print(S().llm_model)                                   # prints: other-model
```

---

## 🔗 LangChain / LangGraph Connection
Build the LangChain client once (in lifespan), not per request. For LangGraph with memory, use a Postgres/Redis checkpointer so state survives container restarts. Pin versions together: `langchain-core`, `langchain-openai`, `langgraph` should be tested as a set.

```python
# Reuse one compiled graph per process (illustrative)
# state["graph"] = build_graph().compile(checkpointer=PostgresSaver(...))   # external state store
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Unpinned dependencies
✅ Correct: pin versions and rebuild deliberately.

```text
# Wrong: langchain
# Right: langchain-core==0.3.0   (the version you tested)
```

❌ Mistake 2: Creating the LLM client inside each request
✅ Correct: create once in `lifespan`, reuse (connection pooling).

❌ Mistake 3: Using `--reload` in production
✅ Correct: reload is for development only; it watches files and wastes resources.

---

## 🧠 Tricky Interview Question
**Q**: "You set `--workers 4` and the container memory doubles, then gets killed. Why?"

**Answer**: Each uvicorn worker is a separate process and loads its own copy of the app: vector index, tokenizers, caches. Memory scales with the number of workers, and copy-on-write sharing helps only partly in Python. Reduce workers, lazy load, keep big indexes in an external vector DB, or scale with more small containers instead.

---

## ⚫ Interview Questions + Answers

Q1: Why `PYTHONUNBUFFERED=1`?
A1: It sends Python output straight to stdout so container logs appear immediately.

Q2: Why a health check?
A2: The orchestrator uses it to restart unhealthy containers and to know when to send traffic.

Q3: One process or many per container?
A3: Prefer one uvicorn process per container and scale containers. Use multiple workers only when memory allows and you need simple vertical scaling.

Q4: How do you give the container the API key?
A4: At runtime: `docker run --env-file`, Compose secrets, or the cloud secret manager. Never `ENV OPENAI_API_KEY=...` in the Dockerfile.

Q5: (Hard) How do you achieve zero-downtime deploys with slow LLM requests?
A5: Rolling or blue/green deploy with readiness probes, `--timeout-graceful-shutdown` and orchestrator stop timeout longer than the max request time, load balancer connection draining, and streaming or async job patterns for very long tasks so requests do not depend on one container lifetime.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production FastAPI + LangChain service

❌ Avoid when:
- Local quick tests (a venv is fine)

---

## 📊 Visual Diagram
```
 requirements.txt ─▶ [pip install layer] ─▶ [code layer] ─▶ USER appuser
                                                              │
 docker run --env-file .env -p 8000:8000                      ▼
                                           uvicorn app.main:app
                                           ├─ /health  (HEALTHCHECK)
                                           └─ /classify ─▶ LangChain ─▶ LLM API
 SIGTERM ─▶ graceful shutdown (finish in-flight requests)
```

---

## 💰 Cost Impact
Token cost is set by your prompts, but deployment choices add or save money: one shared LLM client avoids connection overhead; timeouts and `max_tokens` prevent runaway calls; right-sized containers (often 0.5-1 vCPU, 512MB-1GB for API-based apps; illustrative) cut compute. Retries inside containers can multiply token spend: cap them.
Optimize: small images, autoscaling, request timeouts, response caching, and monitoring tokens per request from the `usage` field.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Lifespan | Startup/shutdown hook in FastAPI | FastAPI का start/stop hook |
| SIGTERM | Polite stop signal | बंद करने का विनम्र signal |
| Graceful shutdown | Finish work then exit | काम पूरा करके बंद होना |
| Pinning | Fixing exact versions | सटीक versions तय करना |
| Non-root | Running without admin rights | बिना admin अधिकार के चलना |
| Worker | Extra server process | अतिरिक्त server process |

---

## ⚡ 3-Line Summary
English: Pin dependencies, run as non-root, and read config from the environment. Create LangChain clients once in lifespan and use health checks plus graceful shutdown. Scale with more containers, not unlimited workers.
Hindi: Dependencies pin करो, non-root चलाओ और config environment से पढ़ो। LangChain clients lifespan में एक बार बनाओ और health checks व graceful shutdown रखो। ज़्यादा containers से scale करो, बेहिसाब workers से नहीं।

---

## ➡️ Next Topic
**543. Multi-Stage Build for AI**: make the image smaller and safer by separating build and runtime stages.
