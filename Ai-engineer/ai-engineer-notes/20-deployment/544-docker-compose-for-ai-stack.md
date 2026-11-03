
---

# 544. Docker Compose for AI Stack
# हिंदी में: AI Stack के लिए Docker Compose

---

## 🔵 Simple Definition (English)
Docker Compose lets you describe several containers (API, vector database, Redis cache, Postgres, worker) in one `compose.yaml` file and start them all with one command. It is the standard way to run a full AI stack on a laptop or a single server, with networking, volumes and environment set up for you.

## 🔵 सरल परिभाषा (Hindi)
Docker Compose में आप एक `compose.yaml` file में कई containers (API, vector database, Redis cache, Postgres, worker) बताते हैं और एक command से सब चालू कर देते हैं। Laptop या single server पर पूरा AI stack चलाने का यह standard तरीका है, जिसमें networking, volumes और environment अपने-आप set हो जाते हैं।

---

## 🔴 Problem it Solves
- An AI app is never one process: API + vector DB + cache + database + worker.
- "Works on my machine": each developer installs services differently.
- Starting five things by hand, in the right order, with the right ports, is error-prone.
- Data in containers disappears on restart unless you use volumes.

## 🔴 यह क्यों बना? (Hindi)
- AI app कभी एक process नहीं होता: API + vector DB + cache + database + worker।
- "मेरी machine पर चलता है": हर developer services अलग तरह से install करता है।
- पाँच चीज़ें हाथ से, सही क्रम और सही ports के साथ चालू करना गलतियों वाला काम है।
- Volumes के बिना container का data restart पर मिट जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write compose.yaml: one "service" per component (api, qdrant, redis, postgres, worker)
Step 2 → Each service: image or build, ports, environment, volumes, depends_on
Step 3 → Compose creates a private network; services reach each other by service name
         (api calls http://qdrant:6333, not localhost)
Step 4 → healthcheck + depends_on condition: service_healthy makes startup order reliable
Step 5 → Named volumes keep database/vector data across restarts
Step 6 → `docker compose up -d --build` starts everything
Step 7 → `docker compose logs -f api`, `docker compose ps`, `docker compose down` to manage
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → compose.yaml लिखो: हर component (api, qdrant, redis, postgres, worker) के लिए एक "service"
Step 2 → हर service में: image या build, ports, environment, volumes, depends_on
Step 3 → Compose private network बनाता है; services एक-दूसरे को service name से पहचानती हैं
         (api, localhost नहीं बल्कि http://qdrant:6333 को call करता है)
Step 4 → healthcheck + depends_on condition: service_healthy से startup order भरोसेमंद होता है
Step 5 → Named volumes restart के बाद भी database/vector data रखते हैं
Step 6 → `docker compose up -d --build` से सब चालू
Step 7 → `docker compose logs -f api`, `docker compose ps`, `docker compose down` से manage करो
```

---

## 🟡 Real World Example
**Tariff Classification System** local stack:
- `api`: FastAPI service (built from the multi-stage Dockerfile)
- `qdrant`: vector DB holding tariff rulings
- `redis`: cache for repeated HS-code questions
- `postgres`: users, audit logs, usage
- `worker`: ingestion worker that embeds new tariff PDFs

A new developer clones the repo, copies `.env.example` to `.env`, adds their API key, runs `docker compose up`, and gets the whole system in minutes.

**Zomato-style AI**: menu-search stack with API, pgvector Postgres and Redis for session caching.

## 🟡 Real Example Hindi mein
**Tariff Classification System** का local stack:
- `api`: FastAPI service (multi-stage Dockerfile से बनी)
- `qdrant`: tariff rulings वाला vector DB
- `redis`: बार-बार पूछे HS-code सवालों का cache
- `postgres`: users, audit logs, usage
- `worker`: नए tariff PDFs embed करने वाला ingestion worker

नया developer repo clone करता है, `.env.example` को `.env` में copy करता है, अपनी API key डालता है, `docker compose up` चलाता है और मिनटों में पूरा system मिल जाता है।

**Zomato-style AI**: API, pgvector वाला Postgres और session caching के लिए Redis का menu-search stack।

---

## 💻 Code Example — Basic
```python
# Basic: validate a compose-style dict for common mistakes (pure Python, no YAML lib needed)
from typing import Any

def check_compose(cfg: dict[str, Any]) -> list[str]:
    """Return warnings for a parsed compose config."""
    warnings: list[str] = []                           # collected issues
    services: dict[str, Any] = cfg.get("services", {}) # all services
    for name, svc in services.items():
        if svc.get("image", "").endswith(":latest"):   # unpinned image
            warnings.append(f"{name}: pin the image tag")
        for env in svc.get("environment", []):         # list-style env
            if "API_KEY=" in env and not env.split("=", 1)[1].startswith("${"):
                warnings.append(f"{name}: hardcoded key, use ${{VAR}} / env_file")
        if name in ("qdrant", "postgres", "redis") and not svc.get("volumes"):
            warnings.append(f"{name}: no volume, data lost on recreate")
    return warnings

if __name__ == "__main__":
    demo = {"services": {
        "qdrant": {"image": "qdrant/qdrant:latest"},
        "api": {"environment": ["OPENAI_API_KEY=sk-123"]},
    }}
    for w in check_compose(demo):                      # show each warning
        print(w)
```

## 💻 Code Example — Advanced
`compose.yaml` (illustrative; pin image versions you have tested):

```yaml
# compose.yaml: Tariff AI stack
services:
  api:
    build:
      context: .
      target: runtime                  # use the multi-stage "runtime" target
    ports:
      - "8000:8000"
    env_file: .env                     # secrets come from .env (git-ignored)
    environment:
      QDRANT_URL: http://qdrant:6333   # service name, not localhost
      REDIS_URL: redis://redis:6379/0
      DATABASE_URL: postgresql://app:${POSTGRES_PASSWORD}@postgres:5432/tariff
    depends_on:
      qdrant:   { condition: service_started }
      redis:    { condition: service_healthy }
      postgres: { condition: service_healthy }
    restart: unless-stopped

  worker:
    build: { context: ., target: runtime }
    command: ["python", "-m", "app.worker"]
    env_file: .env
    environment:
      QDRANT_URL: http://qdrant:6333
    depends_on: [qdrant, redis]

  qdrant:
    image: qdrant/qdrant:v1.9.0        # example tag: pin a version you tested
    volumes:
      - qdrant_data:/qdrant/storage    # persists vectors

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      retries: 5

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}   # from .env
      POSTGRES_DB: tariff
    volumes:
      - pg_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d tariff"]
      interval: 5s
      retries: 10

volumes:
  qdrant_data:
  pg_data:
```

Async Python that waits for dependencies (useful in the worker even with healthchecks):
```python
# Retry-until-ready helper with timeout (stdlib only)
import asyncio                                         # async sleep and gather
from typing import Awaitable, Callable

async def wait_for(name: str, probe: Callable[[], Awaitable[bool]],
                   timeout: float = 30.0, interval: float = 1.0) -> None:
    """Poll `probe` until it returns True or timeout expires."""
    loop = asyncio.get_running_loop()                  # for monotonic time
    deadline = loop.time() + timeout                   # absolute deadline
    while True:
        try:
            if await probe():                          # dependency is ready
                return
        except Exception:                              # connection errors are expected early
            pass
        if loop.time() >= deadline:                    # give up with a clear error
            raise TimeoutError(f"{name} not ready after {timeout}s")
        await asyncio.sleep(interval)                  # wait before retry

async def fake_probe() -> bool:
    return True                                        # replace with a real ping

if __name__ == "__main__":
    asyncio.run(wait_for("qdrant", fake_probe))        # returns immediately in the demo
    print("ready")
```

---

## 🟠 FastAPI Integration
Inside the container, the FastAPI app reads service URLs from environment variables injected by Compose, and uses the `lifespan` hook to create and close shared clients.

```python
# app/main.py: connect to Compose services by env var
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")  # localhost only for non-Docker dev
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Create clients once (real code: AsyncQdrantClient(url=QDRANT_URL), redis.asyncio.from_url(REDIS_URL))
    app.state.qdrant_url = QDRANT_URL
    app.state.redis_url = REDIS_URL
    yield
    # Close clients here

app = FastAPI(lifespan=lifespan)

@app.get("/config")
async def config() -> dict[str, str]:
    return {"qdrant": app.state.qdrant_url}            # never return secrets here
```
For development use `docker compose watch` (or a bind mount plus `uvicorn --reload`) so code edits appear without rebuilds.

---

## 🔗 LangChain / LangGraph Connection
- LangChain vector stores connect by URL, so pass `QDRANT_URL` from Compose: `QdrantClient(url=os.environ["QDRANT_URL"])`.
- LangGraph's Postgres checkpointer can use the `postgres` service so graph state survives API restarts.
- A Redis service can back LangChain caches (`RedisCache`) or semantic cache.

```python
# LangGraph persistence on the compose Postgres (illustrative; check current package docs)
# from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
# async with AsyncPostgresSaver.from_conn_string(os.environ["DATABASE_URL"]) as saver:
#     await saver.setup()                  # create tables once
#     graph = builder.compile(checkpointer=saver)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `localhost` between containers
```python
# Wrong: inside the api container, localhost is the api container itself
QdrantClient(url="http://localhost:6333")
# Right: use the compose service name
QdrantClient(url="http://qdrant:6333")
```

❌ Mistake 2: `depends_on` without health
✅ Correct: `depends_on` alone only waits for the container to start, not to be ready. Use `condition: service_healthy` with a healthcheck, plus retry logic in the app.

❌ Mistake 3: No volumes, committing `.env`
✅ Correct: Named volumes for stateful services; keep `.env` in `.gitignore` and commit a `.env.example` with fake values.

---

## 🧠 Tricky Interview Question

**Q**: "`docker compose down` and `up` again, and all your vectors are gone. Another teammate says it never happens to them. What is different?"

**Answer**: The teammate probably has a named volume (or bind mount) for the vector DB storage path, while yours writes into the container's writable layer, which is deleted when the container is removed. Note also that `docker compose down -v` deletes named volumes, so check for that flag. Fix: mount a volume at the exact data path the database uses (check the image docs: for Qdrant `/qdrant/storage`), and use `down` without `-v` unless you intend a reset. Also keep a snapshot/backup process: volumes are not backups.

---

## ⚫ Interview Questions + Answers

Q1: What is Docker Compose for?
A1: Defining and running multi-container applications with one YAML file and one command. Best for local development, tests and small single-host deployments.

Q2: How do containers talk to each other in Compose?
A2: Compose creates a default network where each service is reachable by its service name through built-in DNS.

Q3: Volume vs bind mount?
A3: A named volume is managed by Docker and is good for persistent data (databases). A bind mount maps a host folder into the container and is good for live-editing source code in development.

Q4: How do you manage secrets in Compose?
A4: Use `env_file` with a git-ignored `.env` for development, or Compose `secrets` (mounted as files) for sensitive values; in production use your platform's secret manager. Never hardcode keys in the YAML.

Q5 (Hard): When should you stop using Compose and move to Kubernetes or a managed service?
A5: When you need multi-node scheduling, autoscaling on load, rolling or canary deployments, self-healing across machines, or strict resource isolation. Compose runs on one host, so that host is a single point of failure. A common path: Compose for dev/CI, managed containers (ECS, Cloud Run) or Kubernetes for production, with the same images.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Local development and integration tests of the full AI stack
- Demos, small internal tools, single-server deployments

❌ Avoid when:
- You need high availability and autoscaling across machines
- You need GPU scheduling across nodes or zero-downtime rollouts at scale

---

## 📊 Visual Diagram
```
                 docker compose up
                         |
        +----------------+------------------------------+
        |   default network (service-name DNS)          |
        |                                               |
 User -> | api :8000 -----> qdrant :6333   [vol: qdrant_data]
        |   |  \                                         |
        |   |   +--------> redis  :6379                  |
        |   +-----------> postgres :5432 [vol: pg_data] |
        |                                               |
        | worker --------> qdrant, redis                |
        +-----------------------------------------------+
        .env  ->  secrets / API keys injected into api, worker
```

---

## 💰 Cost Impact
- Compose itself is free; it saves developer time and avoids using paid cloud resources for dev and test.
- Running a local vector DB and Redis means dev and CI do not call hosted services, but LLM calls still cost tokens. Use a mock or a small, cheap model in dev and tests to avoid spending tokens on every test run.
- Redis caching in the stack reduces repeated LLM calls: for example if 30% of tariff queries repeat, you save about 30% of tokens on those paths (illustrative).
- Set resource limits (`deploy.resources` or `mem_limit`) so a runaway worker does not exhaust a laptop or small VM.
- On a single cloud VM, Compose can be the cheapest production-like setup for small projects, but weigh downtime risk.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Service | One container definition in Compose | Compose में एक container की परिभाषा |
| Volume | Persistent storage for containers | Container का स्थायी storage |
| Bind mount | Host folder mapped into container | Host folder को container में जोड़ना |
| `depends_on` | Start order between services | Services का start क्रम |
| Healthcheck | Test that the service is ready | Service तैयार है या नहीं की जाँच |
| `.env` file | Local environment variables | Local environment variables |
| Service name DNS | Reach services by name | नाम से services तक पहुँचना |

---

## ⚡ 3-Line Summary
English: Compose runs your whole AI stack (API, vector DB, Redis, Postgres, worker) from one YAML file. Use service names for networking, volumes for data, healthchecks for startup order and `.env` for secrets. It is great for dev and small setups, not for multi-node production.
Hindi: Compose एक YAML file से पूरा AI stack (API, vector DB, Redis, Postgres, worker) चलाता है। Networking के लिए service names, data के लिए volumes, startup order के लिए healthchecks और secrets के लिए `.env` use करो। Dev और छोटे setups के लिए बढ़िया है, multi-node production के लिए नहीं।

---

## ➡️ Next Topic
**545. Environment Variables for AI** — how to configure models, keys and limits cleanly across dev, staging and production.
