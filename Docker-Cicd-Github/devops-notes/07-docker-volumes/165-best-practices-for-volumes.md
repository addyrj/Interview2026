# 165. Best Practices for Volumes
# हिंदी में: Volumes के लिए Best Practices

---

## 🔵 Simple Definition (English)
**Volume best practices** are the rules that keep container data safe, portable and secure: use named volumes for persistent data, keep containers stateless, set correct permissions, mount read-only when possible, back up regularly, and never store secrets in volumes.

## 🔵 सरल परिभाषा (Hindi)
**Volume best practices** वो नियम हैं जो container data को safe, portable और secure रखते हैं: persistent data के लिए named volumes, containers को stateless रखना, सही permissions, जहाँ हो सके read-only mount, नियमित backup, और secrets कभी volume में नहीं।

---

## 🔴 Problem it Solves
Teams often learn volumes the hard way: a database loses data after redeploy because it used an anonymous volume, a bind mount makes the app run only on one developer's laptop, root-owned files block deploys, or a compromised container overwrites its own code. Without a checklist, every project repeats the same incidents.

## 🔴 यह क्यों बना? (Hindi)
Teams अक्सर volumes मुश्किल तरीके से सीखती हैं: anonymous volume की वजह से redeploy पर database का data चला गया, bind mount की वजह से app सिर्फ एक developer के laptop पर चलता है, root-owned files से deploy रुक गया, या compromised container ने अपना ही code overwrite कर दिया। Checklist न हो तो हर project यही गलतियाँ दोहराता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decide what is STATE (db files, uploads) and what is CODE (image)
Step 2 → State goes to a NAMED volume (or managed DB like RDS); code stays in the image
Step 3 → Mount with least privilege: :ro for config/static, rw only where app writes
Step 4 → Fix ownership: run as non-root user, chown the volume path in Dockerfile
Step 5 → Label + back up volumes (cron + off-site copy to S3)
Step 6 → Monitor disk usage (docker system df) and prune only unlabelled junk
Step 7 → Test restore regularly - a backup never restored is a hope, not a backup
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → तय करो क्या STATE है (db files, uploads) और क्या CODE (image)
Step 2 → State named volume में (या RDS जैसा managed DB); code image में
Step 3 → कम से कम अधिकार: config/static के लिए :ro, rw सिर्फ वहाँ जहाँ app लिखता है
Step 4 → Ownership ठीक करो: non-root user चलाओ, Dockerfile में path chown करो
Step 5 → Volumes पर label लगाओ और backup लो (cron + S3 पर off-site copy)
Step 6 → Disk usage देखते रहो (docker system df), prune सिर्फ बिना-label कचरे पर
Step 7 → Restore का test करते रहो - जो backup कभी restore नहीं हुआ वो उम्मीद है, backup नहीं
```

---

## 🟡 Real World Example
An e-commerce company on a single EC2 box ran Postgres in Docker. A teammate used `./pgdata:/var/lib/postgresql/data` (bind mount) and later moved the repo folder; the DB "reset". After a post-mortem they adopted: named volume `pgdata`, label `keep=true`, nightly `pg_dump` to S3, weekly restore drill on staging, and `:ro` mounts for Nginx config. Next incident, a bad deploy was rolled back in 5 minutes and no data was lost.

## 🟡 Real Example Hindi mein
एक e-commerce company एक EC2 box पर Docker में Postgres चलाती थी। एक साथी ने `./pgdata:/var/lib/postgresql/data` (bind mount) use किया और बाद में repo folder हिलाया; DB "reset" हो गया। Post-mortem के बाद उन्होंने अपनाया: named volume `pgdata`, label `keep=true`, रात को S3 पर `pg_dump`, staging पर हफ्तेवार restore drill, और Nginx config के लिए `:ro` mounts। अगली बार bad deploy 5 मिनट में rollback हुआ और कोई data नहीं गया।

---

## 💻 Code / Config Example — Basic
```yaml
# docker-compose.yml - minimal, correct volume usage
services:
  db:
    image: postgres:16-alpine                 # example tag; pin and update deliberately
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_pw  # read password from a file, not plain env
    secrets:
      - db_pw                                 # attach the secret defined below
    volumes:
      - pgdata:/var/lib/postgresql/data       # NAMED volume: survives container recreation
secrets:
  db_pw:
    file: ./secrets/db_pw.txt                 # file kept out of git (.gitignore)
volumes:
  pgdata: {}                                  # declare the named volume
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.prod.yml - production-grade volume practices
services:
  api:
    image: myorg/api:1.4.2                    # example immutable tag, never :latest in prod
    user: "1000:1000"                         # run as non-root so files are not root-owned
    read_only: true                           # container filesystem is read-only
    tmpfs:
      - /tmp                                  # writable scratch space in RAM only
    volumes:
      - uploads:/app/uploads                  # the ONE writable persistent path
      - ./config/app.json:/app/config.json:ro # config mounted read-only
    restart: unless-stopped                   # come back after reboot
  nginx:
    image: nginx:1.27-alpine                  # example tag
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro  # read-only config
      - static:/usr/share/nginx/html:ro       # static files shared from build, read-only
    ports:
      - "80:80"                               # public HTTP
volumes:
  uploads:
    labels:
      keep: "true"                            # protect from prune scripts
  static: {}                                  # rebuilt each release, safe to lose
```

```dockerfile
# Dockerfile snippet - make the volume path writable for a non-root user
FROM node:20-alpine                           # example base image
WORKDIR /app                                  # app directory
RUN mkdir -p /app/uploads \
    && chown -R node:node /app/uploads        # give node user (uid 1000) ownership BEFORE volume is mounted
USER node                                     # drop root privileges
COPY --chown=node:node . .                    # copy code with right owner
CMD ["node", "server.js"]                     # start the app
```

---

## 🟠 My Stack Integration
- **Node.js API:** uploads in a named volume, or better in S3 so the container is fully stateless and horizontally scalable.
- **FastAPI:** same; mount ML model files read-only (`models:/models:ro`).
- **React:** build output goes into the Nginx image (multi-stage), no volume in production. In dev, a bind mount gives hot reload.
- **Nginx:** config and certificates mounted `:ro`; Let's Encrypt certs in a named volume `certs`.
- **VPS/AWS:** put `/var/lib/docker` on a separate EBS disk, snapshot it daily, or prefer RDS/Atlas for databases and keep Docker volumes for cache only.

```bash
# nightly backup of a named volume to S3 (aws cli configured on the VPS)
docker run --rm -v pgdata:/data:ro -v "$PWD":/backup alpine \
  tar czf /backup/pgdata-$(date +%F).tgz -C /data .   # archive volume read-only
aws s3 cp pgdata-$(date +%F).tgz s3://my-backups/pg/   # ship off-box
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Relying on anonymous volumes (a hash name) for databases.
✅ Correct: Always name the volume so you can find, back up and protect it.

❌ Mistake 2: Bind-mounting source code in production.
✅ Correct: Bake code into the image; bind mounts are for local development only.

❌ Mistake 3: Running as root and getting permission-denied or root-owned files on the host.
✅ Correct: Use a non-root `USER`, `chown` the path in the image, or set `user:` in Compose.

❌ Mistake 4: Storing secrets, `.env` or private keys in a shared volume.
✅ Correct: Use Docker/Compose secrets or AWS Secrets Manager; mount `:ro` if a file is needed.

❌ Mistake 5: No backup test. 
✅ Correct: Schedule a restore drill and alert if the backup file size drops suddenly.

---

## 🧠 Tricky Interview Question
**Q:** Your API container writes user uploads to `/app/uploads`. You scale to 3 replicas behind Nginx using a local named volume. Users report images randomly missing. Why, and how do you fix it?

**Answer:** Local named volumes are per-host (and per-container if mounted in each replica separately). Each replica writes to its own volume, so a file uploaded via replica A is invisible to replica B. Fix: store uploads in shared object storage (S3), or use a network filesystem (EFS/NFS) via a volume driver. Best practice is to keep app containers stateless and push state to S3/RDS.

---

## ⚫ Interview Questions + Answers

Q1: Named volume vs bind mount, which for production data?
A1: Named volume (managed by Docker, portable, easy backup). Bind mounts depend on host paths and permissions.

Q2: Why mount configs as read-only?
A2: Least privilege. A compromised process cannot modify config or code.

Q3: What does `read_only: true` plus `tmpfs` achieve?
A3: Immutable container filesystem; only listed paths are writable, which limits malware persistence.

Q4: Should databases run in Docker volumes on production?
A4: Possible for small setups with backups; for critical data prefer managed services (RDS, Atlas) for replication and PITR.

Q5: How do you handle volume permission errors?
A5: Match UID/GID of the container user with the volume owner, use `chown` in the Dockerfile, or `user:` in Compose.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need data to outlive containers (databases, uploads, certs)
- Sharing read-only assets between containers
- You want easy backup and migration with `docker run ... tar`

❌ Avoid when:
- Data is temporary (use `tmpfs`)
- Multi-host scaling needs shared storage (use S3/EFS instead of local volumes)
- Secrets (use secrets mechanisms)

---

## 📊 Visual Diagram
```
        +-------------------- Docker host (VPS) --------------------+
        |                                                           |
        |  [nginx]--(:ro)-->  static vol, nginx.conf                |
        |                                                           |
        |  [api: non-root, read_only]                               |
        |      |-- /tmp ........ tmpfs (RAM, gone on stop)          |
        |      |-- /app/uploads  named vol "uploads" (keep=true)    |
        |                                                           |
        |  [db]--> named vol "pgdata" ---> nightly tar ---> S3      |
        +-----------------------------------------------------------+
   Rule: code in IMAGE, state in VOLUME/S3, secrets in SECRET store
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Stateless | Container keeps no data inside | बिना data रखने वाला container |
| Named volume | Volume managed by Docker with a name | नाम वाली volume |
| Read-only mount | Mount that cannot be modified | केवल-पढ़ने वाला mount |
| tmpfs | In-memory temporary filesystem | RAM में अस्थायी storage |
| Least privilege | Give only needed access | कम से कम अधिकार |
| Restore drill | Practice restoring from backup | backup से वापसी का अभ्यास |

---

## ⚡ 3-Line Summary
English: Keep containers stateless; put state in named volumes or managed services.
Mount read-only, run non-root, never store secrets in volumes.
Back up, label, and test restores regularly.
Hindi: Containers को stateless रखो; state named volumes या managed services में रखो।
Read-only mount, non-root user, और secrets कभी volume में नहीं।
Backup लो, label लगाओ और restore का test करते रहो।

---

## ➡️ Next Topic
**166. Docker Networking — Complete Guide** - volumes handle storage; next we learn how containers talk to each other and the outside world.
