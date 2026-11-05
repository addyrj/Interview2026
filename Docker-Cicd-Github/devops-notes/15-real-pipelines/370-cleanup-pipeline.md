---

# 370. Cleanup Pipeline
# हिंदी में: Cleanup Pipeline

---

## 🔵 Simple Definition (English)
A cleanup pipeline is a scheduled workflow that deletes things you no longer need: old container images in the registry, old workflow artifacts and caches, merged branches, and unused Docker data on the VPS. It keeps cost low and disks from filling up.

## 🔵 सरल परिभाषा (Hindi)
Cleanup pipeline एक scheduled workflow है जो गैर-ज़रूरी चीज़ें हटाता है: registry की पुरानी container images, पुराने workflow artifacts और caches, merge हो चुकी branches, और VPS पर बेकार Docker data। इससे खर्च कम रहता है और disk नहीं भरती।

---

## 🔴 Problem it Solves
- Every deploy leaves a new image; after a year the registry has thousands of GB-sized layers.
- VPS disk reaches 100 percent, Postgres stops writing, site goes down at 3 AM.
- Stale branches and artifacts clutter the repo and eat storage quota.

## 🔴 यह क्यों बना? (Hindi)
- हर deploy नई image छोड़ जाता है; साल भर बाद registry में हज़ारों GB की layers।
- VPS disk 100 प्रतिशत भर जाती है, Postgres लिखना बंद कर देता है, रात 3 बजे site बंद।
- Stale branches और artifacts repo में कचरा और storage quota खाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Weekly schedule + manual trigger (with a dry-run switch)
Step 2 → Registry: list image versions, keep newest N and anything tagged release
Step 3 → Repo: delete artifacts/caches older than X days
Step 4 → VPS: docker image/container/builder prune with age filters
Step 5 → Report what was deleted; dry-run default for first runs
Step 6 → Alert if disk usage is still above threshold
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Weekly schedule + manual trigger (dry-run switch के साथ)
Step 2 → Registry: image versions list करें, नवीनतम N और release tag वाली रखें
Step 3 → Repo: X दिन से पुराने artifacts/caches हटाएँ
Step 4 → VPS: age filters के साथ docker image/container/builder prune
Step 5 → क्या हटाया उसकी report; पहले runs में dry-run default
Step 6 → Disk usage अब भी threshold से ऊपर हो तो alert
```

---

## 🟡 Real World Example
A startup's EC2 instance (30 GB disk) went down because 40 old API images had piled up under `/var/lib/docker`. After adding a weekly cleanup, the box keeps the last 5 versions for rollback, prunes everything older than 7 days, and the registry job keeps the last 10 SHA tags. Disk stays below 55 percent and GHCR storage cost stopped growing.

## 🟡 Real Example Hindi mein
एक startup का EC2 instance (30 GB disk) इसलिए बंद हुआ क्योंकि `/var/lib/docker` में 40 पुरानी API images जमा थीं। Weekly cleanup जोड़ने के बाद box rollback के लिए आख़िरी 5 versions रखता है, 7 दिन से पुराना सब prune करता है, और registry job आख़िरी 10 SHA tags रखता है। Disk 55 प्रतिशत से नीचे रहती है और GHCR storage खर्च बढ़ना बंद हो गया।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/cleanup-basic.yml
name: Cleanup basic                    # Name
on:
  schedule:
    - cron: "0 22 * * 0"               # Sundays 22:00 UTC
  workflow_dispatch:                   # Manual run
jobs:
  prune-vps:
    runs-on: ubuntu-latest
    steps:
      - uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.VPS_HOST }}
          username: deploy
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            docker image prune -af --filter "until=168h"   # Remove unused images older than 7 days
            docker builder prune -f --filter "until=168h"  # Remove old build cache
            df -h /                                        # Print disk usage for the log
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/cleanup.yml
name: Cleanup
on:
  schedule:
    - cron: "0 22 * * 0"
  workflow_dispatch:
    inputs:
      dry_run:
        description: Only list, do not delete
        type: boolean
        default: true                  # Safe default
permissions:
  contents: read
  packages: write                      # Needed to delete package versions
  actions: write                       # Needed to delete caches and artifacts
env:
  DRY: ${{ github.event_name == 'workflow_dispatch' && inputs.dry_run || 'false' }}  # "true"/"false"
jobs:
  registry:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/delete-package-versions@v5   # Official action (example version)
        with:
          package-name: my-repo/api                # Package path under the owner
          package-type: container
          min-versions-to-keep: 10                 # Always keep the newest 10
          delete-only-untagged-versions: false     # Also removes old tagged versions
        if: env.DRY == 'false'
  caches-and-artifacts:
    runs-on: ubuntu-latest
    steps:
      - name: Delete caches older than 7 days
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}    # gh CLI auth
        run: |
          set -euo pipefail
          CUTOFF=$(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ)
          # List caches as "id<TAB>lastAccessedAt" and select old ones
          gh api --paginate "repos/${{ github.repository }}/actions/caches" \
            --jq ".actions_caches[] | select(.last_accessed_at < \"$CUTOFF\") | .id" |
          while read -r ID; do
            if [ "$DRY" = "true" ]; then echo "would delete cache $ID"; else gh api -X DELETE "repos/${{ github.repository }}/actions/caches/$ID"; fi
          done
  branches:
    runs-on: ubuntu-latest
    steps:
      - name: List merged branches older than 30 days (report only)
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh api --paginate "repos/${{ github.repository }}/branches" --jq '.[].name' | grep -v -E '^(main|develop)$' || true
  vps:
    runs-on: ubuntu-latest
    steps:
      - uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.VPS_HOST }}
          username: deploy
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            set -e
            docker ps --format '{{.Image}}' | sort -u > /tmp/in-use.txt     # Never touch running images
            docker container prune -f --filter "until=168h"                 # Stopped containers over 7 days
            docker image prune -af --filter "until=168h"                    # Unused images over 7 days
            docker volume ls -qf dangling=true                              # LIST only: volumes may hold data
            USE=$(df --output=pcent / | tail -1 | tr -dc '0-9')
            echo "Disk usage: ${USE}%"
            test "$USE" -lt 85                                              # Fail (alert) if still too full
```

---

## 🟠 My Stack Integration
Keep at least the last 3-5 tags on the VPS so the Rollback step of your deploy pipeline still works. Add log rotation so container logs do not fill the disk:

```json
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
```

Save the JSON above as `/etc/docker/daemon.json` on the VPS, then restart Docker (affects new containers). The same applies to Nginx logs: use `logrotate`. For AWS ECR, set a lifecycle policy (keep last N images) instead of a workflow. Workflows above were not run locally; test with dry-run first.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `docker system prune -a --volumes` on production.
✅ Correct: Never prune volumes automatically; databases live there.

❌ Mistake 2: Deleting the image currently running or the previous one needed for rollback.
✅ Correct: Keep the last N tags; filter by age.

❌ Mistake 3: Running destructive cleanup first with no dry-run.
✅ Correct: Dry-run default, review logs, then enable deletion.

❌ Mistake 4: Giving the token broad write rights.
✅ Correct: Scope permissions to only what each job needs.

Security: log what was deleted, restrict who can trigger manual runs, and keep a manual approval for registry deletion in regulated settings.

---

## 🧠 Tricky Interview Question
After `docker image prune -a`, a container restart fails with "image not found". Why?

Answer: `prune -a` removes all images not used by an existing container. Stopped containers were pruned earlier or were never created from that image, so the image was considered unused and deleted. Restarting with a compose file then needs a pull that fails if the registry copy was also cleaned. Keep recent tags in both places.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `docker prune` options?
A1: `image prune` removes dangling images (`-a` all unused), `container prune` stopped containers, `volume prune` unused volumes, `system prune` combines them.

Q2: What are dangling images?
A2: Untagged layers left after a tag moves to a newer build.

Q3: Better than workflows for ECR?
A3: ECR lifecycle policies do it natively and reliably.

Q4: How to avoid deleting what is in use?
A4: Keep newest N tags, protect `release-*` tags, and compare against running images.

Q5: Why is disk the silent killer?
A5: Logs, images and volumes grow quietly; a full disk breaks DB writes and logging.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Frequent deploys create many images, caches and artifacts.

❌ Avoid when:
- Compliance requires retaining every build; archive instead of deleting.

---

## 📊 Visual Diagram
```
 weekly cron --> cleanup workflow (dry-run by default)
                   |
     +-------------+--------------+----------------+
     v             v              v                v
  GHCR old     Actions caches   merged         VPS: prune
  versions     + artifacts      branches       images/containers
  (keep 10)    (>7 days)        (report)       (keep running + last 3)
                   |
              disk < 85% ? else alert
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Prune | Delete unused objects | बेकार objects हटाना |
| Dangling image | Untagged leftover image | बिना tag वाली बची image |
| Retention | How long to keep | कितने समय तक रखना |
| Lifecycle policy | Registry auto-delete rule | Registry का auto-delete नियम |
| Dry-run | Simulate without deleting | बिना हटाए simulation |

---

## ⚡ 3-Line Summary
English: Schedule cleanup of images, caches, artifacts and VPS Docker data.
English: Keep recent versions for rollback and never auto-prune volumes.
English: Use dry-run first and alert on disk usage.
Hindi: Images, caches, artifacts और VPS Docker data की cleanup schedule करें।
Hindi: Rollback के लिए हाल के versions रखें और volumes कभी auto-prune न करें।
Hindi: पहले dry-run चलाएँ और disk usage पर alert रखें।

---

## ➡️ Next Topic
371. Dependency Update Pipeline: keep packages current with Dependabot or Renovate.
