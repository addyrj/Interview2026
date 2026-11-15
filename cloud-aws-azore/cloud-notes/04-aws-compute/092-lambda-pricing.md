---

# 92. Lambda Pricing
# AWS: Lambda pricing
# Azure: Azure Functions Consumption pricing
# हिंदी में: लैम्ब्डा की कीमत

---

## 🔵 Simple Definition (2 lines)
You pay per request plus compute duration measured in GB-seconds (memory × time), rounded to 1 ms.
हिंदी: Lambda में रिक्वेस्ट की संख्या और memory × समय (GB-seconds) के हिसाब से पैसा लगता है।

---

## 🔴 Why it Exists (2 lines)
Pay-per-use means zero cost when idle, but you must understand the formula or a busy function can cost more than a small VPS.

---

## 🟢 How it Works
```
Cost = requests × price_per_request
     + (memory_GB × duration_s × invocations) × price_per_GB_second
Approximate list prices (check current docs; region varies):
  requests    ~ $0.20 per 1M
  duration    ~ $0.0000166667 per GB-s (x86); arm64 is ~20% cheaper
  free tier   ~ 1M requests + 400,000 GB-s per month
Extras: provisioned concurrency, data transfer out, CloudWatch Logs, API Gateway
```

---

## 💻 Code / Config Example
```python
# Quick estimator (prices are approximate; update from the pricing page)
def lambda_cost(invocations, mem_mb, avg_ms,
                req_per_m=0.20, gb_s=0.0000166667,
                free_req=1_000_000, free_gbs=400_000):
    gbs = invocations * (mem_mb / 1024) * (avg_ms / 1000)
    req_cost = max(invocations - free_req, 0) / 1_000_000 * req_per_m
    dur_cost = max(gbs - free_gbs, 0) * gb_s
    return round(req_cost + dur_cost, 2)

# 10M req/month, 512 MB, 200 ms
print(lambda_cost(10_000_000, 512, 200))
# 10M req: gbs = 10M*0.5*0.2 = 1,000,000 ; (1M-0.4M)*1.66667e-5 = 10.0 ; req 9M*0.2/1M = 1.8 => 11.8
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Billing unit | Requests + GB-s | Executions + GB-s |
| Free grant | ~1M req + 400k GB-s | ~1M exec + 400k GB-s (approximate) |
| Always-warm | Provisioned concurrency | Premium plan |
| Pricing | approximate — check current docs | approximate — check current docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Over-allocating memory "just in case".
✅ Correct: Use AWS Lambda Power Tuning; more memory can be cheaper if it shortens duration.

❌ Mistake: Ignoring API Gateway and logging costs.
✅ Correct: Include them; verbose logs in CloudWatch can exceed compute cost.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What are the two cost components?
A1: Request count and duration × memory (GB-seconds).

Q2: [Medium] How does memory affect cost and speed?
A2: CPU scales with memory; doubling memory may halve duration, giving similar or lower cost.

Q3: [Hard] When is a VPS/Fargate cheaper than Lambda?
A3: Steady, high, constant traffic keeping compute busy 24/7; Lambda wins for spiky or low-volume workloads.

---

## ✅ Quick Checklist
□ Estimate invocations × duration × memory
□ Use arm64 where possible
□ Set log retention

---

## ⚡ 1-Line Summary
Lambda bill = requests + GB-seconds | Lambda बिल = रिक्वेस्ट + GB-seconds।

## ➡️ Next: Lambda + API Gateway

---
