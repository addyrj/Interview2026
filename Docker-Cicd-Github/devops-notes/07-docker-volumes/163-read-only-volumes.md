# 163. Read-Only Volumes
# हिंदी में: Read-Only Volumes (सिर्फ पढ़ने वाले volumes)

---

## 🔵 Simple Definition (English)
A read-only volume is a mount the container can read but not change. You add `:ro` to a `-v` mount (or `readonly` in `--mount`, `read_only: true` in Compose long syntax). A related feature, `--read-only`, makes the container's whole root filesystem read-only.

## 🔵 सरल परिभाषा (Hindi)
Read-only volume वो mount है जिसे container पढ़ सकता है पर बदल नहीं सकता। `-v` mount में `:ro` जोड़ते हैं (या `--mount` में `readonly`, Compose long syntax में `read_only: true`)। इससे जुड़ा feature `--read-only` पूरे container के root filesystem को read-only बना देता है।

---

## 🔴 Problem it Solves
- If an attacker gets code execution in a web container, a writable mount lets them overwrite configs, certificates, static files or plant web shells.
- Bugs can also delete or corrupt shared data (for example a cleanup script deleting the wrong folder).
- Least privilege: a container that only needs to read config or serve files should not have write power.

## 🔴 यह क्यों बना? (Hindi)
- अगर attacker को web container में code execution मिल जाए, तो writable mount से वह configs, certificates, static files overwrite या web shell डाल सकता है।
- Bugs भी shared data delete/corrupt कर सकते हैं (जैसे cleanup script गलत folder मिटा दे)।
- Least privilege: जिस container को सिर्फ config पढ़ना या files serve करनी हैं उसे लिखने की ताकत नहीं मिलनी चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Add :ro to the mount:  -v config:/etc/app:ro
Step 2 → Docker mounts the path with the kernel "ro" flag (bind mount remounted read-only).
Step 3 → Any write() inside the container to that path fails: "Read-only file system" (EROFS).
Step 4 → Optionally add --read-only so the rest of the root filesystem is also immutable.
Step 5 → Give genuinely needed writable places explicitly: tmpfs for /tmp, a rw volume for data.
Step 6 → Other containers can still mount the same volume rw (the flag is per mount, not per volume).
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Mount में :ro जोड़ो:  -v config:/etc/app:ro
Step 2 → Docker kernel के "ro" flag के साथ path mount करता है (bind mount read-only remount होता है)।
Step 3 → Container से उस path पर कोई write() हुआ तो error: "Read-only file system" (EROFS)।
Step 4 → चाहें तो --read-only भी जोड़ो ताकि root filesystem का बाकी हिस्सा भी immutable हो।
Step 5 → जहाँ सच में लिखना ज़रूरी है वहाँ अलग से दो: /tmp के लिए tmpfs, data के लिए rw volume।
Step 6 → दूसरे containers वही volume rw mount कर सकते हैं (flag mount पर है, volume पर नहीं)।
```

---

## 🟡 Real World Example
A fintech runs its Nginx container with `read_only: true`, the config mounted `:ro`, and only `/var/cache/nginx`, `/var/run` and `/tmp` as tmpfs. During a pentest, a file-upload bug let the tester run code in a different container but they could not modify Nginx's config or drop a backdoor into the served directory. The auditors listed this as a positive finding.

## 🟡 Real Example Hindi mein
एक fintech अपना Nginx container `read_only: true` से चलाती है, config `:ro` mount है, और सिर्फ `/var/cache/nginx`, `/var/run` और `/tmp` tmpfs हैं। Pentest में file-upload bug से tester दूसरे container में code चला पाया पर Nginx की config नहीं बदल सका और served directory में backdoor नहीं डाल सका। Auditors ने इसे positive finding लिखा।

---

## 💻 Code / Config Example — Basic
```bash
# read-only bind mount of a config file
docker run -d --name web -p 8080:80 \
  -v "$(pwd)/nginx.conf":/etc/nginx/nginx.conf:ro \
  nginx:1.27                                       # :ro -> nginx can read config, never modify it

# prove it: a write attempt fails
docker run --rm -v myvol:/data:ro alpine sh -c 'touch /data/a'
# touch: /data/a: Read-only file system

# same thing with --mount syntax (more explicit)
docker run --rm --mount type=volume,source=myvol,target=/data,readonly alpine ls /data

# whole container read-only, with a RAM scratch dir for /tmp
docker run --rm --read-only --tmpfs /tmp alpine sh -c 'touch /tmp/ok && echo tmp-ok; touch /etc/x'
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.prod.yml - hardened web tier with read-only mounts everywhere possible
services:
  nginx:
    image: nginx:1.27-alpine                      # example tag
    read_only: true                               # root filesystem immutable
    tmpfs:
      - /var/cache/nginx                          # nginx needs to write cache here
      - /var/run                                  # pid file location
      - /tmp                                      # temp files in RAM
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro        # config read-only
      - static:/usr/share/nginx/html:ro                    # static site read-only
      - letsencrypt:/etc/letsencrypt:ro                    # certs read-only
      - type: volume                                       # long syntax, same idea
        source: logs
        target: /var/log/nginx                             # logs must be writable
        read_only: false                                   # explicit rw (only this path)
    ports: ["80:80", "443:443"]
    cap_drop: [ALL]                                        # drop all capabilities
    cap_add: [NET_BIND_SERVICE, CHOWN, SETUID, SETGID]     # minimal caps nginx master needs (verify on your image)
    security_opt: ["no-new-privileges:true"]               # no privilege escalation
  api:
    image: myorg/api:1.0.0                        # Node.js/FastAPI service
    read_only: true                               # immutable root FS
    tmpfs: ["/tmp"]                               # temp files only in RAM
    volumes:
      - uploads:/app/uploads                      # the ONLY writable persistent path
      - ./config/app.yml:/app/config/app.yml:ro   # app config read-only
volumes:
  static:
  letsencrypt:
  logs:
  uploads:
```

---

## 🟠 My Stack Integration
- **React build served by Nginx**: bake into the image, run with `read_only: true`; no write needed except tmpfs.
- **Node.js**: libraries like `multer` write to `/tmp` or uploads. Allow exactly those paths. Some tools write caches to `$HOME`; set `HOME=/tmp` or add tmpfs.
- **FastAPI/uvicorn**: Python writes `__pycache__`; set `PYTHONDONTWRITEBYTECODE=1`.
- **VPS**: backup helpers mount DB volumes `:ro`; certbot is the only rw container for certs.
- **AWS**: ECS has `readonlyRootFilesystem: true` for the same purpose; Kubernetes has `readOnlyRootFilesystem` in securityContext.

```yaml
# env tweaks that make apps work on a read-only root filesystem
    environment:
      PYTHONDONTWRITEBYTECODE: "1"     # no .pyc files
      HOME: /tmp                       # tools writing to ~ go to tmpfs
      NPM_CONFIG_CACHE: /tmp/.npm      # npm cache in tmpfs
```
Security: `read_only` + `cap_drop` + `no-new-privileges` + non-root user is the standard container hardening set.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `--read-only` without tmpfs, then the app crashes writing pid/temp files.
✅ Correct: Add `--tmpfs /tmp` and other required paths; find them from the error messages.

❌ Mistake 2: Thinking `:ro` makes data safe from the host root or other containers.
✅ Correct: It limits only THAT mount. Another container with rw can still change data.

❌ Mistake 3: Mounting the Docker socket `:ro` and feeling safe.
✅ Correct: `/var/run/docker.sock:ro` still allows full API control (ro applies to the socket file, not the API). Avoid mounting it.

❌ Mistake 4: Mounting a DB data dir read-only for the DB itself.
✅ Correct: DB must write. Use `:ro` for replicas/backup helpers only.

---

## 🧠 Tricky Interview Question
You mounted `/var/run/docker.sock:/var/run/docker.sock:ro` into a monitoring container. A teammate says it is safe because it is read-only. Is it?

Answer: No. Read-only affects file operations on the socket inode, but connecting to the socket and sending HTTP API requests still works, so the container can start privileged containers and own the host. Use a socket proxy that filters API calls, or avoid it.

---

## ⚫ Interview Questions + Answers

Q1: How do you make a mount read-only?
A1: `-v name:/path:ro`, or `--mount ...,readonly`, or Compose `read_only: true` in long syntax.

Q2: Difference between `:ro` and `--read-only`?
A2: `:ro` applies to one mount. `--read-only` makes the container's whole root filesystem read-only (mounted volumes stay rw unless marked ro).

Q3: What error appears on writes?
A3: "Read-only file system" (EROFS).

Q4: Why read-only root filesystems in production?
A4: They block malware persistence, accidental writes, and force explicit declaration of writable paths.

Q5: How to handle apps needing temp files?
A5: `tmpfs` mounts for `/tmp`, `/run`, caches.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Config, certificates, static assets, shared reference data, backup sources.
- Production web/API tiers.

❌ Avoid when:
- The process truly writes there (databases, uploads, logs unless shipped to stdout).
- Installers or dev containers that run package managers.

---

## 📊 Visual Diagram
```
 +---------------- container (read_only: true) ----------------+
 |  / (root fs)            -> READ ONLY                         |
 |  /etc/nginx/nginx.conf  -> volume mount :ro   (read only)   |
 |  /usr/share/nginx/html  -> volume mount :ro   (read only)   |
 |  /tmp, /var/run         -> tmpfs (RAM, writable, ephemeral)  |
 |  /var/log/nginx         -> volume rw  (only persistent write)|
 +--------------------------------------------------------------+
   attacker tries: echo hack > /usr/share/nginx/html/index.html
   result: "Read-only file system"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| :ro | Read-only mount flag | सिर्फ पढ़ने का flag |
| --read-only | Immutable root filesystem | अपरिवर्तनीय root filesystem |
| tmpfs | In-memory writable mount | RAM में लिखने वाला mount |
| EROFS | Read-only filesystem error | Read-only filesystem error |
| Least privilege | Give only needed access | सिर्फ ज़रूरी अधिकार |
| Capability | Fine-grained root power | root की छोटी-छोटी शक्तियाँ |

---

## ⚡ 3-Line Summary
English: `:ro` makes a mount unwritable; `--read-only` does it for the whole root filesystem.
Add tmpfs for temp paths and rw volumes only where writing is required.
It is a cheap, strong hardening step against tampering and bugs.
Hindi: `:ro` mount को लिखने लायक नहीं छोड़ता; `--read-only` पूरे root filesystem के लिए यही करता है।
Temp paths के लिए tmpfs और सिर्फ ज़रूरी जगह rw volume दो।
यह tampering और bugs के खिलाफ सस्ता और मज़बूत hardening step है।

---

## ➡️ Next Topic
164. Volume Pruning: safely cleaning unused volumes and reclaiming disk space.
