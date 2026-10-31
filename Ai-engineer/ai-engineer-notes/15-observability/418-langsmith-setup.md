---

# 418. LangSmith Setup
# हिंदी में: LangSmith Setup

---

## 🔵 Simple Definition (English)
LangSmith setup means: create an account, make an API key, install the `langsmith` package, set a few environment variables (`LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`), and run your app. After that, traces appear in the web UI. No code change is needed for LangChain/LangGraph.

## 🔵 सरल परिभाषा (Hindi)
LangSmith setup का मतलब: account बनाओ, API key बनाओ, `langsmith` package install करो, कुछ environment variables (`LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`) set करो और app चलाओ। उसके बाद traces web UI में दिखने लगते हैं। LangChain/LangGraph में code बदलने की ज़रूरत नहीं।

---

## 🔴 Problem it Solves
- Teams waste hours because tracing silently does not work (wrong env var name, key in the wrong workspace, `.env` not loaded).
- Dev, staging and production traces get mixed together without separate projects/keys.
- Secrets get committed to git.

## 🔴 यह क्यों बना? (Hindi)
- Tracing चुपचाप काम नहीं करती (env var का गलत नाम, गलत workspace की key, `.env` load नहीं हुआ) और घंटे बर्बाद होते हैं।
- Separate projects/keys न हों तो dev, staging और production के traces मिल जाते हैं।
- Secrets git में commit हो जाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Sign up at smith.langchain.com, create/select a workspace
Step 2 → Settings → API Keys → create key (personal or service key)
Step 3 → pip install -U langsmith langchain-openai
Step 4 → Put keys in .env (git-ignored): LANGSMITH_API_KEY, OPENAI_API_KEY
Step 5 → Set LANGSMITH_TRACING=true and LANGSMITH_PROJECT=<name>
Step 6 → Run the app → SDK sends runs in the background
Step 7 → Open the project in the UI and verify the first trace
Step 8 → One key + one project per environment (dev / staging / prod)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → smith.langchain.com पर sign up करो, workspace चुनो/बनाओ
Step 2 → Settings → API Keys → key बनाओ (personal या service key)
Step 3 → pip install -U langsmith langchain-openai
Step 4 → .env में keys रखो (git-ignored): LANGSMITH_API_KEY, OPENAI_API_KEY
Step 5 → LANGSMITH_TRACING=true और LANGSMITH_PROJECT=<नाम> set करो
Step 6 → App चलाओ → SDK background में runs भेजता है
Step 7 → UI में project खोलकर पहला trace verify करो
Step 8 → हर environment (dev / staging / prod) के लिए अलग key + project
```

---

## 🟡 Real World Example
**Tariff Classification System**: Three projects are created: `tariff-dev`, `tariff-staging`, `tariff-prod`. Developers use personal keys locally with `tariff-dev`. CI uses a service key limited to `tariff-staging`. Production pods get `LANGSMITH_PROJECT=tariff-prod` from a Kubernetes secret. A startup check calls `Client().list_projects()` and logs a warning if tracing is on but the key is invalid, so nobody discovers missing traces after an incident.

**Zomato AI**: Each microservice (search, offers, support) sets its own `LANGSMITH_PROJECT`, so teams see only their traces.

## 🟡 Real Example Hindi mein
**Tariff System**: तीन projects बनाए: `tariff-dev`, `tariff-staging`, `tariff-prod`। Developers local में personal key से `tariff-dev` use करते हैं। CI में `tariff-staging` तक सीमित service key है। Production pods को Kubernetes secret से `LANGSMITH_PROJECT=tariff-prod` मिलता है। Startup पर check होता है कि tracing on है पर key invalid तो warning log हो, ताकि incident के बाद पता न चले कि traces थे ही नहीं।

**Zomato AI**: हर microservice (search, offers, support) अपना `LANGSMITH_PROJECT` रखता है, इसलिए हर team को सिर्फ़ अपने traces दिखते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: validate that your LangSmith env vars are set correctly (pure Python, offline)
import os                                                     # read environment variables

REQUIRED: list[str] = ["LANGSMITH_API_KEY", "LANGSMITH_PROJECT"]  # must exist when tracing is on

def check_env(env: dict[str, str]) -> list[str]:              # returns a list of problems
    problems: list[str] = []                                  # collect messages
    if env.get("LANGSMITH_TRACING", "").lower() != "true":    # tracing flag must be "true"
        problems.append("LANGSMITH_TRACING is not 'true' (tracing is OFF)")
    for name in REQUIRED:                                     # check each required variable
        if not env.get(name):                                 # missing or empty
            problems.append(f"{name} is missing")
    key = env.get("LANGSMITH_API_KEY", "")                    # look at the key format
    if key and not key.startswith(("lsv2_", "ls__")):         # keys start with lsv2_
        problems.append("API key format looks wrong")
    return problems                                           # empty list means OK

# Simulated environment (never print real keys!):
fake_env = {"LANGSMITH_TRACING": "true", "LANGSMITH_API_KEY": "lsv2_pt_demo", "LANGSMITH_PROJECT": "tariff-dev"}
print("fake env problems:", check_env(fake_env))              # []
print("real env problems:", check_env(dict(os.environ)))      # shows what is missing on your machine
```

## 💻 Code Example — Advanced
```python
# Production startup module: load .env, validate, verify connectivity, never crash the app
# pip install langsmith python-dotenv
import asyncio                                                # async wrapper
import logging                                                # structured logs
import os                                                     # env vars
from dataclasses import dataclass                             # config container

from dotenv import load_dotenv                                # loads .env in local dev

logger = logging.getLogger("observability")                   # module logger

@dataclass(frozen=True)
class TracingConfig:                                          # immutable config
    enabled: bool                                             # is tracing on
    project: str                                              # project name
    sample_rate: float                                        # 0..1, fraction of requests traced

def load_config() -> TracingConfig:
    load_dotenv(override=False)                               # .env never overrides real env
    enabled = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
    project = os.getenv("LANGSMITH_PROJECT", "default")       # default project if not set
    try:
        rate = float(os.getenv("TRACE_SAMPLE_RATE", "1.0"))   # parse sampling rate
    except ValueError:                                        # bad value => safe default
        rate = 1.0
    return TracingConfig(enabled, project, min(max(rate, 0.0), 1.0))  # clamp to [0,1]

def verify_sync() -> bool:
    """Return True if the key works. Must never raise."""
    from langsmith import Client                              # imported lazily (optional dependency)
    try:
        client = Client()                                     # reads key + endpoint from env
        next(iter(client.list_projects(limit=1)), None)       # cheap authenticated call
        return True
    except Exception as exc:                                  # network or auth problem
        logger.warning("LangSmith check failed: %s", type(exc).__name__)
        return False

async def startup_check() -> None:
    cfg = load_config()                                       # read settings
    if not cfg.enabled:                                       # nothing to verify
        logger.info("Tracing disabled")
        return
    ok = await asyncio.to_thread(verify_sync)                 # run blocking call off the event loop
    if not ok:                                                # disable to avoid noisy errors
        os.environ["LANGSMITH_TRACING"] = "false"
        logger.error("Tracing turned off: LangSmith unreachable or key invalid")

if __name__ == "__main__":
    print(load_config())                                      # safe to run without keys
```

---

## 🟠 FastAPI Integration
Run the startup check in FastAPI's `lifespan` so the app starts even if LangSmith is down, and add a debug route that reports (without leaking secrets) whether tracing is active.

```python
from contextlib import asynccontextmanager                    # lifespan helper
from fastapi import FastAPI                                   # framework
import os                                                     # env

@asynccontextmanager
async def lifespan(app: FastAPI):                             # runs at startup and shutdown
    await startup_check()                                     # from the advanced example
    yield                                                     # app serves requests here
    # shutdown: LangChain flushes callbacks; see wait_for_all_tracers below

app = FastAPI(lifespan=lifespan)                              # attach lifespan

@app.get("/debug/tracing")                                    # protect this route in production!
async def tracing_status() -> dict[str, str | bool]:
    return {"enabled": os.getenv("LANGSMITH_TRACING") == "true",   # boolean only
            "project": os.getenv("LANGSMITH_PROJECT", "default")}  # no key is returned
```

---

## 🔗 LangChain / LangGraph Connection
LangChain reads `LANGSMITH_*` (older `LANGCHAIN_*` names still work) at runtime. You can also override per call using `tracing_v2_enabled` or `config`. In short-lived processes (scripts, serverless) call `wait_for_all_tracers()` before exit so the last traces are not lost.

```python
from langchain_core.tracers.langchain import wait_for_all_tracers  # flush helper
from langchain_core.tracers.context import tracing_v2_enabled      # turn tracing on for a block

# with tracing_v2_enabled(project_name="tariff-dev"):          # trace only this block
#     chain.invoke({"p": "power bank"})
# wait_for_all_tracers()                                       # flush before the script ends
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Setting `LANGSMITH_TRACING="True "` or forgetting it entirely and wondering why nothing shows.
✅ Correct: exact lowercase `true`, and verify with a startup check.

```python
# Wrong
os.environ["LANGSMITH_TRACING"] = "yes"
# Right
os.environ["LANGSMITH_TRACING"] = "true"
```

❌ Mistake 2: Setting env vars AFTER importing/creating clients in a way that they never see them, or using one key for all environments.
✅ Correct: load env first (top of `main`), separate keys and projects per environment.

```python
# Wrong: client created before load_dotenv()
from openai import OpenAI; client = OpenAI(); load_dotenv()
# Right
load_dotenv(); from openai import OpenAI; client = OpenAI()
```

---

## 🧠 Tricky Interview Question
**Q**: "You enabled LangSmith in production but the project shows no traces from your Lambda function. Local runs are fine. Why?"

**Answer**: Tracing is sent from a background thread. A Lambda/serverless runtime may freeze or exit before the buffer is flushed. Fix: call `wait_for_all_tracers()` (LangChain) or `client.flush()` (SDK) before returning. Also check that env vars exist in the Lambda config (not just local `.env`), that the function has outbound internet/VPC egress to `api.smith.langchain.com`, and that the key belongs to the right workspace.

---

## ⚫ Interview Questions + Answers

Q1: Which env vars enable tracing? (Easy)
A1: `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY`, and optionally `LANGSMITH_PROJECT`. Older docs use `LANGCHAIN_TRACING_V2` and `LANGCHAIN_API_KEY`.

Q2: Where do you keep the API key? (Easy)
A2: In environment variables or a secrets manager, never in source control.

Q3: How do you separate dev and prod traces? (Medium)
A3: Different `LANGSMITH_PROJECT` per environment, and ideally different API keys/workspaces so prod data has stricter access.

Q4: How do you trace only some requests? (Medium)
A4: Use `tracing_v2_enabled` / `langsmith.tracing_context(enabled=True)` conditionally based on a sampling rule, or set `LANGSMITH_TRACING=false` globally and enable per request.

Q5: Your company needs data to stay in-house. What are the options? (Hard)
A5: Use the EU region or self-hosted LangSmith (Kubernetes deployment, enterprise plan), point `LANGSMITH_ENDPOINT` to it, mask inputs/outputs with `process_inputs`/`process_outputs` or `hide_inputs`/`hide_outputs`, or choose an open-source alternative such as Langfuse self-hosted. Also set data retention and RBAC.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Starting any LLM project: set tracing up on day one
- Different teams/environments need separation

❌ Avoid when:
- Handling data that cannot leave your network, without self-hosting or masking
- Tracing high-volume trivial calls (sample instead)

---

## 📊 Visual Diagram
```
  .env / Secrets Manager
  ├─ LANGSMITH_TRACING=true
  ├─ LANGSMITH_API_KEY=lsv2_...
  └─ LANGSMITH_PROJECT=tariff-prod
            │
            ▼
   App process ──(background thread)──► api.smith.langchain.com
            │                                   │
       startup_check()                   Project "tariff-prod"
       (warn, never crash)               └─ first trace ✔
```

---

## 💰 Cost Impact
- Setup uses zero LLM tokens. LangSmith pricing is by trace count and retention (a free developer tier exists; check the current pricing page). 
- Optimise: sample prod (e.g. 10-20%), use `TRACE_SAMPLE_RATE`, keep dev traces short-lived, avoid tracing health checks and tiny utility functions, and hide large retrieved contexts if they are not needed.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| API key | Secret to authenticate | Authentication की गुप्त key |
| Environment variable | OS-level config value | OS स्तर का config |
| Workspace | Team space in LangSmith | LangSmith में team की जगह |
| Service key | Key for automation/CI | Automation के लिए key |
| Flush | Send buffered traces now | Buffer के traces तुरंत भेजना |
| Endpoint | URL of the LangSmith server | LangSmith server का URL |

---

## ⚡ 3-Line Summary
English: Install `langsmith`, create an API key, and set `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY` and `LANGSMITH_PROJECT`. Use separate keys and projects per environment, and validate the setup at startup without crashing the app. Flush traces in serverless or short scripts.
Hindi: `langsmith` install करो, API key बनाओ और `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT` set करो। हर environment के लिए अलग key और project रखो, और startup पर setup जाँचो पर app crash मत होने दो। Serverless या छोटी scripts में traces flush करो।

---

## ➡️ Next Topic
**419. Tracing in LangSmith** — reading traces, nested runs, metadata and tags.
