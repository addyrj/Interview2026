# 03. Back-of-the-Envelope Estimation ⭐
# हिंदी में: Back-of-the-Envelope Estimation — इंटरव्यू में 3–5 मिनट में मोटे-मोटे numbers निकालना: कितनी requests प्रति सेकंड (QPS), कितना storage, कितनी bandwidth, cache कितना बड़ा, कितने servers — ताकि design के फ़ैसले numbers से साबित हों

---

## 🔵 Simple Definition (English)
**Back-of-the-envelope estimation** is quick, rounded math to size a system: **traffic (QPS), storage, bandwidth, memory/cache and machine counts**, using simple assumptions and powers of ten. Precision doesn't matter. **Order of magnitude** and the **decisions** the numbers drive do ("1k QPS fits one Postgres", "1M QPS needs sharding and caching").
Core formulas:
- **Average QPS** = DAU × actions per user per day ÷ 86,400 (≈ 10⁵ s/day)
- **Peak QPS** ≈ average × 2–5 (or ×10 for event spikes like IPL or sales)
- **Storage** = new items/day × size per item × retention days × replication factor
- **Bandwidth** = QPS × payload size (separately for ingress and egress)
- **Cache size** ≈ hot fraction (often ~20%) × daily read set
- **Servers** ≈ peak QPS ÷ sustainable QPS per server (+ headroom ~30–50%)

## 🔵 सरल परिभाषा (Hindi)
Back-of-the-envelope = system का आकार जानने के लिए जल्दी का मोटा गणित — traffic (QPS), storage, bandwidth, cache और कितनी machines — आसान assumptions और 10 की घातों से; सटीकता नहीं, सही "पैमाना" और उससे होने वाले फ़ैसले मायने रखते हैं ("1k QPS एक Postgres पर", "10 लाख QPS के लिए sharding + cache")।
सूत्र: औसत QPS = DAU × प्रति यूज़र काम ÷ 86,400 (~10⁵); peak ≈ औसत × 2–5 (IPL/sale पर ×10); storage = रोज़ के items × आकार × कितने दिन × replication; bandwidth = QPS × payload; cache ≈ रोज़ पढ़े जाने वाले डेटा का ~20%; servers ≈ peak QPS ÷ एक server की क्षमता (+30–50% बफ़र)।

---

## 🔴 Problem it Solves
Without numbers, design choices are guesses:
- Do we need a cache? Sharding? A queue? CDN? How many Redis nodes? Is a single region enough?
- Candidates either **over-engineer** (Kafka plus 50 shards for 100 QPS) or **under-design** (one MySQL for 2M writes/s).
Interviewers explicitly look for **quantitative reasoning**: can you translate "100M DAU" into concrete capacity and justify the architecture? Estimation also surfaces the **dominant cost or bottleneck** early (video storage, egress bandwidth, LLM tokens).

## 🔴 यह क्यों बना? (Hindi)
बिना numbers के design के फ़ैसले अंदाज़े हैं: cache चाहिए? sharding? queue? CDN? कितने Redis nodes? एक region काफ़ी? उम्मीदवार या तो ज़रूरत से ज़्यादा (100 QPS के लिए Kafka + 50 shards) या कम (20 लाख writes/s के लिए एक MySQL) बनाते हैं।
Interviewer साफ़ तौर पर numbers वाली सोच देखते हैं — "10 करोड़ DAU" को असली capacity में बदलकर design साबित कर सकते हो? अनुमान से सबसे बड़ा ख़र्च/रुकावट (video storage, egress, LLM tokens) जल्दी दिखता है।

---

## 🟢 How it Works — Step by Step

### Handy constants

```
1 day = 86,400 s ≈ 10⁵ s (round!)          1 month ≈ 2.5 × 10⁶ s       1 year ≈ 3 × 10⁷ s
1 million/day ≈ 12/s       100 million/day ≈ 1,200/s       1 billion/day ≈ 12,000/s
Sizes: char (ASCII) 1 B; Devanagari char in UTF-8 ≈ 3 B; int 4 B; long/timestamp 8 B; UUID 16 B
       short text/tweet ~ 300 B–1 KB with metadata; JSON API response 1–10 KB
       thumbnail 20–50 KB; photo (compressed) 200 KB–2 MB; 1 min 1080p stream ≈ 5 Mbps ≈ 40 MB
Powers: KB 10³, MB 10⁶, GB 10⁹, TB 10¹², PB 10¹⁵
Replication factor typically ×3; add ~20–30% for indexes/overhead
```

### The 5-step method

```
1. Users & actions: DAU, actions/user/day, read:write ratio, peak factor (state assumptions!)
2. Traffic: write QPS, read QPS (avg & peak)
3. Storage: per-item size × items/day × retention × replication (+ index overhead)
4. Bandwidth: ingress (uploads) & egress (reads × payload) → CDN needed?
5. Memory/servers: cache hot set; app servers = peak QPS / per-server capacity; DB sizing vs limits
→ Then say what the numbers imply for the design
```

### Worked example 1 — Twitter-like feed

```
DAU 200M; each user posts 2 tweets/day, views feed 20 times/day (20 tweets each)
Writes: 200M × 2 / 10⁵ = 4,000 tweets/s (peak ×3 ≈ 12k/s)
Feed reads: 200M × 20 / 10⁵ = 40k feed requests/s (peak ~120k/s) → read-heavy → cache feeds (fan-out)
Storage (text): 400M tweets/day × 1 KB = 400 GB/day → ×365 ≈ 146 TB/yr → ×3 replication ≈ 440 TB/yr
Media: 10% tweets with 500 KB image → 40M × 0.5 MB = 20 TB/day → object storage + CDN (dominant!)
Implication: precomputed timelines in cache, sharded tweet store, CDN for media
```

### Worked example 2 — WhatsApp-like messaging

```
DAU 500M × 40 messages/day = 20B msgs/day → 200k msgs/s avg, peak (New Year) ×5 ≈ 1M/s
Message ~100 B ciphertext + metadata ~200 B → 20B × 200 B = 4 TB/day transient (deleted after delivery)
Concurrent connections: ~40% online at peak → 200M sockets; ~1M sockets per gateway server →
~200+ gateway servers (with headroom ~300) across regions
Implication: connection gateways, per-device inbox store, store-and-forward, push for offline
```

### Worked example 3 — Swiggy-like orders (India)

```
Orders/day 3M; dinner 2-hour peak handles 35% of orders → 1.05M / 7,200 s ≈ 150 orders/s (rain/IPL ×2 → 300/s)
Order write fan-out: order + payment + notification + rider assignment events ≈ 10 events/order → 3k events/s peak
Location: 300k active riders × 1 update / 5 s = 60k location writes/s → in-memory geo index (Redis/H3), not SQL
Menu reads: 30M menu views/day ÷ 10⁵ ≈ 300/s avg, peak ~3k/s → cache menus (60 s TTL) + CDN images
Implication: SQL fine for orders (300/s), but location tracking needs a specialized hot path
```

### Worked example 4 — URL shortener

```
100M new URLs/month → ~40 writes/s (peak 200/s); reads 100:1 → 4k/s (peak 20k/s)
Storage: 100M × 12 × 5 yrs × 500 B = 3 TB (+ replication 9 TB) → modest
Short code length: base62 → 62⁷ ≈ 3.5 × 10¹² combos ≫ 6B URLs over 5 years → 7 chars enough
Cache: 20% of daily reads' unique URLs (say 20M × 500 B = 10 GB) → fits in a Redis cluster
```

### Worked example 5 — LLM support bot (tokens)

```
165k turns/day × (4,000 input + 250 output tokens) = 660M input + 41M output tokens/day
Peak TPM ≈ 50 turns/s × 4,250 × 60 ≈ 12.7M tokens/min → check provider rate-limit tier
Cost ≈ input_M × price_in + output_M × price_out → compare vs budget; optimize with caching/routing (AI 153)
```

### Server count estimation

```
Rule-of-thumb sustainable throughput per instance (simple JSON API, well-tuned): ~1k–5k req/s (Go/Node),
DB: Postgres single primary ~ thousands–tens of thousands simple QPS; Redis node ~100k ops/s
App servers = peak QPS / per-server QPS × 1.3 headroom → e.g., 120k / 3k × 1.3 ≈ 52 instances
Always say "rough; would load-test to confirm"
```

### Sanity checks & tips

```
- Round aggressively (86,400 → 10⁵; 2.6M → 3M); keep units visible (B, KB, /s)
- Check ratios: reads vs writes, peak vs avg, storage per user per year (e.g., 1 GB/user/yr OK?)
- Identify the DOMINANT term (media storage, egress, sockets, tokens) and design around it
- Don't spend > 5 minutes; write numbers on the board and reuse them in decisions
```

## 🟢 कैसे काम करता है? (Hindi)
1. याद रखो: 1 दिन ≈ 10⁵ सेकंड; 10 लाख/दिन ≈ 12/s; 10 करोड़/दिन ≈ 1,200/s; देवनागरी अक्षर UTF-8 में ~3 bytes; photo 200 KB–2 MB; 1080p stream का 1 मिनट ≈ 40 MB; replication ×3।
2. 5 कदम: यूज़र्स और काम (DAU, प्रति यूज़र काम, read:write, peak — assumptions बोलो) → traffic (औसत और peak QPS) → storage (आकार × रोज़ × दिन × replication) → bandwidth (CDN चाहिए?) → cache और servers → और बताओ इससे design में क्या तय हुआ।
3. Twitter: 4k tweets/s, 40k feed reads/s → read-heavy, feeds cache; media 20 TB/दिन सबसे बड़ा — object storage + CDN; WhatsApp: 20 अरब messages/दिन ≈ 2 लाख/s, peak 10 लाख/s, 20 करोड़ sockets → ~200–300 gateway servers।
4. Swiggy: peak ~150–300 orders/s (SQL काफ़ी), पर riders की location 60k writes/s → Redis/H3; URL shortener: 40 writes/s, 4k reads/s, 3 TB, 7 अक्षर base62 काफ़ी, cache ~10 GB; LLM bot: रोज़ 66 करोड़ input tokens, peak ~1.27 करोड़ tokens/मिनट — provider की सीमा जाँचो।
5. Servers = peak QPS ÷ एक server की क्षमता × 1.3; tips — ज़ोर से round करो, units लिखो, अनुपात जाँचो, सबसे बड़ा हिस्सा पहचानो, 5 मिनट से ज़्यादा नहीं, numbers board पर रखकर फ़ैसलों में इस्तेमाल करो।

---

## 🟡 Real World Example

**Jeff Dean's "Numbers Everyone Should Know"** — Google's famous latency and throughput list (memory vs disk vs network) popularized order-of-magnitude reasoning for system design. It's still the basis for estimation conversations (Playbook 04).

**WhatsApp's 2M connections per server (2012)** — a real data point that makes connection-gateway estimates concrete: hundreds of millions of concurrent users imply hundreds of servers, not millions.

**Cricket streaming in India** — Hotstar/JioCinema record concurrency in the multiple crores of viewers means egress in tens of terabits per second at peak (e.g., 30M viewers × ~1.5 Mbps average ≈ 45 Tbps). That's why multi-CDN and ISP caching are mandatory: estimation reveals the dominant constraint immediately.

## 🟡 Real Example Hindi में
Jeff Dean की "Numbers Everyone Should Know" सूची (memory बनाम disk बनाम network) ने पैमाने वाली सोच लोकप्रिय की; WhatsApp का 2012 का "एक server पर 20 लाख कनेक्शन" बताता है कि करोड़ों online यूज़र्स = सैकड़ों servers, लाखों नहीं।
Hotstar/JioCinema पर करोड़ों एक साथ cricket दर्शक — जैसे 3 करोड़ × ~1.5 Mbps ≈ 45 Tbps egress — इसलिए multi-CDN और ISP caching ज़रूरी; अनुमान तुरंत सबसे बड़ी रुकावट दिखा देता है।

---

## 🟠 My Stack Example

### Tiny estimation helper (use while practising)
```python
DAY = 100_000            # rounded seconds/day
def qps(dau, per_user_per_day, peak=3): avg = dau * per_user_per_day / DAY; return avg, avg * peak
def storage_tb(items_per_day, bytes_per_item, days, replication=3): return items_per_day * bytes_per_item * days * replication / 1e12
def servers(peak_qps, per_server=3000, headroom=1.3): return int(peak_qps / per_server * headroom) + 1

print(qps(200e6, 20))                       # feed reads: (40000.0, 120000.0)
print(storage_tb(400e6, 1_000, 365))        # tweets text ≈ 438 TB/yr with replication
print(servers(120_000))                      # ≈ 53 app instances
```

### How to say it in the interview
```
"Let me do quick math. 200M DAU × 20 feed views ≈ 4 × 10⁹ per day ≈ 40k/s, peak ~120k/s.
 That's read-heavy by ~10×, so I'll precompute timelines and cache them. Media dominates storage
 (~20 TB/day), so object storage + CDN is a must. These are rough; I'd validate with load tests."
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you convert daily active users into QPS?**
A1: Multiply DAU by the number of relevant actions per user per day to get daily requests, then divide by roughly 10⁵ seconds per day for the average QPS. Apply a peak factor (2–5× for daily peaks, higher for events like sales or cricket matches) to get peak QPS. Do this separately for reads and writes, since their ratio drives caching and replication decisions.

**Q2: How do you estimate storage needs?**
A2: Estimate the size of one item including metadata (text, IDs, timestamps), multiply by items created per day and by the retention period in days, then multiply by the replication factor (typically 3) and add overhead for indexes (~20–30%). Estimate large blobs like images and videos separately, since they usually dominate and belong in object storage with CDN delivery. Express results in TB or PB per year.

**Q3: Why does estimation matter if numbers are rough?**
A3: Because design choices depend on order of magnitude, not exact values. A hundred QPS, ten thousand QPS and a million QPS lead to fundamentally different architectures (single database, replicas plus caching, sharding plus queues plus multi-region). Estimation also reveals the dominant bottleneck or cost early (media storage, egress bandwidth, concurrent connections, LLM tokens) and shows the interviewer quantitative reasoning.

**Q4: How do you estimate the number of servers?**
A4: Take peak QPS for a component and divide by a reasonable sustainable throughput per instance (benchmarked or rule-of-thumb, depending on workload complexity), then add headroom (30–50%) for failures and deploys, and consider N+1 or N+2 redundancy across zones. For stateful systems, also check memory or storage per node (cache hot set ÷ memory per node, connections per gateway). State that you'd confirm with load testing.

**Q5: What are common estimation mistakes?**
A5: Spending too long on precise arithmetic, forgetting peak versus average, mixing units (bits vs bytes, MB vs GB), ignoring replication and index overhead, missing the dominant cost (media or egress), not separating reads from writes, and computing numbers but never using them to justify decisions. Round aggressively, label units and connect every number to a design choice.

---

## 🔷 Trade-offs
✅ Quick rounded math: keeps pace, shows reasoning — ❌ can be off by 2–3× (fine) — never by 1000× (sanity-check).
✅ Explicit assumptions: transparent — ❌ wrong assumptions → invite interviewer to correct them.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| DAU / MAU | Daily / monthly active users | रोज़ / महीने के सक्रिय यूज़र |
| QPS | Queries (requests) per second | प्रति सेकंड requests |
| Peak factor | Peak ÷ average traffic | सबसे ज़्यादा भीड़ का गुणक |
| Read:write ratio | Reads per write | पढ़ना बनाम लिखना |
| Retention | How long data is kept | डेटा कितने दिन रखें |
| Replication factor | Number of copies | कितनी कॉपियाँ |
| Egress | Outbound data transfer | बाहर जाने वाला डेटा |
| Hot set | Frequently accessed data | बार-बार पढ़ा जाने वाला डेटा |
| Headroom | Spare capacity buffer | अतिरिक्त क्षमता |
| Order of magnitude | Power-of-ten scale | 10 की घात वाला पैमाना |

---

## ⚡ 3-Line Summary
**English:**
1. QPS = DAU × actions ÷ 10⁵ (× peak factor); storage = items/day × size × retention × replication; bandwidth = QPS × payload.
2. Size caches (hot set) and servers (peak ÷ per-server × headroom); find the dominant term (media, egress, sockets, tokens).
3. Round aggressively, state assumptions, keep units, spend ≤ 5 minutes, and use every number to justify a design decision.

**Hindi:**
1. QPS = DAU × काम ÷ 10⁵ (× peak); storage = रोज़ × आकार × दिन × replication; bandwidth = QPS × payload।
2. Cache और servers का आकार; सबसे बड़ा हिस्सा पहचानो (media, egress, sockets, tokens)।
3. Round करो, assumptions बोलो, units रखो, 5 मिनट तक, और हर number से फ़ैसला साबित करो।

---

## ➡️ Next Topic Suggestion
**04. Numbers Every Engineer Should Know** — Estimation needs reference numbers. Next: latency of memory, disk, network and regions, typical throughput of common systems, availability "nines", and data sizes.
