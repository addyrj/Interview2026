# 117. docker image prune
# हिंदी में: docker image prune

---

## 🔵 Simple Definition (English)
`docker image prune` deletes unused images. By default it removes only **dangling** images (untagged layers, shown as `<none>`). With `-a` it removes **all images not used by any container**. Filters like `--filter until=168h` limit it by age.

## 🔵 सरल परिभाषा (Hindi)
`docker image prune` unused images हटाता है। Default रूप में सिर्फ **dangling** images (बिना tag की layers, `<none>` दिखती हैं) हटाता है। `-a` के साथ **किसी भी container में इस्तेमाल न हो रही सारी images** हटाता है। `--filter until=168h` जैसे filters उम्र से सीमित करते हैं।

---

## 🔴 Problem it Solves
- Every deploy leaves the previous image on the VPS; after a few months a 20 GB disk is 100% full and Docker or Postgres fails to write.
- CI self-hosted runners accumulate gigabytes of intermediate images.
- Old images also keep old vulnerable libraries around.

## 🔴 यह क्यों बना? (Hindi)
- हर deploy पिछली image VPS पर छोड़ देता है; कुछ महीनों में 20 GB disk 100% भर जाती है और Docker या Postgres लिखना बंद कर देते हैं।
- Self-hosted CI runners पर GB भर intermediate images जमा हो जाती हैं।
- पुरानी images पुरानी vulnerable libraries भी रखे रहती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → See usage:        docker system df
Step 2 → Dangling only:    docker image prune          (asks for confirmation)
Step 3 → Skip prompt:      docker image prune -f
Step 4 → All unused:       docker image prune -a       (any image without a container)
Step 5 → Age filter:       docker image prune -a --filter "until=168h"
Step 6 → Automate weekly with cron / systemd timer; keep last N releases for rollback
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Usage देखो:       docker system df
Step 2 → सिर्फ dangling:    docker image prune          (confirmation पूछता है)
Step 3 → Prompt छोड़ो:      docker image prune -f
Step 4 → सारी unused:       docker image prune -a       (जिस image का container नहीं)
Step 5 → उम्र का filter:    docker image prune -a --filter "until=168h"
Step 6 → हफ्ते में cron / systemd timer से चलाओ; rollback के लिए आखिरी N releases रखो
```

---

## 🟡 Real World Example
A startup's 25 GB EC2 root volume reached 100% at 3 AM; the API container could not write logs and crashed. `docker system df` showed 18 GB of images, mostly old `api:<sha>` tags from daily deploys. They ran `docker image prune -a --filter until=168h -f`, freed 15 GB and added a weekly cron job. They kept the last week of images so rollback stays possible.

## 🟡 Real Example Hindi mein
एक startup का 25 GB EC2 root volume रात 3 बजे 100% भर गया; API container logs नहीं लिख पाया और crash हुआ। `docker system df` में 18 GB images दिखीं, ज़्यादातर रोज़ के deploys के पुराने `api:<sha>` tags। उन्होंने `docker image prune -a --filter until=168h -f` चलाया, 15 GB खाली हुए और हफ्ते का cron job लगाया। पिछले एक हफ्ते की images रखीं ताकि rollback संभव रहे।

---

## 💻 Code / Config Example — Basic
```bash
# How much space do images, containers, volumes and build cache use?
docker system df
# List dangling images (untagged leftovers)
docker images -f dangling=true
# Remove dangling images, asking for confirmation
docker image prune
# Remove dangling images without asking
docker image prune -f
# Remove ALL images not used by a container (careful: next deploy re-pulls)
docker image prune -a -f
# Only those created more than 7 days (168h) ago
docker image prune -a -f --filter "until=168h"
```

## 💻 Code / Config Example — Advanced
```bash
#!/usr/bin/env bash
# docker-cleanup.sh - safe weekly cleanup for a VPS (run from cron)
# Exit on error, undefined variable, pipe failure
set -euo pipefail

# Log file for audit
LOG=/var/log/docker-cleanup.log
# Timestamp helper
ts() { date '+%Y-%m-%d %H:%M:%S'; }

# Record disk usage before cleanup
echo "$(ts) before:" >> "$LOG"
docker system df >> "$LOG"

# Remove unused images older than 7 days; images used by running containers are always kept
docker image prune -a -f --filter "until=168h" >> "$LOG"
# Remove build cache older than 7 days
docker builder prune -f --filter "until=168h" >> "$LOG"
# Remove stopped containers older than 7 days (their images become prunable next run)
docker container prune -f --filter "until=168h" >> "$LOG"
# NOTE: we intentionally do NOT run "docker volume prune": it can delete database data

# Record disk usage after cleanup
echo "$(ts) after:" >> "$LOG"
docker system df >> "$LOG"
```

```cron
# /etc/cron.d/docker-cleanup - every Sunday 03:30, run as root
30 3 * * 0 root /usr/local/bin/docker-cleanup.sh
```
(Shell script checked with `bash -n`; not executed against a Docker daemon here. The `until` filter and `docker builder prune` are standard Docker CLI options.)

---

## 🟠 My Stack Integration
- **VPS deploy**: add `docker image prune -f` to the end of your deploy script (dangling only, safe), and the weekly `-a --filter until=` job for older tags.
- **AWS ECR**: images in the registry are cleaned by **ECR lifecycle policies**, not `docker image prune` (that only affects the local host).
- **GitHub Actions self-hosted runner**: schedule the same script; hosted runners reset themselves.

```yaml
# GitHub Actions deploy step (snippet): cleanup after a successful deploy over SSH
- name: Deploy and cleanup
  run: |
    ssh deploy@${{ secrets.VPS_HOST }} '
      cd /srv/app &&
      docker compose pull &&
      docker compose up -d &&
      docker image prune -f
    '
```
(Requires SSH key setup in the workflow; not run locally.)

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running `docker system prune -a --volumes` on a production host.
✅ Correct: Never prune volumes in production; it deletes unused named volumes (database data if the DB container is stopped).

❌ Mistake 2: Pruning `-a` with no age filter right before a rollback is needed.
✅ Correct: Keep recent images (`until=`) so rollback does not need a re-pull.

❌ Mistake 3: Believing prune cleans the registry.
✅ Correct: It only cleans the local host; use ECR/GHCR retention policies for the registry.

❌ Mistake 4: Never pruning at all.
✅ Correct: Schedule it and alert on disk usage.

---

## 🧠 Tricky Interview Question
"You ran `docker image prune -a` while a container was stopped (not removed). Was its image deleted?"

Answer: No. `-a` removes images not referenced by any container; a stopped container still references its image, so the image is kept. If the container had been removed first, the image would be deleted. That is why `docker container prune` before `image prune -a` frees more space.

---

## ⚫ Interview Questions + Answers

Q1: What is a dangling image?
A1: An untagged image (`<none>:<none>`), typically left when a tag moves to a newer build.

Q2: `image prune` vs `system prune`?
A2: `image prune` removes images only; `system prune` removes stopped containers, unused networks, dangling images and build cache (add `-a` for all unused images, `--volumes` for volumes).

Q3: How to limit by age?
A3: `--filter "until=168h"`.

Q4: Does prune remove images used by running containers?
A4: Never.

Q5: How to prevent filling the disk?
A5: Scheduled prune, log rotation (`max-size`), monitoring disk alerts, and small images.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Disk usage grows after repeated deploys or CI builds.
- As a final step in deploy scripts (dangling only).

❌ Avoid when:
- You need instant rollback to old images that are no longer running.
- On shared hosts where other teams rely on cached images (use filters or labels).

---

## 📊 Visual Diagram
```
 Images on host
 ┌──────────────────────────────────────────────────────────────┐
 │ api:9d2f (running)         ── kept always                    │
 │ api:3f9a (stopped ctr)     ── kept by "prune -a" (referenced)│
 │ api:old1 (unused, 20 days) ── removed by -a --filter until   │
 │ <none> (dangling)          ── removed by plain "prune"       │
 └──────────────────────────────────────────────────────────────┘
 Safe order: docker container prune -> docker image prune -a --filter until=168h
 NEVER: docker volume prune on a DB host
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dangling image | Untagged image | बिना tag की image |
| prune | Delete unused objects | unused हटाना |
| -a | All unused, not just dangling | सारी unused |
| until filter | Age limit | उम्र की सीमा |
| docker system df | Disk usage report | disk usage रिपोर्ट |
| Lifecycle policy | Registry auto-cleanup | registry की auto-सफाई |

---

## ⚡ 3-Line Summary
English: `docker image prune` frees disk by deleting unused images.
Plain prune removes dangling images; `-a` removes every unused one.
Use age filters, never prune volumes in production, and schedule it.
Hindi: `docker image prune` unused images हटाकर disk खाली करता है।
सादा prune dangling हटाता है; `-a` हर unused image हटाता है।
Age filters लगाओ, production में volumes prune मत करो, और schedule करो।

---

## ➡️ Next Topic
**118. Dangling Images** - what dangling images are, why they appear after rebuilds, and how to find them before pruning.
