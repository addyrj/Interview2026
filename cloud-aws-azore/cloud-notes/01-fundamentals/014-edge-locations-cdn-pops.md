---

# 14. Edge Locations / CDN POPs
# AWS: CloudFront edge locations, Route 53, Global Accelerator
# Azure: Azure Front Door / Azure CDN points of presence (POPs)
# हिंदी में: एज लोकेशन = यूज़र के पास का छोटा सर्वर जो कंटेंट कैश करता है

---

## 🔵 Simple Definition (2 lines)
Edge locations (POPs) are small sites close to users that cache content and terminate connections, separate from full regions.
हिंदी: यूज़र के नज़दीक के कैश सर्वर, जिससे इमेज, JS और वीडियो तेज़ लोड होते हैं।

---

## 🔴 Why it Exists (2 lines)
Distance adds latency, and serving every request from the origin is slow and costly.
A CDN serves cached copies nearby and offloads the origin.

---

## 🟢 How it Works
```
User (Delhi) --> nearest edge POP --cache HIT--> response (fast)
                        |
                    cache MISS
                        v
                 Origin (S3 / ALB / Blob / App)  -> cached for TTL
Controls: Cache-Control headers, TTL, invalidation, HTTPS, WAF
```

---

## 💻 Code / Config Example
```javascript
// Express: let CDN cache static assets for a year (fingerprinted names), HTML not cached
const express = require("express");
const app = express();
app.use("/static", express.static("public", {
  maxAge: "365d", immutable: true            // sets Cache-Control: public, max-age=..., immutable
}));
app.get("/", (req, res) => {
  res.set("Cache-Control", "no-cache");       // always revalidate with origin
  res.send("<h1>hello</h1>");
});
app.listen(3000);
```
```bash
# AWS: invalidate changed paths on CloudFront (distribution id is a placeholder)
aws cloudfront create-invalidation --distribution-id E123EXAMPLE --paths "/index.html"
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| CDN | CloudFront | Azure Front Door (Standard/Premium), Azure CDN |
| Global anycast TCP | Global Accelerator | Front Door |
| Edge compute | Lambda@Edge, CloudFront Functions | Front Door rules engine |
| Pricing | Per GB out + requests (check docs) | Similar (check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Caching API responses with user data publicly.
✅ Correct: Use Cache-Control: private/no-store for personalized responses.

❌ Mistake: Relying on invalidations for every deploy.
✅ Correct: Use versioned filenames (app.3f2a.js).

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is an edge location?
A1: A CDN site near users that caches content.

Q2: [Medium] Edge location vs region?
A2: Regions run full services; edges mainly cache/accelerate and run limited compute.

Q3: [Hard] Cache hit ratio is low. Debug?
A3: Check cache key (query strings/cookies/headers forwarded), TTLs and Cache-Control from origin, Vary headers, and consider origin shield/tiered caching.

---

## ✅ Quick Checklist
□ Static assets fingerprinted
□ Cache-Control set at origin
□ HTTPS and WAF on the CDN

---

## ⚡ 1-Line Summary
Edge caches bring content close to users | एज कैश कंटेंट को यूज़र के पास ले आते हैं।

## ➡️ Next: 15. AWS vs Azure vs GCP Overview

---
