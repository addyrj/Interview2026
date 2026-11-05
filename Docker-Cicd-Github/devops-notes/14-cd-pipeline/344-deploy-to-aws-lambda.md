# 344. Deploy to AWS Lambda
# हिंदी में: AWS Lambda पर Deploy करना

---

## 🔵 Simple Definition (English)
AWS Lambda runs your function only when invoked (HTTP via API Gateway/Function URL, SQS, cron) and bills per millisecond. In CI/CD you either upload a **zip** (`aws lambda update-function-code --zip-file`) or point the function at a **container image in ECR**, then publish a **version** and move an **alias** to it.

## 🔵 सरल परिभाषा (Hindi)
AWS Lambda आपका function सिर्फ call होने पर चलाता है (API Gateway/Function URL, SQS, cron से) और millisecond के हिसाब से bill करता है। CI/CD में आप **zip** upload करते हैं (`aws lambda update-function-code --zip-file`) या function को ECR की **container image** पर लगाते हैं, फिर **version** publish करके **alias** उस पर ले जाते हैं।

---

## 🔴 Problem it Solves
Always-on servers cost money while idle and need scaling and patching. Lambda scales to zero and automatically to thousands of concurrent runs. The deploy problem it adds: you must update code safely, keep older versions for rollback, and shift traffic gradually; versions and aliases solve that.

## 🔴 यह क्यों बना? (Hindi)
हमेशा चालू servers idle रहने पर भी पैसे लेते हैं और scaling व patching माँगते हैं। Lambda शून्य तक scale होता है और अपने आप हज़ारों concurrent runs तक जाता है। नई चुनौती: code सुरक्षित update हो, rollback के लिए पुराने versions रहें और traffic धीरे-धीरे शिफ्ट हो; versions और aliases यही हल करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Install deps and test the function in CI
Step 2 → Package: zip (npm ci --omit=dev) OR build container image to ECR
Step 3 → OIDC role: lambda:UpdateFunctionCode, PublishVersion, UpdateAlias
Step 4 → aws lambda update-function-code (wait until LastUpdateStatus=Successful)
Step 5 → aws lambda publish-version → immutable version N
Step 6 → aws lambda update-alias --name live --function-version N
Step 7 → Smoke test via alias; rollback = point alias to N-1
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → CI में dependencies install करके function test करो।
Step 2 → Package: zip (`npm ci --omit=dev`) या ECR पर container image।
Step 3 → OIDC role: `lambda:UpdateFunctionCode`, `PublishVersion`, `UpdateAlias`।
Step 4 → `update-function-code` चलाओ और `LastUpdateStatus=Successful` तक रुको।
Step 5 → `publish-version` से immutable version N बनता है।
Step 6 → `update-alias --name live --function-version N` से traffic नए version पर।
Step 7 → Alias से smoke test; rollback यानी alias को N-1 पर वापस ले जाना।

---

## 🟡 Real World Example
A Swiggy-like team uses Lambda for an image-resize worker (S3 event) and a webhook receiver. Traffic is spiky (festival sales), so Lambda scales instantly and costs near zero overnight. Each deploy publishes a version; the `live` alias is shifted to the new version, and a CloudWatch alarm on errors triggers a revert of the alias.

## 🟡 Real Example Hindi mein
Swiggy जैसी team image-resize worker (S3 event) और webhook receiver के लिए Lambda इस्तेमाल करती है। Traffic अचानक बढ़ता है (festival sale), Lambda तुरंत scale होता है और रात में लगभग मुफ्त। हर deploy में version बनता है; `live` alias नए version पर जाता है, और error alarm आने पर alias वापस पिछले version पर कर दिया जाता है।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/deploy-lambda-basic.yml (zip upload)
name: deploy-lambda-basic              # workflow name
on:
  push:
    branches: [main]                   # deploy on main
permissions:
  id-token: write                      # OIDC
  contents: read
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4      # get code
      - uses: actions/setup-node@v4    # install Node
        with:
          node-version: 20
      - run: npm ci --omit=dev         # production dependencies only
      - run: zip -r function.zip index.js node_modules   # package the function
      - uses: aws-actions/configure-aws-credentials@v4   # OIDC login
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-lambda-deploy  # example
          aws-region: ap-south-1
      - name: Update code              # upload the new zip
        run: aws lambda update-function-code --function-name webhook-handler --zip-file fileb://function.zip
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/deploy-lambda.yml (zip, version, alias, smoke test, rollback)
name: deploy-lambda
on:
  push:
    branches: [main]
permissions:
  id-token: write
  contents: read
env:
  FUNCTION: webhook-handler            # Lambda function name
  ALIAS: live                          # alias used by API Gateway / Function URL
  AWS_REGION: ap-south-1
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm                   # cache npm downloads
      - run: npm ci                    # full install for tests
      - run: npm test                  # gate: tests must pass
      - run: |                         # rebuild with prod deps for the package
          rm -rf node_modules
          npm ci --omit=dev
          zip -qr function.zip index.js package.json node_modules
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE }}
          aws-region: ${{ env.AWS_REGION }}
      - name: Upload and publish version
        id: pub
        run: |
          aws lambda update-function-code --function-name "$FUNCTION" \
            --zip-file fileb://function.zip > /dev/null          # upload code
          aws lambda wait function-updated --function-name "$FUNCTION"   # wait until ready
          VERSION=$(aws lambda publish-version --function-name "$FUNCTION" \
            --description "sha ${GITHUB_SHA::7}" --query Version --output text)  # immutable
          PREV=$(aws lambda get-alias --function-name "$FUNCTION" --name "$ALIAS" \
            --query FunctionVersion --output text)               # current live version
          echo "version=$VERSION" >> "$GITHUB_OUTPUT"
          echo "prev=$PREV" >> "$GITHUB_OUTPUT"
      - name: Point alias to new version
        run: aws lambda update-alias --function-name "$FUNCTION" --name "$ALIAS" --function-version "${{ steps.pub.outputs.version }}"
      - name: Smoke test, rollback on failure
        run: |
          aws lambda invoke --function-name "$FUNCTION:$ALIAS" \
            --payload '{"ping":true}' --cli-binary-format raw-in-base64-out out.json  # call live alias
          grep -q '"statusCode": *200' out.json || {
            echo "smoke test failed, reverting alias"
            aws lambda update-alias --function-name "$FUNCTION" --name "$ALIAS" \
              --function-version "${{ steps.pub.outputs.prev }}"   # rollback
            exit 1
          }
```

For gradual shifting, `update-alias --routing-config AdditionalVersionWeights={"<new>"=0.1}` sends 10% to the new version (use CodeDeploy for automated canaries). The smoke test assumes your handler returns `{"statusCode":200,...}`; adjust to your handler.

---

## 🟠 My Stack Integration
Node.js handlers fit natively. For FastAPI, wrap with Mangum and ship as a container image (zip limit is 250 MB unzipped, image up to 10 GB):

```dockerfile
# Dockerfile for FastAPI on Lambda (AWS Lambda Python base image, example tag)
FROM public.ecr.aws/lambda/python:3.12
# install dependencies into the Lambda task root
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r requirements.txt
# copy application code
COPY app/ ${LAMBDA_TASK_ROOT}/app/
# handler = module.function exported with Mangum(app)
CMD ["app.main.handler"]
```

Then update with `aws lambda update-function-code --function-name api --image-uri <ecr-uri>:<sha>`. Nginx is not needed: API Gateway or a Function URL fronts it, and React ships to S3/CloudFront.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Invoking `publish-version` immediately after `update-function-code`, getting `ResourceConflictException`.
✅ Correct: `aws lambda wait function-updated` first.

❌ Mistake 2: API Gateway pointed at `$LATEST`.
✅ Correct: Point it at an alias so versions are immutable and rollback is instant.

❌ Mistake 3: Bundling dev dependencies and huge packages (slow cold start).
✅ Correct: `npm ci --omit=dev`, bundle with esbuild.

❌ Mistake 4: Secrets in environment variables in the workflow.
✅ Correct: Use Secrets Manager/SSM Parameter Store and fetch at init.

---

## 🧠 Tricky Interview Question
After deploy, the alias points to version 12 but the function still behaves like version 11 for some requests. Why?

Answer: Existing execution environments (warm containers) of the old version can still serve in-flight and queued invocations, and an alias with **weighted routing** sends a share to the previous version. Also, provisioned concurrency is bound to a version/alias and must be moved. Check the alias routing config and provisioned concurrency.

---

## ⚫ Interview Questions + Answers

Q1: What is a cold start and how to reduce it?
A1: Initialization of a new execution environment. Reduce with smaller packages, lighter runtimes, provisioned concurrency, SnapStart (Java), and keeping init code light.

Q2: Version vs alias?
A2: A version is an immutable snapshot; an alias is a movable pointer to a version.

Q3: Zip vs container image?
A3: Zip: simple, fast for small functions. Image: larger deps (ML libs), same Docker tooling, up to 10 GB.

Q4: How do you do canary deploys?
A4: Alias weighted routing or CodeDeploy with Canary/Linear configs and alarms.

Q5: What are Lambda's limits that affect design?
A5: 15-minute max duration, memory 128 MB to 10 GB, payload limits, and concurrency quotas.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Spiky or low traffic, event-driven jobs, webhooks, cron.
- You want near-zero ops cost.

❌ Avoid when:
- Long-running or stateful processes (>15 min), WebSockets with heavy state.
- Constant high load where containers are cheaper.
- Latency-critical with no budget for provisioned concurrency.

---

## 📊 Visual Diagram
```
 push main ─► tests ─► package (zip / image)
                          │ update-function-code
                          ▼
                    $LATEST  ──publish-version──►  v12 (immutable)
                                                     ▲
   API Gateway / Function URL ─► alias "live" ───────┘  (was v11)
                                      │ smoke test fails?
                                      └──► alias back to v11 (rollback)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Function | Unit of code run on demand | माँग पर चलने वाला code |
| Version | Immutable snapshot | अपरिवर्तनीय snapshot |
| Alias | Named pointer to a version | version का नाम-सूचक |
| Cold start | New environment init delay | पहली बार शुरू होने की देरी |
| Provisioned concurrency | Pre-warmed instances | पहले से गर्म instances |
| Mangum | ASGI adapter for Lambda | FastAPI को Lambda पर चलाने वाला |

---

## ⚡ 3-Line Summary
English: Package, update code, wait, publish a version and move an alias. Roll back by moving the alias. Use images for big dependencies like FastAPI/ML.
Hindi: Package बनाओ, code update करो, इंतज़ार करो, version publish करके alias चलाओ। Rollback में alias वापस ले जाओ। FastAPI/ML के लिए image इस्तेमाल करो।

---

## ➡️ Next Topic
**345. Deploy to Kubernetes** - deploy to a cluster with kubectl, manifests and rollout checks.
