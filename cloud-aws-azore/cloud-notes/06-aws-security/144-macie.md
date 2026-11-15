# 144. Macie
# AWS: Amazon Macie
# Azure: Microsoft Purview (data classification) + Defender for Storage (sensitive data discovery)
# हिंदी में: मैसी - S3 में रखे संवेदनशील डेटा (PII) को पहचानता है

---

## 🔵 Simple Definition
Macie scans S3 buckets with ML and pattern matching to find sensitive data such as names, card numbers and credentials, and flags public or unencrypted buckets.
हिंदी: यह S3 में पर्सनल या गोपनीय डेटा ढूँढकर बताता है कि कहाँ रखा है।

## 🔴 Why it Exists
Teams dump CSV exports into S3 and forget them. Compliance (GDPR, PCI) requires knowing where PII lives.

## 🟢 How it Works
```
S3 buckets --> Macie inventory (bucket-level policy/encryption checks)
      |
   Discovery job (managed + custom identifiers)
      |
   Findings: SensitiveData:S3Object/Personal --> Security Hub / EventBridge
```

## 💻 Code / Config Example
```bash
# Enable Macie and run a one-time classification job (AWS CLI v2, macie2)
aws macie2 enable-macie
aws macie2 create-classification-job \
  --job-type ONE_TIME --name scan-uploads \
  --s3-job-definition '{"bucketDefinitions":[{"accountId":"111122223333","buckets":["my-user-uploads"]}]}'
```

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Macie | Purview + Defender for Storage |
| Scope | S3 only | Blob, SQL, many sources |
| Custom patterns | Custom data identifiers (regex) | Custom classifiers |
| Pricing | Bucket inventory + per GB scanned (check current docs) | Per plan (check current docs) |

## ⚠️ Common Mistakes
❌ Scanning huge buckets in full. ✅ Use sampling or scope by prefix; cost is per GB.
❌ Assuming it covers RDS/DynamoDB. ✅ Macie is S3-only.

## ⚫ Interview Q&A
Q1 [Easy]: What does Macie protect? A1: Sensitive data in S3.
Q2 [Medium]: How are findings used? A2: Sent to Security Hub/EventBridge; trigger Lambda to quarantine or restrict the object.
Q3 [Hard]: How to cut cost on petabytes? A3: Sampling depth, include/exclude by prefix or tag, scan only new objects with scheduled jobs.

## ✅ Quick Checklist
□ Block Public Access on
□ Scan jobs scoped
□ Findings routed to alerts

## ⚡ 1-Line Summary
Macie finds PII lying around in S3 | मैसी S3 में छिपा संवेदनशील डेटा खोजता है।

## ➡️ Next: VPC Flow Logs
