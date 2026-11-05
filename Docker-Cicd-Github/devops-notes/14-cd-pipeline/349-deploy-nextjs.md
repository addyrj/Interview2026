# 349. Deploy Next.js
# हिंदी में: Next.js को Deploy करना

---

## 🔵 Simple Definition (English)
Deploying Next.js means building the app (`next build`), packaging it (usually as a Docker image using the `standalone` output), and running it on a server behind Nginx. A CD workflow automates this on every push to `main`: build image, push to a registry, SSH to the VPS, pull and restart.

## 🔵 सरल परिभाषा (Hindi)
Next.js deploy करने का मतलब है app को build करना (`next build`), उसे package करना (आमतौर पर `standalone` output से Docker image) और server पर Nginx के पीछे चलाना। CD workflow हर `main` push पर यह सब अपने-आप करता है: image build, registry में push, VPS पर SSH, pull और restart।

---

## 🔴 Problem it Solves
Manual Next.js deploys mean: SSH in, `git pull`, `npm install`, `npm run build` on the production box (slow, uses RAM, can crash a small VPS), then restart pm2. Builds differ between laptop and server, and a failed build leaves the site half-updated. Next.js also has quirks: `NEXT_PUBLIC_*` variables are baked in at build time, and a default image with full `node_modules` is 1 GB+.

## 🔴 यह क्यों बना? (Hindi)
Manual deploy में: SSH करो, `git pull`, `npm install`, production box पर ही `npm run build` (slow, RAM खाता है, छोटा VPS crash हो सकता है), फिर pm2 restart। Laptop और server की builds अलग निकलती हैं, और build fail होने पर site आधी-अधूरी update रहती है। Next.js की अपनी quirks भी हैं: `NEXT_PUBLIC_*` variables build के समय ही bake हो जाते हैं, और पूरे `node_modules` वाली image 1 GB+ होती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Push to main triggers the workflow
Step 2 → CI job: npm ci, lint, test, next build (fail fast)
Step 3 → Docker build with output: 'standalone' (small runtime image)
Step 4 → Push image to GHCR tagged with the commit SHA
Step 5 → SSH to the VPS, docker pull the new tag
Step 6 → docker compose up -d (container replaced)
Step 7 → Health check on /api/health; fail the job if unhealthy
Step 8 → Nginx keeps proxying port 80/443 to the container on 3000
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → main पर push से workflow trigger होता है
Step 2 → CI job: npm ci, lint, test, next build (जल्दी fail हो)
Step 3 → output: 'standalone' के साथ Docker build (छोटी runtime image)
Step 4 → Image को commit SHA tag के साथ GHCR में push
Step 5 → VPS पर SSH, नया tag docker pull
Step 6 → docker compose up -d (container बदल जाता है)
Step 7 → /api/health पर health check; unhealthy हो तो job fail
Step 8 → Nginx port 80/443 से container के port 3000 पर proxy करता रहता है
```

---

## 🟡 Real World Example
A startup runs its marketing site and dashboard (Next.js 14, App Router) on one Ubuntu VPS. Before CD, a developer built on the server and the 2 GB machine ran out of memory mid-build, taking the site down for 10 minutes. After moving the build into GitHub Actions and shipping a 150 MB standalone image, deploys take about 3 minutes, the server only runs `docker pull` and `up -d`, and a bad commit never reaches production because the build step fails in CI first.

## 🟡 Real Example Hindi mein
एक startup अपनी marketing site और dashboard (Next.js 14, App Router) एक Ubuntu VPS पर चलाता है। CD से पहले developer server पर build करता था और 2 GB की machine build के बीच में memory खत्म होने से site 10 मिनट down हो गई। Build को GitHub Actions में ले जाने और 150 MB की standalone image भेजने के बाद deploy लगभग 3 मिनट में होता है, server सिर्फ `docker pull` और `up -d` करता है, और खराब commit production तक पहुँचता ही नहीं क्योंकि build step CI में पहले fail हो जाता है।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Dockerfile (basic) - single stage, simple but large image
FROM node:20-alpine
# working directory inside the container
WORKDIR /app
# copy dependency manifests first for layer caching
COPY package*.json ./
# install exact versions from the lockfile
RUN npm ci
# copy the rest of the source code
COPY . .
# build the production bundle
RUN npm run build
# Next.js listens on 3000 by default
EXPOSE 3000
# start the production server (not `next dev`)
CMD ["npm", "start"]
```

```bash
# basic manual deploy from your laptop (what CD will automate)
# build the image locally
docker build -t myapp-web:manual .
# run it, mapping host port 3000 to container port 3000
docker run -d --name web -p 3000:3000 myapp-web:manual
# check that it responds
curl -I http://localhost:3000
```

## 💻 Code / Config Example — Advanced

```javascript
// next.config.js - enable the small standalone output
/** @type {import('next').NextConfig} */
const nextConfig = {
  // copies only the files needed to run into .next/standalone
  output: 'standalone',
  // hides the X-Powered-By: Next.js header (small security win)
  poweredByHeader: false,
};
// export the config for Next.js
module.exports = nextConfig;
```

```dockerfile
# Dockerfile (advanced) - multi-stage, non-root, small
# ---- stage 1: install dependencies ----
FROM node:20-alpine AS deps
# libc6-compat is needed by some native modules on alpine
RUN apk add --no-cache libc6-compat
WORKDIR /app
# only manifests so this layer is cached until deps change
COPY package.json package-lock.json ./
# clean, reproducible install
RUN npm ci

# ---- stage 2: build ----
FROM node:20-alpine AS builder
WORKDIR /app
# reuse node_modules from stage 1
COPY --from=deps /app/node_modules ./node_modules
# copy the app source
COPY . .
# NEXT_PUBLIC_* values are baked in at BUILD time, so pass them as build args
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
# disable anonymous telemetry during the build
ENV NEXT_TELEMETRY_DISABLED=1
# produce .next/standalone and .next/static
RUN npm run build

# ---- stage 3: runtime ----
FROM node:20-alpine AS runner
WORKDIR /app
# production mode, no telemetry
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1
# listen on all interfaces so Docker port mapping works
ENV HOSTNAME=0.0.0.0 PORT=3000
# create an unprivileged user
RUN addgroup -S app && adduser -S app -G app
# public assets (images, favicon)
COPY --from=builder --chown=app:app /app/public ./public
# minimal server + traced node_modules
COPY --from=builder --chown=app:app /app/.next/standalone ./
# static chunks are not in standalone, copy them separately
COPY --from=builder --chown=app:app /app/.next/static ./.next/static
# drop root
USER app
EXPOSE 3000
# lightweight health probe using node (no curl in alpine by default)
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:3000/api/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
# standalone ships its own server.js
CMD ["node", "server.js"]
```

```yaml
# .github/workflows/deploy-nextjs.yml
name: Deploy Next.js            # name shown in the Actions tab
on:
  push:
    branches: [main]            # deploy only from main
concurrency:
  group: deploy-web             # one deploy at a time
  cancel-in-progress: false     # never cancel a running deploy half-way
permissions:
  contents: read                # read the repo
  packages: write               # push to GHCR
jobs:
  build:
    runs-on: ubuntu-latest      # GitHub hosted runner
    outputs:
      tag: ${{ steps.meta.outputs.tag }}   # pass the tag to the deploy job
    steps:
      - uses: actions/checkout@v4          # example version, update as needed
      - uses: actions/setup-node@v4        # install Node for lint and test
        with:
          node-version: 20                 # match the Dockerfile
          cache: npm                       # cache ~/.npm
      - run: npm ci                        # install exact dependencies
      - run: npm run lint --if-present     # lint if the script exists
      - run: npm test --if-present         # tests if the script exists
      - id: meta                           # compute image tag
        run: echo "tag=ghcr.io/${GITHUB_REPOSITORY,,}/web:${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"
      - uses: docker/login-action@v3       # log in to GHCR
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5  # build and push image
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tag }}
          build-args: NEXT_PUBLIC_API_URL=${{ vars.NEXT_PUBLIC_API_URL }}
          cache-from: type=gha             # reuse layers from earlier runs
          cache-to: type=gha,mode=max      # store layers for next run
  deploy:
    needs: build                           # run only if build succeeded
    runs-on: ubuntu-latest
    environment: production                # lets you add approvals/secrets
    steps:
      - uses: appleboy/ssh-action@v1.0.3   # SSH into the VPS (example version)
        with:
          host: ${{ secrets.VPS_HOST }}    # server IP or domain
          username: ${{ secrets.VPS_USER }}# deploy user (not root)
          key: ${{ secrets.VPS_SSH_KEY }}  # private key stored as secret
          script: |
            set -e
            echo "${{ secrets.GHCR_PULL_TOKEN }}" | docker login ghcr.io -u "${{ github.actor }}" --password-stdin
            cd /srv/myapp
            export WEB_IMAGE=${{ needs.build.outputs.tag }}
            docker compose pull web
            docker compose up -d web
            sleep 10
            curl -fsS http://127.0.0.1:3000/api/health
```

---

## 🟠 My Stack Integration
Next.js sits next to your FastAPI API and Nginx on the same VPS. Nginx terminates TLS and routes `/` to Next.js and `/api/` to FastAPI. Server-side code inside Next.js talks to FastAPI through the Docker network name, not the public URL.

```yaml
# /srv/myapp/docker-compose.yml (on the VPS)
services:
  web:
    image: ${WEB_IMAGE}               # tag injected by the deploy script
    restart: unless-stopped           # come back after reboot or crash
    environment:
      API_INTERNAL_URL: http://api:8000   # server-side calls use Docker DNS
    ports:
      - "127.0.0.1:3000:3000"         # only Nginx on the host can reach it
  api:
    image: ghcr.io/me/myapp/api:latest    # FastAPI service
    restart: unless-stopped
    expose:
      - "8000"                        # internal only
```

```nginx
# /etc/nginx/conf.d/myapp.conf
server {
  listen 443 ssl http2;                       # HTTPS
  server_name app.example.com;                # your domain
  ssl_certificate     /etc/letsencrypt/live/app.example.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/app.example.com/privkey.pem;
  location /_next/static/ {                   # hashed assets, cache hard
    proxy_pass http://127.0.0.1:3000;
    add_header Cache-Control "public, max-age=31536000, immutable";
  }
  location / {
    proxy_pass http://127.0.0.1:3000;         # Next.js container
    proxy_set_header Host $host;              # keep the original host
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
```

Security: use a dedicated deploy user, a deploy-only SSH key, secrets in GitHub (never in the image), and bind port 3000 to `127.0.0.1`. Do not put secrets in `NEXT_PUBLIC_*`: they are visible in the browser bundle.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Setting `NEXT_PUBLIC_API_URL` only at container runtime.
✅ Correct: Pass it as a Docker `ARG` at build time; the value is inlined into the JS bundle during `next build`.

❌ Mistake 2: Forgetting `output: 'standalone'` and copying the whole project into the final image.
✅ Correct: Enable standalone and copy `.next/standalone`, `.next/static`, and `public` only.

❌ Mistake 3: Building on the production server.
✅ Correct: Build in CI, ship an image, and let the server only pull and run.

❌ Mistake 4: Container listens on `localhost` so published ports do not work.
✅ Correct: Set `HOSTNAME=0.0.0.0` in the runtime stage.

❌ Mistake 5: Running as root and storing secrets in the image.
✅ Correct: Use `USER app` and inject secrets at runtime.

---

## 🧠 Tricky Interview Question
After deploy, the site shows the old API URL even though you changed the GitHub variable and redeployed. Why?

Answer: `NEXT_PUBLIC_*` values are replaced at build time. If Docker reused a cached layer for `npm run build`, or if the variable was set only at runtime, the old value stays in the bundle. Pass it as a build arg (changing an ARG invalidates the layer that uses it) and rebuild. For truly runtime config, fetch it from a server route or use server-side environment variables instead.

---

## ⚫ Interview Questions + Answers

Q1: Why use `output: 'standalone'`?
A1: It traces the files the server needs and copies them to `.next/standalone` with a minimal `server.js`, cutting the image from over 1 GB to roughly 100-200 MB and speeding up pulls and deploys.

Q2: Where should secrets like database passwords live?
A2: Only as runtime environment variables on the server (or a secrets manager), read in server-side code. Never in `NEXT_PUBLIC_*` and never baked into image layers.

Q3: How do you avoid downtime while the container is replaced?
A3: With one container there is a few seconds of gap. Use blue-green or two replicas behind Nginx upstream, or at least a health check plus quick `up -d`. Covered in topics 351 and 353.

Q4: Why tag images with the commit SHA instead of only `latest`?
A4: A SHA is immutable and traceable, which makes rollback exact (redeploy the previous SHA). `latest` moves and hides which code is running.

Q5: How do you cache static assets correctly?
A5: Files under `/_next/static/` are content-hashed, so serve them with `immutable` long cache headers via Nginx or a CDN; HTML stays short-lived.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You self-host Next.js on a VPS or EC2 and want repeatable deploys.
- You need SSR, API routes or image optimization (a static host is not enough).
- You want cheap predictable cost compared to per-request platforms.

❌ Avoid when:
- The site is fully static: use `next export`/static hosting on S3 + CloudFront.
- You have no one to maintain servers: a managed platform may be cheaper in time.

---

## 📊 Visual Diagram
```
 git push main
      |
      v
 +-----------------+     +------------------+
 | GitHub Actions  | --> | GHCR registry    |
 | lint/test/build |     | web:abc1234      |
 +-----------------+     +---------+--------+
                                   | docker pull (via SSH)
                                   v
 Browser --> Nginx :443 --> [ web container :3000 ] --> [ api (FastAPI) :8000 ]
              (TLS, cache)        Next.js standalone
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| standalone output | Minimal self-contained server build | छोटा, अपने-आप में पूरा server build |
| NEXT_PUBLIC_ | Env vars inlined into browser JS at build | build पर browser JS में डलने वाले variables |
| GHCR | GitHub Container Registry | GitHub का image registry |
| SSH deploy | Run commands on server over SSH | SSH से server पर commands चलाना |
| Health check | Endpoint/command proving the app is alive | app चल रहा है यह जाँचने वाला endpoint |

---

## ⚡ 3-Line Summary
English: Build the Next.js app in CI as a standalone Docker image, push it to a registry, and let the VPS only pull and run it.
Remember that `NEXT_PUBLIC_*` is build-time and secrets must stay server-side.
Put Nginx in front for TLS and caching, and verify with a health check.
Hindi: Next.js को CI में standalone Docker image के रूप में build करो, registry में push करो, और VPS सिर्फ pull करके चलाए।
याद रखो `NEXT_PUBLIC_*` build-time होता है और secrets server-side ही रहें।
TLS और caching के लिए आगे Nginx रखो और health check से verify करो।

---

## ➡️ Next Topic
**350. Deploy FastAPI** — the backend half of the same stack: Uvicorn/Gunicorn, migrations and health checks in a CD pipeline.
