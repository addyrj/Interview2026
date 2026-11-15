---

# 270. AZURE REPOS (GIT)
# AWS: CodeCommit (closed to new customers 2024; most use GitHub)
# Azure: Azure Repos
# हिंदी में: एज़्योर रेपोज़ (गिट)

---

## 🔵 Simple Definition (2 lines)
Azure Repos hosts private Git repositories with pull requests, branch policies, code review and build validation.
हिंदी: Azure Repos प्राइवेट Git रेपो देता है जिसमें PR, रिव्यू और ब्रांच नियम होते हैं।

---

## 🔴 Why it Exists (2 lines)
Teams need access-controlled source hosting tied to work items and pipelines, inside the same Entra ID tenant.

---

## 🟢 How it Works
```
git push feature/login
   -> Pull Request into main
      -> Branch policy checks:
         min reviewers | linked work item | comment resolution
         | build validation (pipeline must pass) | merge strategy
   -> Complete PR -> main -> CI/CD pipeline triggers
```

---

## 💻 Code / Config Example
```bash
git clone https://dev.azure.com/acme/shop-api/_git/shop-api
cd shop-api && git checkout -b feature/login
git commit -am "feat: login" && git push -u origin feature/login

# Create PR from the CLI
az repos pr create --source-branch feature/login --target-branch main \
  --title "feat: login" --work-items 123

# Protect main: 2 reviewers
REPO=$(az repos show --repository shop-api --query id -o tsv)
az repos policy approver-count create --blocking true --enabled true \
  --branch main --repository-id "$REPO" \
  --minimum-approver-count 2 --creator-vote-counts false \
  --allow-downvotes false --reset-on-source-push true
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Git hosting | CodeCommit (legacy) | Repos |
| Code review | PR + approval rules | PR + branch policies |
| Mirror to GitHub | Possible | Possible; Pipelines also work with GitHub repos |
| Pricing | Per active user | Included with Azure DevOps plan |

---

## ⚠️ Common Mistakes
❌ Mistake: Pushing straight to main.
✅ Correct: Branch policy requiring PR, reviewers and passing build.

❌ Mistake: Committing .env or secrets.
✅ Correct: Use Key Vault, secret scanning, and rewrite history if leaked and rotate the secret.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is a branch policy?
A1: Rules on a branch like required reviewers and build validation before merge.

Q2: [Medium] Merge strategies?
A2: Merge commit, squash, rebase and fast-forward, rebase with merge; choose to keep history clean.

Q3: [Hard] Migrate from Azure Repos to GitHub?
A3: `git clone --mirror` then push `--mirror` to GitHub, re-create policies as branch protection, move pipelines to Actions, remap work-item links.

---

## ✅ Quick Checklist
□ main protected
□ Build validation enabled
□ CODEOWNERS-style required reviewers

---

## ⚡ 1-Line Summary
Azure Repos = private Git with enforceable PR rules | Azure Repos = नियमों वाला प्राइवेट Git।

## ➡️ Next: Azure Pipelines (CI/CD)

---
