# 164. Volume Pruning
# हिंदी में: Volume Pruning (बेकार Volumes की सफाई)

---

## 🔵 Simple Definition (English)
**Volume pruning** means deleting Docker volumes that no container uses any more. The command is `docker volume prune`. It frees disk space, but it deletes data permanently, so it must be used with care.

## 🔵 सरल परिभाषा (Hindi)
**Volume pruning** का मतलब है उन Docker volumes को delete करना जिन्हें अब कोई container use नहीं कर रहा। Command है `docker volume prune`। इससे disk space खाली होती है, लेकिन data हमेशा के लिए चला जाता है, इसलिए बहुत सोच-समझकर चलाओ।

---

## 🔴 Problem it Solves
Every time you run `docker compose down -v`, remove a container that had an anonymous volume (`VOLUME` in a Dockerfile), or rename a Compose project, old volumes stay behind. On a small VPS (20-40 GB disk) these "orphan" volumes can silently eat 10+ GB: old Postgres data, old `node_modules` volumes, old build caches. Disk full means your database and Docker daemon stop working. Pruning solves the leak.

## 🔴 यह क्यों बना? (Hindi)
जब भी तुम `docker compose down -v` चलाते हो, या ऐसा container हटाते हो जिसमें anonymous volume थी, या Compose project का नाम बदलते हो, पुरानी volumes पीछे रह जाती हैं। छोटे VPS (20-40 GB disk) पर ये "orphan" volumes चुपचाप 10+ GB खा जाती हैं। Disk full हुई तो database और Docker daemon दोनों रुक जाते हैं। Pruning इसी leak को ठीक करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Docker lists all volumes (docker volume ls)
Step 2 → It finds volumes with ZERO containers attached (running OR stopped)
Step 3 → By default (Engine 23+) only ANONYMOUS volumes are pruned;
         add --all (-a) to also remove unused NAMED volumes
Step 4 → Docker asks "Are you sure?" (skip with -f)
Step 5 → Volumes are deleted from /var/lib/docker/volumes -> data is gone forever
Step 6 → Output shows "Total reclaimed space"
```

Note: the default scope changed in Docker Engine 23.0 (only anonymous volumes pruned unless `--all`). On older engines all unused volumes were removed. Check `docker version` before trusting old blog posts.

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Docker सारी volumes list करता है
Step 2 → वो volumes ढूँढता है जिनसे कोई container जुड़ा नहीं (चालू या बंद, कोई भी नहीं)
Step 3 → Engine 23+ में default सिर्फ ANONYMOUS volumes हटती हैं;
         named volumes भी हटानी हों तो --all (-a) लगाओ
Step 4 → Docker confirm पूछता है (-f से skip)
Step 5 → Volumes /var/lib/docker/volumes से delete, data हमेशा के लिए गया
Step 6 → आख़िर में "Total reclaimed space" दिखता है
```

---

## 🟡 Real World Example
A startup runs a staging VPS where CI redeploys the stack 20 times a day with `docker compose down -v && up`. After two months the 40 GB disk is 95% full because hundreds of anonymous Mongo/Redis volumes piled up. The DevOps engineer adds a weekly cron: `docker volume prune -f --filter "label!=keep"`. Disk drops to 30%. The production DB volume carries the label `keep=true`, so it is never touched.

## 🟡 Real Example Hindi mein
एक startup के staging VPS पर CI दिन में 20 बार `docker compose down -v && up` चलाता है। दो महीने में 40 GB disk 95% भर गई क्योंकि सैकड़ों anonymous Mongo/Redis volumes जमा हो गईं। DevOps engineer ने weekly cron लगाया: `docker volume prune -f --filter "label!=keep"`। Disk 30% पर आ गई। Production DB volume पर `keep=true` label है, इसलिए वो कभी नहीं छुई जाती।

---

## 💻 Code / Config Example — Basic
```bash
# --- inspect first, never prune blind ---
docker system df -v                      # shows disk used by images, containers, volumes
docker volume ls                         # list every volume
docker volume ls -f dangling=true        # list only volumes no container uses

# --- prune ---
docker volume prune                      # asks for confirmation, removes unused ANONYMOUS volumes (Engine 23+)
docker volume prune -f                   # same, but no confirmation prompt (used in scripts)
docker volume prune --all                # ALSO removes unused named volumes (dangerous)

# --- remove one specific volume instead (safer) ---
docker volume rm old_pgdata              # fails if a container still uses it (good safety net)
```

## 💻 Code / Config Example — Advanced
```bash
#!/usr/bin/env bash
# safe-volume-prune.sh - weekly cleanup for a VPS, protects labelled volumes
set -euo pipefail                        # stop on error, unset var, or failed pipe

LOG=/var/log/docker-prune.log            # where we keep an audit trail

echo "=== $(date -Is) before ===" >> "$LOG"   # timestamp the run
docker system df >> "$LOG"                     # record disk usage before cleanup

# list volumes that WOULD be removed (dry run - prune has no dry-run flag)
docker volume ls -qf dangling=true >> "$LOG"   # -q = names only, dangling = unused

# prune only volumes that do NOT carry label keep=true
docker volume prune -f --filter "label!=keep" >> "$LOG" 2>&1

echo "=== $(date -Is) after ===" >> "$LOG"      # timestamp end
docker system df >> "$LOG"                      # record disk usage after cleanup
```

```yaml
# docker-compose.yml - protect the production DB volume with a label
services:
  db:
    image: postgres:16-alpine             # example tag, update to current
    volumes:
      - pgdata:/var/lib/postgresql/data   # named volume holds real data
volumes:
  pgdata:
    labels:
      keep: "true"                        # prune filter label!=keep will skip this volume
```

```bash
# crontab -e  (every Sunday 03:00)
0 3 * * 0 /usr/local/bin/safe-volume-prune.sh
```

---

## 🟠 My Stack Integration
- **Node.js + MongoDB on VPS:** Mongo data lives in a named volume `mongo_data`. Label it `keep=true`. Dev stacks use throwaway volumes that prune can clean.
- **FastAPI + Postgres:** same; never run `--all` on a server that hosts the DB.
- **React + Nginx:** static builds usually need no volume, so nothing to prune.
- **AWS EC2:** prune frees EBS space, which saves cost vs expanding the volume. Take an EBS snapshot before the first prune on any new box.
- **CI runners (GitHub Actions self-hosted):** run `docker volume prune -f` after each job so runners do not fill up.

```yaml
# GitHub Actions step on a self-hosted runner: cleanup after tests
- name: Clean unused volumes          # step label shown in the Actions UI
  if: always()                        # run even if tests failed
  run: docker volume prune -f         # safe on CI: nothing precious lives here
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running `docker volume prune --all -f` on the production server "to free space" and wiping a stopped-but-important DB volume.
✅ Correct: Inspect with `docker volume ls`, label important volumes, use `--filter "label!=keep"`, and take a backup first.

❌ Mistake 2: Stopping the DB container briefly, then pruning. A stopped container no longer protects the volume only if the container was removed; people confuse this.
✅ Correct: Volumes referenced by any container (even stopped) are NOT pruned. But `docker compose down` removes containers, so after `down` the volume becomes unused and is at risk.

❌ Mistake 3: Using `docker system prune --volumes` casually. It prunes containers, networks, images AND volumes.
✅ Correct: Prune each resource type separately and deliberately.

❌ Mistake 4: Assuming old behaviour. Old tutorials say prune removes all unused volumes; newer engines only remove anonymous ones by default.
✅ Correct: Check your Docker version and read the confirmation prompt.

---

## 🧠 Tricky Interview Question
**Q:** You ran `docker compose down` on production by mistake, then a teammate ran `docker volume prune -a -f` an hour later. The database is empty after `up`. What happened and how do you prevent it?

**Answer:** `down` removed the containers, so `pgdata` (a named volume) became "unused". `prune -a` removes unused named volumes, so the data was deleted. Prevention: never use `-a` on production, label critical volumes with `keep=true` and filter on it, keep automated backups (see note 161), restrict who has Docker access (docker group = root), and use `docker compose down` without `-v`. Recovery is only possible from a backup or EBS snapshot.

---

## ⚫ Interview Questions + Answers

Q1: What does `docker volume prune` do?
A1: It deletes volumes not used by any container. In Engine 23+ only anonymous volumes by default; `--all` includes named ones.

Q2: Does prune delete a volume attached to a stopped container?
A2: No. Any container reference (running or stopped) protects the volume. Only after the container is removed does the volume become prunable.

Q3: How can you protect some volumes from prune?
A3: Give them a label and use `--filter "label!=keep"`; also never pass `--all`; also keep backups.

Q4: How is `docker volume rm` different from prune?
A4: `rm` deletes named volumes you pick and refuses if in use; prune bulk-deletes all unused ones.

Q5: Is there a dry-run for prune?
A5: No. Use `docker volume ls -f dangling=true` to preview what is unused.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Dev laptops and CI runners accumulate throwaway volumes
- Disk is almost full and `docker system df` shows large reclaimable volumes
- After decommissioning a project and confirming data is backed up

❌ Avoid when:
- On production with unlabelled volumes
- Right after `compose down` when you still plan to bring the stack back
- Without a recent backup or snapshot

---

## 📊 Visual Diagram
```
 docker volume ls
 +-----------+------------+-----------------------+
 | volume    | used by    | prune fate (default)  |
 +-----------+------------+-----------------------+
 | pgdata    | db (up)    | KEEP  (in use)        |
 | a9f3c...  | (none)     | DELETE (anonymous)    |
 | old_mongo | (none)     | KEEP unless --all     |
 | cache     | (none)     | label keep=true -> KEEP|
 +-----------+------------+-----------------------+
        |
        v
 docker volume prune -f --filter "label!=keep"
        |
        v
 /var/lib/docker/volumes/a9f3c...  --> deleted, space reclaimed
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Prune | Bulk delete unused resources | बेकार चीज़ों की सफाई |
| Anonymous volume | Volume with random hash name | बिना नाम की volume |
| Named volume | Volume you named yourself | नाम वाली volume |
| Dangling volume | Not attached to any container | अनाथ volume |
| Label filter | Select resources by label | label से छाँटना |
| Reclaimed space | Disk freed by cleanup | वापस मिली जगह |

---

## ⚡ 3-Line Summary
English: `docker volume prune` deletes unused volumes and frees disk space.
It is irreversible, so label important volumes, filter by label, and back up first.
Never use `--all` casually on production.
Hindi: `docker volume prune` बेकार volumes हटाकर disk खाली करता है।
यह वापस नहीं होता, इसलिए ज़रूरी volumes पर label लगाओ, filter करो और पहले backup लो।
Production पर `--all` कभी लापरवाही से मत चलाओ।

---

## ➡️ Next Topic
**165. Best Practices for Volumes** - now that you know how to create, back up and delete volumes, the next note collects the rules that keep data safe in production.
