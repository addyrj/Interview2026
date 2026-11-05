# 385. Fargate vs EC2 Launch Type
# हिंदी में: Fargate बनाम EC2 Launch Type

---

## 🔵 Simple Definition (English)
Launch type decides where ECS runs your containers. Fargate is serverless: you give CPU and memory and AWS provides the compute, billed per task per second. EC2 launch type runs tasks on EC2 instances that you own, patch and scale.

## 🔵 सरल परिभाषा (Hindi)
Launch type तय करता है कि ECS आपके containers कहाँ चलाए। Fargate serverless है: आप CPU और memory बताते हो और AWS compute देता है, billing प्रति task प्रति सेकंड। EC2 launch type में tasks आपके अपने EC2 instances पर चलते हैं जिन्हें आप patch और scale करते हो।

---

## 🔴 Problem it Solves
- Running your own instances means OS patches, AMI updates, agent upgrades, disk full alerts and bin-packing.
- On the other hand, sometimes you need GPUs, special kernels, or the lowest price at steady high load, where managed Fargate is not the best fit.
- Teams need a clear rule for which to pick.

## 🔴 यह क्यों बना? (Hindi)
- अपने instances चलाने का मतलब OS patches, AMI updates, agent upgrades, disk full alerts और bin-packing।
- दूसरी तरफ कभी GPU, special kernel, या steady high load पर सबसे कम कीमत चाहिए, जहाँ managed Fargate सबसे सही नहीं।
- Teams को साफ नियम चाहिए कि कब कौन-सा चुनें।

---

## 🟢 How it Works — Step by Step

```
FARGATE
Step 1 → Task definition says cpu=512, memory=1024
Step 2 → ECS launches an isolated micro-VM sized exactly for the task
Step 3 → You pay for vCPU + GB per second while the task runs

EC2
Step 1 → You run an Auto Scaling group of instances with the ECS agent
Step 2 → ECS places tasks onto instances with free CPU/memory
Step 3 → You pay for the instances 24x7, used or idle
```

## 🟢 कैसे काम करता है? (Hindi)
```
FARGATE
Step 1 → Task definition में cpu=512, memory=1024
Step 2 → ECS task के size का एक isolated micro-VM launch करता है
Step 3 → Task चलने के दौरान vCPU + GB का पैसा प्रति सेकंड

EC2
Step 1 → आप ECS agent वाले instances का Auto Scaling group चलाते हो
Step 2 → ECS tasks को खाली CPU/memory वाले instances पर place करता है
Step 3 → Instances का पैसा 24x7, इस्तेमाल हो या नहीं
```

---

## 🟡 Real World Example
A startup with 6 services and 2 engineers picks Fargate: no patching, scale in a minute, per-task isolation. At 3 years old, one ML inference service needs GPU instances and a batch pipeline runs at constant 90% load on 40 vCPUs; those two move to EC2 with Reserved Instances / Savings Plans, saving about 30-40%, while the web APIs stay on Fargate.

## 🟡 Real Example Hindi mein
6 services और 2 engineers वाला startup Fargate चुनता है: patching नहीं, एक मिनट में scale, हर task isolated। 3 साल बाद एक ML inference service को GPU instances चाहिए और एक batch pipeline 40 vCPUs पर लगातार 90% load पर चलती है; ये दोनों Reserved Instances / Savings Plans के साथ EC2 पर चले गए (लगभग 30-40% बचत), जबकि web APIs Fargate पर ही रहीं।

---

## 💻 Code / Config Example — Basic

```bash
# launch-types-basic.sh  - same service, two launch types
set -euo pipefail                                              # stop on error

# Fargate: needs awsvpc network config, no instances needed
aws ecs create-service --cluster prod --service-name api-fg \
  --task-definition api --desired-count 2 --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-aaa],securityGroups=[sg-123]}"

# EC2: tasks need a registered instance with enough capacity
aws ecs create-service --cluster prod --service-name api-ec2 \
  --task-definition api-ec2 --desired-count 2 --launch-type EC2   # requires "requiresCompatibilities": ["EC2"] in the task def
```

## 💻 Code / Config Example — Advanced
Mix both with capacity provider strategy: stable base on Fargate, the rest on EC2 (cheaper at scale), batch on Spot.

```yaml
# service-mixed.yml  - CloudFormation service using strategy instead of LaunchType
AWSTemplateFormatVersion: "2010-09-09"             # template version
Parameters:
  TaskDefArn: {Type: String}                        # task definition revision
  Subnets: {Type: "List<AWS::EC2::Subnet::Id>"}     # private subnets
  Sg: {Type: AWS::EC2::SecurityGroup::Id}           # task security group
  Ec2ProviderName: {Type: String}                   # capacity provider created in topic 384
Resources:
  Service:
    Type: AWS::ECS::Service
    Properties:
      Cluster: prod                                  # existing cluster
      ServiceName: api-mixed
      TaskDefinition: !Ref TaskDefArn                # NOTE: do not set LaunchType when using a strategy
      DesiredCount: 6
      CapacityProviderStrategy:
        - {CapacityProvider: FARGATE, Base: 2, Weight: 1}       # 2 tasks always on Fargate (no instance risk)
        - {CapacityProvider: !Ref Ec2ProviderName, Weight: 3}   # remaining on EC2, 3 parts EC2 to 1 part Fargate
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets: !Ref Subnets
          SecurityGroups: [!Ref Sg]
          AssignPublicIp: DISABLED
```

Comparison cheat sheet:

```yaml
# fargate-vs-ec2.yml  - quick decision table as data
fargate:
  server_management: none (AWS patches the host)
  billing: per task vCPU and GB per second
  startup: 30-60 s typical (image pull each time)
  isolation: each task own kernel boundary
  limits: up to 16 vCPU / 120 GB per task (check current docs), no GPU, ephemeral storage 20-200 GB
  best_for: APIs, workers, spiky traffic, small teams
ec2:
  server_management: you (AMI, patching, agent, disk)
  billing: instance hours, discounts via RI / Savings Plans / Spot
  startup: fast if instance has the image cached and spare capacity
  isolation: tasks share the host kernel
  limits: any instance type, GPUs, big memory, privileged mode, host networking
  best_for: steady high load, GPU, special needs, cost tuning
```

---

## 🟠 My Stack Integration
- Node.js/FastAPI APIs: Fargate (CPU 0.5-1 vCPU).
- FastAPI model inference with GPU: EC2 (g5 instances) via capacity provider.
- Nginx on the VPS today: replaced by ALB; if you keep Nginx, it is a sidecar container on either launch type.
- Cost check: a VPS at 20 USD/month beats Fargate for one tiny app; ECS wins for availability and automation, not for lowest price at tiny scale.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Choosing EC2 "to save money" without counting your ops time.
✅ Correct: Include patching and on-call time; Fargate is often cheaper in total for small teams.

❌ Mistake 2: Oversizing Fargate (4 vCPU for a Node process that uses one core).
✅ Correct: Right-size from CloudWatch metrics; Node is mostly single-threaded, scale out with more small tasks.

❌ Mistake 3: Assuming Fargate task keeps local files.
✅ Correct: Ephemeral storage is deleted; use EFS/S3/RDS.

❌ Mistake 4: Using `LaunchType` and `CapacityProviderStrategy` together.
✅ Correct: Choose one; the strategy is the modern approach.

---

## 🧠 Tricky Interview Question
Traffic is steady, 24x7, 100 tasks of 1 vCPU/2 GB. Finance says Fargate is 20-30% more expensive than EC2. Should you move everything to EC2?

Answer: Not automatically. EC2 is cheaper at high utilisation only if you pack instances well (80%+) and use Savings Plans or Reserved Instances; add engineer time for patching and scaling. Also Fargate Savings Plans / Compute Savings Plans can discount Fargate. Often a hybrid works: steady baseline on discounted EC2, bursts on Fargate. Decide with measured utilisation, not assumptions.

---

## ⚫ Interview Questions + Answers

Q1: Which supports GPU?
A1: EC2 launch type (as of this writing Fargate has no GPU support; verify current docs).

Q2: Which gives better isolation?
A2: Fargate: each task runs in its own micro-VM, not sharing a kernel with other customers' tasks.

Q3: Which is faster to scale?
A3: Fargate scales per task with no instance provisioning (limited by pull time). EC2 needs instances (minutes) unless there is spare capacity.

Q4: Where do logs and secrets differ?
A4: Same mechanisms (awslogs, secrets). EC2 additionally allows host-level agents and daemon services.

Q5: Can the same task definition run on both?
A5: Yes, if `requiresCompatibilities` lists both, and settings are valid for both (awsvpc mode, valid CPU/memory).

---

## 🔷 When to Use + When Not to Use
✅ Use Fargate when:
- Small or medium teams, spiky traffic, security isolation matters

✅ Use EC2 when:
- GPU, huge memory, steady very high utilisation, host-level control

❌ Avoid Fargate when:
- Needing privileged containers, custom kernel modules or GPUs

❌ Avoid EC2 when:
- No one owns patching and capacity planning

---

## 📊 Visual Diagram
```
 FARGATE                         EC2
 +-----------+                   +--------------------------+
 | task      |  (AWS-owned VM)   | instance (you patch it)  |
 | micro-VM  |                   |  task  task  task        |
 +-----------+                   +--------------------------+
 pay: per task-second            pay: per instance-hour (idle too)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fargate | Serverless container compute | Serverless container compute |
| EC2 launch type | Run tasks on your instances | अपने instances पर tasks |
| Bin packing | Fit tasks tightly onto hosts | Tasks को कसकर fit करना |
| Savings Plan | Discount for committed usage | Commitment पर छूट |
| Ephemeral storage | Disk that vanishes with the task | Task के साथ मिटने वाली disk |

---

## ⚡ 3-Line Summary
English: Fargate = no servers, per-task billing, strong isolation; EC2 = control, GPUs, cheaper at steady high load.
Start with Fargate; move specific workloads to EC2 when measurements justify it.
Capacity provider strategies let you mix both.

Hindi: Fargate = कोई server नहीं, per-task billing, मज़बूत isolation; EC2 = control, GPU, steady high load पर सस्ता।
Fargate से शुरू करो; मापे हुए आँकड़े सही ठहराएँ तभी कुछ workloads को EC2 पर ले जाओ।
Capacity provider strategy से दोनों मिलाए जा सकते हैं।

---

## ➡️ Next Topic
386. Deploy to ECS with GitHub Actions: automate everything from push to running service.
