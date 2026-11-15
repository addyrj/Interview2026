# 319. Cloud Migration Strategy
# AWS: Migration Hub + Application Migration Service (MGN) + DMS
# Azure: Azure Migrate + Azure Database Migration Service
# हिंदी में: VPS या ऑन-प्रेम से क्लाउड में सुरक्षित तरीके से जाना - 6 R, वेव्स और रोलबैक

---

## 🔵 Simple Definition
Inventory your apps, choose a strategy per app (the 6 Rs), move in waves, and keep a rollback path.
हिंदी: ऐप्स की सूची, हर ऐप की रणनीति (6 R), वेव्स में मूव और रोलबैक तैयार।

## 🔴 Why it Exists
Big-bang migrations fail. A phased, data-aware plan limits risk and downtime.

## 🟢 How it Works
```
1 Assess   : discover apps, dependencies, sizes, owners (Migration Hub / Azure Migrate)
2 Decide   : Rehost | Replatform | Refactor | Repurchase | Retire | Retain
3 Foundation: landing zone, network, IAM, logging, tags
4 Migrate in waves: low-risk first; data via DMS (full load + CDC) / file sync
5 Cutover  : freeze writes -> final sync -> validate -> DNS switch (low TTL set earlier)
6 Optimize : right-size, cost, decommission old after retention period
```

## 💻 Code / Config Example
`migration-plan.yaml`: waves, per-app strategy, DMS mode, cutover and rollback. `sync-data.sh`: repeatable `aws s3 sync` of uploads from a VPS (syntax-checked with `bash -n`, not run - no AWS CLI/credentials).
Typical Node.js/VPS path: Dockerize app -> ECS/Container Apps -> Postgres via DMS -> switch DNS.

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Discovery/tracking | Migration Hub / Application Discovery | Azure Migrate |
| Server rehost | Application Migration Service | Azure Migrate: Server Migration |
| DB migration | DMS (+ SCT) | Azure Database Migration Service |
| Bulk files | S3 sync / DataSync / Snowball | AzCopy / Data Box |
| Pricing | tooling is mostly free; you pay for target resources (approximate - check current docs) | same |

## 💰 Cost / HA / Security
- Cost: run old and new in parallel only briefly; estimate with calculators before committing.
- HA: keep rollback ready (reverse replication, old env alive) until validated.
- Security: encrypt in transit and at rest during transfer, least-privilege migration roles, remove them after.

## ⚠️ Common Mistakes
❌ Migrating the app but forgetting hidden dependencies (cron, SMTP, file shares).
✅ Dependency mapping and traffic observation first.

❌ DNS TTL left at 24h.
✅ Lower TTL days before cutover.

## ⚫ Interview Q&A
Q1 [Easy]: What are the 6 Rs?
A1: Rehost, Replatform, Refactor, Repurchase, Retire, Retain.

Q2 [Medium]: How do you migrate a live database with minimal downtime?
A2: Full load plus change data capture (DMS) to keep target in sync, then short write freeze, final catch-up, validate, switch.

Q3 [Hard]: Cutover failed validation at 2 AM; what now?
A3: Execute pre-agreed rollback (repoint DNS to source, source stays authoritative), investigate with captured logs, fix, reschedule; this is why reverse replication/rollback criteria are defined up front.

## ✅ Quick Checklist
□ Inventory + dependency map
□ Strategy and wave per app
□ Tested cutover and rollback runbook

## ⚡ 1-Line Summary
Assess, pick an R, migrate in waves, cut over with a rollback. | आकलन, R चुनो, वेव्स में मूव, रोलबैक के साथ कटओवर।

## ➡️ Next: 320. Cloud Cost Optimization
