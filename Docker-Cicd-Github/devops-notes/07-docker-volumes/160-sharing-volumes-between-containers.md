# 160. Sharing Volumes Between Containers
# हिंदी में: Containers के बीच Volumes Share करना

---

## 🔵 Simple Definition (English)
Sharing a volume means mounting the same named volume into two or more containers so they see the same files. One container may write (producer) while others read (consumers), for example an app writing static files and Nginx serving them, or a backup job reading a database volume.

## 🔵 सरल परिभाषा (Hindi)
Volume share करने का मतलब है एक ही named volume को दो या ज़्यादा containers में mount करना ताकि वे वही files देखें। एक container लिख सकता है (producer) और बाकी पढ़ सकते हैं (consumers), जैसे app static files लिखे और Nginx उन्हें serve करे, या backup job database volume को पढ़े।

---

## 🔴 Problem it Solves
- Containers are isolated; one cannot read another's filesystem. Without sharing you would copy files with `docker cp` or bake them into images.
- Patterns like sidecar (log shipper), shared uploads, certificate renewal (certbot + nginx) and backup jobs all need a common directory.
- `volumes_from` and named volumes give a clean, declarative way to do it.

## 🔴 यह क्यों बना? (Hindi)
- Containers isolated होते हैं; एक दूसरे का filesystem नहीं पढ़ सकता। Sharing के बिना `docker cp` करना पड़ता या files को image में डालना पड़ता।
- Sidecar (log shipper), shared uploads, certificate renewal (certbot + nginx) और backup jobs, सबको एक common directory चाहिए।
- `volumes_from` और named volumes यह काम साफ़ और declarative तरीके से करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Declare one named volume (shared_static).
Step 2 → Mount it in container A (writer) at /app/static.
Step 3 → Mount the SAME volume in container B (reader) at /usr/share/nginx/html/static, read-only (:ro).
Step 4 → Both mounts point to the same host folder: /var/lib/docker/volumes/shared_static/_data.
Step 5 → A writes a file → B sees it immediately (same files on disk, no copy).
Step 6 → Rule: only ONE writer for a given file/DB, or use locking; many readers are fine.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → एक named volume declare करो (shared_static)।
Step 2 → उसे container A (writer) में /app/static पर mount करो।
Step 3 → वही volume container B (reader) में /usr/share/nginx/html/static पर read-only (:ro) mount करो।
Step 4 → दोनों mounts एक ही host folder पर इशारा करते हैं: /var/lib/docker/volumes/shared_static/_data।
Step 5 → A file लिखता है → B को तुरंत दिखती है (वही files, कोई copy नहीं)।
Step 6 → नियम: किसी file/DB के लिए सिर्फ एक writer रखो, या locking करो; कई readers ठीक हैं।
```

---

## 🟡 Real World Example
A Django/FastAPI shop runs `collectstatic` at startup into a shared volume `static`. Nginx mounts the same volume read-only and serves `/static/` directly, so Python never handles image or CSS requests. Separately, a `certbot` container writes certificates to the `letsencrypt` volume and Nginx reads them; renewals reload Nginx with no rebuild.

## 🟡 Real Example Hindi mein
एक Django/FastAPI shop startup पर `collectstatic` को shared volume `static` में चलाता है। Nginx वही volume read-only mount करके `/static/` सीधे serve करता है, इसलिए Python को image या CSS requests छूनी ही नहीं पड़तीं। अलग से, `certbot` container certificates `letsencrypt` volume में लिखता है और Nginx उन्हें पढ़ता है; renewal पर Nginx reload होता है, rebuild नहीं।

---

## 💻 Code / Config Example — Basic
```bash
# two containers, one volume
docker volume create shared                       # create the shared volume

docker run -d --name writer \
  -v shared:/out \
  alpine sh -c 'while true; do date >> /out/log.txt; sleep 2; done'   # appends a line every 2s

docker run --rm --name reader \
  -v shared:/in:ro \
  alpine tail -n 3 /in/log.txt                    # reads the same file; :ro prevents writes

# older alternative: reuse mounts of another container
docker run --rm --volumes-from writer alpine ls /out   # inherits ALL volumes of "writer"

docker rm -f writer && docker volume rm shared    # clean up
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - app writes static files, nginx serves them, certbot + backup share volumes
services:
  api:
    image: myorg/shop-api:1.0.0              # example tag
    command: sh -c "cp -r /app/build/static/. /shared/static/ && node server.js"   # publish assets then start
    volumes:
      - static:/shared/static                # WRITER: read-write mount
      - uploads:/app/uploads                 # user uploads (single writer: api)
    networks: [frontend, backend]
  nginx:
    image: nginx:1.27                        # example tag
    ports: ["80:80", "443:443"]
    depends_on: [api]                        # start after api
    volumes:
      - static:/usr/share/nginx/html/static:ro   # READER: read-only
      - uploads:/usr/share/nginx/html/uploads:ro # READER: serve uploads, cannot modify them
      - letsencrypt:/etc/letsencrypt:ro      # certs read-only
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro   # config from repo
    networks: [frontend]
  certbot:
    image: certbot/certbot:latest            # example; pin in production
    volumes:
      - letsencrypt:/etc/letsencrypt         # certbot WRITES certs here
      - certbot_www:/var/www/certbot         # webroot challenge dir
    entrypoint: /bin/sh -c "trap exit TERM; while :; do certbot renew --webroot -w /var/www/certbot; sleep 12h & wait $${!}; done"
  uploads_backup:
    image: alpine:3.20                       # tiny helper image
    profiles: ["backup"]                     # runs only with: docker compose --profile backup run ...
    volumes:
      - uploads:/data:ro                     # read-only so backup cannot damage data
      - ./backups:/backup                    # host folder for tarball
    command: tar czf /backup/uploads-$(date +%F).tgz -C /data .   # compress the volume
networks:
  frontend:
  backend:
    internal: true
volumes:
  static:
  uploads:
  letsencrypt:
  certbot_www:
```

---

## 🟠 My Stack Integration
- **React + Nginx**: use a multi-stage build that copies `build/` into the Nginx image. If you must share builds, use a build container that writes into a volume and exits (init pattern).
- **Node.js / FastAPI uploads**: with ONE API container a shared volume works; with 3+ replicas on several VPS machines a local volume does NOT sync, so use S3 or EFS.
- **VPS backup**: run a throwaway container with the DB volume mounted `:ro` and a host path for output (see note 161).
- **AWS**: EFS can be mounted into containers on multiple EC2 instances (NFS), at a latency cost.

```yaml
# nginx.conf snippet that serves the shared volumes
# location /static/  { alias /usr/share/nginx/html/static/;  expires 7d; }   # cache static files
# location /uploads/ { alias /usr/share/nginx/html/uploads/; add_header X-Content-Type-Options nosniff; }
```
Security: mount `:ro` everywhere a container only reads; serve uploads with `nosniff` and never execute them; a compromised reader cannot tamper with data.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Two containers writing the same SQLite/DB file via a shared volume.
✅ Correct: One writer. Use a real DB server for concurrent writes.

❌ Mistake 2: Forgetting `:ro` on reader containers.
✅ Correct: Add `:ro` to limit blast radius.

❌ Mistake 3: Assuming a volume is shared across different servers.
✅ Correct: Local volumes exist on one host only. Use S3/EFS/NFS for multi-host.

❌ Mistake 4: Permission mismatch (writer runs as uid 1000, reader as root with `:ro` is fine, but another writer as uid 999 fails).
✅ Correct: Align uid/gid via `user:` or `chown` in an init step (note 162).

❌ Mistake 5: Relying on Docker to populate the volume from an image for a second container.
✅ Correct: Docker copies image contents into an EMPTY named volume only at first mount; later image updates will not refresh it. Re-sync explicitly on each deploy.

---

## 🧠 Tricky Interview Question
Your React build is copied into a named volume `web` at first deploy and Nginx serves it. After you ship a new image, users still see the old site. Why?

Answer: Docker initializes a named volume from the image path only when the volume is empty. On later deploys the volume already contains old files, so the new image content is hidden by the volume. Fixes: bake the build into the Nginx image (no volume), delete the volume on deploy, or copy files explicitly on container start.

---

## ⚫ Interview Questions + Answers

Q1: How do you share data between containers?
A1: Mount the same named volume (or bind-mount path) in each, or use `--volumes-from` / Compose `volumes:`.

Q2: What does `--volumes-from` do?
A2: Mounts all volumes of another container at the same paths into the new one. Handy for backup helpers.

Q3: Is concurrent writing safe?
A3: Not automatically. The kernel allows it but your app must handle locking; use a database for concurrent writes.

Q4: Volume vs network for sharing data?
A4: Volume shares files on one host; network (HTTP/gRPC/queue) shares data across hosts and is better for services.

Q5: How do you share across hosts?
A5: NFS/EFS volume driver options, S3 via SDK, or a distributed file system.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Static assets / uploads between app and Nginx on one host.
- Sidecar log shipping, certificate sharing, backup helpers.

❌ Avoid when:
- Several hosts or autoscaling groups are involved.
- High-concurrency writes to the same file.

---

## 📊 Visual Diagram
```
  +---------------+  rw   +---------------------+   ro  +---------------+
  | api (writer)  |------>|  VOLUME "static"    |<------| nginx (reader)|
  | /shared/static|       |  /var/lib/docker/   |       | /usr/share/   |
  +---------------+       |  volumes/static/_data|      | nginx/html/   |
                          +----------^----------+       +---------------+
                                     | ro
                          +----------+----------+
                          | backup helper       |
                          +---------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| volumes_from | Reuse another container's mounts | दूसरे container के mounts reuse करना |
| Sidecar | Helper container beside the main one | मुख्य container के साथ helper |
| :ro | Read-only mount flag | सिर्फ पढ़ने वाला mount |
| Producer/Consumer | Writer and reader of shared data | लिखने वाला/पढ़ने वाला |
| EFS | AWS shared network file system | AWS का shared file system |
| Webroot | Folder used for ACME challenge | ACME challenge का folder |

---

## ⚡ 3-Line Summary
English: Mount the same named volume in many containers to share files on one host.
Give readers `:ro`, keep a single writer, and remember volumes do not cross hosts.
Named volumes are filled from an image only when empty, so redeploy assets explicitly.
Hindi: एक ही named volume कई containers में mount करके एक host पर files share करो।
Readers को `:ro` दो, writer एक रखो, और याद रखो कि volumes hosts के पार नहीं जाते।
Named volume image से सिर्फ खाली होने पर भरता है, इसलिए assets को deploy पर खुद sync करो।

---

## ➡️ Next Topic
161. Volume Backup + Restore: how to safely copy a volume to a tarball or S3 and bring it back.
