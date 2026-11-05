# 390. AWS CodeDeploy Basics
# हिंदी में: AWS CodeDeploy की बुनियाद

---

## 🔵 Simple Definition (English)
**AWS CodeDeploy** is a managed service that copies a release bundle to your servers (EC2, on-prem, Lambda, ECS) and runs your scripts in a fixed order (stop, install, start, validate) as described in an **`appspec.yml`** file. It controls how many servers update at once and can roll back automatically.

## 🔵 सरल परिभाषा (Hindi)
**AWS CodeDeploy** एक managed service है जो release bundle को आपके servers (EC2, on-prem, Lambda, ECS) पर copy करती है और **`appspec.yml`** में लिखे क्रम (stop, install, start, validate) में आपकी scripts चलाती है। यह तय करती है कि एक साथ कितने servers update हों और ज़रूरत पड़ने पर अपने आप rollback करती है।

---

## 🔴 Problem it Solves
With plain SSH/SSM loops you must code: server list, one-at-a-time order, health check, "what if server 3 fails?", and rollback. That script grows, breaks, and is different per project.

CodeDeploy gives a standard model: **deployment groups** (which servers), **deployment configs** (how fast), **hooks** (what to run), **automatic rollback** (on failure or alarm), and a deployment history/UI.

## 🔴 यह क्यों बना? (Hindi)
सादे SSH/SSM loops में आपको खुद code करना पड़ता है: server list, एक-एक करके क्रम, health check, "server 3 fail हो गया तो?", और rollback। वह script बढ़ती जाती है, टूटती है, और हर project में अलग होती है।

CodeDeploy एक standard model देता है: **deployment group** (कौन से servers), **deployment config** (कितनी तेज़ी से), **hooks** (क्या चलाना), **automatic rollback** और deployment history/UI।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Install CodeDeploy agent on each EC2 (and give instance role S3 read)
Step 2 → CI zips the app + appspec.yml + scripts, uploads to S3 (revision)
Step 3 → CI calls "aws deploy create-deployment" for application + deployment group
Step 4 → Agent downloads revision from S3
Step 5 → Hooks run in order:
         ApplicationStop -> DownloadBundle -> BeforeInstall -> Install(files)
         -> AfterInstall -> ApplicationStart -> ValidateService
Step 6 → If a hook exits non-zero -> instance marked failed -> rollback (if enabled)
Step 7 → CI waits: "aws deploy wait deployment-successful"
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर EC2 पर CodeDeploy agent install करें (और instance role को S3 read दें)
Step 2 → CI app + appspec.yml + scripts को zip करके S3 में upload करता है (revision)
Step 3 → CI application + deployment group के लिए "aws deploy create-deployment" call करता है
Step 4 → Agent S3 से revision download करता है
Step 5 → Hooks क्रम से चलते हैं:
         ApplicationStop -> DownloadBundle -> BeforeInstall -> Install(files)
         -> AfterInstall -> ApplicationStart -> ValidateService
Step 6 → Hook non-zero exit दे तो instance failed -> rollback (अगर enabled)
Step 7 → CI इंतज़ार करता है: "aws deploy wait deployment-successful"
```

---

## 🟡 Real World Example
An ed-tech company runs a Node.js monolith on an Auto Scaling Group of 6 EC2 instances. They use CodeDeploy with `CodeDeployDefault.OneAtATime`: each instance is removed from the ALB, updated, validated by a `ValidateService` hook that curls `/health`, and put back. A new instance launched by auto scaling at 2 AM automatically receives the latest successful revision, which an SSH script could never do.

## 🟡 Real Example Hindi mein
एक ed-tech कंपनी अपना Node.js monolith 6 EC2 instances के Auto Scaling Group पर चलाती है। वे CodeDeploy का `CodeDeployDefault.OneAtATime` इस्तेमाल करते हैं: हर instance ALB से निकाला जाता है, update होता है, `ValidateService` hook `/health` को curl करके जाँचता है, और वापस लगाया जाता है। रात 2 बजे auto scaling से बना नया instance अपने आप latest सफल revision पा लेता है, जो SSH script कभी नहीं कर सकती।

---

## 💻 Code / Config Example — Basic

`appspec.yml` for an EC2/on-prem Node.js app (must be in the root of the bundle).

```yaml
version: 0.0                                     # appspec version, always 0.0
os: linux                                        # target operating system
files:                                           # what to copy and where
  - source: /                                    # everything in the bundle
    destination: /opt/myapp                      # target folder on the server
file_exists_behavior: OVERWRITE                  # replace old files instead of failing
permissions:                                     # fix owner after copying
  - object: /opt/myapp
    owner: ubuntu                                # app runs as this user
    group: ubuntu
    type:
      - directory
      - file
hooks:                                           # lifecycle scripts, paths relative to bundle
  ApplicationStop:
    - location: scripts/stop.sh                  # stop the old version
      timeout: 60                                # seconds before hook is failed
      runas: ubuntu                              # user to run it as
  BeforeInstall:
    - location: scripts/before_install.sh        # cleanup / prerequisites
      timeout: 120
  AfterInstall:
    - location: scripts/after_install.sh         # npm ci, build, env fetch
      timeout: 300
  ApplicationStart:
    - location: scripts/start.sh                 # start the new version
      timeout: 60
  ValidateService:
    - location: scripts/validate.sh              # health check; non-zero = failed deploy
      timeout: 90
```

Scripts used by the hooks:

```bash
#!/usr/bin/env bash
# scripts/stop.sh : stop old app (must not fail if app is not running on first deploy)
pm2 stop myapp || true          # "|| true" so first deployment does not fail
```

```bash
#!/usr/bin/env bash
# scripts/validate.sh : fail the deployment if the app is not healthy
set -e                                           # exit at the first error
for i in $(seq 1 10); do                         # try 10 times
  if curl -fsS http://localhost:3000/health; then   # -f fails on HTTP 4xx/5xx
    exit 0                                       # healthy -> hook passes
  fi
  sleep 3                                        # wait and retry
done
exit 1                                           # never healthy -> hook fails -> rollback
```

## 💻 Code / Config Example — Advanced

GitHub Actions: zip bundle, upload to S3, create deployment, wait. (OIDC login, topic 394.) Bucket name and role ARN are examples.

```yaml
name: codedeploy-ec2                             # workflow name

on:
  push:
    branches: [main]                             # deploy from main

permissions:
  id-token: write                                # OIDC
  contents: read                                 # checkout

env:
  AWS_REGION: ap-south-1                         # region
  BUCKET: myco-codedeploy-artifacts              # S3 bucket for revisions
  APP: myapp                                     # CodeDeploy application
  GROUP: myapp-prod                              # deployment group

jobs:
  deploy:
    runs-on: ubuntu-latest                       # runner
    environment: production                      # approval gate possible
    steps:
      - uses: actions/checkout@v4                # get code

      - uses: actions/setup-node@v4              # Node for build/test
        with:
          node-version: 20                       # LTS example
          cache: npm                             # cache npm downloads

      - run: npm ci && npm test                  # install exactly from lockfile, run tests

      - uses: aws-actions/configure-aws-credentials@v4   # OIDC login
        with:
          role-to-assume: arn:aws:iam::111122223333:role/gha-codedeploy
          aws-region: ${{ env.AWS_REGION }}

      - name: Bundle and upload revision         # zip must contain appspec.yml at root
        run: |
          zip -r bundle.zip . -x ".git/*" "node_modules/.cache/*"   # create the bundle
          aws s3 cp bundle.zip "s3://$BUCKET/$APP/${{ github.sha }}.zip"   # upload revision

      - name: Create deployment                  # ask CodeDeploy to deploy it
        id: dep
        run: |
          ID=$(aws deploy create-deployment \
            --application-name "$APP" \
            --deployment-group-name "$GROUP" \
            --s3-location bucket="$BUCKET",key="$APP/${{ github.sha }}.zip",bundleType=zip \
            --description "GitHub ${{ github.sha }}" \
            --query deploymentId --output text)
          echo "id=$ID" >> "$GITHUB_OUTPUT"

      - name: Wait for success                   # fails the job on failure/rollback
        run: aws deploy wait deployment-successful --deployment-id "${{ steps.dep.outputs.id }}"
```

---

## 🟠 My Stack Integration
- **Node.js**: `after_install.sh` runs `npm ci --omit=dev` and `pm2 reload`; or `docker compose pull && up -d` if containerised.
- **FastAPI**: create a venv in `AfterInstall`, `systemctl restart fastapi` in `ApplicationStart`, validate on `/docs` or `/health`.
- **React**: not via CodeDeploy; use S3 + CloudFront.
- **Nginx**: keep config in the bundle, `nginx -t && systemctl reload nginx` in `AfterInstall` so a bad config fails the deploy before traffic is affected.
- **VPS**: CodeDeploy can also manage non-AWS servers ("on-premises instances") if you install the agent and register them, handy during a VPS-to-AWS migration.

```bash
#!/usr/bin/env bash
# scripts/after_install.sh : typical Nginx + Node step (run as root via runas: root)
set -e                                           # stop on error
cd /opt/myapp                                    # app folder
npm ci --omit=dev                                # install only production deps
nginx -t                                         # test Nginx config, fails deploy if invalid
systemctl reload nginx                           # apply Nginx config without dropping connections
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `appspec.yml` not at the root of the zip (it is in a subfolder).
✅ Correct: Zip from inside the project so `appspec.yml` is at the top level.

❌ Mistake 2: `ApplicationStop` fails on the first deploy because nothing is running.
✅ Correct: Make stop scripts idempotent with `|| true`.

❌ Mistake 3: Instance role cannot read the S3 bucket, so DownloadBundle fails.
✅ Correct: Give the EC2 instance profile `s3:GetObject` on the artifact bucket.

❌ Mistake 4: Agent not installed or not running.
✅ Correct: Install via user-data/SSM and check `systemctl status codedeploy-agent`.

❌ Mistake 5: No `ValidateService` hook, so broken app counts as success.
✅ Correct: Always add a real health check and enable auto rollback.

---

## 🧠 Tricky Interview Question
A CodeDeploy deployment fails on `ApplicationStop` for the new revision, even though your new scripts are fine. Why?

Answer: CodeDeploy runs `ApplicationStop` from the **previously successful revision's** scripts (the one on the instance), not the new bundle. If the old stop script was buggy, the new revision can never deploy until you fix the old file on the instance or deploy with "ignore ApplicationStop failures". That is why stop scripts must be simple and idempotent.

---

## ⚫ Interview Questions + Answers

Q1: What is a deployment group?
A1: A set of target instances (by EC2 tags, Auto Scaling groups) plus settings: deployment config, load balancer, alarms, rollback rules.

Q2: In-place vs blue/green on EC2 with CodeDeploy?
A2: In-place updates existing instances (cheaper, brief per-instance downtime handled by LB). Blue/green launches a fresh Auto Scaling group with the new revision and shifts the ALB, then terminates the old group.

Q3: Which deployment configs exist?
A3: `OneAtATime`, `HalfAtATime`, `AllAtOnce` for EC2; canary/linear presets for Lambda and ECS. You can also define a custom minimum-healthy-hosts config.

Q4: How do new Auto Scaling instances get the app?
A4: CodeDeploy hooks into the ASG; a new instance gets the last successful revision automatically.

Q5: How is the CI job notified of failure?
A5: `aws deploy wait deployment-successful` exits non-zero if the deployment fails or is stopped.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Fleets of EC2/on-prem servers or Auto Scaling groups
- You need hooks, rolling, and auto rollback without writing orchestration
- Compliance wants a deployment audit trail

❌ Avoid when:
- One small server (SSH/SSM is simpler)
- Fully containerised on EKS (use Helm/Argo CD)
- You need advanced traffic shaping on ECS (use native ECS or CodeDeploy for ECS, topic 388)

---

## 📊 Visual Diagram
```
 GitHub Actions
   | zip + appspec.yml
   v
 +---------+   create-deployment   +-------------+
 |   S3    | <-------------------- | CodeDeploy  |
 | bundle  |                       |  service    |
 +----+----+                       +------+------+
      | download                          | instructions
      v                                   v
 +-----------------------------------------------+
 | EC2 + CodeDeploy agent                         |
 | Stop -> BeforeInstall -> Files -> AfterInstall |
 |   -> Start -> ValidateService (curl /health)   |
 +-----------------------------------------------+
      fail? -> automatic rollback to last good revision
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| AppSpec | Deployment instruction file | Deployment निर्देश file |
| Revision | Versioned bundle in S3/GitHub | S3 में versioned bundle |
| Deployment group | Target servers + settings | Target servers और settings |
| Hook | Script at a lifecycle step | lifecycle step पर चलने वाली script |
| In-place | Update the same servers | उन्हीं servers को update करना |
| Agent | Daemon on server that executes deploy | server पर चलने वाला daemon |

---

## ⚡ 3-Line Summary
English: CodeDeploy ships a bundle to servers and runs ordered lifecycle hooks from appspec.yml.
English: It handles batch size, health validation, Auto Scaling and automatic rollback.
English: CI only uploads to S3, creates the deployment and waits for the result.
Hindi: CodeDeploy bundle को servers पर भेजती है और appspec.yml के क्रम से lifecycle hooks चलाती है।
Hindi: Batch size, health validation, Auto Scaling और automatic rollback यही संभालती है।
Hindi: CI सिर्फ S3 में upload करता है, deployment बनाता है और नतीजे का इंतज़ार करता है।

---

## ➡️ Next Topic
**391. AWS Lambda Deploy**: not all workloads need servers at all; next we deploy serverless functions from GitHub Actions.
