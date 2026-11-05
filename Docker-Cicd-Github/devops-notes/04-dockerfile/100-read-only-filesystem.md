# 100. Read-Only Filesystem
# हिंदी में: Read-Only Filesystem

---

## 🔵 Simple Definition (English)
A read-only root filesystem (`docker run --read-only`, compose `read_only: true`) mounts the container's root layer without write permission. The app can write only to explicitly provided writable places such as `tmpfs` or named volumes.

## 🔵 सरल परिभाषा (Hindi)
Read-only root filesystem (`docker run --read-only`, compose में `read_only: true`) में container की root layer बिना write permission के mount होती है। App सिर्फ उन जगहों पर लिख सकती है जो साफ तौर पर writable दी गई हों, जैसे `tmpfs` या named volumes।

---

## 🔴 Problem it Solves
If an attacker gets code execution, the first thing they do is write: drop a backdoor binary, edit app code, change `/etc/hosts`, install a crypto miner. A normal container filesystem is writable, so these persist for the life of the container. With a read-only root, the attacker cannot modify binaries or code, which kills a whole class of attacks and also exposes bugs where apps write logs/temp files to random places.

## 🔴 यह क्यों बना? (Hindi)
अगर attacker को code execution मिल जाए तो वह सबसे पहले लिखता है: backdoor binary डालता है, app code बदलता है, `/etc/hosts` बदलता है, crypto miner install करता है। सामान्य container filesystem writable होता है, इसलिए ये बदलाव container के जीवन भर बने रहते हैं। Read-only root में attacker binaries या code नहीं बदल सकता, जिससे हमलों की एक पूरी category खत्म हो जाती है, और apps के उन bugs का भी पता चलता है जो logs/temp files कहीं भी लिख देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Start container with --read-only (root fs mounted ro)
Step 2 → Any write to / returns "Read-only file system" (EROFS)
Step 3 → Provide --tmpfs /tmp (RAM-backed, wiped on stop)
Step 4 → Provide -v data:/app/data for state that must persist
Step 5 → Find what the app writes (run, read errors, docker diff)
Step 6 → Add only those paths; keep everything else immutable
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Container --read-only के साथ start करो (root fs ro)
Step 2 → / पर कोई भी write "Read-only file system" (EROFS) देता है
Step 3 → --tmpfs /tmp दो (RAM में, stop पर साफ)
Step 4 → जो state बचानी है उसके लिए -v data:/app/data दो
Step 5 → पता करो app क्या लिखती है (run, errors पढ़ो, docker diff)
Step 6 → सिर्फ वही paths जोड़ो; बाकी सब immutable रहने दो
```

---

## 🟡 Real World Example
A hosting company ran customer Node apps. One customer's app had an RCE bug and the attacker tried `curl -o /usr/bin/xmrig ... && chmod +x` to start a miner. Because containers were `read_only: true` with `noexec` tmpfs, the download failed with "Read-only file system" and the executable bit could not be used from `/tmp`. The alert fired and no miner ran.

## 🟡 Real Example Hindi mein
एक hosting company customers के Node apps चलाती थी। एक customer के app में RCE bug था और attacker ने `curl -o /usr/bin/xmrig ... && chmod +x` से miner चलाने की कोशिश की। Containers `read_only: true` और `noexec` tmpfs के साथ थे, इसलिए download "Read-only file system" से fail हुआ और `/tmp` से executable नहीं चल सका। Alert बजा और कोई miner नहीं चला।

---

## 💻 Code / Config Example — Basic

```bash
# Run a container with an immutable root filesystem
# --read-only : root fs is read-only | --tmpfs : writable RAM disk, no exec | -p : publish app port
docker run -d --name api \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  -p 3000:3000 \
  myorg/api:1.0.0

# Prove it works: writing outside the allowed paths fails
docker exec api sh -c 'touch /etc/test'   # -> touch: /etc/test: Read-only file system
docker exec api sh -c 'touch /tmp/ok'     # -> succeeds (tmpfs)

# Find what an app tries to modify (run it WITHOUT --read-only first)
docker diff api                           # A=added C=changed D=deleted paths
```

---

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.yml - hardened stack for a VPS: Nginx + FastAPI + Node worker
services:
  nginx:
    image: nginx:1.27-alpine              # example tag
    read_only: true                       # immutable root fs
    tmpfs:
      - /var/cache/nginx                  # nginx cache dir must be writable
      - /var/run                          # pid file location
      - /tmp                              # temp upload buffers
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro  # config mounted read-only
    ports:
      - "80:80"                           # public HTTP
    cap_drop:
      - ALL                               # drop all capabilities
    cap_add:
      - NET_BIND_SERVICE                  # allow port 80
      - CHOWN                             # nginx entrypoint chowns cache dirs
      - SETUID                            # workers switch user
      - SETGID                            # workers switch group
    security_opt:
      - no-new-privileges:true            # block privilege escalation
    depends_on:
      - api                               # start after the API
    restart: unless-stopped               # restart policy
  api:
    image: myorg/fastapi:1.0.0            # FastAPI image (non-root, see topic 99)
    read_only: true                       # immutable root fs
    user: "10001:10001"                   # non-root
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=64m    # temp files only in RAM, no executables
    volumes:
      - uploads:/app/data                 # only persistent writable path
    environment:
      PYTHONDONTWRITEBYTECODE: "1"        # do not write .pyc to the read-only fs
    cap_drop:
      - ALL                               # no capabilities needed
    security_opt:
      - no-new-privileges:true            # block privilege escalation
    expose:
      - "8000"                            # internal only
    restart: unless-stopped               # restart policy
volumes:
  uploads: {}                             # persistent user uploads
```

Note: the exact capabilities and tmpfs paths Nginx needs vary by image version; test with `docker compose up` and read the logs. This file was not run on the machine where these notes were written.

---

## 🟠 My Stack Integration
**Node.js**: set `NODE_ENV=production`; npm may try to write `~/.npm` (avoid running npm in the container, run `node` directly); give `/tmp` as tmpfs. **FastAPI**: set `PYTHONDONTWRITEBYTECODE=1`; uvicorn/gunicorn need `/tmp` (gunicorn heartbeat file) so use `--worker-tmp-dir /dev/shm`. **Nginx**: needs cache/run/tmp writable. **AWS ECS**: `"readonlyRootFilesystem": true` in the container definition. **Kubernetes**: `securityContext.readOnlyRootFilesystem: true` plus `emptyDir` volumes.

```yaml
# ECS task definition fragment (JSON as YAML-compatible view; adapt to your IaC)
containerDefinitions:
  - name: api                         # container name
    image: myorg/api:1.0.0            # image
    readonlyRootFilesystem: true      # immutable root fs
    user: "10001"                     # non-root
    linuxParameters:
      tmpfs:
        - containerPath: /tmp         # writable temp
          size: 64                    # MiB
```

Security: pair with non-root, dropped capabilities and `noexec` on tmpfs; ship logs to stdout rather than files.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Enabling `--read-only` without `/tmp` and the app crashes at startup.
✅ Correct: Run once without it, use `docker diff` and add tmpfs/volumes for each write path.

❌ Mistake 2: Mounting a whole writable volume at `/app`, defeating the purpose.
✅ Correct: Mount only a small data directory like `/app/data`.

❌ Mistake 3: Believing `read_only` also makes volumes read-only.
✅ Correct: Volumes stay writable unless mounted `:ro`; mount config files `:ro`.

---

## 🧠 Tricky Interview Question
With `--read-only`, can a process still write inside the container? Where?

Answer: Yes, to anything mounted writable: `--tmpfs` paths, named volumes, bind mounts (without `:ro`). Also Docker itself manages `/etc/hosts`, `/etc/resolv.conf` and `/etc/hostname` as bind mounts which remain writable-ish for the runtime. Read-only applies to the image layer/root fs only, not to these explicit mounts. Hence you design the writable surface deliberately.

---

## ⚫ Interview Questions + Answers

Q1: What does `--read-only` change?
A1: The container's root filesystem is mounted read-only; writes fail with EROFS.

Q2: tmpfs vs volume?
A2: tmpfs lives in RAM and disappears on stop (temp data); a volume persists on disk.

Q3: How to find which paths an app writes?
A3: `docker diff <container>` on a normal run, `strace`, or read the EROFS errors.

Q4: Why `noexec` on tmpfs?
A4: It stops attackers from running binaries they download into `/tmp`.

Q5: Does read-only protect against all attacks?
A5: No. Memory-only attacks, data theft and attacks via writable volumes remain; it is one layer of defense in depth.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Stateless web/API containers in production.
- Compliance (CIS Docker Benchmark) requires it.

❌ Avoid when:
- Databases or apps that write all over the filesystem (use volumes for their data dirs instead of full ro).
- Local dev with hot reload.

---

## 📊 Visual Diagram
```
  Container
  +-----------------------------------------+
  | / (image layers)         READ-ONLY  X   |  <- attacker cannot write
  |   /usr/bin, /app code                   |
  |-----------------------------------------|
  | /tmp      tmpfs (RAM)    writable, noexec|
  | /app/data volume (disk)  writable        |
  | /etc/hosts etc. runtime-managed          |
  +-----------------------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| EROFS | Read-only file system error | read-only filesystem error |
| tmpfs | RAM-backed temporary filesystem | RAM वाला temp filesystem |
| Volume | Persistent Docker-managed storage | स्थायी storage |
| noexec | Mount option blocking execution | execute रोकने वाला option |
| docker diff | Shows changed files in a container | बदली files दिखाता है |

---

## ⚡ 3-Line Summary
English: Mount the root filesystem read-only and allow writes only to tmpfs and specific volumes.
Find write paths with docker diff.
Combine with non-root, noexec tmpfs and dropped capabilities.
Hindi: Root filesystem read-only रखो और writes सिर्फ tmpfs व चुने volumes पर दो।
Write paths `docker diff` से खोजो।
Non-root, noexec tmpfs और dropped capabilities के साथ जोड़ो।

---

## ➡️ Next Topic
**101. Docker Image Layers**: understand how images are built from layers, which makes size, cache and immutability make sense.
