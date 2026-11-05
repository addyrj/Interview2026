# 090. Layer Caching — How it Works
# हिंदी में: Layer Caching कैसे काम करती है

---

## 🔵 Simple Definition (English)
Every Dockerfile instruction creates a **layer**. Docker stores each layer in a cache. On the next build, if an instruction and its inputs are unchanged, Docker reuses the cached layer instead of running it again. The moment one layer changes, **all layers after it** are rebuilt.

## 🔵 सरल परिभाषा (Hindi)
Dockerfile की हर instruction एक **layer** बनाती है। Docker हर layer को cache में रखता है। अगली build में अगर instruction और उसके inputs नहीं बदले तो Docker उसे दोबारा चलाने की जगह cached layer reuse करता है। जैसे ही एक layer बदलती है, उसके **बाद की सभी layers** दोबारा बनती हैं।

---

## 🔴 Problem it Solves
Installing dependencies takes minutes. If every one-line code change re-ran `npm ci`, developers would wait on every build and CI minutes (and money) would be wasted. Caching makes rebuilds near-instant when only source code changes. But it only works if you understand the rules, because a badly ordered Dockerfile invalidates the cache constantly and gives you slow builds with no obvious reason.

## 🔴 यह क्यों बना? (Hindi)
Dependencies install होने में मिनट लगते हैं। अगर हर एक-line code change पर `npm ci` दोबारा चलता तो developers हर build पर इंतज़ार करते और CI minutes (और पैसे) बर्बाद होते। Caching से सिर्फ source बदलने पर rebuild लगभग तुरंत हो जाता है। लेकिन यह तभी काम करता है जब आप नियम समझें, क्योंकि गलत क्रम वाली Dockerfile cache को बार-बार invalid करती है और बिना साफ कारण के build धीमा हो जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Docker walks the Dockerfile top to bottom, one instruction at a time
Step 2 → For each instruction it asks: do I have a cached layer with the same parent
         layer AND the same instruction text (and same input files for COPY/ADD)?
Step 3 → YES -> "CACHED": reuse, skip execution
Step 4 → NO  -> run it, create a new layer
Step 5 → Once any step misses, every following step misses too (the parent changed)
Step 6 → RUN is compared by its TEXT only (not by what the command would download)
Step 7 → COPY/ADD are compared by a checksum of the copied files' content (not mtime)
```

What invalidates a layer:
- Instruction text changed (even a space or a different `ARG` value used by it).
- For `COPY`/`ADD`: file contents or metadata (like permissions) changed.
- The parent layer was rebuilt.
- Different `--build-arg` value used by that instruction.
- `--no-cache`, or `docker builder prune`/`docker system prune` removed it.

What does NOT invalidate it: a `RUN apt-get update` is cached forever by its text, even if upstream packages changed (stale packages!).

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Docker Dockerfile को ऊपर से नीचे, एक-एक instruction देखता है
Step 2 → हर instruction पर पूछता है: क्या ऐसी cached layer है जिसकी parent layer
         और instruction का text (और COPY/ADD के input files) वही हैं?
Step 3 → हाँ -> "CACHED": reuse, चलाना छोड़ो
Step 4 → नहीं -> चलाओ, नई layer बनाओ
Step 5 → एक step miss हुआ तो उसके बाद के सारे steps miss होते हैं (parent बदल गया)
Step 6 → RUN की तुलना सिर्फ उसके TEXT से होती है (command क्या download करता, उससे नहीं)
Step 7 → COPY/ADD की तुलना copy की गई files की content checksum से होती है (mtime से नहीं)
```

Layer कब invalid होती है:
- Instruction का text बदला (एक space या उसमें use हुई `ARG` की अलग value भी)।
- `COPY`/`ADD` में: files की content या metadata (जैसे permissions) बदली।
- Parent layer फिर से बनी।
- उस instruction में use हुई `--build-arg` की value अलग हो।
- `--no-cache`, या `docker builder prune`/`docker system prune` ने उसे हटा दिया।

कब invalid नहीं होती: `RUN apt-get update` अपने text की वजह से हमेशा cached रहता है, चाहे upstream packages बदल गए हों (पुराने packages!)।

---

## 🟡 Real World Example
A Node.js team's CI build takes 5 minutes for every commit. Their Dockerfile does `COPY . .` first and `RUN npm ci` second. Any change to any file (even a README typo) changes the `COPY . .` checksum, so `npm ci` reruns. After swapping the order to `COPY package*.json` -> `npm ci` -> `COPY . .`, typical commits only rebuild the last layer: 15 seconds. And a different incident: a team's image kept shipping an old OpenSSL because `RUN apt-get update && apt-get install -y openssl` stayed cached for months. They fixed it by adding a weekly scheduled rebuild with `--no-cache` and `--pull`.

## 🟡 Real Example Hindi mein
एक Node.js team का CI build हर commit पर 5 मिनट लेता है। उनकी Dockerfile पहले `COPY . .` और फिर `RUN npm ci` करती है। किसी भी file का बदलाव (README का typo भी) `COPY . .` का checksum बदल देता है, इसलिए `npm ci` दोबारा चलता है। क्रम बदलकर `COPY package*.json` -> `npm ci` -> `COPY . .` करने पर सामान्य commits सिर्फ आखिरी layer rebuild करते हैं: 15 सेकंड। एक और घटना: एक team की image महीनों तक पुराना OpenSSL भेजती रही क्योंकि `RUN apt-get update && apt-get install -y openssl` cached रहा। उन्होंने `--no-cache` और `--pull` वाला साप्ताहिक scheduled rebuild जोड़कर इसे ठीक किया।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Basic: BAD ORDER (any file change reruns npm ci)
# Base image (example tag)
FROM node:20-alpine
# Working directory
WORKDIR /app
# Copies everything first: any source edit changes this layer...
COPY . .
# ...so this slow step reruns on EVERY build
RUN npm ci
# Start the app
CMD ["node", "server.js"]
```

```dockerfile
# Basic: GOOD ORDER (dependencies cached until package files change)
# Base image (example tag)
FROM node:20-alpine
# Working directory
WORKDIR /app
# Layer 1: only the manifests (changes rarely)
COPY package.json package-lock.json ./
# Layer 2: slow install, cached while manifests are unchanged
RUN npm ci --omit=dev
# Layer 3: source code (changes constantly, so it is last)
COPY . .
# Start the app
CMD ["node", "server.js"]
```

```bash
# First build: every step runs
docker build -t demo .
# Edit server.js, rebuild: steps 1-2 print CACHED (BuildKit) / "Using cache" (classic)
docker build -t demo .
# Force a clean build (ignore cache) and re-pull the base image
docker build --no-cache --pull -t demo .
# Show the layers and their sizes
docker history demo
```

## 💻 Code / Config Example — Advanced

```dockerfile
# syntax=docker/dockerfile:1
# Advanced: cache-aware FastAPI build with mounts, ordering of volatile ARGs, and a cache-busting knob
# Python slim base (example tag)
FROM python:3.12-slim
# Python flags
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
# Working directory
WORKDIR /app
# OS packages: stable, so it sits near the top and stays cached
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*
# Only requirements first: reinstall happens only when this file changes
COPY requirements.txt .
# BuildKit cache mount: pip's download cache survives between builds even when this layer reruns
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
# Source code (frequent changes) comes after the slow layers
COPY app ./app
# VOLATILE values last so they do not bust the layers above
ARG GIT_SHA=unknown
# Label that changes on every commit (cheap layer, placed at the end)
LABEL org.opencontainers.image.revision="${GIT_SHA}"
# Optional cache-buster: change its value to force layers AFTER it to rebuild (e.g., weekly)
ARG CACHE_BUST=0
# Refresh OS security patches whenever CACHE_BUST changes (the ARG is used in the text)
RUN echo "cache bust: ${CACHE_BUST}" && apt-get update && apt-get -y upgrade \
    && rm -rf /var/lib/apt/lists/*
# Non-root user
USER 10001
# Start the API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# .github/workflows/build.yml: persistent layer cache across CI runs (runners are ephemeral!)
name: build
# Run on pushes to main
on:
  push:
    branches: [main]
  # Weekly rebuild to pick up OS security patches
  schedule:
    - cron: "0 3 * * 1"
jobs:
  image:
    # GitHub hosted runner (fresh VM each run, so no local cache without this setup)
    runs-on: ubuntu-latest
    steps:
      # Get code
      - uses: actions/checkout@v4
      # Buildx is required for external cache backends (version is an example)
      - uses: docker/setup-buildx-action@v3
      # Build with GitHub Actions cache; scheduled runs bust the patch layer
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: false
          tags: api:ci
          # Read previous layers from the GHA cache
          cache-from: type=gha
          # Write all layers (mode=max includes intermediate stages)
          cache-to: type=gha,mode=max
          # Pass the run number: a new value every run invalidates the upgrade layer (use a weekly value if you want less churn)
          build-args: |
            CACHE_BUST=${{ github.run_number }}
```

---

## 🟠 My Stack Integration
- **Node.js**: manifests -> `npm ci` -> source. Add `RUN --mount=type=cache,target=/root/.npm` to speed even cache misses.
- **FastAPI**: `requirements.txt` -> `pip install` -> source; pin versions so layers are deterministic.
- **React**: separate `deps` stage; `COPY --from=deps node_modules`; the build stage reruns only when source changes.
- **GitHub Actions**: runners are fresh VMs, so there is **no local cache** between runs. Use `cache-from/cache-to: type=gha` (or `type=registry` pointing at a cache tag in GHCR/ECR).
- **VPS**: if you build on the VPS, the cache lives in `/var/lib/docker`. Prune old cache carefully (`docker builder prune --filter until=168h`) to avoid disk-full outages. Prefer building in CI and pulling on the VPS.
- **Security**: cached layers can contain stale vulnerable packages. Rebuild with `--pull --no-cache` on a schedule, and let Dependabot/Renovate bump base images.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `COPY . .` before dependency install.
✅ Correct: Copy manifests first, install, then copy the rest.

❌ Mistake 2: Separate `RUN apt-get update` layer. It is cached by text and later `install` may use a stale index (fail with 404s).
✅ Correct: `RUN apt-get update && apt-get install -y ...` in one instruction.

❌ Mistake 3: Putting `ARG GIT_SHA` / timestamps at the top.
✅ Correct: Declare volatile ARGs at the bottom, just before they are used.

❌ Mistake 4: Assuming CI has a cache because your laptop does.
✅ Correct: Configure `type=gha` or registry cache in CI.

❌ Mistake 5: Relying on cache for security updates.
✅ Correct: Scheduled `--no-cache --pull` rebuilds.

---

## 🧠 Tricky Interview Question
You change only a comment in `server.js`. Docker still reruns `npm ci`. Another day, you change `package-lock.json` and Docker reuses the old `npm ci` result. Explain both, assuming no `--no-cache`.

Answer: (1) The first happens when `COPY . .` precedes `npm ci`: the comment edit changes the content checksum of the copied context, invalidating `COPY` and every layer after it, including `npm ci`. Fix by copying manifests first. (2) The second happens if the lock file is **not** among the files copied before `npm ci` (for example only `package.json` is copied first, or `package-lock.json` is excluded by `.dockerignore`). Then the `COPY` and `RUN` inputs are unchanged and the cached install is reused, with stale dependencies. Fix: copy both `package.json` and `package-lock.json` before install, and use `npm ci`.

---

## ⚫ Interview Questions + Answers

Q1: What is the cache key for a `RUN` layer?
A1: The parent layer plus the exact instruction text (and relevant ARG/ENV values). Docker does not look at what the command downloads.

Q2: What is the cache key for a `COPY` layer?
A2: The parent layer, the instruction, and a checksum of the file contents and metadata of the sources (modification time is ignored).

Q3: Why do later layers rebuild after one miss?
A3: Layers are chained: each layer's identity depends on its parent. A new parent means every child must be recomputed.

Q4: How do you bypass the cache?
A4: `docker build --no-cache`, change an ARG used in the layer, or `--pull` to also refresh the base image.

Q5: Why does CI rebuild everything each time?
A5: Ephemeral runners have an empty cache. Configure an external cache (`type=gha`, `type=registry`) in Buildx.

---

## 🔷 When to Use + When Not to Use
✅ Use caching when:
- Fast local and CI iteration. Always order layers deliberately.
- Dependency installs dominate build time.

❌ Bypass caching when:
- You need the latest security patches (scheduled `--no-cache --pull`).
- A command downloads mutable content (`apt-get update`, `curl latest`) and you suspect stale results.
- Debugging a mysterious build difference ("works on CI but not locally").

---

## 📊 Visual Diagram

```
 Build #1                         Build #2 (only app code changed)
 --------                         --------------------------------
 FROM node:20-alpine   [run]      FROM node:20-alpine   CACHED
 COPY package*.json    [run]      COPY package*.json    CACHED
 RUN npm ci            [run] 90s  RUN npm ci            CACHED   (0s)
 COPY . .              [run]      COPY . .              CHANGED -> run
 CMD ...               [run]      CMD ...               rebuilt (miss chain)
                                  ------------------------------------
        one miss  ==>  everything BELOW it reruns
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Layer | Result of one instruction | एक instruction का नतीजा |
| Cache hit | Layer reused | layer reuse हुई |
| Cache miss | Layer rebuilt | layer दोबारा बनी |
| Invalidation | Cache no longer valid | cache का अमान्य होना |
| `--no-cache` | Ignore cache | cache को अनदेखा करना |
| Cache mount | Persistent folder for tools | tools के लिए स्थायी cache folder |

---

## ⚡ 3-Line Summary
English: Each instruction is a layer, reused when its text and inputs are unchanged. One cache miss rebuilds everything after it, so put stable steps first and volatile ones last. CI needs an external cache, and scheduled no-cache builds protect against stale packages.
Hindi: हर instruction एक layer है, जो text और inputs न बदलने पर reuse होती है। एक cache miss उसके बाद सब कुछ rebuild करता है, इसलिए स्थिर steps पहले और बदलने वाले आखिर में रखो। CI को external cache चाहिए, और scheduled no-cache builds पुराने packages से बचाते हैं।

---

## ➡️ Next Topic
**091. Optimizing Layer Cache**: now that you know the rules, apply them with concrete techniques, such as cache mounts, stage splitting and registry cache.
