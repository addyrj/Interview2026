# 113. Build Arguments
# हिंदी में: Build Arguments

---

## 🔵 Simple Definition (English)
A **build argument** is a variable declared with `ARG` in a Dockerfile and set at build time with `--build-arg NAME=value`. It exists only during the build (unlike `ENV`, which persists in the running container). Build args are visible in image history, so never put secrets in them.

## 🔵 सरल परिभाषा (Hindi)
**Build argument** Dockerfile में `ARG` से declare किया गया variable है जिसकी value build के समय `--build-arg NAME=value` से दी जाती है। यह सिर्फ build के दौरान रहता है (`ENV` की तरह running container में नहीं)। Build args image history में दिखते हैं, इसलिए इनमें secrets कभी न डालें।

---

## 🔴 Problem it Solves
- One Dockerfile must serve many versions (Node 20/22, different app version) without editing the file.
- Build-time values (app version, git SHA, proxy URL, `VITE_API_URL` for React) are needed during the build.
- Hard-coding values forces copies of Dockerfiles for each environment.

## 🔴 यह क्यों बना? (Hindi)
- एक Dockerfile को file बदले बिना कई versions (Node 20/22, अलग app version) के लिए चलना चाहिए।
- Build के दौरान app version, git SHA, proxy URL, React का `VITE_API_URL` जैसी values चाहिए।
- Values hard-code करने पर हर environment के लिए Dockerfile की copies बनानी पड़ती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Declare: ARG NODE_VERSION=22   (default value optional)
Step 2 → ARG before FROM can be used in FROM; it is out of scope after FROM unless redeclared
Step 3 → Run: docker build --build-arg NODE_VERSION=20 .
Step 4 → Use inside: RUN echo $NODE_VERSION  or  ENV APP_VERSION=$APP_VERSION
Step 5 → ARG disappears from the final container env (unless copied to ENV)
Step 6 → Values still appear in `docker history` - they are NOT secret
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Declare करो: ARG NODE_VERSION=22   (default value optional)
Step 2 → FROM से पहले का ARG FROM में चलता है; FROM के बाद दोबारा declare करना पड़ता है
Step 3 → चलाओ: docker build --build-arg NODE_VERSION=20 .
Step 4 → अंदर इस्तेमाल: RUN echo $NODE_VERSION  या  ENV APP_VERSION=$APP_VERSION
Step 5 → ARG final container के env में नहीं रहता (जब तक ENV में copy न करो)
Step 6 → Values `docker history` में फिर भी दिखती हैं - ये secret नहीं हैं
```

---

## 🟡 Real World Example
A React (Vite) frontend needs the API URL baked into the JS bundle: `VITE_API_URL`. CI builds `web` once for staging with `--build-arg VITE_API_URL=https://staging-api.example.com` and again for production with the production URL. A developer once passed `--build-arg NPM_TOKEN=...` to install private packages; the token appeared in `docker history` of the public image. They moved to a BuildKit secret mount and rotated the token.

## 🟡 Real Example Hindi mein
एक React (Vite) frontend को API URL JS bundle में चाहिए: `VITE_API_URL`। CI staging के लिए `--build-arg VITE_API_URL=https://staging-api.example.com` से और production के लिए production URL से `web` build करता है। एक developer ने private packages के लिए `--build-arg NPM_TOKEN=...` दिया था; token public image के `docker history` में दिख गया। उन्होंने BuildKit secret mount अपनाया और token rotate किया।

---

## 💻 Code / Config Example — Basic
```dockerfile
# ARG before FROM: usable in the FROM line (default 22.11.0)
ARG NODE_VERSION=22.11.0
# Use the argument to choose the base image tag
FROM node:${NODE_VERSION}-slim
# ARG used after FROM must be declared again
ARG APP_VERSION=0.0.0-dev
# Convert to ENV only if the running app needs it
ENV APP_VERSION=${APP_VERSION}
# Work dir
WORKDIR /app
# Copy manifests, install, copy code
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
# Start the app
CMD ["node", "server.js"]
```

```bash
# Override the defaults at build time
docker build --build-arg NODE_VERSION=20.18.0 --build-arg APP_VERSION=1.2.3 -t myorg/api:1.2.3 .
```

## 💻 Code / Config Example — Advanced
```dockerfile
# syntax=docker/dockerfile:1
# Build React with a build-time API URL, serve with Nginx
ARG NODE_VERSION=22.11.0
# ---- build stage ----
FROM node:${NODE_VERSION}-slim AS build
# Public (non-secret) URL baked into the bundle
ARG VITE_API_URL=http://localhost:8000
# Vite reads variables prefixed with VITE_ from the environment
ENV VITE_API_URL=${VITE_API_URL}
WORKDIR /app
COPY package*.json ./
# BuildKit secret mount: token is available only during this RUN, not stored in layers
# (the .npmrc is created from the secret file at /run/secrets/npmrc)
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci
COPY . .
# Produce static files in /app/dist
RUN npm run build

# ---- runtime stage ----
FROM nginx:1.27-alpine
# Copy built static files
COPY --from=build /app/dist /usr/share/nginx/html
# Custom Nginx config for SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

```bash
# Pass a public arg and a secret file; secret never lands in history
docker build \
  --build-arg VITE_API_URL=https://api.example.com \
  --secret id=npmrc,src=$HOME/.npmrc \
  -t myorg/web:1.0.0 .
```
(Not built locally. `--mount=type=secret` needs BuildKit, the default builder in current Docker.)

---

## 🟠 My Stack Integration
- **React**: API URL, feature flags (public values) -> `ARG` to `ENV VITE_*`.
- **Node/FastAPI**: version/SHA labels; runtime config (DB URL, keys) goes in container env or secrets, NOT build args.
- **GitHub Actions**: pass `${{ github.sha }}` as `APP_VERSION`.

```yaml
# build-push step passing build args from GitHub Actions
- uses: docker/build-push-action@v6
  with:
    context: ./web
    push: true
    tags: ghcr.io/myorg/web:${{ github.sha }}
    build-args: |
      VITE_API_URL=https://api.example.com
      APP_VERSION=${{ github.sha }}
    secrets: |
      npmrc=${{ secrets.NPMRC }}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Passing passwords or tokens via `--build-arg`.
✅ Correct: `--secret` with `RUN --mount=type=secret`.

❌ Mistake 2: Using ARG after FROM without redeclaring.
✅ Correct: Declare `ARG NAME` again inside each stage that needs it.

❌ Mistake 3: Expecting `ARG` to be available when the container runs.
✅ Correct: Use `ENV` (or runtime `-e`) for runtime values.

❌ Mistake 4: Changing a build arg value on every build (like a timestamp) early in the Dockerfile.
✅ Correct: Place volatile ARGs late; they bust cache for all later layers.

---

## 🧠 Tricky Interview Question
"You build the React app once and deploy the same image to staging and prod, but `VITE_API_URL` is baked in. How do you handle it?"

Answer: Build args are fixed at build time, so one image cannot serve both unless you build per environment (breaking "build once"). Options: (1) use a relative URL (`/api`) and let Nginx proxy per environment; (2) generate a `config.js` at container start from environment variables (an entrypoint script using `envsubst`) so the same image is configurable at runtime.

---

## ⚫ Interview Questions + Answers

Q1: ARG vs ENV?
A1: ARG exists at build time only; ENV persists into the container runtime and image config.

Q2: Are build args secure?
A2: No, they are in `docker history` and image metadata.

Q3: How to give a secret during build?
A3: BuildKit `--secret` plus `RUN --mount=type=secret`.

Q4: Where can ARG be declared before FROM?
A4: Global scope, only for use in FROM lines; redeclare inside a stage to use it there.

Q5: Does changing an ARG invalidate cache?
A5: Yes, from the first instruction that uses it.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Choosing base-image versions and passing public build metadata.
- Frontend public config that must be compiled in.

❌ Avoid when:
- Any secret or credential.
- Values that should change per deployment without rebuilding (use runtime env).

---

## 📊 Visual Diagram
```
 CLI: --build-arg APP_VERSION=1.2.3
              │
              ▼
 Dockerfile:  ARG APP_VERSION  ──► used in RUN / FROM         (build time only)
                    │
                    └── ENV APP_VERSION=$APP_VERSION ──► visible in container (runtime)

 History:  `docker history` shows ARG values  =>  NO SECRETS HERE
 Secrets:  --secret id=x  ──► RUN --mount=type=secret,id=x   (never stored)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ARG | Build-time variable | build-time variable |
| ENV | Runtime variable | runtime variable |
| --build-arg | Set ARG value | ARG की value |
| Secret mount | Temporary secret file | अस्थायी secret file |
| Scope | Where variable is visible | variable कहाँ दिखता है |
| envsubst | Replace $VAR in files | $VAR बदलने का tool |

---

## ⚡ 3-Line Summary
English: ARG passes values into the build only.
Use for versions and public config; never for secrets.
Use BuildKit secrets for tokens, ENV/runtime config for deployment values.
Hindi: ARG सिर्फ build में values पहुँचाता है।
Versions और public config के लिए इस्तेमाल करो; secrets के लिए कभी नहीं।
Tokens के लिए BuildKit secrets, deployment values के लिए ENV/runtime config।

---

## ➡️ Next Topic
**114. Docker BuildKit** - the modern builder behind secret mounts, cache mounts and parallel stages.
