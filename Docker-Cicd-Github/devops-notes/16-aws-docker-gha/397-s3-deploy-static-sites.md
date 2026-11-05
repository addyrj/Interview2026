# 397. S3 Deploy (Static Sites)
# हिंदी में: S3 पर Static Site Deploy

---

## 🔵 Simple Definition (English)
A static site (React/Vite build, docs, landing page) is just files: HTML, JS, CSS, images. **Amazon S3** stores those files cheaply and durably, and **CloudFront** serves them worldwide over HTTPS. Deploying means building in CI and running `aws s3 sync` to upload the build output to the bucket.

## 🔵 सरल परिभाषा (Hindi)
Static site (React/Vite build, docs, landing page) बस files होती हैं: HTML, JS, CSS, images। **Amazon S3** इन files को सस्ते और टिकाऊ तरीके से रखता है और **CloudFront** इन्हें दुनिया भर में HTTPS पर परोसता है। Deploy का मतलब है CI में build करना और `aws s3 sync` से build output को bucket में upload करना।

---

## 🔴 Problem it Solves
Serving a React build from a VPS with Nginx means: patching the server, scaling for traffic spikes, TLS renewal, one region only, and you pay for an always-on machine for files that never change.

S3 + CloudFront: no server, effectively unlimited scale, global edge caching, about cents per month for small sites, and 99.99% availability design.

## 🔴 यह क्यों बना? (Hindi)
React build को VPS पर Nginx से परोसने का मतलब: server patch करना, traffic spike के लिए scale करना, TLS renewal, सिर्फ एक region, और ऐसी files के लिए हमेशा चालू machine का खर्च जो बदलती ही नहीं।

S3 + CloudFront: कोई server नहीं, लगभग असीमित scale, global edge caching, छोटी sites के लिए महीने के कुछ पैसे, और बहुत ऊँची availability।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create private S3 bucket (Block Public Access ON)
Step 2 → Create CloudFront distribution with Origin Access Control (OAC) to that bucket
Step 3 → Bucket policy allows only that CloudFront distribution to read
Step 4 → CI: npm ci -> npm test -> npm run build (dist/ or build/)
Step 5 → Upload hashed assets (app.3f9a.js) with long cache: max-age=31536000, immutable
Step 6 → Upload index.html with no-cache so users get new asset names immediately
Step 7 → aws s3 sync --delete removes old files; invalidate CloudFront for index.html (topic 398)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Private S3 bucket बनाएँ (Block Public Access ON)
Step 2 → उस bucket के लिए Origin Access Control (OAC) वाला CloudFront distribution बनाएँ
Step 3 → Bucket policy सिर्फ उसी CloudFront distribution को read की अनुमति दे
Step 4 → CI: npm ci -> npm test -> npm run build (dist/ या build/)
Step 5 → Hash वाले assets (app.3f9a.js) लंबे cache के साथ upload: max-age=31536000, immutable
Step 6 → index.html को no-cache के साथ upload करें ताकि नए asset नाम तुरंत मिलें
Step 7 → aws s3 sync --delete पुरानी files हटाता है; index.html के लिए CloudFront invalidate करें (topic 398)
```

---

## 🟡 Real World Example
A D2C brand hosts its Vite React storefront on S3 + CloudFront. During a flash sale, traffic grows 40x within minutes; since it is static files at the edge, nothing needs scaling. API calls go to the ECS backend on `api.brand.com`. Each merge to `main` ships the frontend in about 90 seconds, with no server to SSH into.

## 🟡 Real Example Hindi mein
एक D2C brand अपना Vite React storefront S3 + CloudFront पर रखता है। Flash sale में कुछ मिनटों में traffic 40 गुना बढ़ता है; चूँकि यह edge पर static files हैं, कुछ scale नहीं करना पड़ता। API calls `api.brand.com` पर ECS backend जाती हैं। `main` पर हर merge के साथ frontend लगभग 90 सेकंड में ship हो जाता है, SSH करने को कोई server नहीं।

---

## 💻 Code / Config Example — Basic

```yaml
name: s3-static-basic                            # workflow name
on:
  push:
    branches: [main]                             # deploy on main
permissions:
  id-token: write                                # OIDC to AWS
  contents: read                                 # checkout
jobs:
  deploy:
    runs-on: ubuntu-latest                       # runner
    steps:
      - uses: actions/checkout@v4                # get code
      - uses: actions/setup-node@v4              # install Node
        with:
          node-version: 20                       # LTS example
          cache: npm                             # cache npm
      - run: npm ci                              # exact dependency install
      - run: npm run build                       # produces dist/ (Vite) ; CRA uses build/
        env:
          VITE_API_URL: https://api.example.com  # public build-time config only
      - uses: aws-actions/configure-aws-credentials@v4   # OIDC login
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ap-south-1
      - run: aws s3 sync dist/ s3://my-site-prod --delete   # upload new, delete removed files
```

## 💻 Code / Config Example — Advanced

Two-pass upload with correct cache headers, SPA-safe, plus the IAM policy and bucket policy.

```yaml
name: s3-static-prod                             # workflow name
on:
  push:
    branches: [main]                             # deploy trigger
permissions:
  id-token: write                                # OIDC
  contents: read                                 # checkout
concurrency:
  group: frontend-prod                           # one deploy at a time
  cancel-in-progress: false                      # let a running deploy finish
env:
  BUCKET: my-site-prod                           # S3 bucket name
  DIST_DIR: dist                                 # build output folder
jobs:
  deploy:
    runs-on: ubuntu-latest                       # runner
    environment: production                      # protection rules
    steps:
      - uses: actions/checkout@v4                # code
      - uses: actions/setup-node@v4              # Node
        with:
          node-version: 20
          cache: npm
      - run: npm ci                              # install
      - run: npm test -- --run                   # unit tests (vitest style flag)
      - run: npm run build                       # build with hashed filenames
        env:
          VITE_API_URL: https://api.example.com  # public config only
      - uses: aws-actions/configure-aws-credentials@v4   # OIDC login
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ap-south-1
      - name: Upload hashed assets (long cache)  # everything except index.html
        run: |
          aws s3 sync "$DIST_DIR" "s3://$BUCKET" \
            --exclude "index.html" \
            --cache-control "public,max-age=31536000,immutable" \
            --delete                             # remove files that no longer exist locally
      - name: Upload index.html (no cache)       # entry file must always be fresh
        run: |
          aws s3 cp "$DIST_DIR/index.html" "s3://$BUCKET/index.html" \
            --cache-control "no-cache,no-store,must-revalidate" \
            --content-type "text/html; charset=utf-8"
      - name: Verify                             # simple post-deploy check
        run: curl --fail --silent --show-error https://www.example.com/ | grep -qi "<div id=\"root\">"
```

Bucket policy (private bucket, readable only by one CloudFront distribution through OAC):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontServicePrincipalReadOnly",
      "Effect": "Allow",
      "Principal": { "Service": "cloudfront.amazonaws.com" },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-site-prod/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::111122223333:distribution/E123EXAMPLE"
        }
      }
    }
  ]
}
```

IAM policy for the deploy role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:DeleteObject", "s3:GetObject"],
      "Resource": "arn:aws:s3:::my-site-prod/*"
    },
    {
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::my-site-prod"
    }
  ]
}
```

SPA routing: for React Router, configure CloudFront custom error responses so 403/404 return `/index.html` with status 200 (or use a CloudFront Function).

---

## 🟠 My Stack Integration
- **React**: this is the primary use. API URL via `VITE_API_URL` at build time; secrets never in the bundle.
- **Node.js / FastAPI**: stay on ECS/EC2 behind an ALB at `api.example.com`; configure CORS to allow only `https://www.example.com`.
- **Nginx**: no longer needed for the frontend. If you still want Nginx for the API only, it sits in front of Node/FastAPI.
- **VPS migration**: keep the VPS API, move the frontend to S3 first (zero-risk step), update DNS for `www` only.
- **Next.js**: static export (`output: 'export'`) works on S3; SSR needs Lambda/ECS/Amplify instead.
- **Rollback**: enable bucket versioning, or keep each build in `s3://bucket-artifacts/<sha>/` and re-sync the old one.

```bash
# rollback example: re-publish a previous build kept as an artifact
aws s3 sync s3://my-site-artifacts/3f9a1c2/ s3://my-site-prod --delete \
  --cache-control "public,max-age=31536000,immutable" --exclude "index.html"   # assets
aws s3 cp s3://my-site-artifacts/3f9a1c2/index.html s3://my-site-prod/index.html \
  --cache-control "no-cache"                     # entry file
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Making the bucket public ("static website hosting" with `Principal: *`).
✅ Correct: Private bucket + CloudFront OAC; S3 website endpoints do not support HTTPS by themselves.

❌ Mistake 2: Same cache header for `index.html` and hashed assets.
✅ Correct: Immutable one-year cache for hashed files; no-cache for `index.html`.

❌ Mistake 3: `--delete` uploaded in the middle of deploy, so users briefly request deleted old chunks and get 404.
✅ Correct: Upload new files first, delete old ones later (or keep the previous build for a few minutes/hours), because users with old `index.html` still request old chunks.

❌ Mistake 4: Forgetting `s3:ListBucket` permission on the bucket ARN (not `/*`).
✅ Correct: Separate statement for the bucket resource itself.

❌ Mistake 5: Putting API keys in `VITE_*` variables.
✅ Correct: They are public in the bundle. Keep secrets in the backend.

---

## 🧠 Tricky Interview Question
After a deploy, some users see a blank page with "ChunkLoadError: Loading chunk 482 failed". What happened and how do you prevent it?

Answer: Those users loaded the old `index.html` (cached or open in a tab) which references old hashed chunks; your `sync --delete` removed them, so the browser gets 404 (or the SPA fallback returns HTML for a JS URL). Prevent by keeping previous assets available for a while (do not delete immediately; clean up older than N days via lifecycle rules), no-cache on `index.html`, and a client-side handler that reloads the page on chunk load errors.

---

## ⚫ Interview Questions + Answers

Q1: Why not serve directly from S3?
A1: S3 website endpoints are HTTP only, public, single-region, and slow for global users. CloudFront adds HTTPS, caching at the edge, compression, WAF and keeps the bucket private.

Q2: OAC vs OAI?
A2: Both let CloudFront access a private bucket. OAC is the newer recommended one (supports SSE-KMS, all regions, short-term credentials); OAI is legacy.

Q3: What does `aws s3 sync` compare?
A3: By default size and last-modified time, not content. Use `--exact-timestamps` or `--size-only` carefully; for builds, hashed names make this reliable.

Q4: How do you do preview environments?
A4: One bucket prefix or separate bucket per PR (`s3://previews/pr-142/`), CloudFront function to route, delete on PR close.

Q5: How do you keep deploys fast with large sites?
A5: Use `sync` (only changed files), parallel transfers (CLI default), gzip/brotli at CloudFront, and keep build output small.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- SPA/static site with an API elsewhere
- You want low cost, global speed and minimal ops
- Marketing and docs sites

❌ Avoid when:
- Server-side rendering at request time is required (use ECS/Lambda/Amplify)
- You need complex server rewrites not possible with CloudFront Functions

---

## 📊 Visual Diagram
```
 Developer --push--> GitHub Actions
                        | npm ci, test, build -> dist/
                        | OIDC role
                        v
                 +-------------+   OAC (private)   +----------------+
                 |  S3 bucket  | <---------------- |  CloudFront    | <-- Users (HTTPS, edge cache)
                 | (private)   |                   |  + custom cert |
                 +-------------+                   +--------+-------+
                                                            | /api/* (optional behaviour)
                                                            v
                                                    ALB -> ECS (Node/FastAPI)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| S3 bucket | Object storage container | object storage का container |
| OAC | Lets CloudFront read a private bucket | CloudFront को private bucket पढ़ने देता है |
| Cache-Control | Header controlling caching | caching नियंत्रित करने वाला header |
| Immutable asset | Hashed file that never changes | hash वाली file जो कभी नहीं बदलती |
| Sync | Upload only differences | सिर्फ अंतर upload करना |
| SPA | Single page application | Single page application |

---

## ⚡ 3-Line Summary
English: Build the site in CI, upload to a private S3 bucket, and serve it through CloudFront.
English: Use long cache for hashed assets and no-cache for index.html.
English: Do not delete old chunks instantly, and keep the bucket private.
Hindi: CI में site build करें, private S3 bucket में upload करें, और CloudFront से परोसें।
Hindi: Hash वाले assets को लंबा cache दें और index.html को no-cache।
Hindi: पुराने chunks तुरंत delete न करें, और bucket को private रखें।

---

## ➡️ Next Topic
**398. CloudFront Invalidation**: edge caches may still hold the old `index.html`, so next we learn to invalidate them safely and cheaply.
