# 07. Revision Sheet — Auth, Security + Distributed Systems
# हिंदी में: Auth, Security + Distributed Systems की Revision Sheet — JWT, OAuth2, OIDC, sessions, RBAC, rate limiting algorithms, API versioning, idempotency; CAP, consistency, 2PC, Saga, CQRS, event sourcing; circuit breaker, retry + jitter, bulkhead, load shedding, timeouts, health checks, failover; queues, Kafka, DLQ, EDA; locks, leader election, quorum, clocks; service discovery, API gateway, BFF, mesh, gRPC, WebSocket at scale; और observability (Topics 54–110)

---

## 🔵 Simple Definition (English)
A **compact refresher** for `03-Auth-Security-API/` (54–64), `04-Distributed-Systems/` (65–99) and the essentials of `05-Observability-Infra/` (100–110). These topics show up as **deep dives and follow-ups** in nearly every design: "How do you authenticate?", "What if the payment service times out?", "How do you avoid double charges?", "What's your consistency model?", "How do services find each other?", "How would you know it's broken?"

## 🔵 सरल परिभाषा (Hindi)
`03-Auth-Security-API/` (54–64), `04-Distributed-Systems/` (65–99) और `05-Observability-Infra/` (100–110) की संक्षिप्त दोहराई — लगभग हर design की गहराई और follow-ups में आते हैं: "auth कैसे?", "payment service timeout हो तो?", "दो बार charge कैसे रोकें?", "consistency model क्या?", "services एक-दूसरे को कैसे ढूँढें?", "टूटा है यह कैसे पता चलेगा?"।

---

## 🔴 Problem it Solves
Distributed-systems and security follow-ups separate mid-level from senior answers. You need **precise mechanisms and trade-offs** at your fingertips (token expiry and rotation, idempotency keys, saga compensation, at-least-once delivery and dedupe, retry with jitter, quorum math), plus **when not to use** a pattern (2PC across microservices, event sourcing for simple CRUD).

## 🔴 यह क्यों बना? (Hindi)
Distributed systems और security के follow-ups से mid-level और senior जवाब अलग दिखते हैं — सटीक तरीके और trade-offs तुरंत याद होने चाहिए (token expiry/rotation, idempotency keys, saga compensation, at-least-once + dedupe, jitter वाला retry, quorum का गणित), और कब कोई pattern इस्तेमाल न करें (microservices में 2PC, साधारण CRUD पर event sourcing)।

---

## 🟢 How it Works — Step by Step (the cheat sheet)

### Auth & API safety (54–64)

```
JWT (54): signed token (header.payload.signature); stateless verification (RS256/ES256 with public keys/JWKS);
  short-lived access (5–15 min) + refresh token (rotate, reuse detection); can't revoke instantly → short TTL,
  denylist for emergencies; never store secrets in payload (it's only base64).
OAuth 2.0 (55): delegated authorization; Authorization Code + PKCE for apps/SPAs; client credentials for
  service-to-service; scopes; never implicit flow; tokens from authorization server.
OIDC (56): identity layer on OAuth → ID token (who the user is), userinfo, discovery; "Login with Google".
Session vs token (57): server sessions (cookie + Redis store, easy revoke, CSRF care) vs tokens (stateless,
  scale easily, harder revoke). Web: HttpOnly cookies; mobile: Keychain/Keystore.
RBAC (58): roles → permissions; check on every request server-side; ABAC/ReBAC for finer rules (owner,
  tenant, relationships); least privilege.
Rate limiting (59): protect services & fairness; per user/IP/API key; return 429 + Retry-After; distributed
  via Redis (atomic Lua) or gateway.
Token bucket (60): bucket refills at rate r, capacity b → allows bursts up to b; most common.
Leaky bucket (61): queue drains at constant rate → smooths bursts; adds queuing delay.
Sliding window (62): log (exact, memory-heavy) or counter (weighted current+previous window) → avoids fixed-
  window boundary spikes.
API versioning (63): URL (/v2), header, or date-based; additive changes; deprecation windows; mobile old versions!
Idempotency (64): client sends Idempotency-Key; server stores key → result; retries return same result;
  essential for payments/orders; scope by user + endpoint; TTL; handle concurrent same-key requests.
```

### Consistency & transactions (65–72)

```
CAP (65): during a network Partition, choose Consistency or Availability; PACELC adds: Else, Latency vs
  Consistency. CP: banking ledger; AP: social likes/feeds, shopping cart (merge later).
Strong consistency (66): reads see latest write (single leader, quorum reads/writes, consensus like Raft).
Eventual consistency (67): replicas converge; read-your-writes, monotonic reads as session guarantees.
Distributed transactions (68): span services/DBs → avoid when possible (design aggregates in one service).
2PC (69): coordinator prepare → commit; atomic but blocking, coordinator SPOF, poor availability → rarely
  across microservices.
Saga (70): sequence of local transactions with COMPENSATIONS on failure; orchestration (central coordinator)
  or choreography (events); design idempotent steps & compensations (refund, release inventory).
CQRS (71): separate write model (commands) and read models (queries/projections) → optimized reads; eventual
  consistency between them.
Event sourcing (72): store events as source of truth; rebuild state by replay; audit trail & temporal queries;
  complexity (schema evolution, snapshots) → use for ledgers/audit-heavy domains, not simple CRUD.
```

### Resilience patterns (73–81)

```
Circuit breaker (73): closed → open after failures (fail fast) → half-open probe → closed; protects callers
  & failing service; pair with fallbacks.
Retry + exponential backoff (74): retry transient errors only (timeouts, 5xx, 429) with increasing delays;
  cap attempts; only idempotent operations (or with idempotency keys).
Jitter (75): randomize backoff → avoid synchronized retry storms (thundering herd).
Bulkhead (76): isolate resources (separate pools/queues/threads per dependency or tenant) so one failure
  doesn't sink everything.
Graceful degradation (77): drop non-essential features (recommendations, reviews) when dependencies fail;
  serve cached/stale data.
Load shedding (78): reject excess requests early (503 + Retry-After), prioritize critical traffic (checkout >
  browse) to keep the system alive under overload.
Timeouts (79): every network call has a timeout; inner timeouts shorter than outer (DB 2 s < service 8 s <
  gateway 30 s); deadlines propagated.
Health checks (80): liveness (restart if dead) vs readiness (remove from LB until ready); don't make liveness
  depend on downstreams (cascading restarts).
Failover (81): active-passive or active-active; automatic promotion of replicas; DNS/LB rerouting; test it
  (chaos drills); watch split-brain (fencing tokens, quorum).
```

### Messaging & events (82–87)

```
Message queues (82): decouple producers/consumers, absorb spikes, async work; delivery semantics:
  at-most-once, at-least-once (common → consumers must be idempotent), "exactly-once" = effect via dedupe/
  transactions.
Kafka (83): partitioned, replicated, append-only log; ordering per partition (key = order_id); consumer groups
  scale reads; retention & replay; high throughput; outbox pattern for reliable publish from DB.
RabbitMQ (84): broker with exchanges/queues/routing keys, acks, per-message routing, priority; great for task
  queues & complex routing; less suited to replayable streams.
SQS + SNS (85): managed queue (standard: at-least-once, best-effort order; FIFO: ordered, dedupe) + pub/sub
  fan-out (SNS → many SQS queues).
DLQ (86): messages that fail N times move to dead-letter queue for inspection/replay; alert on DLQ depth.
Event-driven architecture (87): services react to events (OrderPlaced → payment, notification, analytics);
  loose coupling, scalability; harder debugging, eventual consistency, schema governance (registry).
```

### Coordination (88–91)

```
Distributed locks (88): Redis (SET NX PX + token, Redlock debates) or ZooKeeper/etcd (sessions, stronger);
  always use TTL + fencing tokens; prefer avoiding locks (idempotency, partitioning, DB constraints).
Leader election (89): one active leader for a task (scheduler, partition owner) via etcd/ZooKeeper/Raft or
  DB lease; leases expire on failure.
Quorum (90): N replicas, write W, read R; R + W > N → read sees latest write (e.g., N=3, W=2, R=2).
Vector / Lamport clocks (91): Lamport → total order consistent with causality; vector clocks → detect
  concurrent updates (conflicts) in multi-master systems.
```

### Service infrastructure (92–99)

```
Service discovery (92): registry (Consul, Eureka, K8s DNS/Services); client-side vs server-side discovery.
API gateway (93): single entry: routing, auth, rate limiting, TLS, request transformation, observability.
BFF (93a): per-client backend (web/mobile) aggregating services into screen-shaped responses.
Service mesh (94): sidecars (Envoy) for mTLS, retries, timeouts, traffic shifting, telemetry without app code;
  adds operational complexity.
gRPC (95): HTTP/2 + Protobuf; fast, typed, streaming; great internally; browsers need gRPC-Web/gateway.
WebSocket at scale (96): connection gateways, session registry (user → gateway), pub/sub fan-out, heartbeats,
  reconnect/resume, LB stickiness, graceful drain on deploy.
Real-time systems (97): push vs pull, SSE/WS/MQTT, fan-out strategies, presence, ordering & dedupe.
Microservice boundaries (98): split by business capability/bounded context (DDD), own data, minimize chatty
  sync calls; avoid "distributed monolith".
Database per service (99): each service owns its data; others access via API/events; sagas for cross-service
  workflows; CDC/outbox to propagate changes.
```

### Observability & infra essentials (100–110)

```
Logs (structured JSON, correlation/request IDs) · Metrics (RED: rate, errors, duration; USE for resources) ·
Traces (OpenTelemetry spans across services) · SLI/SLO/SLA + error budgets (99.9% → ~43 min/month) ·
Alerting on symptoms (SLO burn rate), not every cause · DR: RPO (data loss tolerated) vs RTO (downtime
tolerated), backups tested · Multi-region: active-passive vs active-active, data replication & conflicts ·
Kubernetes basics (deployments, HPA, probes) · Chaos engineering · Terraform (IaC) · Capacity planning
```

### Classic combinations to say in designs

```
Payment: idempotency key + DB transaction + outbox → Kafka → saga (reserve → charge → confirm / compensate)
         + webhooks verification + reconciliation
Calling a flaky dependency: timeout + retry w/ backoff & jitter (idempotent only) + circuit breaker +
         bulkhead + fallback/degradation
Async processing: queue + idempotent consumers + DLQ + backpressure/autoscaling on lag
Multi-tenant SaaS API: gateway auth (JWT/OIDC) + RBAC/tenant checks in service + per-tenant rate limits
```

## 🟢 कैसे काम करता है? (Hindi)
1. Auth: JWT (signed, छोटी उम्र, refresh rotation, तुरंत revoke मुश्किल), OAuth2 (Authorization Code + PKCE, service-to-service के लिए client credentials), OIDC (ID token = कौन है), sessions बनाम tokens, RBAC (हर request पर सर्वर पर जाँच); rate limiting — token bucket (burst), leaky bucket (smooth), sliding window; API versioning (सिर्फ़ जोड़ो); idempotency key (payments/orders में ज़रूरी)।
2. Consistency: CAP (partition पर C या A), PACELC; strong (leader/quorum/Raft) बनाम eventual; 2PC (blocking, microservices में बहुत कम), Saga (local transactions + compensation — orchestration/choreography), CQRS (लिखना/पढ़ना अलग), event sourcing (events = सच, ledger/audit के लिए)।
3. Resilience: circuit breaker (closed/open/half-open), retry + backoff + jitter (सिर्फ़ idempotent), bulkhead (अलग pools), graceful degradation, load shedding (503 + Retry-After, ज़रूरी traffic पहले), timeouts (अंदर वाले छोटे), liveness बनाम readiness, failover (split-brain से बचो)।
4. Messaging: at-least-once + idempotent consumers; Kafka (partition में क्रम, consumer groups, replay, outbox), RabbitMQ (routing, task queues), SQS/SNS (managed, FIFO), DLQ, event-driven; coordination — locks (TTL + fencing token), leader election (leases), quorum (R + W > N), Lamport/vector clocks।
5. Infra: service discovery, API gateway, BFF, service mesh (mTLS, retries), gRPC (अंदरूनी तेज़), WebSocket at scale, DDD boundaries, database per service + saga/outbox; observability — logs/metrics/traces, SLO + error budget, RPO/RTO; आम जोड़ — payment = idempotency + transaction + outbox + saga + webhook + reconciliation।

---

## 🟡 Real World Example
- **Stripe** popularized Idempotency-Key headers for payment APIs. Retries never double-charge.
- **Netflix Hystrix** made circuit breakers and bulkheads mainstream. Netflix's Chaos Monkey pioneered chaos engineering.
- **Uber's Cadence/Temporal**: durable workflow engines for sagas and long-running processes at scale.
- **Kafka at LinkedIn**: built as a distributed commit log for activity streams, now the backbone of event-driven systems everywhere (Flipkart, Swiggy, Zomato and banks).

## 🟡 Real Example Hindi में
- Stripe ने payment APIs में Idempotency-Key header लोकप्रिय किया — retry पर दोहरा charge नहीं।
- Netflix के Hystrix ने circuit breaker और bulkhead आम बनाए; Chaos Monkey से chaos engineering शुरू हुआ।
- Uber का Cadence/Temporal sagas और लंबे processes के लिए; LinkedIn पर बना Kafka आज Flipkart, Swiggy, Zomato और बैंकों समेत हर जगह event-driven systems की रीढ़।

---

## 🟠 My Stack Example

### Patterns in 10 lines each
```js
// Idempotency (Express + Redis)
app.post('/payments', auth, async (req, res) => {
  const key = `idem:${req.user.id}:${req.get('Idempotency-Key')}`;
  const prev = await redis.get(key); if (prev) return res.json(JSON.parse(prev));
  if (!(await redis.set(`${key}:lock`, 1, 'NX', 'EX', 30))) return res.status(409).json({ error: { code: 'IN_PROGRESS' } });
  const result = await payments.create(req.user.id, req.body);
  await redis.set(key, JSON.stringify(result), 'EX', 86400); res.json(result);
});
```
```python
# Retry with exponential backoff + full jitter (idempotent calls only)
async def call_with_retry(fn, attempts=4, base=0.2, cap=5.0):
    for i in range(attempts):
        try: return await asyncio.wait_for(fn(), timeout=2.0)
        except (asyncio.TimeoutError, TransientError):
            if i == attempts - 1: raise
            await asyncio.sleep(random.uniform(0, min(cap, base * 2 ** i)))
```

---

## ⚫ Interview Questions + Answers (rapid fire)

**Q1: How do you guarantee a payment isn't charged twice?**
A1: Clients send an idempotency key per payment attempt. The server records the key with the request fingerprint and result atomically, returning the stored result for retries and rejecting concurrent duplicates. Payment creation with the PSP also passes an idempotency reference. Confirmation comes from verified webhooks processed idempotently, and daily reconciliation against PSP records catches anomalies. Downstream consumers of payment events dedupe by event ID because queues are at-least-once.

**Q2: Saga vs 2PC?**
A2: 2PC coordinates an atomic commit across participants via prepare and commit phases. It gives strong atomicity but blocks resources, depends on a coordinator and hurts availability, so it rarely fits microservices. A saga breaks the workflow into local transactions, each with a compensating action, executed via an orchestrator or event choreography. It gives availability and loose coupling with eventual consistency, but requires idempotent steps and well-designed compensations (refund, release inventory).

**Q3: How do you call an unreliable downstream service safely?**
A3: Set a timeout shorter than the caller's own deadline. Retry only transient failures, only for idempotent operations, with exponential backoff, jitter and a cap. Wrap the call in a circuit breaker that fails fast when the dependency is unhealthy. Isolate it with a bulkhead (a dedicated pool or concurrency limit), provide a fallback (cached data or degraded feature), and monitor latency and error rates with alerts.

**Q4: Explain at-least-once delivery and how to handle duplicates.**
A4: Most queues guarantee a message is delivered one or more times, because redeliveries happen after timeouts, crashes or missing acks. Consumers must therefore be idempotent: dedupe by message or event ID (a processed-IDs table or unique constraint), use upserts or conditional updates, and make side effects idempotent (idempotency keys to external APIs). Exactly-once effects come from idempotency plus transactional outbox and inbox patterns, not from the broker alone.

**Q5: What does R + W > N mean?**
A5: In quorum-replicated systems with N replicas, a write is acknowledged by W replicas and a read queries R replicas. If R + W > N, every read quorum overlaps every write quorum in at least one replica, so reads see the latest acknowledged write. Tuning W and R trades latency and availability (W=1 for fast writes, R=1 for fast reads) against consistency.

---

## 🔷 Trade-offs
✅ Strong consistency: simpler reasoning — ❌ latency/availability cost; eventual: scale — ❌ stale reads & conflict handling.
✅ Async events: decoupling — ❌ debugging & ordering complexity; sync calls: simple — ❌ cascading failures.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| PKCE | OAuth code protection | OAuth सुरक्षा |
| Refresh rotation | New refresh token each use | हर बार नया token |
| Token bucket | Burst-friendly limiter | burst वाली सीमा |
| Idempotency key | Dedupe retried writes | दोहराव रोकने की key |
| Saga / compensation | Local txns + undo steps | कदम + वापसी |
| Outbox pattern | Reliable event publish from DB | DB से पक्का event |
| Circuit breaker | Fail fast on unhealthy deps | ख़राब dependency पर तुरंत रोक |
| At-least-once | Possible duplicates | दोहराव संभव |
| Quorum | Overlapping replica sets | replicas का बहुमत |
| SLO / error budget | Reliability target / allowance | भरोसे का लक्ष्य / छूट |

---

## ⚡ 3-Line Summary
**English:**
1. Auth: short-lived JWT + rotating refresh, OAuth Code+PKCE, OIDC for identity, server-side RBAC; rate limit with token bucket/sliding window; idempotency keys for writes.
2. Distributed data: CAP/PACELC, strong vs eventual, avoid 2PC → sagas with compensations, outbox, CQRS/event sourcing only where justified; idempotent consumers for at-least-once queues.
3. Resilience & infra: timeouts, retries + jitter, circuit breakers, bulkheads, degradation, load shedding, health checks, failover; gateway/BFF/mesh/gRPC; observe with logs, metrics, traces and SLOs.

**Hindi:**
1. Auth: छोटा JWT + rotating refresh, OAuth + PKCE, OIDC, सर्वर पर RBAC; token bucket; writes पर idempotency key।
2. Distributed डेटा: CAP, strong बनाम eventual, 2PC नहीं → saga, outbox; queues में idempotent consumers।
3. Resilience: timeouts, retry + jitter, circuit breaker, bulkhead, degradation, load shedding, failover; logs/metrics/traces/SLO।

---

## ➡️ Next Topic Suggestion
**08. Revision Sheet — Frontend + Mobile** — Next: the client-side refresher covering rendering patterns, Web Vitals, state and data fetching, security, caching, React Native architecture, offline sync, push, deep links, performance and releases (F01–F22, M01–M22).
