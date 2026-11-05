# 92. Image Size Optimization
# हिंदी में: Docker Image का Size कम करना

---

## 🔵 Simple Definition (English)
Image size optimization means making your Docker image as small as possible: small base image, only runtime files, no build tools, no caches. A smaller image pulls faster, starts faster, costs less storage and has fewer vulnerabilities.

## 🔵 सरल परिभाषा (Hindi)
Image size optimization का मतलब है Docker image को जितना हो सके छोटा बनाना: छोटी base image, सिर्फ runtime files, build tools और caches नहीं। छोटी image जल्दी pull होती है, जल्दी start होती है, storage कम लेती है और उसमें vulnerabilities भी कम होती हैं।

---

## 🔴 Problem it Solves
A naive `FROM node:20` + `COPY . .` + `npm install` image is 1.1 GB+. It contains compilers, git, npm cache, test files, `.git` folder and devDependencies. Every deploy to your VPS or ECS pulls 1 GB, CI is slow, the registry bill grows, and a bigger attack surface means more CVEs for scanners to flag.

## 🔴 यह क्यों बना? (Hindi)
Naive `FROM node:20` + `COPY . .` + `npm install` image 1.1 GB+ की बन जाती है। उसमें compilers, git, npm cache, test files, `.git` folder और devDependencies सब आ जाते हैं। हर deploy पर VPS या ECS को 1 GB pull करना पड़ता है, CI slow होता है, registry का bill बढ़ता है, और बड़ा attack surface मतलब scanners ज़्यादा CVEs दिखाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Measure first: docker image ls, docker history <image>
Step 2 → Choose a small base (node:20-alpine / -slim / distroless)
Step 3 → Add .dockerignore (node_modules, .git, tests, .env)
Step 4 → Use multi-stage build: build tools stay in builder stage
Step 5 → Install only production deps (npm ci --omit=dev)
Step 6 → Combine RUN commands, clean caches in the SAME layer
Step 7 → Re-measure and compare (target: 1 GB -> 100-200 MB)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले नापो: docker image ls, docker history <image>
Step 2 → छोटी base चुनो (node:20-alpine / -slim / distroless)
Step 3 → .dockerignore बनाओ (node_modules, .git, tests, .env)
Step 4 → Multi-stage build: build tools builder stage में ही रहते हैं
Step 5 → सिर्फ production deps install करो (npm ci --omit=dev)
Step 6 → RUN commands जोड़ो, cache उसी layer में साफ करो
Step 7 → फिर से नापो और तुलना करो (लक्ष्य: 1 GB -> 100-200 MB)
```

---

## 🟡 Real World Example
A startup ran its Node.js API on a single VPS with 20 GB disk. Each deploy left a 1.2 GB image; after 15 deploys the disk was full and `docker pull` failed at 2 AM. After switching to `node:20-alpine`, multi-stage and `.dockerignore`, the image became 140 MB. Deploy time dropped from 3 minutes to 25 seconds, and `docker image prune` in the deploy script kept the disk healthy.

## 🟡 Real Example Hindi mein
एक startup अपना Node.js API 20 GB disk वाले एक VPS पर चलाती थी। हर deploy 1.2 GB की image छोड़ जाता था; 15 deploys के बाद disk भर गई और रात 2 बजे `docker pull` fail हो गया। `node:20-alpine`, multi-stage और `.dockerignore` लगाने के बाद image 140 MB की हो गई। Deploy time 3 मिनट से 25 सेकंड हो गया और deploy script में `docker image prune` से disk ठीक रही।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Dockerfile.basic - small image with minimal changes
# Small base image instead of the 1 GB node:20 (tag is an example, update it)
FROM node:20-alpine
# All following commands run inside /app
WORKDIR /app
# Copy only dependency manifests first (cache friendly)
COPY package.json package-lock.json ./
# Install only production dependencies and clean npm cache in the same layer
RUN npm ci --omit=dev && npm cache clean --force
# Copy the rest of the source (.dockerignore filters junk)
COPY . .
# Document the port the app listens on
EXPOSE 3000
# Start the app (exec form, so signals reach node)
CMD ["node", "server.js"]
```

```bash
# .dockerignore contents (create this file next to the Dockerfile)
cat > .dockerignore <<'EOF'
node_modules
npm-debug.log
.git
.gitignore
.env
.env.*
Dockerfile*
docker-compose*.yml
coverage
tests
*.md
EOF

# measure before and after
docker build -t api:basic -f Dockerfile.basic .   # build the image
docker image ls api:basic                          # show the SIZE column
docker history api:basic                           # see size of every layer
```

## 💻 Code / Config Example — Advanced

```dockerfile
# Dockerfile - production: multi-stage, cache mounts, non-root
# syntax=docker/dockerfile:1
# Stage 1: install ALL deps and build (TypeScript etc.)
FROM node:20-alpine AS builder
# Work directory for the builder stage
WORKDIR /app
# Copy manifests only so the install layer is cached
COPY package.json package-lock.json ./
# BuildKit cache mount keeps the npm cache OUT of the image layers
RUN --mount=type=cache,target=/root/.npm npm ci
# Copy source code
COPY . .
# Compile TypeScript to dist/
RUN npm run build
# Remove devDependencies so only prod modules remain
RUN npm prune --omit=dev

# Stage 2: tiny runtime image
FROM node:20-alpine AS runtime
# Production mode: frameworks skip dev-only code
ENV NODE_ENV=production
# Runtime work directory
WORKDIR /app
# Copy ONLY what is needed to run, owned by the built-in non-root "node" user
COPY --from=builder --chown=node:node /app/node_modules ./node_modules
# Copy compiled output
COPY --from=builder --chown=node:node /app/dist ./dist
# package.json is needed for "type", version etc.
COPY --from=builder --chown=node:node /app/package.json ./package.json
# Drop root privileges
USER node
# App port
EXPOSE 3000
# Container-level health check (wget exists in alpine busybox)
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/health || exit 1
# Start the compiled app
CMD ["node", "dist/main.js"]
```

```bash
# Inspect where the space goes (optional tool "dive" must be installed separately)
docker history --no-trunc --format '{{.Size}}\t{{.CreatedBy}}' api:prod | head -20
```

---

## 🟠 My Stack Integration
**Node.js**: alpine + multi-stage + `npm ci --omit=dev`. **FastAPI**: `python:3.12-slim` (not alpine, wheels are glibc based) with `pip install --no-cache-dir`. **React**: build in node stage, serve static files from `nginx:alpine` (about 25-40 MB). **VPS/AWS**: smaller images mean faster `docker pull` from ECR and faster rollbacks.

```yaml
# docker-compose.yml - use the optimized images on the VPS (example)
services:
  api:
    image: myorg/api:1.4.2          # small multi-stage image from the registry
    restart: unless-stopped         # restart after crash or reboot
    env_file: .env                  # secrets stay outside the image
    ports:
      - "127.0.0.1:3000:3000"       # only Nginx on the host can reach it
  web:
    image: myorg/web:1.4.2          # nginx:alpine + static React build
    restart: unless-stopped         # keep it alive
    ports:
      - "80:80"                     # public HTTP (put TLS in front)
```

Security: smaller image = fewer packages = fewer CVEs. Never bake `.env`, SSH keys or `.git` into layers; deleting a file in a later layer does NOT remove it from the earlier layer.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `RUN apt-get update` in one layer and `rm -rf /var/lib/apt/lists/*` in the next.
✅ Correct: Do install and cleanup in the same `RUN`, because layers are immutable and the earlier layer still holds the data.

❌ Mistake 2: `COPY . .` before installing dependencies, with no `.dockerignore`.
✅ Correct: Copy manifests first, install, then copy source. Always keep `.dockerignore` (node_modules, .git, .env).

❌ Mistake 3: Using alpine for a Python app with numpy/pandas.
✅ Correct: Use `python:3.12-slim`; alpine (musl) often has no prebuilt wheels so it compiles for minutes and may even become bigger.

---

## 🧠 Tricky Interview Question
You deleted `node_modules/.cache` with `RUN rm -rf` in a later line, but the image size did not shrink. Why?

Answer: Each Dockerfile instruction creates a read-only layer. `rm` in a new layer only adds a "whiteout" marker; the data still exists in the earlier layer and counts toward total size. The fix is to never create the data in a persistent layer: clean in the same `RUN`, use a multi-stage build, or use a BuildKit `--mount=type=cache`.

---

## ⚫ Interview Questions + Answers

Q1: How do you find which layer makes an image big?
A1: `docker history <image>` shows size per instruction; the tool `dive` gives an interactive view per layer.

Q2: Why multi-stage builds shrink images?
A2: Compilers, devDependencies and source stay in the builder stage; only the final stage's layers are shipped, using `COPY --from=builder`.

Q3: Alpine vs slim for size?
A3: Alpine is ~5 MB base, slim ~75 MB for Debian-slim, but alpine uses musl and can break native modules or Python wheels. Choose by compatibility first.

Q4: Does `.dockerignore` affect image size?
A4: Yes. It shrinks the build context sent to the daemon and prevents `COPY . .` from adding junk like `.git` and `node_modules`; it also avoids leaking `.env`.

Q5: Does squashing layers help?
A5: It can merge layers but also breaks layer sharing/cache between images. Multi-stage is the preferred approach.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Images go to a registry and are pulled often (CI, ECS, Kubernetes, VPS).
- Security scanning flags many CVEs from unused OS packages.
- Disk on VPS is limited.

❌ Avoid when:
- Over-optimizing a local dev image where debugging tools (curl, bash) are more useful.
- A tiny base breaks required native libraries; correctness beats a 50 MB gain.

---

## 📊 Visual Diagram
```
 BEFORE (1.2 GB)                    AFTER (140 MB)
+--------------------+            +--------------------+
| node:20 (Debian)   | 1.0 GB     | node:20-alpine     | 50 MB
| + build tools      |            | + prod node_modules| 60 MB
| + devDependencies  |            | + dist/ (compiled) | 5 MB
| + .git, tests      |            +--------------------+
| + npm cache        |             builder stage is thrown away
+--------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Layer | Read-only filesystem diff per instruction | हर instruction की read-only परत |
| .dockerignore | Files excluded from build context | build से बाहर रखी files |
| Multi-stage | Several FROM in one Dockerfile | एक Dockerfile में कई stages |
| Cache mount | BuildKit temp cache not saved in image | image में न जाने वाला cache |
| Attack surface | Amount of code an attacker can use | हमले की सतह |

---

## ⚡ 3-Line Summary
English: Pick a small base, use multi-stage, and ship only runtime files.
Clean caches in the same layer and always use `.dockerignore`.
Measure with `docker history` before and after.
Hindi: छोटी base चुनो, multi-stage use करो और सिर्फ runtime files भेजो।
Cache उसी layer में साफ करो और हमेशा `.dockerignore` रखो।
पहले और बाद में `docker history` से नापो।

---

## ➡️ Next Topic
**93. Multi-Stage Build — Complete Guide**: the main technique behind size optimization, explained fully with named stages, targets and cache.
