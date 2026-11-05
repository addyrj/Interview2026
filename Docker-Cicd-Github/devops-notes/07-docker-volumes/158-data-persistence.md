# 158. Data Persistence
# हिंदी में: Data Persistence (डेटा को स्थायी रखना)

---

## 🔵 Simple Definition (English)
Data persistence means data stays alive after a container stops, is deleted, or is replaced by a new image version. By default everything a container writes goes into a thin writable layer that is destroyed with the container. To persist data you mount a volume, a bind mount, or use external storage (RDS, S3, EFS).

## 🔵 सरल परिभाषा (Hindi)
Data persistence का मतलब है कि container रुकने, delete होने या नए image version से replace होने के बाद भी data ज़िंदा रहे। Default रूप से container जो कुछ लिखता है वो एक पतली writable layer में जाता है जो container के साथ खत्म हो जाती है। Data बचाने के लिए volume, bind mount या external storage (RDS, S3, EFS) use करते हैं।

---

## 🔴 Problem it Solves
- Containers are ephemeral by design: you redeploy by killing the old one and starting a new one. If Postgres files lived inside the container, every deploy would wipe the database.
- Writing into the writable layer is also slower (copy-on-write via the storage driver) and the layer cannot be shared with other containers.
- Persistence separates the lifecycle of code (image, changes every deploy) from the lifecycle of data (volume, lives for years).

## 🔴 यह क्यों बना? (Hindi)
- Containers design से ephemeral हैं: deploy का मतलब पुराना container मारो और नया चलाओ। अगर Postgres की files container के अंदर होतीं तो हर deploy पर database साफ़ हो जाता।
- Writable layer में लिखना slow भी है (storage driver का copy-on-write) और इसे दूसरे containers से share नहीं कर सकते।
- Persistence code (image, हर deploy पर बदलता) और data (volume, सालों जीता है) का lifecycle अलग कर देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Container starts: image layers (read-only) + one thin writable layer on top.
Step 2 → App writes a file to a normal path  → goes to writable layer → lost on `docker rm`.
Step 3 → You declare a mount: -v pgdata:/var/lib/postgresql/data
Step 4 → Docker bind-mounts the host folder over that path inside the container.
Step 5 → App writes to that path → bytes land on host disk (the volume), not in the layer.
Step 6 → Container deleted/replaced → volume untouched → new container mounts same volume.
Step 7 → New container sees the old data and continues.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Container शुरू: image layers (read-only) + ऊपर एक पतली writable layer।
Step 2 → App सामान्य path पर file लिखता है → writable layer में जाती है → `docker rm` पर खत्म।
Step 3 → आप mount declare करते हैं: -v pgdata:/var/lib/postgresql/data
Step 4 → Docker host का folder उस path के ऊपर container के अंदर mount कर देता है।
Step 5 → App उस path पर लिखता है → bytes host disk (volume) पर जाते हैं, layer में नहीं।
Step 6 → Container delete/replace → volume सुरक्षित → नया container वही volume mount करता है।
Step 7 → नया container पुराना data देखता है और वहीं से चलता रहता है।
```

---

## 🟡 Real World Example
A food-delivery startup deploys its FastAPI order service on a single EC2 VPS with Postgres in Docker. Every Friday they ship a new image. Because Postgres uses the named volume `orders_pgdata` and user-uploaded invoices live in an S3 bucket, `docker compose up -d` with the new image takes 10 seconds and zero data is lost. The one time a junior engineer forgot the volume line, Saturday's orders vanished at the next redeploy: a classic postmortem.

## 🟡 Real Example Hindi mein
एक food-delivery startup अपनी FastAPI order service एक EC2 VPS पर Postgres (Docker में) के साथ चलाती है। हर शुक्रवार नया image जाता है। Postgres named volume `orders_pgdata` इस्तेमाल करता है और user के invoices S3 bucket में हैं, इसलिए नए image के साथ `docker compose up -d` 10 सेकंड में हो जाता है और कोई data नहीं जाता। एक बार junior engineer volume की line भूल गया तो अगले redeploy पर शनिवार के orders गायब हो गए: classic postmortem।

---

## 💻 Code / Config Example — Basic
```bash
# PROVE that data is lost without a volume (runs on any machine with Docker)
docker run -d --name t1 alpine sh -c 'echo hello > /data.txt && sleep 600'  # write a file in writable layer
docker exec t1 cat /data.txt                     # prints: hello
docker rm -f t1                                  # remove container: writable layer destroyed
docker run --rm alpine cat /data.txt             # error: No such file (new container, fresh layer)

# NOW WITH a named volume
docker run -d --name t2 -v mydata:/data alpine sh -c 'echo hello > /data/f.txt && sleep 600'  # write into volume
docker rm -f t2                                  # container removed, volume mydata stays
docker run --rm -v mydata:/data alpine cat /data/f.txt   # prints: hello  (data survived)
docker volume rm mydata                          # clean up the demo volume
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.prod.yml - persistence for every stateful piece of an app
services:
  api:                                   # Node.js API (stateless: no volume for app data)
    image: myorg/orders-api:1.4.2        # example tag; image holds code only
    restart: unless-stopped              # come back after reboot
    environment:
      UPLOAD_BUCKET: orders-invoices-prod   # files go to S3, not to local disk
    read_only: true                      # container root filesystem read-only (security)
    tmpfs:
      - /tmp                             # scratch space in RAM, intentionally NOT persisted
    depends_on:
      db:
        condition: service_healthy       # start only when DB is ready
  db:                                    # Postgres: the stateful part
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/pg_pw   # secret from file
    volumes:
      - pgdata:/var/lib/postgresql/data  # PERSIST: database files
      - pgbackups:/backups               # PERSIST: dump files written by cron job
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]   # ready check
      interval: 10s                      # run every 10s
      timeout: 5s                        # fail if no answer in 5s
      retries: 5                         # 5 failures = unhealthy
    secrets:
      - pg_pw
  redis:                                 # cache: persistence optional
    image: redis:7
    command: ["redis-server", "--appendonly", "yes"]   # AOF persistence inside the volume
    volumes:
      - redisdata:/data                  # Redis writes AOF/RDB here
volumes:
  pgdata:                                # named volume for DB
  pgbackups:                             # named volume for dumps
  redisdata:                             # named volume for redis
secrets:
  pg_pw:
    file: ./secrets/pg_pw.txt            # not committed to git
```

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: keep them stateless. Sessions in Redis, files in S3, data in Postgres. Then any container can die at any time.
- **React**: build output is static, baked into an Nginx image. No volume needed. Only Let's Encrypt certificates need persistence (`/etc/letsencrypt`) so you do not hit rate limits.
- **Nginx on VPS**: persist certs and logs: `./certs:/etc/letsencrypt` bind mount or a named volume.
- **AWS**: on EC2 the volume lives on the instance's EBS disk. If the instance is terminated and the EBS is deleted-on-termination, data goes too. Better: use RDS for production DB, or enable EBS snapshots (AWS Backup) for the VPS.

```yaml
# nginx service that keeps certificates across redeploys
  nginx:
    image: nginx:1.27                      # example tag
    ports: ["80:80", "443:443"]            # public ports
    volumes:
      - letsencrypt:/etc/letsencrypt:ro    # certs persisted, read-only for nginx
      - ./nginx.conf:/etc/nginx/nginx.conf:ro   # config from repo, read-only
```
Security: persisted data is plaintext on disk. Use encrypted EBS, restrict file permissions, and never store secrets in a volume that is shared widely.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Storing uploads in the container filesystem (`/app/uploads`).
✅ Correct: Mount a volume or, better, upload to S3 so you can scale to several containers.

❌ Mistake 2: Mounting the volume at the wrong path (`/var/lib/postgres` instead of `/var/lib/postgresql/data`).
✅ Correct: Check the image docs. A wrong path means Docker creates an empty anonymous volume and your data still lands in the layer.

❌ Mistake 3: Believing "volume = backup".
✅ Correct: A volume survives container deletion, not disk failure or `rm -rf`. Take snapshots and dumps (note 161).

❌ Mistake 4: Persisting everything, including caches and temp files.
✅ Correct: Persist only what you cannot regenerate. Use `tmpfs` for scratch data.

---

## 🧠 Tricky Interview Question
Your container restarts after a crash (`restart: always`). Did you lose the files it wrote to its filesystem?

Answer: No. A restart of the same container keeps its writable layer, so data survives `docker restart` and automatic restarts. Data is lost only when the container is removed (`docker rm`, `compose down`, recreate on image change, or `compose up` detecting a changed config). That is why "it worked after restart but vanished after deploy" is the typical symptom of missing persistence.

---

## ⚫ Interview Questions + Answers

Q1: Why are containers ephemeral?
A1: They are meant to be replaced, not repaired. Immutable image + external state makes deploys, scaling and rollback simple.

Q2: Three ways to persist data?
A2: Named volumes (Docker-managed), bind mounts (host path), and external services (RDS, S3, EFS). tmpfs is the opposite: memory only.

Q3: Where does the writable layer live?
A3: Under the storage driver directory, usually `/var/lib/docker/overlay2/<id>/diff`. It is deleted with the container.

Q4: Is it OK to run a production database in Docker?
A4: For small setups on a VPS yes, with a named volume, backups and monitoring. For critical production, managed RDS or an operator-managed cluster is safer.

Q5: How do you make an app horizontally scalable w.r.t. state?
A5: Make it stateless: sessions in Redis, files in S3, data in a shared DB. Then volumes are needed only for the stateful services.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Databases, message queues with disk storage, certificates, search indexes.
- User-generated files on a single host (when S3 is not available).

❌ Avoid when:
- The data is a cache or temp file (use tmpfs or no persistence).
- You need data shared across many hosts (use S3, EFS, or a network driver instead of a local volume).

---

## 📊 Visual Diagram
```
  WITHOUT VOLUME                          WITH VOLUME
  +------------------+                    +------------------+
  | container v1     |                    | container v1     |
  | [writable layer] |  docker rm         | [writable layer] |
  |   data.db  ----X |  ---------->       |   (empty)        |
  +------------------+   data LOST        +--------+---------+
                                                   | mount
  +------------------+                    +--------v---------+
  | container v2     |                    | VOLUME pgdata    |  <- survives
  | (new, empty)     |                    |   data.db        |
  +------------------+                    +--------^---------+
                                                   | mount
                                          +--------+---------+
                                          | container v2     |  sees data.db
                                          +------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Ephemeral | Short-lived, disposable | अस्थायी |
| Writable layer | Top layer where container writes | container की लिखने वाली परत |
| Persistence | Data surviving container removal | data का बचा रहना |
| Stateless | App keeps no local state | बिना local state वाला app |
| tmpfs | RAM-only mount | सिर्फ RAM वाला mount |
| Snapshot | Point-in-time disk copy (EBS) | किसी समय की disk copy |

---

## ⚡ 3-Line Summary
English: Container filesystem dies with the container; volumes outlive it.
Mount a volume at the exact data path of stateful services, keep apps stateless.
A volume is not a backup: add snapshots and dumps.
Hindi: Container का filesystem container के साथ खत्म होता है; volumes उससे ज़्यादा जीते हैं।
Stateful services के सही data path पर volume mount करो और apps को stateless रखो।
Volume backup नहीं है: snapshots और dumps भी लो।

---

## ➡️ Next Topic
159. Database Volumes: the most important persistence case, running Postgres/MySQL/MongoDB safely with volumes.
