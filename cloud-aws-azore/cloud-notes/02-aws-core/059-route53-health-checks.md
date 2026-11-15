# 59. Route 53 Health Checks
# AWS: Route 53 Health Checks
# Azure: Traffic Manager endpoint monitoring / Front Door health probes
# हिंदी में: endpoint ठीक है या नहीं, यह जाँचकर खराब वाले को DNS से हटाना

---

## 🔵 Simple Definition (2 lines)
Route 53 checkers around the world probe an endpoint (HTTP/HTTPS/TCP), a calculated group, or a CloudWatch alarm, and mark it healthy or unhealthy.
अनहेल्दी endpoint को DNS जवाब से हटा दिया जाता है, जिससे फेलओवर होता है।

---

## 🔴 Why it Exists (2 lines)
DNS would keep sending users to a dead server.
Health checks let failover, weighted and latency records skip failed endpoints.

---

## 🟢 How it Works
```
Checkers (multiple Regions) --GET /health every 30s (or 10s fast)--> endpoint
Healthy if >18% of checkers say OK (default) and failure threshold not exceeded
Types: endpoint | calculated (AND/OR of others) | CloudWatch alarm (private resources)
Record linked to check -> unhealthy => record not returned
```

---

## 💻 Code / Config Example
```bash
aws route53 create-health-check --caller-reference "api-primary-001" \
  --health-check-config '{
    "Type": "HTTPS",
    "FullyQualifiedDomainName": "api-primary.example.com",
    "Port": 443,
    "ResourcePath": "/health",
    "RequestInterval": 30,
    "FailureThreshold": 3
  }'
# Then reference the returned Id as "HealthCheckId" in a failover record:
#   "Failover": "PRIMARY", "SetIdentifier": "primary", "HealthCheckId": "<id>"
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Route 53 health check | Traffic Manager monitoring / Front Door probe |
| Protocols | HTTP, HTTPS, TCP | HTTP, HTTPS, TCP |
| Private targets | CloudWatch alarm based | N/A for Traffic Manager (public endpoints only) |
| Pricing | per check/month, extras for HTTPS/fast interval (approximate — check current docs) | per endpoint / probe cost (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Security group blocks Route 53 checker IPs.
✅ Correct: Allow Route 53 health checker IP ranges (published in ip-ranges.json) on the endpoint.

❌ Mistake: `/health` only checks that the process is up.
✅ Correct: Check critical dependencies carefully (DB) but avoid cascading false failures.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What can a health check monitor?
A1: An endpoint, other health checks (calculated), or a CloudWatch alarm.

Q2: [Medium] How to monitor a private VPC resource?
A2: Route 53 checkers are public; create a CloudWatch alarm on the resource metric and base the health check on it.

Q3: [Hard] Design multi-Region failover for an API.
A3: Failover records (primary/secondary alias or IPs) each with health checks, low TTL, alarm via SNS; test failover regularly.

---

## ✅ Quick Checklist
□ Dedicated /health endpoint
□ Checker IPs allowed
□ Linked to failover records
□ SNS alarm on unhealthy

---

## ⚡ 1-Line Summary
Health checks let DNS stop sending users to dead endpoints. | हेल्थ चेक DNS को खराब endpoint पर ट्रैफिक भेजने से रोकता है।

## ➡️ Next: RDS — Complete Guide
