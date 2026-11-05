# 091. Optimizing Layer Cache
# हिंदी में: Layer Cache को Optimize करना

---

## 🔵 Simple Definition (English)
Optimizing the layer cache means **structuring your Dockerfile and CI so that the slowest steps are reused as often as possible**: stable instructions first, frequently changing files last, dependency manifests copied separately, cache mounts for package managers, and an external cache for CI.

## 🔵 सरल परिभाषा (Hindi)
Layer cache optimize करने का मतलब है **Dockerfile और CI को ऐसे बनाना कि सबसे धीमे steps ज़्यादा से ज़्यादा बार reuse हों**: स्थिर instructions पहले, बार-बार बदलने वाली files आखिर में, dependency manifests अलग copy करना, package managers के लिए cache mounts, और CI के लिए external cache।

---

## 🔴 Problem it Solves
Knowing how caching works (note 090) is not enough: real projects have monorepos, many stages, `npm ci` that still downloads 300 MB when it misses, and CI runners that start empty. Build times creep up to 8-10 minutes, developers stop waiting for CI, and deploy frequency drops. Optimization turns a 8-minute build into 30-60 seconds and cuts CI cost and the time-to-fix during an outage.

## 🔴 यह क्यों बना? (Hindi)
Caching कैसे काम करती है (note 090) यह जानना काफी नहीं: असली projects में monorepos, कई stages, `npm ci` जो miss पर भी 300 MB download करता है, और खाली शुरू होने वाले CI runners होते हैं। Build time 8-10 मिनट तक पहुँच जाता है, developers CI का इंतज़ार छोड़ देते हैं और deploy frequency घट जाती है। Optimization 8 मिनट के build को 30-60 सेकंड में बदल देती है और CI खर्च तथा outage के दौरान fix का समय घटाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Measure first: docker build --progress=plain . (see which steps take time)
Step 2 → Order: base -> OS packages -> manifests -> install -> source -> build -> metadata
Step 3 → Split stages: deps / build / runtime; stages reuse independently
Step 4 → .dockerignore: unchanged context for irrelevant edits
Step 5 → BuildKit cache mounts: RUN --mount=type=cache for npm/pip/apt downloads
Step 6 → Bind-mount manifests: RUN --mount=type=bind,source=package.json,target=package.json
         (avoids a separate COPY layer)
Step 7 → CI: cache-from/cache-to (type=gha or type=registry) so fresh runners reuse layers
Step 8 → Monorepo: copy only the needed package's files; per-service Dockerfile.dockerignore
Step 9 → Re-measure; keep a weekly --no-cache --pull job for security freshness
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → पहले नापो: docker build --progress=plain . (कौन-से steps समय लेते हैं)
Step 2 → क्रम: base -> OS packages -> manifests -> install -> source -> build -> metadata
Step 3 → Stages बाँटो: deps / build / runtime; stages अलग-अलग reuse होते हैं
Step 4 → .dockerignore: अप्रासंगिक edits पर context वही रहे
Step 5 → BuildKit cache mounts: npm/pip/apt downloads के लिए RUN --mount=type=cache
Step 6 → Manifests को bind-mount करो: RUN --mount=type=bind,source=package.json,target=package.json
         (अलग COPY layer की ज़रूरत नहीं)
Step 7 → CI: cache-from/cache-to (type=gha या type=registry) ताकि नए runners layers reuse करें
Step 8 → Monorepo: सिर्फ ज़रूरी package की files copy करो; हर service की Dockerfile.dockerignore
Step 9 → दोबारा नापो; security freshness के लिए साप्ताहिक --no-cache --pull job रखो
```

---

## 🟡 Real World Example
A company runs a monorepo with a React app, a Node.js API and a FastAPI service, all built on every pull request. Before optimization: 3 images x 6 minutes. They (1) split each Dockerfile into deps/build/runtime stages, (2) added `--mount=type=cache` for npm and pip, (3) added per-service ignore files so a change in the React app does not touch the API's context, and (4) enabled `type=gha` cache. Pull requests touching only the frontend now rebuild only the frontend image, in about 40 seconds, and the other two are fully cached. Monthly GitHub Actions minutes dropped by about 60%.

## 🟡 Real Example Hindi mein
एक कंपनी के monorepo में React app, Node.js API और FastAPI service हैं, जो हर pull request पर build होते हैं। Optimization से पहले: 3 images x 6 मिनट। उन्होंने (1) हर Dockerfile को deps/build/runtime stages में बाँटा, (2) npm और pip के लिए `--mount=type=cache` जोड़ा, (3) हर service के लिए अलग ignore files बनाईं ताकि React app का बदलाव API के context को न छुए, और (4) `type=gha` cache चालू किया। अब सिर्फ frontend बदलने वाले PR सिर्फ frontend image rebuild करते हैं, लगभग 40 सेकंड में, और बाकी दो पूरी तरह cached रहती हैं। GitHub Actions के मासिक minutes लगभग 60% घट गए।

---

## 💻 Code / Config Example — Basic

```dockerfile
# syntax=docker/dockerfile:1
# Basic optimisation: manifests first + BuildKit npm cache mount
# Base image (example tag)
FROM node:20-alpine
# Working directory
WORKDIR /app
# Copy manifests only (this layer changes only when dependencies change)
COPY package.json package-lock.json ./
# npm's download cache is kept on the builder between builds, even when this layer reruns
RUN --mount=type=cache,target=/root/.npm npm ci --omit=dev
# Copy source last
COPY . .
# Run unprivileged
USER node
# Start app
CMD ["node", "server.js"]
```

```bash
# Time a cold build
time docker build -t demo .
# Change one source file and time a warm build (should be seconds)
echo "// touch" >> server.js && time docker build -t demo .
# Inspect build cache usage on this machine (BuildKit)
docker buildx du
# Remove build cache older than 7 days (safe housekeeping on a VPS)
docker builder prune --filter "until=168h" -f
```

## 💻 Code / Config Example — Advanced

```dockerfile
# syntax=docker/dockerfile:1
# Advanced: monorepo service Dockerfile (Node API) with deps/build/runtime stages and bind-mounted manifests
# Node version in one place
ARG NODE_VERSION=20-alpine

# ---- Stage deps: production dependencies only (cache key = manifests) ----
FROM node:${NODE_VERSION} AS prod-deps
# Working directory
WORKDIR /app
# Bind-mount the manifests (no COPY layer) and use a cache mount for npm downloads
RUN --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=package-lock.json,target=package-lock.json \
    --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev

# ---- Stage build: all dependencies + compile ----
FROM node:${NODE_VERSION} AS build
# Working directory
WORKDIR /app
# Install everything (dev deps needed for the TypeScript compile)
RUN --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=package-lock.json,target=package-lock.json \
    --mount=type=cache,target=/root/.npm \
    npm ci
# Copy source and config (changes often)
COPY tsconfig.json ./
# Application source
COPY src ./src
# Compile TypeScript to dist/
RUN npm run build

# ---- Stage runtime: smallest, most stable layers first ----
FROM node:${NODE_VERSION} AS runtime
# Production mode
ENV NODE_ENV=production
# Working directory
WORKDIR /app
# Prod node_modules (rebuilt only when manifests change)
COPY --from=prod-deps /app/node_modules ./node_modules
# Manifest needed by the runtime (e.g., "type": "module" resolution)
COPY package.json ./
# Compiled output (changes with every code change, so it is nearly last)
COPY --from=build /app/dist ./dist
# Volatile metadata at the very end
ARG GIT_SHA=unknown
# Label with the commit
LABEL org.opencontainers.image.revision="${GIT_SHA}"
# Run unprivileged
USER node
# Start compiled app
CMD ["node", "dist/server.js"]
```

```gitignore
# services/api/Dockerfile.dockerignore (BuildKit: used automatically with services/api/Dockerfile)
# Ignore everything by default
*
# Allow only what the API build needs
!package.json
!package-lock.json
!tsconfig.json
!src/
# Junk inside allowed folders
**/*.test.ts
**/node_modules
```

```yaml
# .github/workflows/ci.yml: matrix build of three services with a per-service cache scope
name: ci
# Run on pull requests
on: [pull_request]
jobs:
  images:
    # GitHub hosted runner
    runs-on: ubuntu-latest
    # Build the three images in parallel
    strategy:
      matrix:
        # Service folder names in the monorepo (examples)
        service: [web, api, worker]
    steps:
      # Fetch code
      - uses: actions/checkout@v4
      # Buildx enables external cache (action versions are examples; update)
      - uses: docker/setup-buildx-action@v3
      # Build each service with its own cache scope so they do not evict each other
      - uses: docker/build-push-action@v6
        with:
          # Per-service build context
          context: services/${{ matrix.service }}
          push: false
          tags: ${{ matrix.service }}:ci
          # Reuse layers from previous runs for this service
          cache-from: type=gha,scope=${{ matrix.service }}
          # Save layers for the next run
          cache-to: type=gha,scope=${{ matrix.service }},mode=max
```

```yaml
# Alternative cache backend: registry cache (works across machines, e.g. CI + the VPS)
# Used inside docker/build-push-action "with:"
cache-from: type=registry,ref=ghcr.io/your-org/api:buildcache
cache-to: type=registry,ref=ghcr.io/your-org/api:buildcache,mode=max
```

---

## 🟠 My Stack Integration
- **Node.js**: bind-mounted manifests + npm cache mount + separate prod-deps and build stages (above).
- **FastAPI**: pip cache mount; if you compile wheels, build wheels in a `builder` stage (`pip wheel`) and install them in runtime with `--no-index --find-links`.
- **React/Nginx**: `deps` stage cached on `package-lock.json`; `build` stage only on source; Nginx final stage only copies `dist`.
- **GitHub Actions**: `type=gha` is easiest (cache limit per repository is 10 GB, old entries evicted); use `type=registry` for large images or sharing with the VPS.
- **VPS**: build in CI, push to GHCR/ECR, and `docker compose pull` on the VPS. If you must build on the VPS, schedule `docker builder prune --filter until=...` in cron to avoid a full disk.
- **AWS**: ECR can store a registry cache (use `image-manifest=true,oci-mediatypes=true` options with `type=registry` when pushing cache to ECR; check the current Buildx/ECR documentation as this is version-dependent).
- **Security**: cache mounts are not part of the final image, so tokens used via `--mount=type=secret` do not enter layers; do not store secrets in cache mounts.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Optimising without measuring.
✅ Correct: Use `--progress=plain` and look at step timings (or `docker buildx build --progress=plain`) first.

❌ Mistake 2: Using `cache-to: type=gha` without `cache-from`.
✅ Correct: Always set both.

❌ Mistake 3: Using one cache scope for all services, so they evict each other (GHA cache is limited).
✅ Correct: `scope=` per service.

❌ Mistake 4: Copying a whole monorepo into every image build.
✅ Correct: Per-service context plus `Dockerfile.dockerignore` allow-list.

❌ Mistake 5: Using `docker system prune -a` on the production VPS to "free space" and deleting images needed for rollback.
✅ Correct: Prune build cache only (`docker builder prune`) and keep the last N tags.

❌ Mistake 6: Assuming a cache mount's content ships in the image.
✅ Correct: It does not. The installed files must end up in the layer via the command's output (e.g., `node_modules`).

---

## 🧠 Tricky Interview Question
You added `RUN --mount=type=cache,target=/root/.npm npm ci`. A colleague says "now the layer is always cached, we don't need to order COPY commands carefully". Is he right?

Answer: No. A cache **mount** is a separate mechanism from the **layer** cache. If the layer's inputs change (manifests, or any earlier layer), the `RUN` still executes; the cache mount only makes that execution faster by keeping npm's download cache (no re-download). Layer ordering still decides whether the command runs at all. Also, the cache mount contents live on the builder, so on ephemeral CI runners they are lost unless exported (the `type=gha` cache stores layers, not mount caches; mount caches need extra tooling). Use both techniques together.

---

## ⚫ Interview Questions + Answers

Q1: Layer cache vs cache mount?
A1: Layer cache reuses whole step results. A cache mount keeps a directory (like `~/.npm`) between builds so a re-executed step is faster. Mount contents are not in the image.

Q2: How do you reuse cache on ephemeral CI runners?
A2: Buildx `--cache-from/--cache-to` with `type=gha`, `type=registry`, `type=local`, or `type=s3` (backends vary by version).

Q3: What does `mode=max` do?
A3: Exports cache for all layers, including intermediate stages of multi-stage builds. The default `min` exports only the final image's layers.

Q4: Why split a Dockerfile into stages for caching?
A4: Each stage's layers are cached independently, and BuildKit can skip stages the final target does not need and build independent stages in parallel.

Q5: How do you debug why the cache missed?
A5: `docker build --progress=plain`, compare `COPY` inputs (use `.dockerignore`), check ARG values and the instruction text, and confirm the builder instance/cache backend are the same as before.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Builds take more than a minute or run on every PR.
- Monorepos or several services built in CI.
- Bandwidth to package registries is slow or rate-limited.

❌ Avoid / be careful when:
- A tiny project, since complexity costs more than it saves.
- You need guaranteed-fresh packages (use scheduled `--no-cache --pull`).
- Shared caches could be poisoned: restrict who can write the cache (only trusted branches, not forks).

---

## 📊 Visual Diagram

```
  PR #1 (cold)                       PR #2 (frontend only)
  +----------------+                 +----------------+
  | web   6 min    | --cache-to-->   | web   40 s     |  reuse deps layers
  | api   6 min    |   (GHA /        | api   cached   |  <- no change: 5 s
  | worker 6 min   |    registry)    | worker cached  |  <- no change: 5 s
  +----------------+                 +----------------+

  Inside one image:
   [base][OS pkgs][manifests][npm ci (cache mount)] [src] [build] [LABEL sha]
   |<-------- stable: almost always CACHED ------->| |<- volatile: rebuilt ->|
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache mount | Persistent dir during RUN | RUN के दौरान स्थायी folder |
| Bind mount (build) | Temporarily map a file into RUN | RUN में file को अस्थायी जोड़ना |
| cache-from / cache-to | Import / export build cache | cache लाना / भेजना |
| `type=gha` | GitHub Actions cache backend | GitHub Actions का cache backend |
| `mode=max` | Export all stages' layers | सभी stages की layers export |
| Scope | Name to separate caches | caches अलग रखने का नाम |

---

## ⚡ 3-Line Summary
English: Order layers from stable to volatile, split stages, and use cache mounts so even a miss is fast. On CI, export and import cache with Buildx (`gha` or registry) using one scope per service. Measure first, and still rebuild periodically for security patches.
Hindi: Layers को स्थिर से बदलने वाले क्रम में रखो, stages बाँटो और cache mounts use करो ताकि miss भी तेज़ हो। CI में Buildx (`gha` या registry) से हर service के लिए एक scope के साथ cache export/import करो। पहले नापो, और security patches के लिए समय-समय पर rebuild भी करो।

---

## ➡️ Next Topic
**092. Multi-stage Builds** (next in the Dockerfile series): the stage-splitting used here gets its full treatment, with patterns for Node.js, FastAPI and React.
