---

# 91. Lambda Cold Start
# AWS: Lambda cold start (SnapStart, provisioned concurrency)
# Azure: Azure Functions cold start (Premium plan pre-warmed instances)
# हिंदी में: लैम्ब्डा कोल्ड स्टार्ट

---

## 🔵 Simple Definition (2 lines)
A cold start is the extra delay when Lambda must create a new execution environment, download code and init the runtime before running your handler.
हिंदी: Cold start वह अतिरिक्त देरी है जब Lambda को नया एनवायरनमेंट बनाना पड़ता है।

---

## 🔴 Why it Exists (2 lines)
Idle environments are removed to save resources. The first request after idle or a scale-up pays the init cost, which hurts latency-sensitive APIs.

---

## 🟢 How it Works
```
Cold:  download code -> start runtime -> INIT (imports, clients) -> handler   (slow)
Warm:  reuse environment ------------------------------------> handler       (fast)

Reduce it:
  - smaller package, fewer imports (esbuild bundle for Node.js)
  - init clients/connections outside the handler
  - more memory = more CPU = faster init
  - arm64 (Graviton), lighter runtimes (Node, Python, Go vs heavy JVM)
  - SnapStart (supported Java, and newer Python/.NET -- check current docs)
  - Provisioned concurrency (pre-warmed)
  - Avoid VPC attach unless needed (modern VPC cold starts are much better)
```

---

## 💻 Code / Config Example
```javascript
// index.mjs : good pattern, heavy init once per environment
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, GetCommand } from "@aws-sdk/lib-dynamodb";

const t0 = Date.now();
const ddb = DynamoDBDocumentClient.from(new DynamoDBClient({}));   // INIT phase
console.log("init ms", Date.now() - t0);

export const handler = async (event) => {
  const r = await ddb.send(new GetCommand({
    TableName: process.env.TABLE_NAME, Key: { id: event.id } }));
  return r.Item ?? null;
};
```
```bash
# Bundle to shrink package (esbuild)
npx esbuild index.mjs --bundle --platform=node --target=node20 --format=esm \
  --minify --outfile=dist/index.mjs --external:@aws-sdk/*   # SDK v3 ships in runtime
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Mitigation | Provisioned concurrency / SnapStart | Premium plan always-ready/pre-warmed |
| Free scale to zero | Yes | Consumption: yes (cold starts) |
| Observability | REPORT line `Init Duration` in logs | Application Insights |
| Pricing | Init billed in some cases (approximate — check current docs) | Premium has base cost (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Creating SDK clients inside the handler.
✅ Correct: Create once at module level.

❌ Mistake: Shipping a 50 MB node_modules for a tiny function.
✅ Correct: Bundle and tree-shake.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is a cold start?
A1: Latency from creating a new execution environment before the handler runs.

Q2: [Medium] How do you measure it?
A2: `Init Duration` in the CloudWatch REPORT line, or X-Ray's Initialization segment.

Q3: [Hard] An API needs p99 < 200 ms with spiky traffic. What do you do?
A3: Bundle small, arm64, init outside handler, tune memory, provisioned concurrency (or autoscaled) for the baseline; or move to Fargate if traffic is steady.

---

## ✅ Quick Checklist
□ Clients outside handler
□ Bundled and minified
□ Provisioned concurrency only where needed

---

## ⚡ 1-Line Summary
Cold start = init delay on new environment | Cold start = नए एनवायरनमेंट की शुरुआती देरी।

## ➡️ Next: Lambda Pricing

---
