# 72. FROM Instruction
# हिंदी में: FROM Instruction (Base image चुनना)

---

## 🔵 Simple Definition (English)
`FROM` sets the base image on which the new image is built and starts a new build stage. It must be the first instruction (only `ARG` and comments may come before it). Syntax: `FROM [--platform=<p>] <image>[:tag|@digest] [AS <name>]`.

## 🔵 सरल परिभाषा (Hindi)
`FROM` वह base image तय करता है जिसके ऊपर नई image बनती है और नया build stage शुरू करता है। यह पहली instruction होनी चाहिए (इससे पहले सिर्फ `ARG` और comments आ सकते हैं)। Syntax: `FROM [--platform=<p>] <image>[:tag|@digest] [AS <name>]`।

---

## 🔴 Problem it Solves
Without a base you would have to build an OS userland, libc and a runtime from nothing. `FROM` lets you start from a maintained image (Node, Python, Alpine, Debian slim, distroless) with security patches. The wrong choice causes huge images, CVEs, glibc/musl incompatibilities, or builds that silently change when a tag moves.

## 🔴 यह क्यों बना? (Hindi)
Base के बिना आपको OS userland, libc और runtime शून्य से बनाना पड़ता। `FROM` से आप security patches वाली maintained image (Node, Python, Alpine, Debian slim, distroless) से शुरू करते हो। गलत चुनाव से image बहुत बड़ी, CVEs वाली, glibc/musl की incompatibility, या tag बदलने पर चुपचाप बदलने वाले builds मिलते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Builder reads FROM and resolves the reference (registry, repo, tag/digest)
Step 2 → Pulls the base image layers (cached if already local)
Step 3 → New stage starts with that filesystem as its starting point
Step 4 → Following instructions add layers on top
Step 5 → With "AS name", later stages can COPY --from=name
Step 6 → "FROM scratch" starts empty (for static binaries like Go)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Builder FROM पढ़कर reference resolve करता है (registry, repo, tag/digest)
Step 2 → Base image की layers pull करता है (local हों तो cache से)
Step 3 → नया stage उसी filesystem से शुरू होता है
Step 4 → आगे की instructions उसके ऊपर layers जोड़ती हैं
Step 5 → "AS name" से बाद के stages COPY --from=name कर सकते हैं
Step 6 → "FROM scratch" खाली शुरुआत है (Go जैसे static binaries के लिए)
```

---

## 🟡 Real World Example
A startup used `FROM node:latest` for its API. One day `latest` jumped from Node 20 to a newer major; a native module failed to compile and the Friday deploy broke. They switched to `FROM node:20.18-alpine3.20` (example), later to a digest pin, with Dependabot/Renovate raising PRs for updates, so upgrades became deliberate PRs rather than surprises. Image size also fell from 1.1 GB to about 180 MB.

## 🟡 Real Example Hindi mein
एक startup अपने API के लिए `FROM node:latest` इस्तेमाल करती थी। एक दिन `latest` Node 20 से नए major पर चला गया; native module compile नहीं हुआ और शुक्रवार का deploy टूट गया। उन्होंने `FROM node:20.18-alpine3.20` (example) पर pin किया, बाद में digest पर, और Dependabot/Renovate update के PR बनाते हैं, यानी upgrades अब सोच-समझकर होते हैं। Image size 1.1 GB से घटकर करीब 180 MB हो गई।

---

## 💻 Code / Config Example — Basic
```dockerfile
# Dockerfile -- basic FROM usage (example tags; check Docker Hub for current ones)
# official Node 20 on Alpine Linux, small footprint
FROM node:20-alpine
# create and enter /app
WORKDIR /app
# copy source into the image
COPY . .
# default command
CMD ["node", "index.js"]
```

## 💻 Code / Config Example — Advanced
```dockerfile
# Dockerfile -- ARG before FROM, multi-stage, digest pin, platform, scratch/distroless
# ARG allowed before FROM: used only in FROM lines
ARG NODE_VERSION=20.18
# optional digest, empty by default (fill when pinning)
ARG BASE_DIGEST=

# build on the runner's native arch
FROM --platform=$BUILDPLATFORM node:${NODE_VERSION}-alpine AS deps
# working directory of stage "deps"
WORKDIR /app
# manifests only
COPY package*.json ./
# install all deps (including dev) for building
RUN npm ci

# new stage based on previous stage "deps"
FROM deps AS build
# add source
COPY . .
# produce /app/dist
RUN npm run build

# separate stage for production-only modules
FROM node:${NODE_VERSION}-alpine AS prod-deps
# working dir
WORKDIR /app
# manifests
COPY package*.json ./
# only runtime dependencies
RUN npm ci --omit=dev

# tiny runtime without shell (example image)
FROM gcr.io/distroless/nodejs20-debian12 AS runtime
# app dir
WORKDIR /app
# runtime deps from stage prod-deps
COPY --from=prod-deps /app/node_modules ./node_modules
# compiled output from stage build
COPY --from=build /app/dist ./dist
# distroless provides a non-root user
USER nonroot
# distroless node image uses node as entrypoint
CMD ["dist/server.js"]
```
Stage names (`deps`, `build`, `prod-deps`) were checked by script; image not built locally. Distroless tag/user names are version-dependent: verify on the project page.

---

## 🟠 My Stack Integration
Choose base per service. Pin versions in one place with `ARG` so CI can override.

```yaml
# docker-compose.yml -- pass base image versions as build args
services:                               # services
  node-api:                             # Node.js API
    build:                              # build section
      context: ./node-api               # folder with Dockerfile
      args:                             # values for ARG in Dockerfile
        NODE_VERSION: "20.18"           # pins Node version (example)
  fastapi:                              # Python service
    build:                              # build section
      context: ./fastapi                # folder
      args:                             # ARG values
        PY_VERSION: "3.12"              # used as FROM python:${PY_VERSION}-slim
  react:                                # React build + nginx
    build: ./react                      # Dockerfile: FROM node AS build, then FROM nginx:1.27-alpine
```
Guideline: Node/React build stage: `node:*-alpine`; FastAPI: `python:*-slim` (Alpine often slows pip wheels because of musl); final React stage: `nginx:*-alpine`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `FROM ubuntu` or `FROM node` (implicit `latest`).
✅ Correct: Pin a version tag, ideally plus digest for production.

❌ Mistake 2: Using full `node:20` (about 1 GB) for the final image.
✅ Correct: `-slim`/`-alpine` or distroless for runtime, full image only in build stage.

❌ Mistake 3: Alpine for Python projects with compiled wheels, getting slow builds and musl bugs.
✅ Correct: `python:3.12-slim` (Debian, glibc).

❌ Mistake 4: Building an `amd64` VPS image on Apple Silicon without noticing, getting "exec format error".
✅ Correct: `docker buildx build --platform linux/amd64` or set `FROM --platform=linux/amd64`.

---

## 🧠 Tricky Interview Question
Why can you write `ARG VERSION=20` before `FROM` and use it there, but not use it later in the stage without re-declaring?

Answer: An `ARG` declared before the first `FROM` lives outside any build stage and is only available to `FROM` lines. After `FROM`, the stage scope starts empty; to use the value inside the stage you must redeclare `ARG VERSION` (without default, it inherits the global default).

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a tag and a digest in FROM?
A1: A tag can be moved by the publisher. A digest (`image@sha256:...`) is an immutable content hash, so the build is reproducible.

Q2: What is `FROM scratch`?
A2: An empty base image, used for statically linked binaries (Go, Rust). No shell, no libc.

Q3: Alpine vs slim vs distroless?
A3: Alpine: tiny, musl libc, has shell/apk. Slim: Debian-based, trimmed, glibc, widely compatible. Distroless: only runtime, no shell/package manager, smallest attack surface, harder to debug.

Q4: Can a Dockerfile have multiple FROM?
A4: Yes; each starts a new stage. Only the last stage (or `--target`) becomes the final image.

Q5: How to keep base images up to date?
A5: Pin, then use Dependabot/Renovate plus scheduled rebuilds and image scanning (Trivy) in GitHub Actions.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every Dockerfile (it is mandatory).
- Multi-stage builds: one `FROM` per stage.
- Platform-specific builds with `--platform`.

❌ Avoid when:
- Using untrusted or unmaintained public base images.
- Using floating tags such as `latest` in production.
- Picking a heavy OS image when a slim variant works.

---

## 📊 Visual Diagram
```
  FROM node:20 AS build           FROM nginx:1.27-alpine AS runtime
  +---------------------+         +---------------------------+
  | node + npm + source |  COPY   | nginx + /usr/share/nginx/ |
  | npm run build       | ------> |   html (static files)     |
  | (1 GB, discarded)   | --from  | (~50 MB, shipped)         |
  +---------------------+         +---------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Base image | Starting filesystem of new image | नई image की शुरुआती filesystem |
| Stage | One FROM section | एक FROM वाला हिस्सा |
| Digest | sha256 of the image manifest | Image manifest का hash |
| scratch | Empty image | खाली image |
| Distroless | Runtime-only image | सिर्फ runtime वाली image |
| musl / glibc | C libraries (Alpine / Debian) | C libraries |

---

## ⚡ 3-Line Summary
English: `FROM` selects the base image and starts a build stage. Pin tags or digests, prefer slim/alpine/distroless for runtime, and use multi-stage builds. Mutable tags break reproducibility.
Hindi: `FROM` base image चुनता है और build stage शुरू करता है। Tags या digests pin करो, runtime के लिए slim/alpine/distroless लो, multi-stage इस्तेमाल करो। Mutable tags reproducibility तोड़ते हैं।

---

## ➡️ Next Topic
**73. RUN Instruction** — base चुनने के बाद build के समय commands चलाना और layers को छोटा रखना।
