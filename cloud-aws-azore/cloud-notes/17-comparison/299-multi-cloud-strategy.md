# 299. Multi-cloud Strategy
# AWS: Used alongside other clouds (EKS Anywhere, Outposts, S3 API)
# Azure: Azure Arc to manage resources across clouds
# हिंदी में: मल्टी-क्लाउड रणनीति

---

## 🔵 Simple Definition
Using two or more cloud providers on purpose, for resilience, compliance, best-of-breed services or acquisitions.
हिंदी: जान-बूझकर दो या अधिक क्लाउड इस्तेमाल करना, रेजिलिएंस, कंप्लायंस या बेहतर सर्विस के लिए।

---

## 🔴 Why it Exists
Avoid single-vendor lock-in or outage risk, meet data residency, or use a unique service (e.g. one cloud's AI or analytics).

---

## 🟢 How it Works
```
Common layer: Terraform + containers/Kubernetes + OpenTelemetry + OIDC SSO
  Cloud A (primary)  <-- DNS / traffic manager -->  Cloud B (DR or specific workload)
  Data: replicated object storage / DB logical replication
```

---

## 💻 Code / Config Example
```hcl
# Terraform with two providers in one config
terraform {
  required_providers {
    aws     = { source = "hashicorp/aws",     version = "~> 5.0" }
    azurerm = { source = "hashicorp/azurerm", version = "~> 3.0" }
  }
}
provider "aws"     { region = "ap-south-1" }
provider "azurerm" { features {} }

resource "aws_s3_bucket" "primary" { bucket = "myapp-primary-assets" }
resource "azurerm_resource_group" "dr" {
  name     = "rg-dr"
  location = "centralindia"
}
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Hybrid/multi mgmt | EKS Anywhere, Outposts | Azure Arc |
| IaC neutral tool | Terraform | Terraform |
| Native IaC | CloudFormation | Bicep/ARM |
| Cost | Egress between clouds is charged | Same |

---

## ⚠️ Common Mistakes
❌ Mistake: Multi-cloud "just in case" and using only lowest-common-denominator features.
✅ Correct: Have a concrete driver; otherwise one cloud done well.

❌ Mistake: Ignoring egress cost and latency between clouds.
✅ Correct: Keep chatty services together.

---

## ⚫ Interview Q&A
Q1: [Easy] Why multi-cloud?
A1: Resilience, compliance, best-of-breed, avoiding lock-in.

Q2: [Medium] Main drawbacks?
A2: More complexity, skills, security surface, and egress cost.

Q3: [Hard] Design DR across clouds?
A3: Containers + Terraform in both, async data replication, DNS failover, regular drills, defined RPO/RTO.

---

## ✅ Quick Checklist
□ Clear business driver
□ Neutral tooling (Terraform, K8s, OTel)
□ Egress and skills costed

---

## ⚡ 1-Line Summary
Multi-cloud adds resilience but also real complexity. | मल्टी-क्लाउड रेजिलिएंस देता है पर जटिलता भी बढ़ाता है।

## ➡️ Next: 300. Cloud-agnostic Architecture
