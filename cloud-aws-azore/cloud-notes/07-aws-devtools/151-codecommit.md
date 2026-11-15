# 151. CodeCommit
# AWS: AWS CodeCommit
# Azure: Azure Repos
# हिंदी में: कोडकमिट - AWS का प्राइवेट Git रिपॉजिटरी

---

## 🔵 Simple Definition
CodeCommit is a managed, private Git hosting service integrated with IAM. Note: AWS stopped onboarding new customers in July 2024; availability has changed since, so check current docs before choosing it.
हिंदी: यह IAM से जुड़ा मैनेज्ड Git सर्वर है; नया प्रोजेक्ट शुरू करने से पहले इसकी वर्तमान स्थिति जरूर देखें।

## 🔴 Why it Exists
Keep source code inside your AWS account with IAM access control and no Git server to operate.

## 🟢 How it Works
```
git push --> CodeCommit repo (encrypted, IAM auth: HTTPS-GRC / SSH / credential helper)
                |
         event --> EventBridge / SNS / Lambda --> CodePipeline
```

## 💻 Code / Config Example
```bash
# Create repo and clone using IAM credentials (no passwords) - AWS CLI v2 + git-remote-codecommit
aws codecommit create-repository --repository-name my-api
pip install git-remote-codecommit
git clone codecommit::ap-south-1://my-api
```
```text
# Most teams just use GitHub with GitHub Actions + OIDC to AWS instead
# (your stack): no CodeCommit needed.
```

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | CodeCommit | Azure Repos |
| Auth | IAM | Entra ID / PAT |
| PRs | Basic, approval rules | Rich PR policies |
| Status | Closed to new customers in 2024 (verify current) | Active, part of Azure DevOps |

## ⚠️ Common Mistakes
❌ Picking CodeCommit for a new project without checking status. ✅ Prefer GitHub/GitLab.
❌ Using long-lived Git credentials. ✅ Use git-remote-codecommit with roles.

## ⚫ Interview Q&A
Q1 [Easy]: How does CodeCommit authenticate? A1: IAM (HTTPS credentials, SSH keys, or role-based helper).
Q2 [Medium]: How to trigger CI on push? A2: EventBridge rule on repository state change -> CodePipeline/CodeBuild.
Q3 [Hard]: How do you migrate off it? A3: `git clone --mirror`, push to the new remote, update webhooks and pipeline sources, rotate credentials.

## ✅ Quick Checklist
□ Check service availability first
□ Role-based auth only
□ Branch approval rules

## ⚡ 1-Line Summary
CodeCommit is AWS's IAM-integrated Git, now largely replaced by GitHub | कोडकमिट AWS का Git है, पर ज्यादातर टीमें अब GitHub चुनती हैं।

## ➡️ Next: CodeBuild
