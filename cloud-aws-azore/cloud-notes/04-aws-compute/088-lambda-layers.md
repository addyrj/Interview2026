---

# 88. Lambda Layers
# AWS: Lambda Layers
# Azure: N/A (no direct feature); closest = shared packages / custom container image
# हिंदी में: लैम्ब्डा लेयर्स

---

## 🔵 Simple Definition (2 lines)
A layer is a zip of libraries or shared code that many functions can attach, extracted under /opt at runtime.
हिंदी: Layer एक zip है जिसमें साझा लाइब्रेरी होती हैं, जिसे कई Lambda फ़ंक्शन इस्तेमाल कर सकते हैं।

---

## 🔴 Why it Exists (2 lines)
Bundling the same heavy dependencies in every function bloats packages and slows deploys. Layers share them once.

---

## 🟢 How it Works
```
layer.zip
  └─ nodejs/node_modules/...      (Node.js)
  └─ python/lib/python3.12/site-packages/...  (Python)
        |
publish-layer-version -> ARN with version number
        |
Function config: Layers=[arn:...:layer:deps:3]  (max 5 layers)
Runtime: extracted to /opt ; Node finds /opt/nodejs/node_modules automatically
Total unzipped size (function + layers) <= 250 MB (approximate — check current docs)
```

---

## 💻 Code / Config Example
```bash
# Build a Node.js layer (AWS CLI v2; publish step needs real credentials)
mkdir -p layer/nodejs && cd layer/nodejs
npm init -y && npm install lodash
cd .. && zip -r ../deps-layer.zip nodejs && cd ..

aws lambda publish-layer-version --layer-name deps \
  --zip-file fileb://deps-layer.zip \
  --compatible-runtimes nodejs20.x

aws lambda update-function-configuration --function-name hello \
  --layers arn:aws:lambda:ap-south-1:123456789012:layer:deps:1
```
```javascript
// index.mjs : import comes from the layer (/opt/nodejs/node_modules)
import _ from "lodash";
export const handler = async () => ({ statusCode: 200, body: _.camelCase("hello world") });
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Shared deps | Layers (versioned) | N/A: bundle deps or use container image |
| Limit | 5 layers per function | Not applicable |
| Alternative | Container image up to 10 GB | Custom container on Functions Premium |
| Pricing | No extra charge for layers (approximate — check current docs) | N/A |

---

## ⚠️ Common Mistakes
❌ Mistake: Wrong folder structure (files not under `nodejs/`), so imports fail.
✅ Correct: Follow the runtime-specific path.

❌ Mistake: Using `latest` thinking layer versions auto-update.
✅ Correct: Layer versions are immutable; update the function to the new ARN version.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is a layer?
A1: A versioned zip with libs/code mounted at /opt for functions.

Q2: [Medium] Do layers bypass the size limit?
A2: No, function plus layers must stay within the unzipped limit; use container images for bigger.

Q3: [Hard] Layers vs container images?
A3: Layers: quick sharing of small deps across functions. Containers: bigger deps, full control, same Docker workflow as the rest of your stack, but heavier builds.

---

## ✅ Quick Checklist
□ Correct directory layout for runtime
□ Layer version pinned in IaC
□ Layer architecture matches function (x86_64/arm64)

---

## ⚡ 1-Line Summary
Layers share dependencies across functions | Layers से कई फ़ंक्शन एक ही डिपेंडेंसी साझा करते हैं।

## ➡️ Next: Lambda Environment Variables

---
