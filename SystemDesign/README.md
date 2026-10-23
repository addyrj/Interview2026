# 📘 System Design — Complete Interview Guide (Backend + Frontend + Mobile + AI)
# हिंदी में: सिस्टम डिज़ाइन — इंटरव्यू की पूरी तैयारी, एक ही जगह

> Target: 4–6 years experience interviews.
> Stack used in every example: **React, Next.js, React Native, Node.js, FastAPI, Python, PostgreSQL, MySQL, MongoDB, Redis, Docker, Nginx, GitHub Actions, AWS**.
> Read top to bottom. Tick `[x]` when you finish a topic.

---

## 🗺️ Roadmap — How to Study

```
Week 1-2  →  01-Fundamentals           (how the internet + servers work)
Week 3-4  →  02-Databases-Caching      (where 50% of interview questions come from)
Week 5    →  03-Auth-Security-API
Week 6-7  →  04-Distributed-Systems
Week 8    →  05-Observability-Infra
Week 9    →  07-Frontend  +  08-Mobile  (your daily work — easy marks)
Week 10   →  06-Backend-Design-Problems + 09-FullStack-Design-Problems
Week 11   →  10-AI-Engineering
Week 12   →  11-Interview-Playbook     (revise + mock answers)
```

**Daily routine (1.5–2 hrs):**
1. Read 2 topics fully (diagram + example + code).
2. Close the file, answer the 5 interview questions out loud.
3. Read the "3-Line Summary" of yesterday's topics (spaced revision).

**Every topic file has the same sections:**
Definition (+ Hindi) → Problem it solves → How it works (diagram) → Real-world example → My Stack example (code) → 5 Interview Q&A → Trade-offs → Key terms → 3-line summary → Next topic.

---

## 01 — Fundamentals  `01-Fundamentals/`

- [ ] [01. How Internet Works](01-Fundamentals/01-How-Internet-Works.md)
- [ ] [02. DNS — Domain Name System](01-Fundamentals/02-DNS.md)
- [ ] [03. IP Address + Ports](01-Fundamentals/03-IP-Address-Ports.md)
- [ ] [04. TCP vs UDP](01-Fundamentals/04-TCP-vs-UDP.md)
- [ ] [05. HTTP vs HTTPS](01-Fundamentals/05-HTTP-vs-HTTPS.md)
- [ ] [06. TLS/SSL — How Encryption Works](01-Fundamentals/06-TLS-SSL.md)
- [ ] [07. REST API Design](01-Fundamentals/07-REST-API-Design.md)
- [ ] [07a. GraphQL ⭐ (added)](01-Fundamentals/07a-GraphQL.md)
- [ ] [08. WebSockets](01-Fundamentals/08-WebSockets.md)
- [ ] [09. Client-Server Architecture](01-Fundamentals/09-Client-Server-Architecture.md)
- [ ] [10. Request-Response Lifecycle](01-Fundamentals/10-Request-Response-Lifecycle.md)
- [ ] [11. Reverse Proxy (Nginx)](01-Fundamentals/11-Reverse-Proxy-Nginx.md)
- [ ] [12. Forward Proxy](01-Fundamentals/12-Forward-Proxy.md)
- [ ] [13. Monolith Architecture](01-Fundamentals/13-Monolith-Architecture.md)
- [ ] [14. Microservices Architecture](01-Fundamentals/14-Microservices-Architecture.md)
- [ ] [15. Vertical Scaling](01-Fundamentals/15-Vertical-Scaling.md)
- [ ] [16. Horizontal Scaling](01-Fundamentals/16-Horizontal-Scaling.md)
- [ ] [17. Latency](01-Fundamentals/17-Latency.md)
- [ ] [18. Throughput](01-Fundamentals/18-Throughput.md)
- [ ] [19. Availability](01-Fundamentals/19-Availability.md)
- [ ] [20. Bandwidth](01-Fundamentals/20-Bandwidth.md)
- [ ] [21. Load Balancing Basics](01-Fundamentals/21-Load-Balancing-Basics.md)
- [ ] [22. Load Balancing Algorithms](01-Fundamentals/22-Load-Balancing-Algorithms.md)
- [ ] [23. Stateless vs Stateful](01-Fundamentals/23-Stateless-vs-Stateful.md)
- [ ] [24. Single Point of Failure (SPOF)](01-Fundamentals/24-Single-Point-of-Failure.md)

## 02 — Databases + Caching  `02-Databases-Caching/`

- [ ] [25. SQL Databases (MySQL/PostgreSQL)](02-Databases-Caching/25-SQL-Databases.md)
- [ ] [26. NoSQL Databases](02-Databases-Caching/26-NoSQL-Databases.md)
- [ ] [27. SQL vs NoSQL — When to Use](02-Databases-Caching/27-SQL-vs-NoSQL.md)
- [ ] [28. Database Indexes](02-Databases-Caching/28-Database-Indexes.md)
- [ ] [29. Composite Indexes](02-Databases-Caching/29-Composite-Indexes.md)
- [ ] [30. Query Optimization + EXPLAIN](02-Databases-Caching/30-Query-Optimization-EXPLAIN.md)
- [ ] [31. Normalization](02-Databases-Caching/31-Normalization.md)
- [ ] [32. Denormalization](02-Databases-Caching/32-Denormalization.md)
- [ ] [33. Transactions](02-Databases-Caching/33-Transactions.md)
- [ ] [34. ACID Properties](02-Databases-Caching/34-ACID-Properties.md)
- [ ] [35. Isolation Levels](02-Databases-Caching/35-Isolation-Levels.md)
- [ ] [36. Database Locks](02-Databases-Caching/36-Database-Locks.md)
- [ ] [37. MVCC](02-Databases-Caching/37-MVCC.md)
- [ ] [38. Connection Pooling](02-Databases-Caching/38-Connection-Pooling.md)
- [ ] [39. Pagination (Cursor vs Offset)](02-Databases-Caching/39-Pagination-Cursor-vs-Offset.md)
- [ ] [40. Read Replicas](02-Databases-Caching/40-Read-Replicas.md)
- [ ] [41. Database Partitioning](02-Databases-Caching/41-Database-Partitioning.md)
- [ ] [42. Database Sharding](02-Databases-Caching/42-Database-Sharding.md)
- [ ] [43. Redis — Caching](02-Databases-Caching/43-Redis-Caching.md)
- [ ] [44. Redis Data Structures](02-Databases-Caching/44-Redis-Data-Structures.md)
- [ ] [45. Cache-Aside Pattern](02-Databases-Caching/45-Cache-Aside-Pattern.md)
- [ ] [46. Write-Through Pattern](02-Databases-Caching/46-Write-Through-Pattern.md)
- [ ] [47. Write-Back Pattern](02-Databases-Caching/47-Write-Back-Pattern.md)
- [ ] [48. Cache TTL + Invalidation](02-Databases-Caching/48-Cache-TTL-Invalidation.md)
- [ ] [49. Cache Eviction (LRU/LFU)](02-Databases-Caching/49-Cache-Eviction-LRU-LFU.md)
- [ ] [50. Cache Stampede + Thundering Herd](02-Databases-Caching/50-Cache-Stampede-Thundering-Herd.md)
- [ ] [51. CDN — Content Delivery Network](02-Databases-Caching/51-CDN.md)
- [ ] [51a. Object Storage (AWS S3) ⭐ (added)](02-Databases-Caching/51a-Object-Storage-S3.md)
- [ ] [52. Consistent Hashing](02-Databases-Caching/52-Consistent-Hashing.md)
- [ ] [53. Bloom Filters](02-Databases-Caching/53-Bloom-Filters.md)
- [ ] [53a. Search Engines (Elasticsearch) ⭐ (added)](02-Databases-Caching/53a-Search-Engines-Elasticsearch.md)
- [ ] [53b. OLTP vs OLAP — Data Warehouse, Data Lake, ETL/ELT, Batch vs Streaming ⭐ (added)](02-Databases-Caching/53b-OLTP-OLAP-DataWarehouse-ETL.md)

## 03 — Auth + Security + API  `03-Auth-Security-API/`

- [ ] [54. JWT Authentication](03-Auth-Security-API/54-JWT-Authentication.md)
- [ ] [55. OAuth 2.0](03-Auth-Security-API/55-OAuth-2.md)
- [ ] [56. OpenID Connect](03-Auth-Security-API/56-OpenID-Connect.md)
- [ ] [57. Session vs Token Auth](03-Auth-Security-API/57-Session-vs-Token-Auth.md)
- [ ] [58. RBAC — Role Based Access Control](03-Auth-Security-API/58-RBAC.md)
- [ ] [59. Rate Limiting](03-Auth-Security-API/59-Rate-Limiting.md)
- [ ] [60. Token Bucket Algorithm](03-Auth-Security-API/60-Token-Bucket.md)
- [ ] [61. Leaky Bucket Algorithm](03-Auth-Security-API/61-Leaky-Bucket.md)
- [ ] [62. Sliding Window Algorithm](03-Auth-Security-API/62-Sliding-Window.md)
- [ ] [63. API Versioning](03-Auth-Security-API/63-API-Versioning.md)
- [ ] [64. Idempotency](03-Auth-Security-API/64-Idempotency.md)

## 04 — Distributed Systems  `04-Distributed-Systems/`

- [ ] [65. CAP Theorem](04-Distributed-Systems/65-CAP-Theorem.md)
- [ ] [66. Strong Consistency](04-Distributed-Systems/66-Strong-Consistency.md)
- [ ] [67. Eventual Consistency](04-Distributed-Systems/67-Eventual-Consistency.md)
- [ ] [68. Distributed Transactions](04-Distributed-Systems/68-Distributed-Transactions.md)
- [ ] [69. Two Phase Commit (2PC)](04-Distributed-Systems/69-Two-Phase-Commit.md)
- [ ] [70. Saga Pattern](04-Distributed-Systems/70-Saga-Pattern.md)
- [ ] [71. CQRS Pattern](04-Distributed-Systems/71-CQRS-Pattern.md)
- [ ] [72. Event Sourcing](04-Distributed-Systems/72-Event-Sourcing.md)
- [ ] [73. Circuit Breaker Pattern](04-Distributed-Systems/73-Circuit-Breaker.md)
- [ ] [74. Retry + Exponential Backoff](04-Distributed-Systems/74-Retry-Exponential-Backoff.md)
- [ ] [75. Jitter](04-Distributed-Systems/75-Jitter.md)
- [ ] [76. Bulkhead Pattern](04-Distributed-Systems/76-Bulkhead-Pattern.md)
- [ ] [77. Graceful Degradation](04-Distributed-Systems/77-Graceful-Degradation.md)
- [ ] [78. Load Shedding](04-Distributed-Systems/78-Load-Shedding.md)
- [ ] [79. Timeout Pattern](04-Distributed-Systems/79-Timeout-Pattern.md)
- [ ] [80. Health Checks (Liveness + Readiness)](04-Distributed-Systems/80-Health-Checks.md)
- [ ] [81. Failover](04-Distributed-Systems/81-Failover.md)
- [ ] [82. Message Queues](04-Distributed-Systems/82-Message-Queues.md)
- [ ] [83. Kafka — Event Streaming](04-Distributed-Systems/83-Kafka-Event-Streaming.md)
- [ ] [84. RabbitMQ](04-Distributed-Systems/84-RabbitMQ.md)
- [ ] [85. AWS SQS + SNS](04-Distributed-Systems/85-AWS-SQS-SNS.md)
- [ ] [86. Dead Letter Queue (DLQ)](04-Distributed-Systems/86-Dead-Letter-Queue.md)
- [ ] [87. Event-Driven Architecture](04-Distributed-Systems/87-Event-Driven-Architecture.md)
- [ ] [88. Distributed Locks](04-Distributed-Systems/88-Distributed-Locks.md)
- [ ] [89. Leader Election](04-Distributed-Systems/89-Leader-Election.md)
- [ ] [90. Quorum](04-Distributed-Systems/90-Quorum.md)
- [ ] [91. Vector Clocks / Lamport Clocks](04-Distributed-Systems/91-Vector-Lamport-Clocks.md)
- [ ] [92. Service Discovery](04-Distributed-Systems/92-Service-Discovery.md)
- [ ] [93. API Gateway](04-Distributed-Systems/93-API-Gateway.md)
- [ ] [93a. BFF — Backend For Frontend ⭐ (added)](04-Distributed-Systems/93a-BFF-Backend-For-Frontend.md)
- [ ] [94. Service Mesh (Istio)](04-Distributed-Systems/94-Service-Mesh-Istio.md)
- [ ] [95. gRPC](04-Distributed-Systems/95-gRPC.md)
- [ ] [96. WebSocket at Scale](04-Distributed-Systems/96-WebSocket-at-Scale.md)
- [ ] [97. Real-Time Systems](04-Distributed-Systems/97-Real-Time-Systems.md)
- [ ] [98. Microservices Boundaries](04-Distributed-Systems/98-Microservices-Boundaries.md)
- [ ] [99. Database Per Service](04-Distributed-Systems/99-Database-Per-Service.md)

## 05 — Observability + Infra  `05-Observability-Infra/`

- [ ] [100. Observability — Logs](05-Observability-Infra/100-Observability-Logs.md)
- [ ] [101. Observability — Metrics](05-Observability-Infra/101-Observability-Metrics.md)
- [ ] [102. Observability — Traces](05-Observability-Infra/102-Observability-Traces.md)
- [ ] [103. SLI / SLO / SLA](05-Observability-Infra/103-SLI-SLO-SLA.md)
- [ ] [104. Error Budgets](05-Observability-Infra/104-Error-Budgets.md)
- [ ] [105. Disaster Recovery (RPO/RTO)](05-Observability-Infra/105-Disaster-Recovery-RPO-RTO.md)
- [ ] [106. Multi-Region Architecture](05-Observability-Infra/106-Multi-Region-Architecture.md)
- [ ] [107. Kubernetes Basics](05-Observability-Infra/107-Kubernetes-Basics.md)
- [ ] [108. Chaos Engineering](05-Observability-Infra/108-Chaos-Engineering.md)
- [ ] [109. Infrastructure as Code (Terraform)](05-Observability-Infra/109-Infrastructure-as-Code-Terraform.md)
- [ ] [110. Capacity Planning](05-Observability-Infra/110-Capacity-Planning.md)
- [ ] [110a. Deployment Strategies — Blue-Green, Canary, Rolling, Strangler Fig ⭐ (added)](05-Observability-Infra/110a-Deployment-Strategies.md)

## 06 — Backend Design Problems  `06-Backend-Design-Problems/`

- [ ] [111. URL Shortener](06-Backend-Design-Problems/111-URL-Shortener.md)
- [ ] [112. Rate Limiter Design](06-Backend-Design-Problems/112-Rate-Limiter-Design.md)
- [ ] [113. Authentication Service](06-Backend-Design-Problems/113-Authentication-Service.md)
- [ ] [114. Notification System](06-Backend-Design-Problems/114-Notification-System.md)
- [ ] [115. Chat Application (WhatsApp)](06-Backend-Design-Problems/115-Chat-Application-WhatsApp.md)
- [ ] [116. Instagram Design](06-Backend-Design-Problems/116-Instagram-Design.md)
- [ ] [117. Twitter/Feed System](06-Backend-Design-Problems/117-Twitter-Feed-System.md)
- [ ] [118. E-Commerce Platform](06-Backend-Design-Problems/118-E-Commerce-Platform.md)
- [ ] [119. Payment System](06-Backend-Design-Problems/119-Payment-System.md)
- [ ] [120. File Storage (Google Drive)](06-Backend-Design-Problems/120-File-Storage-Google-Drive.md)
- [ ] [121. Video Streaming (YouTube)](06-Backend-Design-Problems/121-Video-Streaming-YouTube.md)
- [ ] [122. Search System (Google)](06-Backend-Design-Problems/122-Search-System-Google.md)
- [ ] [123. Real-Time IoT Platform](06-Backend-Design-Problems/123-Real-Time-IoT-Platform.md)
- [ ] [124. Food Delivery (Swiggy/Zomato)](06-Backend-Design-Problems/124-Food-Delivery-Swiggy-Zomato.md)
- [ ] [125. Ride Sharing (Uber/Ola)](06-Backend-Design-Problems/125-Ride-Sharing-Uber-Ola.md)
- [ ] [126. Analytics Platform](06-Backend-Design-Problems/126-Analytics-Platform.md)

## 07 — Frontend (Web) System Design  `07-Frontend-System-Design/`

- [ ] [F01. Frontend System Design Framework (RADIO)](07-Frontend-System-Design/F01-Frontend-System-Design-Framework-RADIO.md)
- [ ] [F02. How the Browser Renders a Page (Critical Rendering Path)](07-Frontend-System-Design/F02-How-Browser-Renders-Critical-Rendering-Path.md)
- [ ] [F03. Rendering Patterns — CSR vs SSR vs SSG vs ISR](07-Frontend-System-Design/F03-Rendering-Patterns-CSR-SSR-SSG-ISR.md)
- [ ] [F04. React Server Components + Streaming (Next.js App Router)](07-Frontend-System-Design/F04-React-Server-Components-Streaming.md)
- [ ] [F05. Core Web Vitals (LCP, INP, CLS)](07-Frontend-System-Design/F05-Core-Web-Vitals-LCP-INP-CLS.md)
- [ ] [F06. Bundling, Code Splitting + Lazy Loading](07-Frontend-System-Design/F06-Bundling-Code-Splitting-Lazy-Loading.md)
- [ ] [F07. Browser Caching (Cache-Control, ETag)](07-Frontend-System-Design/F07-Browser-Caching-Cache-Control-ETag.md)
- [ ] [F08. Service Workers + PWA + Offline](07-Frontend-System-Design/F08-Service-Workers-PWA-Offline.md)
- [ ] [F09. State Management (Local vs Global vs Server State)](07-Frontend-System-Design/F09-State-Management-Local-Global-Server.md)
- [ ] [F10. Data Fetching + Server State (React Query / SWR)](07-Frontend-System-Design/F10-Data-Fetching-Server-State-React-Query.md)
- [ ] [F11. API Layer for Frontend (REST vs GraphQL vs BFF)](07-Frontend-System-Design/F11-API-Layer-Frontend-REST-GraphQL-BFF.md)
- [ ] [F12. Pagination, Infinite Scroll + Virtualization](07-Frontend-System-Design/F12-Pagination-Infinite-Scroll-Virtualization.md)
- [ ] [F13. Real-Time on Frontend (Polling vs SSE vs WebSocket)](07-Frontend-System-Design/F13-Real-Time-Frontend-Polling-SSE-WebSocket.md)
- [ ] [F14. Frontend Security (XSS, CSRF, CSP)](07-Frontend-System-Design/F14-Frontend-Security-XSS-CSRF-CSP.md)
- [ ] [F15. CORS](07-Frontend-System-Design/F15-CORS.md)
- [ ] [F16. Auth on Frontend (Token Storage + Refresh Flow)](07-Frontend-System-Design/F16-Auth-Frontend-Token-Storage-Refresh.md)
- [ ] [F17. Image + Asset Optimization](07-Frontend-System-Design/F17-Image-Asset-Optimization.md)
- [ ] [F18. Accessibility (a11y)](07-Frontend-System-Design/F18-Accessibility-a11y.md)
- [ ] [F19. Internationalization (i18n)](07-Frontend-System-Design/F19-Internationalization-i18n.md)
- [ ] [F20. Design Systems + Component Libraries](07-Frontend-System-Design/F20-Design-Systems-Component-Libraries.md)
- [ ] [F21. Micro-Frontends + Monorepo](07-Frontend-System-Design/F21-Micro-Frontends-Monorepo.md)
- [ ] [F22. Frontend Observability + Feature Flags + A/B Testing](07-Frontend-System-Design/F22-Frontend-Observability-Feature-Flags-AB-Testing.md)

## 08 — Mobile System Design (React Native)  `08-Mobile-System-Design/`

- [ ] [M01. Mobile System Design Framework](08-Mobile-System-Design/M01-Mobile-System-Design-Framework.md)
- [ ] [M02. How React Native Works (Bridge vs New Architecture — JSI, Fabric, TurboModules)](08-Mobile-System-Design/M02-How-React-Native-Works-Bridge-JSI-Fabric-TurboModules.md)
- [ ] [M03. Hermes + App Startup Time](08-Mobile-System-Design/M03-Hermes-App-Startup-Time.md)
- [ ] [M04. App Lifecycle + Background Tasks](08-Mobile-System-Design/M04-App-Lifecycle-Background-Tasks.md)
- [ ] [M05. Local Storage (AsyncStorage, MMKV, SQLite, WatermelonDB, Keychain)](08-Mobile-System-Design/M05-Local-Storage-AsyncStorage-MMKV-SQLite-WatermelonDB-Keychain.md)
- [ ] [M06. Offline-First Architecture](08-Mobile-System-Design/M06-Offline-First-Architecture.md)
- [ ] [M07. Data Sync + Conflict Resolution](08-Mobile-System-Design/M07-Data-Sync-Conflict-Resolution.md)
- [ ] [M08. Networking on Mobile (Flaky Network, Retry, Batching)](08-Mobile-System-Design/M08-Networking-Mobile-Flaky-Network-Retry-Batching.md)
- [ ] [M09. API Design for Mobile (Payload, Versioning, Backward Compatibility)](08-Mobile-System-Design/M09-API-Design-Mobile-Payload-Versioning-Compatibility.md)
- [ ] [M10. Push Notifications (FCM + APNs)](08-Mobile-System-Design/M10-Push-Notifications-FCM-APNs.md)
- [ ] [M11. Deep Linking + Universal Links](08-Mobile-System-Design/M11-Deep-Linking-Universal-Links.md)
- [ ] [M12. Image Loading + Caching on Mobile](08-Mobile-System-Design/M12-Image-Loading-Caching-Mobile.md)
- [ ] [M13. List Performance (FlatList vs FlashList)](08-Mobile-System-Design/M13-List-Performance-FlatList-vs-FlashList.md)
- [ ] [M14. Mobile Performance (JS Thread vs UI Thread, Memory, Re-renders)](08-Mobile-System-Design/M14-Mobile-Performance-JS-UI-Thread-Memory-Rerenders.md)
- [ ] [M15. Mobile Security (Secure Storage, SSL Pinning, Root/Jailbreak)](08-Mobile-System-Design/M15-Mobile-Security-Secure-Storage-SSL-Pinning-Root.md)
- [ ] [M16. Mobile Auth (Token Refresh + Biometric Login)](08-Mobile-System-Design/M16-Mobile-Auth-Token-Refresh-Biometric.md)
- [ ] [M17. OTA Updates (EAS Update / CodePush)](08-Mobile-System-Design/M17-OTA-Updates-EAS-Update-CodePush.md)
- [ ] [M18. App Release, Versioning + Force Update](08-Mobile-System-Design/M18-App-Release-Versioning-Force-Update.md)
- [ ] [M19. Mobile CI/CD (EAS Build, Fastlane, GitHub Actions)](08-Mobile-System-Design/M19-Mobile-CI-CD-EAS-Build-Fastlane-GitHub-Actions.md)
- [ ] [M20. Location Tracking + Maps](08-Mobile-System-Design/M20-Location-Tracking-Maps.md)
- [ ] [M21. Media Upload from Mobile (Chunked + Resumable)](08-Mobile-System-Design/M21-Media-Upload-Mobile-Chunked-Resumable.md)
- [ ] [M22. Crash Reporting + Analytics (Sentry, Firebase)](08-Mobile-System-Design/M22-Crash-Reporting-Analytics-Sentry-Firebase.md)

## 09 — Full-Stack Design Problems (Mobile + Web + Backend, end-to-end)  `09-FullStack-Design-Problems/`

- [ ] [P01. WhatsApp — mobile app + web + backend](09-FullStack-Design-Problems/P01-WhatsApp-Mobile-Web-Backend.md)
- [ ] [P02. Instagram — Feed + Stories + Reels](09-FullStack-Design-Problems/P02-Instagram-Feed-Stories-Reels.md)
- [ ] [P03. Uber/Ola — Rider app + Driver app + backend](09-FullStack-Design-Problems/P03-Uber-Ola-Rider-Driver-Backend.md)
- [ ] [P04. Swiggy/Zomato — Customer app + Restaurant panel + Delivery app](09-FullStack-Design-Problems/P04-Swiggy-Zomato-Customer-Restaurant-Delivery.md)
- [ ] [P05. Google Docs — Collaborative Editor](09-FullStack-Design-Problems/P05-Google-Docs-Collaborative-Editor.md)
- [ ] [P06. Search Autocomplete / Typeahead](09-FullStack-Design-Problems/P06-Search-Autocomplete-Typeahead.md)
- [ ] [P07. YouTube — Video Player + Upload](09-FullStack-Design-Problems/P07-YouTube-Video-Player-Upload.md)
- [ ] [P08. Amazon/Flipkart — Product Page + Cart + Checkout](09-FullStack-Design-Problems/P08-Amazon-Flipkart-Product-Page-Cart-Checkout.md)
- [ ] [P09. Notification Center (In-app + Push + Email)](09-FullStack-Design-Problems/P09-Notification-Center-InApp-Push-Email.md)
- [ ] [P10. Real-Time Admin / Analytics Dashboard](09-FullStack-Design-Problems/P10-Real-Time-Admin-Analytics-Dashboard.md)

## 10 — AI Engineering  `10-AI-Engineering/`

- [ ] [127. LLM Basics — How it Works](10-AI-Engineering/127-LLM-Basics-How-it-Works.md)
- [ ] [128. OpenAI API + Claude API](10-AI-Engineering/128-OpenAI-API-Claude-API.md)
- [ ] [129. Prompt Engineering](10-AI-Engineering/129-Prompt-Engineering.md)
- [ ] [130. Few-Shot + Zero-Shot](10-AI-Engineering/130-Few-Shot-Zero-Shot.md)
- [ ] [131. Chain of Thought](10-AI-Engineering/131-Chain-of-Thought.md)
- [ ] [132. Structured Output](10-AI-Engineering/132-Structured-Output.md)
- [ ] [133. Embeddings](10-AI-Engineering/133-Embeddings.md)
- [ ] [134. Vector Databases](10-AI-Engineering/134-Vector-Databases.md)
- [ ] [135. Pinecone + pgvector](10-AI-Engineering/135-Pinecone-pgvector.md)
- [ ] [136. Chunking Strategies](10-AI-Engineering/136-Chunking-Strategies.md)
- [ ] [137. RAG — Full Pipeline](10-AI-Engineering/137-RAG-Full-Pipeline.md)
- [ ] [138. Hybrid Search (BM25 + Vector)](10-AI-Engineering/138-Hybrid-Search-BM25-Vector.md)
- [ ] [139. Reranking](10-AI-Engineering/139-Reranking.md)
- [ ] [140. Tool Use / Function Calling](10-AI-Engineering/140-Tool-Use-Function-Calling.md)
- [ ] [141. ReAct Pattern](10-AI-Engineering/141-ReAct-Pattern.md)
- [ ] [142. LangChain Basics](10-AI-Engineering/142-LangChain-Basics.md)
- [ ] [143. LangGraph](10-AI-Engineering/143-LangGraph.md)
- [ ] [144. Multi-Agent Systems](10-AI-Engineering/144-Multi-Agent-Systems.md)
- [ ] [145. Agent Memory Types](10-AI-Engineering/145-Agent-Memory-Types.md)
- [ ] [146. RAG Evaluation (Ragas)](10-AI-Engineering/146-RAG-Evaluation-Ragas.md)
- [ ] [147. LangSmith Observability](10-AI-Engineering/147-LangSmith-Observability.md)
- [ ] [148. LLM Caching](10-AI-Engineering/148-LLM-Caching.md)
- [ ] [149. Guardrails + Safety](10-AI-Engineering/149-Guardrails-Safety.md)
- [ ] [150. Fine Tuning Basics](10-AI-Engineering/150-Fine-Tuning-Basics.md)
- [ ] [151. AI System Design at Scale](10-AI-Engineering/151-AI-System-Design-at-Scale.md)
- [ ] [152. Hallucination Handling](10-AI-Engineering/152-Hallucination-Handling.md)
- [ ] [153. Cost Optimization (Tokens)](10-AI-Engineering/153-Cost-Optimization-Tokens.md)
- [ ] [154. Streaming Responses](10-AI-Engineering/154-Streaming-Responses.md)
- [ ] [155. Deploy AI App (Docker + AWS)](10-AI-Engineering/155-Deploy-AI-App-Docker-AWS.md)

## 11 — Interview Playbook  `11-Interview-Playbook/`

- [ ] [01. How to Answer a Backend System Design Round (step-by-step framework)](11-Interview-Playbook/01-How-to-Answer-Backend-System-Design-Round.md)
- [ ] [02. How to Answer a Frontend / Mobile System Design Round](11-Interview-Playbook/02-How-to-Answer-Frontend-Mobile-System-Design-Round.md)
- [ ] [03. Back-of-the-Envelope Estimation ⭐](11-Interview-Playbook/03-Back-of-the-Envelope-Estimation.md)
- [ ] [04. Numbers Every Engineer Should Know (latency, sizes, QPS)](11-Interview-Playbook/04-Numbers-Every-Engineer-Should-Know.md)
- [ ] [05. Revision Sheet — Fundamentals](11-Interview-Playbook/05-Revision-Sheet-Fundamentals.md)
- [ ] [06. Revision Sheet — Databases + Caching](11-Interview-Playbook/06-Revision-Sheet-Databases-Caching.md)
- [ ] [07. Revision Sheet — Auth, Security + Distributed Systems](11-Interview-Playbook/07-Revision-Sheet-Auth-Security-Distributed-Systems.md)
- [ ] [08. Revision Sheet — Frontend + Mobile](11-Interview-Playbook/08-Revision-Sheet-Frontend-Mobile.md)
- [ ] [09. Revision Sheet — AI Engineering](11-Interview-Playbook/09-Revision-Sheet-AI-Engineering.md)
- [ ] [10. Top 100 Most-Asked Questions (with short answers)](11-Interview-Playbook/10-Top-100-Most-Asked-Questions.md)
- [ ] [11. Common Mistakes in System Design Interviews](11-Interview-Playbook/11-Common-Mistakes-in-System-Design-Interviews.md)
- [ ] [12. "Tell me about a system you designed" — how to present your own projects](11-Interview-Playbook/12-Tell-Me-About-a-System-You-Designed.md)

---

## 🧭 Legend
- ⭐ (added) = not in the original list, but asked very often in interviews.
- Original master prompt: [How.md](How.md)
