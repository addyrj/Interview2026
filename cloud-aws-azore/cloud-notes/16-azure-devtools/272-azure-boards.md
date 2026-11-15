---

# 272. AZURE BOARDS
# AWS: N/A (no native equivalent; closest: Jira / third-party)
# Azure: Azure Boards
# हिंदी में: एज़्योर बोर्ड्स

---

## 🔵 Simple Definition (2 lines)
Azure Boards tracks work items (epics, features, user stories, bugs, tasks) with backlogs, Kanban boards and sprints.
हिंदी: Boards में काम (stories, bugs, tasks) का बैकलॉग, कानबन और स्प्रिंट मैनेज होता है।

---

## 🔴 Why it Exists (2 lines)
Teams need traceability from requirement to commit to release. Boards links work items to PRs and deployments.

---

## 🟢 How it Works
```
Process template: Agile | Scrum | Basic | CMMI
Epic -> Feature -> User Story -> Task (+ Bug)
Backlog -> Sprint (iteration path) -> Kanban columns
Link: commit message "Fixes AB#123" or PR link -> auto-close on merge
Dashboards: velocity, burndown, cumulative flow
```

---

## 💻 Code / Config Example
```bash
az boards work-item create --type "User Story" \
  --title "Login with OTP" --assigned-to dev@example.com \
  --iteration "shop-api\\Sprint 5"

# Query active bugs with WIQL
az boards query --wiql "SELECT [System.Id],[System.Title] FROM WorkItems WHERE [System.WorkItemType]='Bug' AND [System.State]<>'Closed'" -o table

# Link commit to work item by message
git commit -m "fix: otp retry limit Fixes AB#123"
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Work tracking | N/A (AWS-only gap; use Jira) | Boards |
| Git integration | Third-party | Native AB# links |
| Reporting | Third-party | Dashboards, Analytics views |
| Pricing | N/A | Basic plan free for first 5 users (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Work items not linked to commits/PRs.
✅ Correct: Require linked work item in branch policy.

❌ Mistake: Huge tasks with no estimate.
✅ Correct: Break into tasks of 1-2 days and track remaining work.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Hierarchy of work items?
A1: Epic > Feature > User Story/PBI > Task, bugs alongside.

Q2: [Medium] Agile vs Scrum template?
A2: Agile uses User Story; Scrum uses Product Backlog Item and Committed states.

Q3: [Hard] How do you measure delivery from Boards?
A3: Use cycle time and lead time widgets, cumulative flow, and link deployments to work items for DORA-style metrics.

---

## ✅ Quick Checklist
□ Process template chosen at start
□ Work items linked to PRs
□ Sprint dates and capacity set

---

## ⚡ 1-Line Summary
Boards = backlog, sprints and traceable work items | Boards = काम का हिसाब और ट्रैकिंग।

## ➡️ Next: Azure Artifacts

---
