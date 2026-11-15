# 21. AWS CLI Setup
# AWS: AWS CLI v2 (`aws`)
# Azure: Azure CLI (`az`)
# हिंदी में: टर्मिनल से AWS को कंट्रोल करने का टूल

---

## 🔵 Simple Definition
The AWS CLI is a command-line tool that calls AWS APIs using your credentials, so you can script everything you can click in the console.
हिंदी: AWS CLI एक कमांड-लाइन टूल है जिससे आप टर्मिनल से AWS की हर सर्विस चला सकते हैं।

---

## 🔴 Why it Exists
Console clicks are slow and not repeatable. CLI gives scripting, CI/CD (GitHub Actions) and automation.

---

## 🟢 How it Works
```
aws <service> <command> --options
   |
   v
~/.aws/credentials + ~/.aws/config  (profile, region)
   |
   v
Signed (SigV4) HTTPS request -> AWS API endpoint of the region
```
Credential order: env vars -> profile -> SSO -> container/EC2 instance role.

---

## 💻 Code / Config Example
```bash
# Install on Linux VPS (v2)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip
unzip awscliv2.zip && sudo ./aws/install
aws --version

# Static keys (dev only) - prompts for key, secret, region, output
aws configure --profile dev
# Better: SSO (no long-lived keys)
aws configure sso

# Who am I? (first command to run when debugging)
aws sts get-caller-identity --profile dev

# Useful flags
aws ec2 describe-instances --region ap-south-1 \
  --query 'Reservations[].Instances[].[InstanceId,State.Name]' --output table
```
GitHub Actions: prefer OIDC role (`aws-actions/configure-aws-credentials`) over stored keys.

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| CLI | `aws` (v2) | `az` |
| Login | `aws configure` / `aws configure sso` | `az login` |
| Identity check | `aws sts get-caller-identity` | `az account show` |
| Multiple accounts | profiles (`--profile`) | subscriptions (`az account set`) |
| Output filter | `--query` (JMESPath) | `--query` (JMESPath) |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: Committing `~/.aws/credentials` or access keys in `.env`/Git.
✅ Correct: Use SSO, instance roles or GitHub OIDC; rotate any leaked key at once.

❌ Mistake: Forgetting region, so resources "vanish".
✅ Correct: Set `region` in the profile or pass `--region`.

---

## ⚫ Interview Q&A
Q1: [Easy] How do you check which AWS account the CLI uses?
A1: `aws sts get-caller-identity` shows account ID, user/role ARN.

Q2: [Medium] How does the CLI find credentials?
A2: Chain: CLI flags, env vars (`AWS_ACCESS_KEY_ID`), shared credentials/config file profile, SSO, then container/EC2 role metadata.

Q3: [Hard] How do you avoid long-lived keys in CI?
A3: GitHub OIDC provider in IAM, role with trust policy on the repo/branch, workflow gets short-lived STS credentials via AssumeRoleWithWebIdentity.

---

## ✅ Quick Checklist
□ CLI v2 installed, `aws --version` works
□ Using SSO/role, not root keys
□ Default region and profile set

---

## ⚡ 1-Line Summary
`aws` CLI scripts AWS via signed API calls; use profiles and SSO, never commit keys. | `aws` CLI से AWS ऑटोमेट होता है; प्रोफाइल/SSO इस्तेमाल करें, keys कभी commit न करें।

## ➡️ Next: AWS Regions + AZs
