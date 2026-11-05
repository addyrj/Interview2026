# 108. Base Image Selection
# हिंदी में: Base Image का चुनाव

---

## 🔵 Simple Definition (English)
The **base image** is the image in your `FROM` line: the OS layer and runtime your app is built on. Choosing it decides image size, security surface, compatibility and build speed.

## 🔵 सरल परिभाषा (Hindi)
**Base image** वह image है जो आपकी `FROM` line में होती है: OS layer और runtime जिस पर आपकी app बनती है। इसका चुनाव image का size, security surface, compatibility और build speed तय करता है।

---

## 🔴 Problem it Solves
- `node:22` (Debian full) is about 1 GB; slow to pull, many packages that can carry CVEs.
- Too small a base (alpine/musl) can break native modules (`sharp`, `bcrypt`, some Python wheels).
- Random community base images may be unmaintained or malicious.
- A wrong choice shows up later as slow deploys on small VPS disks and failed security scans.

## 🔴 यह क्यों बना? (Hindi)
- `node:22` (पूरा Debian) लगभग 1 GB है; pull धीमा, और बहुत से packages जिनमें CVEs हो सकते हैं।
- बहुत छोटा base (alpine/musl) native modules (`sharp`, `bcrypt`, कुछ Python wheels) तोड़ सकता है।
- कोई भी community base image unmaintained या malicious हो सकती है।
- गलत चुनाव बाद में छोटे VPS disk पर धीमे deploy और failed security scans के रूप में दिखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → List needs: language runtime, native libs, shell for debugging?
Step 2 → Pick family: full (debian) | slim | alpine | distroless | scratch
Step 3 → Pin version + OS: node:22.11.0-slim-bookworm
Step 4 → Use multi-stage: fat builder image, tiny runtime image
Step 5 → Scan (trivy/docker scout) and compare size + CVE count
Step 6 → Rebuild regularly to pick up base-image security patches
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → ज़रूरतें लिखो: language runtime, native libs, debugging के लिए shell?
Step 2 → Family चुनो: full (debian) | slim | alpine | distroless | scratch
Step 3 → Version + OS pin करो: node:22.11.0-slim-bookworm
Step 4 → Multi-stage: बड़ा builder image, छोटा runtime image
Step 5 → Scan (trivy/docker scout) करो; size और CVE count तुलना करो
Step 6 → Base-image के security patches के लिए नियमित rebuild करो
```

---

## 🟡 Real World Example
A team ran a FastAPI service on `python:3.12` (about 1 GB). Pulls on their 20 GB VPS took minutes and the disk filled with old layers. Moving to `python:3.12-slim-bookworm` cut it to about 150 MB. Another team chose alpine for a Node service that used `sharp`; the install needed extra build tooling and had runtime issues, so they moved to `node:22-slim` and everything was stable.

## 🟡 Real Example Hindi mein
एक team की FastAPI service `python:3.12` (लगभग 1 GB) पर चलती थी। उनके 20 GB VPS पर pull में मिनट लगते और disk पुरानी layers से भर जाती। `python:3.12-slim-bookworm` पर जाने से लगभग 150 MB हो गई। दूसरी team ने `sharp` इस्तेमाल करने वाली Node service के लिए alpine चुना; install में extra build tooling लगी और runtime issues आए, तो `node:22-slim` पर गए और सब stable हो गया।

---

## 💻 Code / Config Example — Basic
```dockerfile
# Slim Debian base: small and glibc compatible (example tag, update regularly)
FROM python:3.12.7-slim-bookworm
# App folder
WORKDIR /app
# Copy requirements first for layer caching
COPY requirements.txt .
# Install without pip cache to keep the image small
RUN pip install --no-cache-dir -r requirements.txt
# Copy source code
COPY . .
# Run FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Compare sizes of candidate bases
docker pull node:22-slim
docker pull node:22-alpine
# Show size column for node images
docker images node
```

## 💻 Code / Config Example — Advanced
```dockerfile
# syntax=docker/dockerfile:1
# ---------- Stage 1: build (full toolchain) ----------
FROM node:22.11.0-bookworm AS build
# Work dir for build
WORKDIR /app
# Dependency manifests first
COPY package.json package-lock.json ./
# Install ALL deps (dev included) for build step
RUN npm ci
# Copy source
COPY . .
# Produce production bundle into /app/dist
RUN npm run build
# Reinstall only production deps for runtime
RUN npm prune --omit=dev

# ---------- Stage 2: runtime (small, non-root) ----------
FROM node:22.11.0-slim AS runtime
# Production mode: faster, fewer debug paths
ENV NODE_ENV=production
# Work dir at runtime
WORKDIR /app
# Copy only what is needed from build stage
COPY --from=build --chown=node:node /app/node_modules ./node_modules
COPY --from=build --chown=node:node /app/dist ./dist
COPY --from=build --chown=node:node /app/package.json ./package.json
# Drop root: the official image ships a 'node' user
USER node
# Document the port
EXPOSE 3000
# Start the compiled app
CMD ["node", "dist/server.js"]
```
(Dockerfile syntax checked with a script, not built locally. Tags are examples.)

---

## 🟠 My Stack Integration
- **Node.js API**: `node:22-slim` runtime (alpine only if no native modules).
- **FastAPI**: `python:3.12-slim-bookworm`.
- **React**: build in `node:22-slim`, serve with `nginx:1.27-alpine` (static files have no native dependency issues).
- **VPS/AWS**: smaller images = faster `docker pull` and less ECR storage.

```dockerfile
# React static site: build then serve with small Nginx
FROM node:22.11.0-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Final tiny image: only Nginx plus static files
FROM nginx:1.27-alpine
# Copy compiled assets to Nginx web root
COPY --from=build /app/dist /usr/share/nginx/html
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Always choosing alpine "because it is smallest".
✅ Correct: Alpine uses musl libc; test native modules/wheels first, or use `-slim`.

❌ Mistake 2: `FROM ubuntu` then installing Node manually.
✅ Correct: Use the official language image; it is maintained and patched.

❌ Mistake 3: Shipping the compiler/build tools in the runtime image.
✅ Correct: Multi-stage build.

❌ Mistake 4: Never rebuilding, so base CVEs pile up.
✅ Correct: Scheduled weekly rebuild plus scanning.

---

## 🧠 Tricky Interview Question
"Your alpine-based Python image builds fine but `pip install` takes 10 minutes and compiles everything. Why, and what do you do?"

Answer: Many Python wheels are built for glibc (manylinux). Alpine uses musl, so pip falls back to compiling from source. Switch to `python:3.12-slim` (glibc) and wheels install in seconds. Alpine is smaller but not always faster or simpler.

---

## ⚫ Interview Questions + Answers

Q1: Difference between slim and alpine?
A1: Slim is trimmed Debian (glibc). Alpine is a different minimal distro (musl libc, apk).

Q2: What is a distroless image?
A2: An image with only the app runtime and no shell or package manager; very small attack surface, harder to debug.

Q3: What is `scratch`?
A3: An empty base; used for static binaries (Go, Rust).

Q4: Why pin the OS codename (bookworm)?
A4: So an automatic Debian release change does not alter your base unexpectedly.

Q5: How do you reduce CVEs in a base?
A5: Choose slim/distroless, rebuild often, scan with Trivy or Docker Scout, drop unneeded packages.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- slim: default choice for most Node/Python services.
- alpine: pure-JS apps, static Nginx, tiny tools.
- distroless/scratch: mature services needing minimum surface.

❌ Avoid when:
- alpine with heavy native/C-extension dependencies.
- Full images in production unless you really need the tools.

---

## 📊 Visual Diagram
```
 Size (approx)     Tools   Compat   Attack surface
 node:22 (full)    ~1GB    high     large
 node:22-slim      ~230MB  high     medium
 node:22-alpine    ~160MB  medium   small  (musl)
 distroless        ~120MB  app only very small (no shell)
 scratch           binary  static   minimal

 Multi-stage: [builder: fat] ──copy artefacts──► [runtime: slim, USER node]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Base image | Image in FROM | FROM वाली image |
| slim | Trimmed Debian | छोटा Debian |
| alpine | Tiny musl distro | छोटा musl distro |
| distroless | No shell/pkg manager | shell के बिना |
| musl / glibc | C libraries | C libraries |
| CVE | Known vulnerability | ज्ञात कमज़ोरी |

---

## ⚡ 3-Line Summary
English: The base image sets size, security and compatibility.
Default to official slim images; use alpine only after testing.
Pin versions, build multi-stage, rebuild and scan regularly.
Hindi: Base image size, security और compatibility तय करती है।
Official slim images default रखो; alpine सिर्फ test करके।
Version pin करो, multi-stage बनाओ, नियमित rebuild और scan करो।

---

## ➡️ Next Topic
**109. Official vs Community Images** - how to decide which publisher to trust for the images in your `FROM` line.
