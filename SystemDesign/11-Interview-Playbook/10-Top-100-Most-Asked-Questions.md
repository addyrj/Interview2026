# 10. Top 100 Most-Asked Questions (with short answers)
# हिंदी में: सबसे ज़्यादा पूछे जाने वाले 100 सवाल — backend, databases, auth, distributed systems, reliability, design problems, frontend, mobile और AI — हर एक का छोटा, साफ़ जवाब और विस्तार के लिए topic का हवाला

---

## 🔵 Simple Definition (English)
A **self-test bank** of the 100 questions that come up most often in system design interviews (and their follow-ups), each with a **crisp 1–3 sentence answer** and a pointer `(→ topic)` to the full explanation in this guide. Use it for **active recall**: read the question, answer aloud, then check.

## 🔵 सरल परिभाषा (Hindi)
सबसे ज़्यादा पूछे जाने वाले 100 system design सवालों (और follow-ups) का अभ्यास भंडार — हर एक का 1–3 वाक्य का साफ़ जवाब और पूरी व्याख्या के लिए `(→ topic)`; तरीका: सवाल पढ़ो, ज़ोर से जवाब दो, फिर मिलाओ।

---

## 🔴 Problem it Solves
Reading notes feels productive, but interviews test **retrieval under pressure**. Practising short, structured answers to the most common questions builds fluency, so in the interview you spend your thinking on the design rather than recalling definitions.

## 🔴 यह क्यों बना? (Hindi)
Notes पढ़ना अच्छा लगता है, पर इंटरव्यू दबाव में याद करने की परीक्षा है; आम सवालों के छोटे, ढाँचे वाले जवाबों का अभ्यास करने से इंटरव्यू में दिमाग़ design पर लगता है, परिभाषाएँ याद करने पर नहीं।

---

## 🟢 How it Works — Step by Step
Cover the answer, say yours aloud in about 30 seconds, then compare. Mark weak ones and open the linked topic.

### A. Fundamentals & networking (1–10)
*हिंदी सार: URL से page तक का रास्ता, TCP/UDP, HTTP versions, TLS, REST/GraphQL/WebSocket, proxy, scaling, stateless और SPOF।*

**1. What happens when you type a URL in the browser?** DNS resolves the IP, then TCP/QUIC and TLS handshakes run, the HTTP request goes through CDN/LB to a server, the response comes back, and the browser parses, fetches assets, lays out, paints and runs JS. (→ 01, F02)

**2. TCP vs UDP?** TCP is reliable, ordered and congestion-controlled (web, APIs, DBs). UDP is connectionless and low-latency without guarantees (video calls, gaming, DNS, QUIC). (→ 04)

**3. HTTP/1.1 vs HTTP/2 vs HTTP/3?** 1.1 has keep-alive but head-of-line blocking. 2 multiplexes streams over one TCP connection with header compression. 3 runs on QUIC over UDP: no TCP HOL blocking, faster handshakes, connection migration. (→ 05)

**4. How does TLS work?** The handshake negotiates keys (ECDHE, 1-RTT in TLS 1.3), the server proves identity with a CA-signed certificate, then traffic is encrypted symmetrically. It gives confidentiality, integrity and authentication, not authorization. (→ 06)

**5. REST vs GraphQL?** REST is resource endpoints, simple and cacheable. GraphQL lets clients request exact nested fields in one round trip, at the cost of server complexity (N+1, cost limits, harder caching). (→ 07, 07a)

**6. When would you use WebSockets?** For bidirectional, low-latency real-time messaging (chat, collaboration, live location). Use SSE for one-way server push and polling for rare updates. (→ 08, F13)

**7. Reverse proxy vs forward proxy?** A reverse proxy sits in front of servers (TLS termination, load balancing, caching, rate limiting). A forward proxy sits in front of clients (egress control, anonymity). (→ 11, 12)

**8. Vertical vs horizontal scaling?** Vertical means a bigger machine (simple, capped, SPOF). Horizontal means more machines behind a load balancer (needs stateless services, scales further). (→ 15, 16)

**9. Why stateless services?** Any instance can serve any request, which enables horizontal scaling, rolling deploys and failure recovery. State lives in DB/Redis/tokens. (→ 23)

**10. What is a single point of failure and how do you remove it?** It's any component whose failure stops the system. Remove it with redundancy, replication, failover, multi-AZ or multi-region, and graceful degradation. (→ 24)

### B. Databases & caching (11–25)
*हिंदी सार: SQL बनाम NoSQL, indexes, isolation, locks, MVCC, pagination, replicas, sharding, caching patterns, stampede, CDN, consistent hashing, bloom filter।*

**11. SQL vs NoSQL — how do you choose?** By access patterns and consistency needs: SQL for relational data and transactions (orders, payments), NoSQL for massive scale with simple key or time access (chat, IoT, sessions), or for specialized queries (search, graph). Often both. (→ 27)

**12. How does a database index work?** Usually a B-tree mapping key values to row locations, so lookups and range scans take O(log n) instead of full scans. It speeds reads but costs write speed and storage. (→ 28)

**13. What's the leftmost-prefix rule?** A composite index (a, b, c) serves queries filtering on a, (a, b), or (a, b, c), not on b alone. Put equality columns first, then range or sort columns. (→ 29)

**14. How do you debug a slow query?** EXPLAIN ANALYZE: check for seq scans, row-estimate mismatches, sort spills and join types. Then add or adjust indexes, rewrite the query, avoid functions on indexed columns, fix N+1 and update statistics. (→ 30)

**15. Explain ACID.** Atomicity (all or nothing), Consistency (constraints hold), Isolation (concurrent transactions don't interfere beyond the chosen level), Durability (committed data survives crashes via the WAL). (→ 34)

**16. Isolation levels and anomalies?** Read Committed prevents dirty reads, Repeatable Read prevents non-repeatable reads, Serializable prevents phantoms and write skew (with retries). Postgres defaults to RC, MySQL to RR. (→ 35)

**17. Optimistic vs pessimistic locking?** Pessimistic locks rows first (SELECT FOR UPDATE), which is good under high contention. Optimistic checks a version on update and retries on conflict, which is good when conflicts are rare. (→ 36)

**18. What is MVCC?** Multi-version concurrency control keeps row versions so readers see a consistent snapshot without blocking writers. It needs cleanup (vacuum), and long transactions cause bloat. (→ 37)

**19. Offset vs cursor pagination?** Offset is simple but slow on deep pages and unstable when rows are inserted. Cursor/keyset (WHERE (ts, id) < last) is fast and stable for feeds but can't jump to page N. (→ 39)

**20. Read replicas — what's the catch?** Replication lag gives stale reads. Use read-your-writes from the primary for recent writes and route only lag-tolerant reads to replicas. (→ 40)

**21. Partitioning vs sharding?** Partitioning splits a table within one database (range or hash) for pruning and retention. Sharding spreads data across multiple servers by a shard key to scale writes and storage. (→ 41, 42)

**22. How do you choose a shard key?** Match the dominant access pattern (user_id, tenant_id), aim for high cardinality and even distribution, plan for hot keys, and avoid frequent cross-shard operations. (→ 42)

**23. Cache-aside vs write-through vs write-back?** Cache-aside: the app loads on a miss and invalidates on write (most common). Write-through: write cache and DB together (fresh, slower writes). Write-back: write cache and flush later (fast, risk of loss). (→ 45–47)

**24. How do you prevent a cache stampede?** Single-flight locks or request coalescing, jittered TTLs, early or probabilistic refresh, stale-while-revalidate, and background refresh for very hot keys. (→ 50)

**25. What is consistent hashing?** Keys and nodes sit on a hash ring (with virtual nodes), so adding or removing a node remaps only about 1/N of keys. It's used in distributed caches and databases. (→ 52)

### C. Auth, security & API design (26–35)
*हिंदी सार: JWT, OAuth/OIDC, sessions, RBAC, rate limiting algorithms, versioning, idempotency, XSS/CSRF/CORS।*

**26. How does JWT authentication work?** The server signs a token with claims, and services verify the signature locally (stateless). Keep access tokens short-lived with rotating refresh tokens, since revocation is hard. (→ 54)

**27. OAuth 2.0 vs OpenID Connect?** OAuth delegates authorization (access tokens with scopes). OIDC adds authentication: an ID token describing the user ("Login with Google"). Apps use Authorization Code + PKCE. (→ 55, 56)

**28. Sessions vs tokens?** Server sessions (cookie plus Redis) are easy to revoke and need CSRF protection. Tokens are stateless and scale easily but are harder to revoke. Many web apps use HttpOnly cookies, and mobile apps use Keychain-stored tokens. (→ 57, F16, M16)

**29. How do you implement RBAC?** Map users to roles to permissions, check on every request server-side (middleware plus resource ownership and tenant checks), apply least privilege, and use ABAC/ReBAC for finer rules. (→ 58)

**30. Token bucket vs leaky bucket vs sliding window?** Token bucket allows bursts up to capacity at an average rate. Leaky bucket smooths output to a constant rate. A sliding window counts requests over a rolling window, avoiding fixed-window edge spikes. (→ 60–62)

**31. How do you design a distributed rate limiter?** Use Redis with atomic Lua (token bucket per key), keyed by user/IP/API key, enforced at the gateway, returning 429 with Retry-After, with local fallbacks if Redis is down. (→ 59, 112)

**32. What is idempotency and why does it matter?** Repeating a request has the same effect as once. Clients send an Idempotency-Key and the server stores and returns the first result, which is essential for payments and orders under retries. (→ 64)

**33. How do you version APIs?** URL (/v2), header or date-based versions. Prefer additive changes, deprecate with timelines, and support old mobile app versions. (→ 63, M09)

**34. XSS vs CSRF — and defences?** XSS injects scripts into your page: escape output, sanitize HTML, use CSP. CSRF forges cross-site requests using cookies: use SameSite cookies, CSRF tokens and Origin checks. (→ F14)

**35. What is CORS?** A browser-enforced mechanism where servers allow specific origins to read cross-origin responses (with preflight for non-simple requests). It protects users, not your API. (→ F15)

### D. Distributed systems & messaging (36–50)
*हिंदी सार: CAP, consistency, 2PC बनाम Saga, CQRS, event sourcing, resilience patterns, queues, Kafka, DLQ, locks, quorum, clocks।*

**36. Explain the CAP theorem.** During a network partition a distributed system must choose consistency (reject or wait) or availability (serve possibly stale data). PACELC adds the latency versus consistency trade-off when there's no partition. (→ 65)

**37. Strong vs eventual consistency — examples?** Strong: bank balances, inventory decrements, seat booking. Eventual: likes, follower counts, feeds, analytics. (→ 66, 67)

**38. Why avoid 2PC in microservices?** It blocks resources, depends on a coordinator, reduces availability and couples services. Use sagas with compensations and the outbox pattern instead. (→ 69, 70)

**39. Orchestration vs choreography sagas?** Orchestration: a central coordinator tells services what to do (clear flow, easier monitoring). Choreography: services react to events (looser coupling, harder to trace). (→ 70)

**40. What is CQRS?** Separate write models (commands) from read models (projections optimized for queries), synchronized asynchronously. It adds eventual consistency and complexity. (→ 71)

**41. When is event sourcing worth it?** When you need a full audit trail, temporal queries or rebuildable projections (ledgers, compliance). Avoid it for simple CRUD due to schema-evolution and replay complexity. (→ 72)

**42. Explain the circuit breaker pattern.** After repeated failures the breaker opens and calls fail fast, then half-open probes test recovery before closing again. It prevents cascading failures, usually paired with fallbacks. (→ 73)

**43. Why add jitter to retries?** Synchronized retries from many clients create retry storms after outages. Randomized backoff spreads them out. (→ 74, 75)

**44. Bulkhead vs load shedding?** A bulkhead isolates resources per dependency or tenant so one failure doesn't exhaust everything. Load shedding rejects excess low-priority traffic to keep the core alive. (→ 76, 78)

**45. Liveness vs readiness probes?** Liveness restarts a dead process. Readiness removes an instance from traffic until it can serve. Don't tie liveness to downstream health. (→ 80)

**46. Why use a message queue?** To decouple services, absorb spikes, enable async processing and retries, and fan out events. Consumers must be idempotent because delivery is usually at-least-once. (→ 82)

**47. Kafka vs RabbitMQ vs SQS?** Kafka: a partitioned replayable log with high throughput and per-key ordering, good for event streaming. RabbitMQ: flexible routing and task queues. SQS: managed, simple queues (FIFO option) with SNS fan-out. (→ 83–85)

**48. How do you publish events reliably after a DB write?** The transactional outbox: write the business row and the outbox row in one transaction, then a relay (or CDC) publishes to Kafka. Consumers dedupe. (→ 87, 99)

**49. How do distributed locks work, and what's the risk?** Acquire with TTL in Redis (SET NX PX) or etcd/ZooKeeper leases. Risks are expired locks and GC pauses, so use fencing tokens, or avoid locks with idempotency and DB constraints. (→ 88)

**50. What does quorum R + W > N give you?** Read and write sets overlap, so reads see the latest acknowledged write (e.g., N=3, W=2, R=2). (→ 90)

### E. Reliability, observability & infra (51–58)
*हिंदी सार: logs/metrics/traces, SLI/SLO/SLA, error budget, RPO/RTO, multi-region, Kubernetes, capacity planning।*

**51. Logs vs metrics vs traces?** Logs are detailed discrete events (debugging). Metrics are aggregated numbers over time (dashboards and alerts). Traces follow one request across services (latency breakdown). Correlate them with request IDs. (→ 100–102)

**52. SLI vs SLO vs SLA?** SLI: the measured indicator (p99 latency, success rate). SLO: the internal target (99.9% success). SLA: the contractual promise with penalties, set looser than the SLO. (→ 103)

**53. What is an error budget?** The allowed unreliability (100% − SLO). If it's burned, prioritize reliability work and slow releases. If it's healthy, ship faster. (→ 103)

**54. RPO vs RTO?** RPO is the maximum acceptable data loss (time since the last good copy). RTO is the maximum acceptable downtime to recover. They drive backup frequency and failover design. (→ 106)

**55. Active-passive vs active-active multi-region?** Active-passive is simpler (failover to standby; some RTO and RPO). Active-active serves from both (lower latency, higher availability) but needs conflict handling and data replication strategy. (→ 107)

**56. How do you alert well?** Alert on user-facing symptoms and SLO burn rates rather than every cause, with runbooks, deduplication and severity levels, to avoid alert fatigue. (→ 103, 104)

**57. How does Kubernetes help?** It provides declarative deployments, self-healing, horizontal autoscaling (HPA), service discovery, rolling updates and liveness/readiness probes, at the cost of operational complexity. (→ 108)

**58. How do you do capacity planning?** Forecast peak load (events like IPL and sales), measure per-instance capacity with load tests, add headroom and redundancy, pre-scale before known spikes, and track utilization trends. (→ 110, Playbook 03)

### F. Classic design prompts — one-line approach (59–72)
*हिंदी सार: हर मशहूर design सवाल का मुख्य विचार — गहराई के लिए 06 और 09 folders।*

**59. Design a URL shortener.** Generate base62 codes from unique IDs (range allocation), store code → URL in a key-value store, cache hot codes in Redis plus the CDN, use 301/302 trade-offs, and add expiry and abuse scanning. (→ 111)

**60. Design a rate limiter.** Use a token bucket per key in Redis with atomic Lua at the API gateway, configurable rules, 429 + Retry-After, and fail-open versus fail-closed decisions. (→ 112)

**61. Design an authentication service.** Signup and login (password hashing with argon2/bcrypt, OTP), short JWTs plus rotating refresh tokens, sessions in Redis, OAuth/OIDC providers, MFA, rate limits and an audit log. (→ 113)

**62. Design a notification system.** Producers emit events to a priority queue, the service handles preferences, templates, caps and quiet hours, and channel workers deliver (push, email, SMS with DLT, in-app inbox), with retries, DLQ and tracking. (→ 114, P09)

**63. Design WhatsApp.** Persistent connection gateways, a session registry, per-device inboxes (store-and-forward), client message IDs for dedupe, receipts, group fan-out, push for offline, E2EE per device. (→ 115, P01)

**64. Design Instagram / a news feed.** Upload pipeline plus CDN, hybrid fan-out (push for normal users, pull for celebrities), ML ranking, cursor pagination, a cached feed, counters via streams. (→ 116, 117, P02)

**65. Design an e-commerce platform.** Catalog (search plus cache), cart (server-side), checkout with inventory reservation, idempotent orders, payment via PSP webhooks, order state machine, flash-sale queueing. (→ 118, P08)

**66. Design a payment system.** Idempotency keys, a double-entry ledger, PSP integration with signed webhooks, a payment state machine, retries plus reconciliation, outbox events, PCI scope minimization (tokenization). (→ 119)

**67. Design Google Drive / Dropbox.** Chunked, resumable uploads to object storage, dedupe by content hash, a metadata DB, sync clients with change feeds, sharing ACLs, versioning, conflict copies. (→ 120)

**68. Design YouTube.** Resumable upload, then parallel transcoding into an HLS/DASH ladder, CDN plus ISP caches, an ABR player, view counting via the event pipeline, recommendations. (→ 121, P07)

**69. Design search autocomplete.** A prefix trie or FST with precomputed top-k per node, built offline from query logs plus a trending layer; client debounce, cancellation and caching; CDN caching of short prefixes. (→ 122, P06)

**70. Design Uber / Ola.** Drivers stream locations into an H3/geohash index, dispatch over k-rings ranked by ETA with per-driver locks, a server-authoritative trip state machine, surge per cell, live tracking. (→ 125, P03)

**71. Design Swiggy / Zomato.** A three-sided order state machine, restaurant alert escalation (WS, push, IVR), just-in-time rider assignment from prep-time and travel models, live tracking, UPI payments via webhooks. (→ 124, P04)

**72. Design a real-time analytics dashboard.** Events go to Kafka, then Flink aggregates into a real-time OLAP store (ClickHouse/Pinot/Druid) feeding a query API with RLS and caching, then SSE live tiles and a virtualized frontend. (→ 126, P10)

### G. Frontend (73–82)
*हिंदी सार: rendering, Web Vitals, hydration, state, React Query, caching, virtualization, token storage, a11y, PWA।*

**73. CSR vs SSR vs SSG vs ISR?** CSR renders in the browser (apps behind login). SSR renders per request (SEO plus personalization). SSG renders at build time (fastest). ISR is static with background or on-demand regeneration (large catalogs). Choose per route. (→ F03)

**74. What are Core Web Vitals?** LCP ≤ 2.5 s (loading), INP ≤ 200 ms (responsiveness), CLS ≤ 0.1 (stability), measured at p75 from real users. (→ F05)

**75. What is hydration and why can it hurt?** Attaching JS behaviour to server-rendered HTML re-runs component code, so big bundles delay interactivity (INP). Mitigate with RSC, code splitting and selective or streaming hydration. (→ F03, F04)

**76. How do you decide where state lives?** Server data in a server-state cache (React Query), shareable view state in the URL, forms in a form library, local UI state in components, app-wide client state in Zustand/Redux or Context. Derive, don't duplicate. (→ F09)

**77. How does React Query caching work?** Query keys identify data. staleTime controls freshness, refetches happen on focus, reconnect or invalidation, identical requests are deduped, and optimistic updates use rollback. (→ F10)

**78. How do you cache static assets and HTML?** Hashed assets get `max-age=31536000, immutable`. HTML gets `no-cache` with an ETag. Personalized responses are `private`, sensitive ones `no-store`. (→ F07)

**79. How do you render 100k rows smoothly?** Server-side pagination, sorting and filtering plus virtualization (render only visible rows), memoized rows and Web Workers for heavy transforms. (→ F12, P10)

**80. Where should a SPA store tokens?** Access token in memory, refresh token in an HttpOnly Secure SameSite cookie with rotation (or a BFF session). Never long-lived tokens in localStorage. (→ F16)

**81. How do you make a custom dropdown accessible?** Prefer native controls or proven libraries; otherwise follow the ARIA combobox/listbox pattern with keyboard navigation, focus management, labels and live announcements. (→ F18)

**82. What does a service worker enable?** Programmable caching (offline app shell, cache-first assets, network-first data), background sync, push notifications and installable PWAs. (→ F08)

### H. Mobile (83–90)
*हिंदी सार: RN architecture, startup, offline-first, conflicts, push, deep links, lists, OTA/releases।*

**83. How does React Native's New Architecture differ from the bridge?** JSI gives direct JS-to-native calls without JSON serialization, Fabric is a concurrent renderer with synchronous layout, and TurboModules are lazy, typed native modules (Codegen). (→ M02)

**84. How do you speed up app cold start?** Use Hermes, inline requires, lazy screens and SDKs, MMKV for boot data, cached first-screen data and a splash until meaningful content, then measure on low-end Android release builds. (→ M03)

**85. How do you design offline-first?** The local DB is the UI's source of truth. Writes go local plus to an outbox in one transaction, a sync engine pushes with idempotency and backoff and pulls deltas with cursors and tombstones, and the UI shows sync states. (→ M06)

**86. How do you resolve sync conflicts?** Detect with server versions (not device clocks), then resolve per data type: field LWW, server-authoritative domain rules, 3-way merge, operations, CRDTs, or user choice. (→ M07)

**87. How do push notifications work?** The app gets an APNs/FCM token and sends it to the backend, which sends payloads via the vendor API, and the OS delivers. Manage token refresh and pruning, channels, collapse keys and TTL. It's best-effort, not the source of truth. (→ M10)

**88. Universal Links vs custom URL schemes?** Universal/App Links are verified HTTPS links (domain association files) with a web fallback that can't be hijacked. Custom schemes are easy but claimable by any app. (→ M11)

**89. FlatList vs FlashList?** FlatList virtualizes by mounting and unmounting. FlashList recycles cells by type, which is much faster on low-end devices. Use memoized rows and sized images in both. (→ M13)

**90. OTA updates vs store releases?** OTA replaces JS bundles and assets for compatible runtime versions (quick fixes, staged rollout, rollback). Native changes need store releases with staged rollout and force update for old versions. (→ M17, M18)

### I. AI engineering (91–100)
*हिंदी सार: RAG, hybrid + rerank, chunking, tools, agents, hallucinations, evals, guardrails, cost, streaming।*

**91. What is RAG and why use it?** Retrieve relevant chunks from your data and ground the LLM's answer in them with citations. It gives fresh, private, permission-aware knowledge without retraining. (→ 137)

**92. Why hybrid search plus reranking?** BM25 catches exact terms (IDs, codes), vectors catch meaning, RRF fuses them, and a cross-encoder reranker picks the truly relevant few, which improves precision with fewer tokens. (→ 138, 139)

**93. How do you choose chunk size?** Follow document structure (sections, FAQ pairs, tables with headers), with about 300–800 tokens and 10–20% overlap as a start. Enrich chunks with context and tune with retrieval evals. (→ 136)

**94. How does tool or function calling work safely?** The model proposes tool calls (name plus JSON args), and your code validates, authorizes from the session, enforces limits and confirmations, executes idempotently and returns results. (→ 140)

**95. ReAct agent vs workflow?** Workflows hard-code known steps (cheap, predictable). ReAct agents loop reason-act-observe for open-ended tasks, with step, cost and time limits and human handoff. (→ 141, 143)

**96. How do you reduce hallucinations?** Ground answers in retrieved sources with citations, allow abstention below a retrieval threshold, get facts from tools, constrain outputs with schemas, verify claims and citations post-generation, and keep humans on high-stakes decisions. (→ 152)

**97. How do you evaluate a RAG system?** Measure retrieval (context recall and precision, recall@k) separately from generation (faithfulness, relevancy, correctness) on golden, production and synthetic datasets, gating changes in CI and sampling production online. (→ 146)

**98. How do you defend against prompt injection?** Treat all retrieved and user content as data, keep privileges and limits in code and tools, require approvals for risky actions, filter exfiltration channels, and red-team continuously, assuming injection can succeed. (→ 149)

**99. How do you cut LLM costs?** Route or cascade to smaller models, use prompt caching for stable prefixes, response caching for FAQs, lean per-route prompts, top-k context, summarized history, capped outputs, batch APIs for offline work and bounded agents, with per-feature budgets. (→ 153)

**100. How do you stream LLM responses in production?** Relay provider SSE deltas through the backend without buffering (disable proxy buffering, long LB timeouts, heartbeats), cancel on client disconnect, send status events for tools, and validate citations at the end. (→ 154)

---

## 🟢 कैसे काम करता है? (Hindi)
1. हर सवाल पढ़ो, जवाब ढको, 30 सेकंड में ज़ोर से जवाब दो, फिर मिलाओ; कमज़ोर सवाल पर निशान लगाकर `(→ topic)` वाली file खोलो।
2. A–E (1–58): fundamentals, databases, auth/security, distributed systems, reliability — परिभाषा + मुख्य तरीका + trade-off के ढाँचे में जवाब दो।
3. F (59–72): हर मशहूर design का एक-line मुख्य विचार याद रखो, फिर इंटरव्यू में Playbook 01 के ढाँचे से फैलाओ।
4. G–H (73–90): frontend और mobile — numbers (LCP, INP, CLS, startup) और tools (React Query, FlashList, OTA) के साथ।
5. I (91–100): AI — RAG, hybrid + rerank, tools, agents, hallucination, evals, guardrails, ख़र्च, streaming; हफ़्ते में दो बार पूरा set दोहराओ।

---

## 🟡 Real World Example
These questions reflect recurring themes in system design loops at global companies (Google, Meta, Amazon, Microsoft, Uber) and Indian product companies (Flipkart, Swiggy, Zomato, PhonePe, Razorpay, CRED, Meesho), where interviewers often begin with a design prompt (section F) and probe with follow-ups from sections A–E and G–I.

## 🟡 Real Example Hindi में
ये सवाल Google, Meta, Amazon, Uber और Flipkart, Swiggy, Zomato, PhonePe, Razorpay, CRED, Meesho के design rounds के आम विषय हैं — interviewer अक्सर section F जैसे design सवाल से शुरू करके A–E और G–I जैसे follow-ups पूछते हैं।

---

## 🟠 My Stack Example

### Practice routine
```
Day 1: Q1–25 aloud (record yourself) · Day 2: Q26–50 · Day 3: Q51–72 (sketch each design for 5 min)
Day 4: Q73–100 · Day 5: random 20 + one full 45-min mock design (Playbook 01/02)
Track misses in a sheet → reread linked topics → retest after 2 days (spaced repetition)
```

---

## ⚫ Interview Questions + Answers

**Q1: How should you use this list?**
A1: For active recall and spaced repetition: answer aloud before reading, mark misses, revisit the linked deep-dive topics, and retest after a few days. Combine it with full mock designs, so you practise connecting short answers into end-to-end systems.

**Q2: Should you memorize these answers word for word?**
A2: No. Understand the mechanism and trade-off behind each so you can adapt it to the interviewer's context and follow-ups. Use the short answers as anchors, then expand with numbers and examples relevant to the prompt.

**Q3: What if an interviewer asks something not on the list?**
A3: Apply the same structure: clarify the question, state the core mechanism, give a concrete example, discuss trade-offs and alternatives, and relate it to the system being designed. Most new questions are variations of these fundamentals.

**Q4: How many questions should you be fluent in before an interview?**
A4: Aim to answer all 100 comfortably in under a minute each, and to expand any of the 14 design prompts in section F into a structured 45-minute design. Prioritize the sections matching the role (backend, frontend, mobile or AI).

**Q5: How do you know you're ready?**
A5: When you can run mock interviews end to end within time, consistently clarify requirements, use numbers to justify decisions, handle follow-ups from every section without long pauses, and explain trade-offs clearly, ideally validated by peers or mentors giving rubric-based feedback.

---

## 🔷 Trade-offs
✅ Short answers build fluency — ❌ always expand with context, numbers and trade-offs in the real interview.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Active recall | Answer from memory before checking | पहले याद से जवाब |
| Spaced repetition | Revisit at increasing intervals | अंतराल पर दोहराना |
| Follow-up question | Deeper probe after an answer | आगे का सवाल |
| Design prompt | Open-ended system to design | design वाला सवाल |
| Mock interview | Practice under real conditions | अभ्यास इंटरव्यू |

---

## ⚡ 3-Line Summary
**English:**
1. 100 high-frequency questions across fundamentals, data, security, distributed systems, reliability, design prompts, frontend, mobile and AI.
2. Answer aloud in ~30 seconds, check, mark misses and reread the linked topics.
3. Use spaced repetition plus full mock designs to turn short answers into fluent end-to-end reasoning.

**Hindi:**
1. 100 आम सवाल — fundamentals से AI तक।
2. 30 सेकंड में ज़ोर से जवाब, मिलाओ, कमज़ोर सवाल की file पढ़ो।
3. अंतराल पर दोहराओ और पूरे mock designs करो।

---

## ➡️ Next Topic Suggestion
**11. Common Mistakes in System Design Interviews** — Knowing answers isn't enough if you fall into common traps. Next: the mistakes that cost offers, and how to avoid each one.
