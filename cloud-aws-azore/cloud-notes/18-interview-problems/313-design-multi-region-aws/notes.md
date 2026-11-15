# 313. Design Multi-region AWS
# AWS: Route 53 failover + DynamoDB Global Tables + S3 CRR (+ Aurora Global Database)
# Azure: Front Door / Traffic Manager + Cosmos DB multi-region + GRS/RA-GRS storage
# हिंदी में: दो रीजन में ऐप चलाना ताकि एक रीजन गिरे तो भी सर्विस चलती रहे

---

## 🔵 Simple Definition
Run the same stack in two Regions; DNS sends users to the healthy one and data is replicated across Regions.
हिंदी: दो रीजन में एक जैसा सिस्टम, DNS हेल्दी रीजन पर ट्रैफिक भेजता है।

## 🔴 Why it Exists
A whole Region outage (rare) or latency for global users cannot be fixed by Multi-AZ alone. Needed when RTO/RPO or compliance demand it.

## 🟢 How it Works
```
Users -> Route 53 (failover / latency records + health check)
            |-- PRIMARY  ap-south-1     ALB -> ECS/EC2 -> Aurora writer / DynamoDB
            '-- SECONDARY ap-southeast-1 ALB -> ECS/EC2 -> Aurora replica / DynamoDB replica
Data: DynamoDB Global Table (multi-active, async), S3 CRR (async), Aurora Global DB (1 writer region)
Failure: health check fails x3 -> DNS answers secondary (TTL bound) -> promote DB if needed
```

## 💻 Code / Config Example
`main.tf` (this folder): two provider aliases, DynamoDB global table replica, Route 53 PRIMARY/SECONDARY failover with health check, S3 cross-region replication with IAM role.
Prereqs not included: the two ALBs/app stacks (see 301, 307), hosted zone. Not applied - no credentials; `terraform validate` not run (terraform not installed).

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Global routing | Route 53 failover/latency | Front Door (L7) / Traffic Manager (DNS) |
| NoSQL replication | DynamoDB Global Tables | Cosmos DB multi-region writes |
| Relational | Aurora Global Database | Azure SQL failover groups / PG read replicas |
| Object storage | S3 CRR | GRS / GZRS, object replication |
| Pricing | inter-region transfer + duplicate compute (approximate - check current docs) | similar |

## 💰 Cost / HA / Security
- Cost: roughly doubles infra; pilot-light or warm-standby DR reduces it. Inter-region data transfer is billed.
- HA: Route 53 health checks + low TTL (e.g. 60s); DNS failover is not instant (client caching). Test failover regularly.
- Security: KMS keys are Regional - use multi-Region keys or per-Region keys; replicate secrets (Secrets Manager replica); same IAM/SCP in both.

## ⚠️ Common Mistakes
❌ Replicating data but never testing failover.
✅ Run game-days; automate promotion runbook.

❌ Assuming active-active writes are conflict-free.
✅ Global Tables use last-writer-wins; design keys/ownership per Region.

## ⚫ Interview Q&A
Q1 [Easy]: Multi-AZ vs multi-region?
A1: Multi-AZ survives a datacenter failure inside a Region; multi-region survives a whole Region failure.

Q2 [Medium]: Active-passive vs active-active?
A2: Active-passive: secondary idle/warm, simpler, higher RTO. Active-active: both serve traffic, lower RTO, needs conflict handling and data design.

Q3 [Hard]: Primary region dies; what breaks that you did not replicate?
A3: Typical gaps: Regional KMS keys, secrets, ECR images, AMIs, parameter store, IAM-independent config, Route 53 TTL caching, DB promotion time, quotas in the DR Region.

## ✅ Quick Checklist
□ RTO/RPO defined and DR tier chosen
□ Data, secrets, images, keys replicated
□ Failover drill done and documented

## ⚡ 1-Line Summary
Multi-region = replicated stack + health-checked DNS failover, paid for in cost and complexity. | मल्टी-रीजन = रेप्लिकेटेड स्टैक + DNS फेलओवर, बदले में ज़्यादा खर्च और जटिलता।

## ➡️ Next: 314. Design Cost Optimized AWS
