# 187. image vs build
# हिंदी में: `image` बनाम `build`

---

## 🔵 Simple Definition (English)
`image:` tells Compose to **pull** a ready-made image from a registry (Docker Hub, GHCR, AWS ECR). `build:` tells Compose to **build** an image from a Dockerfile on disk. You can use both: Compose builds from `build:` and tags the result with the `image:` name.

## 🔵 सरल परिभाषा (Hindi)
`image:` Compose को बताता है कि registry (Docker Hub, GHCR, AWS ECR) से बनी-बनाई image **pull** करो। `build:` बताता है कि disk पर रखी Dockerfile से image **build** करो। दोनों साथ भी चल सकते हैं: Compose `build:` से बनाता है और नतीजे को `image:` के नाम से tag कर देता है।

---

## 🔴 Problem it Solves
Developers need to build from source (their own Node.js/FastAPI code, changing every commit) but also use third-party images (postgres, redis, nginx) unchanged. Without a clear distinction you rebuild Postgres needlessly or, worse, deploy untagged local builds to production that nobody can reproduce. The pair `image`/`build` lets the same file describe "build locally in dev, pull the exact tested tag in prod".

## 🔴 यह क्यों बना? (Hindi)
Developers को अपना कोड (Node.js/FastAPI, हर commit पर बदलता) source से build करना होता है, पर third-party images (postgres, redis, nginx) जैसी हैं वैसी चाहिए। साफ फर्क न हो तो Postgres बेवजह rebuild होगा, या बदतर, बिना tag की local build production में चली जाएगी जिसे कोई दोबारा बना नहीं सकता। `image`/`build` की जोड़ी से एक ही file कहती है: "dev में local build, prod में पूरी तरह test किया गया exact tag pull करो।"

---

## 🟢 How it Works — Step by Step

```
Step 1 → Service has only `image:` → Compose pulls it if not present locally.
Step 2 → Service has only `build:` → Compose builds; image name is <project>-<service>.
Step 3 → Service has BOTH → Compose builds, then tags the image as `image:` value.
Step 4 → `docker compose build` builds only; `up --build` builds then runs.
Step 5 → `docker compose pull` pulls only services that have `image:`.
Step 6 → `docker compose push` pushes images to the registry named in `image:`.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → सिर्फ `image:` हो → local में न हो तो Compose pull करता है।
Step 2 → सिर्फ `build:` हो → Compose build करता है; image का नाम <project>-<service> होता है।
Step 3 → दोनों हों → Compose build करके नतीजे को `image:` के नाम से tag करता है।
Step 4 → `docker compose build` सिर्फ build करता है; `up --build` build करके चलाता है।
Step 5 → `docker compose pull` सिर्फ उन services को pull करता है जिनमें `image:` है।
Step 6 → `docker compose push` images को `image:` में दिए registry पर push करता है।
```

---

## 🟡 Real World Example
A SaaS team keeps `compose.yaml` with `build:` for api and web plus `image: ghcr.io/acme/api:${TAG}`. In GitHub Actions, `docker compose build && docker compose push` publishes images tagged with the git SHA. On the production VPS they use a second file that has only `image:` lines, so the server never needs the source code or Docker build tools, just `docker compose pull && docker compose up -d`.

## 🟡 Real Example Hindi mein
एक SaaS टीम की `compose.yaml` में api और web के लिए `build:` और साथ में `image: ghcr.io/acme/api:${TAG}` है। GitHub Actions में `docker compose build && docker compose push` git SHA tag वाली images publish करता है। Production VPS पर दूसरी file में सिर्फ `image:` lines हैं, इसलिए server को source code या build tools नहीं चाहिए, बस `docker compose pull && docker compose up -d`।

---

## 💻 Code / Config Example — Basic

```yaml
services:                        # containers
  db:                            # third-party service: pull only
    image: postgres:16-alpine    # example tag; pulled from Docker Hub
    environment:                 # required by image
      POSTGRES_PASSWORD: example # DEV ONLY
  api:                           # our own code: build
    build: ./api                 # short form: context folder with Dockerfile
    ports:                       # publish port
      - "3000:3000"              # host:container
```

## 💻 Code / Config Example — Advanced

```yaml
services:                                  # containers
  api:                                     # Node.js API
    image: ghcr.io/acme/api:${TAG:-dev}    # name used for tag/push; default "dev"
    pull_policy: build                     # always build instead of pull (Compose 2.x option)
    build:                                 # build instructions (long form)
      context: ./api                       # folder sent to the builder
      dockerfile: Dockerfile.prod          # Dockerfile name relative to context
      target: runtime                      # multi-stage target to stop at
      args:                                # build-time ARG values
        NODE_VERSION: "20"                 # example ARG, must exist in Dockerfile
        APP_VERSION: ${TAG:-dev}           # pass version into image
      cache_from:                          # reuse cache from registry
        - ghcr.io/acme/api:buildcache      # example cache image
      labels:                              # image metadata
        org.opencontainers.image.source: "https://github.com/acme/api"   # link to repo
      platforms:                           # multi-arch build targets
        - linux/amd64                      # normal VPS / EC2
        - linux/arm64                      # Graviton / Apple silicon
    restart: unless-stopped                # restart policy
  web:                                     # React app served by nginx
    image: ghcr.io/acme/web:${TAG:-dev}    # tag
    build:                                 # build
      context: ./web                       # folder
      args:                                # build args
        VITE_API_URL: https://api.example.com   # baked into the JS bundle at build time
  cache:                                   # third party, pull only
    image: redis:7-alpine                  # example tag
    pull_policy: if_not_present            # pull only when missing (default is missing)
```

Notes: `pull_policy` values include `always`, `never`, `missing`, `if_not_present`, `build` (version dependent, check your Compose version). `platforms:` multi-arch builds need buildx/QEMU; not built locally here.

---

## 🟠 My Stack Integration
Dev laptop: `build:`. VPS: `image:` from GHCR with the git SHA. Use two files: base `compose.yaml` (images) and `compose.build.yaml` (adds `build:` for CI/dev).

```yaml
# compose.yaml - what runs on the VPS (image only)
services:                                  # VPS services
  api:                                     # FastAPI
    image: ghcr.io/addyrj/fastapi-app:${TAG:?set TAG}   # must pass TAG, no accidental :latest
    restart: unless-stopped                # restart policy
  web:                                     # React behind nginx
    image: ghcr.io/addyrj/react-app:${TAG:?set TAG}     # same TAG for consistency
    restart: unless-stopped                # restart policy
# compose.build.yaml would add:  services: { api: { build: ./api }, web: { build: ./web } }
# CI:  docker compose -f compose.yaml -f compose.build.yaml build && ... push
# VPS: TAG=<sha> docker compose pull && TAG=<sha> docker compose up -d
```

Security: pin tags (or digests `image: nginx@sha256:...`), never use `latest` in prod, log in to the registry with a read-only token on the VPS, scan images (Trivy) in CI, and keep secrets out of `build.args` because they are stored in image history.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `latest` in production `image:`.
✅ Correct: Pin to a version or git SHA/digest.

❌ Mistake 2: Passing secrets via `build.args` (visible in `docker history`).
✅ Correct: Use BuildKit secrets or runtime env.

❌ Mistake 3: Editing code and running `docker compose up` expecting a rebuild.
✅ Correct: `docker compose up --build` or `docker compose build`.

❌ Mistake 4: Huge build context (node_modules, .git) making builds slow.
✅ Correct: Add `.dockerignore`.

❌ Mistake 5: Giving `build:` but no `image:`, then trying to `push`.
✅ Correct: Set `image:` with a registry path so push knows the destination.

---

## 🧠 Tricky Interview Question
"A service has both `build:` and `image: myrepo/api:1.0`. Compose is already showing a local image `myrepo/api:1.0` from last month. You run `docker compose up -d`. Does your new code run?"

Answer: Not necessarily. `up` reuses an existing image with that tag and only builds if the image is missing. The old image tagged `myrepo/api:1.0` exists, so Compose starts it. You need `--build`, or `docker compose build` first. In CI, also bump the tag per commit so stale tags cannot be reused.

---

## ⚫ Interview Questions + Answers

Q1: When both image and build exist, what happens?
A1: Compose builds from `build:` and tags the image with `image:`; `push` uses that name.

Q2: How to build a specific stage?
A2: `build.target: runtime` selects a multi-stage target.

Q3: Difference between `build.args` and `environment`?
A3: Args exist at build time only (ARG); environment exists at container runtime. Args may leak in image metadata.

Q4: How to force a fresh pull?
A4: `docker compose pull` or `pull_policy: always`.

Q5: How to build without cache?
A5: `docker compose build --no-cache`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- `build:` in dev and CI for your own services.
- `image:` for third-party services and for production deploys.

❌ Avoid when:
- Building on the production server (slow, needs source and toolchain; build in CI instead).
- Using untagged images you cannot reproduce.

---

## 📊 Visual Diagram
```
   DEV / CI                         REGISTRY (GHCR/ECR)              PRODUCTION VPS
 +-----------+   build:  +-------+   push    +-----------+   pull    +-------------+
 | Dockerfile| --------> | image | --------> | acme/api  | --------> | compose.yaml|
 | + source  |  tag from | local |  :git-sha | :git-sha  |           | image: only |
 +-----------+  image:   +-------+           +-----------+           +-------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| image | Ready packaged filesystem + metadata | तैयार packaged image |
| build | Instructions to create an image | image बनाने की instructions |
| context | Files sent to builder | builder को भेजी जाने वाली files |
| target | Stage in multi-stage Dockerfile | multi-stage का एक stage |
| pull_policy | When to pull images | कब image pull हो |

---

## ⚡ 3-Line Summary
English: `image` pulls from a registry; `build` builds from a Dockerfile.
English: With both, Compose builds and tags the result with the image name.
English: Build in CI, push a pinned tag, and only pull on the server.
Hindi: `image` registry से pull करता है; `build` Dockerfile से बनाता है।
Hindi: दोनों हों तो Compose build करके image के नाम से tag करता है।
Hindi: CI में build करें, pinned tag push करें, server पर सिर्फ pull करें।

---

## ➡️ Next Topic
188. ports Mapping - once the image runs, decide which container ports are reachable from the host.
