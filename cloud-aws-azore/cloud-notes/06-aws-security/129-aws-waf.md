# 129. AWS WAF
# AWS: AWS WAF (WAFv2)
# Azure: Azure WAF on Application Gateway / Front Door
# हिंदी में: वेब ऐप फ़ायरवॉल जो SQL injection, बॉट और ज़्यादा रिक्वेस्ट को रोकता है

---

## 🔵 Simple Definition
WAF inspects HTTP(S) requests and allows, blocks or counts them using rules, attached to CloudFront, ALB, API Gateway or AppSync.
हिंदी: WAF HTTP रिक्वेस्ट जाँचकर नियमों के आधार पर उन्हें अनुमति देता या रोकता है।

---

## 🔴 Why it Exists
Apps face SQLi, XSS, bots and abusive clients that security groups cannot see (they work at L3/L4).

---

## 🟢 How it Works
```
Client -> CloudFront / ALB + Web ACL
              rules evaluated by priority:
              1 AWS Managed Common rules  -> block
              2 Rate limit per IP         -> block
              default action: allow
```

---

## 💻 Code / Config Example
```hcl
# Terraform (aws provider ~> 5.x) - Web ACL with managed rules + rate limit
resource "aws_wafv2_web_acl" "api" {
  name  = "api-acl"
  scope = "REGIONAL" # CLOUDFRONT needs us-east-1
  default_action { allow {} }

  rule {
    name     = "common"
    priority = 1
    override_action { none {} }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "common"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "rate"
    priority = 2
    action { block {} }
    statement {
      rate_based_statement {
        limit              = 1000
        aggregate_key_type = "IP"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "rate"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "api-acl"
    sampled_requests_enabled   = true
  }
}
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | WAFv2 Web ACL | WAF policy |
| Managed rules | AWS Managed Rules | OWASP Default Rule Set |
| Rate limiting | Rate-based rule | Rate limit custom rule |
| Pricing | Per ACL, rule, request (approximate - check current docs) | Per gateway/policy (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Going straight to Block mode and breaking real users.
✅ Correct: Start with Count, review logs, then Block.

❌ Mistake: Creating a CLOUDFRONT-scope ACL in the wrong region.
✅ Correct: CloudFront scope must be created in us-east-1.

---

## ⚫ Interview Q&A
Q1: [Easy] What does WAF protect against?
A1: Common web exploits (SQLi, XSS) and abusive traffic at layer 7.

Q2: [Medium] WAF vs security group?
A2: SG filters by IP/port (L3/L4); WAF inspects HTTP content.

Q3: [Hard] How to handle false positives?
A3: Count mode, logging to S3/CloudWatch, exclude specific rules in the managed group, scope-down statements.

---

## ✅ Quick Checklist
□ Managed rules + rate limit
□ Logging enabled
□ Tested in Count mode first

---

## ⚡ 1-Line Summary
WAF filters malicious HTTP requests | WAF दुर्भावनापूर्ण HTTP रिक्वेस्ट को फ़िल्टर करता है।

## ➡️ Next: AWS Secrets Manager
