# 386. Deploy to ECS with GitHub Actions
# हिंदी में: GitHub Actions से ECS पर Deploy करना

---

## 🔵 Simple Definition (English)
This pipeline builds your Docker image, pushes it to ECR, writes a new ECS task definition revision containing that image, and updates the ECS service, waiting until the rollout is stable. It uses OIDC for credentials and the official AWS actions.

## 🔵 सरल परिभाषा (Hindi)
यह pipeline आपकी Docker image build करती है, ECR में push करती है, उस image वाला नया ECS task definition revision बनाती है, और ECS service update करके rollout stable होने तक wait करती है। Credentials के लिए OIDC और official AWS actions इस्तेमाल होते हैं।

---

## 🔴 Problem it Solves
- Manual deploys (SSH, console clicks) are slow, inconsistent and unaudited.
- "It works on my machine": the deployed artifact is not the tested one.
- Nobody knows which commit is in production.

## 🔴 यह क्यों बना? (Hindi)
- Manual deploys (SSH, console clicks) धीमे, असंगत और बिना audit के होते हैं।
- "मेरी machine पर चलता है": deploy हुई चीज़ tested वाली नहीं होती।
- किसी को पता नहीं production में कौन-सा commit है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Push/merge to main triggers the workflow
Step 2 → Test job (npm ci, npm test)
Step 3 → OIDC: assume AWS role (no stored keys)
Step 4 → Login to ECR, docker build, push :GIT_SHA
Step 5 → amazon-ecs-render-task-definition: copy current task def JSON, set new image
Step 6 → amazon-ecs-deploy-task-definition: register revision, update service
Step 7 → wait-for-service-stability: true -> job fails if rollout fails (circuit breaker rollback)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → main पर push/merge से workflow चलता है
Step 2 → Test job (npm ci, npm test)
Step 3 → OIDC: AWS role assume (कोई stored keys नहीं)
Step 4 → ECR login, docker build, :GIT_SHA push
Step 5 → amazon-ecs-render-task-definition: मौजूदा task def JSON copy करके नई image सेट
Step 6 → amazon-ecs-deploy-task-definition: revision register, service update
Step 7 → wait-for-service-stability: true -> rollout fail हो तो job fail (circuit breaker rollback)
```

---

## 🟡 Real World Example
A team merges 12 PRs a day. Each merge to `main` runs this workflow, and 6-8 minutes later the new version serves production traffic. A reviewer can see in the Actions log which SHA is live. When a deploy fails health checks, the ECS circuit breaker rolls back and the workflow turns red, so nobody has to babysit.

## 🟡 Real Example Hindi mein
एक team दिन में 12 PRs merge करती है। `main` पर हर merge यह workflow चलाता है, और 6-8 मिनट बाद नया version production traffic serve करता है। Reviewer Actions log में देख सकता है कि कौन-सा SHA live है। Deploy health check में fail हो तो ECS circuit breaker rollback करता है और workflow लाल हो जाता है, किसी को निगरानी नहीं करनी पड़ती।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/deploy-ecs-basic.yml
name: deploy-ecs-basic                 # workflow name
on:
  push:
    branches: [main]                   # deploy on every push to main
permissions:
  id-token: write                      # required for OIDC
  contents: read                       # required for checkout
jobs:
  deploy:
    runs-on: ubuntu-latest             # runner
    steps:
      - uses: actions/checkout@v4      # get code (example version)
      - uses: aws-actions/configure-aws-credentials@v4   # OIDC login
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-ecs-deploy   # example role
          aws-region: ap-south-1       # region
      - id: ecr
        uses: aws-actions/amazon-ecr-login@v2             # docker login to ECR
      - name: Build and push
        run: |
          IMG=${{ steps.ecr.outputs.registry }}/myapp-api:${{ github.sha }}
          docker build -t "$IMG" .     # build image
          docker push "$IMG"           # push image tagged with commit SHA
          echo "IMG=$IMG" >> "$GITHUB_ENV"   # make it available to next steps
      - name: Force service to use new task def
        run: |
          aws ecs describe-task-definition --task-definition api --query taskDefinition > td.json   # current definition
          jq --arg i "$IMG" 'del(.taskDefinitionArn,.revision,.status,.requiresAttributes,.compatibilities,.registeredAt,.registeredBy) | .containerDefinitions[0].image=$i' td.json > new.json   # swap image
          ARN=$(aws ecs register-task-definition --cli-input-json file://new.json --query taskDefinition.taskDefinitionArn --output text)   # new revision
          aws ecs update-service --cluster prod --service api --task-definition "$ARN"   # roll out
          aws ecs wait services-stable --cluster prod --services api                    # wait until done
```

## 💻 Code / Config Example — Advanced
Uses the official render + deploy actions, a stored task definition file in git, tests first, concurrency control and a GitHub environment.

```yaml
# .github/workflows/deploy-ecs.yml
name: deploy-ecs                         # workflow name
on:
  push:
    branches: [main]                     # production branch
concurrency:
  group: deploy-prod-ecs                 # one deploy at a time
  cancel-in-progress: false              # do not cancel a running deploy
permissions:
  id-token: write                        # OIDC
  contents: read                         # checkout
env:
  AWS_REGION: ap-south-1                 # region
  ECR_REPOSITORY: myapp-api              # ECR repo name
  ECS_CLUSTER: prod                      # cluster
  ECS_SERVICE: api                       # service
  CONTAINER_NAME: api                    # container name inside the task definition
  TASK_DEF_FILE: .aws/task-definition.json   # task definition kept in git
jobs:
  test:
    runs-on: ubuntu-latest               # test runner
    steps:
      - uses: actions/checkout@v4        # code
      - uses: actions/setup-node@v4      # Node
        with:
          node-version: 20               # version
          cache: npm                     # cache deps
      - run: npm ci && npm test          # install and test
  deploy:
    needs: test                          # only if tests pass
    runs-on: ubuntu-latest
    environment: production              # can require manual approval
    steps:
      - uses: actions/checkout@v4        # code
      - uses: aws-actions/configure-aws-credentials@v4   # short-lived credentials
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-ecs-deploy
          aws-region: ${{ env.AWS_REGION }}
      - id: ecr
        uses: aws-actions/amazon-ecr-login@v2             # ECR login
      - uses: docker/setup-buildx-action@v3               # buildx for cache
      - id: build
        uses: docker/build-push-action@v6                 # build + push
        with:
          context: .
          push: true
          tags: ${{ steps.ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - id: render
        uses: aws-actions/amazon-ecs-render-task-definition@v1   # inject image into JSON
        with:
          task-definition: ${{ env.TASK_DEF_FILE }}        # file in repo
          container-name: ${{ env.CONTAINER_NAME }}        # which container to change
          image: ${{ steps.ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ github.sha }}
      - uses: aws-actions/amazon-ecs-deploy-task-definition@v2   # register + update service
        with:
          task-definition: ${{ steps.render.outputs.task-definition }}   # rendered file
          service: ${{ env.ECS_SERVICE }}
          cluster: ${{ env.ECS_CLUSTER }}
          wait-for-service-stability: true                 # fail if rollout fails
```

Least-privilege deploy role policy (attach to `gha-ecs-deploy`, besides the ECR push rights from topic 377):

```yaml
# deploy-role-policy.yml  - policy statements shown as YAML for readability (convert to JSON in IAM)
Version: "2012-10-17"
Statement:
  - Effect: Allow
    Action: [ecs:DescribeServices, ecs:DescribeTaskDefinition, ecs:RegisterTaskDefinition, ecs:UpdateService]
    Resource: "*"                                   # Describe/Register cannot be scoped to one ARN
  - Effect: Allow
    Action: iam:PassRole                            # needed to give roles to the new task def
    Resource:
      - arn:aws:iam::123456789012:role/ecsTaskExecutionRole
      - arn:aws:iam::123456789012:role/api-task-role
    Condition:
      StringEquals: {"iam:PassedToService": "ecs-tasks.amazonaws.com"}   # only to ECS tasks
```

---

## 🟠 My Stack Integration
- Node.js: the above. FastAPI: swap `setup-node` for `setup-python` and `pytest`.
- React: separate workflow: `npm run build`, `aws s3 sync build/ s3://my-frontend --delete`, then CloudFront invalidation.
- Keep the VPS path as a fallback: a second job with `appleboy/ssh-action` is possible, but ECS removes the need.

```yaml
# .github/workflows/frontend.yml  - React to S3 + CloudFront
name: frontend                         # workflow name
on:
  push:
    branches: [main]
    paths: ["frontend/**"]             # only when frontend changes
permissions: {id-token: write, contents: read}
jobs:
  ship:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: {node-version: 20, cache: npm, cache-dependency-path: frontend/package-lock.json}
      - run: cd frontend && npm ci && npm run build    # build static files
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-frontend
          aws-region: ap-south-1
      - run: aws s3 sync frontend/build s3://my-frontend --delete   # upload, remove old files
      - run: aws cloudfront create-invalidation --distribution-id E123EXAMPLE --paths "/*"   # refresh CDN
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting `wait-for-service-stability`.
✅ Correct: Without it the job is green even if the rollout later rolls back.

❌ Mistake 2: Admin credentials for the workflow.
✅ Correct: OIDC role with the minimal ECS/ECR/PassRole permissions.

❌ Mistake 3: Deploying with `latest` tag and `force-new-deployment`.
✅ Correct: SHA tag in a new task definition revision; traceable and rollback-friendly.

❌ Mistake 4: Running deploys from pull requests of forks.
✅ Correct: Only `push` to main, or environments with required reviewers.

❌ Mistake 5: Missing `iam:PassRole`.
✅ Correct: Add it with a `PassedToService` condition; otherwise register fails with AccessDenied.

---

## 🧠 Tricky Interview Question
The workflow is green, but the app in production still runs the old code. The service shows the new task definition revision. What do you check?

Answer: Check whether the new tasks actually became healthy and the old ones were replaced: the deployment may have been rolled back by the circuit breaker while the job was not waiting (no `wait-for-service-stability`), so the service points back to the old revision. Also verify the image tag in the revision, that the ALB points to the new tasks, and CloudFront or browser caching for frontend assets.

---

## ⚫ Interview Questions + Answers

Q1: Why render a task definition file instead of editing via jq?
A1: The official action is maintained, keeps the definition in git (reviewable), and avoids fragile scripting. jq works but you own the read-only-field cleanup.

Q2: How to do approvals before prod?
A2: GitHub environments with required reviewers; the job waits for an approver.

Q3: How do you roll back?
A3: Re-run the workflow on the previous commit, or `aws ecs update-service --task-definition api:<old>`. Circuit breaker rolls back automatically on failed deploys.

Q4: How does the workflow know the deploy succeeded?
A4: `wait-for-service-stability` polls until running count equals desired with the new revision primary and old tasks stopped, within a timeout (default 30 minutes; adjustable).

Q5: Secrets in the pipeline?
A5: App secrets live in Secrets Manager/SSM referenced by the task definition. GitHub only holds non-secret IDs (role ARN is not secret), so nothing sensitive is stored there.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every ECS service; trunk-based deployments to staging and prod

❌ Avoid when:
- You need advanced traffic shifting (use CodeDeploy blue/green, topic 388)
- Infra changes (use Terraform/CloudFormation pipeline separately)

---

## 📊 Visual Diagram
```
 push main
    |
  test --> OIDC --> ECR login --> build+push :sha
                                      |
          render task def (new image) v
                       register revision api:43
                                      |
                 update service --> rolling update --> stable?
                                      | yes: green    | no: circuit breaker rollback + red
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OIDC | Keyless auth GitHub to AWS | बिना key का auth |
| Render | Insert new image in task def JSON | Task def में नई image डालना |
| Stability | Rollout complete and healthy | Rollout पूरा और healthy |
| PassRole | Permission to give a role to a service | Service को role देने की permission |
| Environment | GitHub gate with approvals | Approval वाला GitHub gate |

---

## ⚡ 3-Line Summary
English: Test, build, push :sha to ECR, render a new task definition and update the service.
Use OIDC with a least-privilege role and wait for service stability.
Task definition lives in git so every deploy is reviewable and rollback is easy.

Hindi: Test, build, :sha ECR में push, नया task definition render और service update।
Least-privilege role के साथ OIDC इस्तेमाल करो और service stability का wait करो।
Task definition git में रहती है, इसलिए हर deploy reviewable और rollback आसान है।

---

## ➡️ Next Topic
387. ECS Rolling Update: what ECS does between "update service" and "stable".
