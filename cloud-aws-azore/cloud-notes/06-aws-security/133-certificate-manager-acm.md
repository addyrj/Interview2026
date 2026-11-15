# 133. Certificate Manager (ACM)
# AWS: AWS Certificate Manager (ACM)
# Azure: App Service Managed Certificates / Key Vault certificates / Front Door managed certs
# हिंदी में: HTTPS के लिए SSL/TLS सर्टिफिकेट अपने-आप बनाना और रिन्यू करना

---

## 🔵 Simple Definition
ACM issues and auto-renews public TLS certificates (free) for use with ALB, CloudFront, API Gateway.
हिंदी: ACM मुफ़्त पब्लिक TLS सर्टिफिकेट देता है और उन्हें अपने-आप रिन्यू करता है।

---

## 🔴 Why it Exists
Manual certificates expire and cause outages.

---

## 🟢 How it Works
```
Request cert for api.example.com
  -> DNS validation (CNAME in Route 53)
  -> Issued -> attach to ALB listener 443 / CloudFront
  -> Auto-renews while the CNAME stays
Note: CloudFront certs must be in us-east-1. Public ACM certs cannot be exported.
```

---

## 💻 Code / Config Example
```hcl
# Terraform (aws provider ~> 5.x)
resource "aws_acm_certificate" "api" {
  domain_name       = "api.example.com"
  validation_method = "DNS"
  lifecycle { create_before_destroy = true }
}

resource "aws_route53_record" "validation" {
  for_each = {
    for o in aws_acm_certificate.api.domain_validation_options :
    o.domain_name => { name = o.resource_record_name, type = o.resource_record_type, value = o.resource_record_value }
  }
  zone_id = var.zone_id
  name    = each.value.name
  type    = each.value.type
  records = [each.value.value]
  ttl     = 60
}

resource "aws_acm_certificate_validation" "api" {
  certificate_arn         = aws_acm_certificate.api.arn
  validation_record_fqdns = [for r in aws_route53_record.validation : r.fqdn]
}
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Public cert | ACM (free) | App Service managed cert (free), Front Door managed |
| Private CA | ACM Private CA | Key Vault + external CA |
| Renewal | Automatic | Automatic for managed certs |
| Export | Not for public certs | Not for managed certs |

---

## ⚠️ Common Mistakes
❌ Mistake: Cert stuck in Pending validation.
✅ Correct: Create the validation CNAME and keep it.

❌ Mistake: ACM cert for CloudFront made in ap-south-1.
✅ Correct: Create it in us-east-1.

---

## ⚫ Interview Q&A
Q1: [Easy] Is ACM free?
A1: Public certificates are free when used with integrated services.

Q2: [Medium] Why can't I install an ACM cert on my VPS/EC2 nginx?
A2: Public ACM certs cannot be exported; use Let's Encrypt/certbot there or terminate TLS at ALB/CloudFront.

Q3: [Hard] DNS vs email validation?
A3: DNS validation is automatable and enables auto-renewal; email is manual and fragile.

---

## ✅ Quick Checklist
□ DNS validation record kept
□ Correct region
□ HTTP to HTTPS redirect set

---

## ⚡ 1-Line Summary
ACM = free auto-renewing TLS certs | ACM मुफ़्त और ऑटो-रिन्यू होने वाले TLS सर्टिफिकेट देता है।

## ➡️ Next: CloudTrail - Audit Logs
