# 301. Design 3-Tier App on AWS
# AWS: ALB + EC2 Auto Scaling (or ECS) + RDS PostgreSQL
# Azure: Application Gateway + VM Scale Set / App Service + Azure Database for PostgreSQL
# हिंदी में: 3-टियर ऐप = वेब (ALB), ऐप (Node.js/FastAPI) और डेटाबेस (RDS) अलग-अलग लेयर में

---

## 🔵 Simple Definition
Presentation (ALB/CDN), application (Node.js/NestJS on private subnets) and data (RDS in isolated subnets) tiers, each in its own subnet tier and security group.
हिंदी: तीन लेयर अलग सबनेट और सिक्योरिटी ग्रुप में रखें ताकि सिर्फ ज़रूरी ट्रैफिक ही आगे जाए।

## 🔴 Why it Exists
Independent scaling, blast-radius control, and the DB is never internet-reachable.

## 🟢 How it Works
```
Internet -> ALB (public subnets, 2 AZ, SG: 443 from 0.0.0.0/0)
              |  SG: app port only from ALB SG
              v
        ASG / ECS tasks (private subnets, 2 AZ) --NAT--> internet (egress)
              |  SG: 5432 only from app SG
              v
        RDS Postgres Multi-AZ (isolated subnets, no route to internet)
```

## 💻 Code / Config Example
Files in this folder:
- `main.tf` : VPC, 3 subnet tiers x 2 AZ, SGs, ALB, launch template + ASG, RDS (Terraform AWS provider ~> 5.x, not applied/validated here)
- `user_data.sh` : installs Docker and runs the app image

Decisions: SG-to-SG references instead of CIDRs; RDS password managed by Secrets Manager (`manage_master_user_password`); one NAT per AZ in prod (one here for cost).

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| L7 LB | ALB | Application Gateway |
| Compute | EC2 ASG / ECS | VMSS / App Service |
| Network | VPC + subnets + SG | VNet + subnets + NSG |
| DB | RDS Multi-AZ | Azure DB for PostgreSQL Flexible (zone-redundant HA) |
| Pricing | NAT + ALB + RDS dominate (approximate - check current docs) | App Gateway + DB dominate |

## 💰 Cost / HA / Security
- Cost: NAT gateway and Multi-AZ RDS are the big fixed costs; use VPC endpoints for S3/ECR to cut NAT traffic.
- HA: 2+ AZ everywhere, ASG min 2, RDS Multi-AZ.
- Security: DB isolated, secrets in Secrets Manager, ALB + WAF, IMDSv2 required, encrypted storage.

## ⚠️ Common Mistakes
❌ DB in a public subnet with 0.0.0.0/0 on 5432.
✅ Isolated subnets, SG allows only app SG.

❌ Single-AZ ALB/ASG.
✅ Subnets in at least two AZs.

## ⚫ Interview Q&A
Q1 [Easy]: Why separate subnets per tier?
A1: Different route tables and SGs; the DB has no internet route.

Q2 [Medium]: How does the app reach the internet for package pulls?
A2: Private subnet route to a NAT gateway in a public subnet (or VPC endpoints for AWS services).

Q3 [Hard]: How would you scale reads and survive an AZ failure?
A3: Multi-AZ standby for failover (automatic, same endpoint), read replicas for read scaling, app uses a separate reader endpoint; ASG spans AZs and ALB health checks replace instances.

## ✅ Quick Checklist
□ 2+ AZ in every tier
□ SG-to-SG rules only
□ DB encrypted, backups on, secret not in code

## ⚡ 1-Line Summary
Public ALB, private app, isolated DB, SG chaining. | ALB पब्लिक, ऐप प्राइवेट, DB अलग-थलग।

## ➡️ Next: 302. Design Serverless API on AWS
