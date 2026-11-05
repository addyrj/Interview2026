# 68. docker cp
# हिंदी में: docker cp (Container और Host के बीच files copy करना)

---

## 🔵 Simple Definition (English)
`docker cp` copies files or folders between a container's filesystem and the host's filesystem, in either direction. It works on running and stopped containers and does not need the container to have `cp` or `tar` installed.

## 🔵 सरल परिभाषा (Hindi)
`docker cp` container के filesystem और host के filesystem के बीच files या folders copy करता है, दोनों दिशाओं में। यह running और stopped दोनों containers पर चलता है और container में `cp` या `tar` होना ज़रूरी नहीं।

---

## 🔴 Problem it Solves
Containers are isolated; their filesystem is not directly visible from the host. When a FastAPI container crashes you may need its log file, a generated report, a core dump or a SQLite file. Or you want to drop a hotfix config in for a quick test. Without `docker cp` you would need `exec` + `cat` hacks or to rebuild the image and lose the crash state.

## 🔴 यह क्यों बना? (Hindi)
Containers isolated होते हैं; उनका filesystem host से सीधे नहीं दिखता। FastAPI container crash होने पर आपको उसकी log file, generated report, core dump या SQLite file चाहिए हो सकती है। या किसी config को जल्दी test करना हो। `docker cp` के बिना `exec` + `cat` जैसे jugaad या image दोबारा build करना पड़ता, और crash की state खो जाती।

---

## 🟢 How it Works — Step by Step

```
Step 1 → docker cp CONTAINER:SRC_PATH HOST_DEST   (container -> host)
Step 2 → or docker cp HOST_SRC CONTAINER:DEST_PATH (host -> container)
Step 3 → Docker daemon reads the container's merged filesystem (via tar stream)
Step 4 → Files are streamed back/forward through the Docker API socket
Step 5 → Ownership/permissions: files copied in are owned by root unless you use -a
Step 6 → Mounted volumes are NOT included when copying from a container path under a mount
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → docker cp CONTAINER:SRC_PATH HOST_DEST   (container से host)
Step 2 → या docker cp HOST_SRC CONTAINER:DEST_PATH (host से container)
Step 3 → Docker daemon container का merged filesystem tar stream की तरह पढ़ता है
Step 4 → Files Docker API socket से आगे-पीछे stream होती हैं
Step 5 → Permissions: अंदर copy की गई files root की होती हैं, -a से source का owner रहता है
Step 6 → Volume mount वाले paths के लिए container से copy करने पर mount की files नहीं आतीं
```

---

## 🟡 Real World Example
A payment-reconciliation Node.js job container exits with an error at 3 AM. Next morning you run `docker cp recon-job:/app/output/report.csv ./report.csv` to rescue the partial CSV from the stopped container, then `docker cp recon-job:/app/logs ./logs` to read the stack trace. For nginx, you copy the default config out (`docker cp nginx:/etc/nginx/nginx.conf .`) to use it as a starting template.

## 🟡 Real Example Hindi mein
रात 3 बजे एक payment-reconciliation Node.js job container error से exit हो जाता है। अगली सुबह आप `docker cp recon-job:/app/output/report.csv ./report.csv` से stopped container से अधूरी CSV बचा लेते हो, और `docker cp recon-job:/app/logs ./logs` से stack trace पढ़ते हो। Nginx के लिए default config बाहर निकालकर (`docker cp nginx:/etc/nginx/nginx.conf .`) अपनी template बना सकते हो।

---

## 💻 Code / Config Example — Basic
```bash
# ---- Basic docker cp ----
docker run -d --name demo nginx:1.27-alpine           # start a sample container (example tag)
docker cp demo:/etc/nginx/nginx.conf ./nginx.conf     # container -> host: copy one file into current dir
docker cp demo:/usr/share/nginx/html ./html-backup    # container -> host: copy a whole directory
echo "hello" > hello.txt                              # create a small test file on host
docker cp hello.txt demo:/usr/share/nginx/html/       # host -> container: put file into web root
docker exec demo cat /usr/share/nginx/html/hello.txt  # verify the file is inside the container
docker cp demo:/etc/nginx/. ./nginx-conf/             # trailing "/." copies directory CONTENTS only
docker rm -f demo                                     # cleanup the demo container
```

## 💻 Code / Config Example — Advanced
```bash
#!/usr/bin/env bash
# collect-crash-data.sh -- grab evidence from a crashed container before removing it
set -euo pipefail                                        # fail on error, unset var, pipe failure
C="${1:?usage: collect-crash-data.sh <container>}"       # container name or id (required)
OUT="crash-$(date +%Y%m%d-%H%M%S)-$C"                    # timestamped output folder name
mkdir -p "$OUT"                                          # create folder for evidence
docker inspect "$C" > "$OUT/inspect.json"                # save full container metadata (env, mounts, exit code)
docker logs --timestamps "$C" > "$OUT/stdout-stderr.log" 2>&1  # save logs with timestamps
docker cp "$C:/app/logs" "$OUT/app-logs" || echo "no /app/logs"   # copy app logs, continue if missing
docker cp -a "$C:/app/output" "$OUT/output" || true      # -a keeps uid/gid of the source files
docker diff "$C" > "$OUT/fs-changes.txt"                 # record what changed in filesystem (see topic 69)
tar czf "$OUT.tar.gz" "$OUT"                             # compress evidence for sharing
echo "Saved $OUT.tar.gz"                                 # tell the operator where the file is
```
`bash -n` syntax check done; actual copy behaviour not run locally (no Docker daemon here). `-a` and `-L` flags exist in `docker cp`; confirm with `docker cp --help` on your version.

---

## 🟠 My Stack Integration
Use `docker cp` for debugging, not for deployment. Deployment goes through images and volumes.

```yaml
# docker-compose.yml -- the right way for persistent data, so you rarely need cp for it
services:                                    # stack services
  api:                                       # FastAPI app
    image: ghcr.io/addyrj/api:9fceb02        # pinned example image
    volumes:                                 # persistent / shared paths
      - api-logs:/app/logs                   # logs survive container removal
      - ./nginx/conf.d:/etc/nginx/conf.d:ro  # config mounted read-only instead of docker cp
volumes:                                     # named volume declarations
  api-logs:                                  # managed by Docker, backed up separately
```
On the VPS: `docker cp api:/app/logs/error.log /tmp/` then `scp` it to your laptop. To hot-test an Nginx config: `docker cp ./site.conf nginx:/etc/nginx/conf.d/` then `docker exec nginx nginx -s reload` (changes are lost when the container is recreated).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `docker cp` to "deploy" new code into a container.
✅ Correct: Rebuild the image and redeploy; copied files vanish on recreate and drift from Git.

❌ Mistake 2: Expecting files in a bind mount or volume to be copied out.
✅ Correct: Read them from the host mount path, or use a temporary container (`docker run --rm -v vol:/d -v $PWD:/b alpine cp -a /d /b`).

❌ Mistake 3: Wrong trailing slash semantics (`./dir` vs `./dir/.`) causing nested folders.
✅ Correct: Use `src/.` to copy contents; test with `ls` after copy.

❌ Mistake 4: Copying secrets (`.env`) out and leaving them on a shared server.
✅ Correct: Delete after use, restrict permissions (`chmod 600`), never commit.

---

## 🧠 Tricky Interview Question
You `docker cp` a new `settings.json` into a running container and the app picks it up. After `docker compose up -d --force-recreate` the old settings are back. Why, and how do you fix it permanently?

Answer: The copy writes into the container's writable layer, which is discarded when the container is recreated; the image still has the old file. Fix by baking the file into the image (`COPY` in Dockerfile) or mounting it as a bind mount/config in Compose, so it is version-controlled.

---

## ⚫ Interview Questions + Answers

Q1: Does `docker cp` work on a stopped container?
A1: Yes. Unlike `docker exec`, it only needs the container's filesystem to exist, so it works on stopped (not yet removed) containers.

Q2: Does it need `tar` inside the image?
A2: No. The daemon creates the tar stream itself; this is why it works on distroless/scratch images.

Q3: How do you copy from one container to another?
A3: Not directly. Copy to host first (`docker cp a:/f .` then `docker cp ./f b:/f`), or share a volume.

Q4: What happens to file ownership when copying in?
A4: Files are owned by root inside the container unless `-a` (archive mode) preserves uid/gid from source.

Q5: How is it different from a bind mount?
A5: `cp` is a one-time snapshot copy; a bind mount is a live shared path that reflects changes both ways.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Retrieving logs/dumps/reports from crashed containers.
- Extracting default configs as templates.
- Quick one-off tests of a config file.

❌ Avoid when:
- Deploying or updating application code.
- Syncing frequently changing data (use volumes).
- Backing up databases (use `pg_dump`/`mongodump`).

---

## 📊 Visual Diagram
```
        HOST (VPS)                                  CONTAINER (api)
   +-----------------+        docker cp           +------------------+
   | /home/ubuntu/   | <-------------------------- | /app/logs/err.log|
   |   err.log       |   (tar stream via daemon)   |                  |
   |                 | --------------------------> | /app/config.json |
   +-----------------+   docker cp ./config.json   +------------------+
                        api:/app/   (lost on recreate!)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Writable layer | Top layer where container changes live | Container की लिखने योग्य layer |
| Bind mount | Host path shared live into container | Host path का live share |
| Volume | Docker-managed persistent storage | Docker का persistent storage |
| Tar stream | Archive format used for transfer | Transfer में इस्तेमाल archive |
| Archive mode (-a) | Preserve uid/gid | Owner/group बनाए रखना |
| Ephemeral | Lost when container is removed | अस्थायी |

---

## ⚡ 3-Line Summary
English: `docker cp` copies files between host and container, even stopped ones, with no tools needed inside. It is great for debugging and extracting logs. Copied-in files are temporary; deploy through images and volumes.
Hindi: `docker cp` host और container के बीच files copy करता है, stopped container में भी, अंदर किसी tool के बिना। Debugging और logs निकालने के लिए बढ़िया है। अंदर copy की गई files अस्थायी हैं; deploy images और volumes से करो।

---

## ➡️ Next Topic
**69. docker diff** — container में क्या-क्या files बदली/जुड़ी/हटीं, यह देखकर समझेंगे कि writable layer में असल में क्या होता है।
