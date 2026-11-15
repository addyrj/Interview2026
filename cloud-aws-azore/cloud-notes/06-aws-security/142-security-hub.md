# 142. Security Hub
# AWS: AWS Security Hub
# Azure: Microsoft Defender for Cloud (secure score + regulatory compliance)
# हिंदी में: सिक्योरिटी हब - सारे सुरक्षा अलर्ट और कंप्लायंस जाँच एक जगह

---

## 🔵 Simple Definition
Security Hub aggregates findings from GuardDuty, Inspector, Macie and others, and runs automated best-practice checks (e.g. CIS, AWS Foundational Security Best Practices).
हिंदी: यह अलग-अलग सुरक्षा सेवाओं के नतीजे एक डैशबोर्ड में दिखाता है और नियमों की जाँच करता है।

## 🔴 Why it Exists
Many tools = many consoles. Teams need one prioritised view plus a standard format to automate fixes.

## 🟢 How it Works
```
GuardDuty  Inspector  Macie  Config  3rd-party
     \        |         |      |      /
      +--- Security Hub (ASFF format) ---+
                 |            |
         Security standards   EventBridge --> ticket / Lambda
         (checks via Config)
```

## 💻 Code / Config Example
```bash
# Enable with the default standards (AWS CLI v2)
aws securityhub enable-security-hub --enable-default-standards

# Show failed critical findings
aws securityhub get-findings \
  --filters '{"SeverityLabel":[{"Value":"CRITICAL","Comparison":"EQUALS"}],"ComplianceStatus":[{"Value":"FAILED","Comparison":"EQUALS"}]}' \
  --max-items 10
```

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Security Hub | Defender for Cloud |
| Score | Security score per standard | Secure Score |
| Standards | CIS, PCI DSS, AWS FSBP | CIS, PCI, ISO via regulatory compliance |
| Pricing | Per check and per finding ingested (check current docs) | Free CSPM tier; paid plans extra (check current docs) |

## ⚠️ Common Mistakes
❌ Enabling Security Hub without AWS Config recording. ✅ Config must be on, or checks cannot run.
❌ Chasing every Low finding. ✅ Triage Critical/High first, suppress accepted risks.

## ⚫ Interview Q&A
Q1 [Easy]: What is ASFF? A1: AWS Security Finding Format, the common JSON schema for findings.
Q2 [Medium]: Difference from GuardDuty? A2: GuardDuty detects threats; Security Hub aggregates and checks configuration compliance.
Q3 [Hard]: How to centralise multi-account/multi-region? A3: Delegated admin in Organizations plus a finding aggregator region.

## ✅ Quick Checklist
□ AWS Config enabled
□ Standards chosen (FSBP, CIS)
□ Findings automated to tickets/Slack

## ⚡ 1-Line Summary
Security Hub is the single pane for security findings | सिक्योरिटी हब सुरक्षा का एक ही कंट्रोल पैनल है।

## ➡️ Next: Inspector
