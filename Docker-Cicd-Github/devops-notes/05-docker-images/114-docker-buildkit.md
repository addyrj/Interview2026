# 114. Docker BuildKit
# हिंदी में: Docker BuildKit

---

## 🔵 Simple Definition (English)
**BuildKit** is Docker's modern build engine. It builds independent stages in parallel, skips unused stages, transfers only needed context files, and adds features such as cache mounts, secret mounts, SSH mounts, multi-platform builds and remote cache export. It is the default builder in current Docker Engine (23.0+) and Docker Desktop.

## 🔵 सरल परिभाषा (Hindi)
**BuildKit** Docker का आधुनिक build engine है। यह independent stages को parallel build करता है, unused stages छोड़ देता है, सिर्फ ज़रूरी context files भेजता है, और cache mounts, secret mounts, SSH mounts, multi-platform builds और remote cache export जैसे features जोड़ता है। यह मौजूदा Docker Engine (23.0+) और Docker Desktop में default builder है।

---

## 🔴 Problem it Solves
- The legacy builder ran steps strictly one after another and uploaded the whole context.
- No safe way to use secrets during build; people leaked tokens in layers.
- `apt`/`npm`/`pip` downloads repeated on every cache miss.
- No proper multi-architecture or CI cache story.

## 🔴 यह क्यों बना? (Hindi)
- पुराना builder steps को एक के बाद एक चलाता था और पूरा context upload करता था।
- Build में secrets इस्तेमाल करने का सुरक्षित तरीका नहीं था; लोग tokens layers में leak कर देते थे।
- Cache miss पर `apt`/`npm`/`pip` downloads हर बार दोहराए जाते थे।
- Multi-architecture और CI cache की सही व्यवस्था नहीं थी।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Dockerfile is parsed into a dependency graph (LLB) instead of a linear list
Step 2 → Independent stages run in parallel; unused stages are skipped
Step 3 → Only changed/needed context files are transferred
Step 4 → Special mounts (cache, secret, ssh, bind) are attached to a single RUN
Step 5 → Results exported: load into local Docker, push to registry, or export cache
Step 6 → Use `docker buildx` for extra drivers (docker-container) and multi-platform
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Dockerfile linear list की जगह dependency graph (LLB) में बदलती है
Step 2 → Independent stages parallel चलते हैं; unused stages skip होते हैं
Step 3 → सिर्फ बदली/ज़रूरी context files transfer होती हैं
Step 4 → एक RUN के साथ special mounts (cache, secret, ssh, bind) जुड़ते हैं
Step 5 → नतीजा export: local Docker में load, registry में push, या cache export
Step 6 → अतिरिक्त drivers (docker-container) और multi-platform के लिए `docker buildx` इस्तेमाल करो
```

---

## 🟡 Real World Example
A CI pipeline for a FastAPI + React repo has two Dockerfile stages: `frontend-build` and `backend-deps`. With the legacy builder they ran serially (6 min). With BuildKit they run in parallel and the total drops to about 3.5 min. The team also replaced a leaked `ARG GH_TOKEN` with `--mount=type=secret`, so their image no longer contains the token.

## 🟡 Real Example Hindi mein
FastAPI + React repo की CI pipeline में Dockerfile के दो stages हैं: `frontend-build` और `backend-deps`। पुराने builder में ये क्रम से चलते (6 मिनट)। BuildKit में parallel चलते हैं और कुल समय लगभग 3.5 मिनट रह जाता है। Team ने leak हो रहे `ARG GH_TOKEN` को `--mount=type=secret` से बदल दिया, अब image में token नहीं है।

---

## 💻 Code / Config Example — Basic
```bash
# Check which Docker version you have (BuildKit default from 23.0)
docker version --format '{{.Server.Version}}'
# Force BuildKit on older Docker engines for one command
DOCKER_BUILDKIT=1 docker build -t myorg/api:dev .
# Use the buildx front-end (always BuildKit)
docker buildx build -t myorg/api:dev --load .
# Show plain, full logs (good for debugging cache misses)
docker buildx build --progress=plain -t myorg/api:dev --load .
```

## 💻 Code / Config Example — Advanced
```dockerfile
# syntax=docker/dockerfile:1
# The syntax line above selects the BuildKit Dockerfile frontend (enables new features)
FROM python:3.12.7-slim-bookworm AS base
# Avoid .pyc files and buffer issues
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# Work dir
WORKDIR /app

# ---- independent stage: Python dependencies ----
FROM base AS deps
# Copy only requirements
COPY requirements.txt .
# Cache mount: pip's download cache survives between builds (not stored in the image)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# ---- independent stage: private package using a secret ----
FROM base AS private
# Secret is mounted at /run/secrets/pip_conf only during this RUN
RUN --mount=type=secret,id=pip_conf,target=/etc/pip.conf \
    pip download --no-deps --dest /wheels some-private-package==1.0.0

# ---- final stage ----
FROM base AS runtime
# Pull installed packages from the deps stage
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
# Copy the app code with a bind mount-free simple COPY
COPY . .
# Start FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```
(Stage names and syntax verified by script; image not built locally. Because `private` is not referenced by `runtime`, BuildKit skips it entirely, which shows the unused-stage optimization.)

---

## 🟠 My Stack Integration
- Local: Docker Desktop already uses BuildKit; use `docker buildx build`.
- GitHub Actions: `docker/setup-buildx-action` creates a BuildKit builder, required for cache export (`type=gha` or `type=registry`).
- VPS: install the Docker Engine (23+) and buildx plugin if you must build there; better to pull prebuilt images.

```yaml
# GitHub Actions steps (snippet) - set up BuildKit builder
- uses: docker/setup-qemu-action@v3      # emulate other CPUs for multi-arch
- uses: docker/setup-buildx-action@v3    # create BuildKit builder
- uses: docker/build-push-action@v6
  with:
    context: .
    push: false          # build only; set true to push
    tags: myorg/api:ci
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `--mount=type=cache` and assuming the cache exists on a fresh CI runner.
✅ Correct: Cache mounts live on the builder; on ephemeral runners export/import cache (topic 116).

❌ Mistake 2: Forgetting `# syntax=docker/dockerfile:1` and then using newer features on old setups.
✅ Correct: Add the syntax directive at the very first line.

❌ Mistake 3: Using `docker build --secret` without `RUN --mount=type=secret`.
✅ Correct: Both sides are required.

❌ Mistake 4: Piping secrets through ARG/ENV.
✅ Correct: Use secret mounts or SSH mounts (`--mount=type=ssh`).

---

## 🧠 Tricky Interview Question
"Two stages in your Dockerfile are not needed by the final target. Does the legacy builder or BuildKit run them?"

Answer: The legacy builder executes every stage from top to bottom, wasting time. BuildKit builds only the stages the requested target depends on, and runs independent ones concurrently.

---

## ⚫ Interview Questions + Answers

Q1: What is BuildKit?
A1: Docker's modern, concurrent, cache-efficient build backend (default since Docker 23.0).

Q2: Name three BuildKit features.
A2: Parallel stages, cache mounts, secret mounts (also SSH mounts, multi-platform, cache export).

Q3: `docker build` vs `docker buildx build`?
A3: With BuildKit default they are close; buildx exposes extra options (`--platform`, `--cache-to`, other drivers).

Q4: How to enable BuildKit on old Docker?
A4: `DOCKER_BUILDKIT=1` or set `"features": {"buildkit": true}` in daemon.json.

Q5: Where is a secret mount stored?
A5: In a tmpfs-like mount only for that RUN; never in a layer.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Almost always: faster builds, safer secrets, multi-arch.

❌ Avoid when:
- Very old Docker (< 18.09) that cannot support it; upgrade instead.
- Tools that expect legacy build output (rare; mostly some old CI wrappers).

---

## 📊 Visual Diagram
```
 Legacy builder:  stage A ─► stage B ─► stage C ─► final      (serial)

 BuildKit graph:
        ┌─► stage frontend ─┐
 start ─┤                   ├─► final
        └─► stage deps ─────┘        (parallel)
        x   stage private (unused)   (skipped)

 RUN mounts:  [cache]  [secret]  [ssh]  [bind]  -> not saved in layers
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BuildKit | Modern build engine | आधुनिक build engine |
| buildx | CLI plugin for BuildKit | BuildKit का CLI |
| LLB | Internal build graph | internal build graph |
| Cache mount | Persistent cache dir | persistent cache folder |
| Secret mount | Temporary secret file | अस्थायी secret |
| Frontend | Dockerfile syntax parser | syntax parser |

---

## ⚡ 3-Line Summary
English: BuildKit builds faster with parallel stages and smarter caching.
It adds secret, SSH and cache mounts plus multi-platform builds.
It is the default in modern Docker; use buildx for advanced options.
Hindi: BuildKit parallel stages और smart caching से तेज़ build करता है।
इसमें secret, SSH, cache mounts और multi-platform builds हैं।
नए Docker में यह default है; advanced options के लिए buildx इस्तेमाल करो।

---

## ➡️ Next Topic
**115. BuildKit Cache** - cache mounts and layer cache in detail.
