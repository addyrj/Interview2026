# 080. ENV vs ARG — Difference
# हिंदी में: ENV और ARG में अंतर

---

## 🔵 Simple Definition (English)
`ENV` sets an environment variable that is stored in the image and available **at build time and at runtime**. `ARG` sets a variable that exists **only at build time**. ENV is for app configuration; ARG is for build parameters.

## 🔵 सरल परिभाषा (Hindi)
`ENV` एक environment variable set करता है जो image में save रहता है और **build time और runtime दोनों** में मिलता है। `ARG` वाला variable **सिर्फ build time** में रहता है। ENV app configuration के लिए है; ARG build parameters के लिए।

---

## 🔴 Problem it Solves
Developers constantly mixed these two up. They put `NODE_ENV` in an `ARG` and wondered why the app ran in development mode, or put a version selector in `ENV` and polluted the runtime environment. Knowing the difference decides whether a value can be changed by `docker run -e` (ENV can, ARG cannot), whether it leaks into the final image, and whether the cache is reused.

## 🔴 यह क्यों बना? (Hindi)
Developers इन दोनों को अक्सर mix कर देते थे। `NODE_ENV` को `ARG` में डाल दिया और app development mode में चली, या version selector को `ENV` में डाल दिया और runtime environment गंदा हुआ। अंतर जानने से तय होता है कि value `docker run -e` से बदली जा सकती है (ENV हाँ, ARG नहीं), final image में leak होगी या नहीं, और cache reuse होगा या नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → ARG: you pass --build-arg at `docker build`; visible only to RUN etc. during build
Step 2 → ENV: written into image config (docker inspect -> Config.Env)
Step 3 → Container start: Docker loads image ENV into the process environment
Step 4 → `docker run -e KEY=other` overrides ENV; there is no equivalent for ARG
Step 5 → Common pattern: ARG VERSION -> ENV VERSION=$VERSION (bridge build -> runtime)
```

| Feature | ARG | ENV |
|---|---|---|
| Available during build | Yes | Yes (after the ENV line) |
| Available in running container | No | Yes |
| Set with | `--build-arg` | `ENV` line, `-e`, `--env-file` |
| Override at run | No | Yes |
| Can be used in `FROM` | Yes (before first FROM) | No |
| Stored in image config | Name/value in history | Yes, in Config.Env |
| Secrets safe? | No | No (also visible in `docker inspect`) |

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → ARG: `docker build` में --build-arg देते हो; सिर्फ build के दौरान RUN आदि को दिखता है
Step 2 → ENV: image config में लिख दिया जाता है (docker inspect -> Config.Env)
Step 3 → Container start: Docker image के ENV को process environment में load करता है
Step 4 → `docker run -e KEY=other` ENV को override करता है; ARG के लिए ऐसा कुछ नहीं
Step 5 → आम pattern: ARG VERSION -> ENV VERSION=$VERSION (build से runtime तक पुल)
```

---

## 🟡 Real World Example
A FastAPI service uses `ARG PYTHON_VERSION` to choose the base image (a pure build concern) and `ENV PYTHONUNBUFFERED=1` so logs flush immediately in `docker logs` (a runtime concern). It also sets `ENV LOG_LEVEL=info` as a default; on the VPS, the operator overrides it temporarily with `docker run -e LOG_LEVEL=debug` to debug an incident without rebuilding.

## 🟡 Real Example Hindi mein
एक FastAPI service base image चुनने के लिए `ARG PYTHON_VERSION` (build की चिंता) और `ENV PYTHONUNBUFFERED=1` (ताकि `docker logs` में log तुरंत दिखें, runtime की चिंता) इस्तेमाल करती है। `ENV LOG_LEVEL=info` default है; VPS पर incident debug करने के लिए operator बिना rebuild किए `docker run -e LOG_LEVEL=debug` से इसे अस्थायी रूप से बदल देता है।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Basic: ENV vs ARG side by side
# Base image (example tag, update to a current one)
FROM node:20-alpine
# ARG: exists only while building, not in the running container
ARG BUILD_DATE=unknown
# ENV: stored in the image, visible at runtime, overridable with -e
ENV NODE_ENV=production
# ENV: default port the app reads from process.env.PORT
ENV PORT=3000
# Working directory
WORKDIR /app
# Copy app files
COPY . .
# Use ARG at build time only
RUN echo "built on ${BUILD_DATE}" > /app/build-info.txt
# Start app
CMD ["node", "server.js"]
```

```bash
# Build passing the ARG
docker build --build-arg BUILD_DATE="$(date -u +%F)" -t demo .
# Prints NODE_ENV and PORT (ENV works at runtime); BUILD_DATE prints nothing (ARG is gone)
docker run --rm demo sh -c 'echo "$NODE_ENV $PORT [$BUILD_DATE]"'
# Override an ENV at run time
docker run --rm -e PORT=8080 demo sh -c 'echo $PORT'
```

## 💻 Code / Config Example — Advanced

```dockerfile
# syntax=docker/dockerfile:1
# Advanced: the ARG -> ENV bridge, safe secret handling, runtime overrides
# Pick base image version at build time
ARG PYTHON_VERSION=3.12
# Base image (slim variant, example tag)
FROM python:${PYTHON_VERSION}-slim AS runtime
# Re-declare ARGs inside this stage
ARG APP_VERSION=dev
# Commit SHA from CI
ARG GIT_SHA=unknown
# Bridge: copy ARGs into ENV so the app can expose /version
# Also set Python flags: no .pyc files, unbuffered logs
ENV APP_VERSION=${APP_VERSION} \
    GIT_SHA=${GIT_SHA} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOG_LEVEL=info \
    PORT=8000
# Working directory
WORKDIR /app
# Copy requirements first for cache efficiency
COPY requirements.txt .
# Install with the pip cache mounted (BuildKit), nothing left in the layer
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
# Copy the application code
COPY app ./app
# Create a non-root user (system user, no home, no login shell)
RUN useradd --system --no-create-home --shell /usr/sbin/nologin appuser
# Drop privileges
USER appuser
# Document the port
EXPOSE 8000
# Start uvicorn; shell form is avoided so signals reach the process
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Run with overrides: ENV values change per environment, no rebuild
docker run -d --name api -p 8000:8000 \
  -e LOG_LEVEL=debug \
  --env-file ./prod.env \
  myapi:1.4.2
# Check what the image carries
docker inspect --format '{{json .Config.Env}}' myapi:1.4.2
```

---

## 🟠 My Stack Integration
- **Node.js**: `ENV NODE_ENV=production` must be ENV (libraries read it at runtime). `ARG NODE_VERSION` is for the base image.
- **React**: Build-time values (`VITE_*`) are baked into JS, so use `ARG`. A runtime `ENV` on an Nginx container will NOT change already-built JS.
- **FastAPI**: `ENV PYTHONUNBUFFERED=1` for logs; settings (DB URL) come from runtime `-e`/secrets.
- **Nginx**: use `ENV` plus `envsubst` templates (official image supports `/etc/nginx/templates/*.template`) for runtime upstream hosts.
- **VPS / AWS**: store secrets in AWS SSM/Secrets Manager or `.env` on the server with `chmod 600`, never in `ENV` in the Dockerfile.

```yaml
# docker-compose.yml on the VPS: runtime ENV is overridden here, build ARG separate
services:
  # FastAPI backend
  api:
    build:
      # Where the Dockerfile lives
      context: ./backend
      # BUILD-time only (ARG)
      args:
        PYTHON_VERSION: "3.12"
    # RUNTIME env (overrides image ENV)
    environment:
      # Debug level for this environment
      LOG_LEVEL: info
    # Secrets / DB URL kept out of the image
    env_file:
      - ./prod.env
    # Restart automatically after reboot
    restart: unless-stopped
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `ARG NODE_ENV=production` and expecting Express to run in production mode.
✅ Correct: `ENV NODE_ENV=production`, or bridge: `ARG NODE_ENV=production` then `ENV NODE_ENV=$NODE_ENV`.

❌ Mistake 2: `ENV DB_PASSWORD=...` in the Dockerfile.
✅ Correct: Pass at runtime with `--env-file`, Docker/Compose secrets, or AWS Secrets Manager. Anyone with the image can read `ENV` via `docker inspect`.

❌ Mistake 3: Setting `ENV DEBIAN_FRONTEND=noninteractive` globally. It persists into the runtime image.
✅ Correct: Use it inline: `RUN DEBIAN_FRONTEND=noninteractive apt-get install -y ...`, or as an `ARG`.

❌ Mistake 4: Expecting `ENV` change at `docker run` to update a React bundle.
✅ Correct: Rebuild with the new `ARG`, or load config from a runtime `/config.js` served by Nginx.

---

## 🧠 Tricky Interview Question
A Dockerfile has `ARG TOKEN` and `ENV TOKEN=${TOKEN}`. You build with `--build-arg TOKEN=abc` and push. Later someone runs `docker run -e TOKEN=xyz IMAGE env`. What does the container print, and what is exposed?

Answer: It prints `TOKEN=xyz`, because runtime `-e` overrides the image ENV. But the image itself still contains `TOKEN=abc` in `Config.Env` (and in history), so anyone who pulls it sees `abc`. The bridging pattern made the build-time secret permanent. The fix is to not bake secrets, use `--secret` during build and runtime injection at start.

---

## ⚫ Interview Questions + Answers

Q1: Which one is available in a running container?
A1: `ENV`. `ARG` is build-only.

Q2: How do you override each?
A2: ARG with `docker build --build-arg`; ENV with `docker run -e`, `--env-file`, or compose `environment:`.

Q3: Can a variable be both?
A3: Yes, with the bridge pattern: `ARG X=default` then `ENV X=$X`. The build-arg sets the default baked into the image, and runtime can still override it.

Q4: If both an ARG and an ENV have the same name, which wins during build?
A4: The `ENV` value overrides the `ARG` value for instructions after the ENV line.

Q5: Why is `ENV` not safe for secrets?
A5: It is stored in image config and shown by `docker inspect` and `docker history`. Anyone with image or daemon access can read it.

---

## 🔷 When to Use + When Not to Use
✅ Use `ENV` when:
- App needs the value at runtime (`NODE_ENV`, `PORT`, `LOG_LEVEL`, `PYTHONUNBUFFERED`).
- You want a sensible default that operators can override.

✅ Use `ARG` when:
- Value affects only the build (base image version, build date, package mirror).
- You do not want the variable in the container environment.

❌ Avoid both when:
- The value is a secret. Use BuildKit secrets (build) or runtime secret stores (run).

---

## 📊 Visual Diagram

```
          BUILD TIME                          RUNTIME
  +-------------------------+        +---------------------------+
  |  ARG  --build-arg X=1   |        |  container process        |
  |    visible to RUN       |   X    |    ARG not visible        |
  |                         |        |                           |
  |  ENV  Y=2               | -----> |  ENV Y=2 (default)        |
  |    visible to RUN       | image  |    docker run -e Y=9      |
  |    stored in image      |        |    -> Y=9 (override)      |
  +-------------------------+        +---------------------------+
          ARG X -> ENV X=$X  (bridge pattern)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ENV | Persistent environment variable | स्थायी environment variable |
| ARG | Build-only variable | सिर्फ build का variable |
| Override | Replace default value | default value बदलना |
| Bridge pattern | ARG copied into ENV | ARG को ENV में copy करना |
| docker inspect | Shows image/container config | config दिखाने वाला command |
| env-file | File of KEY=VALUE lines | KEY=VALUE वाली file |

---

## ⚡ 3-Line Summary
English: ENV lives in the image and the running container; ARG lives only during the build. Use ENV for runtime config, ARG for build parameters, and the ARG-to-ENV bridge for metadata. Neither is safe for secrets.
Hindi: ENV image और चलते container में रहता है; ARG सिर्फ build के दौरान। Runtime config के लिए ENV, build parameters के लिए ARG, और metadata के लिए ARG से ENV का पुल। Secrets के लिए दोनों सुरक्षित नहीं हैं।

---

## ➡️ Next Topic
**081. EXPOSE Instruction**: after variables, learn how a container documents which ports it listens on, and why EXPOSE alone does not publish a port.
