# 128. AWS Shield (DDoS)
# AWS: AWS Shield Standard / Shield Advanced
# Azure: Azure DDoS Protection
# हिंदी में: DDoS हमलों से बचाव की सेवा

---

## 🔵 Simple Definition
Shield protects against DDoS attacks. Standard is automatic and free for all AWS customers; Advanced is a paid tier with more protection and support.
हिंदी: Shield DDoS हमलों से बचाता है, Standard सभी के लिए अपने-आप चालू रहता है।

---

## 🔴 Why it Exists
Volumetric and protocol attacks (SYN flood, UDP reflection) can take a site offline.

---

## 🟢 How it Works
```
Attack traffic --> AWS edge (CloudFront / Route 53 / ELB / Global Accelerator)
                       |  Shield Standard filters common L3/L4 attacks
                       v
  Shield Advanced: protected resources, DDoS response team (DRT),
  attack visibility, cost protection, L7 mitigation with WAF
```

---

## 💻 Code / Config Example
```bash
# Shield Advanced needs a subscription (paid). AWS CLI v2:
aws shield create-subscription
aws shield create-protection --name api-alb \
  --resource-arn arn:aws:elasticloadbalancing:ap-south-1:123456789012:loadbalancer/app/api/abc123
aws shield list-protections
```
Shield Standard needs no configuration. Put the app behind CloudFront/ALB to benefit.

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Basic | Shield Standard (free, automatic) | Infrastructure DDoS protection (default) |
| Enhanced | Shield Advanced (paid) | DDoS Network/IP Protection (paid) |
| L7 | AWS WAF | Front Door / App Gateway WAF |
| Pricing | Advanced has a monthly fee (approximate - check current docs) | Per plan/IP (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Exposing the origin IP directly.
✅ Correct: Front with CloudFront/ALB and restrict origin to them.

❌ Mistake: Assuming Shield stops application-layer abuse.
✅ Correct: Add WAF rate-based rules.

---

## ⚫ Interview Q&A
Q1: [Easy] Is Shield Standard free?
A1: Yes, enabled automatically for all customers.

Q2: [Medium] Shield vs WAF?
A2: Shield = DDoS (mostly L3/L4, plus L7 with Advanced + WAF); WAF = HTTP rule filtering.

Q3: [Hard] Design DDoS-resilient architecture.
A3: CloudFront + WAF rate limits + Shield Advanced, autoscaling, Route 53, hidden origin, caching.

---

## ✅ Quick Checklist
□ Traffic goes via edge services
□ WAF rate rule present
□ Alarms on traffic spikes

---

## ⚡ 1-Line Summary
Shield absorbs DDoS attacks at the edge | Shield एज पर DDoS हमलों को सोख लेता है।

## ➡️ Next: AWS WAF
