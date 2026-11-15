# 307. Deploy Node.js to ECS
# AWS: ECS on Fargate + ECR + ALB
# Azure: Azure Container Apps (or App Service for Containers) + ACR
# हिंदी में: Node.js कंटेनर को ECR में पुश करके Fargate पर चलाना, बिना सर्वर संभाले

---

## 🔵 Simple Definition
Build a Docker image, push to ECR, and let an ECS service run N Fargate tasks behind an ALB with rolling deploys.
हिंदी: इमेज बनाओ, ECR में डालो, ECS सर्विस उसे चलाती और अपडेट करती है।

## 🔴 Why it Exists
Run containers without managing EC2 hosts, with health-based rolling deployments.

## 🟢 How it Works
```
git push -> GitHub Actions (OIDC role) -> docker build/push ECR :sha
   -> render task-definition.json (new image) -> register revision
   -> ECS service rolling update (min healthy 100%, max 200%) behind ALB /health
Task execution role: pull image + write logs + read secrets for injection
Task role: what the app code itself may call (here: one secret)
```

## 💻 Code / Config Example
Files in this folder: `server.js` + `package.json` (app, health route, SIGTERM drain), `Dockerfile` (multi-stage, non-root), `task-definition.json` (Fargate, awsvpc, secrets from Secrets Manager, awslogs), `deploy.yml` (GitHub Actions; copy to `.github/workflows/`), `task-role-policy.json`.
Prereqs not included: cluster, service, ALB, ECR repo, roles (see 301 for network + ALB).

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Registry | ECR | ACR |
| Runtime | ECS Fargate | Container Apps / App Service |
| Secrets | Secrets Manager via `secrets` | Key Vault references |
| Logs | CloudWatch Logs | Log Analytics |
| Pricing | per vCPU-second + GB-second (approximate - check current docs) | similar consumption model |

## 💰 Cost / HA / Security
- Cost: right-size 256 CPU/512 MB first; Fargate Spot for non-critical; ARM64 (Graviton) cheaper.
- HA: service desired count >= 2 across 2+ AZ subnets; deployment circuit breaker with rollback.
- Security: tasks in private subnets, execution vs task role separation, image scanning in ECR, OIDC instead of access keys.

## ⚠️ Common Mistakes
❌ Using `latest` tag; cannot roll back.
✅ Tag with commit SHA.

❌ Putting secrets in `environment`.
✅ Use `secrets` with Secrets Manager/SSM.

## ⚫ Interview Q&A
Q1 [Easy]: Task definition vs service?
A1: Task definition is the blueprint (image, CPU, env); a service keeps N copies running and handles deploys.

Q2 [Medium]: Execution role vs task role?
A2: Execution role is used by ECS agent (pull, logs, secret injection); task role is used by your code at runtime.

Q3 [Hard]: A deploy keeps failing health checks; how do you stop customer impact?
A3: Rolling update keeps old tasks until new ones are healthy; enable deployment circuit breaker with rollback, set health check grace period, check app logs and SG/port mapping.

## ✅ Quick Checklist
□ Image tagged by SHA
□ Health check + SIGTERM handling
□ Secrets injected, not baked in

## ⚡ 1-Line Summary
ECR image + task definition + ECS service = managed container deploys. | इमेज + टास्क डेफिनिशन + सर्विस = मैनेज्ड कंटेनर डिप्लॉय।

## ➡️ Next: 308. Deploy FastAPI to Lambda
