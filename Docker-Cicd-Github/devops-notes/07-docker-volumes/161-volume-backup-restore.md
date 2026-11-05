# 161. Volume Backup + Restore
# हिंदी में: Volume Backup और Restore

---

## 🔵 Simple Definition (English)
Volume backup means copying the contents of a Docker volume to a safe place (tar file, S3, another server), and restore means putting it back into a (new) volume. Docker has no built-in `docker volume backup` command, so you use a temporary helper container that mounts the volume and runs `tar`, or use app-level tools like `pg_dump`.

## 🔵 सरल परिभाषा (Hindi)
Volume backup का मतलब है Docker volume की contents को सुरक्षित जगह (tar file, S3, दूसरा server) पर copy करना, और restore का मतलब उसे (नए) volume में वापस रखना। Docker में `docker volume backup` जैसा built-in command नहीं है, इसलिए एक temporary helper container volume mount करके `tar` चलाता है, या `pg_dump` जैसे app-level tools इस्तेमाल होते हैं।

---

## 🔴 Problem it Solves
- A volume survives container deletion but not disk failure, human error (`down -v`), ransomware or a bad migration.
- Volume data lives in `/var/lib/docker/volumes`, owned by root and internal to Docker; copying it by hand is fragile.
- Teams need repeatable, scheduled, tested restores (RPO/RTO). A backup never restored is only a hope.

## 🔴 यह क्यों बना? (Hindi)
- Volume container delete होने पर बचता है, लेकिन disk failure, human error (`down -v`), ransomware या खराब migration से नहीं।
- Volume data `/var/lib/docker/volumes` में root के अधीन है और Docker का internal हिस्सा है; हाथ से copy करना नाज़ुक है।
- Teams को दोहराने योग्य, scheduled और tested restores चाहिए (RPO/RTO)। जो backup कभी restore नहीं हुआ वो सिर्फ उम्मीद है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → (Databases) Prefer logical dump: pg_dump / mysqldump / mongodump -> consistent file.
Step 2 → (Files) Start a helper container: mount volume read-only at /data and a host dir at /backup.
Step 3 → Helper runs: tar czf /backup/<name>-<date>.tgz -C /data .
Step 4 → Copy tarball off the host: aws s3 cp ... (encrypted bucket, lifecycle rule).
Step 5 → RESTORE: create a NEW empty volume, mount it in a helper, extract the tarball into it.
Step 6 → Start the app container on the restored volume and run a smoke test.
Step 7 → Schedule with cron / systemd timer and test the restore monthly.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → (Databases) Logical dump बेहतर: pg_dump / mysqldump / mongodump -> consistent file।
Step 2 → (Files) Helper container चलाओ: volume को /data पर read-only और host dir को /backup पर mount।
Step 3 → Helper चलाता है: tar czf /backup/<name>-<date>.tgz -C /data .
Step 4 → Tarball को host से बाहर भेजो: aws s3 cp ... (encrypted bucket, lifecycle rule)।
Step 5 → RESTORE: नया खाली volume बनाओ, helper में mount करो, tarball extract करो।
Step 6 → Restored volume पर app container चलाओ और smoke test करो।
Step 7 → cron / systemd timer से schedule करो और हर महीने restore test करो।
```

---

## 🟡 Real World Example
A startup's VPS disk was corrupted at 3 AM. Because a nightly cron ran `pg_dump | gzip | aws s3 cp` and kept 14 days, they launched a fresh EC2, installed Docker, pulled the image, restored the latest dump in 6 minutes and lost under 24 hours of data. A competitor without tested backups spent three days rebuilding from application logs.

## 🟡 Real Example Hindi mein
एक startup के VPS की disk रात 3 बजे corrupt हो गई। क्योंकि nightly cron `pg_dump | gzip | aws s3 cp` चलाता था और 14 दिन रखता था, उन्होंने नया EC2 बनाया, Docker install किया, image pull की और latest dump 6 मिनट में restore कर दिया, 24 घंटे से कम का data गया। बिना tested backup वाला competitor तीन दिन application logs से rebuild करता रहा।

---

## 💻 Code / Config Example — Basic
```bash
# ---------- BACKUP a volume to a tarball in the current folder ----------
docker run --rm \
  -v pgdata:/data:ro \
  -v "$(pwd)":/backup \
  alpine:3.20 \
  tar czf /backup/pgdata-$(date +%F).tgz -C /data .
# --rm            : delete helper when done
# -v pgdata:/data:ro : source volume, read-only so we cannot damage it
# -v $(pwd):/backup  : host folder where the tarball is written
# tar czf ... -C /data . : create gzip tar of the volume contents

# ---------- RESTORE into a NEW volume ----------
docker volume create pgdata_restored             # new empty volume
docker run --rm \
  -v pgdata_restored:/data \
  -v "$(pwd)":/backup:ro \
  alpine:3.20 \
  tar xzf /backup/pgdata-2026-11-04.tgz -C /data  # extract into the volume (use your real file name)
```

## 💻 Code / Config Example — Advanced
```bash
#!/usr/bin/env bash
# backup-prod.sh - nightly backup of Postgres + uploads volume to S3 (example; test before use)
set -euo pipefail                                # fail fast on any error
STAMP=$(date +%F-%H%M)                           # timestamp for file names
DEST=/var/backups/docker                         # local staging dir on the VPS
BUCKET=s3://my-company-backups/orders            # example bucket (versioning + SSE enabled)
mkdir -p "$DEST"                                 # create staging dir if missing

# 1) Logical DB dump from the running container: consistent, small, portable
docker exec -t orders-db pg_dump -U app -d appdb -Fc \
  > "$DEST/appdb-$STAMP.dump"                    # -Fc = custom compressed format for pg_restore

# 2) Uploads volume as tarball using a throwaway helper
docker run --rm \
  -v orders_uploads:/data:ro \
  -v "$DEST":/backup \
  alpine:3.20 \
  tar czf "/backup/uploads-$STAMP.tgz" -C /data .

# 3) Verify archive readable (cheap integrity check)
tar tzf "$DEST/uploads-$STAMP.tgz" > /dev/null   # lists files, fails if corrupt
pg_restore --list "$DEST/appdb-$STAMP.dump" > /dev/null 2>&1 || docker run --rm -v "$DEST":/b postgres:16 pg_restore --list "/b/appdb-$STAMP.dump" > /dev/null   # verify dump

# 4) Upload encrypted at rest (SSE) and remove local copies older than 3 days
aws s3 cp "$DEST/appdb-$STAMP.dump"  "$BUCKET/" --sse AES256
aws s3 cp "$DEST/uploads-$STAMP.tgz" "$BUCKET/" --sse AES256
find "$DEST" -type f -mtime +3 -delete           # keep local disk small

# 5) Heartbeat so monitoring alerts if backup stops running
curl -fsS -m 10 https://hc-ping.com/YOUR-UUID > /dev/null   # healthchecks.io style (example)

# ---- restore drill (run on a test host) ----
# docker volume create pgdata_test
# docker run -d --name pgtest -v pgdata_test:/var/lib/postgresql/data -e POSTGRES_PASSWORD=x postgres:16
# docker exec -i pgtest pg_restore -U postgres -d postgres --create < appdb-<stamp>.dump
# crontab -e:  15 2 * * *  /opt/scripts/backup-prod.sh >> /var/log/backup.log 2>&1
```

---

## 🟠 My Stack Integration
- **Postgres (Node.js / FastAPI)**: nightly `pg_dump -Fc`, weekly full volume tar, plus EBS snapshots (AWS Backup) of the VPS.
- **MongoDB**: `mongodump --archive --gzip`.
- **Nginx certs volume**: tar once after issuing; renewal recreates anyway.
- **React**: nothing to back up; it is rebuilt from Git by CI.
- **AWS**: S3 with versioning, SSE and lifecycle (Glacier after 30 days); an IAM role on the EC2 instead of access keys.

```yaml
# compose "backup" service that runs on demand: docker compose --profile backup run --rm backup
services:
  backup:
    image: postgres:16                       # contains pg_dump
    profiles: ["backup"]                     # does not start with normal "up"
    depends_on: [db]                         # needs DB reachable
    environment:
      PGPASSWORD_FILE: /run/secrets/pg_pw    # note: pg_dump reads PGPASSFILE, adapt to your secret handling
    volumes:
      - ./backups:/backups                   # output folder on host
    entrypoint: ["sh", "-c", "PGPASSWORD=$(cat /run/secrets/pg_pw) pg_dump -h db -U app -Fc appdb > /backups/appdb-$(date +%F).dump"]
    secrets: [pg_pw]                         # mount secret
```
Security: encrypt backups (S3 SSE-KMS), restrict bucket IAM to write-only for the server, never put DB passwords on the command line (they show in `ps`).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Tar-ing a live database volume and assuming it is consistent.
✅ Correct: Use `pg_dump`, or stop the DB container first, or use snapshots with DB flush.

❌ Mistake 2: Never testing restore.
✅ Correct: Schedule a monthly restore drill to a scratch host and record the time taken.

❌ Mistake 3: Keeping backups only on the same disk/host.
✅ Correct: 3-2-1 rule: 3 copies, 2 media, 1 off-site (S3 in another region).

❌ Mistake 4: Restoring into the live volume without a pre-restore copy.
✅ Correct: Restore to a new volume, verify, then switch the container to it.

❌ Mistake 5: Losing file ownership/permissions when extracting.
✅ Correct: Extract as root inside the helper with `tar xzf` (preserves uid/gid and modes by default for root) and keep the same image user afterwards.

---

## 🧠 Tricky Interview Question
You backed up a Postgres volume with `tar` while the DB was running. Restore works but Postgres reports "database system was not properly shut down" and sometimes corruption. Why?

Answer: A file-level copy of a running database captures files at different moments, so the data files and WAL may be inconsistent. Postgres tries crash recovery using WAL and may succeed, but there is no guarantee. Correct approaches: `pg_dump` (logical, consistent snapshot via MVCC), `pg_basebackup` (physical, consistent), stop the DB before tar, or take an atomic volume/EBS snapshot with `pg_backup_start`/`pg_backup_stop` (version names differ: older `pg_start_backup`).

---

## ⚫ Interview Questions + Answers

Q1: Is there a `docker volume backup` command?
A1: No (Docker Desktop has a Volumes Backup extension, but the CLI does not). Use a helper container with `tar`, or DB tools.

Q2: Why mount the source volume read-only during backup?
A2: To guarantee the backup process cannot modify or delete production data.

Q3: Logical vs physical backup?
A3: Logical (`pg_dump`) exports SQL/objects: portable across versions, slower to restore. Physical (files, `pg_basebackup`) copies disk files: fast, same major version only.

Q4: What are RPO and RTO?
A4: RPO = how much data you can lose (time between backups). RTO = how long recovery may take.

Q5: How to automate?
A5: cron or systemd timer on the host, or a scheduled container; ship to S3; alert via heartbeat if it did not run.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any volume holding data you cannot recreate.
- Before upgrades, migrations or risky `compose` changes.

❌ Avoid when:
- Data is a cache (Redis cache-only, build caches).
- You already use managed DB backups (RDS automated snapshots), though a separate logical dump is still wise.

---

## 📊 Visual Diagram
```
 BACKUP                                          RESTORE
 +-----------+  ro   +------------+              +--------------+
 | volume    |------>| helper     |              | new volume   |
 | pgdata    |       | tar czf    |              | pgdata_new   |
 +-----------+       +-----+------+              +------^-------+
                           |                            | tar xzf
                    pgdata-DATE.tgz  ---> S3 -----> +----+-------+
                    (encrypted, versioned)          | helper     |
                                                    +------------+
                                                          |
                                               start app on pgdata_new, smoke test
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Helper container | Short-lived container doing a task | अस्थायी काम करने वाला container |
| tar | Archive tool | files को archive करने का tool |
| RPO | Max tolerable data loss time | कितना data खो सकते हैं |
| RTO | Max tolerable recovery time | कितनी देर में recover करना है |
| Snapshot | Atomic disk copy | एक साथ ली गई disk copy |
| 3-2-1 rule | 3 copies, 2 media, 1 off-site | 3 copies, 2 media, 1 बाहर |

---

## ⚡ 3-Line Summary
English: Back up volumes with a throwaway tar container or, for databases, with dump tools.
Store copies off-host, encrypted, and restore into a new volume to verify.
An untested backup is not a backup.
Hindi: Volumes का backup throwaway tar container से लो, databases के लिए dump tools से।
Copies host के बाहर, encrypted रखो, और नए volume में restore करके verify करो।
बिना test किया backup, backup नहीं है।

---

## ➡️ Next Topic
162. Volume Permissions: why restored or shared files sometimes give "permission denied" and how uid/gid fix it.
