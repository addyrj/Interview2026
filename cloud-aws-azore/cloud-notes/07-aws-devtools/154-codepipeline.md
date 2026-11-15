# 154. CodePipeline
# AWS: AWS CodePipeline
# Azure: Azure Pipelines (multi-stage) / GitHub Actions workflows
# हिंदी में: कोडपाइपलाइन - Source से Deploy तक पूरा CI/CD फ्लो जोड़ने वाला ऑर्केस्ट्रेटर

---

## 🔵 Simple Definition
CodePipeline models a release as stages (Source, Build, Test, Approval, Deploy) and moves artifacts between them using CodeBuild, CodeDeploy, CloudFormation, ECS and others.
हिंदी: यह अलग-अलग स्टेज को क्रम से जोड़कर पूरा रिलीज़ फ्लो अपने-आप चलाता है।

## 🔴 Why it Exists
Glue between build and deploy tools, with manual approvals and audit history, all inside AWS.

## 🟢 How it Works
```
Source (GitHub via CodeConnections) -> Build (CodeBuild)
   -> Manual Approval -> Deploy (ECS / CodeDeploy / CFN)
Artifacts passed through an S3 artifact bucket
```

## 💻 Code / Config Example
```yaml
# CloudFormation fragment (V2 pipeline)
Resources:
  Pipeline:
    Type: AWS::CodePipeline::Pipeline
    Properties:
      PipelineType: V2
      RoleArn: !GetAtt PipelineRole.Arn
      ArtifactStore: { Type: S3, Location: !Ref ArtifactBucket }
      Stages:
        - Name: Source
          Actions:
            - Name: Src
              ActionTypeId: { Category: Source, Owner: AWS, Provider: CodeStarSourceConnection, Version: "1" }
              Configuration:
                ConnectionArn: !Ref GitHubConnectionArn
                FullRepositoryId: myorg/my-api
                BranchName: main
              OutputArtifacts: [{ Name: SrcOut }]
        - Name: Build
          Actions:
            - Name: Build
              ActionTypeId: { Category: Build, Owner: AWS, Provider: CodeBuild, Version: "1" }
              Configuration: { ProjectName: !Ref BuildProject }
              InputArtifacts: [{ Name: SrcOut }]
              OutputArtifacts: [{ Name: BuildOut }]
```

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | CodePipeline | Azure Pipelines |
| Definition | Console / CFN / CDK | YAML in repo |
| Approval | Manual approval action | Environments approvals |
| Pricing | Per active pipeline (check current docs) | Parallel jobs |

## ⚠️ Common Mistakes
❌ Pipeline role too broad (AdministratorAccess). ✅ Least-privilege role per action.
❌ Using deprecated GitHub OAuth source. ✅ Use CodeConnections (GitHub app).

## ⚫ Interview Q&A
Q1 [Easy]: What are stages and actions? A1: Stage = group; action = unit of work (build, deploy).
Q2 [Medium]: How to add manual approval? A2: Approval action with SNS notification.
Q3 [Hard]: Cross-account deploy? A3: Artifact bucket + KMS key shared, assume role in the target account.

## ✅ Quick Checklist
□ Least-privilege roles
□ Approval before prod
□ Artifacts encrypted with KMS

## ⚡ 1-Line Summary
CodePipeline chains build, test and deploy | कोडपाइपलाइन बिल्ड से डिप्लॉय तक की कड़ी जोड़ता है।

## ➡️ Next: CodeArtifact
