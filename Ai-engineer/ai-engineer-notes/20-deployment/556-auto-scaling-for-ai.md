
---

# 556. Auto Scaling for AI
# हिंदी में: AI के लिए Auto Scaling

---

## 🔵 Simple Definition (English)
Auto scaling automatically adds or removes instances (ECS tasks, pods, SageMaker instances) when load changes. AI apps are I/O bound (waiting on LLMs), so CPU is often a poor signal; **requests per target**, concurrency, queue depth or latency usually work better. You set a minimum, a maximum, and a target value.

## 🔵 सरल परिभाषा (Hindi)
Auto scaling load बदलने पर instances (ECS tasks, pods, SageMaker instances) अपने आप बढ़ाता या घटाता है। AI apps I/O bound होते हैं (LLM का इंतज़ार), इसलिए CPU अक्सर खराब signal है; **requests per target**, concurrency, queue depth या latency बेहतर रहते हैं। आप minimum, maximum और target value तय करते हैं।

---

## 🔴 Problem it Solves
Fixed capacity is either too small at peak (timeouts, errors) or too big off-peak (wasted money). Traffic for AI products is spiky: a tariff rule change causes every broker to re-classify at once. Autoscaling matches capacity to demand.

## 🔴 यह क्यों बना? (Hindi)
Fixed capacity या तो peak पर कम पड़ती है (timeouts, errors) या off-peak में ज़्यादा (पैसा बर्बाद)। AI products का traffic spiky होता है: tariff rule बदलने पर सारे brokers एक साथ दोबारा classify करते हैं। Autoscaling capacity को demand से मिलाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose a metric that tracks load (RequestCountPerTarget, queue depth, p95 latency)
Step 2 → Set min and max capacity (min >= 2 for availability, max protects budget)
Step 3 → Target tracking: "keep ~40 requests per target"; the service computes needed count
Step 4 → Metric breaches target → scale out (add tasks), with a short cooldown
Step 5 → New task needs startup time (image pull, model/index load) before it is healthy
Step 6 → Load drops → scale in slowly (longer cooldown) to avoid flapping
Step 7 → Scale-in sends SIGTERM; app drains in-flight requests (graceful shutdown)
Step 8 → Optional scheduled scaling for known peaks (month-end filing)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → ऐसी metric चुनो जो load दिखाए (RequestCountPerTarget, queue depth, p95 latency)
Step 2 → min और max capacity तय करो (min >= 2 availability के लिए, max budget बचाता है)
Step 3 → Target tracking: "प्रति target ~40 requests रखो"; service ज़रूरी count निकालती है
Step 4 → Metric target पार करे → scale out (tasks जोड़ो), छोटा cooldown
Step 5 → नए task को startup समय चाहिए (image pull, model/index load)
Step 6 → Load घटे → धीरे scale in (लंबा cooldown) ताकि flapping न हो
Step 7 → Scale-in SIGTERM भेजता है; app चल रही requests पूरी करती है
Step 8 → Optional scheduled scaling ज्ञात peaks के लिए (month-end filing)
```

---

## 🟡 Real World Example
**Tariff Classification System**: Usually 2 tasks. On the last three days of each month, customs filing triples traffic. A scheduled action raises min to 4 on day 28, and target tracking on `ALBRequestCountPerTarget` (target 50) adds up to 12 tasks. An LLM provider rate limit of, say, 500 requests/min caps useful max capacity, so max is set accordingly.

**Zomato-style**: Dinner time (7-10 pm) spikes chat-assistant load; scheduled scaling pre-warms capacity before 7 pm.

## 🟡 Real Example Hindi mein
**Tariff System**: आम तौर पर 2 tasks। हर महीने के आख़िरी तीन दिन customs filing से traffic तीन गुना हो जाता है। Scheduled action 28 तारीख को min 4 कर देती है और `ALBRequestCountPerTarget` (target 50) पर target tracking 12 tasks तक जोड़ती है। LLM provider की rate limit (मान लो 500 requests/min) उपयोगी max capacity सीमित करती है, इसलिए max उसी हिसाब से रखा है।

**Zomato-style**: रात 7-10 बजे chat-assistant पर load बढ़ता है; scheduled scaling 7 बजे से पहले capacity तैयार रखती है।

---

## 💻 Code Example — Basic
```python
# Compute desired instance count from load (the math behind target tracking); runs offline
import math  # for ceiling


def desired_instances(current_load: float, target_per_instance: float, min_n: int = 2, max_n: int = 12) -> int:
    """Return how many instances are needed to keep each near the target."""
    if target_per_instance <= 0:  # guard against bad config
        raise ValueError("target_per_instance must be positive")  # clear error
    needed = math.ceil(current_load / target_per_instance)  # raw need
    return max(min_n, min(max_n, needed))  # clamp between min and max


if __name__ == "__main__":
    print(desired_instances(current_load=480, target_per_instance=50))  # 10 instances
    print(desired_instances(current_load=30, target_per_instance=50))  # clamped to min 2
    print(desired_instances(current_load=2000, target_per_instance=50))  # clamped to max 12
```

## 💻 Code Example — Advanced
```python
# Configure ECS service autoscaling with boto3: target tracking + scheduled scaling, with error handling
import asyncio  # async wrapper
from typing import Any  # typing

import boto3  # AWS SDK
from botocore.exceptions import ClientError  # AWS errors


def configure_scaling(cluster: str, service: str, alb_resource_label: str, region: str = "ap-south-1") -> dict[str, Any]:
    """Register the scalable target and attach policies."""
    aas = boto3.client("application-autoscaling", region_name=region)  # autoscaling client
    resource_id = f"service/{cluster}/{service}"  # identifies the ECS service
    try:
        aas.register_scalable_target(
            ServiceNamespace="ecs",  # ECS service
            ResourceId=resource_id,  # target service
            ScalableDimension="ecs:service:DesiredCount",  # we scale task count
            MinCapacity=2,  # always at least two for availability
            MaxCapacity=12,  # budget and provider rate-limit cap
        )
        policy = aas.put_scaling_policy(
            PolicyName="requests-per-target",  # policy name
            ServiceNamespace="ecs",
            ResourceId=resource_id,
            ScalableDimension="ecs:service:DesiredCount",
            PolicyType="TargetTrackingScaling",  # keep a metric near a target
            TargetTrackingScalingPolicyConfiguration={
                "TargetValue": 50.0,  # requests per task per minute (tune with load tests)
                "PredefinedMetricSpecification": {
                    "PredefinedMetricType": "ALBRequestCountPerTarget",  # I/O friendly metric
                    "ResourceLabel": alb_resource_label,  # app/<alb>/<id>/targetgroup/<tg>/<id>
                },
                "ScaleOutCooldown": 60,  # react fast to spikes
                "ScaleInCooldown": 300,  # shrink slowly
            },
        )
        aas.put_scheduled_action(
            ServiceNamespace="ecs",
            ScheduledActionName="month-end-prewarm",  # name
            ResourceId=resource_id,
            ScalableDimension="ecs:service:DesiredCount",
            Schedule="cron(0 6 28 * ? *)",  # 06:00 UTC on day 28 each month
            ScalableTargetAction={"MinCapacity": 4, "MaxCapacity": 12},  # raise the floor
        )
        return policy  # return policy details
    except ClientError as exc:
        raise RuntimeError(f"autoscaling setup failed: {exc.response['Error']['Message']}") from exc  # readable error


async def configure_scaling_async(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Async wrapper to call from an async deployment tool."""
    return await asyncio.to_thread(configure_scaling, *args, **kwargs)  # run in thread
```

---

## 🟠 FastAPI Integration
Expose a metric the scaler can use, and protect the instance from overload while a new one starts: a concurrency limiter returns 429/503 quickly instead of queueing forever.

```python
# FastAPI concurrency guard + in-flight gauge endpoint
import asyncio  # semaphore
from fastapi import FastAPI, HTTPException  # framework

app = FastAPI()  # app
MAX_INFLIGHT = 20  # per-instance concurrent LLM calls
sem = asyncio.Semaphore(MAX_INFLIGHT)  # limiter
inflight = 0  # current count


@app.post("/classify")  # route
async def classify(text: str) -> dict[str, str]:
    global inflight  # module-level counter
    if sem.locked():  # all slots busy
        raise HTTPException(status_code=503, detail="busy, retry", headers={"Retry-After": "2"})  # shed load
    async with sem:  # take a slot
        inflight += 1  # count
        try:
            await asyncio.sleep(0.1)  # replace with the LLM call
            return {"hs_code": "8517.13"}  # result
        finally:
            inflight -= 1  # release count


@app.get("/metrics-lite")  # simple gauge for a custom metric
async def metrics_lite() -> dict[str, int]:
    return {"inflight": inflight, "max": MAX_INFLIGHT}  # can be pushed to CloudWatch
```

---

## 🔗 LangChain / LangGraph Connection
Long LangGraph runs should not be scaled by web request count. Put runs on a queue (SQS, Redis) and scale workers on queue depth. Persistent checkpointers let any worker resume a run if a scaled-in worker is stopped.

```python
# Worker loop consuming a queue; scale the number of these workers on queue depth
import asyncio  # async loop


async def worker(queue: "asyncio.Queue[str]", graph_run) -> None:
    while True:  # run forever
        job = await queue.get()  # wait for a job
        try:
            await graph_run(job)  # run the LangGraph workflow
        finally:
            queue.task_done()  # mark finished
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Scaling on CPU for an I/O-bound LLM service
```python
# Wrong: CPU stays at 15% while all workers wait on the LLM, so it never scales out
metric = "ECSServiceAverageCPUUtilization"
# Correct: scale on load that reflects waiting work
metric = "ALBRequestCountPerTarget"  # or queue depth / custom in-flight gauge
```

❌ Mistake 2: No maximum, ignoring the provider rate limit
```python
# Wrong: 100 tasks all hit the LLM at once, 429 errors and a huge bill
max_capacity = 1000
# Correct: cap by provider limits and budget, then use a queue for the rest
max_capacity = 12
```

---

## 🧠 Tricky Interview Question
**Q**: "Traffic doubles suddenly. Autoscaling adds tasks, but errors continue for 3 minutes. Why, and how do you fix it?"

**Answer**: Scaling is not instant: metrics are aggregated per minute, new tasks must be provisioned, pull the image and load models or indexes, and pass health checks. Meanwhile existing tasks are overloaded. Fix: scale out aggressively and scale in slowly, keep headroom (target ~50-60% of capacity), smaller images and faster startup, scheduled pre-warming for known peaks, load shedding with 503 and Retry-After, and a queue for non-interactive work. Also check that the LLM provider rate limit is not the real bottleneck.

---

## ⚫ Interview Questions + Answers

Q1: What is horizontal vs vertical scaling?
A1: Horizontal adds more instances; vertical makes one instance bigger. Autoscaling usually means horizontal.

Q2: What is target tracking?
A2: A policy that keeps a metric (like requests per target) near a target value by adding or removing capacity automatically.

Q3: Why are cooldowns used?
A3: To avoid flapping: scaling again before the previous change has taken effect.

Q4: Why not scale on CPU for LLM API apps?
A4: They mostly wait on network I/O, so CPU stays low while requests queue; use concurrency, request count or latency.

Q5: How do you scale a GPU-hosted model endpoint?
A5: Scale on invocations per instance or GPU utilisation, account for slow startup (loading weights can take minutes), keep a minimum warm, use batching in the server to raise throughput per GPU, and consider queue-based async inference for bursts. Costs are high per instance, so scale-in must be careful but not too slow.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Traffic is variable or spiky
- You can make instances stateless and quick to start

❌ Avoid when:
- Constant steady load (fixed capacity plus savings plan is simpler)
- Startup takes very long and you cannot pre-warm
- Provider rate limit is the bottleneck, not your capacity

---

## 📊 Visual Diagram
```
 requests/target
   100 │              ╭───╮ ← spike
    50 │ ─ ─ target ─ ┼───┼ ─ ─ ─
     0 └────────────────────────▶ time
 tasks:  2     2    4    8    8    6    3    2
                scale-out fast ▲        ▼ scale-in slow
 min=2 ─────────────────────────────── max=12 (budget / rate-limit cap)
```

---

## 💰 Cost Impact
Autoscaling lets you pay for average rather than peak capacity. Example (illustrative): 2 tasks at about $0.048/hour each normally, 10 tasks for 6 peak hours a day is about $2.9 extra per day, versus about $11.5 per day if you ran 10 tasks around the clock. But autoscaling can also raise LLM spend: more instances means more parallel calls and tokens, so set max capacity and per-user limits. Token usage per request is unchanged; reduce it with caching, small models and `max_tokens`. Use Spot capacity for queue workers.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Auto scaling | Automatic capacity changes | अपने-आप capacity बदलना |
| Target tracking | Keep metric near target | Metric को target के पास रखना |
| Scale out / in | Add / remove instances | Instances जोड़ना / घटाना |
| Cooldown | Wait between scaling actions | दो scaling के बीच इंतज़ार |
| Queue depth | Pending jobs count | इंतज़ार में jobs की संख्या |
| Load shedding | Reject excess load early | ज़्यादा load जल्दी मना करना |

---

## ⚡ 3-Line Summary
English: Autoscaling adds and removes instances using a metric and target. For I/O-bound AI apps scale on requests per target, concurrency or queue depth, not CPU. Cap the maximum to respect provider rate limits and budget.
Hindi: Autoscaling metric और target के आधार पर instances जोड़ता-घटाता है। I/O-bound AI apps में CPU नहीं, requests per target, concurrency या queue depth पर scale करो। Provider rate limits और budget के लिए maximum सीमित रखो।

---

## ➡️ Next Topic
**557. Health Checks for AI** — telling the platform when an instance is alive and ready, so scaling and balancing work correctly.
