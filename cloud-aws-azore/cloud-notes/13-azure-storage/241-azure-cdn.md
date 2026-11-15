---

# 241. Azure CDN
# AWS: CloudFront
# Azure: Azure CDN (classic) / Azure Front Door Standard/Premium (recommended)
# हिंदी में: Azure CDN = यूज़र के पास के सर्वर से स्टैटिक कंटेंट तेज़ पहुँचाना

---

## 🔵 Simple Definition (2 lines)
A CDN caches your content (images, JS, video) on edge servers close to users, so requests do not travel to your origin every time.
Azure CDN हर यूज़र को नज़दीकी एज सर्वर से कंटेंट देता है, इसलिए साइट तेज़ चलती है और origin पर लोड कम पड़ता है।

---

## 🔴 Why it Exists (2 lines)
A single-region origin is slow for far-away users and expensive under heavy traffic.
CDN cuts latency, absorbs traffic spikes and offloads bandwidth from your VPS/Blob.

---

## 🟢 How it Works
```
User (Delhi) -> Edge POP (nearby)
                 |-- cache HIT  -> response (fast)
                 |-- cache MISS -> Origin (Blob static site / App Service / VPS)
                                    -> edge stores copy for TTL (Cache-Control)
Profile (Azure CDN) -> Endpoint (xyz.azureedge.net) -> Origin + caching rules + custom domain/HTTPS
```
Note: Microsoft has announced retirement of Azure CDN from Edgio and is steering new work to Azure Front Door (check current docs for dates).

---

## 💻 Code / Config Example
```bash
# Azure CLI: CDN profile + endpoint in front of a Blob static website
az group create -n rg-demo -l centralindia
az cdn profile create -g rg-demo -n demo-cdn --sku Standard_Microsoft
az cdn endpoint create -g rg-demo --profile-name demo-cdn -n demo-assets-ep \
  --origin mystorageacct.z29.web.core.windows.net \
  --origin-host-header mystorageacct.z29.web.core.windows.net \
  --no-http   # HTTPS only

# Purge after deploying a new frontend build (GitHub Actions step)
az cdn endpoint purge -g rg-demo --profile-name demo-cdn -n demo-assets-ep --content-paths '/*'
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | CloudFront | Azure CDN / Front Door |
| Origin | S3, ALB, custom | Blob, App Service, custom |
| Invalidate | `create-invalidation` | `az cdn endpoint purge` |
| HTTPS cert | ACM (free) | Managed cert (free) |
| Pricing | Per GB out + requests (approximate - check current docs) | Per GB out by zone (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Deploying new `app.js` with the same name and wondering why users see the old one.
✅ Correct: Use hashed filenames (`app.3f2a.js`) plus long TTL, and purge only `index.html`.

❌ Mistake: Caching authenticated API responses at the edge.
✅ Correct: Cache only static paths; send `Cache-Control: no-store` for private data.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What does a CDN do?
A1: Serves cached content from edge locations near the user, reducing latency and origin load.

Q2: [Medium] How do you update content that is already cached?
A2: Wait for TTL, purge the path, or (better) version file names so the URL changes.

Q3: [Hard] Azure CDN vs Front Door - which for a new project?
A3: Front Door combines CDN, global load balancing, WAF and routing; Microsoft recommends it for new builds. Classic Azure CDN SKUs are being retired.

---

## ✅ Quick Checklist
□ Origin is HTTPS and host header set correctly
□ Cache-Control headers defined per content type
□ Purge step added in CI/CD after deploy

---

## ⚡ 1-Line Summary
A CDN serves cached content from nearby edges for speed and lower origin load | CDN कंटेंट को यूज़र के पास कैश करके साइट तेज़ बनाता है।

## ➡️ Next: 242. Storage Replication Options

---
