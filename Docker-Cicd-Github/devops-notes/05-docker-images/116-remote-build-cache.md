# 116. Remote Build Cache
# हिंदी में: Remote Build Cache

---

## 🔵 Simple Definition (English)
A **remote build cache** stores BuildKit cache outside the builder machine (in a registry, GitHub Actions cache, S3, or a local directory) using `--cache-to` and `--cache-from`. Fresh CI runners can then reuse layers from earlier builds instead of starting from zero.

## 🔵 सरल परिभाषा (Hindi)
**Remote build cache** BuildKit cache को builder machine के बाहर (registry, GitHub Actions cache, S3 या local directory में) `--cache-to` और `--cache-from` से रखता है। इससे नए CI runners शुरू से build करने की जगह पुराने builds की layers reuse कर सकते हैं।

---

## 🔴 Problem it Solves
- GitHub-hosted runners are destroyed after every job: every CI build is a cold build.
- Several developers/servers build the same layers independently.
- Long CI times (10-15 minutes) slow down releases and consume paid minutes.

## 🔴 यह क्यों बना? (Hindi)
- GitHub-hosted runners हर job के बाद नष्ट हो जाते हैं: हर CI build cold build होता है।
- कई developers/servers वही layers अलग-अलग बनाते हैं।
- लंबा CI समय (10-15 मिनट) releases धीमे करता है और paid minutes खर्च करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Use a BuildKit builder with the docker-container driver (docker buildx create --use)
Step 2 → Build with --cache-from type=...  (import cache if available)
Step 3 → Build with --cache-to type=...,mode=max  (export cache after build)
Step 4 → mode=max also exports intermediate stage layers; mode=min only the final image layers
Step 5 → Next run on any machine imports the cache and shows CACHED for unchanged steps
Step 6 → Backends: registry, gha (GitHub Actions), local, s3, azblob
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → docker-container driver वाला BuildKit builder इस्तेमाल करो (docker buildx create --use)
Step 2 → --cache-from type=... से build (cache हो तो import)
Step 3 → --cache-to type=...,mode=max से build (build के बाद cache export)
Step 4 → mode=max intermediate stage layers भी export करता है; mode=min सिर्फ final image की layers
Step 5 → अगली बार किसी भी machine पर cache import होता है और unchanged steps CACHED दिखते हैं
Step 6 → Backends: registry, gha (GitHub Actions), local, s3, azblob
```

---

## 🟡 Real World Example
A team's GitHub Actions build of a FastAPI + ML dependencies image took 11 minutes every push because pip installed large wheels. After adding `cache-from: type=gha` and `cache-to: type=gha,mode=max`, pushes that do not touch `requirements.txt` take about 90 seconds. For their self-hosted ARM runner they used `type=registry` with a `:buildcache` tag in ECR so multiple runners share the same cache.

## 🟡 Real Example Hindi mein
एक team की FastAPI + ML dependencies image का GitHub Actions build हर push पर 11 मिनट लेता था क्योंकि pip बड़े wheels install करता था। `cache-from: type=gha` और `cache-to: type=gha,mode=max` जोड़ने के बाद जिन pushes में `requirements.txt` नहीं बदलती वे लगभग 90 सेकंड में हो जाते हैं। Self-hosted ARM runner के लिए उन्होंने ECR में `:buildcache` tag वाला `type=registry` इस्तेमाल किया ताकि कई runners एक ही cache share करें।

---

## 💻 Code / Config Example — Basic
```bash
# Create a builder that supports cache export (docker-container driver)
docker buildx create --name cachebuilder --driver docker-container --use
# Build and export cache to a local folder, import from it next time
docker buildx build \
  --cache-from type=local,src=/tmp/buildcache \
  --cache-to type=local,dest=/tmp/buildcache,mode=max \
  -t myorg/api:dev --load .
# Same idea with a registry tag as the cache store (needs login first)
docker buildx build \
  --cache-from type=registry,ref=myorg/api:buildcache \
  --cache-to type=registry,ref=myorg/api:buildcache,mode=max \
  -t myorg/api:dev --push .
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/ci-build.yml - GHA cache with a registry fallback
name: ci-build
on:
  push:
    branches: [main]
  pull_request:
jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      # Read repository
      contents: read
      # Push image and cache to GHCR
      packages: write
    steps:
      # Get the code
      - uses: actions/checkout@v4
      # Create the BuildKit builder (required for cache export)
      - uses: docker/setup-buildx-action@v3
      # Log in to GHCR (not on forks' PRs, which have no write token)
      - uses: docker/login-action@v3
        if: github.event_name != 'pull_request'
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      # Build with layered cache sources
      - uses: docker/build-push-action@v6
        with:
          context: .
          # Push only from main, not from pull requests
          push: ${{ github.event_name != 'pull_request' }}
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          # Import: GitHub cache first, registry cache as backup
          cache-from: |
            type=gha,scope=api
            type=registry,ref=ghcr.io/${{ github.repository }}:buildcache
          # Export: GitHub cache with all stages (mode=max)
          cache-to: type=gha,scope=api,mode=max
```
(Not run locally; action versions and the GHA cache backend are examples to verify against current docs. GHA cache has a size limit per repository, currently 10 GB.)

---

## 🟠 My Stack Integration
- **GitHub Actions + GHCR/ECR**: `type=gha` for speed, `type=registry` for sharing between runners and developers.
- **AWS ECR**: ECR supports cache manifests; use `image-manifest=true,oci-mediatypes=true` options with registry cache.
- **VPS builder**: a long-lived buildx builder keeps a local cache; no remote cache needed.

```yaml
# Registry cache exporting to ECR (options are version-dependent)
cache-to: type=registry,ref=123456789012.dkr.ecr.ap-south-1.amazonaws.com/api:buildcache,mode=max,image-manifest=true,oci-mediatypes=true
cache-from: type=registry,ref=123456789012.dkr.ecr.ap-south-1.amazonaws.com/api:buildcache
```
(ECR account ID and region above are placeholders.)

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `--cache-to` with the default `docker` driver.
✅ Correct: Create a `docker-container` builder (setup-buildx-action does this).

❌ Mistake 2: Exporting with default `mode=min` and wondering why builder stages are not cached.
✅ Correct: Use `mode=max` for multi-stage builds.

❌ Mistake 3: Allowing untrusted PRs to write to a shared registry cache.
✅ Correct: Export cache only from trusted branches (cache poisoning risk).

❌ Mistake 4: Putting secrets into cached layers.
✅ Correct: Use secret mounts; caches are readable by whoever can read the cache store.

---

## 🧠 Tricky Interview Question
"You enabled `cache-from type=gha` but every build still reruns `npm ci`. The Dockerfile is the same. What could be wrong?"

Answer: Likely causes: (1) no `cache-to` was configured, so nothing was ever saved; (2) `mode=min` excluded the intermediate stage; (3) an early layer changes each time (`ARG BUILD_DATE`, `COPY . .` before `npm ci`); (4) different `scope` values between jobs; (5) the cache was evicted because the repo exceeded its cache limit. Check logs with `--progress=plain` for `importing cache manifest`.

---

## ⚫ Interview Questions + Answers

Q1: Why is remote cache needed in CI?
A1: Runners are ephemeral, so local cache disappears.

Q2: Name cache backends.
A2: inline, registry, local, gha, s3, azblob.

Q3: `inline` vs `registry` cache?
A3: Inline embeds cache info into the image itself (min mode only); registry stores it as a separate artifact and supports `mode=max`.

Q4: Is remote cache safe?
A4: Treat it as trusted input; restrict write access and exclude secrets.

Q5: Does it speed up the first build?
A5: No; only later builds benefit.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Ephemeral CI runners, multiple build machines, heavy dependency installs.

❌ Avoid when:
- A single persistent builder already holds the cache.
- Builds are tiny (cache transfer may cost more than building).

---

## 📊 Visual Diagram
```
 Run #1 (cold)                         Run #2 (new runner)
 runner ─ build ─► image               runner ─ import cache ─► build (CACHED steps) ─► image
         └ export cache ──┐                        ▲
                          ▼                        │
                 ┌─────────────────┐               │
                 │ cache store     │───────────────┘
                 │ (gha/registry)  │
                 └─────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| cache-from | Import cache | cache import |
| cache-to | Export cache | cache export |
| mode=max | Export all layers | सभी layers export |
| gha cache | GitHub Actions cache | GitHub का cache |
| Registry cache | Cache stored in registry | registry में cache |
| Ephemeral runner | Deleted after job | job के बाद नष्ट runner |

---

## ⚡ 3-Line Summary
English: Remote cache lets fresh CI runners reuse earlier layers.
Use `cache-from` and `cache-to` with `mode=max`.
Restrict who can write cache and never cache secrets.
Hindi: Remote cache नए CI runners को पुरानी layers reuse करने देता है।
`cache-from` और `cache-to` को `mode=max` के साथ इस्तेमाल करो।
कौन cache लिख सकता है सीमित करो और secrets कभी cache मत करो।

---

## ➡️ Next Topic
**117. docker image prune** - cleaning the images and cache your builds leave behind.
