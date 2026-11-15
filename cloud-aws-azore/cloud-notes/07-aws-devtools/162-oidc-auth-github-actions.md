# 162. OIDC Auth for GitHub Actions
# AWS: IAM OIDC identity provider + AssumeRoleWithWebIdentity
# Azure: Entra ID app registration + federated credentials
# हिंदी में: बिना password/key के GitHub से AWS login

---

## 🔵 Simple Definition
GitHub issues a short-lived signed JWT per workflow run; AWS trusts it and exchanges it for temporary role credentials.
हिंदी: GitHub एक अस्थायी token देता है, AWS उसे मानकर temporary credentials दे देता है, कोई secret key नहीं।

---

## 🔴 Why it Exists
Static access keys in secrets leak, never rotate and are over-privileged.
OIDC gives credentials that expire (default about 1 hour) and are bound to a specific repo/branch.

---

## 🟢 How it Works
```
workflow (id-token: write)
  -> asks GitHub OIDC (token.actions.githubusercontent.com) for JWT
  -> calls sts:AssumeRoleWithWebIdentity with JWT + role ARN
  -> AWS checks trust policy: issuer, aud=sts.amazonaws.com, sub=repo:ORG/REPO:ref:...
  -> returns temp creds -> aws cli/sdk works
```

---

## 💻 Code / Config Example
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:my-org/my-api:ref:refs/heads/main"
      }
    }
  }]
}
```
```bash
# one-time: create the OIDC provider (thumbprint no longer required by AWS for GitHub)
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com
```
```yaml
# in workflow: permissions: id-token: write
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789012:role/gha-deploy
    aws-region: ap-south-1
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Trust object | IAM OIDC provider + role trust policy | App registration federated credential |
| Subject match | `sub` condition | Federated credential subject (repo/branch/environment) |
| Login step | configure-aws-credentials | azure/login with client-id, tenant-id, subscription-id |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: `sub` condition missing or `repo:my-org/*:*` — any repo in the org can assume the role.
✅ Correct: Pin to exact repo and branch/environment.

❌ Mistake: Forgetting `permissions: id-token: write`.
✅ Correct: Add it at job or workflow level, otherwise "Could not load credentials".

---

## ⚫ Interview Q&A
Q1: [Easy] Why OIDC over access keys?
A1: Short-lived, no secrets to store or rotate.

Q2: [Medium] Which claims should the trust policy check?
A2: `aud` = sts.amazonaws.com and `sub` restricted to repo and ref or environment.

Q3: [Hard] How do you give prod deploy only to approved runs?
A3: Use a GitHub Environment `production` with reviewers and set `sub` to `repo:ORG/REPO:environment:production`.

---

## ✅ Quick Checklist
□ OIDC provider created once per account
□ Trust policy has aud and sub
□ Role policy is least privilege

---

## ⚡ 1-Line Summary
OIDC swaps a GitHub JWT for temporary AWS credentials | OIDC में GitHub का JWT देकर AWS से temporary credentials मिलते हैं।

## ➡️ Next: 163. Deploying Node.js to ECS
