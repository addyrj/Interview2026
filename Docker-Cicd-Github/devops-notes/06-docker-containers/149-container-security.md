---

# 149. Container Security
# हिंदी में: Container Security (Containers को सुरक्षित बनाना)

---

## 🔵 Simple Definition (English)
Container security means reducing what an attacker can do **if your app is compromised**. Containers share the host kernel, so the goal is least privilege: run as a **non-root user**, drop Linux **capabilities**, use a **read-only filesystem**, apply **resource limits**, use **minimal scanned images**, and keep **secrets** out of images.

## 🔵 सरल परिभाषा (Hindi)
Container security का मतलब है कि अगर आपका app compromise हो जाए तो attacker **क्या-क्या कर सकता है** उसे कम करना। Containers host kernel share करते हैं, इसलिए लक्ष्य है least privilege: **non-root user** से चलाना, Linux **capabilities** हटाना, **read-only filesystem**, **resource limits**, **minimal scanned images** और **secrets** को images से बाहर रखना।

---

## 🔴 Problem it Solves
By default a container process runs as **root** with a wide set of capabilities and a writable filesystem. A bug in your Node.js app (RCE, path traversal) then gives the attacker root inside the container, tools to download malware, and a chance to escape to the host via kernel bugs or a mounted `docker.sock`. Real incidents: crypto miners in exposed Docker APIs, leaked AWS keys baked into images, and containers with `--privileged` giving full host takeover.

## 🔴 यह क्यों बना? (Hindi)
Default में container process **root** से चलता है, ढेर सारी capabilities और writable filesystem के साथ। आपके Node.js app में bug (RCE, path traversal) होने पर attacker को container के अंदर root, malware download करने के tools और kernel bug या mounted `docker.sock` से host तक पहुँचने का मौका मिलता है। असली घटनाएँ: खुले Docker API पर crypto miners, images में छपी AWS keys, और `--privileged` वाले containers से पूरे host का कब्ज़ा।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build: small base image (alpine/slim/distroless), pinned tag or digest
Step 2 → Build: create non-root USER, no secrets in layers, multi-stage build
Step 3 → Scan: trivy / docker scout in CI, fail on HIGH/CRITICAL
Step 4 → Run: --user, --read-only, --cap-drop ALL, no-new-privileges, limits
Step 5 → Isolate: private networks, no docker.sock mount, no --privileged
Step 6 → Secrets: runtime env / secrets manager, never COPY .env into image
Step 7 → Monitor: logs, Falco/audit, patch base images regularly
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Build: छोटी base image (alpine/slim/distroless), pinned tag या digest।
Step 2 → Build: non-root USER बनाओ, layers में secrets नहीं, multi-stage build।
Step 3 → Scan: CI में trivy / docker scout, HIGH/CRITICAL पर fail।
Step 4 → Run: `--user`, `--read-only`, `--cap-drop ALL`, `no-new-privileges`, limits।
Step 5 → Isolate: private networks, `docker.sock` mount नहीं, `--privileged` नहीं।
Step 6 → Secrets: runtime env / secrets manager, `.env` को image में COPY नहीं।
Step 7 → Monitor: logs, Falco/audit, base images नियमित patch।

---

## 🟡 Real World Example
Your VPS runs a Node.js API. A dependency has a deserialization bug and an attacker gets code execution. With a hardened container: the user is `node` (not root), filesystem is read-only so the attacker cannot drop a miner binary, capabilities are dropped so no raw sockets, memory/CPU limits stop a miner from eating the box, and the network is internal so it cannot call out. The same bug on a default container would likely become a full server incident.

## 🟡 Real Example Hindi mein
आपके VPS पर Node.js API चलती है। किसी dependency में deserialization bug से attacker को code execution मिल जाता है। Hardened container में: user `node` है (root नहीं), filesystem read-only है इसलिए miner binary नहीं रख सकता, capabilities हटी हैं तो raw sockets नहीं, memory/CPU limits miner को box खाने से रोकती हैं, और network internal है तो बाहर call भी नहीं कर सकता। वही bug default container पर शायद पूरे server का incident बन जाता।

---

## 💻 Code / Config Example — Basic
```dockerfile
# Dockerfile - non-root Node.js image (basic hardening)
FROM node:20-alpine                     # small base; example tag, pin and update regularly
WORKDIR /app                            # app directory
COPY package*.json ./                   # copy manifests first for layer caching
RUN npm ci --omit=dev                   # install only production dependencies, reproducible
COPY --chown=node:node . .              # copy code owned by the built-in non-root user "node"
USER node                               # drop root: everything after runs as uid 1000
EXPOSE 3000                             # documentation only
CMD ["node", "server.js"]               # exec form so signals reach node
```

```bash
# Run with basic runtime hardening
docker run -d --name api \
  --read-only \                         # root filesystem is read-only
  --tmpfs /tmp \                        # writable scratch space in RAM
  --cap-drop ALL \                      # remove all Linux capabilities
  --security-opt no-new-privileges:true \ # block setuid privilege escalation
  --memory 256m --cpus 0.5 \            # resource limits against abuse
  -p 127.0.0.1:3000:3000 \              # only localhost, Nginx in front
  myorg/api:1.4.2                       # pinned version
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - hardened production service
services:
  api:
    image: myorg/api:1.4.2              # immutable, scanned tag (or @sha256 digest)
    user: "1000:1000"                   # explicit non-root uid:gid
    read_only: true                     # read-only root filesystem
    tmpfs:
      - /tmp:size=64m,mode=1777         # writable temp dir, limited size, in memory
    cap_drop:
      - ALL                             # start with zero capabilities
    # cap_add:
    #   - NET_BIND_SERVICE              # add back only if binding ports < 1024
    security_opt:
      - no-new-privileges:true          # forbid gaining more privileges
      # - seccomp:default               # default seccomp profile is already ON; never disable it
    pids_limit: 200                     # stop fork bombs
    mem_limit: 512m                     # hard memory cap (OOM kills inside, not host)
    cpus: 1.0                           # CPU cap
    ulimits:
      nofile:
        soft: 4096                      # open files limit (soft)
        hard: 8192                      # open files limit (hard)
    environment:
      NODE_ENV: production              # production mode
    secrets:
      - db_password                     # mounted at /run/secrets/db_password (file, not env)
    networks:
      - backend                         # private network
    restart: unless-stopped             # self-heal
    healthcheck:
      test: ["CMD", "node", "-e", "require('http').get('http://localhost:3000/health',r=>process.exit(r.statusCode===200?0:1)).on('error',()=>process.exit(1))"] # no curl needed
      interval: 30s
      timeout: 3s
      retries: 3
secrets:
  db_password:
    file: ./secrets/db_password.txt     # file kept outside Git (chmod 600)
networks:
  backend:
    internal: true                      # no outbound internet unless needed
```

```bash
# CI step: scan image before push (example with Trivy, tool must be installed)
trivy image --severity HIGH,CRITICAL --exit-code 1 myorg/api:1.4.2  # fail build on serious CVEs
# Check effective settings of a running container
docker inspect -f 'user={{.Config.User}} ro={{.HostConfig.ReadonlyRootfs}} caps_drop={{.HostConfig.CapDrop}} priv={{.HostConfig.Privileged}}' api
```
Not run locally (no Docker daemon). Some apps break with `read_only` if they write to disk (logs, uploads, `.cache`); list those paths under `tmpfs` or volumes.

---

## 🟠 My Stack Integration
- **Node.js**: official image already has user `node`; use `npm ci --omit=dev`, never run `npm install` as root in production, and enable `npm audit` in CI.
- **FastAPI**: create a user (`RUN adduser --disabled-password --uid 10001 app` and `USER app`), run `uvicorn` on 8000, avoid `--reload` in production.
- **React**: build in a Node stage, copy `dist` into `nginxinc/nginx-unprivileged` (runs as non-root on 8080).
- **Nginx on VPS**: terminate TLS, add security headers, rate limit. Nginx container: `cap_drop: ALL` plus `NET_BIND_SERVICE` only if it binds 80/443 as non-root.
- **AWS**: use ECR image scanning, IAM roles for EC2/ECS instead of access keys in env, IMDSv2 required (blocks SSRF stealing role credentials), Security Groups tight.
- **Never** mount `/var/run/docker.sock` into app containers: it equals root on the host.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running as root because "it just works".
✅ Correct: `USER node` / `user: "1000:1000"`; fix file permissions with `--chown`.

❌ Mistake 2: Using `latest` tags and never rebuilding.
✅ Correct: Pin tags/digests, rebuild weekly, scan in CI.

❌ Mistake 3: `ENV AWS_SECRET_ACCESS_KEY=...` in the Dockerfile or `COPY .env .`.
✅ Correct: Inject at runtime; use BuildKit `--mount=type=secret` for build-time secrets; add `.env` to `.dockerignore`.

❌ Mistake 4: Mounting `docker.sock` or using `--privileged` for convenience.
✅ Correct: Use a socket proxy with limited API access, or avoid entirely.

❌ Mistake 5: Believing the container is a full security boundary like a VM.
✅ Correct: It shares the kernel; add seccomp/AppArmor, patch the host, consider gVisor/Kata for untrusted code.

---

## 🧠 Tricky Interview Question
You set `USER node` in the Dockerfile, but a security scan still flags "container runs as root". Why?

Answer: The runtime can override the image user (`docker run -u 0`, Compose `user: root`, Kubernetes `runAsUser: 0`). Another cause: the final stage in a multi-stage build never set `USER` (only the build stage did). Also a user namespace remap or an entrypoint script that does `su`/`sudo` could matter. Verify with `docker exec api id` and `docker inspect -f '{{.Config.User}}'`, and enforce policy (Kubernetes `runAsNonRoot: true`, admission control).

---

## ⚫ Interview Questions + Answers

Q1: Why is running as root in a container risky if it is isolated?
A1: Container root is uid 0 on the host kernel. With a kernel bug, mounted sensitive paths, or extra capabilities it can escape; even inside, root can modify everything writable.

Q2: What are Linux capabilities?
A2: Split-up root powers (e.g. NET_ADMIN, SYS_ADMIN, CHOWN). Docker grants a default subset; `--cap-drop ALL` plus selective `--cap-add` follows least privilege.

Q3: What does `no-new-privileges` do?
A3: Sets a kernel flag so processes cannot gain privileges through setuid binaries or file capabilities.

Q4: How to handle secrets properly?
A4: Not in image layers or `ENV` (visible in `docker inspect`/`history`). Use runtime injection, Docker/Swarm secrets, AWS Secrets Manager/SSM, or BuildKit secret mounts for build time.

Q5: What are seccomp and AppArmor?
A5: Kernel filters limiting syscalls (seccomp) and file/network access (AppArmor). Docker applies default profiles; never disable them with `unconfined` without strong reason.

Q6: How does image choice affect security?
A6: Fewer packages mean fewer CVEs and fewer attacker tools. Distroless/alpine/slim are smaller; scan with Trivy/Scout.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every production container, always (it is a baseline, not an option).
- Any internet-facing service or one handling user uploads/data.

❌ Avoid (or relax carefully) when:
- A specific tool truly needs a capability (e.g. tcpdump needs NET_RAW): add only that one, document why.
- Local dev needs writable code mounts: keep `read_only` and `cap_drop` in prod overlays, not dev.

---

## 📊 Visual Diagram
```
 Attacker exploits app bug
        |
 +------v-------------------------------------------+
 | Layer 1: non-root user       -> no root powers    |
 | Layer 2: cap_drop ALL        -> no raw sockets    |
 | Layer 3: read_only + tmpfs   -> cannot drop binary|
 | Layer 4: seccomp/AppArmor    -> dangerous syscalls blocked
 | Layer 5: mem/cpu/pids limits -> no miner / fork bomb
 | Layer 6: internal network    -> no call-home      |
 | Layer 7: no docker.sock / not privileged          |
 +------+-------------------------------------------+
        v
   Host kernel + other containers stay safe (defense in depth)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Least privilege | Give only needed permissions | सिर्फ ज़रूरी अनुमतियाँ देना |
| Capability | A slice of root's power | Root की शक्ति का एक हिस्सा |
| seccomp | Syscall filter | Syscalls पर filter |
| AppArmor | Mandatory access control profile | अनिवार्य access control profile |
| CVE | Public vulnerability ID | सार्वजनिक vulnerability ID |
| Defense in depth | Many layers of protection | सुरक्षा की कई परतें |

---

## ⚡ 3-Line Summary
English: Assume the app can be hacked and limit the damage: non-root, drop capabilities, read-only filesystem, limits.
Use small scanned images and keep secrets out of images.
Never mount docker.sock or use privileged mode in app containers.
Hindi: मानकर चलो कि app hack हो सकता है और नुकसान सीमित करो: non-root, capabilities हटाओ, read-only filesystem, limits।
छोटी scanned images लो और secrets को images से बाहर रखो।
App containers में कभी docker.sock mount या privileged mode मत इस्तेमाल करो।

---

## ➡️ Next Topic
**150. Privileged Mode — Risks** - the single flag that undoes almost all the hardening above.
