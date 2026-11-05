# 380. ECR Lifecycle Policies
# हिंदी में: ECR Lifecycle Policies (पुरानी images का auto cleanup)

---

## 🔵 Simple Definition (English)
An ECR lifecycle policy is a set of JSON rules attached to a repository that automatically expires (deletes) images by age or count, for example "delete untagged images after 7 days" or "keep only the newest 30 release images".

## 🔵 सरल परिभाषा (Hindi)
ECR lifecycle policy एक repository से जुड़े JSON rules का set है जो images को age या count के आधार पर अपने आप expire (delete) करता है, जैसे "untagged images 7 दिन बाद delete करो" या "सिर्फ नई 30 release images रखो"।

---

## 🔴 Problem it Solves
- Every CI build adds an image. 20 builds per day x 200 MB = lots of GB; ECR bills per GB-month.
- Untagged images (from re-pushed tags) pile up silently.
- Nobody wants to clean manually; manual cleanup risks deleting the running version.

## 🔴 यह क्यों बना? (Hindi)
- हर CI build एक image जोड़ता है। रोज़ 20 builds x 200 MB = बहुत GB; ECR हर GB-month का पैसा लेता है।
- Untagged images (tag दोबारा push करने से) चुपचाप जमा होती रहती हैं।
- Manual cleanup कोई नहीं करता; और गलती से चल रहा version delete हो सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write rules, each with rulePriority (1 = evaluated first)
Step 2 → Each rule has a selection (tagStatus, tagPrefixList, countType, countNumber)
Step 3 → Action is always {"type": "expire"}
Step 4 → ECR evaluates rules periodically (not instantly; can take ~24 hours)
Step 5 → Matching images are expired; an image matched by a lower-number rule is not reconsidered
Step 6 → Use "preview" (dry run) before applying to see what would be deleted
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप rules लिखते हो, हर में rulePriority (1 सबसे पहले evaluate)
Step 2 → हर rule में selection (tagStatus, tagPrefixList, countType, countNumber)
Step 3 → Action हमेशा {"type": "expire"} होता है
Step 4 → ECR समय-समय पर evaluate करता है (तुरंत नहीं; ~24 घंटे लग सकते हैं)
Step 5 → Match हुई images expire होती हैं; कम number वाले rule से match हुई image दोबारा नहीं देखी जाती
Step 6 → लागू करने से पहले "preview" (dry run) से देखो क्या delete होगा
```

---

## 🟡 Real World Example
A SaaS company noticed an ECR bill of 400 USD/month for 3 TB of images, most of them untagged leftovers. They added: expire untagged after 3 days; keep last 20 images with prefix `prod-`; keep last 10 `staging-`; expire `pr-` images after 7 days. The bill dropped to about 40 USD and production rollbacks (last 20 versions) remained possible.

## 🟡 Real Example Hindi mein
एक SaaS company ने देखा कि 3 TB images का ECR bill 400 USD/month है, जिनमें ज़्यादातर untagged बचे हुए थे। उन्होंने rules जोड़े: untagged 3 दिन बाद expire; `prod-` prefix की आखिरी 20 images रखो; `staging-` की 10; `pr-` images 7 दिन बाद expire। Bill लगभग 40 USD हो गया और production rollback (पिछले 20 versions) फिर भी संभव रहा।

---

## 💻 Code / Config Example — Basic

```json
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Delete untagged images older than 7 days",
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countUnit": "days",
        "countNumber": 7
      },
      "action": { "type": "expire" }
    }
  ]
}
```

Apply it (save the JSON as `policy.json`):

```bash
# apply-lifecycle-basic.sh
set -euo pipefail                                          # stop on error
aws ecr put-lifecycle-policy --repository-name myapp-api \
  --lifecycle-policy-text file://policy.json               # attach JSON rules to the repo
aws ecr get-lifecycle-policy --repository-name myapp-api   # read back to confirm
```

## 💻 Code / Config Example — Advanced
Multiple rules by tag prefix, with a dry-run preview first.

```json
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Expire untagged images after 3 days",
      "selection": { "tagStatus": "untagged", "countType": "sinceImagePushed", "countUnit": "days", "countNumber": 3 },
      "action": { "type": "expire" }
    },
    {
      "rulePriority": 2,
      "description": "Expire pull-request images after 7 days",
      "selection": { "tagStatus": "tagged", "tagPrefixList": ["pr-"], "countType": "sinceImagePushed", "countUnit": "days", "countNumber": 7 },
      "action": { "type": "expire" }
    },
    {
      "rulePriority": 3,
      "description": "Keep only the last 10 staging images",
      "selection": { "tagStatus": "tagged", "tagPrefixList": ["staging-"], "countType": "imageCountMoreThan", "countNumber": 10 },
      "action": { "type": "expire" }
    },
    {
      "rulePriority": 4,
      "description": "Keep only the last 30 production images",
      "selection": { "tagStatus": "tagged", "tagPrefixList": ["prod-"], "countType": "imageCountMoreThan", "countNumber": 30 },
      "action": { "type": "expire" }
    }
  ]
}
```

```bash
# lifecycle-preview.sh  - see what WOULD be deleted before enabling
set -euo pipefail                                              # strict mode
aws ecr start-lifecycle-policy-preview --repository-name myapp-api \
  --lifecycle-policy-text file://policy.json                   # begin dry run
sleep 10                                                       # preview runs asynchronously
aws ecr get-lifecycle-policy-preview --repository-name myapp-api \
  --query 'previewResults[].{tags:imageTags,pushed:imagePushedAt,rule:appliedRulePriority}'   # list victims
```

---

## 🟠 My Stack Integration
Tag your CI images with a prefix so lifecycle rules can tell them apart: `prod-4f2a9c1` for main, `pr-123-ab12cd3` for pull requests. In the GitHub Actions metadata step:

```yaml
# snippet for docker/metadata-action@v5 'tags' input (inside your build step)
tags: |
  type=sha,prefix=prod-,enable=${{ github.ref == 'refs/heads/main' }}
  type=sha,prefix=pr-${{ github.event.number }}-,enable=${{ github.event_name == 'pull_request' }}
```

Safety rule for ECS: the image in the currently running task definition must never fall outside the "keep" window. Keep at least as many as the number of revisions you might roll back to.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: "Keep last 5" with 10 deploys a day.
✅ Correct: Count by environment prefix and keep enough for rollback and audit (20-30).

❌ Mistake 2: Applying without preview.
✅ Correct: Run `start-lifecycle-policy-preview` first.

❌ Mistake 3: Same priority numbers or overlapping broad rules (tagStatus `any` at priority 1).
✅ Correct: Priorities are unique; put the broad `any` rule with the highest number (evaluated last). A `tagStatus: any` rule must have the highest priority number.

❌ Mistake 4: Expecting instant deletion.
✅ Correct: Evaluation is asynchronous, so cost drops later.

---

## 🧠 Tricky Interview Question
Your policy keeps the last 10 images. A service you have not deployed for 3 months suddenly fails to scale: image not found. The service's image was fine until now. What happened?

Answer: Other pushes (e.g. other branches or rebuilds) made the old running image fall outside "last 10", so it was expired. The running tasks kept working because they had already pulled it, but new tasks cannot. Fix: separate rules by tag prefix per environment, keep the deployed tag in a protected prefix (e.g. `release-`), and use age + count rules carefully.

---

## ⚫ Interview Questions + Answers

Q1: imageCountMoreThan vs sinceImagePushed?
A1: Count rule keeps N newest images; age rule expires images older than N days. Count suits tagged releases; age suits untagged/PR images.

Q2: Does lifecycle delete images in use by ECS?
A2: ECR does not check usage. It deletes by rule, which can break scaling or rollback. You must design rules around what you deploy.

Q3: How are rules evaluated?
A3: In priority order; an image is acted on by the first rule that matches it.

Q4: Where does an untagged image come from?
A4: Re-pushing a mutable tag leaves the old image without a tag, also multi-arch manifest children and cancelled pushes.

Q5: Do lifecycle policies work with immutable tags?
A5: Yes, they are independent. Immutable tags prevent overwrites; lifecycle handles deletion.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every repository that receives CI pushes

❌ Avoid when:
- Compliance requires retaining all images (then archive elsewhere first)
- You have not defined which tags are "protected"

---

## 📊 Visual Diagram
```
 repo myapp-api  (push stream)
   prod-a1 prod-a2 ... prod-a45   pr-9-x  pr-10-y  <untagged> <untagged>
        |                              |        |        |
   rule4: keep newest 30         rule2: >7d  rule1: >3d
        v                              v        v
   older prod-* expired            expired   expired
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Lifecycle policy | Auto expire rules | Auto delete के नियम |
| rulePriority | Evaluation order number | Rule का क्रम |
| tagStatus | tagged, untagged or any | Tag की स्थिति |
| countType | How to count: by number or by days | गिनने का तरीका |
| Preview | Dry run of the policy | Dry run |

---

## ⚡ 3-Line Summary
English: Lifecycle policies expire old ECR images by age or count to save cost.
Use tag prefixes per environment, preview first, and keep enough for rollback.
Deletion ignores what is running, so design rules around your deploy tags.

Hindi: Lifecycle policies पुरानी ECR images को age या count से expire करके cost बचाती हैं।
Environment के हिसाब से tag prefixes रखो, पहले preview देखो, rollback जितनी images रखो।
Deletion यह नहीं देखता कि क्या चल रहा है, इसलिए rules अपने deploy tags के हिसाब से बनाओ।

---

## ➡️ Next Topic
381. AWS ECS — Complete Guide: where the images from ECR actually run.
