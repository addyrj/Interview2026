# 118. Dangling Images
# हिंदी में: Dangling Images (बिना नाम वाली बची हुई images)

---

## 🔵 Simple Definition (English)
A dangling image is an image layer set that has **no tag and no name** (shown as `<none>:<none>`) because a newer build took over its tag. It is not used by any container, but it still eats disk space until you remove it.

## 🔵 सरल परिभाषा (Hindi)
Dangling image वह image है जिसका **कोई tag या नाम नहीं** बचा (`<none>:<none>` दिखता है) क्योंकि नए build ने उसका tag ले लिया। कोई container इसे इस्तेमाल नहीं करता, फिर भी जब तक आप हटाएँ नहीं यह disk घेरती रहती है।

---

## 🔴 Problem it Solves
Understanding dangling images solves the "disk full on VPS" problem:
- Every `docker build -t api:latest .` retags the new image; the old one becomes `<none>`.
- A CI server or a small VPS building 20 times a day collects gigabytes of dead images.
- Disk full means Docker cannot write layers, containers crash, logs stop, and the database may fail to write.
- Teams confuse "dangling" (no tag) with "unused" (no container). They are different and need different cleanup commands.

## 🔴 यह क्यों बना? (Hindi)
Dangling images समझने से "VPS पर disk full" की समस्या हल होती है:
- हर `docker build -t api:latest .` नई image को वही tag दे देता है; पुरानी `<none>` बन जाती है।
- दिन में 20 बार build करने वाला CI server या छोटा VPS GB-भर मरी हुई images जमा कर लेता है।
- Disk full होने पर Docker layers नहीं लिख पाता, containers crash होते हैं, logs रुकते हैं, database भी write नहीं कर पाता।
- लोग "dangling" (tag नहीं) और "unused" (container नहीं) को एक समझ लेते हैं। ये अलग हैं और इनके cleanup commands भी अलग हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You build api:latest (image ID aaa111). Tag "latest" -> aaa111
Step 2 → You change code and build api:latest again (image ID bbb222)
Step 3 → Docker MOVES the tag "latest" from aaa111 to bbb222
Step 4 → aaa111 now has no tag -> shown as <none>:<none> = DANGLING
Step 5 → docker images -f dangling=true lists it
Step 6 → docker image prune removes only dangling images
Step 7 → docker image prune -a removes ALL images not used by any container (bigger hammer)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप api:latest build करते हैं (image ID aaa111). Tag "latest" -> aaa111
Step 2 → code बदलकर फिर api:latest build करते हैं (image ID bbb222)
Step 3 → Docker tag "latest" को aaa111 से हटाकर bbb222 पर ले जाता है
Step 4 → aaa111 का अब कोई tag नहीं -> <none>:<none> = DANGLING
Step 5 → docker images -f dangling=true से यह दिखती है
Step 6 → docker image prune सिर्फ dangling images हटाता है
Step 7 → docker image prune -a उन सभी images को हटाता है जो किसी container में use नहीं हो रहीं (बड़ा हथौड़ा)
```

---

## 🟡 Real World Example
A developer runs a Node.js API on a 25 GB EC2 t3.small. A GitHub Actions deploy job SSHes in, runs `docker build -t api:latest .` and restarts. After three weeks `df -h` shows 100 percent and the deploy fails with "no space left on device". `docker system df` shows 14 GB of reclaimable images, most of them `<none>`. A weekly cron with `docker image prune -f` and a deploy step that prunes after success fixes it permanently.

## 🟡 Real Example Hindi mein
एक developer 25 GB की EC2 t3.small पर Node.js API चलाता है। GitHub Actions का deploy job SSH करके `docker build -t api:latest .` चलाता और restart करता है। तीन हफ्ते बाद `df -h` 100 percent दिखाता है और deploy "no space left on device" से fail होता है। `docker system df` में 14 GB reclaimable images हैं, ज़्यादातर `<none>`। हर हफ्ते की cron में `docker image prune -f` और deploy सफल होने के बाद prune step लगाने से समस्या हमेशा के लिए खत्म।

---

## 💻 Code / Config Example — Basic
```bash
# Show disk usage split by images, containers, volumes, build cache
docker system df

# List only dangling images (no tag) - these are safe prune candidates
docker images -f dangling=true

# Same but print just IDs (handy for scripts)
docker images -q -f dangling=true

# Remove dangling images; -f skips the "are you sure" prompt
docker image prune -f

# Remove dangling AND every image no container uses (be careful on a shared box)
docker image prune -a -f

# Remove only unused images older than 7 days (168h) - safer than plain -a
docker image prune -a -f --filter "until=168h"

# Show why an image is <none>: see its layers and parent history
docker history <IMAGE_ID>
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/deploy.yml  (example: update action versions before using)
name: deploy                                   # workflow name shown in the Actions tab
on:
  push:
    branches: [main]                           # run only when main branch gets a push
jobs:
  deploy:
    runs-on: ubuntu-latest                     # GitHub hosted runner
    steps:
      - name: Deploy and clean up on VPS
        uses: appleboy/ssh-action@v1.0.3       # SSH action (example version)
        with:
          host: ${{ secrets.VPS_HOST }}        # server IP kept in GitHub secrets
          username: ${{ secrets.VPS_USER }}    # non-root deploy user
          key: ${{ secrets.VPS_SSH_KEY }}      # private key from secrets, never in repo
          script: |                            # commands run on the VPS
            set -e                             # stop at first failing command
            cd /srv/myapp                      # project folder with docker-compose.yml
            docker compose pull                # fetch new images
            docker compose up -d               # recreate changed containers
            docker image prune -f              # remove dangling images AFTER containers switched
            docker image prune -a -f --filter "until=168h"  # drop unused images older than 7 days
            docker builder prune -f --filter "until=168h"   # drop old build cache too
            docker system df                   # log the final disk usage for debugging
```

```bash
# /etc/cron.weekly/docker-clean  (chmod +x). Weekly safety net on the VPS
#!/usr/bin/env bash                           # run with bash
set -euo pipefail                              # fail fast, error on unset vars
docker image prune -f                          # remove dangling images
docker container prune -f --filter "until=72h" # remove containers stopped more than 3 days ago
docker volume ls -qf dangling=true             # only LIST dangling volumes; never auto-delete DB data
```

---

## 🟠 My Stack Integration
- **Node.js / FastAPI:** each deploy builds a new image; with SHA tags (`api:3f9a1c2`) old versions keep a name (good for rollback) but pile up, so prune by age, not blindly.
- **React:** the multi-stage build leaves an intermediate builder stage; `docker builder prune` clears that cache.
- **Nginx / VPS:** put the prune in the deploy script after `docker compose up -d`, so the running image is protected.
- **AWS:** on ECS EC2 hosts set `ECS_IMAGE_CLEANUP_INTERVAL` and similar agent settings; for ECR use lifecycle policies for the registry side.

```yaml
# docker-compose.yml fragment: tag by SHA so builds do not create <none> for the same tag
services:
  api:                                         # Node.js / FastAPI service
    image: myorg/api:${GIT_SHA:-dev}           # unique tag per commit, default "dev" for local
    build: ./api                               # build context for local development
    restart: unless-stopped                    # survive reboot, stay stopped if you stop it
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running `docker system prune -a --volumes` on a production box to "clean up".
✅ Correct: `--volumes` can delete a stopped database container's volume data. Use `docker image prune` and filters; never prune volumes automatically.

❌ Mistake 2: Pruning BEFORE `docker compose up -d`, so the rollback image or the one about to start is gone.
✅ Correct: Prune after the new containers are healthy, and keep the last N tagged images for rollback.

❌ Mistake 3: Thinking dangling means unused and that `docker image prune` frees everything.
✅ Correct: Plain prune only removes untagged images. Tagged but unused images need `-a`.

❌ Mistake 4: Ignoring build cache, which can be larger than the images themselves.
✅ Correct: Check `docker system df` and run `docker builder prune` as well.

---

## 🧠 Tricky Interview Question
You run `docker image prune -f` and it frees nothing, yet `docker system df` says 12 GB reclaimable. Why?

Answer: The space is in images that still have tags (old `api:v1`, `api:v2`) but are not used by any container. `prune` without `-a` only deletes dangling (untagged) images. Use `docker image prune -a --filter "until=168h"`. Another source is build cache (`docker builder prune`). Also note an untagged image that is a parent layer of a tagged image is NOT shown as dangling and is not removable.

---

## ⚫ Interview Questions + Answers

Q1: What is a dangling image?
A1: An image with no repository name and tag (`<none>:<none>`), usually left when a new build re-used the tag. It is no longer referenced by name.

Q2: Difference between dangling and unused images?
A2: Dangling = no tag. Unused = no container references it (it may be tagged). `prune` removes dangling; `prune -a` removes all unused.

Q3: Can a running container use a dangling image?
A3: Yes. If you rebuilt the tag while the container ran, the container keeps using the old image, which is now `<none>`. Docker will refuse to remove it while the container exists.

Q4: How do you list and remove dangling images safely?
A4: `docker images -f dangling=true` to look, then `docker image prune -f`. In scripts prefer filters like `until=168h`.

Q5: How to avoid creating dangling images at all?
A5: Tag every build uniquely (git SHA or semver) instead of re-pushing `latest`, and use CI runners that are thrown away after each job so nothing accumulates.

---

## 🔷 When to Use + When Not to Use
✅ Use pruning when:
- Disk usage on a VPS or self-hosted runner grows after repeated builds.
- You added a post-deploy cleanup step in CD.
- You need to find out what `docker system df` calls reclaimable.

❌ Avoid when:
- Pruning with `-a` right before a rollback may be needed.
- Running `system prune --volumes` on a server holding database volumes.
- Several teams share one Docker host and an image may be needed by another project.

---

## 📊 Visual Diagram
```
 build #1                build #2 (same tag)
 +-----------+           +-----------+
 | api:latest|  ------>  | api:latest|   tag moves to new image
 |  aaa111   |           |  bbb222   |
 +-----------+           +-----------+
       |
       v
 +--------------+
 | <none>:<none>|  = DANGLING (aaa111)
 |   aaa111     |
 +--------------+
       |
 docker image prune -f
       v
   [ removed, disk freed ]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dangling image | Image with no tag/name | बिना tag वाली image |
| `<none>:<none>` | Display for untagged image | कोई नाम नहीं |
| Prune | Delete unused Docker objects | अनुपयोगी objects हटाना |
| Build cache | Saved build steps for reuse | build का cache |
| Reclaimable | Space Docker can free | वापस मिल सकने वाली जगह |
| `until=` filter | Only items older than a time | समय से पुराने items |

---

## ⚡ 3-Line Summary
English: A dangling image is an untagged leftover from a re-used tag.
English: `docker image prune` removes dangling ones; `-a` removes all unused ones.
English: Prune after deploy, by age, and never prune volumes automatically on production.
Hindi: Dangling image उस tag की बची हुई बिना नाम वाली पुरानी image है।
Hindi: `docker image prune` dangling हटाता है; `-a` सभी unused हटाता है।
Hindi: Deploy के बाद, उम्र के हिसाब से prune करें और production पर volumes कभी अपने आप prune न करें।

---

## ➡️ Next Topic
**119. Image Scanning (Trivy)** — cleaning old images saves disk; scanning the images you keep finds known vulnerabilities before they reach production.
