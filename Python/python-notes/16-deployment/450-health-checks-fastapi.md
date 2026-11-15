---

# 450. Health Checks in FastAPI
# हिंदी में: FastAPI में Health Checks (service ज़िंदा और तैयार है या नहीं)

---

## 🔵 Simple Definition (English)
A health check is a small endpoint that tells a platform "is this service alive?" (liveness) and "can it serve traffic right now?" (readiness). Load balancers, Docker and Kubernetes call it every few seconds and restart or stop routing to unhealthy instances.

## 🔵 सरल परिभाषा (Hindi)
Health check एक छोटा endpoint है जो platform को बताता है "service ज़िंदा है?" (liveness) और "अभी traffic ले सकती है?" (readiness)। Load balancer, Docker और Kubernetes इसे हर कुछ सेकंड में call करते हैं और unhealthy instance को restart करते हैं या उसे traffic देना बंद कर देते हैं।

---

## 🔴 Problem it Solves
A process can be running yet useless: the DB connection is dead, the app is deadlocked, or it is still warming up. Without a health check the load balancer keeps sending users to it and they see errors. With one, broken instances are removed automatically and deploys switch traffic only when the new version is ready.

## 🔴 यह क्यों बना? (Hindi)
Process चल रहा हो फिर भी बेकार हो सकता है: DB connection टूटा है, app अटक गई है, या अभी warm-up हो रहा है। Health check के बिना load balancer users को वहीं भेजता रहता है और उन्हें errors दिखते हैं। Health check होने पर खराब instances अपने-आप हट जाते हैं और deploy में traffic तभी बदलता है जब नया version तैयार हो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Platform calls GET /health/live every N seconds (liveness probe)
Step 2 → App answers 200 immediately, with NO dependency calls
Step 3 → If liveness keeps failing, platform restarts the container
Step 4 → Platform also calls GET /health/ready (readiness probe)
Step 5 → App pings DB, cache and others in parallel, each with a timeout
Step 6 → All ok -> 200; any failure -> 503, load balancer stops sending traffic
Step 7 → On shutdown the app flips to 503 first (draining), then exits
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Platform हर N सेकंड में GET /health/live call करता है (liveness probe)
Step 2 → App तुरंत 200 देता है, किसी dependency को छुए बिना
Step 3 → Liveness लगातार fail हो तो platform container restart करता है
Step 4 → Platform GET /health/ready (readiness probe) भी call करता है
Step 5 → App, DB और cache को parallel में ping करता है, हर एक पर timeout के साथ
Step 6 → सब ठीक -> 200; कोई fail -> 503, load balancer traffic भेजना बंद कर देता है
Step 7 → Shutdown पर app पहले 503 देता है (draining), फिर exit करता है
```

---

## 🟡 Real World Example
A Zomato-style order service runs 6 pods behind a load balancer. One pod loses its Redis connection; `/health/ready` returns 503 for it, so traffic goes to the other 5 and users never notice. During a deploy the new pod only gets traffic after its readiness check is green. Kubernetes uses the liveness probe to restart a pod stuck in a deadlock.

## 🟡 Real Example Hindi mein
Zomato जैसी order service के 6 pods load balancer के पीछे चलते हैं। एक pod का Redis connection टूट गया; उसका `/health/ready` 503 देता है, इसलिए traffic बाकी 5 पर चला जाता है और users को पता भी नहीं चलता। Deploy में नए pod को traffic तभी मिलता है जब उसका readiness check हरा हो। Deadlock में फँसे pod को Kubernetes liveness probe से restart करता है।

---

## 💻 Code Example — Basic
```python
# Basic: the smallest useful health endpoint (pip install fastapi httpx)
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # in-process test client

app: FastAPI = FastAPI()  # create app


@app.get("/health")  # GET /health
def health() -> dict[str, str]:  # typed response
    return {"status": "ok"}  # 200 means "process is up"


client: TestClient = TestClient(app)  # no real server needed
res = client.get("/health")  # call the endpoint
print(res.status_code, res.json())  # show result
# Output: 200 {'status': 'ok'}
```

## 💻 Code Example — Advanced
```python
# Production: separate liveness and readiness, parallel dependency checks with timeouts
import asyncio  # run checks concurrently
import time  # measure latency
from typing import Awaitable, Callable, Dict, List  # type hints

from fastapi import FastAPI, Response, status  # framework pieces

app: FastAPI = FastAPI()  # create the app
STATE: Dict[str, bool] = {"db_up": True, "shutting_down": False}  # fake infra flags for the demo


async def check_db() -> None:
    """Pretend DB ping (in real code: await session.execute(text('SELECT 1')))."""
    await asyncio.sleep(0.01)  # simulate network time
    if not STATE["db_up"]:  # database is down
        raise ConnectionError("db unreachable")  # signal failure


async def check_cache() -> None:
    """Pretend Redis ping (in real code: await redis.ping())."""
    await asyncio.sleep(0.01)  # simulate network time


CHECKS: Dict[str, Callable[[], Awaitable[None]]] = {"db": check_db, "cache": check_cache}  # registry


async def run_check(name: str, fn: Callable[[], Awaitable[None]]) -> Dict[str, str]:
    """Run one check with a timeout so a slow dependency cannot hang the probe."""
    start: float = time.perf_counter()  # start timer
    try:
        await asyncio.wait_for(fn(), timeout=1.0)  # 1 second budget
        status_text: str = "ok"  # success
    except Exception as exc:  # any failure or timeout
        status_text = f"fail: {type(exc).__name__}"  # short reason, never the connection string
    ms: float = round((time.perf_counter() - start) * 1000, 1)  # latency in ms
    return {"name": name, "status": status_text, "ms": str(ms)}  # one result row


@app.get("/health/live")  # liveness: is the process alive?
async def live() -> Dict[str, str]:
    return {"status": "alive"}  # no dependencies on purpose


@app.get("/health/ready")  # readiness: can it serve traffic?
async def ready(response: Response) -> Dict[str, object]:
    if STATE["shutting_down"]:  # draining: ask for no new traffic
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "draining"}
    rows: List[Dict[str, str]] = await asyncio.gather(*(run_check(n, f) for n, f in CHECKS.items()))  # parallel
    healthy: bool = all(r["status"] == "ok" for r in rows)  # everything ok?
    if not healthy:  # tell the load balancer
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "ready" if healthy else "unready",
            "checks": [{"name": r["name"], "status": r["status"]} for r in rows]}


if __name__ == "__main__":  # demo with the in-process client
    from fastapi.testclient import TestClient
    c = TestClient(app)
    r = c.get("/health/live"); print(r.status_code, r.json())
    # Output: 200 {'status': 'alive'}
    r = c.get("/health/ready"); print(r.status_code, r.json())
    # Output: 200 {'status': 'ready', 'checks': [{'name': 'db', 'status': 'ok'}, {'name': 'cache', 'status': 'ok'}]}
    STATE["db_up"] = False  # simulate a DB outage
    r = c.get("/health/ready"); print(r.status_code, r.json())
    # Output: 503 {'status': 'unready', 'checks': [{'name': 'db', 'status': 'fail: ConnectionError'}, {'name': 'cache', 'status': 'ok'}]}
    STATE["db_up"] = True; STATE["shutting_down"] = True  # simulate SIGTERM draining
    r = c.get("/health/ready"); print(r.status_code, r.json())
    # Output: 503 {'status': 'draining'}
```

Verified by running with FastAPI 0.162 / Python 3.13.3 (a harmless Starlette deprecation warning about httpx may print; latency fields vary per run and are excluded from the response above).

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (FastAPI)
@app.get("/health/live")
async def live() -> dict[str, str]:
    return {"status": "alive"}
```
```javascript
// JavaScript (Express)
app.get("/health/live", (req, res) => res.json({ status: "alive" }));
// NestJS: @nestjs/terminus HealthCheckService does the DB/cache checks
```

Key differences: the idea is identical (probe URL plus 200/503). FastAPI uses `Response.status_code` or `JSONResponse` for the 503; Express uses `res.status(503)`. Node has the `terminus` package; in Python you write small checks like the ones above or use `fastapi-health`.

---

## 🟠 FastAPI Connection
The probes are wired in the Dockerfile or the orchestrator, calling the same endpoints.

```python
# Docker HEALTHCHECK and Kubernetes probes call these routes (config files, not run here):
#
# Dockerfile:
#   HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
#     CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health/live', timeout=2).status==200 else 1)"
#
# Kubernetes (deployment.yaml):
#   livenessProbe:  { httpGet: { path: /health/live,  port: 8000 }, periodSeconds: 10 }
#   readinessProbe: { httpGet: { path: /health/ready, port: 8000 }, periodSeconds: 5 }
#
# Python-side: lifespan flips STATE["shutting_down"] = True when the app receives SIGTERM.
from contextlib import asynccontextmanager  # lifespan helper
from typing import AsyncIterator  # type

from fastapi import FastAPI  # framework

STATE: dict[str, bool] = {"shutting_down": False}  # shared flag


@asynccontextmanager  # startup/shutdown in one function
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield  # app serves requests here
    STATE["shutting_down"] = True  # runs at shutdown: readiness now returns 503


app: FastAPI = FastAPI(lifespan=lifespan)  # attach lifespan
```

Not run: the Dockerfile and Kubernetes snippets (no Docker/Kubernetes here). The Python parts above were run.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Liveness checks the database
✅ Correct: liveness must not depend on anything external, otherwise a DB outage makes Kubernetes restart every healthy pod and turns a small incident into a big one.

```python
# Wrong
@app.get("/health/live")
async def live():
    await db.execute("SELECT 1")   # DB down -> all pods restarted
# Right
@app.get("/health/live")
async def live():
    return {"status": "alive"}
```

❌ Mistake 2: Returning HTTP 200 with `{"status": "down"}`
✅ Correct: probes look at the status code. Return 503 when unhealthy.

❌ Mistake 3: Slow, unbounded checks (no timeout) or leaking secrets in the response
✅ Correct: use `asyncio.wait_for`, run checks in parallel, and report only names and "ok/fail", never connection strings or stack traces.

---

## 🧠 Tricky Interview Question

**Q**: What does this return, and why is it a bug in a health check?

```python
import time
from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
async def health():
    time.sleep(5)          # pretend "check the DB" with a blocking driver
    return {"status": "ok"}
```

**Answer**: It returns `{"status": "ok"}` after 5 seconds, but `time.sleep` blocks the whole event loop because the function is `async def`. During those 5 seconds the single-threaded loop of that worker serves no other request, so probes every 5 seconds can keep the worker busy and real traffic times out. Use `await asyncio.sleep` / an async driver, or declare the endpoint with plain `def` so FastAPI runs it in a thread pool.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between liveness, readiness and startup probes?
A1: Liveness = should the container be restarted? Readiness = should it receive traffic right now? Startup = give slow-booting apps time before liveness begins. Liveness is cheap and internal; readiness checks dependencies.

Q2: Why return 503 and not 500?
A2: 503 Service Unavailable means a temporary condition where the instance should not receive traffic; load balancers and probes treat any non-2xx as failing, but 503 communicates intent and may include `Retry-After`.

Q3: Should the health endpoint be authenticated?
A3: Usually no for liveness (probes cannot easily send tokens), but keep it minimal and expose nothing sensitive. Detailed diagnostics belong on an internal-only or authenticated route.

Q4: How do you handle a slow dependency in a readiness check?
A4: Wrap it in a timeout, run checks concurrently, and optionally cache results for a few seconds so a flood of probes does not overload the dependency.

Q5: How do health checks support zero-downtime deploys?
A5: The new version starts, becomes ready, then receives traffic. The old version flips to "draining" (503 on readiness), finishes in-flight requests and exits. Traffic always has a ready target.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running behind a load balancer, Docker restart policy or Kubernetes
- You deploy often and want zero-downtime releases
- You depend on a DB, cache or queue that can fail independently

❌ Avoid when:
- You check every third-party API in readiness (a vendor outage should not take you offline; degrade gracefully instead)
- You put heavy queries in the probe
- The check returns 200 always (a false sense of safety)

---

## 📊 Visual Diagram

```
 Load Balancer / Kubernetes
        │ every 5-10s
        ├──► GET /health/live  ──► 200 always (process alive)  ──► fail x3 → RESTART
        └──► GET /health/ready ──► ping DB ─┐
                                    ping Redis ├─ all ok → 200 → route traffic
                                               └─ any fail → 503 → remove from pool
 SIGTERM ──► readiness = 503 (draining) ──► finish requests ──► exit
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Liveness probe | Is the process alive? | process ज़िंदा है? |
| Readiness probe | Can it take traffic? | traffic ले सकता है? |
| 503 | Service unavailable | service अभी उपलब्ध नहीं |
| Draining | Finish work, take no new work | नया काम बंद, पुराना पूरा |
| Probe | Periodic automatic check | नियमित स्वचालित जाँच |
| Zero-downtime deploy | Release without user impact | बिना रुकावट release |

---

## ⚡ 3-Line Summary
English: Expose `/health/live` (cheap, no dependencies) and `/health/ready` (checks DB/cache with timeouts, returns 503 when unhealthy). Platforms use them to restart or route traffic. Flip readiness to 503 on shutdown for graceful draining.
Hindi: `/health/live` (सस्ता, बिना dependency) और `/health/ready` (timeout के साथ DB/cache जाँच, unhealthy पर 503) बनाएँ। Platform इनसे restart या traffic routing तय करता है। Shutdown पर readiness को 503 कर दें ताकि draining ठीक से हो।

---

## ➡️ Next Topic
**451. Coding Problems (Reverse String and more)** — start the interview problems section; next up in this set is 452. Check Palindrome.
