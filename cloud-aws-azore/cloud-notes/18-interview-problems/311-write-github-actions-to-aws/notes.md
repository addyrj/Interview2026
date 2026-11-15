# 311. Write GitHub Actions → AWS
# AWS: IAM OIDC identity provider + IAM role + GitHub Actions
# Azure: Entra ID workload identity federation (federated credential) + azure/login
# हिंदी में: GitHub Actions से AWS में बिना लंबी-अवधि वाली access key के, OIDC से लॉगिन

---

## 🔵 Simple Definition
GitHub issues a short-lived OIDC token per job; AWS STS exchanges it for temporary credentials of a role whose trust policy matches your repo and branch.
हिंदी: कोई secret key स्टोर नहीं, हर जॉब को अस्थायी क्रेडेंशियल मिलते हैं।

## 🔴 Why it Exists
Static IAM user keys in GitHub secrets leak, never rotate and are over-privileged.

## 🟢 How it Works
```
Job (permissions: id-token: write) -> GitHub OIDC token (sub=repo:org/repo:ref:refs/heads/main)
  -> configure-aws-credentials -> sts:AssumeRoleWithWebIdentity
  -> IAM role trust policy checks aud + sub -> 1h temp creds -> ECR push / ECS deploy
```

## 💻 Code / Config Example
Files: `oidc.tf` (provider + role), `trust-policy.json` (same trust as JSON), `permissions-policy.json` (ECR push + ECS deploy + PassRole on two roles), `workflow.yml` (test, then gated deploy job). Replace account ID, org/repo, names. Not run against AWS.

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Trust setup | OIDC provider + role trust policy | App registration federated credential |
| Login action | aws-actions/configure-aws-credentials | azure/login |
| Scoping | `sub` claim (repo/branch/environment) | subject (repo/branch/environment) |
| Pricing | free | free |

## 💰 Cost / HA / Security
- Cost: free; use `cache` and `concurrency` to save runner minutes.
- HA: run deploys serialised per environment; rollback by re-deploying a previous SHA.
- Security: pin `sub` to repo and branch/environment (never `repo:org/*` loosely), least-privilege permissions, protect `production` environment with reviewers, pin third-party actions by SHA for high-risk repos.

## ⚠️ Common Mistakes
❌ Trust policy without a `sub` condition: any repo on GitHub could assume the role.
✅ Match `aud` and exact `sub`.

❌ Forgetting `permissions: id-token: write`.
✅ Set it on the deploy job only.

## ⚫ Interview Q&A
Q1 [Easy]: Why OIDC instead of access keys?
A1: Credentials are short-lived and scoped by token claims, nothing long-lived to leak.

Q2 [Medium]: Which claims should the trust policy check?
A2: `aud = sts.amazonaws.com` and `sub` such as `repo:org/repo:ref:refs/heads/main` or `repo:org/repo:environment:production`.

Q3 [Hard]: A pull request from a fork must not deploy; how?
A3: Deploy only on push to main/protected environments; fork PRs get no id-token and the trust `sub` does not match PR refs.

## ✅ Quick Checklist
□ OIDC provider created once
□ Trust policy pinned to repo + ref
□ Role permissions minimal

## ⚡ 1-Line Summary
Short-lived OIDC role instead of stored keys. | स्टोर की गई keys की जगह अस्थायी OIDC रोल।

## ➡️ Next: 312. Setup CloudWatch Alarms
