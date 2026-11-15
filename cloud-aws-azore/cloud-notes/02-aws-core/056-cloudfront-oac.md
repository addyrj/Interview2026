# 56. CloudFront OAC
# AWS: CloudFront Origin Access Control (replaces OAI)
# Azure: Front Door Premium Private Link to storage / managed identity access
# हिंदी में: सिर्फ CloudFront को प्राइवेट S3 पढ़ने देने का सुरक्षित तरीका

---

## 🔵 Simple Definition (2 lines)
OAC makes CloudFront sign its requests to S3 (SigV4) so the bucket can stay private and trust only your distribution.
OAC से बकेट प्राइवेट रहता है और सिर्फ आपका CloudFront उसे पढ़ सकता है।

---

## 🔴 Why it Exists (2 lines)
The older OAI lacked SSE-KMS support, all Regions and POST/PUT methods.
OAC is the current recommended method with short-lived credentials and better security.

---

## 🟢 How it Works
```
Viewer -> CloudFront --SigV4 signed--> S3 (private)
Bucket policy: Allow Principal cloudfront.amazonaws.com
               Condition AWS:SourceArn = distribution ARN
```

---

## 💻 Code / Config Example
```yaml
# CloudFormation
Resources:
  Oac:
    Type: AWS::CloudFront::OriginAccessControl
    Properties:
      OriginAccessControlConfig:
        Name: site-oac
        OriginAccessControlOriginType: s3
        SigningBehavior: always
        SigningProtocol: sigv4
  # In the Distribution's S3 origin set: OriginAccessControlId: !GetAtt Oac.Id
  # and S3OriginConfig: { OriginAccessIdentity: "" }
```
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "AllowCloudFrontServicePrincipalReadOnly",
    "Effect": "Allow",
    "Principal": { "Service": "cloudfront.amazonaws.com" },
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::my-site-prod/*",
    "Condition": { "StringEquals": {
      "AWS:SourceArn": "arn:aws:cloudfront::111122223333:distribution/E123EXAMPLE" } }
  }]
}
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Private origin access | OAC (legacy: OAI) | Front Door Premium Private Link to Blob |
| Auth to origin | SigV4 by CloudFront | Private network path (no public access) |
| Scope condition | AWS:SourceArn on distribution | Approve private endpoint connection |
| Pricing | OAC free | Premium SKU and Private Link cost (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using OAI for new setups.
✅ Correct: Use OAC.

❌ Mistake: Bucket policy trusts all CloudFront distributions.
✅ Correct: Condition on your distribution's ARN.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What does OAC do?
A1: Lets CloudFront access a private S3 origin using signed requests.

Q2: [Medium] OAC vs OAI?
A2: OAC supports SSE-KMS, all Regions, dynamic methods and uses service principal + SourceArn; OAI is legacy.

Q3: [Hard] OAC with SSE-KMS objects?
A3: The KMS key policy must allow the `cloudfront.amazonaws.com` service principal to decrypt/generate data keys with the distribution SourceArn condition.

---

## ✅ Quick Checklist
□ OAC created, attached to S3 origin
□ Bucket policy with SourceArn
□ Block Public Access on
□ KMS key policy updated if SSE-KMS

---

## ⚡ 1-Line Summary
OAC lets only your CloudFront read a private bucket. | OAC से सिर्फ आपका CloudFront प्राइवेट बकेट पढ़ सकता है।

## ➡️ Next: Route 53 — DNS
