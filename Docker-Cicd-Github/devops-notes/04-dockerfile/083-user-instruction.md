# 083. USER Instruction
# हिंदी में: USER इंस्ट्रक्शन (Non-root Container)

---

## 🔵 Simple Definition (English)
`USER` sets the user (and optionally group) that runs all following `RUN`, `CMD` and `ENTRYPOINT` instructions, and the container's main process. By default containers run as **root**; `USER` lets you drop to a low-privilege account.

## 🔵 सरल परिभाषा (Hindi)
`USER` उस user (और optional group) को set करता है जो आगे की सभी `RUN`, `CMD`, `ENTRYPOINT` instructions और container का main process चलाता है। Default में containers **root** से चलते हैं; `USER` से आप कम-privilege account पर आ जाते हैं।

---

## 🔴 Problem it Solves
Running as root inside a container is dangerous: if an attacker exploits your Node.js or FastAPI app (RCE), they become root in the container, can write anywhere, and have a much easier path to escape to the host through a kernel or runtime bug or a mounted volume or `docker.sock`. The principle of least privilege says the app needs only to read its code and write its data folder. `USER` enforces that.

## 🔴 यह क्यों बना? (Hindi)
Container में root चलाना खतरनाक है: अगर attacker आपकी Node.js या FastAPI app exploit (RCE) कर ले तो वह container में root बन जाता है, कहीं भी लिख सकता है, और kernel/runtime bug, mounted volume या `docker.sock` के ज़रिए host तक पहुँचना आसान हो जाता है। Least privilege कहता है कि app को सिर्फ अपना code पढ़ना और data folder में लिखना है। `USER` यही लागू करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a user in the image (or use an existing one, e.g. "node")
Step 2 → Install packages / set up files as root (apt, npm ci, chown)
Step 3 → Put `USER appuser` after setup (or USER 10001, numeric is best)
Step 4 → Later RUN/CMD/ENTRYPOINT run as that user
Step 5 → At runtime `docker run --user 2000:2000` or Compose `user:` can override it
Step 6 → Files the app must write must be owned by that UID (COPY --chown / chown)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Image में user बनाओ (या मौजूदा use करो, जैसे "node")
Step 2 → Packages / files की setup root रहते हुए करो (apt, npm ci, chown)
Step 3 → Setup के बाद `USER appuser` लगाओ (या USER 10001, numeric सबसे अच्छा)
Step 4 → आगे की RUN/CMD/ENTRYPOINT उसी user से चलती हैं
Step 5 → Runtime पर `docker run --user 2000:2000` या Compose `user:` इसे override कर सकते हैं
Step 6 → जिन files में app को लिखना है वे उसी UID के owner होनी चाहिए (COPY --chown / chown)
```

---

## 🟡 Real World Example
A fintech team's security scan (Trivy / audit) flags "container runs as root". Their Node.js API image is changed to `USER node`, and Kubernetes adds `runAsNonRoot: true`. Later, a dependency vulnerability allows an attacker to run commands, but they can only write to `/app/uploads`, cannot install packages, cannot bind port 80, and cannot modify system files. Impact is contained. The one side effect: the app must use port 3000, not 80 (fine, since Nginx handles 80).

## 🟡 Real Example Hindi mein
एक fintech team का security scan (Trivy / audit) बताता है "container runs as root"। उनकी Node.js API image में `USER node` लगाया जाता है और Kubernetes में `runAsNonRoot: true`। बाद में किसी dependency की vulnerability से attacker commands चला पाता है, पर वह सिर्फ `/app/uploads` में लिख सकता है; packages install नहीं कर सकता, port 80 bind नहीं कर सकता, system files नहीं बदल सकता। नुकसान सीमित रहता है। एक side effect: app को port 80 की जगह 3000 use करना पड़ता है (ठीक है, क्योंकि 80 Nginx संभालता है)।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Basic USER example: official node image already ships a non-root "node" user (uid 1000)
# Base image (example tag)
FROM node:20-alpine
# Working directory (created as root)
WORKDIR /app
# Copy manifests; --chown gives files to node so the app can read/write them
COPY --chown=node:node package*.json ./
# Install dependencies (still root here, which is fine for setup)
RUN npm ci --omit=dev
# Copy source with correct ownership
COPY --chown=node:node . .
# Switch to the unprivileged user: everything after this runs as node
USER node
# Start the app (runs as node, not root)
CMD ["node", "server.js"]
```

```bash
# Verify: should print "node" and uid 1000, not root
docker run --rm myapi id
# Confirm the main process user
docker run --rm myapi whoami
```

## 💻 Code / Config Example — Advanced

```dockerfile
# syntax=docker/dockerfile:1
# Advanced: FastAPI with a dedicated fixed-UID user, read-only code, writable data dir
# Python slim base (example tag)
FROM python:3.12-slim
# Python runtime flags
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
# Fixed UID/GID make volume permissions predictable across hosts
ARG APP_UID=10001
# Group id (same value for simplicity)
ARG APP_GID=10001
# Create group and user: system account, no shell, no home directory
RUN groupadd --system --gid ${APP_GID} app \
    && useradd --system --uid ${APP_UID} --gid app --no-create-home --shell /usr/sbin/nologin app
# Working directory owned by root (code is read-only for the app)
WORKDIR /app
# Dependency manifest
COPY requirements.txt .
# Install as root into system site-packages
RUN pip install --no-cache-dir -r requirements.txt
# Copy code; owned by root, readable by everyone, not writable by app
COPY app ./app
# Create the only writable directory and hand it to the app user
RUN mkdir -p /var/lib/app && chown ${APP_UID}:${APP_GID} /var/lib/app
# Declare persistent data location (after ownership is set)
VOLUME ["/var/lib/app"]
# Drop privileges using numeric ids (works with runAsNonRoot checks in Kubernetes)
USER ${APP_UID}:${APP_GID}
# Unprivileged port (>1024)
EXPOSE 8000
# Start uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml: extra hardening on top of USER
services:
  # FastAPI backend
  api:
    # Built from the Dockerfile above
    build: ./backend
    # Enforce the user even if the image forgets it
    user: "10001:10001"
    # Root filesystem becomes read-only
    read_only: true
    # Allow temp files only in memory
    tmpfs:
      - /tmp
    # Writable data volume
    volumes:
      - api_data:/var/lib/app
    # Drop all Linux capabilities (app does not need any)
    cap_drop:
      - ALL
    # Block privilege escalation via setuid binaries
    security_opt:
      - no-new-privileges:true
    # Restart policy
    restart: unless-stopped
# Named volume declaration
volumes:
  api_data:
```

---

## 🟠 My Stack Integration
- **Node.js**: use `USER node` (exists in official images). Use `COPY --chown=node:node`.
- **FastAPI**: create a user with `useradd`; slim/debian images do not have one ready.
- **React/Nginx**: use `nginxinc/nginx-unprivileged` (runs as uid 101, listens on 8080) so even the web tier is non-root. Update `proxy_pass`/port mapping to 8080.
- **VPS**: bind mounts need host files readable by the container UID (`chown 10001:10001 ./data`).
- **AWS ECS/EKS**: set `user` in the task definition or `runAsNonRoot`/`runAsUser` in the pod; many policies (PSA "restricted") require it.
- **Ports**: non-root cannot bind ports below 1024 (unless a capability is added). Map `80:8000` at the edge instead.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting `USER app` before `RUN apt-get install` / `npm ci -g`. It fails with "permission denied".
✅ Correct: Do privileged setup first, then `USER` near the end.

❌ Mistake 2: Copying files as root and expecting the app to write logs/uploads there. You get `EACCES`.
✅ Correct: `COPY --chown=` or `chown` only the specific writable directories.

❌ Mistake 3: `chown -R app /` or `chmod -R 777 /app` to "fix" permissions.
✅ Correct: Give ownership to only the data dir; keep code read-only.

❌ Mistake 4: Using `USER appuser` (name) when Kubernetes needs to verify non-root; it cannot map a name to a UID.
✅ Correct: Use numeric `USER 10001`.

❌ Mistake 5: Using `sudo` in containers.
✅ Correct: Not needed; do privileged steps before `USER`.

---

## 🧠 Tricky Interview Question
Your app runs as non-root and works locally, but on the VPS it crashes with "EACCES: permission denied, open '/app/data/db.sqlite'" when you bind mount `./data:/app/data`. Why?

Answer: Bind mounts keep the host's ownership. The host folder `./data` is owned by your host user (e.g., UID 1001 or root), while the container process runs as UID 1000/10001. The kernel compares numeric IDs, not names, so the write is denied. Fix: `chown 10001:10001 ./data` on the host (or use a named volume, which copies the image's ownership on first use), or run with a matching `user:`.

---

## ⚫ Interview Questions + Answers

Q1: Why not run containers as root?
A1: If the app is compromised, the attacker gets root inside the container, with far more power and a better chance to escape or damage mounted data. Least privilege reduces the blast radius.

Q2: Is root in a container the same as root on the host?
A2: By default UID 0 in the container is UID 0 on the host (kernel-wise), restricted by namespaces, capabilities and seccomp. With user namespace remapping or rootless Docker it maps to an unprivileged host UID.

Q3: Can a non-root user bind to port 80?
A3: Not by default (ports below 1024 are privileged). Use a high port and map it, or add `NET_BIND_SERVICE`, or set the sysctl `net.ipv4.ip_unprivileged_port_start`.

Q4: Where can you override USER?
A4: `docker run --user`, Compose `user:`, Kubernetes `securityContext.runAsUser`.

Q5: Name/ID difference in USER?
A5: `USER` accepts name or UID. Numeric UIDs are preferred, since they work even if the name does not exist in `/etc/passwd` and let Kubernetes verify non-root.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every production application image. This is a baseline.
- Security scans or Pod Security standards require non-root.

❌ Avoid when:
- A build step really needs root: keep those before `USER` (do not skip USER at the end).
- Tools that need privileged operations (some init/network tools); give a specific capability, not root.

---

## 📊 Visual Diagram

```
 Dockerfile order of operations

  FROM node:20-alpine
        |
  [root]  apt/apk install, npm ci, mkdir, chown     <- setup as root
        |
  USER 10001                                         <- privilege drop
        |
  [uid 10001]  CMD ["node","server.js"]              <- app runs here
        |
        v
  Attacker via RCE:  can write /app/uploads only
                     cannot install, cannot edit /etc, cannot bind :80
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| USER | Sets running user | चलाने वाला user तय करता है |
| Least privilege | Give only needed rights | सिर्फ ज़रूरी अधिकार देना |
| UID/GID | Numeric user/group id | user/group की संख्या |
| `--chown` | Set owner while copying | copy करते समय owner तय करना |
| Capability | Fine-grained root power | root की छोटी-छोटी शक्तियाँ |
| Rootless Docker | Docker daemon without root | बिना root का Docker daemon |

---

## ⚡ 3-Line Summary
English: `USER` makes the container process run as a low-privilege account instead of root. Do setup as root first, then switch, use numeric UIDs, and `chown` only the writable folders. This limits damage when an app is exploited.
Hindi: `USER` container process को root की जगह कम-privilege account से चलाता है। पहले root से setup करो, फिर switch करो, numeric UID use करो और सिर्फ writable folders पर `chown` करो। इससे app exploit होने पर नुकसान सीमित रहता है।

---

## ➡️ Next Topic
**084. LABEL Instruction**: after permissions, learn how to attach metadata (owner, version, source repo) to images for governance and automation.
