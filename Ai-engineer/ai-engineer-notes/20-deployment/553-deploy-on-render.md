
---

# 553. Deploy on Render
# हिंदी में: Render पर Deploy

---

## 🔵 Simple Definition (English)
Render is a cloud platform (PaaS) that deploys web services, background workers, cron jobs and databases from a Git repo or Docker image. You describe infrastructure in a `render.yaml` **Blueprint** and Render handles TLS, builds, health checks and zero-downtime deploys. Free-tier services sleep when idle, so they are for testing only.

## 🔵 सरल परिभाषा (Hindi)
Render एक cloud platform (PaaS) है जो Git repo या Docker image से web services, background workers, cron jobs और databases deploy करता है। आप `render.yaml` **Blueprint** में infrastructure लिखते हैं और Render TLS, builds, health checks और zero-downtime deploys सँभालता है। Free tier की services idle होने पर सो जाती हैं, इसलिए सिर्फ testing के लिए हैं।

---

## 🔴 Problem it Solves
Teams need reproducible deploys of an API plus worker plus database without writing Terraform. Render gives infrastructure-as-code in one YAML file, preview environments for pull requests, and private networking between services.

## 🔴 यह क्यों बना? (Hindi)
Teams को API + worker + database के reproducible deploys चाहिए, Terraform लिखे बिना। Render एक YAML में infrastructure-as-code, pull requests के लिए preview environments और services के बीच private networking देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Put render.yaml in the repo root describing services
Step 2 → In Render dashboard: New → Blueprint → select the repo
Step 3 → Render builds (buildCommand) and starts (startCommand) each service
Step 4 → Secrets: mark env vars sync:false so they are entered in the dashboard
Step 5 → healthCheckPath is polled; the new instance receives traffic only when healthy
Step 6 → Old instance is stopped after the new one is live (zero-downtime)
Step 7 → autoDeploy: every push to the branch redeploys
Step 8 → Workers read from a queue (Redis/Key Value); services talk over private network
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Repo root में render.yaml रखो जिसमें services लिखी हों
Step 2 → Dashboard: New → Blueprint → repo चुनो
Step 3 → Render हर service build (buildCommand) और start (startCommand) करता है
Step 4 → Secrets: env vars को sync:false करो, dashboard में भरो
Step 5 → healthCheckPath poll होता है; healthy होने पर ही traffic मिलता है
Step 6 → नया instance live होने के बाद पुराना बंद होता है (zero-downtime)
Step 7 → autoDeploy: branch पर हर push redeploy करता है
Step 8 → Workers queue (Redis/Key Value) से पढ़ते हैं; services private network से बात करती हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: `render.yaml` defines `tariff-api` (web service), `tariff-worker` (background worker processing bulk invoice uploads) and a Postgres database with pgvector for HS code embeddings. Pull requests get preview environments so reviewers can test classification changes.

**Amazon-style**: A nightly cron job re-embeds new product descriptions.

## 🟡 Real Example Hindi mein
**Tariff System**: `render.yaml` में `tariff-api` (web service), `tariff-worker` (bulk invoice uploads का background worker) और HS code embeddings के लिए pgvector वाला Postgres है। Pull requests को preview environments मिलते हैं ताकि reviewers classification changes test कर सकें।

**Amazon-style**: रात का cron job नए product descriptions को दोबारा embed करता है।

---

## 💻 Code Example — Basic
```python
# Generate and validate a render.yaml from Python (offline). Requires PyYAML only if you want to dump YAML;
# here we use a simple dict and json so it runs with the standard library.
import json  # standard library
from typing import Any  # typing


def render_blueprint(service_name: str, repo_branch: str = "main") -> dict[str, Any]:
    """Return the render.yaml structure as a dict."""
    return {
        "services": [
            {
                "type": "web",  # a public web service
                "name": service_name,  # service name
                "runtime": "python",  # native Python runtime
                "plan": "starter",  # paid plan, free plan sleeps (illustrative plan name)
                "branch": repo_branch,  # branch to deploy
                "buildCommand": "pip install -r requirements.txt",  # build step
                "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",  # run step
                "healthCheckPath": "/health",  # readiness check
                "autoDeploy": True,  # deploy on push
                "envVars": [
                    {"key": "PYTHON_VERSION", "value": "3.12.3"},  # pin Python
                    {"key": "OPENAI_API_KEY", "sync": False},  # secret entered in dashboard
                ],
            }
        ]
    }


if __name__ == "__main__":
    bp = render_blueprint("tariff-api")  # build the blueprint
    assert bp["services"][0]["healthCheckPath"] == "/health"  # sanity check
    print(json.dumps(bp, indent=2))  # JSON is valid YAML, so Render can read it
```

## 💻 Code Example — Advanced
```python
# Trigger a deploy through Render's REST API from CI, with retries and async support
import asyncio  # async runtime
import os  # env vars
from typing import Any  # typing

import httpx  # async HTTP client

API = "https://api.render.com/v1"  # Render public API base


async def trigger_deploy(service_id: str, clear_cache: bool = False, retries: int = 3) -> dict[str, Any]:
    """Start a deploy of a Render service and return the deploy object."""
    token = os.environ["RENDER_API_KEY"]  # API key from CI secrets
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}  # auth headers
    body = {"clearCache": "clear" if clear_cache else "do_not_clear"}  # cache option
    async with httpx.AsyncClient(timeout=30.0) as client:  # one client
        for attempt in range(1, retries + 1):  # retry loop
            try:
                r = await client.post(f"{API}/services/{service_id}/deploys", headers=headers, json=body)  # call
                r.raise_for_status()  # error on 4xx/5xx
                return r.json()  # deploy info
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code < 500:  # client errors will not succeed on retry
                    raise  # fail fast
            except httpx.TransportError:  # network hiccup
                pass  # retry
            await asyncio.sleep(2 ** attempt)  # exponential backoff
    raise RuntimeError("Render deploy trigger failed after retries")  # give up


if __name__ == "__main__":
    # asyncio.run(trigger_deploy(os.environ["RENDER_SERVICE_ID"]))  # run in CI
    print("Set RENDER_API_KEY and RENDER_SERVICE_ID, then call trigger_deploy")  # usage hint
```

---

## 🟠 FastAPI Integration
```python
# FastAPI app that works on Render: PORT env, /health, Postgres from DATABASE_URL
import os  # env
from fastapi import FastAPI  # framework

app = FastAPI(title="tariff-api")  # app
DATABASE_URL = os.getenv("DATABASE_URL", "")  # Render injects it when linked via fromDatabase in the blueprint


@app.get("/health")  # health route used by Render
async def health() -> dict[str, bool]:
    return {"ok": True, "db_configured": bool(DATABASE_URL)}  # cheap check, no LLM call
```

---

## 🔗 LangChain / LangGraph Connection
Render's Postgres supports the pgvector extension, so a LangChain `PGVector` store can hold HS code embeddings in the same database. A background worker service can run LangGraph jobs that exceed web request timeouts.

```python
# LangChain PGVector on Render Postgres (needs langchain-postgres, psycopg)
import os  # env
from langchain_openai import OpenAIEmbeddings  # embeddings
from langchain_postgres import PGVector  # vector store

store = PGVector(
    embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),  # embedding model
    collection_name="hs_codes",  # logical collection
    connection=os.environ["DATABASE_URL"].replace("postgres://", "postgresql+psycopg://"),  # driver URL
)
docs = store.similarity_search("smart phone", k=3)  # semantic search
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the free plan for a production API
```python
# Wrong: free web services spin down after idle time, first request takes a long cold start
plan = "free"
# Correct: paid always-on plan for production, free only for demos
plan = "starter"
```

❌ Mistake 2: Writing files to local disk
```python
# Wrong: filesystem is ephemeral, files vanish at each deploy/restart
open("cache.json", "w").write(data)
# Correct: use Postgres/Redis/object storage, or attach a persistent disk (paid) for needed files
```

---

## 🧠 Tricky Interview Question
**Q**: "After every deploy your users see 502 errors for a few seconds, even though Render does zero-downtime deploys. Why?"

**Answer**: Zero-downtime only works if the new instance passes the health check and the old one drains. Common causes: no `healthCheckPath` (traffic is sent before the app is ready, for example while loading an index), the app ignoring SIGTERM so in-flight requests are cut, or very slow startup. Fix: add a readiness-style `/health`, lazy or fast startup, handle SIGTERM gracefully (finish requests), and keep a retry on the client side.

---

## ⚫ Interview Questions + Answers

Q1: What is a Render Blueprint?
A1: A `render.yaml` file that defines services, databases and env vars as code.

Q2: Web service vs background worker?
A2: A web service receives HTTP and has a public URL; a background worker runs continuously without HTTP, for queue consumers.

Q3: How do you keep secrets out of `render.yaml`?
A3: Use `sync: false` so the value is set in the dashboard, or environment groups and secret files.

Q4: How can you test pull requests?
A4: Preview environments create a temporary copy of the Blueprint services per PR.

Q5: Compare Render and Railway for an AI API.
A5: Both are PaaS with Git deploys and managed Postgres. Render is strong on Blueprints, background workers, cron jobs and predictable instance-based pricing; Railway on speed and usage-based pricing. Choice depends on pricing model, team familiarity and needed features; neither offers GPUs the way SageMaker does (check current offerings).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Small-to-mid APIs with workers and cron jobs
- You want infrastructure as a single YAML
- You need preview environments

❌ Avoid when:
- Strict VPC or compliance needs
- GPU model hosting
- Deep AWS integration (IAM, Bedrock via roles)

---

## 📊 Visual Diagram
```
 GitHub repo ── render.yaml ──▶ Render Blueprint
                                   │
       ┌───────────────────────────┼────────────────────────┐
       ▼                           ▼                        ▼
 Web: tariff-api            Worker: tariff-worker     Postgres (pgvector)
 /health, $PORT                reads queue                  ▲
       └────────── private network ─────────────────────────┘
 PR opened ──▶ Preview environment (temporary copy)
```

---

## 💰 Cost Impact
Render bills per instance type per month (plus databases and bandwidth); exact prices change, so check the pricing page. Illustrative: a small always-on web service is on the order of $7 to $25 per month. Tokens are separate: if 20K requests/day average 900 tokens on gpt-4o-mini (illustrative $0.15/$0.60 per 1M), LLM cost is a few dollars daily. Optimise: pick the smallest instance that holds one async uvicorn worker, move heavy jobs to a worker that can scale separately, cache answers in Redis/Key Value, use cron jobs for batch work instead of an always-on service, and shut down preview environments when PRs close.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Blueprint | render.yaml infrastructure file | Infrastructure की YAML file |
| Web service | Public HTTP service | Public HTTP service |
| Background worker | Non-HTTP long-running process | बिना HTTP वाला worker |
| Preview environment | Temporary PR copy | PR की अस्थायी copy |
| Cron job | Scheduled task | Schedule पर चलने वाला काम |
| autoDeploy | Deploy on every push | हर push पर deploy |

---

## ⚡ 3-Line Summary
English: Render deploys web services, workers, cron and databases from a Git repo, described in render.yaml. Use a paid plan, a health check and secrets via the dashboard. It suits small-to-mid AI APIs; choose ECS for compliance and GPUs.
Hindi: Render Git repo से web services, workers, cron और databases deploy करता है, render.yaml में लिखकर। Paid plan, health check और dashboard से secrets इस्तेमाल करो। छोटे-मध्यम AI APIs के लिए ठीक; compliance और GPUs के लिए ECS चुनो।

---

## ➡️ Next Topic
**554. Nginx for AI API** — putting a reverse proxy in front of your app, with correct settings for long LLM requests and streaming.
