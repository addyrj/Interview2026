# 97. Distroless Images
# हिंदी में: Distroless Images

---

## 🔵 Simple Definition (English)
Distroless images (from Google) contain only your application and its runtime (for example Node.js or the Python interpreter) plus minimal files such as CA certificates and `/etc/passwd`. They have no shell, no package manager, no `ls`, no `curl`.

## 🔵 सरल परिभाषा (Hindi)
Distroless images (Google की) में सिर्फ आपकी application और उसका runtime (जैसे Node.js या Python interpreter) और कुछ minimal files जैसे CA certificates और `/etc/passwd` होती हैं। इनमें shell, package manager, `ls`, `curl` कुछ नहीं होता।

---

## 🔴 Problem it Solves
Even alpine or slim images include `sh`, `apk`/`apt` and many utilities. After a remote code execution bug, an attacker uses `sh`, `wget` and `apk add` to download tools, scan the network and escalate. Scanners also report CVEs in utilities your app never uses. Distroless removes those tools, so there is nothing to abuse and fewer CVEs.

## 🔴 यह क्यों बना? (Hindi)
Alpine या slim images में भी `sh`, `apk`/`apt` और कई utilities होती हैं। Remote code execution bug के बाद attacker `sh`, `wget` और `apk add` से tools download करके network scan और escalation करता है। Scanners उन utilities के CVEs भी दिखाते हैं जो आपकी app कभी use नहीं करती। Distroless ये tools हटा देता है, इसलिए abuse करने को कुछ नहीं बचता और CVEs कम होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build the app in a normal builder stage (has npm/pip)
Step 2 → Final stage: FROM gcr.io/distroless/nodejs20-debian12
Step 3 → COPY artifacts and prod node_modules only
Step 4 → Use the :nonroot tag (uid 65532) or USER 65532
Step 5 → ENTRYPOINT is already "node"; CMD is just the script path
Step 6 → Debug with :debug tag (busybox shell) or docker debug / ephemeral container
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → App को normal builder stage में build करो (npm/pip है)
Step 2 → Final stage: FROM gcr.io/distroless/nodejs20-debian12
Step 3 → सिर्फ artifacts और prod node_modules copy करो
Step 4 → :nonroot tag (uid 65532) या USER 65532 use करो
Step 5 → ENTRYPOINT पहले से "node" है; CMD में सिर्फ script path
Step 6 → Debug के लिए :debug tag (busybox shell) या ephemeral container
```

---

## 🟡 Real World Example
A payments team had to pass a security audit that required "no shell in production containers". They moved their Node.js API to `distroless/nodejs20-debian12:nonroot`. The scanner's findings fell from 38 to 3, and a pen-tester who found an SSRF could not get a reverse shell because `/bin/sh` did not exist.

## 🟡 Real Example Hindi mein
एक payments team को security audit पास करना था जिसमें "production containers में shell नहीं" की शर्त थी। उन्होंने Node.js API को `distroless/nodejs20-debian12:nonroot` पर move किया। Scanner findings 38 से 3 रह गईं, और SSRF खोजने वाला pen-tester reverse shell नहीं पा सका क्योंकि `/bin/sh` था ही नहीं।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Dockerfile - Node.js on distroless (image names/tags are examples, check the distroless repo)
# Builder stage with npm
FROM node:20-alpine AS build
# Work dir
WORKDIR /app
# Manifests
COPY package.json package-lock.json ./
# Production deps only (plain JS app, no build step)
RUN npm ci --omit=dev
# App source
COPY . .

# Final stage: no shell, no package manager
FROM gcr.io/distroless/nodejs20-debian12:nonroot
# Work dir (created automatically)
WORKDIR /app
# Copy app and modules
COPY --from=build /app /app
# Port
EXPOSE 3000
# ENTRYPOINT is already "node", so only give the script (exec form is required, no shell exists)
CMD ["server.js"]
```

## 💻 Code / Config Example — Advanced

```dockerfile
# syntax=docker/dockerfile:1
# Python FastAPI on distroless (builder Python must match distroless Python: 3.11 on debian12)
# ---- builder ----
FROM python:3.11-slim-bookworm AS builder
# Install deps into a target folder that can be copied
WORKDIR /build
# Requirements
COPY requirements.txt .
# --target puts packages in /deps; no venv symlinks problem with distroless python
RUN pip install --no-cache-dir --target=/deps -r requirements.txt

# ---- runtime ----
# Distroless python3 is Debian 12 based; builder uses the same OS (bookworm) and Python 3.11 in distroless
# NOTE: distroless python version is fixed by the image (3.11 on debian12), so build with the SAME version
FROM gcr.io/distroless/python3-debian12:nonroot
# Work dir
WORKDIR /app
# Dependencies on the Python path
COPY --from=builder /deps /deps
# Tell Python where to find them
ENV PYTHONPATH=/deps
# App code
COPY ./app ./app
# Port
EXPOSE 8000
# Entrypoint is python3; run uvicorn as a module (no shell, no PATH scripts)
CMD ["-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Debug a distroless container (the :debug variant has a busybox shell)
docker run --rm -it --entrypoint=sh gcr.io/distroless/nodejs20-debian12:debug
# Attach a debug container to a running one (needs a recent Docker Desktop / "docker debug" which is a separate feature)
# Kubernetes alternative: kubectl debug -it POD --image=busybox --target=CONTAINER
# Scan the image (trivy installed separately)
trivy image myorg/api:distroless
```

Note: the builder uses the same Python minor version as the distroless python image (Debian 12 python3 is 3.11 at the time of writing; verify in the distroless repo). Not built locally.

---

## 🟠 My Stack Integration
**Node.js**: best fit (`nodejs20-debian12`). **FastAPI**: possible but needs the matching Python version and pure-wheel dependencies; many teams choose `-slim` for Python and distroless for Node/Go/Java. **React**: static, so use `nginx-unprivileged` or Chainguard static images instead. **Health checks**: no `wget`/`curl` exists, so use compose/ECS health checks that call the app from outside or a node script.

```yaml
# docker-compose.yml - distroless Node API with a Node-based health check
services:
  api:
    image: myorg/api:distroless          # distroless runtime image
    restart: unless-stopped              # restart on failure
    read_only: true                      # root filesystem immutable
    cap_drop:
      - ALL                              # drop all Linux capabilities
    security_opt:
      - no-new-privileges:true           # block privilege escalation
    healthcheck:
      # no shell: call node directly with exec form
      test: ["CMD", "/nodejs/bin/node", "-e", "fetch('http://127.0.0.1:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]
      interval: 30s                      # every 30 seconds
      timeout: 3s                        # fail fast
      retries: 3                         # three strikes
    ports:
      - "127.0.0.1:3000:3000"            # only host Nginx can reach it
```

Security: no shell means `docker exec -it api sh` fails by design; log to stdout, ship logs to CloudWatch/Loki, and keep a `:debug` build for staging only.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `CMD npm start` or `RUN` commands in the distroless stage.
✅ Correct: No shell exists. Use exec form only, and run all `RUN` steps in the builder.

❌ Mistake 2: Using `HEALTHCHECK CMD curl ...`.
✅ Correct: Use a Node/Python one-liner or an external orchestrator probe.

❌ Mistake 3: Mismatched Python or glibc versions between builder and distroless.
✅ Correct: Use the same Debian release and Python minor version in both stages.

---

## 🧠 Tricky Interview Question
A container is crash-looping. `docker exec -it c sh` returns "executable file not found". How do you debug a distroless container?

Answer: Read logs first (`docker logs`). Then run the `:debug` tag with `--entrypoint=sh`, or attach a sidecar/ephemeral debug container sharing namespaces (`kubectl debug --target`, or `docker run --pid=container:c --network=container:c busybox`). Never add a shell to production just for debugging.

---

## ⚫ Interview Questions + Answers

Q1: What is in a distroless image?
A1: App runtime, glibc, CA certs, tzdata, `/etc/passwd`; no shell or package manager.

Q2: Distroless vs alpine?
A2: Alpine has busybox and apk (shell access) and uses musl. Distroless uses glibc, has no shell, so smaller attack surface but harder debugging.

Q3: Why exec form is mandatory?
A3: Shell form wraps the command in `/bin/sh -c`, which does not exist.

Q4: What is the `:nonroot` tag?
A4: Variant running as uid 65532 so no `USER` instruction is needed.

Q5: How do you pin distroless safely?
A5: Use a digest (`image@sha256:...`), covered in topic 104, and update it via Dependabot/Renovate.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Compliance asks for minimal images, no shell.
- Go, Java, Node, static binaries in production.

❌ Avoid when:
- Your team depends on `docker exec` for debugging and has no alternative.
- App needs native libs or system tools (ffmpeg, git) at runtime.

---

## 📊 Visual Diagram
```
 alpine / debian-slim                distroless
+----------------------+         +----------------------+
| app + runtime        |         | app + runtime        |
| /bin/sh, apk, wget   |         | (nothing else)       |
| busybox utilities    |         | CA certs, tzdata     |
+----------------------+         +----------------------+
 attacker: sh -> wget -> tools    attacker: no shell, no tools
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Distroless | Image without OS tools | OS tools के बिना image |
| Attack surface | What an attacker can use | हमले के साधन |
| :nonroot | Tag running as non-root | non-root वाला tag |
| :debug | Tag with busybox shell | busybox shell वाला tag |
| Ephemeral container | Temporary debug container | अस्थायी debug container |

---

## ⚡ 3-Line Summary
English: Distroless ships only the app and runtime, with no shell or package manager.
It reduces CVEs and blocks attacker tooling.
Debug with the :debug tag or ephemeral containers.
Hindi: Distroless सिर्फ app और runtime देता है, shell या package manager नहीं।
इससे CVEs कम होते हैं और attacker के tools रुकते हैं।
Debug के लिए :debug tag या ephemeral containers use करो।

---

## ➡️ Next Topic
**98. Alpine vs Debian vs Ubuntu**: choosing the right base distribution.
