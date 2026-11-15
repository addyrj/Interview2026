# 150. Trusted Advisor
# AWS: AWS Trusted Advisor
# Azure: Azure Advisor
# हिंदी में: ट्रस्टेड एडवाइज़र - लागत, सुरक्षा और प्रदर्शन सुधार की सलाह

---

## 🔵 Simple Definition
Trusted Advisor inspects your account against best practices and gives recommendations across cost, performance, security, fault tolerance, service limits and operational excellence.
हिंदी: यह आपके अकाउंट को जाँचकर बताता है कि कहाँ पैसा बचाएँ और कहाँ सुरक्षा सुधारें।

## 🔴 Why it Exists
Idle load balancers, open security groups, unattached EBS volumes are easy to miss. It surfaces them automatically.

## 🟢 How it Works
```
Account resources --> Trusted Advisor checks
   Cost | Performance | Security | Fault tolerance | Service limits
   Basic/Developer support: limited core checks
   Business/Enterprise: full checks + API
```

## 💻 Code / Config Example
```bash
# Needs Business/Enterprise support plan for the Support API (AWS CLI v2, us-east-1)
aws support describe-trusted-advisor-checks --language en --region us-east-1 \
  --query 'checks[?category==`cost_optimizing`].[id,name]'

# Newer API: trustedadvisor
aws trustedadvisor list-recommendations --region us-east-1
```

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Trusted Advisor | Azure Advisor |
| Free tier | Limited core checks | Full recommendations free |
| Categories | Cost, perf, security, FT, limits | Cost, security, reliability, ops excellence, performance |
| API access | Needs paid support plan | Available without extra plan |

## ⚠️ Common Mistakes
❌ Expecting all checks on free plan. ✅ Full set needs Business or Enterprise support.
❌ Ignoring service limit checks. ✅ Act at about 80% of quotas before outages.

## ⚫ Interview Q&A
Q1 [Easy]: What does it recommend? A1: Cost, security, performance, fault tolerance, limits.
Q2 [Medium]: Trusted Advisor vs Security Hub? A2: TA gives broad best-practice advice; Security Hub is a dedicated compliance/finding aggregator.
Q3 [Hard]: How to automate responses? A3: EventBridge events from TA check status changes trigger Lambda or notifications (needs supported plan).

## ✅ Quick Checklist
□ Review monthly
□ Open SG ports fixed
□ Idle resources removed

## ⚡ 1-Line Summary
Trusted Advisor = AWS's built-in account health check | ट्रस्टेड एडवाइज़र अकाउंट का हेल्थ चेकअप है।

## ➡️ Next: CodeCommit
