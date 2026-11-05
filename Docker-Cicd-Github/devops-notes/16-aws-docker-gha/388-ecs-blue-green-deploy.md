# 388. ECS Blue-Green Deploy
# हिंदी में: ECS Blue-Green Deployment

---

## 🔵 Simple Definition (English)
Blue-Green on ECS means you run the **new version (green)** next to the **old version (blue)**, test green on a separate listener, and then switch the load balancer traffic from blue to green in one step. If something breaks, you switch back instantly. On ECS this is usually done with **AWS CodeDeploy** (deployment controller type `CODE_DEPLOY`) and an **ALB with two target groups**.

## 🔵 सरल परिभाषा (Hindi)
ECS पर Blue-Green का मतलब है कि **नया version (green)** पुराने **version (blue)** के बगल में चलता है, green को अलग listener पर test किया जाता है, और फिर load balancer का traffic एक ही step में blue से green पर switch हो जाता है। कुछ गड़बड़ हो तो तुरंत वापस switch कर सकते हैं। ECS पर यह आमतौर पर **AWS CodeDeploy** (deployment controller `CODE_DEPLOY`) और **दो target groups वाले ALB** से होता है।

---

## 🔴 Problem it Solves
A rolling update (previous topic) replaces tasks one by one. During that time old and new code both serve users, a bad release hits some real users before you notice, and rollback means another full rolling deploy (minutes). For database-compatible but risky releases (payment flow, new auth) this is too slow and too exposed.

Blue-green gives: zero downtime, a test window on the new version before any user sees it, and a rollback that is just a listener flip (seconds).

## 🔴 यह क्यों बना? (Hindi)
Rolling update में tasks एक-एक करके बदलते हैं। उस दौरान पुराना और नया दोनों code users को serve करते हैं, बुरी release कुछ real users तक पहुँच जाती है, और rollback का मतलब एक और पूरा rolling deploy (कई मिनट)। Payment या auth जैसी risky release के लिए यह धीमा और असुरक्षित है।

Blue-green में zero downtime, user को दिखाने से पहले नए version को test करने की window, और rollback सिर्फ listener flip (कुछ seconds) में मिलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → CI builds image, pushes to ECR with tag = git SHA
Step 2 → CI renders a NEW task definition revision with that image
Step 3 → CI calls CodeDeploy (appspec.yaml points to the new task def)
Step 4 → CodeDeploy starts GREEN tasks in the idle target group (TG-2)
Step 5 → ALB test listener (port 8080) sends test traffic to GREEN
Step 6 → Optional lifecycle hook (Lambda) runs smoke tests
Step 7 → CodeDeploy shifts production listener (443) BLUE -> GREEN
          (AllAtOnce, Linear 10%/min, or Canary 10% then 90%)
Step 8 → Old BLUE tasks stay alive for a "termination wait" (e.g. 15 min)
Step 9 → Alarm fires? -> auto-rollback to BLUE. Otherwise BLUE is terminated.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → CI image build करके ECR में git SHA tag के साथ push करता है
Step 2 → CI उस image के साथ नया task definition revision बनाता है
Step 3 → CI CodeDeploy को call करता है (appspec.yaml नए task def को point करती है)
Step 4 → CodeDeploy खाली target group (TG-2) में GREEN tasks शुरू करता है
Step 5 → ALB test listener (8080) GREEN पर test traffic भेजता है
Step 6 → Optional hook (Lambda) smoke tests चलाता है
Step 7 → CodeDeploy production listener (443) को BLUE से GREEN पर shift करता है
          (AllAtOnce, Linear 10%/min, या Canary 10% फिर 90%)
Step 8 → पुराने BLUE tasks कुछ देर (जैसे 15 मिनट) चालू रहते हैं
Step 9 → Alarm बजे तो auto-rollback; वरना BLUE terminate हो जाता है
```

---

## 🟡 Real World Example
A food-delivery startup (Swiggy-style) runs its `orders-api` on ECS Fargate behind an ALB. Friday dinner is peak traffic, so a bad deploy costs real money. They use CodeDeploy with `CodeDeployDefault.ECSCanary10Percent5Minutes`: 10% of users hit the new version for 5 minutes, a CloudWatch alarm on 5xx rate watches it, and if the alarm fires CodeDeploy rolls back automatically. The team ships at 6 PM on Friday without fear.

## 🟡 Real Example Hindi mein
एक food-delivery startup (Swiggy जैसा) अपनी `orders-api` ECS Fargate पर ALB के पीछे चलाता है। शुक्रवार रात peak traffic होता है, इसलिए bad deploy का मतलब सीधा नुकसान। वे CodeDeploy का `CodeDeployDefault.ECSCanary10Percent5Minutes` इस्तेमाल करते हैं: 5 मिनट तक 10% users नए version पर जाते हैं, 5xx rate पर CloudWatch alarm नज़र रखता है, और alarm बजे तो CodeDeploy खुद rollback कर देता है। टीम शुक्रवार शाम 6 बजे बिना डर के release करती है।

---

## 💻 Code / Config Example — Basic

The `appspec.yaml` CodeDeploy needs for ECS (it is generated/filled by the GitHub Action, but you must understand it).

```yaml
# appspec.yaml  (ECS flavour: note the Resources list, not "files/hooks" like EC2)
version: 0.0                                    # appspec version, always 0.0 for ECS
Resources:                                      # what to deploy
  - TargetService:                              # fixed key name for ECS
      Type: AWS::ECS::Service                   # resource type CodeDeploy understands
      Properties:                               # service details
        TaskDefinition: <TASK_DEFINITION>       # placeholder; the GitHub Action replaces it with the new ARN
        LoadBalancerInfo:                       # which container receives ALB traffic
          ContainerName: "api"                  # must match container name in task definition
          ContainerPort: 3000                   # Node.js app port inside the container
        PlatformVersion: "LATEST"               # Fargate platform version
```

Create the service once (CLI sketch) with the CODE_DEPLOY controller:

```bash
# one-time: create ECS service that is controlled by CodeDeploy (not by ECS rolling)
aws ecs create-service \
  --cluster prod-cluster \
  --service-name orders-api \
  --task-definition orders-api:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --deployment-controller type=CODE_DEPLOY \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:ap-south-1:111122223333:targetgroup/tg-blue/abc,containerName=api,containerPort=3000 \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-aaa,subnet-bbb],securityGroups=[sg-123],assignPublicIp=DISABLED}"
```

## 💻 Code / Config Example — Advanced

Full GitHub Actions workflow: build, push to ECR, render task definition, and trigger CodeDeploy blue-green, authenticating with OIDC (see topic 394). Action versions are examples; check the latest majors.

```yaml
name: deploy-ecs-bluegreen                       # workflow name in the Actions tab

on:
  push:
    branches: [main]                             # deploy on every merge to main

permissions:
  id-token: write                                # needed for OIDC token request
  contents: read                                 # needed for checkout

env:
  AWS_REGION: ap-south-1                         # Mumbai region
  ECR_REPOSITORY: orders-api                     # ECR repo name
  ECS_SERVICE: orders-api                        # ECS service name
  ECS_CLUSTER: prod-cluster                      # ECS cluster name
  CONTAINER_NAME: api                            # container name inside task def
  CD_APPLICATION: orders-api-cd                  # CodeDeploy application name
  CD_GROUP: orders-api-dg                        # CodeDeploy deployment group name

jobs:
  deploy:
    runs-on: ubuntu-latest                       # GitHub hosted runner
    environment: production                      # lets you add manual approval rules
    concurrency: deploy-prod                     # never run two prod deploys together
    steps:
      - uses: actions/checkout@v4                # get the source code

      - uses: aws-actions/configure-aws-credentials@v4   # OIDC login, no stored keys
        with:
          role-to-assume: arn:aws:iam::111122223333:role/gha-ecs-deploy   # role trusted for this repo
          aws-region: ${{ env.AWS_REGION }}      # region for all later aws calls

      - id: ecr                                  # id so later steps can read outputs
        uses: aws-actions/amazon-ecr-login@v2    # docker login to ECR

      - id: build                                # build and push step
        env:
          REGISTRY: ${{ steps.ecr.outputs.registry }}   # 111122223333.dkr.ecr.ap-south-1.amazonaws.com
          TAG: ${{ github.sha }}                 # immutable tag = commit SHA
        run: |                                   # multi-line shell
          docker build -t "$REGISTRY/$ECR_REPOSITORY:$TAG" .
          docker push "$REGISTRY/$ECR_REPOSITORY:$TAG"
          echo "image=$REGISTRY/$ECR_REPOSITORY:$TAG" >> "$GITHUB_OUTPUT"

      - id: taskdef                              # render new task definition JSON
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: .aws/task-definition.json   # template file kept in the repo
          container-name: ${{ env.CONTAINER_NAME }}    # which container to update
          image: ${{ steps.build.outputs.image }}      # new image URI

      - uses: aws-actions/amazon-ecs-deploy-task-definition@v2   # register + start CodeDeploy
        with:
          task-definition: ${{ steps.taskdef.outputs.task-definition }}   # rendered file
          service: ${{ env.ECS_SERVICE }}        # ECS service
          cluster: ${{ env.ECS_CLUSTER }}        # ECS cluster
          codedeploy-appspec: .aws/appspec.yaml  # appspec in repo (TaskDefinition placeholder)
          codedeploy-application: ${{ env.CD_APPLICATION }}      # CodeDeploy app
          codedeploy-deployment-group: ${{ env.CD_GROUP }}       # deployment group
          wait-for-service-stability: true       # fail the job if the deploy fails/rolls back
```

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: each is one ECS service with container port 3000 / 8000; `/health` endpoint is used by the ALB target group health check (make it cheap and DB-independent or use a shallow check).
- **React**: do NOT use ECS for the static build; use S3 + CloudFront (topic 397/398).
- **Nginx**: ALB replaces Nginx for load balancing on ECS; keep Nginx only as a sidecar if you need special rewrites.
- **VPS**: if you are still on one VPS, blue-green can be imitated with two compose stacks and an Nginx `upstream` switch (topic 402/403). ECS is the managed version.
- **Database**: both blue and green talk to the SAME database, so migrations must be backward compatible (expand, deploy, contract).

```yaml
# .aws/task-definition.json is JSON, but the key knobs for blue-green live in the deployment group:
# (CLI to create the deployment group, shown as bash)
```

```bash
# one-time: create CodeDeploy app + deployment group for ECS blue-green
aws deploy create-application --application-name orders-api-cd --compute-platform ECS
aws deploy create-deployment-group \
  --application-name orders-api-cd \
  --deployment-group-name orders-api-dg \
  --service-role-arn arn:aws:iam::111122223333:role/codedeploy-ecs-role \
  --deployment-config-name CodeDeployDefault.ECSCanary10Percent5Minutes \
  --ecs-services clusterName=prod-cluster,serviceName=orders-api \
  --load-balancer-info '{"targetGroupPairInfoList":[{"targetGroups":[{"name":"tg-blue"},{"name":"tg-green"}],"prodTrafficRoute":{"listenerArns":["arn:aws:elasticloadbalancing:ap-south-1:111122223333:listener/app/prod/abc/def"]},"testTrafficRoute":{"listenerArns":["arn:aws:elasticloadbalancing:ap-south-1:111122223333:listener/app/prod/abc/ghi"]}}]}' \
  --blue-green-deployment-configuration '{"terminateBlueInstancesOnDeploymentSuccess":{"action":"TERMINATE","terminationWaitTimeInMinutes":15},"deploymentReadyOption":{"actionOnTimeout":"CONTINUE_DEPLOYMENT"}}' \
  --auto-rollback-configuration enabled=true,events=DEPLOYMENT_FAILURE,DEPLOYMENT_STOP_ON_ALARM
```

Note: AWS also released a native ECS blue/green strategy (no CodeDeploy) in 2025. Its API and workflow differ; check current ECS docs before choosing, as this is version-dependent.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Creating the service with the default `ECS` rolling controller and expecting CodeDeploy to work.
✅ Correct: The deployment controller can only be chosen at creation time here; create the service with `type=CODE_DEPLOY`.

❌ Mistake 2: Breaking DB schema in the release (dropping a column), so rollback to blue crashes.
✅ Correct: Use expand/contract migrations; blue and green must both work with the same schema.

❌ Mistake 3: Health check path hits the database and the DB is slow, so green never turns healthy.
✅ Correct: Use a light `/health` for the target group; a deeper `/ready` for smoke tests.

❌ Mistake 4: No alarm attached, so "auto rollback" never triggers.
✅ Correct: Attach CloudWatch alarms (5xx count, p95 latency) to the deployment group.

❌ Mistake 5: Using the `latest` tag in the task definition.
✅ Correct: Use the commit SHA tag so every revision is traceable and rollback is exact.

---

## 🧠 Tricky Interview Question
Your blue-green deploy succeeded, but 10 minutes later users report a bug. CodeDeploy already terminated blue after 5 minutes. What are your options, and how would you have avoided this?

Answer: CodeDeploy rollback only works while the deployment is in progress or within the termination wait window. After that, rollback = deploy the previous task definition revision again (a new deployment, takes minutes). To avoid it, set `terminationWaitTimeInMinutes` longer (30-60 min for critical services), keep alarms on business metrics (order success rate, not only 5xx), and keep the previous image in ECR (do not expire it with a lifecycle rule too early).

---

## ⚫ Interview Questions + Answers

Q1: Why does ECS blue-green need two target groups?
A1: Blue tasks stay registered in one group while green tasks register in the other. CodeDeploy changes the listener rule to point at the other group, which is the "switch". One group cannot hold both versions separately.

Q2: Blue-green vs rolling update, when do you choose which?
A2: Rolling is cheap and simple (no extra capacity) and fine for backward-compatible changes. Blue-green needs 2x capacity during deploy but gives instant rollback and pre-traffic testing. Choose blue-green for risky or revenue-critical services.

Q3: What is a canary deployment config in CodeDeploy?
A3: It shifts a small percent (for example 10%) of traffic first, waits a set time (5 min), then shifts the rest. Linear shifts equal steps every N minutes. AllAtOnce shifts 100% immediately.

Q4: What are lifecycle hooks in ECS CodeDeploy?
A4: Points like `BeforeInstall`, `AfterInstall`, `AfterAllowTestTraffic`, `BeforeAllowTraffic`, `AfterAllowTraffic` where a Lambda function runs checks and returns Succeeded or Failed. A failed hook stops and rolls back the deploy.

Q5: How does the GitHub Action know the deploy failed?
A5: With `wait-for-service-stability: true` the action waits for the CodeDeploy deployment to finish; rollback or failure makes the step (and the job) fail.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Zero-downtime plus instant rollback is a business requirement
- You want to smoke-test the new version on a test listener before real users
- Traffic is high and canary/linear shifting reduces blast radius

❌ Avoid when:
- A small internal tool where rolling update is enough (cheaper)
- The release includes a non-backward-compatible DB change
- You cannot afford double capacity during the deploy window

---

## 📊 Visual Diagram
```
                      +------------------+
   Users ---HTTPS---> | ALB :443 (prod)  |----+
                      | ALB :8080 (test) |-+  |
                      +------------------+ |  |
                                           |  |  (switch at step 7)
                      +--------------------+  +---------------------+
                      v                                             v
              +----------------+                            +----------------+
              | TG-2  GREEN    |                            | TG-1  BLUE     |
              | new tasks v2   |                            | old tasks v1   |
              +----------------+                            +----------------+
                      ^
   GitHub Actions --> ECR image --> task def rev N --> CodeDeploy
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Blue | Currently live version | अभी live version |
| Green | New version being released | नया release होने वाला version |
| Target Group | Set of tasks the ALB sends traffic to | ALB जिन tasks को traffic भेजता है उनका group |
| Listener | ALB port/rule that receives traffic | ALB का port/rule जो traffic लेता है |
| AppSpec | CodeDeploy deployment instructions file | CodeDeploy के निर्देशों की file |
| Canary | Small % first, rest later | पहले थोड़ा %, बाकी बाद में |
| Termination wait | Time blue is kept after switch | switch के बाद blue को रखने का समय |

---

## ⚡ 3-Line Summary
English: ECS blue-green runs new tasks beside old ones and flips ALB traffic via CodeDeploy.
English: You get zero downtime, pre-traffic tests and seconds-long rollback, at the cost of 2x capacity during deploy.
English: Keep DB changes backward compatible, attach alarms, and use SHA-tagged images.
Hindi: ECS blue-green नए tasks को पुराने के बगल में चलाकर CodeDeploy से ALB traffic flip करता है।
Hindi: Zero downtime, traffic से पहले test और कुछ seconds में rollback मिलता है, बदले में deploy के दौरान 2x capacity लगती है।
Hindi: DB changes backward compatible रखें, alarms लगाएँ और SHA-tag वाली images इस्तेमाल करें।

---

## ➡️ Next Topic
**389. AWS EC2 Deploy with GitHub Actions**: not every app runs on containers orchestrated by ECS; many teams (and your VPS-style setup) deploy straight to EC2, so we look at SSH/SSM based deploys next.
