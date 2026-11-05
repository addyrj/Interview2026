---

# 063. docker exec
# हिंदी में: docker exec

---

## 🔵 Simple Definition (English)
`docker exec` runs a new command **inside an already running container**. With `-it` it gives you an interactive shell (`docker exec -it api sh`). The extra process shares the container's filesystem, network and environment but is not PID 1.

## 🔵 सरल परिभाषा (Hindi)
`docker exec` किसी **पहले से चल रहे container के अंदर** नया command चलाता है। `-it` के साथ यह interactive shell देता है (`docker exec -it api sh`)। यह अतिरिक्त process container का filesystem, network और environment share करता है, पर PID 1 नहीं होता।

---

## 🔴 Problem it Solves
You often need to look inside: check a config file, run a DB migration, open a Python shell, test DNS to another container, or reload Nginx. Installing SSH inside containers is a bad practice. `docker exec` gives controlled access without opening extra ports.

## 🔴 यह क्यों बना? (Hindi)
अक्सर अंदर झाँकना पड़ता है: config file देखना, DB migration चलाना, Python shell खोलना, दूसरे container तक DNS test करना, या Nginx reload करना। Containers के अंदर SSH install करना बुरा तरीका है। `docker exec` बिना अतिरिक्त ports खोले नियंत्रित access देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → CLI asks the daemon: create an exec instance in container <name> with this command
Step 2 → Daemon joins a NEW process into the container's namespaces (pid, net, mnt, ipc) and cgroup
Step 3 → The process starts with the container's env vars (plus any -e you add) and workdir (or -w)
Step 4 → With -i stdin is attached, with -t a pseudo-terminal is allocated (needed for shells)
Step 5 → Process exits -> exec ends; the container keeps running (unless you killed PID 1)
Step 6 → Changes to files persist only in the container's writable layer; lost when container is recreated
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → CLI daemon से कहता है: container <name> में इस command के साथ exec instance बनाओ
Step 2 → Daemon एक नया process container के namespaces (pid, net, mnt, ipc) और cgroup में जोड़ता है
Step 3 → Process container के env vars (और आपके -e) और workdir (या -w) के साथ शुरू होता है
Step 4 → -i से stdin जुड़ता है, -t से pseudo-terminal मिलता है (shell के लिए ज़रूरी)
Step 5 → Process खत्म -> exec खत्म; container चलता रहता है (जब तक PID 1 न मारा हो)
Step 6 → Files के बदलाव सिर्फ container की writable layer में रहते हैं; container दोबारा बनने पर चले जाते हैं
```

---

## 🟡 Real World Example
Your FastAPI container returns 500 on login. You run `docker exec -it api sh`, `env | grep DATABASE`, and see the DB host is `localhost` instead of `db`. You also run `docker exec api python -c "import socket; print(socket.gethostbyname('db'))"` to confirm DNS. Another day you run `docker exec db psql -U appuser appdb -c "select count(*) from orders"` for a quick check, or `docker exec nginx nginx -s reload` after changing config.

## 🟡 Real Example Hindi mein
आपका FastAPI container login पर 500 दे रहा है। आप `docker exec -it api sh` चलाकर `env | grep DATABASE` देखते हैं और पाते हैं कि DB host `db` की जगह `localhost` है। DNS confirm करने के लिए `docker exec api python -c "import socket; print(socket.gethostbyname('db'))"` भी चलाते हैं। किसी और दिन `docker exec db psql -U appuser appdb -c "select count(*) from orders"` से quick check, या config बदलने के बाद `docker exec nginx nginx -s reload`।

---

## 💻 Code / Config Example — Basic

```bash
# --- docker exec basics ---
docker exec web ls /usr/share/nginx/html         # run one command, print output, return
docker exec -it web sh                           # interactive shell (alpine images have sh, often no bash)
docker exec -it api bash                         # bash if the image includes it (debian/ubuntu based)
docker exec -e DEBUG=1 api env                   # add an env var for this command only
docker exec -w /app api ls                       # set working directory
docker exec -u root api whoami                   # run as another user (default is the container's USER)
docker exec -u 0 -it api sh                      # root shell for debugging a non-root container
docker exec api cat /etc/hosts                   # inspect network files
docker exec api sh -c 'echo $HOSTNAME'           # use sh -c so the variable expands inside the container
docker exec nginx nginx -t                       # validate nginx config
docker exec nginx nginx -s reload                # reload nginx without downtime
```

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# exec-tools.sh - common operational tasks via docker exec (container names are examples)
set -euo pipefail                                # strict shell mode

# 1) Postgres dump without installing anything on the host (no -t so output is clean binary/text)
docker exec db pg_dump -U appuser appdb | gzip > "backup-$(date +%F).sql.gz"   # compressed backup on the host

# 2) Restore into Postgres from a gzip file (-i passes stdin)
gunzip -c backup-2026-01-15.sql.gz | docker exec -i db psql -U appuser -d appdb   # example file name

# 3) Run DB migrations inside the API container (FastAPI + Alembic)
docker exec api alembic upgrade head             # applies pending migrations

# 4) Network debugging from inside the API container (alpine images: apk add curl in a debug image)
docker exec api python -c "import urllib.request; print(urllib.request.urlopen('http://nginx/health').status)"

# 5) Check which user and memory the process has
docker exec api sh -c 'id && cat /proc/1/status | grep VmRSS'   # uid/gid and resident memory of PID 1

# 6) Redis check
docker exec cache redis-cli ping                 # prints PONG when healthy

# 7) Debug a minimal (distroless/scratch) container with a sidecar sharing its namespaces
docker run --rm -it --pid=container:api --network=container:api nicolaka/netshoot   # example public debug image; shares net+pid of "api"
```

```yaml
# docker-compose.yml - use exec from compose; also add a one-off "run" job for migrations
services:
  api:
    build: ./api                                 # FastAPI app image
    restart: unless-stopped                      # keep running
    depends_on:
      db:
        condition: service_healthy               # wait for DB
  db:
    image: postgres:16-alpine                    # example tag
    environment:
      POSTGRES_USER: appuser                     # DB user
      POSTGRES_DB: appdb                         # DB name
      POSTGRES_PASSWORD: ${DB_PASSWORD}          # from .env
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d appdb"]   # DB ready probe
      interval: 10s                              # every 10s
      timeout: 5s                                # time limit per probe
      retries: 5                                 # failures before unhealthy
# Usage:
#   docker compose exec api sh                   # shell in the running api service (no container name needed)
#   docker compose exec -T db pg_dump -U appuser appdb > dump.sql   # -T disables TTY, needed in scripts/CI
#   docker compose run --rm api alembic upgrade head                # NEW one-off container (not exec)
```

---

## 🟠 My Stack Integration
- **FastAPI/Node.js**: `docker compose exec api sh` for env/config checks; run migrations with exec or `run --rm`.
- **Nginx**: `exec nginx nginx -t && exec nginx nginx -s reload` after config edits (config is mounted from the VPS).
- **Postgres/Mongo/Redis**: `exec db psql`, `exec mongo mongosh`, `exec cache redis-cli`.
- **GitHub Actions SSH deploy**: use `docker compose exec -T` (no TTY in CI).
- **AWS**: ECS has the equivalent `aws ecs execute-command --interactive --command "/bin/sh"` (ECS Exec, requires SSM permissions and enabling it on the service).

```yaml
# .github/workflows/migrate.yml - run migrations on the VPS after deploy (note -T: no TTY in CI)
name: migrate                                    # workflow name
on:
  workflow_dispatch:                             # manual trigger
jobs:
  migrate:
    runs-on: ubuntu-latest                       # runner
    steps:
      - name: Run Alembic on VPS                 # SSH and exec
        uses: appleboy/ssh-action@v1.0.3         # example version
        with:
          host: ${{ secrets.VPS_HOST }}          # server address
          username: deploy                       # docker-capable user
          key: ${{ secrets.VPS_SSH_KEY }}        # SSH key secret
          script: |                              # runs on the VPS
            cd /srv/app
            docker compose exec -T api alembic upgrade head
```

Security: exec is a root-equivalent back door when someone has docker access (especially `-u root`). Do not install SSH daemons in containers. Audit who is in the docker group. Avoid leaving debug tools (curl, vim) in production images; use a separate debug container (netshoot) instead. Do not pass secrets as `exec -e` arguments on shared hosts since they appear in process lists and shell history.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `docker exec -it api bash` on an Alpine image: "executable file not found".
✅ Correct: Use `sh` on Alpine; install bash only if really needed.

❌ Mistake 2: Editing config files inside the container with exec and expecting the change to persist.
✅ Correct: Change the image or mounted config in git, then redeploy; changes in the writable layer vanish on recreate.

❌ Mistake 3: `docker exec -it` in cron/CI causing "the input device is not a TTY".
✅ Correct: Drop `-t` (use `-i` or nothing); for Compose use `-T`.

❌ Mistake 4: `docker exec api echo $HOME` prints the HOST's variable (your local shell expanded it).
✅ Correct: `docker exec api sh -c 'echo $HOME'` with single quotes.

❌ Mistake 5: Trying to exec into a stopped container.
✅ Correct: exec works only on running containers; use `docker logs` or `docker run` the image with `--entrypoint sh` to investigate.

---

## 🧠 Tricky Interview Question
You `docker exec -it api sh` and run `kill 1` to "restart the app", but nothing happens. Why, and what happens if you instead run `docker exec api kill -9 1`?

Answer: PID 1 inside a container is special: the kernel ignores signals for which PID 1 has no installed handler, so a plain `kill 1` (SIGTERM) does nothing if the app has no SIGTERM handler. SIGKILL from inside the PID namespace is also ignored for PID 1 (only signals from the parent namespace can kill it, which is why `docker kill` works). The correct way to restart is `docker restart api` (or `docker compose restart api`) from the host.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `docker exec` and `docker run`?
A1: `run` creates a **new** container from an image; `exec` runs a command inside an **existing running** container.

Q2: Difference between `docker exec` and `docker attach`?
A2: `attach` connects to the container's main process (PID 1) stdin/stdout, and Ctrl+C may stop the container; `exec` starts a separate process, so leaving it does not affect the container.

Q3: What do `-i` and `-t` do?
A3: `-i` keeps stdin open; `-t` allocates a pseudo-TTY. Interactive shells need both (`-it`); scripts piping data need `-i` only.

Q4: How do you debug a container that has no shell (distroless)?
A4: Use `docker debug` (Docker Desktop/subscription feature), or run a debug sidecar that shares namespaces (`--pid=container:x --network=container:x`), or `kubectl debug` with an ephemeral container in Kubernetes.

Q5: Does `docker exec` see environment variables set at `docker run`?
A5: Yes. The exec process inherits the container's configured environment (not variables exported later in another shell).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Debugging, one-off admin tasks (migrations, DB dumps, cache flush), reloading Nginx.

❌ Avoid when:
- Making permanent changes (use Dockerfile/config in git).
- Routine production operations that should be automated or run as one-off jobs.

---

## 📊 Visual Diagram
```
 +---------------------- container "api" ----------------------+
 |  PID 1: uvicorn main:app          (the real app, keeps running)
 |  PID 27: sh   <---- docker exec -it api sh   (new process)  |
 |  shares: filesystem, network (172.18.0.3), env, cgroup limit |
 +--------------------------------------------------------------+
        ^
        | exec API call from CLI over /var/run/docker.sock
   you (SSH on VPS)
 exit sh -> PID 27 gone, PID 1 unaffected
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| exec | Run command in running container | चलते container में command चलाना |
| TTY | Pseudo terminal for interactive use | Interactive उपयोग के लिए terminal |
| Namespace | Isolation of PIDs/network/mounts | PID/network/mount की isolation |
| PID 1 | First process, special signal rules | पहला process, signals के खास नियम |
| Sidecar debug | Helper container sharing namespaces | Namespaces share करने वाला helper container |
| ECS Exec | exec on AWS ECS via SSM | AWS ECS पर SSM से exec |

---

## ⚡ 3-Line Summary
English: `docker exec` runs a new command in a running container; `-it` gives a shell.
Use it for debugging and admin tasks, not for permanent changes.
It is powerful and root-equivalent, so restrict access.
Hindi: `docker exec` चलते container में नया command चलाता है; `-it` shell देता है।
इसे debugging और admin tasks के लिए इस्तेमाल करें, स्थायी बदलावों के लिए नहीं।
यह शक्तिशाली और root के बराबर है, इसलिए access सीमित रखें।

---

## ➡️ Next Topic
**064. docker inspect.** See the complete low-level JSON of containers, images, networks and volumes.

---
