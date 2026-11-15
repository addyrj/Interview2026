---

# Q157. Azure SQL Database vs SQL Managed Instance vs SQL Server on VM
# Category: AZURE SQL + NODE.JS INTEGRATION
# Difficulty: ⭐⭐ Medium
# DB: SQL Server / Azure SQL (PostgreSQL/MySQL equivalents: Azure Database for PostgreSQL/MySQL flexible server)

---

## ❓ Question
Your team is migrating an on-prem SQL Server app (some SQL Agent jobs, a cross-database query, a CLR assembly) to Azure. Compare the three options and recommend one. How can you tell at runtime which one you are connected to?

---

## 💡 Quick Concept (2 lines only)
Azure SQL Database = PaaS, one database (or pool), least admin, narrowest instance-level feature set. Managed Instance = PaaS with near-100% instance compatibility (Agent, cross-DB queries, linked servers); SQL Server on VM = IaaS, full OS/instance control and full patching burden.
हिंदी: SQL Database = सबसे कम management, कम instance features। Managed Instance = लगभग पूरा SQL Server, फिर भी PaaS। VM = पूरा control पर patching/backups खुद की ज़िम्मेदारी।

---

## ✅ Answer / Solution

NOTE: conceptual question; not executed on SQL Server / Azure. Feature support changes over time, so confirm in current Microsoft docs.

```sql
-- ============================================
-- WHICH FLAVOUR AM I ON?  (EngineEdition is documented: 5 = Azure SQL Database,
-- 8 = Azure SQL Managed Instance; on-prem/VM returns other values such as 2/3/4)
-- ============================================
SELECT SERVERPROPERTY('EngineEdition')   AS EngineEdition,
       SERVERPROPERTY('ProductVersion')  AS ProductVersion,
       DB_NAME()                         AS CurrentDb;

-- Instance-level feature check you cannot rely on in Azure SQL Database:
-- cross-database query    -> SELECT * FROM OtherDb.dbo.Orders;   (works on MI/VM; not on SQL Database,
--                            use elastic query or consolidate schemas)
-- SQL Agent jobs          -> MI/VM have SQL Agent; SQL Database uses Elastic Jobs / Azure Automation
```

| Need | SQL Database | Managed Instance | SQL on VM |
|---|---|---|---|
| Admin effort | lowest | low | highest |
| Instance features (Agent, cross-DB, linked server) | limited | broad | full |
| OS access / custom installs / any version | no | no | yes |
| Built-in HA/backups/patching | yes | yes | you build it (or use IaaS extension) |
| Migration effort from on-prem | highest (may need refactor) | lowest PaaS path | lowest overall |

Recommendation for the scenario: Managed Instance (Agent jobs + cross-DB queries kept); CLR support and other items should be validated with Azure Data Migration tooling before committing.

---

## 🔍 Why This Works (3 lines max)
The decision is driven by instance-scoped dependencies (Agent, cross-DB, linked servers, CLR, OS-level access) versus how much administration you want to own. New cloud-native apps with one database per app usually fit SQL Database best.
हिंदी: फैसला इस पर कि कौन-से instance-level features चाहिए। नया app = SQL Database; पुराना app जिसमें Agent/cross-DB है = Managed Instance; OS-level control = VM।

---

## ⚡ Alternative Solution

```sql
-- Keep SQL Database but replace instance features:
--  * cross-DB joins      -> merge into one DB with schemas (dbo/sales/billing)
--  * Agent jobs          -> Azure Elastic Jobs / Azure Functions timer / Automation runbook
--  * many small DBs      -> elastic pool (see Q167)
-- Assess first with Azure Data Studio / DMA migration assessment before choosing.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: choosing SQL Database, then discovering USE OtherDb / cross-DB queries and Agent jobs are needed
-- ❌ Wrong: choosing VM "for control" and forgetting you now own patching, backups, HA and licensing
-- ❌ Wrong: assuming a lift-and-shift connection string works - endpoints, auth (Entra) and firewall/VNet model differ
-- ✅ Run an assessment, then pick the most managed option that satisfies the hard requirements
```

---

## 🎯 Interview Tip (1 line)
Say: "I pick the most managed option that satisfies the hard dependencies: SQL Database for a self-contained app, Managed Instance when I need Agent, cross-database or other instance features with minimal refactor, and a VM only for OS access or unsupported features — validated with an assessment tool, and with cost, HA/DR and the migration path considered."

---

## 🔗 Related Questions
→ Q158 (DTU vs vCore) | Q165 (Geo-replication and failover groups) | Q166 (Backup, PITR, LTR) | Q167 (Elastic pools)
