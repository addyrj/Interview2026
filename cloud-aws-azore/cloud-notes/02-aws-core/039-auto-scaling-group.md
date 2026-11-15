# 39. Auto Scaling Group
# AWS: Auto Scaling Group (ASG)
# Azure: Virtual Machine Scale Set (VMSS)
# हिंदी में: एक जैसे सर्वरों का समूह जो अपने-आप संभलता है

---

## 🔵 Simple Definition
An ASG is a logical group of EC2 instances with min, desired and max sizes, spread over subnets/AZs and tied to a load balancer.
हिंदी: ASG एक जैसे EC2 इंस्टेंस का समूह है जिसमें min, desired और max संख्या तय होती है।

---

## 🔴 Why it Exists
It gives self-healing, multi-AZ spread and elastic capacity without manual instance management.

---

## 🟢 How it Works
```
ASG (min 2, desired 2, max 6)
  -> Launch Template
  -> Subnets in AZ-a, AZ-b (balanced)
  -> Target Group (ALB)  + health check type ELB
Lifecycle: Pending -> InService -> Terminating -> Terminated
Maintenance: instance refresh (rolling), lifecycle hooks, warm pools
```

---

## 💻 Code / Config Example
```bash
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name api-asg \
  --launch-template LaunchTemplateName=api-lt,Version='$Default' \
  --min-size 2 --max-size 6 --desired-capacity 2 \
  --vpc-zone-identifier "subnet-aaaa1111,subnet-bbbb2222" \
  --target-group-arns arn:aws:elasticloadbalancing:ap-south-1:123456789012:targetgroup/api-tg/0123456789abcdef \
  --health-check-type ELB --health-check-grace-period 120

# Rolling replace after new template version (GitHub Actions deploy step)
aws autoscaling start-instance-refresh --auto-scaling-group-name api-asg \
  --preferences '{"MinHealthyPercentage":50,"InstanceWarmup":120}'

aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names api-asg \
  --query 'AutoScalingGroups[0].Instances[].[InstanceId,LifecycleState,HealthStatus]'
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Group | ASG | VMSS |
| Zones | Subnets in multiple AZs | Zones setting on scale set |
| Rolling update | Instance refresh | Rolling upgrade policy |
| LB integration | Target groups | Load Balancer / App Gateway pools |
| Pricing | Free; pay for resources | Free; pay for resources |

---

## ⚠️ Common Mistakes
❌ Mistake: Health check type EC2 only, so app-dead instances stay in service.
✅ Correct: Use `ELB` health check with a proper `/health` endpoint.

❌ Mistake: Grace period too short; instances killed while booting.
✅ Correct: Set grace period above your boot + app start time.

---

## ⚫ Interview Q&A
Q1: [Easy] Min, desired, max?
A1: Min = floor, max = ceiling, desired = target count now.

Q2: [Medium] How does an ASG choose which instance to terminate?
A2: Default policy balances AZs first, then picks by oldest launch template/config and closest to next billing hour; configurable termination policies.

Q3: [Hard] Zero-downtime deploy?
A3: Instance refresh with MinHealthyPercentage, ALB health checks, connection draining (deregistration delay), or blue/green with two ASGs/target groups.

---

## ✅ Quick Checklist
□ 2+ AZ subnets
□ ELB health check + grace period
□ Scaling policy attached

---

## ⚡ 1-Line Summary
ASG keeps a min-max fleet of identical, health-checked instances across AZs. | ASG कई AZ में एक जैसे, health-checked इंस्टेंस का न्यूनतम-अधिकतम समूह बनाए रखता है।

## ➡️ Next: Elastic Load Balancer (ALB/NLB)
