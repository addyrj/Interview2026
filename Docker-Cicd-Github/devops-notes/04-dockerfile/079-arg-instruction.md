# 079. ARG Instruction
# हिंदी में: ARG इंस्ट्रक्शन (Build-time Variable)

---

## 🔵 Simple Definition (English)
`ARG` defines a **build-time variable** in a Dockerfile. You pass its value with `docker build --build-arg NAME=value`. It exists only while the image is being built; it is not available to the running container (unless you copy it into an `ENV`).

## 🔵 सरल परिभाषा (Hindi)
`ARG` Dockerfile में एक **build-time variable** define करता है। इसकी value आप `docker build --build-arg NAME=value` से देते हैं। यह सिर्फ image बनते समय मौजूद रहता है; चलते हुए container में यह नहीं मिलता (जब तक आप इसे `ENV` में copy न करें)।

---

## 🔴 Problem it Solves
Without `ARG`, you had to edit the Dockerfile for every change: Node version, app version, build environment, or a private registry URL. That meant one Dockerfile per environment, or `sed` hacks in CI. `ARG` lets one Dockerfile be parameterised: the same file builds `node:20` today and `node:22` tomorrow, and CI can inject the Git commit SHA without touching the file.

## 🔴 यह क्यों बना? (Hindi)
`ARG` के बिना हर बदलाव (Node version, app version, build environment, private registry URL) के लिए Dockerfile edit करनी पड़ती थी। मतलब हर environment के लिए अलग Dockerfile, या CI में `sed` के hacks। `ARG` से एक ही Dockerfile parameterised हो जाती है: वही file आज `node:20` और कल `node:22` बनाती है, और CI बिना file छुए Git commit SHA inject कर सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Declare in Dockerfile:      ARG NODE_VERSION=20-alpine
Step 2 → (Optional) use in FROM:     FROM node:${NODE_VERSION}
Step 3 → Pass at build time:         docker build --build-arg NODE_VERSION=22-alpine .
Step 4 → Builder substitutes ${NODE_VERSION} in later instructions
Step 5 → Build ends -> ARG is gone from the container environment
Step 6 → BUT the value can still be seen in `docker history` -> never put secrets here
```

Important scope rules:
- An `ARG` declared **before the first `FROM`** is only usable inside `FROM` lines. To use it after `FROM`, declare it again (`ARG NODE_VERSION`) inside the stage.
- Each stage in a multi-stage build has its own ARG scope.
- Changing an ARG value invalidates the cache from the first instruction that uses it.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Dockerfile में declare करो:   ARG NODE_VERSION=20-alpine
Step 2 → (Optional) FROM में use करो:  FROM node:${NODE_VERSION}
Step 3 → Build के समय value दो:        docker build --build-arg NODE_VERSION=22-alpine .
Step 4 → Builder आगे की instructions में ${NODE_VERSION} बदल देता है
Step 5 → Build खत्म -> container के environment में ARG नहीं रहता
Step 6 → लेकिन value `docker history` में दिख सकती है -> secrets कभी मत डालो
```

Scope के नियम:
- पहली `FROM` से **पहले** declare किया गया `ARG` सिर्फ `FROM` lines में चलता है। `FROM` के बाद use करने के लिए stage के अंदर दोबारा `ARG NODE_VERSION` लिखना पड़ता है।
- Multi-stage build में हर stage का अपना ARG scope होता है।
- ARG की value बदलने पर जिस instruction में वह पहली बार use हुआ, वहाँ से cache invalid हो जाता है।

---

## 🟡 Real World Example
Your VPS runs a Node.js API. In GitHub Actions the CI job builds the image and passes `--build-arg GIT_SHA=${{ github.sha }}` and `--build-arg APP_VERSION=1.4.2`. The Dockerfile stores them as image labels, and the app exposes `/version`. When production misbehaves at 2 AM, you call `/version`, see the exact commit, and know what is deployed. The same Dockerfile builds on `node:20-alpine` in production and `node:22-alpine` in a test branch that checks the upgrade.

## 🟡 Real Example Hindi mein
आपके VPS पर Node.js API चल रही है। GitHub Actions का CI job image बनाते समय `--build-arg GIT_SHA=${{ github.sha }}` और `--build-arg APP_VERSION=1.4.2` देता है। Dockerfile इन्हें image labels में रखती है और app `/version` endpoint देती है। रात 2 बजे production में गड़बड़ हो तो `/version` से exact commit दिख जाता है और पता चलता है कि क्या deploy है। वही Dockerfile production में `node:20-alpine` और test branch में `node:22-alpine` (upgrade जाँचने के लिए) बनाती है।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Basic ARG example (Node.js)
# ARG declared before FROM: usable only in FROM lines
ARG NODE_VERSION=20-alpine
# Base image tag comes from the ARG (example tag, update to a current one)
FROM node:${NODE_VERSION}
# Re-declare to use inside this stage (ARG before FROM is out of scope here)
ARG APP_VERSION=dev
# Set the working directory inside the image
WORKDIR /app
# Copy the application source
COPY . .
# Print the version while building (proves the ARG is substituted)
RUN echo "Building version ${APP_VERSION}"
# Start the app
CMD ["node", "server.js"]
```

Build commands:

```bash
# Use defaults (NODE_VERSION=20-alpine, APP_VERSION=dev)
docker build -t myapi:dev .
# Override both ARGs at build time
docker build --build-arg NODE_VERSION=22-alpine --build-arg APP_VERSION=1.4.2 -t myapi:1.4.2 .
```

## 💻 Code / Config Example — Advanced

```dockerfile
# syntax=docker/dockerfile:1
# Advanced: multi-stage build with ARGs, labels, and safe runtime ENV
# Global ARG (only usable in FROM lines)
ARG NODE_VERSION=20-alpine
# Stage 1: build stage, named "build"
FROM node:${NODE_VERSION} AS build
# Working directory for the build stage
WORKDIR /app
# Copy only dependency manifests first (better layer cache)
COPY package.json package-lock.json ./
# Install exact locked dependencies
RUN npm ci
# Copy the rest of the source
COPY . .
# Build step (for example TypeScript compile)
RUN npm run build

# Stage 2: runtime stage
FROM node:${NODE_VERSION} AS runtime
# Re-declare ARGs needed in this stage; defaults keep local builds working
ARG APP_VERSION=dev
# Commit SHA injected by CI
ARG GIT_SHA=unknown
# Promote selected ARGs to ENV so the running app can read them
ENV APP_VERSION=${APP_VERSION} GIT_SHA=${GIT_SHA} NODE_ENV=production
# OCI standard labels built from ARGs (visible with docker inspect)
LABEL org.opencontainers.image.version=${APP_VERSION} org.opencontainers.image.revision=${GIT_SHA}
# Working directory for runtime
WORKDIR /app
# Copy only the build output and production deps from the build stage
COPY --from=build /app/dist ./dist
# Copy package manifests so we can install prod-only dependencies
COPY package.json package-lock.json ./
# Install production dependencies only and clean npm cache
RUN npm ci --omit=dev && npm cache clean --force
# Run as the non-root user that ships with the official node image
USER node
# Start the compiled app
CMD ["node", "dist/server.js"]
```

```bash
# CI build with metadata (values come from the pipeline, not hardcoded)
docker build \
  --build-arg APP_VERSION=1.4.2 \
  --build-arg GIT_SHA="$(git rev-parse --short HEAD)" \
  -t myapi:1.4.2 .
```

---

## 🟠 My Stack Integration
- **Node.js / React**: pass `VITE_API_URL` (or `REACT_APP_API_URL`) as an `ARG`. React bakes env values into static JS at build time, so a build-time ARG is the correct tool there (the runtime `ENV` would not help).
- **FastAPI**: pass `PYTHON_VERSION` and `APP_VERSION` to pick `python:${PYTHON_VERSION}-slim`.
- **GitHub Actions**: `docker/build-push-action` takes `build-args:`.
- **docker-compose on VPS**: `build.args`.
- **Nginx**: you can ARG the nginx tag, e.g. `FROM nginx:${NGINX_VERSION}`.

```yaml
# docker-compose.yml fragment (Compose Specification)
services:
  # React frontend served by Nginx
  web:
    build:
      # Build context folder
      context: ./frontend
      # Build-time args passed to the Dockerfile ARGs
      args:
        # Public API URL baked into the React bundle (not a secret)
        VITE_API_URL: https://api.example.com
        # Nginx tag used in FROM
        NGINX_VERSION: 1.27-alpine
  # FastAPI backend
  api:
    build:
      # Backend folder
      context: ./backend
      args:
        # Python base image version
        PYTHON_VERSION: "3.12"
```

```yaml
# .github/workflows/ci.yml fragment (docker/build-push-action)
- name: Build image
  # Official Docker action (example version, update to latest major)
  uses: docker/build-push-action@v6
  with:
    # Build context is repo root
    context: .
    # Do not push in this example
    push: false
    # Multi-line build args
    build-args: |
      APP_VERSION=${{ github.ref_name }}
      GIT_SHA=${{ github.sha }}
```

Security note: never pass tokens through `ARG`. Use BuildKit secrets, shown below in the mistakes section.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Passing secrets such as `--build-arg NPM_TOKEN=abc123`. The value is stored in image history and anyone with the image can read it with `docker history --no-trunc`.
✅ Correct: Use `RUN --mount=type=secret,id=npm_token ...` with `docker build --secret id=npm_token,src=.npmrc-token .` (BuildKit).

❌ Mistake 2: Declaring `ARG NODE_VERSION` before `FROM` and then using `${NODE_VERSION}` after `FROM` expecting a value. It will be empty.
✅ Correct: Re-declare `ARG NODE_VERSION` after `FROM` inside the stage.

❌ Mistake 3: Expecting `process.env.APP_VERSION` to work at runtime with only an `ARG`.
✅ Correct: Add `ENV APP_VERSION=${APP_VERSION}`.

❌ Mistake 4: Using a changing ARG (like a timestamp) early in the Dockerfile. It busts the cache for every later layer.
✅ Correct: Declare such ARGs as late as possible, just before the `LABEL`/`RUN` that uses them.

---

## 🧠 Tricky Interview Question
You build with `--build-arg DB_PASSWORD=secret`, and the Dockerfile only has `ARG DB_PASSWORD` (no `ENV`). Your colleague says "it is safe, the container cannot see it." Is that right?

Answer: Partly. A running container cannot read it via `env`, but the value is recorded in the image metadata and the build history. Anyone who can pull the image can run `docker history --no-trunc IMAGE` and see it. Also, if a `RUN` command used it, it may be in a layer. So it is not safe. Use BuildKit secret mounts (they are not written into layers) or inject the secret at runtime via the orchestrator.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `ARG` and `ENV`?
A1: `ARG` exists only at build time and is set with `--build-arg`. `ENV` is persisted in the image and available at runtime too. Details are in the next note (080).

Q2: Can you use an ARG in `FROM`?
A2: Yes. An ARG declared before the first `FROM` can parametrise the base image (`FROM node:${NODE_VERSION}`). It is then out of scope after `FROM` unless re-declared.

Q3: What happens if you pass `--build-arg FOO=1` but the Dockerfile has no `ARG FOO`?
A3: Docker warns that the build arg was not consumed (classic builder prints a warning; BuildKit may warn), and the value is ignored.

Q4: Does changing an ARG invalidate the cache?
A4: Yes, from the instruction that first uses it (and its descendants). Unused ARG changes do not affect earlier layers.

Q5: Name predefined ARGs.
A5: `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`, `FTP_PROXY` and (with BuildKit) `TARGETPLATFORM`, `TARGETARCH`, `BUILDPLATFORM`, etc. They can be used without declaring (platform ones need an `ARG` line to be visible inside a stage).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Choosing base image versions (Node, Python, Nginx) per build.
- Injecting non-secret metadata (version, commit SHA, build date).
- Baking public config into frontend bundles (React API URL).
- Cross-platform builds with `TARGETARCH`.

❌ Avoid when:
- The value is a secret (password, token, key): use BuildKit `--secret`.
- The value must change at container start without rebuilding: use `ENV` or runtime `-e`.
- The value changes every build and is placed early: it kills caching.

---

## 📊 Visual Diagram

```
  docker build --build-arg APP_VERSION=1.4.2 .
                    |
                    v
        +---------------------------+
        | Dockerfile                |
        |  ARG APP_VERSION=dev      |  <- default if not passed
        |  RUN echo $APP_VERSION    |  <- BUILD TIME only
        |  ENV APP_VERSION=$APP_... |  <- copies into runtime
        +-------------+-------------+
                      |
        +-------------+--------------+
        |                            |
        v                            v
   Build container             Final image
   (ARG visible)               - ARG: gone from env
                               - ENV: present
                               - docker history: ARG VALUE VISIBLE (!)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ARG | Build-time variable | build के समय का variable |
| --build-arg | CLI flag to set ARG | ARG की value देने वाला flag |
| Build context | Folder sent to builder | build के लिए भेजा गया folder |
| Scope | Where a variable is visible | variable कहाँ दिखता है |
| Predefined ARG | Built-in ARG like HTTP_PROXY | पहले से बना ARG |
| BuildKit secret | Safe secret at build time | build के समय सुरक्षित secret |

---

## ⚡ 3-Line Summary
English: `ARG` is a build-time variable set with `--build-arg`. It disappears from the runtime environment but stays visible in image history. Use it for versions and metadata, never for secrets.
Hindi: `ARG` build-time variable है जो `--build-arg` से set होता है। यह runtime environment से गायब हो जाता है पर image history में दिखता है। इसे versions और metadata के लिए use करो, secrets के लिए कभी नहीं।

---

## ➡️ Next Topic
**080. ENV vs ARG: Difference**: now that you know ARG, compare it directly with ENV so you can pick the right one every time.
