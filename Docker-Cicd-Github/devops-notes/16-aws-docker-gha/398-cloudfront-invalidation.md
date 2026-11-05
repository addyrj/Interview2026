# 398. CloudFront Invalidation
# हिंदी में: CloudFront Invalidation

---

## 🔵 Simple Definition (English)
**CloudFront** caches your files at edge locations around the world. An **invalidation** tells CloudFront to drop cached copies of specific paths (like `/index.html` or `/*`) so the next request fetches the fresh file from the origin (S3 or your server). In CI it is one CLI call right after you upload a new build.

## 🔵 सरल परिभाषा (Hindi)
**CloudFront** आपकी files को दुनिया भर के edge locations पर cache करता है। **Invalidation** CloudFront को बताती है कि specific paths (जैसे `/index.html` या `/*`) की cached copies हटा दे, ताकि अगली request पर origin (S3 या आपका server) से ताज़ा file आए। CI में नया build upload करने के तुरंत बाद यह बस एक CLI call है।

---

## 🔴 Problem it Solves
You deploy a fix, but users still see the old page for hours because edge caches hold `index.html` until the TTL expires (default 24 hours if the origin sends no cache headers). Support gets tickets; you cannot say "clear your browser cache" to a million users.

Invalidation removes old copies immediately (usually in a minute or two) so the new version is live for everyone.

## 🔴 यह क्यों बना? (Hindi)
आप fix deploy करते हैं, पर edge caches TTL खत्म होने तक `index.html` रखे रहते हैं (origin cache headers न भेजे तो default 24 घंटे), इसलिए users घंटों पुराना page देखते हैं। Support को tickets आते हैं; दस लाख users से "browser cache साफ़ करो" नहीं कह सकते।

Invalidation पुरानी copies तुरंत हटा देती है (आमतौर पर एक-दो मिनट में) ताकि नया version सबके लिए live हो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → CI uploads new files to S3 (topic 397)
Step 2 → CI calls: aws cloudfront create-invalidation --distribution-id ID --paths "/index.html"
Step 3 → CloudFront returns an Invalidation Id with status InProgress
Step 4 → Edge locations remove cached objects matching the path(s)
Step 5 → Next request at each edge -> cache MISS -> fetch from S3 -> cache again
Step 6 → CI runs "aws cloudfront wait invalidation-completed" (optional)
Step 7 → Smoke test checks the new version string / build id
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → CI नई files S3 में upload करता है (topic 397)
Step 2 → CI call करता है: aws cloudfront create-invalidation --distribution-id ID --paths "/index.html"
Step 3 → CloudFront Invalidation Id और status InProgress लौटाता है
Step 4 → Edge locations matching path की cached objects हटा देते हैं
Step 5 → हर edge पर अगली request -> cache MISS -> S3 से fetch -> दोबारा cache
Step 6 → CI "aws cloudfront wait invalidation-completed" चलाता है (optional)
Step 7 → Smoke test नया version string / build id जाँचता है
```

---

## 🟡 Real World Example
A news site pushes a corrected headline and wants it live in two minutes. Their pipeline uploads the build and invalidates `/index.html` and `/sitemap.xml` only. Because JS and CSS files have hashed names (`main.9c1d.js`), they never need invalidation; the new `index.html` simply points to new file names. They avoid `/*` because after the first 1,000 invalidation paths per month AWS charges per path.

## 🟡 Real Example Hindi mein
एक news site सही की गई headline दो मिनट में live चाहती है। उनकी pipeline build upload करके सिर्फ `/index.html` और `/sitemap.xml` invalidate करती है। JS और CSS files के नाम hashed हैं (`main.9c1d.js`), इसलिए उन्हें invalidate करने की कभी ज़रूरत नहीं; नया `index.html` बस नए file names की तरफ इशारा करता है। वे `/*` से बचते हैं क्योंकि हर महीने के पहले 1,000 invalidation paths के बाद AWS प्रति path charge करता है।

---

## 💻 Code / Config Example — Basic

```bash
# invalidate only the entry file (cheap, enough for hashed-asset SPAs)
aws cloudfront create-invalidation \
  --distribution-id E123EXAMPLE \
  --paths "/index.html"
# wildcard form (counts as ONE path, but removes everything; avoid unless needed)
aws cloudfront create-invalidation --distribution-id E123EXAMPLE --paths "/*"
```

```yaml
name: invalidate-basic                           # workflow name
on:
  workflow_dispatch: {}                          # manual run for testing
permissions:
  id-token: write                                # OIDC
  contents: read                                 # checkout
jobs:
  invalidate:
    runs-on: ubuntu-latest                       # runner
    steps:
      - uses: aws-actions/configure-aws-credentials@v4   # OIDC login
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
          aws-region: us-east-1                  # CloudFront API calls are global; us-east-1 is safe
      - run: aws cloudfront create-invalidation --distribution-id ${{ vars.CF_DISTRIBUTION_ID }} --paths "/index.html"   # drop cached entry file
```

## 💻 Code / Config Example — Advanced

Full deploy: upload to S3, invalidate, wait, verify the new build id. The site writes `build-id.txt` at build time.

```yaml
name: frontend-deploy-with-invalidation         # workflow name
on:
  push:
    branches: [main]                             # deploy from main
permissions:
  id-token: write                                # OIDC
  contents: read                                 # checkout
env:
  BUCKET: my-site-prod                           # S3 bucket
  DISTRIBUTION_ID: E123EXAMPLE                   # CloudFront distribution ID
  SITE_URL: https://www.example.com              # public URL for verification
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
      - run: npm ci && npm run build             # install + build
      - run: echo "${{ github.sha }}" > dist/build-id.txt   # stamp the build for verification
      - uses: aws-actions/configure-aws-credentials@v4   # OIDC login
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ap-south-1
      - name: Upload to S3                       # hashed assets first, entry files last
        run: |
          aws s3 sync dist "s3://$BUCKET" --exclude "index.html" --exclude "build-id.txt" --cache-control "public,max-age=31536000,immutable"
          aws s3 cp dist/index.html "s3://$BUCKET/index.html" --cache-control "no-cache"
          aws s3 cp dist/build-id.txt "s3://$BUCKET/build-id.txt" --cache-control "no-cache"
      - name: Invalidate entry files             # only what changes under the same name
        id: inv
        run: |
          ID=$(aws cloudfront create-invalidation \
            --distribution-id "$DISTRIBUTION_ID" \
            --paths "/index.html" "/build-id.txt" \
            --query Invalidation.Id --output text)   # capture invalidation id
          echo "id=$ID" >> "$GITHUB_OUTPUT"
      - name: Wait until invalidation completes
        run: aws cloudfront wait invalidation-completed --distribution-id "$DISTRIBUTION_ID" --id "${{ steps.inv.outputs.id }}"
      - name: Verify the new build is served     # compare served build id with this commit
        run: |
          for i in 1 2 3 4 5; do
            SERVED=$(curl -fsS "$SITE_URL/build-id.txt?cb=$RANDOM" | tr -d '[:space:]')   # cache-buster for the check
            [ "$SERVED" = "${{ github.sha }}" ] && echo "live: $SERVED" && exit 0
            sleep 10                             # edges may need a moment
          done
          echo "new build not visible"; exit 1   # fail the job
```

IAM needed for the invalidation step (add to the deploy role):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["cloudfront:CreateInvalidation", "cloudfront:GetInvalidation"],
      "Resource": "arn:aws:cloudfront::111122223333:distribution/E123EXAMPLE"
    }
  ]
}
```

---

## 🟠 My Stack Integration
- **React**: invalidate `/index.html` only; use hashed filenames from Vite/Webpack so nothing else needs it.
- **Next.js static / ISR**: invalidate changed HTML paths or use `/*` after a full export; or use versioned paths.
- **Node.js / FastAPI API behind CloudFront**: prefer correct `Cache-Control` from the app (`no-store` for private data, `s-maxage` for public GET) over invalidation. Never cache authenticated responses; forward the `Authorization` header or do not cache.
- **Nginx**: if CloudFront fronts Nginx on EC2, set `add_header Cache-Control` per location; the CDN respects it.
- **VPS**: a VPS-hosted origin works the same way; invalidation is independent of the origin.
- **Alternative**: versioned object keys (`/v123/app.js`) avoid invalidation completely and are free.

```nginx
# Nginx origin snippet (example; run "nginx -t" on your server): cache rules that reduce the need for invalidation
location = /index.html {                          # entry file
    add_header Cache-Control "no-cache";          # CDN and browser must revalidate
}
location /assets/ {                               # hashed build files
    add_header Cache-Control "public, max-age=31536000, immutable";   # cache for one year
}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Invalidating `/*` on every deploy.
✅ Correct: Invalidate only changed non-hashed paths; hashed files never need it. (Wildcard counts as one path, but invalidations hit cache hit-ratio and origin load.)

❌ Mistake 2: Invalidating before the S3 upload finishes.
✅ Correct: Upload first, invalidate after; otherwise the edge re-caches the old file.

❌ Mistake 3: Relying on invalidation for correctness (e.g. private user data).
✅ Correct: Correct cache headers and cache keys; invalidation is a cleanup tool.

❌ Mistake 4: Not waiting or verifying; the pipeline says green but users see old content.
✅ Correct: `wait invalidation-completed` plus a build-id check.

❌ Mistake 5: Forgetting that browsers cache too; invalidation does not clear browser caches.
✅ Correct: `no-cache` on `index.html` so browsers revalidate.

---

## 🧠 Tricky Interview Question
You invalidated `/index.html` and it shows "Completed", yet some users still see the old page. Name three possible reasons.

Answer: (1) Browser or ISP/proxy caches: invalidation affects only CloudFront edges, and `index.html` had `max-age` instead of `no-cache`. (2) Query strings or different cache keys: `/index.html?v=1` and `/` (default root object) are separate cache entries; you invalidated only one path. (3) Origin returned stale content when edges refetched (S3 replication or the upload finished after the invalidation). Fix with correct headers, invalidate `/` and `/index.html`, and sequence upload before invalidation.

---

## ⚫ Interview Questions + Answers

Q1: How much does invalidation cost?
A1: First 1,000 paths per month are free; after that a small charge per path (check pricing). A wildcard path counts as one path.

Q2: Invalidation vs versioned file names?
A2: Versioned names (content hash) are instant, free, and safer, so use them for assets. Invalidate only for fixed-name files such as `index.html`, `robots.txt`, `sitemap.xml`.

Q3: How long does it take?
A3: Usually under a couple of minutes, not guaranteed. Use `wait invalidation-completed` and do not rely on instant effect.

Q4: What is a CloudFront cache key?
A4: The set of request parts (path, selected query strings, headers, cookies) that identify a cached object. Different keys mean different cache entries, so invalidate every variant you serve.

Q5: Can you automate invalidation from S3 events?
A5: Yes, with S3 event to Lambda calling `CreateInvalidation`, but a CI step is simpler and more predictable.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Fixed-name files changed (`index.html`, `config.json`, `sitemap.xml`)
- Emergency removal of wrong or sensitive content
- Content updates must be live within minutes

❌ Avoid when:
- You can use hashed/versioned file names (free and instant)
- Every request for dynamic personalised data (do not cache it)
- High-frequency changes; lower TTL or use `no-cache` instead

---

## 📊 Visual Diagram
```
 CI: aws s3 sync   --->  S3 (new files)
 CI: create-invalidation /index.html
          |
          v
 +-------------+  +-------------+  +-------------+
 | Edge Mumbai |  | Edge London |  | Edge NYC    |   <- old index.html REMOVED
 +------+------+  +------+------+  +------+------+
        | next request = MISS -> fetch new file from S3 -> cache again
        v
     Users get new index.html -> new hashed JS/CSS (already cached for 1 year)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Edge location | CloudFront cache server near users | users के पास cache server |
| TTL | How long an object stays cached | object कितनी देर cached रहे |
| Invalidation | Remove cached objects early | cached objects को जल्दी हटाना |
| Cache key | What makes two requests the same cache entry | दो requests को एक cache entry बनाने वाले हिस्से |
| Origin | Where CloudFront fetches from | CloudFront जहाँ से लाता है |
| Cache-Control | Header with caching rules | caching नियमों वाला header |

---

## ⚡ 3-Line Summary
English: Invalidation removes cached copies at CloudFront edges so new content appears quickly.
English: Invalidate only fixed-name files after the S3 upload; use hashed names for everything else.
English: Wait and verify with a build id, and set correct cache headers for browsers.
Hindi: Invalidation CloudFront edges की cached copies हटाती है ताकि नया content जल्दी दिखे।
Hindi: S3 upload के बाद सिर्फ fixed-name files invalidate करें; बाकी के लिए hash वाले नाम रखें।
Hindi: Build id से wait और verify करें, और browsers के लिए सही cache headers रखें।

---

## ➡️ Next Topic
**399. AWS CDK Basics**: so far we created buckets, distributions and roles by hand; CDK lets us define all of that in TypeScript code.
