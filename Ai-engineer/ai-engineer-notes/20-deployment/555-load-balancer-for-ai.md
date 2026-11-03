
---

# 555. Load Balancer for AI
# हिंदी में: AI के लिए Load Balancer

---

## 🔵 Simple Definition (English)
A load balancer spreads incoming requests across several app instances so no single one is overloaded and a failed one is skipped. For AI apps, requests are slow (seconds) and uneven (one prompt is 100 tokens, another 10,000), so **least outstanding requests** usually beats plain round robin. Examples: AWS ALB, Nginx, HAProxy.

## 🔵 सरल परिभाषा (Hindi)
Load balancer आने वाली requests को कई app instances में बाँटता है ताकि कोई एक overload न हो और खराब instance skip हो जाए। AI apps में requests धीमी (कई seconds) और असमान होती हैं (कोई prompt 100 tokens का, कोई 10,000 का), इसलिए सादे round robin से **least outstanding requests** अक्सर बेहतर है। उदाहरण: AWS ALB, Nginx, HAProxy।

---

## 🔴 Problem it Solves
One instance cannot handle all traffic and is a single point of failure. With round robin, an instance that got three huge prompts becomes slow while another sits idle. A load balancer provides high availability, even utilisation, rolling deploys, and one stable address.

## 🔴 यह क्यों बना? (Hindi)
एक instance सारा traffic नहीं सँभाल सकता और single point of failure है। Round robin में जिस instance को तीन बड़े prompts मिले वह धीमा हो जाता है जबकि दूसरा खाली बैठा रहता है। Load balancer high availability, बराबर इस्तेमाल, rolling deploys और एक stable address देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Clients call one DNS name (api.example.com) pointing to the load balancer
Step 2 → LB terminates TLS and picks a healthy target using an algorithm
Step 3 → Algorithms: round robin, least connections / least outstanding requests, IP hash
Step 4 → LB health checks targets (GET /health); unhealthy ones get no traffic
Step 5 → Idle timeout must exceed the slowest LLM response (ALB default is 60 s)
Step 6 → Deregistration delay (connection draining) lets in-flight requests finish
Step 7 → Sticky sessions (optional) pin a user to one instance for local state
Step 8 → Metrics: request count, target response time, 5xx, healthy host count
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Clients एक DNS नाम (api.example.com) call करते हैं जो LB की ओर जाता है
Step 2 → LB TLS खोलता है और algorithm से healthy target चुनता है
Step 3 → Algorithms: round robin, least connections / least outstanding requests, IP hash
Step 4 → LB targets की health check करता है (GET /health); unhealthy को traffic नहीं
Step 5 → Idle timeout सबसे धीमे LLM जवाब से ज़्यादा होना चाहिए (ALB default 60 s)
Step 6 → Deregistration delay में चल रही requests पूरी हो जाती हैं
Step 7 → Sticky sessions (optional) user को एक instance पर रखती हैं
Step 8 → Metrics: request count, target response time, 5xx, healthy host count
```

---

## 🟡 Real World Example
**Tariff Classification System**: Four `tariff-api` tasks sit behind an ALB. Some invoices have 200 line items, so a request can run 40 s. The ALB idle timeout is raised to 120 s and the target group uses the `least_outstanding_requests` algorithm so a busy task receives fewer new requests.

**Amazon-style**: Product-QA chatbot traffic is spread across many instances; at Prime Day the pool grows.

## 🟡 Real Example Hindi mein
**Tariff System**: ALB के पीछे चार `tariff-api` tasks हैं। कुछ invoices में 200 line items होते हैं, इसलिए request 40 s चल सकती है। ALB idle timeout 120 s किया गया और target group `least_outstanding_requests` algorithm इस्तेमाल करता है ताकि busy task को कम नई requests मिलें।

**Amazon-style**: Product-QA chatbot का traffic कई instances में बँटता है; Prime Day पर pool बढ़ जाता है।

---

## 💻 Code Example — Basic
```python
# A tiny in-process load balancer simulation: round robin vs least outstanding requests (runs offline)
import itertools  # for cycling through backends
from dataclasses import dataclass  # simple data holder


@dataclass
class Backend:
    name: str  # instance name
    outstanding: int = 0  # requests in flight


def round_robin(backends: list[Backend]):
    """Yield backends in order forever."""
    return itertools.cycle(backends)  # simple cycle


def least_outstanding(backends: list[Backend]) -> Backend:
    """Pick the backend with the fewest in-flight requests."""
    return min(backends, key=lambda b: b.outstanding)  # smallest load


if __name__ == "__main__":
    pool = [Backend("a"), Backend("b"), Backend("c")]  # three instances
    pool[0].outstanding = 5  # instance a is busy with slow prompts
    rr = round_robin(pool)  # round robin iterator
    print("round robin picks:", next(rr).name)  # a: ignores load
    print("least outstanding picks:", least_outstanding(pool).name)  # b: avoids the busy one
```

## 💻 Code Example — Advanced
```python
# Async load balancer client with health checks, failover and per-backend concurrency tracking
import asyncio  # async primitives
from dataclasses import dataclass, field  # data holder
from typing import Any  # typing

import httpx  # async HTTP client


@dataclass
class Target:
    url: str  # base URL of an instance
    healthy: bool = True  # current health
    inflight: int = 0  # in-flight requests
    failures: int = 0  # consecutive failures


@dataclass
class LLMBalancer:
    targets: list[Target]  # pool
    max_failures: int = 3  # mark unhealthy after this many
    client: httpx.AsyncClient = field(default_factory=lambda: httpx.AsyncClient(timeout=60.0))  # shared client

    def pick(self) -> Target:
        """Least outstanding among healthy targets."""
        alive = [t for t in self.targets if t.healthy]  # healthy only
        if not alive:  # nothing available
            raise RuntimeError("no healthy backends")  # fail clearly
        return min(alive, key=lambda t: t.inflight)  # least loaded

    async def call(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        """POST to a backend; on connection failure try another one (safe only before the request is processed)."""
        tried: set[str] = set()  # avoid retrying the same target
        while True:
            t = self.pick()  # choose target
            if t.url in tried:  # already failed this one
                raise RuntimeError("all backends failed")  # stop
            tried.add(t.url)  # record
            t.inflight += 1  # count request
            try:
                r = await self.client.post(f"{t.url}{path}", json=payload)  # call
                r.raise_for_status()  # error status
                t.failures = 0  # reset on success
                return r.json()  # return body
            except (httpx.ConnectError, httpx.ConnectTimeout):  # could not connect: safe to retry elsewhere
                t.failures += 1  # count failure
                if t.failures >= self.max_failures:  # too many
                    t.healthy = False  # eject target
            finally:
                t.inflight -= 1  # always release

    async def health_loop(self, interval: float = 5.0) -> None:
        """Probe /health and restore recovered targets."""
        while True:
            for t in self.targets:  # each target
                try:
                    r = await self.client.get(f"{t.url}/health", timeout=2.0)  # probe
                    t.healthy = r.status_code == 200  # update flag
                except httpx.HTTPError:  # unreachable
                    t.healthy = False  # mark down
            await asyncio.sleep(interval)  # wait
```

---

## 🟠 FastAPI Integration
Behind an ALB your FastAPI app needs a `/health` that is cheap and reflects readiness (not LLM availability). Keep the app stateless so any instance can answer any request. Move sessions to Redis. For streaming, make sure the LB supports it and the idle timeout is larger than the longest gap between chunks.

```python
# Stateless FastAPI instance that reports its identity (useful to verify balancing)
import os  # env
import socket  # hostname
from fastapi import FastAPI  # framework

app = FastAPI()  # app


@app.get("/health")  # target group health check
async def health() -> dict[str, str]:
    return {"status": "ok"}  # fast and cheap


@app.get("/whoami")  # debug route to see which instance answered
async def whoami() -> dict[str, str]:
    return {"host": socket.gethostname(), "version": os.getenv("APP_VERSION", "dev")}  # identity
```

---

## 🔗 LangChain / LangGraph Connection
Balancing also happens one level down: between LLM providers. LangChain's `with_fallbacks` switches to another model when one errors, and LangGraph checkpointers (Postgres/Redis) let any instance resume a thread, so the balancer needs no sticky sessions.

```python
# Provider-level failover in LangChain
from langchain_openai import ChatOpenAI  # primary

primary = ChatOpenAI(model="gpt-4o-mini", max_retries=1, timeout=20)  # fast fail
backup = ChatOpenAI(model="gpt-4o", max_retries=1, timeout=30)  # alternative (could be another provider)
llm = primary.with_fallbacks([backup])  # use backup if primary raises
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Idle timeout shorter than the LLM response
```python
# Wrong: ALB idle timeout 60s, LLM answer takes 75s, client gets 504
idle_timeout_seconds = 60
# Correct: set above the slowest legitimate response (and make the app time out first)
idle_timeout_seconds = 120
```

❌ Mistake 2: Storing conversation state in instance memory
```python
# Wrong: next request lands on another instance and the history is gone
history: dict[str, list[str]] = {}
# Correct: shared store (Redis/Postgres) keyed by session id
# await redis.rpush(f"chat:{session_id}", message)
```

---

## 🧠 Tricky Interview Question
**Q**: "Four instances show 25% CPU each but users still see slow responses and 504s on one instance. Why?"

**Answer**: Round robin ignores request cost. One instance may have received several very long prompts, so its event loop and its LLM connections are saturated even though the average CPU is low (the work is mostly waiting on I/O). Use least outstanding requests, limit per-instance concurrency (semaphore), scale on request count per target or latency instead of CPU, and put long jobs on a queue.

---

## ⚫ Interview Questions + Answers

Q1: What does a load balancer do?
A1: Distributes requests across healthy backend instances for availability and even load.

Q2: Layer 4 vs layer 7 load balancing?
A2: L4 (NLB) forwards TCP/UDP without reading HTTP; L7 (ALB) understands HTTP, so it can route by path/header and do health checks per route.

Q3: Why is round robin poor for LLM workloads?
A3: Request cost varies widely (tokens, tool calls), so equal counts do not mean equal load. Least outstanding requests adapts.

Q4: What is connection draining?
A4: When an instance is removed, the LB stops sending new requests but lets in-flight ones finish within the deregistration delay.

Q5: How would you design load balancing across multiple LLM providers with rate limits?
A5: A gateway layer (LiteLLM-style or custom) with per-provider rate-limit tracking, weighted routing, retry with backoff on 429/5xx, fallback order, circuit breakers, and logs of tokens and cost per provider; keep idempotency in mind so retries do not double-bill.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- More than one instance, or you need zero-downtime deploys
- You need health-based routing and TLS in one place

❌ Avoid when:
- Single small prototype (adds cost and complexity)
- Sticky stateful workloads you could not make stateless (consider fixing the state first)

---

## 📊 Visual Diagram
```
 Clients ─▶ DNS ─▶ ┌──────────────────────────┐
                   │ Load Balancer (ALB)      │
                   │ TLS · health · algorithm │
                   └───┬──────────┬────────┬──┘
        least requests │          │        │
                       ▼          ▼        ▼
                 [inst A: 5] [inst B: 1] [inst C: 2 ✗ unhealthy]
                       └─ new request goes to B (fewest in flight)
```

---

## 💰 Cost Impact
An ALB has an hourly charge plus usage units (LCUs); illustrative order is around $16 to $25 per month base plus usage, so check pricing. The bigger effect is indirect: uneven balancing forces you to run extra instances, and retries from timeouts duplicate LLM calls and tokens. Optimise: least-outstanding-requests, correct idle timeouts (so users do not retry), health checks that avoid flapping, autoscaling on requests per target, and a gateway that caches or routes simple queries to cheaper models (for example 70% of tariff lookups to gpt-4o-mini rather than a large model).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Load balancer | Spreads traffic over instances | Traffic बाँटने वाला |
| Round robin | Turn by turn selection | बारी-बारी से चुनना |
| Least outstanding requests | Pick least busy target | सबसे कम busy target |
| Target group | Set of backends for an LB | Backends का समूह |
| Idle timeout | Max silent time on a connection | Connection की चुप्पी सीमा |
| Connection draining | Finish in-flight before removal | हटाने से पहले चल रहे काम पूरे करना |

---

## ⚡ 3-Line Summary
English: A load balancer spreads requests across healthy instances and enables zero-downtime deploys. For slow, uneven LLM calls use least outstanding requests, long idle timeouts and stateless apps. Be careful with retries because they duplicate token cost.
Hindi: Load balancer requests को healthy instances में बाँटता है और zero-downtime deploys देता है। धीमी, असमान LLM calls के लिए least outstanding requests, लंबे idle timeouts और stateless apps रखो। Retries में सावधान रहो क्योंकि tokens का cost दोगुना होता है।

---

## ➡️ Next Topic
**556. Auto Scaling for AI** — adding and removing instances automatically based on the right signals.
