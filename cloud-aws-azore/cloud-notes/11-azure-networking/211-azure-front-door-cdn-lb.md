---

# 211. Azure Front Door (CDN + LB)
# AWS: Amazon CloudFront + Global Accelerator (+ Route 53 routing)
# Azure: Azure Front Door
# हिंदी में: Global CDN, load balancer और WAF एक साथ

---

## 🔵 Simple Definition (2 lines)
Front Door is a global Layer-7 entry point combining CDN caching, SSL offload, routing, failover and WAF.
हिंदी: Front Door global entry point है जो CDN, load balancing, failover और WAF एक साथ देता है।

---

## 🔴 Why it Exists (2 lines)
Users worldwide hit the nearest Microsoft edge, which is faster than going to one region directly.
It also fails over between regional backends automatically.

---

## 🟢 How it Works
```
User -> nearest Microsoft edge POP (anycast, TLS terminates, WAF, cache)
     -> Route (/api/*) -> Origin group: [India origin, EU origin]
        health probes + latency/priority/weight -> best healthy origin
Tiers: Standard (CDN-focused), Premium (WAF managed rules, Private Link origins)
```

---

## 💻 Code / Config Example
```bash
az afd profile create -g rg-demo --profile-name fd-prod --sku Standard_AzureFrontDoor
az afd endpoint create -g rg-demo --profile-name fd-prod --endpoint-name web --enabled-state Enabled

az afd origin-group create -g rg-demo --profile-name fd-prod --origin-group-name og-api \
  --probe-request-type GET --probe-protocol Https --probe-path /health \
  --probe-interval-in-seconds 30 \
  --sample-size 4 --successful-samples-required 3 --additional-latency-in-milliseconds 50

az afd origin create -g rg-demo --profile-name fd-prod --origin-group-name og-api \
  --origin-name india --host-name api-in.example.com --origin-host-header api-in.example.com \
  --priority 1 --weight 1000 --enabled-state Enabled --https-port 443

az afd route create -g rg-demo --profile-name fd-prod --endpoint-name web --route-name r1 \
  --origin-group og-api --supported-protocols Https --patterns-to-match "/api/*" \
  --forwarding-protocol HttpsOnly --link-to-default-domain Enabled
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| CDN + routing | CloudFront | Front Door |
| Non-HTTP anycast | Global Accelerator | Front Door is HTTP(S) only; use Cross-region LB/Traffic Manager |
| WAF | AWS WAF | Front Door WAF policy |
| Pricing | Requests + data out (approximate — check current docs) | Base fee + requests + data out (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Leaving origins reachable directly, bypassing WAF.
✅ Correct: Restrict origin to the `AzureFrontDoor.Backend` service tag and validate the `X-Azure-FDID` header.

❌ Mistake: Caching authenticated API responses.
✅ Correct: Disable caching on dynamic routes or honor Cache-Control.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is Front Door? A1: Global L7 CDN + load balancer + WAF.
Q2: [Medium] Front Door vs Traffic Manager? A2: Front Door proxies traffic at the edge (HTTP); Traffic Manager is DNS-based routing for any protocol.
Q3: [Hard] How do you make origins private? A3: Premium tier with Private Link origins, or lock origin to the Front Door service tag plus FDID header check.

---

## ✅ Quick Checklist
□ WAF policy attached
□ Origin locked to Front Door
□ Health probe path correct
□ Cache rules reviewed

---

## ⚡ 1-Line Summary
Front Door is Azure's CloudFront plus global load balancing | Front Door Azure का CloudFront और global load balancer एक साथ है।

## ➡️ Next: 212. Azure DNS

---
