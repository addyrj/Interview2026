# 159. Database Volumes
# हिंदी में: Database Volumes (डेटाबेस के लिए volumes)

---

## 🔵 Simple Definition (English)
Database volumes are Docker volumes mounted at the exact data directory of a database image (for example `/var/lib/postgresql/data` for Postgres, `/var/lib/mysql` for MySQL, `/data/db` for MongoDB) so that tables, indexes and WAL files survive container replacement.

## 🔵 सरल परिभाषा (Hindi)
Database volumes वो Docker volumes हैं जो database image की सही data directory पर mount होते हैं (जैसे Postgres के लिए `/var/lib/postgresql/data`, MySQL के लिए `/var/lib/mysql`, MongoDB के लिए `/data/db`), ताकि tables, indexes और WAL files container बदलने पर भी बची रहें।

---

## 🔴 Problem it Solves
- Official DB images declare a `VOLUME` in their Dockerfile. If you do not mount a named one, Docker silently creates an anonymous volume with a random name, and a later `docker volume prune` can wipe your database.
- Databases need reliable, fast, durable disk with correct ownership (uid 999 for postgres, 999 for mysql, etc.).
- Major upgrades (Postgres 15 to 16) change the on-disk format, so the same volume cannot simply be reused with a new major image.

## 🔴 यह क्यों बना? (Hindi)
- Official DB images अपनी Dockerfile में `VOLUME` declare करती हैं। अगर आप named volume mount नहीं करते तो Docker चुपचाप random नाम का anonymous volume बना देता है, और बाद में `docker volume prune` आपका database उड़ा सकता है।
- Databases को भरोसेमंद, तेज़, durable disk और सही ownership (postgres के लिए uid 999 आदि) चाहिए।
- Major upgrade (Postgres 15 से 16) में on-disk format बदलता है, इसलिए वही volume नए major image के साथ सीधे reuse नहीं हो सकता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick the right mount path from the image docs (postgres: /var/lib/postgresql/data).
Step 2 → Create/declare a named volume (pgdata).
Step 3 → First start: data dir is empty → entrypoint runs initdb, creates users/DB from env vars,
         and runs scripts in /docker-entrypoint-initdb.d/.
Step 4 → Later starts: data dir is NOT empty → init scripts and POSTGRES_PASSWORD are IGNORED.
Step 5 → Healthcheck (pg_isready) tells Compose when the DB accepts connections.
Step 6 → Backups: pg_dump into a second volume / S3, or volume snapshot with the DB stopped.
Step 7 → Upgrade: dump old → new volume with new image → restore.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Image docs से सही mount path चुनो (postgres: /var/lib/postgresql/data)।
Step 2 → Named volume (pgdata) बनाओ/declare करो।
Step 3 → पहली बार start: data dir खाली → entrypoint initdb चलाता है, env vars से user/DB बनाता है,
         और /docker-entrypoint-initdb.d/ की scripts चलाता है।
Step 4 → आगे की बार: data dir खाली नहीं → init scripts और POSTGRES_PASSWORD IGNORE होते हैं।
Step 5 → Healthcheck (pg_isready) Compose को बताता है कि DB connections ले रहा है।
Step 6 → Backup: pg_dump दूसरे volume / S3 में, या DB बंद करके volume snapshot।
Step 7 → Upgrade: पुराना dump → नए image के नए volume में restore।
```

---

## 🟡 Real World Example
A SaaS team ran MySQL in Docker on one EC2 box. They changed `MYSQL_ROOT_PASSWORD` in compose and redeployed; the new password did not work, because the volume already held an initialized database and the entrypoint skips init. They lost two hours before learning that env-var credentials apply only on first initialization. Fix: connect with the old password, run `ALTER USER`, and update the secret.

## 🟡 Real Example Hindi mein
एक SaaS team ने एक EC2 box पर MySQL Docker में चलाया। उन्होंने compose में `MYSQL_ROOT_PASSWORD` बदलकर redeploy किया; नया password काम नहीं किया क्योंकि volume में initialized database पहले से था और entrypoint init skip करता है। दो घंटे गए तब समझ आया कि env-var credentials सिर्फ पहली initialization पर लागू होते हैं। Fix: पुराने password से connect करके `ALTER USER` चलाओ और secret update करो।

---

## 💻 Code / Config Example — Basic
```yaml
# docker-compose.yml - minimal Postgres with a named volume
services:
  db:
    image: postgres:16                       # example tag; pin a major version
    environment:
      POSTGRES_USER: app                     # DB superuser created on first init
      POSTGRES_PASSWORD: change_me           # demo only; use secrets in production
      POSTGRES_DB: appdb                     # database created on first init
    volumes:
      - pgdata:/var/lib/postgresql/data      # named volume at the Postgres data dir
    ports:
      - "127.0.0.1:5432:5432"                # bind to localhost only, never 0.0.0.0
volumes:
  pgdata:                                    # declare the named volume
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.prod.yml - Postgres + MongoDB + Redis with healthchecks, secrets, init scripts
services:
  postgres:
    image: postgres:16                       # example tag, update after testing
    restart: unless-stopped                  # survive host reboot
    shm_size: 256mb                          # Postgres uses /dev/shm; default 64mb is small
    environment:
      POSTGRES_USER: app                     # app user
      POSTGRES_DB: appdb                     # app database
      POSTGRES_PASSWORD_FILE: /run/secrets/pg_pw   # official images support *_FILE variables
    secrets:
      - pg_pw                                # mount the secret file into the container
    volumes:
      - pgdata:/var/lib/postgresql/data      # persistent data
      - ./initdb:/docker-entrypoint-initdb.d:ro   # *.sql / *.sh run ONLY on first init
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d appdb"]   # returns 0 when ready
      interval: 10s                          # probe every 10 seconds
      timeout: 5s                            # each probe max 5 seconds
      retries: 6                             # unhealthy after 6 failures
      start_period: 20s                      # grace time while initdb runs
    networks: [backend]                      # only the backend network, not public
    deploy:
      resources:
        limits:
          memory: 1g                         # cap memory (honoured by compose v2 on plain Docker)
  mongo:
    image: mongo:7                           # example tag
    restart: unless-stopped
    volumes:
      - mongodata:/data/db                   # MongoDB data dir
      - mongoconfig:/data/configdb           # MongoDB config dir (second declared volume of image)
    networks: [backend]
  redis:
    image: redis:7
    command: ["redis-server", "--appendonly", "yes"]   # durable AOF
    volumes:
      - redisdata:/data                      # redis data dir
    networks: [backend]
networks:
  backend:
    internal: true                           # no outbound internet, no host exposure
volumes:
  pgdata:
  mongodata:
  mongoconfig:
  redisdata:
secrets:
  pg_pw:
    file: ./secrets/pg_pw.txt                # chmod 600, in .gitignore
```

---

## 🟠 My Stack Integration
- **Node.js** connects with `postgres://app:***@postgres:5432/appdb`; the hostname `postgres` is the Compose service name (Docker DNS).
- **FastAPI** with SQLAlchemy: wait for `service_healthy` so migrations (Alembic) do not fail on boot.
- **Nginx** never talks to the DB. Only the `backend` network connects API and DB.
- **VPS**: put Docker's data-root (`/var/lib/docker`) on a separate EBS disk, take nightly snapshots, and also `pg_dump` to S3.
- **AWS**: for real production consider RDS, so patching, PITR backups and failover are managed.

```yaml
# api service waiting for DB
  api:
    image: myorg/api:2.0.1                  # example
    depends_on:
      postgres:
        condition: service_healthy          # wait for pg_isready
    networks: [backend, frontend]           # reaches DB and Nginx
    environment:
      DATABASE_URL_FILE: /run/secrets/db_url   # app reads URL from a secret file
```
Security: never publish 5432 on a public IP; use a firewall (security group) and strong secrets; keep DB on an internal network.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No volume line, relying on the image's anonymous `VOLUME`.
✅ Correct: Always declare a named volume at the data path.

❌ Mistake 2: Changing `POSTGRES_PASSWORD` or init scripts and expecting them to apply.
✅ Correct: They apply on first init only. Use `ALTER USER` or migrations, or start with a new empty volume.

❌ Mistake 3: Bind-mounting a host folder on Docker Desktop (Mac/Windows) for DB data.
✅ Correct: Use a named volume; bind mounts there are slow and can break fsync and permissions.

❌ Mistake 4: Upgrading `postgres:15` to `postgres:16` on the same volume.
✅ Correct: Dump and restore (`pg_dumpall`) or use `pg_upgrade`. Postgres refuses to start with a mismatched data dir.

❌ Mistake 5: Using `docker kill`/power-off often on DB containers.
✅ Correct: `docker stop -t 60 db` gives time for clean shutdown (set `stop_grace_period: 60s`).

---

## 🧠 Tricky Interview Question
You deleted the Postgres container and started a new one with the same compose file, but the app shows an empty database. The volume `pgdata` still exists. What happened?

Answer: Likely the Compose project name changed (different folder name or `-p`), so Compose created a new volume `newproj_pgdata` instead of reusing `oldproj_pgdata`. Check `docker volume ls`, then either set `name:` in the compose file or `COMPOSE_PROJECT_NAME`, or mount the old volume as `external: true`. Another cause: the mount path was wrong so data was in the container layer.

---

## ⚫ Interview Questions + Answers

Q1: Why use a named volume instead of a bind mount for DB data?
A1: Docker manages it, correct permissions are set by the image entrypoint, it is portable, faster on Docker Desktop, and easier to back up with a helper container.

Q2: Do init scripts run on every start?
A2: No, only when the data directory is empty.

Q3: How do you take a consistent backup?
A3: Logical: `pg_dump`/`mongodump` while running. Physical: stop the container then copy/snapshot the volume, or use `pg_basebackup`.

Q4: Why healthchecks for DBs?
A4: `depends_on` alone waits for container start, not readiness; `service_healthy` waits until the DB really accepts connections.

Q5: Why expose 5432 on 127.0.0.1 only?
A5: Publishing on all interfaces exposes the DB to the internet; bots scan 5432/27017 within minutes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Dev, staging, CI integration tests, small single-VPS production.
- You want repeatable infrastructure with backups scripted.

❌ Avoid when:
- You need HA, automatic failover, PITR with minimal ops: use RDS/Atlas or an operator.
- Data is large and needs very high IOPS: dedicated database hosts with tuned storage.

---

## 📊 Visual Diagram
```
 Internet
    |
 [Nginx :443]---frontend net---[API (Node/FastAPI)]
                                     |
                              backend net (internal)
                                     |
                         +-----------v-----------+
                         | postgres container    |
                         |  /var/lib/postgresql/ |
                         |        data           |
                         +-----------+-----------+
                                     | mount
                         +-----------v-----------+
                         | volume: pgdata        |---> nightly pg_dump ---> S3
                         +-----------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Data directory | Folder where the DB stores files | DB की files का folder |
| initdb | First-time DB initialization | पहली बार DB setup |
| WAL | Write-ahead log for durability | durability के लिए log |
| Healthcheck | Command that tells if service is ready | तैयार है या नहीं की जाँच |
| pg_dump | Logical backup tool of Postgres | Postgres का backup tool |
| PITR | Point-in-time recovery | किसी समय पर वापस जाना |

---

## ⚡ 3-Line Summary
English: Mount a named volume at the DB image's exact data path.
Credentials and init scripts apply only to an empty volume; majors need dump/restore.
Keep DB on an internal network, healthchecked, and backed up off the host.
Hindi: DB image के सही data path पर named volume mount करो।
Credentials और init scripts सिर्फ खाली volume पर लागू होते हैं; major upgrade में dump/restore चाहिए।
DB को internal network, healthcheck और host के बाहर backup के साथ रखो।

---

## ➡️ Next Topic
160. Sharing Volumes Between Containers: how two or more containers (app, nginx, backup job) can use the same data safely.
