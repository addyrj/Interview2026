# 53. CloudFront — CDN
# AWS: Amazon CloudFront
# Azure: Azure Front Door (Standard/Premium) / Azure CDN
# हिंदी में: दुनिया भर के एज सर्वरों से कंटेंट तेज़ी से पहुँचाने वाला नेटवर्क

---

## 🔵 Simple Definition (2 lines)
A CDN caches content at edge locations near users and fetches from your origin only on a miss.
यूज़र के पास वाले सर्वर से कंटेंट मिलता है, इसलिए साइट तेज़ और ओरिजिन पर लोड कम।

---

## 🔴 Why it Exists (2 lines)
Distance adds latency and a single origin gets overloaded or DDoSed.
CDN cuts latency, bandwidth cost and adds TLS, WAF and DDoS protection (Shield Standard is automatic).

---

## 🟢 How it Works
```
User -> nearest Edge (cache HIT -> return)
              | MISS
              v
        Regional edge cache -> Origin (S3 / ALB / custom)
Distribution = origins + behaviors (path pattern -> origin, cache policy)
Invalidate: /path/* (first 1,000 paths/month free - check current docs)
```

---

## 💻 Code / Config Example
```bash
# Minimal custom-origin distribution (AWS CLI v2) - web app on ALB
aws cloudfront create-distribution --distribution-config '{
  "CallerReference": "myapp-2026-01",
  "Comment": "myapp",
  "Enabled": true,
  "Origins": {"Quantity": 1, "Items": [{
    "Id": "alb", "DomainName": "myalb-123.ap-south-1.elb.amazonaws.com",
    "CustomOriginConfig": {"HTTPPort": 80, "HTTPSPort": 443, "OriginProtocolPolicy": "https-only"}}]},
  "DefaultCacheBehavior": {
    "TargetOriginId": "alb",
    "ViewerProtocolPolicy": "redirect-to-https",
    "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
  }
}'
# 4135ea2d-... = managed CachingDisabled policy (safe default for APIs)
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | CloudFront | Azure Front Door (also Azure CDN, being retired for some SKUs) |
| Config unit | Distribution + behaviors | Profile + endpoint + routes |
| WAF | AWS WAF | Front Door WAF |
| Pricing | per GB egress + requests (approximate — check current docs) | per base fee + GB + requests (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Caching authenticated/API responses.
✅ Correct: Use CachingDisabled or cache only static paths; forward needed headers deliberately.

❌ Mistake: Deploying new JS without invalidation or versioned filenames.
✅ Correct: Hash filenames (app.abc123.js) and long TTL; invalidate index.html.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is an edge location?
A1: A CloudFront PoP that caches and serves content close to viewers.

Q2: [Medium] How do TTLs work?
A2: Cache policy min/default/max TTL combined with origin Cache-Control headers.

Q3: [Hard] Why can cache hit ratio be low?
A3: Cache key includes too many headers/cookies/query strings; reduce the cache key in the cache policy.

---

## ✅ Quick Checklist
□ HTTPS redirect, ACM cert (us-east-1 for custom domain)
□ Right cache policy per behavior
□ WAF attached if public
□ Versioned asset names

---

## ⚡ 1-Line Summary
CloudFront caches content at the edge for speed and protection. | CloudFront कंटेंट को यूज़र के पास कैश करके तेज़ी और सुरक्षा देता है।

## ➡️ Next: CloudFront + S3
