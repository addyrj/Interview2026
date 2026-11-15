---

# 20. IAM Best Practices
# AWS: IAM Access Analyzer, Credential Report, Identity Center, CloudTrail
# Azure: Entra Conditional Access, PIM, Managed Identity, Access Reviews
# हिंदी में: IAM की सुरक्षित आदतें: कम परमिशन, MFA, रोल, नियमित समीक्षा

---

## 🔵 Simple Definition (2 lines)
A set of habits to keep identities safe: least privilege, MFA, temporary credentials, no root use, and continuous review.
हिंदी: कम-से-कम परमिशन, MFA, अस्थायी क्रेडेंशियल और हर कुछ समय पर ऑडिट।

---

## 🔴 Why it Exists (2 lines)
Most cloud breaches begin with leaked keys or over-broad permissions.
Good hygiene shrinks blast radius and speeds incident response.

---

## 🟢 How it Works
```
1 Root: MFA, no keys, locked away
2 Humans: SSO (Identity Center) + MFA, no long-lived keys
3 Workloads: roles (instance/task/Lambda) or OIDC for CI
4 Least privilege: start narrow, use Access Analyzer to refine
5 Guardrails: SCPs / permission boundaries
6 Rotate / delete unused keys and users (credential report)
7 Log + alert: CloudTrail, GuardDuty
8 Secrets: Secrets Manager / Parameter Store, never in Git
```

---

## 💻 Code / Config Example
```yaml
# GitHub Actions: deploy to AWS with OIDC, no stored keys
name: deploy
on: { push: { branches: [main] } }
permissions:
  id-token: write      # needed to request the OIDC token
  contents: read
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-deploy
          aws-region: ap-south-1
      - run: aws sts get-caller-identity
```
```bash
# Find stale credentials
aws iam generate-credential-report
aws iam get-credential-report --query Content --output text | base64 -d | head
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| MFA/conditional access | MFA, policy conditions | Conditional Access (P1) |
| Just-in-time admin | Temporary role sessions | Privileged Identity Management (P2) |
| Unused access finder | Access Analyzer | Access Reviews |
| Pricing | Mostly free; GuardDuty paid (check docs) | Some features need P1/P2 (check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Committing .env or access keys to GitHub.
✅ Correct: Use OIDC or a secret manager; enable secret scanning and rotate any leaked key at once.

❌ Mistake: Never reviewing permissions after project ends.
✅ Correct: Quarterly access review and delete unused identities.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is least privilege?
A1: Grant only the permissions needed for the task.

Q2: [Medium] How handle an exposed access key?
A2: Deactivate, review CloudTrail for misuse, rotate, remove from history, replace with role-based access.

Q3: [Hard] Secure CI/CD access across accounts.
A3: OIDC federation per repo/branch to a role in each account, narrow policies, SCP guardrails, approval for prod, short session duration, CloudTrail alerts on role assumption.

---

## ✅ Quick Checklist
□ MFA everywhere, root locked
□ No long-lived keys in code or CI
□ Access Analyzer and credential report reviewed

---

## ⚡ 1-Line Summary
Least privilege, MFA, roles over keys, review often | कम परमिशन, MFA, कीज़ की जगह रोल, और नियमित समीक्षा।

## ➡️ Next: 21. (next topic in the list)

---
