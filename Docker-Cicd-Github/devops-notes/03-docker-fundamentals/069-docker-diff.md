# 69. docker diff
# हिंदी में: docker diff (Container में हुए filesystem बदलाव देखना)

---

## 🔵 Simple Definition (English)
`docker diff CONTAINER` lists files and directories that were added (`A`), changed (`C`) or deleted (`D`) in a container's writable layer compared with the image it started from.

## 🔵 सरल परिभाषा (Hindi)
`docker diff CONTAINER` उन files और directories की list देता है जो container की writable layer में, उसकी image के मुकाबले, जुड़ीं (`A`), बदलीं (`C`) या हटीं (`D`)।

---

## 🔴 Problem it Solves
Containers should be disposable and stateless, but apps often secretly write to the filesystem: uploaded files, cache, logs, temp files, `pip install` done by hand. If you do not know what is being written, you cannot decide what needs a volume, you may fill the disk, and you cannot detect tampering after a compromise. `docker diff` shows exactly what drifted from the image.

## 🔴 यह क्यों बना? (Hindi)
Containers disposable और stateless होने चाहिए, पर apps चुपके से filesystem में लिखते हैं: uploads, cache, logs, temp files, हाथ से किया `pip install`। अगर पता न हो क्या लिखा जा रहा है, तो यह तय नहीं कर सकते कि किस path पर volume चाहिए, disk भर सकती है, और compromise के बाद छेड़छाड़ पकड़ना मुश्किल होता है। `docker diff` बताता है image से क्या अलग हुआ।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Image layers are read-only and shared
Step 2 → Container start adds one thin read-write layer on top (overlay2 upperdir)
Step 3 → Any write/delete in container goes to that top layer (copy-on-write)
Step 4 → docker diff compares top layer with the layers below
Step 5 → Output lines: A = added, C = changed, D = deleted (path after the letter)
Step 6 → Mounted volumes/bind mounts do not appear (they are outside the container layer)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Image की layers read-only और shared होती हैं
Step 2 → Container start होने पर ऊपर एक पतली read-write layer जुड़ती है (overlay2 upperdir)
Step 3 → Container में हर write/delete उसी top layer में जाता है (copy-on-write)
Step 4 → docker diff इस top layer की तुलना नीचे की layers से करता है
Step 5 → Output: A = जुड़ा, C = बदला, D = हटा (letter के बाद path)
Step 6 → Volumes/bind mounts यहाँ नहीं दिखते (वे container layer के बाहर हैं)
```

---

## 🟡 Real World Example
A Node.js API container on your VPS has a disk alert: `/var/lib/docker` grew by 8 GB. You run `docker diff api | head` and see `A /app/tmp/uploads/...` thousands of entries, plus `C /root/.npm`. Conclusion: the app stores user uploads in the container layer. The fix is a volume or S3 instead of the writable layer. In another case, after a security scare, `docker diff` shows `A /tmp/.x/miner`, evidence of compromise.

## 🟡 Real Example Hindi mein
आपकी VPS पर Node.js API container का disk alert आता है: `/var/lib/docker` 8 GB बढ़ गया। `docker diff api | head` चलाने पर `A /app/tmp/uploads/...` हज़ारों entries और `C /root/.npm` दिखता है। मतलब app user uploads container layer में रख रही है। समाधान: volume या S3 इस्तेमाल करो। दूसरी स्थिति: security शक होने पर `docker diff` में `A /tmp/.x/miner` दिखे तो वह compromise का सबूत है।

---

## 💻 Code / Config Example — Basic
```bash
# ---- Basic docker diff ----
docker run -d --name demo nginx:1.27-alpine           # start a container (example tag)
docker diff demo                                      # shows files nginx wrote at startup (pid file, cache dirs)
docker exec demo sh -c 'echo test > /tmp/new.txt'     # create a new file inside the container
docker exec demo sh -c 'rm /etc/nginx/conf.d/default.conf'  # delete an image file inside container
docker diff demo                                      # now see: A /tmp/new.txt  and  D /etc/nginx/conf.d/default.conf
docker diff demo | grep '^A'                          # filter: only added paths
docker diff demo | wc -l                              # count how many paths changed
docker rm -f demo                                     # remove container; the changes disappear with it
```

## 💻 Code / Config Example — Advanced
```bash
#!/usr/bin/env bash
# audit-drift.sh -- report containers that wrote outside allowed paths
set -euo pipefail                                         # strict mode
ALLOWED='^(/tmp|/var/run|/var/cache/nginx)'               # regex of paths we accept as writable
for C in $(docker ps --format '{{.Names}}'); do           # loop over every running container name
  BAD=$(docker diff "$C" | awk '{print $2}' | grep -Ev "$ALLOWED" || true)  # paths outside allowed list
  if [ -n "$BAD" ]; then                                  # if any unexpected path exists
    echo "== $C wrote outside allowed paths =="           # header per container
    echo "$BAD" | head -20                                # show first 20 offenders
  fi                                                      # end if
done                                                      # end loop
```
Pair this with a hardened Compose service so drift becomes impossible:

```yaml
# docker-compose.yml -- read-only root filesystem, writes only to tmpfs/volume
services:                          # services map
  api:                             # FastAPI service
    image: ghcr.io/addyrj/api:9fceb02   # pinned example image
    read_only: true                # root filesystem becomes read-only
    tmpfs:                         # in-memory writable dirs
      - /tmp                       # temp files only, gone on restart
    volumes:                       # persistent writes
      - api-data:/app/data         # only this path persists
volumes:                           # named volumes
  api-data:                        # declared volume
```
Not run locally (no daemon); the YAML was parsed for syntax only.

---

## 🟠 My Stack Integration
Run `docker diff` on each of your containers once after a smoke test to learn what should become a volume.

```yaml
# Typical findings translated to Compose for Node.js + FastAPI + Nginx on a VPS
services:                                  # stack
  node-api:                                # Node.js API
    image: ghcr.io/addyrj/node-api:1.2.0   # example image
    tmpfs: ["/tmp"]                        # npm/tmp writes (diff showed C /tmp)
  fastapi:                                 # Python service
    image: ghcr.io/addyrj/fastapi:1.2.0    # example image
    volumes: ["uploads:/app/uploads"]      # diff showed A /app/uploads/*.png -> make persistent
  nginx:                                   # reverse proxy
    image: nginx:1.27-alpine               # example tag
    tmpfs: ["/var/cache/nginx", "/var/run"]  # nginx cache + pid (diff showed these)
volumes:                                   # volume list
  uploads:                                 # uploads persist across deploys
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Expecting `docker diff` to show changes inside volumes/bind mounts.
✅ Correct: Inspect those on the host path or with `docker volume inspect`.

❌ Mistake 2: Using `docker diff` on an image name.
✅ Correct: It only takes a container; use `docker history` or `dive` for images.

❌ Mistake 3: Treating the writable layer as persistent storage because diff shows your data there.
✅ Correct: It is lost on `docker rm`; move data to volumes, S3 or a database.

❌ Mistake 4: Ignoring `C` entries on `/etc/passwd` or `/usr/bin`.
✅ Correct: Unexpected changes to system paths can mean compromise; investigate and redeploy from a clean image.

---

## 🧠 Tricky Interview Question
`docker diff` on a container shows only 3 changed files, yet the host disk usage for that container is 5 GB. Where is the data?

Answer: Large data is likely in a mounted volume or bind mount (not included in diff), or in container logs (`/var/lib/docker/containers/<id>/*-json.log`, which belongs to the host, not the container layer). Check `docker system df -v`, `docker volume ls` and log rotation settings (`max-size`, `max-file`).

---

## ⚫ Interview Questions + Answers

Q1: What do A, C and D mean?
A1: Added, Changed, Deleted relative to the image the container was created from.

Q2: Can diff show changes to a stopped container?
A2: Yes, as long as the container still exists (not removed).

Q3: Why do deleted image files show as D and not disappear?
A3: Image layers are immutable; deletion is recorded as a whiteout marker in the top layer and shown as D.

Q4: How do you reduce the writable layer growth?
A4: Use volumes for data, tmpfs for temp, `read_only: true`, log rotation, and avoid installing packages at runtime.

Q5: Relationship to `docker commit`?
A5: `commit` would turn exactly this diff layer into a new image layer; diff lets you review it first.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Finding which paths need volumes.
- Investigating disk growth or suspicious changes.
- Verifying a read-only filesystem plan.

❌ Avoid when:
- You need image-level analysis (use `docker history`).
- Data lives in volumes (diff will not show it).
- Expecting content diff (it lists paths, not file contents).

---

## 📊 Visual Diagram
```
   +--------------------------------+
   | WRITABLE LAYER (per container) |  <-- docker diff reads this
   |  A /tmp/new.txt                |
   |  C /etc/nginx/nginx.conf       |
   |  D /etc/nginx/conf.d/default   |
   +--------------------------------+
   | image layer 3: app code        |  read-only
   | image layer 2: pip/npm deps    |  read-only
   | image layer 1: OS base         |  read-only
   +--------------------------------+
   Volume /app/data  (outside, not in diff)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Copy-on-write | Copy file to top layer when first modified | बदलने पर ही copy करना |
| Whiteout | Marker for deleted lower-layer file | हटाई फ़ाइल का marker |
| overlay2 | Default storage driver | Default storage driver |
| Drift | Difference from image | Image से अंतर |
| tmpfs | RAM-backed temp filesystem | RAM आधारित अस्थायी storage |
| read_only | Compose flag for read-only root fs | Root fs को read-only करना |

---

## ⚡ 3-Line Summary
English: `docker diff` shows A/C/D changes in a container's writable layer. It reveals hidden writes, disk growth and possible tampering. Move needed data to volumes and make the rest read-only.
Hindi: `docker diff` container की writable layer के A/C/D बदलाव दिखाता है। इससे छुपे हुए writes, disk growth और छेड़छाड़ पता चलती है। ज़रूरी data volumes में रखो और बाकी को read-only करो।

---

## ➡️ Next Topic
**70. docker commit (why avoid it)** — diff की layer को image बना देने वाला command, और इसे production में क्यों नहीं अपनाना चाहिए।
