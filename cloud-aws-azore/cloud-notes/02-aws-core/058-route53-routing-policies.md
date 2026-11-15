# 58. Route 53 Routing Policies
# AWS: Route 53 routing policies
# Azure: Traffic Manager routing methods / Front Door routing
# हिंदी में: DNS जवाब कैसे चुना जाए — वज़न, लेटेंसी, लोकेशन, फेलओवर

---

## 🔵 Simple Definition (2 lines)
A routing policy decides which record value Route 53 returns for a name: simple, weighted, latency, failover, geolocation, geoproximity, multivalue.
एक ही नाम के कई रिकॉर्ड में से कौन-सा जवाब देना है, यह पॉलिसी तय करती है।

---

## 🔴 Why it Exists (2 lines)
Real apps run in multiple servers/Regions and need canary, DR failover and nearest-user routing.
DNS-level policy does this without changing the app.

---

## 🟢 How it Works
```
Simple      : one record (or several values, random)
Weighted    : 90% v1 / 10% v2  (canary, blue-green)
Latency     : Region with lowest latency to user
Failover    : PRIMARY healthy ? primary : SECONDARY (needs health check)
Geolocation : by user country/continent
Geoproximity: by location + bias (uses Traffic Flow)
Multivalue  : up to 8 healthy records
IP-based    : by client CIDR
```

---

## 💻 Code / Config Example
```json
{
  "Changes": [
    { "Action": "UPSERT", "ResourceRecordSet": {
      "Name": "api.example.com", "Type": "A", "SetIdentifier": "blue",
      "Weight": 90, "TTL": 60, "ResourceRecords": [{ "Value": "203.0.113.10" }] } },
    { "Action": "UPSERT", "ResourceRecordSet": {
      "Name": "api.example.com", "Type": "A", "SetIdentifier": "green",
      "Weight": 10, "TTL": 60, "ResourceRecords": [{ "Value": "203.0.113.20" }] } }
  ]
}
```
```bash
aws route53 change-resource-record-sets --hosted-zone-id Z0123456789EXAMPLE --change-batch file://weighted.json
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Weighted | Weighted | Traffic Manager Weighted |
| Nearest | Latency | Performance |
| DR | Failover | Priority |
| Geo | Geolocation / Geoproximity | Geographic |
| Pricing | policy records and queries billed (approximate — check current docs) | per DNS query + endpoints (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Weighted/latency records without unique SetIdentifier.
✅ Correct: Every record in the set needs a distinct SetIdentifier.

❌ Mistake: Failover without a health check on primary.
✅ Correct: Attach a health check to the primary record.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Which policy for canary release?
A1: Weighted.

Q2: [Medium] Latency vs geolocation?
A2: Latency uses measured network latency; geolocation uses user's location regardless of speed (good for compliance/content).

Q3: [Hard] Why is DNS failover not instant?
A3: Health check detection time plus TTL and resolver caching; use low TTL and consider Global Accelerator for faster failover.

---

## ✅ Quick Checklist
□ Right policy for need
□ SetIdentifier unique
□ Health checks on failover records
□ Low TTL for dynamic routing

---

## ⚡ 1-Line Summary
Routing policies decide which endpoint DNS answers with. | रूटिंग पॉलिसी तय करती है DNS किस endpoint का जवाब दे।

## ➡️ Next: Route 53 Health Checks
