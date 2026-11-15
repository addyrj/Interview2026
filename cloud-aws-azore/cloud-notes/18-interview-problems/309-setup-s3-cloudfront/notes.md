# 309. Setup S3 + CloudFront
# AWS: S3 (private) + CloudFront with Origin Access Control
# Azure: Blob Storage static website + Azure Front Door / Azure CDN (or Static Web Apps)
# हिंदी में: S3 में साइट रखें (प्राइवेट), CloudFront से दुनिया भर में तेज़ और HTTPS में परोसें

---

## 🔵 Simple Definition
A private S3 bucket holds static files; CloudFront caches them at edge locations and is the only reader (OAC).
हिंदी: फाइलें प्राइवेट S3 में, CloudFront एज पर कैश करके यूज़र तक पहुंचाता है।

## 🔴 Why it Exists
Cheap, fast, HTTPS static hosting without servers; the bucket is never public.

## 🟢 How it Works
```
Browser -> CloudFront edge (cache hit -> return)
              miss -> SigV4-signed GET (OAC) -> S3 bucket (policy: only this distribution)
Deploy: build -> s3 sync (immutable assets) -> index.html no-cache -> invalidate /index.html
SPA: 403/404 -> /index.html with 200
```

## 💻 Code / Config Example
`main.tf` (bucket, public-access block, SSE, OAC, distribution, bucket policy; provider ~> 5.x, not applied here) and `deploy.yml` (GitHub Actions with OIDC; copy to `.github/workflows/`). Custom domain needs an ACM certificate in us-east-1 plus `aliases` and a Route 53 alias record.

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Storage | S3 | Blob Storage ($web) |
| CDN | CloudFront | Front Door / Azure CDN |
| Origin lock-down | OAC + bucket policy | Private link / SAS / Front Door origin access |
| Alternative | Amplify Hosting | Static Web Apps |
| Pricing | storage + requests + egress (approximate - check current docs) | similar |

## 💰 Cost / HA / Security
- Cost: CloudFront egress is usually cheaper than S3 direct; high cache hit ratio and compression lower it; pick price class.
- HA: S3 is multi-AZ; CloudFront is global.
- Security: Block Public Access, OAC (not legacy OAI), HTTPS redirect, add security headers policy, WAF if needed.

## ⚠️ Common Mistakes
❌ Making the bucket public for hosting.
✅ Keep private, use OAC.

❌ Caching `index.html` for long, users see stale app.
✅ `no-cache` on HTML, hashed filenames with long TTL.

## ⚫ Interview Q&A
Q1 [Easy]: Why use CloudFront in front of S3?
A1: Caching, HTTPS with custom domain, lower latency, and the bucket can stay private.

Q2 [Medium]: OAC vs OAI?
A2: OAC is the newer mechanism using SigV4, supports SSE-KMS and all regions; OAI is legacy.

Q3 [Hard]: How do you ship a release with zero stale-asset errors?
A3: Content-hashed asset names uploaded before index.html, keep old assets for a while, invalidate only index.html.

## ✅ Quick Checklist
□ Public access blocked
□ OAC + scoped bucket policy
□ Cache headers set per file type

## ⚡ 1-Line Summary
Private S3 + CloudFront OAC = secure global static hosting. | प्राइवेट S3 + CloudFront = सुरक्षित और तेज़ स्टैटिक होस्टिंग।

## ➡️ Next: 310. Setup RDS + Elasticache
