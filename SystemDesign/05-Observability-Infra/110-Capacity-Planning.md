# 110. Capacity Planning
# हिंदी में: Capacity Planning — आने वाले ट्रैफ़िक (growth, सेल, IPL) के लिए पहले से हिसाब लगाना कि कितने सर्वर, DB, cache, bandwidth चाहिए, ताकि सिस्टम न गिरे और पैसा भी बर्बाद न हो

---

## 🔵 Simple Definition (English)
**Capacity planning** is the process of **estimating the resources a system needs** (compute, memory, storage, database throughput, network, queue capacity) to meet **expected demand** with **acceptable performance and headroom**, at **reasonable cost**. It combines **traffic forecasting**, **per-unit resource costs** (from measurements and load tests), **bottleneck analysis**, **headroom/redundancy rules**, and **lead times** (how long it takes to add capacity).

## 🔵 सरल परिभाषा (Hindi)
Capacity planning = आगे आने वाले ट्रैफ़िक के लिए पहले से हिसाब — कितने सर्वर, कितना बड़ा DB, Redis में कितनी memory, कितनी bandwidth।
इसमें ट्रैफ़िक का अनुमान, एक सर्वर कितना संभालता है (load test से), सबसे कमज़ोर कड़ी (bottleneck), और अतिरिक्त क्षमता (headroom) शामिल है — ताकि सिस्टम न गिरे और ज़्यादा पैसा भी न लगे।

---

## 🔴 Problem it Solves
- **Under-provisioning:** the Diwali sale starts, the DB hits 100% CPU, checkout fails, and revenue and trust are lost. Autoscaling can't save you if the **database**, **third-party limits** or **cloud quotas** are the bottleneck, or if scaling takes 10 minutes and the spike takes 10 seconds.
- **Over-provisioning:** paying for 5× the servers year-round "just in case".
- **Lead times:** bigger DB instances, reserved capacity, quota increases, new regions, and vendor limit increases (payment gateways, SMS providers) take **days or weeks**.
- **Storage growth:** a disk fills up at 3 AM because nobody tracked growth.

Capacity planning turns **"will it hold?"** into **numbers and plans**.

## 🔴 यह क्यों बना? (Hindi)
कम क्षमता: Diwali सेल में DB 100% और checkout फ़ेल — autoscaling DB या बाहरी सीमाओं (payment gateway, SMS) को नहीं बचा सकता। ज़्यादा क्षमता: साल भर 5 गुना सर्वर का पैसा। और बड़ा DB, quota बढ़ाना, vendor सीमा बढ़ाना — इसमें दिनों से हफ़्तों लगते हैं।
Capacity planning "चलेगा या नहीं?" को संख्याओं और योजना में बदल देता है।

---

## 🟢 How it Works — Step by Step

### The process

```
1. FORECAST DEMAND
   - Organic growth trend (e.g. +8% MoM orders), seasonality (dinner peak, weekends, festivals)
   - Planned events: sale, marketing campaign, IPL final, new city launch, TV ad
   - Translate business metrics → technical: 1 order ≈ 25 API calls, 3 DB writes, 2 push notifications
2. MEASURE PER-UNIT COST (capacity model)
   - Load test: 1 API pod (1 vCPU) handles ~400 RPS at p99 < 300 ms
   - DB: ~5,000 QPS at 60% CPU on db.r7g.xlarge; Redis: 80k ops/s per shard
3. FIND BOTTLENECKS across the whole path (LB, app, DB, cache, queue, 3rd-party APIs, quotas)
4. ADD HEADROOM & REDUNDANCY
   - Target utilization at peak ≤ 60–70% (latency knee, Topic 18)
   - N+1 / survive loss of one AZ (each AZ must carry 50% if one of 3 fails → plan for it)
5. PLAN ACTIONS & LEAD TIMES: autoscaling limits, pre-scaling schedule, DB upgrade dates, quota
   requests, vendor limit increases, reserved instances/savings plans for baseline
6. VALIDATE with load tests at target scale; monitor actual vs forecast; iterate (monthly/quarterly)
```

### Worked example (back-of-envelope): festive sale for a food app

```
Normal peak (dinner):
  DAU 2M, 1.5 orders/user/week → ~430k orders/day; dinner peak hour ≈ 15% → 65k/hour ≈ 1,080/min ≈ 18/s
Sale-day forecast:           5× normal peak → 90 orders/s
API calls per order journey: ~25 (browse, menu, cart, checkout, tracking polls)
                             → 90 × 25 = 2,250 RPS from ordering + browsing traffic ×3 → ~7,000 RPS peak
App pods:                    400 RPS per pod at 70% target → 7,000 / (400 × 0.7) ≈ 25 pods
                             + survive 1 AZ loss (3 AZs): 25 × 1.5 ≈ 38 pods → set HPA max ≥ 45
DB writes:                   90 orders/s × 3 writes = 270 writes/s (fine)
DB reads:                    7,000 RPS × 1.5 queries with 85% cache hit → ~1,600 QPS → fits r7g.xlarge
                             + replicas for headroom; pool size: 45 pods × 10 conns = 450 → PgBouncer!
Redis:                       7,000 RPS × 3 ops = 21k ops/s → 1–2 shards OK; memory check for keys
Kafka:                       order events 90/s + location pings: 20k riders / 3 s = 6.7k msg/s →
                             partitions: target ~5 MB/s per partition → small; choose 12–24 for parallelism
Push notifications:          90 orders/s × 4 pushes = 360/s → check FCM/APNs & SMS provider limits
Payment gateway:             90 TPS → confirm contracted TPS with gateway; add fallback gateway
Bandwidth:                   7,000 RPS × 15 KB = 105 MB/s ≈ 840 Mbps → CDN for images, gzip
Storage growth:              430k orders/day × 2 KB = ~0.9 GB/day + indexes → ~400 GB/year → plan disk
```

### Key formulas
```
Instances = peak RPS / (RPS per instance × target utilization)
Little's Law: concurrency = throughput × latency  (Topic 18) → pool sizes, worker counts
Storage = daily growth × retention × replication factor × (1 + index/overhead %)
Peak factor = peak / average (often 2–5× daily; events 5–20×)
```

### What autoscaling does and doesn't cover
```
Covers: stateless app tiers with gradual ramps (minutes)
Doesn't cover: sudden spikes faster than scale-up time, stateful DBs, cloud quotas/limits
(vCPU quotas, IPs, NAT throughput), third-party rate limits, connection limits, warm caches
→ PRE-SCALE before known events; raise quotas early; load test the real path
```

### Cost side
```
Baseline (always-on) → reserved instances / savings plans (30–70% cheaper)
Variable peaks       → on-demand autoscaling; spot instances for batch/stateless workers
Right-size regularly (CPU 10% all month = oversized); delete idle resources
```

## 🟢 कैसे काम करता है? (Hindi)
1. माँग का अनुमान: growth trend, रात के खाने/त्योहार का पीक, सेल या IPL; business metric को technical में बदलो (1 order ≈ 25 API कॉल)।
2. Load test से नापो: एक pod कितनी RPS, DB कितनी QPS, Redis कितने ops संभालते हैं।
3. पूरे रास्ते में bottleneck ढूँढो — DB, cache, queue, payment gateway, cloud quota।
4. Headroom रखो: पीक पर 60-70% से ज़्यादा उपयोग नहीं, और एक AZ गिरने पर भी चले।
5. कार्य योजना: HPA max, पहले से scale-up, DB upgrade, quota/vendor सीमा बढ़ाना — फिर उसी स्केल पर load test और असली बनाम अनुमान की तुलना।

---

## 🟡 Real World Example

**Hotstar / JioCinema (IPL, Cricket World Cup)** — planned for 25M+ concurrent viewers: months of forecasting, load tests with tens of millions of simulated users, pre-provisioning compute and CDN capacity, and "panic mode" switches to shed features. They pre-scale before toss time because autoscaling can't react to a ~10× surge in seconds.

**Flipkart Big Billion Days** — capacity planning starts months ahead: traffic models per category, end-to-end load tests in production-like environments, cloud and data-center capacity reservations, and payment partner TPS agreements.

**Twitter "fail whale" era** — under-planned capacity during spikes (World Cup, elections) led to frequent outages until capacity models and architecture caught up.

**AWS / cloud quotas** — many teams discover during an event that they hit account limits (EC2 vCPU quota, Lambda concurrency, NAT gateway bandwidth) that take time to raise. Capacity planning includes quota review.

## 🟡 Real Example Hindi में
Hotstar IPL के लिए महीनों पहले योजना बनाता है — करोड़ों नक़ली यूज़र्स से load test, पहले से सर्वर और CDN क्षमता, और toss से पहले pre-scaling, क्योंकि autoscaling अचानक 10 गुना भीड़ पर सेकंडों में काम नहीं करता।
Flipkart बिग बिलियन डेज़ की तैयारी महीनों पहले करता है — payment partners से TPS समझौते तक। कई टीमें event के दिन पाती हैं कि AWS quota ख़त्म हो गया।

---

## 🟠 My Stack Example

### Load test the real journey with k6 (to get per-unit capacity)
```js
import http from 'k6/http';
import { check, sleep } from 'k6';
export const options = {
  scenarios: {
    sale_peak: { executor: 'ramping-arrival-rate', startRate: 100, timeUnit: '1s',
                 preAllocatedVUs: 2000, stages: [{ target: 2000, duration: '10m' }, { target: 7000, duration: '20m' }, { target: 7000, duration: '20m' }] },
  },
  thresholds: { http_req_failed: ['rate<0.005'], 'http_req_duration{name:checkout}': ['p(99)<800'] },
};
export default function () {
  http.get(`${__ENV.API}/api/v1/home?lat=19.07&lng=72.87`, { tags: { name: 'home' } });
  http.get(`${__ENV.API}/api/v1/restaurants/42/menu`, { tags: { name: 'menu' } });
  if (Math.random() < 0.15) {
    const r = http.post(`${__ENV.API}/api/v1/orders`, JSON.stringify({ restaurantId: 42, items: [{ id: 7, qty: 1 }] }),
      { headers: { 'Content-Type': 'application/json', 'Idempotency-Key': `${__VU}-${__ITER}` }, tags: { name: 'checkout' } });
    check(r, { created: (x) => x.status === 201 });
  }
  sleep(1);
}
```
Watch during the test: pod CPU, p99 per route, DB CPU/IOPS/connections, Redis ops and memory, Kafka lag, error rates. Find the first saturation point.

### Capacity sheet (keep it in the repo / wiki)
```
Component        Unit capacity (measured)        Peak forecast    Needed (70% util + AZ loss)   Action / owner / date
API pods         400 RPS / pod                   7,000 RPS        38 pods (HPA max 45)          raise HPA max; vCPU quota
Postgres primary 5k QPS @ 60% CPU (r7g.xlarge)   1.6k QPS         OK                            add 1 read replica
PgBouncer        —                               450 client conns pool 60 server conns          deploy before sale
Redis            80k ops/s/shard                 21k ops/s        1 shard + replica OK          verify memory 6 GB
Kafka            —                               7k msg/s         24 partitions OK              —
Payment gateway  contracted 100 TPS              90 TPS           ⚠ near limit                  ask 200 TPS + backup gateway
SMS provider     50/s                            40/s             ⚠                             raise limit / WhatsApp OTP
```

### Pre-scale on a schedule (before known peaks)
```bash
# Kubernetes: raise minReplicas before the sale; revert after
kubectl patch hpa order-api -n prod -p '{"spec":{"minReplicas":30,"maxReplicas":60}}'
# AWS ECS: scheduled scaling action
aws application-autoscaling put-scheduled-action --service-namespace ecs \
  --resource-id service/prod/order-api --scalable-dimension ecs:service:DesiredCount \
  --scheduled-action-name diwali-prescale --schedule "at(2026-11-01T17:30:00)" \
  --scalable-target-action MinCapacity=30,MaxCapacity=60
```

### Storage growth monitoring (Postgres)
```sql
SELECT relname, pg_size_pretty(pg_total_relation_size(relid)) AS total
FROM pg_catalog.pg_statio_user_tables ORDER BY pg_total_relation_size(relid) DESC LIMIT 10;
-- alert when free storage < 20% or growth rate predicts full in < 30 days (CloudWatch FreeStorageSpace + forecast)
```

### Mobile considerations
```
- App release / push campaign = traffic spike → coordinate with backend (staggered push sends)
- App polling intervals multiply load: 1M active users polling every 10 s = 100k RPS!
  → use push/WebSocket, longer intervals, jitter
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you do capacity planning for a system?**
A1: Forecast demand (growth trends, seasonality, planned events) and translate business volumes into technical load (requests, queries, messages, storage). Measure per-unit capacity of each component via load tests and production metrics. Identify bottlenecks across the full request path, including third-party and cloud limits. Compute required capacity with target utilization (around 60–70% at peak) and redundancy (survive losing an AZ). Account for lead times, pre-scale for known spikes, validate with load tests at target scale, and track actual vs forecast continuously.

**Q2: Why isn't autoscaling enough?**
A2: Autoscaling reacts after load rises and takes minutes (instance boot, image pull, warm-up), while some spikes happen in seconds (a push notification blast, IPL toss). It also mostly applies to stateless tiers. Databases, caches, connection limits, cloud quotas, third-party API limits and Kafka partitions don't autoscale instantly or at all. Planning, pre-scaling, quota increases and architectural headroom are still required.

**Q3: What headroom would you keep and why?**
A3: Typically plan peak utilization around 60–70% of tested capacity, because latency rises sharply near saturation (queueing) and there needs to be room for traffic variance, failover and retries. Also plan for redundancy: with 3 AZs, the remaining 2 must handle the full load if one fails, so each AZ should normally run at or below about 66% of its capacity. Critical event days may warrant even more headroom.

**Q4: How do you estimate the number of servers needed for a given RPS?**
A4: Measure (via load test) how many requests per second one instance handles within the latency SLO, then divide peak RPS by (per-instance RPS × target utilization) and add redundancy. For example, 7,000 RPS ÷ (400 × 0.7) ≈ 25, then about 38 to tolerate an AZ loss. Cross-check downstream limits: the DB connections those instances open, DB QPS, cache ops, and external API TPS. Use Little's Law (concurrency = throughput × latency) to size pools and workers.

**Q5: You expect 10× traffic for a one-day sale next month. What's your plan?**
A5: Forecast per-endpoint traffic and the order rate. Load test the full purchase journey at 10–12× in a production-like environment to find bottlenecks. Fix those (indexes, caching hot items, PgBouncer, read replicas, queueing non-critical work). Raise cloud quotas and vendor limits (payment, SMS, push), and add fallback providers. Pre-scale app tiers and warm caches before the start, and set up a waiting room or rate limits and feature kill switches (graceful degradation). Freeze risky deploys, staff a war room with dashboards and runbooks, and run a game day rehearsal. After the event, compare actual vs forecast to improve the model.

---

## 🔷 Trade-offs
✅ Good planning: reliability during peaks, controlled costs, fewer emergencies, informed purchasing (reservations).
❌ Effort: forecasting is uncertain; load tests are costly/complex; models drift as code changes.
❌ Over-headroom wastes money; under-headroom risks outages → revisit regularly with data.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Capacity planning | Estimating needed resources | ज़रूरी resources का अनुमान |
| Forecast | Predicted future demand | भविष्य की माँग का अनुमान |
| Peak factor | Peak / average traffic | पीक और औसत का अनुपात |
| Headroom | Spare capacity | अतिरिक्त क्षमता |
| Target utilization | Max planned usage (60–70%) | योजनाबद्ध अधिकतम उपयोग |
| Bottleneck | Limiting component | रुकावट वाला हिस्सा |
| Lead time | Time to add capacity | क्षमता बढ़ाने में लगने वाला समय |
| Pre-scaling | Scaling before expected spike | भीड़ से पहले बढ़ाना |
| Load test | Simulated traffic test | नक़ली ट्रैफ़िक से जाँच |
| Quota | Cloud/vendor usage limit | cloud/vendor की सीमा |

---

## ⚡ 3-Line Summary
**English:**
1. Capacity planning = forecast demand → measure per-unit capacity (load tests) → find bottlenecks → size with headroom and redundancy.
2. Autoscaling isn't enough: pre-scale for spikes, plan DB/cache/queue/quota/vendor limits with lead times.
3. Keep a capacity sheet, monitor actual vs forecast, right-size for cost, and rehearse big events.

**Hindi:**
1. Capacity planning = माँग का अनुमान → load test से एक इकाई की क्षमता → bottleneck → headroom के साथ आकार।
2. Autoscaling काफ़ी नहीं: भीड़ से पहले scale, DB/cache/quota/vendor सीमाएँ पहले से।
3. Capacity sheet रखो, असली बनाम अनुमान देखो, ख़र्च ठीक रखो, बड़े events का अभ्यास करो।

---

## ➡️ Next Topic Suggestion
**🎉 Observability & Infra complete!** Next: **111. URL Shortener** in `06-Backend-Design-Problems/`. Now combine everything into full system design interview answers, starting with the classic URL shortener: requirements, estimation, API, data model, ID generation, caching and scaling.
