# 94. Multi-Stage Build for Node.js
# हिंदी में: Node.js के लिए Multi-Stage Build

---

## 🔵 Simple Definition (English)
A Node.js multi-stage Dockerfile installs all dependencies and compiles (TypeScript/NestJS) in a builder stage, then creates a small runtime stage with only production `node_modules` and compiled `dist/`, running as the non-root `node` user.

## 🔵 सरल परिभाषा (Hindi)
Node.js multi-stage Dockerfile में builder stage में सारी dependencies install होती हैं और compile (TypeScript/NestJS) होता है, फिर एक छोटा runtime stage बनता है जिसमें सिर्फ production `node_modules` और compiled `dist/` होते हैं, और app non-root `node` user से चलती है।

---

## 🔴 Problem it Solves
Single-stage Node images keep `typescript`, `eslint`, `jest`, `@types/*` and source `.ts` files. Images reach 1 GB, start slowly, and run as root. If an attacker gets remote code execution, root plus a full toolchain (npm, git, compilers) makes lateral movement easy.

## 🔴 यह क्यों बना? (Hindi)
Single-stage Node images में `typescript`, `eslint`, `jest`, `@types/*` और source `.ts` files रह जाती हैं। Image 1 GB तक पहुँचती है, slow start होती है और root से चलती है। अगर attacker को remote code execution मिल जाए तो root और पूरा toolchain (npm, git, compilers) होने से वह आसानी से आगे बढ़ सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → deps stage: copy package*.json, npm ci (cached layer)
Step 2 → build stage: copy src, npm run build -> dist/
Step 3 → prune: npm ci --omit=dev (prod modules only)
Step 4 → runtime stage: node:20-alpine, USER node
Step 5 → COPY --from=... dist + node_modules only
Step 6 → CMD ["node","dist/main.js"] (exec form, PID 1 = node)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → deps stage: package*.json copy, npm ci (cached layer)
Step 2 → build stage: src copy, npm run build -> dist/
Step 3 → prune: npm ci --omit=dev (सिर्फ prod modules)
Step 4 → runtime stage: node:20-alpine, USER node
Step 5 → COPY --from=... सिर्फ dist + node_modules
Step 6 → CMD ["node","dist/main.js"] (exec form, PID 1 = node)
```

---

## 🟡 Real World Example
A food-delivery backend (NestJS, like a Swiggy order service) deployed on EC2 with 4 containers per host. The old 1.3 GB image meant each scale-out event waited ~2 minutes for pull. With the multi-stage image (160 MB) autoscaled instances became ready in under 30 seconds, which mattered during dinner-time traffic spikes.

## 🟡 Real Example Hindi mein
एक food-delivery backend (NestJS, Swiggy की order service जैसा) EC2 पर हर host में 4 containers के साथ चलता था। पुरानी 1.3 GB image की वजह से हर scale-out में pull का इंतज़ार ~2 मिनट लगता था। Multi-stage image (160 MB) से autoscaled instances 30 सेकंड से कम में ready होने लगे, जो dinner-time traffic spikes में बहुत ज़रूरी था।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Dockerfile - basic 2-stage Node.js build
# Builder stage (example tag, update to current LTS)
FROM node:20-alpine AS builder
# Working directory in the builder
WORKDIR /app
# Copy dependency manifests first for caching
COPY package.json package-lock.json ./
# Clean, reproducible install from the lock file
RUN npm ci
# Copy the application source
COPY . .
# Compile TS to JS (script defined in package.json)
RUN npm run build

# Runtime stage
FROM node:20-alpine
# Working directory in the final image
WORKDIR /app
# Production mode
ENV NODE_ENV=production
# Install only production deps in the final image
COPY package.json package-lock.json ./
# --omit=dev skips devDependencies
RUN npm ci --omit=dev && npm cache clean --force
# Copy compiled app from builder
COPY --from=builder /app/dist ./dist
# Run as non-root user that ships with the official node image
USER node
# Start server
CMD ["node", "dist/main.js"]
```

```bash
# build and run locally (not built/run on the machine that produced these notes)
docker build -t node-api:basic .                          # build the image
docker run --rm -p 3000:3000 --env-file .env node-api:basic  # run it
```

## 💻 Code / Config Example — Advanced

```dockerfile
# syntax=docker/dockerfile:1
# Advanced production Dockerfile for a NestJS / Express TypeScript API
# Pin major version through ARG; update to the current LTS
ARG NODE_VERSION=20
# ---- Stage 1: dependencies (dev + prod) ----
FROM node:${NODE_VERSION}-alpine AS deps
# libc6-compat helps some native modules on alpine
RUN apk add --no-cache libc6-compat
# Work dir
WORKDIR /app
# Manifests only
COPY package.json package-lock.json ./
# npm cache is kept in a BuildKit cache mount, not in the image
RUN --mount=type=cache,target=/root/.npm npm ci

# ---- Stage 2: build ----
FROM deps AS build
# Source code (filtered by .dockerignore)
COPY tsconfig*.json nest-cli.json* ./
# App source folder
COPY src ./src
# Compile to dist/
RUN npm run build

# ---- Stage 3: production-only node_modules ----
FROM node:${NODE_VERSION}-alpine AS prod-deps
# Work dir
WORKDIR /app
# Manifests
COPY package.json package-lock.json ./
# Install production modules only, reusing the npm cache mount
RUN --mount=type=cache,target=/root/.npm npm ci --omit=dev

# ---- Stage 4: runtime ----
FROM node:${NODE_VERSION}-alpine AS runtime
# tini is a tiny init: reaps zombies and forwards signals
RUN apk add --no-cache tini
# Production flag
ENV NODE_ENV=production
# Work dir
WORKDIR /app
# Production modules owned by the non-root user
COPY --from=prod-deps --chown=node:node /app/node_modules ./node_modules
# Compiled output
COPY --from=build --chown=node:node /app/dist ./dist
# Metadata
COPY --chown=node:node package.json ./
# Run as non-root
USER node
# App port
EXPOSE 3000
# Health check using busybox wget
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/health || exit 1
# tini is PID 1; it starts node and forwards SIGTERM for graceful shutdown
ENTRYPOINT ["/sbin/tini", "--"]
# Default command
CMD ["node", "dist/main.js"]
```

```bash
# .dockerignore (required to keep context small and avoid leaking secrets)
cat > .dockerignore <<'EOF'
node_modules
dist
.git
.env
.env.*
coverage
*.log
Dockerfile
docker-compose*.yml
EOF
```

---

## 🟠 My Stack Integration
**Node.js**: this Dockerfile. **Nginx**: runs on the VPS host or as a sibling container and proxies to `api:3000`. **AWS**: push to ECR, run on ECS/EC2. **FastAPI/React** get their own variants (next topics). Enable graceful shutdown (`app.enableShutdownHooks()` in Nest) so `docker stop` (SIGTERM) finishes in-flight requests.

```yaml
# docker-compose.yml - API behind Nginx on a VPS
services:
  api:
    build:
      context: .                      # build from the Dockerfile above
      target: runtime                 # use the final stage
    restart: unless-stopped           # auto restart
    env_file: .env                    # runtime secrets, not baked in
    read_only: true                   # immutable filesystem (see topic 100)
    tmpfs:
      - /tmp                          # writable temp space in RAM
    expose:
      - "3000"                        # visible only on the compose network
  nginx:
    image: nginx:1.27-alpine          # example tag
    ports:
      - "80:80"                       # public entry point
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro  # proxy config
    depends_on:
      - api                           # start after the API container
```

Security: non-root user, no devDependencies, secrets via env/secret store, run `docker scout cves` or `trivy image` in CI (separate tools, install them first).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `COPY . .` before `npm ci` so every code change reinstalls all packages.
✅ Correct: Copy `package*.json`, install, then copy the source.

❌ Mistake 2: `CMD npm start` (shell form).
✅ Correct: `CMD ["node","dist/main.js"]`; npm and `sh` swallow SIGTERM, so shutdown takes 10 seconds then SIGKILL.

❌ Mistake 3: Copying `node_modules` from the host into the image.
✅ Correct: Add `node_modules` to `.dockerignore`; native modules built on macOS will not run on Linux.

---

## 🧠 Tricky Interview Question
Your app works with `docker build` locally but in production the container exits with "Cannot find module 'typescript'" even though `typescript` is in package.json. What happened?

Answer: `typescript` was in `devDependencies`, and the runtime stage used `npm ci --omit=dev`. Something at runtime (for example `ts-node`, or a config file loader) needs it. Fix: precompile everything to JS and do not use ts-node at runtime, or move the truly required package to `dependencies`.

---

## ⚫ Interview Questions + Answers

Q1: Why `npm ci` and not `npm install`?
A1: `npm ci` installs exactly the lock file, fails if it mismatches, and is faster and deterministic.

Q2: Why run as `USER node`?
A2: Least privilege: a compromised app cannot modify system files or bind low ports; the official node image already includes this user (uid 1000).

Q3: Why use tini or `--init`?
A3: Node as PID 1 does not handle signals/zombie processes the way init does. tini (or `docker run --init`) fixes it.

Q4: How do you speed up CI builds?
A4: Order layers by change frequency, use BuildKit cache mounts and `cache-from/cache-to type=gha` or a registry cache.

Q5: How to handle private npm packages at build time?
A5: `RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci` and pass `--secret id=npmrc,src=$HOME/.npmrc`; never use `ARG` for tokens.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- TypeScript, NestJS, Next.js, or any step that produces build output.
- Production deploys to VPS/ECS/Kubernetes.

❌ Avoid when:
- A plain JS script with no build and few deps; a single stage with `npm ci --omit=dev` is enough.
- Local hot-reload development; use a dev target with bind mounts.

---

## 📊 Visual Diagram
```
 package.json --> [deps: npm ci] ----> [build: tsc -> dist/]
        |                                     |
        +--> [prod-deps: npm ci --omit=dev]   |
                      |                       |
                      v                       v
               +-------------- runtime ---------------+
               | node:alpine + tini + USER node       |
               | node_modules(prod) + dist/           |
               +--------------------------------------+
                          |  port 3000
                       Nginx -> Internet
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| npm ci | Install exactly from lock file | lock file से सटीक install |
| devDependencies | Packages needed only to build/test | सिर्फ build/test के packages |
| tini | Minimal init process | छोटा init process |
| PID 1 | First process in container | container का पहला process |
| SIGTERM | Polite stop signal | रुकने का विनम्र signal |

---

## ⚡ 3-Line Summary
English: Build TypeScript in a builder stage and ship only dist plus production modules.
Run as the non-root node user with exec-form CMD and tini.
Use cache mounts and `.dockerignore` for fast, safe builds.
Hindi: TypeScript builder stage में build करो और सिर्फ dist व production modules भेजो।
Non-root node user, exec-form CMD और tini के साथ चलाओ।
तेज़ और सुरक्षित builds के लिए cache mounts और `.dockerignore` लगाओ।

---

## ➡️ Next Topic
**95. Multi-Stage Build for Python**: the same idea for FastAPI using a virtualenv and slim base.
