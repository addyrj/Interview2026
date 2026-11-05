---

# 152. Bind Mounts vs Volumes
# हिंदी में: Bind Mounts बनाम Volumes

---

## 🔵 Simple Definition (English)
A **bind mount** maps an exact file or directory from the host into the container (`-v /home/me/app:/app`). A **volume** is storage Docker creates and manages by name (`-v appdata:/app/data`). Both give containers persistent, shared storage, but they differ in who owns the path, portability, permissions and safety.

## 🔵 सरल परिभाषा (Hindi)
**Bind mount** host की एक सटीक file या directory को container में map करता है (`-v /home/me/app:/app`)। **Volume** वह storage है जिसे Docker नाम से बनाता और manage करता है (`-v appdata:/app/data`)। दोनों persistent और shared storage देते हैं, पर फ़र्क़ है कि path का मालिक कौन है, portability, permissions और safety।

---

## 🔴 Problem it Solves
Developers need two different things. During development you want to edit code on your laptop and see it live in the container (host path). In production you want data storage that does not depend on a particular folder layout of the server, is created and cleaned by Docker, and cannot accidentally expose host files. Using the wrong type causes broken file permissions, security holes and "works on my laptop only" setups.

## 🔴 यह क्यों बना? (Hindi)
Developers को दो अलग चीज़ें चाहिए। Development में laptop पर code edit करके container में live देखना (host path)। Production में ऐसा data storage जो server के folder layout पर निर्भर न हो, Docker बनाए और साफ़ करे, और host की files गलती से expose न करे। गलत type चुनने पर permissions टूटते हैं, security holes बनते हैं और "सिर्फ़ मेरे laptop पर चलता है" वाली setups बनती हैं।

---

## 🟢 How it Works — Step by Step

```
Bind mount:
Step 1 → You give an absolute host path:  -v /srv/app/config:/etc/app:ro
Step 2 → Docker mounts that existing path directly (error with --mount if missing;
         -v silently creates it as root)
Step 3 → Container sees the host files live; edits on either side are instant
Step 4 → UID/GID of files are the HOST's numbers, so permissions must match

Volume:
Step 1 → You give a name:  -v appdata:/app/data
Step 2 → Docker creates /var/lib/docker/volumes/appdata/_data (root-owned area)
Step 3 → Empty volume is seeded from the image content at that path
Step 4 → Docker CLI manages it: ls, inspect, rm, prune, backup helpers, drivers
```

## 🟢 कैसे काम करता है? (Hindi)
```
Bind mount:
Step 1 → आप absolute host path देते हैं:  -v /srv/app/config:/etc/app:ro
Step 2 → Docker उस मौजूद path को सीधे mount करता है (--mount में न हो तो error;
         -v चुपचाप root के नाम से बना देता है)
Step 3 → Container host की files live देखता है; किसी भी तरफ़ का edit तुरंत दिखता है
Step 4 → Files के UID/GID HOST के नंबर होते हैं, इसलिए permissions मिलने चाहिए

Volume:
Step 1 → आप नाम देते हैं:  -v appdata:/app/data
Step 2 → Docker /var/lib/docker/volumes/appdata/_data बनाता है (root वाला क्षेत्र)
Step 3 → Empty volume में उस path पर image की content seed होती है
Step 4 → Docker CLI इसे manage करता है: ls, inspect, rm, prune, backup helpers, drivers
```

---

## 🟡 Real World Example
A Pune SaaS team used a bind mount `./data:/var/lib/postgresql/data` in production because it worked on laptops. On the Ubuntu VPS the folder was owned by the deploy user (UID 1001), but Postgres runs as UID 999, so the container crashed with "permission denied". Someone "fixed" it with `chmod -R 777 data`, making the database files world-writable. They moved to a named volume for data (Docker handles ownership), kept a bind mount only for `nginx.conf:ro` and for `src/` in the dev compose override.

## 🟡 Real Example Hindi mein
Pune की एक SaaS team ने production में bind mount `./data:/var/lib/postgresql/data` लगाया क्योंकि laptops पर चल जाता था। Ubuntu VPS पर वह folder deploy user (UID 1001) का था, पर Postgres UID 999 से चलता है, इसलिए container "permission denied" से crash हुआ। किसी ने `chmod -R 777 data` से "ठीक" कर दिया, जिससे database files सबके लिए writable हो गईं। उन्होंने data के लिए named volume अपनाया (ownership Docker संभालता है), और bind mount सिर्फ़ `nginx.conf:ro` और dev compose override में `src/` के लिए रखा।

---

## 💻 Code / Config Example — Basic

```bash
# BIND MOUNT: live code editing in development
docker run --rm -it \
  -v "$(pwd)":/app \
  -w /app \
  -p 3000:3000 \
  node:20-alpine npm run dev
# $(pwd) is the absolute current host folder; changes appear instantly in /app
# -w sets the working directory; -p publishes the dev server port

# BIND MOUNT, read-only config (safe pattern)
docker run -d --name web -p 80:80 \
  -v /srv/app/nginx.conf:/etc/nginx/conf.d/default.conf:ro \
  nginx:1.27-alpine
# :ro stops the container from modifying the host file

# NAMED VOLUME: database storage
docker run -d --name db -e POSTGRES_PASSWORD=change-me \
  -v pgdata:/var/lib/postgresql/data postgres:16-alpine
# Docker creates and owns pgdata; no host path needed

# Same two mounts using the explicit --mount syntax
docker run --rm \
  --mount type=bind,source=/srv/app/nginx.conf,target=/etc/nginx/conf.d/default.conf,readonly \
  --mount type=volume,source=pgdata,target=/data \
  alpine:3.20 ls /data
# --mount fails loudly if the bind source does not exist; clearer than -v

# Compare ownership problems: see the numeric UID/GID Docker uses inside
docker run --rm -v "$(pwd)":/w alpine:3.20 ls -ln /w
# -n prints numeric IDs; compare with `id -u` on the host
```

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.yml (base: production-safe, uses volumes and read-only binds)
services:
  api:
    image: ghcr.io/acme/node-api:1.8.3             # Node.js image with code baked in
    volumes:
      - uploads:/app/uploads                        # named volume for user data
    user: "1000:1000"                               # fixed non-root UID for predictable ownership

  web:
    image: nginx:1.27-alpine                        # Nginx for React build
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro   # config bind mount, read-only
      - certs:/etc/letsencrypt:ro                    # certificates in a named volume, read-only
    ports:
      - "80:80"                                     # HTTP
      - "443:443"                                   # HTTPS

volumes:
  uploads: {}                                       # Docker-managed storage
  certs: {}                                         # Docker-managed storage
```

```yaml
# docker-compose.override.yml (dev only: loaded automatically by `docker compose up`)
services:
  api:
    build: ./api                                    # build locally instead of pulling
    command: npm run dev                            # nodemon/ts-node watch mode
    volumes:
      - ./api/src:/app/src                          # bind mount: edit code, see it live
      - /app/node_modules                           # anonymous volume: keep container's node_modules
    environment:
      NODE_ENV: development                         # dev behaviour and verbose errors
```

```bash
# Fix bind-mount permission problems the right way (not chmod 777)
sudo chown -R 1000:1000 ./uploads        # make host folder match the container user's UID/GID
# Or run the container with the host user's IDs in dev:
docker run --rm -u "$(id -u):$(id -g)" -v "$(pwd)":/w alpine:3.20 touch /w/ok
# -u uses your UID/GID so files created in /w belong to you, not root
```

Both YAML files parsed; shell blocks passed `bash -n`. Compose merges the override automatically only for plain `docker compose up`; use `-f docker-compose.yml` in production to skip it.

---

## 🟠 My Stack Integration
Dev laptop: bind mount `src/` for Node.js and FastAPI (`uvicorn --reload`), React with Vite dev server. VPS production: images contain the code; volumes hold Postgres, uploads and certificates; bind mounts only for read-only config (`nginx.conf`) and Docker socket-free setups. CI: neither needed; build contexts are copied into the image. Avoid bind-mounting `node_modules` from macOS/Windows into Linux containers because native modules break and file-sync is slow.

```bash
# Production deploy command that ignores the dev override file
docker compose -f docker-compose.yml up -d
# -f selects only the base file, so no bind-mounted source code in production
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using bind mounts for database data in production.
✅ Correct: Named volumes (or managed DB). Bind mounts tie you to host paths, UIDs and SELinux labels.

❌ Mistake 2: Mounting `/var/run/docker.sock` or `/` into a container.
✅ Correct: Never, unless absolutely needed. The Docker socket is root on the host. Use `:ro` and narrow paths otherwise.

❌ Mistake 3: Relative host path without `./` (e.g. `-v data:/x`) which creates a named volume instead of a bind mount.
✅ Correct: Bind mounts start with `/` or `./`. A bare name means volume.

❌ Mistake 4: On SELinux hosts (RHEL/CentOS), bind mounts fail with permission denied.
✅ Correct: Add `:z` (shared) or `:Z` (private) to relabel: `-v ./conf:/etc/app:ro,z`.

---

## 🧠 Tricky Interview Question
Your Node.js container works with the code baked into the image. In dev you add `-v $(pwd):/app` and the app crashes with "Cannot find module 'express'". Why?

Answer: The bind mount covers `/app` entirely, hiding the `node_modules` that `npm ci` installed in the image, and replaces them with the host folder, which has no node_modules (or ones built for macOS). Fix: install dependencies on the host, or add an anonymous/named volume at `/app/node_modules` so the container's copy overlays the bind mount, or bind-mount only `./src`. Mount order matters: more specific mounts win over broader ones.

---

## ⚫ Interview Questions + Answers

Q1: Which is faster?
A1: On Linux both are native speed. On Docker Desktop (Mac/Windows) bind mounts cross a VM file-sharing layer and are much slower than volumes.

Q2: Which is more secure?
A2: Volumes: isolated from host paths and managed by Docker. Bind mounts can expose sensitive host files and let a compromised container modify them unless `:ro`.

Q3: Can a bind mount be created from a missing path?
A3: `-v` creates the missing host directory (as root). `--mount type=bind` returns an error. Prefer `--mount` to catch typos.

Q4: Which one is portable between servers?
A4: Neither automatically. Volumes avoid host path assumptions; moving data still needs backup/restore or a network volume driver.

Q5: How do you pre-populate data?
A5: Volume: seeded from the image on first use. Bind mount: host content is used as is, nothing is copied from the image.

---

## 🔷 When to Use + When Not to Use
✅ Use bind mounts when:
- Live-editing source code in development
- Injecting config files or certificates read-only
- Sharing build output with the host

✅ Use volumes when:
- Database, uploads, any production state
- Backup/restore and drivers are needed
- You want Docker-managed cleanup and permissions

❌ Avoid:
- Bind mounts for production data
- Volumes for files you must edit constantly from the host

---

## 📊 Visual Diagram
```
        BIND MOUNT                               VOLUME
  host: /srv/app/conf  ─────────┐      host: /var/lib/docker/volumes/
  (YOU choose the path)         │             appdata/_data
                                ▼             (DOCKER chooses the path)
                  ┌─────────────────────┐             │
                  │ container /etc/app  │◄────────────┘ via name "appdata"
                  └─────────────────────┘
  + live edit, simple                   + portable names, docker volume CLI
  - host UID/GID, SELinux, exposure     + seeded from image, safer
  - host path must exist/match          - data hidden in /var/lib/docker
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bind mount | Host path inside container | Host path container में |
| Named volume | Docker-managed storage by name | नाम वाला Docker storage |
| :ro | Read-only flag | सिर्फ़ पढ़ने योग्य |
| UID/GID | Numeric user/group IDs | User/group की संख्या ID |
| SELinux :z/:Z | Relabel flags for mounts | Mount के label flags |
| --mount | Explicit, verbose mount syntax | विस्तृत mount syntax |

---

## ⚡ 3-Line Summary
English: Bind mounts map host paths (best for dev code and read-only config); volumes are Docker-managed (best for production data). Watch permissions, UIDs and what a mount hides in the image. Never bind-mount the Docker socket casually.
Hindi: Bind mounts host paths को map करते हैं (dev code और read-only config के लिए बेहतर); volumes Docker-managed हैं (production data के लिए बेहतर)। Permissions, UIDs और mount image की कौन सी files ढकता है, इस पर ध्यान दो। Docker socket को लापरवाही से bind-mount मत करो।

---

## ➡️ Next Topic
**153. tmpfs Mounts**: the third mount type, memory-only storage for secrets and scratch data.

---
