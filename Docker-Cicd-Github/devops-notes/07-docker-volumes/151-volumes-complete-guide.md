---

# 151. Volumes — Complete Guide
# हिंदी में: Volumes — पूरी गाइड

---

## 🔵 Simple Definition (English)
A **Docker volume** is storage managed by Docker that lives outside the container's writable layer, so data survives when the container is stopped, removed or replaced. Docker offers three mount types: **volumes** (managed by Docker, under `/var/lib/docker/volumes`), **bind mounts** (a host path) and **tmpfs** (RAM only).

## 🔵 सरल परिभाषा (Hindi)
**Docker volume** Docker द्वारा managed storage है जो container की writable layer के बाहर रहता है, इसलिए container रुकने, हटने या बदलने पर भी data बचा रहता है। Docker तीन mount types देता है: **volumes** (Docker managed, `/var/lib/docker/volumes` में), **bind mounts** (host का path) और **tmpfs** (सिर्फ़ RAM)।

---

## 🔴 Problem it Solves
A container's filesystem is a thin writable layer on top of read-only image layers. When the container is removed, that layer is deleted. A Postgres container without a volume loses every row on `docker rm`, or on a simple image upgrade. The writable layer is also slower (copy-on-write) and cannot be shared between containers. Volumes solve persistence, performance and sharing.

## 🔴 यह क्यों बना? (Hindi)
Container का filesystem read-only image layers के ऊपर एक पतली writable layer होती है। Container हटते ही वह layer मिट जाती है। Volume के बिना Postgres container `docker rm` पर, या image upgrade पर ही, हर row खो देता है। Writable layer धीमी भी है (copy-on-write) और containers के बीच share नहीं हो सकती। Volumes persistence, performance और sharing की समस्या हल करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create: docker volume create pgdata  (or implicitly by -v pgdata:/path)
Step 2 → Docker makes a directory /var/lib/docker/volumes/pgdata/_data on the host
Step 3 → Start: docker run -v pgdata:/var/lib/postgresql/data postgres
Step 4 → Docker mounts that directory into the container at the given path
Step 5 → First use of an EMPTY volume: Docker copies the image's existing files at that
         path into it (seeding); a non-empty volume hides the image's files
Step 6 → Container writes go straight to the volume, bypassing copy-on-write
Step 7 → docker rm container: volume stays. docker volume rm pgdata: data deleted
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → बनाओ: docker volume create pgdata  (या -v pgdata:/path से अपने आप)
Step 2 → Docker host पर /var/lib/docker/volumes/pgdata/_data directory बनाता है
Step 3 → शुरू करो: docker run -v pgdata:/var/lib/postgresql/data postgres
Step 4 → Docker वह directory दिए गए path पर container में mount करता है
Step 5 → EMPTY volume के पहले use पर: Docker उस path की image वाली files उसमें copy करता है
         (seeding); non-empty volume image की files को ढक देता है
Step 6 → Container की writes सीधे volume में जाती हैं, copy-on-write के बिना
Step 7 → container rm: volume बचा रहता है। docker volume rm pgdata: data मिट जाता है
```

---

## 🟡 Real World Example
An edtech company ran MongoDB in a container without a volume "just for staging". A routine `docker compose down && up` after an image bump wiped 3 weeks of QA test data. In production they use named volumes for `/data/db`, nightly `tar` backups of the volume to S3, and a rule: no stateful container without an explicit volume line reviewed in the pull request.

## 🟡 Real Example Hindi mein
एक edtech company "सिर्फ़ staging के लिए" MongoDB को बिना volume के container में चलाती थी। Image bump के बाद सामान्य `docker compose down && up` ने 3 हफ़्ते का QA test data मिटा दिया। Production में अब `/data/db` के लिए named volumes हैं, volume का रोज़ रात `tar` backup S3 में जाता है, और नियम है: कोई stateful container बिना साफ़ volume line के नहीं, जो pull request में review हो।

---

## 💻 Code / Config Example — Basic

```bash
# Create a named volume explicitly
docker volume create pgdata
# Docker prepares /var/lib/docker/volumes/pgdata/_data and registers the name

# Run Postgres using the volume
docker run -d \
  --name db \
  -e POSTGRES_PASSWORD=change-me \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16-alpine
# -d background; -e sets the admin password (use secrets in production)
# -v name:path mounts the volume; postgres stores all databases at that path

# Remove the container: data must survive
docker rm -f db
# -f stops and removes in one step; the volume pgdata is untouched

# Start a new container on the same volume: data is back
docker run -d --name db2 -e POSTGRES_PASSWORD=change-me \
  -v pgdata:/var/lib/postgresql/data postgres:16-alpine
# same mount, so the new container sees the old database files

# Inspect where Docker stored it
docker volume inspect pgdata
# shows Driver, Mountpoint (/var/lib/docker/volumes/pgdata/_data), Labels, Scope

# Modern, explicit syntax (preferred in scripts)
docker run --rm --mount type=volume,source=pgdata,target=/data alpine:3.20 ls /data
# --mount is verbose and errors on typos; -v silently creates missing things
```

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.yml: production-style stateful stack with volumes of every type
services:
  db:
    image: postgres:16-alpine                       # database image (example tag)
    restart: unless-stopped                         # survive reboot
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_pass  # password read from a secret file
      PGDATA: /var/lib/postgresql/data/pgdata       # subfolder avoids lost+found issues on mounts
    secrets:
      - db_pass                                     # mount the secret
    volumes:
      - pgdata:/var/lib/postgresql/data             # named volume: durable database files
      - ./db/init:/docker-entrypoint-initdb.d:ro    # bind mount: init SQL, read-only
    tmpfs:
      - /tmp:size=64m                               # RAM scratch space, never hits disk
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"] # DB ready check
      interval: 10s                                 # every 10 seconds
      timeout: 3s                                   # strict timeout
      retries: 5                                    # failures before unhealthy

  api:
    image: ghcr.io/acme/node-api:1.8.3              # Node.js API (example tag)
    depends_on:
      db:
        condition: service_healthy                  # wait for the database
    volumes:
      - uploads:/app/uploads                        # user uploads survive redeploys
    read_only: true                                 # immutable root filesystem

volumes:
  pgdata:
    labels:
      backup: "daily"                               # label used by backup scripts
  uploads: {}                                       # named volume for uploaded files

secrets:
  db_pass:
    file: ./secrets/db_pass.txt                     # secret file kept out of git
```

```bash
# Back up a volume to a tar.gz on the host without stopping the app (file-level, see 161)
docker run --rm \
  -v pgdata:/source:ro \
  -v "$(pwd)":/backup \
  alpine:3.20 tar czf /backup/pgdata-$(date +%F).tar.gz -C /source .
# --rm removes the helper; source mounted read-only; /backup is the current host folder
# -C /source . archives the volume contents; for databases prefer pg_dump (consistent)
```

YAML parsed and shell blocks checked with `bash -n`; not run against a Docker daemon. A raw file copy of a live database may be inconsistent, so use `pg_dump` for databases.

---

## 🟠 My Stack Integration
Node.js: uploads folder and local caches go to a named volume; code stays in the image. FastAPI: model files or SQLite (only for tiny apps) on a volume. Postgres/MongoDB/Redis (AOF): always a named volume. React: nothing to persist (static build), so no volume. Nginx: bind-mount config read-only, a named volume for Let's Encrypt certificates and cache. On a VPS, volumes live on the host disk, so plan disk size and offsite backups; on AWS ECS use EFS or EBS-backed volumes.

```yaml
# Nginx + Certbot sharing certificates through a named volume
services:
  web:
    image: nginx:1.27-alpine                 # reverse proxy
    volumes:
      - certs:/etc/letsencrypt:ro            # read-only certificates for Nginx
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro   # config as bind mount
  certbot:
    image: certbot/certbot:v2.11.0           # certificate manager (example tag)
    volumes:
      - certs:/etc/letsencrypt               # read-write so certbot can renew
volumes:
  certs: {}                                  # shared named volume
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running a database container with no volume.
✅ Correct: Always declare a named volume at the database's data directory.

❌ Mistake 2: Running `docker compose down -v` casually.
✅ Correct: `-v` deletes named volumes declared in the compose file. Use plain `down` normally.

❌ Mistake 3: Treating a volume as a backup.
✅ Correct: A volume protects against container removal, not disk failure or `rm -rf`. Take real backups off the host.

❌ Mistake 4: Mounting a volume over a directory that contains app code from the image.
✅ Correct: A mount hides the image's files at that path; mount only data directories.

---

## 🧠 Tricky Interview Question
You mounted a new empty named volume at `/usr/share/nginx/html` and the site shows 403. Another time, you bind-mounted an empty host folder at the same path and got the same result. Why do named volumes sometimes "just work"?

Answer: When an empty named volume is first mounted at a path that already has content in the image, Docker copies the image's files into the volume (seeding), so Nginx still finds its files. Bind mounts do not seed: the empty host directory hides the image's files, so there is nothing to serve (403/404). Seeding happens only on the first mount of an empty volume; after that, the volume's content wins even if the image changes, a classic cause of "my new image doesn't show new files".

---

## ⚫ Interview Questions + Answers

Q1: Where are volumes stored?
A1: `/var/lib/docker/volumes/<name>/_data` on Linux. On Docker Desktop it is inside the Linux VM.

Q2: Volume vs bind mount in one line?
A2: Volume is managed by Docker (portable, safer, backup-friendly); bind mount maps a specific host path (good for dev, config files).

Q3: What does `-v` vs `--mount` differ in?
A3: Same result, but `--mount` is explicit (`type=,source=,target=`) and fails if the host path does not exist; `-v` auto-creates a missing host directory as root.

Q4: Do volumes work across hosts?
A4: Local volumes do not. Use a network/volume driver (NFS, EFS, cloud plugin) or shared storage; databases should replicate instead.

Q5: How do you see which containers use a volume?
A5: `docker ps -a --filter volume=pgdata`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Databases, uploads, caches, certificates, any data that must outlive the container
- Sharing data between containers
- You need near-native I/O performance

❌ Avoid when:
- Data is disposable (use tmpfs or the writable layer)
- You need to edit host files live (use bind mounts in development)
- Multi-host persistence without a proper driver or replication

---

## 📊 Visual Diagram
```
                    HOST
   ┌──────────────────────────────────────────────┐
   │ /var/lib/docker/volumes/pgdata/_data  <──┐   │
   │ /home/deploy/app/nginx.conf  <────────┐  │   │
   │ RAM                                   │  │   │
   │                                       │  │   │
   │  ┌────────── container ───────────┐   │  │   │
   │  │ /var/lib/postgresql/data  ─────┼───┼──┘   │  VOLUME  (Docker managed)
   │  │ /etc/nginx/conf.d/default.conf ┼───┘      │  BIND    (host path)
   │  │ /tmp  ──────────────────────── RAM        │  TMPFS   (memory only)
   │  │ writable layer (deleted with container)   │
   │  └─────────────────────────────────┘         │
   └──────────────────────────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Volume | Docker-managed persistent storage | Docker का persistent storage |
| Bind mount | Host path mapped into container | Host path का mapping |
| tmpfs | In-memory mount | RAM वाला mount |
| Writable layer | Temporary top layer of a container | Container की अस्थायी ऊपरी layer |
| Seeding | Copying image files into an empty volume | Image की files volume में copy |
| Mountpoint | Host directory backing a volume | Volume का host directory |

---

## ⚡ 3-Line Summary
English: Volumes keep data outside the container's disposable layer so it survives removal and upgrades. Use named volumes for databases and uploads, bind mounts for dev and config, tmpfs for secrets and scratch. Volumes are not backups.
Hindi: Volumes data को container की अस्थायी layer के बाहर रखते हैं ताकि हटने और upgrade पर भी बचा रहे। Databases और uploads के लिए named volumes, dev और config के लिए bind mounts, secrets और scratch के लिए tmpfs इस्तेमाल करो। Volumes backup नहीं हैं।

---

## ➡️ Next Topic
**152. Bind Mounts vs Volumes**: a closer comparison of the two main mount types, and when each is the right choice.

---
