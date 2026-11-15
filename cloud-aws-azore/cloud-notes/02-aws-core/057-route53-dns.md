# 57. Route 53 — DNS
# AWS: Amazon Route 53
# Azure: Azure DNS (+ Traffic Manager for routing)
# हिंदी में: डोमेन नाम को IP/सर्विस से जोड़ने वाली DNS सर्विस

---

## 🔵 Simple Definition (2 lines)
Route 53 is AWS's highly available DNS: hosted zones hold records that map names to IPs or AWS resources, and it can also register domains.
Route 53 = डोमेन (api.example.com) को सर्वर/ALB/CloudFront से जोड़ने वाली DNS सर्विस।

---

## 🔴 Why it Exists (2 lines)
Users need names, not IPs, and resources like ALBs change IPs.
Route 53 gives reliable DNS with health-aware routing and native AWS integration.

---

## 🟢 How it Works
```
Browser -> resolver -> Route 53 (hosted zone example.com)
  A      api.example.com   -> 1.2.3.4
  CNAME  www               -> app.example.com   (not allowed at zone apex)
  ALIAS  example.com       -> d123.cloudfront.net / ALB  (free, works at apex)
  TXT, MX, NS, SOA ...
Public zone (internet) vs Private zone (inside VPC)
```

---

## 💻 Code / Config Example
```bash
# Upsert an alias A record pointing to an ALB (AWS CLI v2)
cat > change.json <<'EOF'
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "api.example.com",
      "Type": "A",
      "AliasTarget": {
        "HostedZoneId": "Z35SXDOTRQ7X7K",
        "DNSName": "myalb-123.ap-south-1.elb.amazonaws.com",
        "EvaluateTargetHealth": true
      }
    }
  }]
}
EOF
aws route53 change-resource-record-sets --hosted-zone-id Z0123456789EXAMPLE --change-batch file://change.json
# AliasTarget.HostedZoneId is the ALB's zone ID for its Region (look up in docs)
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| DNS hosting | Route 53 hosted zones | Azure DNS zones |
| Apex to service | Alias record | Alias record set |
| Domain registration | Yes | App Service Domains (limited) / third party |
| Pricing | per zone/month + queries (approximate — check current docs) | per zone + queries (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: CNAME at the root domain.
✅ Correct: Use Alias A/AAAA.

❌ Mistake: High TTL before a migration.
✅ Correct: Lower TTL (60s) beforehand, raise after.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] A vs CNAME vs Alias?
A1: A -> IP; CNAME -> another name; Alias -> AWS resource, free queries, works at apex.

Q2: [Medium] Public vs private hosted zone?
A2: Public answers the internet; private answers only associated VPCs.

Q3: [Hard] Domain registered elsewhere, DNS in Route 53?
A3: Create hosted zone, then set the registrar's nameservers to the 4 NS records Route 53 gives.

---

## ✅ Quick Checklist
□ NS delegated at registrar
□ Alias for apex
□ TTLs planned
□ Private zone for internal names

---

## ⚡ 1-Line Summary
Route 53 maps domain names to your services reliably. | Route 53 डोमेन नाम को आपकी सर्विस से जोड़ता है।

## ➡️ Next: Route 53 Routing Policies
