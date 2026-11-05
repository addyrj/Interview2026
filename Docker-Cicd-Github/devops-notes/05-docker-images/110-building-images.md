# 110. Building Images
# हिंदी में: Images बनाना

---

## 🔵 Simple Definition (English)
**Building an image** means executing the instructions in a Dockerfile in order. Each instruction creates a read-only **layer**; the stack of layers is the image. Layers are cached and shared, so careful ordering makes builds fast.

## 🔵 सरल परिभाषा (Hindi)
**Image build करना** यानी Dockerfile की instructions को क्रम से चलाना। हर instruction एक read-only **layer** बनाती है; layers का stack ही image है। Layers cache और share होती हैं, इसलिए सही क्रम से builds तेज़ होते हैं।

---

## 🔴 Problem it Solves
- "Works on my machine": manual server setup differs on every machine.
- Installing Node, Python and system packages by SSH is slow and unrepeatable.
- Without a build step there is no versioned, shippable artifact for CI/CD.

## 🔴 यह क्यों बना? (Hindi)
- "मेरी machine पर चलता है": manual server setup हर machine पर अलग होता है।
- SSH से Node, Python और system packages install करना धीमा और non-repeatable है।
- Build step के बिना CI/CD के लिए versioned, shippable artifact नहीं होता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write Dockerfile (FROM, WORKDIR, COPY, RUN, CMD)
Step 2 → docker build sends the build context to the builder
Step 3 → Builder runs each instruction; creates a layer; stores cache key
Step 4 → Unchanged instruction + unchanged inputs = "CACHED", reused
Step 5 → A changed layer invalidates all layers AFTER it
Step 6 → Final layers + config JSON = image with an ID (digest); tag it
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Dockerfile लिखो (FROM, WORKDIR, COPY, RUN, CMD)
Step 2 → docker build build context को builder के पास भेजता है
Step 3 → Builder हर instruction चलाकर layer बनाता है; cache key रखता है
Step 4 → Instruction और inputs वही हों तो "CACHED" - दोबारा इस्तेमाल
Step 5 → कोई layer बदली तो उसके बाद की सारी layers invalid हो जाती हैं
Step 6 → Layers + config JSON = image (digest वाली); tag लगाओ
```

---

## 🟡 Real World Example
A Node.js API Dockerfile copies the whole project and runs `npm install` after. Every code edit re-installs 400 packages (3 minutes). After reordering (copy `package*.json`, `npm ci`, then copy source), code-only changes take 5 seconds because the dependency layer stays cached. On GitHub Actions this saves hours of runner time each week.

## 🟡 Real Example Hindi mein
एक Node.js API के Dockerfile में पूरा project copy होता है और फिर `npm install`। हर code edit पर 400 packages दोबारा install (3 मिनट)। क्रम बदलने (`package*.json` copy, `npm ci`, फिर source copy) के बाद सिर्फ code बदलने पर 5 सेकंड लगते हैं क्योंकि dependency layer cached रहती है। GitHub Actions पर यह हर हफ्ते घंटों का runner समय बचाता है।

---

## 💻 Code / Config Example — Basic
```dockerfile
# Start from official Node runtime (example tag)
FROM node:22.11.0-slim
# Set working directory inside the image
WORKDIR /app
# Copy only dependency files first (cache layer)
COPY package.json package-lock.json ./
# Install exact locked dependencies, no dev packages
RUN npm ci --omit=dev
# Copy the rest of the source (changes often, so it comes last)
COPY . .
# Document the listening port
EXPOSE 3000
# Default command when container starts
CMD ["node", "server.js"]
```

```bash
# Build the image from the current folder and tag it
docker build -t myorg/api:1.0.0 .
# Run it to test, mapping port 3000, remove container on exit
docker run --rm -p 3000:3000 myorg/api:1.0.0
```

## 💻 Code / Config Example — Advanced
```dockerfile
# syntax=docker/dockerfile:1
# ---- deps stage: install production dependencies once ----
FROM python:3.12.7-slim-bookworm AS deps
# Do not write .pyc files and flush logs immediately
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# Work dir
WORKDIR /app
# Create virtualenv that we can copy to the final stage
RUN python -m venv /opt/venv
# Put venv first on PATH
ENV PATH="/opt/venv/bin:$PATH"
# Copy only requirements for caching
COPY requirements.txt .
# Install packages without cache
RUN pip install --no-cache-dir -r requirements.txt

# ---- runtime stage: minimal final image ----
FROM python:3.12.7-slim-bookworm AS runtime
# Same env flags
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# Venv on PATH
ENV PATH="/opt/venv/bin:$PATH"
# Create an unprivileged user
RUN useradd --create-home --uid 10001 appuser
# App folder
WORKDIR /app
# Bring the venv from the deps stage
COPY --from=deps /opt/venv /opt/venv
# Copy application code with correct owner
COPY --chown=appuser:appuser . .
# Run as non-root
USER appuser
# FastAPI port
EXPOSE 8000
# Container-level health check using Python stdlib (no curl needed)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status==200 else 1)"
# Start the API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```
(Syntax checked by script only; not built locally.)

---

## 🟠 My Stack Integration
Build in CI, not on the VPS: GitHub Actions builds, pushes to GHCR/ECR, and the VPS only pulls. Keep one Dockerfile per service (`api/Dockerfile`, `web/Dockerfile`).

```yaml
# docker-compose.yml - build locally in dev, use pushed image in prod
services:
  api:
    # Build definition used in development
    build:
      context: ./api
      dockerfile: Dockerfile
    # Image name the build produces / prod pulls
    image: ghcr.io/myorg/api:${TAG:-dev}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `COPY . .` before installing dependencies.
✅ Correct: Copy dependency manifests first.

❌ Mistake 2: Separate `RUN apt-get update` and `RUN apt-get install` lines.
✅ Correct: Combine in one `RUN` (`apt-get update && apt-get install -y --no-install-recommends ... && rm -rf /var/lib/apt/lists/*`).

❌ Mistake 3: Baking secrets (`.env`, SSH keys) into a layer.
✅ Correct: Use BuildKit secret mounts and `.dockerignore`.

❌ Mistake 4: Running as root.
✅ Correct: Add `USER` with a non-root account.

---

## 🧠 Tricky Interview Question
"You `COPY .env .` then `RUN rm .env` in the next line. Is the secret gone from the image?"

Answer: No. The file exists in the earlier layer, and anyone who pulls the image can extract it (`docker save` or `docker history` plus layer unpacking). Deleting in a later layer only hides it. Use `RUN --mount=type=secret` or pass secrets at runtime.

---

## ⚫ Interview Questions + Answers

Q1: What is an image layer?
A1: A read-only filesystem diff created by an instruction (RUN, COPY, ADD).

Q2: Which instructions add layers?
A2: Mainly RUN, COPY, ADD. Others like ENV, CMD, EXPOSE only change metadata.

Q3: Why order instructions from least to most frequently changing?
A3: Cache invalidation cascades downward, so stable steps go first.

Q4: Image vs container?
A4: Image is the read-only template; container is a running instance with a writable layer on top.

Q5: How do multi-stage builds help?
A5: They leave compilers and dev dependencies behind, shrinking the final image and attack surface.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any service you deploy: build once in CI, run anywhere.

❌ Avoid when:
- Doing builds on a tiny production VPS (CPU/disk spikes); build in CI instead.
- Putting runtime configuration or secrets into the image.

---

## 📊 Visual Diagram
```
 Dockerfile              Layers (read-only)               Image
 FROM node:22-slim  ───► [ base layers          ]
 WORKDIR /app       ───► [ metadata            ]
 COPY package*.json ───► [ layer: manifests     ]  <- cached if unchanged
 RUN npm ci         ───► [ layer: node_modules  ]  <- cached if above unchanged
 COPY . .           ───► [ layer: source        ]  <- changes often
 CMD [...]          ───► [ metadata            ]  ══► myorg/api:1.0.0
                                       container adds a writable layer on top
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Layer | Filesystem diff | filesystem परत |
| Build cache | Reused layers | reuse होने वाली layers |
| Dockerfile | Build recipe | build का नुस्खा |
| Multi-stage | Several FROM stages | कई stages |
| Image ID/digest | Content identity | content पहचान |
| Writable layer | Container's top layer | container की ऊपरी layer |

---

## ⚡ 3-Line Summary
English: A build runs Dockerfile steps and produces layered, cacheable images.
Order steps from stable to changing to keep builds fast.
Never put secrets in layers; build in CI.
Hindi: Build Dockerfile के steps चलाकर layered, cacheable image बनाता है।
Stable से बदलने वाले क्रम में steps रखो ताकि build तेज़ रहे।
Layers में secrets मत डालो; CI में build करो।

---

## ➡️ Next Topic
**111. docker build Command** - the flags and options of the command that does all of this.
