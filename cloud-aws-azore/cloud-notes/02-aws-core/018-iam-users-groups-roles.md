---

# 18. IAM Users + Groups + Roles
# AWS: IAM users, groups, roles, instance profiles
# Azure: Entra users, groups, Managed Identities / Service Principals
# हिंदी में: यूज़र = इंसान, ग्रुप = यूज़र्स का समूह, रोल = अस्थायी पहचान

---

## 🔵 Simple Definition (2 lines)
A user is a long-lived identity, a group bundles users for shared permissions, and a role is an assumable identity that gives temporary credentials.
हिंदी: यूज़र स्थायी पहचान है, ग्रुप में परमिशन बाँटते हैं, और रोल अस्थायी क्रेडेंशियल देने वाली पहचान है।

---

## 🔴 Why it Exists (2 lines)
Long-lived keys leak; per-user permissions are hard to manage.
Groups simplify management and roles remove static secrets for apps and cross-account access.

---

## 🟢 How it Works
```
Group "devs" --policy--> members: alice, bob (users)
Role "api-task-role"
   Trust policy : WHO may assume (ecs-tasks.amazonaws.com)
   Permission policy: WHAT it can do (read S3 bucket)
App on ECS/EC2/Lambda -> sts:AssumeRole -> temp creds (auto-rotated)
Groups cannot be a Principal in policies and cannot be nested.
```

---

## 💻 Code / Config Example
```bash
# Create group, user, add user, attach managed policy
aws iam create-group --group-name devs
aws iam create-user --user-name alice
aws iam add-user-to-group --group-name devs --user-name alice
aws iam attach-group-policy --group-name devs \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# Role for an ECS task (trust policy)
cat > trust.json <<'EOF'
{"Version":"2012-10-17","Statement":[{"Effect":"Allow",
 "Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]}
EOF
aws iam create-role --role-name api-task-role --assume-role-policy-document file://trust.json
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Human identity | IAM user / Identity Center user | Entra user |
| Grouping | IAM group | Entra group |
| Workload identity | IAM role | Managed Identity (system/user-assigned) |
| Cross-tenant/account | AssumeRole across accounts | Guest users / Lighthouse / service principal |

---

## ⚠️ Common Mistakes
❌ Mistake: Creating IAM users with access keys for apps.
✅ Correct: Use roles; for CI use GitHub OIDC to assume a role.

❌ Mistake: Confusing ECS task role and task execution role.
✅ Correct: Execution role pulls image/logs; task role is what your code uses.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Why use groups?
A1: To assign permissions once to many users.

Q2: [Medium] Trust policy vs permission policy?
A2: Trust policy says who can assume the role; permission policy says what the role can do.

Q3: [Hard] Give GitHub Actions deploy access without stored keys.
A3: Create an OIDC identity provider for token.actions.githubusercontent.com and a role whose trust policy conditions on sub (repo/branch); workflow uses aws-actions/configure-aws-credentials with role-to-assume.

---

## ✅ Quick Checklist
□ Humans via groups or SSO
□ Apps via roles only
□ Trust policies scoped with conditions

---

## ⚡ 1-Line Summary
Users for people, groups for sharing, roles for temporary workloads | इंसान के लिए यूज़र, बाँटने को ग्रुप, ऐप्स के लिए रोल।

## ➡️ Next: 19. IAM Policies

---
