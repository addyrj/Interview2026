---

# 9. Fault Tolerance Concepts
# AWS: Multi-AZ, SQS retries/DLQ, S3 11 9s durability design, Auto Scaling replace
# Azure: Zone-redundant services, Service Bus DLQ, ZRS/GRS storage, VMSS repair
# हिंदी में: फॉल्ट टॉलरेंस = गड़बड़ी होने पर भी बिना रुके काम करते रहना

---

## 🔵 Simple Definition (2 lines)
Fault tolerance means the system continues operating correctly, with no visible interruption, even when parts fail.
हिंदी: कोई पुर्ज़ा फेल हो जाए तब भी यूज़र को पता न चले और काम सही चलता रहे।

---

## 🔴 Why it Exists (2 lines)
HA tolerates brief failover; some systems (payments, queues) cannot lose requests or data.
Fault tolerance adds redundancy, retries and isolation so failures are absorbed.

---

## 🟢 How it Works
```
HA            : may blip during failover, recovers fast
Fault tolerant: no interruption (higher cost)

Patterns:
 redundancy (N+1)  | retries + exponential backoff + jitter
 circuit breaker   | queue between services (buffer)
 dead-letter queue | bulkheads / timeouts / graceful degradation
 replicated storage (multi-AZ / zone-redundant)
```

---

## 💻 Code / Config Example
```javascript
// Node.js: retry with exponential backoff + jitter (works with any SDK call)
async function withRetry(fn, { retries = 4, base = 200 } = {}) {
  for (let attempt = 0; ; attempt++) {
    try {
      return await fn();
    } catch (err) {
      if (attempt >= retries) throw err;            // give up, let DLQ/alert handle
      const delay = base * 2 ** attempt * (0.5 + Math.random() / 2);
      await new Promise((r) => setTimeout(r, delay));
    }
  }
}
// usage: await withRetry(() => fetch("https://api.example.com/x"));
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Message buffer + DLQ | SQS + DLQ | Service Bus / Storage Queue (DLQ on Service Bus) |
| Replicated storage | S3 (multi-AZ by default for most classes) | Blob ZRS/GRS |
| Self-healing compute | ASG health replacement | VMSS automatic instance repair |
| Chaos testing | AWS Fault Injection Service | Azure Chaos Studio |

---

## ⚠️ Common Mistakes
❌ Mistake: Retrying immediately in a tight loop (retry storm).
✅ Correct: Exponential backoff with jitter and a max attempt cap.

❌ Mistake: Retrying non-idempotent operations blindly (double charge).
✅ Correct: Use idempotency keys.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] HA vs fault tolerance?
A1: HA minimizes downtime; fault tolerance aims for zero interruption, usually costlier.

Q2: [Medium] What is a dead-letter queue?
A2: A queue where messages that failed processing repeatedly are parked for inspection.

Q3: [Hard] How avoid cascading failure between microservices?
A3: Timeouts, circuit breakers, bulkheads, queues for async work, rate limits and graceful degradation (serve cached/partial data).

---

## ✅ Quick Checklist
□ Timeouts set on every network call
□ Operations are idempotent
□ DLQ and alarms on queues

---

## ⚡ 1-Line Summary
Fault tolerance absorbs failures without users noticing | फॉल्ट टॉलरेंस = फेल्योर सोख लेना, यूज़र को पता न चले।

## ➡️ Next: 10. Disaster Recovery Basics

---
