---

# 271. AZURE PIPELINES (CI/CD)
# AWS: CodeBuild + CodePipeline + CodeDeploy
# Azure: Azure Pipelines
# हिंदी में: एज़्योर पाइपलाइन्स

---

## 🔵 Simple Definition (2 lines)
Azure Pipelines builds, tests and deploys code using YAML (azure-pipelines.yml) on Microsoft-hosted or self-hosted agents.
हिंदी: Pipelines YAML से कोड बिल्ड, टेस्ट और डिप्लॉय करती है।

---

## 🔴 Why it Exists (2 lines)
Manual deploys cause drift and mistakes. A pipeline makes every release repeatable, reviewed and auditable.

---

## 🟢 How it Works
```
trigger (push/PR/schedule)
  -> Pipeline
     -> Stage: Build   -> Job -> Steps (script/task)  on agent pool
     -> Stage: Deploy  -> deployment job -> Environment (approvals/checks)
  Artifacts published between stages
  Service connection -> Azure subscription
```

---

## 💻 Code / Config Example
```yaml
# azure-pipelines.yml : Node.js build + deploy to App Service
trigger:
  branches:
    include: [main]

pool:
  vmImage: ubuntu-latest

variables:
  appName: api-prod

stages:
  - stage: Build
    jobs:
      - job: build
        steps:
          - task: NodeTool@0
            inputs:
              versionSpec: '20.x'
          - script: |
              npm ci
              npm test
              npm run build
            displayName: Install, test, build
          - task: ArchiveFiles@2
            inputs:
              rootFolderOrFile: '$(System.DefaultWorkingDirectory)'
              includeRootFolder: false
              archiveFile: '$(Build.ArtifactStagingDirectory)/app.zip'
          - publish: '$(Build.ArtifactStagingDirectory)/app.zip'
            artifact: drop

  - stage: Deploy
    dependsOn: Build
    condition: succeeded()
    jobs:
      - deployment: deploy
        environment: production        # add approvals on this environment
        strategy:
          runOnce:
            deploy:
              steps:
                - task: AzureWebApp@1
                  inputs:
                    azureSubscription: 'sc-azure-prod'   # service connection
                    appType: webAppLinux
                    appName: $(appName)
                    package: '$(Pipeline.Workspace)/drop/app.zip'
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Build | CodeBuild (buildspec.yml) | Pipelines job |
| Orchestration | CodePipeline | Stages |
| Approvals | Manual approval action | Environment approvals/checks |
| Pricing | Per build minute | Free tier of parallel jobs, then paid (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Secrets in YAML.
✅ Correct: Variable groups linked to Key Vault, secret variables, federated service connection.

❌ Mistake: Same pipeline deploys to prod with no gate.
✅ Correct: Environment approvals and branch filters.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Pipeline structure?
A1: Pipeline > stages > jobs > steps.

Q2: [Medium] Microsoft-hosted vs self-hosted agent?
A2: Hosted are fresh managed VMs; self-hosted run in your network (VNet access, custom tools, cached state).

Q3: [Hard] Reuse across 30 repos?
A3: YAML templates in a shared repo referenced via `resources: repositories` and `extends` templates to enforce required steps.

---

## ✅ Quick Checklist
□ YAML in repo
□ Environments with approvals
□ Secrets from Key Vault

---

## ⚡ 1-Line Summary
Pipelines = YAML-defined repeatable build and release | Pipelines = YAML से ऑटोमैटिक बिल्ड और रिलीज़।

## ➡️ Next: Azure Boards

---
