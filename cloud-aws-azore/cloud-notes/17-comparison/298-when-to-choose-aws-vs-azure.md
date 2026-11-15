# 298. When to Choose AWS vs Azure
# AWS: Broadest service catalog, largest market share (generally)
# Azure: Strong Microsoft ecosystem integration
# हिंदी में: AWS या Azure कब चुनें

---

## 🔵 Simple Definition
Choose by existing ecosystem, team skills, compliance and required services, not by brand.
हिंदी: मौजूदा इकोसिस्टम, टीम की स्किल और जरूरत के हिसाब से चुनें, ब्रांड देखकर नहीं।

---

## 🔴 Why it Exists
Both are capable; the wrong pick costs migration effort and productivity.

---

## 🟢 How it Works
```
Microsoft shop (AD, M365, .NET, SQL Server)?  -> lean Azure
Startup / Linux / open-source / widest services? -> lean AWS
Existing credits, partner or customer mandate?  -> follow that
Else: team skill + cost + region/compliance decides
```

---

## 💻 Code / Config Example
```yaml
# Decision matrix (score 1-5, weight by importance)
criteria:
  team_skills:        { aws: 4, azure: 2, weight: 5 }
  existing_ecosystem: { aws: 2, azure: 5, weight: 4 }   # e.g. M365/Entra
  required_services:  { aws: 5, azure: 4, weight: 4 }
  compliance_region:  { aws: 4, azure: 4, weight: 3 }
  cost_credits:       { aws: 3, azure: 4, weight: 3 }
# total = sum(score * weight) per cloud; pick higher, then validate with a PoC
```

---

## 📊 AWS vs Azure Quick Compare
| Factor | AWS | Azure |
|--------|-----|-------|
| Strength | Service breadth, maturity | Enterprise/Microsoft integration, hybrid |
| Identity | IAM | Entra ID with M365 SSO |
| Hybrid | Outposts | Arc, Azure Stack |
| Startups | Credits programs, community | Credits programs (check current terms) |

---

## ⚠️ Common Mistakes
❌ Mistake: Choosing based on a blog benchmark.
✅ Correct: Run a PoC with your own workload.

❌ Mistake: Ignoring talent availability.
✅ Correct: Count skills you already have.

---

## ⚫ Interview Q&A
Q1: [Easy] When is Azure natural?
A1: Microsoft-centric enterprises: Entra ID, M365, SQL Server, .NET.

Q2: [Medium] Why might a startup pick AWS?
A2: Mature ecosystem, many tutorials/hires, broad services, credits.

Q3: [Hard] How defend your choice to a CTO?
A3: Weighted criteria, PoC results, TCO including people and egress, exit strategy, and risk (lock-in, compliance).

---

## ✅ Quick Checklist
□ Skills and ecosystem scored
□ Compliance/region verified
□ PoC done

---

## ⚡ 1-Line Summary
Pick by skills, ecosystem and needs, then prove with a PoC. | स्किल, इकोसिस्टम और जरूरत से चुनें, फिर PoC से सिद्ध करें।

## ➡️ Next: 299. Multi-cloud Strategy
