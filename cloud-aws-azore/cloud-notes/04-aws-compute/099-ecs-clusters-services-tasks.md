---

# 99. ECS Clusters + Services + Tasks
# AWS: ECS cluster, service, task
# Azure: Container Apps environment, container app, revision/replica
# हिंदी में: ECS क्लस्टर, सर्विस और टास्क

---

## 🔵 Simple Definition (2 lines)
Cluster = logical group of capacity. Task = one running copy of a task definition. Service = keeps the desired number of tasks running (with a load balancer).
हिंदी: Cluster = क्षमता का समूह, Task = चलता हुआ कंटेनर समूह, Service = tasks की संख्या बनाए रखता है।

---

## 🔴 Why it Exists (2 lines)
Containers crash and traffic changes. A service restarts failed tasks, spreads them across AZs and scales them; one-off tasks cover batch jobs.

---

## 🟢 How it Works
```
Cluster "prod"
 ├─ Service "api"    desired=3  -> Tasks (long-running) -> ALB target group
 ├─ Service "worker" desired=2  -> Tasks (SQS consumers)
 └─ Standalone task  (RunTask: migration, cron via EventBridge Scheduler)
Task failure -> service scheduler launches replacement
Autoscaling: Application Auto Scaling on CPU / memory / ALB requests per target
```

---

## 💻 Code / Config Example
```bash
# AWS CLI v2 (needs real credentials; not run here)
aws ecs create-cluster --cluster-name prod

aws ecs create-service --cluster prod --service-name api \
  --task-definition api:1 --desired-count 2 --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-aaa,subnet-bbb],securityGroups=[sg-123],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:ap-south-1:123456789012:targetgroup/api/abc,containerName=api,containerPort=3000" \
  --deployment-circuit-breaker "enable=true,rollback=true"

# One-off DB migration task
aws ecs run-task --cluster prod --task-definition migrate:1 --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-aaa],securityGroups=[sg-123]}"

# Scale
aws ecs update-service --cluster prod --service api --desired-count 4
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Group | Cluster | Container Apps environment |
| Long-running | Service | Container app |
| Instance | Task | Replica |
| One-off job | RunTask | Container Apps Job |
| Pricing | Pay for task compute (approximate — check current docs) | Pay for replica compute (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Running a web app as a standalone task.
✅ Correct: Use a service so it self-heals and registers with the ALB.

❌ Mistake: Health check grace period too short, so tasks are killed while booting.
✅ Correct: Set `healthCheckGracePeriodSeconds` to cover startup time.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Task vs service?
A1: Task is a running instance; service maintains a desired count of tasks.

Q2: [Medium] Why `awsvpc` networking?
A2: Each task gets its own ENI and security group, required for Fargate.

Q3: [Hard] Tasks keep restarting. Debug?
A3: Check stopped task reason in console/`describe-tasks`, CloudWatch logs, image pull permissions (execution role/NAT or VPC endpoints), health check path/port, memory OOM, and security group to the DB.

---

## ✅ Quick Checklist
□ Service across at least 2 AZs
□ Circuit breaker + autoscaling
□ Private subnets with NAT/VPC endpoints for ECR

---

## ⚡ 1-Line Summary
Cluster holds, service maintains, task runs | Cluster रखता है, Service बनाए रखती है, Task चलता है।

## ➡️ Next: ECS Task Definition

---
