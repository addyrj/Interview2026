# 73. DYNAMODB ON-DEMAND VS PROVISIONED
# AWS: DynamoDB capacity modes
# Azure: Cosmos DB serverless vs provisioned/autoscale throughput
# हिंदी में: ऑन-डिमांड बनाम प्रोविज़न्ड मोड

---

## 🔵 Simple Definition (2 lines)
On-demand charges per request with no capacity planning; provisioned charges for RCU/WCU you reserve, optionally auto-scaled.
हिंदी: ऑन-डिमांड में हर रिक्वेस्ट का पैसा लगता है; प्रोविज़न्ड में रिज़र्व किए RCU/WCU का।

---

## 🔴 Why it Exists (2 lines)
Unknown or spiky traffic needs elasticity; steady traffic wants the lowest unit price.
Two modes let you trade simplicity against cost.

---

## 🟢 How it Works
```
ON-DEMAND (PAY_PER_REQUEST)       PROVISIONED
 no planning, instant scaling      set RCU/WCU (+ Auto Scaling target ~70%)
 higher cost per request           lower cost if utilisation is steady/high
 good: new app, spiky, dev         good: predictable, 24x7 steady load
You can switch modes, but only about once per 24 hours (check docs)
```

---

## 💻 Code / Config Example
```yaml
# CloudFormation: on-demand table
AWSTemplateFormatVersion: "2010-09-09"
Resources:
  OrdersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: Orders
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - {AttributeName: userId, AttributeType: S}
        - {AttributeName: orderId, AttributeType: S}
      KeySchema:
        - {AttributeName: userId, KeyType: HASH}
        - {AttributeName: orderId, KeyType: RANGE}
      # For provisioned use: BillingMode: PROVISIONED plus
      # ProvisionedThroughput: {ReadCapacityUnits: 5, WriteCapacityUnits: 5}
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Pay-per-request | On-demand | Cosmos DB serverless |
| Reserved throughput | Provisioned (+ Auto Scaling) | Provisioned / Autoscale RU/s |
| Discounts | Reserved capacity for provisioned | Reserved capacity |
| Pricing | Approximate - check current docs | Approximate - check current docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Provisioned with tiny capacity for a spiky app, so throttles.
✅ Correct: Use on-demand or Auto Scaling with headroom.

❌ Mistake: On-demand forever for a huge steady workload.
✅ Correct: Review monthly; move to provisioned when usage is predictable.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Default choice for a new app?
A1: On-demand, since traffic is unknown and ops effort is zero.

Q2: [Medium] When is provisioned cheaper?
A2: Steady, predictable, well-utilised load, especially with reserved capacity.

Q3: [Hard] Can on-demand still throttle?
A3: Yes; it has per-partition limits, and a sudden jump far beyond previous peak or a hot key can throttle until it adapts.

---

## ✅ Quick Checklist
□ Traffic profile known?
□ Billing alarm on
□ Mode reviewed monthly

---

## ⚡ 1-Line Summary
On-demand = simple and elastic; provisioned = cheaper for steady load. | ऑन-डिमांड = सरल और लचीला; प्रोविज़न्ड = स्थिर लोड पर सस्ता।

## ➡️ Next: DynamoDB GSI + LSI

---
