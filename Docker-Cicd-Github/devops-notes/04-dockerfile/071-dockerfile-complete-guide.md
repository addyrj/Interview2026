# 71. Dockerfile — Complete Guide
# हिंदी में: Dockerfile — पूरी गाइड

---

## 🔵 Simple Definition (English)
A Dockerfile is a plain-text recipe of instructions (`FROM`, `COPY`, `RUN`, `CMD`, ...) that `docker build` executes top to bottom to produce an image. Each instruction that changes the filesystem creates a cached layer.

## 🔵 सरल परिभाषा (Hindi)
Dockerfile एक plain-text recipe है जिसमें instructions (`FROM`, `COPY`, `RUN`, `CMD`, ...) होते हैं, और `docker build` उन्हें ऊपर से नीचे चलाकर image बनाता है। Filesystem बदलने वाली हर instruction एक cached layer बनाती है।

---

## 🔴 Problem it Solves
Setting up a server by hand (install Node, copy code, set env) is slow, undocumented and different on every machine. A Dockerfile makes the environment code: versioned in Git, reviewable, rebuildable by CI, identical on laptop, VPS and AWS. It also makes layer caching possible so rebuilds take seconds.

## 🔴 यह क्यों बना? (Hindi)
Server को हाथ से setup करना (Node install, code copy, env set) धीमा, बिना documentation और हर machine पर अलग होता है। Dockerfile environment को code बना देता है: Git में versioned, review होने लायक, CI से rebuild, और laptop, VPS, AWS पर एक जैसा। Layer caching से rebuild कुछ seconds में होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → docker build -t app:1.0 .     (the "." is the build context sent to the daemon)
Step 2 → .dockerignore filters the context (node_modules, .git, .env are skipped)
Step 3 → FROM pulls the base image
Step 4 → Each COPY/RUN/ADD creates a new layer; unchanged steps reuse the cache
Step 5 → Once one step's cache is invalidated, ALL following steps rebuild
Step 6 → Metadata instructions (ENV, EXPOSE, CMD, USER, LABEL) set runtime config
Step 7 → Final image is tagged; docker run starts a container with CMD/ENTRYPOINT
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → docker build -t app:1.0 .     ("." build context है जो daemon को भेजा जाता है)
Step 2 → .dockerignore context छानता है (node_modules, .git, .env छूट जाते हैं)
Step 3 → FROM base image pull करता है
Step 4 → हर COPY/RUN/ADD नई layer बनाता है; जो step बदला नहीं उसका cache चलता है
Step 5 → एक step का cache टूटा तो उसके बाद के सारे steps दोबारा चलते हैं
Step 6 → Metadata instructions (ENV, EXPOSE, CMD, USER, LABEL) runtime config देती हैं
Step 7 → Final image tag होती है; docker run CMD/ENTRYPOINT से container चलाता है
```

---

## 🟡 Real World Example
Your React + Node.js project: the Dockerfile copies only `package*.json` first and runs `npm ci`, then copies source. When you change one `.jsx` file, Docker reuses the dependency layer and only rebuilds the last steps: a 4-minute build becomes 15 seconds in GitHub Actions. Companies like Swiggy keep one Dockerfile per microservice in the same repo as the code.

## 🟡 Real Example Hindi mein
आपका React + Node.js project: Dockerfile पहले सिर्फ `package*.json` copy करके `npm ci` चलाती है, फिर source copy करती है। एक `.jsx` file बदलने पर dependency layer reuse होती है और सिर्फ आख़िरी steps rebuild होते हैं: 4 मिनट का build GitHub Actions में 15 seconds का हो जाता है। Swiggy जैसी companies हर microservice की Dockerfile उसके code वाले repo में रखती हैं।

---

## 💻 Code / Config Example — Basic
```dockerfile
# Dockerfile -- minimal Node.js API (example versions, update them)
# small base image with Node 20
FROM node:20-alpine
# all following paths are relative to /app
WORKDIR /app
# copy only manifests first to cache the dependency layer
COPY package*.json ./
# clean, lockfile-exact install of production deps
RUN npm ci --omit=dev
# copy the rest of the source code
COPY . .
# documentation: app listens on 3000 (does not publish)
EXPOSE 3000
# default start command in exec form
CMD ["node", "server.js"]
```

## 💻 Code / Config Example — Advanced
```dockerfile
# syntax=docker/dockerfile:1.7
# Dockerfile -- production multi-stage build for FastAPI (example versions)
# stage 1: build dependencies, named "builder"
FROM python:3.12-slim AS builder
# keep layer small, no .pyc files
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1
# working dir for the build stage
WORKDIR /build
# copy only requirements to maximise cache hits
COPY requirements.txt .
# install deps into an isolated venv
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install -r requirements.txt

# stage 2: small runtime image, no build tools
FROM python:3.12-slim AS runtime
# use venv binaries, unbuffered logs for docker logs
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1
# create non-root user
RUN groupadd -r app && useradd -r -g app app
# app directory
WORKDIR /app
# take only the finished venv from stage 1
COPY --from=builder /opt/venv /opt/venv
# copy source with correct owner
COPY --chown=app:app ./app ./app
# run as non-root (security)
USER app
# document the port
EXPOSE 8000
# container health probe
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request as u;u.urlopen('http://127.0.0.1:8000/health')" || exit 1
# exec-form start, receives SIGTERM
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
Instruction names and stage references were checked with a script; the image was not built here (no Docker daemon). Update tags regularly.

---

## 🟠 My Stack Integration
One Dockerfile per service, built by CI, run behind Nginx on the VPS.

```yaml
# docker-compose.yml -- builds the Dockerfiles above and wires Nginx in front
services:                                  # services in the stack
  api:                                     # FastAPI service
    build:                                 # build from local Dockerfile
      context: ./api                       # build context folder
      dockerfile: Dockerfile               # file name inside context
    env_file: .env.api                     # runtime secrets, not baked into image
    expose: ["8000"]                       # visible to other containers only
  web:                                     # React static site served by nginx
    build: ./web                           # context with its own Dockerfile
    expose: ["80"]                         # internal port
  nginx:                                   # edge proxy (TLS, routing)
    image: nginx:1.27-alpine               # example tag
    ports: ["80:80", "443:443"]            # only Nginx is public
    depends_on: [api, web]                 # start order
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `COPY . .` before `npm ci`/`pip install`, so every code change reinstalls dependencies.
✅ Correct: Copy manifests, install, then copy source.

❌ Mistake 2: Running as root and using `latest` base tags.
✅ Correct: `USER app` and pinned tags (or digests); scan with Trivy.

❌ Mistake 3: Missing `.dockerignore`, shipping `.git`, `node_modules`, `.env` into the context/image.
✅ Correct: Add `.dockerignore`; secrets go in runtime env or BuildKit secrets.

❌ Mistake 4: Separate `RUN apt-get update` and `RUN apt-get install` lines.
✅ Correct: Combine in one `RUN` with `--no-install-recommends` and cleanup of `/var/lib/apt/lists/*`.

---

## 🧠 Tricky Interview Question
You deleted a secret file in a later `RUN rm secret.key`, yet `docker history` or layer extraction reveals it. Why?

Answer: Each instruction creates an immutable layer. The earlier `COPY secret.key` layer still contains the file; `rm` only adds a whiteout in a newer layer. Anyone pulling the image can extract the earlier layer. Use BuildKit secrets (`RUN --mount=type=secret`), multi-stage builds that never copy the secret into the final stage, and rotate the leaked key.

---

## ⚫ Interview Questions + Answers

Q1: What is the build context?
A1: The directory (and files) sent to the daemon with `docker build`. `COPY` can only read from inside it. Keep it small with `.dockerignore`.

Q2: How does layer caching work?
A2: Docker compares instruction text and, for COPY/ADD, file checksums. If identical to a cached layer, it reuses it; the first miss invalidates all later layers.

Q3: Why multi-stage builds?
A3: Build tools and sources stay in earlier stages; the final image carries only runtime artifacts, so it is smaller and has fewer vulnerabilities.

Q4: Does `EXPOSE` open a port?
A4: No. It documents. You publish with `-p` or Compose `ports`.

Q5: Which instructions create layers?
A5: `RUN`, `COPY`, `ADD` add filesystem layers; others add metadata only.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need reproducible images for any service.
- CI/CD builds and deploys containers.
- Standardising dev, staging and prod environments.

❌ Avoid when:
- A managed platform builds from source for you (buildpacks) and you need no customisation.
- Trying to bake runtime secrets or environment-specific config into the image.
- Using it as a shell script replacement for many unrelated steps.

---

## 📊 Visual Diagram
```
 Dockerfile                    docker build                         Image (layers)
 FROM node:20-alpine   --->  [ layer: base os + node ]  (cached)   +-----------------+
 COPY package*.json    --->  [ layer: manifests ]       (cached)   | CMD node server |
 RUN npm ci            --->  [ layer: node_modules ]    (cached)   | app source      |
 COPY . .              --->  [ layer: source ]          (rebuilt)  | node_modules    |
 CMD [...]             --->  [ metadata ]                          | node base       |
                                                                   +-----------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Build context | Files sent to builder | Builder को भेजी गई files |
| Layer | Cached filesystem step | Cached filesystem step |
| Multi-stage | Several FROMs, copy results | कई FROM वाला build |
| .dockerignore | Exclude list for context | Context से बाहर रखने की list |
| BuildKit | Modern build engine | आधुनिक build engine |
| HEALTHCHECK | Command checking container health | Container की सेहत जाँच |

---

## ⚡ 3-Line Summary
English: A Dockerfile is a versioned build recipe; each step is a cached layer. Order steps from least to most frequently changing, use multi-stage builds, non-root users and `.dockerignore`.
Hindi: Dockerfile versioned build recipe है; हर step एक cached layer है। Steps को कम बदलने वाले से ज़्यादा बदलने वाले क्रम में रखो, multi-stage, non-root user और `.dockerignore` इस्तेमाल करो।

---

## ➡️ Next Topic
**72. FROM Instruction** — हर Dockerfile की पहली instruction: base image कैसे चुनें और pin करें।
