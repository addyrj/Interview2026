# 103. ECS Auto Scaling
# AWS: ECS Service Auto Scaling (Application Auto Scaling)
# Azure: Container Apps scale rules (KEDA) / AKS HPA + Cluster Autoscaler
# हिंदी में: load बढ़ने पर tasks की संख्या अपने-आप बढ़ना और घटना

---

## 🔵 Simple Definition
Application Auto Scaling changes the DesiredCount of an ECS service based on metrics (CPU, memory, ALB requests per target) or a schedule.
Load के हिसाब से container की गिनती अपने-आप घटती-बढ़ती है।

---

## 🔴 Why it Exists
Fixed task counts waste money at night and fall over at peak. Autoscaling matches capacity to demand.

---

## 🟢 How it Works
```
CloudWatch metric (CPU avg) --> Target Tracking policy (target 60%)
        |                               |
        v                               v
 scalable target: min 2 / max 10  --> UpdateService DesiredCount
Scale-out fast (short cooldown), scale-in slow (long cooldown)
EC2 launch type also needs capacity provider managed scaling for instances.
```

---

## 💻 Code / Config Example
```bash
# AWS CLI v2 - target tracking on CPU for service api in cluster prod
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/prod/api \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 --max-capacity 10

aws application-autoscaling put-scaling-policy \
  --policy-name cpu60 \
  --service-namespace ecs \
  --resource-id service/prod/api \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 60.0,
    "PredefinedMetricSpecification": {"PredefinedMetricType": "ECSServiceAverageCPUUtilization"},
    "ScaleOutCooldown": 60,
    "ScaleInCooldown": 300
  }'
```
Other predefined metrics: `ECSServiceAverageMemoryUtilization`, `ALBRequestCountPerTarget`.

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service scaling | Application Auto Scaling | Container Apps KEDA rules / HPA |
| Node scaling | Capacity provider / ASG | Cluster Autoscaler / VMSS |
| Scale to zero | No (min 1 task unless you set 0 manually) | Yes (Container Apps) |
| Pricing | Free feature; pay for tasks + CloudWatch | Same model |

---

## ⚠️ Common Mistakes
❌ Mistake: Min = max or no max cap.
✅ Correct: Sensible min for HA (2+ across AZs) and max for cost cap.

❌ Mistake: Scaling on CPU for an IO-bound Node API.
✅ Correct: Use ALBRequestCountPerTarget or a custom queue-depth metric.

---

## ⚫ Interview Q&A
Q1: [Easy] What does ECS autoscaling change?
A1: The service DesiredCount.
Q2: [Medium] Target tracking vs step scaling?
A2: Target tracking keeps a metric near a value automatically; step scaling uses explicit alarm thresholds and step sizes.
Q3: [Hard] Tasks scale but stay PENDING on EC2 - why?
A3: No instance capacity. Use a capacity provider with managed scaling so the ASG grows too; Fargate avoids this.

---

## ✅ Quick Checklist
□ Scalable target min/max set
□ Right metric for workload
□ Scale-in cooldown longer than scale-out

---

## ⚡ 1-Line Summary
Autoscaling keeps DesiredCount in line with load | Autoscaling load के हिसाब से tasks की संख्या ठीक रखती है।

## ➡️ Next: 104. ECS + ECR
