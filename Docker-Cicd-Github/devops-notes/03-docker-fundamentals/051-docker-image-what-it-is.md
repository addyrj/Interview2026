# 51. Docker Image — What it is
# हिंदी में: Docker Image क्या है

---

## 🔵 Simple Definition (English)
A **Docker image** is a read-only, layered package containing everything needed to run an application: filesystem (OS userland, runtime, libraries, your code), plus metadata (default command, env, exposed ports, user). It is built from a **Dockerfile**, identified by a **tag** and an immutable **digest**, and stored in a registry. An image never runs by itself; a **container** is created from it.

## 🔵 सरल परिभाषा (Hindi)
**Docker image** एक read-only, layers वाला package है जिसमें application चलाने की हर चीज़ होती है: filesystem (OS userland, runtime, libraries, आपका code) और metadata (default command, env, exposed ports, user)। यह **Dockerfile** से बनती है, **tag** और अटल **digest** से पहचानी जाती है, और registry में रखी जाती है। Image खुद नहीं चलती; उससे **container** बनता है।

---

## 🔴 Problem it Solves
Deploying by copying code and running install scripts on each server gives inconsistent results (different OS patches, missing libs). Images make the *result* of the setup the artifact: build once, test it, ship the same bytes everywhere. Layering means a change in your code re-sends only a few KB instead of the whole OS, and unchanged layers are cached and shared across images.

## 🔴 यह क्यों बना? (Hindi)
हर server पर code कॉपी करके install scripts चलाने से नतीजे अलग-अलग आते हैं (OS patches, missing libs)। Images setup के *नतीजे* को ही artifact बना देती हैं: एक बार build, test, और वही bytes हर जगह। Layers का मतलब है कि code बदलने पर सिर्फ़ कुछ KB दोबारा भेजने पड़ते हैं, पूरा OS नहीं, और न बदली layers cache होती और images में share होती हैं।

---

## 🟢 How it Works — Step by Step

```
Dockerfile instruction          ->  resulting layer
FROM node:20-slim               ->  base layers (OS + Node), shared with other images
WORKDIR /app                    ->  metadata only (no size)
COPY package*.json ./           ->  layer: the two files
RUN npm ci --omit=dev           ->  layer: node_modules
COPY . .                        ->  layer: source code
CMD ["node","server.js"]        ->  metadata only

Step 1 → Each filesystem-changing instruction makes a new read-only layer (a tar diff), named by sha256
Step 2 → Image manifest = ordered list of layer digests + config JSON (env, cmd, user, ports)
Step 3 → Image ID / digest = hash of that content -> identical content = identical ID
Step 4 → Build cache: if instruction + inputs are unchanged, the old layer is reused
Step 5 → Cache is invalidated from the first changed layer downward (order matters!)
Step 6 → docker run adds one thin writable layer on top (copy-on-write)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Dockerfile instruction          ->  नतीजा layer
FROM node:20-slim               ->  base layers (OS + Node), दूसरी images के साथ share
WORKDIR /app                    ->  सिर्फ़ metadata (size नहीं)
COPY package*.json ./           ->  layer: दो files
RUN npm ci --omit=dev           ->  layer: node_modules
COPY . .                        ->  layer: source code
CMD ["node","server.js"]        ->  सिर्फ़ metadata

Step 1 → Filesystem बदलने वाली हर instruction नई read-only layer (tar diff) बनाती है, नाम sha256
Step 2 → Image manifest = layer digests की क्रम से सूची + config JSON (env, cmd, user, ports)
Step 3 → Image ID / digest = उस content का hash -> वही content = वही ID
Step 4 → Build cache: instruction + inputs न बदले तो पुरानी layer दोबारा इस्तेमाल
Step 5 → पहली बदली layer से नीचे की सारी cache invalid हो जाती है (क्रम मायने रखता है!)
Step 6 → docker run ऊपर एक पतली writable layer जोड़ता है (copy-on-write)
```

---

## 🟡 Real World Example
A team's Node.js build went from 4 minutes to 20 seconds by reordering the Dockerfile: they copied `package.json` and ran `npm ci` *before* copying the source, so editing a React component no longer invalidated the dependency layer. Another team shrank a FastAPI image from 1.2 GB to 150 MB by using `python:3.12-slim` and a multi-stage build, so VPS pulls and ECR storage got cheaper and the attack surface smaller.

## 🟡 Real Example Hindi mein
एक team का Node.js build 4 मिनट से 20 सेकंड हुआ सिर्फ़ Dockerfile का क्रम बदलकर: उन्होंने source copy करने से *पहले* `package.json` copy करके `npm ci` चलाया, इसलिए React component बदलने पर dependency layer invalid नहीं हुई। दूसरी team ने FastAPI image 1.2 GB से 150 MB की `python:3.12-slim` और multi-stage build से, इसलिए VPS pull और ECR storage सस्ता और attack surface छोटा हुआ।

---

## 💻 Code / Config Example — Basic
```dockerfile
# Dockerfile - Node.js API, layer-cache friendly order
# Base image (example tag; update to a current LTS)
FROM node:20-slim
# Set working directory (created if missing)
WORKDIR /app
# 1) Copy ONLY dependency manifests: this layer changes rarely
COPY package.json package-lock.json ./
# 2) Install dependencies: cached until the manifests change
RUN npm ci --omit=dev
# 3) Copy the source: changes often, so it comes last
COPY . .
# Document the listening port
EXPOSE 3000
# Run as the unprivileged "node" user that ships in the official image
USER node
# Start the server (exec form so signals reach Node)
CMD ["node", "server.js"]
```

```bash
# Inspect an image (needs a Docker daemon)
docker build -t myapi:1.0 .                    # build and tag
docker images myapi                            # size, ID, creation time
docker history myapi:1.0                       # layer-by-layer sizes and the instruction that made each
docker inspect myapi:1.0 --format '{{.Config.Cmd}} {{.Config.ExposedPorts}}'   # metadata
docker image inspect myapi:1.0 --format '{{json .RootFS.Layers}}'              # layer digests
docker save myapi:1.0 -o myapi.tar             # export image to a tar (offline transfer)
docker load -i myapi.tar                       # import it on another machine
```

## 💻 Code / Config Example — Advanced
```dockerfile
# Dockerfile - multi-stage React build served by Nginx (small, non-root, no build tools in final image)
# syntax=docker/dockerfile:1
# ---------- Stage 1: build ----------
# Example tag; node is only needed at build time
FROM node:20-slim AS build
# Working directory for the build stage
WORKDIR /src
# Manifests first for dependency caching
COPY package.json package-lock.json ./
# BuildKit cache mount keeps the npm download cache between builds (needs BuildKit, default in modern Docker)
RUN --mount=type=cache,target=/root/.npm npm ci
# Copy the app source
COPY . .
# Produce static files into /src/dist (Vite default; CRA uses build/)
RUN npm run build

# ---------- Stage 2: runtime ----------
# Unprivileged Nginx variant (runs as non-root, listens on 8080) - example tag
FROM nginxinc/nginx-unprivileged:1.27-alpine AS runtime
# Copy only the built static files from stage 1 (node_modules and sources are left behind)
COPY --from=build /src/dist /usr/share/nginx/html
# Custom Nginx config (SPA fallback to index.html), written by you in ./nginx/default.conf
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
# Unprivileged image listens on 8080
EXPOSE 8080
# Container is healthy if the homepage responds
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD wget -qO- http://localhost:8080/ >/dev/null || exit 1
```

---

## 🟠 My Stack Integration
```dockerfile
# Dockerfile for the FastAPI service - slim base, cache-friendly layers, non-root
FROM python:3.12-slim
# Python: no .pyc files, unbuffered logs (shows up instantly in docker logs)
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# Work directory
WORKDIR /app
# Install dependencies first (cached layer)
COPY requirements.txt .
# --no-cache-dir keeps the layer small
RUN pip install --no-cache-dir -r requirements.txt
# Copy application code last
COPY . .
# Non-root user
RUN useradd --system --uid 10001 appuser
# Drop privileges
USER appuser
# Start the API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```
```text
# .dockerignore - keep junk and secrets out of the build context and layers
node_modules
.git
.env
*.log
dist
__pycache__
```
Nginx on the VPS proxies to containers by name; CI builds/pushes the three images (Node API, FastAPI, React+Nginx) to GHCR/ECR tagged with the commit SHA.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `COPY . .` before installing dependencies.
✅ Correct: Copy manifests -> install -> copy source, to keep the dependency layer cached.

❌ Mistake 2: Deleting a secret in a later layer (`RUN rm .env`).
✅ Correct: Layers are additive; the file stays in the earlier layer. Never copy secrets; use BuildKit `--mount=type=secret` or runtime env.

❌ Mistake 3: Shipping build tools and dev dependencies in the final image.
✅ Correct: Multi-stage builds, `--omit=dev`, slim/alpine/distroless bases.

❌ Mistake 4: `apt-get update` and `install` in separate `RUN` lines.
✅ Correct: Combine and clean: `RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*`.

---

## 🧠 Tricky Interview Question
"Your image is 900 MB. You add `RUN rm -rf /app/big-data` at the end of the Dockerfile. The image is still 900 MB. Why, and how do you fix it?"

Answer: Layers are immutable and stacked: the `rm` creates a new layer that only *hides* the files; the earlier layer holding them still ships. Fix by never adding the data (use `.dockerignore`), doing download-use-delete in a single `RUN`, or using a multi-stage build where the final stage copies only what it needs. The same reason explains why deleted secrets remain recoverable from image layers.

---

## ⚫ Interview Questions + Answers

Q1: What is a Docker image?
A1: A read-only, layered, content-addressed bundle of filesystem + metadata used as a template to start containers.

Q2: Tag vs digest vs image ID?
A2: Tag: movable label (`1.0`). Digest: sha256 of the manifest in a registry, immutable. Image ID: sha256 of the local image config.

Q3: How does layer caching work?
A3: Each instruction's cache key includes the parent layer and its inputs (for COPY, file checksums). First miss invalidates all later layers, so put rarely-changing steps first.

Q4: Base image options and trade-offs?
A4: `slim` (Debian minimal, good compatibility), `alpine` (tiny, musl libc may break some native modules), `distroless` (no shell, smallest attack surface, harder to debug), `scratch` (empty, for static binaries).

Q5: How do you scan and sign images?
A5: Scan with Trivy/Docker Scout/ECR scanning in CI; sign with cosign; pin by digest; rebuild regularly for base-image patches.

---

## 🔷 When to Use + When Not to Use
✅ Use small, pinned, multi-stage images when:
- Any production deploy; CI/CD artifacts

❌ Avoid when:
- Treating images as mutable servers (patching inside a running container); rebuild instead

---

## 📊 Visual Diagram
```
   IMAGE (read-only, shared)                         CONTAINER (runtime)
 +-----------------------------+                +-----------------------------+
 | Layer 5: CMD/EXPOSE (meta)  |                | Writable layer (thin, temp) | <- docker rm deletes this
 | Layer 4: COPY . .   (code)  |   docker run   +-----------------------------+
 | Layer 3: npm ci (node_mods) | ------------>  | Layer 4: code     (read-only)|
 | Layer 2: COPY package*.json |                | Layer 3: node_mods (r/o)     |
 | Layer 1: node:20-slim (base)|                | Layer 1-2 ...      (r/o)     |
 +-----------------------------+                +-----------------------------+
   identified by sha256 digests; unchanged layers cached/shared; change layer 4 -> only 4 (and above) rebuild
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Image | Read-only app package | app का read-only package |
| Layer | One filesystem diff | filesystem का एक बदलाव-परत |
| Dockerfile | Build instructions | build निर्देश |
| Tag | Version label | version नाम |
| Digest | sha256 immutable ID | अटल sha256 पहचान |
| Multi-stage build | Build in one stage, ship another | एक stage में build, दूसरे में ship |
| .dockerignore | Exclude files from context | build से फ़ाइलें बाहर रखना |

---

## ⚡ 3-Line Summary
English: An image is a read-only layered package of filesystem and metadata built from a Dockerfile.
English: Order Dockerfile steps for caching, keep images small with multi-stage builds, and never bake secrets in.
English: Deploy by immutable tag or digest and rebuild to patch, instead of changing running containers.
Hindi: Image Dockerfile से बना filesystem और metadata का read-only layered package है।
Hindi: Caching के लिए Dockerfile का क्रम रखो, multi-stage से image छोटी रखो, और secrets कभी मत डालो।
Hindi: Immutable tag या digest से deploy करो और patch के लिए rebuild करो, चलते container को मत बदलो।

---

## ➡️ Next Topic
**52. Docker Container - What it is** - what happens when an image is run: lifecycle, states, writable layer, and restart behavior.
