# 381. AWS ECS — Complete Guide
# हिंदी में: AWS ECS (Elastic Container Service) की पूरी गाइड

---

## 🔵 Simple Definition (English)
Amazon ECS is AWS's managed container orchestrator. You describe your containers in a task definition, tell ECS how many copies to run (a service), and ECS places them on a cluster (Fargate serverless or your EC2 machines), restarts failures, connects to load balancers and rolls out updates.

## 🔵 सरल परिभाषा (Hindi)
Amazon ECS, AWS का managed container orchestrator है। आप task definition में containers describe करते हो, ECS को बताते हो कितनी copies चलानी हैं (service), और ECS उन्हें cluster (Fargate serverless या आपकी EC2 machines) पर चलाता है, failures restart करता है, load balancer से जोड़ता है और updates roll out करता है।

---

## 🔴 Problem it Solves
- `docker compose` on one VPS is a single point of failure: server dies, app dies.
- Manual scaling, health checks, rolling updates and load-balancer registration are scripts you must maintain.
- Kubernetes solves this too but is heavy; teams already on AWS want something simpler.

## 🔴 यह क्यों बना? (Hindi)
- एक VPS पर `docker compose` single point of failure है: server मरा तो app मरा।
- Manual scaling, health checks, rolling updates और load-balancer registration के scripts आपको maintain करने पड़ते हैं।
- Kubernetes भी यही करता है पर भारी है; AWS पर पहले से बैठी teams को सरल चीज़ चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Push image to ECR
Step 2 → Register a TASK DEFINITION (blueprint: image, cpu, memory, ports, env, logs, roles)
Step 3 → Create a CLUSTER (logical group; Fargate needs no servers)
Step 4 → Create a SERVICE (desired count = 3, load balancer, subnets, security groups)
Step 5 → Scheduler starts 3 TASKS (running copies) across availability zones
Step 6 → ALB health checks; unhealthy task is replaced automatically
Step 7 → New release = new task definition revision -> service rolls out gradually
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Image को ECR में push
Step 2 → TASK DEFINITION register (blueprint: image, cpu, memory, ports, env, logs, roles)
Step 3 → CLUSTER बनाओ (logical group; Fargate में servers नहीं चाहिए)
Step 4 → SERVICE बनाओ (desired count = 3, load balancer, subnets, security groups)
Step 5 → Scheduler 3 TASKS (चलती copies) availability zones में फैलाकर चलाता है
Step 6 → ALB health check; unhealthy task अपने आप replace
Step 7 → नया release = नया task definition revision -> service धीरे-धीरे roll out
```

---

## 🟡 Real World Example
A Swiggy-like ordering API runs as an ECS service on Fargate: 6 tasks across 3 AZs behind an Application Load Balancer. At dinner time, target tracking autoscaling (CPU 60%) goes to 20 tasks, then back down at night. One AZ has a problem; the ALB stops sending traffic to its tasks and ECS launches replacements in the healthy AZs. Nobody patches a server.

## 🟡 Real Example Hindi mein
Swiggy जैसी ordering API Fargate पर ECS service है: Application Load Balancer के पीछे 3 AZs में 6 tasks। Dinner time पर target tracking autoscaling (CPU 60%) से 20 tasks, रात में वापस कम। एक AZ में दिक्कत आए तो ALB उसके tasks को traffic देना बंद करता है और ECS healthy AZs में replacements launch करता है। किसी को server patch नहीं करना पड़ता।

---

## 💻 Code / Config Example — Basic
Quickest path with the CLI: an existing task definition run as a one-off task (no load balancer).

```bash
# ecs-basic.sh  - minimal Fargate setup (example IDs, replace with yours)
set -euo pipefail                                              # stop on first error
aws ecs create-cluster --cluster-name demo                     # logical group for tasks
aws ecs register-task-definition --cli-input-json file://taskdef.json   # blueprint (see topic 382)
aws ecs create-service --cluster demo --service-name api \
  --task-definition api --desired-count 2 --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-aaa,subnet-bbb],securityGroups=[sg-123],assignPublicIp=ENABLED}"
aws ecs wait services-stable --cluster demo --services api     # block until 2 tasks are running
aws ecs list-tasks --cluster demo --service-name api           # list running task ARNs
```

## 💻 Code / Config Example — Advanced
CloudFormation: cluster + service with ALB target group, circuit breaker and autoscaling-ready settings. (Task definition from topic 382 is referenced by parameter.)

```yaml
# ecs-service.yml  - CloudFormation (parameters supplied at deploy time)
AWSTemplateFormatVersion: "2010-09-09"           # template version
Parameters:
  TaskDefArn: {Type: String}                      # task definition revision ARN
  Subnets: {Type: "List<AWS::EC2::Subnet::Id>"}   # private subnets for tasks
  TaskSg: {Type: AWS::EC2::SecurityGroup::Id}     # SG allowing ALB -> task port
  TargetGroupArn: {Type: String}                  # ALB target group (type ip)
Resources:
  Cluster:
    Type: AWS::ECS::Cluster                       # the cluster
    Properties:
      ClusterName: prod                           # name used in CLI commands
      ClusterSettings:
        - Name: containerInsights                 # CloudWatch metrics per task
          Value: enabled
  Service:
    Type: AWS::ECS::Service                       # keeps N tasks alive
    Properties:
      Cluster: !Ref Cluster                       # place in this cluster
      ServiceName: api                            # service name
      LaunchType: FARGATE                         # serverless compute
      TaskDefinition: !Ref TaskDefArn             # which blueprint to run
      DesiredCount: 3                             # number of copies
      HealthCheckGracePeriodSeconds: 60           # ignore ALB health during boot
      DeploymentConfiguration:
        MinimumHealthyPercent: 100                # never drop below desired during update
        MaximumPercent: 200                       # may run double while rolling
        DeploymentCircuitBreaker:
          Enable: true                            # detect failing deploy
          Rollback: true                          # and roll back automatically
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets: !Ref Subnets                   # private subnets
          SecurityGroups: [!Ref TaskSg]           # firewall for tasks
          AssignPublicIp: DISABLED                # no public IP; use NAT/VPC endpoints
      LoadBalancers:
        - ContainerName: api                      # must match name in task definition
          ContainerPort: 3000                     # app port
          TargetGroupArn: !Ref TargetGroupArn     # ALB registers tasks here
```

---

## 🟠 My Stack Integration
- Node.js and FastAPI: one service each, each with an ALB target group or path rule (`/api/*`, `/ml/*`).
- React: static on S3 + CloudFront, not ECS.
- Nginx: the ALB replaces Nginx for routing/TLS on ECS; keep Nginx only if you need custom rules, as a sidecar container.
- VPS migration path: same image already works; only add a task definition.

```yaml
# docker-compose.yml (local/VPS) -> ECS mapping cheat sheet
# services.api.image        -> taskDefinition.containerDefinitions[].image
# services.api.ports        -> containerDefinitions[].portMappings + ALB target group
# services.api.environment  -> containerDefinitions[].environment / secrets
# services.api.deploy.replicas -> service.desiredCount
# services.api.healthcheck  -> containerDefinitions[].healthCheck + ALB health check
# services.api.restart      -> service scheduler (always replaces failed tasks)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Tasks in public subnets with public IPs exposed directly.
✅ Correct: Private subnets, ALB in public subnets, security group allows only the ALB.

❌ Mistake 2: Secrets as plain `environment` values.
✅ Correct: Use `secrets` with Secrets Manager / SSM ARNs.

❌ Mistake 3: No health check grace period, so slow-booting apps get killed in a loop.
✅ Correct: Set `healthCheckGracePeriodSeconds` above start-up time.

❌ Mistake 4: One giant task with API, worker and cron.
✅ Correct: One process type per service so each scales independently.

---

## 🧠 Tricky Interview Question
Your ECS service shows desired 3, running 0, and events say "service was unable to place a task because no container instance met all requirements". Fargate is not used. What is wrong?

Answer: The service uses the EC2 launch type and the cluster has no registered instances with enough free CPU/memory (or the instance AZ/attribute constraints fail). Add capacity (Auto Scaling group via a capacity provider), reduce task size, or switch to Fargate.

---

## ⚫ Interview Questions + Answers

Q1: Task vs service vs task definition?
A1: Task definition = blueprint (versioned). Task = one running instance of it. Service = keeps N tasks running and handles deployments and load balancing.

Q2: ECS vs EKS?
A2: ECS is AWS-native, simpler, no control-plane fee. EKS is managed Kubernetes: portable, bigger ecosystem, more complexity and a control-plane cost.

Q3: What are the two IAM roles?
A3: Execution role (ECS agent: pull from ECR, send logs, read secrets). Task role (your code's AWS permissions, e.g. S3).

Q4: What is awsvpc network mode?
A4: Each task gets its own ENI and private IP, with its own security group. Required for Fargate.

Q5: How does autoscaling work?
A5: Application Auto Scaling changes the service's desired count based on target tracking (CPU, memory, ALB requests per target) or schedules.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You are on AWS and want managed containers without Kubernetes complexity
- You need autoscaling, rolling deploys and ALB integration

❌ Avoid when:
- A tiny hobby app (a single VPS is cheaper)
- You need Kubernetes APIs or multi-cloud portability

---

## 📊 Visual Diagram
```
        ECR image
           |
   Task Definition (rev 12)
           |
  +----- ECS Cluster "prod" ------------------------+
  |  Service "api" (desired=3)                      |
  |   task A (AZ-a)  task B (AZ-b)  task C (AZ-c)   |
  +--------^-----------^-------------^--------------+
           |           |             |
        Application Load Balancer (health checks)
                       |
                    Users
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cluster | Group of capacity for tasks | Tasks की capacity का group |
| Task definition | Container blueprint | Container का blueprint |
| Task | Running copy | चल रही copy |
| Service | Keeps N tasks alive | N tasks चालू रखने वाला |
| Fargate | Serverless compute for containers | Serverless container compute |
| Capacity provider | Link from cluster to compute | Cluster और compute का link |

---

## ⚡ 3-Line Summary
English: ECS runs your containers from task definitions, kept alive by services on a cluster.
Fargate removes server management; ALB and autoscaling give availability and scale.
Execution role pulls and logs, task role is for your app code.

Hindi: ECS आपके containers को task definitions से चलाता है, services उन्हें cluster पर चालू रखती हैं।
Fargate server management हटा देता है; ALB और autoscaling availability व scale देते हैं।
Execution role pull और log करता है, task role आपके app code के लिए है।

---

## ➡️ Next Topic
382. ECS Task Definition: the blueprint in detail.
