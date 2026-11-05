# 93. Multi-Stage Build — Complete Guide
# हिंदी में: Multi-Stage Build — पूरी गाइड

---

## 🔵 Simple Definition (English)
A multi-stage build uses several `FROM` lines in one Dockerfile. Each `FROM` starts a new stage; you build in early stages and copy only the final artifacts into the last stage. Only the last stage (or the one chosen with `--target`) becomes the image.

## 🔵 सरल परिभाषा (Hindi)
Multi-stage build में एक Dockerfile में कई `FROM` लाइनें होती हैं। हर `FROM` नया stage शुरू करता है; आप शुरुआती stages में build करते हैं और सिर्फ final artifacts को आखिरी stage में copy करते हैं। सिर्फ आखिरी stage (या `--target` से चुना हुआ stage) ही image बनता है।

---

## 🔴 Problem it Solves
Before multi-stage (Docker 17.05), people kept compilers and source in the image, or maintained two Dockerfiles plus a shell script (`build.Dockerfile` -> `docker cp` -> `run.Dockerfile`). That was fragile, slow and error-prone. Production images carried gcc, make, devDependencies and source code that attackers could abuse.

## 🔴 यह क्यों बना? (Hindi)
Multi-stage (Docker 17.05) से पहले लोग या तो compilers और source image में ही रखते थे, या दो Dockerfiles और एक shell script (`build.Dockerfile` -> `docker cp` -> `run.Dockerfile`) बनाते थे। यह fragile, slow और error-prone था। Production image में gcc, make, devDependencies और source code रहता था जिसका attackers फायदा उठा सकते थे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → FROM image AS name       (start stage "name")
Step 2 → Install tools, build the app in that stage
Step 3 → FROM runtime-base AS final (new clean filesystem)
Step 4 → COPY --from=name /path /path (pull only artifacts)
Step 5 → docker build [--target name] . (final stage = image)
Step 6 → Unused stages are skipped/discarded by BuildKit
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → FROM image AS name       (stage "name" शुरू)
Step 2 → उसी stage में tools install करो, app build करो
Step 3 → FROM runtime-base AS final (नया साफ filesystem)
Step 4 → COPY --from=name /path /path (सिर्फ artifacts खींचो)
Step 5 → docker build [--target name] . (final stage = image)
Step 6 → BuildKit unused stages छोड़/हटा देता है
```

---

## 🟡 Real World Example
A fintech team had one Dockerfile with stages `deps`, `test`, `build`, `prod`. In GitHub Actions they run `docker build --target test .` to run unit tests inside the container, and on main they build `--target prod` and push it to ECR. One file gives identical environments for test and production, and the prod image never contains test frameworks.

## 🟡 Real Example Hindi mein
एक fintech team की एक Dockerfile में stages थे `deps`, `test`, `build`, `prod`। GitHub Actions में वे `docker build --target test .` से container के अंदर unit tests चलाते हैं, और main पर `--target prod` build करके ECR में push करते हैं। एक ही file से test और production का environment एक जैसा रहता है, और prod image में test frameworks कभी नहीं आते।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Dockerfile - two stage basic example (Go-like idea shown with Node)
# Stage 1 named "build": has npm and all devDependencies
FROM node:20-alpine AS build
# Directory inside the build stage
WORKDIR /src
# Copy manifests first for layer caching
COPY package*.json ./
# Install everything needed to compile
RUN npm ci
# Copy source
COPY . .
# Produce /src/dist
RUN npm run build

# Stage 2 named "final": clean filesystem, nothing from "build" yet
FROM node:20-alpine AS final
# Runtime directory
WORKDIR /app
# Copy only the compiled output from stage "build"
COPY --from=build /src/dist ./dist
# Run it
CMD ["node", "dist/index.js"]
```

```bash
# build the last stage (default)
docker build -t demo:latest .
# stop at the build stage only (debugging)
docker build --target build -t demo:build .
```

## 💻 Code / Config Example — Advanced

```dockerfile
# syntax=docker/dockerfile:1
# Dockerfile - 5 stages: deps, test, build, prod-deps, prod
# Shared base so every stage uses the same Node version (ARG can be overridden)
ARG NODE_VERSION=20
# Base stage reused by others
FROM node:${NODE_VERSION}-alpine AS base
# Common working dir
WORKDIR /app

# Stage "deps": all deps (dev + prod) cached by lock file
FROM base AS deps
# Only manifests, so this layer changes only when deps change
COPY package.json package-lock.json ./
# Cache mount speeds up repeated installs and stays out of the image
RUN --mount=type=cache,target=/root/.npm npm ci

# Stage "test": run with docker build --target test .
FROM deps AS test
# Bring the source
COPY . .
# Fails the build if tests fail
RUN npm test

# Stage "build": compile the app
FROM deps AS build
# Bring the source
COPY . .
# Output goes to /app/dist
RUN npm run build

# Stage "prod-deps": only production node_modules
FROM base AS prod-deps
# Manifests again
COPY package.json package-lock.json ./
# Install without devDependencies
RUN --mount=type=cache,target=/root/.npm npm ci --omit=dev

# Stage "prod": final tiny runtime
FROM base AS prod
# Production mode
ENV NODE_ENV=production
# Only prod modules from the previous stage
COPY --from=prod-deps --chown=node:node /app/node_modules ./node_modules
# Only compiled code from build stage
COPY --from=build --chown=node:node /app/dist ./dist
# Needed by Node for package metadata
COPY --chown=node:node package.json ./
# Non-root runtime
USER node
# App port
EXPOSE 3000
# Start
CMD ["node", "dist/main.js"]
```

```bash
# Run tests only (stops after "test" stage; BuildKit skips unrelated stages)
docker build --target test -t api:test .
# Build production image
docker build --target prod -t api:1.0.0 .
# Override base version at build time
docker build --build-arg NODE_VERSION=22 --target prod -t api:node22 .
```

---

## 🟠 My Stack Integration
**Node.js/NestJS**: deps -> build -> prod-deps -> prod. **FastAPI**: builder installs wheels into a venv, final copies the venv. **React**: build stage -> `nginx:alpine`. **CI**: GitHub Actions runs `--target test`, then pushes `--target prod` to ECR/GHCR; the VPS only pulls the prod tag.

```yaml
# .github/workflows/ci.yml - snippet using stage targets (action versions are examples)
name: ci
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest                   # GitHub hosted runner
    steps:
      - uses: actions/checkout@v4            # get the code
      - uses: docker/setup-buildx-action@v3  # enable BuildKit
      - uses: docker/build-push-action@v6    # build the test stage
        with:
          context: .                         # build context
          target: test                       # run tests inside Docker
          push: false                        # do not publish test stage
          cache-from: type=gha               # reuse GitHub cache
          cache-to: type=gha,mode=max        # save all stage layers
```

Security: secrets used during build must use `--mount=type=secret` (never `ARG`/`ENV`), so they do not remain in the stage history.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `COPY --from=build /app .` copying the entire builder folder.
✅ Correct: Copy only the specific artifacts (`dist`, prod `node_modules`).

❌ Mistake 2: Using stage numbers (`--from=0`) in a long file.
✅ Correct: Name stages with `AS name` so reordering does not break copies.

❌ Mistake 3: Putting secrets in an early stage via `ARG NPM_TOKEN` and thinking they vanish.
✅ Correct: Intermediate stage history still exists in the local cache and builder; use `RUN --mount=type=secret,id=npm`.

---

## 🧠 Tricky Interview Question
You have 5 stages but `docker build --target prod` takes the same time as before and `test` runs too. Why might that happen with the classic builder?

Answer: The legacy builder executed stages sequentially up to the target, including stages not required. BuildKit (default since Docker 23) builds a dependency graph, skips stages that `prod` does not depend on and builds independent stages in parallel. If `prod` does `COPY --from=test`, test becomes a dependency and will run. Check `DOCKER_BUILDKIT=1` and stage dependencies.

---

## ⚫ Interview Questions + Answers

Q1: What is the benefit of multi-stage?
A1: Smaller, safer images; one Dockerfile for build, test and run; no extra scripts.

Q2: Can you copy from an external image?
A2: Yes: `COPY --from=nginx:alpine /etc/nginx/nginx.conf /tmp/` uses an image as a stage.

Q3: What does `--target` do?
A3: It stops the build at the named stage and tags that stage as the image.

Q4: Do stages share cache?
A4: Each instruction is cached by its content and parent layer; unchanged stages are reused on later builds. In CI use `cache-from/cache-to`.

Q5: Is the builder stage's data inside the final image?
A5: No. Only layers of the final stage ship; the builder stays in the build cache on the builder host.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Anything compiled or bundled (TypeScript, React, Go, Java).
- You need tests and prod from one Dockerfile.

❌ Avoid when:
- Pure interpreted script with no build step, a single stage is enough.
- Team cannot debug stages; keep it simple until needed.

---

## 📊 Visual Diagram
```
 Dockerfile
 +---------------------------------------------+
 | FROM node AS deps  --> npm ci               |
 |        |                                    |
 |        +--> FROM deps AS test  (npm test)   |
 |        +--> FROM deps AS build (npm build)--+--dist-+
 | FROM base AS prod-deps (npm ci --omit=dev)--+--mods-+
 |                                             |      v
 | FROM base AS prod  <-- COPY --from=... ------+-----+
 +---------------------------------------------+
        only "prod" layers become the final image
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Stage | Section starting with FROM | FROM से शुरू होने वाला हिस्सा |
| COPY --from | Copy files from another stage/image | दूसरे stage/image से copy |
| --target | Build up to a named stage | नाम वाले stage तक build |
| BuildKit | Modern build engine | नया build engine |
| Artifact | Output file of a build | build का नतीजा |

---

## ⚡ 3-Line Summary
English: Many FROM lines give many stages; build in one and copy results to a clean final stage.
Name stages and use `--target` for test and prod.
BuildKit skips unused stages and caches well.
Hindi: कई FROM से कई stages बनते हैं; एक में build करो और नतीजा साफ final stage में copy करो।
Stages को नाम दो और test/prod के लिए `--target` use करो।
BuildKit unused stages छोड़ देता है और अच्छा cache करता है।

---

## ➡️ Next Topic
**94. Multi-Stage Build for Node.js**: apply this pattern specifically to a Node/NestJS API with prune and non-root user.
