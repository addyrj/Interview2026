# 04. Numbers Every Engineer Should Know (latency, sizes, QPS)
# हिंदी में: हर Engineer को याद रहने चाहिए ऐसे Numbers — memory, SSD, network, शहरों/देशों के बीच की latency, आम systems (Redis, Postgres, Kafka) की लगभग क्षमता, availability के "nines", डेटा के आकार और LLM के numbers — ताकि अनुमान और design के फ़ैसले सही पैमाने पर हों

---

## 🔵 Simple Definition (English)
These are **order-of-magnitude reference numbers** used in system design to reason about **latency, throughput, capacity, availability and cost**. They're not exact benchmarks (hardware and workloads vary), but they tell you instantly that:
- **memory is ~1000× faster than SSD**, which is much faster than a network round trip across regions
- a **cache lookup costs microseconds**, a **database query milliseconds** and a **cross-continent call ~100–250 ms**
- **99.99% availability allows only ~52 minutes of downtime per year**
- a single Redis node handles **~100k simple ops/s**, while a single Postgres primary handles **thousands to tens of thousands** of simple queries/s
- an LLM produces **tens to ~150 tokens per second**, and its first token arrives in **~0.3–1.5 s**
Memorize the **ratios**, not the decimals.

## 🔵 सरल परिभाषा (Hindi)
ये पैमाने वाले (order-of-magnitude) संदर्भ numbers हैं जो latency, throughput, capacity, availability और ख़र्च पर सोचने में मदद करते हैं — सटीक benchmark नहीं (hardware/काम के हिसाब से बदलते हैं), पर तुरंत बताते हैं: memory SSD से ~1000 गुना तेज़, जो देशों के बीच network से बहुत तेज़; cache lookup माइक्रोसेकंड, DB query मिलीसेकंड, महाद्वीपों के पार ~100–250 ms; 99.99% = साल में सिर्फ़ ~52 मिनट बंद; एक Redis node ~1 लाख ops/s, एक Postgres primary हज़ारों से दसियों हज़ार queries/s; LLM ~दसियों से 150 tokens/s और पहला token ~0.3–1.5 s में। दशमलव नहीं, अनुपात याद रखो।

---

## 🔴 Problem it Solves
Without reference numbers, engineers make wrong calls:
- "Let's call the user service 20 times per request". At 2 ms each that's 40 ms, while the latency budget is 50 ms.
- "Store sessions in Postgres and read them on every request" versus Redis in microseconds.
- "Serve Indian users from us-east-1". That adds ~200+ ms per round trip, multiplied by several round trips (TLS, API calls).
- "We promise 99.999% availability" without knowing that means ~5 minutes of downtime a year.
- "One Kafka partition is enough" for 500 MB/s.
In interviews, quoting the right magnitudes makes estimations credible and trade-offs concrete.

## 🔴 यह क्यों बना? (Hindi)
संदर्भ numbers के बिना ग़लत फ़ैसले: "हर request पर user service को 20 बार call करो" (2 ms × 20 = 40 ms जबकि पूरा budget 50 ms); "sessions हर request पर Postgres से पढ़ो" (Redis माइक्रोसेकंड में); "भारतीय यूज़र्स को us-east-1 से serve करो" (हर round trip ~200+ ms, कई round trips के साथ); "99.999% availability का वादा" (साल में ~5 मिनट बंद!); "500 MB/s के लिए एक Kafka partition काफ़ी"।
इंटरव्यू में सही पैमाने बताने से अनुमान भरोसेमंद और trade-offs ठोस बनते हैं।

---

## 🟢 How it Works — Step by Step

### Latency ladder (approximate, modern hardware)

```
L1 cache reference ............................ ~1 ns
Branch mispredict / L2 cache ................... ~3–5 ns
Mutex lock/unlock .............................. ~20–50 ns
Main memory (RAM) reference .................... ~100 ns
Compress 1 KB (fast codec) ..................... ~2–3 µs
Send 1 KB over 1–10 Gbps network ............... ~1–10 µs
Redis GET in same AZ (incl. network) ........... ~0.2–1 ms   (server-side work ≈ µs)
NVMe SSD random 4 KB read ...................... ~20–100 µs
Read 1 MB sequentially from RAM ................ ~50–250 µs
Round trip within a datacenter/AZ .............. ~0.1–0.5 ms
Read 1 MB sequentially from SSD ................ ~0.5–1 ms
Simple indexed DB query (same AZ) .............. ~1–5 ms
Cross-AZ round trip (same region) .............. ~1–2 ms
HDD seek ....................................... ~5–10 ms
Read 1 MB sequentially from HDD ................ ~5–20 ms
Mumbai ↔ Chennai/Delhi round trip .............. ~20–40 ms
Mumbai ↔ Singapore round trip .................. ~50–70 ms
Mumbai ↔ Europe (Frankfurt/London) ............. ~110–150 ms
Mumbai ↔ US East ............................... ~180–250 ms
Mobile network RTT India (4G/5G, good) ......... ~30–80 ms ; congested/3G ~150–500+ ms
TLS 1.3 handshake = +1 RTT (0-RTT on resumption); TCP handshake = +1 RTT
Human perception: < 100 ms feels instant; 1 s keeps flow; > 10 s loses attention
```

### Takeaways from the ladder

```
RAM ≈ 1000× faster than SSD random reads ≈ (SSD) ≫ network across regions
→ Cache hot data in memory; batch & avoid chatty network calls; keep users near servers/CDN
→ Every cross-region hop costs ~100–250 ms → India users → ap-south-1 (Mumbai) / ap-south-2 (Hyderabad) + CDN edges
→ Mobile RTTs dominate app latency → fewer round trips (BFF, HTTP/2–3)
```

### Throughput rules of thumb (single node, simple operations, well-tuned)

```
Redis (single-threaded core) ........ ~100k+ ops/s per node (pipelining → more); cluster scales linearly
Memcached ........................... ~100k–1M ops/s per node (multi-threaded)
PostgreSQL / MySQL primary .......... ~5k–50k simple indexed QPS; writes lower; depends heavily on schema/IO
Kafka ............................... partition ~10–50 MB/s; broker ~100s MB/s–1 GB/s; scale via partitions
Elasticsearch/OpenSearch ............ hundreds–thousands of queries/s per node (query-dependent)
Web/API server (Go/Node/FastAPI) .... ~1k–10k+ simple req/s per instance (I/O-bound async helps)
Nginx (static/proxy) ................ tens of thousands of req/s per node
WebSocket gateway ................... ~100k–1M+ idle connections per tuned server (memory-bound)
Object storage (S3) ................. very high aggregate throughput; per-prefix request rates in thousands/s
1 Gbps link ≈ 125 MB/s ; 10 Gbps ≈ 1.25 GB/s
```

### Availability "nines"

```
┌──────────────┬───────────────────┬────────────────┬─────────────────┐
│ Availability │ Downtime / year   │ / month        │ / week          │
├──────────────┼───────────────────┼────────────────┼─────────────────┤
│ 99%          │ ~3.65 days        │ ~7.3 hours     │ ~1.7 hours      │
│ 99.9%        │ ~8.77 hours       │ ~43.8 minutes  │ ~10.1 minutes   │
│ 99.95%       │ ~4.38 hours       │ ~21.9 minutes  │ ~5 minutes      │
│ 99.99%       │ ~52.6 minutes     │ ~4.38 minutes  │ ~1 minute       │
│ 99.999%      │ ~5.26 minutes     │ ~26 seconds    │ ~6 seconds      │
└──────────────┴───────────────────┴────────────────┴─────────────────┘
Serial dependencies multiply: 3 services at 99.9% each → ~99.7% overall
Redundancy improves: two independent 99% replicas → 1 − 0.01² = 99.99% (if failures independent)
```

### Data size references

```
Powers of 2: 2¹⁰ ≈ 1 thousand (KB), 2²⁰ ≈ 1 million (MB), 2³⁰ ≈ 1 billion (GB), 2⁴⁰ ≈ 1 trillion (TB)
Integers: int32 4 B (±2.1 × 10⁹), int64 8 B; UUID 16 B (36 chars as text); IPv4 4 B; IPv6 16 B
Text: ASCII 1 B/char; Devanagari/most Indic in UTF-8 ≈ 3 B/char; emoji 4 B
Typical objects: user profile row ~1 KB; chat message ~100–300 B; tweet ~300 B–1 KB; JSON response 1–10 KB
Media: thumbnail 20–50 KB; phone photo (compressed) 0.2–3 MB; 1 min video upload 1080p ~50–150 MB;
       streaming 1080p ~4–8 Mbps (≈ 30–60 MB/min); 720p ~2–4 Mbps; audio ~64–128 kbps
Vector embedding: 1024 dims × 4 B = 4 KB (float32), 2 KB (float16)
```

### Time references

```
1 day ≈ 86,400 s ≈ 10⁵ s ; 1 month ≈ 2.6 × 10⁶ s ; 1 year ≈ 3.15 × 10⁷ s
1M requests/day ≈ 12 QPS ; 1B/day ≈ 12k QPS
```

### LLM numbers (2025–26 ballpark; check your provider)

```
English: ~4 characters ≈ 1 token; ~0.75 words per token; Hindi/Indic often 2–4× more tokens per sentence
TTFT: ~0.3–1.5 s (longer for big prompts/reasoning models); output speed ~30–150+ tokens/s
Context windows: ~100k–1M+ tokens (model-dependent); output caps typically several thousand+ tokens
Embedding dimensions: ~512–3072; embedding latency ~10s of ms per batch call
Prompt caching: cached input tokens billed at a fraction of normal input; batch APIs ~50% discount
```

## 🟢 कैसे काम करता है? (Hindi)
1. Latency की सीढ़ी: RAM ~100 ns, NVMe SSD random ~20–100 µs, data center के अंदर round trip ~0.1–0.5 ms, indexed DB query ~1–5 ms, Mumbai ↔ Delhi ~20–40 ms, Mumbai ↔ Singapore ~50–70 ms, Mumbai ↔ US East ~180–250 ms, भारत का 4G ~30–80 ms (भीड़/3G पर 150–500+ ms); TLS/TCP handshake = +1 RTT।
2. सबक: RAM SSD से ~1000 गुना तेज़ — hot डेटा memory में; बार-बार network calls मत करो, batch करो; भारतीय यूज़र्स के लिए Mumbai/Hyderabad region + CDN; mobile पर round trips घटाओ (BFF, HTTP/2–3)।
3. Throughput: Redis ~1 लाख+ ops/s प्रति node, Postgres primary ~5k–50k सरल queries/s, Kafka partition ~10–50 MB/s, API server ~1k–10k req/s, WebSocket gateway ~1 लाख–10 लाख कनेक्शन, 1 Gbps ≈ 125 MB/s।
4. Nines: 99.9% = साल में ~8.8 घंटे, 99.99% = ~52 मिनट, 99.999% = ~5 मिनट; एक के बाद एक 3 services (99.9% हर एक) = ~99.7%; दो स्वतंत्र 99% replicas = 99.99%।
5. आकार: UUID 16 B, देवनागरी अक्षर ~3 B, chat message ~100–300 B, photo 0.2–3 MB, 1080p stream ~4–8 Mbps, 1024-dim embedding 4 KB; समय: 1 दिन ≈ 10⁵ s, 10 लाख/दिन ≈ 12 QPS; LLM: ~4 अक्षर = 1 token (हिंदी में 2–4 गुना), TTFT ~0.3–1.5 s, 30–150 tokens/s।

---

## 🟡 Real World Example

**Jeff Dean / Peter Norvig latency numbers** — circulated widely from Google talks in the late 2000s ("L1 cache 0.5 ns … packet CA→Netherlands→CA 150 ms"). Hardware has improved (SSDs, networks), but the **ratios** still guide caching, batching and placement decisions.

**Amazon's latency insight** — the widely quoted finding that extra latency measurably reduces sales (e.g., 100 ms ≈ 1%) is why teams obsess over p99 and CDN placement.

**Indian region launches** — AWS (Mumbai 2016, Hyderabad 2022), Google Cloud (Mumbai, Delhi) and Azure Indian regions cut round trips for Indian users from ~200 ms (US) to tens of ms, which is critical for UPI, trading apps (Zerodha) and gaming.

**SRE error budgets** — Google SRE practice translates availability targets into concrete downtime budgets (99.9% means ~43 minutes a month), guiding how fast teams can ship and when to freeze releases.

## 🟡 Real Example Hindi में
Jeff Dean/Peter Norvig की latency सूची (Google, 2000s के आख़िर) — hardware सुधरा पर अनुपात आज भी cache, batching और placement के फ़ैसले तय करते हैं; Amazon की बात (100 ms ≈ 1% बिक्री) से टीमें p99 और CDN पर ध्यान देती हैं।
AWS Mumbai (2016), Hyderabad (2022), Google Cloud और Azure के भारतीय regions से भारतीय यूज़र्स की round trip ~200 ms (US) से दसियों ms हुई — UPI, Zerodha जैसे trading ऐप और gaming के लिए ज़रूरी; Google SRE में 99.9% = महीने में ~43 मिनट का error budget — release की रफ़्तार इसी से।

---

## 🟠 My Stack Example

### Quick latency budget for an API call (Mumbai users, Mumbai region)
```
Client (4G) RTT 50 ms × (TLS resumption 0–1 + request 1) ≈ 50–100 ms network
API gateway + auth (JWT verify, local) ......... 1–2 ms
Redis cache hit (session/profile) .............. 0.5 ms
Postgres indexed query × 2 ..................... 4–8 ms
Downstream service call (same AZ) .............. 3–10 ms
Serialization, logging ......................... 1–2 ms
→ Server time ~15–25 ms; user-perceived ~70–130 ms → good. From us-east-1: +200 ms per RTT ✗
```

### Availability math helper
```python
import math
def serial(*avail): return math.prod(avail)                                  # all must work
def parallel(a, n): return 1 - (1 - a) ** n                                  # any one works (independent)
print(serial(0.999, 0.999, 0.999))   # ≈ 0.997 → ~26 h downtime/yr
print(parallel(0.99, 2))             # 0.9999
```

---

## ⚫ Interview Questions + Answers

**Q1: Why do latency numbers matter in system design?**
A1: They let you reason about where time goes and which designs can meet latency targets. Memory access is nanoseconds, SSD reads tens of microseconds, intra-datacenter round trips sub-millisecond, database queries milliseconds and cross-continent calls hundreds of milliseconds. That justifies caching hot data in memory, batching or parallelizing calls instead of chatty sequential RPCs, placing servers and CDNs near users (Mumbai for Indian users), and minimizing mobile round trips.

**Q2: What does 99.99% availability mean in practice?**
A2: About 52.6 minutes of downtime per year, or roughly 4.4 minutes per month. Achieving it requires redundancy across availability zones, no single points of failure, automated failover, safe deployments (canaries, quick rollback), strong monitoring and limited dependencies, because serial dependencies multiply unavailability. Ask whether the business really needs it, since each extra nine increases cost and complexity significantly.

**Q3: Roughly how much can a single Redis or Postgres node handle?**
A3: As rules of thumb for simple operations on well-tuned hardware, a Redis node handles on the order of 100k operations per second (more with pipelining), with clustering for more. A Postgres or MySQL primary handles thousands to tens of thousands of simple indexed queries per second, with writes lower and results heavily dependent on schema, indexes, transaction patterns and I/O. Use these for initial sizing, then benchmark real workloads.

**Q4: How does geography affect your design for Indian users?**
A4: Round trips from India to US regions are ~180–250 ms and to Europe ~110–150 ms, while within India they're tens of ms. Since a request involves multiple round trips (TCP, TLS, API calls), hosting in Indian regions (Mumbai, Hyderabad) with CDN edges in major Indian cities dramatically improves latency. Data-residency rules (RBI for payments data, DPDP considerations) often require Indian regions anyway. For global users, deploy multi-region with geo-routing.

**Q5: What LLM performance numbers should you keep in mind?**
A5: Roughly 4 characters of English per token (Indic languages often need several times more), time to first token around 0.3–1.5 s for typical prompts (longer for very large contexts or reasoning models), output speeds of tens to ~150 tokens per second, context windows from about 100k to over a million tokens depending on model, and pricing per million input and output tokens with discounts for cached input and batch jobs. These drive latency budgets (stream responses), cost estimates and context design.

---

## 🔷 Trade-offs
✅ Memorized magnitudes: fast, credible reasoning — ❌ numbers drift with hardware/providers → speak in ranges and say you'd benchmark.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Latency | Time for one operation | एक काम का समय |
| Throughput | Operations per second | प्रति सेकंड काम |
| RTT | Round-trip time | आने-जाने का समय |
| p99 | 99th percentile latency | 99% requests की सीमा |
| Nines | Availability percentage | उपलब्धता के 9 |
| Error budget | Allowed unreliability | अनुमत गड़बड़ी |
| AZ / region | Datacenter zone / geography | data center क्षेत्र |
| Egress | Outbound data | बाहर जाता डेटा |
| TTFT | Time to first token | पहला token |
| Order of magnitude | Power-of-ten scale | 10 की घात |

---

## ⚡ 3-Line Summary
**English:**
1. Latency ladder: RAM ~100 ns ≪ SSD ~tens of µs ≪ intra-DC RTT ~0.1–0.5 ms ≪ DB query ~ms ≪ cross-region ~100–250 ms; mobile RTTs dominate apps.
2. Throughput rules: Redis ~100k ops/s/node, Postgres ~5k–50k QPS, Kafka partition ~10–50 MB/s, API instance ~1k–10k req/s; nines → 99.99% ≈ 52 min/yr.
3. Sizes & time: 1 day ≈ 10⁵ s, 1M/day ≈ 12 QPS, Devanagari ≈ 3 B/char, photo ~MB, 1080p ~5 Mbps; LLM ~4 chars/token, TTFT ~0.3–1.5 s.

**Hindi:**
1. Latency: RAM ≪ SSD ≪ DC के अंदर ≪ DB query ≪ दूसरे देश (~100–250 ms); mobile round trips सबसे भारी।
2. क्षमता: Redis ~1 लाख ops/s, Postgres ~5k–50k QPS, Kafka partition ~10–50 MB/s; 99.99% ≈ साल में 52 मिनट।
3. आकार/समय: 1 दिन ≈ 10⁵ s, 10 लाख/दिन ≈ 12 QPS, देवनागरी ~3 B/अक्षर; LLM ~4 अक्षर/token, TTFT ~0.3–1.5 s।

---

## ➡️ Next Topic Suggestion
**05. Revision Sheet — Fundamentals** — With the numbers ready, revise the core concepts fast. Next: a one-page refresher of networking, APIs, scaling, load balancing and architecture basics (Topics 01–24).
