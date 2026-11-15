# 66. RDS SECURITY GROUPS
# AWS: VPC Security Groups + private subnets for RDS
# Azure: Firewall rules, VNet integration (delegated subnet), Private Endpoint, NSG
# हिंदी में: RDS तक सिर्फ़ आपका ऐप पहुँचे

---

## 🔵 Simple Definition (2 lines)
A security group is a stateful virtual firewall; for RDS you allow the DB port only from your app's security group.
हिंदी: सिक्योरिटी ग्रुप स्टेटफ़ुल फ़ायरवॉल है; RDS पर DB पोर्ट सिर्फ़ ऐप के सिक्योरिटी ग्रुप से खोलें।

---

## 🔴 Why it Exists (2 lines)
Databases exposed to 0.0.0.0/0 get scanned and breached within hours.
SG-to-SG rules keep access tied to identity, not IPs that change.

---

## 🟢 How it Works
```
Internet X-----> (blocked)
ALB --> App SG (ECS/EC2) --5432--> DB SG  [inbound: TCP 5432 from App SG only]
                                     |
                              RDS in PRIVATE subnets, publicly-accessible = false
Ports: PostgreSQL 5432, MySQL/MariaDB 3306, SQL Server 1433, Oracle 1521
```

---

## 💻 Code / Config Example
```yaml
# CloudFormation: DB SG that only trusts the app SG
AWSTemplateFormatVersion: "2010-09-09"
Parameters:
  VpcId: {Type: "AWS::EC2::VPC::Id"}
Resources:
  AppSG:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: App tier
      VpcId: !Ref VpcId
  DbSG:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: RDS Postgres
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref AppSG
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Network control | Security group on the DB | Server firewall rules / NSG on delegated subnet |
| Private access | Private subnet, no public IP | VNet integration or Private Endpoint |
| Rule source | Another SG or CIDR | IP range or subnet |
| Pricing | Free | Private Endpoint has hourly + data charges (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Opening 5432 to 0.0.0.0/0 "just to test".
✅ Correct: Use SSM/bastion or SG-from-SG; keep publicly-accessible off.

❌ Mistake: Allowing a CIDR of the whole VPC.
✅ Correct: Reference the specific app SG.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Are security groups stateful?
A1: Yes, return traffic is allowed automatically.

Q2: [Medium] Why reference an SG instead of an IP?
A2: Instances scale and change IPs; SG membership follows them.

Q3: [Hard] How does your laptop reach a private RDS safely?
A3: SSM Session Manager port forwarding via a bastion, or VPN; never open the DB to the internet.

---

## ✅ Quick Checklist
□ DB in private subnets, not public
□ Inbound only from app SG
□ Encryption in transit (SSL) enforced

---

## ⚡ 1-Line Summary
Allow the DB port only from the app security group, never the internet. | DB पोर्ट सिर्फ़ ऐप के सिक्योरिटी ग्रुप से खोलें, इंटरनेट से कभी नहीं।

## ➡️ Next: Aurora - What + Why

---
