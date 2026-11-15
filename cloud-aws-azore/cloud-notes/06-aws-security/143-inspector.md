# 143. Inspector
# AWS: Amazon Inspector
# Azure: Microsoft Defender for Cloud (vulnerability assessment, Defender for Containers/Servers)
# हिंदी में: इंस्पेक्टर - सर्वर, कंटेनर इमेज और Lambda में कमजोरियाँ (CVE) खोजता है

---

## 🔵 Simple Definition
Inspector continuously scans EC2 instances, ECR container images and Lambda functions for known software vulnerabilities (CVEs) and network exposure.
हिंदी: यह अपने-आप जाँचता है कि आपके सर्वर या Docker इमेज में कोई पुरानी असुरक्षित लाइब्रेरी तो नहीं।

## 🔴 Why it Exists
New CVEs appear daily; manual scanning does not scale. Inspector rescans when a new CVE is published or a package changes.

## 🟢 How it Works
```
EC2 (SSM agent) / ECR push / Lambda code+deps
          |
      Inspector scan --> match against CVE database
          |
   Finding with risk score --> Security Hub / EventBridge
```

## 💻 Code / Config Example
```bash
# Enable scanning for EC2, ECR, Lambda (AWS CLI v2, inspector2)
aws inspector2 enable --resource-types EC2 ECR LAMBDA

# List critical findings
aws inspector2 list-findings \
  --filter-criteria '{"severity":[{"comparison":"EQUALS","value":"CRITICAL"}]}'
```
```dockerfile
# Fix findings in your Node image: use slim, pinned, patched base
FROM node:20-alpine
RUN apk upgrade --no-cache
```

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Inspector (v2) | Defender for Cloud / Defender for Containers |
| Image scan | ECR enhanced scanning | ACR image vulnerability scanning |
| VM scan | SSM agent based | Agent / agentless |
| Pricing | Per instance/image scanned (check current docs) | Per plan (check current docs) |

## ⚠️ Common Mistakes
❌ EC2 shows "unmanaged". ✅ SSM Agent and an instance profile are required.
❌ Scanning only at build. ✅ Continuous rescan catches CVEs published after deploy.

## ⚫ Interview Q&A
Q1 [Easy]: What does Inspector scan? A1: EC2, ECR images, Lambda functions.
Q2 [Medium]: Inspector vs GuardDuty? A2: Inspector finds vulnerabilities before attack; GuardDuty detects active threats.
Q3 [Hard]: How to block a vulnerable image deployment? A3: Use Inspector findings via EventBridge to fail the pipeline or tag the image, plus a CI gate on critical CVEs.

## ✅ Quick Checklist
□ SSM agent running on EC2
□ ECR enhanced scanning on
□ Critical CVEs gate the pipeline

## ⚡ 1-Line Summary
Inspector finds known CVEs in your servers, images and functions | इंस्पेक्टर पुरानी कमजोर लाइब्रेरी खोजकर बताता है।

## ➡️ Next: Macie
