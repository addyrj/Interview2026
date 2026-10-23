# 05. Revision Sheet — Fundamentals
# हिंदी में: Fundamentals की Revision Sheet — Internet, DNS, TCP/UDP, HTTP/HTTPS, TLS, REST, GraphQL, WebSockets, proxies, monolith बनाम microservices, scaling, latency/throughput/availability, load balancing, stateless design और SPOF — इंटरव्यू से पहले 20 मिनट में दोहराने के लिए (Topics 01–24)

---

## 🔵 Simple Definition (English)
A **one-page refresher** of the fundamentals folder (`01-Fundamentals/`, Topics 01–24): the one-line definition, the key mechanism, the interview trap and the "when to use" rule for each concept. Use it the night before or 30 minutes before an interview, then open the full topic file for anything that feels shaky.

## 🔵 सरल परिभाषा (Hindi)
`01-Fundamentals/` (Topics 01–24) की एक पन्ने वाली दोहराई — हर concept की एक-line परिभाषा, मुख्य तरीका, इंटरव्यू का जाल और "कब इस्तेमाल करें"। इंटरव्यू से पहली रात या 30 मिनट पहले पढ़ो; जो कमज़ोर लगे उसकी पूरी file खोलो।

---

## 🔴 Problem it Solves
Before an interview you can't re-read 24 long files. You need **fast recall** of the essentials and of the **typical follow-up questions**, so you answer crisply and connect concepts during design ("Why WebSocket instead of polling?", "What's the SPOF here?").

## 🔴 यह क्यों बना? (Hindi)
इंटरव्यू से पहले 24 लंबी files दोबारा नहीं पढ़ सकते — ज़रूरी बातें और आम follow-up सवाल जल्दी याद आने चाहिए, ताकि design के दौरान साफ़ जवाब और concepts को जोड़ सको ("polling की जगह WebSocket क्यों?", "यहाँ SPOF कहाँ है?")।

---

## 🟢 How it Works — Step by Step (the cheat sheet)

### Networking (01–06)

```
How the internet works (01): URL → DNS → TCP (+TLS) → HTTP request → server → response → render.
  Packets routed via ISPs/BGP; CDN edges near users. Trap: forgetting DNS & TLS cost on first request.
DNS (02): domain → IP via resolver → root → TLD → authoritative; cached by TTL. Records: A/AAAA, CNAME,
  MX, TXT, NS. Uses: GeoDNS/latency routing, failover. Trap: low TTL for fast failover vs more queries.
IP & ports (03): IP = machine address (IPv4 32-bit, IPv6 128-bit); port = process (443 HTTPS, 5432 Postgres).
  Private ranges (10/8, 172.16/12, 192.168/16) behind NAT.
TCP vs UDP (04): TCP = connection, ordered, reliable, congestion control (web, APIs, DB). UDP = connectionless,
  fast, no guarantees (video calls, gaming, DNS, QUIC builds reliability on UDP). Trap: "UDP is always faster".
HTTP vs HTTPS (05): HTTP/1.1 (keep-alive, head-of-line blocking), HTTP/2 (multiplexing, header compression),
  HTTP/3 (QUIC over UDP, no TCP HOL, connection migration). HTTPS = HTTP over TLS.
TLS (06): handshake (1-RTT in TLS 1.3) → certificate verification (chain to CA) → key exchange (ECDHE,
  forward secrecy) → symmetric encryption (AES-GCM). mTLS for service-to-service. Trap: TLS ≠ authorization.
```

### APIs & real-time (07, 07a, 08)

```
REST (07): resources + HTTP verbs; status codes; idempotent GET/PUT/DELETE; cursor pagination; versioning;
  stateless; cacheable. Trap: POST not idempotent → use Idempotency-Key.
GraphQL (07a): single endpoint, client picks fields, schema & types; fixes over/under-fetching. Costs: N+1
  (DataLoader), caching harder, query cost limits.
WebSockets (08): HTTP Upgrade → persistent full-duplex; for chat, live location, collaboration. Need
  heartbeats, reconnect with backoff, sticky routing or pub/sub fan-out. Alternatives: SSE (server→client),
  long polling, short polling.
```

### Architecture basics (09–14)

```
Client-server (09): clients request, servers serve; thin vs thick clients.
Request-response lifecycle (10): DNS → TCP/TLS → LB → app → cache/DB → response; add timeouts at each hop.
Reverse proxy / Nginx (11): in front of servers: TLS termination, load balancing, caching, compression,
  rate limiting, hiding internals. Forward proxy (12): in front of CLIENTS (corporate egress, anonymity).
Monolith (13): one deployable; simple, fast to start, easy transactions; scaling & team coupling issues later.
Microservices (14): independently deployable services per domain; team autonomy, independent scaling;
  costs: network calls, distributed data/consistency, ops complexity, observability. Rule: start modular
  monolith; split when team/scale demands.
```

### Scaling & performance (15–20)

```
Vertical scaling (15): bigger machine; simple, limited ceiling, SPOF.
Horizontal scaling (16): more machines behind LB; needs stateless services, shared state in DB/cache.
Latency (17): time per request; measure p50/p95/p99 (tail matters); reduce via caching, CDN, fewer round
  trips, async, parallel calls.
Throughput (18): requests/sec; increase via horizontal scaling, batching, async, connection pooling.
  Latency vs throughput trade-off (batching raises throughput, may raise latency).
Availability (19): uptime %; nines (99.9 ≈ 8.8 h/yr, 99.99 ≈ 52 min/yr); achieved by redundancy,
  failover, health checks, multi-AZ; serial dependencies multiply downtime.
Bandwidth (20): data rate capacity of a link (Mbps/Gbps) vs throughput actually achieved; CDN offloads egress.
```

### Load balancing & design principles (21–24)

```
Load balancing basics (21): distribute traffic, health checks, remove unhealthy nodes; L4 (TCP) vs L7 (HTTP,
  path/host routing, TLS termination). Global LB/GeoDNS for multi-region.
Algorithms (22): round robin, weighted RR, least connections, least response time, IP hash, consistent hashing
  (stickiness/caches). Trap: sticky sessions hurt scaling → externalize session state.
Stateless vs stateful (23): stateless servers keep no per-user state in memory → any server can serve any
  request → easy scaling; state lives in DB/Redis/JWT. Stateful (WebSocket gateways, DBs) need special handling.
SPOF (24): any single component whose failure stops the system (one DB, one LB, one region, one DNS
  provider, one engineer!). Remove with redundancy, replication, failover, multi-AZ/region, runbooks.
```

### Quick "which one?" decisions

```
Need server push one-way? → SSE ; two-way low latency? → WebSocket ; rare updates? → polling
Public cacheable API? → REST ; many clients with varied data needs? → GraphQL/BFF
Small team, new product? → modular monolith ; many teams & independent scaling? → microservices
Read latency issue? → cache/CDN ; write throughput issue? → sharding/queues ; availability? → redundancy
```

## 🟢 कैसे काम करता है? (Hindi)
1. Networking: URL → DNS (TTL से cache; GeoDNS/failover) → TCP (+TLS 1.3 का 1-RTT handshake) → HTTP; TCP भरोसेमंद और क्रम वाला, UDP तेज़ पर बिना गारंटी (video call, DNS, QUIC); HTTP/2 multiplexing, HTTP/3 = QUIC (UDP पर, नेटवर्क बदलने पर भी कनेक्शन)।
2. APIs: REST (resources, verbs, status codes, idempotency key, cursor pagination), GraphQL (client fields चुने; N+1 और caching का ध्यान), WebSocket (दोनों तरफ़, heartbeat, reconnect; एक-तरफ़ा के लिए SSE)।
3. Architecture: reverse proxy (servers के आगे — TLS, LB, cache, rate limit) बनाम forward proxy (clients के आगे); monolith पहले (सरल), microservices तब जब टीमें/पैमाना माँगें (network, consistency, ops का ख़र्च)।
4. Scaling: vertical (बड़ी machine, सीमा) बनाम horizontal (कई machines, stateless ज़रूरी); latency p99 देखो, throughput batching/async से; availability के nines और redundancy; bandwidth बनाम असली throughput।
5. LB: L4 बनाम L7, health checks, algorithms (round robin, least connections, consistent hashing), sticky sessions से बचो; stateless servers आसानी से scale; SPOF ढूँढो (एक DB, एक LB, एक region) और redundancy से हटाओ; जल्दी फ़ैसले — push के लिए SSE/WebSocket, read धीमा → cache/CDN, write भारी → sharding/queues।

---

## 🟡 Real World Example
- **HTTP/3 at Google, Cloudflare, Meta**: QUIC improves performance on lossy mobile networks. Uber reported tail-latency gains in markets including India.
- **Netflix and Amazon** moved from monoliths to microservices as teams and scale grew, while Shopify famously kept a modular monolith. Both are valid.
- **WhatsApp**: persistent connections (WebSocket-like) at massive scale, with ~2M connections per server reported in 2012.

## 🟡 Real Example Hindi में
- Google, Cloudflare, Meta पर HTTP/3 (QUIC) कमज़ोर mobile नेटवर्क पर तेज़ है; Uber ने भारत जैसे बाज़ारों में tail latency सुधार बताया।
- Netflix/Amazon टीम और पैमाना बढ़ने पर microservices पर गए, जबकि Shopify ने modular monolith रखा — दोनों सही रास्ते।
- WhatsApp: भारी पैमाने पर हमेशा खुले कनेक्शन (2012 में एक server पर ~20 लाख)।

---

## 🟠 My Stack Example

### Stack mapping (where each fundamental shows up)
```
Nginx (11, 21, 22): TLS termination, reverse proxy, upstream least_conn, rate limiting
Node/Express & FastAPI (07, 10, 23): stateless REST APIs, JWT/session in Redis, timeouts per hop
React/Next.js & React Native (05, 08): HTTPS, HTTP/2, WebSocket/SSE for live updates
Docker + AWS (15, 16, 19, 24): horizontal scaling (ECS/ASG), multi-AZ RDS, ALB health checks, Route 53 failover
```

---

## ⚫ Interview Questions + Answers (rapid fire)

**Q1: What happens when you type a URL and press Enter?**
A1: The browser checks its caches, then DNS resolves the domain to an IP (recursive resolver, root, TLD, authoritative). It opens a TCP connection (or QUIC for HTTP/3), performs a TLS handshake and verifies the certificate, then sends the HTTP request. A CDN or load balancer routes it to a server, which processes it (cache or DB) and responds. The browser parses HTML, fetches CSS, JS and images (often from the CDN), builds the DOM and CSSOM, lays out, paints and runs JavaScript.

**Q2: TCP vs UDP — when do you choose each?**
A2: TCP when you need reliable, ordered delivery with congestion control: web, APIs, databases, file transfer. UDP when low latency matters more than reliability, or when the application implements its own reliability: real-time voice and video, gaming, DNS, and QUIC (HTTP/3), which builds reliability and encryption on top of UDP.

**Q3: Why should application servers be stateless?**
A3: So any instance can handle any request. That enables horizontal scaling, load balancing without sticky sessions, rolling deploys and easy recovery from instance failures. Session and user state go to shared stores (Redis, DB) or signed tokens (JWT). Stateful components (DBs, WebSocket gateways) are scaled with specific techniques such as replication, sharding and connection routing.

**Q4: How do you remove single points of failure?**
A4: Identify every component whose failure stops the system (load balancer, database primary, cache, region, DNS, third-party dependency). Add redundancy (multiple instances across AZs, replicas with automated failover, multi-region for critical paths), health checks and automatic rerouting, graceful degradation when dependencies fail (serve cached data), backups and tested runbooks. Also avoid human SPOFs through on-call rotation and documentation.

**Q5: REST vs GraphQL vs WebSocket — one-line guidance?**
A5: REST for resource-oriented, cacheable request-response APIs (the default). GraphQL when many clients need different shapes of nested data in one round trip. WebSocket when the server and client exchange real-time messages both ways (chat, live tracking). SSE when only the server pushes updates.

---

## 🔷 Trade-offs
✅ Fundamentals answered crisply → earns trust early in the interview — ❌ don't recite; connect them to the design at hand.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| DNS | Name → IP system | नाम से IP |
| TCP / UDP | Reliable / fast transport | भरोसेमंद / तेज़ transport |
| TLS | Encryption + server identity | encryption + पहचान |
| HTTP/2 / HTTP/3 | Multiplexed / QUIC-based HTTP | नए HTTP versions |
| Reverse proxy | Front door for servers | servers का दरवाज़ा |
| Horizontal scaling | Add machines | machines जोड़ना |
| p99 latency | Tail latency | सबसे धीमे 1% की सीमा |
| L4 / L7 LB | Transport / application LB | परत 4 / 7 balancer |
| Stateless | No per-user memory on server | server पर state नहीं |
| SPOF | Single point of failure | अकेला कमज़ोर बिंदु |

---

## ⚡ 3-Line Summary
**English:**
1. Networking path: DNS → TCP/QUIC → TLS → HTTP(1.1/2/3) → LB/proxy → stateless app → cache/DB.
2. APIs: REST default, GraphQL for flexible nested data, WebSocket/SSE for real-time; idempotency & pagination matter.
3. Scale & reliability: horizontal scaling with stateless servers, L4/L7 load balancing, tail latency, nines, and eliminating SPOFs.

**Hindi:**
1. रास्ता: DNS → TCP/QUIC → TLS → HTTP → LB/proxy → stateless ऐप → cache/DB।
2. APIs: REST default, GraphQL लचीले डेटा के लिए, real-time के लिए WebSocket/SSE।
3. पैमाना और भरोसा: stateless + horizontal scaling, L4/L7 LB, p99, nines, SPOF हटाओ।

---

## ➡️ Next Topic Suggestion
**06. Revision Sheet — Databases + Caching** — The second most-asked area: SQL vs NoSQL, indexes, transactions, replication, sharding, caching patterns and storage. Next: the one-page database and caching refresher (Topics 25–53).
