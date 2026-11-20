---

# 27. MCP in Production
# हिंदी में: Production में MCP
# Framework: MCP
# Already Known: No

> Verified against: `mcp` 1.30.0, `fastapi` 0.163.0, `uvicorn` 0.54.0. Ran locally with `TestClient`: a stateless Streamable HTTP MCP service mounted in FastAPI with a per-tool decorator (timeout, concurrency cap, metrics, audit log), `/health`, `/metrics`, and Host-header protection (421 for a bad host). **Not run:** Docker image build, Kubernetes manifests/HPA, a real load balancer, load tests (the millisecond numbers printed below come from a 10 ms `sleep` demo and say nothing about real performance), Prometheus/OpenTelemetry exporters, real LLM traffic. YAML/Dockerfile snippets are templates only.

---

## 🔵 Simple Definition (2-3 lines)
Running MCP in production means treating each MCP server like any other internal API: **stateless HTTP** so replicas scale horizontally, **auth and Host/Origin protection**, **timeouts and concurrency limits**, **health checks**, **metrics/logs/traces per tool**, safe **deploys** and **version pinning**. stdio is for local development; production uses HTTP.

## 🔵 सरल परिभाषा (Hindi)
Production में MCP चलाने का मतलब है हर MCP server को किसी भी internal API की तरह संभालना: **stateless HTTP** ताकि replicas horizontally scale हों, **auth और Host/Origin सुरक्षा**, **timeouts और concurrency limits**, **health checks**, **प्रति-tool metrics/logs/traces**, सुरक्षित **deploys** और **version pinning**। stdio local development के लिए है; production में HTTP चलता है।

---

## 🔴 Problem it Solves
A demo server that works on a laptop fails in production: one slow tool blocks everyone, session state lives on one replica, no one knows which tool is failing, an agent loop floods the server, and a deploy drops in-flight calls. Production practices make the server predictable, observable and safe under load.

## 🔴 यह क्यों बना? (Hindi)
Laptop पर चलने वाला demo server production में फ़ेल होता है: एक धीमा tool सबको रोक देता है, session state एक ही replica पर रहती है, कोई नहीं जानता कौन-सा tool fail हो रहा है, agent loop server को भर देता है, और deploy चल रही calls गिरा देता है। Production practices server को अनुमानित, observable और load में सुरक्षित बनाती हैं।

---

## 🟢 How it Works

```
Step 1 -> FastMCP(stateless_http=True, json_response=True): no per-session memory
Step 2 -> Mount mcp.streamable_http_app() in FastAPI; run mcp.session_manager.run() in lifespan
Step 3 -> Wrap each tool: timeout (asyncio.wait_for), concurrency cap (Semaphore), metrics, audit log
Step 4 -> /health for probes; /metrics (or Prometheus/OTel) for dashboards and alerts
Step 5 -> TransportSecuritySettings: allowed_hosts / allowed_origins (observed 421 for evil Host)
Step 6 -> Auth at gateway or in the app (note 020); secrets from env/secret store
Step 7 -> N replicas behind a load balancer; rolling deploys; pinned versions; canary
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> FastMCP(stateless_http=True, json_response=True): कोई per-session memory नहीं
Step 2 -> mcp.streamable_http_app() को FastAPI में mount करें; lifespan में mcp.session_manager.run()
Step 3 -> हर tool wrap करें: timeout (asyncio.wait_for), concurrency cap (Semaphore), metrics, audit log
Step 4 -> probes के लिए /health; dashboards और alerts के लिए /metrics (या Prometheus/OTel)
Step 5 -> TransportSecuritySettings: allowed_hosts / allowed_origins (गलत Host पर 421 देखा)
Step 6 -> Auth gateway पर या app में (note 020); secrets env/secret store से
Step 7 -> Load balancer के पीछे N replicas; rolling deploys; pinned versions; canary
```

---

## 🟡 Real World Example
**Tariff Agent platform**: 8 replicas of the tariff MCP service behind an internal load balancer serve 40 agent instances. Dashboards show calls, error rate and average latency per tool; an alert fires if `get_duty_rate` errors spike after a deploy; the semaphore stops one runaway agent loop from exhausting the database pool.

## 🟡 Real Example Hindi mein
**Tariff Agent platform**: tariff MCP service के 8 replicas internal load balancer के पीछे 40 agent instances को सेवा देते हैं। Dashboards प्रति tool calls, error rate और average latency दिखाते हैं; deploy के बाद `get_duty_rate` के errors बढ़ें तो alert बजता है; semaphore एक बेकाबू agent loop को database pool खत्म करने से रोकता है।

---

## 💻 Code Example — Basic
```python
# basic_prod.py - the smallest production-leaning server: stateless + JSON + health (ran as part of the advanced file)
import contextlib                                           # lifespan helper
from fastapi import FastAPI                                 # web app
from mcp.server.fastmcp import FastMCP                      # MCP server

mcp = FastMCP("tariff-basic", stateless_http=True, json_response=True)   # scale-friendly settings

@mcp.tool()                                                 # one tool
def get_duty_rate(hs_code: str) -> float:
    """Duty percent for an HS code."""
    return 20.0

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():                   # required, else requests fail
        yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")                                         # liveness/readiness
async def health() -> dict[str, str]:
    return {"status": "ok"}

app.mount("/tariff", mcp.streamable_http_app())            # endpoint: POST /tariff/mcp
# run: uvicorn basic_prod:app --host 0.0.0.0 --port 8000   (add auth BEFORE exposing beyond localhost)
```

## 💻 Code Example — Advanced
```python
# prod_gateway.py - stateless HTTP + per-tool timeout/concurrency/metrics + Host protection (ran via TestClient)
import asyncio, contextlib, functools, logging, time        # stdlib
from collections import defaultdict                         # metric store
from typing import Any, Awaitable, Callable                 # hints
from fastapi import FastAPI                                 # web app
from mcp.server.fastmcp import FastMCP                      # MCP server
from mcp.server.transport_security import TransportSecuritySettings   # Host/Origin allow-list

log = logging.getLogger("tariff.prod")                      # structured logs go here
METRICS: dict[str, dict[str, float]] = defaultdict(lambda: {"calls": 0, "errors": 0, "total_ms": 0.0})
LIMIT = asyncio.Semaphore(20)                               # max concurrent tool executions per replica

mcp = FastMCP("tariff-prod", stateless_http=True, json_response=True,
    transport_security=TransportSecuritySettings(           # list the hostnames your gateway really uses
        enable_dns_rebinding_protection=True,
        allowed_hosts=["localhost:8000", "tariff.internal"],
        allowed_origins=["https://tariff.internal"]))

def instrumented(fn: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    """Wrap a tool: timeout, concurrency cap, latency/error metrics, audit log."""
    @functools.wraps(fn)                                    # keep name/signature -> schema stays correct
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        name, t0 = fn.__name__, time.perf_counter()
        m = METRICS[name]
        m["calls"] += 1
        try:
            async with LIMIT:                               # back-pressure instead of overload
                return await asyncio.wait_for(fn(*args, **kwargs), timeout=5.0)   # never hang forever
        except Exception:
            m["errors"] += 1                                # count failures (timeouts included)
            log.exception("tool %s failed", name)           # stack trace goes to logs, not to the model
            raise
        finally:
            m["total_ms"] += (time.perf_counter() - t0) * 1000
    return wrapper

@mcp.tool()
@instrumented
async def get_duty_rate(hs_code: str) -> float:             # typed tool
    """Duty percent for an HS code."""
    if not hs_code.replace(".", "").isdigit():
        raise ValueError("hs_code must look like 6109.10")
    await asyncio.sleep(0.01)                               # pretend DB call
    return 20.0

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():                   # start MCP task group; stops on shutdown
        yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")                                         # liveness/readiness probe
async def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/metrics")                                        # swap for prometheus_client in real life
async def metrics() -> dict[str, dict[str, float]]:
    return {k: {**v, "avg_ms": round(v["total_ms"] / v["calls"], 2) if v["calls"] else 0.0} for k, v in METRICS.items()}

app.mount("/tariff", mcp.streamable_http_app())            # POST /tariff/mcp
```
Observed with `TestClient(app, base_url="http://localhost:8000")`: `/health` -> `{'status': 'ok'}`; `tools/call get_duty_rate "6109.10"` -> `structuredContent {'result': 20.0}`; `"abc"` -> `isError=True` (stack trace logged server-side only); `/metrics` -> `{'get_duty_rate': {'calls': 2.0, 'errors': 1.0, 'total_ms': ~12, 'avg_ms': ~6}}` (demo numbers); a request with `Host: evil.com` -> `421`. In this stateless mode `tools/call` worked without a prior `initialize` call. Token usage: production controls do not change LLM tokens; error messages and tool outputs do, so keep both small. Async: timeout via `asyncio.wait_for`.

```text
# Dockerfile + deployment sketch - TEMPLATE ONLY, NOT built or run
# FROM python:3.13-slim ; COPY . /app ; RUN pip install -r requirements.txt   (pin exact versions)
# CMD ["uvicorn", "prod_gateway:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
# K8s: Deployment (replicas >= 2), readinessProbe GET /health, resource requests/limits,
#      HPA on CPU or request rate, PodDisruptionBudget, terminationGracePeriodSeconds > longest tool timeout
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Connect to remote prod server | `streamable_http` connection (verified key set) | verify docs | `MCPServerStreamableHttp` with retries params (verified) | verify |
| Client-side retries | `tool_interceptors` | verify | `max_retry_attempts`, `retry_backoff_seconds_base` (verified) | verify |
| Client timeouts | session/connection `timeout` key | verify | `client_session_timeout_seconds`, `params["timeout"]` (verified) | verify |
| Tracing | LangSmith (not run) | verify | SDK tracing (MCP calls traced; not run here) | verify |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Stateful sessions behind a round-robin balancer.
✅ Correct: `stateless_http=True` (state in Redis/DB), or sticky sessions.

❌ Mistake 2: No timeout on tool bodies.
✅ Correct: `asyncio.wait_for` + client timeouts; one hung dependency must not stall the fleet.

❌ Mistake 3: Heavy init inside the MCP `lifespan` with stateless mode.
✅ Correct: Observed per-request lifespan runs in stateless mode (note 025); create pools in the web app lifespan.

❌ Mistake 4: Logging full tool arguments/outputs containing PII.
✅ Correct: Log tool name, caller id, latency, status; redact arguments.

---

## 🧠 Tricky Interview Question
"After scaling the MCP service from 1 to 4 replicas, agents randomly get 'session not found' errors. Why, and what are the trade-offs of the fix?"

Answer: In stateful mode the `Mcp-Session-Id` is known only to the replica that created it; a round-robin balancer sends the next request elsewhere. Fixes: (a) stateless mode - simplest to scale, but you lose server-held session state and features needing server-initiated requests (sampling, some notifications); store state externally; (b) sticky routing on the session header - keeps features but complicates scaling and rolling deploys; (c) a shared session store if the SDK/gateway supports it (verify). Also mention graceful shutdown so in-flight calls finish.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Which transport for production?
A1: Streamable HTTP (stateless where possible); stdio is local-only.

Q2: [Medium] What do you monitor per tool?
A2: Call count, error rate, latency percentiles, timeouts, and caller identity; plus saturation (concurrency/semaphore waits).

Q3: [Hard] How do you stop an agent loop from overloading the server?
A3: Per-client rate limits at the gateway, a concurrency semaphore in the app, client-side `max_turns`, and circuit breakers.

Q4: [Hard] How do you deploy without breaking in-flight calls?
A4: Rolling update with readiness probes, graceful termination longer than the max tool timeout, backward-compatible schemas, canary first.

Q5: [System Design] 2,000 req/s of tariff lookups across many agents.
A5: Stateless replicas with HPA, cached rate table, DB connection pooling and read replicas, L7 balancer, auth at the edge, per-tenant quotas, tracing with trace ids propagated from the agent, dashboards and SLO alerts (design guidance; not load-tested here).

---

## 💰 Cost Impact
LLM cost is unchanged by deployment choices, but wasted turns cost money: slow or flaky tools cause retries and extra model calls (each re-sends the tool schemas). Infra: stateless replicas autoscale; caching hot lookups cuts compute and latency. Track cost per request by combining model `usage` with tool metrics. Instance prices vary by provider - not quoted here.

---

## 🔷 When to Use
✅ Use these practices when:
- Multiple agents/users depend on the server, or it touches business data

❌ Skip when:
- A single-user local tool over stdio

---

## 📊 Visual Diagram
```
 Agents --HTTPS--> [LB / API gateway: auth, rate limit]
                     |--> replica 1 --+
                     |--> replica 2 --+--> [FastAPI]
                     '--> replica N --+      |-- /health  /metrics
                                             '-- /tariff/mcp -> instrumented tools
                                                      |-> DB pool (read-only), cache
 metrics/logs/traces --> dashboards + alerts
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Stateless HTTP | Any replica can serve any request | कोई भी replica कोई भी request संभाले |
| Back-pressure | Limiting concurrent work | एक साथ चलने वाला काम सीमित करना |
| Readiness probe | Tells LB when to send traffic | LB को बताता है कब traffic भेजना है |
| Canary | Small-traffic rollout | थोड़े traffic पर नया version |
| SLO | Target reliability level | भरोसे का लक्ष्य |

---

## ⚡ 3-Line Summary
English: Production MCP is stateless HTTP with auth, Host protection, timeouts, concurrency limits and per-tool metrics. Scale replicas, deploy gradually, and pin versions. Keep logs useful but free of secrets and PII.
Hindi: Production MCP यानी stateless HTTP, साथ में auth, Host सुरक्षा, timeouts, concurrency limits और प्रति-tool metrics। Replicas scale करें, धीरे-धीरे deploy करें और versions pin करें। Logs उपयोगी रखें पर secrets और PII से मुक्त।

---

## ➡️ Next Topic
**028. MCP vs LangChain Tools** - when a protocol server is worth it versus plain in-process tools.

---
