# 109. App Runner
# AWS: AWS App Runner
# Azure: Azure Container Apps (or App Service for Containers)
# हिंदी में: image या GitHub repo दो, HTTPS URL तैयार - बिना VPC/ALB की झंझट

---

## 🔵 Simple Definition
App Runner deploys a container image or source repo as an autoscaling HTTPS web service with no cluster, load balancer or VPC to manage.
सबसे आसान तरीका web API चलाने का: image दो, URL लो।

---

## 🔴 Why it Exists
ECS needs task defs, ALB, subnets, roles. For simple web services that's too much overhead.

---

## 🟢 How it Works
```
ECR image / GitHub repo --> App Runner service
   - auto deploy on new image push (optional)
   - managed TLS + URL  https://xxxx.<region>.awsapprunner.com
   - concurrency-based autoscaling (min/max instances)
   - optional VPC connector for private DB (egress only)
```

---

## 💻 Code / Config Example
```yaml
# apprunner.yaml (source-code deployment, Node.js runtime)
version: 1.0
runtime: nodejs18
build:
  commands:
    build:
      - npm ci
run:
  command: node server.js
  network:
    port: 3000
  env:
    - name: NODE_ENV
      value: production
```
```bash
# Image-based service via CLI (AWS CLI v2) - uses an input file
aws apprunner create-service --cli-input-json file://service.json
```
`service.json` needs ServiceName, SourceConfiguration.ImageRepository (ImageIdentifier, ImageRepositoryType=ECR, ImageConfiguration.Port) and an AuthenticationConfiguration.AccessRoleArn for private ECR.

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Simple container PaaS | App Runner | Container Apps |
| Scale to zero | No (paused/min 1 provisioned) | Yes |
| Private DB access | VPC connector | VNet integration |
| Pricing | Provisioned memory + active vCPU/mem (approximate - check docs) | Per-second vCPU/mem (check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Expecting inbound private-only access easily or background workers.
✅ Correct: App Runner is for HTTP services; use ECS for workers/non-HTTP.

❌ Mistake: Forgetting VPC connector so app can't reach RDS.
✅ Correct: Add a VPC connector with proper security groups.

---

## ⚫ Interview Q&A
Q1: [Easy] What is App Runner for?
A1: Simple managed web apps/APIs from image or source.
Q2: [Medium] How does it scale?
A2: Based on concurrent requests per instance between min and max sizes.
Q3: [Hard] App Runner vs ECS Fargate?
A3: App Runner trades control (networking, sidecars, non-HTTP) for simplicity; Fargate offers full ECS features.

---

## ✅ Quick Checklist
□ Port and health check configured
□ VPC connector if DB is private
□ Min/max instances set

---

## ⚡ 1-Line Summary
App Runner = zero-ops HTTPS container hosting | App Runner = बिना झंझट HTTPS container hosting।

## ➡️ Next: 110. Batch Processing
