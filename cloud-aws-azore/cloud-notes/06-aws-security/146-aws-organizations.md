# 146. AWS Organizations
# AWS: AWS Organizations
# Azure: Management Groups + Subscriptions (with Azure Policy)
# हिंदी में: ऑर्गनाइजेशंस - कई AWS अकाउंट्स को एक जगह से मैनेज करना

---

## 🔵 Simple Definition
Organizations lets you group many AWS accounts into a tree of Organizational Units (OUs), with consolidated billing and central policies (SCPs).
हिंदी: कई अकाउंट (dev, staging, prod) को एक संगठन में जोड़कर बिल और नियम एक जगह से चलाना।

## 🔴 Why it Exists
One account for everything is a blast-radius risk. Separate accounts isolate environments; Organizations makes that manageable.

## 🟢 How it Works
```
Root
 |-- Management account (billing only, no workloads)
 |-- OU: Security  --> log-archive, audit accounts
 |-- OU: Workloads
       |-- OU: Prod    --> prod-app account   (SCP: strict)
       |-- OU: NonProd --> dev, staging accounts
```

## 💻 Code / Config Example
```bash
# Create org and a new member account (AWS CLI v2)
aws organizations create-organization --feature-set ALL
aws organizations create-organizational-unit \
  --parent-id r-abcd --name Workloads
aws organizations create-account \
  --email dev@example.com --account-name dev-app
```

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Hierarchy | Root > OU > Account | Tenant root MG > MG > Subscription > Resource group |
| Guardrails | SCP | Azure Policy / RBAC deny assignments |
| Billing | Consolidated, volume discounts | Billing accounts / enrollments |
| Cost of feature | Organizations is free | Management groups free |

## ⚠️ Common Mistakes
❌ Running workloads in the management account. ✅ Keep it for billing/governance only.
❌ Only "Consolidated billing" feature set. ✅ Use feature set ALL to get SCPs.

## ⚫ Interview Q&A
Q1 [Easy]: Why multiple accounts? A1: Isolation, security boundaries, separate billing.
Q2 [Medium]: What is an OU? A2: A folder of accounts to which policies attach and inherit.
Q3 [Hard]: How is a new account bootstrapped consistently? A3: Control Tower / Account Factory or CloudFormation StackSets to deploy baseline roles, logging, GuardDuty.

## ✅ Quick Checklist
□ Management account empty of workloads
□ Prod and non-prod in separate accounts
□ MFA on root of every account

## ⚡ 1-Line Summary
Organizations = many accounts, one governance tree | ऑर्गनाइजेशंस कई अकाउंट्स को एक नियंत्रण वृक्ष में रखता है।

## ➡️ Next: Service Control Policies (SCP)
