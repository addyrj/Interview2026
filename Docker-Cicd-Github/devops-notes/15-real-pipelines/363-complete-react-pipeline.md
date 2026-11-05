---

# 363. Complete React Pipeline
# हिंदी में: पूरा React Pipeline

---

## 🔵 Simple Definition (English)
A React pipeline installs dependencies, lints, tests, builds the static bundle (`npm run build`), and publishes it either inside an Nginx Docker image or to S3 + CloudFront. React ends as plain HTML/JS/CSS files, so deploy means "put these files behind a web server".

## 🔵 सरल परिभाषा (Hindi)
React pipeline dependencies install करता है, lint, test और static bundle (`npm run build`) बनाता है, फिर उसे Nginx Docker image में या S3 + CloudFront पर publish करता है। React अंत में सिर्फ HTML/JS/CSS files होती हैं, इसलिए deploy का मतलब है "ये files किसी web server के पीछे रख दो"।

---

## 🔴 Problem it Solves
- Building on a laptop produces different bundles (different Node version, local `.env`).
- Forgetting `npm run build`, or uploading the wrong folder.
- Stale browser cache: users keep old JS after a release.
- API URL baked wrongly into the bundle for the wrong environment.

## 🔴 यह क्यों बना? (Hindi)
- Laptop पर build करने से अलग bundle बनते हैं (अलग Node version, local `.env`)।
- `npm run build` भूल जाना या गलत folder upload करना।
- Stale browser cache: release के बाद भी users को पुराना JS मिलता है।
- गलत environment का API URL bundle में बैठ जाना।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Push or PR triggers workflow
Step 2 → npm ci (exact lockfile install, cached)
Step 3 → eslint + vitest/jest
Step 4 → npm run build with VITE_API_URL for the target env
Step 5 → Docker multi-stage: node builds, nginx serves /dist
Step 6 → Push image, deploy to VPS (or sync dist to S3 + invalidate CloudFront)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Push या PR से workflow चलता है
Step 2 → npm ci (lockfile के हिसाब से exact install, cached)
Step 3 → eslint + vitest/jest
Step 4 → Target env के VITE_API_URL के साथ npm run build
Step 5 → Docker multi-stage: node build करता है, nginx /dist serve करता है
Step 6 → Image push, VPS पर deploy (या dist को S3 पर sync + CloudFront invalidate)
```

---

## 🟡 Real World Example
An e-commerce team (Flipkart-style storefront) ships a React admin dashboard daily. Their pipeline builds hashed filenames (`app.8f3a1c.js`), uploads them to S3 with a one-year cache header, and uploads `index.html` with `no-cache`. After the upload, CloudFront is invalidated for `/index.html` only. Users get new releases instantly, and old tabs still load their old hashed files without errors.

## 🟡 Real Example Hindi mein
एक e-commerce team (Flipkart जैसा storefront) रोज़ React admin dashboard release करती है। Pipeline hashed filenames (`app.8f3a1c.js`) बनाता है, उन्हें S3 पर एक साल के cache header के साथ और `index.html` को `no-cache` के साथ upload करता है। फिर सिर्फ `/index.html` के लिए CloudFront invalidate होता है। Users को नया release तुरंत मिलता है और पुराने tabs अपनी पुरानी hashed files बिना error load करते हैं।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/react-basic.yml
name: React CI                         # Workflow name
on:                                    # Triggers
  push:
    branches: [main]                   # Run on main pushes
  pull_request:                        # And on PRs
jobs:
  build:                               # Single job
    runs-on: ubuntu-latest             # Runner
    steps:
      - uses: actions/checkout@v4      # Fetch code
      - uses: actions/setup-node@v4    # Install Node
        with:
          node-version: 20             # LTS used in production
          cache: npm                   # Cache ~/.npm using package-lock.json
      - run: npm ci                    # Clean, reproducible install
      - run: npm run lint              # ESLint
      - run: npm test -- --run         # Tests once (Vitest syntax; adjust for Jest)
      - run: npm run build             # Produce dist/
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/react-pipeline.yml
name: React Pipeline
on:
  push:
    branches: [main]
  pull_request:
concurrency:
  group: react-${{ github.ref }}       # One run per ref
  cancel-in-progress: true             # Drop superseded runs
permissions:
  contents: read                       # Least privilege
  id-token: write                      # Needed for AWS OIDC
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci                    # Exact lockfile install
      - run: npm run lint              # Static checks
      - run: npm test -- --run         # Unit tests
      - run: npx tsc --noEmit          # Type check (remove if no TypeScript)
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build             # Vite reads VITE_* at build time
        env:
          VITE_API_URL: https://api.example.com   # Public value, never a secret
      - uses: actions/upload-artifact@v4   # Share dist with deploy job
        with:
          name: dist
          path: dist
          retention-days: 7            # Keep cost low
  deploy:
    if: github.ref == 'refs/heads/main'
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/download-artifact@v4   # Get the built files
        with:
          name: dist
          path: dist
      - uses: aws-actions/configure-aws-credentials@v4   # OIDC, no long-lived keys
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-react-deploy   # Example ARN
          aws-region: ap-south-1
      - name: Upload hashed assets (long cache)
        run: |
          aws s3 sync dist s3://my-react-bucket --delete --exclude index.html \
            --cache-control "public,max-age=31536000,immutable"
      - name: Upload index.html (never cached)
        run: |
          aws s3 cp dist/index.html s3://my-react-bucket/index.html \
            --cache-control "no-cache"
      - name: Invalidate CloudFront for index.html
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.CF_DIST_ID }} --paths "/index.html"
```

---

## 🟠 My Stack Integration
If you serve React from your VPS (Nginx), use a multi-stage image. The same pipeline pushes it to GHCR and the VPS pulls it.

```dockerfile
# Dockerfile for React on Nginx
# Stage 1: build the bundle
FROM node:20-alpine AS build
# Work inside /app
WORKDIR /app
# Copy manifests first for cache
COPY package.json package-lock.json ./
# Reproducible install
RUN npm ci
# Copy source
COPY . .
# API URL baked at build time
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
# Create dist/
RUN npm run build
# Stage 2: tiny runtime image
FROM nginx:1.27-alpine
# Replace default config with SPA-aware config
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Copy only the built files
COPY --from=build /app/dist /usr/share/nginx/html
# Documented port
EXPOSE 80
```

```nginx
# nginx.conf (SPA fallback and caching)
server {
  listen 80;
  root /usr/share/nginx/html;
  location / { try_files $uri /index.html; add_header Cache-Control "no-cache"; }
  location /assets/ { add_header Cache-Control "public, max-age=31536000, immutable"; }
}
```

Nginx config was not run through `nginx -t` here. Your API (FastAPI/Node) stays on a separate domain or `/api` proxy.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `npm install` in CI.
✅ Correct: Use `npm ci` for lockfile-exact, faster installs.

❌ Mistake 2: Putting API keys in `VITE_*` or `REACT_APP_*` variables.
✅ Correct: Anything in the bundle is public. Keep secrets on the backend.

❌ Mistake 3: No SPA fallback, so refreshing `/orders/5` gives 404.
✅ Correct: `try_files $uri /index.html;`.

❌ Mistake 4: Caching `index.html` for a year.
✅ Correct: `no-cache` on HTML, immutable on hashed assets.

Security: long-lived AWS keys in secrets are risky; use OIDC with a role limited to one bucket. Add `npm audit --omit=dev` as a gate.

---

## 🧠 Tricky Interview Question
You deployed a new React build, but some users still see the old UI and some see a blank page. Why?

Answer: Old `index.html` was cached and points to old hashed JS files that your `--delete` sync already removed, so they 404 and the app goes blank. Fix: keep `index.html` uncached, invalidate it, and avoid deleting previous assets immediately (keep last few versions or delay cleanup).

---

## ⚫ Interview Questions + Answers

Q1: Difference between `npm ci` and `npm install`?
A1: `ci` deletes `node_modules`, installs exactly from the lockfile, fails if lock and package.json differ. Deterministic for CI.

Q2: When do React env vars get their values?
A2: At build time, not runtime. They are replaced in the bundle. For runtime config use a `config.js` loaded before the app or Nginx-injected values.

Q3: Why multi-stage Docker for React?
A3: Node and node_modules (hundreds of MB) are needed only to build. The final Nginx image has only static files, so it is small and has less attack surface.

Q4: S3+CloudFront or Nginx on a VPS?
A4: S3+CloudFront gives global CDN, cheap scale, no server to patch. VPS Nginx is simpler when you already run everything on one box.

Q5: How do you avoid deploying a broken build?
A5: `needs:` gates (lint, test, type check), plus a smoke check by curling the deployed URL.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Static React/Vite SPA with an API on another service.
- You want fast global delivery (S3 + CloudFront).

❌ Avoid when:
- You need server-side rendering and SEO (use Next.js pipeline with a Node runtime).
- Secrets would be required inside the browser code.

---

## 📊 Visual Diagram
```
 push --> [npm ci] --> [lint/test] --> [npm run build -> dist/]
                                              |
                       +----------------------+--------------------+
                       |                                           |
                       v                                           v
        Docker (nginx + dist) -> GHCR -> VPS            S3 sync -> CloudFront
                                                       (invalidate /index.html)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SPA | Single page app | Single page application |
| Bundle | Built JS/CSS output | Build से बनी JS/CSS files |
| Cache busting | Hashed filenames force refresh | Hash वाले नाम से नया file मजबूर करना |
| OIDC | Token-based cloud login | Token आधारित cloud login |
| Invalidation | Clear CDN cached copy | CDN का cache हटाना |

---

## ⚡ 3-Line Summary
English: `npm ci`, lint, test, build, then publish dist via Nginx image or S3 + CloudFront.
English: Cache hashed assets for a year and keep index.html uncached.
English: Never put secrets in the bundle; use OIDC for AWS.
Hindi: `npm ci`, lint, test, build, फिर dist को Nginx image या S3 + CloudFront से publish करें।
Hindi: Hashed assets एक साल cache करें और index.html uncached रखें।
Hindi: Bundle में secrets नहीं; AWS के लिए OIDC।

---

## ➡️ Next Topic
364. Complete NestJS Pipeline: now the Node.js backend, with its build step and database tests.
