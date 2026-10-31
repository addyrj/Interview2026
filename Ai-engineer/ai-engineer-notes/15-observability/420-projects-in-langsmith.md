---

# 420. Projects in LangSmith
# हिंदी में: LangSmith में Projects

---

## 🔵 Simple Definition (English)
A LangSmith project is a named container (like a folder) that groups traces. Each trace belongs to one project, set by `LANGSMITH_PROJECT` or in code. Projects let you separate apps and environments, and give each its own filters, stats, monitors and access.

## 🔵 सरल परिभाषा (Hindi)
LangSmith project एक नाम वाला container (folder जैसा) है जो traces को group करता है। हर trace एक project में जाता है, जो `LANGSMITH_PROJECT` या code से तय होता है। Projects से apps और environments अलग रहते हैं, और हर एक के अपने filters, stats, monitors और access होते हैं।

---

## 🔴 Problem it Solves
- All traces from dev experiments, tests and production in one pile make dashboards meaningless.
- Cost and latency of one app cannot be separated from another.
- Developers should not browse production customer data.

## 🔴 यह क्यों बना? (Hindi)
- Dev experiments, tests और production के traces एक ढेर में हों तो dashboard बेकार हो जाते हैं।
- एक app की cost और latency दूसरे से अलग नहीं की जा सकती।
- Developers को production customer data नहीं देखना चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose a naming scheme: <app>-<env>[-<feature>]
Step 2 → Set LANGSMITH_PROJECT per process (or per call in code)
Step 3 → First trace to a new name auto-creates the project
Step 4 → Open project: filter by tags, metadata, status, latency, cost
Step 5 → Project stats: trace count, error rate, p50/p99 latency, tokens, cost
Step 6 → Add monitors/alerts and automation rules per project
Step 7 → Clean up: delete or archive old experiment projects
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Naming scheme चुनो: <app>-<env>[-<feature>]
Step 2 → हर process में LANGSMITH_PROJECT set करो (या code में per call)
Step 3 → नए नाम पर पहला trace project अपने-आप बना देता है
Step 4 → Project खोलकर tags, metadata, status, latency, cost से filter करो
Step 5 → Project stats: trace count, error rate, p50/p99 latency, tokens, cost
Step 6 → हर project पर monitors/alerts और automation rules लगाओ
Step 7 → सफ़ाई: पुराने experiment projects delete या archive करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Projects: `tariff-prod`, `tariff-staging`, `tariff-dev-aditya`, `tariff-eval-ci`. The prod project shows 12,400 traces/day, 1.2% errors, p99 latency 6s. An A/B test uses metadata `prompt=v3` vs `v4` inside the same project to compare cost per trace. CI evals write to `tariff-eval-ci`, so test traffic never pollutes prod stats.

**Zomato AI**: `search-assistant-prod` and `support-bot-prod` are separate, and the support team's access is limited to the second.

## 🟡 Real Example Hindi mein
**Tariff System**: Projects: `tariff-prod`, `tariff-staging`, `tariff-dev-aditya`, `tariff-eval-ci`। Prod project में 12,400 traces/दिन, 1.2% errors, p99 latency 6s है। A/B test में एक ही project के अंदर metadata `prompt=v3` बनाम `v4` से cost per trace compare होती है। CI evals `tariff-eval-ci` में लिखते हैं, इसलिए test traffic prod stats खराब नहीं करता।

**Zomato AI**: `search-assistant-prod` और `support-bot-prod` अलग हैं और support team को सिर्फ़ दूसरे का access है।

---

## 💻 Code Example — Basic
```python
# Basic: derive the project name from app + environment and validate it (pure Python)
import os                                                     # read env

ALLOWED_ENVS: set[str] = {"dev", "staging", "prod", "eval-ci"}  # known environments

def project_name(app: str, env: str, feature: str | None = None) -> str:
    if env not in ALLOWED_ENVS:                               # fail early on typos like "porduction"
        raise ValueError(f"unknown env {env!r}, use one of {sorted(ALLOWED_ENVS)}")
    parts = [app, env] + ([feature] if feature else [])       # build parts list
    return "-".join(p.strip().lower().replace(" ", "-") for p in parts)  # normalise

print(project_name("tariff", "prod"))                         # tariff-prod
print(project_name("Tariff", "dev", "hs lookup"))             # tariff-dev-hs-lookup
os.environ["LANGSMITH_PROJECT"] = project_name("tariff", "dev")  # LangSmith will read this
print(os.environ["LANGSMITH_PROJECT"])
```

## 💻 Code Example — Advanced
```python
# Manage projects with the LangSmith Client: list, stats, cleanup; per-call project override
# pip install langsmith
import asyncio                                                # async wrapper
import logging                                                # logs
from datetime import datetime, timedelta, timezone            # time math
from langsmith import Client, traceable, tracing_context      # SDK

log = logging.getLogger("projects")                           # logger

def list_old_projects(client: Client, prefix: str, days: int) -> list[str]:
    """Names of projects with this prefix that look unused."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)  # age limit
    old: list[str] = []                                       # results
    for p in client.list_projects(name_contains=prefix):      # iterate matching projects
        last = getattr(p, "last_run_start_time", None) or getattr(p, "start_time", None)  # last activity
        if last is not None and last.replace(tzinfo=last.tzinfo or timezone.utc) < cutoff:
            old.append(p.name)                                # candidate for cleanup
    return old

def cleanup(client: Client, names: list[str], dry_run: bool = True) -> None:
    for name in names:                                        # each candidate
        if dry_run:                                           # safe default: only report
            log.info("would delete %s", name)
            continue
        try:
            client.delete_project(project_name=name)          # irreversible!
        except Exception as exc:                              # keep going on errors
            log.warning("delete failed for %s: %s", name, type(exc).__name__)

@traceable(name="classify")
async def classify(product: str) -> str:
    await asyncio.sleep(0)
    return "8507.60"

async def run_in_project(product: str, project: str) -> str:
    # tracing_context(project_name=...) sends THIS call's trace to a different project
    with tracing_context(enabled=True, project_name=project):
        return await classify(product)

if __name__ == "__main__":
    # Needs LANGSMITH_API_KEY; guarded so the file imports safely without it:
    try:
        c = Client()
        print(list_old_projects(c, "tariff-dev", days=30))    # dry listing
    except Exception as exc:
        print("LangSmith not configured:", type(exc).__name__)
```

---

## 🟠 FastAPI Integration
Choose the project by environment at startup, and optionally send internal/test requests (header `x-test: 1`) to a separate project so they never count in prod dashboards.

```python
import os                                                     # env
from fastapi import FastAPI, Header                           # framework
from langsmith import tracing_context                         # per-call project

app = FastAPI()                                               # app
ENV = os.getenv("APP_ENV", "dev")                             # environment name

@app.get("/classify")
async def route(product: str, x_test: str | None = Header(default=None)) -> dict[str, str]:
    project = f"tariff-{'eval-ci' if x_test else ENV}"        # test traffic goes elsewhere
    with tracing_context(enabled=True, project_name=project): # applies to this request only
        answer = await classify(product)                      # traced function from above
    return {"hs_code": answer, "project": project}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain reads `LANGSMITH_PROJECT`. For one-off runs use `tracing_v2_enabled(project_name=...)`. LangSmith `evaluate()` creates an *experiment* project (prefix via `experiment_prefix`) automatically, so each evaluation run is its own project of traces.

```python
from langchain_core.tracers.context import tracing_v2_enabled # context manager

# with tracing_v2_enabled(project_name="tariff-dev-experiment-1"):
#     chain.invoke({"p": "power bank"})
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using the default project for everything.
✅ Correct: explicit names per app and environment.

```python
# Wrong
# (no LANGSMITH_PROJECT set -> "default")
# Right
os.environ["LANGSMITH_PROJECT"] = "tariff-prod"
```

❌ Mistake 2: Encoding changing data (version, user) in the project name, creating hundreds of projects.
✅ Correct: use tags/metadata for version and user.

```python
# Wrong
project = f"tariff-prod-user-{user_id}"
# Right
config = {"metadata": {"user_id": user_id, "prompt": "v4"}}
```

---

## 🧠 Tricky Interview Question
**Q**: "Prod and staging both write to the same project. What goes wrong and how do you fix it without losing history?"

**Answer**: Metrics mix (error rate and latency blend), alerts fire on staging noise, and staging testers can see prod customer data. Fix: from now on set distinct `LANGSMITH_PROJECT` per environment with separate keys. Old mixed traces cannot be split by name, but if they carry metadata or tags (e.g. `env`) you can filter them; otherwise treat the old project as archived history. Add a startup assertion that the project name contains the environment.

---

## ⚫ Interview Questions + Answers

Q1: What is a LangSmith project? (Easy)
A1: A named group of traces, used to separate apps and environments.

Q2: How is a project created? (Easy)
A2: Automatically when the first trace is sent to a new name, or explicitly with `client.create_project`.

Q3: Project vs tag vs metadata? (Medium)
A3: Project is the coarse container (app/env). Tags and metadata are fine-grained attributes inside a project (version, user, tier) used for filtering.

Q4: How do you compare two prompt versions in production? (Medium)
A4: Keep one project, add `metadata.prompt_version`, then filter and compare error rate, latency, tokens and feedback per version. Or run both as offline experiments on the same dataset.

Q5: How do you design project structure and access for a 20-service company? (Hard)
A5: Convention `<service>-<env>`; one workspace per business unit; service API keys scoped per environment; developers get read access to dev/staging only; prod read via RBAC; automation to delete stale experiment projects; monitoring per prod project with alerts to the owning team; retention shorter for dev.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- More than one app or environment
- You need separate dashboards and permissions

❌ Avoid when:
- Creating a project per user or per request (use metadata)
- Leaving everything in `default`

---

## 📊 Visual Diagram
```
 Workspace: acme-ai
 ├─ tariff-prod        12.4k traces/day  err 1.2%  p99 6s
 │    └─ metadata: prompt=v3 | v4 (A/B)
 ├─ tariff-staging
 ├─ tariff-dev-aditya
 ├─ tariff-eval-ci     (CI experiments)
 └─ support-bot-prod   (different team)
```

---

## 💰 Cost Impact
- Projects themselves are free, but every trace stored counts toward plan limits and retention. Separating test traffic makes cost reports accurate (prod tokens/cost per trace is not diluted by test runs).
- Optimise: shorter retention for dev/eval projects, delete old experiments, sample prod, and use per-project cost views to see which app spends the most tokens.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Project | Container of traces | Traces का container |
| Workspace | Group of projects/users | Projects/users का समूह |
| Experiment | Project made by an eval run | Eval run से बना project |
| Retention | How long traces are kept | Traces कब तक रखे जाएँ |
| RBAC | Role-based access control | Role के हिसाब से access |
| Naming convention | Standard name pattern | नाम रखने का मानक पैटर्न |

---

## ⚡ 3-Line Summary
English: A project groups traces; set it with `LANGSMITH_PROJECT` or `tracing_context(project_name=...)`. Use `<app>-<env>` names and keep versions/users in tags and metadata. Separate projects give clean metrics, access control and cost views.
Hindi: Project traces को group करता है; इसे `LANGSMITH_PROJECT` या `tracing_context(project_name=...)` से set करो। `<app>-<env>` नाम रखो और version/user को tags व metadata में रखो। अलग projects से साफ़ metrics, access control और cost view मिलते हैं।

---

## ➡️ Next Topic
**421. Runs in LangSmith** — the individual steps inside a project, what a run contains and how to query them.
