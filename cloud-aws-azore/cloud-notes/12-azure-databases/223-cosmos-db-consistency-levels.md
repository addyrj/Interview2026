# 223. Cosmos DB Consistency Levels
# AWS: DynamoDB (eventual / strongly consistent reads; Global Tables)
# Azure: Cosmos DB (5 consistency levels)
# हिंदी में: डेटा कितना ताज़ा दिखे बनाम कितनी तेज़ी, इसके बीच का संतुलन

---

## 🔵 Simple Definition (2 lines)
Consistency level decides what a reader sees after a write across replicas: from Strong (always latest) to Eventual (fastest, may lag).
हिंदी: यह तय करता है कि पढ़ने वाले को कितना ताज़ा डेटा मिलेगा, ज्यादा सख्त मतलब ज्यादा latency।

---

## 🔴 Why it Exists (2 lines)
Distributed replicas cannot be both instantly consistent and fastest (CAP/PACELC trade-off).
Cosmos lets you pick the point on that spectrum per account and relax it per request.

---

## 🟢 How it Works
```
Strong  >  Bounded Staleness  >  Session  >  Consistent Prefix  >  Eventual
(latest)   (lag <= K ops / T)    (default)    (ordered, may lag)    (fastest)

Session: a client reads its own writes (via session token) - best for web apps.
Strong: not available with multi-region writes.
Per-request you can only relax, never strengthen, beyond the account default.
```

---

## 💻 Code / Config Example
```bash
# Account default
az cosmosdb update -n myapp-cosmos -g rg-app --default-consistency-level BoundedStaleness \
  --max-interval 300 --max-staleness-prefix 100000
```
```javascript
// Node.js: relax per client (can only weaken the account default)
const { CosmosClient } = require("@azure/cosmos");
const client = new CosmosClient({
  endpoint: process.env.COSMOS_ENDPOINT,
  key: process.env.COSMOS_KEY,
  consistencyLevel: "Eventual",   // Strong | BoundedStaleness | Session | ConsistentPrefix | Eventual
});
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Levels | 2 (eventual, strong per read) | 5 levels |
| Default | Eventual reads | Session |
| Multi-region strong | Global Tables: eventual across regions by default (check docs for newer options) | Strong only single-write-region |
| Pricing | Strong reads cost ~2x RCU (approximate) | Strong/Bounded read RU cost is higher (approximate — check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using Strong "just to be safe" for a global app.
✅ Correct: Session fits most apps; use Strong only for money/inventory needs.

❌ Mistake: Load balancer spreading one user across clients without passing the session token.
✅ Correct: Forward the session token (or stick users) so read-your-writes holds.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Name the five levels.
A1: Strong, Bounded Staleness, Session, Consistent Prefix, Eventual.

Q2: [Medium] Why is Session the default?
A2: It guarantees read-your-writes and monotonic reads for a client at low latency and cost.

Q3: [Hard] Cart service on multi-region writes: which level?
A3: Session (strong is unavailable with multi-write). Handle conflicts with last-writer-wins or a custom conflict policy and design idempotent updates.

---

## ✅ Quick Checklist
□ Default level reviewed against the business need
□ Session token forwarded across services
□ Conflict policy set for multi-write

---

## ⚡ 1-Line Summary
Five levels trade freshness for latency; Session is the sane default | पाँच levels में ताज़गी और स्पीड का सौदा होता है; Session सही डिफ़ॉल्ट है

## ➡️ Next: Cosmos DB Partitioning

---
