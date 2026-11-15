# 54. CloudFront + S3
# AWS: CloudFront with S3 origin (static site / assets)
# Azure: Front Door / CDN with Blob Storage static website origin
# हिंदी में: React/Next static साइट को S3 पर रखकर CloudFront से परोसना

---

## 🔵 Simple Definition (2 lines)
Host built static files (React/Vite) in a private S3 bucket and serve them globally through CloudFront.
S3 में फ़ाइलें, CloudFront से तेज़ डिलीवरी, और बकेट प्राइवेट रहता है।

---

## 🔴 Why it Exists (2 lines)
S3 alone has no custom-domain HTTPS caching at the edge; direct public buckets are insecure and slower.
CloudFront gives HTTPS, caching and keeps the bucket private.

---

## 🟢 How it Works
```
GitHub Actions: npm run build -> aws s3 sync dist s3://site-bucket
                              -> aws cloudfront create-invalidation /index.html
Viewer -> CloudFront -> (OAC signed request) -> private S3 bucket
SPA routing: custom error 403/404 -> /index.html (200)
```

---

## 💻 Code / Config Example
```yaml
# .github/workflows/deploy-web.yml (OIDC role, no stored keys)
name: deploy-web
on: { push: { branches: [main] } }
permissions: { id-token: write, contents: read }
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci && npm run build
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::111122223333:role/gha-deploy-web
          aws-region: ap-south-1
      - run: |
          aws s3 sync dist s3://my-site-prod --delete \
            --cache-control "public,max-age=31536000,immutable" --exclude index.html
          aws s3 cp dist/index.html s3://my-site-prod/index.html --cache-control "no-cache"
          aws cloudfront create-invalidation --distribution-id E123EXAMPLE --paths "/index.html"
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Origin | Private S3 + OAC | Blob static website or private blob + Front Door |
| SPA fallback | Custom error responses | Front Door rules / static website error doc |
| Deploy | `aws s3 sync` | `az storage blob sync` / Static Web Apps |
| Pricing | S3 + CloudFront egress (approximate — check current docs) | Blob + Front Door (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using the S3 website endpoint with a public bucket.
✅ Correct: Use the REST endpoint with OAC and a private bucket.

❌ Mistake: SPA deep links return 403 from S3.
✅ Correct: Map 403/404 to `/index.html` with 200.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Why put CloudFront in front of S3?
A1: Edge caching, HTTPS on custom domain, lower latency and a private bucket.

Q2: [Medium] How do you ship a new frontend release safely?
A2: Hashed asset filenames with long cache; `index.html` no-cache plus invalidation.

Q3: [Hard] Why 403 instead of 404 for missing keys?
A3: Without s3:ListBucket permission S3 returns 403 for missing objects; handle both in error responses.

---

## ✅ Quick Checklist
□ Bucket private, OAC policy added
□ Default root object index.html
□ SPA error mapping
□ OIDC role for CI

---

## ⚡ 1-Line Summary
Private S3 plus CloudFront is the standard static site setup. | प्राइवेट S3 और CloudFront स्टैटिक साइट का स्टैंडर्ड सेटअप है।

## ➡️ Next: CloudFront + ALB
