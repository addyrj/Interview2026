# 089. Dockerfile Best Practices
# हिंदी में: Dockerfile की Best Practices

---

## 🔵 Simple Definition (English)
Dockerfile best practices are proven rules for writing images that are **small, fast to build, secure, reproducible and easy to maintain**: pin versions, use multi-stage builds, order layers for cache, run as non-root, keep secrets out, and add a healthcheck.

## 🔵 सरल परिभाषा (Hindi)
Dockerfile best practices वे आज़माए हुए नियम हैं जिनसे image **छोटी, तेज़ बनने वाली, सुरक्षित, reproducible और maintain करने में आसान** बनती है: versions pin करो, multi-stage build use करो, cache के लिए layers का क्रम रखो, non-root चलाओ, secrets बाहर रखो और healthcheck जोड़ो।

---

## 🔴 Problem it Solves
A naive Dockerfile (`FROM node:latest`, `COPY . .`, `RUN npm install`, run as root) produces a 1.2 GB image that rebuilds from scratch on every code change, breaks when `latest` moves, contains `.env`, includes compilers and dev dependencies for attackers to use, and gets flagged by every scanner. This costs build minutes in CI, registry storage, slow deploys on the VPS, and security incidents. Best practices fix all of these at once.

## 🔴 यह क्यों बना? (Hindi)
एक naive Dockerfile (`FROM node:latest`, `COPY . .`, `RUN npm install`, root से चलाना) 1.2 GB की image बनाती है जो हर code change पर शुरू से rebuild होती है, `latest` बदलने पर टूट जाती है, उसमें `.env` होती है, attacker के काम आने वाले compilers और dev dependencies होते हैं, और हर scanner उसे flag करता है। इससे CI के build minutes, registry storage, VPS पर धीमे deploy और security incidents का खर्च होता है। Best practices ये सब एक साथ ठीक करती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose a small, pinned base: node:20-alpine (or -slim), never :latest
Step 2 → Add .dockerignore (no node_modules, .git, .env)
Step 3 → Multi-stage: build tools in stage 1, only artifacts in the final stage
Step 4 → Order layers: manifests -> install deps -> copy source (cache friendly)
Step 5 → Combine related RUN steps; clean package caches in the same layer
Step 6 → Run as non-root (USER), read-only code, drop capabilities
Step 7 → Exec-form CMD/ENTRYPOINT (signals reach the app), one process per container
Step 8 → HEALTHCHECK, LABELs, no secrets in ARG/ENV/layers
Step 9 → Lint (hadolint) + scan (Trivy) in CI before pushing
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → छोटा, pinned base चुनो: node:20-alpine (या -slim), कभी :latest नहीं
Step 2 → .dockerignore जोड़ो (node_modules, .git, .env नहीं)
Step 3 → Multi-stage: build tools stage 1 में, final stage में सिर्फ artifacts
Step 4 → Layers का क्रम: manifests -> deps install -> source copy (cache के लिए)
Step 5 → संबंधित RUN steps जोड़ो; package caches उसी layer में साफ करो
Step 6 → Non-root (USER), read-only code, capabilities हटाओ
Step 7 → Exec-form CMD/ENTRYPOINT (signals app तक पहुँचें), हर container में एक process
Step 8 → HEALTHCHECK, LABELs, ARG/ENV/layers में secrets नहीं
Step 9 → Push से पहले CI में lint (hadolint) + scan (Trivy)
```

---

## 🟡 Real World Example
A startup's React + Node.js app went from a 1.1 GB image (`node:latest`, single stage, dev dependencies, built on every commit in 6 minutes) to a 140 MB image (multi-stage, `node:20-alpine`, prod deps only, cached dependency layer) building in 50 seconds on GitHub Actions. VPS deploys, which pull the image over a modest connection, dropped from 4 minutes to 30 seconds. A Trivy scan went from 200+ findings to a handful, because there was no build toolchain or OS packages left to be vulnerable.

## 🟡 Real Example Hindi mein
एक startup की React + Node.js app 1.1 GB image (`node:latest`, single stage, dev dependencies, हर commit पर 6 मिनट में build) से 140 MB image (multi-stage, `node:20-alpine`, सिर्फ prod deps, cached dependency layer) पर आई जो GitHub Actions पर 50 सेकंड में build होती है। सामान्य connection पर image pull करने वाले VPS deploy 4 मिनट से 30 सेकंड हो गए। Trivy scan 200+ findings से कुछ ही findings पर आ गया, क्योंकि build toolchain और OS packages बचे ही नहीं जो vulnerable हों।

---

## 💻 Code / Config Example — Basic

```dockerfile
# BAD vs GOOD: this is the GOOD basic version (Node.js API)
# Pinned, small base image (example tag; update regularly)
FROM node:20-alpine
# Set production mode (libraries optimise for it)
ENV NODE_ENV=production
# Working directory
WORKDIR /app
# Copy ONLY manifests first so the install layer is cached until dependencies change
COPY package.json package-lock.json ./
# Reproducible install from the lock file; production deps only; clean cache
RUN npm ci --omit=dev && npm cache clean --force
# Now copy the source (changes often, so it comes late)
COPY . .
# Document the port
EXPOSE 3000
# Run unprivileged
USER node
# Exec form: Node receives SIGTERM directly
CMD ["node", "server.js"]
```

```dockerfile
# BAD (for comparison, do not use)
# Moving tag, huge image
FROM node:latest
# Copies everything, including .env and node_modules, invalidating cache on any change
COPY . .
# Not reproducible, includes dev dependencies
RUN npm install
# Runs as root, shell form (signals go to sh, not node)
CMD npm start
```

## 💻 Code / Config Example — Advanced

```dockerfile
# syntax=docker/dockerfile:1
# Production multi-stage: React (Vite) frontend built by Node, served by unprivileged Nginx
# Stage 0: shared Node version in one place
ARG NODE_VERSION=20-alpine
# Pin Nginx tag in one place too
ARG NGINX_VERSION=1.27-alpine

# ---- Stage 1: dependencies (cached until package files change) ----
FROM node:${NODE_VERSION} AS deps
# Working directory
WORKDIR /app
# Manifests only
COPY package.json package-lock.json ./
# Install ALL deps (build needs dev deps); npm cache is mounted, not stored in the layer
RUN --mount=type=cache,target=/root/.npm npm ci

# ---- Stage 2: build the static site ----
FROM node:${NODE_VERSION} AS build
# Working directory
WORKDIR /app
# Take node_modules from the deps stage
COPY --from=deps /app/node_modules ./node_modules
# Source code (changes often)
COPY . .
# Public API URL baked into the bundle at build time (not a secret)
ARG VITE_API_URL=https://api.example.com
# Make the ARG visible to Vite as an env var for this build only
ENV VITE_API_URL=${VITE_API_URL}
# Produce /app/dist
RUN npm run build

# ---- Stage 3: tiny runtime image ----
FROM nginxinc/nginx-unprivileged:${NGINX_VERSION} AS runtime
# Re-declare for labels
ARG GIT_SHA=unknown
# Metadata for traceability
LABEL org.opencontainers.image.revision="${GIT_SHA}" org.opencontainers.image.source="https://github.com/your-org/your-repo"
# Custom Nginx config (SPA fallback, caching, security headers)
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Only the built static files, no Node, no source, no node_modules
COPY --from=build /app/dist /usr/share/nginx/html
# Unprivileged Nginx listens on 8080 (not 80)
EXPOSE 8080
# Healthcheck with busybox wget (present in alpine nginx image)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q --spider http://127.0.0.1:8080/ || exit 1
```

```nginx
# nginx.conf (conf.d/default.conf) for the SPA; not tested with nginx -t locally
server {
    # Unprivileged port
    listen 8080;
    # Static root
    root /usr/share/nginx/html;
    # Default document
    index index.html;
    # Hide the Nginx version
    server_tokens off;
    # Basic security headers
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    # Hashed asset files can be cached for a long time
    location /assets/ {
        add_header Cache-Control "public, max-age=31536000, immutable";
    }
    # SPA fallback: unknown paths return index.html for client-side routing
    location / {
        try_files $uri /index.html;
    }
}
```

```yaml
# .github/workflows/ci.yml: lint + build + scan before push (action versions are examples)
name: image-ci
# Run for every pull request
on: [pull_request]
jobs:
  build:
    # GitHub hosted runner
    runs-on: ubuntu-latest
    steps:
      # Fetch code
      - uses: actions/checkout@v4
      # Lint the Dockerfile
      - uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: Dockerfile
      # Enable BuildKit features via buildx
      - uses: docker/setup-buildx-action@v3
      # Build without pushing; cache layers in GitHub's cache service
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: false
          load: true
          tags: web:ci
          cache-from: type=gha
          cache-to: type=gha,mode=max
      # Scan the image for known vulnerabilities; fail on HIGH/CRITICAL
      - uses: aquasecurity/trivy-action@0.28.0
        with:
          image-ref: web:ci
          severity: HIGH,CRITICAL
          exit-code: "1"
```

---

## 🟠 My Stack Integration
- **Node.js API**: `node:20-alpine` or `-slim`, `npm ci --omit=dev`, `USER node`, exec-form CMD, handle `SIGTERM` for graceful shutdown (so `docker stop` is fast).
- **FastAPI**: `python:3.12-slim`, `pip install --no-cache-dir`, multi-stage with a venv or wheels if you need compilers, non-root user, uvicorn exec-form.
- **React**: always multi-stage (Node build -> Nginx runtime).
- **Nginx**: `nginx-unprivileged`, config in the image or mounted read-only.
- **VPS**: smaller images mean faster `docker compose pull`; always tag releases (`api:1.4.2`) so you can roll back.
- **AWS**: ECR scan on push + lifecycle policy to delete old images; use image digests in ECS task definitions.
- **GitHub Actions**: BuildKit layer cache (`type=gha`), lint, scan, push with immutable tags.

Alpine uses musl libc: native Node modules (bcrypt, sharp) or some Python wheels may need extra care; if you hit problems, switch to `-slim` (Debian).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `FROM node:latest` or untagged.
✅ Correct: Pin a version (`node:20-alpine`) and ideally a digest for critical images; update on a schedule (Dependabot/Renovate).

❌ Mistake 2: `COPY . .` before installing dependencies.
✅ Correct: `COPY package*.json` -> install -> `COPY . .`.

❌ Mistake 3: Secrets in `ENV`, `ARG`, or copied `.env`.
✅ Correct: BuildKit `--mount=type=secret` for build; runtime secrets via env at run, Docker secrets, or AWS Secrets Manager.

❌ Mistake 4: `apt-get update` and `apt-get install` in separate `RUN` lines, or not cleaning lists.
✅ Correct: `RUN apt-get update && apt-get install -y --no-install-recommends pkg && rm -rf /var/lib/apt/lists/*`.

❌ Mistake 5: Shell-form `CMD npm start`, so SIGTERM goes to `sh`, the app gets killed after 10 s timeout.
✅ Correct: `CMD ["node","server.js"]` (also avoid npm as PID 1).

❌ Mistake 6: One container running Nginx + Node + cron via supervisor.
✅ Correct: One concern per container; Compose wires them together.

---

## 🧠 Tricky Interview Question
Two Dockerfiles install the same packages. In A, `RUN apt-get install -y curl` then a later `RUN rm -rf /var/lib/apt/lists/*`. In B, both are in one `RUN`. Which gives a smaller image and why?

Answer: B. Each `RUN` creates an immutable layer. Files deleted in a later layer still exist in the earlier layer, so the final image size still includes them (they are only hidden). Cleaning must happen in the same layer that created the files. The same logic applies to downloading a tarball and deleting it, which is why multi-stage builds are even better: build files never reach the final stage.

---

## ⚫ Interview Questions + Answers

Q1: Why multi-stage builds?
A1: Compilers, dev dependencies and source stay in earlier stages; the final image holds only runtime artifacts, so it is smaller and has a smaller attack surface.

Q2: Alpine vs slim?
A2: Alpine is smallest (musl libc, busybox), but compatibility issues can appear with native modules and DNS edge cases. Slim (Debian) is a bit bigger and more compatible. Distroless is smaller still with no shell.

Q3: Why exec form for CMD?
A3: No intermediate shell, so signals (SIGTERM) reach the app directly for graceful shutdown; also no shell parsing surprises.

Q4: `COPY` vs `ADD`?
A4: Prefer `COPY` (explicit). `ADD` also fetches URLs and auto-extracts local tar files, which can surprise you; use it only for those features.

Q5: How do you keep builds reproducible?
A5: Pin base tags (or digests), use lock files with `npm ci` / pinned `requirements.txt`, avoid `latest`, and avoid fetching unpinned scripts in `RUN`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every production Dockerfile; make hadolint + Trivy part of CI.

❌ Avoid when (relax a rule consciously):
- Local throwaway dev images, where speed of writing matters more than size.
- Alpine, if native dependencies fight musl; use slim.
- Over-optimising a tiny internal tool image where the effort exceeds the benefit.

---

## 📊 Visual Diagram

```
  Stage "deps"        Stage "build"            Stage "runtime" (shipped)
 +-------------+     +----------------+       +---------------------------+
 | package*.json|--->| node_modules   |       | nginx-unprivileged        |
 | npm ci       |    | source code    |       |  + /usr/share/nginx/html  |
 | (cached)     |    | npm run build  |--dist-->  (static files only)      |
 +-------------+     +----------------+       |  USER 101, HEALTHCHECK    |
   discarded            discarded             +---------------------------+
                                                 ~25-50 MB, few CVEs
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Multi-stage build | Several FROM stages, ship the last | कई FROM stages, आखिरी भेजो |
| Pinning | Fixing exact version | exact version तय करना |
| Layer | Immutable filesystem step | image का स्थायी step |
| Distroless | Image with no OS tools | बिना OS tools की image |
| hadolint | Dockerfile linter | Dockerfile की जाँच करने वाला tool |
| Trivy | Vulnerability scanner | vulnerability scanner |

---

## ⚡ 3-Line Summary
English: Pin small base images, use multi-stage builds and cache-friendly layer order, and run as non-root with exec-form commands. Keep secrets out, add healthchecks, and lint and scan in CI.
Hindi: छोटे pinned base images, multi-stage builds और cache-friendly layer order use करो, और non-root व exec-form commands से चलाओ। Secrets बाहर रखो, healthcheck जोड़ो और CI में lint व scan करो।

---

## ➡️ Next Topic
**090. Layer Caching: How it Works**: many best practices depend on cache. Next we learn exactly how Docker decides to reuse or rebuild a layer.
