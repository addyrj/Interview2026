---

# 143. Exec into Container
# हिंदी में: Container के अंदर जाना (docker exec)

---

## 🔵 Simple Definition (English)
`docker exec` runs a new command inside an already running container. With `-it` and a shell (`sh` or `bash`) it gives you an interactive terminal inside, like SSH but without SSH. In Compose: `docker compose exec <service> <cmd>`. In Kubernetes: `kubectl exec`.

## 🔵 सरल परिभाषा (Hindi)
`docker exec` पहले से चल रहे container के अंदर एक नया command चलाता है। `-it` और shell (`sh` या `bash`) के साथ यह अंदर interactive terminal देता है, SSH जैसा पर बिना SSH के। Compose में: `docker compose exec <service> <cmd>`। Kubernetes में: `kubectl exec`।

---

## 🔴 Problem it Solves
Before containers you SSH into a server to inspect files, test DNS or run a migration. Containers have no SSH daemon (and should not). You still need to check env vars, curl a dependency, run `npm run migrate`, or open `psql`. `docker exec` gives that access without changing the image or exposing another port.

## 🔴 यह क्यों बना? (Hindi)
Containers से पहले आप server में SSH करके files देखते, DNS test करते या migration चलाते थे। Containers में SSH daemon नहीं होता (और होना भी नहीं चाहिए)। फिर भी env vars देखने, dependency पर curl करने, `npm run migrate` चलाने या `psql` खोलने की ज़रूरत पड़ती है। `docker exec` बिना image बदले या नया port खोले यह access देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You run: docker exec -it api sh
Step 2 → CLI calls the Docker API: create an exec instance for container "api"
Step 3 → containerd/runc starts the new process inside the SAME namespaces
         (pid, net, mount, ipc) and cgroup as the container's main process
Step 4 → -i keeps stdin open, -t allocates a pseudo-TTY for a proper terminal
Step 5 → You work inside; the exec'd process is NOT PID 1
Step 6 → Exit the shell: only that process ends, the container keeps running
Step 7 → If the container stops, all exec sessions end with it
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप चलाते हैं: docker exec -it api sh
Step 2 → CLI Docker API से container "api" के लिए exec instance बनवाता है
Step 3 → containerd/runc नया process उसी namespaces (pid, net, mount, ipc)
         और cgroup में शुरू करता है जिसमें container का main process है
Step 4 → -i stdin खुला रखता है, -t सही terminal के लिए pseudo-TTY देता है
Step 5 → आप अंदर काम करते हैं; exec वाला process PID 1 नहीं होता
Step 6 → Shell से निकलो: सिर्फ़ वही process खत्म होता है, container चलता रहता है
Step 7 → Container रुके तो सारे exec sessions उसके साथ खत्म
```

---

## 🟡 Real World Example
A Bengaluru e-commerce site shows "500 error on checkout" after a deploy. The engineer runs `docker exec -it api sh`, then `env | grep DB_` and sees `DB_HOST=localhost` because a compose variable was missing. From the same shell, `nc -zv db 5432` confirms the DB is reachable by service name. They fix the compose file, redeploy, and then run the pending migration with `docker compose exec api npm run migrate`. No server restart, no new image.

## 🟡 Real Example Hindi mein
Bengaluru की एक e-commerce site deploy के बाद checkout पर "500 error" दिखाती है। Engineer `docker exec -it api sh` चलाता है, फिर `env | grep DB_` से देखता है कि `DB_HOST=localhost` है क्योंकि compose variable छूट गया था। उसी shell में `nc -zv db 5432` से confirm होता है कि DB service name से पहुँच में है। वे compose file ठीक करके redeploy करते हैं, फिर pending migration `docker compose exec api npm run migrate` से चलाते हैं। न server restart, न नई image।

---

## 💻 Code / Config Example — Basic

```bash
# Open an interactive shell (alpine images have sh, not bash)
docker exec -it api sh
# -i keep stdin open; -t allocate a terminal; api is the container name; sh is the command

# Use bash when the image has it (debian/ubuntu based)
docker exec -it api bash
# fails with "executable file not found" on alpine, so fall back to sh

# Run one command without an interactive session
docker exec api node -v
# prints the Node version and returns the command's exit code

# Run as a specific user (default is the image's USER)
docker exec -u root api id
# -u root overrides the user for this exec only (needs permission to do so)

# Set a working directory and env var for the exec'd command
docker exec -w /app -e DEBUG=1 api node scripts/check.js
# -w working directory; -e environment variable only for this process

# Open a Postgres shell in the db container
docker exec -it db psql -U postgres -d appdb
# psql opens interactive SQL; -U user; -d database

# Compose version (finds the container by service name)
docker compose exec api sh
# no need to know the generated container name; use -T to disable TTY in scripts
```

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# diag.sh: non-interactive diagnostic bundle from a running container
set -euo pipefail                                   # strict mode: stop on errors

C="${1:?usage: diag.sh <container>}"                # container name is required

# Confirm the container is running before exec (exec fails on stopped ones)
[ "$(docker inspect -f '{{.State.Running}}' "$C")" = "true" ] || { echo "not running" >&2; exit 1; }

echo "== whoami / id =="                            # section header
docker exec "$C" id                                  # which user the app runs as

echo "== processes =="                               # section header
docker exec "$C" ps aux                              # processes inside (needs procps/busybox ps)

echo "== listening ports =="                         # section header
docker exec "$C" sh -c 'netstat -tln 2>/dev/null || ss -tln'   # fallback if netstat is absent

echo "== DNS and connectivity =="                    # section header
docker exec "$C" sh -c 'getent hosts db || nslookup db'        # can we resolve the DB service?

echo "== disk usage =="                              # section header
docker exec "$C" df -h /                             # writable layer free space

echo "== env (secrets masked) =="                    # section header
docker exec "$C" env | sed -E 's/(PASSWORD|SECRET|TOKEN|KEY)=.*/\1=***masked***/I'   # hide secrets
```

```yaml
# docker-compose.yml: make exec practical AND safer
services:
  api:
    image: ghcr.io/acme/node-api:1.8.3     # Node.js API (example tag)
    user: "1000:1000"                      # non-root, so exec shells are non-root too
    read_only: true                        # root filesystem read-only limits damage from exec
    tmpfs:
      - /tmp                               # writable temp space for the app
    cap_drop:
      - ALL                                # drop all Linux capabilities
    security_opt:
      - no-new-privileges:true             # block privilege escalation via setuid
    init: true                             # tini as PID 1 reaps zombie exec processes
```

```bash
# One-off container (not exec) when the service is crashing and cannot be exec'd into
docker compose run --rm --no-deps --entrypoint sh api -c "ls -l /app && env | sort"
# run creates a NEW container from the same image/config; --rm cleans up;
# --no-deps skips starting dependencies; --entrypoint replaces the failing command
```

Shell blocks passed `bash -n` and the YAML was parsed; commands were not run against a live container here.

---

## 🟠 My Stack Integration
Node.js image (alpine): `docker exec -it api sh`; run `npm run migrate` or `node -e` checks. FastAPI: `docker compose exec api python -c "import app; print('ok')"` or `alembic upgrade head`. Nginx container: `docker exec web nginx -t` to validate config, `nginx -s reload` to reload without downtime. On a VPS, SSH into the host once, then exec; never run an SSH server inside containers. For ECS use `aws ecs execute-command` (ECS Exec) with SSM.

```bash
# Safe config reload for the React/Nginx container on the VPS
docker exec web nginx -t && docker exec web nginx -s reload
# nginx -t validates syntax; && ensures reload runs only if the test passed
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Editing code or config inside a container with `docker exec` and expecting it to persist.
✅ Correct: Changes live in the writable layer and vanish on recreate. Fix the image, compose file or volume instead.

❌ Mistake 2: Using `docker exec -it` inside CI scripts, causing "the input device is not a TTY".
✅ Correct: Drop `-t` (or use `docker compose exec -T`) in non-interactive pipelines.

❌ Mistake 3: Running `docker exec -u root` or adding `--privileged` habitually.
✅ Correct: Debug as the app user first; give root only when required and for that command only.

❌ Mistake 4: Trying to exec into a crash-looping or stopped container.
✅ Correct: Use `docker logs`, then `docker run --rm -it --entrypoint sh image` or `docker compose run` to inspect.

---

## 🧠 Tricky Interview Question
You `docker exec -it web sh` and run `kill 1` to restart nginx, but nothing happens. Why?

Answer: PID 1 inside a container is special. The kernel ignores signals sent from within the PID namespace to PID 1 unless that process has installed a handler for that signal (`SIGKILL` and `SIGSTOP` from inside the namespace are also ignored). So `kill 1` does nothing for processes without handlers. To stop or restart the container use `docker restart web` or `docker stop web` from the host; for Nginx config reload use `nginx -s reload`. Running with `init: true` also changes who PID 1 is.

---

## ⚫ Interview Questions + Answers

Q1: `docker exec` vs `docker attach`?
A1: `exec` starts a NEW process in the container; exiting it does not affect the container. `attach` connects to the main process's stdin/stdout; Ctrl+C or exit can stop the container.

Q2: `docker exec` vs `docker run`?
A2: `exec` uses an existing running container. `run` creates a new container from an image, then starts it.

Q3: Can you exec into a stopped container?
A3: No. Start it first, or use `docker run --rm -it --entrypoint sh <image>`, or `docker cp` to copy files out of the stopped container.

Q4: Is exec a security risk?
A4: Yes. Whoever has Docker socket access can exec as root into any container and read secrets. Restrict the `docker` group, audit access, and in Kubernetes limit the `pods/exec` RBAC verb.

Q5: How to debug a distroless image with no shell?
A5: Use `docker debug` (Docker Desktop/Pro feature), `kubectl debug` with an ephemeral container, or build a `:debug` variant of the image with busybox.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Quick inspection, one-off admin tasks (migrations, psql, nginx -t)
- Verifying env vars, DNS and connectivity from inside the network

❌ Avoid when:
- You are "fixing production by hand" inside a container (configuration drift)
- Automating routine tasks (put them in the image, CI, or a Job)
- On shells-less minimal images without a debugging plan

---

## 📊 Visual Diagram
```
  HOST
  ┌───────────────────────────────────────────────────────────┐
  │  docker exec -it api sh                                   │
  │        │  (Docker API / containerd / runc)                │
  │        ▼                                                  │
  │  ┌──────────────── container "api" ───────────────────┐   │
  │  │ shared namespaces: pid, net, mnt, ipc + cgroup     │   │
  │  │                                                    │   │
  │  │  PID 1: node server.js     (main process)          │   │
  │  │  PID 27: sh                (your exec session)     │   │
  │  └────────────────────────────────────────────────────┘   │
  │  exit sh -> PID 27 ends, PID 1 keeps running              │
  └───────────────────────────────────────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| exec | Run a command in a running container | चलते container में command चलाना |
| -it | Interactive + terminal flags | Interactive + terminal flags |
| PID 1 | The container's main process | Container का मुख्य process |
| attach | Connect to main process streams | मुख्य process की streams से जुड़ना |
| TTY | Pseudo terminal | Pseudo terminal |
| ECS Exec | Exec into ECS tasks via SSM | ECS tasks में SSM से exec |

---

## ⚡ 3-Line Summary
English: `docker exec` starts a new process in a running container, usually `sh` for debugging or admin tasks. Changes made this way are temporary and exiting does not stop the container. Treat exec access as root-level access and lock it down.
Hindi: `docker exec` चलते container में नया process शुरू करता है, आम तौर पर debugging या admin के लिए `sh`। इस तरह के बदलाव अस्थायी होते हैं और बाहर निकलने से container नहीं रुकता। Exec access को root-level access मानो और उसे सीमित रखो।

---

## ➡️ Next Topic
**144. Container Debugging**: exec is one tool; next you learn the complete debugging workflow for crashing and misbehaving containers.

---
