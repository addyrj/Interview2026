---

# 449. Python Production Checklist
# हिंदी में: Python Production Checklist (live जाने से पहले की जाँच-सूची)

---

## 🔵 Simple Definition (English)
A production checklist is a list of things to verify before real users touch your Python service: config, secrets, logging, error handling, security, performance limits, health checks, monitoring and rollback. It turns "it works on my laptop" into "it will survive Monday morning traffic".

## 🔵 सरल परिभाषा (Hindi)
Production checklist उन चीज़ों की सूची है जिन्हें असली users के आने से पहले जाँचना होता है: config, secrets, logging, error handling, security, performance limits, health checks, monitoring और rollback। यह "मेरे laptop पर चल रहा है" को "सोमवार सुबह के traffic में भी चलेगा" में बदलती है।

---

## 🔴 Problem it Solves
Most outages are not clever bugs; they are forgotten basics: `DEBUG=True` in prod, no timeout on an HTTP call, logs that nobody can search, a database with no backup, one worker process for the whole app. A checklist makes those basics repeatable and reviewable.

## 🔴 यह क्यों बना? (Hindi)
ज़्यादातर outage कोई मुश्किल bug नहीं होते, बल्कि भूली हुई बुनियादी बातें होती हैं: prod में `DEBUG=True`, HTTP call पर timeout नहीं, ऐसे logs जिन्हें कोई search नहीं कर सकता, बिना backup का database, पूरे app के लिए सिर्फ़ एक worker। Checklist इन बातों को दोहराने योग्य और review करने योग्य बनाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Config: all settings from env vars, validated at startup, no secrets in Git
Step 2 → Code quality: type checks, tests, lint pass in CI; dependencies pinned
Step 3 → Runtime: gunicorn + uvicorn workers, non-root user, graceful shutdown
Step 4 → Reliability: timeouts, retries with backoff, DB pool limits, rate limits
Step 5 → Observability: structured JSON logs, metrics, error tracking, request IDs
Step 6 → Security: HTTPS, strict CORS, input validation, no debug, dependency audit
Step 7 → Operations: /health/live + /health/ready, backups, rollback plan, runbook
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Config: सब settings env vars से, startup पर validate, Git में secrets नहीं
Step 2 → Code quality: CI में type check, tests, lint पास; dependencies pinned
Step 3 → Runtime: gunicorn + uvicorn workers, non-root user, graceful shutdown
Step 4 → Reliability: timeouts, backoff के साथ retries, DB pool limits, rate limits
Step 5 → Observability: structured JSON logs, metrics, error tracking, request IDs
Step 6 → Security: HTTPS, सख्त CORS, input validation, debug बंद, dependency audit
Step 7 → Operations: /health/live + /health/ready, backups, rollback plan, runbook
```

---

## 🟡 Real World Example
Before launching a UPI-style payments API, a team runs the checklist: secrets come from AWS Secrets Manager, logs go to CloudWatch as JSON with a `request_id`, every outgoing call to the bank has a 5-second timeout, the DB pool is capped at 20 per worker, and `/health/ready` gates the load balancer. The first week a bank API slows down and the timeouts and circuit-breaker keep the rest of the service alive.

## 🟡 Real Example Hindi mein
UPI जैसी payments API launch करने से पहले team checklist चलाती है: secrets AWS Secrets Manager से आते हैं, logs `request_id` के साथ JSON में CloudWatch जाते हैं, bank को हर outgoing call पर 5 सेकंड का timeout है, DB pool हर worker पर 20 तक सीमित है, और `/health/ready` load balancer को गेट करता है। पहले हफ़्ते में bank API धीमी पड़ी, तब timeouts और circuit-breaker ने बाकी service को ज़िंदा रखा।

---

## 💻 Code Example — Basic
```python
# Basic: a startup "preflight" that refuses to boot with unsafe production config
from typing import List, Mapping  # type hints

REQUIRED: tuple[str, ...] = ("APP_SECRET_KEY", "APP_DATABASE_URL")  # must exist


def preflight(env: Mapping[str, str]) -> List[str]:
    """Return a list of problems; empty list means safe to start."""
    problems: List[str] = [f"missing {k}" for k in REQUIRED if not env.get(k)]  # absent variables
    if env.get("APP_ENV") == "prod":  # extra rules only for production
        if env.get("APP_DEBUG", "false").lower() == "true":  # debug leaks internals
            problems.append("debug must be off in prod")
        if "*" in env.get("APP_CORS_ORIGINS", ""):  # any website could call the API
            problems.append("wildcard CORS in prod")
        if len(env.get("APP_SECRET_KEY", "")) < 32:  # weak signing key
            problems.append("secret key shorter than 32 chars")
    return problems  # caller decides to exit


print(preflight({"APP_ENV": "prod", "APP_DEBUG": "true", "APP_CORS_ORIGINS": "*", "APP_SECRET_KEY": "short"}))
# Output: ['missing APP_DATABASE_URL', 'debug must be off in prod', 'wildcard CORS in prod', 'secret key shorter than 32 chars']
print(preflight({"APP_ENV": "prod", "APP_SECRET_KEY": "k" * 40, "APP_DATABASE_URL": "postgresql://u@h/db"}))
# Output: []
```

## 💻 Code Example — Advanced
```python
# Production: structured JSON logging (standard library only)
import json  # to build one JSON object per log line
import logging  # standard logging
import logging.config  # dictConfig
from typing import Any, Dict  # type hints


class JsonFormatter(logging.Formatter):
    """Turn each LogRecord into one JSON line that log tools can search."""

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {  # fixed fields
            "level": record.levelname,  # INFO / ERROR
            "logger": record.name,  # which module
            "msg": record.getMessage(),  # message with args applied
        }
        if record.exc_info:  # an exception is attached
            payload["exc"] = self.formatException(record.exc_info).splitlines()[-1]  # last line only
        return json.dumps(payload)  # one line, easy to parse


logging.config.dictConfig({  # configure once at startup
    "version": 1,
    "disable_existing_loggers": False,  # keep uvicorn/sqlalchemy loggers alive
    "formatters": {"json": {"()": JsonFormatter}},  # "()" = custom class
    "handlers": {"out": {"class": "logging.StreamHandler", "stream": "ext://sys.stdout", "formatter": "json"}},
    "root": {"level": "INFO", "handlers": ["out"]},  # log to stdout (Docker/K8s collect it)
})
log: logging.Logger = logging.getLogger("orders")  # module logger
log.info("order created id=%s", 42)  # lazy %-formatting
# Output: {"level": "INFO", "logger": "orders", "msg": "order created id=42"}
try:  # show exception logging
    1 / 0  # raises ZeroDivisionError
except ZeroDivisionError:
    log.exception("payment failed")  # logs at ERROR with traceback info
# Output: {"level": "ERROR", "logger": "orders", "msg": "payment failed", "exc": "ZeroDivisionError: division by zero"}
```

Run command reference (not run here, needs a server): `gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 --timeout 30 --graceful-timeout 30 --bind 0.0.0.0:8000`. Both code blocks above were run on Python 3.13.3 and the outputs are real.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python production run
# gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4
# pip-audit            # dependency vulnerabilities
# logging.config.dictConfig(...)   # structured logs
```
```javascript
// Node production run
// pm2 start app.js -i max          // cluster mode, multiple processes
// npm audit                        // dependency vulnerabilities
// pino()                           // structured JSON logger
```

Key differences: Node is single-threaded but clusters with PM2, Python needs multiple worker processes because of the GIL; both need the same checklist items. `pip-audit` is the Python counterpart of `npm audit`; `pip freeze`/lock files (`uv.lock`, `poetry.lock`) correspond to `package-lock.json`.

---

## 🟠 FastAPI Connection
Wire the checklist into the app: docs off in prod, restricted CORS, request-ID middleware and a global exception handler that does not leak stack traces.

```python
# FastAPI production hardening (pip install fastapi)
import logging  # logging
import uuid  # request ids
from typing import Awaitable, Callable  # types

from fastapi import FastAPI, Request, Response  # framework
from fastapi.middleware.cors import CORSMiddleware  # CORS
from fastapi.responses import JSONResponse  # error body

IS_PROD: bool = True  # in real code: settings.env == "prod"
log: logging.Logger = logging.getLogger("api")  # logger

app: FastAPI = FastAPI(docs_url=None if IS_PROD else "/docs", redoc_url=None)  # hide docs in prod
app.add_middleware(CORSMiddleware, allow_origins=["https://app.example.com"], allow_methods=["GET", "POST"])  # strict CORS


@app.middleware("http")  # runs for every request
async def request_id(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    rid: str = request.headers.get("x-request-id", uuid.uuid4().hex)  # reuse or create
    response: Response = await call_next(request)  # run the endpoint
    response.headers["x-request-id"] = rid  # return it so support can trace
    return response


@app.exception_handler(Exception)  # last-resort handler
async def unhandled(request: Request, exc: Exception) -> JSONResponse:
    log.exception("unhandled error on %s", request.url.path)  # details go to logs
    return JSONResponse({"detail": "Internal Server Error"}, status_code=500)  # nothing leaks to the client
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No timeout on outgoing calls
✅ Correct: always set one; the default for `requests` is "wait forever".

```python
# Wrong
# requests.get("https://bank.example/api")          # can hang a worker forever
# Right
# requests.get("https://bank.example/api", timeout=5)
# httpx.AsyncClient(timeout=5.0)
```

❌ Mistake 2: Running as root / with `--reload` / with one worker in production
✅ Correct: non-root `USER` in the Dockerfile, no `--reload`, several workers (roughly 2 x CPU + 1 for sync, or CPU count for async), and a process manager restart policy.

❌ Mistake 3: `print()` debugging and `except: pass`
✅ Correct: use `logging` with levels; catch specific exceptions and log them with `log.exception`.

```python
# Wrong
try:
    risky()
except:
    pass          # error silently swallowed
# Right
try:
    risky()
except ValueError:
    log.exception("risky failed")   # visible and searchable
    raise
```

---

## 🧠 Tricky Interview Question

**Q**: Your FastAPI app is fast on one worker but returns random 401 errors after you scale to 4 workers. What is likely wrong?

```python
# Each worker is a separate process with its OWN memory
SESSIONS: dict[str, str] = {}   # module-level "session store"
```

**Answer**: State stored in process memory (dict, in-process cache, in-memory rate-limit counters) is not shared between workers or between containers. A login handled by worker 1 is unknown to worker 2, so requests land on a worker without the session. The fix: stateless auth (JWT) or a shared store like Redis/the database. The same applies to rate limits, caches and scheduled jobs that would otherwise run 4 times.

---

## ⚫ Interview Questions + Answers

Q1: What are the first things you check before deploying a Python API?
A1: Config and secrets from the environment, debug off, tests/lint/types green, pinned dependencies, DB migrations applied, health endpoints, logging/monitoring, backups, and a rollback plan.

Q2: How many gunicorn workers should you run?
A2: A common starting point is `(2 x CPU cores) + 1` for sync workers; for `UvicornWorker` (async) start near the core count and load-test. Memory per worker and DB connection limits cap the number.

Q3: Why log to stdout in containers?
A3: The platform (Docker, Kubernetes, systemd) collects stdout and ships it. Writing files inside a container needs rotation and is lost when the container dies.

Q4: What is graceful shutdown?
A4: On SIGTERM the server stops accepting new requests, finishes in-flight ones, closes DB pools, and then exits within a timeout. Otherwise deploys cut customer requests in half.

Q5: How do you handle dependency security?
A5: Pin versions with a lock file, run `pip-audit` in CI, enable Dependabot/Renovate, build from a slim base image and rebuild regularly.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Before every first launch and major release
- As a PR template or CI step so it is not forgotten
- After an incident, to add the missed item

❌ Avoid when:
- Treating it as paperwork that nobody verifies (automate checks instead)
- Over-engineering a hobby script (scale the list to the risk)
- Copying a generic list without adapting it to your own architecture

---

## 📊 Visual Diagram

```
        ┌──────────── Production Readiness ────────────┐
        │ Config ─ Secrets ─ Validation (preflight)    │
        │ Runtime: gunicorn + uvicorn workers, non-root│
        │ Reliability: timeouts, retries, pools, limits│
        │ Observability: JSON logs, metrics, Sentry    │
        │ Security: HTTPS, CORS, no debug, pip-audit   │
        │ Ops: /health/*, backups, rollback, runbook   │
        └──────────────────────┬───────────────────────┘
                               ▼
                    all green? ──► deploy
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Preflight check | Validate config before start | start से पहले config जाँच |
| Structured logging | Logs as JSON fields | JSON fields वाले logs |
| Graceful shutdown | Finish work, then exit | काम पूरा करके बंद होना |
| Timeout | Maximum wait time | अधिकतम इंतज़ार का समय |
| Request ID | Unique id per request | हर request की unique id |
| Rollback | Return to previous version | पिछले version पर लौटना |

---

## ⚡ 3-Line Summary
English: A production checklist covers config, runtime, reliability, observability, security and operations. Automate it with a startup preflight and CI checks. Remember that worker processes do not share memory.
Hindi: Production checklist में config, runtime, reliability, observability, security और operations आते हैं। इसे startup preflight और CI checks से automate करें। याद रखें कि worker processes memory share नहीं करते।

---

## ➡️ Next Topic
**450. Health Checks in FastAPI** — build `/health/live` and `/health/ready` endpoints that load balancers can trust.
