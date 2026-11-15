---

# 86. Lambda Function Setup
# AWS: Lambda (IAM role + zip/container deploy)
# Azure: Azure Functions (Function App)
# हिंदी में: लैम्ब्डा फ़ंक्शन बनाना

---

## 🔵 Simple Definition (2 lines)
Setting up Lambda means: write the handler, create an execution role, package the code, create the function, and test-invoke it.
हिंदी: Lambda सेटअप = हैंडलर लिखो, IAM रोल बनाओ, कोड पैकेज करो, फ़ंक्शन बनाओ और टेस्ट करो।

---

## 🔴 Why it Exists (2 lines)
Lambda needs to know who it runs as (role), what code, which runtime and where the entry point is. Skipping any gives deploy or permission errors.

---

## 🟢 How it Works
```
1. Write handler (index.mjs)
2. Create IAM role (trust: lambda.amazonaws.com + AWSLambdaBasicExecutionRole)
3. zip function.zip index.mjs
4. aws lambda create-function --runtime nodejs20.x --handler index.handler --role <arn>
5. aws lambda invoke --function-name hello out.json
6. CI/CD: GitHub Actions runs update-function-code on push
```

---

## 💻 Code / Config Example
```bash
# AWS CLI v2 (needs real credentials; not run here)
cat > trust.json <<'EOF'
{"Version":"2012-10-17","Statement":[{"Effect":"Allow",
 "Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}
EOF

aws iam create-role --role-name hello-lambda-role \
  --assume-role-policy-document file://trust.json
aws iam attach-role-policy --role-name hello-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

zip function.zip index.mjs
aws lambda create-function --function-name hello \
  --runtime nodejs20.x --handler index.handler \
  --role arn:aws:iam::123456789012:role/hello-lambda-role \
  --zip-file fileb://function.zip

aws lambda invoke --function-name hello --payload '{}' \
  --cli-binary-format raw-in-base64-out out.json && cat out.json
```
```yaml
# .github/workflows/deploy.yml (deploy on push)
name: deploy-lambda
on: { push: { branches: [main] } }
permissions: { id-token: write, contents: read }
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-deploy
          aws-region: ap-south-1
      - run: zip function.zip index.mjs
      - run: aws lambda update-function-code --function-name hello --zip-file fileb://function.zip
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Container | Function | Function App (hosts many functions) |
| Identity | Execution role | Managed identity |
| Deploy | zip / container image / SAM | zip deploy / Core Tools / container |
| Pricing | Pay per request + duration (approximate — check current docs) | Consumption plan similar (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Wrong handler string (e.g. `handler` instead of `index.handler`).
✅ Correct: Format is `<file>.<exportedFunction>`.

❌ Mistake: Long-lived access keys in GitHub secrets.
✅ Correct: Use OIDC role assumption as above.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is an execution role?
A1: IAM role Lambda assumes to call other AWS services and write logs.

Q2: [Medium] Zip vs container image?
A2: Zip is simpler and small (up to 250 MB unzipped); container image allows up to 10 GB and custom runtimes/dependencies.

Q3: [Hard] How to deploy safely?
A3: Publish immutable versions, point an alias, shift traffic gradually (weighted alias / CodeDeploy), and roll back by moving the alias.

---

## ✅ Quick Checklist
□ Correct runtime and handler
□ Role has only needed permissions
□ CI uses OIDC, not static keys

---

## ⚡ 1-Line Summary
Setup = code + role + package + create-function | सेटअप = कोड + रोल + पैकेज + फ़ंक्शन बनाना।

## ➡️ Next: Lambda Triggers

---
