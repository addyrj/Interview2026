# 305. Design Auto Scaling Setup
# AWS: EC2 Auto Scaling (target tracking, scheduled), Application Auto Scaling for ECS
# Azure: VM Scale Sets autoscale / App Service autoscale rules
# हिंदी में: ऑटो स्केलिंग = लोड के हिसाब से इंस्टेंस अपने-आप बढ़ें और घटें

---

## 🔵 Simple Definition
Policies add or remove capacity based on a metric (CPU, requests per target, queue depth) or a schedule, between a min and max.
हिंदी: मेट्रिक या शेड्यूल देखकर मशीनें अपने-आप जोड़ी या हटाई जाती हैं।

## 🔴 Why it Exists
Fixed capacity either wastes money off-peak or fails at peak.

## 🟢 How it Works
```
CloudWatch metric (ALBRequestCountPerTarget / CPU) -> target tracking policy
   value above target -> scale out (fast)      value below target -> scale in (slow, cooldown)
ASG min=2 desired=2 max=10, health check = ELB, warm-up = app boot time
Worker apps: scale on SQS "backlog per instance" (custom metric) not CPU
```

## 💻 Code / Config Example
`autoscaling.tf` (provider ~> 5.x, not applied here): ASG, target tracking on CPU 50% and on ALB requests per target, scheduled scale-up for business hours. `loadtest.sh` generates load with `hey` (syntax-checked only).

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | EC2 Auto Scaling | VMSS autoscale / Azure Monitor autoscale |
| Policy types | target tracking, step, scheduled, predictive | metric rules, schedule, predictive (VMSS) |
| Containers | ECS Service Auto Scaling, Karpenter/HPA on EKS | Container Apps KEDA scaling, AKS HPA |
| Pricing | free; pay for instances | free; pay for instances |

## 💰 Cost / HA / Security
- Cost: scale in aggressively off-peak, use Spot/Graviton in the mix, scheduled floor for known peaks.
- HA: min >= 2 across AZ; max cap protects the DB from connection storms.
- Security: instance profile least privilege; immutable AMI/container images.

## ⚠️ Common Mistakes
❌ Scaling on CPU for an I/O bound API.
✅ Use requests-per-target or latency; test the metric.

❌ Warm-up shorter than app startup (flapping).
✅ Set `estimated_instance_warmup` to real boot time.

## ⚫ Interview Q&A
Q1 [Easy]: Target tracking vs step scaling?
A1: Target tracking keeps a metric near a target value automatically; step scaling uses explicit alarm thresholds and step sizes.

Q2 [Medium]: How do you autoscale a queue worker?
A2: Backlog per instance = ApproximateNumberOfMessages / running tasks, target e.g. acceptable latency / processing time.

Q3 [Hard]: Scaling out but DB melts. What now?
A3: Cap max size, add connection pooling (RDS Proxy/PgBouncer), cache reads, scale DB readers, and apply backpressure with queues.

## ✅ Quick Checklist
□ min/max/desired set sensibly
□ Right metric and warm-up
□ DB limits considered

## ⚡ 1-Line Summary
Scale on the metric that reflects load, with min/max guards. | सही मेट्रिक पर स्केल करें, min/max सीमा के साथ।

## ➡️ Next: 306. Design Secure VPC
