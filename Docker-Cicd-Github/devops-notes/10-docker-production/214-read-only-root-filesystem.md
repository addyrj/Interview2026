# 214. Read-Only Root Filesystem
# हिंदी में: Read-Only Root Filesystem (container का filesystem बदलने से रोकना)

---

## 🔵 Simple Definition (English)
A read-only root filesystem mounts the container's `/` as read-only (`docker run --read-only` or `read_only: true` in Compose). The app cannot create or change files except in explicitly allowed places such as `tmpfs` mounts or named volumes.

## 🔵 सरल परिभाषा (Hindi)
Read-only root filesystem में container का `/` read-only mount होता है (`docker run --read-only` या Compose में `read_only: true`)। App सिर्फ उन जगहों पर लिख सकती है जो साफ़ तौर पर अनुमति वाली हों, जैसे `tmpfs` mounts या named volumes।

---

## 🔴 Problem it Solves
After exploiting an app, attackers download tools (`curl` a miner, a reverse shell), drop scripts into `/tmp` or `/usr/bin`, and edit config files to persist. If the filesystem cannot be written, these steps fail. It also forces a clean design: all state lives in volumes, so containers are truly disposable.

## 🔴 यह क्यों बना? (Hindi)
App exploit करने के बाद attackers tools download करते हैं (miner, reverse shell), `/tmp` या `/usr/bin` में scripts डालते हैं और config files बदलकर टिके रहते हैं। Filesystem writable न हो तो ये steps fail हो जाते हैं। यह साफ़ design भी मजबूर करता है: सारा state volumes में रहता है, इसलिए containers सचमुच disposable होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Add read_only: true to the service (or --read-only to docker run)
Step 2 → Docker mounts the image layers + writable layer as read-only
Step 3 → Any write to / returns "Read-only file system" (EROFS)
Step 4 → Find what your app needs to write (logs, pid files, caches, uploads)
Step 5 → Provide tmpfs for temp paths (/tmp, /run) and named volumes for persistent data
Step 6 → Test: the app starts, serves requests, shuts down without errors
Step 7 → Keep it on: any new write location becomes a visible error, not a silent change
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Service में read_only: true जोड़ें (या docker run में --read-only)
Step 2 → Docker image layers + writable layer को read-only mount करता है
Step 3 → / में कोई भी write "Read-only file system" (EROFS) देता है
Step 4 → पता करें app को क्या लिखना है (logs, pid files, caches, uploads)
Step 5 → अस्थायी paths (/tmp, /run) के लिए tmpfs और स्थायी data के लिए named volumes दें
Step 6 → जाँचें: app चालू होती है, requests देती है, बिना errors के बंद होती है
Step 7 → इसे चालू रखें: नई write जगह अब चुपचाप बदलाव नहीं, दिखने वाला error बनेगी
```

---

## 🟡 Real World Example
A SaaS runs a Node API that renders PDF invoices with a headless browser. After a dependency CVE, an attacker tried to write `/app/node_modules/.hooks/run.sh` to persist across restarts. On the hardened deployment (`read_only: true`, tmpfs for `/tmp`) the write failed with EROFS, the attempt showed in logs, and the alert fired. Restarting the container also returned it to a known-good state automatically.

## 🟡 Real Example Hindi mein
एक SaaS headless browser से PDF invoices बनाने वाली Node API चलाता है। Dependency CVE के बाद attacker ने restarts के बीच टिकने के लिए `/app/node_modules/.hooks/run.sh` लिखने की कोशिश की। Hardened deployment (`read_only: true`, `/tmp` के लिए tmpfs) में write EROFS से fail हुई, कोशिश logs में दिखी और alert चला। Container restart करने से भी वह अपने-आप known-good state में लौट आता है।

---

## 💻 Code / Config Example — Basic
```bash
# docker run with a read-only root filesystem
# --read-only mounts / read-only; --tmpfs /tmp allows a RAM-backed /tmp;
# -p 127.0.0.1:3000:3000 publishes only on localhost; myapp-api:1.0 is an example image
docker run -d --name api --read-only --tmpfs /tmp -p 127.0.0.1:3000:3000 myapp-api:1.0
docker exec api sh -c 'touch /x'    # expected: touch: /x: Read-only file system
```

## 💻 Code / Config Example — Advanced
```yaml
# compose.prod.yaml  (read-only root for the whole stack)
services:
  api:                                      # Node.js
    image: ghcr.io/acme/api:${TAG}          # pinned image
    read_only: true                         # immutable root FS
    user: "10001:10001"                     # non-root (topic 213)
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=64m      # temp files in RAM; noexec blocks running dropped binaries
    volumes:
      - uploads:/app/uploads                # only this folder is persistent and writable
    cap_drop: ["ALL"]
    security_opt: ["no-new-privileges:true"]
  fastapi:                                  # Python
    image: ghcr.io/acme/ml:${TAG}
    read_only: true
    environment:
      PYTHONDONTWRITEBYTECODE: "1"          # do not write .pyc (would fail on read-only FS)
      HF_HOME: /tmp/hf                      # example: caches redirected to tmpfs
    tmpfs: ["/tmp:rw,noexec,nosuid,size=128m"]
  nginx:                                    # Nginx needs several writable dirs
    image: nginx:1.27-alpine
    read_only: true
    tmpfs:
      - /var/cache/nginx                    # proxy/body temp files
      - /var/run                            # pid file
      - /tmp                                # misc temp
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
  postgres:                                 # databases need data dir + run dirs
    image: postgres:16-alpine
    read_only: true
    tmpfs: ["/tmp", "/var/run/postgresql"]  # socket + temp files
    volumes:
      - pgdata:/var/lib/postgresql/data     # data volume stays writable
  redis:
    image: redis:7-alpine
    read_only: true
    volumes: ["redisdata:/data"]            # AOF/RDB files
volumes:
  uploads: {}
  pgdata: {}
  redisdata: {}
```
Find write needs before enabling: `docker diff <container>` lists files the app changed in its writable layer (A=added, C=changed).

---

## 🟠 My Stack Integration
- **Node.js:** disable writes to `node_modules`; put temp files in `os.tmpdir()` (/tmp). Some libs write caches to `$HOME`: set `HOME=/tmp`.
- **FastAPI:** `PYTHONDONTWRITEBYTECODE=1`; model/pip caches to `/tmp`; uvicorn itself writes nothing.
- **React/Nginx:** use tmpfs for `/var/cache/nginx`, `/var/run`, `/tmp` (or the `nginx-unprivileged` image).
- **VPS/AWS:** ECS task definitions have `readonlyRootFilesystem: true`; Kubernetes uses `securityContext.readOnlyRootFilesystem: true`. Same concept.
- **Security:** combine with non-root, `cap_drop`, and `noexec` tmpfs to stop dropped binaries from running.

```bash
# discover what your app writes (run with a normal container first)
docker run -d --name probe myapp-api:1.0           # normal writable run
sleep 20; curl -s localhost:3000/health >/dev/null # exercise the app
docker diff probe                                  # lists changed paths -> these need tmpfs/volumes
docker rm -f probe                                 # cleanup
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Enabling `read_only` without tmpfs; the app crashes on first temp file write.
✅ Correct: Add `tmpfs` for `/tmp` and the specific directories reported by `docker diff` / errors.

❌ Mistake 2: Making the whole app directory a writable volume "just to make it work".
✅ Correct: Make only the specific upload/data folder writable.

❌ Mistake 3: Believing read-only means no volumes can be written. Volumes and tmpfs mounts stay writable.
✅ Correct: Mount volumes as `:ro` too when the app only needs to read them.

❌ Mistake 4: Using read-only as the only defence.
✅ Correct: Layer it with non-root, dropped caps, seccomp, and network limits.

---

## 🧠 Tricky Interview Question
The container is `read_only: true` but you can still write to `/tmp`. Did read-only fail?

Answer: No. `/tmp` is a `tmpfs` mount (or a volume) and mounts are independent of the root filesystem flag. That is intentional: you whitelist exactly the writable places. If `/tmp` should not allow executables add `noexec,nosuid`. If you find `/tmp` writable without having configured it, check for an image with a VOLUME instruction on that path, because VOLUME creates a writable anonymous volume.

---

## ⚫ Interview Questions + Answers

Q1: What error does an app see?
A1: `EROFS: read-only file system` (errno 30).

Q2: tmpfs vs volume for writable paths?
A2: tmpfs lives in RAM and is wiped on stop (good for temp, sockets, pid). Volumes persist (good for uploads, DB data).

Q3: Does read-only stop all attacks?
A3: No. Memory-only malware, network attacks and writes to volumes are still possible; it limits persistence and tool dropping.

Q4: How do you find out what to allow?
A4: Run once normally, use `docker diff`, check startup errors, and test every code path including log files and uploads.

Q5: How does Kubernetes express this?
A5: `securityContext.readOnlyRootFilesystem: true` with `emptyDir` volumes for writable paths.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Stateless web/API containers (Node, FastAPI, Nginx).
- Compliance baselines (CIS Docker Benchmark recommends it).

❌ Avoid when:
- Legacy apps writing to many unknown paths (first refactor).
- Dev containers where you install packages interactively.

---

## 📊 Visual Diagram
```
 +-------------------- container --------------------+
 |  / (root FS)  READ-ONLY   <-- app write = EROFS     |
 |    /usr /bin /app /etc   (image layers)             |
 |                                                     |
 |  /tmp   tmpfs (RAM, noexec)   writable, temporary   |
 |  /app/uploads  named volume   writable, persistent  |
 +-----------------------------------------------------+
 Attacker: curl malware > /usr/bin/x   ->  FAILS
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| read-only FS | Root cannot be written | लिखा न जा सकने वाला root FS |
| tmpfs | RAM-backed temporary mount | RAM आधारित अस्थायी mount |
| EROFS | Read-only filesystem error | read-only filesystem error |
| noexec | Block executing files on a mount | mount पर चलाना रोकना |
| `docker diff` | Show changed files | बदली files दिखाना |
| persistence (attack) | Attacker surviving restarts | attacker का restart के बाद भी टिकना |

---

## ⚡ 3-Line Summary
English: `read_only: true` makes `/` immutable; allow only tmpfs and volumes you need. Discover write paths with `docker diff`. Combine with non-root and dropped capabilities.
Hindi: `read_only: true` `/` को अपरिवर्तनीय बनाता है; सिर्फ ज़रूरी tmpfs और volumes की अनुमति दें। Write paths `docker diff` से खोजें। Non-root और dropped capabilities के साथ मिलाएँ।

---

## ➡️ Next Topic
**215. Dropping Linux Capabilities**: next we remove the root-like powers that processes still carry.
