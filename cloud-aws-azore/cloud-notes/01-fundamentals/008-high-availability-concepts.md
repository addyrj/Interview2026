---

# 8. High Availability Concepts
# AWS: Multi-AZ, ELB/ALB, Auto Scaling, Route 53 health checks
# Azure: Availability Zones, Load Balancer/App Gateway, VMSS, Traffic Manager
# हिंदी में: हाई अवेलेबिलिटी = सिस्टम का लगभग हमेशा चालू रहना

---

## 🔵 Simple Definition (2 lines)
High availability (HA) means designing so the system keeps serving requests even when a component or data center fails, by removing single points of failure.
हिंदी: कोई एक हिस्सा फेल हो जाए तब भी सर्विस चलती रहे, इसके लिए रिडंडेंसी और ऑटो-फेलओवर।

---

## 🔴 Why it Exists (2 lines)
Hardware, networks and deployments fail; downtime costs money and trust.
Redundancy plus health checks lets traffic route around failures.

---

## 🟢 How it Works
```
          Users
            |
      Load Balancer (health checks)
        /          \
  AZ-a [app x2]   AZ-b [app x2]
        \          /
     DB primary (AZ-a)  <-- sync replica/standby (AZ-b), auto failover
Availability % = uptime / total time
99.9% ~ 8.8 h/yr down | 99.99% ~ 52 min/yr down
```

---

## 💻 Code / Config Example
```yaml
# docker-compose style health check your LB can rely on (app side)
services:
  api:
    image: myapp:1.0
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]
      interval: 10s
      timeout: 3s
      retries: 3
```
```bash
# AWS: ALB target group health check on /health
aws elbv2 modify-target-group --target-group-arn <tg-arn> \
  --health-check-path /health --health-check-interval-seconds 15 \
  --healthy-threshold-count 2 --unhealthy-threshold-count 3
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| L7 load balancing | ALB | Application Gateway |
| L4 load balancing | NLB | Azure Load Balancer |
| DNS failover | Route 53 | Traffic Manager / Front Door |
| DB HA | RDS Multi-AZ | Zone-redundant Azure SQL / Flexible Server HA |

---

## ⚠️ Common Mistakes
❌ Mistake: Two instances in the same AZ called "HA".
✅ Correct: Spread across at least 2 AZs.

❌ Mistake: Health check only returns 200 without checking dependencies sensibly.
✅ Correct: Use a lightweight shallow check for LB and a separate deep readiness check.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is a single point of failure?
A1: A component whose failure takes down the system.

Q2: [Medium] Active-active vs active-passive?
A2: Active-active serves from all nodes (better utilization, complex state); active-passive keeps standby for failover (simpler, idle cost).

Q3: [Hard] How do you design a 99.99% web app?
A3: Multi-AZ at every tier, stateless apps, managed HA DB, health checks and autoscaling, safe deployments (rolling/blue-green), tested failover; remember composite SLA is the product of dependencies.

---

## ✅ Quick Checklist
□ 2+ AZs for app and DB
□ Health checks tuned
□ Failover actually tested

---

## ⚡ 1-Line Summary
HA = no single point of failure plus automatic failover | HA = कोई सिंगल पॉइंट ऑफ़ फेल्योर नहीं, अपने-आप फेलओवर।

## ➡️ Next: 9. Fault Tolerance Concepts

---
