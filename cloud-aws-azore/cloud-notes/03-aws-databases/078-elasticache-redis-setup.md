# 78. ELASTICACHE REDIS SETUP
# AWS: ElastiCache replication group (Redis OSS)
# Azure: Azure Cache for Redis instance
# हिंदी में: ElastiCache Redis सेटअप कैसे करें

---

## 🔵 Simple Definition (2 lines)
A Redis setup is a replication group (one primary, optional replicas) placed in private subnets, secured by a security group and TLS.
हिंदी: Redis सेटअप एक रेप्लिकेशन ग्रुप है जो प्राइवेट सबनेट में, सिक्योरिटी ग्रुप और TLS के साथ चलता है।

---

## 🔴 Why it Exists (2 lines)
A single cache node is a SPOF and a public Redis gets hijacked quickly.
A proper setup adds Multi-AZ failover, encryption and network isolation.

---

## 🟢 How it Works
```
1. Subnet group (private subnets, 2+ AZs)
2. Security group: 6379 from App SG only
3. Replication group: primary + 1 replica, automatic failover, Multi-AZ
4. Encryption at rest + in transit (TLS), optional AUTH token / user ACL
5. App connects to the PRIMARY endpoint (writes) / reader endpoint (reads)
```

---

## 💻 Code / Config Example
```yaml
# CloudFormation: Redis replication group
AWSTemplateFormatVersion: "2010-09-09"
Parameters:
  SubnetIds: {Type: "List<AWS::EC2::Subnet::Id>"}
  CacheSgId: {Type: "AWS::EC2::SecurityGroup::Id"}
Resources:
  Subnets:
    Type: AWS::ElastiCache::SubnetGroup
    Properties:
      Description: cache subnets
      SubnetIds: !Ref SubnetIds
  Redis:
    Type: AWS::ElastiCache::ReplicationGroup
    Properties:
      ReplicationGroupDescription: app redis
      Engine: redis
      CacheNodeType: cache.t4g.small
      NumCacheClusters: 2
      AutomaticFailoverEnabled: true
      MultiAZEnabled: true
      AtRestEncryptionEnabled: true
      TransitEncryptionEnabled: true
      CacheSubnetGroupName: !Ref Subnets
      SecurityGroupIds: [!Ref CacheSgId]
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Resource | Replication group | Azure Cache for Redis instance |
| Network | Subnet group + SG | VNet injection or Private Endpoint |
| HA | Multi-AZ + auto failover | Standard/Premium tier replicas, zone redundancy |
| Pricing | Node-hours (approximate - check current docs) | Tier/size (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Connecting without TLS to a TLS-enabled cluster.
✅ Correct: Set `tls: {}` in ioredis / `ssl=True` in redis-py.

❌ Mistake: Trying to reach ElastiCache from your laptop.
✅ Correct: It has no public access; use SSM port-forward or VPN.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Which port does Redis use?
A1: 6379.

Q2: [Medium] Why use a replication group?
A2: Replicas give failover and read scaling.

Q3: [Hard] App cannot connect after enabling TLS. Debug?
A3: TLS must be enabled in the client, endpoint DNS used, SG allows 6379, and the app is in the same VPC or peered network.

---

## ✅ Quick Checklist
□ Private subnet group
□ Encryption at rest and in transit
□ Primary and reader endpoints used correctly

---

## ⚡ 1-Line Summary
Redis in prod = replication group, Multi-AZ, TLS, private network. | प्रोडक्शन Redis = रेप्लिकेशन ग्रुप, मल्टी-AZ, TLS, प्राइवेट नेटवर्क।

## ➡️ Next: ElastiCache Cluster Mode

---
