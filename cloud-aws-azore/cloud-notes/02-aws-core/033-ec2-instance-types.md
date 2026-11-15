# 33. EC2 Instance Types
# AWS: EC2 Instance families (t, m, c, r, g, i ...)
# Azure: VM sizes/series (B, D, F, E, N, L ...)
# हिंदी में: सर्वर का आकार और प्रकार चुनना

---

## 🔵 Simple Definition
An instance type is a named combo of vCPU, memory, network and storage; the name `m7g.large` = family m, generation 7, Graviton (g), size large.
हिंदी: Instance type CPU, RAM और नेटवर्क का तय पैकेज है; नाम से family, generation और size पता चलता है।

---

## 🔴 Why it Exists
Different workloads need different resource ratios; paying for the right shape saves money.

---

## 🟢 How it Works
```
t  burstable   (dev, small APIs; CPU credits)     -> Azure B
m  general     (balanced web/app)                 -> Azure D
c  compute     (CPU heavy, builds)                -> Azure F
r  memory      (caches, in-memory DB)             -> Azure E
i  storage     (NVMe, high IOPS)                  -> Azure L
g/p GPU        (ML)                               -> Azure N
Suffix: g = Graviton (ARM), a = AMD, i = Intel, d = local NVMe, n = network
```

---

## 💻 Code / Config Example
```bash
# Find types matching needs (2 vCPU, >=4 GiB, x86_64, current gen)
aws ec2 describe-instance-types \
  --filters Name=vcpu-info.default-vcpus,Values=2 Name=current-generation,Values=true \
  --query 'InstanceTypes[?MemoryInfo.SizeInMiB>=`4096`].[InstanceType,MemoryInfo.SizeInMiB]' \
  --output table

# Offered in which AZs?
aws ec2 describe-instance-type-offerings --location-type availability-zone \
  --filters Name=instance-type,Values=t3.small --region ap-south-1

# Resize: stop -> change -> start
aws ec2 stop-instances --instance-ids i-0123456789abcdef0
aws ec2 modify-instance-attribute --instance-id i-0123456789abcdef0 \
  --instance-type "{\"Value\": \"t3.medium\"}"
aws ec2 start-instances --instance-ids i-0123456789abcdef0
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Burstable | t3/t4g | B-series |
| General | m6i/m7g | D-series |
| ARM | Graviton (g) | Ampere Altra (Dps v5) |
| Pricing | Per type per region; approximate, check current docs | Per size per region; check docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Running steady production load on t-class and running out of CPU credits.
✅ Correct: Use m/c class or enable unlimited mode knowingly; watch CPUCreditBalance.

❌ Mistake: Picking Graviton with x86-only Docker images.
✅ Correct: Build multi-arch images (`docker buildx --platform linux/amd64,linux/arm64`).

---

## ⚫ Interview Q&A
Q1: [Easy] What does t3.micro mean?
A1: Family t (burstable), generation 3, size micro.

Q2: [Medium] How does burstable CPU work?
A2: Baseline CPU with earned credits; bursts spend credits; when empty it throttles (standard) or charges extra (unlimited).

Q3: [Hard] How to right-size?
A3: Use CloudWatch metrics (CPU, memory via agent), Compute Optimizer recommendations, load test, consider Graviton and Savings Plans.

---

## ✅ Quick Checklist
□ Workload type mapped to family
□ Multi-arch image if ARM
□ Right-sizing reviewed monthly

---

## ⚡ 1-Line Summary
Pick the instance family by workload shape: t burst, m balanced, c CPU, r memory. | Workload के हिसाब से family चुनें: t burst, m संतुलित, c CPU, r memory।

## ➡️ Next: EC2 AMI
