# 01. How to Answer a Backend System Design Round (step-by-step framework)
# हिंदी में: Backend System Design Round कैसे दें — 45–60 मिनट में किसी भी system (URL shortener, WhatsApp, Swiggy, payments) को ढाँचे में डिज़ाइन करने का कदम-दर-कदम तरीका: ज़रूरतें → अनुमान → API → high-level design → data model → गहराई → trade-offs

---

## 🔵 Simple Definition (English)
A **backend system design interview** asks you to design a large-scale system end to end: requirements, capacity, APIs, components, data storage, scaling, reliability and trade-offs. It's evaluated on **how you think**, not on one "correct" answer.
A reliable framework (the order you should follow):
1. **Clarify requirements**: functional, non-functional, scale, constraints, out of scope.
2. **Back-of-the-envelope estimation**: QPS, storage, bandwidth, memory (Playbook 03).
3. **API design**: core endpoints or events with request/response shapes.
4. **High-level design**: draw the main components and data flow.
5. **Data model and storage choices**: entities, schemas, SQL vs NoSQL, partition keys, indexes.
6. **Deep dives**: 2–3 hardest parts (scaling hot paths, consistency, caching, queues, failure handling).
7. **Bottlenecks, failure modes, trade-offs and evolution**: what breaks at 10× and how you'd monitor and evolve it.
Throughout: **think aloud, state assumptions, give numbers, compare options and justify choices**.

## 🔵 सरल परिभाषा (Hindi)
Backend system design इंटरव्यू में आपसे बड़े पैमाने का पूरा system डिज़ाइन करवाया जाता है — ज़रूरतें, capacity, APIs, components, डेटा, scaling, भरोसा और trade-offs; जाँच इस बात की होती है कि आप कैसे सोचते हो, किसी एक "सही" जवाब की नहीं।
क्रम: (1) ज़रूरतें साफ़ करो (functional, non-functional, पैमाना, सीमाएँ, क्या scope में नहीं); (2) अनुमान (QPS, storage, bandwidth); (3) API; (4) high-level design (मुख्य हिस्से और डेटा का बहाव); (5) data model और storage का चुनाव; (6) 2–3 सबसे कठिन हिस्सों की गहराई; (7) bottlenecks, failures, trade-offs, आगे कैसे बढ़ेगा। पूरे समय: ज़ोर से सोचो, assumptions बताओ, numbers दो, विकल्पों की तुलना करके कारण बताओ।

---

## 🔴 Problem it Solves
Most candidates know the concepts (caching, sharding, Kafka) but fail the round because they:
- **Jump into a solution** without clarifying, so they design the wrong system ("Was it real-time? Was it global?").
- **Draw boxes without numbers**, so they can't justify sharding, caching or queue choices.
- **Go deep too early** (an hour on database choice) and never finish the end-to-end design.
- **Name technologies instead of reasoning** ("use Kafka" without why or the trade-off).
- **Go silent**, so the interviewer can't see the thinking.
- **Ignore failures** (what if Redis dies, or the payment webhook is delayed?).
A framework gives **structure under pressure**, makes sure you cover what interviewers score, and leaves time for the deep dives that differentiate senior candidates.

## 🔴 यह क्यों बना? (Hindi)
ज़्यादातर लोग concepts (cache, sharding, Kafka) जानते हैं पर round में fail होते हैं क्योंकि: बिना पूछे सीधे solution (ग़लत system बना दिया — real-time था? global?); बिना numbers के boxes (sharding/cache क्यों, समझा नहीं पाते); बहुत जल्दी गहराई में (एक DB चुनने में आधा घंटा, पूरा design अधूरा); तर्क की जगह सिर्फ़ technologies के नाम ("Kafka लगाओ" — क्यों?); चुप रहना; failures भूलना (Redis मरे तो? webhook देर से आए तो?)।
Framework दबाव में ढाँचा देता है, जो interviewer नंबर देते हैं वो सब cover होता है, और गहराई (जिससे senior अलग दिखते हैं) के लिए समय बचता है।

---

## 🟢 How it Works — Step by Step

### Time plan (45 min; scale proportionally for 60)

```
0–5   Clarify requirements & scope (write them on the board)
5–9   Estimation (QPS, storage, bandwidth, read/write ratio)
9–13  API design (3–6 core endpoints / events)
13–25 High-level design (diagram + walk through main flows)
25–30 Data model & storage choices (schemas, keys, indexes, SQL/NoSQL)
30–42 Deep dives (2–3 topics: the hardest/most interesting parts)
42–45 Bottlenecks, failures, monitoring, trade-offs, future evolution; ask your questions
```

### Step 1 — Requirements (ask, then confirm)

```
Functional: "Users can X, Y, Z" (prioritize top 3; park the rest as 'out of scope')
Non-functional: scale (DAU, QPS), latency targets (p99), availability (99.9 vs 99.99), consistency needs
  (strong for payments, eventual OK for likes), durability, geography (India-only? global?),
  security/compliance (PII, RBI data localization), cost sensitivity
Constraints: read-heavy or write-heavy? peak patterns (IPL, sale days, 9 PM dinner peak)? mobile clients?
Say: "I'll assume … — let me know if you'd like a different assumption."
```

### Step 2 — Estimation (quick, rounded, purposeful)

```
DAU → requests/user/day → QPS avg (÷ ~10^5 s/day) → peak (×2–5)
Storage = items/day × size × retention (+ replication ×3)
Bandwidth = QPS × payload size; Cache size = hot set (e.g., 20% of daily reads)
Use numbers to DECIDE: "1.2M writes/s → single Postgres won't do → partition by user_id"
```

### Step 3 — API

```
POST /v1/urls {long_url, custom_alias?} → 201 {short_url}
GET  /{code} → 301/302 Location
Mention: auth, idempotency keys for writes, pagination (cursor), rate limits, versioning
For async/event systems: name the events/topics and payloads
```

### Step 4 — High-level design

```
Client → CDN → LB/API Gateway → stateless services → cache → DB(s)
                                       └→ queue (Kafka/SQS) → workers → other stores / notifications
Walk through 1–2 key flows end to end (write path & read path), narrating each hop
Keep it simple first; evolve when numbers demand it
```

### Step 5 — Data model & storage

```
Entities & relationships; access patterns FIRST, then choose store:
  relational (transactions, joins) vs key-value (simple lookups at scale) vs wide-column (time-series,
  write-heavy) vs document vs search index vs object storage vs graph
Primary keys, partition/shard keys (avoid hotspots), indexes, retention/TTL
```

### Step 6 — Deep dives (pick what matters for THIS system)

```
Scaling the hot path (caching strategy, read replicas, sharding, CDN)
Consistency & concurrency (transactions, idempotency, locks, sagas, exactly-once effects)
Async processing (queues, retries, DLQ, ordering, backpressure)
Real-time (WebSockets, fan-out, presence)
Search/ranking, geo (geohash/H3), media pipelines
Ask: "Which area would you like me to go deeper on?" — let the interviewer steer
```

### Step 7 — Wrap-up

```
Single points of failure & mitigations; what happens on component failure
Monitoring: SLIs/SLOs, key metrics, alerts; security; cost
Trade-offs you made & alternatives; how design evolves at 10× scale
```

### What interviewers score (signals)

```
Problem navigation: clarifies, scopes, prioritizes
Solution design: coherent end-to-end architecture that meets requirements
Technical depth: correct details in deep dives (not buzzwords)
Trade-offs: compares options with reasons tied to requirements & numbers
Communication: structured, thinks aloud, uses diagrams, listens to hints
Level expectations: SDE-2 = solid design + some depth; Senior = drives, deep dives, failure handling,
  trade-offs; Staff = ambiguity, evolution, org/cost/operability considerations
```

## 🟢 कैसे काम करता है? (Hindi)
1. पहले 5 मिनट: ज़रूरतें पूछो और board पर लिखो — मुख्य 3 features, पैमाना (DAU, QPS), latency, availability, consistency (payment में strong, likes में eventual), भारत-only या global, compliance; बाक़ी को "scope से बाहर" कहो; "मैं यह मान रहा हूँ — अलग चाहिए तो बताइए"।
2. 4 मिनट अनुमान: DAU → QPS (÷ 10^5) → peak (×2–5), storage, bandwidth, cache आकार — और numbers से फ़ैसला ("12 लाख writes/s → एक Postgres नहीं चलेगा → user_id से partition")।
3. API (3–6 endpoints: auth, idempotency, cursor pagination, rate limits) → high-level diagram (client → CDN → LB → stateless services → cache → DB, queue → workers) और लिखने/पढ़ने का पूरा रास्ता बोलकर समझाओ — पहले सरल, numbers माँगें तब जटिल।
4. Data model: पहले access patterns, फिर store का चुनाव (relational, key-value, wide-column, document, search, object storage), keys, shard key (hotspot नहीं), indexes, TTL; फिर 2–3 गहराइयाँ (hot path scaling, consistency/idempotency, queues, real-time, geo) — "किस हिस्से पर गहराई चाहिए?" पूछो।
5. अंत: single point of failure और बचाव, component fail हो तो क्या, monitoring (SLO, alerts), security, ख़र्च, आपके trade-offs और 10× पर बदलाव; interviewer देखते हैं — scope करना, पूरा design, गहराई, trade-offs, बातचीत; senior से उम्मीद — ख़ुद आगे बढ़ाना, failures, trade-offs।

---

## 🟡 Real World Example

**Big-tech loops (Google, Meta, Amazon, Microsoft, Uber)** — system design rounds typically use open-ended prompts like "Design YouTube", "Design a rate limiter" or "Design a news feed", scored on rubrics for problem exploration, design, depth, trade-offs and communication, with expectations rising by level.

**Indian product companies (Flipkart, Swiggy, Zomato, PhonePe, Razorpay, CRED, Meesho)** — frequently ask India-flavoured designs: "Design Swiggy's order tracking", "Design a UPI payment flow", "Design a flash-sale system for Big Billion Days", "Design a notification system for 100M users". Interviewers value realistic constraints (peak events, low-end devices, UPI pending states).

**What separates offers** — debriefs commonly cite "drove the conversation", "used numbers to justify sharding", "handled failure scenarios (idempotency, retries)" and "explained trade-offs clearly" as strong signals, and "jumped to buzzwords" and "ran out of time" as common negatives.

## 🟡 Real Example Hindi में
Google, Meta, Amazon, Uber में "YouTube डिज़ाइन करो", "rate limiter", "news feed" जैसे खुले सवाल — rubric पर नंबर: समस्या समझना, design, गहराई, trade-offs, बातचीत; level बढ़े तो उम्मीद भी।
Flipkart, Swiggy, Zomato, PhonePe, Razorpay, CRED भारतीय सवाल पूछते हैं — "Swiggy order tracking", "UPI payment flow", "Big Billion Days flash sale", "10 करोड़ users के लिए notifications"; असली हालात (peak events, सस्ते फ़ोन, UPI pending) की समझ को महत्व; अच्छे संकेत — बातचीत ख़ुद चलाना, numbers से sharding साबित करना, failures (idempotency, retries) संभालना; बुरे — buzzwords और समय ख़त्म।

---

## 🟠 My Stack Example

### A 45-minute script you can adapt ("Design a URL shortener")
```
[Requirements] "Core: shorten URL, redirect, optional custom alias, expiry. Out of scope: analytics UI.
 Scale: 100M new URLs/month, read:write ≈ 100:1, p99 redirect < 50 ms, 99.99% availability for redirects."
[Estimation] "Writes ≈ 100M/30/86,400 ≈ 40/s (peak ~200/s); reads ≈ 4,000/s (peak ~20k/s).
 Storage: 100M × 12 months × 5 years × ~500 B ≈ 3 TB. Hot set cacheable in Redis (~tens of GB)."
[API] "POST /v1/urls → {short}; GET /{code} → 302 (or 301 if no analytics)."
[HLD] "Clients → CDN/edge → LB → stateless API (Node/FastAPI) → Redis cache → Postgres/DynamoDB.
 Write path: generate code (base62 of ID from a distributed ID generator / pre-allocated ranges) → store."
[Data] "urls(code PK, long_url, owner_id, created_at, expires_at). Key-value access → DynamoDB or
 Postgres partitioned by code hash; index owner_id for 'my links'."
[Deep dive 1] "Code generation without collisions: range allocation per server (Redis INCR blocks)…"
[Deep dive 2] "Redirect latency: cache-aside, CDN caching of 301s, negative caching for unknown codes…"
[Failures] "Redis down → fall back to DB with rate limiting; DB replica lag on fresh links → read-your-write
 via primary for 1 min; abuse → rate limits + malware URL scanning."
[Trade-offs] "302 keeps analytics but more origin traffic; 301 cheaper but caches forever…"
```

### Phrases that show senior thinking
```
"Given the 100:1 read ratio, I'll optimize the read path first."
"This needs strong consistency because money moves; likes can be eventually consistent."
"The bottleneck at 10× is the single writer; I'd partition by user_id because all queries are per-user."
"Option A is simpler; option B scales further but adds operational cost. With our numbers, A is enough for now."
"If this component fails, here's what users see, and here's how we recover."
```

### Whiteboard tips
```
- Write requirements & numbers in a corner; keep them visible
- Draw left-to-right: clients → edge → services → data; label arrows with protocols & payloads
- Use numbered flows (1, 2, 3…) when narrating paths
- Keep a 'parking lot' list of topics to revisit
```

---

## ⚫ Interview Questions + Answers

**Q1: What should you do in the first five minutes?**
A1: Clarify and scope. Ask about core functional requirements and prioritize the top few. Pin down non-functional needs (scale in DAU and QPS, latency targets, availability, consistency requirements, geography, compliance), identify read/write patterns and peaks, and explicitly list what's out of scope. State assumptions out loud and write the requirements down. This prevents designing the wrong system and gives you criteria for every later decision.

**Q2: How much estimation is enough?**
A2: Enough to drive decisions, which usually takes 3–5 minutes of rounded math: average and peak QPS for reads and writes, storage growth over the retention period (including replication), bandwidth, and cache size for the hot set. Then use the numbers explicitly ("20k reads/s means we need caching and replicas; 3 TB fits in a sharded cluster"). Avoid spending ten minutes on precise arithmetic.

**Q3: How do you choose what to deep dive into?**
A3: Pick the parts that are hardest or most critical for this specific system and its requirements: the hot read path for a feed, consistency and idempotency for payments, fan-out and ordering for chat, geo indexing and matching for ride-hailing, ingestion and transcoding for video. Offer two or three options to the interviewer and follow their interest, since they often want to probe a particular area.

**Q4: How do you discuss trade-offs effectively?**
A4: Frame each decision as options with pros and cons tied to the requirements and numbers ("SQL gives transactions we need for orders; NoSQL scales writes but we'd handle consistency in application code"), state which you choose and why, mention when you'd revisit the choice (at 10× scale, or if multi-region becomes a requirement), and acknowledge operational costs (complexity, ops burden, money). Avoid absolute claims.

**Q5: What if you get stuck or the interviewer pushes back?**
A5: Treat it as collaboration. Restate the problem, think aloud about the constraint they're hinting at, propose a simpler version first, then improve it. If they challenge a choice, ask what concern they have (latency? consistency?) and either defend it with reasoning or adapt. Interviewers reward adaptability and clear reasoning over stubbornness. Use the parking lot to come back to open questions.

---

## 🔷 Trade-offs
✅ Following a framework: complete coverage, calm structure — ❌ don't be robotic; adapt to interviewer cues.
✅ Going deep: shows expertise — ❌ only after the end-to-end design exists.
✅ Simple first, evolve later: clarity — ❌ must still show how it scales when asked.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Functional requirement | What the system does | system क्या करे |
| Non-functional requirement | Quality targets (scale, latency) | गुणवत्ता के लक्ष्य |
| Scope | What's in/out | क्या शामिल, क्या नहीं |
| Estimation | Back-of-envelope numbers | मोटा अनुमान |
| High-level design | Main components & flows | मुख्य ढाँचा |
| Deep dive | Detailed exploration of a part | किसी हिस्से की गहराई |
| Bottleneck | Limiting component | रुकावट वाला हिस्सा |
| Trade-off | Choice with pros & cons | फ़ायदे-नुक़सान वाला चुनाव |
| SPOF | Single point of failure | अकेला कमज़ोर बिंदु |
| Think aloud | Narrate reasoning | सोच बोलकर बताना |

---

## ⚡ 3-Line Summary
**English:**
1. Order: requirements → estimation → API → high-level design → data model → 2–3 deep dives → failures, trade-offs, evolution.
2. Use numbers to justify decisions, keep the first design simple, and go deep where this system is hardest.
3. Think aloud, state assumptions, compare options, handle failures, manage time, and let the interviewer steer deep dives.

**Hindi:**
1. क्रम: ज़रूरतें → अनुमान → API → high-level → data model → 2–3 गहराइयाँ → failures, trade-offs, आगे का विकास।
2. Numbers से फ़ैसले, पहला design सरल, और गहराई वहाँ जहाँ यह system सबसे कठिन है।
3. ज़ोर से सोचो, assumptions बताओ, विकल्प तुलना करो, failures संभालो, समय संभालो।

---

## ➡️ Next Topic Suggestion
**02. How to Answer a Frontend / Mobile System Design Round** — Client-side rounds use a different structure and different signals. Next: the RADIO and mobile frameworks applied under interview time pressure.
