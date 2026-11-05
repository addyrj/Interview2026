# 102. Union File System
# हिंदी में: Union File System

---

## 🔵 Simple Definition (English)
A union file system merges several directories (layers) into one single view. Docker uses it (today `overlay2` on Linux) to stack the read-only image layers and one writable container layer, using copy-on-write when a file is modified.

## 🔵 सरल परिभाषा (Hindi)
Union file system कई directories (layers) को मिलाकर एक single view बनाता है। Docker इसे (आजकल Linux पर `overlay2`) इस्तेमाल करता है ताकि read-only image layers और एक writable container layer को stack करे, और file बदलने पर copy-on-write होता है।

---

## 🔴 Problem it Solves
Starting a container by copying a whole 500 MB image directory would take seconds and waste disk per container. 50 containers from one image would need 25 GB. Union mounting lets all 50 containers share the same read-only layers and only store their own small changes, so containers start in milliseconds.

## 🔴 यह क्यों बना? (Hindi)
Container शुरू करने के लिए पूरी 500 MB image directory copy करने में सेकंड लगते और हर container पर disk बर्बाद होती। एक image से 50 containers के लिए 25 GB चाहिए होते। Union mount से सारे 50 containers वही read-only layers share करते हैं और सिर्फ अपने छोटे बदलाव store करते हैं, इसलिए containers milliseconds में start होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → lowerdir = read-only image layers (colon separated list)
Step 2 → upperdir = container's writable layer
Step 3 → workdir  = scratch dir overlayfs needs
Step 4 → merged   = the unified view the container sees as "/"
Step 5 → Read: top-most layer containing the file wins
Step 6 → Write to a lower file: copy-up to upperdir, then modify (CoW)
Step 7 → Delete: whiteout file in upperdir hides the lower file
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → lowerdir = read-only image layers (colon से अलग list)
Step 2 → upperdir = container की writable layer
Step 3 → workdir  = overlayfs की scratch dir
Step 4 → merged   = container को "/" के रूप में दिखने वाला एकीकृत view
Step 5 → Read: जिस सबसे ऊपरी layer में file है वही जीतती है
Step 6 → नीचे की file में write: upperdir में copy-up, फिर बदलाव (CoW)
Step 7 → Delete: upperdir में whiteout file नीचे की file छुपा देती है
```

---

## 🟡 Real World Example
A VPS ran 30 containers from the same Node image. `df` showed only 600 MB used instead of 30 x 160 MB. One container wrote 2 GB of logs into its writable layer (not a volume); the disk filled up and `/var/lib/docker/overlay2` was the culprit. Fix: log to stdout with rotation (`max-size`), and move uploads to a volume.

## 🟡 Real Example Hindi mein
एक VPS पर एक ही Node image से 30 containers चल रहे थे। `df` में 30 x 160 MB की जगह सिर्फ 600 MB use दिखा। एक container ने अपनी writable layer में (volume में नहीं) 2 GB logs लिख दिए; disk भर गई और `/var/lib/docker/overlay2` दोषी निकला। Fix: logs को stdout पर रोटेशन (`max-size`) के साथ भेजो और uploads volume में रखो।

---

## 💻 Code / Config Example — Basic

```bash
# See which storage driver Docker uses (usually overlay2)
docker info --format '{{.Driver}}'

# Start a container and look at its overlay paths
docker run -d --name demo alpine sleep 3600               # tiny long-running container
docker inspect demo --format '{{json .GraphDriver.Data}}' # shows LowerDir, UpperDir, MergedDir, WorkDir

# Create a file in the container: it lands in UpperDir only
docker exec demo sh -c 'echo hello > /new.txt'            # write inside container
docker diff demo                                          # A /new.txt (A=Added)

# Modify a base file: copy-up happens
docker exec demo sh -c 'echo x >> /etc/hostname'          # change existing file
docker diff demo                                          # C /etc (Changed)

# Cleanup: the writable layer disappears with the container
docker rm -f demo                                         # remove container and its upper layer
```

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# overlay-demo.sh - reproduce Docker's union mount by hand (Linux only, needs root)
# Not run on the machine where these notes were written; run it on a Linux VPS.
set -euo pipefail                       # stop on error, unset variable, pipe failure

BASE=$(mktemp -d)                       # temp workspace
mkdir -p "$BASE"/{lower,upper,work,merged}   # four overlay directories

echo "from image layer" > "$BASE/lower/app.txt"   # file that lives in the read-only layer
echo "base config"      > "$BASE/lower/conf.txt"  # another read-only file

# mount the union: lowerdir read-only, upperdir writable
sudo mount -t overlay overlay \
  -o lowerdir="$BASE/lower",upperdir="$BASE/upper",workdir="$BASE/work" \
  "$BASE/merged"

cat "$BASE/merged/app.txt"              # reads from lower -> "from image layer"

echo "modified" >> "$BASE/merged/app.txt"   # write triggers copy-up (CoW)
echo "lower still: $(cat "$BASE/lower/app.txt")"   # lower is untouched
echo "upper has : $(cat "$BASE/upper/app.txt")"    # upper has the modified copy

rm "$BASE/merged/conf.txt"              # delete a lower file
ls -l "$BASE/upper"                     # shows a whiteout (character device 0/0) named conf.txt
ls "$BASE/merged"                       # conf.txt is hidden from the merged view

sudo umount "$BASE/merged"              # unmount the union
rm -rf "$BASE"                          # cleanup (upper/lower removed; needs sudo if root-owned files)
```

```yaml
# docker-compose.yml - keep writes out of the overlay (performance + disk safety)
services:
  api:
    image: myorg/api:1.0.0              # image layers are read-only lowerdirs
    logging:
      driver: json-file                 # default logging driver
      options:
        max-size: "10m"                 # rotate each log file at 10 MB
        max-file: "3"                   # keep 3 files only
    volumes:
      - uploads:/app/uploads            # bypasses overlay: native disk speed, persistent
    tmpfs:
      - /tmp                            # RAM disk for temp data
volumes:
  uploads: {}                           # named volume lives outside the container layer
```

---

## 🟠 My Stack Integration
**Node.js / FastAPI**: write logs to stdout, uploads to volumes; never write in the container layer. **Databases (Postgres/MongoDB)**: always on volumes, since overlay CoW is slow for heavy random writes. **VPS**: monitor `/var/lib/docker` with `docker system df` and prune. **AWS**: on EC2 put `/var/lib/docker` on a large EBS volume; on Fargate you get ephemeral storage (20 GB default) shared by container layers.

```yaml
# crontab-like cleanup via GitHub Actions deploy step (snippet)
- name: Prune old images on VPS            # step name
  run: ssh deploy@vps "docker image prune -af --filter 'until=168h'"   # remove images unused for 7 days
```

Security: container layers are mounted on the host at `/var/lib/docker/overlay2`, readable by host root; do not store secrets in the writable layer. Read-only roots (topic 100) block writes to the upper layer.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Writing heavy data (DB files, logs, uploads) into the container layer.
✅ Correct: Use volumes or bind mounts; overlay copy-on-write is slow and data is lost on `docker rm`.

❌ Mistake 2: Assuming `rm` in a later layer frees space.
✅ Correct: Lower layers keep the data; a whiteout only hides it.

❌ Mistake 3: Never pruning `/var/lib/docker`.
✅ Correct: Schedule `docker image prune` / `docker system df` checks.

---

## 🧠 Tricky Interview Question
A 2 GB file exists in the image. In a running container you change 1 byte of it. How much extra disk is used and why does the first write feel slow?

Answer: With overlay2, copy-up works at file level, so the entire 2 GB file is copied to the upper layer before the write, so about 2 GB extra and a delay on the first write. Later writes go to the copy. That is why big mutable files (databases) must live in volumes.

---

## ⚫ Interview Questions + Answers

Q1: What is overlay2?
A1: The default Docker storage driver on modern Linux, built on the kernel's OverlayFS, merging lowerdir layers and an upperdir.

Q2: What is copy-on-write?
A2: Data is shared until modified; at modification time it is copied to the writable layer first.

Q3: What is a whiteout?
A3: A special marker in the upper layer that hides a file from lower layers, how deletions are represented.

Q4: Why do volumes perform better than the container layer?
A4: They bypass the union filesystem and use the host filesystem directly.

Q5: Is the data in the container layer persistent?
A5: No, it is deleted with the container (`docker rm`), though it survives stop/start.

---

## 🔷 When to Use + When Not to Use
✅ Use (rely on it) when:
- Normal stateless containers; it is automatic.
- You need fast start and shared base layers.

❌ Avoid writing through it when:
- Databases, heavy logging, user uploads.
- Performance-sensitive random I/O.

---

## 📊 Visual Diagram
```
   Container's view of "/"   (merged)
   +--------------------------------------+
   |  /new.txt    from  upperdir (RW)     |  <- container layer
   |  /app.txt    modified copy in upper  |
   +--------------------------------------+
   |  lowerdir 3: COPY . .      (RO)      |
   |  lowerdir 2: RUN npm ci    (RO)      |  <- image layers, shared
   |  lowerdir 1: node:20-alpine (RO)     |
   +--------------------------------------+
   read: top-down search    write: copy-up    delete: whiteout
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OverlayFS | Linux union filesystem | Linux का union filesystem |
| lowerdir / upperdir | Read-only / writable directories | read-only / writable directories |
| Copy-on-write | Copy only when modified | बदलते समय ही copy |
| Whiteout | Marker hiding a deleted file | delete हुई file छुपाने वाला marker |
| Storage driver | Component managing layers | layers manage करने वाला component |

---

## ⚡ 3-Line Summary
English: A union filesystem presents stacked layers as one directory, overlay2 in Docker.
Reads search top-down, writes copy up the file, deletes use whiteouts.
Keep heavy writes in volumes, not the container layer.
Hindi: Union filesystem stacked layers को एक directory की तरह दिखाता है, Docker में overlay2।
Read ऊपर से नीचे खोजता है, write में file copy-up होती है, delete whiteout से होता है।
भारी writes volumes में रखो, container layer में नहीं।

---

## ➡️ Next Topic
**103. Image Manifest**: the JSON document that lists an image's layers and config for registries.
