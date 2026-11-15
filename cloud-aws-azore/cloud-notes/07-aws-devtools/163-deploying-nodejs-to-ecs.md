# 163. Deploying Node.js to ECS
# AWS: ECR + ECS (Fargate) with GitHub Actions
# Azure: ACR + Azure Container Apps / App Service for Containers
# हिंदी में: Node.js (NestJS) app को ECS पर deploy करना

---

## 🔵 Simple Definition
Build a Docker image, push to ECR, register a new ECS task definition revision and update the service for a rolling deploy.
हिंदी: image बनाओ, ECR में push करो, task definition अपडेट करके ECS service को नया version दो।

---

## 🔴 Why it Exists
Manual `docker pull` on a VPS has no rollback or health checks.
ECS replaces tasks gradually and only after the load balancer health check passes.

---

## 🟢 How it Works
```
push main -> test -> docker build -> ECR (tag = git sha)
 -> render task definition with new image
 -> ecs update service -> new tasks start -> ALB health OK -> old tasks drained
 (circuit breaker rolls back on failure)
```

---

## 💻 Code / Config Example
```yaml
# .github/workflows/deploy-node.yml
name: deploy-node
on:
  push:
    branches: [main]
permissions:
  id-token: write
  contents: read
env:
  AWS_REGION: ap-south-1
  ECR_REPOSITORY: nest-api
  ECS_SERVICE: nest-api-svc
  ECS_CLUSTER: prod
  TASK_DEF_FILE: .aws/task-definition.json
  CONTAINER_NAME: api
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-deploy
          aws-region: ${{ env.AWS_REGION }}
      - id: ecr
        uses: aws-actions/amazon-ecr-login@v2
      - id: build
        run: |
          IMAGE=${{ steps.ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ github.sha }}
          docker build -t "$IMAGE" .
          docker push "$IMAGE"
          echo "image=$IMAGE" >> "$GITHUB_OUTPUT"
      - id: taskdef
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: ${{ env.TASK_DEF_FILE }}
          container-name: ${{ env.CONTAINER_NAME }}
          image: ${{ steps.build.outputs.image }}
      - uses: aws-actions/amazon-ecs-deploy-task-definition@v2
        with:
          task-definition: ${{ steps.taskdef.outputs.task-definition }}
          service: ${{ env.ECS_SERVICE }}
          cluster: ${{ env.ECS_CLUSTER }}
          wait-for-service-stability: true
```
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
EXPOSE 3000
USER node
CMD ["node", "dist/main.js"]
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Registry | ECR | ACR |
| Runtime | ECS Fargate | Container Apps / App Service |
| Deploy action | amazon-ecs-deploy-task-definition | azure/container-apps-deploy-action or webapps-deploy |
| Pricing | Fargate per vCPU-second and GB-second (approximate — check current docs) | Container Apps consumption plan, similar model |

---

## ⚠️ Common Mistakes
❌ Mistake: Tagging images `latest` only.
✅ Correct: Tag with git SHA so rollback and audit are exact.

❌ Mistake: Not setting the health check path/grace period, so tasks loop restarting.
✅ Correct: Expose `/health`, set ALB target health check and `healthCheckGracePeriodSeconds`.

---

## ⚫ Interview Q&A
Q1: [Easy] What is a task definition?
A1: A JSON blueprint: image, CPU/memory, ports, env, logging, roles.

Q2: [Medium] Execution role vs task role?
A2: Execution role lets ECS pull from ECR/write logs/read secrets at start; task role is what your app code uses for AWS APIs.

Q3: [Hard] How do you get zero-downtime and auto rollback?
A3: Rolling update with min healthy 100%, max 200%, deployment circuit breaker with rollback enabled, ALB health checks; or CodeDeploy blue/green.

---

## ✅ Quick Checklist
□ Image tagged by SHA
□ Secrets from Secrets Manager, not in image
□ Circuit breaker enabled, `wait-for-service-stability` on

---

## ⚡ 1-Line Summary
Build, push to ECR, render task definition, update ECS service | image build करो, ECR में push करो और ECS service अपडेट करो।

## ➡️ Next: 164. Deploying FastAPI to ECS
