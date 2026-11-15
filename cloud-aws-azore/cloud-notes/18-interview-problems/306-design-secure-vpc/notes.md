# 306. Design Secure VPC
# AWS: VPC, subnets, SG, NACL, VPC endpoints, Flow Logs
# Azure: VNet, subnets, NSG, Private Endpoints/Service Endpoints, NSG flow logs
# हिंदी में: सुरक्षित VPC = प्राइवेट सबनेट, कम से कम अनुमति, और हर ट्रैफिक का लॉग

---

## 🔵 Simple Definition
A network with public, private and isolated subnet tiers, least-privilege security groups, private access to AWS services, and flow logs.
हिंदी: सिर्फ ज़रूरी चीज़ें पब्लिक, बाकी सब प्राइवेट, और हर कनेक्शन का रिकॉर्ड।

## 🔴 Why it Exists
Default-open networks lead to data exfiltration and lateral movement.

## 🟢 How it Works
```
Public subnets   : ALB, NAT          (route 0.0.0.0/0 -> IGW)
Private subnets  : app               (0.0.0.0/0 -> NAT; S3/ECR via endpoints)
Isolated subnets : DB                (no internet route)
SG  = stateful, allow-only, SG-to-SG       NACL = stateless backstop (deny known bad)
S3 gateway endpoint (free) + interface endpoints (ECR, Secrets Manager, Logs)
Flow Logs -> CloudWatch Logs / S3 ; admin access via SSM Session Manager (no SSH port)
```

## 💻 Code / Config Example
`vpc.tf` (provider ~> 5.x, not applied here): VPC, three subnet tiers, S3 gateway endpoint, Secrets Manager interface endpoint, flow logs with IAM role, default SG locked down. `s3-vpce-policy.json`: endpoint policy restricting S3 access to one bucket.

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Network | VPC | VNet |
| Firewall rules | SG (stateful), NACL (stateless) | NSG (stateful), Azure Firewall |
| Private PaaS access | VPC endpoints (PrivateLink) | Private Endpoint |
| Logs | VPC Flow Logs | NSG flow logs / VNet flow logs |
| Admin access | SSM Session Manager | Azure Bastion |

## 💰 Cost / HA / Security
- Cost: interface endpoints and NAT cost per hour + per GB (approximate - check current docs); the S3 gateway endpoint is free.
- HA: subnets in 2+ AZ, endpoints in each AZ.
- Security: no 0.0.0.0/0 ingress except ALB 443, IMDSv2, flow logs on, WAF at edge, GuardDuty.

## ⚠️ Common Mistakes
❌ SSH open to 0.0.0.0/0.
✅ SSM Session Manager, no inbound 22.

❌ Using the default VPC/default SG for production.
✅ Dedicated VPC; default SG with no rules.

## ⚫ Interview Q&A
Q1 [Easy]: SG vs NACL?
A1: SG is stateful at the ENI and allow-only; NACL is stateless at the subnet and supports allow and deny with numbered rules.

Q2 [Medium]: How can private instances reach S3 without internet?
A2: S3 gateway endpoint via route table entry; add an endpoint policy to limit buckets.

Q3 [Hard]: How would you detect and contain a compromised instance?
A3: Flow Logs/GuardDuty alert, swap its SG to an isolation SG (no ingress/egress), snapshot for forensics, rotate credentials the role had.

## ✅ Quick Checklist
□ Three subnet tiers
□ Endpoints for S3 and secrets
□ Flow logs enabled, default SG empty

## ⚡ 1-Line Summary
Segment, least-privilege, private endpoints, log everything. | सेगमेंट करें, कम अनुमति दें, सब लॉग करें।

## ➡️ Next: 307. Deploy Node.js to ECS
