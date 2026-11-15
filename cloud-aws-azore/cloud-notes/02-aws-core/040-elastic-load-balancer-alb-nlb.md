# 40. Elastic Load Balancer (ALB/NLB)
# AWS: Elastic Load Balancing (ALB, NLB, GWLB)
# Azure: Application Gateway (L7), Load Balancer (L4)
# हिंदी में: आने वाला ट्रैफिक कई सर्वरों में बांटने वाला

---

## 🔵 Simple Definition
ELB distributes incoming traffic across healthy targets in multiple AZs; ALB works at Layer 7 (HTTP), NLB at Layer 4 (TCP/UDP/TLS).
हिंदी: ELB ट्रैफिक को कई स्वस्थ सर्वरों में बांटता है; ALB HTTP स्तर पर और NLB TCP स्तर पर काम करता है।

---

## 🔴 Why it Exists
One server is a single point of failure. A load balancer gives HA, health checks, TLS termination and routing.

---

## 🟢 How it Works
```
Client -> DNS -> ALB (public subnets, 2+ AZs)
          Listener :443 (ACM cert) -> rules:
             /api/*  -> Target Group api (Node.js :3000)
             /ml/*   -> Target Group fastapi (:8000)
          Health check GET /health -> only healthy targets get traffic
NLB: static IP per AZ, very low latency, preserves source IP, TCP/UDP.
```

---

## 💻 Code / Config Example
```bash
VPC_ID=vpc-0123456789abcdef0
TG=$(aws elbv2 create-target-group --name api-tg --protocol HTTP --port 3000 \
  --vpc-id $VPC_ID --health-check-path /health --target-type instance \
  --query 'TargetGroups[0].TargetGroupArn' --output text)

ALB=$(aws elbv2 create-load-balancer --name api-alb --type application \
  --subnets subnet-aaaa1111 subnet-bbbb2222 --security-groups sg-aaaa1111 \
  --query 'LoadBalancers[0].LoadBalancerArn' --output text)

aws elbv2 create-listener --load-balancer-arn $ALB --protocol HTTPS --port 443 \
  --certificates CertificateArn=arn:aws:acm:ap-south-1:123456789012:certificate/xxxx \
  --default-actions Type=forward,TargetGroupArn=$TG

# Redirect HTTP -> HTTPS
aws elbv2 create-listener --load-balancer-arn $ALB --protocol HTTP --port 80 \
  --default-actions 'Type=redirect,RedirectConfig={Protocol=HTTPS,Port=443,StatusCode=HTTP_301}'
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| L7 HTTP | ALB | Application Gateway |
| L4 TCP/UDP | NLB | Azure Load Balancer |
| WAF | AWS WAF on ALB | WAF on Application Gateway / Front Door |
| TLS certs | ACM (free public) | Key Vault / App Gateway managed certs |
| Pricing | Hourly + capacity units (LCU) (approximate, check current docs) | Hourly + capacity units (check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Targets show unhealthy because SG blocks ALB.
✅ Correct: App SG must allow app port from ALB SG; health path must return 200.

❌ Mistake: ALB in private subnets for an internet-facing app.
✅ Correct: Internet-facing ALB lives in public subnets, targets in private.

---

## ⚫ Interview Q&A
Q1: [Easy] ALB vs NLB?
A1: ALB: HTTP/HTTPS, path/host routing, WebSocket, WAF. NLB: TCP/UDP/TLS, ultra-low latency, static/Elastic IPs.

Q2: [Medium] What is a target group and deregistration delay?
A2: Target group is the set of targets plus health checks; deregistration delay lets in-flight requests finish before removing a target.

Q3: [Hard] Route `/api` to Node.js and `/predict` to FastAPI with HTTPS and blue/green?
A3: One ALB, listener rules by path to two target groups; for blue/green use weighted forwarding between two target groups of the new and old ASG, shifting weights gradually.

---

## ✅ Quick Checklist
□ 2+ public subnets in different AZs
□ ACM cert + HTTP->HTTPS redirect
□ `/health` endpoint and SG chain correct

---

## ⚡ 1-Line Summary
ALB routes HTTP by path/host, NLB moves raw TCP fast; both spread load over healthy targets. | ALB HTTP को path/host से रूट करता है, NLB तेज़ TCP; दोनों स्वस्थ टारगेट में लोड बांटते हैं।

## ➡️ Next: S3 Basics
