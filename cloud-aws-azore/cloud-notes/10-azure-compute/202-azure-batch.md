---

# 202. Azure Batch
# AWS: AWS Batch
# Azure: Azure Batch
# हिंदी में: बड़े पैमाने पर parallel jobs चलाने की सेवा

---

## 🔵 Simple Definition (2 lines)
Azure Batch schedules large numbers of compute jobs/tasks on a managed pool of VMs and scales the pool for you.
हिंदी: Azure Batch हज़ारों jobs को VMs के pool पर अपने-आप schedule और scale करके चलाता है।

---

## 🔴 Why it Exists (2 lines)
Rendering, simulations, ETL or video encoding need hundreds of cores for a short time, not a permanent cluster.
Batch handles queueing, retries, VM provisioning and teardown so you pay only while tasks run.

---

## 🟢 How it Works
```
Batch Account
   |-- Pool (VMs, autoscale formula, container or app package)
   |-- Job  (belongs to a pool)
         |-- Task 1..N  (command line, input/output in Blob Storage)
Scheduler assigns tasks -> nodes -> retries failed tasks -> scales pool down
```

---

## 💻 Code / Config Example
```bash
# Create Batch account + login (Azure CLI)
az batch account create -n mybatchacct -g rg-demo -l centralindia
az batch account login -n mybatchacct -g rg-demo --shared-key-auth

# Pool with 2 Ubuntu nodes
az batch pool create --id pool1 --vm-size Standard_D2s_v3 \
  --target-dedicated-nodes 2 \
  --image canonical:0001-com-ubuntu-server-jammy:22_04-lts \
  --node-agent-sku-id "batch.node.ubuntu 22.04"

# Job + task
az batch job create --id job1 --pool-id pool1
az batch task create --job-id job1 --task-id t1 \
  --command-line "/bin/bash -c 'echo processing && sleep 5'"
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | AWS Batch | Azure Batch |
| Compute | EC2 / Fargate / Spot | VM pools, Spot (low-priority) nodes |
| Unit of work | Job definition + job queue | Pool, job, task |
| Pricing | No extra fee, pay for compute | No extra fee, pay for VMs/storage |

---

## ⚠️ Common Mistakes
❌ Mistake: Leaving a fixed-size pool running after jobs finish.
✅ Correct: Use an autoscale formula or set target nodes to 0.

❌ Mistake: Running short, tiny API-style tasks on Batch.
✅ Correct: Use Functions/Container Apps jobs for short event work; Batch for heavy parallel compute.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is Azure Batch? A1: A managed service to run parallel/HPC jobs on a pool of VMs.
Q2: [Medium] Pool vs job vs task? A2: Pool is the set of VMs, job groups tasks bound to a pool, a task is one command execution.
Q3: [Hard] How do you cut cost for fault-tolerant jobs? A3: Use Spot nodes with task retries, autoscale to zero, and keep data in Blob so nodes are disposable.

---

## ✅ Quick Checklist
□ Autoscale or resize to 0 when idle
□ Task retry count set
□ Inputs/outputs in Blob Storage
□ Spot nodes for tolerant workloads

---

## ⚡ 1-Line Summary
Azure Batch runs big parallel jobs on auto-scaled VM pools | Azure Batch बड़े parallel jobs को auto-scaled VM pools पर चलाता है।

## ➡️ Next: 203. Azure Logic Apps

---
