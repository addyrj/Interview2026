# 375. Multi-Region Deploy Pipeline
# हिंदी में: Multi-Region Deploy Pipeline (एक साथ कई AWS regions में deploy)

---

## 🔵 Simple Definition (English)
A multi-region deploy pipeline builds one Docker image once, makes it available in two or more AWS regions (for example `ap-south-1` Mumbai and `ap-southeast-1` Singapore), and rolls it out to each region in a controlled order. Traffic is then routed to the nearest healthy region using Route 53.

## 🔵 सरल परिभाषा (Hindi)
Multi-region deploy pipeline एक Docker image एक बार build करती है, उसे दो या ज़्यादा AWS regions (जैसे `ap-south-1` Mumbai और `ap-southeast-1` Singapore) में उपलब्ध कराती है, और हर region में controlled order में rollout करती है। फिर Route 53 user को सबसे पास वाले healthy region पर भेजता है।

---

## 🔴 Problem it Solves
- One region = one failure domain. If `ap-south-1` has an outage, the whole product is down.
- Users far from the region see high latency (Mumbai server, user in Singapore = 80-120 ms extra on every call).
- Compliance rules sometimes need data/processing near the user.
- Deploying manually to each region means different versions in different places and human errors.

## 🔴 यह क्यों बना? (Hindi)
- एक region = एक failure domain। अगर `ap-south-1` में outage आया तो पूरा product बंद।
- Region से दूर बैठे users को ज़्यादा latency मिलती है (Mumbai server, Singapore user = हर call पर 80-120 ms extra)।
- Compliance में कभी data/processing user के पास चाहिए होती है।
- हर region में हाथ से deploy करने पर versions अलग-अलग हो जाते हैं और गलतियाँ होती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Push to main -> GitHub Actions starts
Step 2 → Test job: lint + unit tests (once, not per region)
Step 3 → Build job: build image ONCE, tag with git SHA, push to primary ECR (Mumbai)
Step 4 → ECR cross-region replication copies the SAME image digest to Singapore
Step 5 → Deploy job #1 (primary region) -> update ECS service -> wait for stable
Step 6 → Smoke test primary region health URL
Step 7 → Deploy job #2 (secondary region) -> only if primary succeeded
Step 8 → Route 53 health checks + latency routing send users to healthy region
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → main पर push -> GitHub Actions शुरू
Step 2 → Test job: lint + unit tests (एक बार, हर region के लिए नहीं)
Step 3 → Build job: image एक बार build, git SHA से tag, primary ECR (Mumbai) में push
Step 4 → ECR cross-region replication वही image (same digest) Singapore में copy करता है
Step 5 → Deploy job #1 (primary) -> ECS service update -> stable होने तक wait
Step 6 → Primary का health URL smoke test
Step 7 → Deploy job #2 (secondary) -> सिर्फ अगर primary सफल रहा
Step 8 → Route 53 health check + latency routing user को healthy region पर भेजता है
```

---

## 🟡 Real World Example
Think of a food-delivery app like Swiggy. Mumbai is the main region; Singapore serves the South-East Asia customers. A bad release is dangerous: if you push to both regions at once and the release has a bug, both regions break together. So the pipeline deploys to Mumbai first, waits for ECS to report a stable service and for the smoke test to pass, and only then touches Singapore. If Mumbai fails, Singapore still runs the old good version and Route 53 keeps serving users.

## 🟡 Real Example Hindi mein
Swiggy जैसे food-delivery app को सोचो। Mumbai main region है, Singapore South-East Asia के customers के लिए। Bad release खतरनाक है: अगर दोनों regions में एक साथ push किया और bug निकला, तो दोनों एक साथ टूटेंगे। इसलिए pipeline पहले Mumbai में deploy करती है, ECS stable और smoke test pass होने का wait करती है, तब Singapore को छूती है। Mumbai fail हुआ तो Singapore पुराने अच्छे version पर चलता रहेगा और Route 53 users को serve करता रहेगा।

---

## 💻 Code / Config Example — Basic
Simplest version: a matrix runs the same deploy steps for each region (in parallel, no ordering). Good for learning, not safest.

```yaml
# .github/workflows/multi-region-basic.yml
name: multi-region-basic            # name shown in the Actions tab

on:
  push:
    branches: [main]                # run only when code lands on main

permissions:
  id-token: write                   # needed for OIDC login to AWS (no stored keys)
  contents: read                    # needed to checkout the repo

jobs:
  deploy:
    runs-on: ubuntu-latest          # GitHub-hosted Linux runner
    strategy:
      matrix:
        region: [ap-south-1, ap-southeast-1]   # one job copy per region
    steps:
      - uses: actions/checkout@v4   # get the code (example version, update as needed)
      - uses: aws-actions/configure-aws-credentials@v4   # login to AWS using OIDC
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-deploy   # example role ARN
          aws-region: ${{ matrix.region }}                            # region for THIS matrix job
      - name: Force new deployment    # tell ECS to pull the image again and restart tasks
        run: |
          aws ecs update-service --cluster prod --service api --force-new-deployment
```

## 💻 Code / Config Example — Advanced
Production style: test once, build once, replicate via ECR, deploy primary first, smoke test, then secondary.

```yaml
# .github/workflows/multi-region-deploy.yml
name: multi-region-deploy                 # workflow name

on:
  push:
    branches: [main]                      # deploy on merge to main
  workflow_dispatch: {}                   # also allow manual run from the UI

concurrency:
  group: prod-deploy                      # only one prod deploy at a time
  cancel-in-progress: false               # never cancel a deploy halfway

permissions:
  id-token: write                         # OIDC token for AWS
  contents: read                          # read repo

env:
  PRIMARY_REGION: ap-south-1              # Mumbai (build + first rollout)
  SECONDARY_REGION: ap-southeast-1        # Singapore (second rollout)
  REPO: myapp-api                         # ECR repository name (same in both regions)
  ROLE: arn:aws:iam::123456789012:role/gha-deploy   # example IAM role for OIDC

jobs:
  test:
    runs-on: ubuntu-latest                # runner for tests
    steps:
      - uses: actions/checkout@v4         # checkout code
      - uses: actions/setup-node@v4       # install Node.js
        with:
          node-version: 20                # match the Dockerfile Node version
          cache: npm                      # cache npm downloads
      - run: npm ci && npm test           # clean install and run tests

  build:
    needs: test                           # build only if tests pass
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.meta.outputs.tag }}  # pass image tag to later jobs
    steps:
      - uses: actions/checkout@v4
      - id: meta                          # step id so we can read its output
        run: echo "tag=${GITHUB_SHA::12}" >> "$GITHUB_OUTPUT"   # short SHA as immutable tag
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ env.ROLE }}           # assume deploy role
          aws-region: ${{ env.PRIMARY_REGION }}     # build pushes to Mumbai ECR
      - id: ecr
        uses: aws-actions/amazon-ecr-login@v2       # docker login to ECR
      - name: Build and push
        run: |
          IMG=${{ steps.ecr.outputs.registry }}/${{ env.REPO }}:${{ steps.meta.outputs.tag }}
          docker build -t "$IMG" .                  # build once
          docker push "$IMG"                        # ECR replication copies it to Singapore

  deploy-primary:
    needs: build                          # wait for image
    runs-on: ubuntu-latest
    environment: production-mumbai        # GitHub environment (can require approval)
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ env.ROLE }}
          aws-region: ${{ env.PRIMARY_REGION }}
      - name: Deploy and wait
        env:
          TAG: ${{ needs.build.outputs.tag }}       # image tag from build job
        run: ./scripts/deploy-ecs.sh "$TAG" prod api   # see "My Stack Integration"
      - name: Smoke test
        run: curl -fsS --retry 5 --retry-delay 5 https://mumbai.api.example.com/health

  deploy-secondary:
    needs: [build, deploy-primary]        # only after primary is healthy
    runs-on: ubuntu-latest
    environment: production-singapore
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ env.ROLE }}
          aws-region: ${{ env.SECONDARY_REGION }}   # now talk to Singapore
      - name: Wait until image is replicated
        run: |
          for i in $(seq 1 30); do   # retry up to 30 times (about 5 minutes)
            aws ecr describe-images --repository-name "$REPO" --image-ids imageTag=${{ needs.build.outputs.tag }} && exit 0   # image present -> done
            sleep 10                 # replication is async, wait and retry
          done
          echo "image not replicated in time" && exit 1   # fail the job clearly
      - name: Deploy and wait
        env:
          TAG: ${{ needs.build.outputs.tag }}
        run: ./scripts/deploy-ecs.sh "$TAG" prod api
```

---

## 🟠 My Stack Integration
Your Node.js/FastAPI API runs as an ECS service in each region behind an ALB. React is static (S3 + CloudFront, global, no regional deploy needed). Nginx on your single VPS can stay as an internal tool server. A small helper script keeps the workflow readable.

```bash
#!/usr/bin/env bash
# scripts/deploy-ecs.sh  usage: deploy-ecs.sh <image-tag> <cluster> <service>
set -euo pipefail                          # stop on any error, unset var, or pipe failure
TAG="$1"; CLUSTER="$2"; SERVICE="$3"       # read arguments
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)   # find AWS account id
REGION="${AWS_REGION:-ap-south-1}"         # region comes from configure-aws-credentials
IMAGE="$ACCOUNT.dkr.ecr.$REGION.amazonaws.com/myapp-api:$TAG"          # region-local ECR URL
# fetch current task definition JSON, swap the image, drop read-only fields
aws ecs describe-task-definition --task-definition "$SERVICE" --query taskDefinition \
 | jq --arg IMG "$IMAGE" 'del(.taskDefinitionArn,.revision,.status,.requiresAttributes,.compatibilities,.registeredAt,.registeredBy) | .containerDefinitions[0].image=$IMG' > /tmp/td.json
NEW=$(aws ecs register-task-definition --cli-input-json file:///tmp/td.json --query taskDefinition.taskDefinitionArn --output text)   # new revision
aws ecs update-service --cluster "$CLUSTER" --service "$SERVICE" --task-definition "$NEW" >/dev/null   # roll out
aws ecs wait services-stable --cluster "$CLUSTER" --services "$SERVICE"   # block until rollout done
echo "deployed $IMAGE in $REGION"
```

Enable replication once (CLI, run by an admin):

```bash
# replicate every repo in this account from ap-south-1 to ap-southeast-1
aws ecr put-replication-configuration --region ap-south-1 --replication-configuration \
 '{"rules":[{"destinations":[{"region":"ap-southeast-1","registryId":"123456789012"}]}]}'
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Building the image separately in each region.
✅ Correct: Build once, replicate. Same digest everywhere means you test what you ship.

❌ Mistake 2: Deploying all regions in parallel.
✅ Correct: Deploy a canary/primary region first, smoke test, then the rest.

❌ Mistake 3: Using the `latest` tag.
✅ Correct: Tag with git SHA; `latest` can point to different images in different regions during replication.

❌ Mistake 4: Long-lived AWS keys in GitHub secrets.
✅ Correct: Use OIDC with a role restricted to your repo and branch.

❌ Mistake 5: Forgetting that the database is not multi-region.
✅ Correct: Plan DB (Aurora Global, DynamoDB global tables, or read replicas) separately; app regions without data strategy are just latency.

---

## 🧠 Tricky Interview Question
Your pipeline deployed Mumbai fine, but Singapore deploy fails with "image not found". Re-running works 2 minutes later. Why, and how do you fix it permanently?

Answer: ECR replication is asynchronous. The image was pushed to Mumbai a few seconds ago and had not reached Singapore when the second job started. Fix: add a wait/retry loop that polls `aws ecr describe-images` in the destination region before updating the service (the Mumbai deploy time usually hides this, but not always), or push directly to both registries from the build job.

---

## ⚫ Interview Questions + Answers

Q1: Why build once and not once per region?
A1: Same artifact in all regions guarantees identical behavior, saves build time, and avoids drift caused by different base-image pulls at different times.

Q2: Active-active vs active-passive?
A2: Active-active: both regions serve traffic (Route 53 latency/weighted routing). Active-passive: secondary only takes over on failover. Active-active needs a multi-region data plan.

Q3: How does Route 53 know a region is down?
A3: Health checks against an endpoint (e.g. `/health` of the ALB). On repeated failure, the record is removed from answers and traffic goes to the other region.

Q4: How do you roll back a multi-region release?
A4: Re-run the deploy with the previous SHA tag (images are immutable), region by region, or use ECS deployment circuit breaker to auto-rollback per region.

Q5: How to keep secrets per region?
A5: AWS Secrets Manager / SSM Parameter Store are regional. Replicate secrets with Secrets Manager replication or create them in each region; task definitions reference region-local ARNs.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Users are spread across continents and latency matters
- You need disaster recovery beyond one region
- Compliance requires regional processing

❌ Avoid when:
- A small app with users in one country (cost and complexity double)
- Your database cannot be replicated yet
- Team has no on-call capacity for two regions

---

## 📊 Visual Diagram
```
                 GitHub Actions
   test -> build (once) -> push ECR Mumbai
                               |
                     ECR replication (async)
                               v
                         ECR Singapore
   deploy-primary (Mumbai) -> smoke test -> deploy-secondary (Singapore)

   Users --> Route 53 (latency + health check)
              |                       |
         ALB Mumbai              ALB Singapore
         ECS service             ECS service
              \                       /
               DB (primary + replica / global)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Region | Separate AWS geographic location | AWS का अलग भौगोलिक इलाका |
| ECR replication | Auto copy of images to other regions | Images का दूसरे region में auto copy |
| OIDC | Keyless login from GitHub to AWS | बिना key के GitHub से AWS login |
| Canary region | First region used to test a release | पहले test के लिए region |
| Latency routing | Route 53 sends user to the fastest region | सबसे तेज़ region पर भेजना |
| Active-active | All regions serve traffic | सभी regions traffic देते हैं |

---

## ⚡ 3-Line Summary
English: Build the image once and replicate it to every region through ECR.
Deploy region by region (primary first, smoke test, then others) using OIDC credentials.
Route 53 health checks and latency routing steer users to a healthy region.

Hindi: Image एक बार build करो और ECR से हर region में replicate करो।
Region-by-region deploy करो (पहले primary, smoke test, फिर बाकी), OIDC credentials के साथ।
Route 53 health check और latency routing users को healthy region पर भेजते हैं।

---

## ➡️ Next Topic
376. AWS ECR — Complete Guide: the registry that holds and replicates the images this pipeline depends on.
