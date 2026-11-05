---

# 153. tmpfs Mounts
# हिंदी में: tmpfs Mounts (सिर्फ़ RAM में storage)

---

## 🔵 Simple Definition (English)
A **tmpfs mount** is a temporary filesystem stored in the host's memory (RAM, and swap if the host swaps). It is created when the container starts and destroyed when the container stops, and nothing is written to the host disk. Linux only. Used with `--tmpfs` or `--mount type=tmpfs`.

## 🔵 सरल परिभाषा (Hindi)
**tmpfs mount** host की memory (RAM, और host swap करे तो swap) में बना अस्थायी filesystem है। यह container शुरू होने पर बनता है और रुकने पर नष्ट हो जाता है, और host disk पर कुछ नहीं लिखा जाता। सिर्फ़ Linux पर। `--tmpfs` या `--mount type=tmpfs` से इस्तेमाल होता है।

---

## 🔴 Problem it Solves
Some data should never touch disk: decrypted secrets, session tokens, upload scratch files, a build's temporary output. Writing them to the writable layer or a volume leaves traces after the container dies (disk forensics, backups, snapshots). Also, disk I/O for hot scratch data (sorting, caches) is slower than memory. And a `read_only: true` container still needs a few writable spots like `/tmp` and `/run`.

## 🔴 यह क्यों बना? (Hindi)
कुछ data कभी disk को छूना नहीं चाहिए: decrypted secrets, session tokens, upload के scratch files, build का temporary output। इन्हें writable layer या volume में लिखने पर container मरने के बाद भी निशान रहते हैं (disk forensics, backups, snapshots)। साथ ही hot scratch data (sorting, caches) के लिए disk I/O memory से धीमा है। और `read_only: true` container को भी `/tmp` और `/run` जैसी कुछ writable जगहें चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You declare: --tmpfs /tmp:rw,noexec,nosuid,size=64m
Step 2 → Docker asks the kernel to mount a tmpfs at /tmp inside the container namespace
Step 3 → Files created there live in page cache / RAM only
Step 4 → Memory is used on demand up to the size limit (default: 50% of host RAM if unset)
Step 5 → Usage counts toward the container's memory cgroup (--memory limit applies)
Step 6 → Container stops (or restarts): tmpfs content is gone. Data is never shared
         with other containers and cannot be committed with docker commit
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप declare करते हैं: --tmpfs /tmp:rw,noexec,nosuid,size=64m
Step 2 → Docker kernel से container namespace में /tmp पर tmpfs mount करवाता है
Step 3 → वहाँ बनी files सिर्फ़ page cache / RAM में रहती हैं
Step 4 → Memory ज़रूरत के हिसाब से size limit तक इस्तेमाल होती है (size न दो तो host RAM का 50%)
Step 5 → Usage container के memory cgroup में गिनी जाती है (--memory limit लागू होती है)
Step 6 → Container रुके (या restart हो): tmpfs की content खत्म। Data दूसरे containers से
         share नहीं होता और docker commit में नहीं आता
```

---

## 🟡 Real World Example
A payments API receives a signed PDF, converts it, and must not leave customer documents on disk for compliance reasons. The team mounts `/tmp` as tmpfs with `size=256m,noexec,nosuid` and sets the container filesystem read-only. Conversion happens in RAM, files vanish on restart, and an auditor can see there is no document residue on the VPS disk or in nightly volume backups. They also set `--memory 512m` because tmpfs usage counts against the container's memory.

## 🟡 Real Example Hindi mein
एक payments API signed PDF लेकर convert करती है और compliance के कारण customer documents को disk पर नहीं छोड़ सकती। Team `/tmp` को `size=256m,noexec,nosuid` के साथ tmpfs mount करती है और container filesystem read-only रखती है। Conversion RAM में होता है, restart पर files गायब, और auditor देख सकता है कि VPS disk या nightly volume backups में कोई document अवशेष नहीं। वे `--memory 512m` भी लगाते हैं क्योंकि tmpfs usage container की memory में गिनी जाती है।

---

## 💻 Code / Config Example — Basic

```bash
# Short form: --tmpfs path[:options]
docker run -d --name api \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  node:20-alpine node -e "setInterval(()=>{},1000)"
# rw read-write; noexec forbids executing binaries from /tmp (blocks many exploits);
# nosuid ignores setuid bits; size=64m hard cap on how much RAM it can use

# Long form: --mount type=tmpfs
docker run --rm \
  --mount type=tmpfs,destination=/scratch,tmpfs-size=128m,tmpfs-mode=1777 \
  alpine:3.20 sh -c 'df -h /scratch && echo hi > /scratch/a && cat /scratch/a'
# destination is the path inside the container (tmpfs has no source);
# tmpfs-size is in bytes or with suffix (version dependent, m works on current engines);
# tmpfs-mode sets permissions, 1777 means world-writable with sticky bit like /tmp

# Prove it is RAM backed and not persistent
docker run --rm --tmpfs /data alpine:3.20 sh -c 'echo secret > /data/x; mount | grep " /data "'
# mount output shows "tmpfs on /data type tmpfs"

# Inspect the configured tmpfs mounts on a running container
docker inspect api --format '{{json .HostConfig.Tmpfs}}'
# prints the map of path -> options set via --tmpfs
```

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.yml: hardened API using tmpfs for the few writable paths
services:
  api:
    image: ghcr.io/acme/node-api:1.8.3          # Node.js API (example tag)
    read_only: true                              # root filesystem is immutable
    user: "1000:1000"                            # run as non-root
    mem_limit: 512m                              # total RAM cap, includes tmpfs usage
    tmpfs:
      - /tmp:size=64m,mode=1777,noexec,nosuid    # scratch space, cannot execute files
      - /run:size=8m,mode=755,noexec,nosuid      # pid/socket files (small)
    cap_drop:
      - ALL                                      # remove all Linux capabilities
    security_opt:
      - no-new-privileges:true                   # prevent setuid privilege gain
    environment:
      NODE_ENV: production                       # production mode
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]  # liveness probe
      interval: 30s                              # check every 30 seconds
      timeout: 3s                                # fail after 3 seconds
      retries: 3                                 # three failures -> unhealthy

  secrets-demo:
    image: alpine:3.20                           # tiny image for the demo
    command: ["sh", "-c", "ls -l /run/app-secrets && sleep 3600"]   # list then wait
    volumes:
      - type: tmpfs                              # long-form volume entry of type tmpfs
        target: /run/app-secrets                 # in-container path, memory only
        tmpfs:
          size: 1048576                          # size in bytes (1 MiB) in long syntax
```

```bash
# Using tmpfs for a throwaway database in tests: fast and leaves no files
docker run -d --name testdb \
  -e POSTGRES_PASSWORD=test \
  --tmpfs /var/lib/postgresql/data:rw,size=512m \
  postgres:16-alpine -c fsync=off -c synchronous_commit=off -c full_page_writes=off
# data directory in RAM makes test suites much faster; fsync=off is ONLY safe for tests
# (a crash would corrupt data; never use these flags in production)
```

YAML parsed, shell blocks checked with `bash -n`. Not run on a Docker daemon; `tmpfs-size` unit formats and the long Compose `tmpfs.size` field are version dependent, so check your Docker/Compose version.

---

## 🟠 My Stack Integration
Node.js: set `read_only: true`, tmpfs on `/tmp` (some libraries such as `multer` or `sharp` write temporary files). FastAPI/uvicorn: `/tmp` for uploaded temp files (Starlette spools large uploads to temp) and `/run`. Nginx: when read-only, it needs tmpfs on `/var/cache/nginx` and `/var/run` (or `/run`) for the pid file and temp paths. React static: Nginx only. On a VPS with limited RAM, size tmpfs carefully; on AWS ECS use `linuxParameters.tmpfs` in the task definition (Fargate does not support tmpfs, use ephemeral storage or bind a volume).

```yaml
# Read-only Nginx serving the React build with tmpfs for runtime paths
services:
  web:
    image: nginx:1.27-alpine                       # Nginx image
    read_only: true                                # block writes to the root filesystem
    tmpfs:
      - /var/cache/nginx:size=32m                  # proxy/fastcgi temp files
      - /var/run:size=1m                           # pid file location
      - /tmp:size=16m                              # misc scratch
    ports:
      - "80:80"                                    # public HTTP
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting a tmpfs on a database or uploads folder in production.
✅ Correct: tmpfs is lost on restart. Persistent data needs volumes.

❌ Mistake 2: No `size=` limit, letting a runaway process eat host RAM and trigger the OOM killer.
✅ Correct: Always set `size` and a container `--memory` limit.

❌ Mistake 3: Forgetting that `noexec` breaks apps that write and run files (some frameworks unpack native binaries to `/tmp`).
✅ Correct: Test the app; if it needs exec, use a dedicated tmpfs without `noexec` for that path only.

❌ Mistake 4: Expecting tmpfs to work on Windows containers or to be shared between containers.
✅ Correct: Linux only; each container gets its own private tmpfs.

---

## 🧠 Tricky Interview Question
A container has `--memory 256m` and a tmpfs `/tmp` of `size=512m`. A process writes 400 MB to `/tmp`. What happens?

Answer: The tmpfs size limit (512m) is only a ceiling; the pages are charged to the container's memory cgroup. Since the cgroup limit is 256m, the kernel tries to reclaim or swap; tmpfs pages can be swapped if swap is enabled, otherwise the cgroup hits its limit and the OOM killer terminates a process in the container (often the main app), even though the tmpfs "had room". Set tmpfs size well below the memory limit and account for app memory on top.

---

## ⚫ Interview Questions + Answers

Q1: tmpfs vs volume vs bind mount?
A1: tmpfs: RAM only, gone on stop. Volume: Docker-managed disk, persistent. Bind: host path, persistent.

Q2: Is tmpfs data safe from being written to disk?
A2: Mostly. It lives in RAM, but if the host has swap enabled, pages can be swapped out. Disable or encrypt swap for strict secret handling.

Q3: Why add `noexec` and `nosuid`?
A3: They harden `/tmp` against attackers who drop and run a payload there, or abuse setuid binaries.

Q4: Can containers share a tmpfs?
A4: No. A tmpfs mount is private to the container. For shared memory use `--ipc` options or a shared `/dev/shm`.

Q5: What is `--shm-size`?
A5: It sets the size of `/dev/shm` (default 64 MB), which is itself a tmpfs. Chrome/Puppeteer and some databases need larger values.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Temporary files, caches, sockets, pid files with a read-only root filesystem
- Sensitive data that must leave no disk trace
- Fast disposable test databases

❌ Avoid when:
- Data must survive restart
- Large datasets that exceed container memory
- Windows containers or Docker Desktop setups where behavior differs

---

## 📊 Visual Diagram
```
  HOST RAM
  ┌───────────────────────────────────────────────────┐
  │  container memory cgroup (--memory 512m)          │
  │  ┌────────────┐  ┌───────────────────────────┐    │
  │  │ app heap   │  │ tmpfs /tmp (size=64m)     │    │
  │  │ + stack    │  │ files live here, counted  │    │
  │  └────────────┘  │ against the same cgroup   │    │
  │                  └───────────────────────────┘    │
  └───────────────────────────────────────────────────┘
        │ container stops
        ▼
   tmpfs contents erased -> nothing on host disk (unless swap)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| tmpfs | Memory-backed filesystem | Memory वाला filesystem |
| noexec | Disallow running binaries | Binaries चलाने की मनाही |
| nosuid | Ignore setuid bits | setuid bits को अनदेखा |
| read_only | Immutable root filesystem | न बदलने वाला root filesystem |
| /dev/shm | Shared memory tmpfs | Shared memory tmpfs |
| OOM killer | Kernel kills process on memory exhaustion | Memory खत्म होने पर process मारना |

---

## ⚡ 3-Line Summary
English: tmpfs mounts keep data in RAM only, wiped when the container stops. Use them for scratch space, secrets and read-only containers, always with a size cap and `noexec,nosuid`. Their memory counts against the container's limit.
Hindi: tmpfs mounts data को सिर्फ़ RAM में रखते हैं और container रुकने पर मिटा देते हैं। Scratch space, secrets और read-only containers के लिए इस्तेमाल करो, हमेशा size cap और `noexec,nosuid` के साथ। इनकी memory container की limit में गिनी जाती है।

---

## ➡️ Next Topic
**154. Named Volumes**: back to persistent storage, the production-standard way to keep data by name.

---
