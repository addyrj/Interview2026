# 213. Non-Root User Setup
# हिंदी में: Non-Root User Setup (container को root से न चलाना)

---

## 🔵 Simple Definition (English)
By default, processes in a container run as root (UID 0). A non-root setup creates or uses an unprivileged user and switches to it with the `USER` instruction (or `user:` in Compose), so a hacked app has far fewer powers.

## 🔵 सरल परिभाषा (Hindi)
Default में container के processes root (UID 0) से चलते हैं। Non-root setup में unprivileged user बनाकर या मौजूदा user चुनकर `USER` instruction (या Compose में `user:`) से उस पर switch किया जाता है, ताकि hack हुई app के पास बहुत कम अधिकार हों।

---

## 🔴 Problem it Solves
Container root is the same UID 0 as host root. If an attacker exploits your app (RCE in a dependency) and the container has a bind mount, a kernel bug or a mounted Docker socket, root inside can become root on the host. Root can also modify any file in the container, install tools and bind low ports. Least privilege reduces the blast radius.

## 🔴 यह क्यों बना? (Hindi)
Container का root और host का root एक ही UID 0 है। अगर attacker आपकी app (किसी dependency में RCE) exploit कर ले और container में bind mount, kernel bug या mounted Docker socket हो, तो container का root host का root बन सकता है। Root container की कोई भी file बदल सकता है, tools install कर सकता है। Least privilege से नुकसान का दायरा घटता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a user in the image: adduser / useradd with a fixed UID (e.g. 10001)
Step 2 → COPY files with --chown so the user owns what it must write
Step 3 → Add `USER 10001` (or the name) after the install steps that need root
Step 4 → Container starts: PID 1 runs as UID 10001, not root
Step 5 → Writes outside owned paths fail (EACCES): good, it limits damage
Step 6 → Ports below 1024 cannot be bound: use 3000/8000/8080 and map in Compose or Nginx
Step 7 → Bind-mounted folders must be readable/writable by that UID
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Image में fixed UID (जैसे 10001) वाला user बनाएँ: adduser / useradd
Step 2 → `COPY --chown` से वही files उस user की करें जिन्हें उसे लिखना है
Step 3 → जिन install steps को root चाहिए उनके बाद `USER 10001` (या नाम) लिखें
Step 4 → Container चालू होता है: PID 1 root नहीं, UID 10001 से चलता है
Step 5 → Owned paths के बाहर लिखना fail (EACCES): यह अच्छा है, नुकसान सीमित होता है
Step 6 → 1024 से नीचे के ports bind नहीं हो सकते: 3000/8000/8080 रखें और Compose या Nginx में map करें
Step 7 → Bind-mount किए folders उस UID के लिए readable/writable होने चाहिए
```

---

## 🟡 Real World Example
A security audit of a fintech startup finds all 14 containers running as root. A pen tester uploads a malicious file through an image-processing endpoint and gets code execution. As root in the container, he writes to a bind-mounted `/data` folder, replacing a cron script on the host. After the team adds `USER` and removes the writable bind mount, the same exploit can only write inside `/tmp` of a read-only container, and the finding is closed.

## 🟡 Real Example Hindi mein
एक fintech startup के security audit में सामने आता है कि सारे 14 containers root से चल रहे हैं। Pen tester image-processing endpoint से malicious file upload करके code execution पा लेता है। Container में root होने से वह bind-mounted `/data` folder में लिखकर host की cron script बदल देता है। टीम `USER` जोड़कर और writable bind mount हटाकर वही exploit दोहराने पर सिर्फ read-only container के `/tmp` में लिख पाती है, और finding बंद हो जाती है।

---

## 💻 Code / Config Example — Basic
```dockerfile
# Dockerfile  (Basic: Node.js official image already has a "node" user, UID 1000)
FROM node:20-alpine            # example tag
WORKDIR /app                   # app folder (created as root)
COPY --chown=node:node package*.json ./   # give the node user ownership of the files
RUN npm ci --omit=dev          # install as root is fine here, but files are owned by node via chown below
COPY --chown=node:node . .     # copy app code owned by node
USER node                      # from here on, and at runtime, run as non-root
EXPOSE 3000                    # unprivileged port
CMD ["node", "server.js"]      # starts as UID 1000
```

## 💻 Code / Config Example — Advanced
```dockerfile
# api/Dockerfile  (Python: create a dedicated user with fixed UID/GID and no shell)
FROM python:3.12-slim AS builder                     # builder stage (example tag)
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt   # install deps
FROM python:3.12-slim AS runtime                     # runtime stage
ARG UID=10001                                        # fixed numeric UID (build arg)
ARG GID=10001                                        # fixed numeric GID
RUN groupadd --gid ${GID} app \
 && useradd --uid ${UID} --gid ${GID} --no-create-home --shell /usr/sbin/nologin app   # no login shell
WORKDIR /code
COPY --from=builder /install /usr/local              # packages (root-owned, read-only for app: good)
COPY --chown=app:app main.py .                       # code owned by app
RUN mkdir -p /code/data && chown app:app /code/data  # the only writable directory
USER 10001:10001                                     # numeric USER works with Kubernetes runAsNonRoot checks
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```
```yaml
# compose.yaml  (enforce at runtime even if the image forgot USER)
services:
  api:
    build: ./api                      # image above
    user: "10001:10001"               # override/force UID:GID at runtime
    read_only: true                   # root FS immutable
    tmpfs: ["/tmp"]                   # writable temp
    volumes:
      - appdata:/code/data            # named volume (Docker copies ownership from image path on first use)
    cap_drop: ["ALL"]                 # no capabilities
    security_opt: ["no-new-privileges:true"]   # block setuid escalation
  nginx:
    image: nginxinc/nginx-unprivileged:1.27-alpine   # example: official-style image that runs as UID 101 on port 8080
    ports: ["80:8080"]                # host 80 -> container 8080 (non-root cannot bind 80)
volumes:
  appdata: {}
```
Check: `docker compose exec api id` should show `uid=10001`. Quick audit: `docker ps -q | xargs docker inspect --format '{{.Name}} {{.Config.User}}'` (empty means root).

---

## 🟠 My Stack Integration
- **Node.js:** official image has `node` (UID 1000); just add `USER node`.
- **FastAPI:** create your own user (above); keep pip packages root-owned.
- **React:** serve the build with `nginx-unprivileged` (port 8080) so no root is needed at runtime.
- **Nginx on VPS (host):** the master runs as root only to bind 80/443, workers drop to `www-data` or `nginx`. In a container prefer the unprivileged image.
- **AWS:** ECS/Fargate and Kubernetes policies (`runAsNonRoot`) reject root images, so this is also a deployment requirement.
- **Security:** fixed numeric UID, no shell, `cap_drop`, `no-new-privileges`, read-only root.

```dockerfile
# React static site, non-root, final stage only
FROM nginxinc/nginx-unprivileged:1.27-alpine      # runs as non-root by default (UID 101)
COPY --chown=101:101 dist/ /usr/share/nginx/html/ # built React files
EXPOSE 8080                                       # unprivileged port
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting `USER` before `RUN npm install` or `apt-get`, so the install fails with permission errors.
✅ Correct: Do root-needed steps first, then `USER`.

❌ Mistake 2: Binding a non-root app to port 80.
✅ Correct: Use 8080/3000 inside the container and map the host port.

❌ Mistake 3: Bind mounting a host folder owned by root and expecting the app to write there.
✅ Correct: `chown` it to the UID, or use a named volume.

❌ Mistake 4: Copying files as root and leaving everything root-owned, then the app cannot write logs/uploads.
✅ Correct: `COPY --chown`, and give write access only to specific directories.

---

## 🧠 Tricky Interview Question
You added `USER app`, but `docker exec -u 0 api sh` still gives you root. Is the non-root setup broken?

Answer: No. `USER` sets the default user for the main process only. The Docker admin can still exec as root, because anyone who can talk to the Docker daemon is effectively root on the host. The protection is against a compromised app inside the container. Also remember that a user in the `docker` group is equivalent to root, so restrict that group.

---

## ⚫ Interview Questions + Answers

Q1: Why use a numeric UID in `USER`?
A1: Orchestrators like Kubernetes can verify `runAsNonRoot` only if the user is numeric; names require reading `/etc/passwd`.

Q2: What does `--chown` do in `COPY`?
A2: Sets file ownership at copy time without an extra `RUN chown` layer (which would duplicate the data).

Q3: What is user namespace remapping?
A3: A daemon feature (`userns-remap`) that maps container root to an unprivileged host UID, so even container root is harmless on the host. Rootless Docker goes further by running the daemon itself as non-root.

Q4: Can non-root users bind port 80?
A4: Not by default (ports under 1024 are privileged), except with a sysctl `net.ipv4.ip_unprivileged_port_start` change or capability `NET_BIND_SERVICE`. Better to use a high port.

Q5: How do you check a running container's user?
A5: `docker exec <c> id` or `docker inspect --format '{{.Config.User}}'`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Always for application containers in production.

❌ Avoid when:
- A tool truly needs root briefly (installing packages): do it in an earlier build step, then drop privileges. Some special containers like `cadvisor` or log collectors need extra access; give the minimum, not full root.

---

## 📊 Visual Diagram
```
 Root container                       Non-root container
 +----------------------+             +----------------------+
 | app (UID 0)          |             | app (UID 10001)      |
 | can write anywhere   |             | writes only /tmp,/data|
 | can install tools    |             | cannot install/chown |
 +----------+-----------+             +----------+-----------+
            | exploit                              | exploit
            v                                      v
   host files via bind mount at risk       damage stays inside small area
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| UID | Numeric user ID (0 = root) | user की numeric ID |
| USER | Dockerfile instruction to set user | user चुनने वाला instruction |
| least privilege | Give minimum rights | कम से कम अधिकार |
| `--chown` | Set owner while copying | copy करते समय owner तय करना |
| userns-remap | Map container root to host non-root | container root को host non-root से map करना |
| rootless Docker | Daemon runs without root | बिना root के daemon |

---

## ⚡ 3-Line Summary
English: Never run apps as root in containers. Create a fixed-UID user, `COPY --chown`, and set `USER` after root-needed steps. Use high ports and add read-only root plus dropped capabilities.
Hindi: Containers में apps को कभी root से न चलाएँ। Fixed-UID user बनाएँ, `COPY --chown` करें, और root वाले steps के बाद `USER` लगाएँ। High ports रखें और read-only root व dropped capabilities जोड़ें।

---

## ➡️ Next Topic
**214. Read-Only Root Filesystem**: even a non-root app can write files; next we make the whole filesystem immutable.
