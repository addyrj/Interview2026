# 394. OIDC Authentication (No Long-lived Keys)
# हिंदी में: OIDC Authentication (बिना लंबी उम्र वाली Keys के)

---

## 🔵 Simple Definition (English)
**OIDC (OpenID Connect)** lets a GitHub Actions job prove its identity to AWS with a short-lived signed token (a JWT) instead of a stored access key. AWS verifies the token, checks your **trust policy** (repo, branch, environment), and hands back **temporary credentials** (valid about 1 hour). Nothing secret is stored in GitHub.

## 🔵 सरल परिभाषा (Hindi)
**OIDC (OpenID Connect)** से GitHub Actions job अपनी पहचान AWS को stored access key की जगह एक छोटी उम्र वाले signed token (JWT) से साबित करती है। AWS token verify करता है, आपकी **trust policy** (repo, branch, environment) जाँचता है, और **temporary credentials** (लगभग 1 घंटे के लिए) लौटाता है। GitHub में कोई secret store नहीं होता।

---

## 🔴 Problem it Solves
Long-lived `AWS_ACCESS_KEY_ID/SECRET` in GitHub secrets: they never expire, must be rotated by hand, get copied to laptops, show up in logs, and if leaked an attacker can use them from anywhere, any time. Rotating them breaks pipelines, so teams never do.

With OIDC: no secret to leak, credentials expire in an hour, and AWS can restrict "only this repo, only the main branch". This is the current AWS and GitHub recommended approach.

## 🔴 यह क्यों बना? (Hindi)
GitHub secrets में लंबी उम्र वाली `AWS_ACCESS_KEY_ID/SECRET`: ये कभी expire नहीं होतीं, हाथ से rotate करनी पड़ती हैं, laptops पर copy हो जाती हैं, logs में दिख सकती हैं, और leak हो जाएँ तो attacker कहीं से भी, कभी भी इस्तेमाल कर सकता है। Rotate करने पर pipelines टूटती हैं, इसलिए टीमें कभी करती ही नहीं।

OIDC में: leak होने को कोई secret नहीं, credentials एक घंटे में expire, और AWS "सिर्फ यह repo, सिर्फ main branch" की पाबंदी लगा सकता है। यही AWS और GitHub का आज का recommended तरीका है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → One-time: register GitHub as an OIDC identity provider in AWS IAM
         (URL https://token.actions.githubusercontent.com, audience sts.amazonaws.com)
Step 2 → One-time: create IAM role with trust policy (aud + sub conditions)
Step 3 → Workflow sets "permissions: id-token: write"
Step 4 → Job asks GitHub's token service for a JWT
         (claims: repo, ref, environment, workflow, actor, sha ...)
Step 5 → configure-aws-credentials sends JWT to AWS STS AssumeRoleWithWebIdentity
Step 6 → STS validates signature, aud, and the 'sub' against your trust policy
Step 7 → STS returns temporary AccessKey/Secret/SessionToken (about 1 hour)
Step 8 → Following steps use the AWS CLI/SDK normally; credentials vanish after the job
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → एक बार: AWS IAM में GitHub को OIDC identity provider की तरह register करें
         (URL https://token.actions.githubusercontent.com, audience sts.amazonaws.com)
Step 2 → एक बार: trust policy (aud + sub conditions) के साथ IAM role बनाएँ
Step 3 → Workflow में "permissions: id-token: write" रखें
Step 4 → Job GitHub की token service से JWT माँगती है
         (claims: repo, ref, environment, workflow, actor, sha ...)
Step 5 → configure-aws-credentials JWT को AWS STS AssumeRoleWithWebIdentity पर भेजता है
Step 6 → STS signature, aud और 'sub' को आपकी trust policy से verify करता है
Step 7 → STS temporary AccessKey/Secret/SessionToken लौटाता है (लगभग 1 घंटा)
Step 8 → आगे के steps में AWS CLI/SDK सामान्य चलता है; job के बाद credentials खत्म
```

---

## 🟡 Real World Example
A startup had `AWS_SECRET_ACCESS_KEY` in 14 repos. An intern's fork accidentally printed env vars in a debug workflow and the key appeared in a public log; within 20 minutes bots launched GPU instances worth thousands of dollars. After the incident they moved to OIDC: each repo got its own role, `sub` pinned to `repo:acme/api:ref:refs/heads/main`, all keys were deleted. A log leak now exposes nothing useful.

## 🟡 Real Example Hindi mein
एक startup की 14 repos में `AWS_SECRET_ACCESS_KEY` रखी थी। एक intern के fork के debug workflow ने गलती से env vars print कर दिए और key public log में आ गई; 20 मिनट में bots ने हज़ारों डॉलर के GPU instances चला दिए। घटना के बाद वे OIDC पर गए: हर repo को अपना role, `sub` को `repo:acme/api:ref:refs/heads/main` पर pinned, और सारी keys delete। अब log leak से कुछ काम का नहीं मिलता।

---

## 💻 Code / Config Example — Basic

One-time AWS setup with the CLI, then the minimal workflow.

```bash
# 1) Register GitHub as an OIDC provider (once per AWS account)
#    AWS now validates GitHub's certificate itself, but the CLI still wants a thumbprint argument in some versions.
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1   # example; check current GitHub docs value
```

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::111122223333:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:myorg/myrepo:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

```bash
# 2) Create the role using the trust policy saved as trust.json
aws iam create-role --role-name gha-myrepo-main --assume-role-policy-document file://trust.json
# 3) Attach the least-privilege permissions policy (see topic 393)
aws iam attach-role-policy --role-name gha-myrepo-main --policy-arn arn:aws:iam::111122223333:policy/gha-myrepo
```

```yaml
name: oidc-basic                                 # workflow name
on:
  push:
    branches: [main]                             # matches the ref in the trust policy
permissions:
  id-token: write                                # REQUIRED: lets the job request the OIDC JWT
  contents: read                                 # REQUIRED for checkout when you set permissions explicitly
jobs:
  whoami:
    runs-on: ubuntu-latest                       # runner
    steps:
      - uses: aws-actions/configure-aws-credentials@v4   # exchanges JWT for temporary credentials
        with:
          role-to-assume: arn:aws:iam::111122223333:role/gha-myrepo-main   # role to assume
          aws-region: ap-south-1                 # default region
      - run: aws sts get-caller-identity         # shows assumed-role ARN; proves success
```

## 💻 Code / Config Example — Advanced

Trust policy that separates **prod** (environment, with approval) from **PR builds** (read-only), plus workflow using environments. Also shows an organisation-wide pattern.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ProdOnlyFromProductionEnvironment",
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::111122223333:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:myorg/api:environment:production"
        }
      }
    }
  ]
}
```

For a read-only PR role use a different role whose `sub` is `repo:myorg/api:pull_request` (for pull_request events with no environment). Never let `pull_request` from forks assume a write role.

```yaml
name: ci-cd                                      # workflow name
on:
  pull_request:                                  # PR: run checks only
    branches: [main]
  push:
    branches: [main]                             # main: deploy
permissions:
  id-token: write                                # OIDC token allowed
  contents: read                                 # checkout allowed
jobs:
  test:
    runs-on: ubuntu-latest                       # runner
    steps:
      - uses: actions/checkout@v4                # code
      - run: npm ci && npm test                  # no AWS needed for tests at all
  deploy:
    needs: test                                  # only after tests pass
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'   # never on PRs
    runs-on: ubuntu-latest
    environment: production                      # sub becomes ...:environment:production ; can require reviewers
    steps:
      - uses: aws-actions/configure-aws-credentials@v4   # assume the prod role
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}   # not secret; use a repo/environment variable
          aws-region: ap-south-1
          role-session-name: gha-${{ github.run_id }}       # shows in CloudTrail to trace which run
          role-duration-seconds: 1800                       # shorter than default for safety
      - run: aws sts get-caller-identity         # sanity check
```

Note: when a job uses `environment:`, the token `sub` claim becomes `repo:ORG/REPO:environment:NAME`, not the `ref:` form. Mixing the two in the trust policy is the most common failure. You can list both values in a `StringEquals` array if you need both.

---

## 🟠 My Stack Integration
- **Node.js / FastAPI / React workflows**: replace every `AWS_ACCESS_KEY_ID` secret with `role-to-assume`. The ECR, ECS, S3, CloudFront steps in this section all assume this.
- **Docker build and push**: `aws-actions/amazon-ecr-login` works with the OIDC session; no `docker login` password secret.
- **Nginx / VPS (non-AWS)**: OIDC works for AWS APIs only. For a VPS you still need SSH keys or a deploy agent; keep them in environment-scoped secrets, and consider moving the target to EC2 + SSM.
- **Terraform** (topic 400): the same role is used by `terraform` through the AWS provider environment.
- **Other clouds**: Azure, GCP, Vault, and Kubernetes also support GitHub OIDC with the same idea.

```yaml
# workflow-level hardening: pin the third-party action to a full commit SHA (supply-chain safety)
# - uses: aws-actions/configure-aws-credentials@<full-40-char-commit-sha>  # copy the SHA of the release you reviewed
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting `permissions: id-token: write`; error "Could not load credentials" / "Credentials could not be loaded".
✅ Correct: Add it at workflow or job level.

❌ Mistake 2: Trust policy `sub` of `repo:myorg/*` (any repo in the org) or `StringLike` with `*`.
✅ Correct: Exact repo + branch or environment.

❌ Mistake 3: Using `ref:refs/heads/main` in trust policy but the job has `environment: production`.
✅ Correct: Match the actual `sub` (`...:environment:production`). Print the token claims with a debug step (without exposing the token) to confirm.

❌ Mistake 4: Trust policy missing the `aud` condition.
✅ Correct: Always require `aud = sts.amazonaws.com`.

❌ Mistake 5: Setting `permissions:` at top and forgetting `contents: read`; checkout then fails.
✅ Correct: When you define any permission, all others become `none`; list what you need.

---

## 🧠 Tricky Interview Question
With OIDC, an attacker opens a pull request from a fork that modifies the workflow to run `aws s3 rm --recursive`. Does AWS give them credentials?

Answer: By default, workflows triggered by `pull_request` from forks run with a read-only token and do not get `id-token: write`, so no OIDC token is issued. The real risks are `pull_request_target` (runs trusted workflow with secrets and a token on untrusted code) and a trust policy that allows too much. Defences: never check out and run PR code under `pull_request_target` with credentials, require environment approvals, and pin `sub` to protected branches/environments.

---

## ⚫ Interview Questions + Answers

Q1: Why is OIDC better than access keys?
A1: No stored secret, credentials are short-lived, can be scoped by repo/branch/environment, and every session is attributable in CloudTrail.

Q2: What does the `sub` claim contain?
A2: Examples: `repo:ORG/REPO:ref:refs/heads/main`, `repo:ORG/REPO:environment:production`, `repo:ORG/REPO:pull_request`, `repo:ORG/REPO:ref:refs/tags/v1.0`. The format can be customised at repo/org level.

Q3: How long do the credentials last?
A3: Default session is 1 hour (role max session can be changed). The action's `role-duration-seconds` can shorten it.

Q4: Does the token itself get stored?
A4: No. It is minted per job request, valid for minutes, and cannot be reused elsewhere because `aud` and signature are validated.

Q5: How do you migrate from keys?
A5: Create provider + role, switch one workflow, verify with `get-caller-identity`, then delete the secrets and deactivate the IAM user keys.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any GitHub Actions to AWS access (default choice)
- You have compliance or audit requirements
- Multiple repos and environments need separate permissions

❌ Avoid when:
- Self-hosted CI without OIDC support (use short-lived keys via IAM Roles Anywhere)
- Target is not AWS-compatible with web identity (a plain VPS): use SSH keys with strict scopes

---

## 📊 Visual Diagram
```
 +---------------------+  1. request JWT   +------------------------------+
 | GitHub Actions job  | ----------------> | GitHub OIDC token service    |
 | (id-token: write)   | <---------------- | (signs JWT: sub, aud, repo)  |
 +----------+----------+  2. JWT           +------------------------------+
            | 3. AssumeRoleWithWebIdentity (JWT)
            v
 +-------------------------+  4. check aud/sub   +------------------+
 | AWS STS                 | ------------------> | Role trust policy|
 +-----------+-------------+                     +------------------+
             | 5. temp creds (1h)
             v
 +-------------------------+
 | aws cli / sdk in job    |  -> ECR, ECS, S3, CloudFront ...
 +-------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OIDC | Identity protocol on top of OAuth2 | OAuth2 के ऊपर identity protocol |
| JWT | Signed JSON token with claims | claims वाला signed JSON token |
| Claim `sub` | Who the token represents | token किसका है |
| Claim `aud` | Who the token is meant for | token किसके लिए है |
| STS | Issues temporary credentials | अस्थायी credentials जारी करता है |
| Identity provider | Trusted token issuer in IAM | IAM में भरोसेमंद token जारीकर्ता |

---

## ⚡ 3-Line Summary
English: OIDC swaps a signed GitHub token for 1-hour AWS credentials, so no access keys are stored.
English: The trust policy must pin `aud` and an exact `sub` (repo plus branch or environment).
English: Remember `permissions: id-token: write` and delete the old IAM user keys.
Hindi: OIDC GitHub के signed token को 1 घंटे के AWS credentials से बदलता है, इसलिए कोई access key store नहीं होती।
Hindi: Trust policy में `aud` और सटीक `sub` (repo + branch या environment) pin होना चाहिए।
Hindi: `permissions: id-token: write` याद रखें और पुरानी IAM user keys delete करें।

---

## ➡️ Next Topic
**395. AWS Secrets in GitHub Actions**: authentication solved, now the app needs secrets (DB passwords, API keys); we compare GitHub Secrets and AWS Secrets Manager.
