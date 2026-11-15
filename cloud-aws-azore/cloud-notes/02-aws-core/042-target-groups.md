# 42. Target Groups
# AWS: ELB Target Groups
# Azure: Backend Pools (Load Balancer / Application Gateway)
# हिंदी में: वह समूह जहाँ लोड बैलेंसर ट्रैफिक भेजता है

---

## 🔵 Simple Definition (2 lines)
A target group is a set of targets (EC2, IP, Lambda, or ALB) with a protocol, port and health check that a listener forwards to.
टारगेट ग्रुप = सर्वरों की सूची + पोर्ट + हेल्थ चेक, जिन पर ALB/NLB रिक्वेस्ट भेजता है।

---

## 🔴 Why it Exists (2 lines)
Routing rules need a named destination so you can scale, deploy and health-check each service separately.
It enables blue/green and weighted deployments by swapping or weighting groups.

---

## 🟢 How it Works
```
Listener rule --forward--> Target Group
                              |- health check GET /health every 30s
                              |- healthy: i-1 (:3000), i-2 (:3000)
                              |- unhealthy: i-3  -> gets no traffic
Target types: instance | ip (Fargate/ECS awsvpc) | lambda | alb
```

---

## 💻 Code / Config Example
```bash
# AWS CLI v2: create a target group for a NestJS container on ECS Fargate
aws elbv2 create-target-group \
  --name api-tg --protocol HTTP --port 3000 \
  --vpc-id vpc-0123456789abcdef0 --target-type ip \
  --health-check-path /health \
  --health-check-interval-seconds 15 \
  --healthy-threshold-count 2 --unhealthy-threshold-count 3

# Tune graceful deploys: let in-flight requests finish
aws elbv2 modify-target-group-attributes \
  --target-group-arn "<tg-arn>" \
  --attributes Key=deregistration_delay.timeout_seconds,Value=30
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Target Group | Backend pool + health probe + HTTP settings |
| Target types | instance, ip, lambda, alb | VM, VMSS, IP/FQDN, App Service |
| Weighted routing | Forward action with multiple TGs | Traffic Manager / Front Door weights |
| Pricing | No separate charge (LB hours apply) | No separate charge (gateway/LB charges apply) |

---

## ⚠️ Common Mistakes
❌ Mistake: Health check path `/` returns 301/404, so all targets are "unhealthy".
✅ Correct: Dedicated `/health` returning 200 (or set the success matcher).

❌ Mistake: Wrong target type for Fargate (`instance`).
✅ Correct: Use `ip` for awsvpc networking (Fargate).

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What does a health check do?
A1: Probes each target; unhealthy targets are removed from rotation until they pass again.

Q2: [Medium] Why is deregistration delay important?
A2: It lets in-flight requests complete (default 300s) when a target is removed during deploys; lower it for fast APIs.

Q3: [Hard] How do you do a canary release with ALB?
A3: Forward action to two target groups with weights (e.g. 90/10), optionally with stickiness, then shift weights as metrics stay healthy.

---

## ✅ Quick Checklist
□ Correct target type (ip for Fargate)
□ Health check path/threshold tuned
□ Security group allows ALB -> target port
□ Deregistration delay set sensibly

---

## ⚡ 1-Line Summary
A target group is the health-checked pool a load balancer forwards to. | टारगेट ग्रुप वह हेल्थ-चेक वाला पूल है जिस पर लोड बैलेंसर ट्रैफिक भेजता है।

## ➡️ Next: S3 — Complete Guide
