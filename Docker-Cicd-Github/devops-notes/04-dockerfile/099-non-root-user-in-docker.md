# 99. Non-Root User in Docker
# हिंदी में: Docker में Non-Root User

---

## 🔵 Simple Definition (English)
By default, processes in a container run as root (uid 0). Running as a non-root user means creating an unprivileged user in the image and switching to it with the `USER` instruction, so the app has the least privileges it needs.

## 🔵 सरल परिभाषा (Hindi)
Default रूप से container के processes root (uid 0) से चलते हैं। Non-root user का मतलब है image में एक unprivileged user बनाना और `USER` instruction से उस पर switch करना, ताकि app के पास सिर्फ ज़रूरी minimum privileges हों।

---

## 🔴 Problem it Solves
Container root is the same uid 0 as host root (unless user namespaces are used). If an attacker escapes through a kernel bug, a mounted Docker socket or a writable host bind mount, they are root on the host. Many Kubernetes clusters (Pod Security Standards "restricted") and security audits reject root containers outright.

## 🔴 यह क्यों बना? (Hindi)
Container का root वही uid 0 है जो host का root है (जब तक user namespaces use न हों)। अगर attacker kernel bug, mounted Docker socket या writable host bind mount से बाहर निकल जाए तो वह host पर root होता है। कई Kubernetes clusters (Pod Security Standards "restricted") और security audits root containers को सीधे reject कर देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create user/group with fixed uid/gid (e.g. 10001)
Step 2 → Install packages and copy files as root first
Step 3 → chown only the folders the app must write to
Step 4 → USER 10001:10001 (numeric id works with k8s runAsNonRoot)
Step 5 → App listens on port > 1024 (non-root cannot bind 80/443)
Step 6 → Verify: docker run --rm img id  ->  uid=10001
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → तय uid/gid वाला user/group बनाओ (जैसे 10001)
Step 2 → पहले root से packages install और files copy करो
Step 3 → सिर्फ वही folders chown करो जिनमें app को लिखना है
Step 4 → USER 10001:10001 (numeric id k8s runAsNonRoot के साथ चलता है)
Step 5 → App 1024 से बड़े port पर सुने (non-root 80/443 bind नहीं कर सकता)
Step 6 → जाँचो: docker run --rm img id  ->  uid=10001
```

---

## 🟡 Real World Example
On a shared VPS, a startup's Node API ran as root with `/var/run/docker.sock` mounted for a "deploy" feature. A dependency with a prototype-pollution bug allowed command execution; the attacker used the socket to start a privileged container and read other customers' data. After the incident they switched to `USER node`, removed the socket mount and added `no-new-privileges`.

## 🟡 Real Example Hindi mein
एक shared VPS पर एक startup का Node API root से चलता था और "deploy" feature के लिए `/var/run/docker.sock` mount था। एक dependency के prototype-pollution bug से command execution हो गया; attacker ने socket से privileged container चलाकर दूसरे customers का data पढ़ लिया। घटना के बाद उन्होंने `USER node` लगाया, socket mount हटाया और `no-new-privileges` जोड़ा।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Dockerfile - non-root with the user shipped in the official node image
# Alpine-based Node image (example tag)
FROM node:20-alpine
# Work dir
WORKDIR /app
# Copy files owned by the unprivileged "node" user (uid 1000)
COPY --chown=node:node package*.json ./
# Install dependencies (still root here, so npm can write /app)
RUN npm ci --omit=dev
# Copy source owned by node
COPY --chown=node:node . .
# Switch to non-root for runtime
USER node
# Port above 1024
EXPOSE 3000
# Start
CMD ["node", "server.js"]
```

```bash
# verify who runs the process
docker run --rm myimg id            # expect uid=1000(node)
docker run --rm myimg whoami        # expect node
docker exec api ps aux              # PID 1 should not be root
```

## 💻 Code / Config Example — Advanced

```dockerfile
# syntax=docker/dockerfile:1
# Custom user with fixed uid for any base image (Debian/Ubuntu/Python)
FROM python:3.12-slim AS runtime
# Do not buffer logs, do not write pyc
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
# Create a system group and user with fixed ids, no login shell, no home dir
RUN groupadd --system --gid 10001 app \
 && useradd  --system --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin app
# Work dir
WORKDIR /app
# Install deps as root (writes to site-packages)
COPY requirements.txt .
# No pip cache stored
RUN pip install --no-cache-dir -r requirements.txt
# Code owned by app but NOT writable by it (chmod keeps code read-only)
COPY --chown=root:app --chmod=0750 ./app ./app
# A single writable folder for uploads/state
RUN mkdir -p /app/data && chown app:app /app/data
# Switch to numeric uid:gid (k8s runAsNonRoot can verify numeric ids)
USER 10001:10001
# Unprivileged port
EXPOSE 8000
# Start the API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml - enforce hardening at runtime too
services:
  api:
    build: .                          # build from the Dockerfile above
    user: "10001:10001"               # override/force uid:gid even if image forgets USER
    read_only: true                   # root filesystem read-only
    tmpfs:
      - /tmp                          # writable temp in memory
    volumes:
      - apidata:/app/data             # the only persistent writable path
    cap_drop:
      - ALL                           # remove all Linux capabilities
    security_opt:
      - no-new-privileges:true        # prevent setuid privilege gain
    restart: unless-stopped           # restart policy
volumes:
  apidata: {}                         # named volume (owned by uid 10001 on first mount from image)
```

```yaml
# Kubernetes equivalent (snippet, not applied here)
securityContext:
  runAsNonRoot: true          # kubelet refuses root images
  runAsUser: 10001            # numeric uid
  allowPrivilegeEscalation: false  # block setuid escalation
  readOnlyRootFilesystem: true     # immutable root fs
  capabilities:
    drop: ["ALL"]             # drop all capabilities
```

---

## 🟠 My Stack Integration
**Node.js**: `USER node`. **FastAPI**: custom uid 10001 as above. **Nginx**: use `nginxinc/nginx-unprivileged` (port 8080) or run host Nginx as root only for binding 80/443 (its workers already run as `www-data`/`nginx`). **VPS**: bind volumes with matching uid (`chown -R 10001:10001 /srv/app/data`). **AWS ECS/Fargate**: set `"user": "10001"` in the task definition.

Security: never mount `/var/run/docker.sock` into app containers; combine non-root + read-only fs + dropped capabilities + `no-new-privileges`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Adding `USER app` at the top, then `RUN npm ci` fails with EACCES.
✅ Correct: Install as root, `chown` what is needed, put `USER` last before CMD.

❌ Mistake 2: Using `USER appname` while Kubernetes `runAsNonRoot: true` cannot verify names.
✅ Correct: Use numeric `USER 10001`.

❌ Mistake 3: Bind-mounted host folder owned by root, app gets "permission denied".
✅ Correct: `chown` the host directory to the same uid, or use named volumes.

---

## 🧠 Tricky Interview Question
Your non-root container fails: "listen EACCES: permission denied 0.0.0.0:80". What do you do?

Answer: Ports below 1024 are privileged. Options: listen on 8080/3000 and map `-p 80:8080` (or let Nginx on the host do 80/443); or, less preferred, add `--cap-add=NET_BIND_SERVICE` / set `net.ipv4.ip_unprivileged_port_start=0`. Choosing a high port is the best answer.

---

## ⚫ Interview Questions + Answers

Q1: Is container root the same as host root?
A1: Same uid 0 on the same kernel, but constrained by namespaces, capabilities and seccomp. A breakout makes it real root, unless user namespace remapping is enabled.

Q2: How can you run non-root without editing the Dockerfile?
A2: `docker run --user 10001:10001` or `user:` in compose.

Q3: What does `no-new-privileges` do?
A3: Stops processes from gaining more privileges via setuid binaries or file capabilities.

Q4: What is rootless Docker?
A4: The Docker daemon itself runs as a non-root user (user namespaces), so even a daemon breakout is not host root.

Q5: How to check an image's user?
A5: `docker inspect --format '{{.Config.User}}' img`; empty means root.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every production app container (the default rule).
- Kubernetes with restricted Pod Security.

❌ Avoid when:
- A tool must bind low ports or manage the network/kernel (then use specific capabilities, not full root).
- Build stages that install packages (root is fine in the builder).

---

## 📊 Visual Diagram
```
 Root container                       Non-root container
 +-----------------+                  +-----------------+
 | app (uid 0)     |  exploit -->     | app (uid 10001) |  exploit -->
 +-----------------+  can: write /etc +-----------------+  can: only write
        |             load modules           |             /app/data, /tmp
        v             use docker.sock        v             no new privileges
   HOST ROOT (risk)                      limited blast radius
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| uid | Numeric user id | numeric user id |
| USER | Dockerfile instruction to switch user | user बदलने का instruction |
| Capability | Fine-grained root power | root की छोटी शक्तियाँ |
| no-new-privileges | Block privilege gain | privilege बढ़ना रोकता है |
| Rootless Docker | Daemon runs without root | बिना root daemon |

---

## ⚡ 3-Line Summary
English: Create an unprivileged user and switch with USER after installing everything.
Use numeric uid, high ports and combine with read-only fs and dropped capabilities.
It limits damage if the app is compromised.
Hindi: Unprivileged user बनाओ और सब install करने के बाद USER से switch करो।
Numeric uid, high ports use करो और read-only fs व dropped capabilities साथ रखो।
App hack होने पर नुकसान सीमित रहता है।

---

## ➡️ Next Topic
**100. Read-Only Filesystem**: make the container's root filesystem immutable.
