
---

# 552. Deploy on Railway (Easy)
# हिंदी में: Railway पर Deploy (आसान तरीका)

---

## 🔵 Simple Definition (English)
Railway is a hosting platform where you connect a GitHub repo (or a Dockerfile) and it builds and runs your app, gives a public URL, and manages env vars, databases and logs. It is the fastest way to put a FastAPI AI app online for demos, MVPs and small production workloads. Pricing is usage-based and plans change, so check the current page.

## 🔵 सरल परिभाषा (Hindi)
Railway एक hosting platform है जहाँ आप GitHub repo (या Dockerfile) जोड़ते हैं और वह app build करके चलाता है, public URL देता है, और env vars, databases, logs सँभालता है। Demos, MVPs और छोटे production workloads के लिए FastAPI AI app online करने का सबसे तेज़ तरीका। Pricing usage-based है और plans बदलते रहते हैं, current page देखो।

---

## 🔴 Problem it Solves
For a first deploy, AWS means IAM, VPC, ECR, ALB, and many hours of setup. Early teams want "git push, get a URL". Railway removes infra work so you can show the product to users or interviewers quickly.

## 🔴 यह क्यों बना? (Hindi)
पहले deploy के लिए AWS में IAM, VPC, ECR, ALB और घंटों का setup लगता है। शुरुआती teams को "git push, URL मिले" चाहिए। Railway infra का काम हटा देता है ताकि product users या interviewers को जल्दी दिखा सकें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Push your FastAPI project to GitHub (with requirements.txt or Dockerfile)
Step 2 → In Railway: New Project → Deploy from GitHub repo
Step 3 → Railway detects Python (Nixpacks/Railpack) or uses your Dockerfile and builds
Step 4 → Set variables (OPENAI_API_KEY, DATABASE_URL) in the Variables tab
Step 5 → Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
Step 6 → Generate a public domain; Railway injects $PORT and routes HTTPS traffic
Step 7 → Set a healthcheck path (/health); each git push triggers a new deploy
Step 8 → Add Postgres/Redis plugins, view logs and metrics in dashboard
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → FastAPI project GitHub पर push करो (requirements.txt या Dockerfile के साथ)
Step 2 → Railway में New Project → Deploy from GitHub repo
Step 3 → Railway Python detect करके (या Dockerfile से) build करता है
Step 4 → Variables tab में OPENAI_API_KEY, DATABASE_URL डालो
Step 5 → Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
Step 6 → Public domain generate करो; Railway $PORT देता है और HTTPS route करता है
Step 7 → Healthcheck path (/health) सेट करो; हर git push नया deploy करता है
Step 8 → Postgres/Redis जोड़ो, dashboard में logs और metrics देखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The MVP `tariff-api` with Postgres and Redis (for caching) is deployed on Railway for a pilot with 5 customs brokers. Each pull request merged to `main` auto-deploys. When the pilot becomes serious, the same Dockerfile moves to ECS.

**Zomato-style**: A hackathon demo of a food-recommendation chatbot is shared with judges through a Railway URL.

## 🟡 Real Example Hindi mein
**Tariff System**: MVP `tariff-api` Postgres और Redis (caching) के साथ 5 customs brokers के pilot के लिए Railway पर deploy है। `main` पर merge होते ही auto-deploy। Pilot गंभीर होने पर वही Dockerfile ECS पर चला जाता है।

**Zomato-style**: Food-recommendation chatbot का hackathon demo judges को Railway URL से दिखाया जाता है।

---

## 💻 Code Example — Basic
```python
# main.py: a FastAPI app ready for Railway. Run locally: PORT=8000 python main.py
import os  # read PORT and other env vars
import uvicorn  # ASGI server
from fastapi import FastAPI  # framework

app = FastAPI()  # create the app


@app.get("/health")  # Railway healthcheck path
def health() -> dict[str, str]:
    return {"status": "ok"}  # simple response


@app.get("/")  # root route
def root() -> dict[str, str]:
    return {"service": "tariff-api", "env": os.getenv("RAILWAY_ENVIRONMENT_NAME", "local")}  # show environment


if __name__ == "__main__":  # run directly
    port = int(os.environ.get("PORT", "8000"))  # Railway sets PORT, default 8000 locally
    uvicorn.run(app, host="0.0.0.0", port=port)  # bind to all interfaces
```

Config files (not Python), for reference:

```
# railway.json (optional, config as code)
{
  "build": {"builder": "DOCKERFILE", "dockerfilePath": "Dockerfile"},
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

## 💻 Code Example — Advanced
```python
# Production settings: validate env at startup, async DB/LLM clients, graceful errors
import logging  # logs go to stdout, Railway shows them
import os  # env access
from contextlib import asynccontextmanager  # lifespan helper
from typing import AsyncIterator  # type hint

import httpx  # async HTTP client
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # request model

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))  # configure logging from env
log = logging.getLogger("tariff")  # app logger


def require_env(name: str) -> str:
    """Fail fast with a clear message if a variable is missing."""
    value = os.environ.get(name)  # read variable
    if not value:  # missing or empty
        raise RuntimeError(f"Missing required env var: {name}")  # crash at boot, not at first request
    return value  # return the value


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create shared clients on startup and close them on shutdown."""
    app.state.api_key = require_env("OPENAI_API_KEY")  # validate secret at boot
    app.state.http = httpx.AsyncClient(timeout=20.0)  # reusable client
    yield  # app runs here
    await app.state.http.aclose()  # close on SIGTERM so redeploys are clean


app = FastAPI(lifespan=lifespan)  # app with lifespan


class Req(BaseModel):  # request body
    description: str  # product text


@app.post("/classify")  # route
async def classify(req: Req) -> dict[str, str]:
    try:
        r = await app.state.http.post(
            "https://api.openai.com/v1/chat/completions",  # endpoint
            headers={"Authorization": f"Bearer {app.state.api_key}"},  # auth
            json={"model": "gpt-4o-mini", "max_tokens": 60,  # cheap model, capped output
                  "messages": [{"role": "user", "content": f"HS code for {req.description}"}]},
        )
        r.raise_for_status()  # raise on HTTP errors
    except httpx.HTTPError as exc:  # network or API failure
        log.error("llm failed: %s", exc)  # log
        raise HTTPException(status_code=502, detail="LLM upstream error")  # bad gateway
    return {"answer": r.json()["choices"][0]["message"]["content"]}  # answer
```

---

## 🟠 FastAPI Integration
Railway just runs your ASGI app. Three rules: bind to `0.0.0.0`, use the injected `$PORT`, and keep a cheap `/health` route. Use a `Dockerfile` when you need system libraries.

```python
# Dockerfile equivalent expressed as text, for reference (not Python)
# FROM python:3.12-slim
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . .
# CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
print("Railway injects PORT; the CMD above reads it")  # explanatory line so the block is valid Python
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph apps deploy the same way. Railway containers can restart, so keep conversation state in a Postgres checkpointer (a Railway Postgres service), not in memory.

```python
# LangGraph checkpointer on Railway Postgres (needs langgraph-checkpoint-postgres)
import os  # env var access
from langgraph.checkpoint.postgres import PostgresSaver  # Postgres checkpointer

DB_URL = os.environ["DATABASE_URL"]  # Railway injects this from the Postgres plugin
with PostgresSaver.from_conn_string(DB_URL) as saver:  # open connection
    saver.setup()  # create tables once
    # graph = builder.compile(checkpointer=saver)  # use it when compiling your graph
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Hardcoding the port or binding to localhost
```python
# Wrong: Railway cannot reach it, deploy shows "application failed to respond"
uvicorn.run(app, host="127.0.0.1", port=8000)
# Correct:
uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
```

❌ Mistake 2: Committing secrets or storing state on local disk
```python
# Wrong: key in code, uploads saved to container disk (lost on redeploy)
API_KEY = "sk-live-..."
open("uploads/x.pdf", "wb").write(data)
# Correct: key from Variables, files in object storage or an attached Volume
API_KEY = os.environ["OPENAI_API_KEY"]
```

---

## 🧠 Tricky Interview Question
**Q**: "Your Railway app costs ten times more than expected, although traffic is low. Why?"

**Answer**: Usage-based billing charges for memory and CPU time while the service runs, so an app that loads a large model or embeddings into memory, keeps many worker processes, or has a runaway background loop costs a lot even with little traffic. Also LLM API tokens are billed separately by the provider, and a retry loop on errors can multiply calls. Fix: reduce workers and memory, check usage metrics, add rate limits and `max_tokens`, set spend limits in the dashboard and at the LLM provider, and consider sleeping or scaling down non-production environments.

---

## ⚫ Interview Questions + Answers

Q1: Why must the app bind to `0.0.0.0` and use `$PORT`?
A1: The platform's proxy forwards traffic to the container on the port it assigns; `127.0.0.1` is reachable only inside the container.

Q2: How do you keep secrets safe on Railway?
A2: Use the Variables tab (or shared and sealed variables), never commit them, and rotate keys if leaked.

Q3: How do you do database migrations on deploy?
A3: Run them in a pre-deploy command (for example `alembic upgrade head`) so a failed migration stops the release before traffic moves.

Q4: How does Railway handle a bad deploy?
A4: A healthcheck failure keeps the old deployment active, and you can roll back to a previous deployment from the dashboard.

Q5: When should you move from Railway to AWS ECS?
A5: When you need VPC/private networking, compliance, fine-grained IAM, GPUs, regional control, or much cheaper cost at scale. Keep a Dockerfile and 12-factor config from day one so the move is only a deployment change.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- MVPs, demos, interviews, small teams
- You want git-push deploys with built-in Postgres/Redis
- You do not have DevOps staff

❌ Avoid when:
- Strict compliance or private networking is required
- GPU workloads
- Very large, cost-sensitive scale

---

## 📊 Visual Diagram
```
 git push ──▶ GitHub ──▶ Railway build (Dockerfile / Nixpacks)
                              │
                              ▼
                     ┌─────────────────┐   healthcheck /health
 User ── HTTPS ───▶  │ FastAPI :$PORT  │◀──────────────┐
                     └───┬─────────┬───┘               │
                         ▼         ▼               Railway
                    Postgres     Redis             proxy
                         └──▶ LLM API (OPENAI_API_KEY from Variables)
```

---

## 💰 Cost Impact
Railway charges for resources used (CPU, memory, network) plus plan fees that change over time, so treat any number as illustrative and read the pricing page. A light FastAPI app that mostly waits on LLM calls typically needs little RAM, so hosting often costs a few dollars per month. Tokens remain the bigger variable: 10K requests/day x 800 tokens on gpt-4o-mini (illustrative $0.15 input / $0.60 output per 1M) is a few dollars a day. Optimise: one or two uvicorn workers, no model loading in RAM, Redis caching of repeated queries, `max_tokens` caps, provider-side budgets, and scaling down staging environments.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Railway | Git-based app hosting platform | Git से deploy करने वाला hosting |
| $PORT | Port injected by platform | Platform का दिया port |
| Variables | Env var and secrets store | Env vars और secrets की जगह |
| Healthcheck | Path platform pings before routing | Deploy जाँचने वाला path |
| Nixpacks | Auto build system | Auto build system |
| Volume | Persistent disk | Permanent disk |

---

## ⚡ 3-Line Summary
English: Railway builds and runs your FastAPI app from GitHub with almost no setup. Bind to 0.0.0.0, use $PORT, keep secrets in Variables and add a /health route. Great for MVPs; migrate to ECS when compliance or scale demands.
Hindi: Railway GitHub से आपका FastAPI app लगभग बिना setup के build और run करता है। 0.0.0.0 पर bind करो, $PORT इस्तेमाल करो, secrets Variables में रखो और /health route जोड़ो। MVPs के लिए बढ़िया; compliance या scale आने पर ECS पर जाओ।

---

## ➡️ Next Topic
**553. Deploy on Render** — another easy PaaS option with free tiers, blueprints and managed services.
