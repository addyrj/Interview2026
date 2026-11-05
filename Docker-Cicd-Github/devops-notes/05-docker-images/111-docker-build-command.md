# 111. docker build Command
# हिंदी में: docker build Command

---

## 🔵 Simple Definition (English)
`docker build [OPTIONS] PATH` builds an image from a Dockerfile and a **build context** (the PATH). Key options: `-t` (tag), `-f` (Dockerfile path), `--build-arg`, `--target`, `--no-cache`, `--platform`, `--progress`.

## 🔵 सरल परिभाषा (Hindi)
`docker build [OPTIONS] PATH` एक Dockerfile और **build context** (PATH) से image बनाता है। मुख्य options: `-t` (tag), `-f` (Dockerfile का path), `--build-arg`, `--target`, `--no-cache`, `--platform`, `--progress`।

---

## 🔴 Problem it Solves
- One command gives a repeatable image for local, CI and servers.
- Options let you reuse one Dockerfile for dev/prod (`--target`), multiple CPU types (`--platform`) and different versions (`--build-arg`).
- Without knowing the flags, people rebuild everything (`--no-cache`) or forget tags and end up with `<none>` images.

## 🔴 यह क्यों बना? (Hindi)
- एक command local, CI और servers के लिए repeatable image देती है।
- Options से एक Dockerfile dev/prod (`--target`), अलग CPU types (`--platform`) और अलग versions (`--build-arg`) के लिए चलता है।
- Flags न जानने पर लोग सब कुछ rebuild करते हैं (`--no-cache`) या tag भूलकर `<none>` images बना लेते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → docker build -t myorg/api:1.0 .      ("." is the build context)
Step 2 → CLI packs the context (minus .dockerignore) and sends it to the builder
Step 3 → Builder reads ./Dockerfile (or the one from -f)
Step 4 → Runs stages; --target stops at a named stage
Step 5 → Tags the result (-t, can be repeated)
Step 6 → With BuildKit (default in modern Docker) output shows progress and cache hits
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → docker build -t myorg/api:1.0 .      ("." build context है)
Step 2 → CLI context को pack करता है (.dockerignore छोड़कर) और builder को भेजता है
Step 3 → Builder ./Dockerfile (या -f वाली) पढ़ता है
Step 4 → Stages चलाता है; --target नाम वाले stage पर रुक जाता है
Step 5 → नतीजे को tag करता है (-t, कई बार दे सकते हैं)
Step 6 → BuildKit (नए Docker में default) के साथ progress और cache hits दिखते हैं
```

---

## 🟡 Real World Example
A CI job builds FastAPI for both the amd64 EC2 server and a developer's Apple Silicon laptop. It uses `--platform linux/amd64` for production. For unit tests it runs `docker build --target test .` which stops at the `test` stage and never produces the heavy production layers.

## 🟡 Real Example Hindi mein
एक CI job FastAPI को amd64 EC2 server और developer के Apple Silicon laptop दोनों के लिए build करता है। Production के लिए `--platform linux/amd64`। Unit tests के लिए `docker build --target test .` चलता है जो `test` stage पर रुक जाता है और भारी production layers नहीं बनाता।

---

## 💻 Code / Config Example — Basic
```bash
# Build with a tag; "." = current folder is the context
docker build -t myorg/api:1.0.0 .
# Use a Dockerfile with a different name/location, context stays "."
docker build -f docker/Dockerfile.prod -t myorg/api:prod .
# Multiple tags on one build
docker build -t myorg/api:1.0.0 -t myorg/api:1.0 .
# Ignore cache (forces every step to run again)
docker build --no-cache -t myorg/api:1.0.0 .
# Always try to pull a newer base image before building
docker build --pull -t myorg/api:1.0.0 .
# Show full plain output (useful in CI logs)
docker build --progress=plain -t myorg/api:1.0.0 .
```

## 💻 Code / Config Example — Advanced
```bash
#!/usr/bin/env bash
# build.sh - production build script with safety flags
# Stop on error, unset variable, and pipe failures
set -euo pipefail

# Image name and version come from arguments with defaults
IMAGE="${1:-myorg/api}"
# Use short git SHA as the unique tag
SHA="$(git rev-parse --short HEAD)"

# Build for the server CPU type, stop at the "runtime" stage,
# pass version info as build args and add OCI labels for traceability
docker build \
  --platform linux/amd64 \
  --target runtime \
  --pull \
  --build-arg APP_VERSION="${SHA}" \
  --label org.opencontainers.image.revision="${SHA}" \
  --label org.opencontainers.image.source="https://github.com/myorg/myrepo" \
  -t "${IMAGE}:${SHA}" \
  -f Dockerfile \
  .

# Print the resulting image size and ID
docker image ls "${IMAGE}:${SHA}"
```
(`bash -n` syntax-checked, not executed; flags are standard `docker build` options.)

---

## 🟠 My Stack Integration
Dev laptop (Mac M-series) builds arm64 by default, but an AWS t3 EC2 or typical VPS is amd64. If you build locally and push, add `--platform linux/amd64` or use buildx in CI to avoid the "exec format error" on the server.

```yaml
# docker-compose.yml - same flags expressed in Compose
services:
  api:
    build:
      # Context folder sent to the builder
      context: ./api
      # Specific Dockerfile inside the context
      dockerfile: Dockerfile
      # Build only up to this stage
      target: runtime
      # Build-time variable
      args:
        APP_VERSION: ${TAG:-dev}
    # Platform for the VPS
    platform: linux/amd64
    image: myorg/api:${TAG:-dev}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting the `.` (PATH) at the end.
✅ Correct: `docker build -t name .` (error: requires 1 argument).

❌ Mistake 2: Using `--no-cache` on every build "to be safe".
✅ Correct: Trust the cache; use `--no-cache` or `--pull` only for scheduled security rebuilds.

❌ Mistake 3: Building on an M-series Mac and running on amd64 without `--platform`.
✅ Correct: Specify `--platform linux/amd64` or use multi-arch buildx.

❌ Mistake 4: No tag, leaving `<none>:<none>` images.
✅ Correct: Always pass `-t`.

---

## 🧠 Tricky Interview Question
"You edit the Dockerfile in `docker/Dockerfile.prod` and run `docker build -f docker/Dockerfile.prod -t app docker/`. `COPY package.json .` now fails. Why?"

Answer: The last argument is the build context, not the Dockerfile location. Context is now `docker/`, so `package.json` at repo root is outside it. Use context `.` with `-f docker/Dockerfile.prod`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `-f` and the PATH argument?
A1: `-f` picks the Dockerfile; PATH is the context of files available for COPY/ADD.

Q2: What does `--target` do?
A2: Builds only up to the named stage in a multi-stage Dockerfile.

Q3: `--no-cache` vs `--pull`?
A3: `--no-cache` ignores layer cache; `--pull` refreshes the base image, while still using cache for unchanged steps.

Q4: How to build for another CPU architecture?
A4: `--platform linux/arm64` (needs QEMU/buildx for cross-building), or `docker buildx build --platform linux/amd64,linux/arm64`.

Q5: What is `docker buildx build`?
A5: The BuildKit-based CLI plugin with extra features such as multi-platform, cache export and bake.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Local development and simple CI builds.

❌ Avoid when:
- You need multi-arch pushes with remote caches: prefer `docker buildx build` or `build-push-action`.
- Building on the production server.

---

## 📊 Visual Diagram
```
 docker build  -t myorg/api:1.0  -f Dockerfile  --target runtime  .
        │            │              │                │            │
        │            │              │                │            └─ build context (files)
        │            │              │                └─ stop at stage
        │            │              └─ which Dockerfile
        │            └─ name:tag of result
        ▼
  CLI ──(tar of context)──► builder (BuildKit) ──► layers ──► image in local store
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| -t | Tag the image | image का नाम/tag |
| -f | Dockerfile path | Dockerfile का path |
| --target | Stop at a stage | किसी stage तक build |
| --platform | Target CPU/OS | target CPU |
| --pull | Refresh base | base दोबारा pull |
| --no-cache | Skip cache | cache छोड़ो |

---

## ⚡ 3-Line Summary
English: `docker build` turns Dockerfile plus context into a tagged image.
Know `-t`, `-f`, `--target`, `--build-arg`, `--platform`.
The final argument is the context, not the Dockerfile.
Hindi: `docker build` Dockerfile और context से tagged image बनाता है।
`-t`, `-f`, `--target`, `--build-arg`, `--platform` जानो।
आखिरी argument context है, Dockerfile नहीं।

---

## ➡️ Next Topic
**112. Build Context** - what exactly gets sent to the builder and how to keep it small.
