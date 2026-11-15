---

# 446. Deploy on Railway/Render
# हिंदी में: Railway/Render पर Deploy करना

---

## 🔵 Simple Definition (English)
Railway and Render are PaaS (Platform as a Service) hosts. You connect a GitHub repo, tell them how to install and start your app, and they build it, give you an HTTPS URL, manage the server and redeploy on every `git push`. You do not manage Linux, Nginx or certificates.

## 🔵 सरल परिभाषा (Hindi)
Railway और Render PaaS (Platform as a Service) hosts हैं। आप GitHub repo जोड़ते हो, बताते हो कि app कैसे install और start होगा, और वे उसे build करते हैं, HTTPS URL देते हैं, server संभालते हैं और हर `git push` पर फिर से deploy करते हैं। आपको Linux, Nginx या certificates नहीं संभालने।

---

## 🔴 Problem it Solves
A VPS or EC2 deployment needs hours of setup (users, firewall, systemd, Nginx, certbot) and continuous maintenance (patches, backups). For a side project, a startup MVP or a demo for an interview, that time is better spent on the product. PaaS reduces deployment to: connect repo, set start command and env vars, click deploy.

## 🔴 यह क्यों बना? (Hindi)
VPS या EC2 deployment में घंटों का setup (users, firewall, systemd, Nginx, certbot) और लगातार रखरखाव (patches, backups) लगता है। Side project, startup MVP या interview demo के लिए वह समय product पर लगना बेहतर है। PaaS deployment को छोटा कर देता है: repo जोड़ो, start command और env vars डालो, deploy दबाओ।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Push your FastAPI project (main.py + requirements.txt) to GitHub
Step 2 → Create a Web Service (Render) / New Project from repo (Railway)
Step 3 → Build command: pip install -r requirements.txt  (or Dockerfile if present)
Step 4 → Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
Step 5 → Platform injects PORT and your env vars (DATABASE_URL, SECRET_KEY)
Step 6 → Add a managed PostgreSQL; its connection URL is linked into your service
Step 7 → Health check path /health: platform waits for 200 before sending traffic
Step 8 → Every git push to the main branch auto-deploys; roll back from the dashboard
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → FastAPI project (main.py + requirements.txt) GitHub पर push करो
Step 2 → Web Service बनाओ (Render) / repo से New Project (Railway)
Step 3 → Build command: pip install -r requirements.txt (या Dockerfile हो तो वही)
Step 4 → Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
Step 5 → Platform PORT और आपके env vars (DATABASE_URL, SECRET_KEY) inject करता है
Step 6 → managed PostgreSQL जोड़ो; उसकी connection URL आपकी service से जुड़ जाती है
Step 7 → Health check path /health: traffic भेजने से पहले platform 200 का इंतज़ार करता है
Step 8 → main branch पर हर git push से auto-deploy; dashboard से rollback
```

---

## 🟡 Real World Example
A student builds an expense-tracker API for a portfolio. On Render's free tier she deploys the FastAPI service and a free PostgreSQL in 10 minutes, shares `https://expense-api.onrender.com/docs` with recruiters, and every push to GitHub redeploys it. A small startup uses Railway for staging (a preview environment per pull request) and moves production to AWS later when traffic grows.

## 🟡 Real Example Hindi mein
एक student portfolio के लिए expense-tracker API बनाती है। Render के free tier पर वह FastAPI service और free PostgreSQL 10 मिनट में deploy करती है, recruiters को `https://expense-api.onrender.com/docs` भेजती है, और GitHub पर हर push से redeploy हो जाता है। एक छोटा startup staging के लिए Railway इस्तेमाल करता है (हर pull request का preview environment) और traffic बढ़ने पर production AWS पर ले जाता है।

---

## 💻 Code Example — Basic
The three things every PaaS needs: read `$PORT`, bind to `0.0.0.0`, and expose a health check. Ran locally with the test client; the platform was not used:

```python
# Basic: the three things Railway/Render need - read $PORT, bind 0.0.0.0, /health
import os                                         # env vars
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}                       # health check path in the dashboard


def server_args() -> dict[str, str | int]:
    return {"host": "0.0.0.0",                    # NOT 127.0.0.1: the platform proxy is outside the container
            "port": int(os.environ.get("PORT", "8000"))}   # platform injects PORT


os.environ["PORT"] = "10000"                      # simulate Render's default port
print(server_args())                              # {'host': '0.0.0.0', 'port': 10000}
print(TestClient(app).get("/health").json())
# Start command on the platform:  uvicorn main:app --host 0.0.0.0 --port $PORT

# Output (real run, Python 3.13):
# {'host': '0.0.0.0', 'port': 10000}
# {'status': 'ok'}
```

Files you add to the repo (**not run**: no Render/Railway account here):

```text
# requirements.txt
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy>=2.0
psycopg[binary]>=3.2
```
(Pin the versions you actually tested; these are examples.)

## 💻 Code Example — Advanced
Typed settings that fix the common `postgres://` URL, refuse to boot without a database URL, plus validation of `render.yaml` (a Render Blueprint) and `railway.toml` (Railway config as code). Ran locally; the two config files were parsed but not deployed:

```python
# Advanced: settings for PaaS - fix postgres:// URL, require secrets, validate render.yaml/railway.toml
import tomllib                                    # stdlib TOML parser (Python 3.11+)
import yaml                                       # PyYAML

from pydantic import field_validator              # validation hook
from pydantic_settings import BaseSettings        # env-based settings


class Settings(BaseSettings):
    database_url: str                             # REQUIRED: app refuses to boot without it
    port: int = 8000                              # platform sets PORT
    secret_key: str = "dev-only"

    @field_validator("database_url")
    @classmethod
    def fix_scheme(cls, v: str) -> str:
        if v.startswith("postgres://"):           # Heroku/Render style URL
            v = v.replace("postgres://", "postgresql+psycopg://", 1)   # SQLAlchemy 2 needs a driver name
        return v


import os
os.environ.update(DATABASE_URL="postgres://u:p@dpg-abc:5432/db", PORT="10000")
s = Settings()
print(s.database_url, s.port)

RENDER = """
services:
  - type: web
    name: orders-api
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: DATABASE_URL
        fromDatabase: {name: orders-db, property: connectionString}
      - key: SECRET_KEY
        generateValue: true
databases:
  - name: orders-db
    plan: free
"""
RAILWAY = """
[build]
builder = "RAILPACK"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
restartPolicyType = "ON_FAILURE"
"""
web = yaml.safe_load(RENDER)["services"][0]
assert "$PORT" in web["startCommand"] and web["healthCheckPath"] == "/health"
print("render.yaml ok:", web["name"])
cfg = tomllib.loads(RAILWAY)                      # raises TOMLDecodeError on bad syntax
assert cfg["deploy"]["healthcheckPath"] == "/health"
print("railway.toml ok:", cfg["deploy"]["restartPolicyType"])
try:
    os.environ.pop("DATABASE_URL"); Settings()    # missing required secret
except Exception as e:
    print(type(e).__name__)

# Output (real run, Python 3.13):
# postgresql+psycopg://u:p@dpg-abc:5432/db 10000
# render.yaml ok: orders-api
# railway.toml ok: ON_FAILURE
# ValidationError
```

Why `postgres://` is rewritten: many platforms hand you `postgres://...`, but SQLAlchemy 2.x does not accept the bare `postgres` dialect name, so you convert it to `postgresql+psycopg://` (psycopg 3). Keys in `render.yaml` and `railway.toml` follow each platform's docs at the time of writing; always check their current reference because platforms change names (for example Railway's default builder has been renamed before).

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python / FastAPI | Node / Express |
|---------|-----------------|----------------|
| Build | `pip install -r requirements.txt` | `npm ci && npm run build` |
| Start | `uvicorn main:app --host 0.0.0.0 --port $PORT` | `node server.js` |
| Port | `os.environ["PORT"]` | `process.env.PORT` |
| Runtime version | `.python-version` / `runtime.txt` / `PYTHON_VERSION` | `engines` in package.json |
| Config as code | `render.yaml`, `railway.toml` | same files |

```python
# Python way — bind to the platform's port
import os
import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
```
```javascript
// JavaScript way — same rule
const port = process.env.PORT || 3000;
app.listen(port, "0.0.0.0", () => console.log(`listening on ${port}`));
```

Key difference: none in principle. PaaS platforms are language-agnostic, but Python needs an ASGI server command (uvicorn/gunicorn) in the start command, while Node starts itself.

---

## 🟠 FastAPI Connection
On PaaS the FastAPI app must (1) listen on `0.0.0.0:$PORT`, (2) read every secret from env vars, (3) use the platform's managed database URL, (4) log to stdout, and (5) answer `/health` quickly. Free tiers sleep after inactivity (Render free web services spin down), so the first request after idle may take about 30-60 seconds; do not run important background work in-process there. The platform terminates HTTPS, so start uvicorn with `--proxy-headers` if you need the real scheme/IP.

```python
# FastAPI example — CORS from env, so the same code works in staging and production
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins: list[str] = [o for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])
print(origins)      # ['http://localhost:3000'] when CORS_ORIGINS is not set
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Hardcoding the port or binding to `127.0.0.1`
✅ Correct: `--host 0.0.0.0 --port $PORT`

```bash
# Wrong: platform proxy cannot reach it -> "Application failed to respond" / port scan timeout
uvicorn main:app --host 127.0.0.1 --port 8000
# Right
uvicorn main:app --host 0.0.0.0 --port $PORT
```

❌ Mistake 2: Using SQLite or local files for production data
✅ Correct: managed PostgreSQL; the container filesystem is ephemeral and wiped on each deploy

```python
# Wrong: data disappears at the next deploy / restart
DATABASE_URL = "sqlite:///./app.db"
# Right
import os
DATABASE_URL = os.environ["DATABASE_URL"]        # injected by the platform
```

❌ Mistake 3: Committing secrets or forgetting the Python version
✅ Correct: set secrets in the dashboard; pin the Python version

```text
Wrong:  .env with real keys in git; platform picks a different default Python
Right:  env vars in dashboard (or generateValue: true); PYTHON_VERSION=3.13.x (Render) or .python-version
```

---

## 🧠 Tricky Interview Question

```python
# What will this output? (the platform sets PORT="10000")
import os
port = os.environ.get("PORT", 8000)
print(port, type(port).__name__)
print(port + 1)
```
Answer: It prints `10000 str`, and then `port + 1` raises `TypeError: can only concatenate str (not "int") to str`. Environment variables are always strings. The default `8000` is an `int`, so the same code returns an `int` locally (when PORT is unset) and a `str` on the platform, a bug that only appears in production. Always convert: `int(os.environ.get("PORT", "8000"))`, or use Pydantic Settings (`port: int = 8000`) which converts and validates for you.

---

## ⚫ Interview Questions + Answers

Q1: Why does my app work locally but the platform says the deploy failed health check?
A1: Usual causes: binding to 127.0.0.1, ignoring `$PORT`, a crash at import time (missing env var), a slow startup that exceeds the health-check timeout, or a health path that returns 404. Check the deploy logs first, since they print the traceback.

Q2: Render vs Railway vs Heroku vs Fly.io?
A2: All are PaaS. Render has a simple free tier (with spin-down), Blueprints (`render.yaml`) and managed Postgres. Railway is developer-friendly with usage-based pricing and easy service linking. Heroku is the original, now paid only. Fly.io runs your Docker image on VMs near users. Pricing and free tiers change often, so verify before you decide.

Q3: How do you run database migrations on deploy?
A3: Use a pre-deploy command (Render: `preDeployCommand: alembic upgrade head`; Railway: a pre-deploy step in config) so migrations run once before the new version takes traffic, rather than inside every app instance on startup.

Q4: How do you handle background jobs and cron?
A4: Create separate services from the same repo: a worker (Celery/ARQ/RQ) with its own start command and a Redis instance, and cron jobs (Render Cron Job, Railway cron schedule). Do not rely on in-process threads in the web service.

Q5: How do you move from PaaS to something bigger later?
A5: Keep the app twelve-factor: config in env, logs to stdout, stateless processes, a Dockerfile. Then the same container deploys to ECS, Cloud Run or Kubernetes with only the config changed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- MVPs, demos, portfolios, small internal APIs
- A small team without DevOps time
- Preview environments per pull request

❌ Avoid when:
- You need fine control of networking, compliance or custom hardware
- Heavy steady traffic where reserved cloud capacity is much cheaper
- You rely on persistent local disk or long-lived processes on a free tier that sleeps

---

## 📊 Visual Diagram
```
 git push ──> GitHub ──webhook──> Render / Railway
                                     | build: pip install -r requirements.txt
                                     | start: uvicorn main:app --host 0.0.0.0 --port $PORT
                                     v
   User --HTTPS--> [ platform proxy, TLS ] --> [ your container :$PORT ]
                                                  |  DATABASE_URL (env)
                                                  v
                                           [ managed PostgreSQL ]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| PaaS | Platform that runs your code for you | आपका code चलाने वाला platform |
| `$PORT` | Port number injected by the platform | platform का दिया port |
| Blueprint | `render.yaml` infrastructure file | Render की infrastructure file |
| Ephemeral disk | Files lost on redeploy | redeploy पर मिटने वाली files |
| Pre-deploy command | Task run before release | release से पहले चलने वाला काम |
| Health check | URL the platform probes | जिसे platform जाँचता है |
| Twelve-factor | Cloud-friendly app rules | cloud-अनुकूल app के नियम |

---

## ⚡ 3-Line Summary
English: Railway and Render build and run your repo with a start command, an injected PORT and env vars. Bind to 0.0.0.0, read config from the environment and use managed PostgreSQL, not local files. Run migrations in a pre-deploy step and keep a `/health` endpoint.
Hindi: Railway और Render आपके repo को start command, inject किए गए PORT और env vars के साथ build करके चलाते हैं। 0.0.0.0 पर bind करो, config environment से पढ़ो और local files की जगह managed PostgreSQL इस्तेमाल करो। Migrations pre-deploy step में चलाओ और `/health` endpoint रखो।

---

## ➡️ Next Topic
The next topic in the series (after the deployment folder): CI/CD for Python, so every push is tested and deployed automatically, and background workers (Celery + Redis) running beside the API.
