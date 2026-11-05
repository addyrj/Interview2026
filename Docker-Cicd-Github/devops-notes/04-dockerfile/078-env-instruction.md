# 78. ENV Instruction
# हिंदी में: ENV Instruction (Environment variables)

---

## 🔵 Simple Definition (English)
`ENV KEY=value` sets an environment variable that exists both during later build steps and in every container started from the image. It is stored in image metadata, so anyone with the image can read it (`docker inspect`, `docker history`). It differs from `ARG`, which exists only at build time.

## 🔵 सरल परिभाषा (Hindi)
`ENV KEY=value` एक environment variable सेट करता है जो आगे के build steps में भी रहता है और इस image से चलने वाले हर container में भी। यह image metadata में रखा जाता है, इसलिए image रखने वाला कोई भी उसे पढ़ सकता है (`docker inspect`, `docker history`)। `ARG` अलग है: वह सिर्फ build के समय रहता है।

---

## 🔴 Problem it Solves
Apps need configuration (port, log level, runtime mode, `NODE_ENV`, `PYTHONUNBUFFERED`) without hardcoding it in code. ENV provides sensible defaults inside the image that can be overridden per environment at run time (`-e`, `--env-file`, Compose, Kubernetes). The danger: people put passwords in ENV, which leaks them in the image.

## 🔴 यह क्यों बना? (Hindi)
Apps को configuration (port, log level, runtime mode, `NODE_ENV`, `PYTHONUNBUFFERED`) चाहिए, code में hardcode किए बिना। ENV image के अंदर समझदार defaults देता है जिन्हें हर environment में run के समय बदला जा सकता है (`-e`, `--env-file`, Compose, Kubernetes)। खतरा: लोग passwords ENV में रख देते हैं, जिससे image में leak हो जाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → ENV NODE_ENV=production   is recorded in image config (metadata)
Step 2 → Later RUN steps see it (e.g. npm ci reads NODE_ENV)
Step 3 → Containers start with it already in their environment
Step 4 → docker run -e NODE_ENV=staging img   overrides at runtime
Step 5 → Later Dockerfile lines can expand it: WORKDIR $APP_HOME, COPY, ADD, USER, EXPOSE
Step 6 → CMD/ENTRYPOINT in exec form do NOT expand $VAR (no shell) -> use sh -c or app code
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → ENV NODE_ENV=production   image config (metadata) में दर्ज होता है
Step 2 → बाद के RUN steps उसे देखते हैं (जैसे npm ci, NODE_ENV पढ़ता है)
Step 3 → Containers उसी के साथ start होते हैं
Step 4 → docker run -e NODE_ENV=staging img   runtime पर बदल देता है
Step 5 → Dockerfile की बाद की lines उसे expand कर सकती हैं: WORKDIR $APP_HOME, COPY, ADD, USER, EXPOSE
Step 6 → Exec form में CMD/ENTRYPOINT $VAR expand नहीं करते (shell नहीं) -> sh -c या app code इस्तेमाल करो
```

---

## 🟡 Real World Example
A company put `ENV DB_PASSWORD=Pr0d!pass` in a Dockerfile for convenience and pushed the image to a public Docker Hub repo. Bots scraped it within hours and the production DB was accessed. Rotating credentials and moving to runtime secrets (AWS Secrets Manager / SSM Parameter Store, injected through the task or `--env-file` on the VPS) closed the hole. Non-secret defaults (`ENV PORT=8000`, `ENV PYTHONUNBUFFERED=1`) stayed in the Dockerfile.

## 🟡 Real Example Hindi mein
एक company ने सुविधा के लिए Dockerfile में `ENV DB_PASSWORD=Pr0d!pass` डाल दिया और image public Docker Hub repo पर push कर दी। Bots ने कुछ घंटों में उसे scrape किया और production DB में घुस गए। Credentials बदलकर runtime secrets (AWS Secrets Manager / SSM Parameter Store, task या VPS पर `--env-file` से inject) पर जाने से रास्ता बंद हुआ। Non-secret defaults (`ENV PORT=8000`, `ENV PYTHONUNBUFFERED=1`) Dockerfile में ही रहे।

---

## 💻 Code / Config Example — Basic
```dockerfile
# Dockerfile -- basic ENV usage (example tags)
FROM node:20-alpine
# Production mode: frameworks optimise, npm ci skips devDependencies by default
ENV NODE_ENV=production
# Default port the app listens on; override at runtime if needed
ENV PORT=3000
WORKDIR /app
COPY package*.json ./
# npm reads NODE_ENV during build as well
RUN npm ci
COPY . .
# Documentation of the port
EXPOSE 3000
# Exec form: app reads process.env.PORT itself
CMD ["node", "server.js"]
```

## 💻 Code / Config Example — Advanced
```dockerfile
# syntax=docker/dockerfile:1.7
# Dockerfile -- ENV vs ARG, derived variables and the runtime-secret pattern (example tags)
FROM python:3.12-slim
# Build-time only value (not in running container environment unless copied into ENV)
ARG APP_VERSION=dev
# Persist selected build-time value into the runtime environment (visible in docker inspect)
ENV APP_VERSION=${APP_VERSION}
# Several variables in ONE instruction = one metadata step; non-secret defaults only
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_HOME=/srv/api \
    PORT=8000
# Use a variable in later instructions
WORKDIR ${APP_HOME}
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# NEVER: ENV DATABASE_URL=postgres://user:pass@host/db  (visible to anyone with the image)
# Secrets arrive at runtime: docker run --env-file /etc/api.env  or Compose env_file / AWS Secrets Manager
# Exec form does not expand $PORT, so use a shell wrapper only when you need expansion; exec keeps signals
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
```
Dockerfile instructions were validated by script; not built locally. Build with `docker build --build-arg APP_VERSION=1.4.2 .`. Tags are examples.

---

## 🟠 My Stack Integration
Defaults in the Dockerfile, environment-specific values in Compose, secrets in `.env` files or a secret manager, never in Git.

```yaml
# docker-compose.yml -- runtime configuration on the VPS
services:                                      # services
  api:                                         # FastAPI service
    image: ghcr.io/addyrj/api:9fceb02          # example pinned image
    environment:                               # non-secret overrides, committed to Git is OK
      LOG_LEVEL: info                          # runtime log level
      PORT: "8000"                             # overrides Dockerfile ENV PORT
    env_file:                                  # secrets live in a file that is NOT in Git
      - /etc/addyrj/api.env                    # contains DATABASE_URL, JWT_SECRET (chmod 600)
  react:                                       # React build served by nginx
    build:                                     # build section
      context: ./web                           # folder
      args:                                    # build-time args (public values only!)
        VITE_API_URL: https://api.example.com  # baked into static JS bundle: never put secrets here
```
GitHub Actions: store secrets in Settings, Secrets and variables, then pass them to the deploy step as `env:`; never `echo` them. Ensure `.env` is in `.gitignore` and `.dockerignore`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Secrets in `ENV` or `ARG` (both visible via `docker history`/`inspect`).
✅ Correct: Runtime injection (`--env-file`, secret manager) or BuildKit `--mount=type=secret` for build-time needs.

❌ Mistake 2: Expecting `CMD ["node","app.js","--port","$PORT"]` to expand `$PORT`.
✅ Correct: Read `process.env.PORT` in code, or `CMD ["sh","-c","exec node app.js --port $PORT"]`.

❌ Mistake 3: `ENV` for a one-time build variable, such as `ENV DEBIAN_FRONTEND=noninteractive`, which then leaks into every container.
✅ Correct: Use `ARG DEBIAN_FRONTEND=noninteractive` or set it inline in the `RUN`.

❌ Mistake 4: Putting secret values in React `VITE_*`/`REACT_APP_*` variables, assuming they stay private.
✅ Correct: Those are compiled into public JavaScript; only put public config there.

---

## 🧠 Tricky Interview Question
Your Dockerfile has `ENV API_URL=http://localhost:8000`. In Compose you set `environment: API_URL=http://api:8000` and it works. But for your React build the URL is still localhost in the browser. Why?

Answer: React (Vite/CRA) reads variables at build time and inlines them into static JS. A runtime container env var does not change already compiled files. Use build args at image build time, or serve a `config.js` generated at container start (entrypoint script with `envsubst`), or let the browser call a relative `/api` path routed by Nginx.

---

## ⚫ Interview Questions + Answers

Q1: ENV vs ARG?
A1: ARG exists only during build (not in containers, unless copied to ENV). ENV persists in image metadata and runtime environment.

Q2: Precedence at runtime?
A2: `docker run -e` / Compose `environment` override Dockerfile `ENV`; `env_file` entries are overridden by `environment` entries.

Q3: Are ENV values secret?
A3: No. Anyone with the image can read them via `docker inspect` or `docker history`. Use secret stores.

Q4: Does each ENV create a layer?
A4: It creates a metadata-only entry; combine variables in one instruction for tidiness.

Q5: How do you see a container's environment?
A5: `docker exec c env`, `docker inspect --format '{{.Config.Env}}' c`, or `docker compose config` to see resolved values.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Non-secret defaults: `NODE_ENV`, `PORT`, `PYTHONUNBUFFERED`, `TZ`.
- Paths needed by later Dockerfile steps and at runtime (`PATH`, `APP_HOME`).

❌ Avoid when:
- Storing passwords, tokens or keys.
- Build-only toggles (use ARG).
- Config that differs per environment and should not be baked in.

---

## 📊 Visual Diagram
```
 Build time                                   Run time
 ARG APP_VERSION=dev  --(build-arg)-->  value only while building
 ENV APP_VERSION=${APP_VERSION} ------> image metadata ----> container env
                                              ^                    ^
                          docker inspect / history          docker run -e / env_file
                          (anyone can read!)                 (overrides at start)

 Secrets:  AWS Secrets Manager / .env (chmod 600) --runtime--> container   (NOT in image)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ENV | Persistent environment variable | स्थायी environment variable |
| ARG | Build-time only variable | सिर्फ build के समय का variable |
| env_file | File of KEY=value for runtime | Runtime के लिए KEY=value file |
| Secret manager | Service storing secrets | Secrets रखने की service |
| Inline substitution | $VAR expanded by shell | Shell द्वारा $VAR का expand होना |
| Metadata | Image config info | Image की config जानकारी |

---

## ⚡ 3-Line Summary
English: ENV sets persistent variables in the image and container; ARG is build-only. Anything in ENV or ARG can be read from the image, so keep secrets out and inject at runtime. Exec-form CMD does not expand variables.
Hindi: ENV image और container में स्थायी variables सेट करता है; ARG सिर्फ build के लिए है। ENV या ARG की कोई भी चीज़ image से पढ़ी जा सकती है, इसलिए secrets बाहर रखो और runtime पर दो। Exec-form CMD variables expand नहीं करता।

---

## ➡️ Next Topic
**79. EXPOSE and ARG details** — अगली instructions: port documentation, build arguments और उनका ENV से सही मेल।
