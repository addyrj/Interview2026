# 383. ECS Service
# हिंदी में: ECS Service (tasks को चालू और balanced रखने वाला)

---

## 🔵 Simple Definition (English)
An ECS service keeps a desired number of copies of a task definition running. It replaces failed tasks, registers tasks with a load balancer, spreads them across availability zones, performs rolling deployments and can autoscale.

## 🔵 सरल परिभाषा (Hindi)
ECS service किसी task definition की desired संख्या में copies चालू रखती है। Failed tasks को replace करती है, tasks को load balancer में register करती है, उन्हें availability zones में फैलाती है, rolling deployment करती है और autoscale भी कर सकती है।

---

## 🔴 Problem it Solves
- A bare task that crashes stays dead. Someone must restart it.
- Without a service nothing connects tasks to the ALB or removes dead ones from rotation.
- Updating by hand means downtime or scripting start/stop order.

## 🔴 यह क्यों बना? (Hindi)
- अकेला task crash हो जाए तो मरा रहता है। किसी को restart करना पड़ता है।
- Service के बिना tasks को ALB से जोड़ने या dead tasks हटाने वाला कोई नहीं।
- Hand से update करने पर downtime या start/stop order के scripts चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You set desiredCount=3, task definition api:42, subnets, ALB target group
Step 2 → Scheduler launches tasks, spreading across AZs
Step 3 → Tasks register in the ALB target group; ALB health check must pass
Step 4 → Task dies -> scheduler starts another to reach desiredCount
Step 5 → Update to api:43 -> new tasks start, old ones drain and stop (rolling)
Step 6 → Circuit breaker: if new tasks keep failing -> rollback to api:42
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप desiredCount=3, task definition api:42, subnets, ALB target group सेट करते हो
Step 2 → Scheduler tasks launch करता है, AZs में फैलाकर
Step 3 → Tasks ALB target group में register; ALB health check pass होना ज़रूरी
Step 4 → Task मरा -> scheduler desiredCount पूरा करने के लिए नया शुरू करता है
Step 5 → api:43 पर update -> नए tasks शुरू, पुराने drain होकर बंद (rolling)
Step 6 → Circuit breaker: नए tasks बार-बार fail हों -> api:42 पर rollback
```

---

## 🟡 Real World Example
A food-ordering backend has three services in one cluster: `api` (3-20 tasks, behind ALB), `worker` (queue consumer, scales on SQS depth) and `scheduler` (exactly 1 task). Each has its own task definition, scaling policy and deploy cadence. The `api` service gets a new release 10 times a day with zero downtime because of the rolling strategy with 100% minimum healthy.

## 🟡 Real Example Hindi mein
Food-ordering backend के एक cluster में तीन services हैं: `api` (ALB के पीछे 3-20 tasks), `worker` (queue consumer, SQS depth पर scale) और `scheduler` (ठीक 1 task)। हर का अपना task definition, scaling policy और deploy cadence है। `api` में दिन में 10 बार नया release zero downtime से जाता है, क्योंकि rolling strategy में minimum healthy 100% है।

---

## 💻 Code / Config Example — Basic

```bash
# service-basic.sh  - create and later update a service via CLI
set -euo pipefail                                                  # fail fast
aws ecs create-service \
  --cluster prod --service-name api \
  --task-definition api:42 --desired-count 2 --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-aaa,subnet-bbb],securityGroups=[sg-123],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:ap-south-1:123456789012:targetgroup/api/abc123,containerName=api,containerPort=3000" \
  --health-check-grace-period-seconds 60                           # give app 60s before ALB health matters
aws ecs update-service --cluster prod --service api --desired-count 4   # scale manually
aws ecs describe-services --cluster prod --services api \
  --query 'services[0].{desired:desiredCount,running:runningCount,events:events[:3].message}'   # check state and last events
```

## 💻 Code / Config Example — Advanced
Autoscaling on CPU and ALB requests, using Application Auto Scaling in CloudFormation. Service resource is from topic 381; here we add scaling.

```yaml
# ecs-autoscaling.yml  - CloudFormation fragment as a full template
AWSTemplateFormatVersion: "2010-09-09"          # template version
Parameters:
  ClusterName: {Type: String, Default: prod}    # cluster name
  ServiceName: {Type: String, Default: api}     # service name
  AlbResourceLabel: {Type: String}              # "app/my-alb/123/targetgroup/api/456" for request metric
Resources:
  ScalableTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget   # registers the service as scalable
    Properties:
      ServiceNamespace: ecs                      # namespace for ECS
      ScalableDimension: ecs:service:DesiredCount   # what we scale
      ResourceId: !Sub service/${ClusterName}/${ServiceName}   # which service
      MinCapacity: 3                             # never below 3 (one per AZ)
      MaxCapacity: 20                            # cost safety ceiling
  CpuPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: cpu-60                         # name
      PolicyType: TargetTrackingScaling          # keep a metric near a target
      ScalingTargetId: !Ref ScalableTarget       # attach to the target above
      TargetTrackingScalingPolicyConfiguration:
        TargetValue: 60                          # aim for 60% average CPU
        PredefinedMetricSpecification:
          PredefinedMetricType: ECSServiceAverageCPUUtilization   # built-in metric
        ScaleOutCooldown: 60                     # wait 60s between scale-outs
        ScaleInCooldown: 300                     # scale in slowly to avoid flapping
  RequestPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: alb-requests-500
      PolicyType: TargetTrackingScaling
      ScalingTargetId: !Ref ScalableTarget
      TargetTrackingScalingPolicyConfiguration:
        TargetValue: 500                         # about 500 requests per task per minute
        PredefinedMetricSpecification:
          PredefinedMetricType: ALBRequestCountPerTarget   # request-based metric
          ResourceLabel: !Ref AlbResourceLabel   # identifies ALB and target group
```

---

## 🟠 My Stack Integration
Run Node API and FastAPI as separate services behind one ALB with path rules (`/api/*` -> node, `/ml/*` -> fastapi). Deploy the React build to S3 and CloudFront. A worker service (no load balancer) handles background jobs from the same image with a different command.

```yaml
# docker-compose.yml analogy: one image, two roles -> two ECS services
# service "api"    : image X, command default,          ALB attached,  desired 3
# service "worker" : image X, command node dist/worker, no ALB,         desired 1
#   (override command in the worker's task definition containerDefinitions[].command)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `desiredCount` hard-coded in IaC while autoscaling also changes it.
✅ Correct: Omit DesiredCount after first create, or ignore drift, so deploys do not reset the scale.

❌ Mistake 2: `MinimumHealthyPercent: 50` on a 2-task service.
✅ Correct: Use 100 / 200 for zero downtime when you have headroom.

❌ Mistake 3: Wrong health check path or port on the target group.
✅ Correct: Match `/health` and the container port; otherwise tasks are killed in a loop.

❌ Mistake 4: Subnets in one AZ.
✅ Correct: At least two AZs.

---

## 🧠 Tricky Interview Question
You deploy a new task definition. The service shows running count 3 but users get 502 errors for a minute. Old tasks were stopped quickly. What went wrong?

Answer: Likely the deregistration delay and health check settings. New tasks registered but were not yet healthy while old ones were stopped (minimum healthy too low), or the app lacks SIGTERM handling so in-flight requests were cut. Fix: min healthy 100%, a correct grace period and health check, `deregistration_delay` matching request time, and graceful shutdown in the app.

---

## ⚫ Interview Questions + Answers

Q1: Service types?
A1: REPLICA (N copies, default) and DAEMON (one per EC2 container instance, EC2 only).

Q2: Deployment controllers?
A2: ECS (rolling), CODE_DEPLOY (blue/green) and EXTERNAL. ECS now also supports built-in blue/green in newer API versions (check current docs).

Q3: What does `forceNewDeployment` do?
A3: Starts a new deployment using the same task definition, for pulling a re-pushed tag or restarting tasks.

Q4: How are tasks spread?
A4: Placement strategies (EC2) like spread by AZ; Fargate spreads across the given subnets automatically.

Q5: What is service discovery?
A5: Cloud Map or ECS Service Connect gives tasks DNS names so services talk without a load balancer (internal microservices).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Long-running APIs, workers, anything that must stay alive

❌ Avoid when:
- One-off or scheduled batch jobs (use `run-task` or EventBridge scheduled tasks)

---

## 📊 Visual Diagram
```
           desiredCount = 3
 Service "api" ------------------------+
    |            |            |        |
 task(AZ-a)  task(AZ-b)  task(AZ-c)    | replaces any that die
    ^            ^            ^        |
    +------ ALB target group (health /health)
                   ^
                 Users
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| desiredCount | Target number of tasks | कितने tasks चाहिए |
| Target group | ALB's list of healthy tasks | ALB की healthy tasks सूची |
| Grace period | Time health checks are ignored | Health check अनदेखा रहने का समय |
| Circuit breaker | Auto rollback of bad deploys | खराब deploy का auto rollback |
| Target tracking | Autoscale to hold a metric | Metric को स्थिर रखने वाला scaling |

---

## ⚡ 3-Line Summary
English: A service keeps N tasks alive, wired to a load balancer, across AZs.
It performs rolling deploys with min/max percent and a circuit breaker.
Autoscaling changes desiredCount automatically, so do not fight it in IaC.

Hindi: Service N tasks को load balancer से जोड़कर AZs में चालू रखती है।
यह min/max percent और circuit breaker के साथ rolling deploy करती है।
Autoscaling desiredCount अपने आप बदलता है, इसलिए IaC में उससे मत लड़ो।

---

## ➡️ Next Topic
384. ECS Cluster: the capacity layer services run on.
