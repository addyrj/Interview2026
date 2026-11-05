---

# 061. docker rm + docker rmi
# हिंदी में: docker rm और docker rmi

---

## 🔵 Simple Definition (English)
`docker rm` deletes **containers** (stopped ones, or running ones with `-f`). `docker rmi` (same as `docker image rm`) deletes **images** from the local machine. Neither deletes named volumes by default.

## 🔵 सरल परिभाषा (Hindi)
`docker rm` **containers** delete करता है (रुके हुए, या चलते हुए `-f` के साथ)। `docker rmi` (यानी `docker image rm`) local machine से **images** delete करता है। दोनों में से कोई भी named volumes को default रूप से delete नहीं करता।

---

## 🔴 Problem it Solves
Every deploy leaves old images; every `docker run` without `--rm` leaves a stopped container. On a 25 GB VPS this fills the disk in weeks, and then Docker, the database and SSH all start failing with "no space left on device". Removing what you do not need keeps the host healthy.

## 🔴 यह क्यों बना? (Hindi)
हर deploy पुराने images छोड़ जाता है; `--rm` के बिना हर `docker run` एक रुका हुआ container छोड़ता है। 25 GB के VPS पर हफ्तों में disk भर जाती है, और फिर Docker, database और SSH सब "no space left on device" से fail होने लगते हैं। जो चीज़ें ज़रूरी नहीं उन्हें हटाने से host स्वस्थ रहता है।

---

## 🟢 How it Works — Step by Step

```
docker rm
Step 1 → Daemon checks the container is stopped (running ones need -f, which kills first)
Step 2 → Removes the container's writable layer, metadata and logs
Step 3 → Anonymous volumes are removed only with -v; named volumes are kept

docker rmi
Step 1 → Daemon checks no container (even stopped) uses the image
Step 2 → If the image has several tags, removing one tag only untags it ("Untagged: ...")
Step 3 → When the last tag goes, layers not shared by other images are deleted ("Deleted: sha256:...")
Step 4 → -f forces removal of a tagged image used by stopped containers; running ones still block it
```

## 🟢 कैसे काम करता है? (Hindi)

```
docker rm
Step 1 → Daemon देखता है container रुका है (चलते हुए के लिए -f, जो पहले kill करता है)
Step 2 → Container की writable layer, metadata और logs हटाता है
Step 3 → Anonymous volumes सिर्फ -v से हटते हैं; named volumes बचे रहते हैं

docker rmi
Step 1 → Daemon देखता है कोई container (रुका हुआ भी) उस image को use तो नहीं कर रहा
Step 2 → Image के कई tags हों तो एक tag हटाने पर सिर्फ untag होता है ("Untagged: ...")
Step 3 → आखिरी tag हटने पर वे layers delete होती हैं जो दूसरी images में share नहीं हैं ("Deleted: sha256:...")
Step 4 → -f tagged image को हटवाता है जिसे रुके containers use करते थे; चलते containers फिर भी रोकते हैं
```

---

## 🟡 Real World Example
Your GitHub Actions pipeline deploys a new `api:<git-sha>` image to the VPS every commit. After two months there are 150 old images (about 300 MB each = 45 GB) and the VPS stops accepting deploys. A weekly cron `docker image prune -af --filter "until=168h"` frees the space while keeping the images from the last week for fast rollback. Companies like Razorpay keep the last N versions for rollback and delete the rest.

## 🟡 Real Example Hindi mein
आपकी GitHub Actions pipeline हर commit पर VPS पर नया `api:<git-sha>` image deploy करती है। दो महीने बाद 150 पुराने images हैं (लगभग 300 MB प्रत्येक = 45 GB) और VPS deploys लेना बंद कर देता है। हर हफ्ते चलने वाला cron `docker image prune -af --filter "until=168h"` जगह खाली करता है और पिछले हफ्ते के images जल्दी rollback के लिए रखता है। Razorpay जैसी कंपनियाँ rollback के लिए आखिरी N versions रखती हैं और बाकी हटा देती हैं।

---

## 💻 Code / Config Example — Basic

```bash
# --- Removing containers ---
docker rm web                                    # remove a stopped container by name
docker rm -f web                                 # force: kill if running, then remove
docker rm -v web                                 # also remove anonymous volumes of that container
docker rm web db cache                           # remove several at once
docker rm $(docker ps -aq --filter "status=exited")   # remove all exited containers
docker container prune                           # remove all stopped containers (asks to confirm)
docker container prune -f --filter "until=24h"   # no prompt, only those stopped >24h ago

# --- Removing images ---
docker images                                    # see what is present
docker rmi nginx:1.27-alpine                     # remove by name:tag (example tag)
docker rmi 3f8a4339aadd                          # remove by image ID
docker rmi -f myapi:old                          # force removal (when only stopped containers use it)
docker image prune                               # remove dangling images (<none>:<none>)
docker image prune -a                            # remove ALL images not used by any container
```

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# cleanup.sh - safe weekly cleanup on the VPS (run from cron). Keeps volumes untouched.
# Cron example: 0 3 * * 0 /srv/scripts/cleanup.sh >> /var/log/docker-cleanup.log 2>&1
set -euo pipefail                                # strict shell mode

echo "[$(date -Is)] disk before:"                # timestamp for the log
docker system df                                 # show usage by images/containers/volumes/cache

docker container prune -f --filter "until=24h"   # stopped containers older than a day
docker image prune -af --filter "until=168h"     # unused images older than 7 days (keeps rollback window)
docker builder prune -f --filter "until=168h"    # old BuildKit cache
# NOTE: we intentionally do NOT run "docker volume prune" or "docker system prune --volumes"

# Keep only the newest 5 tags of one repository (example repo name: myapi)
docker images myapi --format '{{.ID}} {{.CreatedAt}} {{.Tag}}' \
  | sort -k2,3 -r \
  | awk 'NR>5 {print $1}' \
  | sort -u \
  | xargs -r docker rmi 2>/dev/null || true      # images still in use are refused by Docker, which is fine

echo "[$(date -Is)] disk after:"
docker system df                                 # compare
```

```yaml
# .github/workflows/deploy.yml - clean old images after a successful deploy
name: deploy                                     # workflow name
on:
  push:
    branches: [main]                             # deploy on main
jobs:
  deploy:
    runs-on: ubuntu-latest                       # GitHub runner
    steps:
      - name: Deploy and clean                   # SSH to VPS
        uses: appleboy/ssh-action@v1.0.3         # example version
        with:
          host: ${{ secrets.VPS_HOST }}          # VPS IP from secrets
          username: deploy                       # user with docker access
          key: ${{ secrets.VPS_SSH_KEY }}        # private key from secrets
          script: |                              # commands on server
            cd /srv/app
            docker compose pull
            docker compose up -d
            docker image prune -f
```

---

## 🟠 My Stack Integration
- **Compose**: `docker compose down` removes containers and networks; add `--rmi local` to remove locally built images, `-v` to remove volumes (dangerous).
- **Node.js/React builds**: multi-stage builds leave dangling intermediate images; `docker image prune` cleans them.
- **FastAPI**: tag by git SHA, keep last 5 for rollback.
- **Nginx**: never `rm -f` the proxy during peak traffic without a replacement; use `docker compose up -d` to recreate.
- **AWS ECR**: remote cleanup uses ECR lifecycle policies; `docker rmi` only cleans the local host.

```yaml
# docker-compose.yml - one-off jobs that clean themselves up (no stopped-container buildup)
services:
  migrate:
    image: ghcr.io/example/api:1.4.2             # example image
    command: ["alembic", "upgrade", "head"]      # run DB migrations
    profiles: ["tools"]                          # not started by plain "up"
    restart: "no"                                # run once
# run with: docker compose run --rm migrate  (--rm deletes the container afterwards)
```

Security: old images keep old vulnerable libraries and may contain leaked secrets in layers; deleting them reduces attack surface, but rebuild with fixed dependencies too. Never run `docker rm -f $(docker ps -aq)` on a shared production host. Restrict docker access, because `rm -f` on a running container is a service outage.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `docker system prune -a --volumes` on production, wiping an unused-looking DB volume.
✅ Correct: Prune containers/images only, with age filters; back up and label important volumes.

❌ Mistake 2: Trying `docker rmi` and getting "image is being used by stopped container".
✅ Correct: `docker rm` that container first (or `docker container prune`), then `docker rmi`.

❌ Mistake 3: Using `rm -f` to "restart" a service.
✅ Correct: `docker compose up -d --force-recreate service` or `docker restart`.

❌ Mistake 4: Deleting all images before a deploy, making rollback impossible and re-pulling everything.
✅ Correct: Keep a rollback window (last 3-5 versions).

---

## 🧠 Tricky Interview Question
You ran `docker rmi myapi:1.0` and Docker printed only `Untagged: myapi:1.0`, and disk space did not shrink. Why?

Answer: The same image ID has another tag (for example `myapi:latest`) or is the parent of another image, so only that tag was removed. Layers are deleted only when no tag or container references the image. Remove all tags (`docker rmi myapi:latest`) or use `docker image prune -a`, and check with `docker images --digests` and `docker system df`.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `docker rm` and `docker rmi`?
A1: `rm` removes containers; `rmi` removes images.

Q2: What is a dangling image?
A2: An image with no tag (`<none>:<none>`), usually left over after rebuilding a tag. `docker image prune` removes dangling images; `-a` also removes unused tagged images.

Q3: Does `docker rm` delete data stored in a named volume?
A3: No. Named volumes remain; `-v` removes only anonymous volumes of that container.

Q4: How do you make a container delete itself on exit?
A4: `docker run --rm`.

Q5: How do you free disk on a full VPS safely?
A5: Check `docker system df`, prune stopped containers and old images with `--filter until=`, rotate logs, prune build cache; avoid pruning volumes unless backed up.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Cleaning after deploys/CI, freeing disk, deleting test containers.

❌ Avoid when:
- Force-removing production containers without a replacement.
- Pruning volumes or all images without understanding what depends on them.

---

## 📊 Visual Diagram
```
 IMAGE  myapi (layers: A-B-C) tags: 1.0, latest
   |  docker run -> CONTAINER c1 (writable layer W1)
   |
 docker rm c1      -> W1 deleted, image stays, volumes stay
 docker rmi myapi:1.0    -> "Untagged" (tag latest still points to A-B-C)
 docker rmi myapi:latest -> "Untagged" + "Deleted" layers C, B, A (if unshared)

 order: stop -> rm container -> rmi image -> (optionally) prune cache
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Untag | Remove a name from an image | Image से नाम हटाना |
| Dangling image | Image with no tag | बिना tag वाली image |
| Prune | Bulk delete unused objects | बेकार objects को एक साथ हटाना |
| Writable layer | Container's temporary changes | Container के अस्थायी बदलाव |
| Build cache | Saved build steps | Build के सहेजे गए steps |
| Rollback window | Old versions kept for recovery | Recovery के लिए रखे पुराने versions |

---

## ⚡ 3-Line Summary
English: `docker rm` deletes containers, `docker rmi` deletes images, volumes are not touched by default.
Automate age-based pruning so the disk never fills up.
Never prune volumes or force-remove production containers casually.
Hindi: `docker rm` containers हटाता है, `docker rmi` images, और volumes default में सुरक्षित रहते हैं।
Age-based pruning automate करें ताकि disk कभी न भरे।
Volumes prune या production containers को लापरवाही से force-remove न करें।

---

## ➡️ Next Topic
**062. docker logs.** Before deleting a crashed container, read its logs to learn why it died.

---
