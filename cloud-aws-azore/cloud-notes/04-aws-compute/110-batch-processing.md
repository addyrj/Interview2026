# 110. Batch Processing
# AWS: AWS Batch
# Azure: Azure Batch
# हिंदी में: बहुत सारे background jobs को queue में डालकर automatically compute पर चलाना

---

## 🔵 Simple Definition
AWS Batch queues jobs (containers) and runs them on managed EC2/Spot/Fargate compute that scales with the queue.
Jobs queue में डालो, Batch compute बनाकर चला देता है और काम ख़त्म होने पर बंद।

---

## 🔴 Why it Exists
Nightly reports, video encoding, data crunching need lots of compute briefly. Keeping servers idle is wasteful.

---

## 🟢 How it Works
```
submit-job --> Job Queue (priority) --> Compute Environment (Fargate / EC2 / Spot)
                   |                          |
          Job Definition (image, vCPU, mem)   scales 0..maxvCpus
Job states: SUBMITTED -> RUNNABLE -> STARTING -> RUNNING -> SUCCEEDED/FAILED
```

---

## 💻 Code / Config Example
```json
{
  "jobDefinitionName": "report-job",
  "type": "container",
  "platformCapabilities": ["FARGATE"],
  "containerProperties": {
    "image": "123456789012.dkr.ecr.ap-south-1.amazonaws.com/report:v1",
    "command": ["python", "report.py"],
    "resourceRequirements": [
      { "type": "VCPU", "value": "0.5" },
      { "type": "MEMORY", "value": "1024" }
    ],
    "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
    "networkConfiguration": { "assignPublicIp": "ENABLED" }
  },
  "retryStrategy": { "attempts": 2 }
}
```
```bash
aws batch register-job-definition --cli-input-json file://jobdef.json
aws batch submit-job --job-name nightly --job-queue my-queue --job-definition report-job
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Batch service | AWS Batch | Azure Batch |
| Cheap compute | Spot | Spot / low-priority VMs |
| Orchestration | Step Functions | Data Factory / Logic Apps |
| Pricing | Free service; pay compute used | Same |

---

## ⚠️ Common Mistakes
❌ Mistake: Jobs stuck in RUNNABLE.
✅ Correct: Check compute environment max vCPUs, subnet/IGW or NAT for image pull, instance limits.

❌ Mistake: Non-idempotent jobs with retries.
✅ Correct: Make jobs idempotent.

---

## ⚫ Interview Q&A
Q1: [Easy] What is AWS Batch?
A1: Managed batch job scheduler and compute.
Q2: [Medium] Why jobs stay RUNNABLE?
A2: No capacity or can't launch compute (limits, network, wrong role).
Q3: [Hard] Batch vs Lambda vs ECS tasks?
A3: Lambda has time limit (15 min); Batch handles long, heavy, queued/dependent jobs with Spot; plain ECS tasks lack queueing and priority.

---

## ✅ Quick Checklist
□ Spot with retry strategy
□ Idempotent jobs
□ Max vCPU cap to limit cost

---

## ⚡ 1-Line Summary
Batch runs queued containerised jobs on scaling compute | Batch queue के jobs को scaling compute पर चलाता है।

## ➡️ Next: 111. SQS - Complete Guide
