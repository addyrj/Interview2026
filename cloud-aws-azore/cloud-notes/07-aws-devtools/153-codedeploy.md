# 153. CodeDeploy
# AWS: AWS CodeDeploy
# Azure: Azure Pipelines deployment jobs / App Service deployment slots
# हिंदी में: कोडडिप्लॉय - EC2, ECS, Lambda पर नया वर्जन सुरक्षित तरीके से रोल आउट करता है

---

## 🔵 Simple Definition
CodeDeploy automates deployments to EC2/on-prem servers, ECS services and Lambda, with rolling, in-place or blue/green strategies and automatic rollback.
हिंदी: नया वर्जन धीरे-धीरे या ब्लू/ग्रीन तरीके से डालता है और गड़बड़ होने पर वापस लौटा देता है।

## 🔴 Why it Exists
Copying files by SSH causes downtime and manual rollback. CodeDeploy gives repeatable, health-checked releases.

## 🟢 How it Works
```
Artifact (S3/GitHub) + appspec --> CodeDeploy
EC2: agent runs hooks  ApplicationStop -> BeforeInstall -> AfterInstall
                       -> ApplicationStart -> ValidateService
ECS/Lambda: shifts traffic (canary/linear/all-at-once) via ALB / alias
Alarm fires --> automatic rollback
```

## 💻 Code / Config Example
```yaml
# appspec.yml (EC2/on-prem, Node.js app)
version: 0.0
os: linux
files:
  - source: /
    destination: /var/www/my-api
hooks:
  ApplicationStop:
    - location: scripts/stop.sh
      timeout: 60
  AfterInstall:
    - location: scripts/install.sh   # npm ci --omit=dev
      timeout: 300
  ApplicationStart:
    - location: scripts/start.sh     # pm2 restart
      timeout: 60
  ValidateService:
    - location: scripts/health.sh    # curl -f localhost:3000/health
      timeout: 60
```
```bash
# scripts/health.sh
#!/bin/bash
curl -fsS http://localhost:3000/health
```

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | CodeDeploy | Pipelines deploy jobs, slots swap |
| Blue/green | ECS, Lambda, EC2 | App Service slots |
| Rollback | Auto on alarm/failure | Slot swap back |
| Pricing | No charge for EC2/Lambda/ECS deployments; small per-update fee for on-prem (approximate - check current docs) | Included with pipeline |

## ⚠️ Common Mistakes
❌ Agent not installed/IAM role missing on EC2. ✅ Install agent, attach instance profile with S3 read.
❌ Hook script not executable or returns non-zero silently. ✅ `chmod +x`, use `set -e`.

## ⚫ Interview Q&A
Q1 [Easy]: What is appspec? A1: Deployment instructions file (files + lifecycle hooks).
Q2 [Medium]: In-place vs blue/green? A2: In-place updates existing instances; blue/green launches new ones and shifts traffic.
Q3 [Hard]: ECS canary 10% for 5 minutes? A3: Deployment config CodeDeployDefault.ECSCanary10Percent5Minutes with alarms for rollback.

## ✅ Quick Checklist
□ Agent running
□ ValidateService hook present
□ Alarms tied to rollback

## ⚡ 1-Line Summary
CodeDeploy = safe, rollback-capable releases | कोडडिप्लॉय सुरक्षित रोलआउट और ऑटो रोलबैक देता है।

## ➡️ Next: CodePipeline
