# 198. Docker Compose Commands (up, down, ps, logs, exec, build)
# हिंदी में: Docker Compose Commands (up, down, ps, logs, exec, build)

---

## 🔵 Simple Definition (English)
Docker Compose commands are the CLI verbs (`docker compose <verb>`) that manage the whole multi-container stack described in `docker-compose.yml`: build images, start/stop containers, inspect status, read logs and run commands inside containers, all with a single command instead of many `docker run` calls.

## 🔵 सरल परिभाषा (Hindi)
Docker Compose commands वे CLI verbs (`docker compose <verb>`) हैं जो `docker-compose.yml` में लिखे पूरे multi-container stack को manage करते हैं: image build करना, containers start/stop करना, status देखना, logs पढ़ना और containers के अंदर command चलाना, सब कुछ कई `docker run` की जगह एक command से।

---

## 🔴 Problem it Solves
Without Compose you type long `docker run` commands for each container with networks, volumes, env vars, and you must remember the order. One typo = broken stack. Compose commands act on the *project* (all services) so `up`, `down`, `logs` are one-liners and repeatable by every teammate and by CI.

## 🔴 यह क्यों बना? (Hindi)
Compose के बिना हर container के लिए networks, volumes, env vars के साथ लंबे `docker run` command लिखने पड़ते हैं और order याद रखना पड़ता है। एक typo = stack टूट गया। Compose commands पूरे *project* (सभी services) पर काम करते हैं इसलिए `up`, `down`, `logs` one-liner हैं और हर teammate और CI के लिए repeatable।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Compose finds the file (docker-compose.yml / compose.yaml) in the current folder
Step 2 → Project name = folder name (override with -p or `name:`) ; it prefixes all resources
Step 3 → `build`   : builds images for services that have `build:`
Step 4 → `up`      : creates networks/volumes, builds if missing, starts containers in dependency order
Step 5 → `ps/logs` : read current state and output of the project's containers
Step 6 → `exec`    : runs a command inside an ALREADY running container
Step 7 → `down`    : stops and removes containers + networks (volumes only with -v)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Compose current folder में file (docker-compose.yml / compose.yaml) ढूँढता है
Step 2 → Project name = folder का नाम (-p या `name:` से बदलें); सभी resources के आगे यही लगता है
Step 3 → `build`   : जिन services में `build:` है उनकी images बनाता है
Step 4 → `up`      : networks/volumes बनाता है, ज़रूरत हो तो build करता है, dependency order में containers start करता है
Step 5 → `ps/logs` : project के containers की मौजूदा स्थिति और output दिखाता है
Step 6 → `exec`    : पहले से चल रहे container के अंदर command चलाता है
Step 7 → `down`    : containers + networks रोककर हटाता है (volumes सिर्फ -v से)
```

---

## 🟡 Real World Example
On your **VPS** you deploy a new Node.js API version: `git pull`, `docker compose build api`, `docker compose up -d api` (recreates only api), `docker compose logs -f --tail=100 api` to watch it boot, and `docker compose exec api node -v` to verify. If it fails, `docker compose ps` shows `Restarting` and you read logs. This is the same daily loop **Swiggy**-style platform teams run in staging.

## 🟡 Real Example Hindi mein
अपने **VPS** पर Node.js API का नया version deploy करने के लिए: `git pull`, `docker compose build api`, `docker compose up -d api` (सिर्फ api दोबारा बनता है), `docker compose logs -f --tail=100 api` से boot देखना, और `docker compose exec api node -v` से verify। फेल हो तो `docker compose ps` में `Restarting` दिखता है और logs पढ़ते हैं। यही रोज़ का loop **Swiggy** जैसी platform teams staging में चलाती हैं।

---

## 💻 Code / Config Example — Basic

```yaml
# docker-compose.yml used for the commands below
services:
  api:
    build: .                      # build image from ./Dockerfile
    ports:
      - "3000:3000"               # host:container
    environment:
      NODE_ENV: production        # runtime mode
  redis:
    image: redis:7-alpine         # example tag
```

```bash
# --- build ---
docker compose build                 # build all services that have build:
docker compose build --no-cache api  # rebuild api ignoring layer cache
# --- up ---
docker compose up                    # foreground, shows logs, Ctrl+C stops
docker compose up -d                 # detached (background)
docker compose up -d --build         # rebuild images then start
docker compose up -d --force-recreate   # recreate containers even if config unchanged
docker compose up -d --scale api=3   # run 3 replicas (do not publish a fixed host port!)
# --- ps ---
docker compose ps                    # running containers of this project
docker compose ps -a                 # include stopped
# --- logs ---
docker compose logs -f api           # follow logs of one service
docker compose logs --tail=50 -t     # last 50 lines with timestamps
# --- exec / run ---
docker compose exec api sh           # shell in running api container
docker compose exec -T api node -v   # -T = no TTY (needed in CI/cron)
docker compose run --rm api npm test # NEW one-off container, removed after
# --- down ---
docker compose stop                  # stop but keep containers
docker compose down                  # stop + remove containers and networks
docker compose down -v               # ALSO delete named volumes (data loss!)
```

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# deploy.sh : safe redeploy script for a VPS (copy-paste ready)
set -euo pipefail                          # stop on error, unset var, pipe failure
cd /opt/myapp                              # project directory on the VPS
export COMPOSE_PROJECT_NAME=myapp          # fixed project name (not folder-dependent)

git pull --ff-only                         # fetch new code, refuse merges
docker compose config -q                   # validate the compose file (exit non-zero if invalid)
docker compose build --pull api            # rebuild, pulling fresh base image
docker compose up -d --no-deps api         # recreate ONLY api, leave db/redis alone
# wait until the container reports healthy (needs healthcheck in the file)
for i in $(seq 1 30); do
  status=$(docker compose ps --format json api | grep -o '"Health":"[a-z]*"' || true)  # read health field
  echo "$status" | grep -q healthy && break  # healthy -> stop waiting
  sleep 2                                    # check every 2s, max 60s
done
docker compose logs --tail=50 api          # show boot logs for the record
docker image prune -f                      # clean dangling images to save disk
docker compose ps                          # final status table
```

```bash
# Useful extras
docker compose config                      # print the final merged config (great for debugging)
docker compose config --services           # list service names
docker compose top                         # processes in each container
docker compose events                      # live stream of container events
docker compose pull                        # pull newer images for services with image:
docker compose restart api                 # restart without recreating
docker compose cp api:/app/log.txt ./log.txt   # copy file out of a container
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d   # multiple files (see 201)
```
The `--format json` output of `ps` differs slightly between Compose releases (one JSON per line vs array); this script's grep is an example, adjust for your version. The script was syntax-checked only, not run against a live daemon.

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: `docker compose run --rm api npm test` or `pytest` runs tests in the exact image you ship.
- **Nginx**: after changing the conf, `docker compose exec nginx nginx -t && docker compose exec nginx nginx -s reload` reloads without downtime.
- **Postgres**: `docker compose exec db psql -U app -d app` for a SQL shell; `exec -T db pg_dump ... > backup.sql` for backups.
- **GitHub Actions on EC2/VPS**: the SSH step simply runs the `deploy.sh` above.

```bash
# nightly Postgres backup from cron on the VPS
docker compose -f /opt/myapp/docker-compose.yml exec -T db \
  pg_dump -U app app | gzip > /backups/app_$(date +%F).sql.gz   # -T because cron has no TTY
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `docker compose down -v` on production "to clean up".
✅ Correct: Use `down` without `-v`. `-v` deletes named volumes, which means your database.

❌ Mistake 2: `up -d` after code change but no rebuild, then wondering why nothing changed.
✅ Correct: `up -d --build` or `build` first (the image is not rebuilt automatically if it already exists).

❌ Mistake 3: `exec` in cron/CI fails with "the input device is not a TTY".
✅ Correct: Add `-T`.

❌ Mistake 4: `exec` on a service that is not running.
✅ Correct: Use `run --rm` for a new container, or check `ps` first.

❌ Mistake 5: Running a command from the wrong folder (a different project name is used, so Compose "sees" nothing).
✅ Correct: `-f` path and `-p name`, or `COMPOSE_PROJECT_NAME`.

---

## 🧠 Tricky Interview Question
What is the difference between `docker compose run api cmd` and `docker compose exec api cmd`?

Answer: `exec` runs inside the already-running container (same filesystem, same process namespace, fails if stopped). `run` creates a brand-new container from the service definition (also starts dependencies, ports are NOT published by default, use `--service-ports`), runs the command, and it stays in `ps -a` unless you pass `--rm`. Use `exec` for debugging live state, `run --rm` for one-off jobs like migrations and tests.

---

## ⚫ Interview Questions + Answers

Q1: What does `up -d` do if the container exists and config is unchanged?
A1: Nothing, it leaves it running. If config or image changed, only that service is recreated.

Q2: `stop` vs `down`?
A2: `stop` halts containers but keeps them (and networks). `down` removes containers and networks; named volumes stay unless `-v`.

Q3: How to see the final config after merging files and env interpolation?
A3: `docker compose config`.

Q4: How do you scale a service?
A4: `up -d --scale web=3`, or `deploy.replicas`; avoid fixed host port mappings or use a load balancer.

Q5: How to follow logs of just two services?
A5: `docker compose logs -f api nginx`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Single host (dev laptop, CI runner, one VPS) multi-container apps.
- Repeatable local and test environments.

❌ Avoid when:
- You need multi-node orchestration, rolling updates, auto-healing: use Kubernetes / ECS / Swarm.

---

## 📊 Visual Diagram
```
 docker-compose.yml
        |
        v
 +-----------------+   build   +---------+
 | docker compose  |---------->| images  |
 |   up -d         |   create  +---------+
 |                 |---------->| network |
 |                 |---------->| volumes |
 |                 |   start   +---------+
 |                 |---------->| containers |
 +-----------------+
   ps / logs / exec  --> inspect & enter containers
   down              --> remove containers + network (-v: volumes too)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| project | Group of resources with one name | एक नाम वाले resources का समूह |
| detached (-d) | Run in background | background में चलाना |
| exec | Run command in running container | चल रहे container में command |
| run --rm | One-off new container, auto-removed | एक बार का नया container, अपने आप हटता है |
| recreate | Replace container with new config | नए config से container बदलना |

---

## ⚡ 3-Line Summary
English: Compose commands manage the whole stack: build, up, ps, logs, exec, down.
`up -d --build` deploys, `exec`/`run` debug, `down` cleans (never `-v` on prod).
Use `config` to validate and `-T` in non-interactive scripts.
Hindi: Compose commands पूरे stack को manage करते हैं: build, up, ps, logs, exec, down।
`up -d --build` deploy करता है, `exec`/`run` debug, `down` सफाई (prod पर `-v` कभी नहीं)।
Validate के लिए `config` और scripts में `-T` इस्तेमाल करें।

---

## ➡️ Next Topic
**199. docker compose vs docker-compose**: the old hyphenated binary versus the new plugin, and why scripts break when you mix them.
