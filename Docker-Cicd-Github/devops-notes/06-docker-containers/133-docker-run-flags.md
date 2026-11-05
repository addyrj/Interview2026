---

# 133. docker run Flags (-d, -p, -v, -e, --name, --network)
# हिंदी में: docker run के Flags

---

## 🔵 Simple Definition (English)
`docker run [OPTIONS] IMAGE [COMMAND]` creates and starts a container, and its flags control how: `-d` runs in background, `-p` publishes ports, `-v` mounts storage, `-e` sets environment variables, `--name` names it, `--network` picks the network.

## 🔵 सरल परिभाषा (Hindi)
`docker run [OPTIONS] IMAGE [COMMAND]` container बनाता और चलाता है, और flags तय करते हैं कैसे: `-d` background में, `-p` port publish, `-v` storage mount, `-e` environment variables, `--name` नाम, `--network` network चुनना।

---

## 🔴 Problem it Solves
A bare `docker run myimage` gives a container that blocks your terminal, has a random name, no reachable port, no persistent data and no config. Real apps need all of that. Flags let one image behave differently in dev, staging and prod without rebuilding it (build once, configure at run time).

## 🔴 यह क्यों बना? (Hindi)
सिर्फ़ `docker run myimage` से ऐसा container बनता है जो terminal रोक लेता है, random नाम, कोई reachable port, कोई persistent data और config नहीं। असली apps को यह सब चाहिए। Flags से एक ही image dev, staging और prod में बिना rebuild के अलग व्यवहार करती है (एक बार build, run-time पर configure)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → CLI parses flags and sends a create request to dockerd
Step 2 → dockerd pulls the image if missing locally
Step 3 → Applies flags: name, env, network attach, volume mounts, port rules (iptables), limits
Step 4 → Creates writable layer and starts PID 1 (CMD/ENTRYPOINT, or your COMMAND override)
Step 5 → With -d: prints container ID and returns; without -d: attaches your terminal to output
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → CLI flags parse करके dockerd को create request भेजता है
Step 2 → Image local में न हो तो dockerd pull करता है
Step 3 → Flags लागू: name, env, network, volume mounts, port rules (iptables), limits
Step 4 → Writable layer बनती है और PID 1 (CMD/ENTRYPOINT या आपका COMMAND) शुरू
Step 5 → -d के साथ: container ID print करके लौट आता है; बिना -d: terminal attach रहता है
```

---

## 🟡 Real World Example
Deploying a FastAPI service on an AWS EC2 box: one command combines everything: detached, named `pay-api`, port 8000 bound to localhost for Nginx, `.env` file for secrets, a volume for uploads, on a custom network next to Postgres. The same image on your laptop runs with different `-e` values and no volume.

## 🟡 Real Example Hindi mein
AWS EC2 पर FastAPI service deploy: एक command में सब: detached, नाम `pay-api`, port 8000 सिर्फ़ localhost पर (Nginx के लिए), secrets के लिए `.env` file, uploads के लिए volume, और Postgres के पास custom network पर। वही image laptop पर अलग `-e` values और बिना volume के चलती है।

---

## 💻 Code / Config Example — Basic
```bash
#!/usr/bin/env bash
# run-basic.sh - the six most used flags
docker network create appnet                      # user-defined network (name resolution works here)

docker run \
  -d \
  --name web \
  --network appnet \
  -p 8080:80 \
  -v "$PWD/site:/usr/share/nginx/html:ro" \
  -e TZ=Asia/Kolkata \
  nginx:1.27-alpine
# -d                  : detached, run in background and print container ID
# --name web          : fixed readable name instead of random one
# --network appnet    : attach to our network, not default bridge
# -p 8080:80          : host port 8080 -> container port 80
# -v host:ctr:ro      : bind mount ./site read-only into nginx web root
# -e TZ=...           : environment variable inside the container
# nginx:1.27-alpine   : image (example tag)

curl -s localhost:8080 | head -n 3                # test it
docker rm -f web                                  # cleanup
```

## 💻 Code / Config Example — Advanced
```bash
#!/usr/bin/env bash
# run-prod.sh - production-style run for a Node.js API (example values)
set -euo pipefail                                         # stop on any error

docker run -d \
  --name orders-api \
  --hostname orders-api \
  --network backend \
  --restart unless-stopped \
  --init \
  -p 127.0.0.1:3000:3000 \
  --env-file /opt/orders/.env.production \
  -e NODE_ENV=production \
  -v orders_uploads:/app/uploads \
  --read-only --tmpfs /tmp \
  --memory 512m --cpus 1.0 \
  --user 1000:1000 \
  --cap-drop ALL \
  --security-opt no-new-privileges:true \
  --log-opt max-size=10m --log-opt max-file=3 \
  --health-cmd "node -e \"fetch('http://localhost:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))\"" \
  --health-interval 15s \
  myorg/orders-api:1.4.2
# --hostname          : hostname inside container
# --restart           : come back after crash/reboot, not after manual stop
# --init              : tini as PID 1, proper signals
# -p 127.0.0.1:...    : reachable only from the host (Nginx), not the internet
# --env-file          : secrets from a file (chmod 600), not typed in shell history
# -v named volume     : persistent uploads managed by Docker
# --read-only+tmpfs   : immutable root fs, RAM-only /tmp
# --memory/--cpus     : resource caps (topic 138)
# --user              : do not run as root (image must allow it)
# --cap-drop ALL      : remove all Linux capabilities
# no-new-privileges   : block setuid privilege escalation
# --log-opt           : rotate logs (topic 139/140)
# --health-*          : healthcheck (topic 142); fetch needs Node 18+
```
```bash
# Other flags worth knowing
docker run -it --rm alpine:3.20 sh        # -i keep stdin, -t pseudo-terminal, --rm auto-delete
docker run --rm -w /app -v "$PWD":/app node:20-alpine node -v   # -w working dir for the command
docker run --entrypoint /bin/sh -it myorg/api:1.4.2             # override ENTRYPOINT for debugging
```

---

## 🟠 My Stack Integration
**Node.js**: `-e NODE_ENV=production`, `--init`, and a named volume only if you write files.
**FastAPI**: `-p 127.0.0.1:8000:8000`, `--env-file`, command override like `uvicorn app.main:app --host 0.0.0.0` (must bind 0.0.0.0).
**React**: `docker run -d -p 127.0.0.1:8081:80 myorg/web:2.0.0` (Nginx image with the build output).
**VPS + Nginx**: publish to 127.0.0.1 only and let host Nginx terminate TLS.
**AWS**: the same options map to ECS task definition fields (portMappings, environment, mountPoints, logConfiguration).

```nginx
# /etc/nginx/conf.d/api.conf - host Nginx in front of the container (not tested here)
server {
  listen 80;                                   # plain HTTP (add TLS with certbot in real use)
  server_name api.example.com;                 # your domain
  location / {
    proxy_pass http://127.0.0.1:3000;          # container published on localhost only
    proxy_set_header Host $host;               # pass original host
    proxy_set_header X-Forwarded-For $remote_addr;   # pass client IP
  }
}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Flags after the image name, like `docker run myimage -p 80:80`.
✅ Correct: everything after IMAGE is passed to the container as arguments. Put options before the image.

❌ Mistake 2: `-p 3000:3000` for a database or admin API on a public VPS.
✅ Correct: `-p 127.0.0.1:...` or no publish; Docker's iptables rules can bypass UFW.

❌ Mistake 3: Secrets via `-e DB_PASSWORD=...` typed in the shell.
✅ Correct: `--env-file` with strict file permissions, or Docker/AWS secrets.

❌ Mistake 4: App listens on `127.0.0.1` inside the container, so `-p` shows nothing.
✅ Correct: bind `0.0.0.0` inside the container.

❌ Mistake 5: Running as root with all capabilities.
✅ Correct: `--user`, `--cap-drop ALL`, `no-new-privileges`.

---

## 🧠 Tricky Interview Question
`docker run -d -p 8080:80 nginx` works. Then `docker run -d -p 8080:80 nginx` again fails. Why, and what if you drop `-p` on the second?

Answer: A host port can be bound by only one container; the second fails with "port is already allocated". Without `-p` the container runs but is unreachable from the host (still reachable by other containers on the same network, using its IP or name on user-defined networks). Use a different host port, or a reverse proxy.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `-d` and `-it`?
A1: `-d` detaches and runs in the background; `-it` keeps stdin open with a terminal for interactive shells.

Q2: What does `-v` do vs `--mount`?
A2: Both mount storage. `-v` is short syntax; `--mount type=bind,src=...,dst=...` is explicit and errors if the host path is missing (while `-v` silently creates a directory).

Q3: `-e` vs `--env-file`?
A3: `-e KEY=VAL` sets one variable inline; `--env-file` loads many from a file, keeping them out of shell history.

Q4: Why use `--name`?
A4: Predictable name for scripts, logs, and DNS on user-defined networks; otherwise Docker generates names like `eager_turing`.

Q5: Why a custom network instead of default bridge?
A5: User-defined bridges give automatic DNS by container name and better isolation.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Quick single-container runs, debugging, one-off jobs.
- Simple VPS deploys scripted by CI.

❌ Avoid when:
- A stack has many services: long commands are error-prone; use Compose.
- You need self-healing multi-node scheduling: use Kubernetes/ECS.

---

## 📊 Visual Diagram
```
 docker run -d --name api --network backend -p 127.0.0.1:3000:3000 -v data:/app/data -e K=V IMAGE
      |        |            |                |                       |                |
      |        |            |                |                       |                +--> env in container
      |        |            |                |                       +--> volume mount
      |        |            |                +--> host:container port rule
      |        |            +--> joins network (DNS by name)
      |        +--> container name
      +--> background

 Internet -> Nginx(host:80/443) -> 127.0.0.1:3000 -> [container api:3000] -> db (network backend)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Detached (-d) | Run in background | Background में चलाना |
| Publish (-p) | Map host port to container | Host port को container से जोड़ना |
| Bind mount | Host folder mounted in container | Host folder का mount |
| Named volume | Docker-managed storage | Docker द्वारा managed storage |
| env-file | File of environment variables | Env variables की file |
| Capability | Fine-grained root power | Root की छोटी शक्ति |

---

## ⚡ 3-Line Summary
English: `docker run` flags configure name, network, ports, storage, env and security at run time.
Put options before the image name; publish only what you need, on 127.0.0.1 when behind Nginx.
Use Compose when commands get long.

Hindi: `docker run` flags run-time पर name, network, ports, storage, env और security तय करते हैं।
Options image के नाम से पहले लिखें; सिर्फ़ ज़रूरी port publish करें, Nginx के पीछे हो तो 127.0.0.1 पर।
Command लंबी हो जाए तो Compose इस्तेमाल करें।

---

## ➡️ Next Topic
**134. Port Mapping (-p)**: the most misunderstood flag, with host IP binding, UDP, random ports and the firewall bypass issue.
