# 391. AWS Lambda Deploy
# हिंदी में: AWS Lambda Deploy करना

---

## 🔵 Simple Definition (English)
**AWS Lambda** runs your code as functions without managing servers; you pay per request and per millisecond. Deploying Lambda from GitHub Actions means packaging the code (a **zip** or a **container image**), uploading it with the AWS CLI, then publishing an immutable **version** and moving an **alias** (like `prod`) to it.

## 🔵 सरल परिभाषा (Hindi)
**AWS Lambda** आपका code बिना server संभाले functions की तरह चलाता है; payment प्रति request और प्रति millisecond होता है। GitHub Actions से Lambda deploy का मतलब है code को (**zip** या **container image** में) package करना, AWS CLI से upload करना, फिर एक immutable **version** publish करके **alias** (जैसे `prod`) को उस पर ले जाना।

---

## 🔴 Problem it Solves
Uploading a zip by hand in the console has no history, no tests, no rollback, and people overwrite each other. Also `$LATEST` is mutable: if production points at `$LATEST`, any upload instantly changes live traffic.

With versions + aliases from CI, you test first, publish an immutable version, then shift the alias (optionally gradually), and rollback = point the alias to the old version number.

## 🔴 यह क्यों बना? (Hindi)
Console में हाथ से zip upload करने पर कोई history, test या rollback नहीं होता और लोग एक-दूसरे का काम overwrite कर देते हैं। साथ ही `$LATEST` mutable है: production उसी पर हो तो हर upload तुरंत live traffic बदल देता है।

CI से version + alias इस्तेमाल करने पर पहले test होता है, immutable version publish होता है, फिर alias shift होता है (चाहें तो धीरे-धीरे), और rollback = alias को पुराने version number पर ले जाना।

---

## 🟢 How it Works — Step by Step

```
Step 1 → CI installs deps and runs tests
Step 2 → CI packages: zip of code + production node_modules (or docker image -> ECR)
Step 3 → aws lambda update-function-code (upload)
Step 4 → aws lambda wait function-updated (code is ready)
Step 5 → aws lambda publish-version (freeze as immutable version N)
Step 6 → aws lambda update-alias --name prod --function-version N
         (optional: routing-config for 10% canary to N, 90% to N-1)
Step 7 → Smoke test the alias URL / invoke; rollback = alias back to N-1
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → CI dependencies install करके tests चलाता है
Step 2 → CI package बनाता है: code + production node_modules का zip (या docker image -> ECR)
Step 3 → aws lambda update-function-code (upload)
Step 4 → aws lambda wait function-updated (code तैयार)
Step 5 → aws lambda publish-version (immutable version N में freeze)
Step 6 → aws lambda update-alias --name prod --function-version N
         (optional: routing-config से 10% canary N पर, 90% N-1 पर)
Step 7 → Alias URL/invoke पर smoke test; rollback = alias को N-1 पर लौटाना
```

---

## 🟡 Real World Example
A Razorpay-style startup uses a Lambda `send-receipt-email` triggered by an SQS queue after each payment. Traffic is spiky (sales events), so Lambda scales to hundreds of concurrent runs and costs nearly zero at night. The pipeline publishes a version per commit and moves the `prod` alias with a 10% canary for 10 minutes while a CloudWatch alarm on `Errors` watches.

## 🟡 Real Example Hindi mein
एक Razorpay जैसा startup हर payment के बाद SQS queue से चलने वाला Lambda `send-receipt-email` इस्तेमाल करता है। Traffic spiky है (sales events), इसलिए Lambda सैकड़ों concurrent runs तक scale होता है और रात में लगभग zero cost। Pipeline हर commit पर version publish करती है और `prod` alias को 10 मिनट के लिए 10% canary के साथ move करती है, जबकि `Errors` पर CloudWatch alarm नज़र रखता है।

---

## 💻 Code / Config Example — Basic

A tiny Node.js handler and a simple deploy using the CLI.

```javascript
// index.js : Lambda handler (CommonJS, Node.js runtime)
exports.handler = async (event) => {             // Lambda calls this function
  const name = (event && event.name) || 'world'; // read input safely
  return {                                       // response for API Gateway / invoke
    statusCode: 200,                             // HTTP status
    body: JSON.stringify({ message: `Hello ${name}` }),   // JSON string body
  };
};
```

```yaml
name: lambda-basic                               # workflow name

on:
  push:
    branches: [main]                             # deploy on main

permissions:
  id-token: write                                # OIDC to AWS
  contents: read                                 # checkout

jobs:
  deploy:
    runs-on: ubuntu-latest                       # runner
    steps:
      - uses: actions/checkout@v4                # code
      - uses: aws-actions/configure-aws-credentials@v4   # OIDC login
        with:
          role-to-assume: arn:aws:iam::111122223333:role/gha-lambda-deploy
          aws-region: ap-south-1
      - run: zip -r function.zip index.js        # package the single file
      - run: aws lambda update-function-code --function-name hello-fn --zip-file fileb://function.zip   # upload code
      - run: aws lambda wait function-updated --function-name hello-fn   # wait until the update finishes
```

## 💻 Code / Config Example — Advanced

Test, build with production deps only, publish version, canary alias shift, smoke test, auto rollback on failure.

```yaml
name: lambda-prod                                # workflow name

on:
  push:
    branches: [main]                             # trigger

permissions:
  id-token: write                                # OIDC
  contents: read                                 # checkout

env:
  FN: send-receipt-email                         # Lambda function name
  ALIAS: prod                                    # alias that production traffic uses
  AWS_REGION: ap-south-1                         # region

jobs:
  deploy:
    runs-on: ubuntu-latest                       # runner
    environment: production                      # approval/protection
    concurrency: lambda-${{ github.ref }}        # avoid overlapping deploys
    steps:
      - uses: actions/checkout@v4                # code
      - uses: actions/setup-node@v4              # Node
        with:
          node-version: 20                       # match Lambda runtime (nodejs20.x)
          cache: npm                             # cache downloads
      - run: npm ci && npm test                  # tests before anything is uploaded
      - run: npm ci --omit=dev                   # reinstall only runtime deps for a smaller package
      - run: zip -qr function.zip index.js src node_modules   # package code + deps

      - uses: aws-actions/configure-aws-credentials@v4   # OIDC login
        with:
          role-to-assume: arn:aws:iam::111122223333:role/gha-lambda-deploy
          aws-region: ${{ env.AWS_REGION }}

      - name: Upload and publish version
        id: pub
        run: |
          aws lambda update-function-code --function-name "$FN" --zip-file fileb://function.zip >/dev/null   # upload
          aws lambda wait function-updated --function-name "$FN"          # code is ready
          NEW=$(aws lambda publish-version --function-name "$FN" --description "${GITHUB_SHA::7}" --query Version --output text)   # immutable version
          OLD=$(aws lambda get-alias --function-name "$FN" --name "$ALIAS" --query FunctionVersion --output text)   # current prod version
          echo "new=$NEW" >> "$GITHUB_OUTPUT"                              # save for later steps
          echo "old=$OLD" >> "$GITHUB_OUTPUT"

      - name: Canary 10 percent                  # alias still points to OLD, 10% goes to NEW
        run: |
          aws lambda update-alias --function-name "$FN" --name "$ALIAS" \
            --function-version "${{ steps.pub.outputs.old }}" \
            --routing-config "AdditionalVersionWeights={\"${{ steps.pub.outputs.new }}\"=0.1}"

      - name: Smoke test canary                  # invoke the alias (hits both versions by weight)
        run: |
          for i in 1 2 3 4 5 6 7 8 9 10; do
            aws lambda invoke --function-name "$FN:$ALIAS" --payload '{"ping":true}' --cli-binary-format raw-in-base64-out out.json >/dev/null   # call function
            grep -q '"statusCode":200' out.json || { echo "bad response"; cat out.json; exit 1; }   # fail on bad result
          done

      - name: Promote to 100 percent             # full cutover
        run: |
          aws lambda update-alias --function-name "$FN" --name "$ALIAS" \
            --function-version "${{ steps.pub.outputs.new }}" \
            --routing-config "AdditionalVersionWeights={}"

      - name: Rollback on failure                # runs only if an earlier step failed
        if: failure()
        run: |
          aws lambda update-alias --function-name "$FN" --name "$ALIAS" \
            --function-version "${{ steps.pub.outputs.old }}" \
            --routing-config "AdditionalVersionWeights={}"
```

Version-dependent: the Node runtime name (`nodejs20.x`, `nodejs22.x`) changes over time; check the Lambda supported-runtimes list. The smoke test assumes your function returns `{"statusCode":200,...}`.

---

## 🟠 My Stack Integration
- **Node.js**: ideal fit (fast cold start); keep handler small, reuse DB connections outside the handler, use RDS Proxy for SQL.
- **FastAPI**: possible with the **Lambda Web Adapter** or Mangum (ASGI adapter) in a container image; good for low/spiky traffic, worse for steady high traffic (cost, cold starts).
- **React**: Lambda is not for static files; use S3 + CloudFront, and Lambda only for API/edge needs.
- **Nginx / VPS**: no Nginx needed; API Gateway or Lambda Function URL is the front door. Keep long-running or websocket workloads on the VPS/ECS.
- **Secrets**: read from Secrets Manager / Parameter Store at cold start and cache in memory (topics 395/396), never zip `.env`.

```bash
# container-image variant (FastAPI): push image to ECR, then point the function at it
aws lambda update-function-code \
  --function-name fastapi-fn \
  --image-uri 111122223333.dkr.ecr.ap-south-1.amazonaws.com/fastapi-lambda:${GITHUB_SHA}   # image URI with immutable tag
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Production triggers point to `$LATEST`.
✅ Correct: Point triggers/API Gateway at an alias (`prod`) and move the alias.

❌ Mistake 2: Running `publish-version` right after `update-function-code` without waiting.
✅ Correct: `aws lambda wait function-updated` first, otherwise you get ResourceConflictException or an old code snapshot.

❌ Mistake 3: Zipping dev dependencies and tests (50 MB package, slow cold start).
✅ Correct: `npm ci --omit=dev`, or bundle with esbuild.

❌ Mistake 4: Giving the CI role `lambda:*` on `*`.
✅ Correct: Limit to the exact function ARNs and needed actions (topic 393).

❌ Mistake 5: Forgetting the 250 MB unzipped limit (zip) / 10 GB (image).
✅ Correct: Use layers, bundling or container images when you are near the limit.

---

## 🧠 Tricky Interview Question
You published version 12 and moved alias `prod` to it. The function now fails, you point the alias back to 11, but errors continue for a minute. Why?

Answer: Existing warm execution environments of version 12 may still be serving in-flight and already-routed requests; also event sources like SQS may have retries/batches in progress, and clients may cache DNS/connection. Alias updates are quick but not an instant kill of running invocations. Also if both versions write to the same DB schema, bad data from v12 may still cause errors in v11. So rollback is fast, not instantaneous; use canary weights to limit exposure.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a version and an alias?
A1: A version is an immutable snapshot of code + config. An alias is a named pointer (`prod`) to one version, or to two with weights, so triggers never change when you deploy.

Q2: What is a cold start and how do you reduce it?
A2: The time to create a new execution environment and init your code. Reduce with a smaller package, fewer imports, provisioned concurrency, SnapStart (Java), or ARM (Graviton) runtimes.

Q3: Zip vs container image?
A3: Zip is simpler and starts faster for small functions (limit 250 MB unzipped). Image allows up to 10 GB and your own base/tools, good for Python ML or FastAPI.

Q4: How do you do gradual deployment?
A4: Alias `routing-config` weights manually (as above), or AWS CodeDeploy for Lambda with `Canary10Percent5Minutes` / `Linear10PercentEvery1Minute` and alarms.

Q5: How do you deploy environment variables safely?
A5: Config in function environment (non-secret), secrets fetched from Secrets Manager/SSM at runtime or via encrypted env vars with KMS; never in git.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Event-driven or spiky workloads (queues, webhooks, cron, image resize)
- You want near-zero ops and pay-per-use
- Small APIs where cold start is acceptable

❌ Avoid when:
- Steady heavy traffic (ECS/EC2 usually cheaper)
- Long jobs over 15 minutes, or persistent websockets
- Tight latency SLAs without provisioned concurrency budget

---

## 📊 Visual Diagram
```
 GitHub Actions
   test -> zip/image -> update-function-code -> publish-version (N)
                                                    |
                                                    v
   Events (SQS / API GW / S3)          +-----------------------------+
          |                            | alias: prod                 |
          +--------------------------> |  90% -> version N-1         |
                                       |  10% -> version N  (canary) |
                                       +-----------------------------+
   Alarm on Errors? -> alias back to N-1 (rollback)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Function version | Immutable code snapshot | Code का immutable snapshot |
| Alias | Named pointer to a version | Version की तरफ नाम वाला pointer |
| Cold start | Startup delay of new environment | नए environment का शुरुआती delay |
| Layer | Shared library package | साझा library package |
| Provisioned concurrency | Pre-warmed environments | पहले से गर्म रखे environments |
| Execution role | IAM role the function runs as | function जिस IAM role से चलता है |

---

## ⚡ 3-Line Summary
English: Deploy Lambda by uploading code, waiting, publishing an immutable version and moving an alias.
English: Use canary weights and alarms for safe rollout; rollback is an alias change.
English: Keep packages small, secrets out of the zip, and CI permissions narrow.
Hindi: Lambda deploy = code upload, wait, immutable version publish और alias को move करना।
Hindi: सुरक्षित rollout के लिए canary weights और alarms इस्तेमाल करें; rollback सिर्फ alias बदलना है।
Hindi: Package छोटा रखें, secrets zip से बाहर रखें, और CI के permissions सीमित रखें।

---

## ➡️ Next Topic
**392. Serverless Framework + GitHub Actions**: writing many CLI commands per function does not scale, so next we manage functions, APIs and queues as one config with Serverless Framework.
