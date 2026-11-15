# 50. S3 ACL + Public Access Block
# AWS: S3 ACLs, Object Ownership, Block Public Access
# Azure: Container public access level / "Allow Blob anonymous access" setting
# हिंदी में: पुराने ACL और बकेट को गलती से पब्लिक होने से रोकने वाला सेफ्टी स्विच

---

## 🔵 Simple Definition (2 lines)
ACLs are legacy per-object/bucket permissions; Block Public Access (BPA) is a safety switch that overrides any policy/ACL making data public.
ACL पुराना तरीका है; Block Public Access चालू रखो तो डेटा गलती से भी पब्लिक नहीं होगा।

---

## 🔴 Why it Exists (2 lines)
Many data leaks came from accidentally public buckets.
AWS now defaults to ACLs disabled and BPA on for new buckets to stop this.

---

## 🟢 How it Works
```
Object Ownership = BucketOwnerEnforced  -> ACLs disabled (recommended default)
BPA 4 settings:
  BlockPublicAcls | IgnorePublicAcls | BlockPublicPolicy | RestrictPublicBuckets
Account-level BPA + bucket-level BPA; any public grant is blocked while on
```

---

## 💻 Code / Config Example
```bash
# Turn on all four BPA settings for the bucket
aws s3api put-public-access-block --bucket my-app-uploads-prod \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# Disable ACLs (bucket owner owns all objects)
aws s3api put-bucket-ownership-controls --bucket my-app-uploads-prod \
  --ownership-controls 'Rules=[{ObjectOwnership=BucketOwnerEnforced}]'

# Account-wide guardrail
aws s3control put-public-access-block --account-id 111122223333 \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Public guard | Block Public Access | Account setting `allowBlobPublicAccess=false` |
| Legacy perms | ACLs | Container access level (private/blob/container) |
| Scope | Bucket and account | Storage account and container |
| Pricing | free | free |

---

## ⚠️ Common Mistakes
❌ Mistake: Using `public-read` ACL for uploads.
✅ Correct: Keep private; serve via CloudFront OAC or pre-signed URLs.

❌ Mistake: Turning BPA off to "fix" an AccessDenied.
✅ Correct: Fix the IAM/bucket policy instead.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is Block Public Access?
A1: Settings that prevent public ACLs and policies at bucket or account level.

Q2: [Medium] Why disable ACLs?
A2: Simpler, single permission model (policies), bucket owner owns all objects; AWS recommends it.

Q3: [Hard] Which wins: BPA or a public bucket policy?
A3: BPA; with BlockPublicPolicy/RestrictPublicBuckets the public policy is rejected or its public access ignored.

---

## ✅ Quick Checklist
□ BPA on at account level
□ Object Ownership = BucketOwnerEnforced
□ No public-read ACLs
□ Access Analyzer for S3 reviewed

---

## ⚡ 1-Line Summary
Disable ACLs and keep Block Public Access on. | ACL बंद करो और Block Public Access हमेशा चालू रखो।

## ➡️ Next: S3 Pre-signed URLs
