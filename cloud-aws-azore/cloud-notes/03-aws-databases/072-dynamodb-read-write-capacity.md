# 72. DYNAMODB READ/WRITE CAPACITY
# AWS: DynamoDB RCU / WCU
# Azure: Cosmos DB Request Units (RU/s)
# हिंदी में: DynamoDB रीड/राइट कैपेसिटी

---

## 🔵 Simple Definition (2 lines)
Capacity is measured in RCUs and WCUs: 1 RCU = one strongly consistent read per second of up to 4 KB; 1 WCU = one write per second of up to 1 KB.
हिंदी: 1 RCU = प्रति सेकंड 4 KB तक की एक स्ट्रॉन्ग रीड; 1 WCU = प्रति सेकंड 1 KB तक की एक राइट।

---

## 🔴 Why it Exists (2 lines)
DynamoDB must reserve throughput per partition to give predictable latency.
Knowing the maths lets you size cost and avoid throttling.

---

## 🟢 How it Works
```
Read  : 4 KB per RCU strongly consistent
        eventually consistent = 2 reads per RCU (half cost)
        transactional read    = 2 RCU per 4 KB
Write : 1 KB per WCU ; transactional write = 2 WCU per 1 KB
Example: 100 reads/s of 6 KB items, eventually consistent
  items = ceil(6/4)=2 RCU each -> 100*2 = 200 -> /2 = 100 RCU
Example: 50 writes/s of 2.5 KB -> ceil(2.5)=3 WCU each -> 150 WCU
Over limit -> ProvisionedThroughputExceededException (retry with backoff)
```

---

## 💻 Code / Config Example
```bash
# Set provisioned capacity (AWS CLI v2)
aws dynamodb update-table \
  --table-name Orders \
  --billing-mode PROVISIONED \
  --provisioned-throughput ReadCapacityUnits=100,WriteCapacityUnits=150

# Strongly consistent read of one item
aws dynamodb get-item --table-name Orders --consistent-read \
  --key '{"userId":{"S":"u1"},"orderId":{"S":"o-100"}}'
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Unit | RCU / WCU | RU/s (one unit for reads and writes) |
| 1 unit means | 4 KB read / 1 KB write per second | 1 RU about a 1 KB point read |
| Autoscale | Application Auto Scaling | Autoscale RU/s |
| Pricing | Per unit-hour (approximate - check current docs) | Per RU/s-hour (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Forgetting rounding up (6 KB read = 2 RCU, not 1.5).
✅ Correct: Always round item size up to the next 4 KB / 1 KB.

❌ Mistake: Using Scan and burning RCUs.
✅ Correct: Query by key; Scan consumes RCUs for all data read, not just filtered items.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is 1 RCU?
A1: One strongly consistent read per second up to 4 KB (two eventually consistent).

Q2: [Medium] Compute WCU for 200 writes/s of 3 KB.
A2: 3 WCU per write, so 600 WCU.

Q3: [Hard] You are throttled but table usage is low. Why?
A3: Hot partition; capacity is divided across partitions and a single key exceeds its share. Fix the key design (sharding), not just raise capacity.

---

## ✅ Quick Checklist
□ Item size measured
□ Consistency model chosen
□ Retries with exponential backoff (SDK default)

---

## ⚡ 1-Line Summary
RCU = 4 KB reads, WCU = 1 KB writes, per second; always round up. | RCU = 4 KB रीड, WCU = 1 KB राइट प्रति सेकंड; हमेशा ऊपर की ओर राउंड करें।

## ➡️ Next: DynamoDB On-demand vs Provisioned

---
