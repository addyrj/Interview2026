# 37. EC2 Auto Scaling
# AWS: Amazon EC2 Auto Scaling
# Azure: Virtual Machine Scale Sets (autoscale)
# हिंदी में: लोड के हिसाब से सर्वर अपने-आप घटाना-बढ़ाना

---

## 🔵 Simple Definition
EC2 Auto Scaling automatically adds or removes instances based on demand or schedule and replaces unhealthy ones.
हिंदी: Auto Scaling लोड के अनुसार इंस्टेंस अपने-आप बढ़ाता/घटाता है और खराब इंस्टेंस बदल देता है।

---

## 🔴 Why it Exists
Fixed capacity either fails at peak or wastes money off-peak. Scaling gives availability and cost efficiency.

---

## 🟢 How it Works
```
CloudWatch metric (CPU, ALB RequestCountPerTarget, SQS depth)
        -> scaling policy -> ASG changes desired capacity
        -> Launch Template -> new instance -> registers in target group
Health checks (EC2 / ELB) -> unhealthy -> terminate + replace
Types: target tracking | step | scheduled | predictive
```

---

## 💻 Code / Config Example
```bash
# Keep average CPU around 50% (target tracking)
cat > policy.json <<'EOF'
{
  "TargetValue": 50.0,
  "PredefinedMetricSpecification": {
    "PredefinedMetricType": "ASGAverageCPUUtilization"
  },
  "DisableScaleIn": false
}
EOF
python3 -c "import json;json.load(open('policy.json'))" && echo json ok

aws autoscaling put-scaling-policy --auto-scaling-group-name api-asg \
  --policy-name cpu50 --policy-type TargetTrackingScaling \
  --target-tracking-configuration file://policy.json

# Scheduled scale for office hours (UTC cron)
aws autoscaling put-scheduled-update-group-action --auto-scaling-group-name api-asg \
  --scheduled-action-name morning --recurrence "0 4 * * 1-5" --min-size 3
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | EC2 Auto Scaling (ASG) | VM Scale Sets + Autoscale |
| Template | Launch Template | Scale set model/image |
| Metrics | CloudWatch | Azure Monitor |
| Pricing | Free; pay for instances | Free; pay for VMs |

---

## ⚠️ Common Mistakes
❌ Mistake: Scaling on CPU for an I/O-bound or queue worker app.
✅ Correct: Scale on ALB request count per target or SQS backlog per instance.

❌ Mistake: No cooldown/warm-up, causing flapping.
✅ Correct: Set instance warm-up and conservative scale-in.

---

## ⚫ Interview Q&A
Q1: [Easy] Scale out vs scale up?
A1: Out adds instances (Auto Scaling); up makes one instance bigger.

Q2: [Medium] Target tracking vs step scaling?
A2: Target tracking keeps a metric near a target automatically (like a thermostat); step uses explicit alarm thresholds and step sizes.

Q3: [Hard] App is stateful (sessions, local uploads). How to scale?
A3: Externalize state: sessions in Redis/ElastiCache, files in S3, DB in RDS; instances become disposable, use connection draining.

---

## ✅ Quick Checklist
□ Stateless app
□ Min >= 2 across 2 AZs
□ Scale-in protection / draining configured

---

## ⚡ 1-Line Summary
Auto Scaling adjusts instance count to demand and self-heals. | Auto Scaling माँग के हिसाब से इंस्टेंस की संख्या बदलता है और खुद ठीक भी करता है।

## ➡️ Next: Launch Template
