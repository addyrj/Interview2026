# 336. Build Docker Image (in CI/CD)
# हिंदी में: CI/CD में Docker Image Build करना

---

## 🔵 Simple Definition (English)
Building a Docker image in a pipeline means GitHub Actions runs `docker build` (usually through **Buildx**) on every push, producing a versioned, immutable image from your `Dockerfile`. The same image is later pushed to a registry and deployed, so "what you tested is what you ship".

## 🔵 सरल परिभाषा (Hindi)
Pipeline में Docker image build करने का मतलब है कि हर push पर GitHub Actions आपके `Dockerfile` से `docker build` (आमतौर पर **Buildx** से) चलाता है और एक versioned, immutable image बनाता है। यही image बाद में registry में push होकर deploy होती है, यानी जो test हुआ वही ship होता है।

---

## 🔴 Problem it Solves
Before CI builds, developers built images on their laptops: different Docker versions, stale `node_modules`, uncommitted files, and "works on my machine" images pushed by hand. Nobody knew which commit an image came from, and builds were slow because there was no shared cache.

## 🔴 यह क्यों बना? (Hindi)
पहले developers अपने laptop पर image बनाते थे: अलग Docker versions, पुराना `node_modules`, uncommitted files और हाथ से push की गई images। किसी को पता नहीं होता था कि image किस commit से बनी है, और shared cache न होने से build धीमा था। CI build से हर image एक commit SHA से जुड़ी, repeatable और cached होती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Push / PR triggers the workflow on a fresh ubuntu runner
Step 2 → actions/checkout pulls the source at the exact commit
Step 3 → docker/setup-buildx-action sets up the BuildKit builder
Step 4 → docker/metadata-action computes tags (sha, branch, semver)
Step 5 → docker/build-push-action runs docker build with GHA cache
Step 6 → push: false on PRs (build only), push: true on main (next topic)
Step 7 → Image is scanned (Trivy) and smoke-tested before it is trusted
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Push / PR से workflow एक नए ubuntu runner पर चलता है।
Step 2 → `actions/checkout` ठीक उसी commit का source लाता है।
Step 3 → `setup-buildx-action` BuildKit builder तैयार करता है।
Step 4 → `metadata-action` tags (sha, branch, semver) निकालता है।
Step 5 → `build-push-action` GitHub Actions cache के साथ build करता है।
Step 6 → PR पर `push: false` (सिर्फ build), main पर `push: true` (अगला topic)।
Step 7 → Image पर Trivy scan और smoke test चलता है, तभी उस पर भरोसा किया जाता है।

---

## 🟡 Real World Example
A Swiggy-style team has a Node.js API. Each PR must prove the image builds, so `docker build` runs on every PR but nothing is pushed. A broken `COPY` path or a missing `npm ci` lockfile fails the PR in 2 minutes instead of failing at 2 AM during deploy. On merge to `main`, the same job tags the image `sha-3f9a1c2` and hands it to the push step.

## 🟡 Real Example Hindi mein
Swiggy जैसी team का Node.js API है। हर PR को साबित करना होता है कि image build होती है, इसलिए हर PR पर `docker build` चलता है पर push नहीं होता। गलत `COPY` path या missing lockfile PR में 2 मिनट में fail हो जाता है, रात 2 बजे deploy में नहीं। `main` पर merge होने पर वही job image को `sha-3f9a1c2` tag देता है और push step को सौंप देता है।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/build.yml  (basic: build only, no push)
name: build-image                      # name shown in the Actions tab
on:                                    # events that start the workflow
  pull_request:                        # run on every pull request
jobs:
  build:                               # job id
    runs-on: ubuntu-latest             # GitHub-hosted Linux runner
    steps:
      - uses: actions/checkout@v4      # fetch the repository code
      - name: Build image              # plain docker build, no cache tricks
        run: docker build -t myapp:ci .   # build and tag as myapp:ci
      - name: Smoke test               # prove the container starts
        run: |                         # multi-line shell script
          docker run -d --name t -p 3000:3000 myapp:ci   # start container
          sleep 5                                         # give app time to boot
          curl -fsS http://localhost:3000/health          # fail if not 200
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/build-advanced.yml (Buildx + cache + metadata + Trivy)
name: build-image-advanced             # workflow name
on:
  push:
    branches: [main]                   # build on main
    tags: ["v*.*.*"]                   # and on release tags
  pull_request:                        # and on PRs (build only)
permissions:
  contents: read                       # least privilege for GITHUB_TOKEN
concurrency:
  group: build-${{ github.ref }}       # one build per branch/PR
  cancel-in-progress: true             # cancel older runs of the same ref
env:
  IMAGE: myorg/api                     # image name used in tags
jobs:
  build:
    runs-on: ubuntu-latest             # runner
    timeout-minutes: 20                # kill hung builds
    steps:
      - uses: actions/checkout@v4      # get source
      - uses: docker/setup-qemu-action@v3      # emulation for arm64 builds
      - uses: docker/setup-buildx-action@v3    # BuildKit builder
      - name: Compute tags and labels
        id: meta                       # referenced below as steps.meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.IMAGE }}     # base image name
          tags: |                      # tag rules
            type=sha,format=short      # sha-3f9a1c2
            type=ref,event=branch      # main
            type=semver,pattern={{version}}   # 1.4.2 from tag v1.4.2
      - name: Build (no push) and load locally
        uses: docker/build-push-action@v6
        with:
          context: .                   # build context = repo root
          file: ./Dockerfile           # Dockerfile path
          push: false                  # do not push yet
          load: true                   # load into local docker for tests
          tags: ${{ env.IMAGE }}:scan  # local-only tag for scanning
          cache-from: type=gha         # read GitHub Actions cache
          cache-to: type=gha,mode=max  # write all layers to cache
          build-args: |                # pass build metadata
            GIT_SHA=${{ github.sha }}
      - name: Trivy vulnerability scan
        uses: aquasecurity/trivy-action@0.28.0   # example version, update
        with:
          image-ref: ${{ env.IMAGE }}:scan  # image to scan
          severity: CRITICAL,HIGH      # only report serious findings
          exit-code: "1"               # fail the job if any found
          ignore-unfixed: true         # skip CVEs with no fix yet
```

---

## 🟠 My Stack Integration
For Node.js / FastAPI / React you want a **multi-stage Dockerfile** so CI produces a small runtime image. Nginx serves the React build; the VPS later pulls the exact tag.

```dockerfile
# Dockerfile (Node.js API, multi-stage, example tags - update regularly)
# stage 1: install dependencies
FROM node:20-alpine AS deps
# working directory
WORKDIR /app
# copy only manifests for cache hits
COPY package*.json ./
# exact, lockfile-based install
RUN npm ci

# stage 2: compile TypeScript
FROM node:20-alpine AS build
WORKDIR /app
# reuse deps
COPY --from=deps /app/node_modules ./node_modules
# copy source
COPY . .
# produce /app/dist
RUN npm run build

# stage 3: small runtime image
FROM node:20-alpine AS runtime
# production mode
ENV NODE_ENV=production
WORKDIR /app
COPY package*.json ./
# prod deps only
RUN npm ci --omit=dev && npm cache clean --force
# compiled output only
COPY --from=build /app/dist ./dist
# never run as root
USER node
# documentation of port
EXPOSE 3000
# start command
CMD ["node", "dist/main.js"]
```

For FastAPI use `python:3.12-slim` with `pip install --no-cache-dir -r requirements.txt`; for React use a `node` build stage plus `nginx:alpine` runtime copying `/app/dist` to `/usr/share/nginx/html`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No `.dockerignore`, so `node_modules`, `.git` and `.env` are sent to the build context (slow, and secrets may leak into layers).
✅ Correct: Add `.dockerignore` with `node_modules`, `.git`, `.env*`, `dist`.

❌ Mistake 2: `COPY . .` before `npm ci`, so every code change busts the dependency cache.
✅ Correct: Copy `package*.json`, install, then copy source.

❌ Mistake 3: Tagging only `latest`, so you cannot tell or roll back versions.
✅ Correct: Tag with commit SHA (and semver for releases).

❌ Mistake 4: Passing secrets via `ARG`/`ENV` (they stay in image history).
✅ Correct: Use BuildKit `--mount=type=secret` for build-time secrets.

---

## 🧠 Tricky Interview Question
Your build takes 9 minutes on CI but 40 seconds locally. Why, and how do you fix it?

Answer: GitHub-hosted runners are **ephemeral**, so the local Docker layer cache does not exist. Fix: use Buildx with `cache-from/cache-to type=gha` (or a registry cache `type=registry`), order Dockerfile layers from least to most frequently changed, and add `.dockerignore`. Also check that `mode=max` is used so intermediate stages of a multi-stage build are cached, not just the final one.

---

## ⚫ Interview Questions + Answers

Q1: Why use Buildx instead of plain `docker build`?
A1: Buildx uses BuildKit: parallel stages, cache export/import, multi-platform builds (amd64/arm64), build secrets and provenance/SBOM attestations.

Q2: Why not push from pull requests?
A2: PRs from forks have no access to secrets, and pushing untrusted code to your registry is a supply-chain risk. Build only, push on `main`.

Q3: What does `cache-to: type=gha,mode=max` do?
A3: It exports all layers, including those of intermediate stages, to the GitHub Actions cache, so later runs reuse them. `mode=min` stores only final-image layers.

Q4: Why tag by commit SHA?
A4: SHA tags are immutable and traceable; you can map any running container back to a commit and roll back precisely. `latest` is a moving pointer.

Q5: How do you keep the image small and safe?
A5: Multi-stage build, slim/alpine base, non-root `USER`, only prod dependencies, pinned base tags (or digests), and a Trivy scan that fails on HIGH/CRITICAL.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You deploy containers anywhere (VPS, ECS, Kubernetes).
- You want repeatable builds and PR-time validation.
- Several developers or services share the pipeline.

❌ Avoid when:
- You deploy a static site to Vercel/Netlify (they build for you).
- Pure Lambda zip deployments with no container image.
- Very large monorepos without path filters (build only what changed).

---

## 📊 Visual Diagram
```
 git push / PR
      │
      ▼
┌────────────────────── GitHub Actions runner ──────────────────────┐
│ checkout ─► setup-buildx ─► metadata (tags) ─► build-push-action  │
│                                   │                  │            │
│                                   ▼                  ▼            │
│                          GHA cache (read/write)   local image     │
│                                                       │           │
│                                      Trivy scan ◄─────┘           │
└───────────────────────────────┬───────────────────────────────────┘
                                │ pass
                                ▼
                    push to registry (next topics)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Buildx | Docker CLI plugin using BuildKit | BuildKit वाला advanced build tool |
| Layer cache | Reused unchanged build steps | पुराने steps दोबारा न चलाना |
| Multi-stage | Several FROM stages, copy only the result | कई stages, सिर्फ result रखना |
| Tag | Human label for an image version | image version का नाम |
| Digest | Immutable sha256 identity of image | image की पक्की पहचान |
| SBOM | List of packages inside an image | image के अंदर packages की सूची |

---

## ⚡ 3-Line Summary
English: CI builds the image from a commit with Buildx and a layer cache. PRs only build and scan; main also pushes. Tag by SHA, keep it small, run non-root.
Hindi: CI commit से Buildx और cache के साथ image बनाता है। PR पर सिर्फ build और scan, main पर push भी। SHA से tag करो, image छोटी रखो, non-root चलाओ।

---

## ➡️ Next Topic
**337. Push to Docker Hub** - the built image must be stored in a registry before any server can pull it.
