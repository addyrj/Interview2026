# 186. volumes Field
# हिंदी में: Compose का top-level `volumes` Field

---

## 🔵 Simple Definition (English)
The top-level `volumes:` key declares **named volumes** that Compose manages for you. Services then mount them by name. Data in a named volume lives outside the container, so it survives `docker compose down` and container recreation.

## 🔵 सरल परिभाषा (Hindi)
Top-level `volumes:` key **named volumes** declare करती है जिन्हें Compose manage करता है। Services उन्हें नाम से mount करती हैं। Named volume का data container के बाहर रहता है, इसलिए `docker compose down` और container दोबारा बनने के बाद भी बचा रहता है।

---

## 🔴 Problem it Solves
Container filesystems are temporary. Delete the Postgres container and all rows vanish. Bind-mounting host folders solves persistence but ties your file to host paths, permission problems (uid mismatch), and is slow on macOS. Top-level named volumes give portable, Docker-managed storage, with optional drivers (NFS, cloud) and settings, and are easily backed up.

## 🔴 यह क्यों बना? (Hindi)
Container का filesystem अस्थायी है। Postgres container delete करो तो सारी rows चली जाती हैं। Host folder को bind-mount करने से data बचता है पर file host paths से बँध जाती है, uid permission समस्याएँ आती हैं, और macOS पर slow है। Top-level named volumes portable, Docker-managed storage देते हैं, optional drivers (NFS, cloud) के साथ, और backup आसान होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Declare: volumes: { pgdata: {} } at top level.
Step 2 → In service: volumes: ["pgdata:/var/lib/postgresql/data"].
Step 3 → `docker compose up` creates volume <project>_pgdata if absent.
Step 4 → Docker stores data in /var/lib/docker/volumes/<project>_pgdata/_data.
Step 5 → If the volume is empty, image content at that path is copied in first time.
Step 6 → `down` keeps volumes; `down -v` DELETES them.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Declare करें: top level पर volumes: { pgdata: {} }।
Step 2 → Service में: volumes: ["pgdata:/var/lib/postgresql/data"]।
Step 3 → `docker compose up` volume <project>_pgdata बनाता है अगर न हो।
Step 4 → Data /var/lib/docker/volumes/<project>_pgdata/_data में रहता है।
Step 5 → Volume खाली हो तो पहली बार image का उस path का content copy होता है।
Step 6 → `down` volumes रखता है; `down -v` उन्हें DELETE कर देता है।
```

---

## 🟡 Real World Example
A founder ran `docker compose down -v` on the VPS "to clean up" before redeploying and lost the production Postgres volume; the last backup was a week old. Afterwards the team declared `pgdata` with `name: shop_pgdata_prod`, added a nightly `pg_dump` cron to S3, and banned `-v` in the deploy script. Redis got its own `redisdata` volume so queue jobs survive restarts.

## 🟡 Real Example Hindi mein
एक founder ने VPS पर redeploy से पहले "सफाई" के लिए `docker compose down -v` चला दिया और production Postgres volume खो गया; आखिरी backup एक हफ्ता पुराना था। बाद में टीम ने `pgdata` को `name: shop_pgdata_prod` के साथ declare किया, S3 में रोज़ रात `pg_dump` cron जोड़ा और deploy script में `-v` पर रोक लगाई। Redis को अपना `redisdata` volume मिला ताकि queue jobs restart पर बचें।

---

## 💻 Code / Config Example — Basic

```yaml
services:                         # containers
  db:                             # database service
    image: postgres:16-alpine     # example tag
    environment:                  # init settings
      POSTGRES_PASSWORD: example  # DEV ONLY
    volumes:                      # mount the named volume
      - pgdata:/var/lib/postgresql/data   # volume_name:container_path
volumes:                          # top-level declaration
  pgdata: {}                      # empty config = defaults (local driver)
```

## 💻 Code / Config Example — Advanced

```yaml
name: shop                        # project name (prefix for volumes)
services:                         # containers
  db:                             # PostgreSQL
    image: postgres:16-alpine     # example tag
    environment:                  # settings
      POSTGRES_PASSWORD: ${DB_PASSWORD:?required}   # fail fast if unset
    volumes:                      # mounts
      - pgdata:/var/lib/postgresql/data   # persistent database files
      - pgbackup:/backup          # place for dumps
  redis:                          # cache / queue
    image: redis:7-alpine         # example tag
    command: ["redis-server", "--appendonly", "yes"]   # AOF persistence
    volumes:                      # mounts
      - redisdata:/data           # redis writes AOF here
  uploads-nfs:                    # service using shared NFS storage
    image: alpine:3.20            # example tag
    command: ["sleep", "infinity"]   # keep container alive
    volumes:                      # mount
      - nfsdata:/shared           # NFS-backed volume
volumes:                          # top-level volume definitions
  pgdata:                         # database data
    name: shop_pgdata_prod        # fixed real name, independent of project name
    labels:                       # metadata for tooling
      backup: "nightly"           # label a backup job can filter on
  pgbackup: {}                    # default local volume
  redisdata: {}                   # default local volume
  nfsdata:                        # volume with custom driver options
    driver: local                 # local driver with NFS mount type
    driver_opts:                  # mount options passed to the driver
      type: nfs                   # filesystem type
      o: "addr=10.0.0.5,rw,nfsvers=4"   # example NFS server and options
      device: ":/exports/uploads" # remote path (example)
  legacy:                         # volume created before Compose
    external: true                # do not create/delete; must exist
    name: old_pgdata              # real name on the host
```

Note: `nfsdata` and `legacy` are examples: they require an NFS server and a pre-existing volume. Remove them if you do not have those. Not run locally.

---

## 🟠 My Stack Integration
For your VPS: PostgreSQL and Redis get named volumes; React static files do NOT need one (baked in image); Nginx certificates from certbot are a named volume or bind mount at `/etc/letsencrypt`. Back up volumes to S3.

```yaml
services:                         # your stack
  postgres:                       # database
    image: postgres:16-alpine     # example tag
    volumes:                      # mounts
      - pgdata:/var/lib/postgresql/data   # persisted data
  nginx:                          # proxy
    image: nginx:1.27-alpine      # example tag
    volumes:                      # mounts
      - certs:/etc/letsencrypt:ro # certbot certificates, read only for nginx
  certbot:                        # certificate renewal
    image: certbot/certbot:v2.11.0   # example tag
    volumes:                      # mounts
      - certs:/etc/letsencrypt    # same volume, read-write
  backup:                         # one-off backup job (run with: docker compose run --rm backup)
    image: alpine:3.20            # example tag
    profiles: ["tools"]           # not started by plain `up`
    volumes:                      # mounts
      - pgdata:/data:ro           # read-only access to DB files
      - ./backups:/out            # host folder receives the tarball
    command: ["tar", "czf", "/out/pgdata.tgz", "-C", "/data", "."]   # file-level copy (stop DB for consistency; prefer pg_dump)
volumes:                          # declarations
  pgdata: {}                      # postgres data
  certs: {}                       # TLS certificates
```

Security: volume data is stored as root on the host at /var/lib/docker/volumes; restrict SSH/sudo access. Never put secrets into a volume you back up to a public bucket. Encrypt EBS/disk at rest on AWS.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running `docker compose down -v` in production.
✅ Correct: Use `down` (no `-v`) and back up before any destructive command.

❌ Mistake 2: Using a volume but a wrong container path (`/var/lib/postgres` instead of `/var/lib/postgresql/data`).
✅ Correct: Check image docs; data must go where the app writes.

❌ Mistake 3: Declaring a volume in the service but forgetting the top-level entry.
✅ Correct: Named volumes must be declared top-level (bind mounts with `./path` need no declaration). Compose errors with "refers to undefined volume".

❌ Mistake 4: Changing `POSTGRES_PASSWORD` and expecting it to apply to an existing volume.
✅ Correct: Env vars only apply on first initialisation. Use `ALTER USER` or recreate the volume.

---

## 🧠 Tricky Interview Question
"You renamed the project folder from `app` to `shop`, redeployed, and your database is empty. The data is not deleted. Where is it?"

Answer: Volume names are prefixed with the project name: it was `app_pgdata`, now Compose created a new `shop_pgdata`. The old volume still exists (`docker volume ls`). Fix: set `name: app_pgdata` on the volume (or top-level `name:`) so the real name is stable, or copy the data to the new volume.

---

## ⚫ Interview Questions + Answers

Q1: Named volume vs bind mount?
A1: Named volume is managed by Docker under /var/lib/docker/volumes; bind mount maps an exact host path. Volumes are better for databases; bind mounts for source code in dev.

Q2: Does `docker compose down` delete volumes?
A2: No, only with `-v` / `--volumes`.

Q3: What does `external: true` mean?
A3: Compose uses a pre-existing volume and never creates or removes it.

Q4: How can two services share data?
A4: Mount the same named volume in both (be careful with concurrent writes).

Q5: How do you back up a named volume?
A5: Run a temporary container mounting it read-only and tar it, or use database-native dumps like `pg_dump`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Databases, queues, uploads, certificates must survive recreation.
- You want Docker to manage permissions and location.

❌ Avoid when:
- You need to edit files from the host editor (use bind mount).
- Data is disposable cache (use tmpfs).

---

## 📊 Visual Diagram
```
 compose.yaml                        Host disk
 volumes:
   pgdata: {}  ------------>  /var/lib/docker/volumes/shop_pgdata/_data
                                         ^
 services:                               | mount
   db:  [container /var/lib/postgresql/data]
 down      -> container removed, volume stays
 down -v   -> container AND volume removed (data lost!)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| named volume | Docker-managed persistent storage | Docker द्वारा managed स्थायी storage |
| bind mount | Host path mapped in container | host path का mapping |
| driver_opts | Options for volume driver | volume driver के options |
| external | Pre-existing resource | पहले से बना resource |
| down -v | Also removes volumes | volumes भी हटाता है |

---

## ⚡ 3-Line Summary
English: Top-level `volumes:` declares Docker-managed persistent storage.
English: Data survives `down` and container recreation, but not `down -v`.
English: Fix the real name with `name:` so renames do not create empty volumes.
Hindi: Top-level `volumes:` Docker-managed स्थायी storage declare करता है।
Hindi: Data `down` और container दोबारा बनने पर बचता है, पर `down -v` पर नहीं।
Hindi: `name:` से असली नाम fix करें ताकि rename पर खाली volume न बने।

---

## ➡️ Next Topic
187. image vs build - after storage, decide where each service's image comes from: a registry or a local Dockerfile.
