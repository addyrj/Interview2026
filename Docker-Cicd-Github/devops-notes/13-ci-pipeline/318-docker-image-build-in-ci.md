# 318. Docker Image Build in CI
# हिंदी में: CI में Docker Image Build करना

---

## 🔵 Simple Definition (English)
Building a Docker image in CI means the pipeline runs `docker build` (usually through Buildx and `docker/build-push-action`) on every change, using layer caching, producing a tagged image. On pull requests you only build (to prove the Dockerfile works); on main you also push to a registry.

## 🔵 सरल परिभाषा (Hindi)
CI में Docker image build करने का मतलब है कि pipeline हर बदलाव पर (आमतौर पर Buildx और `docker/build-push-action` से) layer caching के साथ `docker build` चलाती है और tag वाली image बनाती है। Pull request पर सिर्फ़ build होता है (Dockerfile सही है यह साबित करने के लिए); main पर registry में push भी होता है।

---

## 🔴 Problem it Solves
Building images by hand on a laptop or VPS is inconsistent, slow, and unreviewed. A Dockerfile typo may only be found at deploy time. CI builds the image from a clean checkout every time, tags it with the commit SHA, and keeps a traceable artifact that exactly matches the tested code.

## 🔴 यह क्यों बना? (Hindi)
Laptop या VPS पर हाथ से image बनाना असंगत, धीमा और बिना review का होता है। Dockerfile की typo deploy के समय पकड़ी जा सकती है। CI हर बार साफ़ checkout से image बनाता है, commit SHA से tag करता है और ऐसा traceable artifact रखता है जो tested code से बिल्कुल मेल खाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → actions/checkout gets code (Dockerfile + context)
Step 2 → docker/setup-buildx-action creates a BuildKit builder
Step 3 → docker/metadata-action computes tags/labels (sha, branch, semver)
Step 4 → (main only) docker/login-action authenticates to GHCR / ECR / Docker Hub
Step 5 → build-push-action builds layers; cache-from/to reuses unchanged layers
Step 6 → PR: push=false (or load=true for later scan); main: push=true
Step 7 → Image digest (sha256:...) is output for deploy and scanning
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → actions/checkout code लाता है (Dockerfile + context)
Step 2 → docker/setup-buildx-action एक BuildKit builder बनाता है
Step 3 → docker/metadata-action tags/labels तय करता है (sha, branch, semver)
Step 4 → (सिर्फ़ main) docker/login-action GHCR / ECR / Docker Hub में login करता है
Step 5 → build-push-action layers बनाता है; cache-from/to बिना बदली layers दोबारा इस्तेमाल करता है
Step 6 → PR: push=false (या बाद के scan के लिए load=true); main: push=true
Step 7 → Image digest (sha256:...) deploy और scan के लिए output मिलता है
```

---

## 🟡 Real World Example
Your Node.js API image takes 4 minutes to build from scratch. With `cache-from: type=gha` and a Dockerfile that copies `package*.json` before the source, a code-only change rebuilds in 40 seconds because the `npm ci` layer is reused. The main-branch build pushes `ghcr.io/you/api:3f2a9c1` and your VPS pulls exactly that tag.

## 🟡 Real Example Hindi mein
आपकी Node.js API image शुरू से बनने में 4 मिनट लेती है। `cache-from: type=gha` और ऐसा Dockerfile जो source से पहले `package*.json` copy करे, इससे सिर्फ़ code बदलने पर 40 सेकंड में rebuild होता है क्योंकि `npm ci` layer दोबारा इस्तेमाल होती है। Main branch का build `ghcr.io/you/api:3f2a9c1` push करता है और आपका VPS ठीक वही tag pull करता है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/docker-build.yml  (basic: just prove the image builds)
name: Docker Build                     # Workflow name

on: [pull_request]                     # Build on every PR

jobs:
  build:
    runs-on: ubuntu-latest             # Runner with Docker preinstalled
    steps:
      - uses: actions/checkout@v4      # Get code and Dockerfile
      - name: Build image              # Plain docker build
        run: docker build -t myapi:ci ./backend   # -t names image, ./backend is the build context
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/docker-build.yml  (Buildx, cache, GHCR push on main, SHA tags)
name: Docker Build

on:
  pull_request:
    paths: ["backend/**", ".github/workflows/docker-build.yml"]   # Only when relevant
  push:
    branches: [main]

env:
  REGISTRY: ghcr.io                    # GitHub Container Registry
  IMAGE_NAME: ${{ github.repository }}/api    # owner/repo/api (must be lowercase)

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 25
    permissions:
      contents: read                   # Read code
      packages: write                  # Push to GHCR using GITHUB_TOKEN
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-qemu-action@v3         # Only needed for multi-arch builds
      - uses: docker/setup-buildx-action@v3       # Enables cache export and multi-platform
      - name: Log in to GHCR (not on PRs)
        if: github.event_name != 'pull_request'   # PRs from forks have no write token
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}           # User who triggered
          password: ${{ secrets.GITHUB_TOKEN }}   # Short-lived token, no PAT needed
      - name: Compute tags and labels
        id: meta                                   # Step id, used below
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          # tags: sha-3f2a9c1, main, and latest (latest only on the default branch)
          tags: |
            type=sha,format=short
            type=ref,event=branch
            type=raw,value=latest,enable={{is_default_branch}}
      - name: Build and (maybe) push
        id: build
        uses: docker/build-push-action@v6
        with:
          context: ./backend                       # Build context folder
          file: ./backend/Dockerfile               # Dockerfile path
          platforms: linux/amd64                   # Your VPS/EC2 architecture (add arm64 for Graviton)
          push: ${{ github.event_name != 'pull_request' }}   # Push only outside PRs
          load: ${{ github.event_name == 'pull_request' }}   # Keep image locally on PRs for scanning
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha                     # Pull layer cache from GitHub cache
          cache-to: type=gha,mode=max              # Save all layers to cache
          # build-args are visible in image history: never put secrets here
          build-args: |
            NODE_ENV=production
      - name: Show digest
        if: github.event_name != 'pull_request'
        run: echo "Pushed digest ${{ steps.build.outputs.digest }}"   # Use digest for pinned deploys
```

A cache-friendly multi-stage Dockerfile that the workflow builds (`backend/Dockerfile`):
```dockerfile
# backend/Dockerfile : multi-stage build for a Node.js API
# Stage 1: install dependencies only
FROM node:20-alpine AS deps
# Working directory inside the image
WORKDIR /app
# Copy manifests first so this layer is cached until dependencies change
COPY package.json package-lock.json ./
# Production dependencies only
RUN npm ci --omit=dev

# Stage 2: small runtime image
FROM node:20-alpine AS runtime
# Production mode
ENV NODE_ENV=production
# Working directory
WORKDIR /app
# Bring dependencies from stage 1
COPY --from=deps /app/node_modules ./node_modules
# App source (respect .dockerignore)
COPY . .
# Run as the non-root user that ships with the node image
USER node
# Documentation of the port
EXPOSE 3000
# Start command (exec form, receives signals correctly)
CMD ["node", "src/server.js"]
```

---

## 🟠 My Stack Integration
- **Node.js:** Build as above; `.dockerignore` must exclude `node_modules`, `.git`, `.env`, `coverage`.
- **FastAPI:** Same pattern with `python:3.12-slim`, `pip install --no-cache-dir -r requirements.txt` before copying source; run with `uvicorn`.
- **React:** Multi-stage: build with Node, serve `dist/` with `nginx:alpine`.
- **VPS:** Deploy job SSHes in and runs `docker compose pull && docker compose up -d` with `image: ghcr.io/you/repo/api:sha-xxxx`.
- **AWS:** Swap login to `aws-actions/amazon-ecr-login@v2` with OIDC role (`aws-actions/configure-aws-credentials`) and push to ECR.
- **Secrets:** Never pass secrets as `build-args` (they stay in image history). Use BuildKit `secrets:` if needed at build time.

```yaml
# docker-compose.yml fragment on the VPS using the CI-built tag
services:
  api:
    image: ghcr.io/youruser/yourrepo/api:sha-3f2a9c1   # Immutable tag produced by CI
    restart: unless-stopped                            # Auto restart on crash/reboot
    env_file: .env                                     # Secrets live on the server only
    ports:
      - "127.0.0.1:3000:3000"                          # Bind to localhost; Nginx proxies
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `COPY . .` before `npm ci`, so every code change invalidates the dependency layer.
✅ Correct: Copy manifests, install, then copy source.

❌ Mistake 2: Pushing images on every PR (including forks).
✅ Correct: `push: false` on PRs; push on main/tags only.

❌ Mistake 3: Using only `latest`, so rollbacks are impossible.
✅ Correct: Tag with commit SHA (immutable) plus optional `latest`.

❌ Mistake 4: Passing secrets with `--build-arg` or `ENV`.
✅ Correct: Runtime env on the server, or BuildKit secret mounts.

❌ Mistake 5: Uppercase letters in the GHCR image name, causing "invalid reference format".
✅ Correct: Lowercase `owner/repo`.

---

## 🧠 Tricky Interview Question
Your CI build is fast locally but takes 6 minutes in CI every time, even for a README change. Why?

Answer: GitHub runners are fresh VMs with no Docker layer cache. Without `cache-from/cache-to` (GHA cache or a registry cache) every layer rebuilds. Fix with Buildx plus `type=gha,mode=max` (or `type=registry`), order Dockerfile layers from least to most frequently changing, add `paths` filters so docs-only changes skip the build, and use a `.dockerignore` so irrelevant files do not bust the `COPY` layer.

---

## ⚫ Interview Questions + Answers

Q1: What does `docker/build-push-action` add over `docker build`?
A1: Buildx/BuildKit features: cache import/export, multi-platform builds, secrets, provenance, outputs like digest, all in one declarative step.

Q2: `load` vs `push`?
A2: `push` sends the image to a registry; `load` loads it into the runner's local Docker daemon so later steps (Trivy, tests) can use it. Multi-platform images cannot be loaded.

Q3: Why tag with the commit SHA?
A3: It uniquely ties the image to code, gives easy rollback, and avoids mutable-tag surprises.

Q4: How does GITHUB_TOKEN push to GHCR?
A4: Grant `packages: write` permission and log in with `${{ secrets.GITHUB_TOKEN }}`; the repo must be linked to the package.

Q5: How to keep image small and safe?
A5: Multi-stage builds, slim/alpine bases, non-root user, `--omit=dev`, `.dockerignore`, pinned base image versions or digests.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You deploy containers (VPS compose, ECS, Kubernetes).
- You want reproducible, traceable artifacts.
- You want Dockerfile errors caught in PRs.

❌ Avoid when:
- App deploys as a plain static bundle (S3/CloudFront).
- Docs-only changes (use `paths` filters).
- Pushing from untrusted fork PRs.

---

## 📊 Visual Diagram
```
  git push ──▶ Runner
                 │
   checkout ──▶ buildx ──▶ metadata (tags: sha, main, latest)
                 │
                 ▼
      build-push-action ◀──── cache (GHA / registry)
                 │
        ┌────────┴──────────┐
     PR │                   │ main
        ▼                   ▼
   load locally          push to GHCR/ECR
   (scan: topic 319)           │
                               ▼
                    VPS: docker compose pull && up -d
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Buildx / BuildKit | Modern Docker build engine | आधुनिक Docker build engine |
| Layer cache | Reuse of unchanged build steps | बिना बदले build steps का दोबारा उपयोग |
| Registry | Server storing images (GHCR, ECR) | images रखने वाला server |
| Digest | Content hash identifying an image | image की content hash पहचान |
| Build context | Files sent to the builder | builder को भेजी जाने वाली files |
| Multi-stage | Several FROM stages, small final image | कई FROM stages, छोटी final image |

---

## ⚡ 3-Line Summary
English: CI builds the image from a clean checkout with Buildx, caching and SHA tags.
English: PRs only build (and scan); main pushes to GHCR/ECR for the VPS to pull.
English: Order Dockerfile layers well, never bake secrets, use least-privilege permissions.
Hindi: CI साफ़ checkout से Buildx, caching और SHA tags के साथ image बनाता है।
Hindi: PR पर सिर्फ़ build (और scan); main registry पर push करता है जहाँ से VPS pull करता है।
Hindi: Dockerfile layers सही क्रम में रखें, secrets कभी bake न करें, कम से कम permissions दें।

Note: Dockerfile checked only for valid instruction structure; the image was NOT built (no Docker daemon here). Action versions are examples.

---

## ➡️ Next Topic
319. Docker Image Scan (Trivy): the image exists; now we scan it for OS and library vulnerabilities before pushing.
