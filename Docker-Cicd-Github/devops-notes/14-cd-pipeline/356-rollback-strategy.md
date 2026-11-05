# 356. Rollback Strategy
# हिंदी में: Rollback Strategy

---

## 🔵 Simple Definition (English)
A rollback strategy is your prepared plan to return production to the last known good version when a release goes wrong. It covers how you detect failure, which version to return to, how to switch (redeploy old image, flip traffic, disable a flag) and what to do about the database.

## 🔵 सरल परिभाषा (Hindi)
Rollback strategy वह पहले से तैयार योजना है जिससे release गड़बड़ होने पर production को आखिरी ठीक version पर लौटाया जाता है। इसमें शामिल है: failure कैसे पकड़ें, किस version पर लौटें, कैसे switch करें (पुरानी image redeploy, traffic flip, flag बंद) और database का क्या करें।

---

## 🔴 Problem it Solves
Without a plan, a bad release at midnight turns into panic: nobody knows the previous tag, the old image was pruned from the server, the migration cannot be undone, and fixing forward takes hours while users suffer. Mean time to recovery (MTTR) is what customers feel, not how rarely you fail.

## 🔴 यह क्यों बना? (Hindi)
योजना के बिना आधी रात का खराब release घबराहट बन जाता है: किसी को पिछला tag नहीं पता, पुरानी image server से prune हो चुकी है, migration undo नहीं हो सकती, और fix-forward में घंटे लगते हैं जबकि users परेशान रहते हैं। ग्राहक MTTR (recovery का समय) महसूस करते हैं, यह नहीं कि आप कितनी कम बार fail होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Every release is an immutable image tag (git SHA); keep the last N tags
Step 2 → Record the previously deployed tag before each deploy
Step 3 → Detect failure: health check, error-rate alarm, or human report
Step 4 → Choose the fastest safe lever: flag off > traffic flip > redeploy old tag
Step 5 → Redeploy the previous tag with the same pipeline (tested path)
Step 6 → Check the database: was the migration backward compatible?
Step 7 → Verify health, announce, then write a post-mortem
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर release एक immutable image tag (git SHA) है; आखिरी N tags रखो
Step 2 → हर deploy से पहले पिछला deployed tag record करो
Step 3 → Failure पकड़ो: health check, error-rate alarm या इंसान की report
Step 4 → सबसे तेज़ सुरक्षित तरीका चुनो: flag off > traffic flip > पुराना tag redeploy
Step 5 → उसी pipeline से पिछला tag redeploy करो (जाँचा हुआ रास्ता)
Step 6 → Database जाँचो: क्या migration backward compatible थी?
Step 7 → Health verify करो, सबको बताओ, फिर post-mortem लिखो
```

---

## 🟡 Real World Example
A payments API deploys at 6 PM. By 6:03 the error rate climbs to 8%. The on-call engineer opens the "Rollback" workflow, types the previous SHA `a1b2c3d` and approves. Within 90 seconds the old container is back, errors drop to normal. The migration in that release only added a nullable column, so no database action is needed. The next morning the team fixes the bug and deploys again with a canary. Recovery took minutes because the rollback path was rehearsed.

## 🟡 Real Example Hindi mein
एक payments API शाम 6 बजे deploy होती है। 6:03 तक error rate 8% हो जाता है। On-call engineer "Rollback" workflow खोलता है, पिछला SHA `a1b2c3d` डालता है और approve करता है। 90 सेकंड में पुराना container वापस आ जाता है, errors सामान्य। उस release की migration सिर्फ nullable column जोड़ती थी, इसलिए database पर कुछ नहीं करना पड़ा। अगली सुबह bug ठीक करके canary से दोबारा deploy। Recovery मिनटों में हुई क्योंकि rollback का रास्ता अभ्यास किया हुआ था।

---

## 💻 Code / Config Example — Basic

```bash
# basic manual rollback on the VPS
cd /srv/myapp                                   # project folder
cat .previous_image                             # the image tag deployed before this one
export API_IMAGE=$(cat .previous_image)         # select the previous image
docker compose up -d api                        # recreate the container with the old image
curl -fsS http://127.0.0.1:8000/health          # confirm it is healthy
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/rollback.yml - one-click, audited rollback
name: Rollback
on:
  workflow_dispatch:                           # manual trigger from the Actions tab
    inputs:
      image_tag:
        description: "Image tag (git SHA) to roll back to"
        required: true
        type: string
      reason:
        description: "Why are we rolling back? (for the audit trail)"
        required: true
        type: string
concurrency:
  group: production-deploy                     # share the group with the deploy workflow
  cancel-in-progress: false                    # never cancel a running deploy mid-way
permissions:
  contents: read
jobs:
  rollback:
    runs-on: ubuntu-latest
    environment: production                    # requires reviewer approval
    steps:
      - name: Validate tag format
        run: |
          # only allow 7-40 hex chars to avoid shell injection via the input
          [[ "${{ inputs.image_tag }}" =~ ^[0-9a-f]{7,40}$ ]] || { echo "bad tag"; exit 1; }
      - name: Roll back on the server
        uses: appleboy/ssh-action@v1.0.3       # example version
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            set -euo pipefail
            cd /srv/myapp
            IMAGE="ghcr.io/myorg/myapp/api:${{ inputs.image_tag }}"
            docker pull "$IMAGE"                               # make sure it still exists
            CURRENT=$(grep '^API_IMAGE=' .env | cut -d= -f2-)  # remember what we leave
            echo "$CURRENT" > .rolled_back_from
            sed -i "s|^API_IMAGE=.*|API_IMAGE=${IMAGE}|" .env  # point to the old image
            docker compose up -d api                           # swap container
            for i in $(seq 1 20); do
              curl -fsS http://127.0.0.1:8000/health && echo OK && exit 0
              sleep 3
            done
            echo "Rollback target unhealthy"; exit 1
      - name: Record in job summary
        run: |
          echo "### Rollback executed" >> "$GITHUB_STEP_SUMMARY"
          echo "- Tag: ${{ inputs.image_tag }}" >> "$GITHUB_STEP_SUMMARY"
          echo "- By: ${{ github.actor }}" >> "$GITHUB_STEP_SUMMARY"
```

```bash
# automatic rollback inside the deploy script (pattern)
PREV=$(grep '^API_IMAGE=' .env | cut -d= -f2-)         # save old tag BEFORE changing .env
echo "$PREV" > .previous_image                         # keep for manual rollback
# ... deploy new image ...
if ! ./wait_healthy.sh; then                           # your health wait helper
  sed -i "s|^API_IMAGE=.*|API_IMAGE=${PREV}|" .env     # restore old tag
  docker compose up -d api                             # run old version
  exit 1                                               # mark pipeline as failed
fi
```

```bash
# Kubernetes / AWS equivalents
kubectl rollout undo deployment/api                    # back to previous ReplicaSet
kubectl rollout status deployment/api                  # wait for completion
aws ecs update-service --cluster prod --service api \
    --task-definition api:41                           # redeploy an earlier task definition revision (example)
```

---

## 🟠 My Stack Integration
- Keep at least the last 5 image tags in GHCR/ECR; set the retention policy so they are not deleted.
- On the VPS do not run `docker system prune -a` blindly; it deletes old images you may need.
- React static builds: keep previous `build/` folders (`releases/<sha>`) and flip a `current` symlink.
- Node/FastAPI: rollback is a tag switch; the database is the hard part (see 355).

```bash
# React/Nginx symlink-based release layout (atomic switch and instant rollback)
# /var/www/app/releases/abc1234  /var/www/app/releases/def5678  /var/www/app/current -> releases/def5678
ln -sfn /var/www/app/releases/abc1234 /var/www/app/current   # rollback = repoint the symlink
sudo nginx -s reload                                          # usually not even required for static files
```

Security: restrict the rollback workflow to authorized people (environment reviewers), validate the input tag, and make sure the old version does not contain a known vulnerability you just patched; if it does, prefer a flag-off or fix-forward.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Deploying only `latest`, so the previous version is lost.
✅ Correct: Deploy immutable SHA tags and record the previous one.

❌ Mistake 2: Never rehearsing rollback.
✅ Correct: Practice it in staging and during game days.

❌ Mistake 3: Rolling back code but ignoring the database.
✅ Correct: Make migrations backward compatible and take a backup first.

❌ Mistake 4: Registry cleanup deletes old images.
✅ Correct: Keep retention for the last N releases.

❌ Mistake 5: Rolling back a security patch.
✅ Correct: Use a feature flag or fix forward when the old version is vulnerable.

---

## 🧠 Tricky Interview Question
Is "roll back" always better than "fix forward"?

Answer: No. Rollback is best for fast recovery when the change is the clear cause and the data is compatible. Fix forward is better when a migration is not reversible, the old version has a security hole, or the bug is a one-line fix that can ship faster than coordinating a rollback. Mature teams define the rule in advance: for example "if not recovered within 10 minutes, roll back".

---

## ⚫ Interview Questions + Answers

Q1: What is the fastest rollback mechanism?
A1: A feature-flag kill switch (seconds), then a traffic flip in blue-green, then redeploying a previous image.

Q2: Why immutable image tags?
A1: They guarantee the exact bits you tested are what you redeploy; `latest` can change under you.

Q3: How do you roll back a database migration?
A3: Prefer backward-compatible migrations so no DB rollback is needed. For emergencies use a downgrade script or restore from backup, accepting possible data loss for writes since the backup.

Q4: How do you trigger automatic rollback?
A4: Post-deploy health checks and alarms (CloudWatch, Prometheus) that call a rollback script, or controllers like Argo Rollouts and CodeDeploy.

Q5: What metrics matter?
A5: MTTR, change failure rate, deployment frequency and lead time (DORA metrics).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The release clearly caused the incident and old and new data are compatible.
- Impact is high and the fix is not instant.

❌ Avoid when:
- The old version has a vulnerability, or data changes are irreversible: fix forward or use a flag.
- The failure is unrelated to the release (infra outage): rolling back just adds noise.

---

## 📊 Visual Diagram
```
 releases:  v41 (good) --> v42 (bad, live)
                              |
                 alarm / health check fails
                              |
              +---------------+----------------+
              |               |                |
        flag OFF (sec)   traffic flip       redeploy v41
                          (blue-green)       (tag from record)
              \_______________|________________/
                              v
                     verify /health + metrics
                              v
                  DB check: v41 works on schema v42 ?
                       yes -> done      no -> restore / fix forward
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Rollback | Return to previous version | पिछले version पर वापसी |
| Fix forward | Ship a new fix instead | rollback की जगह नया fix भेजना |
| MTTR | Mean time to recovery | recovery का औसत समय |
| Immutable tag | Tag that never changes | कभी न बदलने वाला tag |
| Kill switch | Flag to disable a feature | feature बंद करने वाला flag |

---

## ⚡ 3-Line Summary
English: Plan rollback before you need it: immutable tags, recorded previous version, and a tested workflow.
Pick the fastest safe lever and always consider the database.
Sometimes fix-forward is better; decide rules in advance.
Hindi: ज़रूरत से पहले rollback की योजना बनाओ: immutable tags, पिछला version record, और जाँचा हुआ workflow।
सबसे तेज़ सुरक्षित तरीका चुनो और database हमेशा सोचो।
कभी fix-forward बेहतर होता है; नियम पहले से तय करो।

---

## ➡️ Next Topic
**357. Deployment Notifications (Slack, Email, Teams)** — telling the team automatically when deploys start, pass or fail.
