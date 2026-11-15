---

# 98. ECS — Elastic Container Service
# AWS: Amazon ECS (Fargate / EC2)
# Azure: Azure Container Apps (closest), AKS, Azure Container Instances
# हिंदी में: ECS (एलास्टिक कंटेनर सर्विस)

---

## 🔵 Simple Definition (2 lines)
ECS is AWS's managed container orchestrator. You describe containers; ECS places, runs, restarts and scales them on Fargate (serverless) or EC2.
हिंदी: ECS AWS का कंटेनर ऑर्केस्ट्रेटर है जो आपके Docker कंटेनर चलाता, रीस्टार्ट और स्केल करता है।

---

## 🔴 Why it Exists (2 lines)
Running Docker by hand on VPSes means manual deploys, no self-healing and no load balancing. ECS automates it without Kubernetes complexity.

---

## 🟢 How it Works
```
Docker image -> ECR
Task Definition (blueprint) -> Service (keeps N tasks running) -> Cluster
                                   |
   ALB -> Target group -> Tasks (Fargate: no servers | EC2: your instances)
Logs -> CloudWatch (awslogs) ; IAM: task execution role + task role
Deploy: rolling update by default; blue/green via CodeDeploy
```

---

## 💻 Code / Config Example
```yaml
# GitHub Actions: build Docker image, push to ECR, update ECS service (OIDC)
name: deploy-ecs
on: { push: { branches: [main] } }
permissions: { id-token: write, contents: read }
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-ecs-deploy
          aws-region: ap-south-1
      - id: ecr
        uses: aws-actions/amazon-ecr-login@v2
      - run: |
          IMG=${{ steps.ecr.outputs.registry }}/api:${{ github.sha }}
          docker build -t $IMG . && docker push $IMG
          echo "IMG=$IMG" >> $GITHUB_ENV
      - run: |
          aws ecs update-service --cluster prod --service api --force-new-deployment
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | ECS (Fargate/EC2) | Container Apps / AKS / ACI |
| Registry | ECR | ACR |
| Orchestration | AWS-native, simple | Container Apps = Kubernetes-based, abstracted |
| Pricing | Fargate vCPU+GB per second; ECS control plane free (approximate — check current docs) | Per vCPU/GB-second (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Giving tasks admin permissions via one role.
✅ Correct: Separate execution role (pull image, logs) from task role (app AWS access), least privilege.

❌ Mistake: Using `latest` tag.
✅ Correct: Tag by commit SHA for traceable rollbacks.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Fargate vs EC2 launch type?
A1: Fargate = serverless, no instances to manage; EC2 = you manage instances, cheaper at sustained scale and more control (GPUs, daemon).

Q2: [Medium] ECS vs EKS?
A2: ECS is simpler and AWS-specific; EKS is managed Kubernetes, portable but more operational overhead.

Q3: [Hard] Zero-downtime deploys?
A3: Rolling update with minimumHealthyPercent/maximumPercent plus ALB health checks and deployment circuit breaker; or CodeDeploy blue/green.

---

## ✅ Quick Checklist
□ Image in ECR, tagged by SHA
□ Tasks in private subnets behind ALB
□ Logs, health checks and autoscaling configured

---

## ⚡ 1-Line Summary
ECS = managed Docker orchestration on AWS | ECS = AWS पर मैनेज्ड Docker ऑर्केस्ट्रेशन।

## ➡️ Next: ECS Clusters + Services + Tasks

---
