---

# 12. SLA in Cloud
# AWS: Per-service SLAs (EC2, S3, RDS...) with service credits
# Azure: Per-service SLAs; Azure SLA for composite calculations
# हिंदी में: SLA = प्रोवाइडर का अपटाइम वादा, चूकने पर क्रेडिट

---

## 🔵 Simple Definition (2 lines)
An SLA (Service Level Agreement) is the provider's written uptime commitment for a service; if missed, you get service credits, not damages.
हिंदी: SLA यानी सर्विस कितने प्रतिशत चालू रहेगी इसका लिखित वादा; चूक पर सिर्फ़ क्रेडिट मिलता है।

---

## 🔴 Why it Exists (2 lines)
Customers need measurable reliability to plan architecture and contracts.
SLA terms also show what you must do (e.g., multi-AZ) to qualify.

---

## 🟢 How it Works
```
Downtime allowed per year (approx):
 99%     ~ 3.65 days
 99.9%   ~ 8.76 hours
 99.95%  ~ 4.38 hours
 99.99%  ~ 52.6 minutes

Composite SLA (serial dependencies) = multiply
 App 99.95% x DB 99.95% = 99.90%
Parallel redundancy raises it: 1-(1-0.999)^2 = 99.9999%
Terms: SLA (promise) / SLO (your target) / SLI (the measurement)
```

---

## 💻 Code / Config Example
```javascript
// Node.js: compute composite SLA and yearly downtime
const serial = (...s) => s.reduce((a, b) => a * b, 1);
const parallel = (s, n) => 1 - Math.pow(1 - s, n);
const minutesPerYear = 365 * 24 * 60;

const app = 0.9995, db = 0.9995;
const composite = serial(app, db);
console.log("composite %", (composite * 100).toFixed(3));
console.log("downtime min/yr", ((1 - composite) * minutesPerYear).toFixed(0));
console.log("2 redundant 99.9% nodes %", (parallel(0.999, 2) * 100).toFixed(4));
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| SLA scope | Per service / per region | Per service; higher with zones for VMs |
| Remedy | Service credits via support claim | Service credits via claim |
| SLA figures | Check each service SLA page | Check each service SLA page |
| Requirement example | Multi-AZ deployment for top EC2 SLA | 2+ VMs across zones for higher VM SLA |

---

## ⚠️ Common Mistakes
❌ Mistake: Assuming 99.99% on one service gives 99.99% for your app.
✅ Correct: Multiply the chain and design redundancy.

❌ Mistake: Not claiming credits within the deadline.
✅ Correct: Track incidents and file within the window stated in the SLA.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is an SLA?
A1: A contractual uptime commitment with remedies when missed.

Q2: [Medium] SLA vs SLO vs SLI?
A2: SLA is the external promise, SLO is the internal goal, SLI is the measured metric.

Q3: [Hard] Your app uses 5 services at 99.95% each in series. Overall?
A3: About 0.9995^5 = 99.75%, about 22 hours of downtime/year; add redundancy or reduce dependencies.

---

## ✅ Quick Checklist
□ Read SLA conditions for services I use
□ Calculated composite SLA
□ Defined own SLOs and alerts

---

## ⚡ 1-Line Summary
SLA is a promise; real reliability comes from your architecture | SLA वादा है, असली भरोसा आपके आर्किटेक्चर से आता है।

## ➡️ Next: 13. Cloud Regions + Availability Zones

---
