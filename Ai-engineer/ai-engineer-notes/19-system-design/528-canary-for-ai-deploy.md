
---

# 528. Canary for AI Deploy
# हिंदी में: AI Deploy के लिए Canary

---

## 🔵 Simple Definition (English)
A canary deploy sends a small slice of real traffic (for example 5%) to a new version of your AI system (new model, prompt, or code) while most users stay on the stable version. You watch quality, latency, errors and cost. If all is healthy, you increase the slice step by step; if not, you roll back.

## 🔵 सरल परिभाषा (Hindi)
Canary deploy में AI system के नए version (नया model, prompt या code) पर real traffic का एक छोटा हिस्सा (जैसे 5%) भेजा जाता है, जबकि बाकी users stable version पर रहते हैं। आप quality, latency, errors और cost देखते हैं। सब ठीक हो तो हिस्सा धीरे-धीरे बढ़ाते हैं; नहीं तो rollback।

---

## 🔴 Problem it Solves
- Offline tests cannot predict how a new prompt or model behaves on real user queries.
- Deploying to 100% at once means a bad prompt hurts every user.
- LLM failures are often quiet: no crash, just worse answers or higher cost.

## 🔴 यह क्यों बना? (Hindi)
- Offline tests नहीं बता सकते कि नया prompt या model real user queries पर कैसा चलेगा।
- एक साथ 100% पर deploy करने से खराब prompt सभी users को नुकसान पहुँचाता है।
- LLM की failures अक्सर चुपचाप होती हैं: crash नहीं, बस खराब जवाब या ज़्यादा cost।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pass offline eval (golden set) first: canary is not a replacement
Step 2 → Deploy new version (v2) next to stable (v1)
Step 3 → Router sends 5% of traffic to v2 (sticky by user id so a user sees one version)
Step 4 → Compare v2 vs v1: error rate, p95 latency, tokens/request, quality score, user feedback
Step 5 → If within thresholds for N minutes/requests → raise to 25%, 50%, 100%
Step 6 → If any threshold is breached → automatic rollback to 0%
Step 7 → Keep v1 ready until v2 is fully promoted
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले offline eval (golden set) पास करो: canary इसका विकल्प नहीं है
Step 2 → नया version (v2) stable (v1) के साथ deploy करो
Step 3 → Router 5% traffic v2 पर भेजता है (user id से sticky, ताकि user को एक ही version दिखे)
Step 4 → v2 और v1 की तुलना: error rate, p95 latency, tokens/request, quality score, user feedback
Step 5 → N मिनट/requests तक thresholds में रहे → 25%, 50%, 100% करो
Step 6 → कोई threshold टूटे → अपने-आप 0% पर rollback
Step 7 → v2 पूरी तरह promote होने तक v1 तैयार रखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The team changes the prompt to give shorter reasoning, hoping to cut tokens. Offline eval looks good. Canary at 5% for a day shows: tokens per request down 30%, but the "officer overrides the HS code" rate rises from 6% to 11%. The canary gate trips on the override-rate threshold and rolls back automatically. Only 5% of officers saw the worse version.

**Zomato-style AI**: A new menu-recommendation model goes to 5% of users in one city first; the team watches order conversion and complaint rate.

## 🟡 Real Example Hindi mein
**Tariff System**: Team prompt बदलती है ताकि reasoning छोटी हो और tokens कम हों। Offline eval अच्छा दिखता है। 5% canary पर एक दिन में दिखता है: tokens per request 30% कम, लेकिन "officer ने HS code override किया" rate 6% से 11% हो गया। Override-rate threshold पर canary gate trip होता है और अपने-आप rollback। सिर्फ 5% officers ने खराब version देखा।

**Zomato-style AI**: नया menu-recommendation model पहले एक शहर के 5% users को जाता है; team order conversion और complaint rate देखती है।

---

## 💻 Code Example — Basic
```python
# Basic canary router: pure Python, deterministic by user id
import hashlib                                         # stable hashing

def bucket(user_id: str) -> int:
    """Map a user to a stable number 0..99."""
    digest = hashlib.sha256(user_id.encode()).hexdigest()  # hash the id
    return int(digest, 16) % 100                       # reduce to 0..99

def pick_version(user_id: str, canary_percent: int) -> str:
    """Return 'v2' for canary users, else 'v1'."""
    return "v2" if bucket(user_id) < canary_percent else "v1"

if __name__ == "__main__":
    users = [f"user-{i}" for i in range(1000)]         # fake users
    v2_count = sum(pick_version(u, 5) == "v2" for u in users)  # count canary users
    print(f"canary users: {v2_count}/1000")            # observed 40 with this hash (about 4%)
    print(pick_version("user-7", 5) == pick_version("user-7", 5))  # True: sticky
```

## 💻 Code Example — Advanced
```python
# Advanced: canary controller with metrics comparison and auto-rollback
import asyncio                                         # async loop
import random                                          # simulate metrics in demo
from dataclasses import dataclass                      # metric container

@dataclass
class Metrics:
    requests: int                                      # sample size
    error_rate: float                                  # 0..1
    p95_ms: float                                      # latency
    tokens_per_req: float                              # cost proxy
    override_rate: float                               # quality proxy (officer overrides)

@dataclass
class Gate:
    max_error_delta: float = 0.01                      # v2 may add at most +1% errors
    max_latency_ratio: float = 1.2                     # v2 p95 <= 1.2x v1
    max_token_ratio: float = 1.3                       # v2 tokens <= 1.3x v1
    max_override_delta: float = 0.02                   # quality guard
    min_requests: int = 200                            # do not decide on tiny samples

def evaluate(v1: Metrics, v2: Metrics, gate: Gate) -> tuple[str, str]:
    """Return (decision, reason): 'wait' | 'promote' | 'rollback'."""
    if v2.requests < gate.min_requests:                # not enough data
        return "wait", "small sample"
    if v2.error_rate - v1.error_rate > gate.max_error_delta:
        return "rollback", "errors up"
    if v2.p95_ms > v1.p95_ms * gate.max_latency_ratio:
        return "rollback", "latency up"
    if v2.tokens_per_req > v1.tokens_per_req * gate.max_token_ratio:
        return "rollback", "cost up"
    if v2.override_rate - v1.override_rate > gate.max_override_delta:
        return "rollback", "quality down"
    return "promote", "healthy"

STEPS: list[int] = [5, 25, 50, 100]                    # traffic ladder

async def fetch_metrics(version: str, percent: int) -> Metrics:
    """Mock metrics source (replace with Prometheus/your store)."""
    await asyncio.sleep(0)                             # yield to the loop
    bad = version == "v2" and random.random() < 0.3    # sometimes v2 is bad
    return Metrics(500, 0.02 if bad else 0.005, 900.0,
                   600.0, 0.12 if bad else 0.06)

async def run_canary() -> int:
    """Walk the ladder; return final percent (0 means rolled back)."""
    gate = Gate()                                      # thresholds
    for pct in STEPS:
        try:
            v1, v2 = await asyncio.gather(fetch_metrics("v1", pct), fetch_metrics("v2", pct))
        except Exception as exc:                       # metrics outage: fail safe
            print("metrics error, rolling back:", exc)
            return 0
        decision, reason = evaluate(v1, v2, gate)      # compare
        print(f"{pct}% -> {decision} ({reason})")
        if decision == "rollback":
            return 0                                   # send 0% to v2
    return 100                                         # fully promoted

if __name__ == "__main__":
    random.seed(1)                                     # reproducible demo
    print("final traffic to v2:", asyncio.run(run_canary()))
```

---

## 🟠 FastAPI Integration
Place the canary split in a thin routing layer (gateway or FastAPI dependency). Return the version in a response header so you can group metrics by version.

```python
# FastAPI: route by sticky bucket, tag metrics with version
import os
from fastapi import Depends, FastAPI, Header

app = FastAPI()

def canary_percent() -> int:
    """Read from env/config so you can change it without redeploying."""
    return int(os.environ.get("CANARY_PERCENT", "0"))  # 0 = canary off

def version_for(user_id: str = Header(default="anon"),
                pct: int = Depends(canary_percent)) -> str:
    return pick_version(user_id, pct)                  # from the basic example

PROMPTS = {"v1": "Classify the goods. Explain in detail.",
           "v2": "Classify the goods. Explain in two lines."}

@app.post("/classify")
async def classify(q: str, version: str = Depends(version_for)) -> dict[str, str]:
    system = PROMPTS[version]                          # version selects prompt/model
    # answer = await llm(system, q)                    # real call goes here
    return {"version": version, "answer": f"[mock:{system[:12]}]"}  # tag for metrics
```
In production, a service mesh or gateway (nginx weighted upstreams, Envoy, cloud load balancers) can do the split, and feature flags (topic 526) can control the percentage.

---

## 🔗 LangChain / LangGraph Connection
- Compare versions with **LangSmith** experiments or tags: tag each run with `version=v2` and compare latency, tokens and feedback.
- In LangGraph, a version is often just a different prompt or graph build: keep `graph_v1` and `graph_v2` compiled and pick one per request.

```python
# LangChain: tag runs with the canary version (illustrative)
# chain = prompt | llm
# result = await chain.ainvoke(
#     {"q": q},
#     config={"tags": [f"version:{version}"], "metadata": {"user_bucket": bucket(user_id)}},
# )
# Then filter traces by tag in LangSmith to compare v1 and v2.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Random split per request
✅ Correct: Sticky split by user id, so a user does not bounce between versions mid-conversation.

```python
# Wrong: a conversation hits v1 then v2
version = "v2" if random.random() < 0.05 else "v1"
# Right: stable bucket
version = pick_version(user_id, 5)
```

❌ Mistake 2: Judging only errors and latency
✅ Correct: LLM regressions are often quality or cost. Track quality proxies (override rate, thumbs down, eval-judge score) and tokens per request too.

❌ Mistake 3: Deciding on a tiny sample
✅ Correct: Set a minimum request count (like `min_requests`) before any promote or rollback decision.

---

## 🧠 Tricky Interview Question

**Q**: "Your canary at 5% shows v2 is 15% cheaper and the same error rate, so you promote it. A week later customers complain about worse answers. What did the canary miss?"

**Answer**: The canary had no quality signal. Errors and cost only measure "did it run and how much". Fix: add quality metrics: LLM-as-judge score on a sampled subset, user feedback, override or retry rate, and automatic comparison on a fixed golden set in parallel. Also check segments: the average can hide a regression in one category (for example Hindi queries or one chapter of the tariff schedule), so slice metrics by segment. Also the 5% sample may have been too small or too short to catch rare categories.

---

## ⚫ Interview Questions + Answers

Q1: What is a canary deployment?
A1: Releasing a new version to a small share of traffic first, checking health, then widening. Named after canaries in coal mines, which warned of danger early.

Q2: Canary vs blue-green?
A2: Blue-green switches all traffic between two full environments at once (fast rollback, but all users are exposed at the switch). Canary shifts traffic gradually, limiting the number of exposed users.

Q3: What metrics do you watch for an AI canary?
A3: Technical: error rate, timeouts, p95 latency. Cost: tokens per request. Quality: judge score, user feedback, retry or override rate. Safety: guardrail block rate, refusal rate.

Q4: Why is stickiness important?
A4: Users should not see inconsistent behaviour mid-session, and it keeps per-user metrics clean. Hash the user id into a bucket.

Q5 (Hard): How would you canary a change that affects stored data, such as a new embedding model?
A5: Embeddings from different models are not comparable, so you cannot mix them in one index. Build a new index (v2 collection) in parallel, backfill it, then send canary traffic to query the v2 index while v1 stays on the old index. Compare retrieval quality (recall on a labelled set, click or answer feedback) and cost. Writes must go to both indexes (dual-write) until promotion. Keep the old index until the rollback window ends.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Changing model, prompt, retrieval settings or tools in production
- You have enough traffic to measure differences
- You have automated metrics and a fast rollback path

❌ Avoid when:
- Traffic is tiny (days to get a valid sample); use offline eval and shadow mode instead
- No quality metric exists: you would be flying blind
- The change cannot run side by side (a breaking schema change)

---

## 📊 Visual Diagram
```
                 +--------------------+
 users --------> |  Router (sticky)   |
                 +---------+----------+
                  95%      |       5%
                   v       |        v
              +---------+  |   +---------+
              | v1      |  |   | v2      |
              | stable  |  |   | canary  |
              +----+----+  |   +----+----+
                   |       |        |
                   v       v        v
              +--------------------------+
              | Metrics: errors, p95,    |
              | tokens, quality, feedback|
              +------------+-------------+
                           v
                 healthy? --yes--> 25% -> 50% -> 100%
                    |
                    no --> rollback to 0%
```

---

## 💰 Cost Impact
- A canary runs two versions at once, so you pay for both while it lasts, but v2 only gets a small share, so extra cost is small.
- It protects you from cost regressions: for example, if v2 uses 600 tokens per request vs 450 for v1 (+33%) and serves 100% of 1M requests per month, that is +150M tokens. Catching it at 5% prevents most of that.
- Track tokens per request as a gate metric (for example, block if above 1.3x v1).
- Optimise: automate rollback so a bad canary stops burning money, and keep canary windows short once the sample is enough.
- Token prices are provider specific and change; numbers here are illustrative.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Canary | Small-traffic trial of a new version | नए version का छोटा trial |
| Rollback | Return to the stable version | Stable version पर वापस |
| Sticky routing | Same user, same version | एक user, एक version |
| Gate | Thresholds that decide promote/rollback | Promote/rollback तय करने वाली सीमाएँ |
| Golden set | Fixed test questions with known answers | पक्के जवाबों वाले test सवाल |
| Shadow mode | Run v2 on copies of traffic, hide output | v2 चलाओ पर user को न दिखाओ |
| Traffic ladder | 5%, 25%, 50%, 100% steps | traffic बढ़ाने की सीढ़ी |

---

## ⚡ 3-Line Summary
English: Canary sends a small sticky slice of traffic to the new AI version and compares it with stable. Gate on errors, latency, tokens and, most important, quality. Roll back automatically when a threshold breaks.
Hindi: Canary नए AI version पर traffic का छोटा sticky हिस्सा भेजकर stable से तुलना करता है। Errors, latency, tokens और सबसे ज़रूरी quality पर gate लगाओ। Threshold टूटे तो अपने-आप rollback करो।

---

## ➡️ Next Topic
**529. AI System Monitoring** — the metrics, logs and alerts that feed canary gates and keep production healthy.
