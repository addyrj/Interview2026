# 393. AWS IAM for GitHub Actions
# हिंदी में: GitHub Actions के लिए AWS IAM

---

## 🔵 Simple Definition (English)
**IAM (Identity and Access Management)** decides who can do what in AWS. For GitHub Actions you create a dedicated **IAM role** with a **permissions policy** (what the pipeline may do: push to ECR, update ECS) and a **trust policy** (who may assume the role: only your repo, via OIDC). The rule is **least privilege**: give only what each pipeline needs.

## 🔵 सरल परिभाषा (Hindi)
**IAM (Identity and Access Management)** तय करता है कि AWS में कौन क्या कर सकता है। GitHub Actions के लिए एक अलग **IAM role** बनता है जिसमें **permissions policy** (pipeline क्या कर सकती है: ECR में push, ECS update) और **trust policy** (कौन role ले सकता है: सिर्फ आपका repo, OIDC से) होती है। नियम है **least privilege**: हर pipeline को सिर्फ उतना दो जितना ज़रूरी है।

---

## 🔴 Problem it Solves
The lazy way: create an IAM user with `AdministratorAccess`, paste its keys into GitHub secrets. If a workflow is compromised (malicious PR, leaked log, bad third-party action), the attacker owns your whole AWS account: can delete databases, mine crypto, read all data.

Scoped roles limit the blast radius: a compromised "deploy frontend" pipeline can only write one S3 bucket and invalidate one distribution.

## 🔴 यह क्यों बना? (Hindi)
आलसी तरीका: `AdministratorAccess` वाला IAM user बनाकर उसकी keys GitHub secrets में डाल देना। अगर workflow compromise हो (malicious PR, log leak, खराब third-party action) तो attacker पूरा AWS account ले लेता है: databases delete, crypto mining, सारा data पढ़ना।

सीमित roles से नुकसान का दायरा छोटा रहता है: compromised "frontend deploy" pipeline सिर्फ एक S3 bucket में लिख सकती है और एक distribution invalidate कर सकती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → List what the pipeline really does (e.g. push image, update ECS service)
Step 2 → Map each action to IAM actions (ecr:PutImage, ecs:UpdateService, ...)
Step 3 → Write a permissions policy with those actions on specific resource ARNs
Step 4 → Write a trust policy: allow GitHub OIDC provider, only for repo X, branch/env Y
Step 5 → Create role, attach policy; put role ARN in the workflow (not a secret key)
Step 6 → Run the pipeline; read "AccessDenied" errors, add only the missing action
Step 7 → Review with IAM Access Analyzer / CloudTrail, remove unused permissions
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → लिखें कि pipeline असल में क्या करती है (जैसे image push, ECS service update)
Step 2 → हर काम को IAM actions से map करें (ecr:PutImage, ecs:UpdateService, ...)
Step 3 → इन actions और specific resource ARNs के साथ permissions policy लिखें
Step 4 → Trust policy लिखें: GitHub OIDC provider, सिर्फ repo X, branch/environment Y के लिए
Step 5 → Role बनाएँ, policy attach करें; workflow में role ARN डालें (secret key नहीं)
Step 6 → Pipeline चलाएँ; "AccessDenied" देखकर सिर्फ missing action जोड़ें
Step 7 → IAM Access Analyzer / CloudTrail से review करें, अनुपयोगी permissions हटाएँ
```

---

## 🟡 Real World Example
A fintech has three pipelines: `web` (React to S3), `api` (ECS), `infra` (Terraform). Each has its own role: `gha-web` can only `s3:PutObject` on `app-prod-web/*` and `cloudfront:CreateInvalidation`; `gha-api` can push to one ECR repo and update one ECS service and `iam:PassRole` for the task role; `gha-infra` is powerful but only assumable from the `main` branch with a manual approval environment. An auditor asks "who can touch prod DB?" and the answer is a short list.

## 🟡 Real Example Hindi mein
एक fintech में तीन pipelines हैं: `web` (React से S3), `api` (ECS), `infra` (Terraform)। हर एक का अपना role है: `gha-web` सिर्फ `app-prod-web/*` पर `s3:PutObject` और `cloudfront:CreateInvalidation` कर सकता है; `gha-api` एक ECR repo में push, एक ECS service update और task role के लिए `iam:PassRole` कर सकता है; `gha-infra` शक्तिशाली है पर सिर्फ `main` branch और manual approval वाले environment से assume हो सकता है। Auditor पूछे "prod DB कौन छू सकता है?" तो जवाब एक छोटी सूची है।

---

## 💻 Code / Config Example — Basic

Permissions policy for a pipeline that pushes one image to ECR (JSON, AWS standard).

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EcrLogin",
      "Effect": "Allow",
      "Action": "ecr:GetAuthorizationToken",
      "Resource": "*"
    },
    {
      "Sid": "PushToOneRepo",
      "Effect": "Allow",
      "Action": [
        "ecr:BatchCheckLayerAvailability",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:PutImage",
        "ecr:BatchGetImage"
      ],
      "Resource": "arn:aws:ecr:ap-south-1:111122223333:repository/orders-api"
    }
  ]
}
```

`ecr:GetAuthorizationToken` does not support resource-level scoping, so `"*"` is required for that single action only.

Create it with the CLI:

```bash
# create the policy from the JSON file above
aws iam create-policy --policy-name gha-orders-api-ecr --policy-document file://ecr-policy.json
# attach to the role (role creation is in topic 394)
aws iam attach-role-policy --role-name gha-orders-api --policy-arn arn:aws:iam::111122223333:policy/gha-orders-api-ecr
```

## 💻 Code / Config Example — Advanced

Permissions for an ECS deploy pipeline, with conditions, plus a CloudFormation-style YAML to create the role as code. Resource names are examples.

```yaml
# gha-role.cfn.yml : CloudFormation template for the CI role (deploy with: aws cloudformation deploy)
AWSTemplateFormatVersion: '2010-09-09'          # CloudFormation template version
Description: IAM role for GitHub Actions ECS deploys   # human description
Parameters:
  GitHubOrg:
    Type: String                                 # your GitHub user/org name
  RepoName:
    Type: String                                 # repository name
Resources:
  GhaRole:
    Type: AWS::IAM::Role                         # the role GitHub assumes
    Properties:
      RoleName: gha-orders-api-deploy            # visible name
      MaxSessionDuration: 3600                   # 1 hour max session
      AssumeRolePolicyDocument:                  # TRUST policy (who can assume)
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Federated: !Sub arn:aws:iam::${AWS::AccountId}:oidc-provider/token.actions.githubusercontent.com
            Action: sts:AssumeRoleWithWebIdentity   # OIDC style assume
            Condition:
              StringEquals:
                token.actions.githubusercontent.com:aud: sts.amazonaws.com   # audience must match
              StringLike:
                token.actions.githubusercontent.com:sub: !Sub repo:${GitHubOrg}/${RepoName}:environment:production   # only this repo + environment
      Policies:
        - PolicyName: ecs-deploy                 # inline PERMISSIONS policy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - ecs:DescribeServices         # read service state
                  - ecs:UpdateService            # roll out new task definition
                  - ecs:RegisterTaskDefinition   # create new revision
                  - ecs:DescribeTaskDefinition   # read current revision
                Resource: '*'                    # these ECS actions are mostly not resource-scopable
              - Effect: Allow
                Action: iam:PassRole             # allow attaching roles to the task
                Resource:
                  - !Sub arn:aws:iam::${AWS::AccountId}:role/orders-api-task-role        # task role only
                  - !Sub arn:aws:iam::${AWS::AccountId}:role/orders-api-execution-role   # execution role only
                Condition:
                  StringEquals:
                    iam:PassedToService: ecs-tasks.amazonaws.com   # only to ECS tasks
              - Effect: Allow
                Action: [ecr:GetAuthorizationToken]   # docker login
                Resource: '*'
              - Effect: Allow
                Action: [ecr:BatchCheckLayerAvailability, ecr:InitiateLayerUpload, ecr:UploadLayerPart, ecr:CompleteLayerUpload, ecr:PutImage, ecr:BatchGetImage]
                Resource: !Sub arn:aws:ecr:${AWS::Region}:${AWS::AccountId}:repository/orders-api   # one repo
Outputs:
  RoleArn:
    Value: !GetAtt GhaRole.Arn                   # paste this ARN in the workflow
```

Pipeline side (no AWS keys anywhere):

```yaml
name: ecs-deploy                                 # workflow
on:
  workflow_dispatch: {}                          # manual trigger for the example
permissions:
  id-token: write                                # allow OIDC token
  contents: read                                 # allow checkout
jobs:
  deploy:
    runs-on: ubuntu-latest                       # runner
    environment: production                      # matches the ":environment:production" in the trust policy
    steps:
      - uses: aws-actions/configure-aws-credentials@v4   # assumes the role
        with:
          role-to-assume: arn:aws:iam::111122223333:role/gha-orders-api-deploy
          aws-region: ap-south-1
      - run: aws sts get-caller-identity         # prints who you are; proves the role works
```

---

## 🟠 My Stack Integration
- **One role per pipeline and per environment** (`gha-web-prod`, `gha-api-staging`); do not share a super-role.
- **Node.js / FastAPI**: roles for ECR push + ECS/EC2 deploy. The runtime app has a *different* role (task/instance role) with only DynamoDB/S3/Secrets read it needs.
- **React**: `s3:PutObject/DeleteObject/ListBucket` on one bucket + `cloudfront:CreateInvalidation` on one distribution.
- **Nginx / VPS**: a VPS outside AWS cannot use IAM roles directly; it needs an IAM user key or IAM Roles Anywhere. Prefer moving to EC2 roles.
- **Separate accounts** for dev/staging/prod (AWS Organizations) is the strongest isolation.

```bash
# find unused permissions after a few weeks (Access Analyzer / last-accessed data)
aws iam generate-service-last-accessed-details --arn arn:aws:iam::111122223333:role/gha-orders-api-deploy   # returns a JobId
aws iam get-service-last-accessed-details --job-id <JobId>   # shows which services were actually used
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `AdministratorAccess` or `Action: "*"` on the CI role.
✅ Correct: Start from the minimal list and add on AccessDenied.

❌ Mistake 2: Trust policy with `sub: repo:myorg/*` or no `sub` condition at all.
✅ Correct: Pin the exact repo and branch/environment; anyone's repo can otherwise get a token and assume your role.

❌ Mistake 3: `iam:PassRole` on `*`.
✅ Correct: Limit to the specific task/execution role ARNs with `iam:PassedToService`.

❌ Mistake 4: One role shared by PR workflows and deploy workflows.
✅ Correct: PR builds get a read-only role or none; only `main`/protected environments assume the deploy role.

❌ Mistake 5: Never reviewing permissions again.
✅ Correct: Quarterly review with last-accessed data and CloudTrail.

---

## 🧠 Tricky Interview Question
Your pipeline role can only `ecs:UpdateService`. A developer with write access to the repo adds a step that registers a task definition running as an admin role. Can they escalate privileges?

Answer: Only if the CI role has `iam:PassRole` to a powerful role (and `ecs:RegisterTaskDefinition`/`RunTask`). `PassRole` is the classic privilege escalation path. With PassRole restricted to the app's own task role (and nothing else), the pipeline cannot hand a stronger role to a task. Also use branch protection and environments, so an arbitrary branch cannot assume the deploy role.

---

## ⚫ Interview Questions + Answers

Q1: Trust policy vs permissions policy?
A1: Trust policy = who can assume the role (principal + conditions). Permissions policy = what the role can do once assumed. Both must be correct.

Q2: IAM user vs IAM role for CI?
A2: User means long-lived access keys that can leak. Role gives temporary credentials (STS), automatically expiring, tied to conditions. Prefer roles with OIDC.

Q3: What is an explicit deny and where does it help?
A3: `Effect: Deny` always wins over Allow. Use it (or Service Control Policies) as guardrails, e.g. deny `iam:*` and `s3:DeleteBucket` for CI roles.

Q4: What is a permissions boundary?
A4: A cap on the maximum permissions a role can ever have, so even if someone attaches a wide policy, the boundary limits the effective permissions.

Q5: How do you debug AccessDenied?
A5: Read the error (it names the action and resource), check CloudTrail for the denied event, use the IAM Policy Simulator, and confirm there is no SCP or boundary blocking it.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any pipeline touching AWS (always)
- Multiple teams or environments share an account
- Compliance requires audit of who can change prod

❌ Avoid when:
- Never skip it; the only anti-pattern is over-broad policies or shared admin keys

---

## 📊 Visual Diagram
```
 GitHub workflow (repo myorg/api, env production)
      | OIDC JWT (sub, aud)
      v
 +--------------------------+      checks      +----------------------+
 |  AWS STS                 | ---------------> |  Trust policy        |
 |  AssumeRoleWithWebIdentity|                 |  aud + sub match?    |
 +------------+-------------+                  +----------------------+
              | temporary credentials (1h)
              v
 +--------------------------+     allowed?     +----------------------+
 |  Role: gha-api-deploy    | ---------------> |  Permissions policy  |
 |  (session)               |                  |  ecr/ecs on named ARNs|
 +--------------------------+                  +----------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| IAM Role | Identity with temporary credentials | अस्थायी credentials वाली पहचान |
| Trust policy | Who may assume the role | कौन role assume कर सकता है |
| Permissions policy | What the role can do | role क्या कर सकता है |
| Least privilege | Minimum access needed | न्यूनतम ज़रूरी access |
| PassRole | Permission to give a role to a service | किसी service को role देने की permission |
| STS | Service issuing temporary credentials | अस्थायी credentials देने वाली service |
| SCP | Org-level permission guardrail | Org स्तर की permission सीमा |

---

## ⚡ 3-Line Summary
English: Give each pipeline its own IAM role with a trust policy tied to your repo and a narrow permissions policy.
English: Avoid admin rights, wildcard PassRole and long-lived user keys.
English: Review with CloudTrail and last-accessed data regularly.
Hindi: हर pipeline को अपना IAM role दें, trust policy आपके repo से बँधी और permissions policy संकरी।
Hindi: Admin rights, wildcard PassRole और लंबी उम्र वाली user keys से बचें।
Hindi: CloudTrail और last-accessed data से नियमित review करें।

---

## ➡️ Next Topic
**394. OIDC Authentication (No Long-lived Keys)**: we used OIDC in the trust policy here; next we set up the provider and the workflow step by step.
