# 377. Authenticate to ECR
# हिंदी में: ECR में Authenticate (Login) करना

---

## 🔵 Simple Definition (English)
Authenticating to ECR means getting a temporary password (valid 12 hours) from AWS using your IAM identity and giving it to Docker, so Docker is allowed to push or pull images. The username is always `AWS`.

## 🔵 सरल परिभाषा (Hindi)
ECR में authenticate करने का मतलब है अपनी IAM identity से AWS से एक temporary password (12 घंटे valid) लेना और Docker को देना, ताकि Docker images push या pull कर सके। Username हमेशा `AWS` होता है।

---

## 🔴 Problem it Solves
- Docker does not understand IAM. ECR needs a bridge between AWS identity and Docker's username/password login.
- Storing permanent passwords in CI is a security risk; a leaked static key gives long-term access.
- Different callers need different methods: a laptop, GitHub Actions, an ECS task, a VPS.

## 🔴 यह क्यों बना? (Hindi)
- Docker IAM को नहीं समझता। ECR को AWS identity और Docker के username/password login के बीच bridge चाहिए।
- CI में permanent password रखना security risk है; leak हुई static key से लंबे समय का access मिलता है।
- अलग callers के लिए अलग तरीके: laptop, GitHub Actions, ECS task, VPS।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Caller has AWS credentials (SSO, IAM role, or OIDC role from GitHub)
Step 2 → Call ecr:GetAuthorizationToken (aws ecr get-login-password)
Step 3 → AWS returns a base64 token valid for 12 hours
Step 4 → docker login --username AWS --password-stdin <registry>
Step 5 → Docker stores token in ~/.docker/config.json for that registry host
Step 6 → push/pull work until token expires -> repeat step 2
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Caller के पास AWS credentials हों (SSO, IAM role या GitHub का OIDC role)
Step 2 → ecr:GetAuthorizationToken call (aws ecr get-login-password)
Step 3 → AWS 12 घंटे valid base64 token देता है
Step 4 → docker login --username AWS --password-stdin <registry>
Step 5 → Docker token को ~/.docker/config.json में उस registry host के लिए रखता है
Step 6 → Token expire होने तक push/pull चलेगा -> फिर step 2 दोहराओ
```

---

## 🟡 Real World Example
A team had `AWS_ACCESS_KEY_ID` and secret stored in GitHub secrets for 2 years. A former contractor still had the key in his laptop history. The security team moved to OIDC: GitHub proves who it is with a short-lived token, AWS trusts only `repo:acme/shop:ref:refs/heads/main`, and the role can only push to one ECR repo. Now no static key exists to leak.

## 🟡 Real Example Hindi mein
एक team की GitHub secrets में 2 साल से `AWS_ACCESS_KEY_ID` और secret रखा था। पुराने contractor के laptop history में वही key थी। Security team ने OIDC अपनाया: GitHub short-lived token से अपनी पहचान साबित करता है, AWS सिर्फ `repo:acme/shop:ref:refs/heads/main` पर भरोसा करता है, और role सिर्फ एक ECR repo में push कर सकता है। अब leak होने के लिए कोई static key ही नहीं।

---

## 💻 Code / Config Example — Basic

```bash
# ecr-login-basic.sh  - login from a laptop or VPS
set -euo pipefail                                     # exit on any error
REGION=ap-south-1                                     # region of your registry
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)   # find account id (also proves creds work)
aws ecr get-login-password --region "$REGION" \
 | docker login --username AWS --password-stdin "$ACCOUNT.dkr.ecr.$REGION.amazonaws.com"
# the pipe keeps the password out of shell history and process list (never use -p on the command line)
```

## 💻 Code / Config Example — Advanced
GitHub Actions with OIDC. First the IAM trust policy, then the workflow.

```yaml
# trust-policy.yml  - CloudFormation for the role GitHub assumes
AWSTemplateFormatVersion: "2010-09-09"             # template version
Resources:
  GithubOidc:
    Type: AWS::IAM::OIDCProvider                    # tell AWS to trust GitHub tokens
    Properties:
      Url: https://token.actions.githubusercontent.com   # GitHub's OIDC issuer
      ClientIdList: [sts.amazonaws.com]             # audience AWS expects
  PushRole:
    Type: AWS::IAM::Role                            # role the workflow will assume
    Properties:
      RoleName: gha-ecr-push                        # name used in role-to-assume
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Federated: !Ref GithubOidc            # trust the provider above
            Action: sts:AssumeRoleWithWebIdentity   # OIDC style assume
            Condition:
              StringEquals:
                token.actions.githubusercontent.com:aud: sts.amazonaws.com   # audience check
              StringLike:
                token.actions.githubusercontent.com:sub: repo:acme/shop:ref:refs/heads/main   # ONLY this repo+branch
      Policies:
        - PolicyName: ecr-push-one-repo
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action: ecr:GetAuthorizationToken   # needed for login, cannot be scoped
                Resource: "*"
              - Effect: Allow
                Action:                              # minimum set to push layers and manifest
                  - ecr:BatchCheckLayerAvailability
                  - ecr:InitiateLayerUpload
                  - ecr:UploadLayerPart
                  - ecr:CompleteLayerUpload
                  - ecr:PutImage
                Resource: arn:aws:ecr:ap-south-1:123456789012:repository/myapp-api   # only this repo
```

```yaml
# .github/workflows/ecr-login.yml
name: ecr-login-demo                    # workflow name
on: workflow_dispatch                   # manual trigger for the demo
permissions:
  id-token: write                       # allow GitHub to mint an OIDC token
  contents: read                        # allow checkout
jobs:
  login:
    runs-on: ubuntu-latest              # runner
    steps:
      - uses: aws-actions/configure-aws-credentials@v4     # exchange OIDC token for temp AWS creds (example version)
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-ecr-push   # role from above
          aws-region: ap-south-1        # registry region
      - id: ecr                         # id lets us read outputs
        uses: aws-actions/amazon-ecr-login@v2              # runs docker login for you
      - run: echo "Logged in to ${{ steps.ecr.outputs.registry }}"   # prints registry host (not a secret)
```

---

## 🟠 My Stack Integration
- GitHub Actions: OIDC as above, for the Node/FastAPI image build.
- ECS: no login; the task execution role pulls.
- VPS with Docker Compose: use the credential helper so you never refresh manually.

```bash
# on the VPS (Ubuntu): install helper, then tell Docker to use it for your registry
sudo apt-get install -y amazon-ecr-credential-helper          # package name on Ubuntu 22.04+
mkdir -p ~/.docker                                            # docker config folder
cat > ~/.docker/config.json <<'EOF'
{ "credHelpers": { "123456789012.dkr.ecr.ap-south-1.amazonaws.com": "ecr-login" } }
EOF
# the helper reads AWS creds from ~/.aws or an instance role; use a pull-only IAM user/role here
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `docker login -p <token>` on the command line.
✅ Correct: `--password-stdin` so it never lands in history or `ps`.

❌ Mistake 2: Storing admin AWS keys in CI.
✅ Correct: OIDC role scoped to one repo and the push actions only.

❌ Mistake 3: Missing `permissions: id-token: write` in the workflow.
✅ Correct: Add it, otherwise `configure-aws-credentials` fails with "Could not load credentials".

❌ Mistake 4: Trust policy with `sub: repo:acme/*:*`.
✅ Correct: Pin repo and branch (or environment) so forks and other branches cannot assume the role.

---

## 🧠 Tricky Interview Question
Your cron job refreshes the ECR login every 12 hours, yet pulls fail at hour 12 sharp for a few minutes. Why and how to fix?

Answer: The token lifetime is exactly 12 hours, and the cron fires at the same instant the token expires; a pull in that gap uses an expired token. Refresh more often (every 6 hours) or use the credential helper, which fetches a fresh token per request.

---

## ⚫ Interview Questions + Answers

Q1: Why is the username always AWS?
A1: ECR ignores the username identity; the token already encodes who you are. `AWS` is a fixed placeholder.

Q2: Which IAM permission is needed for login only?
A2: `ecr:GetAuthorizationToken`, which must be on resource `*`.

Q3: OIDC vs access keys in CI?
A3: OIDC gives short-lived credentials bound to repo and branch, nothing to rotate or leak. Keys are long-lived and often over-privileged.

Q4: How does an ECS task authenticate?
A4: The task execution role (not the task role) is used by the ECS agent to pull from ECR and write logs.

Q5: Can you log in to another account's registry?
A5: Yes if that repo's policy allows your principal, and you log in against that account's registry host.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any push or pull from ECR outside ECS/EKS
- Use OIDC for all GitHub Actions to AWS access

❌ Avoid when:
- Static keys in repo secrets if OIDC is available
- Public images that need no login

---

## 📊 Visual Diagram
```
 GitHub job --OIDC token--> AWS STS --temp creds--> job
 job --GetAuthorizationToken--> ECR --12h token--> docker login
 docker push/pull --(token)--> 123456789012.dkr.ecr.ap-south-1.amazonaws.com
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OIDC | Identity federation without static keys | बिना static key के identity |
| STS | AWS token service | AWS का temporary credential service |
| Execution role | Role ECS uses to pull images | Image pull करने वाला role |
| Credential helper | Docker plugin that fetches tokens on demand | Token खुद लाने वाला plugin |
| Token | 12 hour password for the registry | 12 घंटे का password |

---

## ⚡ 3-Line Summary
English: ECR login = IAM identity to a 12-hour token handed to Docker with username AWS.
Use OIDC in GitHub Actions, execution roles in ECS, credential helper on a VPS.
Scope permissions to one repo and never put the token on a command line.

Hindi: ECR login = IAM identity से 12 घंटे का token, Docker को username AWS के साथ देना।
GitHub Actions में OIDC, ECS में execution role, VPS पर credential helper इस्तेमाल करो।
Permissions एक repo तक सीमित रखो और token कभी command line पर मत लिखो।

---

## ➡️ Next Topic
378. Push Image to ECR: build, tag and push with a proper tagging strategy.
