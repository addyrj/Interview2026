# 157. CloudFormation Basics
# AWS: AWS CloudFormation
# Azure: ARM templates / Bicep
# हिंदी में: क्लाउडफॉर्मेशन - टेम्पलेट फ़ाइल से AWS संसाधन बनाना और मैनेज करना

---

## 🔵 Simple Definition
CloudFormation provisions AWS resources from a declarative YAML/JSON template. Each deployed template is a stack that can be updated, rolled back or deleted as a unit.
हिंदी: एक टेम्पलेट लिखिए, पूरा स्टैक बन जाता है; गलती होने पर अपने-आप रोलबैक।

## 🔴 Why it Exists
Console clicking is not repeatable. Templates in Git give reviewable, reproducible infrastructure.

## 🟢 How it Works
```
template.yaml (Parameters, Resources, Outputs)
    --> create/update stack --> change set (preview)
    --> provision in dependency order
    failure --> rollback   |   drift detection finds manual changes
```

## 💻 Code / Config Example
```yaml
AWSTemplateFormatVersion: "2010-09-09"
Description: Private S3 bucket for uploads
Parameters:
  Env:
    Type: String
    AllowedValues: [dev, prod]
    Default: dev
Resources:
  UploadBucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Retain
    Properties:
      BucketName: !Sub "my-uploads-${Env}-${AWS::AccountId}"
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
Outputs:
  BucketArn:
    Value: !GetAtt UploadBucket.Arn
    Export: { Name: !Sub "${Env}-upload-bucket-arn" }
```
```bash
aws cloudformation deploy --template-file template.yaml \
  --stack-name uploads-dev --parameter-overrides Env=dev
```

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | CloudFormation | ARM / Bicep |
| Preview | Change sets | what-if |
| Unit | Stack | Deployment at RG/subscription |
| Pricing | Free for AWS resources | Free |

## ⚠️ Common Mistakes
❌ Manual console edits (drift). ✅ Change via template; run drift detection.
❌ Deleting stack loses data. ✅ DeletionPolicy: Retain/Snapshot on stateful resources.

## ⚫ Interview Q&A
Q1 [Easy]: Stack? A1: A deployed collection of resources from one template.
Q2 [Medium]: What is a change set? A2: Preview of what an update will add/modify/replace.
Q3 [Hard]: Stack stuck in UPDATE_ROLLBACK_FAILED? A3: Fix the blocking resource, then continue-update-rollback (optionally skipping resources).

## ✅ Quick Checklist
□ Template in Git
□ Change set before prod
□ DeletionPolicy on databases

## ⚡ 1-Line Summary
CloudFormation = declarative stacks with rollback | क्लाउडफॉर्मेशन टेम्पलेट से स्टैक बनाता और रोलबैक करता है।

## ➡️ Next: SAM - Serverless App Model
