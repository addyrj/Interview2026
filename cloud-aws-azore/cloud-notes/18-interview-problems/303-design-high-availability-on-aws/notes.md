# 303. Design High Availability on AWS
# AWS: Multi-AZ ALB + Auto Scaling Group + Aurora/RDS Multi-AZ
# Azure: Availability Zones + Load Balancer/App Gateway + VMSS + zone-redundant DB
# हिंदी में: HA = कोई एक AZ गिरे तो भी सिस्टम चलता रहे (कोई single point of failure नहीं)

---

## 🔵 Simple Definition
Spread every tier across at least 2-3 Availability Zones, remove single points of failure, and automate failure detection and replacement.
हिंदी: हर लेयर कम से कम दो AZ में फैलाएं और फेल होने पर अपने-आप बदलाव (failover) हो।

## 🔴 Why it Exists
Hardware, AZ and deploy failures are normal; the target is an SLA such as 99.9% / 99.99% (about 8.8 h / 53 min downtime a year).

## 🟢 How it Works
```
Route 53 (health checks) -> ALB (nodes in 3 AZ, cross-zone)
        AZ-a: app x1      AZ-b: app x1      AZ-c: app x1   (ASG min=3, ELB health check)
        Aurora: writer (AZ-a) + reader (AZ-b); failover promotes reader (~30-60 s, approximate)
        State outside instances: S3, DynamoDB, ElastiCache replicas, SQS
Deploys: rolling instance refresh with min healthy 66%
```

## 💻 Code / Config Example
`ha.tf` (inputs: VPC subnet IDs, SG IDs; Terraform AWS provider ~> 5.x; not applied here):
ASG over 3 AZ with ELB health check and instance refresh, ALB target group with deregistration delay, Aurora PostgreSQL cluster with a writer and a reader in different AZ.

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Fault domain | Availability Zone | Availability Zone |
| LB | ALB (multi-AZ by design) | Standard LB / App Gateway v2 (zone-redundant) |
| Compute | ASG across AZ | VMSS with zones |
| DB | Aurora / RDS Multi-AZ | Flexible Server zone-redundant HA, SQL zone redundancy |
| SLA | per-service, check AWS SLAs | per-service, composite SLA = product of tiers |

## 💰 Cost / HA / Security
- Cost: N+1 capacity in each AZ roughly doubles standby cost; Multi-AZ DB ~2x single-AZ.
- HA: stateless app, health checks tied to ELB, test failover (AWS FIS / game days).
- Security: HA does not replace backups; keep PITR and cross-account backups.

## ⚠️ Common Mistakes
❌ ASG in one subnet or `health_check_type = EC2` only.
✅ Subnets in 3 AZ and ELB health checks.

❌ Sessions stored in instance memory.
✅ Redis/DynamoDB sessions or stateless JWT.

## ⚫ Interview Q&A
Q1 [Easy]: HA vs DR?
A1: HA handles component/AZ failure within a region automatically; DR recovers from a region loss or data disaster, often with manual steps.

Q2 [Medium]: How is composite availability computed?
A2: Serial dependencies multiply (0.999 x 0.999 = 0.998); redundant parallel components improve it.

Q3 [Hard]: An AZ fails; walk through what happens.
A3: ALB stops routing to unhealthy targets, ASG launches replacements in remaining AZ, DB fails over to the replica; capacity must already exist (headroom) because AZ launches may be contended.

## ✅ Quick Checklist
□ 3 AZ or at least 2
□ No local state, ELB health checks
□ DB Multi-AZ and failover tested

## ⚡ 1-Line Summary
Redundancy in every tier across AZ plus automated failover. | हर टियर में रिडंडेंसी और ऑटो-फेलओवर।

## ➡️ Next: 304. Design Disaster Recovery
