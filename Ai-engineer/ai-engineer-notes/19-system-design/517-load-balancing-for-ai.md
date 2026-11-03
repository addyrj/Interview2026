---

# 517. Load Balancing for AI
# हिंदी में: AI के लिए Load Balancing

---

## 🔵 Simple Definition (English)
Load balancing spreads incoming requests across multiple servers, models or providers so no single one is overloaded. For AI it covers three levels: balancing API replicas, balancing across LLM providers/keys/regions (a "gateway"), and balancing GPU inference servers where requests have very different costs.

## 🔵 सरल परिभाषा (Hindi)
Load balancing आने वाले requests को कई servers, models या providers में बाँटता है ताकि कोई एक overload न हो। AI में तीन स्तर हैं: API replicas के बीच, LLM providers/keys/regions के बीच (gateway), और GPU inference servers के बीच जहाँ हर request की cost बहुत अलग होती है।

---

## 🔴 Problem it Solves
Plain round-robin works for equal, short web requests. LLM requests vary hugely (10 tokens vs 4,000 tokens, 1 s vs 40 s), streaming holds connections open, and providers impose rate limits and have outages. Naive balancing overloads some nodes while others idle.

## 🔴 यह क्यों बना? (Hindi)
Round-robin बराबर, छोटे web requests के लिए ठीक है। LLM requests बहुत अलग होते हैं (10 tokens बनाम 4,000 tokens, 1 s बनाम 40 s), streaming में connection खुला रहता है, और providers की rate limits व outages होते हैं। Naive balancing कुछ nodes को overload और बाकी को खाली छोड़ देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Layer 1: L7 load balancer (nginx/ALB/Envoy) spreads HTTP across API replicas
         - health checks (/healthz), long timeouts for streaming, connection draining
Step 2 → Pick an algorithm: round-robin (equal), least-connections / least-outstanding-requests
         (better for variable LLM latency), weighted (different capacities)
Step 3 → Layer 2: LLM gateway chooses provider/model/key: weighted routing, quota-aware,
         latency-aware, with fallback on errors (429/5xx/timeouts)
Step 4 → Circuit breaker: after N failures stop sending to a target for a cool-down
Step 5 → Layer 3: for self-hosted GPUs use queue-depth aware routing; use continuous
         batching servers (e.g. vLLM) and route by load; session/prefix affinity can raise cache hits
Step 6 → Observe: per-target latency, errors, tokens, cost; adjust weights
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Layer 1: L7 load balancer API replicas में HTTP बाँटता है (health checks, streaming के लिए लंबे timeouts)
Step 2 → Algorithm: round-robin, least-connections (LLM के लिए बेहतर), weighted
Step 3 → Layer 2: LLM gateway provider/model/key चुनता है; errors (429/5xx/timeout) पर fallback
Step 4 → Circuit breaker: N failures के बाद cool-down तक उस target को नहीं भेजो
Step 5 → Layer 3: GPU servers में queue-depth aware routing; continuous batching (जैसे vLLM)
Step 6 → हर target का latency, errors, tokens, cost देखो और weights बदलो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Three API replicas behind a load balancer. The LLM gateway has Provider A (primary, 70% weight, quota 500k tokens/min) and Provider B (30%). When A returns 429s three times in a row, the circuit breaker opens for 30 seconds and all traffic goes to B. Heavy bulk jobs use a separate key so they cannot starve interactive users.
**Amazon-style example**: Shopping assistant traffic split across regions by user location, with failover to another region.

## 🟡 Real Example Hindi mein
**Tariff System**: Load balancer के पीछे तीन API replicas। LLM gateway में Provider A (primary, 70% weight, quota 500k tokens/min) और Provider B (30%)। A लगातार तीन बार 429 दे तो circuit breaker 30 सेकंड के लिए खुल जाता है और सारा traffic B पर जाता है। Bulk jobs अलग key इस्तेमाल करते हैं ताकि interactive users भूखे न रहें।

---

## 💻 Code Example — Basic
```python
# Basic: weighted random vs least-outstanding routing across targets (pure Python, offline)
import random  # weighted selection


targets = {"A": {"weight": 7, "inflight": 3}, "B": {"weight": 3, "inflight": 0}}  # sample state


def weighted_pick() -> str:  # choose by weight
    names = list(targets)  # target names
    weights = [targets[n]["weight"] for n in names]  # weights
    return random.choices(names, weights=weights, k=1)[0]  # one weighted choice


def least_loaded() -> str:  # choose the target with fewest in-flight requests
    return min(targets, key=lambda n: targets[n]["inflight"] / targets[n]["weight"])  # normalised load


random.seed(1)  # reproducible demo
print("weighted:", [weighted_pick() for _ in range(10)])  # mostly A
print("least loaded:", least_loaded())  # B (0 in flight)
```

## 💻 Code Example — Advanced
```python
# Advanced: async LLM gateway with weighted routing, circuit breaker and fallback (offline mocks)
import asyncio  # async runtime
import random  # weighted choice
import time  # clock
from dataclasses import dataclass, field  # target state


@dataclass
class Target:  # one provider/model/key
    name: str  # name
    weight: int  # routing weight
    fail_rate: float  # simulated failure probability
    failures: int = 0  # consecutive failures
    open_until: float = 0.0  # circuit breaker open until this time
    inflight: int = field(default=0)  # current requests

    def available(self) -> bool:  # is the circuit closed?
        return time.monotonic() >= self.open_until  # closed if cool-down passed


async def call(t: Target, prompt: str) -> str:  # mock provider call
    t.inflight += 1  # count in-flight
    try:
        await asyncio.sleep(0.01)  # latency
        if random.random() < t.fail_rate:  # simulated 429/5xx
            raise ConnectionError(f"{t.name} error")  # fail
        return f"{t.name}:{prompt}"  # success
    finally:
        t.inflight -= 1  # always decrement


class Gateway:  # routes requests across targets
    def __init__(self, targets: list[Target], threshold: int = 3, cooldown: float = 0.5) -> None:
        self.targets, self.threshold, self.cooldown = targets, threshold, cooldown  # settings

    async def complete(self, prompt: str) -> str:  # try targets until one works
        pool = [t for t in self.targets if t.available()]  # skip open circuits
        if not pool:  # everything is down
            raise RuntimeError("all providers unavailable")  # explicit failure
        order: list[Target] = []  # attempt order
        while pool:  # weighted random without replacement
            pick = random.choices(pool, weights=[t.weight for t in pool], k=1)[0]  # choose
            order.append(pick)  # add
            pool.remove(pick)  # remove from pool
        for t in order:  # try each in turn
            try:
                out = await asyncio.wait_for(call(t, prompt), timeout=2)  # guarded call
                t.failures = 0  # reset on success
                return out  # done
            except (ConnectionError, asyncio.TimeoutError):  # failure
                t.failures += 1  # count
                if t.failures >= self.threshold:  # too many failures
                    t.open_until = time.monotonic() + self.cooldown  # open the circuit
        raise RuntimeError("all attempts failed")  # nothing worked


async def main() -> None:  # demo
    gw = Gateway([Target("A", 7, fail_rate=0.9), Target("B", 3, fail_rate=0.0)])  # A is flaky
    random.seed(0)  # reproducible
    print([await gw.complete("hs code?") for _ in range(5)])  # falls back to B


if __name__ == "__main__":
    asyncio.run(main())  # run
```

---

## 🟠 FastAPI Integration
FastAPI exposes health endpoints for the load balancer and uses the gateway internally. Make `/healthz` cheap (liveness) and `/readyz` check dependencies (readiness). Keep graceful shutdown so in-flight streams finish.

```python
from fastapi import FastAPI, Response  # app, response
from fastapi.responses import StreamingResponse  # streaming
import asyncio  # sleep
from typing import AsyncIterator  # type

app = FastAPI()  # app
READY = True  # flipped to False during shutdown/drain


@app.get("/healthz")  # liveness: process is up
async def healthz() -> dict[str, str]:
    return {"status": "ok"}  # cheap


@app.get("/readyz")  # readiness: safe to receive traffic?
async def readyz(resp: Response) -> dict[str, bool]:
    if not READY:  # draining
        resp.status_code = 503  # tell the balancer to stop routing here
    return {"ready": READY}  # state


async def token_stream() -> AsyncIterator[str]:  # fake streaming generator
    for t in ["8517", ".", "13"]:  # tokens
        await asyncio.sleep(0.01)  # latency
        yield t  # send token


@app.get("/stream")  # streaming route (balancer needs long timeouts and no buffering)
async def stream() -> StreamingResponse:
    return StreamingResponse(token_stream(), media_type="text/plain")  # stream
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's `with_fallbacks` provides simple failover between models; for real balancing and key/provider routing, teams place an LLM gateway/proxy (for example LiteLLM or a cloud provider gateway) in front and point LangChain's `base_url` at it.

```python
from langchain_core.runnables import RunnableLambda  # offline stand-ins

def provider_a(x: str) -> str:  # primary fails
    raise ConnectionError("429")  # simulated rate limit

def provider_b(x: str) -> str:  # secondary works
    return f"B handled: {x}"  # result

chain = RunnableLambda(provider_a).with_fallbacks([RunnableLambda(provider_b)])  # real fallback API
print(chain.invoke("classify phone"))  # B handled: classify phone
# Real usage: ChatOpenAI(base_url="http://my-gateway/v1", api_key=...) so the gateway does the balancing
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Round-robin for variable-length LLM requests
✅ Correct: least-outstanding-requests or queue-depth aware.
```python
# Wrong
target = targets[i % len(targets)]  # a node may get all the long requests
# Right
target = min(targets, key=lambda t: t.inflight / t.weight)  # load aware
```

❌ Mistake 2: Short proxy timeouts and buffering for streaming
✅ Correct: raise read timeouts, disable response buffering, and drain connections on deploy.

---

## 🧠 Tricky Interview Question
**Q**: "You add a second LLM provider for failover, yet during a provider outage your whole system still slows to a crawl. Why?"

**Answer**: Without a circuit breaker each request first waits for the failing provider's long timeout and only then falls back, so every call pays the timeout. Add short timeouts, health tracking, a circuit breaker that skips the failing provider, hedged requests where justified, and outlier detection. Also test fallback quality and quota on the second provider.

---

## ⚫ Interview Questions + Answers

Q1: What does a load balancer do? (Easy)
A1: Distributes traffic across servers for capacity and availability, using health checks to avoid unhealthy ones.

Q2: Name common algorithms. (Easy)
A2: Round-robin, weighted round-robin, least connections, IP hash / consistent hashing.

Q3: Why least-connections for LLM traffic? (Medium)
A3: Request durations vary a lot; routing to the node with the fewest active requests prevents long requests piling onto one node.

Q4: What is a circuit breaker? (Medium)
A4: After repeated failures it stops sending traffic to a target for a cool-down, then lets a probe request through (half-open) to check recovery.

Q5: How would you balance traffic across self-hosted GPU inference servers? (Hard)
A5: Use servers with continuous batching, route by queue depth or estimated tokens in flight rather than request count, apply prefix/session affinity to reuse KV cache where useful, separate pools for interactive and batch work, autoscale on queue depth, health-check model readiness (weights loaded), and drain gracefully on scale-in.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- More than one replica, provider, key or region
- Uptime requirements, rate-limit constraints

❌ Avoid when:
- Single small internal service where an extra gateway adds more failure points than it removes

---

## 📊 Visual Diagram
```
 Clients ─▶ L7 Load Balancer (health checks, least-conn)
                 │
      ┌──────────┼──────────┐
      ▼          ▼          ▼
    API 1      API 2      API 3     (stateless)
      └──────────┼──────────┘
                 ▼
          LLM Gateway
     ┌───────────┼────────────┐
     ▼           ▼            ▼
 Provider A   Provider B   Self-hosted GPUs
 (70%)        (30%)        (queue-depth routing)
   circuit breaker + fallback on 429/5xx
```

---

## 💰 Cost Impact
Balancing can lower cost by sending a share of traffic to cheaper models or providers, and by avoiding wasted retries; but gateways and extra replicas add infrastructure cost. Failed attempts that time out after partial streaming can burn tokens without value.
Optimise: cost-aware routing (small model first), quotas per tenant, short timeouts, avoid duplicate hedged requests unless needed, keep high prompt-cache hit rates through prefix affinity, track cost per target.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Load balancer | Spreads traffic | traffic बाँटने वाला |
| Health check | Probe to test a node | स्वास्थ्य जाँच |
| Circuit breaker | Stops calls to failing target | विफल target को रोकने वाला |
| Gateway | Single entry for LLM providers | LLM प्रवेश द्वार |
| Failover | Switch to backup | बैकअप पर जाना |
| Least connections | Route to least busy | सबसे कम व्यस्त को |

---

## ⚡ 3-Line Summary
English: AI load balancing has three layers: API replicas, LLM gateway, and GPU servers.
Use load-aware algorithms, health checks, circuit breakers and fallbacks.
Remember streaming needs long timeouts and graceful draining.
Hindi: AI load balancing के तीन layers हैं: API replicas, LLM gateway और GPU servers।
Load-aware algorithms, health checks, circuit breakers और fallbacks इस्तेमाल करो।
Streaming के लिए लंबे timeouts और graceful draining याद रखो।

---

## ➡️ Next Topic
**518. Next topic in System Design folder** — continue with the next item in the roadmap (see How.md for the exact title).
