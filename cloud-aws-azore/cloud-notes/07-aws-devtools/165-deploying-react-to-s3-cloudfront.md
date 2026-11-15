# 165. Deploying React to S3+CloudFront
# AWS: S3 (static hosting origin) + CloudFront CDN
# Azure: Blob Storage static website + Front Door / Azure CDN, or Static Web Apps
# हिंदी में: React app को S3 और CloudFront पर deploy करना

---

## 🔵 Simple Definition
Build React to static files, upload to a private S3 bucket and serve globally through CloudFront with HTTPS.
हिंदी: React build को S3 में डालो और CloudFront से तेज़ और HTTPS के साथ दुनिया भर में दिखाओ।

---

## 🔴 Why it Exists
A static SPA needs no server; S3 + CDN is cheap, fast and scales automatically.
CloudFront caches at edge and hides the bucket (Origin Access Control).

---

## 🟢 How it Works
```
git push -> npm run build (dist/)
 -> aws s3 sync dist s3://bucket (assets: long cache, index.html: no-cache)
 -> cloudfront create-invalidation /index.html
User -> CloudFront edge -> (miss) -> S3 via OAC
SPA routing: 403/404 -> /index.html (200)
```

---

## 💻 Code / Config Example
```yaml
# .github/workflows/deploy-react.yml
name: deploy-react
on:
  push:
    branches: [main]
permissions:
  id-token: write
  contents: read
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-react-deploy
          aws-region: ap-south-1
      - name: Upload hashed assets (long cache)
        run: |
          aws s3 sync dist s3://my-react-bucket --delete \
            --exclude index.html \
            --cache-control "public,max-age=31536000,immutable"
      - name: Upload index.html (never cached)
        run: |
          aws s3 cp dist/index.html s3://my-react-bucket/index.html \
            --cache-control "no-cache"
      - name: Invalidate CDN
        run: aws cloudfront create-invalidation --distribution-id E123ABCDEF --paths "/index.html"
```
Role needs `s3:PutObject`, `s3:DeleteObject`, `s3:ListBucket` on the bucket and `cloudfront:CreateInvalidation` on the distribution.

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Storage | S3 | Blob static website |
| CDN | CloudFront | Front Door / Azure CDN |
| Easiest option | Amplify Hosting | Static Web Apps |
| Pricing | S3 storage + CloudFront transfer (approximate — check current docs) | Similar storage + CDN egress model |

---

## ⚠️ Common Mistakes
❌ Mistake: Public S3 bucket website endpoint.
✅ Correct: Private bucket + CloudFront Origin Access Control.

❌ Mistake: Users see old app after deploy.
✅ Correct: Hashed asset filenames, `no-cache` on index.html, invalidate it.

---

## ⚫ Interview Q&A
Q1: [Easy] Why CloudFront in front of S3?
A1: HTTPS with custom domain, caching, lower latency, bucket stays private.

Q2: [Medium] How does client-side routing work?
A2: Custom error responses map 403/404 to `/index.html` with status 200.

Q3: [Hard] Invalidate or version files?
A3: Version (hash in filename) for assets, invalidate only index.html; invalidations beyond the free monthly allowance cost money.

---

## ✅ Quick Checklist
□ Bucket private with OAC
□ Cache-Control set per file type
□ SPA error mapping and ACM cert (us-east-1)

---

## ⚡ 1-Line Summary
Build, sync to private S3, serve via CloudFront, invalidate index.html | build को S3 में sync करो, CloudFront से serve करो और index.html invalidate करो।

## ➡️ Next: 166. Bedrock — Managed LLMs
