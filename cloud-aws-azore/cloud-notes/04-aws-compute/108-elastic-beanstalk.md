# 108. Elastic Beanstalk
# AWS: AWS Elastic Beanstalk
# Azure: Azure App Service
# हिंदी में: code upload करो, AWS server, load balancer और scaling खुद बना देता है

---

## 🔵 Simple Definition
Beanstalk is a PaaS: you upload an app (Node.js, Python, Docker...) and it provisions EC2, ALB, Auto Scaling and monitoring. You still own the underlying resources.
Code दो, बाकी infra Beanstalk बना देता है (resources आपके account में दिखते हैं)।

---

## 🔴 Why it Exists
Gives Heroku-like simplicity for teams that don't want to hand-assemble EC2 + ALB + ASG, while staying on AWS.

---

## 🟢 How it Works
```
eb init -> eb create -> zip uploaded to S3 -> CloudFormation creates:
   ALB + Auto Scaling Group + EC2 (platform AMI) + security groups
eb deploy -> rolling / immutable / blue-green (swap CNAME)
Config: .ebextensions/*.config or .platform/ hooks, env vars in environment.
```

---

## 💻 Code / Config Example
```bash
# EB CLI (pip install awsebcli) - Node.js app
eb init my-api --platform node.js --region ap-south-1
eb create my-api-prod --elb-type application --instance-type t3.small
eb setenv NODE_ENV=production DB_HOST=mydb.example.com
eb deploy
eb status
```
```yaml
# .ebextensions/options.config
option_settings:
  aws:elasticbeanstalk:application:environment:
    NODE_ENV: production
  aws:autoscaling:asg:
    MinSize: 2
    MaxSize: 4
  aws:elasticbeanstalk:environment:process:default:
    HealthCheckPath: /health
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| PaaS web hosting | Elastic Beanstalk | App Service |
| Underlying infra visible | Yes (EC2, ALB) | Hidden (plans) |
| Deploy strategies | Rolling, immutable, blue/green | Deployment slots swap |
| Pricing | No extra fee; pay underlying resources | Pay App Service plan |

---

## ⚠️ Common Mistakes
❌ Mistake: Manually editing ALB/EC2 settings in console; EB overwrites them.
✅ Correct: Change via `.ebextensions` / option settings.

❌ Mistake: Using the same environment for dev and prod, or putting RDS inside the EB environment.
✅ Correct: Separate environments; create RDS outside so deleting the env does not delete the DB.

---

## ⚫ Interview Q&A
Q1: [Easy] What is Beanstalk?
A1: PaaS orchestrating EC2, ALB and ASG for your app.
Q2: [Medium] Rolling vs immutable deploy?
A2: Rolling updates instances in batches in place; immutable launches a fresh ASG, then swaps - safer rollback.
Q3: [Hard] When avoid Beanstalk?
A3: Microservices needing fine control, containers at scale, or modern IaC pipelines - prefer ECS/App Runner.

---

## ✅ Quick Checklist
□ DB outside the environment
□ Health check path configured
□ Immutable/blue-green for prod

---

## ⚡ 1-Line Summary
Beanstalk = upload code, AWS builds the stack | Beanstalk में code दो, stack AWS बनाता है।

## ➡️ Next: 109. App Runner
