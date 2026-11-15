# 318. Write Azure Pipeline
# AWS: CodePipeline + CodeBuild (or GitHub Actions)
# Azure: Azure Pipelines (azure-pipelines.yml)
# हिंदी में: Azure DevOps में YAML पाइपलाइन - बिल्ड, टेस्ट, इमेज पुश और डिप्लॉय

---

## 🔵 Simple Definition
A YAML file that defines stages, jobs and steps that build, test and deploy your app on every push.
हिंदी: YAML फ़ाइल जो हर पुश पर बिल्ड, टेस्ट और डिप्लॉय चलाती है।

## 🔴 Why it Exists
Repeatable, reviewable delivery with approvals instead of manual deploys.

## 🟢 How it Works
```
trigger (main) -> Stage Build: Node setup -> npm ci/test -> Docker@2 buildAndPush to ACR :commitSHA
              -> Stage Deploy (deployment job, environment "production" + approval)
                    -> AzureCLI@2: az containerapp update --image <acr>/<repo>:<sha>
Hierarchy: pipeline > stages > jobs > steps(tasks/script). Agents = Microsoft-hosted or self-hosted pool.
```

## 💻 Code / Config Example
`azure-pipelines.yml` (this folder): two stages, Docker@2 buildAndPush via a Docker Registry service connection, deployment job bound to an environment, AzureCLI@2 with an ARM service connection. Parsed with PyYAML only; not run on Azure DevOps.

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| CI/CD | CodePipeline + CodeBuild | Azure Pipelines |
| Config | buildspec.yml / pipeline JSON | azure-pipelines.yml |
| Approvals | manual approval action | environment checks |
| Cloud auth | IAM role (OIDC) | service connection (workload identity federation) |
| Pricing | free tiers and per-minute/parallel-job billing (approximate - check current docs) | same |

## 💰 Cost / HA / Security
- Cost: Microsoft-hosted parallel jobs are limited on the free tier; cache npm/Docker layers to cut minutes.
- HA: hosted agents are managed; keep self-hosted pools redundant.
- Security: prefer workload identity federation service connections over secrets; restrict who can use the connection; approvals on production.

## ⚠️ Common Mistakes
❌ Tagging image `latest`.
✅ Tag with `Build.SourceVersion`.

❌ Storing credentials as plain variables.
✅ Secret variables / Key Vault-linked variable group / federated service connection.

## ⚫ Interview Q&A
Q1 [Easy]: Stage vs job vs step?
A1: Stage groups jobs (e.g. Build/Deploy); a job runs on one agent; steps are tasks or scripts inside a job.

Q2 [Medium]: What is a deployment job?
A2: A special job that targets an environment with a strategy (runOnce, rolling, canary) and gets approvals/checks and deployment history.

Q3 [Hard]: Azure Pipelines vs GitHub Actions?
A3: Both YAML CI/CD. Pipelines has environments, mature release controls and Azure Boards integration; Actions has a larger marketplace and tighter GitHub integration. Pick by where code and governance live.

## ✅ Quick Checklist
□ Image tag = commit SHA
□ Environment approval on prod
□ Federated service connection

## ⚡ 1-Line Summary
One YAML: build, test, push, then gated deploy. | एक YAML: बिल्ड, टेस्ट, पुश, फिर अप्रूवल के बाद डिप्लॉय।

## ➡️ Next: 319. Cloud Migration Strategy
