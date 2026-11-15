# 164. Deploying FastAPI to ECS
# AWS: ECR + ECS Fargate behind ALB
# Azure: ACR + Azure Container Apps
# हिंदी में: FastAPI app को ECS पर deploy करना

---

## 🔵 Simple Definition
Containerise FastAPI with uvicorn, push to ECR, and run it as a Fargate service behind an Application Load Balancer.
हिंदी: FastAPI को Docker में पैक करके ECR में रखो और ECS Fargate पर ALB के पीछे चलाओ।

---

## 🔴 Why it Exists
Python services need reproducible runtimes and scaling without managing servers.
Fargate removes EC2 patching; ALB gives health checks and TLS.

---

## 🟢 How it Works
```
Client -> ALB (443) -> target group (port 8000, /health)
                         -> Fargate tasks (uvicorn x N)
CI: build -> ECR -> new task def revision -> service update
```

---

## 💻 Code / Config Example
```dockerfile
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
EXPOSE 8000
# --proxy-headers because ALB terminates TLS
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
```
```json
{
  "family": "fastapi-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/fastapi-task-role",
  "containerDefinitions": [{
    "name": "api",
    "image": "123456789012.dkr.ecr.ap-south-1.amazonaws.com/fastapi-api:latest",
    "essential": true,
    "portMappings": [{"containerPort": 8000, "protocol": "tcp"}],
    "environment": [{"name": "APP_ENV", "value": "prod"}],
    "secrets": [{"name": "DATABASE_URL", "valueFrom": "arn:aws:secretsmanager:ap-south-1:123456789012:secret:prod/db-AbCdEf"}],
    "healthCheck": {
      "command": ["CMD-SHELL", "python -c \"import urllib.request;urllib.request.urlopen('http://localhost:8000/health')\""],
      "interval": 30, "timeout": 5, "retries": 3, "startPeriod": 20
    },
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {"awslogs-group": "/ecs/fastapi-api", "awslogs-region": "ap-south-1", "awslogs-stream-prefix": "api"}
    }
  }]
}
```
The workflow is the same as 163: only `ECR_REPOSITORY`, `ECS_SERVICE` and container name change.

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Run containers | ECS Fargate | Container Apps |
| Load balancer | ALB | Built-in ingress / Application Gateway |
| Secrets | Secrets Manager via `secrets` | Key Vault references |
| Pricing | Pay per vCPU/GB-second (approximate — check current docs) | Pay per vCPU/GB-second consumption |

---

## ⚠️ Common Mistakes
❌ Mistake: Binding uvicorn to `127.0.0.1`.
✅ Correct: Bind `0.0.0.0` so the ALB can reach the task.

❌ Mistake: Running DB migrations at container start on every replica.
✅ Correct: Run Alembic migrations as a one-off ECS task (`run-task`) before the service update.

---

## ⚫ Interview Q&A
Q1: [Easy] Why `awsvpc` network mode?
A1: Each task gets its own ENI and security group; required for Fargate.

Q2: [Medium] How do you scale FastAPI tasks?
A2: Application Auto Scaling target tracking on CPU or ALBRequestCountPerTarget.

Q3: [Hard] Gunicorn workers vs more tasks?
A3: Prefer one uvicorn process per small task and scale tasks horizontally; use `gunicorn -k uvicorn.workers.UvicornWorker` only if you need multiple workers per larger task.

---

## ✅ Quick Checklist
□ `/health` endpoint and ALB health check
□ Secrets via `secrets`, logs to CloudWatch
□ Migrations as separate task

---

## ⚡ 1-Line Summary
FastAPI in Docker on Fargate behind ALB, deployed by CI | FastAPI को Docker में Fargate पर ALB के पीछे CI से deploy करो।

## ➡️ Next: 165. Deploying React to S3+CloudFront
