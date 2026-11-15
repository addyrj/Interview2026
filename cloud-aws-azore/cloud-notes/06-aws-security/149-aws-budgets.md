# 149. AWS Budgets
# AWS: AWS Budgets
# Azure: Cost Management Budgets
# हिंदी में: बजट्स - खर्च की सीमा तय करो और पार होने से पहले अलर्ट पाओ

---

## 🔵 Simple Definition
Budgets lets you set cost or usage thresholds and sends alerts (email/SNS) on actual or forecasted breach; it can also trigger actions.
हिंदी: महीने का बजट तय करें, सीमा पास आने पर ईमेल या SNS अलर्ट मिलता है।

## 🔴 Why it Exists
A forgotten GPU instance can burn thousands. Alerts catch it before the invoice.

## 🟢 How it Works
```
Budget (monthly $50, filter tag/service)
   |-- 80% ACTUAL     --> email
   |-- 100% FORECASTED --> SNS --> Slack
   |-- (optional) Budget Action: attach deny IAM/SCP policy
```

## 💻 Code / Config Example
```yaml
# CloudFormation
Resources:
  MonthlyBudget:
    Type: AWS::Budgets::Budget
    Properties:
      Budget:
        BudgetName: monthly-50usd
        BudgetType: COST
        TimeUnit: MONTHLY
        BudgetLimit: { Amount: 50, Unit: USD }
      NotificationsWithSubscribers:
        - Notification:
            NotificationType: FORECASTED
            ComparisonOperator: GREATER_THAN
            Threshold: 100
            ThresholdType: PERCENTAGE
          Subscribers:
            - { SubscriptionType: EMAIL, Address: me@example.com }
```

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | AWS Budgets | Cost Management budgets |
| Alerts | Email, SNS, Chatbot | Action groups, email |
| Automated action | Budget Actions (IAM/SCP/stop EC2/RDS) | Action group -> Automation/Logic App |
| Pricing | First budgets free; some paid after (check current docs) | Free |

## ⚠️ Common Mistakes
❌ Alert only at 100% actual. ✅ Add a forecasted alert and an 80% actual alert.
❌ Expecting a hard stop. ✅ Budgets alert; stopping needs Budget Actions.

## ⚫ Interview Q&A
Q1 [Easy]: Actual vs forecasted alert? A1: Actual = already spent; forecasted = predicted to exceed.
Q2 [Medium]: Can a budget stop spend? A2: Via Budget Actions applying a restrictive policy or stopping instances.
Q3 [Hard]: Per-team budgets in one org? A3: Filter by cost-allocation tag or linked account, one budget per team.

## ✅ Quick Checklist
□ Forecast alert set
□ SNS to Slack
□ Per-project tag budgets

## ⚡ 1-Line Summary
Budgets warns you before you overspend | बजट्स खर्च बढ़ने से पहले चेतावनी देता है।

## ➡️ Next: Trusted Advisor
