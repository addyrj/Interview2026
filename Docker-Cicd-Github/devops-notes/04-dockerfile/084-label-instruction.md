# 084. LABEL Instruction
# हिंदी में: LABEL इंस्ट्रक्शन (Image Metadata)

---

## 🔵 Simple Definition (English)
`LABEL` adds key-value **metadata** to an image (author, version, source repository, license, description). Labels do not change how the app runs; they help humans, registries, scanners and automation to identify and filter images and containers.

## 🔵 सरल परिभाषा (Hindi)
`LABEL` image में key-value **metadata** जोड़ता है (author, version, source repository, license, description)। Labels app के चलने का तरीका नहीं बदलते; वे इंसानों, registries, scanners और automation को images और containers पहचानने व filter करने में मदद करते हैं।

---

## 🔴 Problem it Solves
Six months later you find an image `registry/api:latest` running on a server. Who built it? From which commit? Which repo? Is it still supported? Without metadata, you must guess. Labels bake this answer into the image. They also let tooling work: Traefik reads labels for routing, Prometheus/Watchtower use labels to select containers, and GitHub Container Registry links a package to its repo via `org.opencontainers.image.source`.

## 🔴 यह क्यों बना? (Hindi)
छह महीने बाद server पर `registry/api:latest` image चलती मिलती है। इसे किसने बनाया? किस commit से? किस repo से? क्या अभी supported है? Metadata के बिना अंदाज़ा लगाना पड़ता है। Labels यह जवाब image में ही रख देते हैं। Tooling भी इन पर चलती है: Traefik routing के लिए labels पढ़ता है, Prometheus/Watchtower containers चुनने के लिए, और GitHub Container Registry `org.opencontainers.image.source` से package को repo से जोड़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Add LABEL key=value lines in the Dockerfile (or --label at build/run time)
Step 2 → Labels are stored in image config (Config.Labels); each LABEL line adds a tiny layer entry
Step 3 → Child images inherit parent labels; same key in child overrides
Step 4 → Read:    docker inspect --format '{{json .Config.Labels}}' IMAGE
Step 5 → Filter:  docker images --filter "label=team=backend"
                  docker ps --filter "label=app=api"
Step 6 → Tools (registry UIs, Traefik, CI) consume them
```

Use the OCI standard keys (`org.opencontainers.image.*`) rather than inventing your own where possible.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Dockerfile में LABEL key=value लिखो (या build/run में --label)
Step 2 → Labels image config (Config.Labels) में save होते हैं
Step 3 → Child image parent के labels inherit करती है; वही key child में हो तो override होती है
Step 4 → पढ़ो:      docker inspect --format '{{json .Config.Labels}}' IMAGE
Step 5 → Filter:    docker images --filter "label=team=backend"
                    docker ps --filter "label=app=api"
Step 6 → Tools (registry UI, Traefik, CI) इन्हें use करते हैं
```

जहाँ संभव हो OCI standard keys (`org.opencontainers.image.*`) use करो, अपनी keys कम बनाओ।

---

## 🟡 Real World Example
Your team pushes images to GitHub Container Registry (GHCR). The Dockerfile sets `org.opencontainers.image.source=https://github.com/your-org/your-repo`. GHCR automatically links the package to the repo, shows the README and lets the repo's Actions token push with its default permissions. On the VPS, an engineer runs `docker ps --filter label=com.example.team=payments` during an incident to list only the payment-team containers. A scanner report maps CVEs to `org.opencontainers.image.revision` (the commit).

## 🟡 Real Example Hindi mein
आपकी team images GitHub Container Registry (GHCR) में push करती है। Dockerfile में `org.opencontainers.image.source=https://github.com/your-org/your-repo` है। GHCR package को repo से अपने-आप जोड़ देता है, README दिखाता है। VPS पर incident के दौरान engineer `docker ps --filter label=com.example.team=payments` चलाकर सिर्फ payment team के containers देखता है। Scanner report CVEs को `org.opencontainers.image.revision` (commit) से map करता है।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Basic LABEL example (Node.js API)
# Base image (example tag)
FROM node:20-alpine
# Simple labels: one per line, values quoted if they contain spaces
LABEL maintainer="devops@example.com"
# Human readable description
LABEL description="Orders API (Node.js)"
# Version of the app (static example)
LABEL version="1.0.0"
# Working directory
WORKDIR /app
# Copy source
COPY . .
# Install production dependencies
RUN npm ci --omit=dev
# Run unprivileged
USER node
# Start the app
CMD ["node", "server.js"]
```

```bash
# Build
docker build -t orders-api:1.0.0 .
# Show all labels as JSON
docker inspect --format '{{json .Config.Labels}}' orders-api:1.0.0
# List images with a particular label
docker images --filter "label=version=1.0.0"
```

## 💻 Code / Config Example — Advanced

```dockerfile
# syntax=docker/dockerfile:1
# Advanced: OCI labels filled by CI through ARGs (one LABEL instruction = one layer entry)
# Python slim base (example tag)
FROM python:3.12-slim
# Build metadata passed from CI (non-secret)
ARG APP_VERSION=dev
# Commit SHA from CI
ARG GIT_SHA=unknown
# Build timestamp in RFC 3339 format from CI
ARG BUILD_DATE=unknown
# Repository URL used by GHCR to link the package
ARG REPO_URL=https://github.com/your-org/your-repo
# Single LABEL instruction with several OCI standard keys
LABEL org.opencontainers.image.title="orders-fastapi" \
      org.opencontainers.image.description="Orders service (FastAPI)" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.revision="${GIT_SHA}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.source="${REPO_URL}" \
      org.opencontainers.image.licenses="MIT" \
      com.example.team="backend" \
      com.example.oncall="backend-oncall@example.com"
# Working directory
WORKDIR /app
# Dependencies
COPY requirements.txt .
# Install without cache
RUN pip install --no-cache-dir -r requirements.txt
# App code
COPY app ./app
# Non-root numeric user
USER 10001
# Start uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# .github/workflows/docker.yml: let docker/metadata-action generate labels automatically
name: docker-image
# Run on pushes to main
on:
  push:
    branches: [main]
jobs:
  build:
    # GitHub hosted runner
    runs-on: ubuntu-latest
    # Needed to push to GHCR with GITHUB_TOKEN
    permissions:
      contents: read
      packages: write
    steps:
      # Get the code
      - uses: actions/checkout@v4
      # Compute tags + OCI labels (version examples, update to current majors)
      - id: meta
        uses: docker/metadata-action@v5
        with:
          # Image name in GHCR
          images: ghcr.io/${{ github.repository }}
      # Log in to GHCR with the built-in token
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      # Build and push with labels from the metadata step
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          # Labels such as org.opencontainers.image.revision are added automatically
          labels: ${{ steps.meta.outputs.labels }}
```

---

## 🟠 My Stack Integration
- **Node.js / FastAPI / React images**: same label block in each Dockerfile; CI fills version and SHA.
- **GHCR**: `org.opencontainers.image.source` links the image to its repo and enables repo-based permissions.
- **Nginx on VPS (Traefik alternative)**: if you later use Traefik, routing rules live in container labels (`traefik.http.routers.api.rule=Host(...)`) in Compose, set at run time.
- **VPS operations**: `docker ps --filter label=...` and `docker image prune --filter "label=..."`/`until=` for cleanup.
- **AWS**: ECR scanning reports show image digest/tags; labels help map back to the repo/team. Tags in ECR are separate from labels.

```yaml
# docker-compose.yml: labels set at runtime for operations (not baked in image)
services:
  # API service
  api:
    # Image pulled from GHCR (example name)
    image: ghcr.io/your-org/orders-api:1.4.2
    # Runtime labels for ops tooling (filter in docker ps)
    labels:
      com.example.team: "backend"
      com.example.env: "production"
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting secrets or internal passwords in labels. Labels are plain text for anyone who can pull the image.
✅ Correct: Only non-sensitive metadata.

❌ Mistake 2: Using the deprecated `MAINTAINER` instruction.
✅ Correct: `LABEL org.opencontainers.image.authors="you@example.com"`.

❌ Mistake 3: Writing many `LABEL` lines and putting a changing label (build date) at the top, breaking cache for every later layer.
✅ Correct: Put volatile labels at the end of the Dockerfile (or pass via build tooling), and combine labels in one instruction.

❌ Mistake 4: Inventing keys such as `author` without namespacing, which collide with others.
✅ Correct: Use reverse-DNS names (`com.example.team`) or OCI keys.

---

## 🧠 Tricky Interview Question
Your base image sets `LABEL version="1.0"`. Your Dockerfile `FROM` that base does not set `version`. What does `docker inspect` of your image show for `version`, and how do you change it at build time without editing the Dockerfile?

Answer: It shows `1.0` because labels are inherited from the parent image. To override without editing the file, use `docker build --label version=2.0 .` (CLI labels override Dockerfile labels, and a child's same-key LABEL overrides the parent). This is exactly what `docker/metadata-action` does in CI.

---

## ⚫ Interview Questions + Answers

Q1: Do labels affect container behaviour?
A1: No. They are metadata only, but tools (Traefik, orchestrators) may act on them.

Q2: How do you view labels?
A2: `docker inspect IMAGE_OR_CONTAINER` (look for `Labels`) or with `--format '{{json .Config.Labels}}'`.

Q3: Which label links a GHCR package to a GitHub repo?
A3: `org.opencontainers.image.source`.

Q4: Replace for `MAINTAINER`?
A4: `LABEL org.opencontainers.image.authors=...`; MAINTAINER is deprecated.

Q5: Image labels vs container labels?
A5: Image labels are set at build time (`LABEL`, `--label` on build). Container labels are set at run time (`docker run --label`, Compose `labels:`) and are used for ops tooling and routing.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every production image: source, revision, version, owner.
- You use tools that discover things via labels (Traefik, monitoring discovery).
- You need to filter images/containers during operations.

❌ Avoid when:
- You are tempted to store config or secrets in them.
- The data changes per run (use runtime labels or env vars).

---

## 📊 Visual Diagram

```
 CI pipeline
   |  --build-arg GIT_SHA=abc123  (or metadata-action --label)
   v
 +-------------------------------+
 | Image  orders-api:1.4.2       |
 |  Labels:                      |
 |   ...image.source   = repo    |
 |   ...image.revision = abc123  |
 |   com.example.team  = backend |
 +---------------+---------------+
                 |
    +------------+-------------+--------------------+
    v                          v                    v
 GHCR links repo        docker ps --filter     Vulnerability scan
 to package             label=team=backend     report -> commit
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LABEL | Key-value metadata on image | image पर key-value metadata |
| OCI | Open Container Initiative standard | container का open standard |
| Reverse-DNS key | Namespaced key like com.example.x | namespace वाली key |
| MAINTAINER | Deprecated author field | पुराना author field |
| GHCR | GitHub Container Registry | GitHub की container registry |
| Revision | Git commit of the build | build का Git commit |

---

## ⚡ 3-Line Summary
English: LABEL stores non-secret metadata (source, version, commit, owner) in the image. Use OCI standard keys, set them from CI, and put volatile ones last. Tools and humans use labels to identify and filter images.
Hindi: LABEL image में non-secret metadata (source, version, commit, owner) रखता है। OCI standard keys use करो, CI से set करो, और बदलने वाली keys आखिर में रखो। Tools और लोग labels से images पहचानते और filter करते हैं।

---

## ➡️ Next Topic
**085. HEALTHCHECK Instruction**: metadata tells what an image is; a healthcheck tells whether the running container is actually working.
