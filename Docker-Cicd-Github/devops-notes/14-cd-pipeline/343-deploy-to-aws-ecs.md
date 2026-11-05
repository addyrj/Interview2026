# 343. Deploy to AWS ECS
# हिंदी में: AWS ECS पर Deploy करना

---

## 🔵 Simple Definition (English)
Amazon ECS (Elastic Container Service) runs your containers as **tasks** inside a **service** that keeps N copies alive. A deploy means registering a new **task definition revision** with the new image and telling the service to roll out that revision (rolling update, optionally with a deployment circuit breaker).

## 🔵 सरल परिभाषा (Hindi)
Amazon ECS (Elastic Container Service) आपके containers को **service** के अंदर **tasks** के रूप में चलाता है जो N copies हमेशा चालू रखती है। Deploy का मतलब है नई image के साथ नया **task definition revision** register करना और service से उसे rolling update में लगाने को कहना (deployment circuit breaker के साथ)।

---

## 🔴 Problem it Solves
On VPS/EC2 you patch servers, restart crashed containers yourself, and scale by hand. ECS (especially with Fargate) schedules containers, replaces unhealthy ones, integrates with ALB health checks and rolls back failed deployments, so you manage only the task definition.

## 🔴 यह क्यों बना? (Hindi)
VPS/EC2 पर आपको servers patch करने, crashed containers restart करने और scale हाथ से करना पड़ता है। ECS (खासकर Fargate के साथ) containers schedule करता है, unhealthy को replace करता है, ALB health checks से जुड़ता है और fail हुए deployment को rollback करता है; आप सिर्फ task definition संभालते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build image, push to ECR tagged with commit SHA
Step 2 → Download current task definition JSON from ECS
Step 3 → amazon-ecs-render-task-definition swaps in the new image URI
Step 4 → amazon-ecs-deploy-task-definition registers a new revision
Step 5 → Service updates: starts new tasks, waits ALB health, drains old
Step 6 → wait-for-service-stability: true → job waits for steady state
Step 7 → Circuit breaker with rollback reverts if new tasks keep failing
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Image build करके commit SHA tag के साथ ECR पर push करो।
Step 2 → ECS से मौजूदा task definition JSON download करो।
Step 3 → `render-task-definition` नई image URI डाल देता है।
Step 4 → `deploy-task-definition` नया revision register करता है।
Step 5 → Service नए tasks शुरू करती है, ALB health का इंतज़ार करती है, पुराने drain करती है।
Step 6 → `wait-for-service-stability: true` से job steady state तक रुकता है।
Step 7 → Circuit breaker + rollback, नए tasks बार-बार fail हों तो पिछले version पर लौटता है।

---

## 🟡 Real World Example
Swiggy-style order service on ECS Fargate: 4 tasks behind an ALB, `minimumHealthyPercent=100`, `maximumPercent=200`. A deploy launches 4 new tasks, waits until `/health` passes on the target group, then drains the old 4. If the new tasks fail health checks, the circuit breaker rolls back automatically and the pipeline reports failure.

## 🟡 Real Example Hindi mein
Swiggy जैसी order service ECS Fargate पर: ALB के पीछे 4 tasks, `minimumHealthyPercent=100`, `maximumPercent=200`। Deploy में 4 नए tasks शुरू होते हैं, target group पर `/health` pass होने तक रुकते हैं, फिर पुराने 4 drain होते हैं। नए tasks fail हों तो circuit breaker अपने आप rollback करता है और pipeline fail दिखाती है।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/deploy-ecs-basic.yml (force new deployment of same tag)
name: deploy-ecs-basic                 # workflow name
on:
  workflow_dispatch:                   # manual trigger
permissions:
  id-token: write                      # OIDC
  contents: read
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4   # assume role
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-ecs-deploy  # example
          aws-region: ap-south-1
      - name: Restart service          # re-pull the same tag
        run: |
          aws ecs update-service --cluster prod --service api --force-new-deployment
          aws ecs wait services-stable --cluster prod --services api
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/deploy-ecs.yml (build -> ECR -> render -> deploy -> wait)
name: deploy-ecs
on:
  push:
    branches: [main]
permissions:
  id-token: write
  contents: read
env:
  AWS_REGION: ap-south-1
  ECR_REPOSITORY: api                  # ECR repo name
  ECS_CLUSTER: prod                    # cluster name
  ECS_SERVICE: api                     # service name
  CONTAINER_NAME: api                  # container name inside task definition
  TASK_DEF_FILE: .aws/task-definition.json   # task definition kept in git
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE }}
          aws-region: ${{ env.AWS_REGION }}
      - id: ecr
        uses: aws-actions/amazon-ecr-login@v2
      - name: Build and push image
        id: image
        run: |
          IMAGE="${{ steps.ecr.outputs.registry }}/${ECR_REPOSITORY}:${GITHUB_SHA}"  # full URI
          docker build -t "$IMAGE" .                    # build
          docker push "$IMAGE"                          # push
          echo "image=$IMAGE" >> "$GITHUB_OUTPUT"       # pass to next step
      - name: Render task definition   # inject new image
        id: render
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: ${{ env.TASK_DEF_FILE }}
          container-name: ${{ env.CONTAINER_NAME }}
          image: ${{ steps.image.outputs.image }}
      - name: Deploy and wait          # register revision + update service
        uses: aws-actions/amazon-ecs-deploy-task-definition@v2
        with:
          task-definition: ${{ steps.render.outputs.task-definition }}
          service: ${{ env.ECS_SERVICE }}
          cluster: ${{ env.ECS_CLUSTER }}
          wait-for-service-stability: true   # fail job if not stable
```

Task definition kept in git:

```json
{
  "family": "api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/api-task-role",
  "containerDefinitions": [{
    "name": "api",
    "image": "123456789012.dkr.ecr.ap-south-1.amazonaws.com/api:placeholder",
    "essential": true,
    "portMappings": [{"containerPort": 3000, "protocol": "tcp"}],
    "environment": [{"name": "NODE_ENV", "value": "production"}],
    "secrets": [{"name": "DATABASE_URL", "valueFrom": "arn:aws:secretsmanager:ap-south-1:123456789012:secret:prod/db"}],
    "healthCheck": {"command": ["CMD-SHELL", "wget -qO- http://localhost:3000/health || exit 1"], "interval": 30, "timeout": 5, "retries": 3},
    "logConfiguration": {"logDriver": "awslogs", "options": {"awslogs-group": "/ecs/api", "awslogs-region": "ap-south-1", "awslogs-stream-prefix": "api"}}
  }]
}
```

Action versions and the exact set of inputs should be re-checked in each action's README; account IDs and ARNs are examples.

---

## 🟠 My Stack Integration
Node.js and FastAPI run as separate ECS services behind one ALB with path rules (`/api/*` to Node, `/ml/*` to FastAPI). React is built to static files on S3 + CloudFront (or an Nginx task). Enable the circuit breaker once:

```bash
# enable circuit breaker with automatic rollback on the service
aws ecs update-service --cluster prod --service api \
  --deployment-configuration "deploymentCircuitBreaker={enable=true,rollback=true},minimumHealthyPercent=100,maximumPercent=200"
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using the `latest` tag in the task definition, so ECS cannot tell anything changed.
✅ Correct: Render a unique SHA tag per deploy to get a new revision.

❌ Mistake 2: Mixing up the execution role and the task role.
✅ Correct: Execution role pulls images/secrets/logs; task role is for your app's AWS calls (S3, SQS).

❌ Mistake 3: Health check grace period too short, tasks killed while starting.
✅ Correct: Set `healthCheckGracePeriodSeconds` on the service.

❌ Mistake 4: Secrets in plain `environment`.
✅ Correct: Use `secrets` with Secrets Manager / Parameter Store.

---

## 🧠 Tricky Interview Question
The deployment hangs for 30 minutes then fails, with tasks starting and stopping repeatedly. What do you check?

Answer: Look at the service Events and stopped-task reason: usually (1) the container exits (bad env/secret, crash), (2) ALB health check path/port mismatch, (3) task cannot pull the image (no NAT/VPC endpoint or missing execution role permission), (4) not enough CPU/memory or subnet IPs. Fix, and enable the circuit breaker so failures roll back quickly instead of looping.

---

## ⚫ Interview Questions + Answers

Q1: Task definition vs service?
A1: Task definition is the blueprint (image, CPU, env); service keeps desired count running and handles deployments.

Q2: Fargate vs EC2 launch type?
A2: Fargate is serverless (no instances to manage, per-task billing); EC2 gives control and can be cheaper at steady high load.

Q3: What do minimumHealthyPercent and maximumPercent do?
A3: They bound capacity during rolling updates: 100/200 means start new tasks first, then stop old, giving zero downtime.

Q4: ECS vs EKS?
A4: ECS is simpler and AWS-specific; EKS is managed Kubernetes with portability and a bigger ecosystem but more complexity.

Q5: How do you do blue/green on ECS?
A5: Use the CodeDeploy deployment controller with two target groups and traffic shifting.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want managed container runtime on AWS with autoscaling.
- Small team, no Kubernetes expertise.

❌ Avoid when:
- You need multi-cloud portability (Kubernetes).
- A single cheap VPS is enough.

---

## 📊 Visual Diagram
```
 git push ─► Actions ─► ECR (api:sha)
                 │
                 ├─ render task-def (new image)
                 └─ register revision :42
                          │
                          ▼
   ┌────────────── ECS service "api" (desired 4) ──────────────┐
   │ old tasks (rev 41) ◄── drain ──┐                           │
   │ new tasks (rev 42) ── healthy on ALB target group ──►      │
   │ circuit breaker: failing? ─► rollback to rev 41            │
   └────────────────────────────────────────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Task definition | Container blueprint | container का नक्शा |
| Service | Keeps N tasks running | N tasks चालू रखने वाला |
| Fargate | Serverless container runtime | बिना server का runtime |
| Execution role | Role to pull image/logs | image pull वाला role |
| Task role | Role for app's AWS calls | app का role |
| Circuit breaker | Auto-rollback on failure | fail पर अपने आप rollback |

---

## ⚡ 3-Line Summary
English: Push SHA image, render a new task definition revision, deploy and wait for stability. Use ALB health checks and the circuit breaker. Keep secrets in Secrets Manager.
Hindi: SHA image push करो, नया task definition revision बनाओ, deploy करके stability का इंतज़ार करो। ALB health checks और circuit breaker लगाओ। Secrets, Secrets Manager में रखो।

---

## ➡️ Next Topic
**344. Deploy to AWS Lambda** - serverless deploys without any long-running container.
