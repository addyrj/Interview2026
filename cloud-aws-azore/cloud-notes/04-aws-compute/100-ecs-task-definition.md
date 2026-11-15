---

# 100. ECS Task Definition
# AWS: ECS Task Definition
# Azure: Container Apps template (containers section) / ACI container group
# हिंदी में: ECS टास्क डेफिनिशन

---

## 🔵 Simple Definition (2 lines)
A task definition is the JSON blueprint of your containers: image, CPU/memory, ports, env vars, secrets, logging and IAM roles.
हिंदी: Task definition कंटेनर का JSON ब्लूप्रिंट है: image, CPU/memory, पोर्ट, env, secrets और लॉगिंग।

---

## 🔴 Why it Exists (2 lines)
ECS needs a versioned, repeatable description of how to run containers. Each change creates a new revision, enabling rollbacks.

---

## 🟢 How it Works
```
Task definition family "api" -> revisions api:1, api:2 ...
 ├─ cpu/memory (task level; Fargate allows fixed combos)
 ├─ containerDefinitions[]: image, portMappings, environment, secrets, logConfiguration
 ├─ executionRoleArn : ECS agent pulls image from ECR, reads secrets, writes logs
 └─ taskRoleArn      : permissions for YOUR app code (S3, DynamoDB...)
register-task-definition -> service points to a revision
```

---

## 💻 Code / Config Example
```json
{
  "family": "api",
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "512",
  "memory": "1024",
  "runtimePlatform": { "cpuArchitecture": "ARM64", "operatingSystemFamily": "LINUX" },
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/api-task-role",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "123456789012.dkr.ecr.ap-south-1.amazonaws.com/api:abc123",
      "essential": true,
      "portMappings": [{ "containerPort": 3000, "protocol": "tcp" }],
      "environment": [{ "name": "NODE_ENV", "value": "production" }],
      "secrets": [
        { "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:ap-south-1:123456789012:secret:prod/db-AbCdEf" }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "wget -qO- http://localhost:3000/health || exit 1"],
        "interval": 30, "timeout": 5, "retries": 3, "startPeriod": 20
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/api",
          "awslogs-region": "ap-south-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```
```bash
aws ecs register-task-definition --cli-input-json file://taskdef.json
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Blueprint | Task definition (versioned revisions) | Container app template (revisions) |
| Secrets | Secrets Manager / SSM via `secrets` | Key Vault references / secrets |
| Roles | Execution role + task role | Managed identity |
| Pricing | No cost for definition itself (approximate — check current docs) | Same |

---

## ⚠️ Common Mistakes
❌ Mistake: Using the task role for image pull and logs (or vice versa).
✅ Correct: Execution role = ECS agent; task role = your app.

❌ Mistake: Fargate cpu/memory combination invalid.
✅ Correct: Use a supported pair (e.g. 512 CPU with 1024-4096 MB); check docs.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What does a task definition contain?
A1: Containers, image, CPU/memory, ports, env/secrets, logging, roles, network mode.

Q2: [Medium] Execution role vs task role?
A2: Execution role lets ECS pull images/fetch secrets/send logs; task role is what your code assumes at runtime.

Q3: [Hard] How do secrets get in safely?
A3: `secrets` with valueFrom (Secrets Manager/SSM); injected as env at start; execution role needs read permission; rotate then force a new deployment.

---

## ✅ Quick Checklist
□ Image pinned to SHA tag
□ Two roles, least privilege
□ Health check and awslogs configured

---

## ⚡ 1-Line Summary
Task definition = versioned JSON blueprint for containers | Task definition = कंटेनर का वर्ज़न वाला JSON ब्लूप्रिंट।

## ➡️ Next: ECS Networking (next batch)

---
