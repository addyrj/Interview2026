# 145. VPC Flow Logs
# AWS: VPC Flow Logs
# Azure: NSG Flow Logs / VNet Flow Logs (Network Watcher)
# हिंदी में: फ्लो लॉग्स - नेटवर्क में आने-जाने वाले ट्रैफिक का रिकॉर्ड

---

## 🔵 Simple Definition
Flow Logs record metadata (source, destination, port, protocol, bytes, ACCEPT/REJECT) of IP traffic on a VPC, subnet or ENI. They do not capture packet contents.
हिंदी: यह बताता है कि कौन किस पोर्ट पर किससे जुड़ा और ट्रैफिक allow हुआ या reject, पर डेटा की सामग्री नहीं।

## 🔴 Why it Exists
To debug "why can't A reach B?", detect scanning, and feed security tools.

## 🟢 How it Works
```
ENI / Subnet / VPC --> Flow Log --> CloudWatch Logs | S3 | Firehose
record: version account eni src dst srcport dstport proto packets bytes start end action status
```

## 💻 Code / Config Example
```bash
# Send VPC flow logs to S3 (AWS CLI v2)
aws ec2 create-flow-logs \
  --resource-type VPC --resource-ids vpc-0abc1234 \
  --traffic-type ALL \
  --log-destination-type s3 \
  --log-destination arn:aws:s3:::my-flow-logs-bucket/vpc/
```
```sql
-- Athena: top rejected sources (table defined on flow log format)
SELECT srcaddr, count(*) c FROM vpc_flow_logs
WHERE action = 'REJECT' GROUP BY srcaddr ORDER BY c DESC LIMIT 10;
```

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | VPC Flow Logs | NSG / VNet Flow Logs |
| Destination | CloudWatch, S3, Firehose | Storage account, Log Analytics (Traffic Analytics) |
| Level | VPC, subnet, ENI | NSG or VNet |
| Note | Pay for log ingestion/storage | Azure announced NSG flow log retirement in favour of VNet flow logs (check current docs) |

## ⚠️ Common Mistakes
❌ Expecting payload capture. ✅ Use Traffic Mirroring for packets.
❌ Logging ALL to CloudWatch forever. ✅ Send to S3 with lifecycle expiry; costs grow fast.

## ⚫ Interview Q&A
Q1 [Easy]: What do flow logs contain? A1: Traffic metadata, not payloads.
Q2 [Medium]: SG allows but app unreachable - how to debug? A2: Check flow logs for ACCEPT/REJECT; REJECT points to NACL or SG; ACCEPT with no reply points to app or return path.
Q3 [Hard]: Does traffic to the DNS resolver or metadata IP appear? A3: No, some traffic (Amazon DNS, instance metadata, DHCP) is not logged.

## ✅ Quick Checklist
□ Destination S3 with lifecycle
□ Custom format has needed fields
□ Athena table ready

## ⚡ 1-Line Summary
Flow Logs show who talked to whom, not what they said | फ्लो लॉग्स बताते हैं कौन किससे जुड़ा, क्या बोला नहीं।

## ➡️ Next: AWS Organizations
