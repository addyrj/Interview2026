---

# 058. docker run — Complete Guide
# हिंदी में: docker run — पूरी गाइड

---

## 🔵 Simple Definition (English)
`docker run` creates a new container from an image and starts it (it is `docker create` + `docker start`). If the image is not local it pulls it first. Options before the image name control ports, env vars, volumes, networks, resource limits, restart policy and security.

## 🔵 सरल परिभाषा (Hindi)
`docker run` किसी image से नया container बनाता है और उसे start करता है (यह `docker create` + `docker start` है)। Image local न हो तो पहले pull करता है। Image के नाम से पहले के options ports, env vars, volumes, networks, resource limits, restart policy और security तय करते हैं।

---

## 🔴 Problem it Solves
Starting an app manually means installing runtimes, setting env vars, choosing ports and managing processes by hand. One `docker run` line gives a repeatable, isolated process with exactly the config you specify, the same on a laptop, VPS or CI.

## 🔴 यह क्यों बना? (Hindi)
App हाथ से चलाने का मतलब runtime install करना, env vars set करना, ports चुनना और process manage करना है। एक `docker run` line repeatable, isolated process देती है जिसमें वही config होती है जो आप बताते हैं, laptop, VPS या CI पर एक जैसी।

---

## 🟢 How it Works — Step by Step

```
Step 1 → CLI sends create request with all your options
Step 2 → If image missing locally -> pull from registry (Docker Hub, ECR, GHCR)
Step 3 → Daemon creates the writable layer, network endpoint, mounts, cgroup limits
Step 4 → Daemon starts the container's main process (ENTRYPOINT + CMD) as PID 1
Step 5 → Foreground mode attaches your terminal; -d returns the container ID immediately
Step 6 → Container stops when PID 1 exits; --rm deletes it afterwards, restart policy may restart it
```

Most-used options:
- `-d` detached, `-it` interactive terminal, `--rm` auto-remove, `--name` name
- `-p HOST:CONTAINER` publish port, `-e KEY=VAL` env var, `--env-file` file of env vars
- `-v` volume/bind mount, `--network` network, `-w` working dir, `-u` user
- `--restart no|on-failure[:N]|always|unless-stopped`
- `--memory`, `--cpus`, `--pids-limit` limits; `--read-only`, `--cap-drop`, `--security-opt` hardening

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → CLI आपके सारे options के साथ create request भेजता है
Step 2 → Image local न हो -> registry (Docker Hub, ECR, GHCR) से pull
Step 3 → Daemon writable layer, network endpoint, mounts, cgroup limits बनाता है
Step 4 → Daemon container का main process (ENTRYPOINT + CMD) PID 1 के रूप में चलाता है
Step 5 → Foreground में terminal attach होता है; -d तुरंत container ID लौटा देता है
Step 6 → PID 1 exit होने पर container रुकता है; --rm बाद में delete करता है, restart policy दोबारा चला सकती है
```

सबसे ज़्यादा इस्तेमाल होने वाले options:
- `-d` background, `-it` interactive terminal, `--rm` auto-delete, `--name` नाम
- `-p HOST:CONTAINER` port publish, `-e KEY=VAL` env var, `--env-file` env vars की file
- `-v` volume/bind mount, `--network` network, `-w` working dir, `-u` user
- `--restart no|on-failure[:N]|always|unless-stopped`
- `--memory`, `--cpus`, `--pids-limit` limits; `--read-only`, `--cap-drop`, `--security-opt` hardening

---

## 🟡 Real World Example
A quick production-like test of your FastAPI image on the VPS before wiring it into Compose: `docker run -d --name api --env-file .env -p 127.0.0.1:8000:8000 --restart unless-stopped --memory 512m ghcr.io/you/api:1.4.2`. Host Nginx proxies to `127.0.0.1:8000`. Zomato-style teams run exactly such lines (via orchestrators) with memory limits so one leaking service cannot take down the node.

## 🟡 Real Example Hindi mein
VPS पर Compose में जोड़ने से पहले अपनी FastAPI image का production जैसा quick test: `docker run -d --name api --env-file .env -p 127.0.0.1:8000:8000 --restart unless-stopped --memory 512m ghcr.io/you/api:1.4.2`। Host का Nginx `127.0.0.1:8000` पर proxy करता है। Zomato जैसी teams orchestrators के ज़रिए ऐसी ही lines memory limits के साथ चलाती हैं ताकि एक leak करने वाली service पूरा node न गिरा दे।

---

## 💻 Code / Config Example — Basic

```bash
# --- docker run basics ---
docker run hello-world                           # run once in foreground, prints message, exits
docker run -d --name web -p 8080:80 nginx:1.27-alpine   # detached nginx, host 8080 -> container 80
docker run --rm -it alpine:3.20 sh               # temporary interactive shell, deleted on exit
docker run -d --name cache redis:7-alpine        # redis with default settings
docker run --rm -e GREETING=hello alpine:3.20 sh -c 'echo $GREETING'   # pass env var to a command
docker run --rm -v "$(pwd)":/work -w /work node:20-alpine node --version  # mount current dir, set workdir
docker run -d --name api2 --restart unless-stopped -p 8000:8000 myapi:1.0   # auto-restart after crash/reboot
```

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# run-api-prod.sh - hardened docker run for a FastAPI container on a VPS
# Image tag is an example; replace with your own pinned version.
set -euo pipefail                                # strict shell mode

docker network inspect backend >/dev/null 2>&1 || docker network create backend   # make sure network exists
docker volume inspect api_uploads >/dev/null 2>&1 || docker volume create api_uploads   # and volume

docker run -d \
  --name api \
  --restart unless-stopped \
  --network backend \
  -p 127.0.0.1:8000:8000 \
  --env-file /srv/app/.env \
  -v api_uploads:/app/uploads \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --user 10001:10001 \
  --cap-drop ALL \
  --security-opt no-new-privileges:true \
  --memory 512m --memory-swap 512m \
  --cpus 1.0 \
  --pids-limit 200 \
  --health-cmd 'curl -fsS http://localhost:8000/health || exit 1' \
  --health-interval 30s --health-timeout 5s --health-retries 3 \
  --log-driver json-file --log-opt max-size=10m --log-opt max-file=3 \
  ghcr.io/example/api:1.4.2                      # last argument: image (+ optional command)

# What each group does:
#  --restart unless-stopped : restart on crash/reboot unless you stopped it
#  -p 127.0.0.1:8000:8000   : only host Nginx can reach it (not the internet)
#  --read-only + --tmpfs    : filesystem is immutable except /tmp and the uploads volume
#  --user / --cap-drop ALL  : no root, no Linux capabilities
#  no-new-privileges        : blocks setuid privilege escalation
#  --memory/--cpus/--pids   : limit blast radius of leaks and fork bombs
#  --health-*               : Docker marks it healthy/unhealthy
#  --log-opt                : rotate logs to protect the disk
```

---

## 🟠 My Stack Integration
- **FastAPI**: bind `127.0.0.1:8000`, run as non-root, `--env-file` for config; Uvicorn must listen on `0.0.0.0` inside the container.
- **Node.js**: same pattern with port 3000; `-e NODE_ENV=production`.
- **React**: no `docker run` for dev server in prod; serve the build with Nginx: `docker run -d -p 80:80 myreact:1.0`.
- **Nginx**: `docker run -d -p 80:80 -p 443:443 -v ./nginx.conf:/etc/nginx/nginx.conf:ro -v letsencrypt:/etc/letsencrypt:ro nginx:1.27-alpine`.
- **AWS**: the same options map to ECS task definition fields (`portMappings`, `environment`, `memory`, `readonlyRootFilesystem`).

```yaml
# docker-compose.yml - the advanced docker run above, expressed as Compose (preferred for production)
services:
  api:
    image: ghcr.io/example/api:1.4.2             # example tag
    restart: unless-stopped                      # --restart
    ports:
      - "127.0.0.1:8000:8000"                    # -p
    env_file:
      - .env                                     # --env-file
    volumes:
      - api_uploads:/app/uploads                 # -v
    read_only: true                              # --read-only
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=64m           # --tmpfs
    user: "10001:10001"                          # --user
    cap_drop:
      - ALL                                      # --cap-drop ALL
    security_opt:
      - no-new-privileges:true                   # --security-opt
    mem_limit: 512m                              # --memory
    cpus: 1.0                                    # --cpus
    pids_limit: 200                              # --pids-limit
volumes:
  api_uploads:                                   # named volume
```

Security: never use `--privileged` or `-v /var/run/docker.sock:/var/run/docker.sock` unless you fully accept root-equivalent exposure. Prefer `--env-file` or secrets over `-e PASSWORD=...` in shell history. Bind to `127.0.0.1` behind Nginx. Drop capabilities, use non-root users, and pin image tags.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `docker run nginx -p 80:80` (options after the image).
✅ Correct: `docker run -p 80:80 nginx`.

❌ Mistake 2: Port mapping `-p 8000` and expecting host port 8000.
✅ Correct: Give both: `-p 8000:8000`. The single form picks a random host port.

❌ Mistake 3: App listens on `127.0.0.1` inside the container, so published port gives "connection reset".
✅ Correct: Bind to `0.0.0.0` inside (`uvicorn --host 0.0.0.0`).

❌ Mistake 4: Forgetting `--name`, getting random names like `eager_curie`, and starting duplicates (`name already in use` on reruns).
✅ Correct: Always name production containers; remove old one first or use Compose.

❌ Mistake 5: Using `-d` with `--rm` and expecting to read logs after a crash.
✅ Correct: Without `--rm` the stopped container remains so `docker logs` still works.

---

## 🧠 Tricky Interview Question
You ran `docker run -d --restart always myapp`, then deliberately ran `docker stop myapp` for maintenance. The VPS reboots overnight and in the morning `myapp` is running again. Why, and how do you prevent it?

Answer: With `--restart always`, a container you stopped manually stays stopped only while the Docker daemon keeps running; when the daemon restarts (e.g. after a reboot) it starts the container again. With `--restart unless-stopped`, a manually stopped container stays stopped even after the daemon restarts. Use `unless-stopped` for predictable ops (change a live container with `docker update --restart unless-stopped myapp`). Note the health check in the advanced example needs `curl` inside the image.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `docker run`, `docker create` and `docker start`?
A1: `create` makes the container without starting it; `start` starts an existing one; `run` does create + start (and pull if needed).

Q2: What do `-p 8080:80` and `EXPOSE 80` mean?
A2: `-p` maps host port 8080 to container port 80 for outside access. `EXPOSE` only documents the port; it does not publish anything.

Q3: How do you pass many env vars?
A3: `--env-file .env` (lines `KEY=value`, no `export`, no quotes handling like a shell). Remember values appear in `docker inspect`.

Q4: What is PID 1 problem in containers?
A4: The main process is PID 1; it must handle signals and reap zombie processes. Shell-form `CMD` wraps in `sh -c` and may not forward SIGTERM. Use exec form and `--init` (tini) when needed.

Q5: How to limit memory, and what happens when exceeded?
A5: `--memory 512m`. If the process exceeds it, the kernel OOM-killer kills it (exit code 137) and the restart policy may restart it.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Quick tests, debugging, one-off jobs (`--rm`), running tools without installing them.
- Learning how options map to Compose/ECS fields.

❌ Avoid when:
- Running multi-container production stacks: use Compose files in git.
- Long commands with secrets typed on the shell.

---

## 📊 Visual Diagram
```
 docker run -d -p 8000:8000 --memory 512m myapi:1.0
        |
        v
 [pull image?] -> [create: layers + writable layer]
        |             + network (bridge, IP 172.17.0.2)
        |             + cgroup (512m RAM)
        v             + port rule: host:8000 -> 172.17.0.2:8000
   [start PID 1: uvicorn ...]
        |
   running --(process exits)--> stopped --(restart policy?)--> running
        |
   docker rm -> gone (volumes remain)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Detached (-d) | Run in background | Background में चलाना |
| Publish (-p) | Map host port to container | Host port को container से जोड़ना |
| Restart policy | When Docker restarts a container | Docker कब दोबारा चलाए |
| PID 1 | Main process of the container | Container का मुख्य process |
| cgroup | Kernel resource limiter | Kernel का resource limiter |
| OOM kill | Killed for exceeding memory | Memory सीमा पार करने पर kill |

---

## ⚡ 3-Line Summary
English: `docker run` creates and starts a container; options go before the image.
Name it, map ports, set env, mount volumes, add restart policy and limits.
Harden with non-root, read-only and dropped capabilities.
Hindi: `docker run` container बनाकर चालू करता है; options image से पहले आते हैं।
नाम दें, ports map करें, env set करें, volumes mount करें, restart policy और limits लगाएँ।
Non-root, read-only और dropped capabilities से hardening करें।

---

## ➡️ Next Topic
**059. docker ps + docker ps -a.** After running containers, learn to list them and read their status.

---
