# 195. volumes in Compose
# हिंदी में: Compose में Volumes (data को container के बाहर सुरक्षित रखना)

---

## 🔵 Simple Definition (English)
The service-level `volumes:` key mounts storage into a container: a named volume managed by Docker, a bind mount from a host folder, or a tmpfs in memory. The top-level `volumes:` key declares named volumes so they can be shared and kept after containers are removed.

## 🔵 सरल परिभाषा (Hindi)
Service-level `volumes:` key container में storage mount करती है: Docker द्वारा managed named volume, host folder से bind mount, या memory में tmpfs। Top-level `volumes:` key named volumes declare करती है ताकि वे share हो सकें और container हटने के बाद भी बचे रहें।

---

## 🔴 Problem it Solves
A container filesystem is temporary. When you run `docker compose down` or recreate a container for a new image, all data written inside it (Postgres rows, uploaded files) is lost. Developers also need their editor changes to appear inside the container immediately without rebuilding.

## 🔴 यह क्यों बना? (Hindi)
Container का filesystem अस्थायी होता है। `docker compose down` चलाने या नई image के लिए container दोबारा बनाने पर अंदर लिखा सारा data (Postgres rows, uploaded files) खो जाता है। Developers को भी चाहिए कि editor के बदलाव rebuild के बिना तुरंत container में दिखें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Declare a named volume at top level: volumes: { pgdata: {} }
Step 2 → In the service, map it: pgdata:/var/lib/postgresql/data
Step 3 → `docker compose up` creates volume "<project>_pgdata" if it does not exist
Step 4 → Docker mounts it into the container; first time, image data at that path is copied in
Step 5 → The container writes data there; it lives on the host under /var/lib/docker/volumes
Step 6 → `docker compose down` removes containers but KEEPS the volume
Step 7 → `docker compose down -v` deletes volumes too (data loss, be careful)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Top level पर named volume declare करें: volumes: { pgdata: {} }
Step 2 → Service में map करें: pgdata:/var/lib/postgresql/data
Step 3 → `docker compose up` "<project>_pgdata" volume बनाता है अगर नहीं है
Step 4 → Docker उसे container में mount करता है; पहली बार image का उस path का data copy होता है
Step 5 → Container वहाँ data लिखता है; वह host पर /var/lib/docker/volumes में रहता है
Step 6 → `docker compose down` containers हटाता है पर volume रखता है
Step 7 → `docker compose down -v` volumes भी मिटा देता है (data loss, सावधान!)
```

---

## 🟡 Real World Example
A Swiggy-like service runs Postgres in Compose on EC2. The team deploys a new API image daily with `docker compose up -d`; the Postgres container is recreated on image bumps, but the `pgdata` named volume keeps all orders. A nightly cron runs `pg_dump` into a bind-mounted `/backups` folder that is then synced to S3.

## 🟡 Real Example Hindi mein
Swiggy जैसी service EC2 पर Compose में Postgres चलाती है। Team रोज़ नई API image `docker compose up -d` से deploy करती है; image बदलने पर Postgres container दोबारा बनता है, पर `pgdata` named volume सारे orders बचाए रखता है। रात को cron `pg_dump` को bind-mount किए `/backups` folder में रखता है, जो फिर S3 में sync होता है।

---

## 💻 Code / Config Example — Basic
```yaml
# docker-compose.yml  (Basic: Postgres with a named volume)
services:
  db:
    image: postgres:16-alpine                 # example tag
    environment:
      POSTGRES_PASSWORD: example              # demo only; use secrets in production
    volumes:
      - pgdata:/var/lib/postgresql/data       # named volume : path inside container
volumes:
  pgdata: {}                                   # declare the named volume (Docker-managed)
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml  (Advanced: all three mount types + long syntax)
services:
  api:
    build: ./api                              # Node.js image
    volumes:
      - type: bind                            # bind mount (host folder)
        source: ./api/src                     # host path (dev only)
        target: /app/src                      # path in container
        read_only: false                      # editor changes visible, container may write
      - type: volume                          # named volume
        source: uploads                       # declared below
        target: /app/uploads                  # user uploaded files persist here
      - type: tmpfs                           # RAM-backed temp storage
        target: /tmp                          # fast, vanishes on stop
        tmpfs:
          size: 67108864                      # 64 MB limit in bytes
      - node_modules:/app/node_modules        # anonymous-style trick: keep container's modules, don't overwrite with host's

  postgres:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data       # persistent DB files
      - ./db/init:/docker-entrypoint-initdb.d:ro   # init SQL, read-only (:ro)
      - ./backups:/backups                    # host folder for dumps

  nginx:
    image: nginx:1.27-alpine
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro  # config read-only
      - ./web/dist:/usr/share/nginx/html:ro          # React build, read-only
      - certs:/etc/letsencrypt:ro                    # TLS certs shared from a volume

volumes:
  pgdata: {}                                  # DB data
  uploads: {}                                 # user files
  node_modules: {}                            # dev dependency cache
  certs:
    external: true                            # created outside this file: docker volume create certs
    name: letsencrypt_certs                   # real volume name on the host
```

Useful commands: `docker volume ls`, `docker volume inspect <name>`, backup: `docker run --rm -v <name>:/data -v $PWD:/out alpine tar czf /out/data.tgz -C /data .`

---

## 🟠 My Stack Integration
- **Node.js dev:** bind mount `./src` plus a `node_modules` named volume so host (Mac) binaries do not overwrite Linux ones. Pair with Compose Watch (topic 200).
- **FastAPI:** bind `./app` in dev; in prod bake code into the image, no bind mount.
- **React + Nginx:** build with a multi-stage image, or mount `dist` read-only for a quick VPS setup.
- **VPS:** place volumes on a disk with space and snapshot it; on AWS use an EBS volume and EBS snapshots.
- **Security:** use `:ro` for configs, never mount `/var/run/docker.sock` or `/` into app containers, and keep secret files out of bind mounts that are in git.

```yaml
# docker-compose.yml  (my stack: persistent redis + postgres)
services:
  redis:
    image: redis:7-alpine                         # cache
    command: ["redis-server", "--appendonly", "yes"]  # AOF persistence on
    volumes:
      - redisdata:/data                           # AOF file stored here
volumes:
  redisdata: {}                                   # named volume
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running `docker compose down -v` in production "to clean up".
✅ Correct: Use `docker compose down` (no -v); delete volumes only intentionally after a backup.

❌ Mistake 2: Bind-mounting an empty host folder over a path that has files in the image (e.g. `/app/node_modules`). The image files disappear.
✅ Correct: Use a named volume for that path or build the folder in the image.

❌ Mistake 3: Wrong file ownership. Postgres or a non-root Node user cannot write to a bind mount owned by root.
✅ Correct: `chown` the host folder to the container UID, or use a named volume.

❌ Mistake 4: Treating a volume as a backup. It lives on the same disk.
✅ Correct: Dump to another place (S3) regularly and test restores.

---

## 🧠 Tricky Interview Question
You changed the image version of Postgres from 15 to 16 in Compose and ran `up -d`. The container crash-loops though the volume has data. Why?

Answer: The data directory was created by Postgres 15; major versions use an incompatible on-disk format, so 16 refuses to start. Volumes persist data but do not migrate it. Use `pg_dump`/`pg_upgrade` or dump from 15 and restore into a new volume with 16.

---

## ⚫ Interview Questions + Answers

Q1: Named volume vs bind mount?
A1: Named volume is managed by Docker (portable, better performance on Mac/Windows, safe default for data). Bind mount maps an exact host path (good for dev code and config), tied to host layout.

Q2: What does top-level `volumes:` do?
A2: Declares named volumes (and options like `external`, `driver`, `name`) so services can reference and share them.

Q3: Short vs long syntax?
A3: Short: `source:target:mode`. Long uses `type`, `source`, `target`, `read_only`, and is clearer and supports tmpfs options.

Q4: How can two containers share data?
A4: Mount the same named volume in both (for example api writes uploads and nginx serves them read-only).

Q5: Where is a named volume physically stored?
A5: Under `/var/lib/docker/volumes/<name>/_data` on Linux hosts.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Databases, uploads, caches that must survive redeploys.
- Dev hot-reload with bind mounts.
- Sharing read-only config.

❌ Avoid when:
- Production app code: bake it into the image for reproducibility.
- Many replicas across nodes (local volumes are per host; use S3/EFS or managed DB).

---

## 📊 Visual Diagram
```
   Host disk                              Container
 +-----------------------------+      +----------------------+
 | /var/lib/docker/volumes/    |<---->| /var/lib/postgresql  |  named volume
 |   proj_pgdata/_data         |      +----------------------+
 | ./api/src (your folder)     |<---->| /app/src             |  bind mount
 +-----------------------------+      | /tmp (RAM)           |  tmpfs
 compose down  -> containers gone, volumes stay
 compose down -v -> volumes deleted too
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| named volume | Docker-managed persistent storage | Docker द्वारा managed स्थायी storage |
| bind mount | Host path mapped into container | host folder का mapping |
| tmpfs | In-memory temporary mount | memory में अस्थायी mount |
| :ro | Read-only flag | सिर्फ पढ़ने योग्य |
| external volume | Volume created outside Compose | Compose के बाहर बना volume |
| persistence | Data survives container removal | data का बचे रहना |

---

## ⚡ 3-Line Summary
English: Volumes keep data outside the container's life. Use named volumes for data, bind mounts for dev code and config, tmpfs for temp files. Never `down -v` on production without a backup.
Hindi: Volumes data को container की उम्र से बाहर रखते हैं। Data के लिए named volumes, dev code और config के लिए bind mounts, temp files के लिए tmpfs। Backup के बिना production पर `down -v` कभी न चलाएँ।

---

## ➡️ Next Topic
**196. networks in Compose**: data is safe; next we control which containers can talk to each other.
