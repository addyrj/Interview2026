# 162. Volume Permissions
# हिंदी में: Volume Permissions (अनुमतियाँ)

---

## 🔵 Simple Definition (English)
Volume permissions are the Linux file owner (uid), group (gid) and mode bits on files inside a mounted volume. A container process can read or write the volume only if its uid/gid matches those permissions, no matter what user names exist inside or outside the container.

## 🔵 सरल परिभाषा (Hindi)
Volume permissions उन files पर Linux का owner (uid), group (gid) और mode bits हैं जो mounted volume के अंदर हैं। Container process तभी volume पढ़/लिख सकता है जब उसका uid/gid इन permissions से match करे, चाहे container के अंदर या बाहर user names कुछ भी हों।

---

## 🔴 Problem it Solves
- Best practice is to run apps as non-root (`USER node`, uid 1000). But volumes are often created as root, so the app gets `EACCES: permission denied`.
- Linux compares numeric IDs only. Host user "ubuntu" (uid 1000) and container user "node" (uid 1000) are the same to the kernel, while "postgres" (uid 999) is a different one.
- Understanding this prevents the dangerous "fix" `chmod 777` and running everything as root.

## 🔴 यह क्यों बना? (Hindi)
- Best practice है app को non-root चलाना (`USER node`, uid 1000)। लेकिन volumes अक्सर root के नाम से बनते हैं, इसलिए app को `EACCES: permission denied` मिलता है।
- Linux सिर्फ numeric IDs की तुलना करता है। Host user "ubuntu" (uid 1000) और container user "node" (uid 1000) kernel के लिए एक ही हैं, जबकि "postgres" (uid 999) अलग है।
- यह समझना खतरनाक "fix" `chmod 777` और सब कुछ root से चलाने से बचाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Volume/bind-mount directory has owner uid:gid and mode (e.g. root:root 755).
Step 2 → Container process runs as a uid (USER in Dockerfile, or --user / compose user:).
Step 3 → Kernel checks uid/gid against the directory: owner? group? other? -> r/w/x allowed?
Step 4 → Named volume, FIRST mount: if the image already has that path with an owner, Docker copies
         the path's ownership/content into the empty volume (so `chown` in Dockerfile helps).
Step 5 → Bind mount: host directory permissions are used as-is (no copy), so you must chown on host.
Step 6 → Mismatch -> EACCES. Fix by chown to the right uid, `user:` to match, or `group_add`.
Step 7 → Rootless Docker / userns-remap shifts uids (container 0 -> host 100000+): plan accordingly.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Volume/bind-mount directory का owner uid:gid और mode होता है (जैसे root:root 755)।
Step 2 → Container process एक uid से चलता है (Dockerfile का USER, या --user / compose user:)।
Step 3 → Kernel uid/gid को directory से मिलाता है: owner? group? other? -> r/w/x मिलेगा?
Step 4 → Named volume, पहली mount: अगर image में वो path किसी owner के साथ है, तो Docker उस path की
         ownership/content खाली volume में copy करता है (इसलिए Dockerfile का `chown` काम आता है)।
Step 5 → Bind mount: host directory की permissions जैसी हैं वैसी ही चलती हैं (copy नहीं), इसलिए host पर chown करना पड़ेगा।
Step 6 → Mismatch -> EACCES। Fix: सही uid पर chown, `user:` match करना, या `group_add`।
Step 7 → Rootless Docker / userns-remap uids shift करता है (container 0 -> host 100000+): इसी हिसाब से plan करो।
```

---

## 🟡 Real World Example
A team hardens their Node.js API to run as `USER node` and mounts `./uploads:/app/uploads`. Uploads start failing with `EACCES` because `./uploads` was created by `root` via a previous container. They fix it with `sudo chown -R 1000:1000 uploads` on the VPS. Another team, running Postgres with a bind mount, hit "data directory has wrong ownership" because the folder was owned by ubuntu (1000) while Postgres runs as uid 999.

## 🟡 Real Example Hindi mein
एक team अपने Node.js API को `USER node` से चलाती है और `./uploads:/app/uploads` mount करती है। Uploads `EACCES` से fail होने लगे क्योंकि `./uploads` पहले किसी container ने `root` के नाम से बनाया था। उन्होंने VPS पर `sudo chown -R 1000:1000 uploads` से fix किया। दूसरी team Postgres को bind mount के साथ चला रही थी और "data directory has wrong ownership" मिला क्योंकि folder का owner ubuntu (1000) था जबकि Postgres uid 999 से चलता है।

---

## 💻 Code / Config Example — Basic
```bash
# reproduce and fix a permission problem
docker volume create appdata                          # new named volume (owned by root:root)

# non-root container (uid 1000) tries to write -> fails
docker run --rm -u 1000:1000 -v appdata:/data alpine sh -c 'touch /data/x'
# touch: /data/x: Permission denied

# fix: one-off root helper changes ownership of the volume contents
docker run --rm -v appdata:/data alpine chown -R 1000:1000 /data   # give uid/gid 1000 ownership

# works now
docker run --rm -u 1000:1000 -v appdata:/data alpine sh -c 'touch /data/x && ls -ln /data'

# inspect numeric owners of a bind mount on the host
ls -ln ./uploads                                      # -n shows numeric uid/gid, what the kernel uses
```

## 💻 Code / Config Example — Advanced
```dockerfile
# Dockerfile - Node.js API that owns its writable dirs, so named volumes inherit correct ownership
FROM node:20-alpine AS runtime                  # small base image (example tag)
WORKDIR /app                                    # app directory
COPY --chown=node:node package*.json ./         # copy manifests with correct owner
RUN npm ci --omit=dev                           # install production deps only
COPY --chown=node:node . .                      # copy code owned by node (uid 1000)
# create the upload dir BEFORE switching user and give it to node;
# a NEW named volume mounted here copies this ownership on first use
RUN mkdir -p /app/uploads && chown -R node:node /app/uploads
USER node                                       # run as non-root (uid 1000, gid 1000)
EXPOSE 3000                                     # document the port
CMD ["node", "server.js"]                       # start the app
```
```yaml
# docker-compose.yml - permissions handled explicitly
services:
  api:
    build: .                                    # build from the Dockerfile above
    user: "1000:1000"                           # explicit uid:gid (matches USER node)
    volumes:
      - uploads:/app/uploads                    # named volume: inherits owner from image on first mount
    read_only: true                             # root FS read-only; only mounted paths writable
    cap_drop: [ALL]                             # drop all Linux capabilities
    security_opt:
      - no-new-privileges:true                  # block privilege escalation
  fastapi:
    image: myorg/fastapi:1.2.0                  # example image running as uid 10001
    user: "10001:10001"                         # non-root user defined in its Dockerfile
    group_add: ["1000"]                         # also join gid 1000 to share files written by api
    volumes:
      - uploads:/data/uploads:ro                # read-only consumer
  db-init-perms:                                # one-shot service to fix ownership of a bind mount
    image: alpine:3.20
    user: "0:0"                                 # root only for this tiny job
    volumes:
      - ./pgdata:/var/lib/postgresql/data       # bind mount example
    command: chown -R 999:999 /var/lib/postgresql/data   # postgres uid/gid in official image
    restart: "no"                               # run once
volumes:
  uploads:
```

---

## 🟠 My Stack Integration
- **Node.js**: official `node` images provide user `node` (uid 1000); `chown` dirs in Dockerfile.
- **FastAPI**: create a user with fixed uid in the Dockerfile (`RUN useradd -u 10001 app`), so volume ownership is predictable.
- **Postgres/MySQL/Mongo**: official images fix ownership of a named volume by themselves via the entrypoint (they start as root, `chown`, then drop privileges). Bind mounts on the host often break this.
- **Nginx**: master runs as root, workers as `nginx` (uid 101 in official image); log/cache volumes must be writable by the right user.
- **VPS**: use `ls -ln` and `id` to compare numeric IDs. SELinux hosts (Amazon Linux/RHEL) may also need `:z` or `:Z` on bind mounts.

```bash
# SELinux example (RHEL/Amazon Linux with SELinux enforcing): relabel bind mount for container access
docker run -v /srv/uploads:/app/uploads:Z myorg/api:1.0   # :Z = private label; :z = shared among containers
```
Security: avoid `chmod 777` and `--privileged`; give the minimum uid/gid, drop capabilities, use `read_only` rootfs.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `chmod -R 777 volume`.
✅ Correct: `chown` to the exact uid:gid the process uses, mode 750/640.

❌ Mistake 2: Running as root to "make it work".
✅ Correct: Fix ownership; root in container is root-equivalent on shared kernel risks.

❌ Mistake 3: Forgetting the Dockerfile `chown` before `USER`.
✅ Correct: `RUN mkdir ... && chown ...` while still root, then `USER node`.

❌ Mistake 4: Expecting the Dockerfile `chown` to apply to a bind mount.
✅ Correct: Bind mounts hide image content; chown on the host path.

❌ Mistake 5: Existing named volume already created as root, so new image `chown` has no effect.
✅ Correct: Chown the existing volume once with a helper container.

---

## 🧠 Tricky Interview Question
`ls -l` on the host shows files owned by "ubuntu", but inside the container they appear owned by "node". Is something wrong?

Answer: No. Names are looked up per environment from /etc/passwd, but the kernel stores only numeric IDs. Uid 1000 is "ubuntu" on the host and "node" in the Node image. Permissions match because the numbers match. The problem appears when numbers differ (999 vs 1000). Use `ls -ln` to compare.

---

## ⚫ Interview Questions + Answers

Q1: Why "permission denied" on a volume although I am root on the host?
A1: The process inside the container runs as a different uid (non-root), and the volume is owned by another uid. Root on host is not relevant.

Q2: How do named volumes get their initial ownership?
A2: If the mount path exists in the image, Docker copies its contents and ownership into the empty named volume at first mount.

Q3: What is userns-remap?
A3: A daemon setting that maps container uids to a high host range, so container root is unprivileged on the host. Volume ownership must match the mapped range.

Q4: What do `:z` and `:Z` do?
A4: SELinux relabel flags for bind mounts: shared (`z`) or private (`Z`).

Q5: How to run an init job to fix permissions?
A5: Use a one-shot root container (or an entrypoint script run as root then `gosu`/`su-exec` to drop to the app user).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running non-root containers with persistent or shared data.
- Hardening production images.

❌ Avoid when:
- Doing quick local throwaway demos (still do not ship root-only fixes to prod).

---

## 📊 Visual Diagram
```
 Host dir ./uploads  owner 0:0 (root) mode 755
        |
        | bind mount
        v
 +-------------------------+
 | container  USER node    |   process uid=1000
 |  write /app/uploads/x   |-----> kernel: uid 1000 != owner 0, mode 755 -> others no write
 +-------------------------+              => EACCES

 Fix: chown -R 1000:1000 ./uploads   =>  uid 1000 == owner  => write OK
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| uid / gid | Numeric user / group id | user / group की संख्या |
| chown | Change file owner | owner बदलना |
| Mode bits | rwx permissions (e.g. 750) | पढ़ने/लिखने/चलाने की अनुमति |
| EACCES | Permission denied error | अनुमति नहीं वाली error |
| userns-remap | Map container uids to host range | uid mapping |
| SELinux label | Security context on files | SELinux की सुरक्षा label |

---

## ⚡ 3-Line Summary
English: Permissions are numeric uid/gid checks, not user names.
Run as non-root, chown the volume to that uid, and avoid chmod 777.
Named volumes inherit image ownership at first mount; bind mounts need host chown.
Hindi: Permissions numeric uid/gid की जाँच हैं, user names की नहीं।
Non-root चलाओ, volume को उसी uid पर chown करो, और chmod 777 से बचो।
Named volume पहली mount पर image की ownership लेता है; bind mount में host पर chown चाहिए।

---

## ➡️ Next Topic
163. Read-Only Volumes: restricting containers to read-only access as a security layer.
