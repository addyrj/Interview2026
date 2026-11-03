---

# 557. Health Checks for AI
# हिंदी में: AI के लिए Health Checks

---

## 🔵 Simple Definition (English)
A health check is a small endpoint (like `/health`) that tells a load balancer or orchestrator whether your app is alive and ready for traffic. For AI apps, "ready" also means the vector DB, cache and model client are reachable, and the model/index finished loading.

## 🔵 सरल परिभाषा (Hindi)
Health check एक छोटा endpoint (जैसे `/health`) है जो load balancer या orchestrator को बताता है कि app जिंदा है और traffic के लिए तैयार है। AI app में "ready" का मतलब यह भी है कि vector DB, cache और model client पहुँच में हैं और model/index load हो चुका है।

---

## 🔴 Problem it Solves
Without checks, a crashed or still-loading instance keeps receiving traffic, and users see 502 errors. A naive check ("port 8000 open") passes even when Qdrant is down. But a deep check that calls the LLM on every probe wastes money and can itself overload the app.

## 🔴 यह क्यों बना? (Hindi)
Checks के बिना crash हुआ या अभी load हो रहा instance traffic लेता रहता है और users को 502 मिलता है। सिर्फ "port खुला है" वाला check Qdrant बंद होने पर भी pass हो जाता है। और हर probe पर LLM call करना पैसा बर्बाद करता है और app को overload कर सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Liveness  (/health/live): process is up? cheap, no dependencies
Step 2 → Readiness (/health/ready): deps OK? vector DB ping, Redis ping, model loaded
Step 3 → Startup probe: give slow model/index loading extra time before liveness starts
Step 4 → Load balancer calls the endpoint every N seconds
Step 5 → Fail threshold reached (e.g. 3 fails) → instance removed from rotation
Step 6 → Liveness fail → orchestrator restarts the container
Step 7 → Never call the paid LLM in the probe; use cached/lightweight dependency checks
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Liveness: process चालू है? सस्ता, कोई dependency नहीं
Step 2 → Readiness: dependencies ठीक? vector DB, Redis ping, model loaded
Step 3 → Startup probe: धीमे model load के लिए अतिरिक्त समय
Step 4 → Load balancer हर N सेकंड endpoint call करता है
Step 5 → Fail limit (जैसे 3) पार → instance rotation से बाहर
Step 6 → Liveness fail → container restart
Step 7 → Probe में paid LLM कभी call न करें
```

---

## 🟡 Real World Example
**Tariff Classification System**: On boot the API loads an HS-code embedding index (takes ~40 s). `/health/live` returns 200 immediately; `/health/ready` returns 503 until the index is loaded and Qdrant answers. The ALB only routes to ready instances, so deployments cause no errors.

**Amazon-style**: A product-search service marks itself unready when its recommendation cache is cold, so traffic goes to warm instances.

## 🟡 Real Example Hindi mein
**Tariff System**: Boot पर API HS-code embedding index load करती है (~40 सेकंड)। `/health/live` तुरंत 200 देता है; `/health/ready` तब तक 503 देता है जब तक index load न हो और Qdrant जवाब न दे। ALB सिर्फ ready instances को traffic देता है, इसलिए deploy में errors नहीं आते।

---

## 💻 Code Example — Basic
```python
# Minimal health endpoints (pip install fastapi uvicorn)
from fastapi import FastAPI                 # framework
from fastapi.responses import JSONResponse  # to set status code

app = FastAPI()                             # create app
READY = False                               # flag flipped after startup work


@app.on_event("startup")                    # runs once at boot (lifespan is the newer style)
async def load() -> None:
    global READY                            # modify module flag
    # ... load index / warm caches here ...
    READY = True                            # now we can take traffic


@app.get("/health/live")
async def live() -> dict[str, str]:
    return {"status": "alive"}              # process is running


@app.get("/health/ready")
async def ready() -> JSONResponse:
    code = 200 if READY else 503            # 503 = not ready, LB skips us
    return JSONResponse({"ready": READY}, status_code=code)
```

## 💻 Code Example — Advanced
```python
# Production: parallel dependency checks with timeouts + cached result
import asyncio                               # concurrency
import time                                  # monotonic clock
from typing import Awaitable, Callable       # type hints
from fastapi import FastAPI                  # framework
from fastapi.responses import JSONResponse   # custom status

app = FastAPI()                              # app
CHECK_TTL = 5.0                              # cache result for 5 seconds (avoid probe storms)
_cache: dict[str, object] = {"at": 0.0, "body": None, "code": 200}


async def check_qdrant() -> None:
    """Raise if the vector DB is unreachable (replace with a real client ping)."""
    await asyncio.sleep(0)                   # placeholder for client.get_collections()


async def check_redis() -> None:
    """Raise if the cache is unreachable (replace with redis.ping())."""
    await asyncio.sleep(0)                   # placeholder


CHECKS: dict[str, Callable[[], Awaitable[None]]] = {
    "qdrant": check_qdrant,                  # name -> coroutine function
    "redis": check_redis,
}


async def run_one(name: str, fn: Callable[[], Awaitable[None]]) -> tuple[str, str]:
    """Run one check with a 2s timeout; never raise."""
    try:
        await asyncio.wait_for(fn(), timeout=2.0)   # bounded wait
        return name, "ok"                            # healthy
    except Exception as exc:                         # timeout or any failure
        return name, f"fail: {type(exc).__name__}"   # report type only (no secrets)


@app.get("/health/ready")
async def ready() -> JSONResponse:
    now = time.monotonic()                           # current time
    if now - float(_cache["at"]) < CHECK_TTL and _cache["body"] is not None:
        return JSONResponse(_cache["body"], status_code=int(_cache["code"]))  # cached
    results = await asyncio.gather(*(run_one(n, f) for n, f in CHECKS.items()))  # parallel
    body = dict(results)                             # {"qdrant": "ok", ...}
    code = 200 if all(v == "ok" for v in body.values()) else 503
    _cache.update(at=now, body=body, code=code)      # store
    return JSONResponse(body, status_code=code)      # respond
```

---

## 🟠 FastAPI Integration
FastAPI routes ARE the health checks. Wire them into Docker, ALB and Kubernetes.

```python
# Docker healthcheck + K8s probes call the same routes. Python side: lifespan-based readiness.
from contextlib import asynccontextmanager   # lifespan helper
from fastapi import FastAPI, Response        # framework


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.ready = False                  # not ready at boot
    app.state.index = {"HS8517": "phones"}   # pretend heavy load
    app.state.ready = True                   # done
    yield                                    # app serves here
    app.state.ready = False                  # flip off on shutdown so LB drains us


app = FastAPI(lifespan=lifespan)             # attach lifespan


@app.get("/health/ready")
async def ready(resp: Response) -> dict[str, bool]:
    ok: bool = bool(app.state.ready)         # read flag
    resp.status_code = 200 if ok else 503    # LB-friendly code
    return {"ready": ok}
```
Dockerfile line (illustrative): `HEALTHCHECK CMD curl -f http://localhost:8000/health/live || exit 1`

---

## 🔗 LangChain / LangGraph Connection
Check the pieces LangChain depends on: the vector store, the checkpointer DB, and the LLM client config. Do NOT run a real chain on each probe. Instead run a rare "synthetic" canary (every few minutes) with a tiny prompt and `max_tokens=5` to detect provider outages.

```python
# Canary: a cheap LLM ping run on a timer, result stored, not per-probe
from langchain_openai import ChatOpenAI      # pip install langchain-openai

llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=5)   # tiny output = tiny cost


async def llm_canary() -> bool:
    try:
        await llm.ainvoke("ping")             # ~10 tokens total
        return True                           # provider reachable
    except Exception:
        return False                          # mark degraded
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling the LLM inside `/health`
✅ Correct: Check dependencies cheaply; canary the LLM separately.
```python
# Wrong: 10s probes x many instances = real token bill + rate-limit hits
@app.get("/health")
async def h(): return {"r": (await llm.ainvoke("hi")).content}
# Right
@app.get("/health")
async def h2(): return {"status": "ok"}
```

❌ Mistake 2: One endpoint for liveness and readiness
✅ Correct: If Qdrant blips and liveness fails, the orchestrator restarts healthy pods and makes things worse.
```python
# Wrong: /health checks Qdrant -> restart loop on DB blip
# Right: /health/live (no deps) restarts; /health/ready (deps) only removes from rotation
```

---

## 🧠 Tricky Interview Question
**Q**: "After a deploy, the new pods are 'healthy' but the first 30 requests all time out. Health checks pass. What happened?"

**Answer**: The check only proved the process was up, not that the model/index/cache was warm. Fix with a readiness gate that flips only after the index is loaded and a warm-up query ran, plus a startup probe so liveness does not kill a slow-loading pod, and `maxUnavailable: 0` rolling updates.

---

## ⚫ Interview Questions + Answers

Q1: Liveness vs readiness?
A1: Liveness = should I restart this? Readiness = should I send traffic to this?

Q2: What status code means "not ready"?
A2: 503 Service Unavailable.

Q3: Why cache the readiness result for a few seconds?
A3: Many probers (LBs, K8s, monitors) can hit it often; caching avoids dependency pings multiplying under load.

Q4: How do you detect LLM provider outages without paying per probe?
A4: Background canary with a tiny prompt every few minutes, plus circuit breaker on real traffic errors; expose status in a degraded field.

Q5: Design health for a RAG service with an optional reranker.
A5: Required deps (vector DB, LLM config) gate readiness; optional deps (reranker) only mark "degraded" and the code falls back to plain retrieval, so you do not drop out of rotation for a non-critical component.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any service behind an ALB, Kubernetes, ECS or Docker healthcheck
- Slow startup (model load, index load)

❌ Avoid when:
- Putting expensive or paid calls in the probe path
- Exposing internal details (hostnames, versions) publicly

---

## 📊 Visual Diagram
```
 Load Balancer ──every 10s──► GET /health/ready
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
         Qdrant ping         Redis ping        index loaded?
              └───────────────┬───────────────────────┘
                     all ok → 200  (in rotation)
                     any fail → 503 (drained)
 Orchestrator ──► GET /health/live (no deps) ──fail x3──► restart
```

---

## 💰 Cost Impact
A correct check costs zero tokens. A wrong one (LLM call per probe) at 3 instances x every 10 s = about 26k calls/day; at ~10 tokens each that is ~260k tokens/day for nothing, and it eats rate limits. Optimise: cache results, canary only every few minutes with `max_tokens=5`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Liveness | Is the process alive | क्या process जिंदा है |
| Readiness | Can it take traffic | क्या traffic ले सकता है |
| Startup probe | Extra time for slow boot | धीमे boot के लिए probe |
| Canary | Synthetic periodic test | समय-समय पर नकली test |
| Degraded | Works with reduced features | कम features के साथ चालू |

---

## ⚡ 3-Line Summary
English: Use separate liveness and readiness endpoints. Check dependencies cheaply with timeouts and short caching. Never call the paid LLM per probe; use a slow canary.
Hindi: Liveness और readiness के अलग endpoints रखें। Dependencies को timeout और short caching के साथ सस्ते में check करें। हर probe पर paid LLM call न करें; धीमा canary इस्तेमाल करें।

---

## ➡️ Next Topic
**558. Graceful Shutdown for AI** — what happens to in-flight LLM streams when a pod is stopped, and how to drain them.
