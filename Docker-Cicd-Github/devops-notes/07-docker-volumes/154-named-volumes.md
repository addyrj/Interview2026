---

# 154. Named Volumes
# हिंदी में: Named Volumes (नाम वाले Volumes)

---

## 🔵 Simple Definition (English)
A **named volume** is a Docker-managed volume that you create with a human-friendly name (`pgdata`, `uploads`) and reuse by that name across containers and restarts. Unlike an anonymous volume (random ID), a named volume is easy to find, back up, share and keep. It is the standard way to store production data in Docker.

## 🔵 सरल परिभाषा (Hindi)
**Named volume** Docker-managed volume है जिसे आप इंसानी नाम (`pgdata`, `uploads`) से बनाते हैं और उसी नाम से containers और restarts में दोबारा इस्तेमाल करते हैं। Anonymous volume (random ID) के उलट, named volume को ढूँढना, backup लेना, share करना और संभालकर रखना आसान है। Docker में production data रखने का यही standard तरीका है।

---

## 🔴 Problem it Solves
With anonymous volumes (random 64-character IDs), after a few redeploys you cannot tell which volume holds the real database and which is junk. Cleanup commands may delete the wrong one, backups cannot target a name, and a new container silently starts with an empty volume instead of reusing old data. Names make storage identifiable, reusable and auditable.

## 🔴 यह क्यों बना? (Hindi)
Anonymous volumes (64 अक्षरों की random ID) में कुछ redeploys के बाद पता नहीं चलता कि असली database किस volume में है और कौन सा कचरा है। Cleanup commands गलत volume मिटा सकते हैं, backups किसी नाम को target नहीं कर सकते, और नया container चुपचाप खाली volume से शुरू हो जाता है, पुराना data reuse नहीं करता। नाम storage को पहचानने योग्य, reusable और audit-योग्य बनाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Name it: docker volume create pgdata   (or let -v pgdata:/path create it)
Step 2 → Docker stores it at /var/lib/docker/volumes/pgdata/_data with driver "local"
Step 3 → Any container can mount it by name: -v pgdata:/var/lib/postgresql/data
Step 4 → Container removed or image upgraded -> volume and data remain
Step 5 → Compose prefixes the name with the project: myapp_pgdata (unless name: is set)
Step 6 → Manage with: docker volume ls | inspect | rm | prune
Step 7 → Data is deleted only by explicit removal (docker volume rm, compose down -v, prune)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → नाम दो: docker volume create pgdata   (या -v pgdata:/path खुद बना देता है)
Step 2 → Docker इसे /var/lib/docker/volumes/pgdata/_data पर driver "local" से रखता है
Step 3 → कोई भी container नाम से mount कर सकता है: -v pgdata:/var/lib/postgresql/data
Step 4 → Container हटे या image upgrade हो -> volume और data बचे रहते हैं
Step 5 → Compose नाम में project prefix लगाता है: myapp_pgdata (जब तक name: न दें)
Step 6 → Manage करो: docker volume ls | inspect | rm | prune
Step 7 → Data सिर्फ़ साफ़ removal से मिटता है (docker volume rm, compose down -v, prune)
```

---

## 🟡 Real World Example
A Hyderabad logistics company runs Postgres and Redis on a single VPS with Compose. Their compose project folder is renamed from `tracker` to `tracker-v2` during a refactor. On the next `docker compose up`, Compose creates `tracker-v2_pgdata` (new project prefix) and starts an empty database, and the old `tracker_pgdata` sits untouched. Nobody lost data, but the app looked empty for 20 minutes. The fix: they set explicit `name: tracker_pgdata` for the volume (or `external: true`) so the name no longer depends on the folder name.

## 🟡 Real Example Hindi mein
Hyderabad की एक logistics company एक VPS पर Compose से Postgres और Redis चलाती है। Refactor में compose project folder का नाम `tracker` से `tracker-v2` कर दिया गया। अगले `docker compose up` पर Compose ने `tracker-v2_pgdata` (नया project prefix) बनाया और खाली database शुरू किया, जबकि पुराना `tracker_pgdata` जस का तस पड़ा रहा। Data नहीं गया, पर app 20 मिनट खाली दिखी। समाधान: उन्होंने volume में साफ़ `name: tracker_pgdata` (या `external: true`) रखा ताकि नाम folder के नाम पर निर्भर न रहे।

---

## 💻 Code / Config Example — Basic

```bash
# Create a named volume with a label
docker volume create --label app=tracker --label env=prod pgdata
# --label adds metadata you can filter on later

# List volumes, filtered by label
docker volume ls --filter label=app=tracker
# prints DRIVER and VOLUME NAME for matching volumes

# Mount it in a container (short syntax)
docker run -d --name db -e POSTGRES_PASSWORD=change-me \
  -v pgdata:/var/lib/postgresql/data postgres:16-alpine
# name:path => named volume mount; Docker creates it if it did not exist

# Same mount using --mount (explicit)
docker run -d --name db2 -e POSTGRES_PASSWORD=change-me \
  --mount type=volume,source=pgdata2,target=/var/lib/postgresql/data postgres:16-alpine
# type=volume with a source name = named volume; omit source for an anonymous one

# Mount read-only in a second container (e.g. a reporting job)
docker run --rm -v pgdata:/data:ro alpine:3.20 ls /data
# :ro prevents writes from this container

# Find all containers using a volume
docker ps -a --filter volume=pgdata --format '{{.Names}}'
# shows who depends on the volume before you delete it

# Delete (only when no container uses it)
docker rm -f db db2 && docker volume rm pgdata pgdata2
# volume rm fails with "volume is in use" if a container still references it
```

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.yml: explicit volume names, external volume, driver options
name: tracker                                   # fixes the project name (Compose v2.x+)

services:
  db:
    image: postgres:16-alpine                   # database image (example tag)
    restart: unless-stopped                     # come back after reboot
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_pass   # password from a secret file
    secrets:
      - db_pass                                 # attach the secret
    volumes:
      - pgdata:/var/lib/postgresql/data         # use the volume defined below

  redis:
    image: redis:7.4-alpine                     # cache with append-only persistence
    command: ["redis-server", "--appendonly", "yes"]   # write every change to the AOF file
    volumes:
      - redisdata:/data                         # redis writes dump/AOF in /data

  api:
    image: ghcr.io/acme/node-api:1.8.3          # Node.js API (example tag)
    volumes:
      - uploads:/app/uploads                    # shared uploads volume (external)

volumes:
  pgdata:
    name: tracker_pgdata                        # exact Docker name, ignores project prefix
    labels:
      backup: "daily"                           # label read by the backup script
  redisdata:
    name: tracker_redisdata                     # stable name for redis data
  uploads:
    external: true                              # created outside compose, never deleted by down -v
    name: shared_uploads                        # the existing volume name on this host

secrets:
  db_pass:
    file: ./secrets/db_pass.txt                 # keep out of git
```

```bash
# Create the external volume once, before the first `docker compose up`
docker volume create shared_uploads
# compose will error "external volume not found" if this was skipped

# Nightly backup of every volume labelled backup=daily (cron on the VPS)
set -euo pipefail                                       # stop on errors
mkdir -p /backups                                       # target folder on the host
for v in $(docker volume ls -q --filter label=backup=daily); do   # volumes with the label
  docker run --rm -v "$v":/source:ro -v /backups:/backup alpine:3.20 \
    tar czf "/backup/${v}-$(date +%F).tar.gz" -C /source .       # compressed archive per volume
done
# file-level copy is crash-consistent at best; for Postgres also run pg_dump
```

YAML parsed and shell checked with `bash -n`; not executed on a Docker daemon. The top-level `name:` property needs a recent Compose v2 (version-dependent).

---

## 🟠 My Stack Integration
Postgres/MongoDB: `pgdata`/`mongodata` named volumes with explicit `name:`. Redis: `redisdata` with AOF on. Node.js and FastAPI: `uploads` volume for user files (or S3 in a scaled setup). Nginx: `certs` volume shared with Certbot. For AWS, named volumes on one EC2 mean a single point of failure: use RDS for the database, S3 for uploads, and keep Compose volumes for local and small-VPS setups. Snapshots of the EBS disk that holds `/var/lib/docker` give cheap whole-host backups.

```bash
# Quick sizing check before a backup or migration on the VPS
docker system df -v | sed -n '/Local Volumes space usage/,$p'
# prints each volume with SIZE and number of LINKS (containers using it)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Relying on the folder name for volume identity and losing "your" database after renaming the project directory.
✅ Correct: Set `name:` on the volume or the top-level `name:` of the compose project.

❌ Mistake 2: Running `docker compose down -v` or `docker volume prune -a` on production.
✅ Correct: Plain `docker compose down`; use `external: true` for critical volumes so `down -v` cannot remove them.

❌ Mistake 3: Mounting one volume read-write into two databases.
✅ Correct: One database process per data directory; share files only for non-concurrent data like uploads or certificates.

❌ Mistake 4: Upgrading Postgres major version (15 to 16) with the same volume.
✅ Correct: Data formats are incompatible. Dump and restore, or use `pg_upgrade`, into a new volume.

---

## 🧠 Tricky Interview Question
You change the image from `postgres:15` to `postgres:16` and run `docker compose up -d`. The container exits immediately with "database files are incompatible with server". The volume is named and intact. What is the correct upgrade path?

Answer: A named volume keeps the old data files, and the new major version refuses to start on them because the on-disk format changed. Take a logical backup (`pg_dumpall` from the old container), start Postgres 16 with a NEW volume, restore the dump, test, then retire the old volume after a safe period. Alternatively use `pg_upgrade` with both binaries. Persistence does not mean compatibility, and you should always back up before changing the image of a stateful service.

---

## ⚫ Interview Questions + Answers

Q1: Named vs anonymous volume?
A1: Named has a chosen name and is meant to be reused; anonymous has a random hex ID, is created when you mount a path without a name (`-v /data`) and is easy to lose track of.

Q2: What does `docker compose down` do to named volumes?
A2: Nothing; they are kept. `down -v` removes the named volumes declared in the compose file (not `external` ones).

Q3: How do you reference a volume that already exists?
A3: Declare it under `volumes:` with `external: true` (and `name:` if the Docker name differs).

Q4: How can two containers share a named volume safely?
A4: Mount it in both. Make one writer and others read-only (`:ro`) where possible, and avoid concurrent writes to the same files.

Q5: How to copy data out of a named volume?
A5: Run a throwaway container mounting the volume plus a host folder and `tar`/`cp`, or `docker cp` from a container that mounts it.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production state: databases, uploads, certificates
- You want backups, labels and clear ownership
- The same data must survive redeploys

❌ Avoid when:
- Scratch data (use tmpfs)
- Editing files live from the host (use bind mounts in dev)
- You need multi-host sharing without a network driver

---

## 📊 Visual Diagram
```
   compose project "tracker"
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │ db          │   │ redis       │   │ api         │
   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
          │ pgdata          │ redisdata       │ uploads (external)
          ▼                 ▼                 ▼
   tracker_pgdata    tracker_redisdata    shared_uploads
   ─────────────────────────────────────────────────────
   /var/lib/docker/volumes/<name>/_data   (host disk)
   containers come and go ──► names and data stay
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Named volume | Volume with a chosen name | चुने हुए नाम वाला volume |
| external | Volume created outside compose | Compose के बाहर बना volume |
| Project prefix | Compose adds project name to volume name | Project नाम का prefix |
| Label | Key/value metadata | Key/value metadata |
| AOF | Redis append-only persistence file | Redis की append-only file |
| pg_upgrade | Tool to upgrade Postgres major versions | Postgres major upgrade tool |

---

## ⚡ 3-Line Summary
English: Named volumes give persistent data a stable identity you can mount, back up and share. In Compose, set an explicit `name:` or `external: true` so project renames and `down -v` cannot hurt you. Never reuse a volume across incompatible database versions.
Hindi: Named volumes persistent data को ऐसी स्थिर पहचान देते हैं जिसे आप mount, backup और share कर सकें। Compose में साफ़ `name:` या `external: true` रखो ताकि project rename और `down -v` नुक़सान न करें। Incompatible database versions के बीच कभी volume reuse मत करो।

---

## ➡️ Next Topic
**155. Anonymous Volumes**: the nameless counterpart, how they get created accidentally and how to avoid or use them on purpose.

---
