---

# 339. LangGraph Deployment
# हिंदी में: LangGraph Deployment (Production में चलाना)

---

## 🔵 Simple Definition (English)
Deployment means running your graph as a reliable service for real users. There are two routes: (1) your own FastAPI app packaged in Docker (full control), or (2) the LangGraph server, configured by a `langgraph.json` file, which gives you ready-made endpoints for runs, threads, streaming and persistence (run locally with `langgraph dev`, self-host with Docker, or use LangGraph Cloud/Platform).

## 🔵 सरल परिभाषा (Hindi)
Deployment का मतलब है आपके graph को real users के लिए भरोसेमंद service के रूप में चलाना। दो रास्ते हैं: (1) आपका अपना FastAPI app Docker में package (पूरा control), या (2) LangGraph server, जो `langgraph.json` file से configure होता है और runs, threads, streaming व persistence के ready-made endpoints देता है (`langgraph dev` से local, Docker से self-host, या LangGraph Cloud/Platform)।

---

## 🔴 Problem it Solves
"Works on my laptop" fails in production: memory is in RAM and lost on restart, secrets are hard-coded, long runs time out, two instances give different answers, and nobody knows why a run failed. Deployment practices give you persistence (Postgres), configuration (env vars), health checks, scaling (stateless pods), observability (tracing) and repeatable builds (Docker image).

## 🔴 यह क्यों बना? (Hindi)
"मेरे laptop पर चलता है" production में फेल होता है: memory RAM में है और restart पर चली जाती है, secrets hard-coded हैं, लंबे runs time out होते हैं, दो instances अलग जवाब देते हैं, और कोई नहीं जानता run क्यों फेल हुआ। Deployment practices persistence (Postgres), configuration (env vars), health checks, scaling (stateless pods), observability (tracing) और repeatable builds (Docker image) देती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Put the graph in an importable module that exposes a compiled `graph` variable
Step 2 → Pin dependencies (pyproject.toml / requirements.txt)
Step 3 → Create langgraph.json: {"dependencies": ["."], "graphs": {"tariff": "./app/graph.py:graph"}, "env": ".env"}
Step 4 → Test locally: `langgraph dev` (in-memory server + Studio) or `uvicorn app.main:app`
Step 5 → Build an image (Dockerfile or `langgraph build -t tariff-agent`)
Step 6 → Provide Postgres (checkpoints) and Redis (queues/streaming, for the LangGraph server) via env vars
Step 7 → Deploy N stateless replicas behind a load balancer; add health + readiness checks
Step 8 → Turn on tracing, alerts on error rate / latency / cost; roll out with canary
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Graph को ऐसे module में रखो जो compiled `graph` variable expose करे
Step 2 → Dependencies pin करो (pyproject.toml / requirements.txt)
Step 3 → langgraph.json बनाओ: {"dependencies": ["."], "graphs": {"tariff": "./app/graph.py:graph"}, "env": ".env"}
Step 4 → Local test: `langgraph dev` (in-memory server + Studio) या `uvicorn app.main:app`
Step 5 → Image build करो (Dockerfile या `langgraph build -t tariff-agent`)
Step 6 → Env vars से Postgres (checkpoints) और Redis (queues/streaming, LangGraph server के लिए) दो
Step 7 → Load balancer के पीछे N stateless replicas चलाओ; health + readiness checks जोड़ो
Step 8 → Tracing, error rate / latency / cost के alerts चालू करो; canary से rollout करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: the graph lives in `app/graph.py`. Dev: `langgraph dev` for quick testing in Studio. Staging/Prod: Docker image with FastAPI, `AsyncPostgresSaver` pointing to a managed Postgres, secrets from the cloud secret manager, 3 replicas. A nightly job deletes checkpoints older than 30 days. **Amazon AI**: blue/green deploy so a new prompt version can be rolled back in a minute.

## 🟡 Real Example Hindi mein
**Tariff System**: Graph `app/graph.py` में है। Dev: Studio में तेज़ testing के लिए `langgraph dev`। Staging/Prod: FastAPI वाला Docker image, managed Postgres पर `AsyncPostgresSaver`, cloud secret manager से secrets, 3 replicas। रात का job 30 दिन से पुराने checkpoints delete करता है। **Amazon AI**: blue/green deploy ताकि नया prompt version एक मिनट में rollback हो सके।

---

## 💻 Code Example — Basic
```python
# app/graph.py - the module that both `langgraph.json` and FastAPI import
# Runs offline: python graph.py  (pip install langgraph)
import json  # to print the generated config
import os  # read environment variables
from typing import TypedDict  # state typing

from langgraph.graph import END, START, StateGraph  # graph API


class State(TypedDict):  # state
    product: str
    hs_code: str


def classify(state: State) -> dict[str, str]:  # node
    return {"hs_code": "8517.13"}  # placeholder for an LLM call


def build() -> "CompiledStateGraph":  # type is a compiled graph
    b = StateGraph(State)  # builder
    b.add_node("classify", classify)  # node
    b.add_edge(START, "classify")  # entry
    b.add_edge("classify", END)  # exit
    return b.compile()  # NO checkpointer: the LangGraph server injects its own persistence


graph = build()  # this module-level variable is what "graphs" in langgraph.json points to

if __name__ == "__main__":
    # The config file the LangGraph server reads (written here only to show its shape):
    config = {
        "dependencies": ["."],  # install this package
        "graphs": {"tariff": "./graph.py:graph"},  # name -> file:variable
        "env": ".env",  # file with OPENAI_API_KEY etc.
        "python_version": "3.12",  # runtime
    }
    print(json.dumps(config, indent=2))  # show the file content
    print(graph.invoke({"product": "phone", "hs_code": ""}))  # smoke test
    print("LANGSMITH_TRACING =", os.environ.get("LANGSMITH_TRACING", "unset"))  # config comes from env
```

## 💻 Code Example — Advanced
```python
# Self-hosted production app: settings from env, health/readiness, DB checkpointer in lifespan
import logging  # logs
import os  # env vars
from contextlib import asynccontextmanager  # lifespan
from typing import AsyncIterator, TypedDict  # typing

from fastapi import FastAPI, HTTPException  # web
from langgraph.checkpoint.memory import MemorySaver  # fallback for local dev
from langgraph.graph import END, START, StateGraph  # graph API

log = logging.getLogger("tariff.deploy")  # logger


class State(TypedDict):
    product: str
    hs_code: str


async def classify(state: State) -> dict[str, str]:  # async node
    return {"hs_code": "8517.13"}


def build(checkpointer) -> object:  # factory used by prod and tests
    b = StateGraph(State)
    b.add_node("classify", classify)
    b.add_edge(START, "classify")
    b.add_edge("classify", END)
    return b.compile(checkpointer=checkpointer)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    db_url = os.environ.get("DATABASE_URL")  # set in production, absent locally
    if db_url:  # production: durable checkpoints shared by all replicas
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver  # pip install langgraph-checkpoint-postgres psycopg[pool]

        async with AsyncPostgresSaver.from_conn_string(db_url) as saver:  # manages the connection
            await saver.setup()  # creates tables once (idempotent)
            app.state.graph = build(saver)  # compile with Postgres
            app.state.ready = True  # now accept traffic
            yield  # serve requests
            app.state.ready = False  # draining on shutdown
    else:  # local dev
        log.warning("DATABASE_URL not set -> using in-memory checkpoints (NOT for production)")
        app.state.graph = build(MemorySaver())
        app.state.ready = True
        yield


app = FastAPI(lifespan=lifespan)


@app.get("/healthz")  # liveness: process is up
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")  # readiness: safe to receive traffic
async def readyz() -> dict[str, str]:
    if not getattr(app.state, "ready", False):  # DB not connected yet
        raise HTTPException(status_code=503, detail="not ready")
    return {"status": "ready"}
```

```dockerfile
# Dockerfile (self-hosted FastAPI route)
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir .
COPY app ./app
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

---

## 🟠 FastAPI Integration
Two deployment styles: (a) your own FastAPI (above), (b) the LangGraph server, which already exposes `/threads`, `/runs`, `/runs/stream` and so on. A hybrid is common: your FastAPI handles auth, quotas and business rules and calls the LangGraph server through `langgraph_sdk`.

```python
from fastapi import FastAPI  # web
from langgraph_sdk import get_client  # pip install langgraph-sdk

app = FastAPI()  # your gateway
lg = get_client(url="http://langgraph-server:8123")  # LangGraph server address from env in real code


@app.post("/classify/{thread_id}")
async def classify(thread_id: str, product: str) -> dict[str, object]:  # gateway route
    result = await lg.runs.wait(  # create a run and wait for it to finish
        thread_id,  # existing thread
        "tariff",  # graph name from langgraph.json
        input={"product": product, "hs_code": ""},  # graph input
    )
    return {"result": result}  # final state
```

---

## 🔗 LangChain / LangGraph Connection
`langgraph.json` + the `langgraph` CLI (`pip install -U "langgraph-cli[inmem]"`) is the official packaging path: `langgraph dev` (local, hot reload, Studio), `langgraph build` (Docker image), `langgraph up` (local Docker with Postgres and Redis). The server replaces your checkpointer with its own Postgres persistence, so do not pass one in `compile()` when deploying this way. LangSmith traces are enabled with environment variables, so each deployment is observable with no code changes.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Shipping `MemorySaver` or secrets in the image
✅ Correct: DB-backed saver, secrets from environment/secret manager.

```python
# Wrong - memory lost on restart; key leaked in git history
llm = ChatOpenAI(api_key="sk-live-123")
graph = builder.compile(checkpointer=MemorySaver())

# Right
llm = ChatOpenAI()   # reads OPENAI_API_KEY from the environment
graph = builder.compile(checkpointer=postgres_saver)
```

❌ Mistake 2: Passing your own checkpointer when using the LangGraph server
✅ Correct: Export the graph without a checkpointer; the platform adds persistence.

```python
# Wrong (for langgraph.json deployments) - conflicts with platform persistence
graph = builder.compile(checkpointer=MemorySaver())

# Right
graph = builder.compile()
```

---

## 🧠 Tricky Interview Question

**Q**: "A run takes 4 minutes (many tool calls). Behind your load balancer, requests fail after 60 seconds although the graph finishes fine. What do you do?"

**Answer**: The HTTP timeout, not LangGraph, kills the request. Do not just raise timeouts everywhere. Use an asynchronous job pattern: `POST /runs` returns a `run_id` immediately, a worker executes the graph (background task, queue, or LangGraph server background runs), and the client polls `GET /runs/{id}` or reconnects to a stream. Checkpointing lets a crashed worker resume. Add idempotency keys so a retried POST does not start a duplicate (paid) run.

---

## ⚫ Interview Questions + Answers

Q1: What is `langgraph.json`? (Easy)
A1: The config file for the LangGraph CLI/server: it lists dependencies, graph entry points (`name: path:variable`), env file and runtime version.

Q2: Why not use `MemorySaver` in production? (Easy)
A2: It lives in process RAM: lost on restart and not shared across replicas. Use Postgres/Redis savers.

Q3: What does `langgraph dev` do? (Medium)
A3: Starts a local development server with hot reload and in-memory persistence, and connects to LangGraph Studio for visual debugging. It is not for production.

Q4: How do you handle secrets and config? (Medium)
A4: Environment variables injected by the platform/secret manager, never baked into images; a `.env` file only for local dev and excluded from git and from the image.

Q5: Design zero-downtime deploys for a graph whose state schema changes. (Hard)
A5: Existing checkpoints were written with the old schema. Make changes backward compatible: add optional fields with defaults, do not rename or retype keys in place, and write a migration node/script for breaking changes. Deploy with canary or blue/green, keep old and new versions running while old threads drain, and test by loading real old checkpoints in CI. Version the state (a `schema_version` field) so nodes can adapt.

---

## 🔷 When to Use + When Not to Use
✅ Use the LangGraph server/Platform when:
- You want threads, runs, streaming, cron and human-in-the-loop endpoints without writing them
- You want Studio integration and less ops work

✅ Use your own FastAPI when:
- You need full control of auth, routing and existing infrastructure

❌ Avoid when:
- Deploying `langgraph dev` as production
- Sharing one in-memory graph across replicas

---

## 📊 Visual Diagram
```
 Client ─► Load balancer ─► [Pod 1] [Pod 2] [Pod 3]   (stateless replicas)
                               │        │       │
                               └────────┴───────┘
                                    │
                   ┌────────────────┼─────────────────┐
                   ▼                ▼                 ▼
              Postgres          Redis (queues,     LangSmith
          (checkpoints, store)   streaming)        (traces)
                   ▲
   langgraph.json ─┴─► image built by `langgraph build` or Dockerfile
```

---

## 💰 Cost Impact
- Infrastructure: a small app (2 replicas, managed Postgres) is typically tens of dollars per month, usually small compared with LLM spend at scale.
- Token impact: persistence adds no tokens, but retries after timeouts can double-charge. Use idempotency keys and resume from checkpoints instead of restarting.
- Optimise: autoscale replicas by load, prune old checkpoints, cache frequent answers, set per-user budgets, and monitor cost per route with traces.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| langgraph.json | Deployment config file | Deployment config file |
| langgraph dev | Local dev server | Local development server |
| Replica | One running copy of the app | App की एक चलती copy |
| Readiness probe | Check that app can take traffic | Traffic लेने के लिए तैयार है या नहीं |
| Blue/green | Two versions, switch traffic | दो versions, traffic बदलना |
| Idempotency | Same request, same effect once | एक ही request का असर एक बार |

---

## ⚡ 3-Line Summary
English: Deploy a graph either as your own FastAPI app in Docker or through the LangGraph server configured by `langgraph.json`. Production needs a database checkpointer, env-based secrets, health checks and stateless replicas. Use async jobs for long runs and make schema changes backward compatible.
Hindi: Graph को या तो Docker में अपने FastAPI app के रूप में deploy करो, या `langgraph.json` से configure LangGraph server से। Production में database checkpointer, env-based secrets, health checks और stateless replicas चाहिए। लंबे runs के लिए async jobs और schema बदलाव backward compatible रखो।

---

## ➡️ Next Topic
**340. LangGraph Best Practices** — design, testing, safety and cost rules that keep graphs maintainable.
