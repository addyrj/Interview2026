---

# 212. Docker Security Hardening
# हिंदी में: Docker Security Hardening

---

## 🔵 Simple Definition (English)
**Docker security hardening** means reducing what an attacker can do if they break into a container: least privilege (non-root, dropped capabilities), restricted filesystem, limited syscalls, network isolation, scanned minimal images, and a locked-down Docker host and daemon.

## 🔵 सरल परिभाषा (Hindi)
**Docker security hardening** का मतलब है कि अगर attacker container में घुस भी जाए तो वह कितना कम नुकसान कर सके: least privilege (non-root, dropped capabilities), restricted filesystem, सीमित syscalls, network isolation, scanned minimal images, और locked-down Docker host व daemon।

---

## 🔴 Problem it Solves
Containers are **not** virtual machines. They share the host kernel. By default a container process runs as root inside, has 14 Linux capabilities, can write anywhere in its filesystem, and can reach every other container on the default bridge. A single RCE bug in your Express app then gives the attacker a powerful foothold, and kernel bugs or misconfigurations (privileged mode, docker.sock) can turn it into full host takeover.

## 🔴 यह क्यों बना? (Hindi)
Containers virtual machines **नहीं** हैं। वे host kernel share करते हैं। Default में container के अंदर process root चलाता है, उसके पास 14 Linux capabilities होती हैं, वह filesystem में कहीं भी लिख सकता है, और default bridge पर हर दूसरे container तक पहुँच सकता है। तब Express app में एक RCE bug attacker को मज़बूत foothold दे देता है, और kernel bugs या misconfiguration (privileged mode, docker.sock) से पूरे host पर कब्ज़ा हो सकता है।

---

## 🟢 How it Works — Step by Step

```
Layer 1 IMAGE    → minimal base (alpine/distroless), no secrets, scan with Trivy
Layer 2 USER     → USER non-root (UID >= 10000)
Layer 3 FS       → --read-only + tmpfs for /tmp
Layer 4 CAPS     → --cap-drop ALL, add back only what is needed
Layer 5 SYSCALLS → seccomp profile (default or custom)
Layer 6 MAC      → AppArmor / SELinux profile
Layer 7 NETWORK  → user-defined networks, internal: true, no published DB ports
Layer 8 RESOURCE → memory, CPU, pids limits
Layer 9 HOST     → patched kernel, rootless Docker / userns-remap, protect docker.sock
```

## 🟢 कैसे काम करता है? (Hindi)
```
Layer 1 IMAGE    → minimal base (alpine/distroless), secrets नहीं, Trivy से scan
Layer 2 USER     → USER non-root (UID >= 10000)
Layer 3 FS       → --read-only + /tmp के लिए tmpfs
Layer 4 CAPS     → --cap-drop ALL, सिर्फ ज़रूरी वापस जोड़ो
Layer 5 SYSCALLS → seccomp profile (default या custom)
Layer 6 MAC      → AppArmor / SELinux profile
Layer 7 NETWORK  → user-defined networks, internal: true, DB ports publish नहीं
Layer 8 RESOURCE → memory, CPU, pids limits
Layer 9 HOST     → patched kernel, rootless Docker / userns-remap, docker.sock की सुरक्षा
```

---

## 🟡 Real World Example
A payments startup runs a Node.js webhook receiver exposed to the internet. A dependency has a prototype-pollution to RCE bug. With default settings the attacker would get root in the container, download tools with curl, write a crypto miner to disk and scan the internal network. With hardening: the user is UID 10001, root filesystem read-only (cannot drop binaries), all caps dropped (no raw sockets), no shell in a distroless image, DB on an internal network, and limits stop the miner from eating CPU. The exploit succeeds but achieves almost nothing, and alerts fire on the restarts.

## 🟡 Real Example Hindi mein
एक payments startup internet पर खुला Node.js webhook receiver चलाता है। एक dependency में prototype-pollution से RCE bug है। Default settings में attacker को container में root मिलता, curl से tools download करता, disk पर crypto miner लिखता और internal network scan करता। Hardening के साथ: user UID 10001, root filesystem read-only (binaries नहीं लिख सकता), सभी caps dropped (raw sockets नहीं), distroless image में shell नहीं, DB internal network पर, और limits miner को CPU खाने नहीं देते। Exploit सफल होता है पर लगभग कुछ हासिल नहीं होता, और restarts पर alerts आते हैं।

---

## 💻 Code / Config Example — Basic

```bash
# Run a container with the main hardening flags
docker run -d \
  --name webhook \
  --user 10001:10001 \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --cap-drop ALL \
  --security-opt no-new-privileges:true \
  --memory 256m --cpus 0.5 --pids-limit 100 \
  -p 127.0.0.1:3000:3000 \
  myorg/webhook:1.4.2
# --user                run as non-root UID:GID
# --read-only           root filesystem is immutable
# --tmpfs               writable RAM dir, no executables allowed
# --cap-drop ALL        drop every Linux capability
# no-new-privileges     setuid binaries cannot gain rights
# --memory/--cpus/--pids-limit  resource caps vs DoS
# -p 127.0.0.1:...      publish only on localhost (reverse proxy in front)
```

Check what you ended up with:
```bash
docker inspect webhook --format 'user={{.Config.User}} ro={{.HostConfig.ReadonlyRootfs}} caps_drop={{.HostConfig.CapDrop}} priv={{.HostConfig.Privileged}}'
# prints the effective security settings so you can verify them
```

---

## 💻 Code / Config Example — Advanced

```dockerfile
# Dockerfile (hardened Node.js, multi-stage, distroless runtime)
FROM node:20-alpine AS build
# build stage has npm and compilers; it will NOT ship
WORKDIR /app
# working dir
COPY package*.json ./
# manifests first
RUN npm ci --omit=dev
# production deps only
COPY src ./src
# only the source folder, not the whole repo

FROM gcr.io/distroless/nodejs20-debian12:nonroot
# runtime: no shell, no package manager, non-root user preset (example tag)
WORKDIR /app
# working dir in final image
COPY --from=build /app /app
# copy app and node_modules from build stage
USER 65532:65532
# explicit non-root UID (distroless nonroot user)
EXPOSE 3000
# documentation only
CMD ["src/index.js"]
# distroless node image uses node as entrypoint, so pass only the script
```

```yaml
# docker-compose.yml (hardened service + isolated networks)
services:
  webhook:
    image: myorg/webhook:1.4.2           # pinned, scanned image (example)
    user: "65532:65532"                  # non-root
    read_only: true                      # immutable root fs
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=64m   # scratch space only
    cap_drop: [ALL]                      # no capabilities
    security_opt:
      - no-new-privileges:true           # no escalation
      - seccomp=default                  # explicit default profile (Docker's default anyway)
    pids_limit: 100                      # fork-bomb protection
    mem_limit: 256m                      # memory cap
    cpus: 0.5                            # CPU cap
    networks: [front, back]              # only needed networks
    ports:
      - "127.0.0.1:3000:3000"            # localhost only
    healthcheck:
      test: ["CMD", "/nodejs/bin/node", "-e", "require('http').get('http://localhost:3000/health',r=>process.exit(r.statusCode===200?0:1)).on('error',()=>process.exit(1))"]   # distroless has no curl; use node
      interval: 30s                      # probe interval
      timeout: 3s                        # probe timeout
      retries: 3                         # failures before unhealthy

  db:
    image: postgres:16-alpine            # example tag
    networks: [back]                     # NOT on the front network
    cap_drop: [ALL]                      # drop caps first
    cap_add: [CHOWN, SETUID, SETGID, FOWNER, DAC_OVERRIDE]   # Postgres entrypoint needs these
    security_opt:
      - no-new-privileges:true           # no escalation
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/pg   # secret file
    secrets: [pg]                        # mount secret
    volumes:
      - pgdata:/var/lib/postgresql/data  # data

networks:
  front:                                 # reachable by proxy
  back:
    internal: true                       # no internet egress

secrets:
  pg:
    file: ./secrets/pg.txt               # keep out of git

volumes:
  pgdata:
```

Daemon-level hardening (`/etc/docker/daemon.json`):
```json
{
  "icc": false,
  "no-new-privileges": true,
  "live-restore": true,
  "userland-proxy": false,
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
```
`icc:false` blocks container-to-container talk on the default bridge; `live-restore` keeps containers alive when dockerd restarts. Test after changing; `icc:false` can break apps that rely on the default bridge.

Verification note: YAML and JSON parsed; Dockerfile instructions checked for validity. Nothing was built or run here; the distroless healthcheck path and Postgres capability list should be tested on your Docker version.

---

## 🟠 My Stack Integration
- **Node.js/FastAPI**: build in a full image, run on distroless/slim, non-root; FastAPI needs only a writable `/tmp`.
- **React**: Nginx-unprivileged image (`nginxinc/nginx-unprivileged`) listens on 8080 and runs as non-root, no caps needed to bind port 80.
- **Nginx on VPS**: Docker edits iptables directly and **bypasses UFW**; so publishing `-p 5432:5432` opens the world. Bind to `127.0.0.1` or use `DOCKER-USER` chain rules.
- **AWS**: security groups allow only 80/443/22 (from your IP); IMDSv2 required (`HttpTokens=required`) so a compromised container cannot steal instance credentials; ECR scan-on-push; use IAM task/instance roles with least privilege.

```bash
# Block container access to the EC2 metadata service (defense in depth)
sudo iptables -I DOCKER-USER -d 169.254.169.254 -j DROP   # containers cannot reach IMDS
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `--privileged` "to make it work".
✅ Correct: Find the exact capability or device needed (`--cap-add NET_ADMIN`, `--device /dev/x`).

❌ Mistake 2: Mounting `/var/run/docker.sock` into a container (CI tools, Portainer).
✅ Correct: Avoid; if unavoidable, use a socket proxy limiting API calls, or rootless Docker.

❌ Mistake 3: Believing UFW protects published container ports.
✅ Correct: Bind to localhost, use `DOCKER-USER` rules, and verify with `nmap` from outside.

❌ Mistake 4: Secrets in `ENV` inside the Dockerfile.
✅ Correct: Runtime secrets, or BuildKit `--mount=type=secret` for build-time needs.

❌ Mistake 5: Scanning once, then never again.
✅ Correct: Scan in CI and on a schedule; new CVEs appear against old images.

---

## 🧠 Tricky Interview Question
**Q:** The container runs as non-root. Can an attacker still become root on the host?

**Answer:** Yes, in several cases: the container is privileged or has dangerous capabilities (`SYS_ADMIN`, `SYS_PTRACE`); docker.sock is mounted (the attacker can start a new privileged container mounting `/`); a sensitive host path is bind-mounted writable; or a kernel/runc vulnerability allows escape. Non-root reduces risk but is one layer. Also, UID 0 inside maps to UID 0 on the host unless user namespaces/rootless Docker are used, so a root process that escapes is root on the host.

---

## ⚫ Interview Questions + Answers

**Q1: Containers vs VMs, security-wise?**
A1: VMs have their own kernel behind a hypervisor (strong isolation). Containers share the host kernel and rely on namespaces, cgroups, capabilities and seccomp, so the attack surface is the kernel syscall interface. Hence layered hardening.

**Q2: What is rootless Docker or userns-remap?**
A2: The daemon and containers run as an unprivileged host user, or container root maps to a high host UID. Even if an attacker escapes as "root", they are an unprivileged user on the host.

**Q3: What does `no-new-privileges` do?**
A3: Sets a kernel flag so the process and children cannot gain extra privileges through setuid/setgid binaries or file capabilities.

**Q4: How do you handle vulnerabilities found by Trivy in the base image?**
A4: Update the base/rebuild, switch to a slimmer/distroless base, check if the vulnerable package is even used, and document exceptions (`.trivyignore`) with an expiry. Prioritise fixable CRITICAL/HIGH.

**Q5: Why avoid `latest` and unknown public images?**
A5: Supply-chain risk. Use official or verified images, pin versions/digests, and consider signing with cosign and verifying in CI.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Anything internet-facing, multi-tenant, or handling money/PII
- Compliance needs (PCI, SOC2, ISO 27001)

❌ Avoid when:
- Never skip fully; but local throwaway dev containers can skip read-only/distroless for convenience. Do not harden blindly in production without testing, since over-restriction causes outages.

---

## 📊 Visual Diagram
```
 Attacker -> RCE in app
     |
     v
 [non-root user] -> cannot bind low ports, edit system files
     |
 [read-only fs ] -> cannot persist malware
     |
 [caps dropped ] -> no raw sockets, no mount, no chown
     |
 [seccomp/AppArmor] -> dangerous syscalls blocked
     |
 [internal network] -> cannot reach DB/internet freely
     |
 [limits       ] -> cannot exhaust host
     v
 Contained blast radius
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Least privilege | Give only needed permissions | सिर्फ ज़रूरी permissions देना |
| Capability | Fine-grained slice of root power | Root की शक्ति का छोटा हिस्सा |
| Blast radius | Damage if compromised | Compromise होने पर नुकसान का दायरा |
| Rootless | Docker running without root | बिना root के चलने वाला Docker |
| Distroless | Image without shell/package manager | बिना shell/package manager की image |

---

## ⚡ 3-Line Summary
English: Containers share the host kernel, so you must layer defences: non-root, read-only, no caps, seccomp, network isolation, limits.
Never use privileged mode or expose docker.sock; remember Docker bypasses UFW.
Scan continuously and test hardened settings before production.

Hindi: Containers host kernel share करते हैं, इसलिए परतों में सुरक्षा चाहिए: non-root, read-only, caps नहीं, seccomp, network isolation, limits।
Privileged mode या docker.sock कभी expose मत करो; याद रखो Docker UFW को bypass करता है।
लगातार scan करो और production से पहले hardened settings test करो।

---

## ➡️ Next Topic
**213. Non-Root User Setup**: the first and most important hardening step, done properly in Dockerfiles.

---
