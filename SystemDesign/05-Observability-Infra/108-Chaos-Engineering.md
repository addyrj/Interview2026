# 108. Chaos Engineering
# हिंदी में: Chaos Engineering — जानबूझकर और नियंत्रित तरीके से सिस्टम में गड़बड़ी डालना (सर्वर बंद करना, देरी डालना), ताकि असली outage से पहले ही कमज़ोरियाँ पता चल जाएँ

---

## 🔵 Simple Definition (English)
**Chaos engineering** is the discipline of **running controlled experiments that inject failures** into a system (killing instances, adding network latency, dropping packets, failing a dependency, exhausting CPU or disk, simulating an AZ or region outage) to **verify the system behaves as expected** and to **discover weaknesses before they cause real outages**.
It follows the scientific method: **hypothesis → experiment → observe → learn → fix**, starting small and limiting the **blast radius**.

## 🔵 सरल परिभाषा (Hindi)
Chaos engineering में हम जानबूझकर, नियंत्रित तरीके से गड़बड़ी करते हैं — कोई सर्वर बंद, नेटवर्क में देरी, कोई dependency फ़ेल — और देखते हैं कि सिस्टम वैसे ही संभलता है या नहीं जैसा हम सोचते हैं।
मक़सद: असली outage आने से पहले ही कमज़ोरियाँ ढूँढकर ठीक करना। छोटे से शुरू करो, असर (blast radius) सीमित रखो।

---

## 🔴 Problem it Solves
We **design** for failure (retries, timeouts, circuit breakers, failover, graceful degradation), but:
- Failover scripts that were **never exercised** often **don't work** when needed.
- Timeouts are **missing or wrong** in some client library.
- A "non-critical" dependency is actually in the **critical path**.
- Alerts don't fire, dashboards are misleading, runbooks are outdated, and on-call doesn't know the steps.
- Hidden **single points of failure** (a shared config service, DNS, a cron leader).

Real outages are expensive teachers. Chaos engineering finds these issues **on your schedule**, under control, with the team ready.

## 🔴 यह क्यों बना? (Hindi)
हम retry, timeout, failover सब बनाते हैं, पर बिना चलाए failover script अक्सर ज़रूरत पर काम नहीं करती; कहीं timeout ही नहीं है; "ग़ैर-ज़रूरी" service असल में ज़रूरी रास्ते में है; alerts नहीं बजते; runbook पुराना है।
Chaos engineering ये कमियाँ अपने तय समय पर, नियंत्रण में, टीम के तैयार रहते ढूँढ लेता है।

---

## 🟢 How it Works — Step by Step

### The experiment loop

```
1. Define STEADY STATE (measurable business/SLI): orders/min, checkout success %, p99 latency
2. HYPOTHESIS: "If one payment-service pod is killed, checkout success stays ≥ 99.5% and p99 < 1s"
3. Plan the experiment: failure type, target, scope (1 pod, 1% traffic, staging first), duration,
   ABORT CONDITIONS (stop if success < 98%), rollback plan, who's watching
4. RUN: inject the failure (tooling), observe dashboards/traces/alerts
5. ANALYZE: hypothesis held? What broke? Did alerts fire? Was the runbook right?
6. FIX weaknesses (code, config, alerts, runbooks) → re-run → automate as regular test
```

### Types of failures to inject

```
Infrastructure:  kill pod/instance/container, terminate node, fill disk, CPU/memory stress,
                 clock skew, reboot
Network:         latency (+500 ms), packet loss, DNS failure, partition between services/AZs,
                 bandwidth limits
Dependency:      make DB/Redis/Kafka unavailable or slow, third-party API returns 500/timeouts,
                 expired certificate, throttling (429)
Application:     exceptions in a code path, bad config push, feature-flag misfire
Region/AZ:       evacuate an AZ or region (game day)
People/process:  game days — simulated incident with on-call; test runbooks & communication
```

### Start small, grow carefully (blast radius)

```
Local/dev → staging → production with tiny scope (1 pod, 1% of users, internal users) → wider
Run during business hours with engineers watching (not 2 AM)
Automatic abort on SLO breach; feature flags / mesh rules to stop instantly
Communicate: announce experiments; get buy-in; never surprise the on-call team
Prerequisites: good observability (you must SEE the effect) and basic resilience already in place
```

### Tools

```
Netflix Chaos Monkey (random instance termination) & the Simian Army
AWS Fault Injection Service (FIS): stop EC2/ECS tasks, AZ power interruption, API throttling, latency
Gremlin (commercial), LitmusChaos & Chaos Mesh (Kubernetes), Toxiproxy (network faults for testing),
Istio fault injection (delay/abort HTTP), Steadybit, chaos-toolkit
```

### What you typically discover
```
- Missing timeouts → threads/connections pile up when a dependency is slow
- Retry storms after a dependency recovers
- Health checks that mark everything unhealthy (or nothing)
- Failover that takes 10 min instead of 1 (DNS caching, connection pools)
- Alerts too late/noisy; dashboards missing key panels
- Cache-down → DB overload (stampede)
- Single-AZ resources hiding in "multi-AZ" setups
```

## 🟢 कैसे काम करता है? (Hindi)
1. Steady state तय करो (orders/मिनट, checkout success %, p99) और परिकल्पना बनाओ: "एक payment pod बंद हो तो भी success ≥ 99.5% रहेगा"।
2. योजना: कौन-सी गड़बड़ी, कितना दायरा (1 pod, 1% ट्रैफ़िक), कब रुकना है (abort condition), कौन देख रहा है।
3. गड़बड़ी डालो (pod kill, देरी, dependency बंद, AZ बंद) और dashboards, traces, alerts देखो।
4. परिकल्पना सही निकली? क्या टूटा? alerts बजे? runbook सही था? — फिर ठीक करो और दोबारा चलाओ।
5. छोटे से शुरू करो (staging → production में थोड़ा), दिन के समय, टीम को बताकर; पहले अच्छी monitoring ज़रूरी है।

---

## 🟡 Real World Example

**Netflix Chaos Monkey (2011)** — randomly terminates production instances during business hours, forcing every service to tolerate instance loss. Later "Chaos Kong" simulated entire AWS region failures. This practice is why Netflix stayed up during real AWS outages that took down others.

**Amazon GameDay** — Amazon runs GameDays that simulate data-center failures to test recovery processes and people. Jesse Robbins ("Master of Disaster") pioneered this.

**AWS Fault Injection Service** — AWS productized chaos experiments, including AZ power interruption scenarios, for customers.

**LinkedIn, Slack, Uber, Capital One** — run regular chaos experiments and game days. Slack's "Disasterpiece Theater" exercises test failure scenarios with the on-call teams.

**Indian companies before sale events** — Flipkart (Big Billion Days) and Hotstar (IPL) run extensive load and failure drills, killing nodes and degrading dependencies under load, weeks before peak events.

## 🟡 Real Example Hindi में
Netflix का Chaos Monkey (2011) दिन में production के सर्वर random बंद करता है; Chaos Kong पूरा AWS region बंद करने का अभ्यास करता है — इसलिए असली AWS outage में Netflix चलता रहा।
Amazon "GameDay" में डेटा सेंटर गिरने का अभ्यास करता है। Flipkart और Hotstar बड़े events से हफ़्तों पहले load के साथ सर्वर बंद करके टेस्ट करते हैं।

---

## 🟠 My Stack Example

### Experiment doc (template)
```
Title: Payment service pod failure during checkout
Steady state: checkout success ≥ 99.5%, p99 < 1s, orders/min within ±10% of baseline
Hypothesis: killing 1 of 4 payment pods causes no user-visible errors (retries + readiness + LB)
Scope: production, 1 pod, 10 minutes, business hours, on-call aware
Abort if: checkout success < 98% for 2 min OR p99 > 3s → stop experiment, scale up
Result: ✅/❌ + findings + action items (owner, due date)
```

### Kubernetes: kill a pod / inject latency with Chaos Mesh
```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata: { name: kill-one-payment-pod, namespace: chaos }
spec:
  action: pod-kill
  mode: one
  selector: { namespaces: [prod], labelSelectors: { app: payment-api } }
---
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata: { name: redis-latency, namespace: chaos }
spec:
  action: delay
  mode: all
  selector: { namespaces: [prod], labelSelectors: { app: order-api } }
  direction: to
  externalTargets: ["redis.prod.svc.cluster.local"]
  delay: { latency: "300ms", jitter: "50ms" }
  duration: "5m"
```

### Istio fault injection (no extra tool)
```yaml
http:
  - match: [{ headers: { x-chaos: { exact: "true" } } }]     # only internal test traffic
    fault: { abort: { percentage: { value: 100 }, httpStatus: 503 } }
    route: [{ destination: { host: reco-service } }]
```

### Local/dev: Toxiproxy to test timeouts & fallbacks (Node integration tests)
```js
// docker run -p 8474:8474 -p 26379:26379 ghcr.io/shopify/toxiproxy
import Toxiproxy from 'toxiproxy-node-client';
const toxi = new Toxiproxy('http://localhost:8474');
const proxy = await toxi.createProxy({ name: 'redis', listen: '0.0.0.0:26379', upstream: 'redis:6379' });
await proxy.addToxic({ name: 'slow', type: 'latency', attributes: { latency: 2000 } });
// now run: GET /api/v1/menu/42 → expect response < 600ms from DB fallback (cache timeout works)
const t0 = Date.now(); const r = await fetch('http://localhost:3000/api/v1/menu/42');
assert(r.ok && Date.now() - t0 < 600);
```

### AWS Fault Injection Service (ECS task stop)
```json
{
  "description": "Stop 30% of order-api tasks",
  "targets": { "tasks": { "resourceType": "aws:ecs:task", "selectionMode": "PERCENT(30)",
                          "parameters": { "cluster": "prod", "service": "order-api" } } },
  "actions": { "stop": { "actionId": "aws:ecs:stop-task", "targets": { "Tasks": "tasks" } } },
  "stopConditions": [{ "source": "aws:cloudwatch:alarm", "value": "arn:aws:cloudwatch:...:alarm:checkout-success-low" }]
}
```

### Game day agenda (2 hours)
```
1. Scenario briefing (e.g., "Redis primary fails during dinner peak")      10 min
2. Inject failure; on-call responds using runbook (others observe)          45 min
3. Recover; measure detection time, mitigation time, user impact            15 min
4. Retro: what surprised us? alert gaps? runbook fixes? action items        30 min
```

### Mobile/web chaos
```
- Test apps under poor networks (Network Link Conditioner, Android emulator throttling, Charles)
- Simulate API 500s/timeouts via a debug proxy or feature flag → verify cached UI, retry, error states
```

---

## ⚫ Interview Questions + Answers

**Q1: What is chaos engineering?**
A1: Experimenting on a system by deliberately injecting realistic failures (instance or pod termination, latency, errors, network partitions, resource exhaustion, AZ or region loss) under controlled conditions, to build confidence that it withstands turbulent production conditions. It follows a scientific approach: define the steady state, hypothesize, run experiments with a limited blast radius and abort conditions, observe, learn, and fix weaknesses.

**Q2: How do you run chaos experiments safely in production?**
A2: Have solid observability and basic resilience first. Define steady-state metrics and automatic abort conditions tied to SLOs. Start in staging, then production with a minimal blast radius (one instance, a small percentage of traffic, internal users). Run during business hours with engineers watching and stakeholders informed. Have a rollback or kill switch ready, and expand scope gradually. Document results and track fixes.

**Q3: What's the difference between chaos engineering and regular testing?**
A3: Traditional tests verify known expected behaviour of components, usually in controlled environments. Chaos engineering explores emergent behaviour of the whole system under real-world failure conditions (often in production, with real traffic, configurations and dependencies), revealing unknowns like missing timeouts, retry storms, broken failover, bad alerts and human process gaps. It complements unit, integration and load tests.

**Q4: What is a game day?**
A4: A planned exercise where the team simulates a significant failure scenario (database failover, region evacuation, dependency outage), often in production or a production-like environment, and practices detection, response, communication and recovery using real runbooks and tools. It tests both systems and people. It ends with a retrospective and action items: improved alerts, runbooks, automation and architecture fixes.

**Q5: Give examples of weaknesses chaos experiments typically reveal.**
A5: Missing or too-long timeouts that cause resource exhaustion when a dependency is slow; retry storms; cache failures overloading the database; health checks that cause restart storms; failover slower than the RTO because of DNS caching or stale connection pools; alerts that don't fire or fire too late; hidden single points of failure (one NAT gateway, a config service, a leader cron); and runbooks with outdated steps.

---

## 🔷 Trade-offs
✅ Advantages:
- Finds weaknesses before customers do; validates resilience, alerts, runbooks; builds on-call confidence.

❌ Disadvantages:
- Risk of causing real impact if poorly controlled; needs maturity (observability, rollback).
- Organizational resistance; time investment; requires follow-through on findings.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Chaos engineering | Controlled failure experiments | नियंत्रित गड़बड़ी के प्रयोग |
| Steady state | Normal measurable behaviour | सामान्य नापने लायक हालत |
| Hypothesis | Expected outcome under failure | अपेक्षित नतीजा |
| Blast radius | Scope of impact | असर का दायरा |
| Abort condition | When to stop the experiment | प्रयोग रोकने की शर्त |
| Fault injection | Introducing errors/latency | जानबूझकर ग़लती/देरी डालना |
| Game day | Simulated incident exercise | नक़ली incident अभ्यास |
| Chaos Monkey | Netflix tool killing instances | Netflix का सर्वर बंद करने वाला टूल |
| Runbook | Step-by-step response guide | कदम-दर-कदम निर्देश |

---

## ⚡ 3-Line Summary
**English:**
1. Chaos engineering injects controlled failures to verify resilience and uncover hidden weaknesses before real outages.
2. Method: steady state → hypothesis → small-blast-radius experiment with abort conditions → observe → fix → automate.
3. Tools: Chaos Monkey, AWS FIS, Chaos Mesh/Litmus, Gremlin, Toxiproxy, Istio faults; complement with game days.

**Hindi:**
1. Chaos engineering = नियंत्रित गड़बड़ी डालकर देखना कि सिस्टम संभलता है या नहीं, और छिपी कमियाँ ढूँढना।
2. तरीका: सामान्य हालत → परिकल्पना → छोटा प्रयोग (रुकने की शर्त के साथ) → देखो → ठीक करो।
3. टूल: Chaos Monkey, AWS FIS, Chaos Mesh, Gremlin, Toxiproxy; साथ में game days।

---

## ➡️ Next Topic Suggestion
**109. Infrastructure as Code (Terraform)** — Recovering and rebuilding environments quickly (and identically across regions) requires infrastructure defined in code. Next: Terraform, covering providers, state, modules, plan/apply, and safe workflows.
