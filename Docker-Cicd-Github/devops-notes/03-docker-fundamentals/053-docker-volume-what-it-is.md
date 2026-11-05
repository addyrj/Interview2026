---

# 053. Docker Volume — What it is
# हिंदी में: Docker Volume — यह क्या है

---

## 🔵 Simple Definition (English)
A **Docker volume** is storage managed by Docker that lives outside a container's writable layer. Data in a volume survives when the container is stopped, removed or recreated. It is the standard way to keep database files, uploads and certificates.

## 🔵 सरल परिभाषा (Hindi)
**Docker volume** Docker द्वारा manage किया जाने वाला storage है जो container की writable layer के बाहर रहता है। Container stop, remove या दोबारा create होने पर भी volume का data बचा रहता है। Database files, uploads और certificates रखने का यही standard तरीका है।

---

## 🔴 Problem it Solves
A container's filesystem is temporary. When you run `docker rm`, everything written inside it is gone. If your Postgres container stores data in its own layer, one redeploy deletes the whole database. Also, the writable layer is slower (copy-on-write) and cannot be shared easily between containers. Volumes fix this: data is stored separately, has its own lifecycle, can be backed up, and can be mounted in many containers.

## 🔴 यह क्यों बना? (Hindi)
Container का filesystem temporary होता है। `docker rm` चलाते ही अंदर लिखा सब कुछ चला जाता है। अगर Postgres अपना data container की layer में रखे, तो एक redeploy पूरा database उड़ा देगा। Writable layer slow भी होती है (copy-on-write) और containers के बीच share करना मुश्किल है। Volume इसे solve करता है: data अलग जगह रहता है, उसका अपना lifecycle है, backup हो सकता है और कई containers में mount हो सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → docker volume create pgdata (or Docker creates it automatically on first use)
Step 2 → Docker makes a directory on the host: /var/lib/docker/volumes/pgdata/_data
Step 3 → docker run -v pgdata:/var/lib/postgresql/data mounts that directory into the container
Step 4 → Container writes to /var/lib/postgresql/data -> bytes land in the host directory
Step 5 → Container is removed -> volume stays (named volumes are NOT deleted by docker rm)
Step 6 → New container mounts the same volume -> old data is still there
```

Three kinds of mounts:
- **Named volume** `-v pgdata:/path` — managed by Docker, best for production data.
- **Bind mount** `-v /host/path:/path` — you choose the host folder, good for dev source code.
- **tmpfs** `--tmpfs /path` — RAM only, gone on stop, good for secrets/temp files.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → docker volume create pgdata (या पहली बार use होने पर Docker खुद बना देता है)
Step 2 → Docker host पर एक directory बनाता है: /var/lib/docker/volumes/pgdata/_data
Step 3 → docker run -v pgdata:/var/lib/postgresql/data उस directory को container में mount करता है
Step 4 → Container /var/lib/postgresql/data में लिखता है -> bytes host directory में जाते हैं
Step 5 → Container remove हुआ -> volume बचा रहता है (named volume को docker rm delete नहीं करता)
Step 6 → नया container वही volume mount करता है -> पुराना data मौजूद है
```

तीन तरह के mounts:
- **Named volume** `-v pgdata:/path` — Docker manage करता है, production data के लिए best।
- **Bind mount** `-v /host/path:/path` — host folder आप चुनते हैं, dev में source code के लिए अच्छा।
- **tmpfs** `--tmpfs /path` — सिर्फ RAM, stop पर गायब, secrets/temp files के लिए।

---

## 🟡 Real World Example
Your VPS runs a FastAPI app with Postgres. Last month you upgraded Postgres from 15 to 16 by pulling a new image and recreating the container. Because `pgdata` is a named volume, the data stayed. A teammate who ran Postgres without a volume lost two weeks of staging data on the same upgrade. Swiggy-style order services keep their DB volumes on fast SSD disks and snapshot them nightly.

## 🟡 Real Example Hindi mein
आपके VPS पर FastAPI app और Postgres चल रहा है। पिछले महीने आपने नया image pull करके container दोबारा बनाया और Postgres 15 से 16 किया। `pgdata` named volume था, इसलिए data बचा रहा। एक teammate ने volume के बिना Postgres चलाया था और उसी upgrade में staging का दो हफ्ते का data खो गया। Swiggy जैसे order services अपने DB volumes fast SSD पर रखते हैं और रोज़ रात snapshot लेते हैं।

---

## 💻 Code / Config Example — Basic

```bash
# --- Basic volume commands (Docker Engine 20.10+) ---
docker volume create pgdata                      # create a named volume called pgdata
docker volume ls                                 # list all volumes on this host
docker run -d --name db \
  -e POSTGRES_PASSWORD=example_pass \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16                                    # mount volume at Postgres data directory
docker rm -f db                                  # delete the container, volume stays safe
docker volume inspect pgdata                     # show mountpoint, driver, labels
docker run -d --name db2 \
  -e POSTGRES_PASSWORD=example_pass \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16                                    # new container, same old data
docker volume rm pgdata                          # fails while a container uses it (good safety)
docker volume prune                              # delete all volumes not used by any container (careful!)
```

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.yml - production-style stack with named volumes, read-only mount and backup volume
# Image tags are examples; update them to the versions you run.
services:                                        # all containers of the stack
  db:                                            # Postgres service
    image: postgres:16-alpine                    # small official image, pinned major version
    restart: unless-stopped                      # restart after VPS reboot unless stopped manually
    environment:                                 # env vars read by the postgres image
      POSTGRES_USER: appuser                     # database user
      POSTGRES_DB: appdb                         # database name
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password  # read password from a file, not plain env
    secrets:                                     # attach the secret defined below
      - db_password                              # appears as /run/secrets/db_password
    volumes:                                     # persistent storage for this service
      - pgdata:/var/lib/postgresql/data          # named volume holds the DB files
      - ./initdb:/docker-entrypoint-initdb.d:ro  # bind mount, read-only, runs SQL on first start
    healthcheck:                                 # tells Docker when DB is really ready
      test: ["CMD-SHELL", "pg_isready -U appuser -d appdb"]  # exit 0 means ready
      interval: 10s                              # check every 10 seconds
      timeout: 5s                                # fail the check after 5 seconds
      retries: 5                                 # unhealthy after 5 failures
  api:                                           # FastAPI service
    build: ./api                                 # build from ./api/Dockerfile
    depends_on:                                  # start order
      db:
        condition: service_healthy               # wait until the DB healthcheck passes
    volumes:
      - uploads:/app/uploads                     # user uploads survive redeploys
      - type: tmpfs                              # RAM-only mount
        target: /tmp                             # scratch space, wiped on stop
  backup:                                        # one-shot backup helper
    image: alpine:3.20                           # tiny image with tar
    profiles: ["tools"]                          # only runs when asked: --profile tools
    volumes:
      - pgdata:/data:ro                          # mount the DB volume read-only
      - ./backups:/backups                       # host folder to store archive
    command: ["tar", "czf", "/backups/pgdata.tar.gz", "-C", "/data", "."]  # compress volume
volumes:                                         # declare named volumes
  pgdata:                                        # Docker creates and owns this volume
  uploads:                                       # second volume for files
secrets:                                         # compose file-based secrets
  db_password:
    file: ./secrets/db_password.txt              # keep this file out of git (.gitignore)
```

---

## 🟠 My Stack Integration
- **Postgres/MongoDB/Redis**: always a named volume at the image's data directory.
- **FastAPI uploads**: named volume or, better, S3 (volumes live on one VPS only).
- **Nginx**: share `certs` volume with certbot so Let's Encrypt certificates survive redeploys.
- **Node.js / React**: no volume in production (stateless image); bind mounts only in dev for hot reload.
- **AWS**: on EC2/VPS the volume sits on EBS; take EBS snapshots. On ECS use EFS or EBS volumes instead of host paths.

```yaml
# docker-compose.prod.yml - nginx + certbot share certificates through a volume
services:
  nginx:
    image: nginx:1.27-alpine                     # example tag, update regularly
    ports:
      - "80:80"                                  # HTTP for ACME challenge and redirect
      - "443:443"                                # HTTPS
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro      # config from repo, read-only
      - letsencrypt:/etc/letsencrypt:ro          # certs, nginx only reads them
      - webroot:/var/www/certbot:ro              # ACME challenge files
  certbot:
    image: certbot/certbot                       # official certbot image
    volumes:
      - letsencrypt:/etc/letsencrypt             # certbot writes certs here
      - webroot:/var/www/certbot                 # certbot writes challenge files here
volumes:
  letsencrypt:                                   # persists certificates
  webroot:                                       # shared challenge directory
```

Security: use `:ro` whenever a container only needs to read; never mount `/var/run/docker.sock` or `/` casually; keep volume backups encrypted; DB volumes should be readable only by root on the host (Docker does this under `/var/lib/docker`).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running a database with no volume (anonymous volume or none), then recreating the container and losing data.
✅ Correct: Use a named volume at the correct data path (`/var/lib/postgresql/data`, `/data/db` for Mongo).

❌ Mistake 2: Running `docker volume prune` or `docker compose down -v` on production to "clean up".
✅ Correct: Use `docker compose down` without `-v`. Prune only after checking `docker volume ls` and having backups.

❌ Mistake 3: Bind mounting a host folder over an image directory that already has files (it hides them).
✅ Correct: Mount to an empty path, or use a named volume (which copies the image's initial content on first use).

❌ Mistake 4: Permission errors because container user (e.g. uid 1000) cannot write to the volume.
✅ Correct: Fix ownership with `chown` in the Dockerfile before `VOLUME`/`USER`, or use `user:` in compose with matching ownership.

---

## 🧠 Tricky Interview Question
You recreated your Postgres container with `docker compose up -d` and the old data is still there, but after changing `POSTGRES_PASSWORD` the old password still works. Why?

Answer: The `POSTGRES_*` variables are used only when the data directory is empty (first initialisation). Since the volume already holds an initialised cluster, the image skips init and ignores the new password. To change it, run `ALTER USER ... PASSWORD ...` inside the DB, or (only in dev) delete the volume so it re-initialises.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a volume and a bind mount?
A1: A volume is created and managed by Docker under `/var/lib/docker/volumes`; a bind mount maps an exact host path you choose. Volumes are portable, easier to back up and safer; bind mounts depend on host folder layout and are mostly for development.

Q2: Does `docker rm` delete named volumes?
A2: No. Named volumes stay. Anonymous volumes are removed only if you use `docker rm -v`. `docker compose down -v` removes the compose-declared volumes.

Q3: How do you back up a volume?
A3: Run a temporary container that mounts the volume read-only plus a host folder and tars it: `docker run --rm -v pgdata:/data:ro -v $(pwd):/backup alpine tar czf /backup/pg.tgz -C /data .`. For databases prefer logical dumps (`pg_dump`) because file copies of a running DB can be inconsistent.

Q4: Can multiple containers share one volume?
A4: Yes, but Docker gives no locking. Two databases writing the same files will corrupt them. Sharing is fine for read-mostly data (certs, static files).

Q5: Where is volume data stored and how do you find it?
A5: On Linux under `/var/lib/docker/volumes/<name>/_data`. Use `docker volume inspect <name>` to see the `Mountpoint`. On Docker Desktop it is inside the Linux VM, not directly on your Mac/Windows disk.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Data must outlive the container (databases, uploads, certificates, Prometheus/Grafana data).
- Several containers need the same files.
- You want Docker-managed, backup-friendly storage.

❌ Avoid when:
- The app is stateless (use no volume, keep it in the image or in S3).
- You need live source reload in dev (use bind mount).
- You need multi-host shared storage (use EFS/NFS/cloud storage, not a plain local volume).

---

## 📊 Visual Diagram
```
 Host (VPS)
 +--------------------------------------------------------------+
 |  /var/lib/docker/volumes/pgdata/_data   <-- real bytes live  |
 |            ^                    ^                            |
 |            | mount              | mount (later)              |
 |  +---------+--------+   +-------+----------+                 |
 |  | container db (v1)|   | container db (v2)|                 |
 |  | /var/lib/postgres|   | /var/lib/postgres|                 |
 |  | ql/data          |   | ql/data          |                 |
 |  +------------------+   +------------------+                 |
 |   docker rm  ----X        same data again                    |
 +--------------------------------------------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Named volume | Docker-managed storage with a name | नाम वाला Docker-managed storage |
| Anonymous volume | Volume with random ID, easy to lose | बिना नाम का volume, खोना आसान |
| Bind mount | Host folder mapped into container | Host folder को container में जोड़ना |
| tmpfs | In-memory mount | सिर्फ RAM वाला mount |
| Mountpoint | Host path of the volume | Volume का host path |
| Prune | Delete unused resources | बेकार resources हटाना |

---

## ⚡ 3-Line Summary
English: A volume is Docker-managed storage that lives outside the container layer.
Named volumes survive `docker rm`, so databases and uploads keep their data across redeploys.
Back them up, mount read-only when possible, and never prune production volumes blindly.
Hindi: Volume Docker-managed storage है जो container layer के बाहर रहता है।
Named volume `docker rm` के बाद भी बचता है, इसलिए database और uploads redeploy में safe रहते हैं।
Backup लें, जहाँ हो सके read-only mount करें, और production volumes को आँख बंद करके prune न करें।

---

## ➡️ Next Topic
**054. Docker Network — What it is.** Volumes solve storage; next we solve how your api, db and nginx containers find and talk to each other.

---
